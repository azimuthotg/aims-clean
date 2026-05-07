# AIMS — คู่มือ Deploy บน Production Server

**ระบบ:** AIMS (Academic Information Management System)
**มหาวิทยาลัย:** มหาวิทยาลัยนครพนม (NPU)
**URL Production:** https://lib.npu.ac.th/aims/
**Server:** Windows Server, IIS + ARR (Reverse Proxy), Waitress

---

## สถาปัตยกรรม

```
Internet
   ↓ HTTPS
IIS + ARR (lib.npu.ac.th)
   ↓ Reverse Proxy /aims/ → 127.0.0.1:8001
Waitress (Python WSGI)
   ↓
Django 5.0 (AIMS App)
   ↓
MySQL (aims DB + api DB)
```

---

## ข้อกำหนดระบบ

| รายการ | ค่า |
|---|---|
| OS | Windows Server |
| Python | 3.12.x |
| Virtual Environment | `C:\project\aims_project\venv\` |
| Project Directory | `C:\project\aims_project\` |
| Port | 8001 (Waitress) |
| Service Manager | NSSM |
| Oracle Client | `C:\oracle\instantclient_21_20\` (สำหรับ Oracle DB) |

---

## การ Deploy ครั้งแรก (Initial Setup)

### 1. Clone โปรเจกต์

```powershell
cd C:\project
git clone https://github.com/azimuthotg/aims-clean.git aims_project
cd aims_project
```

### 2. สร้าง Virtual Environment

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. ตั้งค่า `.env`

สร้างไฟล์ `C:\project\aims_project\.env`:

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=lib.npu.ac.th,127.0.0.1

# Path Prefix (IIS Reverse Proxy)
FORCE_SCRIPT_NAME=/aims
CSRF_TRUSTED_ORIGINS=https://lib.npu.ac.th

# Django DB (aims)
DB_ENGINE=django.db.backends.mysql
DB_NAME=aims
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=202.29.55.213
DB_PORT=3306

# Analytics DB (api)
API_DB_HOST=202.29.55.213
API_DB_PORT=3306
API_DB_USER=your_api_user
API_DB_PASSWORD=your_api_password
API_DB_NAME=api

# Oracle (สำหรับ sync นักศึกษา)
ORACLE_CLIENT_LIB=C:/oracle/instantclient_21_20
ORACLE_HOST=202.29.55.15
ORACLE_PORT=1521
ORACLE_SERVICE=npu
ORACLE_USER=admin_e
ORACLE_PASSWORD=your_oracle_password

# Staff Source DB
STAFF_SRC_HOST=202.29.55.29
STAFF_SRC_USER=ge_website
STAFF_SRC_PASSWORD=your_staff_password
STAFF_SRC_DB=cp665407_npu_staff

# LDAP API
LDAP_API_TOKEN=your-ldap-jwt-token

# Google Sheets (สำหรับสถิติงานบริการ)
GOOGLE_SHEETS_SPREADSHEET_ID=your-spreadsheet-id

# Waitress
WAITRESS_HOST=127.0.0.1
WAITRESS_PORT=8001
WAITRESS_THREADS=8
```

### 4. Migrate Database

```powershell
venv\Scripts\activate
python manage.py migrate
python manage.py collectstatic --noinput
```

### 5. ตั้งค่า NSSM Service

```powershell
# ดาวน์โหลด NSSM จาก https://nssm.cc/
nssm install AIMS "C:\project\aims_project\venv\Scripts\python.exe"
nssm set AIMS AppParameters "C:\project\aims_project\deploy\waitress_serve.py"
nssm set AIMS AppDirectory "C:\project\aims_project"
nssm set AIMS AppStdout "C:\project\aims_project\logs\waitress.log"
nssm set AIMS AppStderr "C:\project\aims_project\logs\waitress_error.log"
nssm start AIMS
```

### 6. ตั้ง Windows Task Scheduler (Auto Sync)

```powershell
# รันใน PowerShell as Administrator
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
& "C:\project\aims_project\deploy\task_scheduler\register_tasks.ps1"
```

จะสร้าง 2 tasks อัตโนมัติ:
- **AIMS Sync Staff** — ทุกวัน 02:00 น.
- **AIMS Sync Students** — ทุกวัน 02:30 น.

---

## การ Deploy อัปเดต (Update Deployment)

### ขั้นตอนมาตรฐาน

```powershell
cd C:\project\aims_project
git pull origin main
venv\Scripts\activate
pip install -r requirements.txt   # ถ้ามี dependency ใหม่
python manage.py migrate          # ถ้ามี migration ใหม่
```

