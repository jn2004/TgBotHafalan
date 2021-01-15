from telegram.error import Conflict

from botme import dispatcher, OWNER
from . import function
from .database import db


def error_handler(update, context):
    try:
        raise context.error
    except:
        raise context.error

    context.bot.send_message(
        chat_id=int(OWNER),
        text=f"Saya terjadi error:(\n`{context.error}`",
    )


# dispatcher.add_error_handler(error_handler)
