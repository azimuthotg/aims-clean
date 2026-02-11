import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime
import json
from django.conf import settings

# ตำแหน่งของไฟล์ credentials
CREDENTIALS_FILE = os.path.join(settings.BASE_DIR, 'credentials', 'control-room-440116-7cd01a8c02bd.json')

# ID ของ Google Spreadsheet
SPREADSHEET_ID = '1Z64aIUqfH2SMc__m3brPINUE6kqgQq_ii0OC8uXiae8'

def get_sheet_service():
    """
    สร้าง Google Sheets API Service
    """
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    
    try:
        credentials = service_account.Credentials.from_service_account_file(
            CREDENTIALS_FILE, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=credentials)
        return service
    except Exception as e:
        print(f"Error creating sheets service: {e}")
        return None

def get_service_statistics():
    """
    ดึงข้อมูลสถิติจาก Google Sheets และพิมพ์แสดงผลเพื่อตรวจสอบ
    """
    print("\n" + "="*50)
    print("เริ่มต้นทำงานฟังก์ชัน get_service_statistics")
    
    service = get_sheet_service()
    if not service:
        print("เกิดข้อผิดพลาด: ไม่สามารถเชื่อมต่อ Google Sheets API ได้")
        return None
    
    print("เชื่อมต่อ Google Sheets API สำเร็จ")
    
    try:
        # ดึงข้อมูลจาก Sheet "Dashboard"
        range_name = 'Dashboard!A1:C50'  # ปรับช่วงให้ครอบคลุมข้อมูลทั้งหมด
        print(f"กำลังดึงข้อมูลจาก range: {range_name}")
        
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        print(f"ดึงข้อมูลสำเร็จ: ได้ข้อมูลทั้งหมด {len(values)} แถว")
        
        if not values:
            print("ไม่พบข้อมูลในชีต")
            return None
        
        # แสดงข้อมูลดิบ
        print("\nข้อมูลดิบจาก Google Sheet (5 แถวแรก):")
        for i, row in enumerate(values[:5]):
            print(f"  แถวที่ {i}: {row}")
        
        # แสดงหัวตาราง
        if values and len(values) > 0:
            print(f"\nหัวตาราง: {values[0]}")
        
        # แปลงข้อมูลให้อยู่ในรูปแบบที่ใช้งานง่าย
        print("\nเริ่มต้นแปลงข้อมูล...")
        data = []
        
        # ข้ามแถวแรกที่เป็นหัวตาราง
        for i, row in enumerate(values[1:], 1):
            print(f"  แปลงแถวที่ {i}: {row}")
            
            # แก้ไขที่ 1: จัดการกรณีที่ข้อมูลไม่ครบ 3 คอลัมน์
            # สร้างแถวใหม่ที่มีข้อมูลครบ 3 คอลัมน์
            processed_row = row.copy() if len(row) > 0 else []
            
            # ตรวจสอบความยาวของแถวและเพิ่มข้อมูลที่ขาดหายไป
            while len(processed_row) < 3:
                processed_row.append("")
            
            date_info = processed_row[0].strip()  # คอลัมน์ A: ปี (เช่น "2566")
            month_info = processed_row[1].strip() if len(processed_row) > 1 else ""  # คอลัมน์ B: เดือน (เช่น "ต.ค.")
            
            # แก้ไขที่ 2: แยกปีและเดือนจากข้อมูลในแต่ละคอลัมน์แทนที่จะแยกจากคอลัมน์เดียว
            year = date_info  # เก็บปีเป็น text ตามที่อยู่ในคอลัมน์แรก
            month = month_info  # เก็บเดือนเป็น text ตามที่อยู่ในคอลัมน์ที่สอง
            
            print(f"    ปี: {year}, เดือน: {month}")
            
            # แปลงข้อมูลจำนวนผู้ใช้บริการเป็นตัวเลข
            visit_count_str = processed_row[2] if processed_row[2] else "0"
            print(f"    ข้อมูลจำนวนผู้ใช้บริการ: '{visit_count_str}'")
            
            try:
                # ลบเครื่องหมายคอมม่าและแปลงเป็นตัวเลข
                visit_count = int(visit_count_str.replace(',', ''))
                print(f"    แปลงเป็นตัวเลขสำเร็จ: {visit_count}")
            except (ValueError, TypeError) as e:
                print(f"    เกิดข้อผิดพลาดในการแปลงค่า: {e}")
                visit_count = 0
            
            # ตรวจสอบว่ามีปีและเดือน
            if year and month:
                # สร้างข้อมูลใหม่
                item = {
                    'date_info': f"{year} {month}",
                    'year': year,
                    'month': month,
                    'visit_count': visit_count
                }
                print(f"    สร้างข้อมูลสำเร็จ: {item}")
                data.append(item)
            else:
                print(f"    ข้ามแถวนี้เนื่องจากไม่มีข้อมูลปีหรือเดือน")
        
        print(f"\nแปลงข้อมูลเสร็จสิ้น: ได้ข้อมูลทั้งหมด {len(data)} รายการ")
        
        # ตรวจสอบข้อมูลแยกตามปี
        years = {}
        for item in data:
            year = item['year']
            if year not in years:
                years[year] = []
            years[year].append(item)
        
        print("\nข้อมูลแยกตามปี:")
        for year, items in years.items():
            print(f"  ปี {year}: {len(items)} รายการ")
        
        # แสดงตัวอย่างข้อมูลสำหรับปี 2567 และ 2568
        print("\nตัวอย่างข้อมูลปี 2567:")
        for item in [i for i in data if i['year'] == '2567'][:3]:  # แสดง 3 รายการแรก
            print(f"  {item}")
        
        print("\nตัวอย่างข้อมูลปี 2568:")
        for item in [i for i in data if i['year'] == '2568'][:3]:  # แสดง 3 รายการแรก
            print(f"  {item}")
        
        print("="*50 + "\n")
        return data
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการดึงข้อมูลจาก Google Sheets: {e}")
        import traceback
        traceback.print_exc()
        print("="*50 + "\n")
        return None

