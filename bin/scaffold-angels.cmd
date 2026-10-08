@echo off
call "%~dp0_env.cmd"
rem scaffold-angels                 write the standard card set for all 20 angels (existing cards are kept)
rem scaffold-angels SLUG            one angel, e.g. scaffold-angels seraphine
rem scaffold-angels --alpha         only the two alpha test heroes (alpha/female, alpha/male) for trying other photos
rem scaffold-angels --coverage      report which library pieces the angels use; writes nothing
if "%~1"=="--alpha" (
  %PY% tools\generators\scaffold_angel_set.py --alpha
  call "%~dp0_end.cmd" %errorlevel%
  exit /b %errorlevel%
)
if "%~1"=="--coverage" (
  %PY% tools\generators\scaffold_angel_set.py --coverage
  call "%~dp0_end.cmd" %errorlevel%
  exit /b %errorlevel%
)
if "%~1"=="" (
  %PY% tools\generators\scaffold_angel_set.py --all
) else (
  %PY% tools\generators\scaffold_angel_set.py --slug %~1
)
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
echo.
echo Next: refresh-group angel-primes   ^(prompts, workflows, deploy^)
call "%~dp0_end.cmd" 0
