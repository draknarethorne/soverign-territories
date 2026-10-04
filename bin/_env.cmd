@echo off
rem Shared setup for the bin scripts: go to the repo root and pick a Python launcher.
pushd "%~dp0.." >nul
set "PY=python"
where python >nul 2>nul
if errorlevel 1 set "PY=py -3"
