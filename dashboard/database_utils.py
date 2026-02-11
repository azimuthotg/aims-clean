import mysql.connector
from django.conf import settings
import os

def get_db_connection():
    """
    สร้างการเชื่อมต่อกับฐานข้อมูล MySQL
    ใช้ environment variables สำหรับความปลอดภัย
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv('API_DB_HOST', '202.29.55.213'),
            database=os.getenv('API_DB_NAME', 'api'),
            user=os.getenv('API_DB_USER', 'admin_e'),
            password=os.getenv('API_DB_PASSWORD', ''),
            ssl_disabled=True  # Fix SSL wrap_socket error
        )
        return connection
    except mysql.connector.Error as e:
        print(f"เกิดข้อผิดพลาดในการเชื่อมต่อกับฐานข้อมูล: {e}")
        return None

def get_staff_summary():
    """
    ดึงข้อมูลสรุปของบุคลากร
    """
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # ข้อมูลสรุปทั้งหมด
        summary = {}
        
        # จำนวนบุคลากรทั้งหมด
        cursor.execute("SELECT COUNT(*) as total FROM staff_info")
        summary['total_staff'] = cursor.fetchone()['total']
        
        # จำนวนบุคลากรแยกตามเพศ
        cursor.execute("SELECT GENDERNAMETH, COUNT(*) as count FROM staff_info GROUP BY GENDERNAMETH ORDER BY count DESC")
        summary['gender_distribution'] = cursor.fetchall()
        
        # จำนวนบุคลากรแยกตามประเภท
        cursor.execute("SELECT STFTYPENAME, COUNT(*) as count FROM staff_info GROUP BY STFTYPENAME ORDER BY count DESC")
        summary['staff_type_distribution'] = cursor.fetchall()
        
        # จำนวนบุคลากรแยกตามหน่วยงาน
        cursor.execute("SELECT DEPARTMENTNAME, COUNT(*) as count FROM staff_info GROUP BY DEPARTMENTNAME ORDER BY count DESC")
        summary['department_distribution'] = cursor.fetchall()
        
        # ปิดการเชื่อมต่อ
        cursor.close()
        connection.close()
        
        return summary
        
    except mysql.connector.Error as e:
        print(f"เกิดข้อผิดพลาดในการดึงข้อมูล: {e}")
        return None
    finally:
        if connection.is_connected():
            connection.close()

def get_available_years():
    """
    ดึงรายการปีที่มีข้อมูลนักศึกษา
    """
    connection = get_db_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                SUBSTRING(student_code, 1, 2) AS year_code,
                CASE 
                    WHEN CAST(SUBSTRING(student_code, 1, 2) AS UNSIGNED) > 50 
                    THEN CAST(SUBSTRING(student_code, 1, 2) AS UNSIGNED) + 2500
                    ELSE CAST(SUBSTRING(student_code, 1, 2) AS UNSIGNED) + 2600
                END AS buddhist_year,
                COUNT(*) as student_count
            FROM students_info
            WHERE SUBSTRING(student_code, 1, 2) REGEXP '^[0-9]{2}$'
            GROUP BY year_code, buddhist_year
            HAVING student_count > 10
            ORDER BY buddhist_year DESC
        """)
        
        years = cursor.fetchall()
        cursor.close()
        connection.close()
        
        return years
        
    except mysql.connector.Error as e:
        print(f"เกิดข้อผิดพลาดในการดึงข้อมูลปี: {e}")
        return []
    finally:
        if connection and connection.is_connected():
            connection.close()

