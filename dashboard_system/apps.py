from django.apps import AppConfig


class DashboardSystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard_system'
    verbose_name = 'AIMS Dashboard System v2.0'
    
    def ready(self):
        """Initialize Dashboard System when Django starts"""
        print("🚀 AIMS Dashboard System v2.0 - Management Analytics Platform Ready!")
