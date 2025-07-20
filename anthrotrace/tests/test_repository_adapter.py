import unittest
from anthrotrace.core.repository_adapter import RepositoryAdapter

class DummyRepo:
    def fetch_logs(self, **kwargs):
        return [{'category': 'A', 'model': 'M1', 'response': 'ok'}]
    def get_all_logs(self):
        return [{'category': 'A', 'model': 'M1', 'response': 'ok'}]

class TestRepositoryAdapter(unittest.TestCase):
    def test_query_logs(self):
        adapter = RepositoryAdapter(DummyRepo())
        logs = adapter.query_logs(category='A')
        self.assertIsInstance(logs, list)
        self.assertEqual(logs[0]['category'], 'A')
        self.assertEqual(logs[0]['model'], 'M1')
        self.assertEqual(logs[0]['response'], 'ok')

if __name__ == '__main__':
    unittest.main() 