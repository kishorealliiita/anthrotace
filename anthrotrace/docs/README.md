AnthroTrace — PromptOps Cost Intelligence SDK

Overview

AnthroTrace is a lightweight SDK for tracking Anthropic prompt usage, logging structured prompt metadata, and monitoring cost.It provides flexible storage adapters and integrates with Prometheus-compatible metrics exporters for observability in production environments.

Key Features

✅ Prompt Logging — Records prompt metadata, usage statistics, and response summaries

✅ Cost Calculation — Tracks input/output tokens and estimates USD cost per prompt based on Anthropic pricing

✅ Pluggable Storage Backends

SQLite — For local development and testing

ClickHouse — For high-throughput production environments

✅ Prometheus Metrics Exporter — Exposes prompt usage and cost metrics for observability

✅ Time-Range Query Support — Filter logs and metrics by date/time with local or UTC handling

Architecture

Prompt Client — Wraps Anthropic API calls and injects logging + metrics

Repository Adapter — Unified interface for writing logs to different storage backends

Storage Implementations

SQLiteRepository

ClickHousePromptLogRepository

Prometheus Metrics Exporter — Collects aggregated prompt usage stats

Streamlit Dashboard — Visualizes benchmark results, metrics, and storage usage

Example Usage

from anthropic_client import AnthropicPromptClient
from repository_adapter import RepositoryAdapter
from sqlite_repository import SQLiteRepository
from metrics.prometheus_metrics_exporter import PrometheusMetricsExporter

# Setup storage and metrics
repo = SQLiteRepository("anthrotrace.db")
adapter = RepositoryAdapter(repo)
metrics_exporter = PrometheusMetricsExporter()

# Initialize client
client = AnthropicPromptClient(adapter, metrics_exporter)

# Send a prompt
result = client.send_prompt("Tell me a joke.")
print(result)

SDK Configuration

Environment Variable

Description

Example

ANTHROPIC_API_KEY

Your Anthropic API key

sk-ant-...

LOG_LEVEL

Logging level (DEBUG, INFO, WARN, ERROR)

INFO

CLICKHOUSE_HOST

ClickHouse host (if used)

localhost

CLICKHOUSE_PORT

ClickHouse port (if used)

8123

Default logging level: INFOLogging can be configured programmatically or via environment variables.

Deployment Options

Mode

Storage

Metrics

Recommended For

Local Dev

SQLite

Prometheus Local

Development, Testing

Production

ClickHouse

Prometheus Remote

Production, Observability

Prometheus Metrics

Exposed metrics include:

anthrotrace_prompt_total — Total prompts sent

anthrotrace_prompt_tokens_total — Total tokens (input + output)

anthrotrace_prompt_cost_usd_total — Total cost in USD

Repository Implementations

SQLiteRepository — Logs prompts in local SQLite DB

ClickHousePromptLogRepository — Stores prompts in ClickHouse (MergeTree) with customizable schema

Supports query filters on category, timestamp, and other metadata

Prerequisites

Python 3.8+

Install dependencies:

pip install -r requirements.txt

ClickHouse server (for production mode)

Prometheus server (for metrics collection)

Running Benchmarks & Dashboard

SQLite Benchmark with Streamlit:

PYTHONPATH=. python3 examples/benchmark_sqllite_streamlit.py

ClickHouse Benchmark with Streamlit:

PYTHONPATH=. python3 examples/benchmark_clickhouse_streamlit.py

Access the dashboard:

http://localhost:8501

Architecture Diagram

+--------------------+          +--------------------+          +--------------------+
|   Prompt Client   |  Logs &  | Repository Adapter |  Writes |   Storage (CH/SQL) |
+--------------------+  Cost    +--------------------+--------->+--------------------+
          |                         |
          | Metrics                 |
          v                         v
   +--------------------+    +--------------------+
   | Prometheus Exporter|    | Streamlit Dashboard|
   +--------------------+    +--------------------+

Roadmap



Contributing

We welcome contributions!Please check CONTRIBUTING.md before submitting a pull request.

License

MIT License — See LICENSE

Disclaimer

AnthroTrace is not affiliated with Anthropic.Use at your own risk, especially in production environments.

