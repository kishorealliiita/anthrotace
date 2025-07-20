import unittest
from anthrotrace.core.clickhouse_prompt_log_repository import ClickHousePromptLogRepository

class DummyClickHouseClient:
    def command(self, *args, **kwargs):
        pass
    def query(self, *args, **kwargs):
        class Result:
            result_rows = []
        return Result()

class TestClickHousePromptLogRepository(unittest.TestCase):
    def test_can_instantiate(self):
        repo = ClickHousePromptLogRepository(clickhouse_client=DummyClickHouseClient())
        self.assertIsInstance(repo, ClickHousePromptLogRepository)

if __name__ == '__main__':
    unittest.main() 