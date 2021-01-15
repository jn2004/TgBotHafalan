import random
import sqlite3
import datetime

import psycopg2

from telegram import InlineKeyboardMarkup

from botme import DATABASE_URL, logger
from .costum import Button


class Database:
    def __init__(self):
        self.connect = psycopg2.connect(DATABASE_URL)
        self.connect.set_session(autocommit=True)
        self.cursor = self.connect.cursor()

    def _status_time(self, db_timestamp):
        ts = datetime.datetime.now() - datetime.datetime.fromtimestamp(
            float(db_timestamp)
        )
        day = ts.days if ts.days else ""
        hour = round(ts.total_seconds() / 3600, 1)
        minute = round(ts.seconds / 60, 1)
        second = ts.seconds
        if ".0" in str(hour):
            hour = int(hour)
        if ".0" in str(minute):
            minute = int(minute)

        return f"{day}/{hour}/{minute}/{second}"

    def _build_surah_button(self, surah):
        surah_button = map(
            lambda x: [
                Button(surah[x][1], f"call_arabic1{surah[x][0]}"),
                Button(surah[x][3], f"call_arabic2{surah[x][0]}"),
                Button(surah[x][2], f"call_ayat{x}"),
            ],
            {random.randint(0, len(surah) - 1) for _ in range(5)},
        )
        markup = InlineKeyboardMarkup(
            [
                [
                    Button("Surah", "call_headerSurah"),
                    Button("Arabic", "call_headerArabic"),
                    Button("Jumlah", "call_headerTotal"),
                ],
                *surah_button,
                [Button("Refresh/Segarkan", "call_ok")],
            ]
        )
        return markup

    def table(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INT
            )"""
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS process_users (
                user_id   INT,
                surah     VARCHAR(30),
                no        INT,
                timestamp FLOAT
            )"""
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS result_users (
                user_id INT,
                surah   VARCHAR(30),
                no      INT,
                status  VARCHAR
            )"""
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS respons (
                user_id INT,
                total   INT
            )"""
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS interval (
                user_id  INT,
                interval INT
            )"""
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS start_id (
                user_id INT
            )"""
        )

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
        with sqlite3.connect("botme/list_surah.db") as db:
            surah = [i for i in db.cursor().execute(sql.format(tuple(n)))]
            return self._build_surah_button(surah)

    def insert_process_id(self, user_id, no):
        sql = """
            SELECT latin FROM surah
            WHERE no = %s """
        timestamp = datetime.datetime.now().timestamp()

        with sqlite3.connect("botme/list_surah.db") as db:
            for i in db.cursor().execute(sql % no):
                self.cursor.execute(
                    f"""
                    INSERT INTO process_users(user_id, surah, no, timestamp)
                    VALUES ({user_id}, '{i[0]}', {no}, {timestamp}) """
                )

    def successful(self, user_id):
        self.cursor.execute(
            f"""
            SELECT user_id, surah, no, timestamp
            FROM process_users
            WHERE user_id = {user_id} """
        )

        db_user_id, db_surah, db_name, db_timestamp = self.cursor.fetchone()
        status = self._status_time(db_timestamp)

        self.cursor.execute(
            f"""
            INSERT INTO result_users
            VALUES ({db_user_id}, '{db_surah}', {db_name}, '{status}') """
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
        self.cursor.execute(
            f"""
            DELETE FROM interval
            WHERE user_id = {user_id}
            """
        )
        self.cursor.execute(f"DELETE FROM start_id WHERE user_id = {user_id}")

    def start(self, user_id=None, method="GET"):
        if method == "GET":
            self.cursor.execute(f"SELECT * FROM start_id")
            return self.cursor.fetchall()
        elif method == "PUSH":
            self.cursor.execute(f"INSERT INTO start_id VALUES({user_id})")

    def getid(self):
        self.cursor.execute("SELECT * FROM process_users")
        return self.cursor.fetchall()

    def respons(self, user_id, delete=False):
        if delete:
            self.cursor.execute(
                f"""
                DELETE FROM respons
                WHERE user_id = {user_id} """
            )
        else:
            self.cursor.execute(
                f"""
                SELECT total FROM respons
                WHERE user_id = {user_id} """
            )
            total = self.cursor.fetchone()
            if total:
                self.cursor.execute(
                    f"""
                    UPDATE respons SET total = {int(total[0])+1}
                    WHERE user_id = {user_id}"""
                )
                if int(total[0]) > 5:
                    return True
            else:
                self.cursor.execute(
                    f"""INSERT INTO respons
                    VALUES({user_id}, 1)"""
                )

    def interval(self, user_id, method, INTERVAL=1, opt=None):
        if method == "CHANGE":
            interval = self.interval(user_id, "GET")[1]
            if opt:  # naik
                interval += INTERVAL
            else:  # turun
                interval -= INTERVAL
            self.cursor.execute(
                f"""UPDATE interval SET interval = {interval}
                WHERE user_id = {user_id}
                """
            )

        elif method == "PUSH":
            self.cursor.execute(
                f"""INSERT INTO interval(user_id, interval)
                VALUES ({user_id}, 5)
                """
            )
        elif method == "GET":
            self.cursor.execute(
                f"""SELECT * FROM interval
                WHERE user_id = {user_id}
                """
            )
            return self.cursor.fetchone()


db = Database()
db.table()
