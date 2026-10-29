@echo off
rem originals    rename every original after its folder, scale to 944x1104, prune copies whose original is gone, re-point chosen photos   (originals --dry-run previews; --only NAME for one folder)
call "%~dp0_env.cmd"
%PY% tools\art\originals.py --apply %*
call "%~dp0_end.cmd" %errorlevel%
