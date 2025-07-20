import unittest
from anthrotrace.core.mock_repository import MockRepository

class TestMockRepository(unittest.TestCase):
    def setUp(self):
        self.repo = MockRepository()

    def test_insert_and_fetch(self):
        self.repo.insert_log('cat', 'prompt', 'resp', 1, 2, 0.5, 0.01)
        logs = self.repo.fetch_logs()
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]['category'], 'cat')
        self.assertEqual(logs[0]['prompt_text'], 'prompt')
        self.assertEqual(logs[0]['response'], 'resp')

    def test_get_all_logs(self):
        self.repo.insert_log('cat', 'prompt', 'resp', 1, 2, 0.5, 0.01)
        logs = self.repo.get_all_logs()
        self.assertEqual(len(logs), 1)

if __name__ == '__main__':
    unittest.main() 