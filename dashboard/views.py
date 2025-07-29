from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .database_utils import get_staff_summary,get_student_summary,get_db_connection
import json
import mysql.connector
from .sheets_utils import get_service_statistics, get_formatted_statistics
from django.http import JsonResponse

@login_required
def dashboard_home(request):
    """
    หน้าหลักสำหรับเลือกประเภท Dashboard
    """
    return render(request, 'dashboard/index.html')

@login_required
def staff_dashboard(request):
    """
    แสดง Dashboard ข้อมูลบุคลากร
    """
    # ดึงข้อมูลสรุปบุคลากร
    summary = get_staff_summary()
    
    if not summary:
        # กรณีเกิดข้อผิดพลาดในการดึงข้อมูล
        return render(request, 'dashboard/error.html', {'error_message': 'ไม่สามารถดึงข้อมูลบุคลากรได้'})
    
    # เตรียมข้อมูลสำหรับแสดงผลในกราฟ
    department_labels = [dept['DEPARTMENTNAME'] or 'ไม่ระบุ' for dept in summary['department_distribution']]
    department_data = [dept['count'] for dept in summary['department_distribution']]
    
    staff_type_labels = [stype['STFTYPENAME'] or 'ไม่ระบุ' for stype in summary['staff_type_distribution']]
    staff_type_data = [stype['count'] for stype in summary['staff_type_distribution']]
    
    gender_labels = [gender['GENDERNAMETH'] or 'ไม่ระบุ' for gender in summary['gender_distribution']]
    gender_data = [gender['count'] for gender in summary['gender_distribution']]
    
    context = {
        'total_staff': summary['total_staff'],
        'department_labels': json.dumps(department_labels[:10]),  # แสดง 10 อันดับแรก
        'department_data': json.dumps(department_data[:10]),
        'staff_type_labels': json.dumps(staff_type_labels),
        'staff_type_data': json.dumps(staff_type_data),
        'gender_labels': json.dumps(gender_labels),
        'gender_data': json.dumps(gender_data),
        'departments': summary['department_distribution'][:10]  # แสดง 10 หน่วยงานที่มีบุคลากรมากที่สุด
    }
    
    return render(request, 'dashboard/staff_dashboard.html', context)

@login_required
def student_dashboard(request):
    """
    แสดง Dashboard ข้อมูลนักศึกษา
    """
    # ตรวจสอบว่าผู้ใช้มีสิทธิ์เข้าถึง
    if hasattr(request.user, 'is_academic_service') and request.user.is_academic_service:
        # ดึงข้อมูลสรุปนักศึกษา
        summary = get_student_summary()
        
        if not summary:
            # กรณีเกิดข้อผิดพลาดในการดึงข้อมูล
            return render(request, 'dashboard/error.html', {'error_message': 'ไม่สามารถดึงข้อมูลนักศึกษาได้'})
        
        # เตรียมข้อมูลสำหรับแสดงผลในกราฟ
        faculty_labels = [fac['faculty_name'] or 'ไม่ระบุ' for fac in summary['faculty_distribution']]
        faculty_data = [fac['count'] for fac in summary['faculty_distribution']]
        
        program_labels = [prog['program_name'] or 'ไม่ระบุ' for prog in summary['program_distribution']]
        program_data = [prog['count'] for prog in summary['program_distribution']]
        
        level_labels = [level['level_name'] or 'ไม่ระบุ' for level in summary['education_level_distribution']]
        level_data = [level['count'] for level in summary['education_level_distribution']]
        
        gender_labels = [gender['gender'] for gender in summary['gender_distribution']]
        gender_data = [gender['count'] for gender in summary['gender_distribution']]
        
        year_labels = [str(year['year']) for year in summary['year_distribution']]
        year_data = [year['count'] for year in summary['year_distribution']]
        
        context = {
            'total_students': summary['total_students'],
            'faculty_labels': json.dumps(faculty_labels[:10]),  # แสดง 10 อันดับแรก
            'faculty_data': json.dumps(faculty_data[:10]),
            'program_labels': json.dumps(program_labels[:10]),
            'program_data': json.dumps(program_data[:10]),
            'level_labels': json.dumps(level_labels),
            'level_data': json.dumps(level_data),
            'gender_labels': json.dumps(gender_labels),
            'gender_data': json.dumps(gender_data),
            'year_labels': json.dumps(year_labels),
            'year_data': json.dumps(year_data),
            'faculties': summary['faculty_distribution'][:10],  # แสดง 10 คณะที่มีนักศึกษามากที่สุด
            'programs': summary['program_distribution'][:10]  # แสดง 10 สาขาที่มีนักศึกษามากที่สุด
        }
        
        return render(request, 'dashboard/student_dashboard.html', context)
    else:
        return render(request, 'dashboard/unauthorized.html')
    
