# 2026-10-22: manual library actions and scenario testing

**Status:** active (manual action completion and scenario acceptance remain)

## Review and questions: 2026-10-22 16:26 -05:00

Verified successor for the unfinished Oct 20/21 manual-action work.
The [curation contract](../art/likeness-curation-contract.md) retains metadata,
stable-photo continuity, core/protection distinctions, Review/Reject,
retirement and recovery rationale. The manifest schema, not an old delivery
sketch, defines the unified `actions` payload.
Before A2 ask what whole-person rejection should mean; don't invent it from
photo rejection. Before protected unlock implementation, layout L6 must settle
whether relocking retains, disables or cancels staged actions.
Before A9 ask whether explicit core exclusion needs a separate control after
explaining anchor/protection behavior. Production remains a separate gate.

## Scope

Own manual identity/photo action behavior, manifest wiring, safe execution,
recovery, report refresh and user scenario testing. Not engine calibration,
family design, GUI formatting or broad ComfyUI execution.

The [command guide](../art/likeness.md#testing-exported-actions-safely)
owns executable syntax. The [layout plan](2026-10-22-gallery-review-layout.md)
owns the proposed protected-action unlock; the
[engine plan](2026-10-22-likeness-engine-acceptance.md) owns automatic maintenance.

## Delivered checkpoint

- All ten non-workflow photo-action types have saved-JSON validate/apply/undo
  regression coverage. Workflow-photo selection deliberately refuses isolated
  sandbox roots because it changes shared configuration.
- Approval, protection and anchors/core eligibility are distinct. Protecting
  Review does not approve it. Review never contributes to core.
- `photo-retired` archives recoverably outside matching. Ordinary Reject to
  Various is nonpersistent. `match-rejected` saves a content-bound stable-ID
  exclusion; grouped matching and merged successors honor it.
- Standalone person rename preserves identity IDs and history. Cast renames
  keep the slot/folder/workflow references fixed. Current protected rename
  staging uses confirmation; replacing that with an unlock is planned.
- Person protection controls currently cover Models/Prospects, not every
  category. The user's broader manual-action requirement is not yet fully wired.
- No real user action, Amelia Morgan correction or residual maintenance move
  was applied during these implementation checks. Production was untouched.

## Rules and remaining work

Every identity category must support applicable explicit manual identity
actions. Identity protection adds a deliberate safeguard, not a categorical
ban. This does not bypass ownership, path/reference, collision, anchor or
photo-specific safety checks, nor silently approve mutating a fixed cast key.
Explain an action's actual effect and unsupported prerequisites.

Person retirement returns photos to Various for reprocessing; it is not the
same as photo retirement or whole-folder archival. Whole-person rejection
needs an explicit semantic decision before implementation; do not invent it
from the similarly named photo action.

| Live task | Source scope | Retained work |
| --- | --- | --- |
| A1 | Oct 22 manual-action clarifications; Oct 21 5.1i limitations | All-category identity-action audit and protection safeguards |
| A2 | Oct 20 G1; Oct 19 management L5 | Distinct whole-person actions and recoverable unusable-photo policy |
| A3 | Oct 21 5.3 (manual swap portion); transferred Oct 20 C6/I scope | Explicit two-person name swaps |
| A4 | Oct 20 G2, G3 | Destination/consequence preview and full transaction tests |
| A5 | Oct 20 C7 | Stable report replacement without losing dated evidence |
| A6 | Recap/scenario feedback | Explain and test one real scenario at a time |
| A7 | Acceptance feedback: CLI Triggering | Bounded execution UX exploration, not an immediate local server |
| A8 | Oct 20 H6 | Later art-authoring/ComfyUI UI, explicitly outside current delivery |
| Structure plan | Oct 20 H2 | General package extraction, not duplicate refactor ownership here |
| CLI proposal | Oct 20 H4 | User-facing consolidation only after approval and replacement tests |

- [ ] **P1 ai** A1 Inventory identity-level CLI and GUI actions across all
  categories; remove blanket manual-action exclusions through supported
  transactions, not force flags. Specify protected cast operations without
  changing fixed slots accidentally. Coordinate the temporary unlock with
  layout L6; preserve automatic protection and surface unsupported references.
- [ ] **P1 either** A2 Specify then implement merge, person retirement and
  person rejection as distinct operations for applicable identities.
  Preserve stable IDs, references, histories and exclusions. Distinguish
  unusable-photo retirement from repair/resubmit Junk and recoverable
  whole-folder archive. Existing photo retirement is not unfinished code.
- [x] **P1 ai** A3 Implement a confirmed two-person name swap through the
  existing rename control when the entered recorded name has one registered
  owner. Show both identities, name/folder consequences and protection before
  staging; bind both IDs and snapshots in one standalone transaction.
  Preserve third-party collision/reference/stale-state checks, exact swap
  history on both sides and all-or-nothing apply/undo/rollback.
  Delivered Oct 22: schemas, same-control confirmation/export/cancel, guarded
  pair apply/undo, scoped recovery/move maps and explicit swap histories.
  Parent verification: 101 focused tests and normal-temp full quick validation
  passed, including 19/19 mutation cases. Real user UAT remains under A6.
- [ ] **P1 ai** A4 Cover each new action through actual GUI JSON export,
  validate/preview, backup races, apply, refresh and exact undo/restore.
  Show destinations and consequences; reject conflicting batches.
- [ ] **P2 ai** A5 Verify stable-directory report replacement, dated report
  retention, refreshed links and stale-snapshot guidance after apply/undo.
- [ ] **P1 either** A6 Walk through the user's scenarios one at a time:
  predict effects, validate/preview their JSON, apply only with approval,
  regenerate reports and compare the result. Document which command merely
  executes manual decisions and which actually invokes shared maintenance.
  Test rejects from several Models, possible new identities and stronger
  alternative matches without claiming an action apply triggers global healing.
- [ ] **P3 either** A7 Compare download/run versus a lightweight explicit
  execution bridge only if needed. First improve displayed command guidance
  and batch explanations; do not add browser shell/filesystem access, imply
  a download applies actions, or build a server without a separate decision.
- [ ] **P3 either** A8 Keep broader art-authoring and ComfyUI batch UI in
  the future roadmap; preserve manifest integration without browser file access.
- [ ] **P2 either** A9 Inventory explicit core-membership choices alongside
  approval, anchors and protection. Explain existing behavior and decide
  whether a separate manual core exclusion/override is needed; do not use
  protection as an undocumented substitute or imply the requested UI exists.
- [ ] **P2 either** A10 Review action-file intake and completed-batch filing.
  The browser currently downloads to its normal location; the user manually
  placed the Draknisa export in the sandbox's `_actions` directory. Explore
  an explicit supported save/import interaction and a completed/failed batch
  lifecycle tied to batch IDs, backup and undo history. Do not claim static
  HTML can silently choose an arbitrary filesystem destination, move/delete
  the current manifest, or add a local execution server without approval.
- [ ] **P1 ai** A11 Design and implement verified action-scoped recovery
  snapshots from the actual transaction write set. The fixed-slot cast
  rename slice is delivered: history/catalogue bytes, recovery state and
  identity-tree guards, without copying images. Broader actions remain.
  Confirmed swaps now also cover both histories/catalogue, folder/staging move
  maps, inventory/protection guards and exact pair rollback/undo.
  For a non-cast folder rename,
  include exact move/reference maps and reversal checks. Preserve originals
  or hand-edited assets whenever an action overwrites their bytes; generated
  derivatives may be regenerated only when their inputs and settings suffice.
  Broader merge/retirement/rebase transactions need their own recovery scope.
  Prove apply, stale-state refusal, failure rollback and undo before replacing
  full backups outside the delivered fixed-cast scope; never disable recovery.
- [ ] **P2 either** A12 Provide snapshot inventory, disk estimates and
  preview/check/explicit-apply pruning through supported launchers. Decide
  retention counts/days with the user, not an automatic default. Protect active
  undo dependencies, in-progress operations and required production baselines;
  show incomplete snapshots separately and require deliberate cleanup. Do not
  delete existing snapshots as part of the rename acceptance test.

## Next UAT: occupied-name correction, Oct 22 21:40 -05:00

**22:30 implementation checkpoint:** the existing rename control now offers
the confirmed two-person transaction described below. Temporary-library tests
cover GUI production-JS confirmation/decline/cancel/export, saved JSON
apply/undo, crossed same-category destinations, cast/non-cast combinations,
history preservation, stale-state/reference/collision/protection guards and
mid-transaction/undo failures. Parent focused suite: 101 tests passed; full
quick validation passed in normal Windows temp, including 19/19 mutation cases.
An earlier repository-local test-temp attempt encountered access-denied errors;
the successful independent run is the acceptance evidence, not that attempt.

Both sandbox galleries were regenerated with the installed `.3` policy/cache:
232 people, 2,667 photos. Catalogue and both direct name/history records were
hash-identical before/after refresh. The actual pair swap remains unapplied
for the user's morning GUI staging/confirmation. No production changes ran.

The latest user clarification supersedes the earlier reversed descriptions:

| Stable collection | Current recorded name | Correct recorded name |
| --- | --- | --- |
| `Sisters/Draknoxa` | Sydney Sky | Lia Joyce |
| `Prospects/Lia Joyce` | Lia Joyce | Sydney Sky |

This is a name exchange, not a photo reassignment. The Sister slot stays fixed;
the Prospect folder/display/history changes to Sydney Sky. Both collections
retain photo bytes, stable IDs, membership and protection. Show the existing
owner and consequences in the normal rename flow, rather than require a
separate tool or temporary-name workaround. The exported action must explicitly
confirm both participants; never infer consent at CLI apply time.

Implement and verify temporary-library scenarios first, refresh the sandbox
gallery, and let the user stage/confirm the real UAT action. This request does
not authorize production apply. Reusing selected correction intent later is
a possible convenience, not a requirement to retain every downloaded manifest
or bypass production's own IDs, inventories and approval.

### User direction (verbatim)

<!-- markdownlint-disable MD013 -->
```text
So the photos for Draknoxa are Lia Joyce and curent Lia Joyce is actually Sydney Sky -- sorry for confusion. so it's basically swapping those names in the rename.

What would it take to implement that.  These couple staged actions like this are the first things I would do in Production once we validate all the actions in the sandbox.  There's more to come with individual photos - but the naming of the identities that got messed up is the first important thing I will do.  Ideally, I wouldn't have to re-do all these, but that's fine ... I can manually re-do things in Production once I figure it all out in the sandbox

Let's make sure the rename action can do the proper name swap if the name I put into the rename is already taken.  If there is a warning to confirm ahead of time that's fine - so I don't do it blindly, but this is one real case I do need to fix up the names and ensure history is kept about an actual swap.  These are the easy things I need to do.  There are other renames I will wait until Production to do, but this sandbox is real verification in a UAT environment of what I need to do.  I wouldn't try to keep all the .json - but it's a thought about how I would want to re-use some to keep from hand-entering the same later.
```
<!-- markdownlint-enable MD013 -->

## User acceptance: protected cast rename, Oct 22 16:56 -05:00

The user authorized one real sandbox test: Draknisa's recorded person changes
from Sweet Beauty to Amelia Morgan using the staged JSON dated
`2026-10-22T21-50-32-514Z` in Working's `_actions`.
Validate/preview, verified backup, standalone apply, index/report refresh and
user UI review are the scope. No matching/rebase or production operation.
The fixed cast folder, slot and photo filenames stay unchanged; the `z_`
record filename/name/history changes. A non-cast directory rename and image
normalization are a separate next test, not included automatically.

**18:04 successful follow-up:** after the user requested continued autonomous
work, the fixed-cast write-set snapshot was implemented and the rename applied
as `batch_33c618e4297d4ca3bd221181bdcd724f`. Its verified backup contains two
files totaling 44,318 bytes. The `z_` record is now `z_amelia_morgan.txt`,
with corrected name, preserved history and appended rename event.
All 275 images/derivatives remain byte/path-identical, including after report
refresh. Catalogue people/photos, fixed slot, ID, protection, shared config
and production guards are unchanged. Read-only undo preview passed, not applied.
Index and both galleries use saved `.3` policy/cache and retain 232 people/
2,667 review photos. Overview history link and Review rename payload reflect
the new name. User visual acceptance remains; A6 covers further scenarios.
113 focused tests and final quick validation (495 suite tests plus 19/19
mutation cases) pass. Other action types retain full snapshots. No global
matching, rebase or image normalization ran. This supersedes the pauses below.

The first apply stopped at backup creation on a nested retained-run file
beyond Windows MAX_PATH; the live rename/catalogue was not applied. The
backup fix must pass a real long-path regression before retrying. Keep failed
snapshots marked incomplete, never skip the backup.

**17:50 follow-up:** the long-destination regression and 64 focused
backup/action/rename tests pass, as do local-fixture launcher
preview/create/verify and `bin\validate.cmd --quick`. The real retry preflight
verified all 276 identity files and the unchanged live catalogue. However,
the subsequent full-backup preview spent prolonged time in filesystem metadata
calls on local exFAT B:. Timed stacks and a zero thread suspension count
distinguish this from a suspended worker; they do not diagnose the disk.
The preview was stopped before apply. No worker remains running; no rename,
report refresh or production change occurred. A6 remains open. Before resuming,
choose scoped-snapshot implementation first or allow a much longer full run;
the user was unavailable to settle that choice. Never bypass recovery.

## Recovery follow-up: Oct 22

A full library copy for each small action is safe but disproportionate; it is
not the desired final action UX. A11 owns write-set snapshots, A12 owns their
lifecycle, and A10 owns downloaded action manifests. These are separate
artifacts with linked batch IDs, not one directory of disposable files.
The user's originals-only suggestion is an option to evaluate, not permission
to discard hand-edited assets or weaken recovery for broader actions.

Relative manifest paths aid relocation but do not shorten the resolved
filesystem path. The current backup fix uses Windows extended-length snapshot
paths; no global Windows long-path setting change is required for that fix.
It has a passing real Windows long-destination regression. The actual rename's
smaller completed transaction snapshot was also verified, as recorded above.

### User feedback (verbatim)

<!-- markdownlint-disable MD013 -->
```text
In terms of a backup for a rename - backing up the entire library will be excessive if I do them one at a time.  It might be a first approach to handling these, but I will definitely need a way to purge them since they are 5GB due to the library size.  So yes, we need a backup - but what is the right thing to do?  Maybe just backing up originals since the 911x1104 are generated and I don't need them backed up for everyone?  That's just an idea, but I'm sure you can think about the right way to have a _backup snapshot instead of a full backup.  More to think about -but for initial testing in the sandbox we'll do what is needed to ensure things are working and we don't corrupt the entire library with some of the actions that have much more effect than a rename.  Think about it and I guess that's more work to add into the docs/plans for the actions work.    Running into a path limit is something we'll need to consider and whether relative paths are more appropriate and how it all works.  Let me know if I need to make a window setting or what is the right approach.
```
<!-- markdownlint-enable MD013 -->

## Execution boundary

Documentation reconciliation itself did not authorize action execution or a
new likeness run. The later authorization covers only the single rename test
above, now applied and report-verified. The user's source feedback remains intact. The recap scenario
request is preserved verbatim below; full acceptance feedback has its primary
copy in the layout plan, with coverage in the documentation audit.

## Raw scenario feedback (verbatim)

### Single-rename test request

<!-- markdownlint-disable MD013 -->
```text
Ok - so now that you have read all the plans - what do you think is the priority I should test first.  I was going to just test the rename since that was the last topic we had.  So I downloaded a staged action and placed it into "B:\Sovereign Territories Sandbox\Working\_actions\people-gallery-actions-2026-10-22T21-50-32-514Z.json" for the Draknisa raname from Sweet Beauty to Amelia Morgan.  I would like to run that through and verify it.  Also - the download location went to my normal browser downloads - it would be ideal if we woulc download them into the "working directory" under the _actions like I did do ... and that likely means we need to move them somewhere once completed ... but we can deal with that as additional user acceptance feedback items.  For now - the focus is on just testing a single rename and re-running things so that all the files have proper name, the z_ file is renamed and history is included and that I verify the output in the UI.  Once that is done, I will stage a rename for a Prospect - which will also include renaming the directory and re-generating all the images in the proper name and so-on.
```
<!-- markdownlint-enable MD013 -->

### Earlier recap/scenario request

Source: `feedback/update_recap_10_22.md`, Oct 22.


<!-- markdownlint-disable MD013 -->
```text
Can we update the 10-22 recap with correct time and contents of where we are at now.  That might be good for me to read at this point and ensure I know what things to test and verify - and what is still outstanding.  I'll want to test some of the actions, but moving images around and then re-running the likeness overall to see how that might impact the organize/self-healing aspects.  I probably need some notes written on what exactly happens each time we run likeness commands and when the self-healing/automatic moving will execute.  For instance, if I move a bunch of items to reject to various from several models - would it also pull back any other low scoring images from other existing identities where the likeness is a much better match to a new prospect or when does all that happen.  I know we have a lot of various functionality built in now and I need a clear understanding of certain scenarios and how it works.  We can discuss them one-by-one as I want to do them in the gui and you can run them and we can discuss the expected outcome of each.
```
<!-- markdownlint-enable MD013 -->
