import argparse
import sys
from pathlib import Path

from database.init_db import init_database
from database.loader import load_rooms, load_students
from services.export_service import ExportService
from services.index_service import IndexService
from services.log_service import LogService
from services.query_service import QueryService


def run_app(args: argparse.Namespace) -> None:
    log_service = LogService(args.output_root)
    run_folder = log_service.create_run_folder(_get_action_name(args))
    log_service.save_command(run_folder, sys.argv)
    log_service.save_log(run_folder, "Command started.")

    try:
        if args.query:
            _run_query_command(args, run_folder, log_service)
        elif args.indexes:
            _run_index_command(args, run_folder, log_service)
    except Exception as error:
        log_service.save_log(run_folder, f"Command failed: {error}")
        log_service.save_metadata(
            run_folder,
            {
                "status": "failed",
                "error": str(error),
                "run_folder": str(run_folder),
            },
        )
        raise

    log_service.save_log(run_folder, "Command completed.")
    print(f"Run logs saved to {run_folder}")


def _run_query_command(
    args: argparse.Namespace,
    run_folder: Path,
    log_service: LogService,
) -> None:
    init_database()
    log_service.save_log(run_folder, "Database schema initialized.")

    if not args.skip_load:
        load_rooms(args.rooms)
        load_students(args.students)
        log_service.save_log(run_folder, "Rooms and students loaded.")
    else:
        log_service.save_log(run_folder, "Data loading skipped.")

    query_service = QueryService()
    export_service = ExportService()

    if args.query == "all":
        results = query_service.run_all_queries()
        sql_text = _format_named_sql(
            {
                query_name: query_service.get_sql(query_name)
                for query_name in query_service.available_queries()
            }
        )
        row_counts = {
            query_name: len(rows)
            for query_name, rows in results.items()
        }
    else:
        rows = query_service.run_query(args.query)
        results = {args.query: rows}
        sql_text = query_service.get_sql(args.query)
        row_counts = {args.query: len(rows)}

    result_path = run_folder / f"result.{args.format}"
    export_service.export(results, args.format, result_path)
    log_service.save_sql(run_folder, "query.sql", sql_text)

    if args.explain:
        explain_text = _get_explain_text(args.query, query_service)
        log_service.save_sql(run_folder, "explain.txt", explain_text)

    log_service.save_metadata(
        run_folder,
        {
            "status": "success",
            "action": "query",
            "query": args.query,
            "format": args.format,
            "result_path": str(result_path),
            "row_counts": row_counts,
            "explain": args.explain,
            "run_folder": str(run_folder),
        },
    )
    log_service.save_log(run_folder, f"Query result exported to {result_path}.")
    print(f"Results exported to {result_path}")


def _run_index_command(
    args: argparse.Namespace,
    run_folder: Path,
    log_service: LogService,
) -> None:
    init_database()
    log_service.save_log(run_folder, "Database schema initialized.")

    index_service = IndexService()
    executed_sql = index_service.run(args.indexes, args.index)
    sql_text = "\n\n".join(executed_sql)

    log_service.save_sql(run_folder, "indexes.sql", sql_text)
    log_service.save_metadata(
        run_folder,
        {
            "status": "success",
            "action": "indexes",
            "index_action": args.indexes,
            "index": args.index,
            "executed_statement_count": len(executed_sql),
            "run_folder": str(run_folder),
        },
    )
    log_service.save_log(
        run_folder,
        f"Index command '{args.indexes}' completed for '{args.index}'.",
    )
    print(f"Index command completed: {args.indexes} {args.index}")


def _get_action_name(args: argparse.Namespace) -> str:
    if args.query:
        action_name = f"{args.query}_{args.format}"
        if args.explain:
            action_name = f"{action_name}_explain"
        return action_name

    return f"indexes_{args.indexes}_{args.index}"


def _format_named_sql(sql_by_name: dict[str, str]) -> str:
    sections = []

    for query_name, sql in sql_by_name.items():
        sections.append(f"-- {query_name}\n{sql.strip()}")

    return "\n\n".join(sections)


def _get_explain_text(query_name: str, query_service: QueryService) -> str:
    if query_name == "all":
        explain_by_name = {
            name: query_service.explain_query(name)
            for name in query_service.available_queries()
        }
        return _format_named_sql(explain_by_name)

    return query_service.explain_query(query_name)