def test_database_connection(request):
    """
    ทดสอบการเชื่อมต่อฐานข้อมูลและแสดงผลลัพธ์
    """
    if not request.user.is_superuser:
        return redirect('dashboard:home')
        
    connection = get_db_connection()
    status = {}
    
    if connection:
        status['connected'] = True
        
        # ทดสอบตาราง staff_info
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM staff_info")
            record = cursor.fetchone()
            status['staff_count'] = record[0]
            status['staff_table_exists'] = True
        except mysql.connector.Error:
            status['staff_table_exists'] = False
            
        # ทดสอบตาราง students_info
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM students_info")
            record = cursor.fetchone()
            status['student_count'] = record[0]
            status['student_table_exists'] = True
        except mysql.connector.Error:
            status['student_table_exists'] = False
            
        connection.close()
    else:
        status['connected'] = False
    
    return render(request, 'dashboard/db_test.html', {'status': status})

@login_required
def service_statistics_view(request):
    """
    แสดงหน้าสถิติบริการ
    """
    # ดึงข้อมูลจาก Google Sheet
    all_stats = get_service_statistics()
    
    # แยกข้อมูลปี 2567 และ 2568 เท่านั้น (ไม่รวมปี 2566)
    data_2567 = [item for item in all_stats if item['year'] == '2567']
    data_2568 = [item for item in all_stats if item['year'] == '2568']
    
    print(f"ข้อมูลปี 2567: {len(data_2567)} รายการ")
    print(f"ข้อมูลปี 2568: {len(data_2568)} รายการ")
    
    # เรียงข้อมูลตามเดือน
    thai_month_order = {
        'ม.ค.': 1, 'ก.พ.': 2, 'มี.ค.': 3, 'เม.ย.': 4, 'พ.ค.': 5, 'มิ.ย.': 6,
        'ก.ค.': 7, 'ส.ค.': 8, 'ก.ย.': 9, 'ต.ค.': 10, 'พ.ย.': 11, 'ธ.ค.': 12
    }
    
    data_2567.sort(key=lambda x: thai_month_order.get(x['month'], 0))
    data_2568.sort(key=lambda x: thai_month_order.get(x['month'], 0))
    
    # เตรียมข้อมูลสำหรับกราฟ
    months = ['ม.ค.', 'ก.พ.', 'มี.ค.', 'เม.ย.', 'พ.ค.', 'มิ.ย.', 
              'ก.ค.', 'ส.ค.', 'ก.ย.', 'ต.ค.', 'พ.ย.', 'ธ.ค.']
    
    # เตรียมข้อมูลสำหรับกราฟเปรียบเทียบรายเดือน
    chart_data = {
        'labels': months,
        'data_2567': [0] * 12,
        'data_2568': [0] * 12
    }
    
    # เติมข้อมูลปี 2567
    for item in data_2567:
        month_index = thai_month_order.get(item['month'], 0) - 1
        if 0 <= month_index < 12:
            chart_data['data_2567'][month_index] = item['visit_count']
    
    # เติมข้อมูลปี 2568
    for item in data_2568:
        month_index = thai_month_order.get(item['month'], 0) - 1
        if 0 <= month_index < 12:
            chart_data['data_2568'][month_index] = item['visit_count']
    
    # คำนวณผลรวมรายปี
    sum_2567 = sum(item['visit_count'] for item in data_2567)
    sum_2568 = sum(item['visit_count'] for item in data_2568)
    
    # สรุปข้อมูล
    diff_percent = 0
    if sum_2567 > 0:
        diff_percent = ((sum_2568 - sum_2567) / sum_2567) * 100
    
    summary = {
        'total_2567': sum_2567,
        'total_2568': sum_2568,
        'diff_percent': diff_percent
    }
    
    print(f"สรุปข้อมูล: {summary}")
    print(f"ข้อมูลกราฟ: {chart_data}")
    
    # ส่งเฉพาะข้อมูลปี 2567 และ 2568 ไปยังเทมเพลต
    context = {
        'data_2567': data_2567,
        'data_2568': data_2568,
        'chart_data': chart_data,
        'summary': summary
    }
    
    return render(request, 'dashboard/service_statistics.html', context)

def test_sheets_api(request):
    from .sheets_utils import test_sheets_connection
    
    result = test_sheets_connection()
    
    return JsonResponse({
        'success': result,
        'message': 'Connection successful' if result else 'Connection failed'
    })

def test_raw_sheets_data(request):
    """
    ทดสอบดึงข้อมูลดิบจาก Google Sheets
    """
    from .sheets_utils import get_raw_sheet_data
    
    data = get_raw_sheet_data()
    
    return JsonResponse({
        'success': data is not None,
        'message': 'Data retrieved successfully' if data else 'Failed to retrieve data',
        'data': data
    })