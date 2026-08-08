@echo off
set timestamp=%date% %time%
set logFile=C:\Users\Karen\.openclaw\workspace\memory\health-checks.log

:: Test 1: Can we write a file?
echo test > C:\Users\Karen\.openclaw\workspace\.health-tmp.txt
if exist C:\Users\Karen\.openclaw\workspace\.health-tmp.txt (
    set execStatus=PASS
    set execDetail=File write working
    del C:\Users\Karen\.openclaw\workspace\.health-tmp.txt
) else (
    set execStatus=FAIL
    set execDetail=File write failed
)

:: Test 2: Node config exists?
if exist C:\Users\Karen\.openclaw\node.json (
    set nodeStatus=PASS
    set nodeDetail=node.json exists
) else (
    set nodeStatus=FAIL
    set nodeDetail=node.json missing
)

:: Test 3: Count sessions
call :countSessions
if %sessionCount% gtr 100 (
    set orphanStatus=WARN
    set orphanDetail=High count: %sessionCount%
) else (
    set orphanStatus=PASS
    set orphanDetail=Count OK: %sessionCount%
)

:: Log results
echo ## Health Check - %timestamp% >> %logFile%
echo. >> %logFile%
echo exec_write: %execStatus% - %execDetail% >> %logFile%
echo node_config: %nodeStatus% - %nodeDetail% >> %logFile%
echo orphan_sessions: %orphanStatus% - %orphanDetail% >> %logFile%
echo --- >> %logFile%
echo. >> %logFile%

exit /b 0

:countSessions
set sessionCount=0
for %%F in (C:\Users\Karen\.openclaw\agents\main\sessions\*.jsonl) do set /a sessionCount+=1
goto :eof
