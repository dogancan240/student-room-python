from pathlib import Path

from database.connection import get_connection


class IndexService:
    ADD_INDEX_FILES = {
        "room_id": "index_student_room_id.sql",
        "room_id_birthday": "index_student_room_id_birthday.sql",
        "room_id_sex": "index_student_room_id_sex.sql",
    }

    REMOVE_INDEX_FILES = {
        "room_id": "remove_index_student_room_id.sql",
        "room_id_birthday": "remove_index_student_room_id_birthday.sql",
        "room_id_sex": "remove_index_student_room_id_sex.sql",
    }

    def __init__(self, indexes_dir: Path | None = None) -> None:
        self.indexes_dir = indexes_dir or Path(__file__).with_name("indexes")

    def apply_index(self, index_name: str) -> list[str]:
        return self._execute_index_files(self.ADD_INDEX_FILES, index_name)

    def remove_index(self, index_name: str) -> list[str]:
        return self._execute_index_files(self.REMOVE_INDEX_FILES, index_name)

    def apply_all_indexes(self) -> list[str]:
        return self.apply_index("all")

    def remove_all_indexes(self) -> list[str]:
        return self.remove_index("all")

    def run(self, action: str, index_name: str) -> list[str]:
        if action == "add":
            return self.apply_index(index_name)
        if action == "remove":
            return self.remove_index(index_name)

        raise ValueError("Index action must be 'add' or 'remove'.")

    def _execute_index_files(
        self,
        index_files: dict[str, str],
        index_name: str,
    ) -> list[str]:
        selected_names = self._get_selected_index_names(index_files, index_name)
        executed_sql: list[str] = []

        with get_connection() as connection:
            with connection.cursor() as cursor:
                for selected_name in selected_names:
                    sql = self._read_index_sql(index_files[selected_name])
                    cursor.execute(sql)
                    executed_sql.append(sql)

            connection.commit()

        return executed_sql

    def _get_selected_index_names(
        self,
        index_files: dict[str, str],
        index_name: str,
    ) -> tuple[str, ...]:
        if index_name == "all":
            return tuple(index_files)

        if index_name not in index_files:
            available = ", ".join((*index_files.keys(), "all"))
            raise ValueError(
                f"Unknown index '{index_name}'. Available indexes: {available}."
            )

        return (index_name,)

    def _read_index_sql(self, filename: str) -> str:
        index_path = self.indexes_dir / filename
        sql = index_path.read_text(encoding="utf-8").strip()

        if not sql:
            raise ValueError(f"Index file is empty: {index_path}")

        return sql
