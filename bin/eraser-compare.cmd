@echo off
rem eraser-compare   same-mask eraser A/B (saved LaMa vs OpenCV Telea/NS) from an existing preparation report; preview by default
call "%~dp0_env.cmd"
%PY% tools\art\eraser_benchmark.py %*
call "%~dp0_end.cmd" %errorlevel%
