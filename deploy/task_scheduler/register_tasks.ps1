# =====================================================
#  AIMS — Register Windows Task Scheduler Jobs
#  รันครั้งเดียวใน PowerShell as Administrator
# =====================================================

$AIMS_DIR = "C:\project\aims_project"

# --- Task 1: Sync Staff (02:00) ---
$action1 = New-ScheduledTaskAction `
    -Execute "$AIMS_DIR\deploy\task_scheduler\sync_staff.bat"

$trigger1 = New-ScheduledTaskTrigger `
    -Daily -At "02:00"

$settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1) `
    -StartWhenAvailable

Register-ScheduledTask `
    -TaskName "AIMS Sync Staff" `
    -Action $action1 `
    -Trigger $trigger1 `
    -Settings $settings `
    -RunLevel Highest `
    -Force

Write-Host "[OK] Registered: AIMS Sync Staff (daily 02:00)"

# --- Task 2: Sync Students (02:30) ---
$action2 = New-ScheduledTaskAction `
    -Execute "$AIMS_DIR\deploy\task_scheduler\sync_students.bat"

$trigger2 = New-ScheduledTaskTrigger `
    -Daily -At "02:30"

Register-ScheduledTask `
    -TaskName "AIMS Sync Students" `
    -Action $action2 `
    -Trigger $trigger2 `
    -Settings $settings `
    -RunLevel Highest `
    -Force

Write-Host "[OK] Registered: AIMS Sync Students (daily 02:30)"

# --- แสดง tasks ที่ลงทะเบียนแล้ว ---
Write-Host ""
Write-Host "=== Tasks registered ==="
Get-ScheduledTask -TaskName "AIMS Sync Staff", "AIMS Sync Students" |
    Select-Object TaskName, State |
    Format-Table -AutoSize
