#  ENERGYLOEBOT version 0.9 by dariusua

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
bot = telebot.TeleBot("5976583067:AAHW-opSW5CAL_7ZxNzx_wRXFD1JMyTlrq4")
#bot = telebot.TeleBot(TOKEN)

markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
item1 = types.KeyboardButton("✅ Підключити сповіщення")
item2 = types.KeyboardButton("🔕 Відключити сповіщення")
item3 = types.KeyboardButton("📖 Повний графік(фото)")
item4 = types.KeyboardButton("⚙ Налаштування")
markup.add(item1, item2).row(item3).add(item4)

markup_settings = types.InlineKeyboardMarkup(row_width = 1)
item1 = types.InlineKeyboardButton(text="🌙 Нічні сповіщення", callback_data='night_notice')
item2 = types.InlineKeyboardButton(text="🔘 Сповіщення про можливі відключення", callback_data='maybe_notice')
item3 = types.InlineKeyboardButton(text="🕐 Час до надсилання сповіщення", callback_data='change_time_to_notice')
item4 = types.InlineKeyboardButton(text="⬅ Назад", callback_data='back')
markup_settings.add(item1, item2, item3, item4)

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
    # night INTEGER DEFAULT(0)
    # maybe INTEGER DEFAULT(0)
    # time_to INTEGER DEFAULT(30)
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
        learngroup = types.InlineKeyboardButton(text="Дізнатись свою групу", url='https://poweroff.loe.lviv.ua/gav_city3')
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
        data_photo = cursor.execute("SELECT group_number FROM database WHERE user_id = ?", (message.from_user.id,)).fetchone()
        try:
            if data_photo[0] == 1:
                photo = open('1group.png', 'rb')
                bot.send_photo(message.from_user.id, photo)
            elif data_photo[0] == 2:
                photo = open('2group.png', 'rb')
                bot.send_photo(message.from_user.id, photo)
            elif data_photo[0] == 3:
                photo = open('3group.png', 'rb')
                bot.send_photo(message.from_user.id, photo)
        except:
            bot.send_message(message.from_user.id, "Помилка! Попробуйте підключитись до вашої групи.")
        connect.commit()

# Налаштування
    elif message.text == "⚙ Налаштування":
        bot.send_message(message.from_user.id, "⚙ НАЛАШТУВАННЯ:", reply_markup=markup_settings)

    elif message.text == "⬅ Назад":
        bot.send_message(message.from_user.id, "МЕНЮ:", reply_markup=markup)

    elif message.text == "/start":
        pass

    elif message.text == "/send":
        pass

    else:
        bot.send_message(message.from_user.id, "Цієї команди не існує.")

# Функція розсилки для 1 групи
def send10_g1():
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    results = cursor.execute("SELECT user_id FROM database WHERE group_number = '1' AND time_to = '10'").fetchall()
    howmuchtime1 = datetime.now() + timedelta(minutes=130)
    howmuchtime2 = howmuchtime1 + timedelta(hours=4)
    text = f"‼ За графіком 1️⃣ групи планується відключення світла в період з {howmuchtime1.strftime('%H:%M')} до {howmuchtime2.strftime('%H:%M')}!"
    for row in results:
        active_value = row[0]
        set_active = cursor.execute("SELECT active FROM database WHERE user_id = ?", (active_value,))
        try:
            bot.send_message(row[0], text)
            if set_active != 1:
                cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("1", active_value))
        except:
            cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("0", active_value))
            time.sleep(1)
    bot.send_message(880691612, f"ПОВІДОМЛЕННЯ ПРО РОЗСИЛКУ: \n\n{text}")
    connect.commit()

def send30_g1():
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    results = cursor.execute("SELECT user_id FROM database WHERE group_number = '1' AND time_to = '30'").fetchall()
    howmuchtime1 = datetime.now() + timedelta(minutes=150)
    howmuchtime2 = howmuchtime1 + timedelta(hours=4)
    text = f"‼ За графіком 1️⃣ групи планується відключення світла в період з {howmuchtime1.strftime('%H:%M')} до {howmuchtime2.strftime('%H:%M')}!"
    for row in results:
        active_value = row[0]
        set_active = cursor.execute("SELECT active FROM database WHERE user_id = ?", (active_value,))
        try:
            bot.send_message(row[0], text)
            if set_active != 1:
                cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("1", active_value))
        except:
            cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("0", active_value))
            time.sleep(1)
    connect.commit()

def send60_g1():
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    results = cursor.execute("SELECT user_id FROM database WHERE group_number = '1' AND time_to = '60'").fetchall()
    howmuchtime1 = datetime.now() + timedelta(minutes=180)
    howmuchtime2 = howmuchtime1 + timedelta(hours=4)
    text = f"‼ За графіком 1️⃣ групи планується відключення світла в період з {howmuchtime1.strftime('%H:%M')} до {howmuchtime2.strftime('%H:%M')}!"
    for row in results:
        active_value = row[0]
        set_active = cursor.execute("SELECT active FROM database WHERE user_id = ?", (active_value,))
        try:
            bot.send_message(row[0], text)
            if set_active != 1:
                cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("1", active_value))
        except:
            cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("0", active_value))
            time.sleep(1)
    connect.commit()

# Функція розсилки для 2 групи
def send10_g2():
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    results = cursor.execute("SELECT user_id FROM database WHERE group_number = '2' AND time_to = '10'").fetchall()
    howmuchtime1 = datetime.now() + timedelta(minutes=130)
    howmuchtime2 = howmuchtime1 + timedelta(hours=4)
    text = f"‼ За графіком 2️⃣ групи планується відключення світла в період з {howmuchtime1.strftime('%H:%M')} до {howmuchtime2.strftime('%H:%M')}!"
    for row in results:
        active_value = row[0]
        set_active = cursor.execute("SELECT active FROM database WHERE user_id = ?", (active_value,))
        try:
            bot.send_message(row[0], text)
            if set_active != 1:
                cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("1", active_value))
        except:
            cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("0", active_value))
            time.sleep(1)
    connect.commit()


def send30_g2():
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    results = cursor.execute("SELECT user_id FROM database WHERE group_number = '2' AND time_to = '30'").fetchall()
    howmuchtime1 = datetime.now() + timedelta(minutes=150)
    howmuchtime2 = howmuchtime1 + timedelta(hours=4)
    text = f"‼ За графіком 2️⃣ групи планується відключення світла в період з {howmuchtime1.strftime('%H:%M')} до {howmuchtime2.strftime('%H:%M')}!"
    for row in results:
        active_value = row[0]
        set_active = cursor.execute("SELECT active FROM database WHERE user_id = ?", (active_value,))
        try:
            bot.send_message(row[0], text)
            if set_active != 1:
                cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("1", active_value))
        except:
            cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("0", active_value))
            time.sleep(1)
    connect.commit()


def send60_g2():
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    results = cursor.execute("SELECT user_id FROM database WHERE group_number = '2' AND time_to = '60'").fetchall()
    howmuchtime1 = datetime.now() + timedelta(minutes=180)
    howmuchtime2 = howmuchtime1 + timedelta(hours=4)
    text = f"‼ За графіком 2️⃣ групи планується відключення світла в період з {howmuchtime1.strftime('%H:%M')} до {howmuchtime2.strftime('%H:%M')}!"
    for row in results:
        active_value = row[0]
        set_active = cursor.execute("SELECT active FROM database WHERE user_id = ?", (active_value,))
        try:
            bot.send_message(row[0], text)
            if set_active != 1:
                cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("1", active_value))
        except:
            cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("0", active_value))
            time.sleep(1)
    connect.commit()

