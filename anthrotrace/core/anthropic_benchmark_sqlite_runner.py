import time
import anthropic
from datetime import datetime, timezone

from anthrotrace.core.sqlite_repository import SQLiteRepository
from anthrotrace.core.cost_calculator import calculate_cost

class AnthropicBenchmarkWithSQLite:
    def __init__(self, api_key, db_path="data/prompt_logs.db", metrics_exporter=None, cost_calculator=None):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.sqlite_repo = SQLiteRepository(db_path=db_path)
        self.metrics = metrics_exporter  # Injected externally (shared instance)
        self.cost_calculator = cost_calculator or calculate_cost

    def run_and_return(self, category, prompt_text, model="claude-sonnet-4-20250514"):
        try:
            start_time = time.time()
            response = self.client.messages.create(
                model=model,
                max_tokens=300,
                temperature=0,
                system="You are a helpful assistant.",
                messages=[{"role": "user", "content": prompt_text}]
            )
            duration = time.time() - start_time
            usage = response.usage

            input_tokens = usage.input_tokens if usage else 0
            output_tokens = usage.output_tokens if usage else 0
            cost = self.cost_calculator({
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "category": category,
                "prompt_text": prompt_text,
                "response": response.content[0].text if response.content else None,
                # Add more fields as needed for custom calculators
            })

            result = {
                "category": category,
                "model": model or "unknown",
                "prompt_text": prompt_text,
                "response": response.content[0].text if response.content else None,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "duration": duration,
                "cost": cost,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            print(f"[SUCCESS] Benchmark completed for category: {category}")

            if self.metrics:
                self._emit_metrics(result, success=True)

            self._insert_into_sqlite(result)
            return result

        except Exception as e:
            print(f"[ERROR] Benchmark run failed for category {category}: {e}")

            fail_result = {
                "category": category,
                "model": model or "unknown",
                "prompt_text": prompt_text,
                "response": None,
                "input_tokens": 0,
                "output_tokens": 0,
                "duration": 0.0,
                "cost": 0.0,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            if self.metrics:
                self._emit_metrics(fail_result, success=False)

            self._insert_into_sqlite(fail_result)
            return fail_result

    def _insert_into_sqlite(self, result):
        if not self.sqlite_repo:
            return  # Skip if SQLite is disabled

        insert_sql = """
        INSERT INTO prompt_logs
        (category, model, prompt_text, response, input_tokens, output_tokens, duration, cost, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.sqlite_repo.conn.execute(insert_sql, (
            result["category"],
            result["model"],
            result["prompt_text"],
            result["response"],
            result["input_tokens"],
            result["output_tokens"],
            result["duration"],
            result["cost"],
            result["timestamp"]
        ))
        self.sqlite_repo.conn.commit()

    def _emit_metrics(self, result, success=True):
        if not self.metrics:
            return

        category = result["category"]
        total_tokens = result["input_tokens"] + result["output_tokens"]

        self.metrics.emit_metric("prompt_total_tokens", total_tokens, {"category": category})
        self.metrics.emit_metric("prompt_total_cost_usd", result["cost"], {"category": category})
        self.metrics.emit_metric("prompt_avg_duration_seconds", result["duration"], {"category": category})

        if success:
            self.metrics.emit_metric("prompt_success_total", 1, {"category": category})
        else:
            self.metrics.emit_metric("prompt_failure_total", 1, {"category": category})

        self.metrics.emit_histogram("prompt_latency_seconds", result["duration"], None, {"category": category})
        self.metrics.emit_histogram("prompt_cost_per_run_usd", result["cost"], None, {"category": category})
        self.metrics.emit_histogram("prompt_total_tokens_histogram", total_tokens, None, {"category": category})