def get_student_summary(year_filter=None):
    """
    ดึงข้อมูลสรุปของนักศึกษา
    รองรับการกรองตามปี (year_filter = buddhist year เช่น 2568)
    """
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # สร้าง WHERE clause สำหรับกรองปี
        year_condition = ""
        if year_filter:
            year_code = str(year_filter)[-2:]  # เอา 2 หลักท้าย เช่น 2568 -> 68
            year_condition = f"WHERE SUBSTRING(student_code, 1, 2) = '{year_code}'"
        
        # ข้อมูลสรุปทั้งหมด
        summary = {}
        
        # จำนวนนักศึกษาทั้งหมด
        cursor.execute(f"SELECT COUNT(*) as total FROM students_info {year_condition}")
        result = cursor.fetchone()
        summary['total_students'] = result['total'] if result else 0
        
        # จำนวนนักศึกษาแยกตามคณะ
        try:
            cursor.execute(f"SELECT faculty_name, COUNT(*) as count FROM students_info {year_condition} GROUP BY faculty_name ORDER BY count DESC")
            summary['faculty_distribution'] = cursor.fetchall()
        except mysql.connector.Error:
            summary['faculty_distribution'] = []
        
        # จำนวนนักศึกษาแยกตามหลักสูตร/สาขาวิชา และคณะ
        try:
            cursor.execute(f"""
                SELECT program_name, faculty_name, level_name, COUNT(*) as count 
                FROM students_info {year_condition} 
                GROUP BY program_name, faculty_name, level_name 
                ORDER BY faculty_name, count DESC, program_name, level_name
            """)
            summary['program_distribution'] = cursor.fetchall()
        except mysql.connector.Error:
            summary['program_distribution'] = []
        
        # จำนวนนักศึกษาแยกตามระดับการศึกษา
        try:
            cursor.execute(f"SELECT level_name, COUNT(*) as count FROM students_info {year_condition} GROUP BY level_name ORDER BY count DESC")
            summary['education_level_distribution'] = cursor.fetchall()
        except mysql.connector.Error:
            summary['education_level_distribution'] = []
        
        # จำนวนนักศึกษาแยกตามเพศ (ใช้ prefix_name ในการประมาณ)
        try:
            where_clause = year_condition if year_condition else "WHERE 1=1"
            cursor.execute(f"""
                SELECT 
                    CASE 
                        WHEN prefix_name IN ('นาย') THEN 'ชาย' 
                        WHEN prefix_name IN ('นางสาว', 'นาง') THEN 'หญิง'
                        ELSE 'ไม่ระบุ' 
                    END AS gender,
                    COUNT(*) as count 
                FROM students_info 
                {where_clause}
                GROUP BY gender
                ORDER BY count DESC
            """)
            summary['gender_distribution'] = cursor.fetchall()
        except mysql.connector.Error:
            summary['gender_distribution'] = []
        
        # จำนวนนักศึกษาแยกตามปีที่เข้าศึกษา (จากรหัสนักศึกษา)
        try:
            cursor.execute(f"""
                SELECT 
                    SUBSTRING(student_code, 1, 2) AS year_code,
                    COUNT(*) as count
                FROM students_info
                {year_condition}
                GROUP BY year_code
                ORDER BY year_code DESC
            """)
            year_distribution = cursor.fetchall()
            
            # แปลงรหัสปี 2 หลัก เป็นปี พ.ศ. 4 หลัก
            for row in year_distribution:
                try:
                    year_code = int(row['year_code'])
                    if year_code > 50:  # สมมติว่าเป็นปี พ.ศ. 25xx
                        row['year'] = 2500 + year_code
                    else:  # สมมติว่าเป็นปี พ.ศ. 26xx
                        row['year'] = 2600 + year_code
                except (ValueError, TypeError):
                    row['year'] = 'ไม่ระบุ'
            
            summary['year_distribution'] = year_distribution
        except mysql.connector.Error:
            summary['year_distribution'] = []
        
        # ปิดการเชื่อมต่อ
        cursor.close()
        connection.close()
        
        return summary
        
    except mysql.connector.Error as e:
        print(f"เกิดข้อผิดพลาดในการดึงข้อมูลนักศึกษา: {e}")
        return None
    finally:
        if connection and connection.is_connected():
            connection.close()

def get_department_detail(department_name):
    """
    ดึงข้อมูลรายละเอียดของหน่วยงานเฉพาะ
    """
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # ข้อมูลสรุปหน่วยงาน
        department_info = {}
        
        # จำนวนบุคลากรทั้งหมดในหน่วยงาน
        cursor.execute("SELECT COUNT(*) as total FROM staff_info WHERE DEPARTMENTNAME = %s", (department_name,))
        result = cursor.fetchone()
        department_info['total_staff'] = result['total'] if result else 0
        
        # จำนวนบุคลากรแยกตามเพศ
        cursor.execute("""
            SELECT GENDERNAMETH, COUNT(*) as count 
            FROM staff_info 
            WHERE DEPARTMENTNAME = %s 
            GROUP BY GENDERNAMETH 
            ORDER BY count DESC
        """, (department_name,))
        department_info['gender_distribution'] = cursor.fetchall()
        
        # จำนวนบุคลากรแยกตามตำแหน่ง
        cursor.execute("""
            SELECT POSNAMETH, COUNT(*) as count 
            FROM staff_info 
            WHERE DEPARTMENTNAME = %s 
            GROUP BY POSNAMETH 
            ORDER BY count DESC
        """, (department_name,))
        department_info['position_distribution'] = cursor.fetchall()
        
        # จำนวนบุคลากรแยกตามประเภทการจ้าง
        cursor.execute("""
            SELECT STFTYPENAME, COUNT(*) as count 
            FROM staff_info 
            WHERE DEPARTMENTNAME = %s 
            GROUP BY STFTYPENAME 
            ORDER BY count DESC
        """, (department_name,))
        department_info['employment_type_distribution'] = cursor.fetchall()
        
        # รายชื่อบุคลากรทั้งหมดในหน่วยงาน
        cursor.execute("""
            SELECT STAFFID, PREFIXFULLNAME, STAFFNAME, STAFFSURNAME, 
                   GENDERNAMETH, POSNAMETH, STFTYPENAME
            FROM staff_info 
            WHERE DEPARTMENTNAME = %s 
            ORDER BY POSNAMETH, STAFFNAME, STAFFSURNAME
        """, (department_name,))
        department_info['staff_list'] = cursor.fetchall()
        
        # ปิดการเชื่อมต่อ
        cursor.close()
        connection.close()
        
        return department_info
        
    except mysql.connector.Error as e:
        print(f"เกิดข้อผิดพลาดในการดึงข้อมูลหน่วยงาน: {e}")
        return None
    finally:
        if connection and connection.is_connected():
            connection.close()

