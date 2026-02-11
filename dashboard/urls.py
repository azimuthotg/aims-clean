# aims_project/dashboard/urls.py
from django.urls import path
from . import views
from .push_notifications import subscribe_push, unsubscribe_push, test_notification

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('staff/', views.staff_dashboard, name='staff'),
    # Export Excel - ใช้ URL แยกต่างหากเพื่อหลีกเลี่ยงปัญหา path matching
    path('staff/export/department/<path:department_name>/', views.export_department_excel, name='export_department_excel'),
    path('staff/department/<path:department_name>/', views.department_detail, name='department_detail'),
    path('student/', views.student_dashboard, name='student'),
    path('student/faculty/<path:faculty_name>/', views.faculty_detail, name='faculty_detail'),
    path('student/level/<path:level_name>/', views.level_detail, name='level_detail'),
    
    # Export URLs
    path('student/export/excel/', views.export_student_excel, name='export_student_excel'),
    
    path('db-test/', views.test_database_connection, name='db_test'),
    path('service-statistics/', views.service_statistics_view, name='service_statistics'),  # เพิ่มเส้นทางใหม่
    path('test-api/', views.test_sheets_api, name='test_sheets_api'),
    path('test-raw-data/', views.test_raw_sheets_data, name='test_raw_sheets_data'),
    
    # Push Notifications URLs
    path('push/subscribe/', subscribe_push, name='push_subscribe'),
    path('push/unsubscribe/', unsubscribe_push, name='push_unsubscribe'),
    path('push/test/', test_notification, name='push_test'),
]