""" Работа с расходами — их добавление, удаление, статистики"""
import datetime
import re
from typing import List, NamedTuple, Optional
import matplotlib.pyplot as plt
import pytz

import db
import exceptions
from categories import Categories


class Message(NamedTuple):
    """Структура распаршенного сообщения о новом расходе"""
    amount: int
    category_text: str


class Expense(NamedTuple):
    """Структура добавленного в БД нового расхода"""
    id: Optional[int]
    amount: int
    category_name: str
    date: Optional[str]


def add_expense(raw_message: str, us_id: str, ptype: str) -> Expense:
    """Добавляет новое сообщение.
    Принимает на вход текст сообщения, пришедшего в бот."""
    parsed_message = _parse_message(raw_message)
    category = Categories().get_category(
        parsed_message.category_text)
    inserted_row_id = db.insert("expense", {
        "amount": parsed_message.amount,
        "created": _get_now_formatted(),
        "category_codename": category.codename,
        "raw_text": raw_message,
        "user_id": us_id,
        "paying_type": ptype
    })
    return Expense(id=None,
                   amount=parsed_message.amount,
                   category_name=category.name,
                   date=None)


def _parse_message(raw_message: str) -> Message:
    regexp_result = re.match(r"([\d ]+) (.*)", raw_message)
    # \d - цифра, + - одно и более символов, . - один любой символ, * - ноль и более символов
    if not regexp_result or not regexp_result.group(0) \
            or not regexp_result.group(1) or not regexp_result.group(2):
        raise exceptions.NotCorrectMessage(
            "Не могу понять сообщение. Пожалуйста, укажите потраченную сумму в числовом формате, "
            "например:\n1500")

    amount = regexp_result.group(1).replace(" ", "")
    category_text = regexp_result.group(2).strip().lower()
    return Message(amount=amount, category_text=category_text)


def _get_now_formatted() -> str:
    """Возвращает сегодняшнюю дату строкой"""
    return _get_now_datetime().strftime("%Y-%m-%d %H:%M:%S")


def _get_now_datetime() -> datetime.datetime:
    """Возвращает сегодняшний datetime с учётом времненной зоны Мск."""
    tz = pytz.timezone("Europe/Moscow")
    now = datetime.datetime.now(tz)
    return now


