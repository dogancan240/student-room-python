import json
from datetime import date, datetime
from pathlib import Path

from database.connection import get_connection


def load_json_file(file_path: str) -> list[dict]:
    path = Path(file_path)

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


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
