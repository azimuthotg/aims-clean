# aims_project/dashboard/urls.py
from django.urls import path
from . import views
from .push_notifications import subscribe_push, unsubscribe_push

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('staff/', views.staff_dashboard, name='staff'),
    path('staff/export/excel/', views.export_staff_excel, name='export_staff_excel'),
    path('staff/export/department/<path:department_name>/', views.export_department_excel, name='export_department_excel'),
    path('staff/department/<path:department_name>/', views.department_detail, name='department_detail'),
    path('student/', views.student_dashboard, name='student'),
    path('student/faculty/export/<path:faculty_name>/', views.export_faculty_excel, name='export_faculty_excel'),
    path('student/faculty/<path:faculty_name>/', views.faculty_detail, name='faculty_detail'),
    path('student/level/export/<path:level_name>/', views.export_level_excel, name='export_level_excel'),
    path('student/level/<path:level_name>/', views.level_detail, name='level_detail'),
    path('student/export/excel/', views.export_student_excel, name='export_student_excel'),
    path('service-statistics/', views.service_statistics_view, name='service_statistics'),

    # Push Notifications
    path('push/subscribe/', subscribe_push, name='push_subscribe'),
    path('push/unsubscribe/', unsubscribe_push, name='push_unsubscribe'),
]