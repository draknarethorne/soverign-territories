@echo off
call "%~dp0_env.cmd"
if /i "%~1"=="--isolated" (
  %PY% tools\validators\test_validate_data.py --isolated %2
  exit /b
)
rem validate            schema/link checks, all offline regression modules and audits
rem validate --quick    also a short validator self-test, one case per kind of check (under 2 minutes)
rem validate --full     also the whole validator self-test (about 6 minutes; it changes real files in place and undoes each change)
%PY% tools\validators\validate_data.py
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\workflows\test_comfy_workflows.py
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% -m unittest tools.workflows.test_reference_rendering tools.workflows.test_reference_execution tools.workflows.test_reference_gallery tools.workflows.test_reference_outputs tools.workflows.test_reference_comparison tools.workflows.test_backdrop
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\workflows\test_finals.py
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\art\test_originals.py
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\art\test_gallery_maintenance.py
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\art\test_image_preparation.py
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% -m unittest tools.art.test_clean_preparation tools.art.test_retained_preparation
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% -m unittest tools.art.test_eraser_benchmark tools.art.test_intake_sequence tools.art.test_overlay_reference_review tools.art.test_overlays
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\art\test_preparation_provenance.py
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\art\test_duplicates.py
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\art\test_library_backup.py
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\art\test_library_sync.py
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\art\test_likeness.py
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% -m unittest discover -s tools/art/likeness_library/tests -p test_*.py
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\art\test_people.py
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\art\test_people_gallery.py
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\art\test_artists_gallery.py
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\art\test_prime_compare.py
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\workflows\test_finals_commands.py
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\workflows\test_templates.py
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\workflows\test_video_templates.py
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\workflows\test_cli_surface.py
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% -m unittest tools.generators.test_gen_prompt_extends tools.generators.test_deluxe_reference tools.validators.test_validation_isolation tools.validators.test_quality_gates
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% -m unittest tools.art.test_dragon_companions tools.art.test_rename_originals_storage tools.art.test_storage_retention tools.art.test_temporary_storage
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\art\test_negation_audit.py
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\art\negation_audit.py --no-sources --check
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\art\test_identity_audit.py
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\art\identity_audit.py --check
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\art\test_todo_report.py
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\art\audits\tests\test_codex_drift.py
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\art\audits\codex_drift.py --check
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
if /i "%~1"=="--quick" %PY% tools\validators\test_validate_data.py --quick
if /i "%~1"=="--full" %PY% tools\validators\test_validate_data.py
call "%~dp0_end.cmd" %errorlevel%
