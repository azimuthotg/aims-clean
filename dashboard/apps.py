from django.apps import AppConfig


class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'

    def ready(self):
        # APScheduler disabled — ใช้ Windows Task Scheduler แทน
        # ดู deploy/task_scheduler/ สำหรับ .bat files
        pass
