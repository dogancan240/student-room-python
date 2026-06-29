from pathlib import Path

from database.connection import get_connection


def init_database() -> None:
    schema_path = Path(__file__).with_name("schema.sql")
    schema_sql = schema_path.read_text(encoding="utf-8")

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(schema_sql)

        connection.commit()


if __name__ == "__main__":
    init_database()
    print("Database tables created successfully.")