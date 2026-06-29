from contextlib import contextmanager
from typing import Iterator

import psycopg

from config import DB_CONFIG


@contextmanager
def get_connection() -> Iterator[psycopg.Connection]:
    connection = psycopg.connect(**DB_CONFIG)

    try:
        yield connection
    finally:
        connection.close()