จากนั้น restart NSSM service:

```powershell
nssm restart AIMS
# หรือผ่าน Services Manager (services.msc)
```

### ตรวจสอบหลัง Deploy

```powershell
# ดู service status
nssm status AIMS

# ดู log
Get-Content "C:\project\aims_project\logs\waitress.log" -Tail 20
```

เปิดเบราว์เซอร์ทดสอบ: https://lib.npu.ac.th/aims/

---

## โครงสร้างไฟล์สำคัญ

```
C:\project\aims_project\
├── .env                          ← environment variables (ไม่ commit)
├── manage.py
├── requirements.txt
├── venv\                         ← Python virtual environment (Windows)
├── logs\                         ← Log files (ไม่ commit)
│   ├── waitress.log
│   ├── sync_staff.log
│   └── sync_students.log
├── accounts\                     ← Authentication app
├── dashboard\                    ← Operational dashboards
│   └── management\commands\
│       ├── sync_staff.py         ← Sync บุคลากร
│       └── sync_students.py      ← Sync นักศึกษา
├── dashboard_system\             ← Executive dashboard
├── deploy\
│   ├── waitress_serve.py         ← Waitress entry point
│   └── task_scheduler\
│       ├── sync_staff.bat        ← Task Scheduler batch
│       ├── sync_students.bat
│       └── register_tasks.ps1    ← ลงทะเบียน tasks
└── credentials\
    └── *.json                    ← Google Sheets credentials (ไม่ commit)
```

---

## URL หลัก

| URL | คำอธิบาย |
|---|---|
| `/aims/` | Portal / Login |
| `/aims/dashboard/` | Dashboard หลัก |
| `/aims/dashboard/staff/` | ข้อมูลบุคลากร |
| `/aims/dashboard/student/` | ข้อมูลนักศึกษา |
| `/aims/dashboard/service-statistics/` | สถิติงานบริการ |
| `/aims/dashboard/sync/` | Sync Monitor |
| `/aims/executive/` | Executive Dashboard |
| `/aims/accounts/users/` | จัดการผู้ใช้ |
| `/aims/admin/` | Django Admin |

---

## การ Sync ข้อมูล

### รันด้วยมือ

```powershell
venv\Scripts\activate
python manage.py sync_staff       # sync บุคลากร
python manage.py sync_students    # sync นักศึกษา
```

### ดู Log

```powershell
Get-Content "C:\project\aims_project\logs\sync_staff.log" -Tail 20
Get-Content "C:\project\aims_project\logs\sync_students.log" -Tail 20
```

### ตรวจสอบผ่าน UI

เข้า https://lib.npu.ac.th/aims/dashboard/sync/

---

## Oracle Instant Client

ต้องติดตั้งสำหรับ sync ข้อมูลนักศึกษา (Oracle DB เก่า):

1. ดาวน์โหลด: https://www.oracle.com/database/technologies/instant-client/winx64-64-downloads.html
2. เลือก **Version 21.20** (Basic Package)
3. แตกไฟล์ไปที่ `C:\oracle\instantclient_21_20\`
4. เพิ่มใน `.env`:
   ```env
   ORACLE_CLIENT_LIB=C:/oracle/instantclient_21_20
   ```
   > ⚠️ ใช้ forward slash `/` ไม่ใช่ backslash `\`

---

## Troubleshooting

### Service ไม่ขึ้น

```powershell
nssm status AIMS
Get-Content "C:\project\aims_project\logs\waitress_error.log" -Tail 30
```

### Sync ล้มเหลว

1. เช็ค log: `Get-Content "C:\project\aims_project\logs\sync_staff.log" -Tail 20`
2. ตรวจสอบ credentials ใน `.env`
3. ทดสอบ network connection ไปยัง source DB

### Oracle DPY-3010 Error

```
DPY-3010: connections to this database server version are not supported
```
**สาเหตุ:** Oracle server เก่าเกินไป ต้องใช้ thick mode
**แก้:** ตรวจสอบว่า `ORACLE_CLIENT_LIB` ใน `.env` ใช้ forward slash และ path ถูกต้อง

### UnicodeEncodeError บน Windows

```
UnicodeEncodeError: 'charmap' codec can't encode character
```
**สาเหตุ:** มี emoji ใน print() statement
**แก้:** ลบ emoji ออกจากโค้ด หรือเพิ่ม `PYTHONUTF8=1` ใน environment

---

*อัปเดตล่าสุด: 7 พฤษภาคม 2569*
