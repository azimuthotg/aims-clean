@echo off
REM ============================================================
REM AIMS Dashboard - Service Management Script
REM ============================================================

set SERVICE_NAME=AIMS-Dashboard
set NSSM_PATH=C:\nssm\nssm.exe

:menu
cls
echo ============================================================
echo   AIMS Dashboard - Service Management
echo ============================================================
echo.
echo   1. ดูสถานะ service (Status)
echo   2. เริ่ม service (Start)
echo   3. หยุด service (Stop)
echo   4. รีสตาร์ท service (Restart)
echo   5. แก้ไขการตั้งค่า (Edit)
echo   6. ดู log files
echo   7. ลบ service (Remove)
echo   8. ออก (Exit)
echo.
echo ============================================================
set /p choice="เลือกหมายเลข: "

if "%choice%"=="1" goto status
if "%choice%"=="2" goto start
if "%choice%"=="3" goto stop
if "%choice%"=="4" goto restart
if "%choice%"=="5" goto edit
if "%choice%"=="6" goto logs
if "%choice%"=="7" goto remove
if "%choice%"=="8" goto end
goto menu

:status
echo.
echo [INFO] สถานะ service:
%NSSM_PATH% status %SERVICE_NAME%
echo.
pause
goto menu

:start
echo.
echo [INFO] กำลังเริ่ม service...
%NSSM_PATH% start %SERVICE_NAME%
timeout /t 2 >nul
%NSSM_PATH% status %SERVICE_NAME%
echo.
pause
goto menu

:stop
echo.
echo [INFO] กำลังหยุด service...
%NSSM_PATH% stop %SERVICE_NAME%
timeout /t 2 >nul
%NSSM_PATH% status %SERVICE_NAME%
echo.
pause
goto menu

:restart
echo.
echo [INFO] กำลังรีสตาร์ท service...
%NSSM_PATH% restart %SERVICE_NAME%
timeout /t 3 >nul
%NSSM_PATH% status %SERVICE_NAME%
echo.
pause
goto menu

:edit
echo.
echo [INFO] เปิดหน้าต่างแก้ไข service...
%NSSM_PATH% edit %SERVICE_NAME%
goto menu

:logs
echo.
echo [INFO] Log files location:
echo   - C:\inetpub\wwwroot\aims\logs\aims_stdout.log
echo   - C:\inetpub\wwwroot\aims\logs\aims_stderr.log
echo.
echo [INFO] แสดง 30 บรรทัดล่าสุดของ stdout log:
echo ----------------------------------------
if exist "C:\inetpub\wwwroot\aims\logs\aims_stdout.log" (
    powershell -command "Get-Content 'C:\inetpub\wwwroot\aims\logs\aims_stdout.log' -Tail 30"
) else (
    echo ไม่พบไฟล์ log
)
echo ----------------------------------------
echo.
pause
goto menu

:remove
echo.
echo [WARNING] คุณกำลังจะลบ service!
set /p confirm="พิมพ์ 'YES' เพื่อยืนยัน: "
if "%confirm%"=="YES" (
    %NSSM_PATH% stop %SERVICE_NAME% >nul 2>&1
    %NSSM_PATH% remove %SERVICE_NAME% confirm
    echo [INFO] ลบ service เรียบร้อยแล้ว
) else (
    echo [INFO] ยกเลิกการลบ
)
pause
goto menu

:end
echo.
echo Goodbye!
exit /b 0
