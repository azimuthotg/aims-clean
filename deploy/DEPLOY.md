# AIMS Dashboard - Deployment Guide

## สำหรับ Windows Server + Waitress + NSSM

---

## 1. ข้อกำหนดเบื้องต้น (Prerequisites)

### ซอฟต์แวร์ที่ต้องติดตั้ง:
- **Python 3.12+** - https://www.python.org/downloads/
- **Git** - https://git-scm.com/download/win
- **NSSM** - https://nssm.cc/download

### ติดตั้ง NSSM:
1. ดาวน์โหลด NSSM จาก https://nssm.cc/download
2. แตกไฟล์และ copy `nssm.exe` ไปที่ `C:\nssm\nssm.exe`
3. หรือเพิ่ม path ของ NSSM ใน System PATH

---

## 2. Clone โปรเจค

```cmd
cd C:\projects
git clone https://github.com/azimuthotg/aims-clean.git aims_project
cd aims_project
```

---

## 3. สร้าง Virtual Environment

```cmd
python -m venv venv
venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
pip install waitress
```

---

## 4. ตั้งค่า Environment Variables

### สร้างไฟล์ `.env`:

```cmd
copy .env.example .env
notepad .env
```

### แก้ไขค่าใน `.env`:

```env
# Django Settings
SECRET_KEY=your-secure-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your-server-ip,your-domain.com

# Database Configuration
DB_ENGINE=django.db.backends.mysql
DB_NAME=aims
DB_USER=your-db-username
DB_PASSWORD=your-db-password
DB_HOST=202.29.55.213
DB_PORT=3306

# External API Database
API_DB_HOST=202.29.55.213
API_DB_PORT=3306
API_DB_USER=your-api-db-username
API_DB_PASSWORD=your-api-db-password
API_DB_NAME=api

# LDAP Authentication
LDAP_API_URL=https://api.npu.ac.th/v2/ldap/auth_and_get_personnel/
LDAP_API_TOKEN=your-ldap-token

# Waitress Server
WAITRESS_HOST=0.0.0.0
WAITRESS_PORT=8005
WAITRESS_THREADS=4
```

---

## 5. ทดสอบการทำงาน

### ทดสอบ Django:
```cmd
python manage.py check
python manage.py migrate
```

### ทดสอบ Waitress:
```cmd
python waitress_server.py
```

เปิด browser ไปที่ http://localhost:8005/ ตรวจสอบว่าทำงานได้

กด `Ctrl+C` เพื่อหยุด

---

## 6. ติดตั้ง Windows Service

### แก้ไข paths ใน `deploy/install_service.bat`:

```bat
set PROJECT_DIR=C:\projects\aims_project
set PYTHON_PATH=C:\projects\aims_project\venv\Scripts\python.exe
set SCRIPT_PATH=C:\projects\aims_project\waitress_server.py
set NSSM_PATH=C:\nssm\nssm.exe
```

### รัน install script (ต้องรันด้วย Administrator):

```cmd
cd C:\projects\aims_project\deploy
install_service.bat
```

---

## 7. จัดการ Service

### คำสั่ง NSSM:

| คำสั่ง | การใช้งาน |
|--------|-----------|
| `nssm start AIMS-Dashboard` | เริ่ม service |
| `nssm stop AIMS-Dashboard` | หยุด service |
| `nssm restart AIMS-Dashboard` | รีสตาร์ท service |
| `nssm status AIMS-Dashboard` | ดูสถานะ |
| `nssm edit AIMS-Dashboard` | แก้ไขการตั้งค่า |
| `nssm remove AIMS-Dashboard` | ลบ service |

### หรือใช้ script:

```cmd
deploy\manage_service.bat
```

---

## 8. ตรวจสอบ Log Files

Log files อยู่ที่:
- `C:\projects\aims_project\logs\aims_stdout.log`
- `C:\projects\aims_project\logs\aims_stderr.log`

### ดู log แบบ real-time:

```powershell
Get-Content "C:\projects\aims_project\logs\aims_stdout.log" -Wait -Tail 50
```

---

## 9. อัพเดทโค้ด

```cmd
cd C:\projects\aims_project

REM หยุด service
nssm stop AIMS-Dashboard

REM Pull โค้ดใหม่
git pull origin main

REM เปิด virtual environment
venv\Scripts\activate

REM ติดตั้ง dependencies ใหม่ (ถ้ามี)
pip install -r requirements.txt

REM รัน migrations (ถ้ามี)
python manage.py migrate

REM เริ่ม service
nssm start AIMS-Dashboard
```

---

## 10. Firewall Configuration

เปิด port 8005 ใน Windows Firewall:

```powershell
# รันด้วย Administrator
New-NetFirewallRule -DisplayName "AIMS Dashboard" -Direction Inbound -Port 8005 -Protocol TCP -Action Allow
```

---

## 11. IIS Reverse Proxy (Optional)

ถ้าต้องการใช้ IIS เป็น reverse proxy:

### ติดตั้ง URL Rewrite และ ARR:
1. ดาวน์โหลด URL Rewrite: https://www.iis.net/downloads/microsoft/url-rewrite
2. ดาวน์โหลด ARR: https://www.iis.net/downloads/microsoft/application-request-routing

### ตั้งค่า web.config (ในโฟลเดอร์ IIS site):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <system.webServer>
        <rewrite>
            <rules>
                <rule name="AIMS Reverse Proxy" stopProcessing="true">
                    <match url="(.*)" />
                    <action type="Rewrite" url="http://localhost:8005/{R:1}" />
                </rule>
            </rules>
        </rewrite>
    </system.webServer>
</configuration>
```

---

## 12. Troubleshooting

### Service ไม่ start:
1. ตรวจสอบ log files
2. ตรวจสอบ path ใน NSSM: `nssm edit AIMS-Dashboard`
3. ทดสอบรัน manual: `python waitress_server.py`

### Database connection error:
1. ตรวจสอบค่าใน `.env`
2. ตรวจสอบ firewall ระหว่าง server กับ database

### Permission denied:
1. รัน Command Prompt ด้วย Administrator
2. ตรวจสอบ permission ของโฟลเดอร์ logs

### Port already in use:
```cmd
netstat -ano | findstr :8005
taskkill /PID <PID> /F
```

---

## 13. Security Checklist

- [ ] ตั้ง `DEBUG=False` ใน production
- [ ] ใช้ `SECRET_KEY` ที่ซับซ้อน
- [ ] ตั้งค่า `ALLOWED_HOSTS` ให้ถูกต้อง
- [ ] ใช้ HTTPS (ผ่าน IIS หรือ reverse proxy)
- [ ] ตั้งค่า firewall ให้เปิดเฉพาะ port ที่จำเป็น
- [ ] ไม่ commit ไฟล์ `.env` ขึ้น git
- [ ] ตั้งค่า database user ให้มี permission เฉพาะที่จำเป็น

---

## Contact

หากพบปัญหา กรุณาติดต่อทีมพัฒนา
