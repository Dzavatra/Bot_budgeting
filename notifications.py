import asyncio
import aioschedule
import datetime
from loader import dp, bot
import db
from expenses import _get_now_datetime


async def sending():
    today = str(_get_now_datetime()).split()[0]
    cursor = db.get_cursor()
    cursor.execute("select user_id, active "
                   "from users ")
    users = cursor.fetchall()
    for user in users:
        cursor.execute("select sum(amount) "
                       "from expense where date(created) = ? and user_id = ?", (today, user[0],))
        all_today_expenses = cursor.fetchone()[0]
        if not all_today_expenses:
            try:
                await bot.send_message(chat_id=user[0],
                                       text="<b>Бот заскучал...</b>\nКажется, Вы забыли добавить расходы за сегодня 🙁")
                if int(user[1]) == 0:
                    db.set_active(user[0], 1)
            except:
                db.set_active(user[0], 0)
        else:
            await bot.send_message(chat_id=user[0],
                                   text="<b>Вижу Ваши расходы</b> 📈\nЕсли вдруг забыли еще что-то добавить, самое время это сделать!")


def change_advice():
    start_week = 20
    current_date = datetime.date.today()
    current_week = int(current_date.strftime("%W"))
    note_id = current_week - start_week
    return note_id


async def send_article():
    cursor = db.get_cursor()
    cursor.execute("select user_id, active "
                   "from users ")
    users = cursor.fetchall()
    cursor.execute("select article, link "
                   "from articles "
                   "where id = ?", (change_advice(),))
    article = cursor.fetchone()
    for user in users:
        try:
            await bot.send_message(chat_id=user[0],
                                   text=f"{article[0]}\n\n<i>Ознакомиться: {article[1]}</i>")
            if int(user[1]) == 0:
                db.set_active(user[0], 1)
        except:
            db.set_active(user[0], 0)


async def scheduler():
    aioschedule.every().day.at("21:00").do(sending)
    aioschedule.every().friday.at("11:00").do(send_article)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)
