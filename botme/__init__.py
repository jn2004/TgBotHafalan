import os
import logging

from telegram.ext import Updater

from apscheduler.schedulers.background import BackgroundScheduler

from botme.config import TOKEN

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher
j = updater.job_queue
j.scheduler = BackgroundScheduler(timezone="Asia/Jakarta")
