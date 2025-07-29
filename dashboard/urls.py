# aims_project/dashboard/urls.py
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('staff/', views.staff_dashboard, name='staff'),
    path('student/', views.student_dashboard, name='student'),
    path('db-test/', views.test_database_connection, name='db_test'),
    path('service-statistics/', views.service_statistics_view, name='service_statistics'),  # เพิ่มเส้นทางใหม่
    path('test-api/', views.test_sheets_api, name='test_sheets_api'),
    path('test-raw-data/', views.test_raw_sheets_data, name='test_raw_sheets_data'),
]