import streamlit as st
from datetime import datetime, timedelta, timezone
import pandas as pd
from dateutil import tz
import requests
import time

from anthrotrace.core.benchmark_summary_service import BenchmarkSummaryService
from anthrotrace.core.repository_adapter import RepositoryAdapter
from anthrotrace.core.clickhouse_prompt_log_repository import ClickHousePromptLogRepository
from anthrotrace.core.sqlite_repository import SQLiteRepository
from clickhouse_connect import get_client
from anthrotrace.metrics.prometheus_metrics_exporter import PrometheusMetricsExporter

def get_filter_datetimes(start_date, end_date, return_utc=False):
    local_tz = tz.tzlocal()
    start_dt = datetime.combine(start_date, datetime.min.time()).replace(tzinfo=local_tz)
    end_dt = datetime.combine(end_date + timedelta(days=1), datetime.min.time()).replace(tzinfo=local_tz)
    return (start_dt.astimezone(timezone.utc), end_dt.astimezone(timezone.utc)) if return_utc else (start_dt, end_dt)

# ---- Setup ----
st.set_page_config(page_title="Anthropic Benchmark Summary", layout="wide")
st.title("Anthropic Benchmark Summary Dashboard")

if "metrics_exporter" not in st.session_state:
    st.session_state.metrics_exporter = PrometheusMetricsExporter(port=8001)
metrics_exporter = st.session_state.metrics_exporter

# ---- Sidebar ----
st.sidebar.header("Filters")
data_source = st.sidebar.radio("Select Data Source", ["ClickHouse", "SQLite"])

repo = None
clickhouse_error = None
if data_source == "ClickHouse":
    try:
        clickhouse_client = get_client(host="localhost", port=8123, username="default", password="")
        repo = ClickHousePromptLogRepository(clickhouse_client)
    except Exception as e:
        clickhouse_error = str(e)
        st.sidebar.warning(f"Could not connect to ClickHouse: {clickhouse_error}")
        repo = None
else:
    repo = SQLiteRepository(db_path="data/prompt_logs.db")

if repo is not None:
    adapter = RepositoryAdapter(repo)
    summary_service = BenchmarkSummaryService(adapter)
else:
    adapter = None
    summary_service = None

try:
    if adapter is not None:
        all_logs = adapter.query_logs()
        categories = ["All Categories"] + sorted({log.get("category") for log in all_logs if log.get("category")})
        models = ["All Models"] + sorted({log.get("model") for log in all_logs if log.get("model")})
    else:
        categories, models = ["All Categories"], ["All Models"]
except Exception as e:
    st.sidebar.warning(f"Error fetching categories/models: {e}")
    categories, models = ["All Categories"], ["All Models"]

selected_category = st.sidebar.selectbox("Select Category", categories)
selected_model = st.sidebar.selectbox("Select Model", models)

local_now = datetime.now().astimezone()
start_date = st.sidebar.date_input("Start Date", value=local_now.date() - timedelta(days=1))
end_date = st.sidebar.date_input("End Date", value=local_now.date())

bucket_options = ["1min", "5min", "15min", "30min"]
selected_bucket = st.sidebar.selectbox("Aggregation Interval", bucket_options, index=0)

# ---- Filters ----
if data_source == "ClickHouse":
    start_datetime, end_datetime = get_filter_datetimes(start_date, end_date, return_utc=True)
else:
    start_datetime, end_datetime = get_filter_datetimes(start_date, end_date, return_utc=False)

