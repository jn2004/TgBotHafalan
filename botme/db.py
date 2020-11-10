import sqlite3
import random
import base64

import psycopg2

from telegram import InlineKeyboardMarkup as Markup

from botme.costum import Button

class Database:
    
    def __init__(self):
        self.connect = psycopg2.connect(
            host="ec2-54-237-155-151.compute-1.amazonaws.com",
            user="xkpckogpdxvslg",
            password="5c99eb9300a66c724dfafb22ae66d06abe0f5905650bd7a1568d4a19056d1120",
            database="dbjpj802sk4jrn"
        )
        self.cursor = self.connect.cursor()
    
    def table(self):
        t1 = """
            CREATE TABLE IF NOT EXISTS users (
                user_id INT
            )"""
        t2 = """
            CREATE TABLE IF NOT EXISTS process_users (
                user_id INT,
                surah VARCHAR(30),
                no INT
            )"""        
        t3 = """
            CREATE TABLE IF NOT EXISTS result_users (
                user_id INT,
                surah VARCHAR(30),
                no INT,
                status VARCHAR(10)
            )"""
        self.cursor.execute(t1)
        self.cursor.execute(t2)
        self.cursor.execute(t3)

    def check_proses(self, user_id):
        sql = """
            SELECT *
            FROM process_users 
            WHERE user_id = %d """
        self.cursor.execute(sql % user_id)
        return self.cursor.fetchone()

    def check_result(self, user_id):
        sql = """
            SELECT no, surah, status
            FROM result_users 
            WHERE user_id = %d """
        self.cursor.execute(sql % user_id)
        return [i for i in self.cursor.fetchall()]

    def get_surah_button(self, user_id):
        sql = """
            SELECT no, latin, jumlah, arabic
            FROM surah 
            WHERE no"""
        test = """
            SELECT no 
            FROM result_users 
            WHERE user_id = %d """
        self.cursor.execute(test % (user_id))
        for j, i in enumerate(self.cursor.fetchall()):
            if j == 0:
                sql += " NOT LIKE " + str(i[0])  
            else:    
                sql += " AND no NOT LIKE " + str(i[0])
        
        db = sqlite3.connect("botme/new.db")
        surah = [i for i in db.cursor().execute(sql)]
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
        db = sqlite3.connect("botme/new.db")

        for i in db.cursor().execute(sql % no):
            # latin = base64.b64encode(i[0].encode())
            sql = """
                INSERT INTO process_users(user_id, surah, no)
                VALUES (%d, '%s', %s) """ % (user_id, i[0], no)

        self.cursor.execute(sql)
        self.connect.commit()
    
    def successful(self, user_id, status):
        sql1 = """
            SELECT user_id, surah, no
            FROM process_users 
            WHERE user_id = %d """
        self.cursor.execute(sql1 % user_id)
        result = self.cursor.fetchone()
        sql2 = """
            INSERT INTO result_users(user_id, surah, no, status)
            VALUES (%d, '%s', %d, '%s') """
        sql3 = """
            DELETE FROM process_users
            WHERE user_id = %d """
        self.cursor.execute(sql2 % (*result, status))
        self.cursor.execute(sql3 % user_id)
        self.connect.commit()

    def insertme(self, user_id):
        sql = """
            INSERT INTO users(user_id)
            VALUES (%d) """

        self.cursor.execute(sql % user_id)
        self.connect.commit()

    def getme(self, user_id):
        sql = """
            SELECT *
            FROM users
            WHERE user_id = %d """
        self.cursor.execute(sql % user_id)
        return self.cursor.fetchone()

    def delme(self, user_id):
        sql = """
            DELETE FROM users
            WHERE user_id = %d """
        self.cursor.execute(sql % user_id)
        self.connect.commit()
    
    def getid(self):
        sql = """
            SELECT *
            FROM process_users"""
        self.cursor.execute(sql)
        return self.cursor.fetchone()

db = Database()
db.table()
