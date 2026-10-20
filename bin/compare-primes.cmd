@echo off
rem compare-primes   put the Prime renders of each hero side by side (Qwen and FireRed, normal flow and any configured alternate flow) and score how close each face is to the photo it started from
rem                  compare-primes.cmd [HERO ...] [--all-renders] [--out FILE.png]     reads the ComfyUI output folders; writes <work>\_reports\comparisons\primes\prime_compare.png
call "%~dp0_env.cmd"
%PY% tools\art\prime_compare.py %*
call "%~dp0_end.cmd" %errorlevel%
