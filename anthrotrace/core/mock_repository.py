class MockRepository:
    def __init__(self):
        self.logs = []

    def insert_log(self, category, prompt_text, response, input_tokens, output_tokens, duration, cost=0, timestamp=None):
        from datetime import datetime
        if timestamp is None:
            # Use UTC datetime object for consistency
            timestamp = datetime.utcnow()
        # Always store as a datetime object
        self.logs.append({
            'category': category,
            'prompt_text': prompt_text,
            'response': response,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'duration': duration,
            'cost': cost,
            'timestamp': timestamp
        })

    def fetch_logs(self):
        return self.logs

    def get_all_logs(self):
        return self.logs

    def get_aggregated_stats(self):
        # Return mock aggregated stats for demonstration
        if not self.logs:
            return []
        from collections import defaultdict
        stats = defaultdict(lambda: {'total_tokens': 0, 'total_cost': 0, 'total_duration': 0, 'count': 0})
        for log in self.logs:
            cat = log['category']
            stats[cat]['total_tokens'] += log['input_tokens'] + log['output_tokens']
            stats[cat]['total_cost'] += log['cost']
            stats[cat]['total_duration'] += log['duration']
            stats[cat]['count'] += 1
        result = []
        for cat, s in stats.items():
            avg_duration = s['total_duration'] / s['count'] if s['count'] else 0
            result.append((cat, s['total_tokens'], round(s['total_cost'], 5), round(avg_duration, 2)))
        return result

    def convert_logs_to_metrics(self, exporter):
        stats = self.get_aggregated_stats()
        duration_buckets = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
        token_buckets = [100, 500, 1000, 2000, 5000, 10000]
        for stat in stats:
            category, total_tokens, total_cost, avg_duration = stat
            labels = {'category': category}
            exporter.emit_metric("prompt_total_tokens", total_tokens, labels, metric_type="counter")
            exporter.emit_metric("prompt_total_cost_usd", total_cost, labels, metric_type="counter")
            exporter.emit_metric("prompt_avg_duration_seconds", avg_duration, labels, metric_type="gauge")
            exporter.emit_histogram("prompt_duration_seconds", avg_duration, duration_buckets, labels)
            exporter.emit_histogram("prompt_total_tokens_histogram", total_tokens, token_buckets, labels)
        print(f"[MOCK METRICS] Emitted {len(stats)} metrics sets from MockRepository")

    def populate_sample_logs(self):
        import datetime
        today = datetime.datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)
        self.insert_log(
            category="claude-sonnet-4",
            prompt_text="Summarize OpenTelemetry in 3 points.",
            response="OpenTelemetry is an observability framework...",
            input_tokens=120,
            output_tokens=80,
            duration=1.2,
            cost=0.002,
            timestamp=today
        )
        self.insert_log(
            category="claude-sonnet-4",
            prompt_text="Explain the benefits of OpenTelemetry.",
            response="It provides vendor-neutral observability...",
            input_tokens=100,
            output_tokens=100,
            duration=1.5,
            cost=0.003,
            timestamp=today
        )
        self.insert_log(
            category="claude-sonnet-4",
            prompt_text="What is tracing?",
            response="Tracing tracks requests across services...",
            input_tokens=90,
            output_tokens=110,
            duration=1.1,
            cost=0.0025,
            timestamp=today
        )