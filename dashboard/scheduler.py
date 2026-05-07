import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore

logger = logging.getLogger(__name__)


def sync_staff_job():
    from dashboard.management.commands.sync_staff import run_sync_staff
    try:
        log = run_sync_staff(triggered_by='schedule')
        logger.info(f'[scheduler] sync_staff complete: {log.records_synced} records')
    except Exception as e:
        logger.error(f'[scheduler] sync_staff failed: {e}')


def sync_students_job():
    from dashboard.management.commands.sync_students import run_sync_students
    try:
        log = run_sync_students(triggered_by='schedule')
        logger.info(f'[scheduler] sync_students complete: {log.records_synced} records')
    except Exception as e:
        logger.error(f'[scheduler] sync_students failed: {e}')


def start():
    scheduler = BackgroundScheduler(timezone='Asia/Bangkok')
    scheduler.add_jobstore(DjangoJobStore(), 'default')

    scheduler.add_job(
        sync_staff_job,
        trigger=CronTrigger(hour=2, minute=0),
        id='sync_staff_daily',
        replace_existing=True,
        misfire_grace_time=3600,
    )
    scheduler.add_job(
        sync_students_job,
        trigger=CronTrigger(hour=2, minute=30),
        id='sync_students_daily',
        replace_existing=True,
        misfire_grace_time=3600,
    )

    scheduler.start()
    logger.info('[scheduler] APScheduler started — sync_staff@02:00, sync_students@02:30')
