# =============================================================
# AIMS Project — IIS + NSSM Setup Script
# รัน: .\deploy\iis\setup_iis.ps1 ด้วย PowerShell (Administrator)
# =============================================================

param(
    [string]$ProjectPath   = "C:\project\aims_project",
    [string]$NssmPath      = "C:\nssm\nssm.exe",
    [string]$IisRootPath   = "C:\iis_root",
    [string]$ServiceName   = "AIMS",
    [int]$Port             = 8001
)

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AIMS Project — Setup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ------------------------------------------------------------
# 1. ตรวจสอบ path สำคัญ
# ------------------------------------------------------------
# ตั้ง DJANGO_SETTINGS_MODULE ให้ชัดเจน (ป้องกัน inherit จาก project_tracker)
$env:DJANGO_SETTINGS_MODULE = "aims_project.settings"
Write-Host "   DJANGO_SETTINGS_MODULE = $env:DJANGO_SETTINGS_MODULE" -ForegroundColor DarkGray

Write-Host "[1/6] ตรวจสอบ paths..." -ForegroundColor Yellow

if (-not (Test-Path "$ProjectPath\manage.py")) {
    Write-Error "ไม่พบ manage.py ที่ $ProjectPath — ตรวจสอบ path โปรเจ็กต์"
    exit 1
}
if (-not (Test-Path $NssmPath)) {
    Write-Error "ไม่พบ nssm.exe ที่ $NssmPath"
    exit 1
}
Write-Host "   ✅ paths OK" -ForegroundColor Green

# ------------------------------------------------------------
# 2. Collect Static Files
# ------------------------------------------------------------
Write-Host "[2/6] Collect static files..." -ForegroundColor Yellow
& "$ProjectPath\venv\Scripts\python.exe" "$ProjectPath\manage.py" collectstatic --noinput
if ($LASTEXITCODE -ne 0) {
    Write-Error "collectstatic ล้มเหลว"
    exit 1
}
Write-Host "   ✅ static files collected" -ForegroundColor Green

# ------------------------------------------------------------
# 3. Database Migration
# ------------------------------------------------------------
Write-Host "[3/6] Database migration..." -ForegroundColor Yellow
& "$ProjectPath\venv\Scripts\python.exe" "$ProjectPath\manage.py" migrate
if ($LASTEXITCODE -ne 0) {
    Write-Error "migrate ล้มเหลว"
    exit 1
}
Write-Host "   ✅ migrations done" -ForegroundColor Green

# ------------------------------------------------------------
# 4. สร้าง NSSM Service
# ------------------------------------------------------------
Write-Host "[4/6] สร้าง Windows Service '$ServiceName'..." -ForegroundColor Yellow

# หยุด service เดิมก่อน (ถ้ามี)
$existingService = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($existingService) {
    Write-Host "   พบ service เดิม — หยุดและลบก่อน..." -ForegroundColor DarkYellow
    & $NssmPath stop $ServiceName confirm 2>$null
    & $NssmPath remove $ServiceName confirm 2>$null
    Start-Sleep -Seconds 2
}

# สร้าง service ใหม่
& $NssmPath install $ServiceName `
    "$ProjectPath\venv\Scripts\python.exe" `
    "$ProjectPath\deploy\waitress_serve.py"

& $NssmPath set $ServiceName AppDirectory "$ProjectPath"
& $NssmPath set $ServiceName DisplayName "AIMS - Academic Information Management System"
& $NssmPath set $ServiceName Description "AIMS Django app via Waitress on port $Port"
& $NssmPath set $ServiceName Start SERVICE_AUTO_START

# Log directory
$logDir = "$ProjectPath\logs"
New-Item -ItemType Directory -Path $logDir -Force | Out-Null
& $NssmPath set $ServiceName AppStdout "$logDir\waitress.log"
& $NssmPath set $ServiceName AppStderr "$logDir\waitress_error.log"
& $NssmPath set $ServiceName AppRotateFiles 1
& $NssmPath set $ServiceName AppRotateBytes 10485760  # 10 MB

Write-Host "   ✅ service '$ServiceName' สร้างแล้ว" -ForegroundColor Green

# ------------------------------------------------------------
# 5. เพิ่ม IIS Server Variables (ถ้ายังไม่มี)
# ------------------------------------------------------------
Write-Host "[5/6] ตั้งค่า IIS Server Variables..." -ForegroundColor Yellow

Import-Module WebAdministration -ErrorAction SilentlyContinue

$vars = @("HTTP_X_FORWARDED_PROTO", "HTTP_X_FORWARDED_HOST")
foreach ($var in $vars) {
    $existing = Get-WebConfiguration `
        -PSPath "MACHINE/WEBROOT/APPHOST" `
        -Filter "system.webServer/rewrite/allowedServerVariables/add[@name='$var']" `
        -ErrorAction SilentlyContinue

    if (-not $existing) {
        Add-WebConfiguration `
            -PSPath "MACHINE/WEBROOT/APPHOST" `
            -Filter "system.webServer/rewrite/allowedServerVariables" `
            -Value @{ name = $var }
        Write-Host "   ✅ เพิ่ม $var" -ForegroundColor Green
    } else {
        Write-Host "   ℹ️  $var มีอยู่แล้ว" -ForegroundColor DarkGray
    }
}

# ------------------------------------------------------------
# 6. เพิ่ม Virtual Directory สำหรับ Static Files
# ------------------------------------------------------------
Write-Host "[6/6] เพิ่ม IIS Virtual Directory /aims/static/..." -ForegroundColor Yellow

$staticPath = "$ProjectPath\staticfiles"
$siteName   = "Default Web Site"

try {
    $vdir = Get-WebVirtualDirectory -Site $siteName -Application "/" -Name "aims/static" -ErrorAction SilentlyContinue
    if (-not $vdir) {
        New-WebVirtualDirectory -Site $siteName -Application "/" `
            -Name "aims/static" -PhysicalPath $staticPath
        Write-Host "   ✅ Virtual Directory /aims/static/ → $staticPath" -ForegroundColor Green
    } else {
        Write-Host "   ℹ️  Virtual Directory มีอยู่แล้ว" -ForegroundColor DarkGray
    }
} catch {
    Write-Warning "ไม่สามารถสร้าง Virtual Directory อัตโนมัติได้ — สร้างผ่าน IIS Manager แทน"
    Write-Host "   Alias: aims/static  →  Physical: $staticPath" -ForegroundColor DarkYellow
}

# ------------------------------------------------------------
# Start Service
# ------------------------------------------------------------
Write-Host ""
Write-Host "Starting service '$ServiceName'..." -ForegroundColor Cyan
& $NssmPath start $ServiceName
Start-Sleep -Seconds 3
& $NssmPath status $ServiceName

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Setup เสร็จสิ้น!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  ทดสอบ Waitress:" -ForegroundColor White
Write-Host "  Invoke-WebRequest -Uri 'http://127.0.0.1:$Port/' -UseBasicParsing" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  หมายเหตุ: อย่าลืมเพิ่ม rules ใน C:\iis_root\web.config" -ForegroundColor Yellow
Write-Host "  (ดูตัวอย่างใน deploy\iis\web.config)" -ForegroundColor Yellow
Write-Host ""
