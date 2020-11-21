import importlib

from apscheduler.jobstores.base import JobLookupError

from telegram.ext import (
    CommandHandler,
    MessageHandler,
    Filters,
)

from botme import dispatcher, updater, logger
from botme.core import modules

for module in modules:
    importlib.import_module(f"botme.core.{module}")


def main():
    updater.start_polling()
    logger.info("Listening using polling")
    updater.idle()


if __name__ == "__main__":
    main()
