from telegram.error import Conflict

from botme import dispatcher, j
from . import function
from .database import db

OWNER = [1328007524, 1399167510]


def error_handler(update, context):
    try:
        raise context.error
    except Conflict:
        if db.getid():
            for i in db.getid():
                if not j.get_job(str(i[0])):
                    j.add_job(
                        function.call,
                        "interval",
                        hours=2,
                        args=(int(i[0]),),
                        id=str(i[0]),
                    )
        else:
            print("h")

        context.bot.send_message(
            chat_id=OWNER[0],
            text=str(context.error),
        )


dispatcher.add_error_handler(error_handler)
