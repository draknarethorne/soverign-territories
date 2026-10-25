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
echo   L  Photo library: sort new photos in Various, remove duplicates, rebuild all scaled images
echo   R  Photo review gallery (read-only Gallery and Review audit)
echo   G  Preview gallery upkeep (rename, padded/head/chest; no matching or writes)
echo   P  Preview sandbox image preparation comparisons (no source or identity changes)
echo   J  Preview early Junk quarantine from a completed preparation report (no moves)
echo   T  Preview artist-only likeness grouping in the sandbox (shared engine, no moves)
echo   V  Preview separate Artist gallery pages (no matching or source changes)
echo   C  Photo library check (read only: anything waiting?)
echo   B  Back up the photo library and ComfyUI inputs
echo   X  Clean sandbox rebase (preview or verify; apply separately after reviewing the plan)
echo   S  Style audit (which art wording leans illustrated)
echo   H  Help (all scripts)
echo   Q  Quit
set "CH="
set /p "CH=Choice: "
if /i "%CH%"=="Q" exit /b 0
if /i "%CH%"=="H" call "%~dp0help.cmd" & pause & goto menu
if /i "%CH%"=="S" call "%~dp0style-audit.cmd" & pause & goto menu
if /i "%CH%"=="L" call "%~dp0library.cmd" & pause & goto menu
if /i "%CH%"=="R" call "%~dp0people-gallery-review.cmd" & pause & goto menu
if /i "%CH%"=="G" call "%~dp0people-gallery.cmd" --dry-run & pause & goto menu
if /i "%CH%"=="C" call "%~dp0library-check.cmd" & pause & goto menu
if /i "%CH%"=="B" goto backup
if /i "%CH%"=="X" goto sandboxrebase
if /i "%CH%"=="P" goto preparation
if /i "%CH%"=="J" goto preparationjunk
if /i "%CH%"=="T" goto artistlikeness
if /i "%CH%"=="V" goto artistgallery
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
:preparation
set "ROOT="
set "RUN="
set /p "ROOT=Sandbox Working absolute path: "
set /p "RUN=Comparison run absolute path inside Working\_reports\preparation: "
call "%~dp0prepare-images.cmd" --root "%ROOT%" --out "%RUN%" --dry-run
pause
goto menu
:preparationjunk
set "ROOT="
set "RUN="
set /p "ROOT=Sandbox Working absolute path: "
set /p "RUN=Existing preparation run absolute path: "
call "%~dp0prepare-images.cmd" --root "%ROOT%" --out "%RUN%" --quarantine-junk --dry-run
pause
goto menu
:artistlikeness
set "ROOT="
set /p "ROOT=Sandbox Working absolute path: "
call "%~dp0likeness-artists.cmd" --root "%ROOT%" --dry-run group --singles
pause
goto menu
:artistgallery
set "ROOT="
set /p "ROOT=Sandbox Working absolute path: "
call "%~dp0artists-gallery.cmd" --root "%ROOT%" --dry-run
pause
goto menu
:sandboxrebase
set "ROOT="
set "RUN="
set /p "ROOT=Sandbox Working absolute path: "
set /p "RUN=New run directory inside Working (or existing run to verify): "
set "VERIFY="
set /p "VERIFY=Verify existing run only? (y/n): "
if /i "%VERIFY%"=="y" (
  call "%~dp0sandbox-rebase.cmd" "%ROOT%" "%RUN%" --check
) else (
  call "%~dp0sandbox-rebase.cmd" "%ROOT%" "%RUN%" --dry-run
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
:backup
set "APPLY="
set "FLAG="
set /p "APPLY=Create the snapshot now? (n = preview only): "
if /i "%APPLY%"=="y" set "FLAG=--apply"
call "%~dp0library-backup.cmd" %FLAG%
pause
goto menu