# ---- Generate Summary ----
if st.sidebar.button("Generate Summary"):
    if repo is None:
        st.error("Cannot generate summary: No data source available.")
    else:
        st.success(f"Summary for `{selected_category}` / `{selected_model}` from `{start_date}` to `{end_date}` using `{data_source}`")

        summary = summary_service.get_summary(
            category=None if selected_category == "All Categories" else selected_category,
            model=None if selected_model == "All Models" else selected_model,
            start_time=start_datetime,
            end_time=end_datetime
        )

        if summary:
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Runs", summary["total_runs"])
            col2.metric("Success Ratio (%)", summary["success_ratio"])
            col3.metric("Avg Latency (sec)", summary["average_latency_sec"])

            col4, col5, col6 = st.columns(3)
            col4.metric("Avg Input Tokens", summary["average_input_tokens"])
            col5.metric("Avg Output Tokens", summary["average_output_tokens"])
            col6.metric("Avg Cost (USD)", summary["average_cost_usd"])

            st.markdown(f"**Last Run Timestamp:** {summary['last_run_timestamp']}")

            try:
                metrics_exporter.emit_metric("prompt_total_tokens", summary["total_runs"], {"category": selected_category})
                metrics_exporter.emit_metric("prompt_avg_duration_seconds", summary["average_latency_sec"], {"category": selected_category})
            except Exception as e:
                st.warning(f"Failed to emit Prometheus metrics: {e}")

            # ---- Charts ----
            filtered_logs = adapter.query_logs(
                category=None if selected_category == "All Categories" else selected_category,
                model=None if selected_model == "All Models" else selected_model,
                start_time=start_datetime,
                end_time=end_datetime
            )

            if filtered_logs:
                df = pd.DataFrame(filtered_logs)
                st.dataframe(df, use_container_width=True)

                df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors='coerce')
                df["bucket"] = df["timestamp"].dt.floor(selected_bucket)

                df["status"] = df["response"].apply(lambda r: "success" if r and str(r).strip() else "failure")
                df["total_tokens"] = df["input_tokens"] + df["output_tokens"]

                st.subheader(f"📈 Requests Over Time ({selected_bucket})")
                st.line_chart(df.groupby(["bucket", "status"]).size().unstack(fill_value=0))

                st.subheader("💵 Total Cost Over Time")
                st.line_chart(df.groupby("bucket")["cost"].sum())

                st.subheader("🔢 Total Tokens Processed Over Time")
                st.line_chart(df.groupby("bucket")["total_tokens"].sum())

                st.subheader("📊 Success vs Failure Percentage Over Time")
                ratio = df.groupby(["bucket", "status"]).size().unstack(fill_value=0)
                ratio["total"] = ratio.sum(axis=1)
                ratio["success_ratio"] = (ratio.get("success", 0) / ratio["total"]) * 100
                ratio["failure_ratio"] = (ratio.get("failure", 0) / ratio["total"]) * 100
                st.line_chart(ratio[["success_ratio", "failure_ratio"]])

                # ---- Insights ----
                st.subheader("🔥 Insights & Outliers")

                st.write("🔻 Top Categories by Failure Count")
                st.dataframe(df[df["status"] == "failure"].groupby("category").size().sort_values(ascending=False).head(5))

                st.write("🐢 Slowest Prompts by Avg Duration")
                st.dataframe(df.groupby("prompt_text")["duration"].mean().sort_values(ascending=False).head(5))

                st.write("💰 Top Cost Categories")
                st.dataframe(df.groupby("category")["cost"].sum().sort_values(ascending=False).head(5))

            else:
                st.info("No detailed logs for selected filters.")
        else:
            st.warning("No data found for given filters.")

# ---- Prometheus Export ----
if st.sidebar.button("Show Prometheus Metrics"):
    with st.expander("🔍 Raw Prometheus Metrics"):
        try:
            response = requests.get("http://localhost:8001/metrics")
            if response.status_code == 200:
                st.text_area("Prometheus Metrics", response.text, height=300)
            else:
                st.warning("Could not fetch Prometheus metrics from exporter.")
        except Exception as e:
            st.error(f"Error fetching Prometheus metrics: {e}")

with st.expander("📊 Metrics Exporter Health"):
    st.metric("Total Metrics Emitted", metrics_exporter.emitted_metrics_count)
