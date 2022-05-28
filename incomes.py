from typing import List, NamedTuple, Optional
import db
import exceptions
import datetime
import re
import pytz


class Income(NamedTuple):
    id: Optional[int]
    amount: int
    cat: str
    date: Optional[str]


def add_income(inc: str, cat: str, ptype: str, us_id: str) -> Income:
    income = _parse_message(inc)
    inserted_row_id = db.insert("income", {
        "amount": income,
        "category": cat,
        "paying_type": ptype,
        "user_id": us_id,
        "created": _get_now_formatted()
    })
    return Income(id=None, amount=income, cat=None, date=None)


def _parse_message(inc: str):
    test = inc.isdigit()
    if not test:
        raise exceptions.NotCorrectMessage(
            "Не могу понять сообщение. Пожалуйста, укажите полученную сумму в числовом формате, "
            "например:\n180000")
    return inc


def _get_now_formatted() -> str:
    """Возвращает сегодняшнюю дату строкой"""
    return _get_now_datetime().strftime("%Y-%m-%d %H:%M:%S")


def _get_now_datetime() -> datetime.datetime:
    """Возвращает сегодняшний datetime с учётом времненной зоны Мск."""
    tz = pytz.timezone("Europe/Moscow")
    now = datetime.datetime.now(tz)
    return now


def get_last_incs(us_id) -> str:
    cursor = db.get_cursor()
    cursor.execute(f"select id, amount, category, date(created) "
                   f"from income "
                   f"where user_id = ? order by 1 desc limit 5", (us_id, ))
    result = cursor.fetchall()
    if not result:
        return None
    last_incomes = [Income(id=row[0], amount=row[1],  cat=row[2], date=row[3]) for row in result]
    return last_incomes


def delete_income(row_id: int) -> None:
    """Удаляет сообщение по его идентификатору"""
    db.delete("income", row_id)
