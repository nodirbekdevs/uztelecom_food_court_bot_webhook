from src.loader import scheduler
from src.schedule.interval import update_token


def run_schedule():
    scheduler.add_job(update_token, 'interval', minutes=25)
    scheduler.start()
