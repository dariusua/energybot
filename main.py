import sqlite3
import time
import telebot
import datetime
# import schedule
import scheduler
import datetime as dt
from scheduler import Scheduler
from scheduler.trigger import Monday
from datetime import datetime, timedelta
from telebot import types
from threading import Thread
from config import TOKEN

schedule = Scheduler()
bot = telebot.TeleBot(TOKEN)

markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
item1 = types.KeyboardButton("✅ Підключити сповіщення")
item2 = types.KeyboardButton("🔕 Відключити сповіщення")
item3 = types.KeyboardButton("📖 Повний графік(фото)")
item4 = types.KeyboardButton("⚙ Налаштування")
markup.add(item1, item2, item3, item4)

#Початок роботи
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f'Привіт 👋 \n\n🤖 Цей бот створений задля сповіщення користувачів "Львівобленерго" про планові відключення у вашому населеному пункті. \n✏️ Бот буде відсилати повідомлення з попередженням за 30 хвилин до відключення світла. \n❗️ Бот не є офіційним! \n\n📋 Для підключення сповіщень, натисніть на кнопку "✅ Підключити сповіщення" нижче.', reply_markup=markup)

#Розсилка по команді
@bot.message_handler(commands=['sendforall'])
def sendforall(message):
    if message.from_user.id == 880691612:
        connect = sqlite3.connect('users.db')
        cursor = connect.cursor()
        cursor.execute("SELECT id FROM group1")
        results = cursor.fetchall()
        for result in results:
            bot.send_message(result[0], message.text)
        cursor.execute("SELECT id FROM group2")
        results = cursor.fetchall()
        for result in results:
            bot.send_message(result[0], message.text)
        cursor.execute("SELECT id FROM group3")
        results = cursor.fetchall()
        for result in results:
            bot.send_message(result[0], message.text)
        connect.commit()
    else:
        bot.send_message(message.from_user.id, "Для виконання цієї команди ви повинні бути адміном бота.")