def process_service_statistics(data):
    """
    ประมวลผลข้อมูลสถิติสำหรับการแสดงผล
    """
    if not data:
        return None
    
    # จัดกลุ่มข้อมูลตามปี
    yearly_data = {}
    for item in data:
        year = item['year']
        if year not in yearly_data:
            yearly_data[year] = {'total': 0, 'months': {}}
        
        yearly_data[year]['total'] += item['count']
        yearly_data[year]['months'][item['month']] = item['count']
    
    # แปลงข้อมูลเป็นรูปแบบที่ใช้ในการแสดงผล
    yearly_summary = []
    for year, data in yearly_data.items():
        yearly_summary.append({
            'year': year,
            'total': data['total'],
            'months': data['months']
        })
    
    # เรียงลำดับตามปี
    yearly_summary.sort(key=lambda x: x['year'])
    
    return {
        'raw_data': data,
        'yearly_summary': yearly_summary
    }

def get_monthly_data():
    """
    ดึงข้อมูลและจัดรูปแบบสำหรับการแสดงผลรายเดือน
    """
    data = get_service_statistics()
    if not data:
        return None
    
    # เรียงลำดับข้อมูลตามวันที่
    thai_month_order = {
        'ม.ค.': 1, 'ก.พ.': 2, 'มี.ค.': 3, 'เม.ย.': 4, 'พ.ค.': 5, 'มิ.ย.': 6,
        'ก.ค.': 7, 'ส.ค.': 8, 'ก.ย.': 9, 'ต.ค.': 10, 'พ.ย.': 11, 'ธ.ค.': 12
    }
    
    # เรียงลำดับข้อมูลตามปี และเดือน
    sorted_data = sorted(data, key=lambda x: (int(x['year']), thai_month_order.get(x['month'], 0)))
    
    # สร้างข้อมูลสำหรับกราฟ
    labels = [f"{item['month']} {item['year']}" for item in sorted_data]
    values = [item['count'] for item in sorted_data]
    
    return {
        'labels': labels,
        'values': values,
        'data': sorted_data
    }

def get_yearly_data():
    """
    ดึงข้อมูลและจัดรูปแบบสำหรับการแสดงผลรายปี
    """
    data = get_service_statistics()
    if not data:
        return None
    
    processed_data = process_service_statistics(data)
    if not processed_data:
        return None
    
    yearly_summary = processed_data['yearly_summary']
    
    # สร้างข้อมูลสำหรับกราฟ
    labels = [item['year'] for item in yearly_summary]
    values = [item['total'] for item in yearly_summary]
    
    return {
        'labels': labels,
        'values': values,
        'data': yearly_summary
    }

def get_latest_statistics():
    """
    ดึงข้อมูลสถิติล่าสุด
    """
    monthly_data = get_monthly_data()
    yearly_data = get_yearly_data()
    
    if not monthly_data or not yearly_data:
        return None
    
    # ดึงข้อมูลล่าสุด
    latest_month = monthly_data['data'][-1] if monthly_data['data'] else None
    latest_year = yearly_data['data'][-1] if yearly_data['data'] else None
    
    # คำนวณค่าเฉลี่ยรายเดือนของปีล่าสุด
    avg_monthly = 0
    if latest_year and latest_year['total'] > 0:
        month_count = len(latest_year['months'])
        if month_count > 0:
            avg_monthly = latest_year['total'] / month_count
    
    return {
        'latest_month': latest_month,
        'latest_year': latest_year,
        'avg_monthly': avg_monthly,
        'total_all_time': sum(item['total'] for item in yearly_data['data'])
    }

