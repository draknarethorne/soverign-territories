@echo off
rem Double-click menu for the common operations. Each choice runs one of the scripts in this folder.
:menu
echo.
echo  Sovereign Territories
echo   1  Refresh DEV for a hero (prompts, workflows, deploy)
echo   2  Deploy to DEV
echo   3  Deploy to UAT
echo   4  Promote DEV to UAT (move)
echo   5  Promote UAT to PROD (move)
echo   6  Status
echo   7  Workspaces
echo   8  Validate
echo   9  Refresh FireRed for a hero (prompts, workflows, deploy)
echo   A  Animate a hero (video prompts, workflows, deploy)
echo   H  Help (all scripts)
echo   Q  Quit
set "CH="
set /p "CH=Choice: "
if /i "%CH%"=="Q" exit /b 0
if /i "%CH%"=="H" call "%~dp0help.cmd" & pause & goto menu
if "%CH%"=="6" call "%~dp0status.cmd" & pause & goto menu
if "%CH%"=="7" call "%~dp0workspaces.cmd" & pause & goto menu
if "%CH%"=="8" call "%~dp0validate.cmd" & pause & goto menu
set "SCRIPT="
if "%CH%"=="1" set "SCRIPT=refresh-dev.cmd"
if "%CH%"=="2" set "SCRIPT=deploy-dev.cmd"
if "%CH%"=="3" set "SCRIPT=deploy-uat.cmd"
if "%CH%"=="4" set "SCRIPT=promote-uat.cmd"
if "%CH%"=="5" set "SCRIPT=promote-prod.cmd"
if "%CH%"=="9" set "SCRIPT=refresh-firered.cmd"
if /i "%CH%"=="A" set "SCRIPT=animate.cmd"
if not defined SCRIPT goto menu
set "HERO="
set "STG="
set /p "HERO=Hero (for example Draknara): "
set /p "STG=Stage (poses, head, scene, hair, motion, armor, clothing, studio; blank for all): "
set "DRY="
set /p "DRY=Dry run first? (y/n): "
set "FLAG="
if /i "%DRY%"=="y" set "FLAG=--dry-run"
if "%STG%"=="" (
  call "%~dp0%SCRIPT%" "%HERO%" "" %FLAG%
) else (
  call "%~dp0%SCRIPT%" "%HERO%" "%STG%" %FLAG%
)
pause
goto menu
