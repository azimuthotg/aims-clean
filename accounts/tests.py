import mysql.connector
import sys

def test_db_connection():
    try:
        # เชื่อมต่อกับฐานข้อมูล
        connection = mysql.connector.connect(
            host='202.29.55.213',
            database='api',
            user='admin_e',  # ใส่ username จริง
            password='REMOVED_PASSWORD'  # ใส่ password จริง
        )
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"เชื่อมต่อกับ MySQL Server สำเร็จ (เวอร์ชัน: {db_info})")
            
            # ทดสอบดึงข้อมูลจำนวนบุคลากรทั้งหมด
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM staff_info")
            record = cursor.fetchone()
            print(f"จำนวนบุคลากรทั้งหมด: {record[0]}")
            
            # ลิสต์ข้อมูลบุคลากร 10 รายการแรก
            print("\nข้อมูลบุคลากร 10 รายการแรก:")
            cursor.execute("SELECT STAFFID, STAFFCITIZENID, PREFIXFULLNAME, STAFFNAME, STAFFSURNAME, GENDERNAMETH, DEPARTMENTNAME FROM staff_info LIMIT 10")
            staff_records = cursor.fetchall()
            
            # แสดงผลข้อมูล
            for record in staff_records:
                print(f"รหัสบุคลากร: {record[0]}, ชื่อ-นามสกุล: {record[2]} {record[3]} {record[4]}, หน่วยงาน: {record[6] or 'ไม่ระบุ'}")
            
            # ปิดการเชื่อมต่อ
            cursor.close()
            connection.close()
            print("\nปิดการเชื่อมต่อกับฐานข้อมูลแล้ว")
            
    except mysql.connector.Error as e:
        print(f"เกิดข้อผิดพลาดในการเชื่อมต่อกับฐานข้อมูล: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_db_connection()