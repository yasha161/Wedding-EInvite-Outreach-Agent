@echo off
cd /d "%~dp0"
set BATCH_NAME=%1
if "%BATCH_NAME%"=="" set BATCH_NAME=night

echo ======================================================== >> leads\wedding_automation.log
echo [%DATE% %TIME%] Starting Scheduled Wedding Batch: %BATCH_NAME% >> leads\wedding_automation.log
echo ======================================================== >> leads\wedding_automation.log

python wedding_agent.py --batch %BATCH_NAME% --send --max 15 >> leads\wedding_automation.log 2>&1

echo [%DATE% %TIME%] Finished Wedding Batch: %BATCH_NAME% >> leads\wedding_automation.log
echo. >> leads\wedding_automation.log
