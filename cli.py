import argparse


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run room/student analytics queries or manage PostgreSQL indexes."
    )
    command_group = parser.add_mutually_exclusive_group(required=True)
    command_group.add_argument(
        "--query",
        choices=QUERY_CHOICES,
        help="Analytics query to run.",
    )
    command_group.add_argument(
        "--indexes",
        choices=("add", "remove"),
        help="Add or remove database indexes.",
    )

    parser.add_argument(
        "--index",
        default="all",
        choices=INDEX_CHOICES,
        help="Index target for --indexes. Defaults to all.",
    )
    parser.add_argument(
        "--format",
        choices=("json", "xml"),
        help="Output format for query results.",
    )
    parser.add_argument(
        "--students",
        default="data/students.json",
        help="Path to the students JSON file. Defaults to data/students.json.",
    )
    parser.add_argument(
        "--rooms",
        default="data/rooms.json",
        help="Path to the rooms JSON file. Defaults to data/rooms.json.",
    )
    parser.add_argument(
        "--output-root",
        default="output/runs",
        help="Folder where command logs and results are saved.",
    )
    parser.add_argument(
        "--explain",
        action="store_true",
        help="Save EXPLAIN ANALYZE output for query commands.",
    )
    parser.add_argument(
        "--skip-load",
        action="store_true",
        help="Skip loading JSON data before running a query.",
    )

    args = parser.parse_args()

    if args.query and not args.format:
        parser.error("--format is required when using --query.")

    if args.indexes and args.format:
        parser.error("--format can only be used with --query.")

    if args.indexes and args.explain:
        parser.error("--explain can only be used with --query.")

    if args.indexes and args.skip_load:
        parser.error("--skip-load can only be used with --query.")

    if args.query and args.index != "all":
        parser.error("--index can only be used with --indexes.")

    return args
