import logging
from aiogram import Bot, Dispatcher, executor, types
from db import Database
from config import TOKEN

logging.basicConfig(level=logging.INFO)

bot = Bot(TOKEN)
dp = Dispatcher(bot)
db = Database('database.db')

db.create_db()

# Маркап меню
markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
item1 = types.KeyboardButton("✅ Підключити сповіщення")
item2 = types.KeyboardButton("🔕 Відключити сповіщення")
item3 = types.KeyboardButton("📖 Повний графік(фото)")
item4 = types.KeyboardButton("⚙ Налаштування")
markup.add(item1, item2, item3, item4)

# Маркап груп
markup_group = types.ReplyKeyboardMarkup(resize_keyboard=True)
item1 = types.KeyboardButton("Група 1")
item2 = types.KeyboardButton("Група 2")
item3 = types.KeyboardButton("Група 3")
markup_group.add(item1, item2, item3)

# Початок роботи
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await bot.send_message(message.from_user.id, f'Привіт 👋 \n\n🤖 Цей бот створений задля сповіщення користувачів "Львівобленерго" про планові відключення у вашому населеному пункті. \n✏️ Бот буде відсилати повідомлення з попередженням за 30 хвилин до відключення світла. \n❗️ Бот не є офіційним! \n\n📋 Для підключення сповіщень, натисніть на кнопку "✅ Підключити сповіщення" нижче.', reply_markup=markup)

# Розсилка по команді
@dp.message_handler(commands=['send'])
async def send(message: types.Message):
    if message.from_user.id == "880691612":
        text = message.text[6:]



@dp.message_handler(content_types='text')
async def message_reply(message: types.Message):
# Підключення сповіщеннь
    if message.text == "✅ Підключити сповіщення":
        await bot.send_message(message.chat.id, f'✅ Для підключення сповіщень про відключення світла Вам необхідно натиснути на кнопку з номером вашої групи. \n❓ Щоб дізнатись номер вашої групи, перейдіть за посиланням та внизу сторінки, ввівши свої дані, ви зможете дізнатись свою групу: https://poweroff.loe.lviv.ua', reply_markup=markup_group)

# Підключення до 1 групи
    elif message.text == "Група 1":
        # db.add_user_g1(message.from_user.id)
        # db.check_if_username_is_none(message.from_user.username, message.from_user.firstname, message.from_user.secondname)
        group = "1"
        db.add_user(message.from_user.id, group)
        bot.send_message(message.from_user.id, f'✅ Ви успішно підключилися до сповіщень 1️⃣ групи! \n\n🕐 Відтепер ви будете отримувати сповіщення за 30 хвилин до відключення світла. \n🔕 Задля вашого ж комфорту, сповіщення не будуть надсилатися в нічний період(з 00:00 до 08:00). \n\n Щоб змінити групу, натисніть на кнопку "✅ Підключити сповіщення" нижче.', reply_markup=markup)
        bot.send_message(880691612, f"{loginchat} підключився до 1 групи")

# Підключення до 2 групи
    elif message.text == "Група 2":
        # db.add_user_g2(message.from_user.id)
        # db.check_if_username_is_none(message.from_user.username, message.from_user.firstname, message.from_user.secondname)
        group = "2"
        db.add_user(message.from_user.id, group)
        bot.send_message(message.from_user.id, f'✅ Ви успішно підключилися до сповіщень 2️⃣ групи! \n\n🕐 Відтепер ви будете отримувати сповіщення за 30 хвилин до відключення світла. \n🔕 Задля вашого ж комфорту, сповіщення не будуть надсилатися в нічний період(з 00:00 до 08:00). \n\n Щоб змінити групу, натисніть на кнопку "✅ Підключити сповіщення" нижче.', reply_markup=markup)
        bot.send_message(880691612, f"{loginchat} підключився до 2 групи")

# Підключення до 3 групи
    elif message.text == "Група 3":
        #db.add_user_g3(message.from_user.id)
        #db.check_if_username_is_none(message.from_user.username, message.from_user.firstname, message.from_user.secondname)
        group = "3"
        db.add_user(message.from_user.id, group)
        bot.send_message(message.from_user.id, f'✅ Ви успішно підключилися до сповіщень 3️⃣ групи! \n\n🕐 Відтепер ви будете отримувати сповіщення за 30 хвилин до відключення світла. \n🔕 Задля вашого ж комфорту, сповіщення не будуть надсилатися в нічний період(з 00:00 до 08:00). \n\n Щоб змінити групу, натисніть на кнопку "✅ Підключити сповіщення" нижче.', reply_markup=markup)
        bot.send_message(880691612, f"{loginchat} підключився до 3 групи")

# Відключення сповіщень
    elif message.text == "🔕 Відключити сповіщення":
        db.del_user(message.from_user.id)
        await bot.send_message(message.from_user.id, '❌ Ви відключилися від сповіщень про відключення електроенергії. Дякуємо за використання бота!😢 \n\nЩоб підключитись знову, натисніть на кнопку "✅ Підключити сповіщення" нижче.', reply_markup=markup)
        db.check_if_username_is_none(message.from_user.username, message.from_user.firstname, message.from_user.secondname)
        bot.send_message(880691612, f"{loginchat} відключився від сповіщень")

# Надсилання фото з графіком відключень
    elif message.text == "📖 Повний графік(фото)":
        photo = open('image.png', 'rb')
        bot.send_photo(message.from_user.id, photo)

# 1Налаштування
    elif message.text == "⚙ Налаштування":
        markup_settings = types.ReplyKeyboardMarkup(resize_keyboard=True)
    #    item1 = types.KeyboardButton("🌙 Включити нічні сповіщення")
    #    item2 = types.KeyboardButton("Кнопка")
    #    item3 = types.KeyboardButton("Кнопка")
        item4 = types.KeyboardButton("⬅ Назад")
    #    markup_settings.add(item1, item2, item3, item4)
        markup_settings.add(item4)
        bot.send_message(message.from_user.id, "Нажаль, ця команда тимчасово недоступна.", reply_markup=markup)

    elif message.text == "/start":
        pass

# Постійна робота бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates = True)