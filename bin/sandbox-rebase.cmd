@echo off
setlocal
rem Intake-aware clean start. --dry-run inventories; --intake-only --apply prepares and stops.
rem No flags prepares/resumes and previews matching. --apply installs an existing reviewed preview.
rem --replan can resume incomplete matching from verified intake and its saved measurements; never installs.
rem --resume-install --check/--apply verifies completed unpublished staging before reuse.
if "%~2"=="" (
  echo Usage: sandbox-rebase.cmd "SANDBOX\Working" "SANDBOX\Working\_sandbox-state\RUN" [--baseline working] [--dry-run ^| --intake-only --apply ^| --replan ^| --apply ^| --check ^| --undo]
  echo Completed unpublished stage: --resume-install --check, then --resume-install --apply
  echo Unowned legacy cast collisions: explicitly add --preserve-legacy-derivatives to check/apply
  echo Approved core trial: keep --cast-seeds core --record-core-protection on every step
  echo --profile fast^|lean^|full: FAST keeps originals and defers editing/944x1104; recovery is separate
  echo --regroup --cast-seeds core: member-first identity/appearance lifecycle, maintained stage reports
  echo --regroup --directed --directed-recipe NAME: explicit experimental directed mode; no default recipe
  echo --dry-run --core-selection-preview: writes a read-only JSON receipt and original-backed HTML candidate viewer; no face/model work
  exit /b 2
)
set "ST_REBASE_ROOT=%~1"
set "ST_REBASE_RUN=%~2"
set "ST_REBASE_ARGS="
shift /1
shift /1
:arguments
if "%~1"=="" goto run
set ST_REBASE_ARGS=%ST_REBASE_ARGS% %1
shift /1
goto arguments
:run
call "%~dp0_env.cmd"
%PY% tools\art\likeness.py --root "%ST_REBASE_ROOT%" clean-rebase --run-dir "%ST_REBASE_RUN%" %ST_REBASE_ARGS%
set "ST_REBASE_CODE=%errorlevel%"
rem Every successful matched step refreshes the run's recap page and the run index (none before matching exists).
if not "%ST_REBASE_CODE%"=="0" goto finish
echo %ST_REBASE_ARGS% | findstr /i /c:"--dry-run" /c:"--intake-only" >nul && goto finish
if not exist "%ST_REBASE_RUN%\run.json" goto finish
%PY% tools\art\likeness_library\rebase_recap.py "%ST_REBASE_RUN%"
set "ST_REBASE_CODE=%errorlevel%"
:finish
call "%~dp0_end.cmd" %ST_REBASE_CODE%