# Функція розсилки для 3 групи
def send10_g3():
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    results = cursor.execute("SELECT user_id FROM database WHERE group_number = '3' AND time_to = '10'").fetchall()
    howmuchtime1 = datetime.now() + timedelta(minutes=130)
    howmuchtime2 = howmuchtime1 + timedelta(hours=4)
    text = f"‼ За графіком 3️⃣ групи планується відключення світла в період з {howmuchtime1.strftime('%H:%M')} до {howmuchtime2.strftime('%H:%M')}!"
    for row in results:
        active_value = row[0]
        set_active = cursor.execute("SELECT active FROM database WHERE user_id = ?", (active_value,))
        try:
            bot.send_message(row[0], text)
            if set_active != 1:
                cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("1", active_value))
        except:
            cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("0", active_value))
            time.sleep(1)
    connect.commit()

def send30_g3():
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    results = cursor.execute("SELECT user_id FROM database WHERE group_number = '3' AND time_to = '30'").fetchall()
    howmuchtime1 = datetime.now() + timedelta(minutes=150)
    howmuchtime2 = howmuchtime1 + timedelta(hours=4)
    text = f"‼ За графіком 3️⃣ групи планується відключення світла в період з {howmuchtime1.strftime('%H:%M')} до {howmuchtime2.strftime('%H:%M')}!"
    for row in results:
        active_value = row[0]
        set_active = cursor.execute("SELECT active FROM database WHERE user_id = ?", (active_value,))
        try:
            bot.send_message(row[0], text)
            if set_active != 1:
                cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("1", active_value))
        except:
            cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("0", active_value))
            time.sleep(1)
    connect.commit()

def send60_g3():
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    results = cursor.execute("SELECT user_id FROM database WHERE group_number = '3' AND time_to = '60'").fetchall()
    howmuchtime1 = datetime.now() + timedelta(minutes=180)
    howmuchtime2 = howmuchtime1 + timedelta(hours=4)
    text = f"‼ За графіком 3️⃣ групи планується відключення світла в період з {howmuchtime1.strftime('%H:%M')} до {howmuchtime2.strftime('%H:%M')}!"
    for row in results:
        active_value = row[0]
        set_active = cursor.execute("SELECT active FROM database WHERE user_id = ?", (active_value,))
        try:
            bot.send_message(row[0], text)
            if set_active != 1:
                cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("1", active_value))
        except:
            cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("0", active_value))
            time.sleep(1)
    connect.commit()

# Функція розсилки нічних сповіщень для 1 групи
def send10_night_g1():
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    results = cursor.execute("SELECT user_id FROM database WHERE group_number = '1' AND night = '1' AND time_to = '10'").fetchall()
    howmuchtime1 = datetime.now() + timedelta(minutes=130)
    howmuchtime2 = howmuchtime1 + timedelta(hours=4)
    text = f"‼ За графіком 1️⃣ групи планується відключення світла в період з {howmuchtime1.strftime('%H:%M')} до {howmuchtime2.strftime('%H:%M')}!"
    for row in results:
        active_value = row[0]
        set_active = cursor.execute("SELECT active FROM database WHERE user_id = ?", (active_value,))
        try:
            bot.send_message(row[0], text)
            if set_active != 1:
                cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("1", active_value))
        except:
            cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("0", active_value))
            time.sleep(1)
    connect.commit()

def send30_night_g1():
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    results = cursor.execute("SELECT user_id FROM database WHERE group_number = '1' AND night = '1' AND time_to = '30'").fetchall()
    howmuchtime1 = datetime.now() + timedelta(minutes=150)
    howmuchtime2 = howmuchtime1 + timedelta(hours=4)
    text = f"‼ За графіком 1️⃣ групи планується відключення світла в період з {howmuchtime1.strftime('%H:%M')} до {howmuchtime2.strftime('%H:%M')}!"
    for row in results:
        active_value = row[0]
        set_active = cursor.execute("SELECT active FROM database WHERE user_id = ?", (active_value,))
        try:
            bot.send_message(row[0], text)
            if set_active != 1:
                cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("1", active_value))
        except:
            cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("0", active_value))
            time.sleep(1)
    connect.commit()

def send60_night_g1():
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    results = cursor.execute("SELECT user_id FROM database WHERE group_number = '1' AND night = '1' AND time_to = '60'").fetchall()
    howmuchtime1 = datetime.now() + timedelta(minutes=180)
    howmuchtime2 = howmuchtime1 + timedelta(hours=4)
    text = f"‼ За графіком 1️⃣ групи планується відключення світла в період з {howmuchtime1.strftime('%H:%M')} до {howmuchtime2.strftime('%H:%M')}!"
    for row in results:
        active_value = row[0]
        set_active = cursor.execute("SELECT active FROM database WHERE user_id = ?", (active_value,))
        try:
            bot.send_message(row[0], text)
            if set_active != 1:
                cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("1", active_value))
        except:
            cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("0", active_value))
            time.sleep(1)
    connect.commit()

# Функція розсилки нічних сповіщень для 2 групи
def send10_night_g2():
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    results = cursor.execute("SELECT user_id FROM database WHERE group_number = '2' AND night = '1' AND time_to = '10'").fetchall()
    howmuchtime1 = datetime.now() + timedelta(minutes=130)
    howmuchtime2 = howmuchtime1 + timedelta(hours=4)
    text = f"‼ За графіком 2️⃣ групи планується відключення світла в період з {howmuchtime1.strftime('%H:%M')} до {howmuchtime2.strftime('%H:%M')}!"
    for row in results:
        active_value = row[0]
        set_active = cursor.execute("SELECT active FROM database WHERE user_id = ?", (active_value,))
        try:
            bot.send_message(row[0], text)
            if set_active != 1:
                cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("1", active_value))
        except:
            cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("0", active_value))
            time.sleep(1)
    connect.commit()


def send30_night_g2():
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    results = cursor.execute("SELECT user_id FROM database WHERE group_number = '2' AND night = '1' AND time_to = '30'").fetchall()
    howmuchtime1 = datetime.now() + timedelta(minutes=150)
    howmuchtime2 = howmuchtime1 + timedelta(hours=4)
    text = f"‼ За графіком 2️⃣ групи планується відключення світла в період з {howmuchtime1.strftime('%H:%M')} до {howmuchtime2.strftime('%H:%M')}!"
    for row in results:
        active_value = row[0]
        set_active = cursor.execute("SELECT active FROM database WHERE user_id = ?", (active_value,))
        try:
            bot.send_message(row[0], text)
            if set_active != 1:
                cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("1", active_value))
        except:
            cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("0", active_value))
            time.sleep(1)
    connect.commit()

def send60_night_g2():
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    results = cursor.execute("SELECT user_id FROM database WHERE group_number = '2' AND night = '1' AND time_to = '60'").fetchall()
    howmuchtime1 = datetime.now() + timedelta(minutes=180)
    howmuchtime2 = howmuchtime1 + timedelta(hours=4)
    text = f"‼ За графіком 2️⃣ групи планується відключення світла в період з {howmuchtime1.strftime('%H:%M')} до {howmuchtime2.strftime('%H:%M')}!"
    for row in results:
        active_value = row[0]
        set_active = cursor.execute("SELECT active FROM database WHERE user_id = ?", (active_value,))
        try:
            bot.send_message(row[0], text)
            if set_active != 1:
                cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("1", active_value))
        except:
            cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("0", active_value))
            time.sleep(1)
    connect.commit()

# Функція розсилки нічних сповіщень для 3 групи
def send10_night_g3():
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    results = cursor.execute("SELECT user_id FROM database WHERE group_number = '3' AND night = '1' AND time_to = '10'").fetchall()
    howmuchtime1 = datetime.now() + timedelta(minutes=130)
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
            time.sleep(1)
    connect.commit()

def send30_night_g3():
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    results = cursor.execute("SELECT user_id FROM database WHERE group_number = '3' AND night = '1' AND time_to = '30'").fetchall()
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
            time.sleep(1)
    connect.commit()

def send60_night_g3():
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    results = cursor.execute("SELECT user_id FROM database WHERE group_number = '3' AND night = '1' AND time_to = '60'").fetchall()
    howmuchtime1 = datetime.now() + timedelta(minutes=180)
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
            time.sleep(1)
    connect.commit()