def get_today_statistics(us_id) -> str:
    today = str(_get_now_datetime()).split()[0]
    """Возвращает строкой статистику расходов за сегодня"""
    cursor = db.get_cursor()
    cursor.execute("select sum(amount) "
                   "from expense where date(created) = ? and user_id = ?", (today, us_id,))
    all_today_expenses = cursor.fetchone()[0]
    if all_today_expenses:
        cursor.execute("select category_codename, sum(amount) "
                       "from expense where date(created) = ? and user_id = ? group by category_codename order by 2 desc", (today, us_id, ))
        result = cursor.fetchall()
        today_expenses = Categories().get_categ_name(result)
        names = []
        vals = []
        pie_list = today_expenses.split('\n')
        for row in pie_list[:-1]:
            row = row.split(' — ')
            names.append(row[0])
            vals.append(row[1].split()[0])
        colors = ["#8dc2b4", "#adf0fe", "#814d5b", "#febbad", "#4d6a62",
                  "#534d6a", "#a56db6", "#a37f88", "#81886c", "#736c88",
                  "#c2a49a", "#c19bc2", "#dcddbc", "#8c8bb3"]
        fig, ax = plt.subplots()
        ax.pie(vals, wedgeprops=dict(width=0.4), colors=colors, autopct="%.1f%%", radius=1.5)
        ax.set_title('Сегодняшние расходы', fontsize=20, fontname='Century Gothic')
        ax.legend(labels=names, bbox_to_anchor=(0.9, 0.9))
        ax.axis('equal')
        pic_name = 'pies/today' + '-' + str(us_id) + '.png'
        plt.savefig(pic_name, bbox_inches='tight')
        cursor.execute("select sum(amount) "
                       "from expense where date(created) = ? and paying_type = 'Наличные' and user_id = ?",
                       (today, us_id,))
        cash = cursor.fetchone()[0]
        if not cash:
            cash = 0
        cursor.execute("select sum(amount) "
                       "from expense where date(created) = ? and paying_type = 'Безналичный расчет' and user_id = ?",
                       (today, us_id,))
        non_cash = cursor.fetchone()[0]
        if not non_cash:
            non_cash = 0
    else:
        all_today_expenses = 0
    cursor.execute("select sum(amount) "
                   "from income where date(created) = ? and user_id = ?", (today, us_id, ))
    all_today_incomes = cursor.fetchone()[0]
    if all_today_incomes:
        cursor.execute("select sum(amount) "
                       "from income where date(created) = ? and user_id = ? and paying_type = 'Наличные'", (today, us_id,))
        cash_incomes = cursor.fetchone()[0]
        if not cash_incomes:
            cash_incomes = 0
        cursor.execute("select sum(amount) "
                       "from income where date(created) = ? and user_id = ? and paying_type = 'Безналичный расчет'",
                       (today, us_id,))
        non_cash_incomes = cursor.fetchone()[0]
        if not non_cash_incomes:
            non_cash_incomes = 0
    else:
        all_today_incomes = 0
    if all_today_expenses and all_today_incomes:
        balance = all_today_incomes - all_today_expenses
        if balance < 0:
            balance = '🔴 ' + str(balance)
        elif balance > 0:
            balance = '🟢 ' + str(balance)
        return (f"📊 <b>Сегодняшняя статистика ({today})</b>:\n\n"
                f"• Расходы сегодня:\n"
                f"{today_expenses}"
                f"<b>Всего — {all_today_expenses} руб.</b>\n\n"
                f"💶 Оплачено <b>наличными</b>: {cash} руб.\n"
                f"💳 Оплачно <b>картой/переводом</b>: {non_cash} руб.\n\n"
                f"• Сегодняшние доходы:\n"
                f"<b>Всего — {all_today_incomes} руб.</b>\n\n"
                f"💶 Получено <b>наличными</b>: {cash_incomes} руб.\n"
                f"💳 На <b>р/с</b> или <b>карту</b>: {non_cash_incomes} руб.\n\n"
                f"<b>Итого за сегодня: {balance} руб.</b>")
    elif all_today_expenses and not all_today_incomes:
        return (f"📊 <b>Сегодняшняя статистика ({today})</b>:\n\n"
                f"• Расходы сегодня:\n"
                f"{today_expenses}"
                f"<b>Всего — {all_today_expenses} руб.</b>\n\n"
                f"💶 Оплачено <b>наличными</b>: {cash} руб.\n"
                f"💳 Оплачно <b>картой/переводом</b>: {non_cash} руб.\n\n"
                f"Доходов сегодня пока нет.")
    elif not all_today_expenses and all_today_incomes:
        return (f"📊 <b>Сегодняшняя статистика ({today})</b>:\n\n"
                f"Расходов сегодня пока нет.\n\n"
                f"• Сегодняшние доходы:\n"
                f"<b>Всего — {all_today_incomes} руб.</b>\n\n"
                f"💶 Получено <b>наличными</b>: {cash_incomes} руб.\n"
                f"💳 На <b>р/с</b> или <b>карту</b>: {non_cash_incomes} руб.")
    else:
        return ("За сегодняшний день расходов и доходов пока нет.")


