import config
from DB import BotDB
from Parser.parser import *
import logging
from aiogram import Bot, Dispatcher, executor, types
import os
import random
from prettytable import PrettyTable
from aiogram.dispatcher.filters import Text


# Объект бота
bot = Bot(token=config.TOKEN)
# Диспетчер для бота
dp = Dispatcher(bot)
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)


@dp.message_handler(commands="start")
async def start(message: types.Message):
    db = BotDB('main.db')
    try:
        user_name = message.from_user.username
    except:
        user_name = None
    if (not db.user_exists(message.from_user.id)):
        db.add_user(message.from_user.id, user_name)
    sti = open('img/sticker.webp', 'rb')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item = types.KeyboardButton("Помощь ❓")
    markup.add(item)
    await message.answer_sticker(sti, reply_markup=markup)
    sti.close()

@dp.message_handler(commands=('search', 's'))
async def search(message: types.Message):
    db = BotDB('main.db')
    game = ' '.join(message.text.lower().split()[1:])
    db.add_command(message.from_user.id, ' '.join(message.text.split()[1:]))
    db.close()

    try:
        await big_parser(message=message, game=game, PARSER=ZakaZakaParser, shop="Zaka-Zaka")
        await big_parser(message=message, game=game, PARSER=SteamAccountParser, shop="Steam Account")
        await big_parser(message=message, game=game, PARSER=SteamPayParser, shop="Steam Pay")
        await big_parser(message=message, game=game, PARSER=SteamBuyParser, shop="Steam Buy")
        file = open(os.path.join('img', random.choice(os.listdir('img'))), 'rb')
        await message.answer_sticker(file)
        file.close()
    except:
        await message.reply("Введите запрос точнее ❗")


@dp.message_handler(commands=['admin'])
async def admin_panel(message: types.Message):
    db = BotDB('main.db')
    status = db.get_user_status(message.from_user.id)
    if status == "ADMIN":
        if message.text.lower().split()[1:][0] == "on":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            if db.in_admin_status(message.from_user.id) == 0:
                db.change_in_admin_status(message.from_user.id, 1)
                item1 = types.KeyboardButton("Список пользователей 📖")
                item2 = types.KeyboardButton("Список команд 📃")
                item3 = types.KeyboardButton("❌ OFF ❌")
                markup.row(item1, item2)
                markup.row(item3)
                await message.answer("Режим администратора включен❗❗❗", reply_markup=markup)
            elif db.in_admin_status(message.from_user.id) == 1:
                await message.answer("Вы и так в режиме администратора❗", reply_markup=markup)
        elif message.text.lower().split()[1:][0] == "off":
            if db.in_admin_status(message.from_user.id) == 1:
                db.change_in_admin_status(message.from_user.id, 0)
                await message.answer(reply_markup=types.ReplyKeyboardRemove(), text="Режим администратора выключен❗❗❗")
            elif db.in_admin_status(message.from_user.id) == 0:
                await message.answer("Вы и так не в режиме администратора")
    elif status == "USER":
        await message.answer(text="Я не знаю что ответить 😢")
    return db.close()

@dp.message_handler(commands=['change', 'c'])
async def change(message: types.Message):
    db = BotDB('main.db')
    status = db.get_user_status(message.from_user.id)
    if status == "ADMIN":
        if db.in_admin_status(message.from_user.id) == 1:
            msg = message.text.split()[1:]
            if len(msg) == 2 and msg[0].isdigit() and msg[1] in ['admin', 'user']:
                user_id, new_status = msg
                if db.user_exists(user_id) == True:
                    db.change_user_status(user_id=user_id, new_status=new_status)
                    await message.answer("Готово ✅")
                elif db.user_exists(user_id) == False:
                    await message.answer("ID не найден ❌")
        elif db.in_admin_status(message.from_user.id) == 0:
            await message.answer("Сначала войдите в режим администратора")
    elif status == "USER":
        await message.answer(text="Я не знаю что ответить 😢")
    return db.close()


async def big_parser(message, game, PARSER, shop):
    Shop = PARSER(game=game).parse()

    if Shop == [] or Shop == "Сервер не отвечает":
        final_result = f"❌ {shop}: Игра не найдена :("
        return await message.answer(final_result)
    else:
        markup = types.InlineKeyboardMarkup()
        for i in Shop:
            btn = types.InlineKeyboardButton(text=f'{i[0]} - {i[1]} руб.', url=i[2])
            markup.add(btn)
        return await message.answer(f"✅ {shop}", reply_markup=markup)

@dp.message_handler(Text(equals="❌ OFF ❌"))
async def quit(message: types.Message):
    db = BotDB("main.db")
    if db.in_admin_status(message.from_user.id) == 1:
        db.change_in_admin_status(message.from_user.id, 0)
        await message.answer("Режим администратора выключен❗❗❗", reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.answer("Вы и так не в режиме администратора")
    return db.close()


@dp.message_handler(Text(equals="Список команд 📃"))
async def commands_list(message: types.Message):
    db = BotDB("main.db")
    status = db.get_user_status(message.from_user.id)
    if status == "ADMIN":
        if db.in_admin_status(message.from_user.id) == 1:
            table = PrettyTable()
            table.field_names = ["User ID", "Username",  "Command", "Time"]
            for i in db.get_all_commands():
                table.add_row(i)
            if len(str(table)) > 4096:
                for i in range(0, len(str(table)), 4096):
                    await message.answer(f"<pre>{str(table)[i:i + 4096]}</pre>", parse_mode="HTML")
            else:
                await message.answer(f"<pre>{table}</pre>", parse_mode="HTML")
        elif db.in_admin_status(message.from_user.id) == 0:
            await message.answer("Сначала войдите в режим администратора")
    elif status == "USER":
        await message.answer(text="Я не знаю что ответить 😢")
    return db.close()

@dp.message_handler(Text(equals="Список пользователей 📖"))
async def users_list(message: types.Message):
    db = BotDB('main.db')
    status = db.get_user_status(message.from_user.id)
    if status == "ADMIN":
        if db.in_admin_status(message.from_user.id) == 1:
            table = PrettyTable()
            table.field_names = ["User ID", "Username", "Join time"]
            for i in db.get_all_users():
                table.add_row(i)
            if len(str(table)) > 4096:
                for i in range(0, len(str(table)), 4096):
                    await message.answer(f"<pre>{str(table)[i:i + 4096]}</pre>", parse_mode="HTML")
            else:
                await message.answer(f"<pre>{table}</pre>", parse_mode="HTML")
        elif db.in_admin_status(message.from_user.id) == 0:
            await message.answer("Сначала войдите в режим администратора")
    elif status == "USER":
        await message.answer(text="Я не знаю что ответить 😢")
    return db.close()

@dp.message_handler(content_types=['text'])
async def lalala(message: types.Message):
    help_text = """
Для поиска цен на игры введите:
/search название игры
/s название игры
Ожидайте анализа данных!
"""
    if message.chat.type == 'private':
        if message.text == 'Помощь ❓':
            await message.reply(help_text)



if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)