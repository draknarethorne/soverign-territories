@echo off
call "%~dp0_env.cmd"
rem The fast code tests: workflow tool (homes, accepts, zz_ guards) and the generator (piece extends).
%PY% tools\workflows\test_comfy_workflows.py
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\generators\test_gen_prompt_extends.py
call "%~dp0_end.cmd" %errorlevel%
