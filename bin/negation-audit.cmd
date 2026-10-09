@echo off
call "%~dp0_env.cmd"
rem negation-audit            find negations (do not, never, no X, not Y) in the positive prompts: a model reads them as the thing named
rem negation-audit --check    exit 1 if a command or flip-risk phrase is left (validate.cmd runs this)
rem negation-audit --review   also list the generic no/not/nothing/without phrases
%PY% tools\art\negation_audit.py %*
call "%~dp0_end.cmd" %errorlevel%
