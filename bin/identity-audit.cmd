@echo off
call "%~dp0_env.cmd"
rem identity-audit            check every angel, sister and bound hero: hair, eye and skin colour defined and carried by the Prime prompt, the Bare prompt applies the build, female angels are slender
rem identity-audit --check    exit 1 on any problem (validate.cmd runs this)
%PY% tools\art\identity_audit.py %*
call "%~dp0_end.cmd" %errorlevel%
