from prometheus_client import Counter, Gauge, Histogram, CollectorRegistry, start_http_server
import threading


class PrometheusMetricsExporter:
    _server_started = False
    _lock = threading.Lock()

    def __init__(self, port=8000):
        with PrometheusMetricsExporter._lock:
            if not PrometheusMetricsExporter._server_started:
                try:
                    start_http_server(port)
                    print(f"[PROMETHEUS] Metrics server started on http://localhost:{port}/metrics")
                except OSError as e:
                    print(f"[PROMETHEUS] Could not start metrics server on port {port}: {e}")
                PrometheusMetricsExporter._server_started = True

        self.registry = CollectorRegistry()
        self.metrics = {}
        self.histograms = {}
        self.emitted_metrics_count = 0

    def emit_metric(self, name, value, labels, metric_type="gauge"):
        metric_key = (name, tuple(sorted(labels.items())))

        if metric_key not in self.metrics:
            if metric_type == "counter":
                self.metrics[metric_key] = Counter(name, f"{name} counter", labels.keys())
            elif metric_type == "gauge":
                self.metrics[metric_key] = Gauge(name, f"{name} gauge", labels.keys())

        metric = self.metrics[metric_key].labels(**labels)

        if metric_type == "counter":
            metric.inc(value)
        elif metric_type == "gauge":
            metric.set(value)

        self.emitted_metrics_count += 1

    def emit_histogram(self, name, value, buckets, labels):
        metric_key = (name, tuple(sorted(labels.items())))

        if metric_key not in self.histograms:
            self.histograms[metric_key] = Histogram(
                name, f"{name} histogram", labels.keys(), buckets=buckets
            )

        self.histograms[metric_key].labels(**labels).observe(value)
        self.emitted_metrics_count += 1
