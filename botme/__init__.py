import os
import logging

from telegram import ParseMode
from telegram.ext import Updater, Defaults

from pytz import timezone

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from botme.config import TOKEN, OWNER, DATABASE_URL, TZ


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TOKEN") or TOKEN
OWNER = os.environ.get("OWNER") or OWNER
DATABASE_URL = os.environ.get("DATABASE_URL") or DATABASE_URL
TZ = os.environ.get("TZ", "UTC") or TZ

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

