@echo off
setlocal
call "%~dp0_env.cmd"
%PY% tools\art\likeness_character_packet.py %*
call "%~dp0_end.cmd" %errorlevel%
