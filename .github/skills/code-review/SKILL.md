---
name: code-review
description: "Use when reviewing Sovereign Territories code changes or a bounded part of the wider codebase for correctness, maintainability, test gaps, duplication and actionable technical debt."
---

# Code review and debt discovery

## Set the review boundary

Read [status](../../../docs/STATUS.md), the affected contracts and the
[planning agreement](../../../docs/plans/README.md). Establish the exact
revision, changed files or repository slice, expected behavior, existing
worktree changes and applicable test evidence. A review is read-only and
does not authorize runtime changes, a new milestone or deployment.

For a broad review, inventory active code, launchers, tests and relevant
documentation by domain; exclude `_archive` unless specifically requested.
Record the actual revision and which files/surfaces were reviewed. Work in
bounded slices, retaining a coverage map and unresolved slices; an inventory
or a list of largest files is not a completed review. Respect the
[existing debt owners](../../../docs/plans/2026-10-12-tooling-debt.md) and
[structure plan](../../../docs/plans/2026-10-20-art-tools-structure.md).

## Review behavior and structure

1. Trace requirements, callers, data ownership, launchers and side effects.
   Read the relevant implementation and tests, including failure, recovery,
   concurrency and boundary behavior where applicable. Use language
   intelligence and focused read-only checks when they settle a question.
2. Look for demonstrated correctness or data-loss risks, unsafe defaults,
   hidden errors, duplicated policy, stale contracts and missing tests. Review
   cohesion, oversized files and unnecessary complexity against real
   responsibilities and callers; file length alone is a triage signal, not
   proof of a defect or a reason to split at arbitrary line counts.
3. Prioritize concrete findings by impact and confidence. Give the relevant
   file and location, observable scenario, consequence and evidence; label
   hypotheses and untested areas. Distinguish current bugs from maintainability
   risks and proposed improvements. Do not claim a clean review of code not
   inspected or tests not run.
4. Fix a small, safe problem only when the current task authorizes it. Route
   a cohesive behavior-preserving extraction to
   [code refactoring](../code-refactoring/SKILL.md); use the security-review
   workflow when explicitly asked to find exploitable vulnerabilities.

Record significant unresolved debt with evidence, impact, owner, priority,
dependencies and a concrete next step in its existing owning plan. Reuse an
existing task before adding one; keep deferred work holding until selected.
Do not silently expand the current queue or mark a review or fix complete
from an inventory. Regenerate the queue after plan changes.
