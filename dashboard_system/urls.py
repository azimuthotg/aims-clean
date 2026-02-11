"""
AIMS Dashboard System v2.0 URLs
Advanced Analytics Dashboard for Management
"""

from django.urls import path
from . import views

app_name = 'dashboard_system'

urlpatterns = [
    # Executive Dashboard Home
    path('', views.dashboard_home, name='home'),
    
    # API Endpoints
    path('api/executive-summary/', views.executive_summary, name='executive_summary'),
    
    # Analytics Views
    path('analytics/', views.advanced_analytics, name='analytics'),
    path('insights/', views.management_insights, name='insights'),
    
    # Reports Center
    path('reports/', views.reports_center, name='reports'),
    
    # Real-time Monitoring
    path('monitoring/', views.real_time_monitoring, name='monitoring'),
]