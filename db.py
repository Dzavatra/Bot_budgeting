from typing import Dict, List, Tuple

import sqlite3


conn = sqlite3.connect("bot.db")
cursor = conn.cursor()


def set_active(user_id, act) -> None:
    act = int(act)
    cursor.execute("update users set active = ? where user_id = ?", (act, user_id,))
    conn.commit()


def user_exists(user_id):
    result = cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
    return result


def add_user(user_id):
    cursor.execute("INSERT INTO users (user_id, active) VALUES (?, 1)", (user_id,))
    conn.commit()
    return

def insert(table: str, column_values: Dict):
    columns = ', '.join( column_values.keys() )
    values = [tuple(column_values.values())]
    placeholders = ", ".join( "?" * len(column_values.keys()) )
    cursor.executemany(
        f"INSERT INTO {table} "
        f"({columns}) "
        f"VALUES ({placeholders})",
        values)
    conn.commit()


def fetchall(table: str, columns: List[str]) -> List[Tuple]:
    columns_joined = ", ".join(columns)
    cursor.execute(f"SELECT {columns_joined} FROM {table}")
    rows = cursor.fetchall()
    result = []
    for row in rows:
        dict_row = {}
        for index, column in enumerate(columns):
            dict_row[column] = row[index]
        result.append(dict_row)
    return result


def fetch(query):
    result_list = []
    for tup in query:
        l = list(tup)
        result_list.append(l[0])
    return result_list

def delete(table: str, row_id: int) -> None:
    row_id = int(row_id)
    cursor.execute(f"delete from {table} where id={row_id}")
    conn.commit()


def get_cursor():
    return cursor


def _init_db():
    """Инициализирует БД"""
    with open("database.sql", "r", encoding='utf-8') as f:
        sql = f.read()
    cursor.executescript(sql)
    conn.commit()


def check_db_exists():
    """Проверяет, инициализирована ли БД, если нет — инициализирует"""
    cursor.execute("SELECT name FROM sqlite_master "
                   "WHERE type='table' AND name='category'")
    table_exists = cursor.fetchall()
    if table_exists:
        return
    _init_db()


check_db_exists()