# Функція розсилки сповіщень про можливі відключення для 1 групи
def send10_maybe_g1():
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    results = cursor.execute("SELECT user_id FROM database WHERE group_number = '1' AND maybe = '1' AND time_to = '10'").fetchall()
    howmuchtime1 = datetime.now() + timedelta(minutes=130)
    howmuchtime2 = howmuchtime1 + timedelta(hours=4)
    text = f"‼ Можливе відключення світла планується в період з {howmuchtime1.strftime('%H:%M')} до {howmuchtime2.strftime('%H:%M')} для 1️⃣ групи!"
    for row in results:
        active_value = row[0]
        set_active = cursor.execute("SELECT active FROM database WHERE user_id = ?", (active_value,))
        try:
            bot.send_message(row[0], text)
            if set_active != 1:
                cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("1", active_value))
        except:
            cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("0", active_value))
            time.sleep(1)
    connect.commit()

def send30_maybe_g1():
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    results = cursor.execute("SELECT user_id FROM database WHERE group_number = '1' AND maybe = '1' AND time_to = '30'").fetchall()
    howmuchtime1 = datetime.now() + timedelta(minutes=150)
    howmuchtime2 = howmuchtime1 + timedelta(hours=4)
    text = f"‼ Можливе відключення світла планується в період з {howmuchtime1.strftime('%H:%M')} до {howmuchtime2.strftime('%H:%M')} для 1️⃣ групи!"
    for row in results:
        active_value = row[0]
        set_active = cursor.execute("SELECT active FROM database WHERE user_id = ?", (active_value,))
        try:
            bot.send_message(row[0], text)
            if set_active != 1:
                cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("1", active_value))
        except:
            cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("0", active_value))
            time.sleep(1)
    connect.commit()

def send60_maybe_g1():
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    results = cursor.execute("SELECT user_id FROM database WHERE group_number = '1' AND maybe = '1' AND time_to = '60'").fetchall()
    howmuchtime1 = datetime.now() + timedelta(minutes=180)
    howmuchtime2 = howmuchtime1 + timedelta(hours=4)
    text = f"‼ Можливе відключення світла планується в період з {howmuchtime1.strftime('%H:%M')} до {howmuchtime2.strftime('%H:%M')} для 1️⃣ групи!"
    for row in results:
        active_value = row[0]
        set_active = cursor.execute("SELECT active FROM database WHERE user_id = ?", (active_value,))
        try:
            bot.send_message(row[0], text)
            if set_active != 1:
                cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("1", active_value))
        except:
            cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("0", active_value))
            time.sleep(1)
    connect.commit()

# Функція розсилки сповіщень про можливі відключення для 2 групи
def send10_maybe_g2():
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    results = cursor.execute("SELECT user_id FROM database WHERE group_number = '2' AND maybe = '1' AND time_to = '10'").fetchall()
    howmuchtime1 = datetime.now() + timedelta(minutes=130)
    howmuchtime2 = howmuchtime1 + timedelta(hours=4)
    text = f"‼ Можливе відключення світла планується в період з {howmuchtime1.strftime('%H:%M')} до {howmuchtime2.strftime('%H:%M')} для 2️⃣ групи!"
    for row in results:
        active_value = row[0]
        set_active = cursor.execute("SELECT active FROM database WHERE user_id = ?", (active_value,))
        try:
            bot.send_message(row[0], text)
            if set_active != 1:
                cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("1", active_value))
        except:
            cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("0", active_value))
            time.sleep(1)
    connect.commit()

def send30_maybe_g2():
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    results = cursor.execute("SELECT user_id FROM database WHERE group_number = '2' AND maybe = '1' AND time_to = '30'").fetchall()
    howmuchtime1 = datetime.now() + timedelta(minutes=150)
    howmuchtime2 = howmuchtime1 + timedelta(hours=4)
    text = f"‼ Можливе відключення світла планується в період з {howmuchtime1.strftime('%H:%M')} до {howmuchtime2.strftime('%H:%M')} для 2️⃣ групи!"
    for row in results:
        active_value = row[0]
        set_active = cursor.execute("SELECT active FROM database WHERE user_id = ?", (active_value,))
        try:
            bot.send_message(row[0], text)
            if set_active != 1:
                cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("1", active_value))
        except:
            cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("0", active_value))
            time.sleep(1)
    connect.commit()

def send60_maybe_g2():
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    results = cursor.execute("SELECT user_id FROM database WHERE group_number = '2' AND maybe = '1' AND time_to = '60'").fetchall()
    howmuchtime1 = datetime.now() + timedelta(minutes=180)
    howmuchtime2 = howmuchtime1 + timedelta(hours=4)
    text = f"‼ Можливе відключення світла планується в період з {howmuchtime1.strftime('%H:%M')} до {howmuchtime2.strftime('%H:%M')} для 2️⃣ групи!"
    for row in results:
        active_value = row[0]
        set_active = cursor.execute("SELECT active FROM database WHERE user_id = ?", (active_value,))
        try:
            bot.send_message(row[0], text)
            if set_active != 1:
                cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("1", active_value))
        except:
            cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("0", active_value))
            time.sleep(1)
    connect.commit()

# Функція розсилки сповіщень про можливі відключення для 3 групи
def send10_maybe_g3():
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    results = cursor.execute("SELECT user_id FROM database WHERE group_number = '3' AND maybe = '1' and time_to = '10'").fetchall()
    howmuchtime1 = datetime.now() + timedelta(minutes=130)
    howmuchtime2 = howmuchtime1 + timedelta(hours=4)
    text = f"‼ Можливе відключення світла планується в період з {howmuchtime1.strftime('%H:%M')} до {howmuchtime2.strftime('%H:%M')} для 3️⃣ групи!"
    for row in results:
        active_value = row[0]
        set_active = cursor.execute("SELECT active FROM database WHERE user_id = ?", (active_value,))
        try:
            bot.send_message(row[0], text)
            if set_active != 1:
                cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("1", active_value))
        except:
            cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("0", active_value))
            time.sleep(1)
    connect.commit()

def send30_maybe_g3():
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    results = cursor.execute("SELECT user_id FROM database WHERE group_number = '3' AND maybe = '1' and time_to = '30'").fetchall()
    howmuchtime1 = datetime.now() + timedelta(minutes=150)
    howmuchtime2 = howmuchtime1 + timedelta(hours=4)
    text = f"‼ Можливе відключення світла планується в період з {howmuchtime1.strftime('%H:%M')} до {howmuchtime2.strftime('%H:%M')} для 3️⃣ групи!"
    for row in results:
        active_value = row[0]
        set_active = cursor.execute("SELECT active FROM database WHERE user_id = ?", (active_value,))
        try:
            bot.send_message(row[0], text)
            if set_active != 1:
                cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("1", active_value))
        except:
            cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("0", active_value))
            time.sleep(1)
    connect.commit()

def send60_maybe_g3():
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    results = cursor.execute("SELECT user_id FROM database WHERE group_number = '3' AND maybe = '1' and time_to = '60'").fetchall()
    howmuchtime1 = datetime.now() + timedelta(minutes=180)
    howmuchtime2 = howmuchtime1 + timedelta(hours=4)
    text = f"‼ Можливе відключення світла планується в період з {howmuchtime1.strftime('%H:%M')} до {howmuchtime2.strftime('%H:%M')} для 3️⃣ групи!"
    for row in results:
        active_value = row[0]
        set_active = cursor.execute("SELECT active FROM database WHERE user_id = ?", (active_value,))
        try:
            bot.send_message(row[0], text)
            if set_active != 1:
                cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("1", active_value))
        except:
            cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("0", active_value))
            time.sleep(1)
    connect.commit()