#Функції кнопок меню
@bot.message_handler(content_types='text')
def message_reply(message: types.Message):
    person_id = message.chat.id
    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()
    if message.text == "✅ Підключити сповіщення":
        cursor.execute("""CREATE TABLE IF NOT EXISTS group1(
            id INTEGER,
            active INTEGER
        )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS group2(
            id INTEGER,
            active INTEGER
        )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS group3(
            id INTEGER,
            active INTEGER
        )""")
        connect.commit()
        markup_group = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Група 1")
        item2 = types.KeyboardButton("Група 2")
        item3 = types.KeyboardButton("Група 3")
        markup_group.add(item1, item2, item3)
        bot.send_message(message.chat.id, f'✅ Для підключення сповіщень про відключення світла Вам необхідно натиснути на кнопку з номером вашої групи. \n❓ Щоб дізнатись номер вашої групи, перейдіть за посиланням та внизу сторінки, ввівши свої дані, ви зможете дізнатись свою групу: https://poweroff.loe.lviv.ua', reply_markup=markup_group)

    elif message.text == "🔕 Відключити сповіщення":
        cursor.execute(f"DELETE FROM group1 WHERE id = {person_id}")
        cursor.execute(f"DELETE FROM group2 WHERE id = {person_id}")
        cursor.execute(f"DELETE FROM group3 WHERE id = {person_id}")
        bot.send_message(message.from_user.id, '❌ Ви відключилися від сповіщень про відключення електроенергії. Дякуємо за використання бота!😢 \n\nЩоб підключитись знову, натисніть на кнопку "✅ Підключити сповіщення" нижче.', reply_markup=markup)

    elif message.text == "Група 1":
        cursor.execute(f"SELECT id FROM group1 WHERE id = {person_id}")
        data = cursor.fetchone()
        if data is None:
            user_id = [message.chat.id]
            active_yes = "1"
            cursor.execute("INSERT INTO group1 (id) VALUES(?);", user_id)
            cursor.execute("INSERT INTO group1 (active) VALUES(?);", active_yes)
        cursor.execute(f"DELETE FROM group2 WHERE id = {person_id}")
        cursor.execute(f"DELETE FROM group3 WHERE id = {person_id}")
        bot.send_message(message.from_user.id, f'✅ Ви успішно підключилися до сповіщень 1️⃣ групи! \n\n🕐 Відтепер ви будете отримувати сповіщення за 30 хвилин до відключення світла. \n🔕 Задля вашого ж комфорту, сповіщення не будуть надсилатися в нічний період(з 00:00 до 08:00). \n\n Щоб змінити групу, натисніть на кнопку "✅ Підключити сповіщення" нижче.', reply_markup=markup)
        bot.send_message(880691612, f"@{message.from_user.username} підключився до 1 групи")

    elif message.text == "Група 2":
        person_id = message.chat.id
        cursor.execute(f"SELECT id FROM group2 WHERE id = {person_id}")
        data = cursor.fetchone()
        if data is None:
            user_id = [message.chat.id]
            active_yes = "1"
            cursor.execute("INSERT INTO group1 (id) VALUES(?);", user_id)
            cursor.execute("INSERT INTO group1 (active) VALUES(?);", active_yes)
        cursor.execute(f"DELETE FROM group1 WHERE id = {person_id}")
        cursor.execute(f"DELETE FROM group3 WHERE id = {person_id}")
        bot.send_message(message.from_user.id, f"✅ Ви успішно підключилися до сповіщень 2️⃣ групи! \n\n🕐 Відтепер ви будете отримувати сповіщення за 30 хвилин до відключення світла. \n🔕 Задля вашого ж комфорту, сповіщення не будуть надсилатися в нічний період(з 00:00 до 08:00). \n/start - змінити групу.", reply_markup=markup)
        bot.send_message(880691612, f"@{message.from_user.username} підключився до 2 групи")

    elif message.text == "Група 3":
        person_id = message.chat.id
        cursor.execute(f"SELECT id FROM group3 WHERE id = {person_id}")
        data = cursor.fetchone()
        if data is None:
            user_id = [message.chat.id]
            active_yes = "1"
            cursor.execute("INSERT INTO group1 (id) VALUES(?);", user_id)
            cursor.execute("INSERT INTO group1 (active) VALUES(?);", active_yes)
        cursor.execute(f"DELETE FROM group1 WHERE id = {person_id}")
        cursor.execute(f"DELETE FROM group2 WHERE id = {person_id}")
        # a = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.from_user.id, f"✅ Ви успішно підключилися до сповіщень 3️⃣ групи! \n\n🕐 Відтепер ви будете отримувати сповіщення за 30 хвилин до відключення світла. \n🔕 Задля вашого ж комфорту, сповіщення не будуть надсилатися в нічний період(з 00:00 до 08:00). \n/start - змінити групу.", reply_markup=markup)
        bot.send_message(880691612, f"@{message.from_user.username} підключився до 3 групи")

    elif message.text == "📖 Повний графік(фото)":
        photo = open('image.png', 'rb')
        bot.send_photo(message.from_user.id, photo)

    elif message.text == "⚙ Налаштування":
    #    markup.settings = types.ReplyKeyboardMarkup(resize_keyboard=True)
    #    item1 = types.KeyboardButton("🌙 Включити нічні сповіщення")
    #    item2 = types.KeyboardButton("🔕 Відключити сповіщення")
    #    item3 = types.KeyboardButton("📖 Повний графік(фото)")
    #    item4 = types.KeyboardButton("⚙ Налаштування")
    #    markup.add(item1, item2, item3, item4)
        bot.send_message(message.from_user.id, "Нажаль, ця команда тимчасово недоступна.")

    elif message.text == "/start":
        pass

    elif message.text == "/test":
        test = datetime.now() + timedelta(minutes=150)
        bot.send_message(message.from_user.id, test)

    else:
        bot.send_message(message.from_user.id, "Данної команди не існує.")

    connect.commit()

#Функція розсилки для 1 групи
def sending_g1():
    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()
    cursor.execute("SELECT id FROM group1")
    results = cursor.fetchall()
    cursor.execute("SELECT active FROM group1")
    active = cursor.fetchall()
    howmuchtime1 = datetime.now() + timedelta(minutes=150)
    howmuchtime2 = howmuchtime1 + timedelta(hours=4)
    for result in results:
        try:
            bot.send_message(result[0], f"‼ За графіком 1️⃣ групи планується відключення світла в період з {howmuchtime1.strftime('%H:%M')} до {howmuchtime2.strftime('%H:%M')}!")
            if int(result[0]) != 1:
                cursor.execute("INSERT INTO group1 (active) VALUES(?);", "1")
        except:
            cursor.execute("INSERT INTO group1 (active) VALUES(?);", "0")

    connect.commit()

