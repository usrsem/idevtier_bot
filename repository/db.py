from sqlite3.dbapi2 import IntegrityError
from typing import Any, Union
from .db_manager import conn, cursor
from loguru import logger as log


def insert(table: str, field_values: dict[str, Any]) -> None:
    fields = ', '.join(field_values.keys() )
    values = [tuple(field_values.values())]
    placeholders = ", ".join( "?" * len(field_values.keys()) )
    try:
        cursor.executemany(
            f"INSERT INTO {table} "
            f"({fields}) "
            f"VALUES ({placeholders})",
            values)
        conn.commit()
    except IntegrityError:
        log.info(f"User already registrated {field_values}")


def selectall(table: str, fields: list[str]) -> tuple[tuple]:
    fields_joined = ", ".join(fields)
    cursor.execute(f"SELECT {fields_joined} FROM {table}")
    rows = cursor.fetchall()
    return tuple(rows)


def delete_by_id(table: str, id: Union[str, int]) -> None:
    raise NotImplementedError("No impl for delete_by_id")
