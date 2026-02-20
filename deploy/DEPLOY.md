# คู่มือการติดตั้งระบบ AIMS
## สำนักวิทยบริการ มหาวิทยาลัยนครพนม

**เวอร์ชัน:** 2.0
**วันที่:** กุมภาพันธ์ 2569
**ผู้จัดทำ:** งานเทคนิคสารสนเทศและการจัดการทรัพยากร

---

## สารบัญ

1. [ภาพรวมระบบ](#1-ภาพรวมระบบ)
2. [สิ่งที่ต้องเตรียม](#2-สิ่งที่ต้องเตรียม)
3. [สถาปัตยกรรมระบบ](#3-สถาปัตยกรรมระบบ)
4. [ขั้นตอนการติดตั้ง](#4-ขั้นตอนการติดตั้ง)
5. [การตั้งค่า Environment](#5-การตั้งค่า-environment)
6. [การติดตั้ง Windows Service](#6-การติดตั้ง-windows-service)
7. [การตั้งค่า IIS](#7-การตั้งค่า-iis)
8. [การทดสอบระบบ](#8-การทดสอบระบบ)
9. [การบำรุงรักษา](#9-การบำรุงรักษา)
10. [การแก้ปัญหาที่พบบ่อย](#10-การแก้ปัญหาที่พบบ่อย)

---

## 1. ภาพรวมระบบ

ระบบ AIMS (Academic Information Management System) เป็นเว็บแอปพลิเคชันพัฒนาด้วย **Django 5.0** สำหรับบริหารจัดการข้อมูลบุคลากรและนักศึกษา

**URL ที่ใช้งาน:**
```
https://lib.npu.ac.th/aims/
```

**ข้อมูลเซิร์ฟเวอร์:**

| รายการ | ค่า |
|--------|-----|
| IP Address | 110.78.83.102 |
| Domain | lib.npu.ac.th |
| OS | Windows Server 2019 |
| Path โปรเจ็กต์ | C:\project\aims_project |
| Port ภายใน | 8001 (Waitress) |

---

## 2. สิ่งที่ต้องเตรียม

### 2.1 ซอฟต์แวร์
| รายการ | เวอร์ชัน | หมายเหตุ |
|--------|----------|---------|
| Windows Server | 2019 | ติดตั้งแล้ว |
| Python | 3.12+ | ต้องติดตั้งก่อน |
| Git | ล่าสุด | สำหรับ clone/pull โค้ด |
| IIS | 10.0 | ติดตั้งแล้ว (จาก project_tracker) |
| ARR Module | 3.0 | ติดตั้งแล้ว (จาก project_tracker) |
| URL Rewrite Module | 2.1 | ติดตั้งแล้ว (จาก project_tracker) |
| NSSM | 2.24 | มีอยู่ที่ C:\nssm\nssm.exe แล้ว |

> **หมายเหตุ:** IIS, ARR, URL Rewrite, NSSM ติดตั้งแล้วทั้งหมดจากการ deploy project_tracker
> ไม่ต้องติดตั้งซ้ำ — ข้ามไปขั้นตอนที่ 4 ได้เลย

### 2.2 ไฟล์ที่ต้องเตรียม
| ไฟล์ | ที่เก็บ | หมายเหตุ |
|------|---------|---------|
| .env | C:\project\aims_project\ | copy จาก deploy\.env.production แล้วแก้ค่า |
| credentials JSON | C:\project\aims_project\credentials\ | Google Sheets API |

---

## 3. สถาปัตยกรรมระบบ

### 3.1 ภาพรวม Path-based Routing

ระบบรันบน Server เดียวกับ project_tracker โดยใช้ **Path-based Routing** แยก path กัน:

```
ผู้ใช้งาน (Browser)
        │
        │  https://lib.npu.ac.th/aims/
        ▼
┌─────────────────────────────────────┐
│  IIS 10.0 (Windows Server 2019)     │
│  Port 443 → รับ HTTPS Request       │
│                                     │
│  SSL: cert2026.pfx (*.npu.ac.th)   │
│  /aims/static/* → staticfiles/     │  ← IIS serve โดยตรง
│  /aims/*        → :8001            │  ← Reverse Proxy
│  /projects/*    → :8000            │  ← project_tracker (เดิม)
└──────────────────┬──────────────────┘
                   │ http://127.0.0.1:8001/
                   ▼
┌─────────────────────────────────────┐
│  Waitress (Python WSGI Server)      │
│  Listen: 127.0.0.1:8001            │
│  Service: AIMS (NSSM)              │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│  Django Application                 │
│  Settings: aims_project.settings   │
│  FORCE_SCRIPT_NAME: /aims          │
└─────────────────────────────────────┘
```

### 3.2 การทำงานของ Path-based Routing

1. Browser ส่ง Request: `https://lib.npu.ac.th/aims/dashboard/staff/`
2. IIS รับ Request และ **ตัด prefix `/aims`** ออก
3. IIS ส่งต่อให้ Waitress: `http://127.0.0.1:8001/dashboard/staff/`
4. Django ประมวลผลและสร้าง URL กลับโดยใส่ `/aims` นำหน้าทุก Link (ผ่าน `FORCE_SCRIPT_NAME`)
5. ผู้ใช้เห็น URL ที่ถูกต้อง: `https://lib.npu.ac.th/aims/dashboard/staff/`

---

## 4. ขั้นตอนการติดตั้ง

### 4.1 Clone โค้ดจาก GitHub

เปิด **PowerShell (Administrator)** แล้วรัน:

```powershell
cd C:\project
git clone https://github.com/azimuthotg/aims-clean.git aims_project
cd C:\project\aims_project
```

### 4.2 สร้าง Virtual Environment และติดตั้ง Dependencies

```powershell
python -m venv venv
.\venv\Scripts\pip.exe install -r requirements.txt
.\venv\Scripts\pip.exe install waitress
```

### 4.3 ตรวจสอบระบบ

```powershell
.\venv\Scripts\python.exe manage.py check
```

---

## 5. การตั้งค่า Environment

### 5.1 สร้างไฟล์ .env

```powershell
copy C:\project\aims_project\deploy\.env.production C:\project\aims_project\.env
notepad C:\project\aims_project\.env
```

แก้ไขค่าที่ต้องเปลี่ยน:

```env
SECRET_KEY=ใส่-random-key-ที่นี่
ALLOWED_HOSTS=localhost,110.78.83.102,lib.npu.ac.th
FORCE_SCRIPT_NAME=/aims
STATIC_URL=/aims/static/
CSRF_TRUSTED_ORIGINS=https://lib.npu.ac.th
DB_USER=ใส่-db-username
DB_PASSWORD=ใส่-db-password
API_DB_USER=ใส่-api-db-username
API_DB_PASSWORD=ใส่-api-db-password
LDAP_API_TOKEN=ใส่-JWT-token
WAITRESS_PORT=8001
```

### 5.2 Generate SECRET_KEY

```powershell
.\venv\Scripts\python.exe -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

นำค่าที่ได้ไปใส่ใน `SECRET_KEY=` ในไฟล์ `.env`

### 5.3 Collect Static Files

```powershell
cd C:\project\aims_project
.\venv\Scripts\python.exe manage.py collectstatic --noinput
```

### 5.4 Run Database Migrations

```powershell
.\venv\Scripts\python.exe manage.py migrate
```

---

## 6. การติดตั้ง Windows Service (NSSM + Waitress)

```powershell
cd C:\project\aims_project

# แปลง Encoding ก่อน (สำคัญ!)
$path = ".\deploy\iis\setup_iis.ps1"
$content = [System.IO.File]::ReadAllText($path, [System.Text.Encoding]::UTF8)
$utf8Bom = New-Object System.Text.UTF8Encoding $true
[System.IO.File]::WriteAllText($path, $content, $utf8Bom)

# รัน Setup Script
.\deploy\iis\setup_iis.ps1
```

Script จะดำเนินการ:
- ✅ Collect static files
- ✅ Run migrations
- ✅ สร้าง NSSM Service ชื่อ **AIMS**
- ✅ เพิ่ม IIS Server Variables
- ✅ สร้าง Virtual Directory `/aims/static/`
- ✅ Start service

### ตรวจสอบสถานะ Service

```powershell
C:\nssm\nssm.exe status AIMS
# ต้องแสดง: SERVICE_RUNNING
```

---

## 7. การตั้งค่า IIS

### 7.1 เพิ่ม Rules ใน web.config

> **สำคัญ:** ไม่ต้องสร้าง web.config ใหม่ — ต้องเพิ่ม rules เข้าไปในไฟล์ที่มีอยู่ที่ `C:\iis_root\web.config`
> (ไฟล์นี้คุม project_tracker อยู่ด้วย อย่า overwrite!)

เปิด `C:\iis_root\web.config` แล้วเพิ่ม rules ของ AIMS เข้าไปใน `<rules>` block:

```xml
<!-- AIMS: Static files — ให้ IIS serve โดยตรง ไม่ผ่าน Waitress -->
<rule name="AIMS Static Files" stopProcessing="true">
    <match url="^aims/static/(.*)" />
    <conditions>
        <add input="{REQUEST_FILENAME}" matchType="IsFile" />
    </conditions>
    <action type="None" />
</rule>

<!-- AIMS: App — Reverse Proxy ไป Waitress port 8001 -->
<rule name="AIMS App" stopProcessing="true">
    <match url="^aims/(.*)" />
    <action type="Rewrite" url="http://127.0.0.1:8001/{R:1}" />
    <serverVariables>
        <set name="HTTP_X_FORWARDED_PROTO" value="https" />
        <set name="HTTP_X_FORWARDED_HOST" value="{HTTP_HOST}" />
    </serverVariables>
</rule>
```

> ดูตัวอย่าง rules ฉบับเต็มได้ที่ `deploy/iis/web.config`

### 7.2 Virtual Directory (ถ้า Script ทำไม่สำเร็จ)

สร้างผ่าน IIS Manager:
```
Site: Default Web Site
Add Virtual Directory:
  Alias:         aims/static
  Physical path: C:\project\aims_project\staticfiles
```

---

## 8. การทดสอบระบบ

### 8.1 ทดสอบ Waitress (ภายใน)

```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:8001/" -UseBasicParsing
# ต้องได้รับ Response (302 redirect ถือว่าปกติ)
```

### 8.2 ทดสอบผ่าน Browser

| URL | ผลที่คาดหวัง |
|-----|-------------|
| `https://lib.npu.ac.th/aims/` | แสดงหน้า Login |
| `https://lib.npu.ac.th/aims/accounts/login/` | แสดงหน้า Login LDAP |
| `https://lib.npu.ac.th/aims/dashboard/staff/` | หน้า Staff Dashboard (ต้อง login ก่อน) |

---

## 9. การบำรุงรักษา

### 9.1 คำสั่ง Service ที่ใช้บ่อย

```powershell
# ดูสถานะ
C:\nssm\nssm.exe status AIMS

# Restart (หลัง git pull หรือแก้ไข .env)
C:\nssm\nssm.exe restart AIMS

# Stop / Start
C:\nssm\nssm.exe stop AIMS
C:\nssm\nssm.exe start AIMS
```

### 9.2 อัปเดตโค้ด

```powershell
cd C:\project\aims_project
git pull origin main
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py collectstatic --noinput
C:\nssm\nssm.exe restart AIMS
```

### 9.3 ดู Log

```powershell
# Log ทั่วไป
Get-Content "C:\project\aims_project\logs\waitress.log" -Tail 50

# Log Error
Get-Content "C:\project\aims_project\logs\waitress_error.log" -Tail 50

# Real-time
Get-Content "C:\project\aims_project\logs\waitress_error.log" -Wait
```

---

## 10. การแก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุ | วิธีแก้ |
|-------|--------|---------|
| **502 Bad Gateway** | AIMS service ไม่ได้รัน | `C:\nssm\nssm.exe start AIMS` |
| **400 Bad Request** | `lib.npu.ac.th` ไม่อยู่ใน ALLOWED_HOSTS | แก้ไข `.env` แล้ว restart |
| **404 ทุกหน้า** | `FORCE_SCRIPT_NAME` ไม่ถูกต้อง | ตรวจสอบ `FORCE_SCRIPT_NAME=/aims` ใน `.env` |
| **Static files หาย** | ยังไม่ได้รัน collectstatic หรือ Virtual Directory ผิด | รัน collectstatic + ตรวจ IIS Virtual Directory |
| **CSRF Error** | `CSRF_TRUSTED_ORIGINS` ไม่มี domain | เพิ่ม `CSRF_TRUSTED_ORIGINS=https://lib.npu.ac.th` ใน `.env` |
| **500.50 URL Rewrite Error** | Server Variable ไม่ได้ unlock | รัน setup_iis.ps1 ใหม่ หรือเพิ่ม allowedServerVariables manual |
| **Login loop** | `SESSION_COOKIE_SECURE=True` แต่ไม่มี HTTPS | ตรวจสอบว่า IIS ส่ง `X-Forwarded-Proto: https` |
| **Script encoding error** | PowerShell อ่าน UTF-8 ผิด | แปลง Encoding ด้วย UTF8 BOM ก่อนรัน script |

---

## ภาคผนวก — โครงสร้างไฟล์สำคัญ

```
C:\project\aims_project\
├── .env                          ← Environment variables (ไม่ commit)
├── deploy\
│   ├── .env.production          ← Template .env สำหรับ production
│   ├── waitress_serve.py        ← Entry point สำหรับ Waitress / NSSM
│   ├── DEPLOY.md                ← คู่มือนี้
│   └── iis\
│       ├── web.config           ← AIMS IIS rules (นำไปเพิ่มใน C:\iis_root\web.config)
│       └── setup_iis.ps1        ← IIS + NSSM Setup script
├── logs\
│   ├── waitress.log             ← Application log
│   └── waitress_error.log       ← Error log
├── staticfiles\                 ← Static files (หลัง collectstatic)
└── credentials\
    └── *.json                   ← Google Sheets API credentials

C:\iis_root\
└── web.config                   ← IIS website root (shared กับ project_tracker)

C:\nssm\
└── nssm.exe                     ← Service Manager (shared)
```

---

*เอกสารนี้จัดทำโดยงานเทคนิคสารสนเทศและการจัดการทรัพยากร สำนักวิทยบริการ มหาวิทยาลัยนครพนม*
