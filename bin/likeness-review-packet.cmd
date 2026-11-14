@echo off
setlocal
call "%~dp0_env.cmd"
%PY% tools\art\likeness_review_packet.py %*
call "%~dp0_end.cmd" %errorlevel%
