"""Checks db existence and creating it if need"""
import sqlite3
from sqlite3.dbapi2 import Connection, Cursor, OperationalError

from loguru import logger as log

try:
    conn: Connection = sqlite3.connect(f"./customer.db")
    cursor: Cursor = conn.cursor()
except OperationalError as e:
    log.error(f"Problem with database: {e}")
    exit()


def check_table_exists(table: str):
    cursor.execute("SELECT name FROM sqlite_master "
                   f"WHERE type='table' AND name='{table}'")
    table_exists = cursor.fetchall()
    if table_exists:
        log.info("Database validated")
        return
    log.warning("Database does not exist")
    _init_db(table)


def _init_db(table: str):
    "Init database from script"
    log.info("Initializing customer database")
    with open(f"./config/create_{table}_db.sql", "r") as f:
        sql = f.read()
    cursor.executescript(sql)
    conn.commit()


