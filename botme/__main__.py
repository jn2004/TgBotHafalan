from apscheduler.jobstores.base import JobLookupError

from telegram import InlineKeyboardMarkup as Markup
from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    Filters,
)

from botme import dispatcher, j, updater, logger
from botme.db import db
from botme.costum import Button, KeyboardMarkup

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


def from_call(update, context):
    query = update.callback_query
    result = query.data.replace("call_", "")
    try:
        user_id = db.getme(update.effective_user.id)[0]
    except TypeError:
        return

    if result[0:4] == "ayat":
        query.answer("Ini jumlah ayat", show_alert=True)
    elif result[0:3] == "ela":
        query.answer("Mohon klik di nama surah", show_alert=True)
    else:
        query.answer()

    if result == "tidak":
        query.edit_message_text("ya")
        if j.get_job(str(user_id)):
            j.resume_job(str(user_id))
    elif result == "no":
        query.edit_message_text("Yah")
    elif result == "ya":
        db.successful(user_id, "sudah")
        text = ""
        for i in sorted(db.check_result(user_id)):
            # latin = base64.b64decode(i[1].strip("b''")).decode()
            text += (
                f"`No     => {i[0]}\nSurah  => {i[1]}\nStatus => {i[2]}`\n\n"
            )
        query.edit_message_text(text)
        if j.get_job(str(user_id)):
            j.resume_job(str(user_id))
    elif db.check_proses(user_id):
        query.edit_message_text("Proses anda sedang berlangsung")
    else:
        if result == "ok":
            query.edit_message_text(
                "Dipilih yak", reply_markup=db.get_surah_button(user_id)
            )
        elif "arabic" == result[0:6]:
            db.insert_process_id(user_id, result[7::])
            query.edit_message_text("oke")


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
                call, "interval", hours=2, args=(user_id,), id=str(user_id)
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
                    call, "interval", hours=2, args=(int(i[0]),), id=str(i[0])
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


def main():
    dispatcher.add_handler(CommandHandler("start", start, run_async=True))
    dispatcher.add_handler(
        MessageHandler(Filters.text("Mengikuti"), on, run_async=True)
    )
    dispatcher.add_handler(
        MessageHandler(
            Filters.text("Berhenti mengikuti"), delme, run_async=True
        )
    )
    dispatcher.add_handler(
        MessageHandler(Filters.text("Mulai"), showup, run_async=True)
    )
    dispatcher.add_handler(
        CallbackQueryHandler(from_call, pattern=r"call_", run_async=True)
    )
    dispatcher.add_handler(CommandHandler("upload", file, run_async=True))
    dispatcher.add_handler(MessageHandler(Filters.all, alll, run_async=True))

    updater.start_polling()
    logger.info("Listening using polling")
    updater.idle()


if __name__ == "__main__":
    main()
