import unittest
import tempfile
import os
from anthrotrace.core.sqlite_repository import SQLiteRepository

class TestSQLiteRepository(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        self.repo = SQLiteRepository(db_path=self.db_path)

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_insert_and_fetch(self):
        self.repo.insert_log('cat', 'model', 'prompt', 'resp', 1, 2, 0.5, 0.01, '2024-06-01T00:00:00')
        logs = self.repo.fetch_logs(category='cat')
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]['category'], 'cat')
        self.assertEqual(logs[0]['model'], 'model')
        self.assertEqual(logs[0]['prompt_text'], 'prompt')
        self.assertEqual(logs[0]['response'], 'resp')

    def test_get_all_logs(self):
        self.repo.insert_log('cat', 'model', 'prompt', 'resp', 1, 2, 0.5, 0.01, '2024-06-01T00:00:00')
        logs = self.repo.get_all_logs()
        self.assertEqual(len(logs), 1)

if __name__ == '__main__':
    unittest.main() 