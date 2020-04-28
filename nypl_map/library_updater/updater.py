from apscheduler.schedulers.background import BackgroundScheduler
from nypl_map.library_updater.data_manager import DataManager
from nypl_map.models import Library

import logging


def start():
    datamanager = DataManager()

    logging.basicConfig()
    logging.getLogger('apscheduler').setLevel(logging.DEBUG)

    scheduler = BackgroundScheduler()
    scheduler.add_job(datamanager.scrape_nypl_info, 'interval', hours=1)
    scheduler.start()
