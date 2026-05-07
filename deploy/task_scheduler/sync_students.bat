@echo off
REM =====================================================
REM  AIMS — Sync Students Info (Windows Task Scheduler)
REM  ตั้งเวลา: ทุกวัน 02:30 น.
REM  Log: C:\projects\aims_project\logs\sync_students.log
REM =====================================================

set AIMS_DIR=C:\project\aims_project
set VENV_PYTHON=C:\Python312\python.exe
set LOG_FILE=%AIMS_DIR%\logs\sync_students.log

REM สร้าง log directory ถ้ายังไม่มี
if not exist "%AIMS_DIR%\logs" mkdir "%AIMS_DIR%\logs"

echo. >> %LOG_FILE%
echo ============================================ >> %LOG_FILE%
echo [%date% %time%] START sync_students >> %LOG_FILE%

"%VENV_PYTHON%" "%AIMS_DIR%\manage.py" sync_students --triggered-by=schedule >> %LOG_FILE% 2>&1

echo [%date% %time%] END sync_students (exit code: %errorlevel%) >> %LOG_FILE%
