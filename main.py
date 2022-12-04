import sqlite3
import time
import telebot
import schedule
from datetime import datetime, timedelta
from telebot import types
from threading import Thread
from config import TOKEN


bot = telebot.TeleBot(TOKEN)

#Початок роботи, запис користувача в БД
@bot.message_handler(commands=['start', 'help'])
def start(message):
    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS group1(
        id INTEGER
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS group2(
        id INTEGER
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS group3(
        id INTEGER
    )""")
    connect.commit()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Група 1")
    item2 = types.KeyboardButton("Група 2")
    item3 = types.KeyboardButton("Група 3")
    markup.add(item1)
    markup.add(item2)
    markup.add(item3)
    bot.send_message(message.chat.id, f'Привіт! 👋 \n\n🤖 Цей бот створений задля сповіщення користувачів "Львівобленерго" про планові відключення у вашому населеному пункті. \n✏️ Бот буде відсилати повідомлення з попередженням за 30 хвилин до відключення світла. \n❗️ Бот не є офіційним! \n\n📋 Для початку роботи, дізнайтесь вашу групу на сайті: https://poweroff.loe.lviv.ua \nПісля цього, виберіть групу нижче:', reply_markup=markup)

#Видалення з бази даних
@bot.message_handler(commands=['delete'])
def delete(message):
    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()
    people_id = message.chat.id
    cursor.execute(f"DELETE FROM group1 WHERE id = {people_id}")
    cursor.execute(f"DELETE FROM group2 WHERE id = {people_id}")
    cursor.execute(f"DELETE FROM group3 WHERE id = {people_id}")
    bot.send_message(message.from_user.id, "❌ Ви відключилися від сповіщень про відключення електроенергії. Дякуємо за використання бота!😢 \n\n/start - підключитись заново.")
    connect.commit()

#Фото з графіком
@bot.message_handler(commands=['grafik'])
def grafik(message):
    photo = open('image.png', 'rb')
    bot.send_photo(message.from_user.id, photo)

#Розсилка по команді
@bot.message_handler(commands=['sendforall'])
def sendforall(message):
    if message.from_user.id == 880691612:
        connect = sqlite3.connect('users.db')
        cursor = connect.cursor()
        cursor.execute("SELECT id FROM group1")
        results = cursor.fetchall()
        text = message.text[12:]
        for result in results:
            bot.send_message(result[0], {text})
        cursor.execute("SELECT id FROM group2")
        results = cursor.fetchall()
        text = message.text[12:]
        for result in results:
            bot.send_message(result[0], {text})
        cursor.execute("SELECT id FROM group3")
        results = cursor.fetchall()
        text = message.text[12:]
        for result in results:
            bot.send_message(result[0], {text})
        connect.commit()
    else:
        bot.send_message(message.from_user.id, "Для виконання цієї команди ви повинні бути адміном бота.")

#Функції з записом в БД
@bot.message_handler(content_types='text')
def message_reply(message: types.Message):
    person_id = message.chat.id
    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()
    if message.text == "Група 1":
        cursor.execute(f"SELECT id FROM group1 WHERE id = {person_id}")
        data = cursor.fetchone()
        if data is None:
            user_id = [message.chat.id]
            cursor.execute("INSERT INTO group1 VALUES(?);", user_id)
        cursor.execute(f"DELETE FROM group2 WHERE id = {person_id}")
        cursor.execute(f"DELETE FROM group3 WHERE id = {person_id}")
        a = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.from_user.id, f"✅ Ви успішно підключилися до сповіщень 1 групи! \n\n🕐 Відтепер ви будете отримувати сповіщення за 30 хвилин до відключення світла. \n🔕 Задля вашого ж комфорту, сповіщення не будуть надсилатися в нічний період(з 00:00 до 08:00). \n/start - змінити групу.", reply_markup=a)
        print(f"{message.from_user.username} підключився до 1 групи")

    elif message.text == "Група 2":
        person_id = message.chat.id
        cursor.execute(f"SELECT id FROM group2 WHERE id = {person_id}")
        data = cursor.fetchone()
        if data is None:
            user_id = [message.chat.id]
            cursor.execute("INSERT INTO group2 VALUES(?);", user_id)
        cursor.execute(f"DELETE FROM group1 WHERE id = {person_id}")
        cursor.execute(f"DELETE FROM group3 WHERE id = {person_id}")
        a = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.from_user.id, f"✅ Ви успішно підключилися до сповіщень 2 групи! \n\n🕐 Відтепер ви будете отримувати сповіщення за 30 хвилин до відключення світла. \n🔕 Задля вашого ж комфорту, сповіщення не будуть надсилатися в нічний період(з 00:00 до 08:00). \n/start - змінити групу.", reply_markup=a)
        print(f"{message.from_user.username} підключився до 2 групи")

    elif message.text == "Група 3":
        person_id = message.chat.id
        cursor.execute(f"SELECT id FROM group3 WHERE id = {person_id}")
        data = cursor.fetchone()
        if data is None:
            user_id = [message.chat.id]
            cursor.execute("INSERT INTO group3 VALUES(?);", user_id)
        cursor.execute(f"DELETE FROM group1 WHERE id = {person_id}")
        cursor.execute(f"DELETE FROM group2 WHERE id = {person_id}")
        a = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.from_user.id, f"✅ Ви успішно підключилися до сповіщень 3 групи! \n\n🕐 Відтепер ви будете отримувати сповіщення за 30 хвилин до відключення світла. \n🔕 Задля вашого ж комфорту, сповіщення не будуть надсилатися в нічний період(з 00:00 до 08:00). \n/start - змінити групу.", reply_markup=a)
        print(f"{message.from_user.username} підключився до 3 групи")

    connect.commit()

#Функція розсилки для 1 групи
def sending_g1():
    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()
    cursor.execute("SELECT id FROM group1")
    results = cursor.fetchall()
    howmuchtime1 = datetime.now() + timedelta(minutes=30)
    howmuchtime2 = howmuchtime1 + timedelta(hours=4)
    for result in results:
        bot.send_message(result[0], f"‼ За графіком групи №1 планується відключення світла в період з {howmuchtime1.strftime('%H:%M')} до {howmuchtime2.strftime('%H:%M')}!")
    connect.commit()

#Функція розсилки для 2 групи
def sending_g2():
    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()
    cursor.execute("SELECT id FROM group2")
    results = cursor.fetchall()
    howmuchtime1 = datetime.now() + timedelta(minutes=30)
    howmuchtime2 = howmuchtime1 + timedelta(hours=4)
    for result in results:
        bot.send_message(result[0], f"‼ За графіком групи №2 планується відключення світла в період з {howmuchtime1.strftime('%H:%M')} до {howmuchtime2.strftime('%H:%M')}!")
    connect.commit()

#Функція розсилки для 3 групи
def sending_g3():
    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()
    cursor.execute("SELECT id FROM group3")
    results = cursor.fetchall()
    howmuchtime1 = datetime.now() + timedelta(minutes=150)
    howmuchtime2 = howmuchtime1 + timedelta(hours=4)
    for result in results:
        bot.send_message(result[0], f"‼ За графіком групи №3 планується відключення світла в період з {howmuchtime1.strftime('%H:%M')} до {howmuchtime2.strftime('%H:%M')}!")
    connect.commit()

#Розсилка для 1 групи
schedule.every().monday.at("10:30").do(sending_g1)
schedule.every().tuesday.at("06:30").do(sending_g1)
schedule.every().tuesday.at("18:30").do(sending_g1)
schedule.every().wednesday.at("14:30").do(sending_g1)
schedule.every().thursday.at("10:30").do(sending_g1)
schedule.every().friday.at("06:30").do(sending_g1)
schedule.every().friday.at("18:30").do(sending_g1)
schedule.every().saturday.at("14:30").do(sending_g1)
schedule.every().sunday.at("10:30").do(sending_g1)

#Розсилка для 2 групи
schedule.every().monday.at("06:30").do(sending_g2)
schedule.every().monday.at("18:30").do(sending_g2)
schedule.every().tuesday.at("14:30").do(sending_g2)
schedule.every().wednesday.at("10:30").do(sending_g2)
schedule.every().thursday.at("06:30").do(sending_g2)
schedule.every().thursday.at("18:30").do(sending_g2)
schedule.every().friday.at("14:30").do(sending_g2)
schedule.every().saturday.at("10:30").do(sending_g2)
schedule.every().sunday.at("06:30").do(sending_g2)
schedule.every().sunday.at("18:30").do(sending_g2)

#Розсилка для 3 групи
schedule.every().monday.at("14:30").do(sending_g3)
schedule.every().tuesday.at("10:30").do(sending_g3)
schedule.every().wednesday.at("06:30").do(sending_g3)
schedule.every().wednesday.at("18:30").do(sending_g3)
schedule.every().thursday.at("14:30").do(sending_g3)
schedule.every().friday.at("10:30").do(sending_g3)
schedule.every().saturday.at("06:30").do(sending_g3)
schedule.every().saturday.at("18:30").do(sending_g3)
schedule.every().sunday.at("14:30").do(sending_g3)

#Робота розсилки(інший потік)
def threaded_function():
    while True:
        schedule.run_pending()
        time.sleep(1)

thread = Thread(target = threaded_function)
thread.daemon = True
thread.start()
bot.polling()