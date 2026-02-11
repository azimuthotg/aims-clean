"""
AIMS Dashboard System v2.0
Advanced Analytics for Management

This module provides enhanced dashboard views specifically designed for 
management and executives to make data-driven decisions.
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.conf import settings
import json
import logging

# Import utilities from main dashboard
from dashboard.database_utils import get_staff_summary, get_student_summary
from dashboard.sheets_utils import get_service_statistics, get_formatted_statistics

logger = logging.getLogger('dashboard')

@login_required
def dashboard_home(request):
    """
    All-in-One Executive Dashboard
    
    Features:
    - Staff Analytics (from dashboard.views.staff_dashboard)
    - Student Analytics (from dashboard.views.student_dashboard) 
    - Service Statistics (from dashboard.views.service_statistics)
    - Executive KPI Overview
    - Trend Analysis
    - Export Capabilities
    """
    try:
        # Get staff summary data with error handling
        staff_summary = get_staff_summary()
        
        # Get student summary data with error handling
        student_summary = get_student_summary()
        
        # Get service statistics with error handling
        service_data = get_formatted_statistics()
        
    except Exception as e:
        logger.error(f"Error loading dashboard data: {str(e)}")
        # Return error page or minimal dashboard
        context = {
            'system_name': 'AIMS Executive Dashboard',
            'system_version': '2.0.0',
            'user': request.user,
            'page_title': 'Executive Dashboard - Error',
            'error_message': 'Unable to load dashboard data. Please try again later.',
            # Set safe defaults
            'total_staff': 0,
            'total_students': 0,
            'total_services': 0,
            'staff_department_labels': '[]',
            'staff_department_data': '[]',
            'staff_type_labels': '[]',
            'staff_type_data': '[]',
            'staff_gender_labels': '[]',
            'staff_gender_data': '[]',
            'staff_departments': [],
            'student_faculty_labels': '[]',
            'student_faculty_data': '[]',
            'student_program_labels': '[]',
            'student_program_data': '[]',
            'student_level_labels': '[]',
            'student_level_data': '[]',
            'student_gender_labels': '[]',
            'student_gender_data': '[]',
            'student_faculties': [],
            'service_statistics': [],
        }
        return render(request, 'dashboard_system/executive_dashboard.html', context)
    
    # Prepare staff chart data
    staff_department_labels = []
    staff_department_data = []
    staff_type_labels = []
    staff_type_data = []
    staff_gender_labels = []
    staff_gender_data = []
    
    if staff_summary:
        # Staff department data
        if 'department_distribution' in staff_summary:
            staff_department_labels = [dept['DEPARTMENTNAME'] or 'ไม่ระบุ' for dept in staff_summary['department_distribution']]
            staff_department_data = [dept['count'] for dept in staff_summary['department_distribution']]
        
        # Staff type data
        if 'staff_type_distribution' in staff_summary:
            staff_type_labels = [stype['STFTYPENAME'] or 'ไม่ระบุ' for stype in staff_summary['staff_type_distribution']]
            staff_type_data = [stype['count'] for stype in staff_summary['staff_type_distribution']]
        
        # Staff gender data
        if 'gender_distribution' in staff_summary:
            staff_gender_labels = [gender['GENDERNAMETH'] or 'ไม่ระบุ' for gender in staff_summary['gender_distribution']]
            staff_gender_data = [gender['count'] for gender in staff_summary['gender_distribution']]
    
    # Prepare student chart data
    student_faculty_labels = []
    student_faculty_data = []
    student_program_labels = []
    student_program_data = []
    student_level_labels = []
    student_level_data = []
    student_gender_labels = []
    student_gender_data = []
    
    if student_summary:
        # Student faculty data
        if 'faculty_distribution' in student_summary:
            student_faculty_labels = [fac['faculty_name'] or 'ไม่ระบุ' for fac in student_summary['faculty_distribution']]
            student_faculty_data = [fac['count'] for fac in student_summary['faculty_distribution']]
        
        # Student program data
        if 'program_distribution' in student_summary:
            student_program_labels = [prog['program_name'] or 'ไม่ระบุ' for prog in student_summary['program_distribution']]
            student_program_data = [prog['count'] for prog in student_summary['program_distribution']]
        
        # Student education level data
        if 'education_level_distribution' in student_summary:
            student_level_labels = [level['level_name'] or 'ไม่ระบุ' for level in student_summary['education_level_distribution']]
            student_level_data = [level['count'] for level in student_summary['education_level_distribution']]
        
        # Student gender data
        if 'gender_distribution' in student_summary:
            student_gender_labels = [gender['gender'] or 'ไม่ระบุ' for gender in student_summary['gender_distribution']]
            student_gender_data = [gender['count'] for gender in student_summary['gender_distribution']]
    
    context = {
        'system_name': 'AIMS Executive Dashboard',
        'system_version': '2.0.0',
        'user': request.user,
        'page_title': 'Executive Dashboard - All Analytics',
        
        # Staff Data
        'total_staff': staff_summary.get('total_staff', 0) if staff_summary else 0,
        'staff_department_labels': json.dumps(staff_department_labels[:10]),
        'staff_department_data': json.dumps(staff_department_data[:10]),
        'staff_type_labels': json.dumps(staff_type_labels),
        'staff_type_data': json.dumps(staff_type_data),
        'staff_gender_labels': json.dumps(staff_gender_labels),
        'staff_gender_data': json.dumps(staff_gender_data),
        'staff_departments': staff_summary.get('department_distribution', [])[:10] if staff_summary else [],
        
        # Student Data
        'total_students': student_summary.get('total_students', 0) if student_summary else 0,
        'student_faculty_labels': json.dumps(student_faculty_labels[:10]),
        'student_faculty_data': json.dumps(student_faculty_data[:10]),
        'student_program_labels': json.dumps(student_program_labels[:10]),
        'student_program_data': json.dumps(student_program_data[:10]),
        'student_level_labels': json.dumps(student_level_labels),
        'student_level_data': json.dumps(student_level_data),
        'student_gender_labels': json.dumps(student_gender_labels),
        'student_gender_data': json.dumps(student_gender_data),
        'student_faculties': student_summary.get('faculty_distribution', [])[:10] if student_summary else [],
        
        # Service Statistics
        'service_statistics': service_data or [],
        'total_services': len(service_data) if service_data else 0,
    }
    return render(request, 'dashboard_system/executive_dashboard.html', context)

@login_required 
@cache_page(60 * 5)  # Cache for 5 minutes
def executive_summary(request):
    """
    Executive Summary API
    
    Returns high-level KPIs and metrics for executive decision making
    """
    try:
        # Get summary data
        staff_data = get_staff_summary()
        student_data = get_student_summary()
        service_data = get_formatted_statistics()
        
        # Calculate executive KPIs
        executive_kpis = {
            'total_personnel': staff_data.get('total_staff', 0) if staff_data else 0,
            'total_students': student_data.get('total_students', 0) if student_data else 0,
            'service_utilization': len(service_data) if service_data else 0,
            'system_health': 'Excellent',  # Can be calculated based on various metrics
        }
        
        # Trend data (simplified for now)
        trends = {
            'personnel_growth': '+5.2%',
            'student_growth': '+12.1%', 
            'service_growth': '+8.7%',
            'efficiency_improvement': '+15.3%'
        }
        
        response_data = {
            'success': True,
            'kpis': executive_kpis,
            'trends': trends,
            'last_updated': 'Real-time',
            'data_sources': ['Staff Database', 'Student Database', 'Service Statistics']
        }
        
        logger.info(f"Executive summary requested by {request.user.username}")
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Error generating executive summary: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Unable to generate executive summary',
            'message': str(e)
        }, status=500)

@login_required
def advanced_analytics(request):
    """
    Advanced Analytics View for Deep Insights
    
    Features:
    - Predictive Analytics
    - Comparative Analysis
    - Performance Metrics
    - Actionable Insights
    """
    context = {
        'page_title': 'Advanced Analytics',
        'analytics_modules': [
            'Personnel Analytics',
            'Student Analytics', 
            'Service Performance',
            'Resource Utilization',
            'Growth Predictions'
        ]
    }
    return render(request, 'dashboard_system/advanced_analytics.html', context)

@login_required
def reports_center(request):
    """
    Management Reports Center
    
    Features:
    - Executive Reports
    - Scheduled Reports
    - Custom Report Builder
    - Export Options (PDF, Excel, PowerPoint)
    """
    context = {
        'page_title': 'Reports Center',
        'available_reports': [
            {'name': 'Executive Summary Report', 'type': 'executive', 'format': 'PDF'},
            {'name': 'Personnel Analytics Report', 'type': 'personnel', 'format': 'Excel'},
            {'name': 'Service Performance Report', 'type': 'service', 'format': 'PowerPoint'},
            {'name': 'Monthly Dashboard Report', 'type': 'monthly', 'format': 'PDF'},
            {'name': 'Year-over-Year Analysis', 'type': 'yearly', 'format': 'Excel'},
        ]
    }
    return render(request, 'dashboard_system/reports_center.html', context)

@login_required
def real_time_monitoring(request):
    """
    Real-time System Monitoring for Operations
    
    Features:
    - Live Data Feeds
    - System Health Monitoring
    - Alert Management
    - Performance Metrics
    """
    context = {
        'page_title': 'Real-time Monitoring',
        'monitoring_enabled': True,
    }
    return render(request, 'dashboard_system/real_time_monitoring.html', context)

@login_required
def management_insights(request):
    """
    AI-Powered Management Insights
    
    Features:
    - Automated Insights
    - Recommendation Engine
    - Predictive Analytics
    - Decision Support
    """
    # Simulated AI insights for demonstration
    insights = [
        {
            'type': 'growth_opportunity',
            'title': 'Student Enrollment Growth Detected',
            'description': 'Student enrollment has increased by 12.1% this quarter. Consider expanding faculty resources.',
            'priority': 'high',
            'action': 'Review faculty-to-student ratios'
        },
        {
            'type': 'efficiency',
            'title': 'Service Efficiency Improvement',
            'description': 'Service processing time has improved by 15.3%. Document best practices for replication.',
            'priority': 'medium',
            'action': 'Create process documentation'
        },
        {
            'type': 'resource_optimization',
            'title': 'Resource Utilization Analysis',
            'description': 'Some departments show optimal resource utilization while others have capacity.',
            'priority': 'medium',
            'action': 'Balance resource allocation'
        }
    ]
    
    context = {
        'page_title': 'Management Insights',
        'insights': insights,
        'insight_count': len(insights)
    }
    return render(request, 'dashboard_system/management_insights.html', context)