import os
from django.core.management.base import BaseCommand
from django.utils import timezone

import mysql.connector

try:
    import oracledb
    ORACLE_AVAILABLE = True
except ImportError:
    ORACLE_AVAILABLE = False

ORACLE_QUERY = """
SELECT V.STUDENTCODE, V.PREFIXNAME, V.STUDENTNAME, V.STUDENTSURNAME,
       V.LEVELID, V.LEVELNAME, V.PROGRAMNAME, V.DEGREENAME, V.FACULTYNAME,
       VP.APASSWORD
FROM AVSREG.VIEWSTUDENTINFO V, AVSREG.VIEWSYSSTUDENTPASSWORD VP
WHERE V.STUDENTID = VP.STUDENTID
AND V.STUDENTSTATUS < 40
ORDER BY V.LEVELID, NLSSORT(V.PROGRAMNAME, 'NLS_SORT=THAI_DICTIONARY'), V.STUDENTCODE
"""

INSERT_QUERY = """
INSERT INTO students_info (student_code, prefix_name, student_name, student_surname,
                           level_id, level_name, program_name, degree_name, faculty_name, apassword)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""


def run_sync_students(triggered_by='manual', triggered_user=None, existing_log=None):
    from dashboard.models import SyncLog

    if existing_log is not None:
        log = existing_log
    else:
        log = SyncLog.objects.create(
            table_name='students_info',
            status='running',
            triggered_by=triggered_by,
            triggered_user=triggered_user,
        )

    if not ORACLE_AVAILABLE:
        log.status = 'failed'
        log.error_message = 'oracledb library not installed. Run: pip install oracledb'
        log.finished_at = timezone.now()
        log.save(update_fields=['status', 'error_message', 'finished_at'])
        raise ImportError('oracledb not installed')

    oracle_conn = None
    mysql_conn = None
    try:
        # Init Oracle client (thick mode) if lib_dir is configured
        oracle_lib = os.getenv('ORACLE_CLIENT_LIB', '')
        if oracle_lib:
            oracledb.init_oracle_client(lib_dir=oracle_lib)

        oracle_dsn = os.getenv(
            'ORACLE_DSN',
            "(DESCRIPTION=(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)"
            f"(HOST={os.getenv('ORACLE_HOST','202.29.55.15')})(PORT={os.getenv('ORACLE_PORT','1521')})))"
            f"(CONNECT_DATA=(SERVICE_NAME={os.getenv('ORACLE_SERVICE','npu')})))"
        )
        oracle_conn = oracledb.connect(
            user=os.getenv('ORACLE_USER', 'admin_e'),
            password=os.getenv('ORACLE_PASSWORD', ''),
            dsn=oracle_dsn,
        )
        oracle_cursor = oracle_conn.cursor()

        mysql_conn = mysql.connector.connect(
            host=os.getenv('API_DB_HOST', '202.29.55.213'),
            user=os.getenv('API_DB_USER', 'admin_e'),
            password=os.getenv('API_DB_PASSWORD', ''),
            database=os.getenv('API_DB_NAME', 'api'),
            ssl_disabled=True,
        )
        mysql_cursor = mysql_conn.cursor()

        # Count records before
        mysql_cursor.execute("SELECT COUNT(*) FROM students_info")
        records_before = mysql_cursor.fetchone()[0]
        log.records_before = records_before
        log.save(update_fields=['records_before'])

        # Fetch Oracle data
        oracle_cursor.execute(ORACLE_QUERY)
        oracle_data = oracle_cursor.fetchall()

        # DELETE all + bulk INSERT in a single transaction (atomic, InnoDB MVCC safe)
        BATCH_SIZE = 500
        mysql_cursor.execute("DELETE FROM students_info")

        synced = 0
        batch = []
        for row in oracle_data:
            batch.append((
                row[0], row[1], row[2], row[3], row[4],
                row[5], row[6], row[7], row[8], row[9],
            ))
            if len(batch) >= BATCH_SIZE:
                mysql_cursor.executemany(INSERT_QUERY, batch)
                synced += len(batch)
                batch = []
        if batch:
            mysql_cursor.executemany(INSERT_QUERY, batch)
            synced += len(batch)

        mysql_conn.commit()

        # Count records after
        mysql_cursor.execute("SELECT COUNT(*) FROM students_info")
        records_after = mysql_cursor.fetchone()[0]

        log.status = 'success'
        log.records_synced = synced
        log.records_after = records_after
        log.finished_at = timezone.now()
        log.save(update_fields=['status', 'records_synced', 'records_after', 'finished_at'])

        oracle_cursor.close()
        mysql_cursor.close()
        return log

    except Exception as e:
        log.status = 'failed'
        log.error_message = str(e)
        log.finished_at = timezone.now()
        log.save(update_fields=['status', 'error_message', 'finished_at'])
        raise
    finally:
        if oracle_conn:
            oracle_conn.close()
        if mysql_conn and mysql_conn.is_connected():
            mysql_conn.close()


class Command(BaseCommand):
    help = 'Sync students_info from Oracle source database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--triggered-by',
            default='manual',
            help='Who triggered this sync (manual, schedule, etc.)',
        )

    def handle(self, *args, **kwargs):
        triggered_by = kwargs.get('triggered_by', 'manual')
        self.stdout.write(f'Starting students_info sync (triggered_by={triggered_by})...')
        try:
            log = run_sync_students(triggered_by=triggered_by)
            self.stdout.write(self.style.SUCCESS(
                f'Sync completed: {log.records_synced} records synced '
                f'(before={log.records_before}, after={log.records_after}, '
                f'duration={log.duration_seconds}s)'
            ))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Sync failed: {e}'))
