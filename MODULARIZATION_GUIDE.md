# Modularization Guide

## Current State Analysis

You already started the right structure:

- `cli.py` exists, but it is empty.
- `app.py` exists, but it is empty.
- `services/queries/` exists, but all query SQL files are empty.
- `services/indexes/` exists, but all index SQL files are empty.
- `services/log_services.py` exists, but it only has a planning comment.
- `services/index_services.py` exists, but it is empty.
- `main.py` still contains the old argument parsing and the old full application flow.
- `services/query_service.py` still keeps SQL inside Python methods.
- `index_experiments/indexes.sql` and `index_experiments/explain_queries.sql` still contain useful SQL that can be reused.

The next goal is to connect the structure you created so every part has one clear job.

## Target CLI

Use the command line as the main user interface.

Recommended commands:

```powershell
python main.py --query room_student_counts --format json
python main.py --query smallest_average_age --format xml
python main.py --query largest_age_difference --format json
python main.py --query mixed_sex_rooms --format json
python main.py --query all --format json
```

For indexes:

```powershell
python main.py --indexes add --index all
python main.py --indexes remove --index all
python main.py --indexes add --index room_id
python main.py --indexes remove --index room_id_sex
```

Optional, but useful:

```powershell
python main.py --query room_student_counts --format json --explain
```

Rules:

- `--query` and `--indexes` should not be used together.
- `--query` requires `--format`.
- `--indexes` does not require `--format`.
- `--index` should default to `all`.
- `--students` and `--rooms` can stay optional with defaults: `data/students.json` and `data/rooms.json`.

## Recommended Final Structure

```text
student-room-python-practice/
  main.py
  cli.py
  app.py
  config.py

  database/
    connection.py
    init_db.py
    loader.py
    schema.sql

  services/
    export_service.py
    query_service.py
    index_service.py
    log_service.py

    queries/
      room_student_counts.sql
      smallest_average_age.sql
      largest_age_difference.sql
      mixed_sex_rooms.sql

    indexes/
      index_student_room_id.sql
      index_student_room_id_birthday.sql
      index_student_room_id_sex.sql
      remove_index_student_room_id.sql
      remove_index_student_room_id_birthday.sql
      remove_index_student_room_id_sex.sql

  output/
    runs/
      2026-06-30_14-30-10_room_student_counts/
        command.txt
        app.log
        query.sql
        result.json
        metadata.json
        explain.txt
```

Recommended naming cleanup:

- Rename `services/index_services.py` to `services/index_service.py`.
- Rename `services/log_services.py` to `services/log_service.py`.

This matches the existing style: `query_service.py`, `export_service.py`.

## Step 1: Make `main.py` Small

`main.py` should only start the application.

Target responsibility:

```python
from app import run_app
from cli import parse_args


def main() -> None:
    args = parse_args()
    run_app(args)


if __name__ == "__main__":
    main()
```

Do not keep query SQL, export logic, index logic, or loading logic in `main.py`.

## Step 2: Build `cli.py`

Move all `argparse` code into `cli.py`.

Recommended arguments:

- `--query`
- `--format`
- `--indexes`
- `--index`
- `--students`
- `--rooms`
- `--output-root`
- `--explain`

Recommended choices:

```python
QUERY_CHOICES = (
    "room_student_counts",
    "smallest_average_age",
    "largest_age_difference",
    "mixed_sex_rooms",
    "all",
)

INDEX_CHOICES = (
    "room_id",
    "room_id_birthday",
    "room_id_sex",
    "all",
)
```

Validation rules to add in `cli.py`:

- If neither `--query` nor `--indexes` is provided, show an error.
- If both `--query` and `--indexes` are provided, show an error.
- If `--query` is provided without `--format`, show an error.
- If `--indexes` is provided, allow only `add` or `remove`.

## Step 3: Use `app.py` As The Orchestrator

`app.py` should decide what the user wanted to do.

High-level flow:

