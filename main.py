import logging
from aiogram import Bot, Dispatcher, executor, types
from db import Database
from config import TOKEN

logging.basicConfig(level=logging.INFO)

bot = Bot(TOKEN)
dp = Dispatcher(bot)
db = Database('database.db')

markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
item1 = types.KeyboardButton("✅ Підключити сповіщення")
item2 = types.KeyboardButton("🔕 Відключити сповіщення")
item3 = types.KeyboardButton("📖 Повний графік(фото)")
item4 = types.KeyboardButton("⚙ Налаштування")
markup.add(item1, item2, item3, item4)

@bot.message_handler(commands=['start'])
async def start(message: types.Message):
    db.add_user_g1(message.from_user.id)
    await bot.send_message(message.from_user.id, f'Привіт 👋 \n\n🤖 Цей бот створений задля сповіщення користувачів "Львівобленерго" про планові відключення у вашому населеному пункті. \n✏️ Бот буде відсилати повідомлення з попередженням за 30 хвилин до відключення світла. \n❗️ Бот не є офіційним! \n\n📋 Для підключення сповіщень, натисніть на кнопку "✅ Підключити сповіщення" нижче.', reply_markup=markup)



if __name__ == "__main__":
    executor.start_polling(dp, skip_updates = True)