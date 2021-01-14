from apscheduler.jobstores.base import JobLookupError

from telegram import InlineKeyboardMarkup as Markup
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    Filters,
)

from botme import dispatcher, j, updater, OWNER
from .database import db
from .costum import Button, KeyboardMarkup, text_status


def ask(user_id):
    """fungsi untuk menanyakan tugas yang dilakukan bot kepada user"""
    process = db.check_proses(user_id)

    if process:
        reply_markup = Markup(
            [[Button("Ya", "call_ya"), Button("Tidak", "call_tidak")]]
        )
        updater.bot.send_message(
            chat_id=user_id,
            text=f"Sudah apa belum menghafal surah {process[1]}?",
            reply_markup=reply_markup,
        )
        if j.get_job(str(user_id)):
            j.pause_job(str(user_id))
    else:
        reply_markup = Markup([[Button("OK", "call_ok"), Button("NO", "call_no")]])
        updater.bot.send_message(
            chat_id=user_id,
            text="Luangkan waktu untuk menghafal Al-Quran ya",
            reply_markup=reply_markup,
        )


def following(update, context):
    """fungsi ketika user sudah mengikuti bot ini"""
    user_id = update.effective_user.id
    reply_markup = [["Mulai"], ["Status"], ["Berhenti mengikuti"]]

    if db.getme(user_id):
        update.message.reply_text("sudah")
    else:
        update.message.reply_text("Oke", reply_markup=KeyboardMarkup(reply_markup))
        db.insertme(user_id)


def start_task(update, context):
    """Awalan memulai tugas untuk menghafal surah"""
    user_id = update.effective_user.id
    while True:
        hours = db.interval(user_id, method="GET")
        if hours:
            break
        else:
            db.interval(user_id, method="PUSH")
            hours = db.interval(user_id, method="GET")
            break
    if db.getme(user_id):
        if j.get_job(str(user_id)):
            text = "Anda sudah mulai"
        if user_id == OWNER:
            ask(user_id)
        else:
            j.add_job(
                ask,
                "interval",
                hours=int(hours[1]),
                args=(user_id,),
                id=str(user_id),
            )
            db.start(user_id=user_id, method="PUSH")
            text = "Memulai"
        update.message.reply_text(text)
    else:
        update.message.reply_text("`user_id` tidak terdaftar")


def start(update, context):
    """untuk memulai bot untuk pertama kali"""
    user = update.effective_user
    text = f"Halo {user.first_name}.\n"
    while True:
        hours = db.interval(user.id, method="GET")
        if hours:
            break
        else:
            db.interval(user.id, method="PUSH")
            break
    if db.getme(user.id):
        text += "Bagaimana kabarmu?"
        reply_markup = [["Mulai"], ["Status"], ["Berhenti mengikuti"]]
    else:
        text += "Sepertinya anda belum mengikuti saya."
        reply_markup = [["Mulai"], ["Mengikuti"]]
    update.message.reply_text(text, reply_markup=KeyboardMarkup(reply_markup))


def delme(update, context):
    """fungsi ketika user hendak berhenti mengikuti bot"""
    reply_markup = KeyboardMarkup([["Mengikuti"]])
    user = update.effective_user

    try:
        db.delme(user.id)
        j.remove_job(str(user.id))
        text = "Yah koo"
    except JobLookupError:
        text = "Anda sudah tidak mengikuti"
    if db.check_proses(user.id):
        text += f"\nTapi proses hafalan {user.first_name} masih saya ingat yaa"
    update.message.reply_text(text, reply_markup=reply_markup)


def status(update, context):
    """cek status user"""
    if context:
        query = False
        user = update.message.from_user
    else:
        query = True
        user = update.from_user
    while True:
        hours = db.interval(user.id, method="GET")
        if hours:
            break
        else:
            db.interval(user.id, method="PUSH")
            break
    result = db.check_result(user.id)
    jeda = db.interval(user.id, method="GET")[1]
    text = f"Nama: {user.first_name} "
    if user.last_name:
        text += user.last_name
    reply_markup = Markup(
        [
            [
                Button("Hafalan: ", "call_total"),
                Button(str(len(result)), "call_total"),
                Button("Cek", "call_cek"),
            ],
            [
                Button("Jeda waktu", "call_jeda"),
                Button(str(jeda), "call_jeda"),
                Button("+", "call_up"),
                Button("-", "call_down"),
            ],
        ]
    )
    if query:
        update.edit_message_text(text, reply_markup=reply_markup)
    else:
        update.message.reply_text(text, reply_markup=reply_markup)


def echo(update, context):
    """fungsi ketika bot tidak tahu perintah user"""
    update.message.reply_text("Gunakan perintah yang tersedia")


dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text("Mengikuti"), following))
dispatcher.add_handler(MessageHandler(Filters.text("Berhenti mengikuti"), delme))
dispatcher.add_handler(MessageHandler(Filters.text("Mulai"), start_task))
dispatcher.add_handler(MessageHandler(Filters.text("Status"), status))
dispatcher.add_handler(MessageHandler(Filters.all, echo))