# Функція розсилки нічних сповіщень про можливі відключення для 1 групи
def send10_night_maybe_g1():
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    results = cursor.execute("SELECT user_id FROM database WHERE group_number = '1' AND night = '1' AND maybe = '1' AND time_to = '10'").fetchall()
    howmuchtime1 = datetime.now() + timedelta(minutes=130)
    howmuchtime2 = howmuchtime1 + timedelta(hours=4)
    text = f"‼ Можливе відключення світла планується в період з {howmuchtime1.strftime('%H:%M')} до {howmuchtime2.strftime('%H:%M')} для 1️⃣ групи!"
    for row in results:
        active_value = row[0]
        set_active = cursor.execute("SELECT active FROM database WHERE user_id = ?", (active_value,))
        try:
            bot.send_message(row[0], text)
            if set_active != 1:
                cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("1", active_value))
        except:
            cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("0", active_value))
            time.sleep(1)
    connect.commit()

def send30_night_maybe_g1():
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    results = cursor.execute("SELECT user_id FROM database WHERE group_number = '1' AND night = '1' AND maybe = '1' AND time_to = '30'").fetchall()
    howmuchtime1 = datetime.now() + timedelta(minutes=150)
    howmuchtime2 = howmuchtime1 + timedelta(hours=4)
    text = f"‼ Можливе відключення світла планується в період з {howmuchtime1.strftime('%H:%M')} до {howmuchtime2.strftime('%H:%M')} для 1️⃣ групи!"
    for row in results:
        active_value = row[0]
        set_active = cursor.execute("SELECT active FROM database WHERE user_id = ?", (active_value,))
        try:
            bot.send_message(row[0], text)
            if set_active != 1:
                cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("1", active_value))
        except:
            cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("0", active_value))
            time.sleep(1)
    connect.commit()

def send60_night_maybe_g1():
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    results = cursor.execute("SELECT user_id FROM database WHERE group_number = '1' AND night = '1' AND maybe = '1' AND time_to = '60'").fetchall()
    howmuchtime1 = datetime.now() + timedelta(minutes=180)
    howmuchtime2 = howmuchtime1 + timedelta(hours=4)
    text = f"‼ Можливе відключення світла планується в період з {howmuchtime1.strftime('%H:%M')} до {howmuchtime2.strftime('%H:%M')} для 1️⃣ групи!"
    for row in results:
        active_value = row[0]
        set_active = cursor.execute("SELECT active FROM database WHERE user_id = ?", (active_value,))
        try:
            bot.send_message(row[0], text)
            if set_active != 1:
                cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("1", active_value))
        except:
            cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("0", active_value))
            time.sleep(1)
    connect.commit()

# Функція розсилки нічних сповіщень про можливі відключення для 2 групи
def send10_night_maybe_g2():
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    results = cursor.execute("SELECT user_id FROM database WHERE group_number = '2' AND night = '1' AND maybe = '1' AND time_to = '10'").fetchall()
    howmuchtime1 = datetime.now() + timedelta(minutes=130)
    howmuchtime2 = howmuchtime1 + timedelta(hours=4)
    text = f"‼ Можливе відключення світла планується в період з {howmuchtime1.strftime('%H:%M')} до {howmuchtime2.strftime('%H:%M')} для 2️⃣ групи!"
    for row in results:
        active_value = row[0]
        set_active = cursor.execute("SELECT active FROM database WHERE user_id = ?", (active_value,))
        try:
            bot.send_message(row[0], text)
            if set_active != 1:
                cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("1", active_value))
        except:
            cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("0", active_value))
            time.sleep(1)
    connect.commit()

def send30_night_maybe_g2():
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    results = cursor.execute("SELECT user_id FROM database WHERE group_number = '2' AND night = '1' AND maybe = '1' AND time_to = '30'").fetchall()
    howmuchtime1 = datetime.now() + timedelta(minutes=150)
    howmuchtime2 = howmuchtime1 + timedelta(hours=4)
    text = f"‼ Можливе відключення світла планується в період з {howmuchtime1.strftime('%H:%M')} до {howmuchtime2.strftime('%H:%M')} для 2️⃣ групи!"
    for row in results:
        active_value = row[0]
        set_active = cursor.execute("SELECT active FROM database WHERE user_id = ?", (active_value,))
        try:
            bot.send_message(row[0], text)
            if set_active != 1:
                cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("1", active_value))
        except:
            cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("0", active_value))
            time.sleep(1)
    connect.commit()

def send60_night_maybe_g2():
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    results = cursor.execute("SELECT user_id FROM database WHERE group_number = '2' AND night = '1' AND maybe = '1' AND time_to = '60'").fetchall()
    howmuchtime1 = datetime.now() + timedelta(minutes=180)
    howmuchtime2 = howmuchtime1 + timedelta(hours=4)
    text = f"‼ Можливе відключення світла планується в період з {howmuchtime1.strftime('%H:%M')} до {howmuchtime2.strftime('%H:%M')} для 2️⃣ групи!"
    for row in results:
        active_value = row[0]
        set_active = cursor.execute("SELECT active FROM database WHERE user_id = ?", (active_value,))
        try:
            bot.send_message(row[0], text)
            if set_active != 1:
                cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("1", active_value))
        except:
            cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("0", active_value))
            time.sleep(1)
    connect.commit()

# Функція розсилки нічних сповіщень про можливі відключення для 3 групи
def send10_night_maybe_g3():
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    results = cursor.execute("SELECT user_id FROM database WHERE group_number = '3' AND night = '1' AND maybe = '1' AND time_to = '10'").fetchall()
    howmuchtime1 = datetime.now() + timedelta(minutes=130)
    howmuchtime2 = howmuchtime1 + timedelta(hours=4)
    text = f"‼ Можливе відключення світла планується в період з {howmuchtime1.strftime('%H:%M')} до {howmuchtime2.strftime('%H:%M')} для 3️⃣ групи!"
    for row in results:
        active_value = row[0]
        set_active = cursor.execute("SELECT active FROM database WHERE user_id = ?", (active_value,))
        try:
            bot.send_message(row[0], text)
            if set_active != 1:
                cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("1", active_value))
        except:
            cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("0", active_value))
            time.sleep(1)
    connect.commit()

def send30_night_maybe_g3():
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    results = cursor.execute("SELECT user_id FROM database WHERE group_number = '3' AND night = '1' AND maybe = '1' AND time_to = '30'").fetchall()
    howmuchtime1 = datetime.now() + timedelta(minutes=150)
    howmuchtime2 = howmuchtime1 + timedelta(hours=4)
    text = f"‼ Можливе відключення світла планується в період з {howmuchtime1.strftime('%H:%M')} до {howmuchtime2.strftime('%H:%M')} для 3️⃣ групи!"
    for row in results:
        active_value = row[0]
        set_active = cursor.execute("SELECT active FROM database WHERE user_id = ?", (active_value,))
        try:
            bot.send_message(row[0], text)
            if set_active != 1:
                cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("1", active_value))
        except:
            cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("0", active_value))
            time.sleep(1)
    connect.commit()

def send60_night_maybe_g3():
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    results = cursor.execute("SELECT user_id FROM database WHERE group_number = '3' AND night = '1' AND maybe = '1' AND time_to = '60'").fetchall()
    howmuchtime1 = datetime.now() + timedelta(minutes=180)
    howmuchtime2 = howmuchtime1 + timedelta(hours=4)
    text = f"‼ Можливе відключення світла планується в період з {howmuchtime1.strftime('%H:%M')} до {howmuchtime2.strftime('%H:%M')} для 3️⃣ групи!"
    for row in results:
        active_value = row[0]
        set_active = cursor.execute("SELECT active FROM database WHERE user_id = ?", (active_value,))
        try:
            bot.send_message(row[0], text)
            if set_active != 1:
                cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("1", active_value))
        except:
            cursor.execute("UPDATE database SET active = ? WHERE user_id = ?", ("0", active_value))
            time.sleep(1)
    connect.commit()

time_for_sche = datetime.now() + timedelta(minutes=1)
time_for_sched = time_for_sche.strftime('%H:%M')

