from telegram.ext import CallbackQueryHandler

from botme import dispatcher, j

from .database import db


def callback(update, context):
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
        msg = query.edit_message_text("ya")
        if j.get_job(str(user_id)):
            if db.respons(user_id):
                msg.delete()
                query.message.reply_text("Tolong disiplin!")
                print("hai")
            j.resume_job(str(user_id))
    elif result == "no":
        query.edit_message_text("Yah")
    elif result == "ya":
        db.successful(user_id, "sudah")
        db.respons(user_id, delete=True)
        text = ""
        for i in sorted(db.check_result(user_id)):
            # latin = base64.b64decode(i[1].strip("b''")).decode()
            text += f"`No     => {i[0]}\nSurah  => {i[1]}\nStatus => {i[2]}`\n\n"
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


dispatcher.add_handler(CallbackQueryHandler(callback, pattern=r"call_", run_async=True))
