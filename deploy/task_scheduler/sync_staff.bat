@echo off
REM =====================================================
REM  AIMS — Sync Staff Info (Windows Task Scheduler)
REM  ตั้งเวลา: ทุกวัน 02:00 น.
REM  Log: C:\projects\aims_project\logs\sync_staff.log
REM =====================================================

set AIMS_DIR=C:\project\aims_project
set VENV_PYTHON=%AIMS_DIR%\venv\Scripts\python.exe
set LOG_FILE=%AIMS_DIR%\logs\sync_staff.log

REM สร้าง log directory ถ้ายังไม่มี
if not exist "%AIMS_DIR%\logs" mkdir "%AIMS_DIR%\logs"

echo. >> %LOG_FILE%
echo ============================================ >> %LOG_FILE%
echo [%date% %time%] START sync_staff >> %LOG_FILE%

"%VENV_PYTHON%" "%AIMS_DIR%\manage.py" sync_staff --triggered-by=schedule >> %LOG_FILE% 2>&1

echo [%date% %time%] END sync_staff (exit code: %errorlevel%) >> %LOG_FILE%
