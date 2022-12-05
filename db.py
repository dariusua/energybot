import sqlite3

class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

    def add_user(self, user_id, group):
        with self.connection:
            data = self.cursor.execute("SELECT `user_id` FROM `database` WHERE `user_id` = ?", (user_id,)).fetchone()
            if data is None:
                self.cursor.execute("INSERT INTO `database` (`user_id`, `group`, `active`) VALUES (?, ?, ?)", (user_id, group, "1",))
            else:
                self.cursor.execute("UPDATE `database` SET (`group`) = ? WHERE `user_id` = ?", (group, user_id,))

# # Добавлення користувача в таблицу 1 групи
#     def add_user_g1(self, user_id):
#         with self.connection:
#             data = self.cursor.execute("SELECT `user_id` FROM `group1` WHERE `user_id` = ?", (user_id,)).fetchone()
#             if data is None:
#                 self.cursor.execute("INSERT INTO `group1` (`user_id`, `active`) VALUES (?, ?)", (user_id, "1",))
#             self.cursor.execute("DELETE FROM `group2` WHERE `user_id` = ?", (user_id,))
#             self.cursor.execute("DELETE FROM `group3` WHERE `user_id` = ?", (user_id,))
#
# # Добавлення користувача в таблицу 2 групи
#     def add_user_g2(self, user_id):
#         with self.connection:
#             data = self.cursor.execute("SELECT `user_id` FROM `group2` WHERE `user_id` = ?", (user_id,)).fetchone()
#             if data is None:
#                 self.cursor.execute("INSERT INTO `group2` (`user_id`, `active`) VALUES (?, ?)", (user_id, "1",))
#             self.cursor.execute("DELETE FROM `group1` WHERE `user_id` = ?", (user_id,))
#             self.cursor.execute("DELETE FROM `group3` WHERE `user_id` = ?", (user_id,))
#
# # Добавлення користувача в таблицу 3 групи
#     def add_user_g3(self, user_id):
#         with self.connection:
#             data = self.cursor.execute("SELECT `user_id` FROM `group3` WHERE `user_id` = ?", (user_id,)).fetchone()
#             if data is None:
#                 self.cursor.execute("INSERT INTO `group3` (`user_id`, `active`) VALUES (?, ?)", (user_id, "1",))
#             self.cursor.execute("DELETE FROM `group1` WHERE `user_id` = ?", (user_id,))
#             self.cursor.execute("DELETE FROM `group2` WHERE `user_id` = ?", (user_id,))

# Добавлення користувача з бази даних
    def del_user(self, user_id):
        with self.connection:
            self.cursor.execute("DELETE FROM `database` WHERE `user_id` = ?", (user_id,))
            # self.cursor.execute("DELETE FROM `group1` WHERE `user_id` = ?", (user_id,))
            # self.cursor.execute("DELETE FROM `group2` WHERE `user_id` = ?", (user_id,))
            # self.cursor.execute("DELETE FROM `group3` WHERE `user_id` = ?", (user_id,))

# Провірка користувача на наявність псевдоніму
    def check_if_username_is_none(self, user_username, user_firstname, user_secondname):
        if user_username == "None":
            loginchat = f"{user_firstname} {user_secondname}"
        else:
            loginchat = f"@{user_username}"
        return loginchat

# Розсилка повідомлень від адміна
    def send(self):


