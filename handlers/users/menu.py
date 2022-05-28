from loader import dp, bot
from aiogram.types import Message, ReplyKeyboardRemove, InputFile
from keyboards.default import menu, paying, incs
from aiogram.dispatcher.filters import Command, Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from categories import Categories
import exceptions
import expenses
import incomes


@dp.message_handler(Command('menu'))
async def show_menu(message: Message):
    await message.answer('Выберите кнопку из меню ниже',
                         reply_markup=menu)


class FSMExp(StatesGroup):
    categ = State()
    expen = State()
    ptype = State()


@dp.message_handler(Text(equals='Добавить расход'), state=None)
async def add_exp(message: Message):
    await FSMExp.categ.set()
    await message.answer('Укажите название или категорию траты\n\n/cancel (отмена)')


@dp.message_handler(state="*", commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state="*")
async def cancel(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.answer('Добавление отменено', reply_markup=menu)


@dp.message_handler(state=FSMExp.categ)
async def get_cat(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await FSMExp.next()
    await message.answer('Укажите потраченную сумму\n\n/cancel (отмена)')


@dp.message_handler(state=FSMExp.expen)
async def get_sum(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['sum'] = message.text
        user_exp = data['sum'] + ' ' + data['name']
    try:
        expenses._parse_message(user_exp)
    except exceptions.NotCorrectMessage as e:
        await message.answer(str(e))
        return
    await FSMExp.next()
    await message.answer('Укажите тип оплаты\n\n/cancel (отмена)', reply_markup=paying)


@dp.message_handler(state=FSMExp.ptype)
async def get_type(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['type'] = message.text
        user_exp = data['sum'] + ' ' + data['name']
    ex = expenses.add_expense(user_exp, message.from_user.id, message.text)
    answer_message = (f"Трата суммой <b>{ex.amount}</b> руб. добавлена в категорию <b>{ex.category_name.capitalize()}</b>.")
    await message.answer(answer_message, reply_markup=ReplyKeyboardRemove())
    await message.answer('Главное меню:',
                         reply_markup=menu)
    await state.finish()


@dp.message_handler(Text(equals='Сегодняшняя статистика'))
async def today_stat(message: Message):
    answer_message = expenses.get_today_statistics(message.from_user.id)
    if '• Расходы сегодня:' in answer_message:
        pic_name = 'pies/today' + '-' + str(message.from_user.id) + '.png'
        await message.answer_photo(InputFile(pic_name), answer_message)
    else:
        await message.answer(answer_message)


@dp.message_handler(Text(equals='Отчёт за неделю'))
async def month_stat(message: Message):
    answer_message = expenses.get_week_statistics(message.from_user.id)
    if '• Расходы за неделю:' in answer_message:
        pic_name = 'pies/week' + '-' + str(message.from_user.id) + '.png'
        await message.answer_photo(InputFile(pic_name), answer_message)
    else:
        await message.answer(answer_message)


@dp.message_handler(Text(equals='Отчёт за месяц'))
async def month_stat(message: Message):
    answer_message = expenses.get_month_statistics(message.from_user.id)
    if '• Расходы в текущем месяце:' in answer_message:
        pic_name = 'pies/month' + '-' + str(message.from_user.id) + '.png'
        await message.answer_photo(InputFile(pic_name), answer_message)
    else:
        await message.answer(answer_message)


@dp.message_handler(Text(equals='Недавние расходы'))
async def last_exps(message: Message):
    last_exp = expenses.get_last_exps(message.from_user.id)
    if not last_exp:
        await message.answer("Расходов ещё нет.")
        return
    l_exp = [
        f"• {expense.category_name.capitalize()} — {expense.date} — <b>{expense.amount} руб.</b>  "
        f"(/delete{expense.id} - удалить)"
        for expense in last_exp]
    answer_message = "📝 Недавние расходы:\n\n" + "\n".join(l_exp)
    await message.answer(answer_message)


@dp.message_handler(lambda message: message.text.startswith('/delete'))
async def del_expense(message: Message):
    row_id = int(message.text[7:])
    expenses.delete_expense(row_id)
    answer_message = "Запись успешно удалена!"
    await message.answer(answer_message)


@dp.message_handler(Text(equals='Категории расходов'))
async def categories_list(message: Message):
    categories = Categories().get_all_categories()
    await message.answer("Категории расходов:\n\n• " + \
                     ("\n• ".join(["<b>" + c.name.capitalize() + "</b>" + " (" + ", ".join(c.aliases) + ")" for c in categories])))


class FSMInc(StatesGroup):
    inc = State()
    category = State()
    ptype = State()


@dp.message_handler(Text(equals='Добавить доход'), state=None)
async def add_inc(message: Message):
    await FSMInc.inc.set()
    await message.answer('Укажите полученную сумму\n\n/cancel (отмена)')


@dp.message_handler(state=FSMInc.inc)
async def get_sum(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['sum'] = message.text
        inc = data['sum']
    try:
        incomes._parse_message(inc)
    except exceptions.NotCorrectMessage as e:
        await message.answer(str(e))
        return
    await FSMInc.next()
    await message.answer('Укажите тип дохода\n\n/cancel (отмена)', reply_markup=incs)


@dp.message_handler(state=FSMInc.category)
async def get_cat(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['cat'] = message.text
    await FSMInc.next()
    await message.answer('Укажите способ получения\n\n/cancel (отмена)', reply_markup=paying)


@dp.message_handler(state=FSMInc.ptype)
async def get_type(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['type'] = message.text
        inc = incomes.add_income(data['sum'], data['cat'], data['type'], message.from_user.id)
    answer_message = (f"Полученный доход суммой <b>{inc.amount}</b> руб. учтён.")
    await message.answer(answer_message, reply_markup=ReplyKeyboardRemove())
    await message.answer('Главное меню:', reply_markup=menu)
    await state.finish()


@dp.message_handler(Text(equals='Последние доходы'))
async def last_exps(message: Message):
    last_inc = incomes.get_last_incs(message.from_user.id)
    if not last_inc:
        await message.answer("Доходов пока нет.")
        return
    l_inc = [
        f"• {income.cat} - {income.date} — <b>{income.amount} руб.</b>  "
        f"(/remove{income.id} - удалить)"
        for income in last_inc]
    answer_message = "📝 Последние доходы:\n\n" + "\n".join(l_inc)
    await message.answer(answer_message)


@dp.message_handler(lambda message: message.text.startswith('/remove'))
async def del_income(message: Message):
    row_id = int(message.text[7:])
    incomes.delete_income(row_id)
    answer_message = "Запись успешно удалена!"
    await message.answer(answer_message)


@dp.message_handler()
async def empty_message(message: Message):
    answer_message = 'Такой команды нет.\nВыберите команду из основного меню.'
    await message.reply(answer_message)
    await message.delete()
