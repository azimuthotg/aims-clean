from django.apps import AppConfig


class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'

    def ready(self):
        import sys
        import os
        # Only start in server processes, not during migrate/makemigrations/shell/etc.
        server_commands = {'runserver', 'waitress_serve'}
        if not any(cmd in sys.argv for cmd in server_commands):
            return
        if os.environ.get('SCHEDULER_ENABLED', 'true').lower() != 'true':
            return
        try:
            from dashboard import scheduler
            scheduler.start()
        except Exception:
            pass