#Розсилка для 1 групи
schedule.every().sunday.at("22:00").do(send60_night_g1)
schedule.every().sunday.at("22:30").do(send30_night_g1)
schedule.every().sunday.at("22:50").do(send10_night_g1)
schedule.every().monday.at("06:00").do(send60_night_maybe_g1)
schedule.every().monday.at("06:30").do(send30_night_maybe_g1)
schedule.every().monday.at("06:50").do(send10_night_maybe_g1)
schedule.every().monday.at("10:00").do(send60_g1)
schedule.every().monday.at("10:30").do(send30_g1)
schedule.every().monday.at("10:50").do(send10_g1)
schedule.every().monday.at("18:00").do(send60_maybe_g1)
schedule.every().monday.at("18:30").do(send30_maybe_g1)
schedule.every().monday.at("18:50").do(send10_maybe_g1)

schedule.every().wednesday.at("22:00").do(send60_night_g1)
schedule.every().wednesday.at("22:30").do(send30_night_g1)
schedule.every().wednesday.at("22:50").do(send10_night_g1)
schedule.every().thursday.at("06:00").do(send60_night_maybe_g1)
schedule.every().thursday.at("06:30").do(send30_night_maybe_g1)
schedule.every().thursday.at("06:50").do(send10_night_maybe_g1)
schedule.every().thursday.at("10:00").do(send60_g1)
schedule.every().thursday.at("10:30").do(send30_g1)
schedule.every().thursday.at("10:50").do(send10_g1)
schedule.every().thursday.at("18:00").do(send60_maybe_g1)
schedule.every().thursday.at("18:30").do(send30_maybe_g1)
schedule.every().thursday.at("18:50").do(send10_maybe_g1)

schedule.every().saturday.at("22:00").do(send60_night_g1)
schedule.every().saturday.at("22:30").do(send30_night_g1)
schedule.every().saturday.at("22:50").do(send10_night_g1)
schedule.every().sunday.at("06:00").do(send60_night_maybe_g1)
schedule.every().sunday.at("06:30").do(send30_night_maybe_g1)
schedule.every().sunday.at("06:50").do(send10_night_maybe_g1)
schedule.every().sunday.at("10:00").do(send60_g1)
schedule.every().sunday.at("10:30").do(send30_g1)
schedule.every().sunday.at("10:50").do(send10_g1)
schedule.every().sunday.at("18:00").do(send60_maybe_g1)
schedule.every().sunday.at("18:30").do(send30_maybe_g1)
schedule.every().sunday.at("18:50").do(send10_maybe_g1)

schedule.every().tuesday.at("02:00").do(send60_night_maybe_g1)
schedule.every().tuesday.at("02:30").do(send30_night_maybe_g1)
schedule.every().tuesday.at("02:50").do(send10_night_maybe_g1)
schedule.every().tuesday.at("06:00").do(send60_night_g1)
schedule.every().tuesday.at("06:30").do(send30_night_g1)
schedule.every().tuesday.at("06:50").do(send10_night_g1)
schedule.every().tuesday.at("14:00").do(send60_maybe_g1)
schedule.every().tuesday.at("14:30").do(send30_maybe_g1)
schedule.every().tuesday.at("14:50").do(send10_maybe_g1)
schedule.every().tuesday.at("18:00").do(send60_g1)
schedule.every().tuesday.at("18:30").do(send30_g1)
schedule.every().tuesday.at("18:50").do(send10_g1)

schedule.every().friday.at("02:00").do(send60_night_maybe_g1)
schedule.every().friday.at("02:30").do(send30_night_maybe_g1)
schedule.every().friday.at("02:50").do(send10_night_maybe_g1)
schedule.every().friday.at("06:00").do(send60_night_g1)
schedule.every().friday.at("06:30").do(send30_night_g1)
schedule.every().friday.at("06:50").do(send10_night_g1)
schedule.every().friday.at("14:00").do(send60_maybe_g1)
schedule.every().friday.at("14:30").do(send30_maybe_g1)
schedule.every().friday.at("14:50").do(send10_maybe_g1)
schedule.every().friday.at("18:00").do(send60_g1)
schedule.every().friday.at("18:30").do(send30_g1)
schedule.every().friday.at("18:50").do(send10_g1)

schedule.every().tuesday.at("22:00").do(send60_night_maybe_g1)
schedule.every().tuesday.at("22:30").do(send30_night_maybe_g1)
schedule.every().tuesday.at("22:50").do(send10_night_maybe_g1)
schedule.every().wednesday.at("02:00").do(send60_night_g1)
schedule.every().wednesday.at("02:30").do(send30_night_g1)
schedule.every().wednesday.at("02:50").do(send10_night_g1)
schedule.every().wednesday.at("10:00").do(send60_maybe_g1)
schedule.every().wednesday.at("10:30").do(send30_maybe_g1)
schedule.every().wednesday.at("10:50").do(send10_maybe_g1)
schedule.every().wednesday.at("14:00").do(send60_g1)
schedule.every().wednesday.at("14:30").do(send30_g1)
schedule.every().wednesday.at("14:50").do(send10_g1)

schedule.every().friday.at("22:00").do(send60_night_maybe_g1)
schedule.every().friday.at("22:30").do(send30_night_maybe_g1)
schedule.every().friday.at("22:50").do(send10_night_maybe_g1)
schedule.every().saturday.at("02:00").do(send60_night_g1)
schedule.every().saturday.at("02:30").do(send30_night_g1)
schedule.every().saturday.at("02:50").do(send10_night_g1)
schedule.every().saturday.at("10:00").do(send60_maybe_g1)
schedule.every().saturday.at("10:30").do(send30_maybe_g1)
schedule.every().saturday.at("10:50").do(send10_maybe_g1)
schedule.every().saturday.at("14:00").do(send60_g1)
schedule.every().saturday.at("14:30").do(send30_g1)
schedule.every().saturday.at("14:50").do(send10_g1)

#Розсилка для 2 групи
schedule.every().monday.at("02:30").do(send30_night_maybe_g2)
schedule.every().monday.at("02:00").do(send60_night_maybe_g2)
schedule.every().monday.at("02:50").do(send10_night_maybe_g2)
schedule.every().monday.at("06:00").do(send60_night_g2)
schedule.every().monday.at("06:30").do(send30_night_g2)
schedule.every().monday.at("06:50").do(send10_night_g2)
schedule.every().monday.at("14:00").do(send60_maybe_g2)
schedule.every().monday.at("14:30").do(send30_maybe_g2)
schedule.every().monday.at("14:50").do(send10_maybe_g2)
schedule.every().monday.at("18:00").do(send60_g2)
schedule.every().monday.at("18:30").do(send30_g2)
schedule.every().monday.at("18:50").do(send10_g2)

schedule.every().thursday.at("02:00").do(send60_night_maybe_g2)
schedule.every().thursday.at("02:30").do(send30_night_maybe_g2)
schedule.every().thursday.at("02:50").do(send10_night_maybe_g2)
schedule.every().thursday.at("06:00").do(send60_night_g2)
schedule.every().thursday.at("06:30").do(send30_night_g2)
schedule.every().thursday.at("06:50").do(send10_night_g2)
schedule.every().thursday.at("14:00").do(send60_maybe_g2)
schedule.every().thursday.at("14:30").do(send30_maybe_g2)
schedule.every().thursday.at("14:50").do(send10_maybe_g2)
schedule.every().thursday.at("18:00").do(send60_g2)
schedule.every().thursday.at("18:30").do(send30_g2)
schedule.every().thursday.at("18:50").do(send10_g2)

schedule.every().sunday.at("02:00").do(send60_night_maybe_g2)
schedule.every().sunday.at("02:30").do(send30_night_maybe_g2)
schedule.every().sunday.at("02:50").do(send10_night_maybe_g2)
schedule.every().sunday.at("06:00").do(send60_night_g2)
schedule.every().sunday.at("06:30").do(send30_night_g2)
schedule.every().sunday.at("06:50").do(send10_night_g2)
schedule.every().sunday.at("14:00").do(send60_maybe_g2)
schedule.every().sunday.at("14:30").do(send30_maybe_g2)
schedule.every().sunday.at("14:50").do(send10_maybe_g2)
schedule.every().sunday.at("18:00").do(send60_g2)
schedule.every().sunday.at("18:30").do(send30_g2)
schedule.every().sunday.at("18:50").do(send10_g2)

