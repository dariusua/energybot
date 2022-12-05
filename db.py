import sqlite3

class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

    def add_user_g1(self, user_id):
        with self.connection:
            data = self.cursor.execute("SELECT user_id FROM `group1` WHERE `user_id` VALUES (?)", (user_id,)).fetchone()
            if data is None:
                self.cursor.execute("INSERT INTO `group1` (`user_id`, `active`) VALUES (?, ?)", (user_id, "1",))
            self.cursor.execute("DELETE FROM `group2` WHERE `id` VALUES (?)", (user_id,))
            self.cursor.execute("DELETE FROM `group3` WHERE `id` VALUES (?)", (user_id,))
