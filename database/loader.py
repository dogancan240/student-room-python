import json
from datetime import date, datetime
from pathlib import Path

from database.connection import get_connection


def load_json_file(file_path: str) -> list[dict]:
    path = Path(file_path)

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_initial_data_if_needed(
    rooms_file_path: str,
    students_file_path: str,
) -> tuple[str, ...]:
    table_status = get_table_data_status()
    loaded_tables = []

    if not table_status["rooms"]:
        load_rooms(rooms_file_path)
        loaded_tables.append("rooms")

    if not table_status["students"]:
        load_students(students_file_path)
        loaded_tables.append("students")

    return tuple(loaded_tables)


def get_table_data_status() -> dict[str, bool]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    EXISTS (SELECT 1 FROM rooms),
                    EXISTS (SELECT 1 FROM students);
                """
            )
            rooms_have_data, students_have_data = cursor.fetchone()

    return {
        "rooms": rooms_have_data,
        "students": students_have_data,
    }


def parse_birthday(value: str) -> date:
    return datetime.fromisoformat(value).date()


def load_rooms(file_path: str) -> None:
    rooms = load_json_file(file_path)

    with get_connection() as connection:
        with connection.cursor() as cursor:
            for room in rooms:
                cursor.execute(
                    """
                    INSERT INTO rooms (id, name)
                    VALUES (%s, %s)
                    ON CONFLICT (id) DO NOTHING;
                    """,
                    (room["id"], room["name"]),
                )

        connection.commit()


def load_students(file_path: str) -> None:
    students = load_json_file(file_path)

    with get_connection() as connection:
        with connection.cursor() as cursor:
            for student in students:
                cursor.execute(
                    """
                    INSERT INTO students (id, name, birthday, sex, room_id)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING;
                    """,
                    (
                        student["id"],
                        student["name"],
                        parse_birthday(student["birthday"]),
                        student["sex"],
                        student["room"],
                    ),
                )

        connection.commit()
