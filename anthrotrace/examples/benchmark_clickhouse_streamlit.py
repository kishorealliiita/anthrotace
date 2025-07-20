from anthrotrace.core.yaml_prompt_loader import load_prompts_with_categories
from anthrotrace.core.clickhouse_prompt_log_repository import ClickHousePromptLogRepository
from anthrotrace.core.anthropic_benchmark_sqlite_runner import AnthropicBenchmarkWithSQLite
from clickhouse_connect import get_client

import concurrent.futures
import random
import os

API_KEY = os.environ.get("ANTHROPIC_API_KEY")
FORCE_FAILURE_RATE = 0.2
PARALLEL_WORKERS = 5

# Load Prompts
prompts = load_prompts_with_categories("anthrotrace/data/anthrotrace_common_prompts.yaml")
random.shuffle(prompts)

def run_prompt_to_clickhouse(prompt):
    try:
        # Per-thread ClickHouse client and repo
        clickhouse_client = get_client(host="localhost", port=8123, username="default", password="")
        clickhouse_repo = ClickHousePromptLogRepository(clickhouse_client)

        # Benchmark runner (per thread)
        runner = AnthropicBenchmarkWithSQLite(
            api_key=API_KEY,
            metrics_exporter=None  # Optional if you want to disable Prometheus here
        )
        runner.sqlite_repo = None  # Disable SQLite insert

        force_fail = random.random() < FORCE_FAILURE_RATE
        if force_fail:
            print(f"[FORCE-FAIL] {prompt['category']}")
            clickhouse_repo.insert_log(
                category=prompt["category"],
                model="claude-sonnet-4-20250514",
                prompt_text="!!! Intentional bad prompt for failure test !!!",
                response=None,
                input_tokens=0,
                output_tokens=0,
                duration=0.0,
                cost=0.0
            )
        else:
            result = runner.run_and_return(
                category=prompt["category"],
                prompt_text=prompt["prompt_text"],
                model="claude-sonnet-4-20250514"
            )

            clickhouse_repo.insert_log(
                category=result["category"],
                model=result["model"],
                prompt_text=result["prompt_text"],
                response=result["response"],
                input_tokens=result["input_tokens"],
                output_tokens=result["output_tokens"],
                duration=result["duration"],
                cost=result["cost"]
            )

        print(f"[SUCCESS] {prompt['category']} processed.")

    except Exception as e:
        print(f"[ERROR] Benchmark run failed for {prompt['category']}: {e}")

with concurrent.futures.ThreadPoolExecutor(max_workers=PARALLEL_WORKERS) as executor:
    futures = [executor.submit(run_prompt_to_clickhouse, prompt) for prompt in prompts]
    concurrent.futures.wait(futures)

print("✅ Parallel Benchmarking to ClickHouse Completed.")
