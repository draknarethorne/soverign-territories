@echo off
call "%~dp0_env.cmd"
rem denoise            show the denoise every generated workflow should start at;  denoise --reset applies it (repo and workspaces, backed up first)
rem denoise --reset -w "Angel Primes"   the repo, but only that workspace; a denoise you set by hand is kept (add --force to overwrite)
%PY% tools\workflows\comfy_workflows.py denoise %*
call "%~dp0_end.cmd" %errorlevel%
