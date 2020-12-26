from telegram import (
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


class KeyboardMarkup(ReplyKeyboardMarkup):
    def __init__(self, array, resize_keyboard=True, **kwargs):
        super().__init__(array, resize_keyboard=resize_keyboard, **kwargs)


class Button(InlineKeyboardButton):
    def __init__(self, array, callback_data):
        super().__init__(array, callback_data=callback_data)


def utimeout(query, j, job_id):
    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Back", callback_data="call_ok")]]
    )

    j.remove_job(job_id)
    query.edit_message_text(
        "Mohon untuk segera memilih", reply_markup=reply_markup
    )


def text_status(db, user_id):
    result = sorted(db.check_result(user_id))
    if result:
        for i in result:
            time = i[2].split("/")
            t = ""
            if time[0]:
                t += f"{time[0]} hari "
            if int(time[1][0]):
                t += f"{time[1]} jam "
            if int(time[2][0]):
                t += f"{time[2]} menit "
            else:
                t += f"{time[3]} detik "
            
            yield f"`No    => {i[0]}\nSurah => {i[1]}\nWaktu => {t}`\n\n"
    else:
        yield "Sepertinya anda belum menghafal"


def chinterval(query, db, j, status, o):
    user_id = str(query.from_user.id)
    interval = db.interval(user_id, "GET")[1]
    if j.get_job(user_id):
        if interval > 23 and o:
            db.interval(user_id, "CHANGE", INTERVAL=23, opt=0)
        elif interval < 2 and not o:
            db.interval(user_id, "CHANGE", INTERVAL=23, opt=1)
        else:
            db.interval(user_id, "CHANGE", opt=o)
        status(query, None)
        j.reschedule_job(
            user_id, trigger="interval", hours=db.interval(user_id, "GET")[1]
        )
    else:
        query.edit_message_text("Anda harus klik `Mulai` dulu")
