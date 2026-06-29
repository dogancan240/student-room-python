# Student Room Database Practice

Python script for loading `rooms` and `students` JSON files into PostgreSQL and exporting the required SQL query results as JSON or XML.

## What It Does

- Creates the `rooms` and `students` tables.
- Loads rooms and students from JSON files.
- Runs all required analytics in SQL:
  - rooms with student counts
  - 5 rooms with the smallest average student age
  - 5 rooms with the largest student age difference
  - rooms where students of different sexes live
- Exports results to JSON or XML.
- Provides SQL files for index experiments and `EXPLAIN` plans.

## Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install "psycopg[binary]" python-dotenv
```

Create a PostgreSQL database, then add a `.env` file:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=student_rooms
DB_USER=postgres
DB_PASSWORD=your_password
```

## Run The App

Export JSON:

```powershell
python main.py --students data/students.json --rooms data/rooms.json --format json --output output/results.json
```

Export XML:

```powershell
python main.py --students data/students.json --rooms data/rooms.json --format xml --output output/results.xml
```

If `--output` is omitted, the default path is `output/results.<format>`.

## Index Experiments

The recommended indexes are in `index_experiments/indexes.sql`. The explain-plan queries are in `index_experiments/explain_queries.sql`.

Create folders for saved benchmark artifacts:

```powershell
New-Item -ItemType Directory -Force output\explain_plans
New-Item -ItemType Directory -Force output\benchmark_results
```

Use your own PostgreSQL connection values in the examples below.

Run a baseline without custom indexes:

```powershell
psql -h localhost -U postgres -d student_rooms -c "DROP INDEX IF EXISTS idx_students_room_id; DROP INDEX IF EXISTS idx_students_room_id_birthday; DROP INDEX IF EXISTS idx_students_room_id_sex;"
psql -h localhost -U postgres -d student_rooms -f index_experiments/explain_queries.sql -o output/explain_plans/00_without_indexes.txt
```

Try `students(room_id)`:

```powershell
psql -h localhost -U postgres -d student_rooms -c "DROP INDEX IF EXISTS idx_students_room_id; DROP INDEX IF EXISTS idx_students_room_id_birthday; DROP INDEX IF EXISTS idx_students_room_id_sex;"
psql -h localhost -U postgres -d student_rooms -c "CREATE INDEX IF NOT EXISTS idx_students_room_id ON students(room_id);"
psql -h localhost -U postgres -d student_rooms -f index_experiments/explain_queries.sql -o output/explain_plans/01_room_id_index.txt
```

Try `students(room_id, birthday)`:

```powershell
psql -h localhost -U postgres -d student_rooms -c "DROP INDEX IF EXISTS idx_students_room_id; DROP INDEX IF EXISTS idx_students_room_id_birthday; DROP INDEX IF EXISTS idx_students_room_id_sex;"
psql -h localhost -U postgres -d student_rooms -c "CREATE INDEX IF NOT EXISTS idx_students_room_id_birthday ON students(room_id, birthday);"
psql -h localhost -U postgres -d student_rooms -f index_experiments/explain_queries.sql -o output/explain_plans/02_room_id_birthday_index.txt
```

Try `students(room_id, sex)`:

```powershell
psql -h localhost -U postgres -d student_rooms -c "DROP INDEX IF EXISTS idx_students_room_id; DROP INDEX IF EXISTS idx_students_room_id_birthday; DROP INDEX IF EXISTS idx_students_room_id_sex;"
psql -h localhost -U postgres -d student_rooms -c "CREATE INDEX IF NOT EXISTS idx_students_room_id_sex ON students(room_id, sex);"
psql -h localhost -U postgres -d student_rooms -f index_experiments/explain_queries.sql -o output/explain_plans/03_room_id_sex_index.txt
```

Apply all recommended indexes:

```powershell
psql -h localhost -U postgres -d student_rooms -f index_experiments/indexes.sql
psql -h localhost -U postgres -d student_rooms -f index_experiments/explain_queries.sql -o output/explain_plans/04_all_indexes.txt
```

Save benchmark notes in `output/benchmark_results/`, for example:

```powershell
@"
Baseline: check output/explain_plans/00_without_indexes.txt
room_id index: check output/explain_plans/01_room_id_index.txt
room_id_birthday index: check output/explain_plans/02_room_id_birthday_index.txt
room_id_sex index: check output/explain_plans/03_room_id_sex_index.txt
all indexes: check output/explain_plans/04_all_indexes.txt
"@ | Set-Content output\benchmark_results\summary.txt
```

## Assignment Notes

- All math is done in SQL inside PostgreSQL.
- The project uses raw SQL with `psycopg`; no ORM is used.
- The current folder is not initialized as a git repository. Before submission, push the completed task to a public Git repository.
- The final assignment reply should include a link to that public Git repository.
