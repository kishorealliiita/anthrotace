import clickhouse_connect
from repository.clickhouse_prompt_log_repository import ClickHousePromptLogRepository
import argparse
import json
from datetime import datetime


def generate_metrics_report(output_format="table", filter_category=None, since=None, until=None):
    client = clickhouse_connect.get_client(host='localhost', port=8123)
    repo = ClickHousePromptLogRepository(clickhouse_client=client)
    stats = repo.get_aggregated_stats()

    if filter_category:
        stats = [row for row in stats if row[0] == filter_category]

    if since or until:
        def in_date_range(row):
            timestamp = row[4] if len(row) > 4 else None  # assuming timestamp is at index 4 if present
            if timestamp:
                if since and timestamp < since:
                    return False
                if until and timestamp > until:
                    return False
            return True

        stats = [row for row in stats if in_date_range(row)]

    if output_format == "table":
        print("Category           | Total Tokens | Total Cost (USD) | Avg Duration (s)")
        print("-------------------|--------------|-------------------|-----------------")
        for category, total_tokens, total_cost, avg_duration in stats:
            print(f"{category:<19} | {total_tokens:<12} | {total_cost:<17} | {avg_duration:<15}")

        # Summary totals
        total_tokens_sum = sum(row[1] for row in stats)
        total_cost_sum = round(sum(row[2] for row in stats), 5)
        avg_duration_avg = round(sum(row[3] for row in stats) / len(stats), 2) if stats else 0
        print(f"\n[SUMMARY] Total Tokens: {total_tokens_sum} | Total Cost (USD): {total_cost_sum} | Avg Duration (s): {avg_duration_avg}")

    elif output_format == "json":
        json_output = [
            {
                "category": category,
                "total_tokens": total_tokens,
                "total_cost_usd": total_cost,
                "avg_duration_seconds": avg_duration
            }
            for category, total_tokens, total_cost, avg_duration in stats
        ]
        summary = {
            "total_tokens_sum": sum(row[1] for row in stats),
            "total_cost_usd_sum": round(sum(row[2] for row in stats), 5),
            "avg_duration_seconds_avg": round(sum(row[3] for row in stats) / len(stats), 2) if stats else 0
        }
        print(json.dumps({"data": json_output, "summary": summary}, indent=2))
    else:
        print(f"Unsupported format: {output_format}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate metrics report from ClickHouse")
    parser.add_argument("--format", choices=["table", "json"], default="table", help="Output format")
    parser.add_argument("--category", type=str, help="Filter by category")
    parser.add_argument("--since", type=lambda s: datetime.strptime(s, '%Y-%m-%d'), help="Filter records since this date (YYYY-MM-DD)")
    parser.add_argument("--until", type=lambda s: datetime.strptime(s, '%Y-%m-%d'), help="Filter records until this date (YYYY-MM-DD)")
    args = parser.parse_args()

    generate_metrics_report(output_format=args.format, filter_category=args.category, since=args.since, until=args.until)