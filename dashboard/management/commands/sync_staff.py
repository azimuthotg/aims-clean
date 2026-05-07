import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone

import mysql.connector


SOURCE_QUERY = """
SELECT
    `STAFF_STAFF`.STAFFID,
    `STAFF_STAFF`.STAFFCITIZENID,
    staff_prefix.PREFIXFULLNAME,
    STAFFNAME,
    STAFFSURNAME,
    DATE_FORMAT(STAFFBIRTHDATE, '%d-%m-%Y') as STAFFBIRTHDATE,
    staff_gender.GENDERNAMETH,
    staff_positionname.POSNAMETH,
    staff_stafftype.STFTYPENAME,
    staff_substafftype.SUBSTFTYPENAME,
    staff_staffstatus.STFSTANAME,
    sys_department.DEPARTMENTNAME
FROM `STAFF_STAFF`
    LEFT JOIN staff_position on `STAFF_STAFF`.`POSID` = staff_position.POSID
    LEFT JOIN staff_positionname on `staff_position`.`POSNAMEID` = staff_positionname.POSNAMEID
    LEFT JOIN staff_gender on `STAFF_STAFF`.`GENDERID` = staff_gender.GENDERID
    LEFT JOIN staff_prefix on `STAFF_STAFF`.`PREFIXID`= staff_prefix.PREFIXID
    LEFT JOIN staff_stafftype on `STAFF_STAFF`.`STFTYPEID` = staff_stafftype.STFTYPEID
    LEFT JOIN staff_substafftype on `STAFF_STAFF`.`SUBSTFTYPEID` = staff_substafftype.SUBSTFTYPENAME
    LEFT JOIN staff_staffstatus on `STAFF_STAFF`.`STAFFSTATUS` = staff_staffstatus.STFSTAID
    LEFT JOIN sys_department on staff_position.DEPARTMENTID = sys_department.DEPARTMENTID
WHERE STAFFSTATUS = 1
"""

UPSERT_QUERY = """
INSERT INTO staff_info (
    STAFFID, STAFFCITIZENID, PREFIXFULLNAME, STAFFNAME, STAFFSURNAME,
    STAFFBIRTHDATE, GENDERNAMETH, POSNAMETH, STFTYPENAME, SUBSTFTYPENAME,
    STFSTANAME, DEPARTMENTNAME
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
    STAFFCITIZENID = VALUES(STAFFCITIZENID),
    PREFIXFULLNAME = VALUES(PREFIXFULLNAME),
    STAFFNAME = VALUES(STAFFNAME),
    STAFFSURNAME = VALUES(STAFFSURNAME),
    STAFFBIRTHDATE = VALUES(STAFFBIRTHDATE),
    GENDERNAMETH = VALUES(GENDERNAMETH),
    POSNAMETH = VALUES(POSNAMETH),
    STFTYPENAME = VALUES(STFTYPENAME),
    SUBSTFTYPENAME = VALUES(SUBSTFTYPENAME),
    STFSTANAME = VALUES(STFSTANAME),
    DEPARTMENTNAME = VALUES(DEPARTMENTNAME)
"""


def convert_date(date_str):
    try:
        return datetime.strptime(date_str, '%d-%m-%Y').strftime('%Y-%m-%d')
    except (ValueError, TypeError):
        return None


def run_sync_staff(triggered_by='manual', triggered_user=None, existing_log=None):
    from dashboard.models import SyncLog

    if existing_log is not None:
        log = existing_log
    else:
        log = SyncLog.objects.create(
            table_name='staff_info',
            status='running',
            triggered_by=triggered_by,
            triggered_user=triggered_user,
        )

    source_conn = None
    target_conn = None
    try:
        source_conn = mysql.connector.connect(
            host=os.getenv('STAFF_SRC_HOST', '202.29.55.29'),
            user=os.getenv('STAFF_SRC_USER', 'ge_website'),
            password=os.getenv('STAFF_SRC_PASSWORD', 'gewebsite@npu'),
            database=os.getenv('STAFF_SRC_DB', 'cp665407_npu_staff'),
            ssl_disabled=True,
        )
        target_conn = mysql.connector.connect(
            host=os.getenv('API_DB_HOST', '202.29.55.213'),
            user=os.getenv('API_DB_USER', 'admin_e'),
            password=os.getenv('API_DB_PASSWORD', ''),
            database=os.getenv('API_DB_NAME', 'api'),
            charset='utf8mb4',
            collation='utf8mb4_general_ci',
            ssl_disabled=True,
        )

        src_cursor = source_conn.cursor(prepared=True)
        tgt_cursor = target_conn.cursor()

        # Count records before
        tgt_cursor.execute("SELECT COUNT(*) FROM staff_info")
        records_before = tgt_cursor.fetchone()[0]
        log.records_before = records_before
        log.save(update_fields=['records_before'])

        # Fetch source data
        src_cursor.execute(SOURCE_QUERY)
        rows = src_cursor.fetchall()

        # UPSERT in batches + track synced STAFFIDs
        synced = 0
        synced_ids = []
        batch = []
        BATCH_SIZE = 500
        for row in rows:
            row = list(row)
            synced_ids.append(row[0])  # STAFFID is col 0
            row[5] = convert_date(row[5])
            batch.append(row)
            if len(batch) >= BATCH_SIZE:
                tgt_cursor.executemany(UPSERT_QUERY, batch)
                target_conn.commit()
                synced += len(batch)
                batch = []
        if batch:
            tgt_cursor.executemany(UPSERT_QUERY, batch)
            target_conn.commit()
            synced += len(batch)

        # DELETE stale records (not in source active set)
        if synced_ids:
            placeholders = ','.join(['%s'] * len(synced_ids))
            tgt_cursor.execute(
                f"DELETE FROM staff_info WHERE STAFFID NOT IN ({placeholders})",
                synced_ids,
            )
            target_conn.commit()

        # Count records after
        tgt_cursor.execute("SELECT COUNT(*) FROM staff_info")
        records_after = tgt_cursor.fetchone()[0]

        log.status = 'success'
        log.records_synced = synced
        log.records_after = records_after
        log.finished_at = timezone.now()
        log.save(update_fields=['status', 'records_synced', 'records_after', 'finished_at'])

        src_cursor.close()
        tgt_cursor.close()
        return log

    except Exception as e:
        log.status = 'failed'
        log.error_message = str(e)
        log.finished_at = timezone.now()
        log.save(update_fields=['status', 'error_message', 'finished_at'])
        raise
    finally:
        if source_conn and source_conn.is_connected():
            source_conn.close()
        if target_conn and target_conn.is_connected():
            target_conn.close()


class Command(BaseCommand):
    help = 'Sync staff_info from source MySQL database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--triggered-by',
            default='manual',
            help='Who triggered this sync (manual, schedule, etc.)',
        )

    def handle(self, *args, **kwargs):
        triggered_by = kwargs.get('triggered_by', 'manual')
        self.stdout.write(f'Starting staff_info sync (triggered_by={triggered_by})...')
        try:
            log = run_sync_staff(triggered_by=triggered_by)
            self.stdout.write(self.style.SUCCESS(
                f'Sync completed: {log.records_synced} records synced '
                f'(before={log.records_before}, after={log.records_after}, '
                f'duration={log.duration_seconds}s)'
            ))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Sync failed: {e}'))
