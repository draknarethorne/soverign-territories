@echo off
call "%~dp0_env.cmd"
if "%~1"=="" (
  echo Usage: refresh-group GROUP [--dry-run]    e.g. refresh-group angel-primes   ^(or sovereign-dawn, sovereign-territories, drakn-sisters^)
  echo Everything for one whole set: prompts, video prompts, Qwen and MiniMax workflows, deploy to the set's home workspace.
  call "%~dp0_end.cmd" 1
  exit /b 1
)
set "EXTRA=%~2"
echo == prompts
%PY% tools\generators\gen_prompt.py --group %~1 >nul
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
echo == video prompts
%PY% tools\generators\gen_animation.py >nul
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
echo == workflows
%PY% tools\workflows\comfy_workflows.py make --create --group %~1 %EXTRA%
%PY% tools\workflows\comfy_workflows.py make --create --engine minimax --group %~1 %EXTRA%
echo == deploy to the home workspace
%PY% tools\workflows\comfy_workflows.py deploy --group %~1 %EXTRA%
%PY% tools\workflows\comfy_workflows.py deploy --engine minimax --group %~1 %EXTRA%
call "%~dp0_end.cmd" %errorlevel%