```text
create run folder
save command.txt
initialize database
load rooms and students

if user selected query:
    run selected query or all queries
    export result
    save metadata
    optionally save EXPLAIN result

if user selected indexes:
    add or remove selected index SQL files
    save metadata
```

Keep `app.py` readable. It should coordinate services, not contain SQL or XML/JSON formatting details.

## Step 4: Fill `services/queries/*.sql`

Move SQL out of `services/query_service.py` and into these files.

`services/queries/room_student_counts.sql`:

```sql
SELECT
    r.id AS room_id,
    r.name AS room_name,
    COUNT(s.id) AS student_count
FROM rooms r
LEFT JOIN students s ON r.id = s.room_id
GROUP BY r.id, r.name
ORDER BY r.id;
```

`services/queries/smallest_average_age.sql`:

```sql
SELECT
    r.id AS room_id,
    r.name AS room_name,
    ROUND(AVG((CURRENT_DATE - s.birthday) / 365.25)::numeric, 2)::float AS average_age
FROM rooms r
JOIN students s ON r.id = s.room_id
GROUP BY r.id, r.name
ORDER BY average_age ASC, r.id
LIMIT 5;
```

`services/queries/largest_age_difference.sql`:

```sql
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
LIMIT 5;
```

`services/queries/mixed_sex_rooms.sql`:

```sql
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
```

## Step 5: Rewrite `QueryService`

`QueryService` should load SQL files and execute them.

Recommended responsibilities:

- Know the query name to SQL file mapping.
- Read SQL from `services/queries/`.
- Execute one query.
- Execute all queries.
- Convert rows into `list[dict]`.
- Optionally run `EXPLAIN (ANALYZE, BUFFERS)` for a query.

Recommended mapping:

```python
QUERY_FILES = {
    "room_student_counts": "room_student_counts.sql",
    "smallest_average_age": "smallest_average_age.sql",
    "largest_age_difference": "largest_age_difference.sql",
    "mixed_sex_rooms": "mixed_sex_rooms.sql",
}
```

Recommended public methods:

```python
run_query(query_name: str) -> list[dict]
run_all_queries() -> dict[str, list[dict]]
get_sql(query_name: str) -> str
explain_query(query_name: str) -> str
```

Important detail:

- Do not keep four separate methods like `get_room_student_counts()` forever.
- A modular service should let the CLI choose the query by name.

## Step 6: Fill `services/indexes/*.sql`

Use the SQL from `index_experiments/indexes.sql`.

`services/indexes/index_student_room_id.sql`:

```sql
CREATE INDEX IF NOT EXISTS idx_students_room_id
ON students(room_id);
```

`services/indexes/index_student_room_id_birthday.sql`:

```sql
CREATE INDEX IF NOT EXISTS idx_students_room_id_birthday
ON students(room_id, birthday);
```

`services/indexes/index_student_room_id_sex.sql`:

```sql
CREATE INDEX IF NOT EXISTS idx_students_room_id_sex
ON students(room_id, sex);
```

`services/indexes/remove_index_student_room_id.sql`:

```sql
DROP INDEX IF EXISTS idx_students_room_id;
```

`services/indexes/remove_index_student_room_id_birthday.sql`:

```sql
DROP INDEX IF EXISTS idx_students_room_id_birthday;
```

`services/indexes/remove_index_student_room_id_sex.sql`:

```sql
DROP INDEX IF EXISTS idx_students_room_id_sex;
```

## Step 7: Build `IndexService`

`IndexService` should work like `QueryService`, but for index SQL files.

Recommended mapping:

```python
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
```

Recommended public methods:

```python
apply_index(index_name: str) -> list[str]
remove_index(index_name: str) -> list[str]
apply_all_indexes() -> list[str]
remove_all_indexes() -> list[str]
```

Return the SQL strings that were executed so `LogService` can save them.

## Step 8: Build `LogService`

Your `log_service` should make the output folder more detailed.

Recommended run folder:

```text
output/runs/<timestamp>_<action_name>/
```