#Функція розсилки для 2 групи
def sending_g2():
    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()
    cursor.execute("SELECT id FROM group2")
    results = cursor.fetchall()
    cursor.execute("SELECT active FROM group2")
    active = cursor.fetchall()
    howmuchtime1 = datetime.now() + timedelta(minutes=150)
    howmuchtime2 = howmuchtime1 + timedelta(hours=4)
    for result in results:
        try:
            bot.send_message(result[0], f"‼ За графіком 2️⃣ групи планується відключення світла в період з {howmuchtime1.strftime('%H:%M')} до {howmuchtime2.strftime('%H:%M')}!")
            if int(result[0]) != 1:
                cursor.execute("INSERT INTO group2 (active) VALUES(?);", "1")
        except:
            cursor.execute("INSERT INTO group2 (active) VALUES(?);", "0")

    connect.commit()

#Функція розсилки для 3 групи
def sending_g3():
    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()
    cursor.execute("SELECT id FROM group3")
    results = cursor.fetchall()
    cursor.execute("SELECT active FROM group3")
    active = cursor.fetchall()
    howmuchtime1 = datetime.now() + timedelta(minutes=150)
    howmuchtime2 = howmuchtime1 + timedelta(hours=4)
    for result in results:
        try:
            bot.send_message(result[0], f"‼ За графіком 3️⃣ групи планується відключення світла в період з {howmuchtime1.strftime('%H:%M')} до {howmuchtime2.strftime('%H:%M')}!")
            if int(result[0]) != 1:
                cursor.execute("INSERT INTO group2 (active) VALUES(?);", "1")
        except:
            cursor.execute("INSERT INTO group2 (active) VALUES(?);", "0")

    connect.commit()

#Розсилка для 1 групи
# schedule.every().monday.at("10:30").do(sending_g1)
# schedule.every().tuesday.at("06:30").do(sending_g1)
# schedule.every().tuesday.at("18:30").do(sending_g1)
# schedule.every().wednesday.at("14:30").do(sending_g1)
# schedule.every().thursday.at("10:30").do(sending_g1)
# schedule.every().friday.at("06:30").do(sending_g1)
# schedule.every().friday.at("18:30").do(sending_g1)
# schedule.every().saturday.at("14:30").do(sending_g1)
# schedule.every().sunday.at("10:30").do(sending_g1)

#Розсилка для 2 групи
# schedule.every().monday.at("06:30").do(sending_g2)
# schedule.every().monday.at("18:30").do(sending_g2)
# schedule.every().tuesday.at("14:30").do(sending_g2)
# schedule.every().wednesday.at("10:30").do(sending_g2)
# schedule.every().thursday.at("06:30").do(sending_g2)
# schedule.every().thursday.at("18:30").do(sending_g2)
# schedule.every().friday.at("14:30").do(sending_g2)
# schedule.every().saturday.at("10:30").do(sending_g2)
# schedule.every().sunday.at("06:30").do(sending_g2)
# schedule.every().sunday.at("18:30").do(sending_g2)

#Розсилка для 3 групи
schedule.weekly(Monday(dt.time(hour=14, minute=45)), sending_g3())
# schedule.every().tuesday.at("10:30").do(sending_g3)
# schedule.every().wednesday.at("06:30").do(sending_g3)
# schedule.every().wednesday.at("18:30").do(sending_g3)
# schedule.every().thursday.at("14:30").do(sending_g3)
# schedule.every().friday.at("10:30").do(sending_g3)
# schedule.every().saturday.at("06:30").do(sending_g3)
# schedule.every().saturday.at("18:30").do(sending_g3)
# schedule.every().sunday.at("14:30").do(sending_g3)

#Робота розсилки(інший потік)
def threaded_function():
    while True:
        schedule.run_pending()
        time.sleep(1)

thread = Thread(target = threaded_function)
thread.daemon = True
thread.start()
bot.polling()