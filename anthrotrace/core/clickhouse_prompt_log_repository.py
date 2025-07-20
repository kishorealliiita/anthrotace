class ClickHousePromptLogRepository:
    def __init__(self, clickhouse_client=None):
        self.client = clickhouse_client
        if not self.client:
            raise NotImplementedError("ClickHouse client is required.")
        self._create_table_if_not_exists()
    
    def _create_table_if_not_exists(self):
        """Create the prompt_logs table if it doesn't exist"""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS prompt_logs (
            id UInt32,
            category String,
            model String,
            prompt_text String,
            response String,
            input_tokens UInt32,
            output_tokens UInt32,
            duration Float64,
            cost Float64,
            timestamp DateTime64(3, 'UTC') DEFAULT now()
        ) ENGINE = MergeTree()
        ORDER BY (timestamp, category)
        """
        try:
            self.client.command(create_table_query)
        except Exception as e:
            print(f"[ClickHouse] Warning: Could not create table: {e}")
    
    def insert_log(self, category, model, prompt_text, response, input_tokens, output_tokens, duration, cost=0):
        query = """
        INSERT INTO prompt_logs (category, model, prompt_text, response, input_tokens, output_tokens, duration, cost, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """
        try:
            self.client.command(query, parameters=[
                category,
                model,
                prompt_text,
                response,
                input_tokens,
                output_tokens,
                duration,
                cost
            ])
        except Exception as e:
            print(f"[ClickHouse] Insert Error: {e}")
    
    def fetch_logs(self, category=None, model=None, start_time=None, end_time=None, limit=100):
        conditions = []
        params = []

        if category:
            conditions.append("category = %s")
            params.append(category)
        if model:
            conditions.append("model = %s")
            params.append(model)
        if start_time:
            conditions.append("timestamp >= %s")
            params.append(start_time)
        if end_time:
            conditions.append("timestamp <= %s")
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
            rows = self.client.query(query, parameters=params).result_rows
            columns = ["category", "model", "prompt_text", "response", "input_tokens", "output_tokens", "duration", "cost", "timestamp"]
            return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            print(f"[ClickHouse] Fetch Error: {e}")
            return []


    def get_aggregated_stats(self, start_time=None, end_time=None):
        conditions = []
        params = []
        
        if start_time:
            conditions.append("timestamp >= %s")
            params.append(start_time)
        if end_time:
            conditions.append("timestamp <= %s")
            params.append(end_time)
        
        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        query = f"""
        SELECT 
            category,
            SUM(input_tokens + output_tokens) as total_tokens,
            ROUND(SUM(cost), 5) as total_cost,
            ROUND(AVG(duration), 2) as avg_duration
        FROM prompt_logs
        {where_clause}
        GROUP BY category
        """
        try:
            return self.client.query(query, parameters=params).result_rows
        except Exception as e:
            print(f"[ClickHouse] Aggregated Stats Error: {e}")
            return []
    
    def convert_logs_to_metrics(self, exporter):
        stats = self.get_aggregated_stats()
        
        # Define histogram buckets
        duration_buckets = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
        token_buckets = [100, 500, 1000, 2000, 5000, 10000]
        
        for stat in stats:
            category, total_tokens, total_cost, avg_duration = stat
            labels = {'category': category}
            
            try:
                exporter.emit_metric("prompt_total_tokens", total_tokens, labels, metric_type="counter")
                exporter.emit_metric("prompt_total_cost_usd", total_cost, labels, metric_type="counter")
                exporter.emit_metric("prompt_avg_duration_seconds", avg_duration, labels, metric_type="gauge")
                exporter.emit_histogram("prompt_duration_seconds", avg_duration, duration_buckets, labels)
                exporter.emit_histogram("prompt_total_tokens_histogram", total_tokens, token_buckets, labels)
            except Exception as e:
                print(f"[ClickHouse] Metric Emit Error for {category}: {e}")
        
        print(f"[METRICS] Emitted {len(stats)} metric sets from ClickHouse")
    
    def get_all_logs(self):
    # Return last 100 logs without filters (default behavior)
        return self.fetch_logs(limit=100)

