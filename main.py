# ENERGYBOT version 1.9.9 by dariusua

import telebot
import sqlite3
import schedule
import time
import keyboards as k
from telebot import types
from datetime import datetime, timedelta
from threading import Thread, Lock
from config import TOKEN

bot = telebot.TeleBot(TOKEN)
mutex = Lock()
time_worked = 0


def connect_db():
    connect = sqlite3.connect('database.db')
    return connect


def locked(f):
    def f_locked(*args, **kwargs):
        with mutex:
            return f(*args, **kwargs)

    return f_locked


# Початок роботи, створення бази даних
@bot.message_handler(commands=['start'])
@locked
def start(message: types.Message):
    connect = connect_db()
    cursor = connect.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS database(
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_number INTEGER,
        active INTEGER DEFAULT(1),
        night INTEGER DEFAULT(0),
        maybe INTEGER DEFAULT(0),
        time_to INTEGER DEFAULT(30),
        time_connect INTEGER DEFAULT(0)
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS banned_from_support(
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        reason TEXT DEFAULT(0),
        date TEXT
    )""")
    connect.commit()
    if_exists = cursor.execute("SELECT EXISTS (SELECT user_id FROM database WHERE user_id = ?)", (message.chat.id,)).fetchone()
    if if_exists[0] == 0:
        try:
            bot.send_message(message.chat.id, f'Привіт 👋 \n\n🤖 Цей бот створений задля сповіщення жителів міста Львів та Львівської області про планові відключення у вашому населеному пункті. \n✏️ Бот буде відсилати повідомлення з попередженням за 30 хвилин до відключення світла. \n\n📋 Для підключення сповіщень, натисніть на кнопку "✅ Підключити сповіщення" нижче.', reply_markup=k.register_to_bot())
        except telebot.apihelper.ApiTelegramException:
            pass
    else:
        try:
            bot.send_message(message.chat.id, f'Привіт 👋 \n\n🤖 Цей бот створений задля сповіщення жителів міста Львів та Львівської області про планові відключення у вашому населеному пункті. \n✏️ Бот буде відсилати повідомлення з попередженням за 30 хвилин до відключення світла.', reply_markup=k.main_menu())
        except telebot.apihelper.ApiTelegramException:
            pass


# Функція розсилки через команду
@bot.message_handler(commands=['send'])
@locked
def send_for_all(message: types.Message):
    if message.chat.id == 880691612:
        connect = connect_db()
        cursor = connect.cursor()
        results = cursor.execute("SELECT user_id FROM database").fetchall()
        text = message.text[6:]
        for row in results:
            active_value = row[0]
            set_active = cursor.execute(f"SELECT active FROM database WHERE user_id = {active_value}")
            try:
                bot.send_message(row[0], text, reply_markup=k.main_menu())
                if set_active != 1:
                    cursor.execute(f"UPDATE database SET active = 1 WHERE user_id = {active_value}")
            except telebot.apihelper.ApiTelegramException:
                cursor.execute(f"UPDATE database SET active = 0 WHERE user_id = {active_value}")
                time.sleep(1)
        connect.commit()
    else:
        try:
            bot.send_message(message.chat.id, "Для виконання цієї команди Ви повинні бути адміном.", reply_markup=k.main_menu())
        except telebot.apihelper.ApiTelegramException:
            pass


# Підрахунок скільки користувачів в боті
@bot.message_handler(commands=['stats'])
def stats(message: types.Message):
    global time_worked
    if message.chat.id == 880691612 or message.chat.id == 720509891:
        connect = connect_db()
        cursor = connect.cursor()
        result_all = cursor.execute("SELECT COUNT(*) FROM database").fetchone()
        result_g1 = cursor.execute("SELECT COUNT(*) FROM database WHERE group_number = 1").fetchone()
        result_g2 = cursor.execute("SELECT COUNT(*) FROM database WHERE group_number = 2").fetchone()
        result_g3 = cursor.execute("SELECT COUNT(*) FROM database WHERE group_number = 3").fetchone()
        result_night = cursor.execute("SELECT COUNT(*) FROM database WHERE night = 1").fetchone()
        result_maybe = cursor.execute("SELECT COUNT(*) FROM database WHERE maybe = 1").fetchone()
        result_night_maybe = cursor.execute("SELECT COUNT(*) FROM database WHERE night = 1 AND maybe = 1").fetchone()
        result_time10 = cursor.execute("SELECT COUNT(*) FROM database WHERE time_to = 10").fetchone()
        result_time30 = cursor.execute("SELECT COUNT(*) FROM database WHERE time_to = 30").fetchone()
        result_time60 = cursor.execute("SELECT COUNT(*) FROM database WHERE time_to = 60").fetchone()
        result_bagged_users1 = cursor.execute("SELECT COUNT(*) FROM database WHERE maybe != 1 AND maybe != 0").fetchone()
        result_bagged_users2 = cursor.execute("SELECT COUNT(*) FROM database WHERE night != 1 AND night != 0").fetchone()
        result_bagged_users3 = cursor.execute("SELECT COUNT(*) FROM database WHERE time_to != 10 AND time_to != 30 AND time_to != 60").fetchone()
        result_not_active = cursor.execute("SELECT COUNT(*) FROM database WHERE active = 0").fetchone()
        result_active = cursor.execute("SELECT COUNT(*) FROM database WHERE active = 1").fetchone()
        bot.send_message(message.chat.id, f"📊 Статистика всіх користувачів: \n\nКористувачів 1 групи: {result_g1[0]} \nКористувачів 2 групи: {result_g2[0]} \nКористувачів 3 групи: {result_g3[0]} \n\nКористувачів, які користуються нічними сповіщеннями: {result_night[0]} \nКористувачів, які користуються сповіщеннями про можливі відключення: {result_maybe[0]} \nКористувачів, які користуються нічними сповіщеннями та сповіщення про можливі відключення: {result_night_maybe[0]} \n\nКористувачів, яким сповіщення приходять за 10 хвилин до відключення: {result_time10[0]} \nКористувачів, яким сповіщення приходять за 30 хвилин до відключення: {result_time30[0]} \nКористувачів, яким сповіщення приходять за 60 хвилин до відключення: {result_time60[0]} \n\nКористувачів, в яких виникла помилка та не надсилаються сповіщення: {result_bagged_users1[0]+result_bagged_users2[0]+result_bagged_users3[0]} \nАктивних користувачів: {result_active[0]} \nНеактивних користувачів: {result_not_active[0]} \n\nВсього користувачів: {result_all[0]}", reply_markup=k.main_menu())
        connect.commit()
    else:
        try:
            bot.send_message(message.chat.id, "Для виконання цієї команди Ви повинні бути адміном.", reply_markup=k.main_menu())
        except telebot.apihelper.ApiTelegramException:
            pass


@bot.message_handler(commands=['support'])
@locked
def start_support(message: types.Message):
    connect = connect_db()
    cursor = connect.cursor()
    data = cursor.execute(f"SELECT EXISTS (SELECT user_id FROM banned_from_support WHERE user_id = {message.chat.id})").fetchone()
    if data[0] == 0:
        msg = bot.send_message(message.chat.id, "Для відправлення повідомлення в технічну підтримку нашого боту, напишіть нижче текст повідомлення. \n\nНагадуємо, що повідомлення повинно бути написано в адекватній формі, без некоректних висловлювань і тому подібного.", reply_markup=k.support())
        bot.register_next_step_handler(msg, send_msg_to_support)
    else:
        bot.send_message(message.chat.id, "Ви не можете звернутись в технічку підтримку через бан!", reply_markup=k.main_menu())

def send_msg_to_support(message: types.Message):
    if message.text == "⬅ Назад":
        bot.send_message(message.chat.id, "МЕНЮ:", reply_markup=k.main_menu())
    else:
        bot.send_message(880691612, f"{message.chat.first_name} (`{message.chat.id}`) звернувся в технічну підтримку з повідомленням: \n\n{message.text}", reply_markup=k.main_menu(), parse_mode="Markdown")
        bot.send_message(message.chat.id, "Ваше звернення успішно відправлено!", reply_markup=k.main_menu())

@bot.message_handler(commands=['send_to'])
def send_to(message: types.Message):
    if message.chat.id == 880691612:
        full_cmd = message.text.split(" ", 3)
        try:
            if full_cmd[1] == "1":
                support_or_no_msg = "Відповідь на ваше звернення в технічну підтримку: \n\n"
            else:
                support_or_no_msg = ""
            bot.send_message(full_cmd[2], f"{support_or_no_msg}{full_cmd[3]}")
            bot.send_message(message.chat.id, "Повідомлення успішно відправлено!")
        except telebot.apihelper.ApiTelegramException:
            bot.send_message(message.chat.id, f"Виникла помилка при надсиланні повідомлення користувачу з айді {full_cmd[2]}!")

# Робота кнопок
@bot.message_handler(content_types='text')
@locked
def message_reply(message: types.Message):
    connect = connect_db()
    cursor = connect.cursor()
    person_id = message.chat.id

    # Підключення сповіщень
    if message.text == "✅ Підключити сповіщення":
        if_exists = cursor.execute("SELECT EXISTS (SELECT user_id FROM database WHERE user_id = ?)", (message.chat.id,)).fetchone()
        if if_exists[0] == 0:
            try:
                bot.send_message(message.chat.id, f'✅ Для підключення сповіщень про відключення світла Вам необхідно натиснути на кнопку з номером вашої групи. \n❓ Щоб дізнатись номер вашої групи, натисніть на кнопку "Дізнатись свою групу", та перейшовши за посиланням і ввівши свої дані, ви зможете дізнатись свою групу.', reply_markup=k.connect_to_group())
            except telebot.apihelper.ApiTelegramException:
                pass
        else:
            try:
                bot.send_message(message.chat.id, f'✅ Для зміни вашої групи, натисніть на кнопку з номером необхідної Вам групи. \n❓ Щоб дізнатись номер вашої групи, натисніть на кнопку "Дізнатись свою групу", та перейшовши за посиланням і ввівши свої дані, ви зможете дізнатись свою групу.', reply_markup=k.connect_to_group())
            except telebot.apihelper.ApiTelegramException:
                pass

    # Зміна групи
    elif message.text == "🔁 Змінити групу":
        if_exists = cursor.execute("SELECT EXISTS (SELECT user_id FROM database WHERE user_id = ?)", (message.chat.id,)).fetchone()
        if if_exists[0] == 1:
            try:
                bot.send_message(message.chat.id, f'✅ Для зміни вашої групи, натисніть на кнопку з номером необхідної Вам групи. \n❓ Щоб дізнатись номер вашої групи, натисніть на кнопку "Дізнатись свою групу", та перейшовши за посиланням і ввівши свої дані, ви зможете дізнатись свою групу.', reply_markup=k.connect_to_group())
            except telebot.apihelper.ApiTelegramException:
                pass
        else:
            try:
                bot.send_message(message.chat.id, f'✅ Для підключення сповіщень про відключення світла Вам необхідно натиснути на кнопку з номером вашої групи. \n❓ Щоб дізнатись номер вашої групи, натисніть на кнопку "Дізнатись свою групу", та перейшовши за посиланням і ввівши свої дані, ви зможете дізнатись свою групу.', reply_markup=k.connect_to_group())
            except telebot.apihelper.ApiTelegramException:
                pass

    # Відключення сповіщень
    elif message.text == "🔕 Відключити сповіщення":
        if_exists = cursor.execute("SELECT EXISTS (SELECT user_id FROM database WHERE user_id = ?)", (message.chat.id,)).fetchone()
        if if_exists[0] == 1:
            cursor.execute("DELETE FROM database WHERE user_id = ?", (person_id,))
            connect.commit()
            try:
                bot.send_message(message.chat.id, '❌ Ви відключилися від сповіщень про відключення електроенергії. Дякуємо за використання бота!😢 \n\nЩоб підключитись знову, натисніть на кнопку "✅ Підключити сповіщення" нижче.', reply_markup=k.register_to_bot())
            except telebot.apihelper.ApiTelegramException:
                pass


    # Надсилання фото з графіком відключень
    elif message.text == "🖼 Фото графіку" or message.text == "🖼 Повний графік(фото)" or message.text == "📖 Повний графік(фото)":
        data_photo = cursor.execute("SELECT group_number FROM database WHERE user_id = ?", (message.chat.id,)).fetchone()
        if data_photo is not None:
            with open('{}group.png'.format(data_photo[0]), 'rb') as photo:
                try:
                    bot.send_photo(message.chat.id, photo)
                except telebot.apihelper.ApiTelegramException:
                    pass

    elif message.text == "⚙ Налаштування":
        if_exists = cursor.execute("SELECT EXISTS (SELECT user_id FROM database WHERE user_id = ?)", (message.chat.id,)).fetchone()
        if if_exists[0] == 1:
            try:
                bot.send_message(message.from_user.id, "⚙ НАЛАШТУВАННЯ:", reply_markup=k.settings())
            except telebot.apihelper.ApiTelegramException:
                pass

    elif message.text.startswith("/bot "):
        if message.chat.id == 880691612:
            if message.text[5:].isdigit():
                global time_worked
                time_worked_before = time_worked
                time_worked = int(message.text[5:])
                bot.send_message(message.chat.id, f"Час роботи боту оновлений з {time_worked_before} до {time_worked} годин!")

    elif message.text == "/start" or message.text.startswith("/send") or message.text == "/stats" or message.text == "/support" or message.text.startswith("/send_to"):
        pass

    else:
        try:
            bot.send_message(message.from_user.id, "Цієї команди не існує.", reply_markup=k.main_menu())
        except telebot.apihelper.ApiTelegramException:
            pass


@locked
def check_working_bot():
    global time_worked
    connect = connect_db()
    cursor = connect.cursor()
    cursor.execute("DELETE FROM database WHERE active = 0")
    connect.commit()
    connected_ppl = cursor.execute("SELECT COUNT(*) FROM database").fetchone()
    time_worked += 1
    bot.send_message(880691612, f"Бот працює вже стільки годин: {time_worked}, підключено людей: {connected_ppl[0]}.")


schedule.every().hour.at(":15").do(check_working_bot)


# Функція розсилки
@locked
def send(group, night, maybe, time_to, what_text):
    connect = connect_db()
    cursor = connect.cursor()
    query = f"SELECT user_id FROM database WHERE group_number = {group} AND time_to = {time_to} "
    if night == 1:
        query += f"AND night = {night} "
    if maybe == 1:
        query += f"AND maybe = {maybe} "
    results = cursor.execute(query).fetchall()
    group_number = {1: "1️⃣", 2: "2️⃣", 3: "3️⃣"}.get(group, group)
    time_to = {10: 130, 30: 150, 60: 180}.get(time_to, time_to)
    howmuchtime1 = datetime.now() + timedelta(minutes=time_to)
    howmuchtime2 = howmuchtime1 + timedelta(hours=4)
    text = {
        1: f"🔴 З {howmuchtime1.strftime('%H')}:00 до {howmuchtime2.strftime('%H')}:00 планується відключення світла по графіку {group_number} групи!",
        2: f"🟡 З {howmuchtime1.strftime('%H')}:00 до {howmuchtime2.strftime('%H')}:00 планується можливе відключення світла по графіку {group_number} групи!"
    }.get(what_text, what_text)
    for row in results:
        active_value = row[0]
        set_active = cursor.execute(f"SELECT active FROM database WHERE user_id = {active_value}").fetchone()[0]
        try:
            bot.send_message(row[0], text)
            if set_active != 1:
                cursor.execute(f"UPDATE database SET active = 1 WHERE user_id = {active_value}")
        except telebot.apihelper.ApiTelegramException:
            cursor.execute(f"UPDATE database SET active = 0 WHERE user_id = {active_value}")
            time.sleep(1)
    connect.commit()


# Розсилка для 1 групи
schedule.every().sunday.at("22:00").do(send, 1, 1, 0, 60, 1)
schedule.every().sunday.at("22:30").do(send, 1, 1, 0, 30, 1)
schedule.every().sunday.at("22:50").do(send, 1, 1, 0, 10, 1)
schedule.every().monday.at("06:00").do(send, 1, 0, 1, 60, 2)
schedule.every().monday.at("06:30").do(send, 1, 0, 1, 30, 2)
schedule.every().monday.at("06:50").do(send, 1, 0, 1, 10, 2)
schedule.every().monday.at("10:00").do(send, 1, 0, 0, 60, 1)
schedule.every().monday.at("10:30").do(send, 1, 0, 0, 30, 1)
schedule.every().monday.at("10:50").do(send, 1, 0, 0, 10, 1)
schedule.every().monday.at("18:00").do(send, 1, 0, 1, 60, 2)
schedule.every().monday.at("18:30").do(send, 1, 0, 1, 30, 2)
schedule.every().monday.at("18:50").do(send, 1, 0, 1, 10, 2)

schedule.every().wednesday.at("22:00").do(send, 1, 1, 0, 60, 1)
schedule.every().wednesday.at("22:30").do(send, 1, 1, 0, 30, 1)
schedule.every().wednesday.at("22:50").do(send, 1, 1, 0, 10, 1)
schedule.every().thursday.at("06:00").do(send, 1, 0, 1, 60, 2)
schedule.every().thursday.at("06:30").do(send, 1, 0, 1, 30, 2)
schedule.every().thursday.at("06:50").do(send, 1, 0, 1, 10, 2)
schedule.every().thursday.at("10:00").do(send, 1, 0, 0, 60, 1)
schedule.every().thursday.at("10:30").do(send, 1, 0, 0, 30, 1)
schedule.every().thursday.at("10:50").do(send, 1, 0, 0, 10, 1)
schedule.every().thursday.at("18:00").do(send, 1, 0, 1, 60, 2)
schedule.every().thursday.at("18:30").do(send, 1, 0, 1, 30, 2)
schedule.every().thursday.at("18:50").do(send, 1, 0, 1, 10, 2)

schedule.every().saturday.at("22:00").do(send, 1, 1, 0, 60, 1)
schedule.every().saturday.at("22:30").do(send, 1, 1, 0, 30, 1)
schedule.every().saturday.at("22:50").do(send, 1, 1, 0, 10, 1)
schedule.every().sunday.at("06:00").do(send, 1, 0, 1, 60, 2)
schedule.every().sunday.at("06:30").do(send, 1, 0, 1, 30, 2)
schedule.every().sunday.at("06:50").do(send, 1, 0, 1, 10, 2)
schedule.every().sunday.at("10:00").do(send, 1, 0, 0, 60, 1)
schedule.every().sunday.at("10:30").do(send, 1, 0, 0, 30, 1)
schedule.every().sunday.at("10:50").do(send, 1, 0, 0, 10, 1)
schedule.every().sunday.at("18:00").do(send, 1, 0, 1, 60, 2)
schedule.every().sunday.at("18:30").do(send, 1, 0, 1, 30, 2)
schedule.every().sunday.at("18:50").do(send, 1, 0, 1, 10, 2)

schedule.every().tuesday.at("02:00").do(send, 1, 1, 1, 60, 2)
schedule.every().tuesday.at("02:30").do(send, 1, 1, 1, 30, 2)
schedule.every().tuesday.at("02:50").do(send, 1, 1, 1, 10, 2)
schedule.every().tuesday.at("06:00").do(send, 1, 1, 0, 60, 1)
schedule.every().tuesday.at("06:30").do(send, 1, 1, 0, 30, 1)
schedule.every().tuesday.at("06:50").do(send, 1, 1, 0, 10, 1)
schedule.every().tuesday.at("14:00").do(send, 1, 0, 1, 60, 2)
schedule.every().tuesday.at("14:30").do(send, 1, 0, 1, 30, 2)
schedule.every().tuesday.at("14:50").do(send, 1, 0, 1, 10, 2)
schedule.every().tuesday.at("18:00").do(send, 1, 0, 0, 60, 1)
schedule.every().tuesday.at("18:30").do(send, 1, 0, 0, 30, 1)
schedule.every().tuesday.at("18:50").do(send, 1, 0, 0, 10, 1)

schedule.every().friday.at("02:00").do(send, 1, 1, 1, 60, 2)
schedule.every().friday.at("02:30").do(send, 1, 1, 1, 30, 2)
schedule.every().friday.at("02:50").do(send, 1, 1, 1, 10, 2)
schedule.every().friday.at("06:00").do(send, 1, 1, 0, 60, 1)
schedule.every().friday.at("06:30").do(send, 1, 1, 0, 30, 1)
schedule.every().friday.at("06:50").do(send, 1, 1, 0, 10, 1)
schedule.every().friday.at("14:00").do(send, 1, 0, 1, 60, 2)
schedule.every().friday.at("14:30").do(send, 1, 0, 1, 30, 2)
schedule.every().friday.at("14:50").do(send, 1, 0, 1, 10, 2)
schedule.every().friday.at("18:00").do(send, 1, 0, 0, 60, 1)
schedule.every().friday.at("18:30").do(send, 1, 0, 0, 30, 1)
schedule.every().friday.at("18:50").do(send, 1, 0, 0, 10, 1)

schedule.every().tuesday.at("22:00").do(send, 1, 1, 1, 60, 2)
schedule.every().tuesday.at("22:30").do(send, 1, 1, 1, 30, 2)
schedule.every().tuesday.at("22:50").do(send, 1, 1, 1, 10, 2)
schedule.every().wednesday.at("02:00").do(send, 1, 1, 0, 60, 1)
schedule.every().wednesday.at("02:30").do(send, 1, 1, 0, 30, 1)
schedule.every().wednesday.at("02:50").do(send, 1, 1, 0, 10, 1)
schedule.every().wednesday.at("10:00").do(send, 1, 0, 1, 60, 2)
schedule.every().wednesday.at("10:30").do(send, 1, 0, 1, 30, 2)
schedule.every().wednesday.at("10:50").do(send, 1, 0, 1, 10, 2)
schedule.every().wednesday.at("14:00").do(send, 1, 0, 0, 60, 1)
schedule.every().wednesday.at("14:30").do(send, 1, 0, 0, 30, 1)
schedule.every().wednesday.at("14:50").do(send, 1, 0, 0, 10, 1)

schedule.every().friday.at("22:00").do(send, 1, 1, 1, 60, 2)
schedule.every().friday.at("22:30").do(send, 1, 1, 1, 30, 2)
schedule.every().friday.at("22:50").do(send, 1, 1, 1, 10, 2)
schedule.every().saturday.at("02:00").do(send, 1, 1, 0, 60, 1)
schedule.every().saturday.at("02:30").do(send, 1, 1, 0, 30, 1)
schedule.every().saturday.at("02:50").do(send, 1, 1, 0, 10, 1)
schedule.every().saturday.at("10:00").do(send, 1, 0, 1, 60, 2)
schedule.every().saturday.at("10:30").do(send, 1, 0, 1, 30, 2)
schedule.every().saturday.at("10:50").do(send, 1, 0, 1, 10, 2)
schedule.every().saturday.at("14:00").do(send, 1, 0, 0, 60, 1)
schedule.every().saturday.at("14:30").do(send, 1, 0, 0, 30, 1)
schedule.every().saturday.at("14:50").do(send, 1, 0, 0, 10, 1)

# Розсилка для 2 групи
schedule.every().monday.at("02:00").do(send, 2, 1, 1, 60, 2)
schedule.every().monday.at("02:30").do(send, 2, 1, 1, 30, 2)
schedule.every().monday.at("02:50").do(send, 2, 1, 1, 10, 2)
schedule.every().monday.at("06:00").do(send, 2, 1, 0, 60, 1)
schedule.every().monday.at("06:30").do(send, 2, 1, 0, 30, 1)
schedule.every().monday.at("06:50").do(send, 2, 1, 0, 10, 1)
schedule.every().monday.at("14:00").do(send, 2, 0, 1, 60, 2)
schedule.every().monday.at("14:30").do(send, 2, 0, 1, 30, 2)
schedule.every().monday.at("14:50").do(send, 2, 0, 1, 10, 2)
schedule.every().monday.at("18:00").do(send, 2, 0, 0, 60, 1)
schedule.every().monday.at("18:30").do(send, 2, 0, 0, 30, 1)
schedule.every().monday.at("18:50").do(send, 2, 0, 0, 10, 1)

schedule.every().thursday.at("02:00").do(send, 2, 1, 1, 60, 2)
schedule.every().thursday.at("02:30").do(send, 2, 1, 1, 30, 2)
schedule.every().thursday.at("02:50").do(send, 2, 1, 1, 10, 2)
schedule.every().thursday.at("06:00").do(send, 2, 1, 0, 60, 1)
schedule.every().thursday.at("06:30").do(send, 2, 1, 0, 30, 1)
schedule.every().thursday.at("06:50").do(send, 2, 1, 0, 10, 1)
schedule.every().thursday.at("14:00").do(send, 2, 0, 1, 60, 2)
schedule.every().thursday.at("14:30").do(send, 2, 0, 1, 30, 2)
schedule.every().thursday.at("14:50").do(send, 2, 0, 1, 10, 2)
schedule.every().thursday.at("18:00").do(send, 2, 0, 0, 60, 1)
schedule.every().thursday.at("18:30").do(send, 2, 0, 0, 30, 1)
schedule.every().thursday.at("18:50").do(send, 2, 0, 0, 10, 1)

schedule.every().sunday.at("02:00").do(send, 2, 1, 1, 60, 2)
schedule.every().sunday.at("02:30").do(send, 2, 1, 1, 30, 2)
schedule.every().sunday.at("02:50").do(send, 2, 1, 1, 10, 2)
schedule.every().sunday.at("06:00").do(send, 2, 1, 0, 60, 1)
schedule.every().sunday.at("06:30").do(send, 2, 1, 0, 30, 1)
schedule.every().sunday.at("06:50").do(send, 2, 1, 0, 10, 1)
schedule.every().sunday.at("14:00").do(send, 2, 0, 1, 60, 2)
schedule.every().sunday.at("14:30").do(send, 2, 0, 1, 30, 2)
schedule.every().sunday.at("14:50").do(send, 2, 0, 1, 10, 2)
schedule.every().sunday.at("18:00").do(send, 2, 0, 0, 60, 1)
schedule.every().sunday.at("18:30").do(send, 2, 0, 0, 30, 1)
schedule.every().sunday.at("18:50").do(send, 2, 0, 0, 10, 1)

schedule.every().monday.at("22:00").do(send, 2, 1, 1, 60, 2)
schedule.every().monday.at("22:30").do(send, 2, 1, 1, 30, 2)
schedule.every().monday.at("22:50").do(send, 2, 1, 1, 10, 2)
schedule.every().tuesday.at("02:00").do(send, 2, 1, 0, 60, 1)
schedule.every().tuesday.at("02:30").do(send, 2, 1, 0, 30, 1)
schedule.every().tuesday.at("02:50").do(send, 2, 1, 0, 10, 1)
schedule.every().tuesday.at("10:00").do(send, 2, 0, 1, 60, 2)
schedule.every().tuesday.at("10:30").do(send, 2, 0, 1, 30, 2)
schedule.every().tuesday.at("10:50").do(send, 2, 0, 1, 10, 2)
schedule.every().tuesday.at("14:00").do(send, 2, 0, 0, 60, 1)
schedule.every().tuesday.at("14:30").do(send, 2, 0, 0, 30, 1)
schedule.every().tuesday.at("14:50").do(send, 2, 0, 0, 10, 1)

schedule.every().thursday.at("22:00").do(send, 2, 1, 1, 60, 2)
schedule.every().thursday.at("22:30").do(send, 2, 1, 1, 30, 2)
schedule.every().thursday.at("22:50").do(send, 2, 1, 1, 10, 2)
schedule.every().friday.at("02:00").do(send, 2, 1, 0, 60, 1)
schedule.every().friday.at("02:30").do(send, 2, 1, 0, 30, 1)
schedule.every().friday.at("02:50").do(send, 2, 1, 0, 10, 1)
schedule.every().friday.at("10:00").do(send, 2, 0, 1, 60, 2)
schedule.every().friday.at("10:30").do(send, 2, 0, 1, 30, 2)
schedule.every().friday.at("10:50").do(send, 2, 0, 1, 10, 2)
schedule.every().friday.at("14:00").do(send, 2, 0, 0, 60, 1)
schedule.every().friday.at("14:30").do(send, 2, 0, 0, 30, 1)
schedule.every().friday.at("14:50").do(send, 2, 0, 0, 10, 1)

schedule.every().tuesday.at("22:00").do(send, 2, 1, 0, 60, 1)
schedule.every().tuesday.at("22:30").do(send, 2, 1, 0, 30, 1)
schedule.every().tuesday.at("22:50").do(send, 2, 1, 0, 10, 1)
schedule.every().wednesday.at("06:00").do(send, 2, 0, 1, 60, 2)
schedule.every().wednesday.at("06:30").do(send, 2, 0, 1, 30, 2)
schedule.every().wednesday.at("06:50").do(send, 2, 0, 1, 10, 2)
schedule.every().wednesday.at("10:00").do(send, 2, 0, 0, 60, 1)
schedule.every().wednesday.at("10:30").do(send, 2, 0, 0, 30, 1)
schedule.every().wednesday.at("10:50").do(send, 2, 0, 0, 10, 1)
schedule.every().wednesday.at("18:00").do(send, 2, 0, 1, 60, 2)
schedule.every().wednesday.at("18:30").do(send, 2, 0, 1, 30, 2)
schedule.every().wednesday.at("18:50").do(send, 2, 0, 1, 10, 2)

schedule.every().friday.at("22:00").do(send, 2, 1, 0, 60, 1)
schedule.every().friday.at("22:30").do(send, 2, 1, 0, 30, 1)
schedule.every().friday.at("22:50").do(send, 2, 1, 0, 10, 1)
schedule.every().saturday.at("06:00").do(send, 2, 0, 1, 60, 2)
schedule.every().saturday.at("06:30").do(send, 2, 0, 1, 30, 2)
schedule.every().saturday.at("06:50").do(send, 2, 0, 1, 10, 2)
schedule.every().saturday.at("10:00").do(send, 2, 0, 0, 60, 1)
schedule.every().saturday.at("10:30").do(send, 2, 0, 0, 30, 1)
schedule.every().saturday.at("10:50").do(send, 2, 0, 0, 10, 1)
schedule.every().saturday.at("18:00").do(send, 2, 0, 1, 60, 2)
schedule.every().saturday.at("18:30").do(send, 2, 0, 1, 30, 2)
schedule.every().saturday.at("18:50").do(send, 2, 0, 1, 10, 2)

# Розсилка для 3 групи
schedule.every().sunday.at("22:00").do(send, 3, 1, 1, 60, 2)
schedule.every().sunday.at("22:30").do(send, 3, 1, 1, 30, 2)
schedule.every().sunday.at("22:50").do(send, 3, 1, 1, 10, 2)
schedule.every().monday.at("02:00").do(send, 3, 1, 0, 60, 1)
schedule.every().monday.at("02:30").do(send, 3, 1, 0, 30, 1)
schedule.every().monday.at("02:50").do(send, 3, 1, 0, 10, 1)
schedule.every().monday.at("10:00").do(send, 3, 0, 1, 60, 2)
schedule.every().monday.at("10:30").do(send, 3, 0, 1, 30, 2)
schedule.every().monday.at("10:50").do(send, 3, 0, 1, 10, 2)
schedule.every().monday.at("14:00").do(send, 3, 0, 0, 60, 1)
schedule.every().monday.at("14:30").do(send, 3, 0, 0, 30, 1)
schedule.every().monday.at("14:50").do(send, 3, 0, 0, 10, 1)

schedule.every().wednesday.at("22:00").do(send, 3, 1, 1, 60, 2)
schedule.every().wednesday.at("22:30").do(send, 3, 1, 1, 30, 2)
schedule.every().wednesday.at("22:50").do(send, 3, 1, 1, 10, 2)
schedule.every().thursday.at("02:00").do(send, 3, 1, 0, 60, 1)
schedule.every().thursday.at("02:30").do(send, 3, 1, 0, 30, 1)
schedule.every().thursday.at("02:50").do(send, 3, 1, 0, 10, 1)
schedule.every().thursday.at("10:00").do(send, 3, 0, 1, 60, 2)
schedule.every().thursday.at("10:30").do(send, 3, 0, 1, 30, 2)
schedule.every().thursday.at("10:50").do(send, 3, 0, 1, 10, 2)
schedule.every().thursday.at("14:00").do(send, 3, 0, 0, 60, 1)
schedule.every().thursday.at("14:30").do(send, 3, 0, 0, 30, 1)
schedule.every().thursday.at("14:50").do(send, 3, 0, 0, 10, 1)

schedule.every().saturday.at("22:00").do(send, 3, 1, 1, 60, 2)
schedule.every().saturday.at("22:30").do(send, 3, 1, 1, 30, 2)
schedule.every().saturday.at("22:50").do(send, 3, 1, 1, 10, 2)
schedule.every().sunday.at("02:00").do(send, 3, 1, 0, 60, 1)
schedule.every().sunday.at("02:30").do(send, 3, 1, 0, 30, 1)
schedule.every().sunday.at("02:50").do(send, 3, 1, 0, 10, 1)
schedule.every().sunday.at("10:00").do(send, 3, 0, 1, 60, 2)
schedule.every().sunday.at("10:30").do(send, 3, 0, 1, 30, 2)
schedule.every().sunday.at("10:50").do(send, 3, 0, 1, 10, 2)
schedule.every().sunday.at("14:00").do(send, 3, 0, 0, 60, 1)
schedule.every().sunday.at("14:30").do(send, 3, 0, 0, 30, 1)
schedule.every().sunday.at("14:50").do(send, 3, 0, 0, 10, 1)

schedule.every().monday.at("22:00").do(send, 3, 1, 0, 60, 1)
schedule.every().monday.at("22:30").do(send, 3, 1, 0, 30, 1)
schedule.every().monday.at("22:50").do(send, 3, 1, 0, 10, 1)
schedule.every().tuesday.at("06:00").do(send, 3, 0, 1, 60, 2)
schedule.every().tuesday.at("06:30").do(send, 3, 0, 1, 30, 2)
schedule.every().tuesday.at("06:50").do(send, 3, 0, 1, 10, 2)
schedule.every().tuesday.at("10:00").do(send, 3, 0, 0, 60, 1)
schedule.every().tuesday.at("10:30").do(send, 3, 0, 0, 30, 1)
schedule.every().tuesday.at("10:50").do(send, 3, 0, 0, 10, 1)
schedule.every().tuesday.at("18:00").do(send, 3, 0, 1, 60, 2)
schedule.every().tuesday.at("18:30").do(send, 3, 0, 1, 30, 2)
schedule.every().tuesday.at("18:50").do(send, 3, 0, 1, 10, 2)

schedule.every().thursday.at("22:00").do(send, 3, 1, 0, 60, 1)
schedule.every().thursday.at("22:30").do(send, 3, 1, 0, 30, 1)
schedule.every().thursday.at("22:50").do(send, 3, 1, 0, 10, 1)
schedule.every().friday.at("06:00").do(send, 3, 0, 1, 60, 2)
schedule.every().friday.at("06:30").do(send, 3, 0, 1, 30, 2)
schedule.every().friday.at("06:50").do(send, 3, 0, 1, 10, 2)
schedule.every().friday.at("10:00").do(send, 3, 0, 0, 60, 1)
schedule.every().friday.at("10:30").do(send, 3, 0, 0, 30, 1)
schedule.every().friday.at("10:50").do(send, 3, 0, 0, 10, 1)
schedule.every().friday.at("18:00").do(send, 3, 0, 1, 60, 2)
schedule.every().friday.at("18:30").do(send, 3, 0, 1, 30, 2)
schedule.every().friday.at("18:50").do(send, 3, 0, 1, 10, 2)

schedule.every().wednesday.at("02:00").do(send, 3, 1, 1, 60, 2)
schedule.every().wednesday.at("02:30").do(send, 3, 1, 1, 30, 2)
schedule.every().wednesday.at("02:50").do(send, 3, 1, 1, 10, 2)
schedule.every().wednesday.at("06:00").do(send, 3, 1, 0, 60, 1)
schedule.every().wednesday.at("06:30").do(send, 3, 1, 0, 30, 1)
schedule.every().wednesday.at("06:50").do(send, 3, 1, 0, 10, 1)
schedule.every().wednesday.at("14:00").do(send, 3, 0, 1, 60, 2)
schedule.every().wednesday.at("14:30").do(send, 3, 0, 1, 30, 2)
schedule.every().wednesday.at("14:50").do(send, 3, 0, 1, 10, 2)
schedule.every().wednesday.at("18:00").do(send, 3, 0, 0, 60, 1)
schedule.every().wednesday.at("18:30").do(send, 3, 0, 0, 30, 1)
schedule.every().wednesday.at("18:50").do(send, 3, 0, 0, 10, 1)

schedule.every().saturday.at("02:00").do(send, 3, 1, 1, 60, 2)
schedule.every().saturday.at("02:30").do(send, 3, 1, 1, 30, 2)
schedule.every().saturday.at("02:50").do(send, 3, 1, 1, 10, 2)
schedule.every().saturday.at("06:00").do(send, 3, 1, 0, 60, 1)
schedule.every().saturday.at("06:30").do(send, 3, 1, 0, 30, 1)
schedule.every().saturday.at("06:50").do(send, 3, 1, 0, 10, 1)
schedule.every().saturday.at("14:00").do(send, 3, 0, 1, 60, 2)
schedule.every().saturday.at("14:30").do(send, 3, 0, 1, 30, 2)
schedule.every().saturday.at("14:50").do(send, 3, 0, 1, 10, 2)
schedule.every().saturday.at("18:00").do(send, 3, 0, 0, 60, 1)
schedule.every().saturday.at("18:30").do(send, 3, 0, 0, 30, 1)
schedule.every().saturday.at("18:50").do(send, 3, 0, 0, 10, 1)
# schedule.every(5).seconds.do(send, 3, 1, 1, 10, 1)


# Робота розсилки(інший потік)
def threaded_function():
    while True:
        schedule.run_pending()
        time.sleep(1)


thread = Thread(target=threaded_function)
thread.daemon = True
thread.start()


@bot.callback_query_handler(func=lambda call: True)
@locked
def callback_inline(call):
    connect = connect_db()
    cursor = connect.cursor()
    person_id = call.message.chat.id
    message_id = call.message.message_id

# Підключення до сповіщень
    if call.data.startswith('group'):
        number = call.data[5:]
        group_number = {1: "1️⃣", 2: "2️⃣", 3: "3️⃣"}.get(int(number), int(number))
        data = cursor.execute(f"SELECT user_id, group_number FROM database WHERE user_id = {person_id}").fetchone()
        if data is None:
            cursor.execute("INSERT INTO database (user_id, group_number) VALUES(?, ?)", (person_id, number,))
        elif data[1] == int(number):
            try:
                bot.delete_message(person_id, message_id)
                bot.send_message(person_id, f'✅ Ви вже підключені до сповіщень цієї групи, ваша група - {group_number}! \n\nМЕНЮ:', reply_markup=k.main_menu())
            except telebot.apihelper.ApiTelegramException:
                pass
        else:
            cursor.execute("UPDATE database SET group_number = ? WHERE user_id = ?", (number, person_id,))
        data_settings = cursor.execute(f"SELECT time_to, night FROM database WHERE user_id = {person_id}").fetchone()
        if data_settings[1] == 0:
            night = "🔕 Задля вашого ж комфорту, сповіщення не будуть надсилатися в нічний період(з 00:00 до 07:59)."
        elif data_settings[1] == 1:
            night = "🌙 Також вам будуть надсилатися сповіщення в нічний період(з 00:00 до 07:59)."
        try:
            bot.delete_message(person_id, message_id)
            bot.send_message(person_id, f'✅ Ви успішно підключилися до сповіщень {group_number} групи! \n\n🕐 Відтепер ви будете отримувати сповіщення за {data_settings[0]} хвилин до відключення світла. \n{night} \n\nЩоб змінити групу, натисніть на кнопку "🔁 Змінити групу" нижче.', reply_markup=k.main_menu())
        except telebot.apihelper.ApiTelegramException:
            pass
        connect.commit()

    # Сповіщення про можливі відключення
    elif call.data == 'maybe_notice':
        data = cursor.execute(f"SELECT maybe FROM database WHERE user_id = {person_id}").fetchone()
        markup, text = k.change_maybe(data[0])
        try:
            bot.edit_message_text(text, reply_markup=markup, chat_id=person_id, message_id=message_id)
        except telebot.apihelper.ApiTelegramException:
            pass

    elif call.data.startswith("maybe_notice_"):
        if call.data[13:] == "on":
            maybe = 1
            text = "✅ Ви успішно включили"
        else:
            maybe = 0
            text = "❌ Ви відключили"
        cursor.execute(f"UPDATE database SET maybe = {maybe} WHERE user_id = {person_id}")
        try:
            bot.edit_message_text(f"{text} сповіщення про можливі відключення світла. \n\n⚙ НАЛАШТУВАННЯ:", reply_markup=k.settings(), chat_id=person_id, message_id=message_id)
        except telebot.apihelper.ApiTelegramException:
            pass
        connect.commit()

# Нічні сповіщення
    elif call.data == 'night_notice':
        data = cursor.execute(f"SELECT night FROM database WHERE user_id = {person_id}").fetchone()
        markup, text = k.change_night(data[0])
        try:
            bot.edit_message_text(text, reply_markup=markup, chat_id=person_id, message_id=message_id)
        except telebot.apihelper.ApiTelegramException:
            pass

    elif call.data.startswith("night_notice_"):
        if call.data[13:] == "on":
            night = 1
            text = "✅ Ви успішно включили"
        else:
            night = 0
            text = "❌ Ви виключили"
        cursor.execute(f"UPDATE database SET night = {night} WHERE user_id = {person_id}")
        try:
            bot.edit_message_text(f"{text} нічні сповіщення. \n\n⚙ НАЛАШТУВАННЯ:", reply_markup=k.settings(), chat_id=person_id, message_id=message_id)
        except telebot.apihelper.ApiTelegramException:
            pass
        connect.commit()

# Час до надсилання сповіщень
    elif call.data == "time_to_notice":
        data = cursor.execute(f"SELECT time_to FROM database WHERE user_id = {person_id}").fetchone()
        markup, text = k.change_time(data[0])
        try:
            bot.edit_message_text(f"🕐 ЧАС ДО НАДСИЛАННЯ СПОВІЩЕННЯ: \n\n• Тут ви можете змінити час до надсилання сповіщень, від 10 до 60 хвилин.\n• На цей момент сповіщенням вам будуть надсилатися за {text} хвилин до відключення світла, щоб змінити, натисніть на одну з кнопок нижче:", reply_markup=markup, chat_id=person_id, message_id=message_id)
        except telebot.apihelper.ApiTelegramException:
            pass

    elif call.data.startswith('set_'):
        data = cursor.execute(f"SELECT time_to FROM database WHERE user_id = {person_id}").fetchone()
        if data[0] != int(call.data[4:6]):
            cursor.execute(f"UPDATE database SET time_to = {call.data[4:6]} WHERE user_id = {person_id}")
            markup, text = k.change_time(call.data[4:6])
            try:
                bot.edit_message_text(f'✅ Ви успішно змінили час до надсилання сповіщень до {text} хвилин. \n\n⚙ НАЛАШТУВАННЯ:', reply_markup=k.settings(), chat_id=person_id, message_id=message_id)
            except telebot.apihelper.ApiTelegramException:
                pass
            connect.commit()
        else:
            try:
                bot.edit_message_text(f'✅ Час до надсилання сповіщень вже дорівнює {data[0]} хвилинам. \n\n⚙ НАЛАШТУВАННЯ:', reply_markup=k.settings(), chat_id=person_id, message_id=message_id)
            except telebot.apihelper.ApiTelegramException:
                pass

    elif call.data == 'back_to_settings':
        try:
            bot.edit_message_text("⚙ НАЛАШТУВАННЯ:", reply_markup=k.settings(), chat_id=person_id, message_id=message_id)
        except telebot.apihelper.ApiTelegramException:
            pass

    elif call.data == 'back_to_menu':
        try:
            bot.edit_message_text("МЕНЮ:", reply_markup=None, chat_id=person_id, message_id=message_id)
        except telebot.apihelper.ApiTelegramException:
            pass


bot.polling(non_stop=True)
