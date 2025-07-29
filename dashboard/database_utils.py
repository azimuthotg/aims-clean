import mysql.connector
from django.conf import settings

def get_db_connection():
    """
    สร้างการเชื่อมต่อกับฐานข้อมูล MySQL
    """
    try:
        connection = mysql.connector.connect(
            host='202.29.55.213',
            database='api',
            user='admin_e' , # ใส่ username จริง
            password='REMOVED_PASSWORD'  # ใส่ password จริง
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

def get_student_summary():
    """
    ดึงข้อมูลสรุปของนักศึกษา
    """
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # ข้อมูลสรุปทั้งหมด
        summary = {}
        
        # จำนวนนักศึกษาทั้งหมด
        cursor.execute("SELECT COUNT(*) as total FROM students_info")
        result = cursor.fetchone()
        summary['total_students'] = result['total'] if result else 0
        
        # จำนวนนักศึกษาแยกตามคณะ
        try:
            cursor.execute("SELECT faculty_name, COUNT(*) as count FROM students_info GROUP BY faculty_name ORDER BY count DESC")
            summary['faculty_distribution'] = cursor.fetchall()
        except mysql.connector.Error:
            summary['faculty_distribution'] = []
        
        # จำนวนนักศึกษาแยกตามหลักสูตร/สาขาวิชา
        try:
            cursor.execute("SELECT program_name, COUNT(*) as count FROM students_info GROUP BY program_name ORDER BY count DESC")
            summary['program_distribution'] = cursor.fetchall()
        except mysql.connector.Error:
            summary['program_distribution'] = []
        
        # จำนวนนักศึกษาแยกตามระดับการศึกษา
        try:
            cursor.execute("SELECT level_name, COUNT(*) as count FROM students_info GROUP BY level_name ORDER BY count DESC")
            summary['education_level_distribution'] = cursor.fetchall()
        except mysql.connector.Error:
            summary['education_level_distribution'] = []
        
        # จำนวนนักศึกษาแยกตามเพศ (ใช้ prefix_name ในการประมาณ)
        try:
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN prefix_name IN ('นาย') THEN 'ชาย' 
                        WHEN prefix_name IN ('นางสาว', 'นาง') THEN 'หญิง'
                        ELSE 'ไม่ระบุ' 
                    END AS gender,
                    COUNT(*) as count 
                FROM students_info 
                GROUP BY gender
                ORDER BY count DESC
            """)
            summary['gender_distribution'] = cursor.fetchall()
        except mysql.connector.Error:
            summary['gender_distribution'] = []
        
        # จำนวนนักศึกษาแยกตามปีที่เข้าศึกษา (จากรหัสนักศึกษา)
        try:
            cursor.execute("""
                SELECT 
                    SUBSTRING(student_code, 1, 2) AS year_code,
                    COUNT(*) as count
                FROM students_info
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