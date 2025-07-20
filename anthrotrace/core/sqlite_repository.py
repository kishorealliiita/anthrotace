import sqlite3

class SQLiteRepository:
    def __init__(self, db_path="data/prompt_logs.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_table_if_not_exists()

    def _create_table_if_not_exists(self):
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS prompt_logs (
            category TEXT NOT NULL,
            model TEXT NOT NULL,
            prompt_text TEXT NOT NULL,
            response TEXT,
            input_tokens INTEGER,
            output_tokens INTEGER,
            duration REAL,
            cost REAL,
            timestamp TEXT NOT NULL
        );
        """
        self.conn.execute(create_table_sql)
        self.conn.commit()

    def insert_log(self, category, model, prompt_text, response, input_tokens, output_tokens, duration, cost=0.0, timestamp=None):
        insert_sql = """
        INSERT INTO prompt_logs (category, model, prompt_text, response, input_tokens, output_tokens, duration, cost, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        self.conn.execute(insert_sql, (category, model, prompt_text, response, input_tokens, output_tokens, duration, cost, timestamp))
        self.conn.commit()

    def fetch_logs(self, category=None, model=None, start_time=None, end_time=None, limit=100):
        conditions = []
        params = []

        if category:
            conditions.append("category = ?")
            params.append(category)
        if model:
            conditions.append("model = ?")
            params.append(model)
        if start_time:
            conditions.append("timestamp >= ?")
            params.append(start_time)
        if end_time:
            conditions.append("timestamp <= ?")
            params.append(end_time)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        query = f"""
        SELECT category, model, prompt_text, response, input_tokens, output_tokens, duration, cost, timestamp
        FROM prompt_logs
        {where_clause}
        ORDER BY timestamp DESC
        LIMIT {limit}
        """
        try:
            cur = self.conn.cursor()
            cur.execute(query, params)
            columns = [col[0] for col in cur.description]
            return [dict(zip(columns, row)) for row in cur.fetchall()]
        except Exception as e:
            print(f"[SQLite] Fetch Error: {e}")
            return []

    def get_all_logs(self):
        return self.fetch_logs(limit=100)
