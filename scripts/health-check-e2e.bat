@echo off
setlocal enabledelayedexpansion

set "timestamp=%date% %time%"
set "logFile=C:\Users\Karen\.openclaw\workspace\memory\health-checks.log"
set "statusFile=C:\Users\Karen\.openclaw\workspace\.health-status.json"
set "testFile=C:\Users\Karen\.openclaw\workspace\.health-test-%random%.txt"

set "overall=PASS"
set "results="

:: Test 1: File write/read
echo health-check-test-%timestamp% > "%testFile%"
set /p written= < "%testFile%"
if exist "%testFile%" del "%testFile%"
if "!written:~0,17!"=="health-check-test" (
    set "results=!results!\"exec_write\": {\"status\": \"PASS\", \"detail\": \"File write/read working\"}, "
) else (
    set "results=!results!\"exec_write\": {\"status\": \"FAIL\", \"detail\": \"Content mismatch or write failed\"}, "
    set "overall=FAIL"
)

:: Test 2: Node config exists
if exist "C:\Users\Karen\.openclaw\node.json" (
    set "results=!results!\"node_config\": {\"status\": \"PASS\", \"detail\": \"node.json exists\"}, "
) else (
    set "results=!results!\"node_config\": {\"status\": \"FAIL\", \"detail\": \"node.json not found\"}, "
    set "overall=FAIL"
)

:: Test 3: Session count
call :countSessions
if !sessionCount! gtr 100 (
    set "results=!results!\"orphan_sessions\": {\"status\": \"WARN\", \"detail\": \"High session count: !sessionCount!\"}, "
    if "!overall!"=="PASS" set "overall=WARN"
) else (
    set "results=!results!\"orphan_sessions\": {\"status\": \"PASS\", \"detail\": \"Session count normal: !sessionCount!\"}, "
)

:: Test 4: Disk space (rough check via dir)
dir C:\ >nul 2>&1
if !errorlevel! equ 0 (
    set "results=!results!\"disk_space\": {\"status\": \"PASS\", \"detail\": \"C: drive accessible\"}, "
) else (
    set "results=!results!\"disk_space\": {\"status\": \"FAIL\", \"detail\": \"C: drive not accessible\"}, "
    set "overall=FAIL"
)

:: Write JSON status
echo { > "%statusFile%"
echo   "timestamp": "%timestamp%", >> "%statusFile%"
echo   "overall": "%overall%", >> "%statusFile%"
echo   "tests": { >> "%statusFile%"
echo     !results:~0,-2! >> "%statusFile%"
echo   } >> "%statusFile%"
echo } >> "%statusFile%"

:: Append to log
echo ## Health Check - %timestamp% >> "%logFile%"
echo. >> "%logFile%"
echo **Overall: %overall%** >> "%logFile%"
echo. >> "%logFile%"
echo | Test | Status | Detail | >> "%logFile%"
echo |------|--------|--------| >> "%logFile%"

:: Parse results for log table - simplified
for %%A in (!results!) do (
    echo %%A >> "%logFile%"
)

echo. >> "%logFile%"
echo --- >> "%logFile%"
echo. >> "%logFile%"

if "%overall%"=="FAIL" exit /b 1
exit /b 0

:countSessions
set "sessionCount=0"
if not exist "C:\Users\Karen\.openclaw\agents\main\sessions\*.jsonl" goto :eof
for %%F in ("C:\Users\Karen\.openclaw\agents\main\sessions\*.jsonl") do (
    set /a sessionCount+=1
)
goto :eof
