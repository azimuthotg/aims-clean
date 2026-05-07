@echo off
REM =====================================================
REM  AIMS — Sync Staff Info (Windows Task Scheduler)
REM  ตั้งเวลา: ทุกวัน 02:00 น.
REM  Log: C:\aims_logs\sync_staff.log
REM =====================================================

set AIMS_DIR=C:\projects\aims_project
set VENV_PYTHON=%AIMS_DIR%\venv_new\Scripts\python.exe
set LOG_FILE=C:\aims_logs\sync_staff.log

REM สร้าง log directory ถ้ายังไม่มี
if not exist "C:\aims_logs" mkdir "C:\aims_logs"

echo. >> %LOG_FILE%
echo ============================================ >> %LOG_FILE%
echo [%date% %time%] START sync_staff >> %LOG_FILE%

"%VENV_PYTHON%" "%AIMS_DIR%\manage.py" sync_staff --triggered-by=schedule >> %LOG_FILE% 2>&1

echo [%date% %time%] END sync_staff (exit code: %errorlevel%) >> %LOG_FILE%