schedule.every().monday.at("22:00").do(send60_night_maybe_g2)
schedule.every().monday.at("22:30").do(send30_night_maybe_g2)
schedule.every().monday.at("22:50").do(send10_night_maybe_g2)
schedule.every().tuesday.at("02:00").do(send60_night_g2)
schedule.every().tuesday.at("02:30").do(send30_night_g2)
schedule.every().tuesday.at("02:50").do(send10_night_g2)
schedule.every().tuesday.at("10:00").do(send60_maybe_g2)
schedule.every().tuesday.at("10:30").do(send30_maybe_g2)
schedule.every().tuesday.at("10:50").do(send10_maybe_g2)
schedule.every().tuesday.at("14:00").do(send60_g2)
schedule.every().tuesday.at("14:30").do(send30_g2)
schedule.every().tuesday.at("14:50").do(send10_g2)

schedule.every().thursday.at("22:00").do(send60_night_maybe_g2)
schedule.every().thursday.at("22:30").do(send30_night_maybe_g2)
schedule.every().thursday.at("22:50").do(send10_night_maybe_g2)
schedule.every().friday.at("02:00").do(send60_night_g2)
schedule.every().friday.at("02:30").do(send30_night_g2)
schedule.every().friday.at("02:50").do(send10_night_g2)
schedule.every().friday.at("10:00").do(send60_maybe_g2)
schedule.every().friday.at("10:30").do(send30_maybe_g2)
schedule.every().friday.at("10:50").do(send10_maybe_g2)
schedule.every().friday.at("14:00").do(send60_g2)
schedule.every().friday.at("14:30").do(send30_g2)
schedule.every().friday.at("14:50").do(send10_g2)

schedule.every().tuesday.at("22:00").do(send60_night_g2)
schedule.every().tuesday.at("22:30").do(send30_night_g2)
schedule.every().tuesday.at("22:50").do(send10_night_g2)
schedule.every().wednesday.at("06:00").do(send60_night_maybe_g2)
schedule.every().wednesday.at("06:30").do(send30_night_maybe_g2)
schedule.every().wednesday.at("06:50").do(send10_night_maybe_g2)
schedule.every().wednesday.at("10:00").do(send60_g2)
schedule.every().wednesday.at("10:30").do(send30_g2)
schedule.every().wednesday.at("10:50").do(send10_g2)
schedule.every().wednesday.at("18:00").do(send60_maybe_g2)
schedule.every().wednesday.at("18:30").do(send30_maybe_g2)
schedule.every().wednesday.at("18:50").do(send10_maybe_g2)

schedule.every().friday.at("22:00").do(send60_night_g2)
schedule.every().friday.at("22:30").do(send30_night_g2)
schedule.every().friday.at("22:50").do(send10_night_g2)
schedule.every().saturday.at("06:00").do(send60_night_maybe_g2)
schedule.every().saturday.at("06:30").do(send30_night_maybe_g2)
schedule.every().saturday.at("06:50").do(send10_night_maybe_g2)
schedule.every().saturday.at("10:00").do(send60_g2)
schedule.every().saturday.at("10:30").do(send30_g2)
schedule.every().saturday.at("10:50").do(send10_g2)
schedule.every().saturday.at("18:00").do(send60_maybe_g2)
schedule.every().saturday.at("18:30").do(send30_maybe_g2)
schedule.every().saturday.at("18:50").do(send10_maybe_g2)

#Розсилка для 3 групи
schedule.every().sunday.at("22:00").do(send60_night_maybe_g3)
schedule.every().sunday.at("22:30").do(send30_night_maybe_g3)
schedule.every().sunday.at("22:50").do(send10_night_maybe_g3)
schedule.every().monday.at("02:00").do(send60_night_g3)
schedule.every().monday.at("02:30").do(send30_night_g3)
schedule.every().monday.at("02:50").do(send10_night_g3)
schedule.every().monday.at("10:00").do(send60_maybe_g3)
schedule.every().monday.at("10:30").do(send30_maybe_g3)
schedule.every().monday.at("10:50").do(send10_maybe_g3)
schedule.every().monday.at("14:00").do(send60_g3)
schedule.every().monday.at("14:30").do(send30_g3)
schedule.every().monday.at("14:50").do(send10_g3)

schedule.every().wednesday.at("22:00").do(send60_night_maybe_g3)
schedule.every().wednesday.at("22:30").do(send30_night_maybe_g3)
schedule.every().wednesday.at("22:50").do(send10_night_maybe_g3)
schedule.every().thursday.at("02:00").do(send60_night_g3)
schedule.every().thursday.at("02:30").do(send30_night_g3)
schedule.every().thursday.at("02:50").do(send10_night_g3)
schedule.every().thursday.at("10:00").do(send60_maybe_g3)
schedule.every().thursday.at("10:30").do(send30_maybe_g3)
schedule.every().thursday.at("10:50").do(send10_maybe_g3)
schedule.every().thursday.at("14:00").do(send60_g3)
schedule.every().thursday.at("14:30").do(send30_g3)
schedule.every().thursday.at("14:50").do(send10_g3)

schedule.every().saturday.at("22:00").do(send60_night_maybe_g3)
schedule.every().saturday.at("22:30").do(send30_night_maybe_g3)
schedule.every().saturday.at("22:50").do(send10_night_maybe_g3)
schedule.every().sunday.at("02:00").do(send60_night_g3)
schedule.every().sunday.at("02:30").do(send30_night_g3)
schedule.every().sunday.at("02:50").do(send10_night_g3)
schedule.every().sunday.at("10:00").do(send60_maybe_g3)
schedule.every().sunday.at("10:30").do(send30_maybe_g3)
schedule.every().sunday.at("10:50").do(send10_maybe_g3)
schedule.every().sunday.at("14:00").do(send60_g3)
schedule.every().sunday.at("14:30").do(send30_g3)
schedule.every().sunday.at("14:50").do(send10_g3)

schedule.every().monday.at("22:00").do(send60_night_g3)
schedule.every().monday.at("22:30").do(send30_night_g3)
schedule.every().monday.at("22:50").do(send10_night_g3)
schedule.every().tuesday.at("06:00").do(send60_night_maybe_g3)
schedule.every().tuesday.at("06:30").do(send30_night_maybe_g3)
schedule.every().tuesday.at("06:50").do(send10_night_maybe_g3)
schedule.every().tuesday.at("10:00").do(send60_g3)
schedule.every().tuesday.at("10:30").do(send30_g3)
schedule.every().tuesday.at("10:50").do(send10_g3)
schedule.every().tuesday.at("18:00").do(send60_maybe_g3)
schedule.every().tuesday.at("18:30").do(send30_maybe_g3)
schedule.every().tuesday.at("18:50").do(send10_maybe_g3)

schedule.every().tuesday.at("22:00").do(send60_night_g3)
schedule.every().tuesday.at("22:30").do(send30_night_g3)
schedule.every().tuesday.at("22:50").do(send10_night_g3)
schedule.every().friday.at("06:00").do(send60_night_maybe_g3)
schedule.every().friday.at("06:30").do(send30_night_maybe_g3)
schedule.every().friday.at("06:50").do(send10_night_maybe_g3)
schedule.every().friday.at("10:00").do(send60_g3)
schedule.every().friday.at("10:30").do(send30_g3)
schedule.every().friday.at("10:50").do(send10_g3)
schedule.every().friday.at("18:00").do(send60_maybe_g3)
schedule.every().friday.at("18:30").do(send30_maybe_g3)
schedule.every().friday.at("18:50").do(send10_maybe_g3)