def get_faculty_detail(faculty_name, year_filter=None):
    """
    ดึงข้อมูลรายละเอียดของคณะเฉพาะ
    รองรับการกรองตามปี (year_filter = buddhist year เช่น 2568)
    """
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # สร้าง WHERE clause สำหรับกรองปีและคณะ
        base_condition = "WHERE faculty_name = %s"
        params = [faculty_name]
        
        if year_filter:
            year_code = str(year_filter)[-2:]  # เอา 2 หลักท้าย เช่น 2568 -> 68
            base_condition += " AND SUBSTRING(student_code, 1, 2) = %s"
            params.append(year_code)
        
        # ข้อมูลสรุปคณะ
        faculty_info = {}
        
        # จำนวนนักศึกษาทั้งหมดในคณะ
        cursor.execute(f"SELECT COUNT(*) as total FROM students_info {base_condition}", params)
        result = cursor.fetchone()
        faculty_info['total_students'] = result['total'] if result else 0
        
        # จำนวนนักศึกษาแยกตามเพศ (จาก prefix_name)
        cursor.execute(f"""
            SELECT 
                CASE 
                    WHEN prefix_name IN ('นาย') THEN 'ชาย' 
                    WHEN prefix_name IN ('นางสาว', 'นาง') THEN 'หญิง'
                    ELSE 'ไม่ระบุ' 
                END AS gender,
                COUNT(*) as count 
            FROM students_info 
            {base_condition}
            GROUP BY gender
            ORDER BY count DESC
        """, params)
        faculty_info['gender_distribution'] = cursor.fetchall()
        
        # จำนวนนักศึกษาแยกตามสาขาวิชา ระดับการศึกษา และคณะ
        cursor.execute(f"""
            SELECT program_name, level_name, faculty_name, COUNT(*) as count 
            FROM students_info 
            {base_condition} 
            GROUP BY program_name, level_name, faculty_name 
            ORDER BY faculty_name, count DESC, program_name, level_name
        """, params)
        faculty_info['program_distribution'] = cursor.fetchall()
        
        # จำนวนนักศึกษาแยกตามระดับการศึกษา
        cursor.execute(f"""
            SELECT level_name, COUNT(*) as count 
            FROM students_info 
            {base_condition} 
            GROUP BY level_name 
            ORDER BY count DESC
        """, params)
        faculty_info['level_distribution'] = cursor.fetchall()
        
        # จำนวนนักศึกษาแยกตามปีเข้าศึกษา
        cursor.execute(f"""
            SELECT 
                SUBSTRING(student_code, 1, 2) AS year_code,
                COUNT(*) as count
            FROM students_info
            {base_condition}
            GROUP BY year_code
            ORDER BY year_code DESC
        """, params)
        year_distribution = cursor.fetchall()
        
        # แปลงรหัสปี 2 หลัก เป็นปี พ.ศ. 4 หลัก
        for row in year_distribution:
            try:
                year_code = int(row['year_code'])
                if year_code > 50:  # สมมติว่าเป็นปี พ.ศ. 25xx
                    row['year'] = 2500 + year_code
                else:  # สมมติว่าเป็นปี พ.ศ. 26xx
                    row['year'] = 2600 + year_code
            except (ValueError, TypeError):
                row['year'] = 'ไม่ระบุ'
        
        faculty_info['year_distribution'] = year_distribution
        
        # ปิดการเชื่อมต่อ
        cursor.close()
        connection.close()
        
        return faculty_info
        
    except mysql.connector.Error as e:
        print(f"เกิดข้อผิดพลาดในการดึงข้อมูลคณะ: {e}")
        return None
    finally:
        if connection and connection.is_connected():
            connection.close()

