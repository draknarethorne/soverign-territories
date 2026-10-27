@echo off
rem Intake-aware clean start. --dry-run inventories; --intake-only --apply prepares and stops.
rem No flags prepares/resumes and previews matching. --apply installs an existing reviewed preview.
rem --replan can resume incomplete matching from verified intake and its saved measurements; never installs.
if "%~2"=="" (
  echo Usage: sandbox-rebase.cmd "SANDBOX\Working" "SANDBOX\Working\_sandbox-state\RUN" [--dry-run ^| --intake-only --apply ^| --replan ^| --apply ^| --check ^| --undo]
  exit /b 2
)
call "%~dp0_env.cmd"
%PY% tools\art\likeness.py --root "%~1" clean-rebase --run-dir "%~2" %3 %4 %5 %6 %7 %8 %9
call "%~dp0_end.cmd" %errorlevel%
