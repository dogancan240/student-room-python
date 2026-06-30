from pathlib import Path

from database.connection import get_connection


class QueryService:
    QUERY_FILES = {
        "room_student_counts": "room_student_counts.sql",
        "smallest_average_age": "smallest_average_age.sql",
        "largest_age_difference": "largest_age_difference.sql",
        "mixed_sex_rooms": "mixed_sex_rooms.sql",
    }

    def __init__(self, queries_dir: Path | None = None) -> None:
        self.queries_dir = queries_dir or Path(__file__).with_name("queries")

    def available_queries(self) -> tuple[str, ...]:
        return tuple(self.QUERY_FILES)

    def run_query(self, query_name: str) -> list[dict]:
        query = self.get_sql(query_name)
        return self._fetch_all(query)

    def run_all_queries(self) -> dict[str, list[dict]]:
        return {
            query_name: self.run_query(query_name)
            for query_name in self.available_queries()
        }

    def get_sql(self, query_name: str) -> str:
        self._validate_query_name(query_name)
        query_path = self.queries_dir / self.QUERY_FILES[query_name]
        query = query_path.read_text(encoding="utf-8").strip()

        if not query:
            raise ValueError(f"Query file is empty: {query_path}")

        return query

    def explain_query(self, query_name: str) -> str:
        query = self.get_sql(query_name).rstrip(";")
        explain_query = f"EXPLAIN (ANALYZE, BUFFERS)\n{query};"

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(explain_query)
                rows = cursor.fetchall()

        return "\n".join(row[0] for row in rows)

    def _validate_query_name(self, query_name: str) -> None:
        if query_name not in self.QUERY_FILES:
            available = ", ".join(self.available_queries())
            raise ValueError(
                f"Unknown query '{query_name}'. Available queries: {available}."
            )

    def _fetch_all(self, query: str) -> list[dict]:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()

        return [dict(zip(columns, row)) for row in rows]
