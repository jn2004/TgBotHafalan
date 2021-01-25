from telegram import InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler

from botme import dispatcher, j
from .database import db
from .function import status
from .costum import utimeout, text_status, chinterval, Button


def callback(update, context):
    query = update.callback_query
    result = query.data.replace("call_", "")
    try:
        user_id = str(db.getme(update.effective_user.id)[0])
    except TypeError:
        return
    if result[0:4] == "ayat":
        query.answer("Ini jumlah ayat", show_alert=True)
    elif result[0:6] == "header":
        query.answer("Mohon klik di nama surah", show_alert=True)
    else:
        query.answer()

    if result == "tidak":
        msg = query.edit_message_text("Y")
        if j.get_job(user_id):
            if db.respons(user_id):
                msg.delete()
                query.message.reply_text("Tolong disiplin!")
            j.resume_job(user_id)
    elif result == "no":
        query.edit_message_text("Yah")
    elif result == "ya":
        db.successful(user_id)
        db.respons(user_id, delete=True)
        text = "".join(text_status(db, user_id))
        query.edit_message_text(text)
        if j.get_job(user_id):
            j.resume_job(user_id)
    elif db.check_proses(user_id):
        query.edit_message_text("Proses anda sedang berlangsung")
    elif result == "status":
        status(query, None)
    elif result == "up":
        chinterval(query, db, j, status, 1)
    elif result == "down":
        chinterval(query, db, j, status, 0)
    elif result == "total" or result == "cek":
        text = "".join(text_status(db, user_id))
        reply_markup = InlineKeyboardMarkup(
            [[Button("Kembali", "call_status")]]
        )
        query.edit_message_text(text, reply_markup=reply_markup)
    else:
        juser_id = user_id + "j"
        if result == "ok":
            query.edit_message_text(
                "Dipilih yak", reply_markup=db.get_surah_button(user_id)
            )
            if not j.get_job(juser_id):
                j.add_job(
                    utimeout,
                    "interval",
                    minutes=7,
                    args=(query, j, juser_id),
                    id=juser_id,
                )
        elif result[0:6] == "arabic":
            if j.get_job(juser_id):
                j.remove_job(juser_id)
            db.insert_process_id(user_id, result[7::])
            query.edit_message_text("Oke semoga berhasil")


dispatcher.add_handler(CallbackQueryHandler(callback, pattern=r"call_"))
