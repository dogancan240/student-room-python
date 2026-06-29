import argparse

from database.init_db import init_database
from database.loader import load_rooms, load_students
from services.query_service import QueryService
from services.export_service import ExportService


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Load rooms and students into PostgreSQL and export required query results."
    )
    parser.add_argument(
        "--students",
        required=True,
        help="Path to the students JSON file.",
    )
    parser.add_argument(
        "--rooms",
        required=True,
        help="Path to the rooms JSON file.",
    )
    parser.add_argument(
        "--format",
        required=True,
        choices=("json", "xml"),
        help="Output format.",
    )
    parser.add_argument(
        "--output",
        help="Output file path. Defaults to output/results.<format>.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_path = args.output or f"output/results.{args.format}"

    init_database()
    load_rooms(args.rooms)
    load_students(args.students)

    query_service = QueryService()
    export_service = ExportService()

    results = {
        "room_student_counts": query_service.get_room_student_counts(),
        "smallest_average_age": query_service.get_rooms_with_smallest_average_age(),
        "largest_age_difference": query_service.get_rooms_with_largest_age_difference(),
        "mixed_sex_rooms": query_service.get_mixed_sex_rooms(),
    }

    export_service.export(
        data=results,
        output_format=args.format,
        output_path=output_path,
    )
    print(f"Results exported to {output_path}")


if __name__ == "__main__":
    main()
