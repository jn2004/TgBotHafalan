import sqlite3
import random

from telegram import InlineKeyboardMarkup as Markup

from botme.costum import Button

class Database:
    
    def __init__(self):
        self.connect = sqlite3.connect("botme/new.db")
        self.cursor = self.connect.cursor()

    def check_proses(self, user_id):
        sql = """
            SELECT *
            FROM process_users 
            WHERE user_id = %d """
        return [i for i in self.cursor.execute(sql % user_id)]

    def check_result(self, user_id):
        sql = """
            SELECT no, surah, status
            FROM result_users 
            WHERE user_id = %d """
        return [i for i in self.cursor.execute(sql % user_id)]

    def get_surah_button(self, user_id):
        sql = """
            SELECT no, latin, jumlah, arabic
            FROM surah 
            WHERE no"""
        test = f"""
            SELECT no 
            FROM result_users 
            WHERE user_id = {user_id}"""
        
        for j, i in enumerate(self.cursor.execute(test)):
            if j == 0:
                sql += " NOT LIKE " + str(i[0])  
            else:    
                sql += " AND no NOT LIKE " + str(i[0])
        surah = [i for i in self.cursor.execute(sql)]
        # number =
        button = list(
            map(
                lambda n: [
                        Button(surah[n][1], "call_arabic1" + str(surah[n][0])),
                        Button(surah[n][3], "call_arabic2" + str(surah[n][0])),
                        Button(surah[n][2], "call_ayat" + str(n))
                        ],
                    list({random.randint(0, len(surah)-1) for i in range(4)})
                )
            )
        del surah
        return Markup([
            [Button("Surah", "call_elaSurah"), 
             Button("Arabic", "call_elaArabic"),
             Button("Jumlah", "call_elaTotal")],
             *button
        ])

    def insert_process_id(self, user_id, no):
        sql = f"""
            SELECT latin
            FROM surah
            WHERE no = %s """
        for i in self.cursor.execute(sql % no):
            sql = f"""
                INSERT INTO process_users(user_id, surah, no)
                VALUES ({user_id}, "{i[0]}", {no}) """
        with self.connect as c:
            self.cursor.execute(sql)
            c.commit()
    
    def successful(self, user_id, status):
        sql = f"""
            SELECT user_id, surah, no
            FROM process_users 
            WHERE user_id = %d """
        
        for r in self.cursor.execute(sql % user_id):    
            sql = f"""
                INSERT INTO result_users(user_id, surah, no, status)
                VALUES ({r[0]}, "{r[1]}", {r[2]}, "{status}");
                DELETE FROM process_users
                WHERE user_id = {user_id}; """
        with self.connect as c:
            self.cursor.executescript(sql)
            c.commit()

    def insertme(self, user_id):
        sql = """
            INSERT INTO users(user_id)
            VALUES (%d) """
        with self.connect as c:
            self.cursor.execute(sql % user_id)
            c.commit()

    def getme(self, user_id):
        sql = """
            SELECT *
            FROM users
            WHERE user_id = %d """

        for i in self.cursor.execute(sql % user_id):
            return i

    def delme(self, user_id):
        sql = """
            DELETE FROM users
            WHERE user_id = %d """
        with self.connect as c:
            self.cursor.execute(sql % user_id)
            c.commit()
