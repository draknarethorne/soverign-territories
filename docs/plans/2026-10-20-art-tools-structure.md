# 2026-10-20: organize Python art tools by domain

**Status:** active (approved Oct 20, 2026; incremental and risk-gated)

## Purpose

Gradually organize `tools/art/` into discoverable domain packages as work is
done, without breaking supported commands, tests, imports, or user workflows.
This plan covers file placement and test layout; it does not authorize a
behavior-changing rewrite or a bulk move of every script.

## Decisions and constraints

| Topic | Direction |
| --- | --- |
| User entry points | Keep `bin/*.cmd` as the stable commands and update them whenever an implementation path moves. |
| Direct script references | Inventory imports, tests, docs, hooks and automation before each move; update all known references or retain a justified compatibility shim. |
| Migration scope | Move related, low-risk code and tests together when the change is bounded and test-covered. Leave high-coupling modules in place until their import and CLI contracts are understood. |
| Existing tools | Preserve behavior and command arguments. This is organization, not an all-at-once refactor. |
| Data and schemas | Keep data under `data/` and validator entry points under `tools/validators/`; organize their tests only when that is independently safe. |
| Package names | Avoid collisions with existing top-level modules. The metadata package is `tools/art/likeness_library/`, not `tools/art/likeness/`, because `likeness.py` already owns the `likeness` import name. |

## Incremental work

- [x] **P1 ai** A1 Inventory art scripts, imports, direct Python references,
  tests, hooks and `bin/*.cmd` entry points; record coupling and test coverage.
- [x] **P1 ai** A2 Propose a domain layout that groups related tools without
  changing command behavior or moving data out of its existing homes.
- [x] **P1 ai** B1 Place the new likeness metadata module and focused tests in
  `tools/art/likeness_library/`; register the focused test in
  `bin/validate.cmd` and pre-commit.
- [x] **P2 ai** C1 Move the next well-bounded art subsystem together with its
  tests, updating launchers and direct references in the same change.
- [ ] **P2 ai** C2 Add or preserve compatibility entry points only where
  callers outside the repository need them; do not add wrappers speculatively.
- [ ] **P2 ai** D1 Keep a reviewed inventory of modules deferred for coupling,
  missing tests, or unsafe path assumptions; revisit them as related work
  creates a safe migration opportunity.
- [ ] **P2 ai** D2 Verify the documented `bin/*.cmd` commands and relevant
  tests after each move; update tool documentation with the new locations.

## Initial inventory

The first static inventory found 32 top-level art Python files, 29 imports
between them, and 19 `bin/*.cmd` launchers that invoke art scripts. The
references also reach validators, tests, runbooks and active plans. The
likeness, originals, people-gallery, screens and library-sync tools form a
connected cluster; moving that cluster wholesale would be a high-risk change.
The metadata package was the first isolated slice. The codex roster audit was
the next: its implementation and tests now live under `tools/art/audits/`, and
its direct launchers, validator entry point, pre-commit hook and current
documentation use the new paths. Later slices should move one subsystem at a
time with its launcher and all known references updated together.

## Initial package map

- `likeness_library/`: identity metadata and, as phases deliver them, core
  audits, review reports and manifest handling. Keep the existing
  `tools/art/likeness.py` entry point untouched until its planned extraction is
  separately tested.
- `library/`: original-photo normalization, duplicate detection, backup and
  library sync. These have shared filesystem and recovery behavior, so move
  them together only after their path and import contracts are mapped.
- `people_management/`: person indexing, People Gallery, screen/crop helpers and their
  tests. These depend on both likeness and original-photo behavior.
- `audits/`: independent art/data audits and their tests, moved one tool at a
  time with the validator and launchers updated.
- Keep specialized standalone tools at their current paths until their
  coupling and public references justify a package.

## Safety and acceptance

- No user photo, workflow, prompt or generated asset is moved as part of Python
  source organization.
- Every move preserves command arguments, default behavior and relevant
  generated outputs unless an explicitly reviewed behavior change is separately
  approved.
- Existing imports and direct script calls are either updated, tested, or
  preserved through a small compatibility entry point.
- The relevant `.cmd` launchers and focused test suites pass after each
  increment; broader suites run when the touched surface warrants them.
- The final inventory distinguishes completed moves from deliberately
  deferred high-risk modules.

## Raw user feedback

Also if we want to move the tests into a more dedicated directory and also move files into directories under the tools/art - i.e. tools/art/likeness that's fine to give some structure to the tools/art directory as it will grow.  Basically you have control of how to make this work with best practices for .py code as well.  Just more freedom you have.

As you add structure - I give you freedom to eventually migrate all existing .py files into the proper structure as part of this work - at least any we are working on today and are "not risky" to move around.  We can start another plan and write that up for remaining work that you choose not to take on in the structuring efforts - but I like what you have done so far.  Makes things cleaner from looking at them.  As long as the .cmd files are there to execute the tools - we should be lessening the risk as we move things.  Just more feedback - so keep on going with the plan and update it as we make these on-the-fly decisions.

If we can do the work now and it makes sense - don't defer.  I didn't mean to imply we NEEDED to wait - just you use your judgement on the risk of moving exieting files around.
