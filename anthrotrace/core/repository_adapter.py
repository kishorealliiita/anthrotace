class RepositoryAdapter:
    def __init__(self, prompt_log_repository):
        self.repo = prompt_log_repository

    def query_logs(self, category=None, model=None, start_time=None, end_time=None):
        # This passes filters down to the repo (which should apply them correctly)
        try:
            return self.repo.fetch_logs(
                category=category,
                model=model,
                start_time=start_time,
                end_time=end_time
            )
        except AttributeError:
            # For SQLite fallback if fetch_logs() is missing
            return self.repo.get_all_logs()
