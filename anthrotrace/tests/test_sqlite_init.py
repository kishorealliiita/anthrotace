import unittest
import tempfile
import os
from anthrotrace.core.sqlite_init import initialize_db

class TestSQLiteInit(unittest.TestCase):
    def test_initialize_db(self):
        db_fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(db_fd)
        try:
            # Patch DB_PATH for the test
            import anthrotrace.core.sqlite_init as sqlite_init_mod
            old_db_path = sqlite_init_mod.DB_PATH
            sqlite_init_mod.DB_PATH = db_path
            initialize_db()
            self.assertTrue(os.path.exists(db_path))
            sqlite_init_mod.DB_PATH = old_db_path
        finally:
            os.unlink(db_path)

if __name__ == '__main__':
    unittest.main() 