schedule.every().wednesday.at("02:00").do(send60_night_maybe_g3)
schedule.every().wednesday.at("02:30").do(send30_night_maybe_g3)
schedule.every().wednesday.at("02:50").do(send10_night_maybe_g3)
schedule.every().wednesday.at("06:00").do(send60_night_g3)
schedule.every().wednesday.at("06:30").do(send30_night_g3)
schedule.every().wednesday.at("06:50").do(send10_night_g3)
schedule.every().wednesday.at("14:00").do(send60_maybe_g3)
schedule.every().wednesday.at("14:30").do(send30_maybe_g3)
schedule.every().wednesday.at("14:50").do(send10_maybe_g3)
schedule.every().wednesday.at("18:00").do(send60_g3)
schedule.every().wednesday.at("18:30").do(send30_g3)
schedule.every().wednesday.at("18:50").do(send10_g3)

schedule.every().saturday.at("02:00").do(send60_night_maybe_g3)
schedule.every().saturday.at("02:30").do(send30_night_maybe_g3)
schedule.every().saturday.at("02:50").do(send10_night_maybe_g3)
schedule.every().saturday.at("06:00").do(send60_night_g3)
schedule.every().saturday.at("06:30").do(send30_night_g3)
schedule.every().saturday.at("06:50").do(send10_night_g3)
schedule.every().saturday.at("14:00").do(send60_maybe_g3)
schedule.every().saturday.at("14:30").do(send30_maybe_g3)
schedule.every().saturday.at("14:50").do(send10_maybe_g3)
schedule.every().saturday.at("18:00").do(send60_g3)
schedule.every().saturday.at("18:30").do(send30_g3)
schedule.every().saturday.at("18:50").do(send10_g3)

#Робота розсилки(інший потік)
def threaded_function():
    while True:
        schedule.run_pending()
        time.sleep(1)

thread = Thread(target = threaded_function)
thread.daemon = True
thread.start()

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    person_id = call.message.chat.id

