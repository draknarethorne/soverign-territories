# Contributing

Thanks for contributing to `soverign-territories`.

## Workflow

1. Create a branch from `main`.
2. Install repository-managed development tools.
3. Install Git hooks.
4. Keep changes focused and scoped.
5. Update docs/schemas/scripts together when system rules change.
6. Run local quality checks.
7. Ensure CI is green.
8. Open a pull request with a clear summary.

## Development setup

From repository root:

1. Install Python 3.12+
2. Create and activate a local virtual environment
3. Install pre-commit
4. Install Git hooks

Recommended commands:

- `python -m venv .venv`
- `.venv\\Scripts\\python.exe -m pip install --upgrade pip pre-commit`
- `.venv\\Scripts\\pre-commit.exe install --install-hooks`
- `.venv\\Scripts\\pre-commit.exe install --hook-type pre-push`

PowerShell contributors also need PSScriptAnalyzer:

- `Install-Module PSScriptAnalyzer -RequiredVersion 1.25.0 -Scope CurrentUser`

## Quality contract

Quality policy is documented in `docs/QUALITY-GATES.md`.

Run routine local checks (no unit or mutation suites):

- `cmd /c bin\check.cmd`

Request the deeper hook suites explicitly:

- `cmd /c bin\check.cmd --deep`

Routine commit hooks check hygiene and data validity. Push does not rerun
them. Unit and mutation hooks use the explicit `manual` stage; CI selects
dependency-relevant tests for branch/PR changes and full coverage for
main/manual acceptance or conservative infrastructure fallback.
Run focused tests for your changes
before committing, rather than relying on an automatic full-suite commit.

Run focused checks while iterating:

- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/Invoke-QualityChecks.ps1`
- `python tools/validators/validate_data.py` (schemas + card<->art link integrity)
- `cmd /c bin\validate.cmd --isolated --quick` (validator smoke mutations on a copy)
- `cmd /c bin\validate.cmd --changed HEAD --dry-run` (preview changed-work selection)
- `cmd /c bin\validate.cmd --changed HEAD --check` (run that selection)
- `cmd /c bin\validate.cmd --scope workflow --check` (explicit subsystem override)
- `cmd /c bin\validate.cmd --full` (full regressions and isolated mutations)

Replace `HEAD` with the branch-point SHA to include committed branch changes.
Test launchers route inherited temporary files under ignored repository `tmp`;
prefer them to bare test commands. `--quick` is now just isolated mutation
smoke coverage, not an implicit full regression run. See the
[quality contract](docs/QUALITY-GATES.md) for dependency/fallback rules.

CI runs on branch pushes and main-targeting PRs, and can also be dispatched
explicitly. A successful local commit
is not proof that CI ran or that branch protection is configured.

## Commit guidance

- Use descriptive commit messages.
- Prefer small, reviewable commits.
- Keep architecture, schema contracts, and tooling updates synchronized.

## Safety requirements

- Do not commit secrets or credentials.
- Use `.env` locally for sensitive values (never commit it).
- Validate schema and tooling changes before push.
