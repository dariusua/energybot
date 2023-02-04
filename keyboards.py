from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, KeyboardButton, InlineKeyboardButton


def register_to_bot():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("✅ Підключити сповіщення"))
    return markup


def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.row(KeyboardButton("🔁 Змінити групу"), KeyboardButton("🔕 Відключити сповіщення")).add(KeyboardButton("🖼 Фото графіку"), KeyboardButton("⚙ Налаштування"))
    return markup


def connect_to_group():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Група 1", callback_data='group1'), InlineKeyboardButton("Група 2", callback_data='group2'), InlineKeyboardButton("Група 3", callback_data='group3'), InlineKeyboardButton("Дізнатись свою групу", url='https://poweroff.loe.lviv.ua/gav_city3'))
    return markup


def support():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("⬅ Назад"))
    return markup


def settings():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton("🔘 Сповіщення про можливі відключення", callback_data="maybe_notice"),
               InlineKeyboardButton("🌙 Нічні сповіщення", callback_data="night_notice"),
               InlineKeyboardButton("🕐 Час до надсилання сповіщення", callback_data="time_to_notice"),
               InlineKeyboardButton("⬅ Назад", callback_data="back_to_menu"))
    return markup


def change_maybe(what_maybe_now):
    markup = InlineKeyboardMarkup(row_width=1)
    if what_maybe_now == 1:
        markup.add(InlineKeyboardButton(text="🔘 Виключити сповіщення про можливі відключення", callback_data="maybe_notice_off"),
                   InlineKeyboardButton("⬅ Назад", callback_data="back_to_settings"))
        text = "🔘 СПОВІЩЕННЯ ПРО МОЖЛИВІ ВІДКЛЮЧЕННЯ: \n\n✅ На даний момент сповіщення про можливі відключення світла включені. \nДля виключення натисніть на кнопку нижче:"
    elif what_maybe_now == 0:
        markup.add(InlineKeyboardButton(text="🔘 Включити сповіщення про можливі відключення", callback_data="maybe_notice_on"),
                   InlineKeyboardButton("⬅ Назад", callback_data="back_to_settings"))
        text = "🔘 СПОВІЩЕННЯ ПРО МОЖЛИВІ ВІДКЛЮЧЕННЯ: \n\n• При включенні цієї функції, бот буде надсилати сповіщення про можливі відключення(детальніше про це на фото вашого графіку).\n❌ На даний момент такі сповіщення виключені, для включення натисніть на кнопку нижче:"
    return markup, text


def change_night(what_night_now):
    markup = InlineKeyboardMarkup(row_width=1)
    if what_night_now == 1:
        markup.add(InlineKeyboardButton("🌙 Виключити нічні сповіщення", callback_data="night_notice_off"), InlineKeyboardButton("⬅ Назад", callback_data="back_to_settings"))
        text = "🌙 НІЧНІ СПОВІЩЕННЯ: \n\n✅ На даний момент сповіщення в нічний період(з 00:00 до 07:59) включені. \nДля виключення натисніть на кнопку нижче:"
    elif what_night_now == 0:
        markup.add(InlineKeyboardButton("🌙 Включити нічні сповіщення", callback_data="night_notice_on"), InlineKeyboardButton("⬅ Назад", callback_data="back_to_settings"))
        text = "🌙 НІЧНІ СПОВІЩЕННЯ: \n\n• При включенні цієї функції, бот буде надсилати сповіщення в нічний період(з 00:00 до 07:59). \n❌ На даний момент такі сповіщення виключені, для включення натисніть на кнопку нижче:"
    return markup, text


def change_time(what_time_now):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton("🕐 10 хвилин", callback_data="set_10min"), InlineKeyboardButton("🕓 30 хвилин", callback_data="set_30min"), InlineKeyboardButton("🕔 60 хвилин", callback_data="set_60min"), InlineKeyboardButton("⬅ Назад", callback_data="back_to_settings"))
    text = {10: "🔟", 30: "3️⃣0️⃣", 60: "6️⃣0️⃣"}.get(int(what_time_now), int(what_time_now))
    return markup, text
