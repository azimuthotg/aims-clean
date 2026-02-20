# คู่มือ Deploy ระบบใหม่บน Server lib.npu.ac.th
## Path-based Routing — Windows Server 2019 + IIS + ARR + NSSM + Waitress

**เวอร์ชัน:** 1.0
**วันที่:** กุมภาพันธ์ 2569
**ผู้จัดทำ:** งานเทคนิคสารสนเทศและการจัดการทรัพยากร

---

## สารบัญ

1. [ภาพรวมสถาปัตยกรรม](#1-ภาพรวมสถาปัตยกรรม)
2. [สถานะระบบปัจจุบัน](#2-สถานะระบบปัจจุบัน)
3. [หลักการ Path-based Routing](#3-หลักการ-path-based-routing)
4. [ขั้นตอน Deploy ระบบใหม่](#4-ขั้นตอน-deploy-ระบบใหม่)
5. [การแก้ไข web.config](#5-การแก้ไข-webconfig)
6. [การทดสอบ](#6-การทดสอบ)
7. [การบำรุงรักษา](#7-การบำรุงรักษา)
8. [ข้อผิดพลาดที่พบบ่อย](#8-ข้อผิดพลาดที่พบบ่อย)

---

## 1. ภาพรวมสถาปัตยกรรม

```
ผู้ใช้งาน (Browser)
        │
        │  https://lib.npu.ac.th/[app-path]/
        ▼
┌──────────────────────────────────────────────┐
│  IIS 10.0 + ARR + URL Rewrite                │
│  IP: 110.78.83.102   Domain: lib.npu.ac.th   │
│  SSL: cert2026.pfx (*.npu.ac.th)             │
│                                              │
│  Port 80  → Redirect ไป HTTPS               │
│  Port 443 → Path-based Routing:             │
│    /projects/*  →  127.0.0.1:8000           │
│    /aims/*      →  127.0.0.1:8001           │
│    /[app3]/*    →  127.0.0.1:8002  (ถัดไป) │
│    /[app4]/*    →  127.0.0.1:8003  (อนาคต) │
└──────────────────────────────────────────────┘
         │                    │
         ▼                    ▼
  [Waitress :8000]    [Waitress :8001]
  ProjectTracker        AIMS
  NSSM Service          NSSM Service
```

**ข้อมูลเซิร์ฟเวอร์:**

| รายการ | ค่า |
|--------|-----|
| IP Address | 110.78.83.102 |
| Domain | lib.npu.ac.th |
| OS | Windows Server 2019 |
| IIS Root | C:\iis_root\ |
| Project Root | C:\project\ |
| NSSM | C:\nssm\nssm.exe |
| SSL Certificate | C:\project\project_tracker\cert\cert2026.pfx |

---

## 2. สถานะระบบปัจจุบัน

| # | ระบบ | Path | Port | Service Name | Location |
|---|------|------|------|-------------|---------|
| 1 | Project Tracker | `/projects/` | 8000 | `ProjectTracker` | `C:\project\project_tracker` |
| 2 | AIMS | `/aims/` | 8001 | `AIMS` | `C:\project\aims_project` |
| 3 | *(ระบบถัดไป)* | `/[path]/` | **8002** | `[ServiceName]` | `C:\project\[folder]` |
| 4 | *(อนาคต)* | `/[path]/` | **8003** | `[ServiceName]` | `C:\project\[folder]` |

> **กฎการจัดสรร Port:**  ระบบแรก = 8000, ระบบที่สอง = 8001, ระบบถัดไป = **เพิ่มทีละ 1 เสมอ**

---

## 3. หลักการ Path-based Routing

### การทำงาน
```
Browser: GET https://lib.npu.ac.th/aims/dashboard/staff/
                                       │
                    IIS ตัด prefix /aims ออก
                                       │
Waitress รับ: GET http://127.0.0.1:8001/dashboard/staff/
                                       │
             Django ประมวลผล URL
                                       │
Django สร้าง URL กลับโดยใส่ /aims นำหน้า (FORCE_SCRIPT_NAME)
                                       │
Browser เห็น: https://lib.npu.ac.th/aims/dashboard/staff/
```

### Django Settings ที่ต้องมีทุกระบบ

```python
# settings.py
FORCE_SCRIPT_NAME = os.getenv('FORCE_SCRIPT_NAME', '')  # เช่น /aims
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
CSRF_TRUSTED_ORIGINS = [...]
STATIC_URL = os.getenv('STATIC_URL', '/static/')  # เช่น /aims/static/
```

### .env ที่ต้องตั้งบน Production

```env
FORCE_SCRIPT_NAME=/aims        # ← ชื่อ path ของระบบนี้
STATIC_URL=/aims/static/       # ← FORCE_SCRIPT_NAME + /static/
CSRF_TRUSTED_ORIGINS=https://lib.npu.ac.th
WAITRESS_HOST=127.0.0.1
WAITRESS_PORT=8001             # ← port ที่จัดสรรให้ระบบนี้
```

---

## 4. ขั้นตอน Deploy ระบบใหม่

> **ตัวอย่าง:** สมมติระบบใหม่ชื่อ `myapp` ใช้ port `8002`
> แทนที่ `myapp` → ชื่อระบบจริง, `8002` → port ที่จัดสรร

### Step 1 — ตรวจสอบ Port ว่าง

```powershell
netstat -ano | findstr ":8002"
# ถ้าไม่มี output = port ว่าง พร้อมใช้
```

### Step 2 — Clone โค้ด

```powershell
cd C:\project
git clone https://github.com/[org]/[repo].git [folder-name]
cd C:\project\[folder-name]
```

### Step 3 — สร้าง Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\pip.exe install -r requirements.txt
.\venv\Scripts\pip.exe install waitress
```

### Step 4 — ตรวจสอบ settings.py

ต้องมี settings เหล่านี้ก่อน deploy:

```python
FORCE_SCRIPT_NAME = os.getenv('FORCE_SCRIPT_NAME', '')
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
CSRF_TRUSTED_ORIGINS = [o.strip() for o in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',') if o.strip()]
STATIC_URL = os.getenv('STATIC_URL', '/static/')
```

### Step 5 — สร้างไฟล์ .env

```powershell
notepad C:\project\[folder-name]\.env
```

```env
SECRET_KEY=[generate ด้วย python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"]
DEBUG=False
ALLOWED_HOSTS=localhost,110.78.83.102,lib.npu.ac.th

FORCE_SCRIPT_NAME=/myapp
STATIC_URL=/myapp/static/
CSRF_TRUSTED_ORIGINS=https://lib.npu.ac.th

DB_NAME=[database-name]
DB_USER=[db-user]
DB_PASSWORD=[db-password]
DB_HOST=202.29.55.213
DB_PORT=3306

WAITRESS_HOST=127.0.0.1
WAITRESS_PORT=8002
WAITRESS_THREADS=8
```

### Step 6 — Generate SECRET_KEY

```powershell
.\venv\Scripts\python.exe -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Step 7 — Migrate และ Collect Static

```powershell
$env:DJANGO_SETTINGS_MODULE = "[package].settings"
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py collectstatic --noinput
```

> **สำคัญ:** ต้องตั้ง `$env:DJANGO_SETTINGS_MODULE` ก่อนทุกครั้ง
> เพราะ server อาจมี env var เก่าค้างจากระบบอื่น

### Step 8 — สร้าง deploy/waitress_serve.py

ไฟล์นี้ต้อง **ไม่มี emoji** ในบรรทัด print เพราะ Windows NSSM log ใช้ encoding cp1252

```python
import os, sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(BASE_DIR, '.env'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '[package].settings')

host    = os.getenv('WAITRESS_HOST', '127.0.0.1')
port    = int(os.getenv('WAITRESS_PORT', '8002'))
threads = int(os.getenv('WAITRESS_THREADS', '8'))

print(f"[START] {host}:{port} ({threads} threads)")

from waitress import serve
from [package].wsgi import application

serve(application, host=host, port=port, threads=threads, url_scheme='https')
```

### Step 9 — ติดตั้ง NSSM Service

```powershell
# สร้าง Service
C:\nssm\nssm.exe install [ServiceName] `
    "C:\project\[folder]\venv\Scripts\python.exe" `
    "C:\project\[folder]\deploy\waitress_serve.py"

# ตั้งค่า
C:\nssm\nssm.exe set [ServiceName] AppDirectory "C:\project\[folder]"
C:\nssm\nssm.exe set [ServiceName] Start SERVICE_AUTO_START

# Log
New-Item -ItemType Directory -Path "C:\project\[folder]\logs" -Force
C:\nssm\nssm.exe set [ServiceName] AppStdout "C:\project\[folder]\logs\waitress.log"
C:\nssm\nssm.exe set [ServiceName] AppStderr "C:\project\[folder]\logs\waitress_error.log"
C:\nssm\nssm.exe set [ServiceName] AppRotateFiles 1
C:\nssm\nssm.exe set [ServiceName] AppRotateBytes 10485760

# Start
C:\nssm\nssm.exe start [ServiceName]
C:\nssm\nssm.exe status [ServiceName]
# ต้องได้: SERVICE_RUNNING
```

### Step 10 — ทดสอบ Waitress โดยตรง

```powershell
Invoke-WebRequest -Uri "http://localhost:8002/accounts/login/" -UseBasicParsing
# ต้องได้ StatusCode: 200
```

### Step 11 — IIS Virtual Directory สำหรับ Static Files

```powershell
Import-Module WebAdministration
New-WebVirtualDirectory -Site "Default Web Site" -Application "/" `
    -Name "myapp/static" `
    -PhysicalPath "C:\project\[folder]\staticfiles"
```

หรือทำผ่าน IIS Manager:
```
Default Web Site → Add Virtual Directory
  Alias:         myapp/static
  Physical path: C:\project\[folder]\staticfiles
```

### Step 12 — แก้ไข C:\iis_root\web.config

**Backup ก่อนเสมอ!**

```powershell
Copy-Item "C:\iis_root\web.config" "C:\iis_root\web.config.bak$(Get-Date -Format 'yyyyMMdd_HHmm')" -Force
```

เพิ่ม rules ใน `<rules>` block (ดูรายละเอียดใน [ส่วนที่ 5](#5-การแก้ไข-webconfig))

---

## 5. การแก้ไข web.config

ไฟล์อยู่ที่ `C:\iis_root\web.config` — **ใช้ร่วมกันทุกระบบ อย่า overwrite!**

### web.config ปัจจุบัน (สมบูรณ์)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <system.webServer>

        <defaultDocument enabled="false" />
        <directoryBrowse enabled="false" />

        <httpProtocol>
            <customHeaders>
                <remove name="X-Powered-By" />
            </customHeaders>
        </httpProtocol>

        <rewrite>
            <rules>

                <!-- Rule 0: Redirect HTTP → HTTPS -->
                <rule name="Force HTTPS" stopProcessing="true">
                    <match url="(.*)" />
                    <conditions>
                        <add input="{HTTPS}" pattern="^OFF$" />
                    </conditions>
                    <action type="Redirect"
                            url="https://{HTTP_HOST}/{R:1}"
                            redirectType="Permanent" />
                </rule>

                <!-- App 1: Project Tracker /projects → :8000 -->
                <rule name="App1 Root Redirect" stopProcessing="true">
                    <match url="^projects$" />
                    <action type="Redirect" url="/projects/" redirectType="Permanent" />
                </rule>
                <rule name="App1 Project Tracker" stopProcessing="true">
                    <match url="^projects/(.*)" />
                    <serverVariables>
                        <set name="HTTP_X_FORWARDED_PROTO" value="https" />
                        <set name="HTTP_X_REAL_IP" value="{REMOTE_ADDR}" />
                    </serverVariables>
                    <action type="Rewrite" url="http://127.0.0.1:8000/{R:1}" />
                </rule>

                <!-- App 2: AIMS /aims → :8001 -->
                <rule name="AIMS Static" stopProcessing="true">
                    <match url="^aims/static/(.*)" />
                    <action type="None" />
                </rule>
                <rule name="AIMS Root Redirect" stopProcessing="true">
                    <match url="^aims$" />
                    <action type="Redirect" url="/aims/" redirectType="Permanent" />
                </rule>
                <rule name="AIMS App" stopProcessing="true">
                    <match url="^aims/(.*)" />
                    <serverVariables>
                        <set name="HTTP_X_FORWARDED_PROTO" value="https" />
                        <set name="HTTP_X_REAL_IP" value="{REMOTE_ADDR}" />
                    </serverVariables>
                    <action type="Rewrite" url="http://127.0.0.1:8001/{R:1}" />
                </rule>

                <!-- App 3: [ระบบถัดไป] /[path] → :8002 -->
                <!--
                <rule name="App3 Static" stopProcessing="true">
                    <match url="^[path]/static/(.*)" />
                    <action type="None" />
                </rule>
                <rule name="App3 Root Redirect" stopProcessing="true">
                    <match url="^[path]$" />
                    <action type="Redirect" url="/[path]/" redirectType="Permanent" />
                </rule>
                <rule name="App3 [Name]" stopProcessing="true">
                    <match url="^[path]/(.*)" />
                    <serverVariables>
                        <set name="HTTP_X_FORWARDED_PROTO" value="https" />
                        <set name="HTTP_X_REAL_IP" value="{REMOTE_ADDR}" />
                    </serverVariables>
                    <action type="Rewrite" url="http://127.0.0.1:8002/{R:1}" />
                </rule>
                -->

            </rules>
        </rewrite>

        <security>
            <requestFiltering>
                <requestLimits maxAllowedContentLength="10485760" />
            </requestFiltering>
        </security>

    </system.webServer>
</configuration>
```

> เมื่อพร้อม deploy ระบบถัดไป: ลบ `<!--` และ `-->` รอบ App 3 แล้วแทน `[path]` และ `8002`

---

## 6. การทดสอบ

### ทดสอบ Waitress โดยตรง

```powershell
# ทดสอบ project_tracker
Invoke-WebRequest -Uri "http://localhost:8000/accounts/login/" -UseBasicParsing

# ทดสอบ AIMS
Invoke-WebRequest -Uri "http://localhost:8001/accounts/login/" -UseBasicParsing

# ทดสอบระบบใหม่
Invoke-WebRequest -Uri "http://localhost:8002/accounts/login/" -UseBasicParsing
```

### ทดสอบผ่าน HTTPS (ทุกระบบพร้อมกัน)

```powershell
"projects","aims" | ForEach-Object {
    $r = try { Invoke-WebRequest "https://lib.npu.ac.th/$_/" -UseBasicParsing } catch { $_.Exception.Response }
    Write-Host "$_ : $($r.StatusCode)"
}
```

---

## 7. การบำรุงรักษา

### คำสั่ง NSSM ที่ใช้บ่อย

```powershell
# ดูสถานะทุกระบบ
C:\nssm\nssm.exe status ProjectTracker
C:\nssm\nssm.exe status AIMS

# Restart หลัง git pull
C:\nssm\nssm.exe restart AIMS

# ดู log
Get-Content "C:\project\aims_project\logs\waitress_error.log" -Tail 50 -Wait
```

### อัปเดตโค้ด

```powershell
cd C:\project\aims_project
git pull origin main
$env:DJANGO_SETTINGS_MODULE = "aims_project.settings"
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py collectstatic --noinput
C:\nssm\nssm.exe restart AIMS
```

---

## 8. ข้อผิดพลาดที่พบบ่อย

| อาการ | สาเหตุ | วิธีแก้ |
|-------|--------|---------|
| `SERVICE_PAUSED` | Process crash → NSSM pause ป้องกัน loop | ดู error log: `Get-Content logs\waitress_error.log -Tail 30` |
| `ModuleNotFoundError: No module named 'config'` | `DJANGO_SETTINGS_MODULE` ค้างจากระบบอื่น | ตั้ง `$env:DJANGO_SETTINGS_MODULE = "[package].settings"` ก่อนรัน manage.py |
| `UnicodeEncodeError: 'charmap' codec` | มี emoji ใน print() ของ waitress_serve.py | ลบ emoji ออก + เพิ่ม `sys.stdout.reconfigure(encoding='utf-8')` |
| `400 Bad Request` | IP/hostname ไม่อยู่ใน `ALLOWED_HOSTS` | ทดสอบด้วย `localhost` แทน `127.0.0.1` |
| `404 Not Found` ที่ root `/` | `FORCE_SCRIPT_NAME` ตั้งไว้ ทำให้ `/` ไม่มี URL | ปกติ — ทดสอบด้วย `/accounts/login/` แทน |
| Static files หาย | ยังไม่ได้ทำ Virtual Directory หรือ URL rule | ตรวจ IIS Virtual Directory + ตรวจ web.config rule `action type="None"` |
| `502 Bad Gateway` | Waitress service ไม่รัน | `C:\nssm\nssm.exe start [ServiceName]` |
| CSRF Error login ไม่ได้ | `CSRF_TRUSTED_ORIGINS` ไม่ถูกต้อง | ตรวจ `.env`: `CSRF_TRUSTED_ORIGINS=https://lib.npu.ac.th` |
| Script encoding error | PowerShell อ่าน UTF-8 ผิด | แปลง Encoding ด้วย UTF-8 BOM ก่อนรัน `.ps1` |
| `Could not find path '...\deploy\iis\setup_iis.ps1'` | รัน script จาก directory ผิด | ใช้ path เต็ม `C:\project\[folder]\deploy\iis\setup_iis.ps1` |

---

## ภาคผนวก — โครงสร้าง Server

```
C:\project\
├── project_tracker\        ← App 1 (port 8000)
│   ├── .env
│   ├── venv\
│   ├── logs\
│   └── deploy\
│       └── waitress_serve.py
│
├── aims_project\           ← App 2 (port 8001)
│   ├── .env
│   ├── venv\
│   ├── staticfiles\
│   ├── logs\
│   └── deploy\
│       ├── waitress_serve.py
│       ├── iis\
│       │   ├── web.config   ← rules template
│       │   └── setup_iis.ps1
│       └── DEPLOY.md
│
└── [app3]\                 ← App 3 (port 8002) — ระบบถัดไป
    ├── .env
    ├── venv\
    └── deploy\

C:\iis_root\
└── web.config              ← IIS rules รวมทุก App (แก้ที่นี่ที่เดียว)

C:\nssm\
└── nssm.exe
```

---

*เอกสารนี้จัดทำโดยงานเทคนิคสารสนเทศและการจัดการทรัพยากร สำนักวิทยบริการ มหาวิทยาลัยนครพนม*
