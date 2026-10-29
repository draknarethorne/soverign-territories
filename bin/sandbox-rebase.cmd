@echo off
setlocal
rem Intake-aware clean start. --dry-run inventories; --intake-only --apply prepares and stops.
rem No flags prepares/resumes and previews matching. --apply installs an existing reviewed preview.
rem --replan can resume incomplete matching from verified intake and its saved measurements; never installs.
if "%~2"=="" (
  echo Usage: sandbox-rebase.cmd "SANDBOX\Working" "SANDBOX\Working\_sandbox-state\RUN" [--baseline working] [--dry-run ^| --intake-only --apply ^| --replan ^| --apply ^| --check ^| --undo]
  exit /b 2
)
set "ST_REBASE_ROOT=%~1"
set "ST_REBASE_RUN=%~2"
set "ST_REBASE_ARGS="
shift /1
shift /1
:arguments
if "%~1"=="" goto run
set ST_REBASE_ARGS=%ST_REBASE_ARGS% %1
shift /1
goto arguments
:run
call "%~dp0_env.cmd"
%PY% tools\art\likeness.py --root "%ST_REBASE_ROOT%" clean-rebase --run-dir "%ST_REBASE_RUN%" %ST_REBASE_ARGS%
call "%~dp0_end.cmd" %errorlevel%
