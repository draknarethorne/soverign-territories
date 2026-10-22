@echo off
rem Fresh cast-seeded rebuild; preview, replan, apply, verify, or undo the saved run.
if "%~2"=="" (
  echo Usage: sandbox-rebase.cmd "SANDBOX\Working" "SANDBOX\Working\_sandbox-state\RUN" [--dry-run ^| --replan ^| --apply ^| --check ^| --undo]
  exit /b 2
)
call "%~dp0_env.cmd"
%PY% tools\art\likeness.py --root "%~1" clean-rebase --run-dir "%~2" %3 %4 %5 %6 %7 %8 %9
call "%~dp0_end.cmd" %errorlevel%
