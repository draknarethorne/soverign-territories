---
name: test-engineering
description: "Use when designing, selecting, running or reviewing tests and validation for Sovereign Territories changes, refactors, failure paths and acceptance evidence."
---

# Test engineering and validation

Read the affected task, contracts, [quality gates](../../../docs/guidelines/QUALITY-GATES.md)
and [launcher help](../../../bin/help.cmd). Establish the observable
requirement, inputs/outputs, state transitions, existing coverage, permitted
roots and available toolchain. Distinguish fixture proof from installed
behavior, real browser evidence and human acceptance.

## Build focused evidence

1. Reproduce the reported failure or establish a behavior baseline before a
   fix/refactor when practical. Add a small regression or characterization
   test that would catch the defect or unsafe extraction; avoid tests that
   merely repeat implementation details or trivial constants.
2. Cover relevant edge cases, invalid input and failure/recovery paths.
   For filesystem or transaction changes, exercise isolation, expected
   before/after content, interrupted steps and rollback without touching live
   libraries. Use existing fixtures, helpers and deterministic inputs; do not
   weaken assertions or hide failures to make a run green.
3. Run supported launchers and preview change selection first. Start with
   the smallest tests covering the change; expand to shared consumers,
   isolated mutation tests or full regression when the selected quality
   contract requires it. Register new test modules in the established
   launcher/inventory rather than creating duplicate runners.
4. Put disposable test outputs in ignored repository `tmp/`; preserve
   durable run evidence separately. Do not launch competing heavy tests
   against a live frozen run, install dependencies speculatively, or use
   Production/shared workspaces as fixtures.
5. Record exact commands, results, skips, environment and untested gates.
   A mocked collaborator does not prove its real transaction; a passing
   fixture, static page or local run does not prove browser behavior,
   production readiness, remote CI or visual/human acceptance.

Use [GUI validation](../gui-validation/SKILL.md) for live browser checks and
[diagnostics and tuning](../diagnostics-tuning/SKILL.md) for failures and
comparable performance experiments.
