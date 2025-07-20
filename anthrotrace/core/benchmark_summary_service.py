from datetime import datetime

class BenchmarkSummaryService:
    def __init__(self, repository):
        self.repo = repository

    def get_summary(self, category=None, model=None, start_time=None, end_time=None):
        logs = self.repo.query_logs(
            category=category,
            model=model,
            start_time=start_time,
            end_time=end_time
        )

        if not logs:
            return None

        total_runs = len(logs)
        successes = sum(1 for log in logs if log.get('response'))
        failures = total_runs - successes

        avg_input_tokens = sum(log.get('input_tokens', 0) for log in logs) / total_runs
        avg_output_tokens = sum(log.get('output_tokens', 0) for log in logs) / total_runs
        avg_cost = sum(log.get('cost', 0.0) for log in logs) / total_runs
        avg_latency = sum(log.get('duration', 0.0) for log in logs) / total_runs

        last_run = max(
            datetime.fromisoformat(str(log.get('timestamp')).replace('Z', '+00:00')).replace(tzinfo=None)
            for log in logs if log.get('timestamp')
        )

        return {
            "category": category or "All Categories",
            "model": model or "All Models",
            "total_runs": total_runs,
            "success_count": successes,
            "failure_count": failures,
            "success_ratio": round((successes / total_runs) * 100, 2),
            "average_input_tokens": round(avg_input_tokens, 2),
            "average_output_tokens": round(avg_output_tokens, 2),
            "average_cost_usd": round(avg_cost, 4),
            "average_latency_sec": round(avg_latency, 2),
            "last_run_timestamp": last_run.isoformat(),
        } 