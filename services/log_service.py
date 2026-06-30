import json
import re
from datetime import datetime
from pathlib import Path


class LogService:
    def __init__(self, output_root: str = "output/runs") -> None:
        self.output_root = Path(output_root)

    def create_run_folder(self, action_name: str) -> Path:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        safe_action_name = self._safe_filename(action_name)
        run_folder = self.output_root / f"{timestamp}_{safe_action_name}"
        counter = 1

        while run_folder.exists():
            run_folder = self.output_root / (
                f"{timestamp}_{safe_action_name}_{counter}"
            )
            counter += 1

        run_folder.mkdir(parents=True, exist_ok=False)
        return run_folder

    def save_command(self, run_folder: Path, command: list[str] | str) -> None:
        if isinstance(command, list):
            command_text = " ".join(command)
        else:
            command_text = command

        self._write_text(run_folder / "command.txt", command_text)

    def save_sql(self, run_folder: Path, filename: str, sql: str) -> None:
        self._write_text(run_folder / filename, sql)

    def save_metadata(self, run_folder: Path, metadata: dict) -> None:
        metadata_path = run_folder / "metadata.json"

        with metadata_path.open("w", encoding="utf-8") as file:
            json.dump(metadata, file, indent=4, ensure_ascii=False, default=str)

    def save_log(self, run_folder: Path, message: str) -> None:
        timestamp = datetime.now().isoformat(timespec="seconds")
        log_line = f"[{timestamp}] {message}\n"

        with (run_folder / "app.log").open("a", encoding="utf-8") as file:
            file.write(log_line)

    def _write_text(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content.strip() + "\n", encoding="utf-8")

    def _safe_filename(self, value: str) -> str:
        safe_value = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")
        return safe_value or "run"

