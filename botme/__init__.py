import os
import logging

from telegram import ParseMode
from telegram.ext import Updater, Defaults

from pytz import timezone

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from botme.config import Required, Optional


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TOKEN") or Required.TOKEN
OWNER = os.environ.get("OWNER") or Required.OWNER
DATABASE_URL = os.environ.get("DATABASE_URL") or Required.DATABASE_URL
TZ = os.environ.get("TZ", "UTC") or Optional.TZ

defaults = Defaults(
    parse_mode=ParseMode.MARKDOWN, tzinfo=timezone(TZ), run_async=True
)

updater = Updater(token=TOKEN, defaults=defaults)
dispatcher = updater.dispatcher
jobstores = {
        "default": SQLAlchemyJobStore(DATABASE_URL)
        }
j = updater.job_queue
j.scheduler = BackgroundScheduler(timezone=timezone(TZ), jobstores=jobstores)