# Підключення до 1 групи
    if call.data == 'group1':
        if call.message.chat.username is None:
            if call.message.chat.last_name is None:
                loginchat = f"{call.message.chat.first_name}"
            else:
                loginchat = f"{call.message.chat.first_name} {call.message.chat.last_name}"
        else:
            loginchat = f"@{call.message.chat.username}"
        cursor.execute(f"SELECT user_id FROM database WHERE user_id = {person_id}")
        data_call_group = cursor.fetchone()
        if data_call_group is None:
            cursor.execute("INSERT INTO database VALUES(?, ?, ?, ?, ?, ?);", (person_id, "1", "1", "0", "0", "30",))
        else:
            cursor.execute("UPDATE database SET group_number = ? WHERE user_id = ?", ("1", person_id,))
        data_time_to = cursor.execute(f"SELECT time_to FROM database WHERE user_id = {person_id}").fetchone()
        connect.commit()
        bot.edit_message_text(f'✅ Ви успішно підключилися до сповіщень 1️⃣ групи! \n\n🕐 Відтепер ви будете отримувати сповіщення за {data_time_to[0]} хвилин до відключення світла. \n🔕 Задля вашого ж комфорту, сповіщення не будуть надсилатися в нічний період(з 00:00 до 08:00). \n\n Щоб змінити групу, натисніть на кнопку "✅ Підключити сповіщення" нижче.', reply_markup=None, chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(880691612, f"{loginchat} підключився(-лась) до 1 групи")

# Підключення до 2 групи
    elif call.data == 'group2':
        if call.message.chat.username is None:
            if call.message.chat.last_name is None:
                loginchat = f"{call.message.chat.first_name}"
            else:
                loginchat = f"{call.message.chat.first_name} {call.message.chat.last_name}"
        else:
            loginchat = f"@{call.message.chat.username}"
        cursor.execute(f"SELECT user_id FROM database WHERE user_id = {person_id}")
        data_call_group = cursor.fetchone()
        if data_call_group is None:
            cursor.execute("INSERT INTO database VALUES(?, ?, ?, ?, ?, ?);", (person_id, "2", "1", "0", "0", "30",))
        else:
            cursor.execute("UPDATE database SET group_number = ? WHERE user_id = ?", ("2", person_id,))
        data_time_to = cursor.execute(f"SELECT time_to FROM database WHERE user_id = {person_id}").fetchone()
        connect.commit()
        bot.edit_message_text(f'✅ Ви успішно підключилися до сповіщень 2️⃣ групи! \n\n🕐 Відтепер ви будете отримувати сповіщення за {data_time_to[0]} хвилин до відключення світла. \n🔕 Задля вашого ж комфорту, сповіщення не будуть надсилатися в нічний період(з 00:00 до 08:00). \n\n Щоб змінити групу, натисніть на кнопку "✅ Підключити сповіщення" нижче.', reply_markup=None, chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(880691612, f"{loginchat} підключився(-лась) до 2 групи")

# Підключення до 3 групи
    elif call.data == 'group3':
        if call.message.chat.username is None:
            if call.message.chat.last_name is None:
                loginchat = f"{call.message.chat.first_name}"
            else:
                loginchat = f"{call.message.chat.first_name} {call.message.chat.last_name}"
        else:
            loginchat = f"@{call.message.chat.username}"
        cursor.execute(f"SELECT user_id FROM database WHERE user_id = {person_id}")
        data_call_group = cursor.fetchone()
        if data_call_group is None:
            cursor.execute("INSERT INTO database VALUES(?, ?, ?, ?, ?, ?);", (person_id, "3", "1", "0", "0", "30",))
        else:
            cursor.execute("UPDATE database SET group_number = ? WHERE user_id = ?", ("3", person_id,))
        connect.commit()
        bot.edit_message_text(f'✅ Ви успішно підключилися до сповіщень 3️⃣ групи! \n\n🕐 Відтепер ви будете отримувати сповіщення за 30 хвилин до відключення світла. \n🔕 Задля вашого ж комфорту, сповіщення не будуть надсилатися в нічний період(з 00:00 до 08:00). \n\n Щоб змінити групу, натисніть на кнопку "✅ Підключити сповіщення" нижче.', reply_markup=None, chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(880691612, f"{loginchat} підключився(-лась) до 3 групи")

# Call_data налаштувань
# Нічні сповіщення
    elif call.data == 'night_notice':
        cursor.execute(f"SELECT night FROM database WHERE user_id = {person_id}")
        data_check_night = cursor.fetchone()
        try:
            if data_check_night[0] == 0:
                markup_check_night_off = types.InlineKeyboardMarkup(row_width=1)
                item1 = types.InlineKeyboardButton("🌙 Включити нічні сповіщення", callback_data="night_notice_on")
                item2 = types.InlineKeyboardButton("⬅ Назад", callback_data="back_to_settings")
                markup_check_night_off.add(item1, item2)
                bot.edit_message_text("🌙 НІЧНІ СПОВІЩЕННЯ: \n\n• При включенні цієї функції, бот буде надсилати сповіщення в нічний період(з 00:00 до 08:00). \n❌ На даний момент такі сповіщення відключені, для включення натисніть на кнопку нижче:", reply_markup=markup_check_night_off, chat_id=call.message.chat.id, message_id=call.message.message_id)
            elif data_check_night[0] == 1:
                markup_check_night_on = types.InlineKeyboardMarkup(row_width=1)
                item1 = types.InlineKeyboardButton("🌙 Виключити нічні сповіщення", callback_data="night_notice_off")
                item2 = types.InlineKeyboardButton("⬅ Назад", callback_data="back_to_settings")
                markup_check_night_on.add(item1, item2)
                bot.edit_message_text("🌙 НІЧНІ СПОВІЩЕННЯ: \n\n✅ На даний момент сповіщення в нічний період(з 00:00 до 08:00) підключені. \nДля відключення натисніть на кнопку нижче:", reply_markup=markup_check_night_on, chat_id=call.message.chat.id, message_id=call.message.message_id)
        except:
            bot.edit.message_text("Помилка! Попробуйте підключитись до вашої групи.", reply_markup=None, chat_id=call.message.chat.id, message_id=call.message.message_id)
        connect.commit()

    elif call.data == 'night_notice_on':
        cursor.execute(f"UPDATE database SET night = 1 WHERE user_id = {person_id}")
        bot.edit_message_text("✅ Ви успішно включили нічні сповіщення. \n\n⚙ НАЛАШТУВАННЯ:", reply_markup=markup_settings, chat_id=call.message.chat.id, message_id=call.message.message_id)
        connect.commit()

    elif call.data == 'night_notice_off':
        cursor.execute(f"UPDATE database SET night = 0 WHERE user_id = {person_id}")
        bot.edit_message_text("❌ Ви відключили нічні сповіщення. \n\n⚙ НАЛАШТУВАННЯ:", reply_markup=markup_settings, chat_id=call.message.chat.id, message_id=call.message.message_id)
        connect.commit()

# Сповіщення про можливі відключення
    elif call.data == 'maybe_notice':
        cursor.execute(f"SELECT maybe FROM database WHERE user_id = {person_id}")
        data_check_maybe = cursor.fetchone()
        try:
            if data_check_maybe[0] == 0:
                markup_check_maybe_off = types.InlineKeyboardMarkup(row_width=1)
                item1 = types.InlineKeyboardButton("🔘 Включити сповіщення про можливі відключення", callback_data="maybe_notice_on")
                item2 = types.InlineKeyboardButton("⬅ Назад", callback_data="back_to_settings")
                markup_check_maybe_off.add(item1, item2)
                bot.edit_message_text("🔘 СПОВІЩЕННЯ ПРО МОЖЛИВІ ВІДКЛЮЧЕННЯ: \n\n• При включенні цієї функції, бот буде надсилати сповіщення про можливі відключення(детальніше про це на фото вашого графіку).\n❌ На даний момент дані сповіщення відключені, для включення натисніть на кнопку нижче:", reply_markup=markup_check_maybe_off, chat_id=call.message.chat.id, message_id=call.message.message_id)
            elif data_check_maybe[0] == 1:
                markup_check_maybe_on = types.InlineKeyboardMarkup(row_width=1)
                item1 = types.InlineKeyboardButton("🔘 Виключити сповіщення про можливі відключення", callback_data="maybe_notice_off")
                item2 = types.InlineKeyboardButton("⬅ Назад", callback_data="back_to_settings")
                markup_check_maybe_on.add(item1, item2)
                bot.edit_message_text("🔘 СПОВІЩЕННЯ ПРО МОЖЛИВІ ВІДКЛЮЧЕННЯ:: \n\n✅ На даний момент сповіщення про можливі відключення світла підключені. \nДля відключення натисніть на кнопку нижче:", reply_markup=markup_check_maybe_on, chat_id=call.message.chat.id, message_id=call.message.message_id)
        except:
            bot.edit.message_text("Помилка! Попробуйте підключитись до вашої групи.", reply_markup=None, chat_id=call.message.chat.id, message_id=call.message.message_id)
        connect.commit()

    elif call.data == 'maybe_notice_on':
        cursor.execute(f"UPDATE database SET maybe = 1 WHERE user_id = {person_id}")
        bot.edit_message_text("✅ Ви успішно включили сповіщення про можливі відключення світла. \n\n⚙ НАЛАШТУВАННЯ:", reply_markup=markup_settings, chat_id=call.message.chat.id, message_id=call.message.message_id)
        connect.commit()

    elif call.data == 'maybe_notice_off':
        cursor.execute(f"UPDATE database SET maybe = 0 WHERE user_id = {person_id}")
        bot.edit_message_text("❌ Ви відключили сповіщення про можливі відключення світла. \n\n⚙ НАЛАШТУВАННЯ:", reply_markup=markup_settings, chat_id=call.message.chat.id, message_id=call.message.message_id)
        connect.commit()

# Час до надсилання сповіщень
    elif call.data == "change_time_to_notice":
        cursor.execute(f"SELECT time_to FROM database WHERE user_id = {person_id}")
        data_check_time_to = cursor.fetchone()
        markup_check_time_to_off = types.InlineKeyboardMarkup(row_width=1)
        item1 = types.InlineKeyboardButton("🕐 10 хвилин", callback_data="set_10min")
        item2 = types.InlineKeyboardButton("🕓 30 хвилин", callback_data="set_30min")
        item3 = types.InlineKeyboardButton("🕔 60 хвилин", callback_data="set_60min")
        item4 = types.InlineKeyboardButton("⬅ Назад", callback_data="back_to_settings")
        markup_check_time_to_off.add(item1, item2, item3, item4)
        try:
            if data_check_time_to[0] == 10:
                time_to_off_stiker = "🔟"
                bot.edit_message_text(f"🕐 ЧАС ДО НАДСИЛАННЯ СПОВІЩЕННЯ: \n\n• Тут ви можете змінити час до надсилання сповіщень, від 10 до 60 хвилин.\n• На цей момент сповіщенням вам будуть надсилатися за {time_to_off_stiker} хвилин до відключення світла, щоб змінити, натисніть на одну з кнопок нижче:", reply_markup=markup_check_time_to_off, chat_id=call.message.chat.id, message_id=call.message.message_id)
            elif data_check_time_to[0] == 30:
                time_to_off_stiker = "3️⃣0️⃣"
                bot.edit_message_text(f"🕐 ЧАС ДО НАДСИЛАННЯ СПОВІЩЕННЯ: \n\n• Тут ви можете змінити час до надсилання сповіщень, від 10 до 60 хвилин.\n• На цей момент сповіщенням вам будуть надсилатися за {time_to_off_stiker} хвилин до відключення світла, щоб змінити, натисніть на одну з кнопок нижче:", reply_markup=markup_check_time_to_off, chat_id=call.message.chat.id, message_id=call.message.message_id)
            elif data_check_time_to[0] == 60:
                time_to_off_stiker = "6️⃣0️⃣"
                bot.edit_message_text(f"🕐 ЧАС ДО НАДСИЛАННЯ СПОВІЩЕННЯ: \n\n• Тут ви можете змінити час до надсилання сповіщень, від 10 до 60 хвилин.\n• На цей момент сповіщенням вам будуть надсилатися за {time_to_off_stiker} хвилин до відключення світла, щоб змінити, натисніть на одну з кнопок нижче:", reply_markup=markup_check_time_to_off, chat_id=call.message.chat.id, message_id=call.message.message_id)
        except:
            pass
        connect.commit()

    elif call.data == 'set_10min':
        cursor.execute(f"UPDATE database SET time_to = 10 WHERE user_id = {person_id}")
        bot.edit_message_text('✅ Ви успішно змінили час до надсилання сповіщень до 🔟 хвилин. \n\n⚙ НАЛАШТУВАННЯ:', reply_markup=markup_settings, chat_id=call.message.chat.id, message_id=call.message.message_id)
        connect.commit()

    elif call.data == 'set_30min':
        cursor.execute(f"UPDATE database SET time_to = 30 WHERE user_id = {person_id}")
        bot.edit_message_text('✅ Ви успішно змінили час до надсилання сповіщень до 3️⃣0️⃣ хвилин. \n\n⚙ НАЛАШТУВАННЯ:', reply_markup=markup_settings, chat_id=call.message.chat.id, message_id=call.message.message_id)
        connect.commit()

    elif call.data == 'set_60min':
        cursor.execute(f"UPDATE database SET time_to = 60 WHERE user_id = {person_id}")
        bot.edit_message_text('✅ Ви успішно змінили час до надсилання сповіщень до ️6️⃣0️⃣ хвилин. \n\n⚙ НАЛАШТУВАННЯ:', reply_markup=markup_settings, chat_id=call.message.chat.id, message_id=call.message.message_id)
        connect.commit()

    elif call.data == 'back_to_settings':
        bot.edit_message_text("⚙ НАЛАШТУВАННЯ:", reply_markup=markup_settings, chat_id=call.message.chat.id, message_id=call.message.message_id)

    elif call.data == 'back':
        bot.edit_message_text("МЕНЮ:", reply_markup=None, chat_id=call.message.chat.id, message_id=call.message.message_id)


bot.polling()