def get_formatted_statistics(period=None):
    """
    ดึงข้อมูลและจัดรูปแบบตามช่วงเวลาที่กำหนด
    
    Parameters:
        period: ช่วงเวลาที่ต้องการ ('all', 'year', 'month', 'quarter')
                หรือระบุปีเป็นสตริง เช่น '2567'
    
    Returns:
        ข้อมูลที่จัดรูปแบบแล้วสำหรับการแสดงผล
    """
    data = get_service_statistics()
    if not data:
        return None
    
    # เรียงลำดับข้อมูลตามวันที่
    thai_month_order = {
        'ม.ค.': 1, 'ก.พ.': 2, 'มี.ค.': 3, 'เม.ย.': 4, 'พ.ค.': 5, 'มิ.ย.': 6,
        'ก.ค.': 7, 'ส.ค.': 8, 'ก.ย.': 9, 'ต.ค.': 10, 'พ.ย.': 11, 'ธ.ค.': 12
    }
    
    # แปลงเดือนไทยเป็นชื่อเต็ม
    thai_month_full = {
        'ม.ค.': 'มกราคม', 'ก.พ.': 'กุมภาพันธ์', 'มี.ค.': 'มีนาคม', 
        'เม.ย.': 'เมษายน', 'พ.ค.': 'พฤษภาคม', 'มิ.ย.': 'มิถุนายน',
        'ก.ค.': 'กรกฎาคม', 'ส.ค.': 'สิงหาคม', 'ก.ย.': 'กันยายน', 
        'ต.ค.': 'ตุลาคม', 'พ.ย.': 'พฤศจิกายน', 'ธ.ค.': 'ธันวาคม'
    }
    
    # กรองข้อมูลตามช่วงเวลาที่กำหนด
    filtered_data = data
    if period and period != 'all':
        if period == 'year':
            # ข้อมูลปีล่าสุด
            latest_year = max(item['year'] for item in data)
            filtered_data = [item for item in data if item['year'] == latest_year]
        elif period == 'month':
            # ข้อมูลเดือนล่าสุด
            sorted_data = sorted(data, key=lambda x: (int(x['year']), thai_month_order.get(x['month'], 0)))
            filtered_data = [sorted_data[-1]] if sorted_data else []
        elif period == 'quarter':
            # ข้อมูล 3 เดือนล่าสุด
            sorted_data = sorted(data, key=lambda x: (int(x['year']), thai_month_order.get(x['month'], 0)))
            filtered_data = sorted_data[-3:] if len(sorted_data) >= 3 else sorted_data
        elif period in [item['year'] for item in data]:
            # ข้อมูลตามปีที่ระบุ
            filtered_data = [item for item in data if item['year'] == period]
    
    # เรียงลำดับข้อมูลตามปีและเดือน
    sorted_data = sorted(filtered_data, key=lambda x: (int(x['year']), thai_month_order.get(x['month'], 0)))
    
    # สร้างข้อมูลสำหรับกราฟ
    labels = [f"{item['month']} {item['year']}" for item in sorted_data]
    values = [item['visit_count'] for item in sorted_data]
    
    # สร้างข้อมูลสรุปเพิ่มเติม
    total_visits = sum(values)
    avg_visits = total_visits / len(values) if values else 0
    max_month = max(sorted_data, key=lambda x: x['visit_count']) if sorted_data else None
    min_month = min(sorted_data, key=lambda x: x['visit_count']) if sorted_data else None
    
    # จัดกลุ่มข้อมูลตามปี
    yearly_data = {}
    for item in sorted_data:
        year = item['year']
        if year not in yearly_data:
            yearly_data[year] = {'total': 0, 'months': {}}
        
        yearly_data[year]['total'] += item['visit_count']
        yearly_data[year]['months'][item['month']] = item['visit_count']
    
    return {
        'labels': labels,
        'values': values,
        'data': sorted_data,
        'summary': {
            'total_visits': total_visits,
            'avg_visits': avg_visits,
            'max_month': max_month,
            'min_month': min_month
        },
        'yearly_data': yearly_data
    }

def test_sheets_connection():
    """
    ทดสอบการเชื่อมต่อกับ Google Sheets API
    """
    print("Testing Google Sheets API connection...")
    service = get_sheet_service()
    if not service:
        print("Failed to create sheet service")
        return False
    
    try:
        result = service.spreadsheets().get(
            spreadsheetId=SPREADSHEET_ID
        ).execute()
        print(f"Successfully connected to sheet: {result.get('properties', {}).get('title')}")
        return True
    except Exception as e:
        print(f"Error connecting to Google Sheets: {e}")
        return False
    
def get_raw_sheet_data():
    """
    ดึงข้อมูลดิบจาก Google Sheets โดยไม่แปลงข้อมูล
    """
    service = get_sheet_service()
    if not service:
        print("Error: Could not create sheet service")
        return None
    
    try:
        # ดึงข้อมูลจาก Sheet "Dashboard"
        print("Fetching data from Google Sheet...")
        range_name = 'Dashboard!A1:C50'  # ปรับช่วงให้ครอบคลุมข้อมูลทั้งหมด
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        print(f"Raw data from sheet: {values}")
        
        # ส่งข้อมูลดิบกลับไปเลย
        return values
    except Exception as e:
        print(f"Error fetching data from sheet: {e}")
        import traceback
        traceback.print_exc()
        return None