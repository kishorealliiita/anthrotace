import unittest
from anthrotrace.core.benchmark_summary_service import BenchmarkSummaryService
import os

class DummyRepo:
    def query_logs(self, category=None, model=None, start_time=None, end_time=None):
        return [
            {'category': 'A', 'model': 'M1', 'input_tokens': 10, 'output_tokens': 5, 'cost': 0.01, 'duration': 1.2, 'response': 'ok', 'timestamp': '2024-06-01T00:00:00'},
            {'category': 'A', 'model': 'M1', 'input_tokens': 20, 'output_tokens': 10, 'cost': 0.02, 'duration': 1.5, 'response': '', 'timestamp': '2024-06-02T00:00:00'},
        ]

class TestBenchmarkSummaryService(unittest.TestCase):
    def test_get_summary(self):
        service = BenchmarkSummaryService(DummyRepo())
        summary = service.get_summary(category='A', model='M1')
        self.assertEqual(summary['total_runs'], 2)
        self.assertEqual(summary['success_count'], 1)
        self.assertEqual(summary['failure_count'], 1)
        self.assertAlmostEqual(summary['average_input_tokens'], 15.0)
        self.assertAlmostEqual(summary['average_output_tokens'], 7.5)
        self.assertAlmostEqual(summary['average_cost_usd'], 0.015)
        self.assertAlmostEqual(summary['average_latency_sec'], 1.35)
        self.assertEqual(summary['category'], 'A')
        self.assertEqual(summary['model'], 'M1')

if __name__ == '__main__':
    yaml_path = os.path.join(os.path.dirname(__file__), "../data/anthrotrace_common_prompts.yaml")
    prompts = load_prompts_with_categories(yaml_path)
    unittest.main() 