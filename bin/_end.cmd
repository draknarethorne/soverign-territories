@echo off
rem Shared teardown: return to the original folder and pass the exit code on.
popd >nul
exit /b %1
