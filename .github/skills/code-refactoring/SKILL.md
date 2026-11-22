---
name: code-refactoring
description: "Use when cleaning up or reorganizing Sovereign Territories code, reducing technical debt, extracting cohesive modules or splitting large files while preserving behavior."
---

# Safe cleanup and refactoring

Read [status](../../../docs/STATUS.md), the selected task and the
[planning agreement](../../../docs/plans/README.md), the applicable domain
contract, [quality gates](../../../docs/guidelines/QUALITY-GATES.md) and
[structure plan](../../../docs/plans/2026-10-20-art-tools-structure.md).
Check for dirty files, active writers and frozen code/input bindings. The
user's preference for cleanup is not permission to change product rules,
Production, shared workspaces or an unrelated holding backlog.

## Improve the code being touched

1. Inspect the existing design and prior helpers before adding logic. While
   implementing a task, remove tightly coupled duplication and improve names
   or organization when the improvement is safe, tested and within scope.
   Do not keep adding unrelated responsibilities to an already large module.
2. For a large touched file, identify cohesive responsibilities and an
   extraction seam. Split a bounded slice into the appropriate existing domain
   package when its interfaces and behavior can be preserved and tested.
   Otherwise record a concrete extraction with owner, risk, missing evidence
   and next gate in the existing plan. Line count alone does not choose the
   boundary or justify a sweeping rewrite.
3. Before moving code, map imports and public/patchable names, direct-script
   execution, launchers, tests, docs, schemas, persisted paths and recovery
   semantics. Establish behavior with existing or focused characterization
   tests, including error and rollback paths. Preserve supported callers and
   add a compatibility entry point only when a real caller needs it.
4. Move one cohesive unit with its callers, tests and directly affected docs;
   preserve observable CLI arguments, output, logging, ordering, state and
   failures. Avoid circular imports, duplicated implementations and
   success-shaped fallbacks. Separate intentional behavior changes from the
   refactor and obtain their required approval.
5. Run the affected supported launcher and smallest tests that prove parity;
   expand for shared consumers or the quality contract. Report what was
   verified and what remains installed- or human-unverified. Use
   [test engineering](../test-engineering/SKILL.md) for proof and
   [code review](../code-review/SKILL.md) to identify further debt.

If a safe extraction cannot be proved, preserve the current behavior and
record the blocker instead of moving code merely to reduce file size. Never
change a live run's hash-bound modules or overwrite concurrent work.
