from apscheduler.jobstores.base import JobLookupError

from telegram import InlineKeyboardMarkup as Markup
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    Filters,
)

from .database import db
from .costum import Button, KeyboardMarkup

from botme import dispatcher, j, updater

OWNER = [1328007524, 1399167510]


def call(user_id):
    ps = db.check_proses(user_id)

    if ps:
        reply_markup = Markup(
            [[Button("Ya", "call_ya"), Button("Tidak", "call_tidak")]]
        )
        updater.bot.send_message(
            chat_id=user_id,
            text=f"Sudah apa belum menghafal surah {ps[1]}?",
            reply_markup=reply_markup,
        )
        if j.get_job(str(user_id)):
            j.pause_job(str(user_id))
    else:
        reply_markup = Markup(
            [[Button("OK", "call_ok"), Button("NO", "call_no")]]
        )
        updater.bot.send_message(
            chat_id=user_id,
            text="Luangkan waktu untuk menghafal Al-Quran ya",
            reply_markup=reply_markup,
        )


def on(update, context):
    user_id = update.effective_user.id
    reply_markup = [["Mulai"], ["Berhenti mengikuti"]]
    if db.getme(user_id):
        update.message.reply_text("sudah")
    else:
        update.message.reply_text(
            "Oke", reply_markup=KeyboardMarkup(reply_markup)
        )
        db.insertme(user_id)


def showup(update, context):
    user_id = update.effective_user.id
    if db.getme(user_id):
        if user_id in OWNER:
            call(user_id)
        if j.get_job(str(user_id)):
            text = "Anda sudah mulai"
        else:
            j.add_job(
                call, "interval", hours=10, args=(user_id,), id=str(user_id)
            )
            text = "Memulai"
        update.message.reply_text(text)
    else:
        update.message.reply_text("`user_id` tidak terdaftar")


def startall(update, context):
    user_id = update.effective_user.id

    if user_id not in OWNER:
        return
    if db.getid():
        for i in db.getid():
            if not j.get_job(str(i[0])):
                j.add_job(
                    call, "interval", hours=10, args=(int(i[0]),), id=str(i[0])
                )
    else:
        print("h")


def start(update, context):
    user = update.effective_user
    text = f"Halo {user.first_name}.\n"
    if db.getme(user.id):
        text += "Bagaimana kabarmu?"
        reply_markup = [["Mulai"], ["Berhenti mengikuti"]]
    else:
        text += "Sepertinya anda belum mengikuti saya."
        reply_markup = [["Mulai"], ["Mengikuti"]]
    update.message.reply_text(text, reply_markup=KeyboardMarkup(reply_markup))


def delme(update, context):
    reply_markup = KeyboardMarkup([["Mengikuti"]])
    user = update.effective_user
    try:
        db.delme(user.id)
        j.remove_job(str(user.id))
        text = "Yah koo"
    except JobLookupError:
        text = "Anda sudah tidak mengikuti"
    if db.check_proses(user.id):
        text += "\nTapi proses hafalan %s masih saya ingat yaa" % (
            user.first_name
        )
    update.message.reply_text(text, reply_markup=reply_markup)


def file(update, context):
    update.message.reply_document(open("botme/new.db", "rb"))


def alll(update, context):
    update.message.reply_text("Gunakan perintah yang tersedia")


dispatcher.add_handler(CommandHandler("start", start, run_async=True))
dispatcher.add_handler(
    MessageHandler(Filters.text("Mengikuti"), on, run_async=True)
)
dispatcher.add_handler(
    MessageHandler(Filters.text("Berhenti mengikuti"), delme, run_async=True)
)
dispatcher.add_handler(
    MessageHandler(Filters.text("Mulai"), showup, run_async=True)
)
dispatcher.add_handler(CommandHandler("upload", file, run_async=True))
dispatcher.add_handler(MessageHandler(Filters.all, alll, run_async=True))
