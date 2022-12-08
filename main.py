#  ENERGYLOEBOT version 0.8 by dariusua

import sqlite3
import time
import telebot
import schedule
import logging
from datetime import datetime, timedelta
from telebot import types
from threading import Thread
from config import TOKEN

logging.basicConfig(level=logging.INFO)
bot = telebot.TeleBot(TOKEN)

markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
item1 = types.KeyboardButton("✅ Підключити сповіщення")
item2 = types.KeyboardButton("🔕 Відключити сповіщення")
item3 = types.KeyboardButton("📖 Повний графік(фото)")
item4 = types.KeyboardButton("⚙ Налаштування")
markup.add(item1, item2).row(item3).add(item4)

# Початок роботи, створення бази даних
@bot.message_handler(commands=['start'])
def start(message: types.Message):
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS database(
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        [group_number] INTEGER NOT NULL,
        active INTEGER DEFAULT(1)
    )""")
    connect.commit()
    bot.send_message(message.from_user.id, f'Привіт 👋 \n\n🤖 Цей бот створений задля сповіщення користувачів "Львівобленерго" про планові відключення у вашому населеному пункті. \n✏️ Бот буде відсилати повідомлення з попередженням за 30 хвилин до відключення світла. \n❗️ Бот не є офіційним! \n\n📋 Для підключення сповіщень, натисніть на кнопку "✅ Підключити сповіщення" нижче.', reply_markup=markup)

# Функція розсилки через команду
@bot.message_handler(commands=['send'])
def send(message: types.Message):
    if message.from_user.id == 880691612:
        connect = sqlite3.connect('database.db')
        cursor = connect.cursor()
        results = cursor.execute("SELECT user_id FROM database").fetchall()
        text = message.text[6:]
        for row in results:
            active_value = row[0]
            set_active = cursor.execute("SELECT active FROM database WHERE user_id = ?", (active_value,))
            try:
                bot.send_message(row[0], {text})
                if set_active != 1:
                    cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("1", active_value))
            except:
                cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("0", active_value))
        bot.send_message(880691612, f"ПОВІДОМЛЕННЯ ПРО РОЗСИЛКУ: \n\n{text}")
    else:
        bot.send_message(message.from_user.id, "Для виконання цієї команди Ви повинні бути адміном.")
    connect.commit()

# Робота кнопок
@bot.message_handler(content_types='text')
def message_reply(message: types.Message):
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    person_id = message.chat.id

# Підключення сповіщень
    if message.text == "✅ Підключити сповіщення":
        markup_group = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton(text="Група 1", callback_data='group1')
        item2 = types.InlineKeyboardButton(text="Група 2", callback_data='group2')
        item3 = types.InlineKeyboardButton(text="Група 3", callback_data='group3')
        learngroup = types.InlineKeyboardButton(text="Дізнатись свою групу", url='https://poweroff.loe.lviv.ua')
        markup_group.add(item1, item2, item3, learngroup)
        bot.send_message(message.chat.id, f'✅ Для підключення сповіщень про відключення світла Вам необхідно натиснути на кнопку з номером вашої групи. \n❓ Щоб дізнатись номер вашої групи, натисніть на кнопку "Дізнатись свою групу", та перейшовши за посиланням і ввівши свої дані, ви зможете дізнатись свою групу.', reply_markup=markup_group)

# Відключити сповіщень
    elif message.text == "🔕 Відключити сповіщення":
        if message.from_user.username is None:
            if message.from_user.last_name is None:
                loginchat = f"{message.from_user.first_name}"
            else:
                loginchat = f"{message.from_user.first_name} {message.from_user.last_name}"
        else:
            loginchat = f"@{message.from_user.username}"
        cursor.execute("DELETE FROM `database` WHERE `user_id` = ?", (person_id,))
        bot.send_message(message.from_user.id, '❌ Ви відключилися від сповіщень про відключення електроенергії. Дякуємо за використання бота!😢 \n\nЩоб підключитись знову, натисніть на кнопку "✅ Підключити сповіщення" нижче.', reply_markup=markup)
        bot.send_message(880691612, f"{loginchat} відключився(-лась) від сповіщень")

# Надсилання фото з графіком відключень
    elif message.text == "📖 Повний графік(фото)":
        cursor.execute("SELECT group_number FROM database WHERE user_id = ?", (message.from_user.id,))
        data = cursor.fetchone()
        if data == "1":
            photo = open('1group.png', 'rb')
            bot.send_photo(message.from_user.id, photo)
        elif data == "2":
            photo = open('2group.png', 'rb')
            bot.send_photo(message.from_user.id, photo)
        elif data == "3":
            photo = open('3group.png', 'rb')
            bot.send_photo(message.from_user.id, photo)
        connect.commit()

# Налаштування
    elif message.text == "⚙ Налаштування":
        markup_settings = types.ReplyKeyboardMarkup(resize_keyboard=True)
        #    item1 = types.KeyboardButton("🌙 Включити нічні сповіщення")
        #    item2 = types.KeyboardButton("Включити сповіщення про можливі відключення")
        #    item3 = types.KeyboardButton("Кнопка")
        item4 = types.KeyboardButton("⬅ Назад")
        #    markup_settings.add(item1, item2, item3, item4)
        markup_settings.add(item4)
        bot.send_message(message.from_user.id, "Нажаль, ця команда тимчасово недоступна.", reply_markup=markup_settings)

    elif message.text == "⬅ Назад":
        bot.send_message(message.from_user.id, "МЕНЮ:", reply_markup=markup)

    elif message.text == "/start":
        pass

    elif message.text == "/send":
        pass

    else:
        bot.send_message(message.from_user.id, "Цієї команди не існує.")

#Функція розсилки для 1 групи
def send_g1():
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    results = cursor.execute("SELECT user_id FROM database WHERE group_number = ?", ("1")).fetchall()
    howmuchtime1 = datetime.now() + timedelta(minutes=150)
    howmuchtime2 = howmuchtime1 + timedelta(hours=4)
    text = f"‼ За графіком 1️⃣ групи планується відключення світла в період з {howmuchtime1.strftime('%H:%M')} до {howmuchtime2.strftime('%H:%M')}!"
    for row in results:
        active_value = row[0]
        set_active = cursor.execute("SELECT active FROM database WHERE user_id = ?", (active_value,))
        try:
            bot.send_message(row[0], {text})
            if set_active != 1:
                cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("1", active_value))
        except:
            cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("0", active_value))
    bot.send_message(880691612, f"ПОВІДОМЛЕННЯ ПРО РОЗСИЛКУ: \n\n{text}")
    connect.commit()

#Функція розсилки для 2 групи
def send_g2():
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    results = cursor.execute("SELECT user_id FROM database WHERE group_number = ?", ("2")).fetchall()
    howmuchtime1 = datetime.now() + timedelta(minutes=150)
    howmuchtime2 = howmuchtime1 + timedelta(hours=4)
    text = f"‼ За графіком 2️⃣ групи планується відключення світла в період з {howmuchtime1.strftime('%H:%M')} до {howmuchtime2.strftime('%H:%M')}!"
    for row in results:
        active_value = row[0]
        set_active = cursor.execute("SELECT active FROM database WHERE user_id = ?", (active_value,))
        try:
            bot.send_message(row[0], {text})
            if set_active != 1:
                cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("1", active_value))
        except:
            cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("0", active_value))
    bot.send_message(880691612, f"ПОВІДОМЛЕННЯ ПРО РОЗСИЛКУ: \n\n{text}")
    connect.commit()

#Функція розсилки для 3 групи
def send_g3():
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    results = cursor.execute("SELECT user_id FROM database WHERE group_number = ?", ("3")).fetchall()
    howmuchtime1 = datetime.now() + timedelta(minutes=150)
    howmuchtime2 = howmuchtime1 + timedelta(hours=4)
    text = f"‼ За графіком 3️⃣ групи планується відключення світла в період з {howmuchtime1.strftime('%H:%M')} до {howmuchtime2.strftime('%H:%M')}!"
    for row in results:
        active_value = row[0]
        set_active = cursor.execute("SELECT active FROM database WHERE user_id = ?", (active_value,))
        try:
            bot.send_message(row[0], {text})
            if set_active != 1:
                cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("1", active_value))
        except:
            cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("0", active_value))
    bot.send_message(880691612, f"ПОВІДОМЛЕННЯ ПРО РОЗСИЛКУ: \n\n{text}")
    connect.commit()

# time_for_sched = datetime.now() + timedelta(minutes=1)
# time_for_sched1 = time_for_sched.strftime('%H:%M')

#Розсилка для 1 групи
schedule.every().monday.at("10:30").do(send_g1)
schedule.every().tuesday.at("06:30").do(send_g1)
schedule.every().tuesday.at("18:30").do(send_g1)
schedule.every().wednesday.at("14:30").do(send_g1)
schedule.every().thursday.at("10:30").do(send_g1)
schedule.every().friday.at("06:30").do(send_g1)
schedule.every().friday.at("18:30").do(send_g1)
schedule.every().saturday.at("14:30").do(send_g1)
schedule.every().sunday.at("10:30").do(send_g1)

#Розсилка для 2 групи
schedule.every().monday.at("06:30").do(send_g2)
schedule.every().monday.at("18:30").do(send_g2)
schedule.every().tuesday.at("14:30").do(send_g2)
schedule.every().wednesday.at("10:30").do(send_g2)
schedule.every().thursday.at("06:30").do(send_g2)
schedule.every().thursday.at("18:30").do(send_g2)
schedule.every().friday.at("14:30").do(send_g2)
schedule.every().saturday.at("10:30").do(send_g2)
schedule.every().sunday.at("06:30").do(send_g2)
schedule.every().sunday.at("18:30").do(send_g2)

#Розсилка для 3 групи
schedule.every().monday.at("14:30").do(send_g3)
schedule.every().tuesday.at("10:30").do(send_g3)
schedule.every().wednesday.at("06:30").do(send_g3)
schedule.every().wednesday.at("18:30").do(send_g3)
schedule.every().thursday.at("14:30").do(send_g3)
schedule.every().friday.at("10:30").do(send_g3)
schedule.every().saturday.at("06:30").do(send_g3)
schedule.every().saturday.at("18:30").do(send_g3)
schedule.every().sunday.at("14:30").do(send_g3)

#Робота розсилки(інший потік)
def threaded_function():
    while True:
        schedule.run_pending()
        time.sleep(1)

thread = Thread(target = threaded_function)
thread.daemon = True
thread.start()

@bot.callback_query_handler(func=lambda call:True)
def callback_query(call):
    req = call.data.split('_')
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    person_id = call.message.chat.id

# Підключення до 1 групи
    if req[0] == 'group1':
        if call.message.chat.username is None:
            if call.message.chat.last_name is None:
                loginchat = f"{call.message.chat.first_name}"
            else:
                loginchat = f"{call.message.chat.first_name} {call.message.chat.last_name}"
        else:
            loginchat = f"@{call.message.chat.username}"
        cursor.execute(f"SELECT user_id FROM database WHERE user_id = {person_id}")
        data = cursor.fetchone()
        user_id = call.message.chat.id
        if data is None:
            cursor.execute("INSERT INTO database VALUES(?, ?, ?);", (user_id, "1", "1", "0",))
        else:
            cursor.execute("UPDATE database SET group_number = ? WHERE user_id = ?", ("1", user_id,))
        connect.commit()
        bot.edit_message_text(f'✅ Ви успішно підключилися до сповіщень 1️⃣ групи! \n\n🕐 Відтепер ви будете отримувати сповіщення за 30 хвилин до відключення світла. \n🔕 Задля вашого ж комфорту, сповіщення не будуть надсилатися в нічний період(з 00:00 до 08:00). \n\n Щоб змінити групу, натисніть на кнопку "✅ Підключити сповіщення" нижче.', reply_markup=markup_del, chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(880691612, f"{loginchat} підключився(-лась) до 1 групи")

# Підключення до 2 групи
    elif req[0] == 'group2':
        if call.message.chat.username is None:
            if call.message.chat.last_name is None:
                loginchat = f"{call.message.chat.first_name}"
            else:
                loginchat = f"{call.message.chat.first_name} {call.message.chat.last_name}"
        else:
            loginchat = f"@{call.message.chat.username}"
        cursor.execute(f"SELECT user_id FROM database WHERE user_id = {person_id}")
        data = cursor.fetchone()
        user_id = call.message.chat.id
        if data is None:
            cursor.execute("INSERT INTO database VALUES(?, ?, ?);", (user_id, "2", "1", "0",))
        else:
            cursor.execute("UPDATE database SET group_number = ? WHERE user_id = ?", ("2", user_id,))
        connect.commit()
        bot.edit_message_text(f'✅ Ви успішно підключилися до сповіщень 2️⃣ групи! \n\n🕐 Відтепер ви будете отримувати сповіщення за 30 хвилин до відключення світла. \n🔕 Задля вашого ж комфорту, сповіщення не будуть надсилатися в нічний період(з 00:00 до 08:00). \n\n Щоб змінити групу, натисніть на кнопку "✅ Підключити сповіщення" нижче.', reply_markup=markup_del, chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(880691612, f"{loginchat} підключився(-лась) до 2 групи")

# Підключення до 3 групи
    if req[0] == 'group3':
        if call.message.chat.username is None:
            if call.message.chat.last_name is None:
                loginchat = f"{call.message.chat.first_name}"
            else:
                loginchat = f"{call.message.chat.first_name} {call.message.chat.last_name}"
        else:
            loginchat = f"@{call.message.chat.username}"
        cursor.execute(f"SELECT user_id FROM database WHERE user_id = {person_id}")
        data = cursor.fetchone()
        user_id = call.message.chat.id
        if data is None:
            cursor.execute("INSERT INTO database VALUES(?, ?, ?);", (user_id, "3", "1", "0",))
        else:
            cursor.execute("UPDATE database SET group_number = ? WHERE user_id = ?", ("3", user_id,))
        connect.commit()
        bot.edit_message_text(f'✅ Ви успішно підключилися до сповіщень 3️⃣ групи! \n\n🕐 Відтепер ви будете отримувати сповіщення за 30 хвилин до відключення світла. \n🔕 Задля вашого ж комфорту, сповіщення не будуть надсилатися в нічний період(з 00:00 до 08:00). \n\n Щоб змінити групу, натисніть на кнопку "✅ Підключити сповіщення" нижче.', reply_markup=None, chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(880691612, f"{loginchat} підключився(-лась) до 3 групи")

bot.polling()