def get_level_detail(level_name, year_filter=None):
    """
    ดึงข้อมูลรายละเอียดของระดับการศึกษาเฉพาะ
    รองรับการกรองตามปี (year_filter = buddhist year เช่น 2568)
    """
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # สร้าง WHERE clause สำหรับกรองปีและระดับการศึกษา
        base_condition = "WHERE level_name = %s"
        params = [level_name]
        
        if year_filter:
            year_code = str(year_filter)[-2:]  # เอา 2 หลักท้าย เช่น 2568 -> 68
            base_condition += " AND SUBSTRING(student_code, 1, 2) = %s"
            params.append(year_code)
        
        # ข้อมูลสรุประดับการศึกษา
        level_info = {}
        
        # จำนวนนักศึกษาทั้งหมดในระดับการศึกษา
        cursor.execute(f"SELECT COUNT(*) as total FROM students_info {base_condition}", params)
        result = cursor.fetchone()
        level_info['total_students'] = result['total'] if result else 0
        
        # จำนวนนักศึกษาแยกตามเพศ (จาก prefix_name)
        cursor.execute(f"""
            SELECT 
                CASE 
                    WHEN prefix_name IN ('นาย') THEN 'ชาย' 
                    WHEN prefix_name IN ('นางสาว', 'นาง') THEN 'หญิง'
                    ELSE 'ไม่ระบุ' 
                END AS gender,
                COUNT(*) as count 
            FROM students_info 
            {base_condition}
            GROUP BY gender
            ORDER BY count DESC
        """, params)
        level_info['gender_distribution'] = cursor.fetchall()
        
        # จำนวนนักศึกษาแยกตามคณะ
        cursor.execute(f"""
            SELECT faculty_name, COUNT(*) as count 
            FROM students_info 
            {base_condition} 
            GROUP BY faculty_name 
            ORDER BY count DESC
        """, params)
        level_info['faculty_distribution'] = cursor.fetchall()
        
        # จำนวนนักศึกษาแยกตามสาขาวิชา (กรุ๊ปตามคณะ)
        cursor.execute(f"""
            SELECT faculty_name, program_name, COUNT(*) as count 
            FROM students_info 
            {base_condition} 
            GROUP BY faculty_name, program_name 
            ORDER BY faculty_name, count DESC
        """, params)
        programs_by_faculty = cursor.fetchall()
        
        # จัดกรุ๊ปข้อมูลตามคณะ และคำนวณผลรวมของแต่ละคณะ
        faculty_programs = {}
        faculty_totals = {}
        total_programs = 0
        
        for item in programs_by_faculty:
            faculty = item['faculty_name'] or 'ไม่ระบุคณะ'
            if faculty not in faculty_programs:
                faculty_programs[faculty] = []
                faculty_totals[faculty] = 0
            
            faculty_programs[faculty].append({
                'program_name': item['program_name'],
                'count': item['count']
            })
            faculty_totals[faculty] += item['count']
            total_programs += 1
        
        level_info['faculty_programs'] = faculty_programs
        level_info['faculty_totals'] = faculty_totals
        level_info['total_programs'] = total_programs
        level_info['program_distribution'] = programs_by_faculty
        
        # จำนวนนักศึกษาแยกตามปีเข้าศึกษา
        cursor.execute(f"""
            SELECT 
                SUBSTRING(student_code, 1, 2) AS year_code,
                COUNT(*) as count
            FROM students_info
            {base_condition}
            GROUP BY year_code
            ORDER BY year_code DESC
        """, params)
        year_distribution = cursor.fetchall()
        
        # แปลงรหัสปี 2 หลัก เป็นปี พ.ศ. 4 หลัก
        for row in year_distribution:
            try:
                year_code = int(row['year_code'])
                if year_code > 50:  # สมมติว่าเป็นปี พ.ศ. 25xx
                    row['year'] = 2500 + year_code
                else:  # สมมติว่าเป็นปี พ.ศ. 26xx
                    row['year'] = 2600 + year_code
            except (ValueError, TypeError):
                row['year'] = 'ไม่ระบุ'
        
        level_info['year_distribution'] = year_distribution
        
        # ปิดการเชื่อมต่อ
        cursor.close()
        connection.close()
        
        return level_info
        
    except mysql.connector.Error as e:
        print(f"เกิดข้อผิดพลาดในการดึงข้อมูลระดับการศึกษา: {e}")
        return None
    finally:
        if connection and connection.is_connected():
            connection.close()