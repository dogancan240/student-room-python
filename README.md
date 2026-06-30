# Student Room Database Practice

Python command-line app for loading `rooms` and `students` JSON files into PostgreSQL, running room analytics queries, managing helpful indexes, and saving detailed command output logs.

## What It Does

- Creates the `rooms` and `students` tables.
- Loads rooms and students from JSON files only when database data is missing.
- Runs one selected analytics query or all analytics queries.
- Exports query results as JSON or XML.
- Adds or removes recommended PostgreSQL indexes from the CLI.
- Saves every command result under `output/runs/` with command text, SQL, metadata, and logs.

## Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Create a PostgreSQL database, then add a `.env` file:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=student_rooms
DB_USER=postgres
DB_PASSWORD=your_password
```

## Query Commands

Run one query:

```powershell
python main.py --query room_student_counts --format json
python main.py --query smallest_average_age --format xml
python main.py --query largest_age_difference --format json
python main.py --query mixed_sex_rooms --format json
```

Run all queries:

```powershell
python main.py --query all --format json
python main.py --query all --format xml
```

Save an `EXPLAIN (ANALYZE, BUFFERS)` result too:

```powershell
python main.py --query room_student_counts --format json --explain
```

Available query names:

```text
room_student_counts
smallest_average_age
largest_age_difference
mixed_sex_rooms
all
```

By default, query commands load these files only when database data is missing:

```text
data/rooms.json
data/students.json
```

You can override those paths:

```powershell
python main.py --query all --format json --rooms data/rooms.json --students data/students.json
```

Query commands automatically skip loading when data already exists. To skip even the empty-table check:

```powershell
python main.py --query all --format json --skip-load
```

## Index Commands

Add all recommended indexes:

```powershell
python main.py --indexes add --index all
```

Remove all recommended indexes:

```powershell
python main.py --indexes remove --index all
```

Manage one index:

```powershell
python main.py --indexes add --index room_id
python main.py --indexes add --index room_id_birthday
python main.py --indexes add --index room_id_sex
python main.py --indexes remove --index room_id_sex
```

Available index names:

```text
room_id
room_id_birthday
room_id_sex
all
```

## Output Logs

Each command creates a new folder under:

```text
output/runs/
```

Example query output:

```text
output/runs/2026-06-30_14-30-10_room_student_counts_json/
  command.txt
  app.log
  query.sql
  result.json
  metadata.json
  explain.txt
```

Example index output:

```text
output/runs/2026-06-30_14-35-20_indexes_add_all/
  command.txt
  app.log
  indexes.sql
  metadata.json
```

## Project Structure

```text
main.py                  # starts the app
cli.py                   # parses command-line arguments
app.py                   # coordinates query/index commands
config.py                # loads database settings

database/
  connection.py          # PostgreSQL connection context manager
  init_db.py             # creates tables from schema.sql
  loader.py              # loads JSON data
  schema.sql             # database schema

services/
  export_service.py      # writes JSON/XML
  query_service.py       # runs SQL query files
  index_service.py       # adds/removes index SQL files
  log_service.py         # saves command logs and metadata
  queries/               # analytics SQL files
  indexes/               # index SQL files
```

## Assignment Notes

- All analytics math is done in SQL inside PostgreSQL.
- The project uses raw SQL with `psycopg`; no ORM is used.
- `index_experiments/` still contains standalone SQL files for manual index experiments and explain-plan comparisons.
