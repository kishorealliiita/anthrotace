from anthrotrace.core.yaml_prompt_loader import load_prompts_with_categories
from anthrotrace.core.anthropic_benchmark_sqlite_runner import AnthropicBenchmarkWithSQLite

import random
import os

API_KEY = os.environ.get("ANTHROPIC_API_KEY")
FORCE_FAILURE_RATE = 0.2

prompts = load_prompts_with_categories("anthrotrace/data/anthrotrace_common_prompts.yaml")
random.shuffle(prompts)

runner = AnthropicBenchmarkWithSQLite(api_key=API_KEY)

for prompt in prompts:
    try:
        force_fail = random.random() < FORCE_FAILURE_RATE

        if force_fail:
            print(f"[INFO] Sending forced failure for category: {prompt['category']}")
            fake_prompt = "!!! Intentional bad prompt for failure test !!!"
            result = runner.run_and_return(
                category=prompt["category"],
                prompt_text=fake_prompt,
                model="claude-sonnet-4-20250514"
            )
            if runner.sqlite_repo:
                runner._insert_into_sqlite(result)
        else:
            result = runner.run_and_return(
                category=prompt["category"],
                prompt_text=prompt["prompt_text"],
                model="claude-sonnet-4-20250514"
            )
            if runner.sqlite_repo:
                runner._insert_into_sqlite(result)

        print(f"[SUCCESS] Benchmark processed for category: {prompt['category']}")

    except Exception as e:
        print(f"[ERROR] Benchmark failed for category {prompt['category']}: {e}")

print("✅ Benchmarking to SQLite Completed.")