def get_week_statistics(us_id) -> str:
    cursor = db.get_cursor()
    cursor.execute(f"select sum(amount) "
                   f"from expense where (julianday('now') - julianday(created)) <= 7 and user_id = ?", (us_id,))
    all_week_expenses = cursor.fetchone()[0]
    if all_week_expenses:
        cursor.execute(f"select category_codename, sum(amount) "
                       f"from expense where (julianday('now') - julianday(created)) <= 7 and user_id = ? group by category_codename order by 2 desc", (us_id, ))
        result = cursor.fetchall()
        week_expenses = Categories().get_categ_name(result)
        names = []
        vals = []
        pie_list = week_expenses.split('\n')
        for row in pie_list[:-1]:
            row = row.split(' — ')
            names.append(row[0])
            vals.append(row[1].split()[0])
        colors = ["#663381", "#8a52a7", "#6d2393", "#b462de", "#ca8cea",
                  "#58525c", "#362c3b", "#1d1a1f", "#81886c", "#736c88",
                  "#c2a49a", "#c19bc2", "#dcddbc", "#8c8bb3"]
        fig, ax = plt.subplots()
        ax.pie(vals, wedgeprops=dict(width=0.4), colors=colors, autopct="%.1f%%",  radius=1.5)
        ax.set_title('Расходы за неделю', fontsize=20, fontname='Century Gothic')
        ax.legend(labels=names, bbox_to_anchor=(0.9, 0.9))
        ax.axis('equal')
        pic_name = 'pies/week' + '-' + str(us_id) + '.png'
        plt.savefig(pic_name, bbox_inches='tight')
        cursor.execute("select sum(amount) "
                   "from expense where (julianday('now') - julianday(created)) <= 7 and paying_type = 'Наличные' and user_id = ?",
                   (us_id,))
        cash = cursor.fetchone()[0]
        if not cash:
            cash = 0
        cursor.execute("select sum(amount) "
                       "from expense where (julianday('now') - julianday(created)) <= 7 and paying_type = 'Безналичный расчет' and user_id = ?",
                       (us_id,))
        non_cash = cursor.fetchone()[0]
        if not non_cash:
            non_cash = 0
    else:
        all_week_expenses = 0
    cursor.execute("select sum(amount) "
                   "from income where (julianday('now') - julianday(created)) <= 7 and user_id = ?", (us_id, ))
    all_week_incomes = cursor.fetchone()[0]
    if all_week_incomes:
        cursor.execute("select sum(amount) "
                       "from income where (julianday('now') - julianday(created)) <= 7 and user_id = ? and paying_type = 'Наличные'", (us_id,))
        cash_incomes = cursor.fetchone()[0]
        if not cash_incomes:
            cash_incomes = 0
        cursor.execute("select sum(amount) "
                       "from income where (julianday('now') - julianday(created)) <= 7 and user_id = ? and paying_type = 'Безналичный расчет'",
                       (us_id,))
        non_cash_incomes = cursor.fetchone()[0]
        if not non_cash_incomes:
            non_cash_incomes = 0
    else:
        all_week_incomes = 0
    if all_week_expenses and all_week_incomes:
        balance = all_week_incomes - all_week_expenses
        if balance < 0:
            balance = '🔴 ' + str(balance)
        elif balance > 0:
            balance = '🟢 ' + str(balance)
        return (f"📊 <b>Отчет за прошедшие 7 дней</b>:\n\n"
                f"• Расходы за неделю:\n"
                f"{week_expenses}"
                f"<b>Всего — {all_week_expenses} руб.</b>\n\n"
                f"💶 Оплачено <b>наличными</b>: {cash} руб.\n"
                f"💳 Оплачно <b>картой/переводом</b>: {non_cash} руб.\n\n"
                f"• Доходы за неделю:\n"
                f"<b>Всего — {all_week_incomes} руб.</b>\n\n"
                f"💶 Получено <b>наличными</b>: {cash_incomes} руб.\n"
                f"💳 На <b>р/с</b> или <b>карту</b>: {non_cash_incomes} руб.\n\n"
                f"<b>Итого за неделю: {balance} руб.</b>")
    elif all_week_expenses and not all_week_incomes:
        return (f"📊 <b>Отчет за прошедшие 7 дней</b>:\n\n"
                f"• Расходы за неделю:\n"
                f"{week_expenses}"
                f"<b>Всего — {all_week_expenses} руб.</b>\n\n"
                f"💶 Оплачено <b>наличными</b>: {cash} руб.\n"
                f"💳 Оплачно <b>картой/переводом</b>: {non_cash} руб.\n\n"
                f"Доходов за неделю пока нет.")
    elif not all_week_expenses and all_week_incomes:
        return (f"📊 <b>Отчет за прошедшие 7 дней</b>:\n\n"
                f"Расходов за неделю пока нет.\n\n"
                f"• Доходы за неделю:\n"
                f"<b>Всего — {all_week_incomes} руб.</b>\n\n"
                f"💶 Получено <b>наличными</b>: {cash_incomes} руб.\n"
                f"💳 На <b>р/с</b> или <b>карту</b>: {non_cash_incomes} руб.")
    else:
        return ("За прошедшие 7 дней расходов и доходов пока нет.")


