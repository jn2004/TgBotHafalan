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
            database="dbjpj802sk4jrn",
        )
        self.connect.set_session(autocommit=True)

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
        self.cursor.execute(
            f"""
            SELECT * FROM process_users
            WHERE user_id = {user_id} """
        )

        return self.cursor.fetchone()

    def check_result(self, user_id):
        self.cursor.execute(
            f"""
            SELECT no, surah, status
            FROM result_users
            WHERE user_id = {user_id} """
        )

        return self.cursor.fetchall()

    def get_surah_button(self, user_id):
        sql = """
            SELECT no, latin, jumlah, arabic
            FROM surah
            WHERE no NOT IN {} """
        self.cursor.execute(
            f"""
            SELECT no
            FROM result_users
            WHERE user_id = {user_id} """
        )
        n = [i[0] for i in self.cursor.fetchall()]
        if len(n) == 1:
            n += [0]
        with sqlite3.connect("botme/new.db") as db:
            surah = [i for i in db.cursor().execute(sql.format(tuple(n)))]
        button = list(
            map(
                lambda n: [
                    Button(surah[n][1], f"call_arabic1{str(surah[n][0])}"),
                    Button(surah[n][3], f"call_arabic2{surah[n][0]}"),
                    Button(surah[n][2], f"call_ayat{n}"),
                ],
                list({random.randint(0, len(surah) - 1) for i in range(4)}),
            )
        )
        return Markup(
            [
                [
                    Button("Surah", "call_elaSurah"),
                    Button("Arabic", "call_elaArabic"),
                    Button("Jumlah", "call_elaTotal"),
                ],
                *button,
            ]
        )

    def insert_process_id(self, user_id, no):
        sql = """
            SELECT latin FROM surah
            WHERE no = %s """
        with sqlite3.connect("botme/new.db") as db:
            for i in db.cursor().execute(sql % no):
                # latin = base64.b64encode(i[0].encode())
                self.cursor.execute(
                    f"""
                    INSERT INTO process_users(user_id, surah, no)
                    VALUES ({user_id}, '{i[0]}', {no}) """
                )

    def successful(self, user_id, status):
        self.cursor.execute(
            f"""
            SELECT user_id, surah, no
            FROM process_users
            WHERE user_id = {user_id} """
        )

        usr, surah, name = self.cursor.fetchone()

        self.cursor.execute(
            f"""
            INSERT INTO result_users
            VALUES ({usr}, '{surah}', {name}, '{status}') """
        )
        self.cursor.execute(
            f"""
            DELETE FROM process_users
            WHERE user_id = {user_id} """
        )

    def insertme(self, user_id):
        self.cursor.execute(
            f"""
            INSERT INTO users(user_id)
            VALUES ({user_id}) """
        )

    def getme(self, user_id):
        self.cursor.execute(
            f"""
            SELECT * FROM users
            WHERE user_id = {user_id} """
        )

        return self.cursor.fetchone()

    def delme(self, user_id):
        self.cursor.execute(
            f"""
            DELETE FROM users
            WHERE user_id = {user_id} """
        )

    def getid(self):
        self.cursor.execute("SELECT * FROM process_users")
        return self.cursor.fetchone()


db = Database()
db.table()
