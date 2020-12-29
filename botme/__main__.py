import importlib

from botme import updater, logger, j, OWNER
from botme.core import modules, function, database
from botme.core.database import db

for module in modules:
    importlib.import_module(f"botme.core.{module}")


def main():
    if database.db.start(method="GET"):
        updater.bot.send_message(chat_id=OWNER, text="Restarting...")
        for i in database.db.start(method="GET"):
            if not j.get_job(str(i[0])):
                j.add_job(
                    function.ask,
                    "interval",
                    hours=database.db.interval(i[0], "GET")[1],
                    args=(i[0],),
                    id=str(i[0]),
                )

    updater.start_polling()
    logger.info("Listening using polling")

    updater.idle()


if __name__ == "__main__":
    main()