def get_month_statistics(us_id) -> str:
    now = _get_now_datetime()
    first_day_of_month = f'{now.year:04d}-{now.month:02d}-01'
    cursor = db.get_cursor()
    cursor.execute(f"select sum(amount) "
                   f"from expense where date(created) >= '{first_day_of_month}' and user_id = ?", (us_id, ))
    all_month_expenses = cursor.fetchone()[0]
    if all_month_expenses:
        cursor.execute(f"select category_codename, sum(amount) "
                       f"from expense where date(created) >= '{first_day_of_month}' and user_id = ? group by category_codename order by 2 desc", (us_id, ))
        result = cursor.fetchall()
        month_expenses = Categories().get_categ_name(result)
        names = []
        vals = []
        pie_list = month_expenses.split('\n')
        for row in pie_list[:-1]:
            row = row.split(' — ')
            names.append(row[0])
            vals.append(row[1].split()[0])
        colors = ["#15143c", "#302e79", "#4441b4", "#3a36dc", "#6965ff",
                  "#a6a5cb", "#74738e", "#3b3a47", "#252529", "#101010",
                  "#c2a49a", "#c19bc2", "#dcddbc", "#8c8bb3"]
        fig, ax = plt.subplots()
        ax.pie(vals, wedgeprops=dict(width=0.4), colors=colors, autopct="%.1f%%", radius=1.5)
        ax.set_title('Расходы за текущий месяц', fontsize=20, fontname='Century Gothic')
        ax.legend(labels=names, bbox_to_anchor=(0.9, 0.9))
        ax.axis('equal')
        pic_name = 'pies/month' + '-' + str(us_id) + '.png'
        plt.savefig(pic_name, bbox_inches='tight')
        cursor.execute(f"select sum(amount) "
                       f"from expense where date(created) >= '{first_day_of_month}' and paying_type = 'Наличные' and user_id = ?", (us_id,))
        cash = cursor.fetchone()[0]
        if not cash:
            cash = 0
        cursor.execute(f"select sum(amount) "
                       f"from expense where date(created) >= '{first_day_of_month}' and paying_type = 'Безналичный расчет' and user_id = ?",
                       (us_id,))
        non_cash = cursor.fetchone()[0]
        if not non_cash:
            non_cash = 0
    else:
        all_month_expenses = 0
    cursor.execute(f"select sum(amount) "
                   f"from income where date(created) >= '{first_day_of_month}' and user_id = ?", (us_id,))
    all_month_incomes = cursor.fetchone()[0]
    if all_month_incomes:
        cursor.execute(f"select sum(amount) "
                       f"from income where date(created) >= '{first_day_of_month}' and user_id = ? and paying_type = 'Наличные'",
                       (us_id,))
        cash_incomes = cursor.fetchone()[0]
        if not cash_incomes:
            cash_incomes = 0
        cursor.execute(f"select sum(amount) "
                       f"from income where date(created) >= '{first_day_of_month}' and user_id = ? and paying_type = 'Безналичный расчет'",
                       (us_id,))
        non_cash_incomes = cursor.fetchone()[0]
        if not non_cash_incomes:
            non_cash_incomes = 0
    else:
        all_month_incomes = 0
    if all_month_expenses and all_month_incomes:
        balance = all_month_incomes - all_month_expenses
        if balance < 0:
            balance = '🔴 ' + str(balance)
        elif balance > 0:
            balance = '🟢 ' + str(balance)
        return (f"📊 <b>Отчет за месяц</b>:\n\n"
                f"• Расходы в текущем месяце:\n"
                f"{month_expenses}"
                f"<b>Всего — {all_month_expenses} руб.</b>\n\n"
                f"💶 Оплачено <b>наличными</b>: {cash} руб.\n"
                f"💳 Оплачно <b>картой/переводом</b>: {non_cash} руб.\n\n"
                f"• Доходы в текущем месяце:\n"
                f"<b>Всего — {all_month_incomes} руб.</b>\n\n"
                f"💶 Получено <b>наличными</b>: {cash_incomes} руб.\n"
                f"💳 На <b>р/с</b> или <b>карту</b>: {non_cash_incomes} руб.\n\n"
                f"<b>Итого за месяц: {balance} руб.</b>")
    elif all_month_expenses and not all_month_incomes:
        return (f"📊 <b>Отчет за месяц</b>:\n\n"
                f"• Расходы в текущем месяце:\n"
                f"{month_expenses}"
                f"<b>Всего — {all_month_expenses} руб.</b>\n\n"
                f"💶 Оплачено <b>наличными</b>: {cash} руб.\n"
                f"💳 Оплачно <b>картой/переводом</b>: {non_cash} руб.\n\n"
                f"Доходов в этом месяце пока нет.")
    elif not all_month_expenses and all_month_incomes:
        return (f"📊 <b>Отчет за месяц</b>:\n\n"
                f"Расходов в этом месяце пока нет.\n\n"
                f"• Доходы в текущем месяце:\n"
                f"<b>Всего — {all_month_incomes} руб.</b>\n\n"
                f"💶 Получено <b>наличными</b>: {cash_incomes} руб.\n"
                f"💳 На <b>р/с</b> или <b>карту</b>: {non_cash_incomes} руб.")
    else:
        return "За текущий месяц расходов и доходов пока нет."


def get_last_exps(us_id) -> str:
    cursor = db.get_cursor()
    cursor.execute(f"select id, amount, c.name, date(created) "
                   f"from expense as ex left join category as c on c.codename = ex.category_codename "
                   f"where user_id = ? order by 1 desc limit 7", (us_id, ))
    result = cursor.fetchall()
    if not result:
        return None
    last_expenses = [Expense(id=row[0], amount=row[1], category_name=row[2], date=row[3]) for row in result]
    return last_expenses


def delete_expense(row_id: int) -> None:
    """Удаляет сообщение по его идентификатору"""
    db.delete("expense", row_id)
