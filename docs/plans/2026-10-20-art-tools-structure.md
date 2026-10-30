# 2026-10-20: organize Python art tools by domain

**Status:** holding (Oct 30 scheduling; approved behavior-preserving scope retained)

**Resume gate:** a bounded extraction required by an approved implementation,
or explicit selection after library acceptance. Do not start package moves
while verifying the frozen sandbox engine and rollback.

## Oct 30: end-to-end complexity feedback ownership

- [ ] **P2 ai** E4 Audit maintainability of the complete current pipeline:
  named/unnamed Various intake, crop/masks/erase/composition, face comparison,
  grouping/core protection, placement, names/history and GUI evidence.
  Map module responsibilities, duplicated policy and state transitions;
  propose only measured, bounded simplifications with regression coverage,
  not a wholesale replacement while baseline installation is blocked.
  Consume the same accepted run's evidence from cast C6/C7 and intake I59;
  engine E4-E7/E13 owns scoring/protection/convergence tests, naming N12/N13
  owns rename/named intake, and face M1-M4 owns conditional second-model
  investigation. Trace loose unnamed versus asserted named arrivals and
  full-photo/core-only rebase with metadata-based name continuity without
  treating old names as identity seeds. Do not rerun or redefine those owners.

## Review and questions: 2026-10-22 16:26 -05:00

Retained independent structure plan, receiving Oct 20 self-healing H2.
Existing package extractions are progress, not closure of the remaining
high-coupling modules or a new behavior-change mandate.
No blocking design question for inventory; ask before a proposed extraction
requires visible CLI/default changes. General package/caller work belongs
here; engine E11 owns engine sunset/behavior acceptance, not duplicate moves.
Keep a bounded shared extraction list so one change is not counted twice.

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
- [x] **P2 ai** E1 Extract cached face embeddings, photo records, centered
  identity-space scoring, folder rules and clustering from the likeness CLI
  into `tools/art/likeness_library/engine.py`; retain the existing CLI and
  import surface and add focused tests to standard validation.
- [x] **P2 ai** E1b Move ComfyUI render indexing and photo/render identity-core
  composition into focused modules with regression tests; preserve the
  existing `likeness.py` public names.
- [ ] **P2 ai** E2 Continue extracting command responsibilities from
  `likeness.py` in bounded, behavior-preserving slices; map direct imports,
  launchers, and tests before moving each slice.
- [ ] **P2 ai** E2a Separate file mutation planning, history, apply, and undo
  from the command layer; preserve preview/apply and recovery semantics.
- [ ] **P2 ai** E2b Separate photo inspection and image operations (clean,
  review, crop, junk) with focused tests and unchanged CLI arguments.
- [ ] **P2 ai** E2c Separate people, artist, cast, and profile workflows;
  retain the existing gallery/originals import contracts while extracting.
- [ ] **P2 ai** E2d Reassess command ownership and remove compatibility names
  only after repository-wide callers and supported launchers are migrated.
- [ ] **P2 ai** E3 Reassess package naming after the CLI is no longer an
  importable top-level `likeness.py` module. Do not add a colliding
  `tools/art/likeness/` package before that migration and its compatibility
  path are tested.

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

