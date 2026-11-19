@echo off
rem Normal profile-based intake. Preview by default; mutation requires explicit --apply.
call "%~dp0_env.cmd"
set "MODE=preview"
for %%A in (%*) do (
  if /i "%%~A"=="--apply" set "MODE=apply"
  if /i "%%~A"=="--dry-run" set "MODE=preview"
  if /i "%%~A"=="--check" set "MODE=check"
  if /i "%%~A"=="--undo" set "MODE=undo"
)
if /i "%MODE%"=="preview" (
  %PY% tools\art\likeness_library\normal_import.py --dry-run %*
) else (
  %PY% tools\art\likeness_library\normal_import.py %*
)
set "RC=%errorlevel%"
call "%~dp0_end.cmd" %RC%
exit /b %RC%
