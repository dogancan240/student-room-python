from database.connection import get_connection


class QueryService:
    def get_room_student_counts(self) -> list[dict]:
        query = """
            SELECT
                r.id AS room_id,
                r.name AS room_name,
                COUNT(s.id) AS student_count
            FROM rooms r
            LEFT JOIN students s ON r.id = s.room_id
            GROUP BY r.id, r.name
            ORDER BY r.id;
        """

        return self._fetch_all(query)

    def get_rooms_with_smallest_average_age(self, limit: int = 5) -> list[dict]:
        query = """
            SELECT
                r.id AS room_id,
                r.name AS room_name,
                ROUND(AVG((CURRENT_DATE - s.birthday) / 365.25)::numeric, 2)::float AS average_age
            FROM rooms r
            JOIN students s ON r.id = s.room_id
            GROUP BY r.id, r.name
            ORDER BY average_age ASC, r.id
            LIMIT %s;
        """

        return self._fetch_all(query, (limit,))

    def get_rooms_with_largest_age_difference(self, limit: int = 5) -> list[dict]:
        query = """
            SELECT
                r.id AS room_id,
                r.name AS room_name,
                ROUND(
                    ((MAX(CURRENT_DATE - s.birthday) - MIN(CURRENT_DATE - s.birthday)) / 365.25)::numeric,
                    2
                )::float AS age_difference
            FROM rooms r
            JOIN students s ON r.id = s.room_id
            GROUP BY r.id, r.name
            HAVING COUNT(s.id) > 1
            ORDER BY age_difference DESC, r.id
            LIMIT %s;
        """

        return self._fetch_all(query, (limit,))

    def get_mixed_sex_rooms(self) -> list[dict]:
        query = """
            SELECT
                r.id AS room_id,
                r.name AS room_name,
                COUNT(s.id) AS student_count,
                COUNT(DISTINCT s.sex) AS sex_count
            FROM rooms r
            JOIN students s ON r.id = s.room_id
            GROUP BY r.id, r.name
            HAVING COUNT(DISTINCT s.sex) > 1
            ORDER BY r.id;
        """

        return self._fetch_all(query)

    def _fetch_all(self, query: str, params: tuple | None = None) -> list[dict]:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()

        return [dict(zip(columns, row)) for row in rows]
