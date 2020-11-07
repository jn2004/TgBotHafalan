from apscheduler.jobstores.base import JobLookupError

from telegram import InlineKeyboardMarkup as Markup, ParseMode
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, Filters

from botme import dispatcher, j, updater, logger
from botme.db import Database as db
from botme.costum import Button, KeyboardMarkup

def call(user_id):
    if db().check_proses(user_id):
        reply_markup = Markup([[Button("Ya", "call_ya"), Button("Tidak", "call_tidak")]])
        updater.bot.send_message(chat_id=user_id,
                                 text="Sudah apa belum?",
                                 reply_markup=reply_markup)
        j.scheduler.pause_job(str(user_id))
    else:
        reply_markup = Markup([[Button("OK", "call_ok"), Button("NO", "call_no")]])
        updater.bot.send_message(chat_id=user_id,
                                 text="Sebelum belajar harus diselengi menghafal dulu",
                                 reply_markup=reply_markup)

def from_call(update, context):
    query = update.callback_query
    result = query.data.replace("call_", "")
    try:
        user_id = db().getme(update.effective_user.id)[0]
    except:
        return    
    
    if result[0:4] == "ayat":
        query.answer("Ini jumlah ayat", show_alert=True)
    elif result[0:3] == "ela":
        query.answer("Mohon klik di nama surah", show_alert=True)        
    else:
        query.answer()
 
    if result == "tidak":
        query.edit_message_text("ya")
        j.scheduler.resume_job(str(user_id))
    elif result == "ya":
        db().successful(user_id, "sudah")
        text = ""
        for i in sorted(db().check_result(user_id)):
            text += f"`No     => {i[0]}\nSurah  => {i[1]}\nStatus => {i[2]}`\n\n"
        query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN)
        j.scheduler.resume_job(str(user_id))  
    elif db().check_proses(user_id):
        query.edit_message_text("Proses anda sedang berlangsung")
    else:
        if result == "ok":
            query.edit_message_text("Dipilih yak", reply_markup=db().get_surah_button(user_id))
        elif "arabic" == result[0:6]:
            db().insert_process_id(user_id, result[7::])
            query.edit_message_text("oke")

def on(update, context):
    user_id = update.effective_user.id
    reply_markup = [["Mulai"], ["Berhenti mengikuti"]]
    if db().getme(user_id):
        update.message.reply_text("sudah")
    else:
        update.message.reply_text("Oke", reply_markup=KeyboardMarkup(reply_markup))
        db().insertme(user_id)

def showup(update, context):
    user_id = update.effective_user.id
    # call(user_id)
    if db().getme(user_id):
        if j.scheduler.get_job(str(user_id)):
            text = "Anda sudah mulai"
        else:
            j.scheduler.add_job(call, "interval", hours=5, args=(user_id,), id=str(user_id))
            text = "Memulai"
        update.message.reply_text(text)
    else:
        update.message.reply_text("user_id tidak terdaftar")

def start(update, context):
    user = update.effective_user
    text = f"Halo {user.first_name}.\n"
    if db().getme(user.id):
        text += "Bagaimana kabarmu?"
        reply_markup = [["Mulai"], ["Berhenti mengikuti"]]
    else:
        text += "Sepertinya anda belum mengikuti saya."
        reply_markup = [["Mulai"], ["Mengikuti"]]
    update.message.reply_text(text, reply_markup=KeyboardMarkup(reply_markup))

def delme(update, context):
    reply_markup = [["Mengikuti"]]
    try:
        db().delme(update.effective_user.id)
        j.scheduler.remove_job(str(update.effective_user.id))
        text = "Yah koo"
    except JobLookupError:
        text = "Anda sudah tidak mengikuti"
    update.message.reply_text(text, reply_markup=KeyboardMarkup(reply_markup))

def file(update, context):
    update.message.reply_document(open("botme/new.db", "rb"))

def alll(update, context):
    update.message.reply_text("Gunakan perintah yang tersedia")

def main():
    dispatcher.add_handler(CommandHandler("start", start, run_async=True))
    dispatcher.add_handler(MessageHandler(Filters.text("Mengikuti"), on, run_async=True))
    dispatcher.add_handler(MessageHandler(Filters.text("Berhenti mengikuti"), delme, run_async=True))
    dispatcher.add_handler(MessageHandler(Filters.text("Mulai"), showup, run_async=True))
    dispatcher.add_handler(CallbackQueryHandler(from_call, pattern=r"call_", run_async=True))
    dispatcher.add_handler(CommandHandler("upload", file, run_async=True))    
    dispatcher.add_handler(MessageHandler(Filters.all, alll, run_async=True))
    
    updater.start_polling(timeout=15, read_latency=4)
    logger.info("Listening using polling")
    updater.idle()

if __name__ == "__main__":
    main()
    

