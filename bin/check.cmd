@echo off
call "%~dp0_env.cmd"
rem Every commit hook. Uses pre-commit when it is installed; otherwise runs the same checks directly.
%PY% -m pre_commit --version >nul 2>nul
if not errorlevel 1 (
  %PY% -m pre_commit run --all-files
  call "%~dp0_end.cmd" %errorlevel%
  exit /b %errorlevel%
)
echo pre-commit is not installed ^(pip install pre-commit^); running the equivalent checks directly.
%PY% tools\validators\validate_data.py
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\workflows\test_comfy_workflows.py
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\generators\test_gen_prompt_extends.py
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\validators\test_validate_data.py
call "%~dp0_end.cmd" %errorlevel%
