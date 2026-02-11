@echo off
REM ============================================================
REM AIMS Dashboard - NSSM Service Installation Script
REM ============================================================
REM วิธีใช้: รันด้วย Administrator privileges
REM ============================================================

setlocal enabledelayedexpansion

REM === Configuration ===
set SERVICE_NAME=AIMS-Dashboard
set DISPLAY_NAME=AIMS Dashboard Service
set DESCRIPTION=Academic Information Management System - Django Web Application

REM === Paths (Production Server) ===
set PROJECT_DIR=C:\inetpub\wwwroot\aims
set PYTHON_PATH=C:\inetpub\wwwroot\aims\aims_env\Scripts\python.exe
set SCRIPT_PATH=C:\inetpub\wwwroot\aims\waitress_server.py
set NSSM_PATH=C:\nssm\nssm.exe

REM === Log files ===
set LOG_DIR=%PROJECT_DIR%\logs
set STDOUT_LOG=%LOG_DIR%\aims_stdout.log
set STDERR_LOG=%LOG_DIR%\aims_stderr.log

echo ============================================================
echo   AIMS Dashboard - Service Installation
echo ============================================================
echo.

REM === Check if running as Administrator ===
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] กรุณารันด้วย Administrator privileges!
    echo         Right-click และเลือก "Run as administrator"
    pause
    exit /b 1
)

REM === Check NSSM exists ===
if not exist "%NSSM_PATH%" (
    echo [ERROR] ไม่พบ NSSM ที่ %NSSM_PATH%
    echo         ดาวน์โหลดจาก: https://nssm.cc/download
    pause
    exit /b 1
)

REM === Check Python exists ===
if not exist "%PYTHON_PATH%" (
    echo [ERROR] ไม่พบ Python ที่ %PYTHON_PATH%
    echo         กรุณาตรวจสอบ path ของ virtual environment
    pause
    exit /b 1
)

REM === Check project exists ===
if not exist "%SCRIPT_PATH%" (
    echo [ERROR] ไม่พบ waitress_server.py ที่ %SCRIPT_PATH%
    pause
    exit /b 1
)

REM === Create log directory ===
if not exist "%LOG_DIR%" (
    echo [INFO] สร้างโฟลเดอร์ logs...
    mkdir "%LOG_DIR%"
)

REM === Remove existing service if exists ===
echo [INFO] ตรวจสอบ service เดิม...
%NSSM_PATH% status %SERVICE_NAME% >nul 2>&1
if %errorLevel% equ 0 (
    echo [INFO] พบ service เดิม กำลังลบ...
    %NSSM_PATH% stop %SERVICE_NAME% >nul 2>&1
    %NSSM_PATH% remove %SERVICE_NAME% confirm >nul 2>&1
    timeout /t 2 >nul
)

REM === Install new service ===
echo [INFO] กำลังติดตั้ง service ใหม่...
%NSSM_PATH% install %SERVICE_NAME% "%PYTHON_PATH%" "%SCRIPT_PATH%"

REM === Configure service ===
echo [INFO] กำหนดค่า service...

REM Display name and description
%NSSM_PATH% set %SERVICE_NAME% DisplayName "%DISPLAY_NAME%"
%NSSM_PATH% set %SERVICE_NAME% Description "%DESCRIPTION%"

REM Working directory
%NSSM_PATH% set %SERVICE_NAME% AppDirectory "%PROJECT_DIR%"

REM Startup type (Automatic)
%NSSM_PATH% set %SERVICE_NAME% Start SERVICE_AUTO_START

REM Log files
%NSSM_PATH% set %SERVICE_NAME% AppStdout "%STDOUT_LOG%"
%NSSM_PATH% set %SERVICE_NAME% AppStderr "%STDERR_LOG%"
%NSSM_PATH% set %SERVICE_NAME% AppStdoutCreationDisposition 4
%NSSM_PATH% set %SERVICE_NAME% AppStderrCreationDisposition 4
%NSSM_PATH% set %SERVICE_NAME% AppRotateFiles 1
%NSSM_PATH% set %SERVICE_NAME% AppRotateOnline 1
%NSSM_PATH% set %SERVICE_NAME% AppRotateBytes 10485760

REM Restart on failure
%NSSM_PATH% set %SERVICE_NAME% AppThrottle 5000
%NSSM_PATH% set %SERVICE_NAME% AppExit Default Restart
%NSSM_PATH% set %SERVICE_NAME% AppRestartDelay 5000

REM === Start the service ===
echo [INFO] กำลังเริ่ม service...
%NSSM_PATH% start %SERVICE_NAME%

REM === Check status ===
timeout /t 3 >nul
%NSSM_PATH% status %SERVICE_NAME%

echo.
echo ============================================================
echo   การติดตั้งเสร็จสมบูรณ์!
echo ============================================================
echo.
echo   Service Name: %SERVICE_NAME%
echo   Status: รัน 'nssm status %SERVICE_NAME%' เพื่อตรวจสอบ
echo   URL: http://localhost:8005/
echo.
echo   คำสั่งที่ใช้บ่อย:
echo   - เริ่ม:    nssm start %SERVICE_NAME%
echo   - หยุด:    nssm stop %SERVICE_NAME%
echo   - รีสตาร์ท: nssm restart %SERVICE_NAME%
echo   - สถานะ:   nssm status %SERVICE_NAME%
echo   - แก้ไข:   nssm edit %SERVICE_NAME%
echo   - ลบ:     nssm remove %SERVICE_NAME%
echo.
echo   Log files:
echo   - stdout: %STDOUT_LOG%
echo   - stderr: %STDERR_LOG%
echo ============================================================

pause