Examples:

```text
output/runs/2026-06-30_14-30-10_room_student_counts/
output/runs/2026-06-30_14-31-20_indexes_add_all/
output/runs/2026-06-30_14-32-05_mixed_sex_rooms_explain/
```

Files to save for query commands:

- `command.txt`: command that was run.
- `query.sql`: SQL query that was executed.
- `result.json` or `result.xml`: exported query result.
- `metadata.json`: timestamp, query name, format, row count, output path.
- `app.log`: readable summary.
- `explain.txt`: only when `--explain` is used.

Files to save for index commands:

- `command.txt`: command that was run.
- `indexes.sql`: index SQL that was executed.
- `metadata.json`: timestamp, index action, selected index name.
- `app.log`: readable summary.

Recommended public methods:

```python
create_run_folder(action_name: str) -> Path
save_command(run_folder: Path, command: list[str]) -> None
save_sql(run_folder: Path, filename: str, sql: str) -> None
save_metadata(run_folder: Path, metadata: dict) -> None
save_log(run_folder: Path, message: str) -> None
```

Use `sys.argv` in `app.py` to save the real command:

```python
" ".join(sys.argv)
```

## Step 9: Adjust `ExportService`

Keep JSON and XML export logic, but make it work with the run folder.

Recommended behavior:

- If query is `room_student_counts` and format is `json`, save `result.json`.
- If query is `all` and format is `json`, save one `result.json` containing all query results.
- If query is `all` and format is `xml`, save one `result.xml` containing all query results.

Do not make `ExportService` create metadata or command logs. That belongs to `LogService`.

## Step 10: Improve Database Loading

Keep current behavior first. After everything works, improve it.

Current behavior:

- `init_database()` runs every time.
- `load_rooms()` runs every time.
- `load_students()` runs every time.
- Inserts use `ON CONFLICT (id) DO NOTHING`.

This is acceptable for now.

Later improvement:

- Add `--skip-load` if you want to run queries without reloading JSON files.
- Use `executemany()` in `database/loader.py` instead of one insert per loop.

## Step 11: Update README

After implementation, update README examples.

Add a section like:

```markdown
## Query Commands

python main.py --query room_student_counts --format json
python main.py --query all --format xml

## Index Commands

python main.py --indexes add --index all
python main.py --indexes remove --index room_id_sex

## Output Logs

Each command creates a folder under output/runs/.
```

## Implementation Order

Follow this order so each step is small and testable:

1. Fill the empty query SQL files.
2. Fill the empty index SQL files.
3. Move argument parsing from `main.py` into `cli.py`.
4. Make `main.py` tiny.
5. Rewrite `QueryService` to load SQL files.
6. Create `IndexService`.
7. Create `LogService`.
8. Create `app.py` orchestration.
9. Adjust `ExportService` only if needed.
10. Update README.
11. Test commands manually.

## Manual Test Checklist

Run these after the refactor:

```powershell
python main.py --query room_student_counts --format json
python main.py --query smallest_average_age --format xml
python main.py --query all --format json
python main.py --indexes add --index all
python main.py --indexes remove --index all
python main.py --query room_student_counts --format json --explain
```

Check that each command creates a new folder inside:

```text
output/runs/
```

For query commands, check:

- `command.txt` exists.
- `query.sql` exists.
- `result.json` or `result.xml` exists.
- `metadata.json` exists.
- `app.log` exists.

For index commands, check:

- `command.txt` exists.
- `indexes.sql` exists.
- `metadata.json` exists.
- `app.log` exists.

## Main Design Rule

Each file should have one clear job:

- `main.py`: start the app.
- `cli.py`: parse command-line arguments.
- `app.py`: coordinate the application flow.
- `query_service.py`: run SQL analytics queries.
- `index_service.py`: add or remove database indexes.
- `export_service.py`: write JSON or XML results.
- `log_service.py`: save command history, SQL, metadata, and logs.
- `database/`: connection, schema creation, and data loading.

