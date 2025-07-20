# Anthrotrace

Anthrotrace is a benchmarking and analytics suite specifically for evaluating prompts and responses from **Anthropic LLMs** (Claude models), with support for **both SQLite and ClickHouse backends**, Prometheus metrics, and a Streamlit dashboard for interactive analysis.

## Features
- **Prompt Benchmarking**: Run and log Anthropic LLM prompt/response benchmarks in parallel.
- **Multi-Backend Support**: Store logs in **SQLite or ClickHouse** (selectable in dashboard and scripts).
- **Metrics Export**: Prometheus-compatible metrics exporter for monitoring.
- **Streamlit Dashboard**: Visualize and analyze prompt logs and metrics interactively.
- **Extensible**: Modular design for adding new repositories, exporters, or data sources.

## Project Structure
```
anthrotrace/
  core/         # Core logic: repositories, runners, adapters, loaders
  metrics/      # Metrics exporters (Prometheus, etc.)
  cli/          # CLI utilities
  streamlit/    # Streamlit dashboard app
  data/         # Prompt YAMLs and (ignored) log data
  examples/     # Example scripts for benchmarking
  tests/        # (If present) Unit tests
  config/       # Config files (e.g., prometheus.yml)
  docs/         # Documentation
```

## Setup
1. **Clone the repository**
```sh
git clone https://github.com/kishorealliiita/anthrotace
cd anthrotrace
```

2. **Install dependencies**
```sh
pip install -r anthrotrace/requirements.txt
```

3. **Set your Anthropic API key**
```sh
export ANTHROPIC_API_KEY=sk-ant-...your_key_here...
```

4. **(Optional) Install in editable mode**
If you want to use imports like `from anthrotrace.core...` everywhere:
```sh
pip install -e .
```
*You do not need to generate a setup.py or pyproject.toml—these are already included.*

## Requirements
- Python 3.8+
- Dependencies (see requirements.txt): anthropic, streamlit, pandas, python-dateutil, prometheus_client, clickhouse-connect, **pyyaml**
- Docker
**To start ClickHouse using Docker:**
```sh
docker run -d --name clickhouse-server -p 8123:8123 -p 9000:9000 yandex/clickhouse-server
```
This will run ClickHouse in the background and expose the default HTTP (8123) and native (9000) ports.

## Usage

### Run Example Benchmarks
- **ClickHouse**:
  ```sh
  python anthrotrace/examples/benchmark_clickhouse_streamlit.py
  ```
- **SQLite**:
  ```sh
  python anthrotrace/examples/benchmark_sqllite_streamlit.py
  ```

### Run the Streamlit Dashboard
```sh
PYTHONPATH=. streamlit run anthrotrace/streamlit/streamlit_app.py
```

- Once running, open your browser to: [http://localhost:8501](http://localhost:8501)

### Prometheus Metrics
- Prometheus metrics are exported on port 8000 (or 8001 for Streamlit dashboard).
- See `anthrotrace/config/prometheus.yml` for example config.

## Data & Logs
- All data and logs are stored in the `data/` directory (which is gitignored).
- Prompts are loaded from `anthrotrace/data/anthrotrace_common_prompts.yaml`.

## Prompt Categories & Customization

The file `anthrotrace/data/anthrotrace_common_prompts.yaml` contains a set of common prompt categories (e.g., Summarization, Code Generation, Bug Fixing, etc.) with example prompts for benchmarking Anthropic LLMs. **You can freely add, remove, or modify categories and prompts in this YAML file to suit your needs.**

- The dashboards and reports will automatically reflect any changes you make to this file—no code changes required.
- This makes it easy to benchmark new tasks, domains, or prompt types as your use case evolves.

## Development
- All core logic is in `anthrotrace/core/`.
- Metrics exporters in `anthrotrace/metrics/`.
- Add new scripts to `anthrotrace/examples/`.
- To add new data sources or exporters, follow the patterns in `core/` and `metrics/`.

## License
See [LICENSE](../LICENSE).

---

**Questions or issues?** Open an issue or contact [Kishore Korathaluri](https://www.linkedin.com/in/kishore-korathaluri/). 

## Dashboards & Reporting

### Streamlit Dashboard
- **Interactive web dashboard** for exploring prompt logs and metrics.
- **Switch between ClickHouse and SQLite** as data sources.
- **Filter** by category, model, and date range.
- **Visualize:**
  - Total runs, success ratio, average latency, input/output tokens, cost, last run timestamp.
  - Time series charts for requests, cost, tokens, and success/failure ratios.
  - Tables for top failures, slowest prompts, and highest cost categories.
- **Export and view Prometheus metrics** directly from the dashboard.
- **Live metrics health panel** for monitoring exporter activity.

**Usage:**
```sh
PYTHONPATH=. streamlit run anthrotrace/streamlit/streamlit_app.py
```
Then open [http://localhost:8501](http://localhost:8501) in your browser.

---

### CLI Metrics Report
- **Generate metrics reports** from ClickHouse logs via command line.
- **Output as table or JSON.**
- **Filter** by category and date range.
- **Shows totals and averages** for tokens, cost, and duration.

**Usage Examples:**
```sh
python anthrotrace/cli/metrics_report.py --format table
python anthrotrace/cli/metrics_report.py --format json --category "Creative Writing" --since 2024-06-01 --until 2024-06-30
```

--- 

## Customizing Cost Calculation

By default, cost is calculated using Anthropic's pricing table. You can provide your own pricing dictionary for custom models or rates:

```python
from anthrotrace.core.cost_calculator import make_cost_calculator
from anthrotrace.core.anthropic_benchmark_sqlite_runner import AnthropicBenchmarkWithSQLite

my_pricing = {
    "my-model": {"input": 1.0, "output": 2.0},
    # ... more models ...
}
my_cost_fn = make_cost_calculator(my_pricing)

runner = AnthropicBenchmarkWithSQLite(api_key, cost_calculator=my_cost_fn)
```

This allows you to benchmark with your own cost logic or rates. 