**Oct 25 continuation:** intake processing is isolated in `intake_library`
(`models`, `subject`, `clutter`, `fill`, `pipeline`, `legacy`); old recipe support
does not generate images. Gallery evidence now shares a single DOM renderer in
`likeness_library/preparation_provenance.py`, rather than separate Review/Artist
implementations. Existing entry points and action semantics remain unchanged.
The [gallery continuation](2026-10-22-gallery-review-layout.md#oct-25-0913-intake-integration-and-next-safe-work)
preserves the user's cross-workstream request. Remaining high-coupling CLI and
image-operation extractions stay open; this is not a wholesale source move.

**Oct 22 extraction progress:** shared candidate planning is in
`likeness_library/planner.py`, policy resolution in `policy.py`, and verified
incoming move/apply/undo transactions in `maintenance.py`; clean-rebuild
filesystem boundaries remain in `clean_rebase.py`. Both primary processing
paths call this shared planning stack. This advances E2/E2a, but does not
complete the CLI extraction: legacy mutation commands, image operations and
library orchestration still need bounded migrations. Reconciliation command
orchestration now lives in `reconcile_command.py`; established action planning
and final-core checking live in `identity_maintenance.py`. The no-policy API
fallback is isolated in `legacy_reconciliation.py`, with unreachable policy
branches removed; normal rebase and routine callers do not use that adapter.
Package naming is unchanged to avoid shadowing
`likeness.py`. No competing `tools/art/likeness/` package was created.
Person-wide staged protection validation/state/history now lives in
`person_actions.py`, sharing the existing action CLI's backup, transaction
and undo boundary rather than duplicating filesystem execution.
Direct family-reference and name-collision reporting now lives in
`family_preview.py` with focused tests; `likeness.py` only registers the
read-only subcommand and dispatches to that module. It reuses the shared
frozen-core builder and existing recorded-name helpers, with no second
matching engine or mutation path.
Overview ranking and workflow-photo display selection now live in
`overview_photos.py`; `people_gallery.py` re-exports the existing ranking
helper and renders the selected thumbnails. Workflow pinning is display-only,
not identity evidence or a change to the ranking rules.
Content-bound rejected-identity decisions now live in `rejections.py`, shared
by candidate preparation, group/individual matching, staged action validation,
maintenance and merge guards. Unsupported legacy mutations and clean-rebuild
ID migration fail explicitly rather than discarding decisions. This bounded
module does not complete the remaining legacy-command extraction.
Whole-person staged rename validation, inventory snapshots and reversible
folder/history changes live in `person_rename.py`; the existing action CLI
retains backup, catalogue guarding and transaction ownership. This is separate
from legacy `likeness rename` and does not invoke photo normalization.
The likeness test hook now matches package descendants and both the catalogue
and engine-policy JSON/schema contracts. Its earlier end anchor incorrectly
skipped Python files; an explicit verbose hook run executes all 127 tests.

- `likeness_library/`: identity metadata and reusable likeness-library
  behavior: cached face embeddings, photo records, identity-space scoring,
  audits, review reports and manifest handling. The name avoids shadowing
  the existing top-level `likeness.py` import; it is distinct from the
  `library/` photo-normalization and synchronization domain.
- `tools/art/likeness.py`: the stable CLI and compatibility import surface.
  Its core image/identity engine has begun moving to `likeness_library/engine.py`;
  command orchestration remains here and will move only in tested slices.
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

The current CLI still coordinates many interdependent workflows. Its next
extraction order is mutation/recovery, image review/transforms, then people
and cast workflows. The existing `likeness_library` package owns shared
likeness behavior; `library_sync.py`, `library_backup.py`, and
`library_audit.py` are separate photo-library orchestration tools and remain
in place until their cross-import and launcher contracts are mapped. Do not
rename packages or move these tools just to make their names look uniform.

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


## Oct 30 source snapshot: pipeline_code_complexity.md

Source: `feedback/pipeline_code_complexity.md`. Coverage: E4. SHA-256: `bb2c7d66ffa0c1159918737a71fe63ef7a8e5e19c00c067055e389e8c0f928f7`.
Captured for planning; open tasks are not implementation acceptance.

<!-- markdownlint-disable MD013 MD009 -->
````text
I am curious after all the work we've done what we think about the code-complexity of the entire image processing pipeline - from the intake of new images in Various galleries, whether from Various/gallery or Various/[person name] (which is relatively untested), through the various stages of cropping, masking, erasing, and final composition. How maintainable and understandable is the code, and are there areas where we could simplify or refactor to reduce complexity without sacrificing functionality?

Then we need to look at the likeness process and how the code handles comparisons, similarity checks, and any adjustments made based on likeness. Are the functions modular and easy to follow, or are there areas where the logic could be streamlined? How well does the code integrate with the rest of the pipeline, and are there opportunities to reduce redundancy or improve clarity?

I know we have added complexity - but hope that we've also ensured that the pipeline flow from beginning to end is solid and doesn't need a major overhaul.  We still have more testing beyond the image processing with how the threshold for similarity and the rules around protecting core photos automatically, moving in/out photos based on the likeness score, assigning the images to a person, naming that person, etc...

We'll need to test the rename as well as the Various/[person name] intake path to ensure that images are correctly assigned, renamed, and processed through the pipeline without introducing errors or inconsistencies.

Also testing the rebase of the entire 100% photos assigned and only keeping core likness, but retaining names of persons without the core present based on meta-data about images and previous names, without forcing images to go into a previous name - but a core set of images with the previous name gives the person it's core again.

The whole point of that process is that some photos have leaked across persons through early bugs and issues, so the rebase is attempting to rebuild the cores and setup the future to assign the original names via the Various/[person name] when it's known and let the Various/gallery assign a new name for brand new set of images I don't have a names for and let the images land where they land.

I'm very pleased with the work on the intake and the series of steps we have done to clean up images and now it's onto the likeness and similarity comparison and we may need to add in those additional comparisons for border-line images, merging persons based on likeness scores, assigning family names and keeping original name history and ensuring overall that the GUI present all the information through a series of well integrated pages.
````
<!-- markdownlint-enable MD013 MD009 -->
