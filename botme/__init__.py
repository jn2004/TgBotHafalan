import os
import logging

from telegram import ParseMode
from telegram.ext import Updater, Defaults

from pytz import timezone

from botme.config import TOKEN

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")

    
defaults = Defaults(
    parse_mode=ParseMode.MARKDOWN,
    tzinfo=timezone("Asia/Jakarta"),
    run_async=True,
)
updater = Updater(token=TOKEN, defaults=defaults)
dispatcher = updater.dispatcher
j = updater.job_queue.scheduler
