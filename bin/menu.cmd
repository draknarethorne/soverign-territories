@echo off
rem Double-click menu for the common operations. Each choice runs one of the scripts in this folder.
:menu
echo.
echo  Sovereign Territories
echo   1  Refresh a hero (prompts, workflows, deploy to her home workspace)
echo   2  Refresh a whole set (angel-primes, sovereign-dawn ...)
echo   3  Set up a workspace (deploy its sets, tidy, cleanup, status)
echo   4  Publish a temporary copy to another workspace
echo   5  Clean up a workspace
echo   6  Status
echo   7  Workspaces
echo   8  Validate
echo   9  Refresh FireRed for a hero
echo   A  Animate a hero (video prompts, workflows, deploy)
echo   S  Style audit (which art wording leans illustrated)
echo   H  Help (all scripts)
echo   Q  Quit
set "CH="
set /p "CH=Choice: "
if /i "%CH%"=="Q" exit /b 0
if /i "%CH%"=="H" call "%~dp0help.cmd" & pause & goto menu
if /i "%CH%"=="S" call "%~dp0style-audit.cmd" & pause & goto menu
if "%CH%"=="2" goto group
if "%CH%"=="3" goto setup
if "%CH%"=="4" goto publish
if "%CH%"=="5" goto cleanup
if "%CH%"=="6" call "%~dp0status.cmd" & pause & goto menu
if "%CH%"=="7" call "%~dp0workspaces.cmd" & pause & goto menu
if "%CH%"=="8" call "%~dp0validate.cmd" & pause & goto menu
set "SCRIPT="
if "%CH%"=="1" set "SCRIPT=refresh.cmd"
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
:group
set "GRP="
set "DRY="
set /p "GRP=Set (angel-primes, sovereign-dawn, sovereign-territories, drakn-sisters): "
set /p "DRY=Dry run first? (y/n): "
set "FLAG="
if /i "%DRY%"=="y" set "FLAG=--dry-run"
call "%~dp0refresh-group.cmd" "%GRP%" %FLAG%
pause
goto menu
:setup
set "WS="
set "APPLY="
set /p "WS=Workspace (for example Angel Primes): "
set /p "APPLY=Apply (n = preview only)? (y/n): "
set "FLAG="
if /i "%APPLY%"=="y" set "FLAG=--apply"
call "%~dp0setup-workspace.cmd" "%WS%" %FLAG%
pause
goto menu
:publish
set "HERO="
set "WS="
set "DRY="
set /p "HERO=Hero (for example Drakness): "
set /p "WS=Workspace that accepts the set (for example Sovereign Territories): "
set /p "DRY=Dry run first? (y/n): "
set "FLAG="
if /i "%DRY%"=="y" set "FLAG=--dry-run"
call "%~dp0publish.cmd" "%HERO%" "%WS%" "" %FLAG%
pause
goto menu
:cleanup
set "WS="
set "APPLY="
set /p "WS=Workspace to clean up (for example Angel Primes): "
set /p "APPLY=Apply (n = preview only)? (y/n): "
set "FLAG="
if /i "%APPLY%"=="y" set "FLAG=--apply"
call "%~dp0cleanup.cmd" "%WS%" %FLAG%
pause
goto menu
