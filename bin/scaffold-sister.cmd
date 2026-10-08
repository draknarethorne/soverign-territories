@echo off
call "%~dp0_env.cmd"
if "%~1"=="" (
  echo Usage: scaffold-sister SLUG    e.g. scaffold-sister draknara   ^(builds the studio kit cards from data\art\_kits\SLUG.json; existing cards are kept^)
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\generators\scaffold_sister_studio.py --slug %~1
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
echo.
echo Next: refresh HERO   ^(prompts, workflows, deploy^)
call "%~dp0_end.cmd" 0
