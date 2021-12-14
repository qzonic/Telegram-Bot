import sqlite3
import datetime

class BotDB:

    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cur = self.conn.cursor()

    def user_exists(self, user_id):
        """Проверяем, есть ли юзер в базе"""
        result = self.cur.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
        self.conn.commit()
        return bool(len(result.fetchall()))

    def add_user(self, user_id, username):
        offset = datetime.timezone(datetime.timedelta(hours=4))
        datetime_mw = datetime.datetime.now(offset)
        if username != None:
            self.cur.execute("""INSERT INTO `users` (`user_id`, `join_date`, `username`) VALUES (?, ?, ?)""", (user_id, datetime_mw.strftime("%d.%m.%Y %H:%M"), username,))
        elif username == None:
            self.cur.execute("""INSERT INTO `users` (`user_id`, `join_date`) VALUES (?, ?)""", (user_id, datetime_mw.strftime("%d.%m.%Y %H:%M"),))
        return self.conn.commit()

    def get_user_id(self, user_id):
        """Достаем id юзера в базе по его user_id"""
        result = self.cur.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
        self.conn.commit()
        return result.fetchone()[0]

    def add_command(self, user_id, command):
        offset = datetime.timezone(datetime.timedelta(hours=4))
        datetime_mw = datetime.datetime.now(offset)
        self.cur.execute("INSERT INTO `users_command` (`from_user`, `command`, `command_time`) VALUES(?, ?, ?)",
                         (self.get_user_id(user_id), command, datetime_mw.strftime("%d.%m.%Y %H:%M"),))
        return self.conn.commit()

    def get_user_status(self, user_id):
        rez = self.cur.execute("SELECT user_status.status FROM `users` LEFT JOIN `user_status` ON users.status = user_status.id WHERE users.user_id = ?", (user_id,))
        return rez.fetchone()[0]

    def change_user_status(self, user_id, new_status):
        if new_status.lower() == "admin":
            self.cur.execute("""UPDATE users set status = 1 WHERE user_id = ?""", (user_id,))
        elif new_status.lower() == "user":
            self.cur.execute("""UPDATE users set status = 2 WHERE user_id = ?""", (user_id,))
        return self.conn.commit()

    def get_all_users(self):
        rez = self.cur.execute("SELECT user_id, username, join_date FROM `users`" )
        return rez.fetchall()

    def in_admin_status(self, user_id):
        rez = self.cur.execute("SELECT in_admin_status FROM `users` WHERE user_id = ?", (user_id,))
        return rez.fetchone()[0]

    def change_in_admin_status(self, user_id, STATUS):
        if STATUS == 1:
            self.cur.execute("UPDATE users set in_admin_status = 1 WHERE user_id = ?", (user_id,))
        if STATUS == 0:
            self.cur.execute("UPDATE users set in_admin_status = 0 WHERE user_id = ?", (user_id,))
        return self.conn.commit()

    def get_all_commands(self):
        return self.cur.execute("SELECT from_user, users.username, command, command_time FROM `users_command` LEFT JOIN `users` ON users.id = users_command.from_user")

    def close(self):
        self.conn.close()


