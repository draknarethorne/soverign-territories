@echo off
call "%~dp0_env.cmd"
set "HERE=%~dp0"
set "NAME=%~1"
if "%NAME%"=="" goto usage
set "REST="
shift
:collect
if "%~1"=="" goto run
set "REST=%REST% %1"
shift
goto collect
:run
if /i "%NAME%"=="identity" %PY% tools\art\identity_audit.py%REST% & goto done
if /i "%NAME%"=="negation" %PY% tools\art\negation_audit.py%REST% & goto done
if /i "%NAME%"=="library"  %PY% tools\art\library_audit.py%REST% & goto done
if /i "%NAME%"=="style"    %PY% tools\art\style_audit.py%REST% & goto done
if /i "%NAME%"=="codex"    %PY% tools\art\audits\codex_drift.py%REST% & goto done
if /i "%NAME%"=="all" goto all
echo Unknown audit '%NAME%'.
:usage
echo Usage: audit NAME [options]
echo    identity   every angel, sister and bound hero: colours defined and in the Prime prompt, build in the Bare prompt, no bulky wording on women   ^(--check fails on a problem^)
echo    negation   negations in the positive prompts, which a model reads as the thing named   ^(--check, --review^)
echo    library    thin library folders that many cards lean on, and pieces no card uses   ^(--scope S^)
echo    style      wording and style checks across the art data
echo    codex      the roster pages in docs\codex\heroes against the cards and identity JSON   ^(--check^)
echo    all        identity, negation and codex in check mode ^(what validate runs^)
call "%HERE%_end.cmd" 1
exit /b 1
:all
%PY% tools\art\identity_audit.py --check
if errorlevel 1 goto done
%PY% tools\art\negation_audit.py --no-sources --check
if errorlevel 1 goto done
%PY% tools\art\audits\codex_drift.py --check
:done
call "%HERE%_end.cmd" %errorlevel%
