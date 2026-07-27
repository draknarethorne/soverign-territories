# Contributing

Thanks for contributing to `soverign-territories`.

## Workflow

1. Create a branch from `main`.
2. Install repository-managed development tools.
3. Install Git hooks.
4. Keep changes focused and scoped.
5. Update docs/specs/scripts together when system rules change.
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

Run all local gates:

- `.venv\\Scripts\\pre-commit.exe run --all-files --show-diff-on-failure`

Run focused checks while iterating:

- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/Invoke-QualityChecks.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/Invoke-PrePushValidation.ps1`

Local hooks improve feedback speed. CI is the non-bypassable source of truth.

## Commit guidance

- Use descriptive commit messages.
- Prefer small, reviewable commits.
- Keep architecture, schema contracts, and tooling updates synchronized.

## Safety requirements

- Do not commit secrets or credentials.
- Use `.env` locally for sensitive values (never commit it).
- Validate schema and tooling changes before push.
