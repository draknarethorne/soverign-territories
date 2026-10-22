@echo off
call "%~dp0_env.cmd"
rem validate            schema and link checks + the workflow tool tests (fast)
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
%PY% tools\art\likeness_library\tests\test_metadata.py
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\art\likeness_library\tests\test_engine.py
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\art\likeness_library\tests\test_identity.py
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% -m unittest tools.art.likeness_library.tests.test_clean_rebase tools.art.likeness_library.tests.test_policy tools.art.likeness_library.tests.test_reconciliation tools.art.likeness_library.tests.test_review_gallery tools.art.likeness_library.tests.test_maintenance tools.art.likeness_library.tests.test_identity_maintenance tools.art.likeness_library.tests.test_actions tools.art.likeness_library.tests.test_family_preview tools.art.likeness_library.tests.test_photo_retirement tools.art.likeness_library.tests.test_rejections tools.art.likeness_library.tests.test_person_rename
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\art\test_people.py
%PY% tools\art\test_people_gallery.py
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
%PY% tools\generators\test_gen_prompt_extends.py
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
