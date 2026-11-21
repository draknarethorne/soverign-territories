# Nov 16: SIMPLE review, category tuning and plan housekeeping

**Status:** holding (focused contract selected through execution-spine RA2j,
T29/T30, RA2d and RA2o; not another active queue)

**Purpose:** finish a reviewable SIMPLE baseline, prioritize bounded
performance recovery while the user reviews concrete placements, select
bounded corrections, then reconcile the older plans.
Do not resume experiments merely because they appear in historical plans.

**Execution owner:** [the sole spine](2026-11-05-priority-reset.md).
RA2j owns publication/check/viewer readiness; RA2d owns human review and rule
acceptance; T29/T30 own the selected performance follow-up; RA2o owns the
subsequent documentation housekeeping. Open checkboxes stay in that spine.
The completed run's evidence stays immutable. The Nov17 selection below
permits bounded code/report work while broader viewer/human acceptance stays
open. The Nov18 17:21 authorization below now selects a real sandbox run.

## Nov 19 post-run13 tuning

The spine's RA2j follow-up stages three changes/decisions before a fresh preview:

- Raise initial core floors to 0.38 for Sisters, Angels and Models, and 0.20
  for Prospects and Potentials. This does not open outbound cast moves or
  change Artist policy, Gallery admission, margins or Review suggestions.
- Resolve same-ID collisions before voting. Archive exact duplicates, retained
  raw aliases and earlier versions under `_duplicates`; a verified prepared
  native is not a newer edit just because its pixels were processed. Route
  the keeper under the normal rules. Keep byte, date, archive and hold evidence
  in the saved movement recap. See the [runbook](../art/likeness.md#draft-sandbox-likeness-policy).
  An apply cannot complete with duplicate active IDs in SIMPLE's general
  library scope. Ordinary timestamp ties have a recorded deterministic keeper;
  a protected Gallery conflict also selects a keeper and archives the other
  copies. Invalid lineage that cannot be safely archived blocks apply.
- Keep the cast Review floor at 0.35 pending a duplicate-resolved preview.
  At fixed run13 scores, 0.38 would exclude 116 of 271 cast Review rows from
  that tier; 0.40 would exclude 157. Neither would promote a photo into Gallery.

The reported Joyce/Rachel case is deferred to RA2d. The installed receipt
records 30 photo placements into the same existing identity (28 Gallery,
two Review), not a whole-identity merge. This says nothing about whether the
placements are correct.

**Replay baseline clarification.** Use the frozen Production-derived Sandbox
`Source` from `simple-clean-20261116-01`, not run13's starting or installed
placements. Retain the snapshot's original folder paths and replay arrivals
in `Various/gallery`; do not move existing named-folder copies into Various
to manufacture test cases. Report named-folder collisions and Various replays
separately where present. No live Production or Source writes.

The frozen manifest still matches the recorded baseline hash. It has 5,731
Gallery/Review paths, including 3,048 in `Various/gallery`. Run13's starting
inventory has 5,454, including 1,990 in `Various/gallery`; all 1,990 match
Source by path and bytes, but 1,332 snapshot paths are absent from run13's
starting inventory. A run13 undo alone is therefore not the selected replay.
The filename-ID census finds 286 groups spanning named folders and
`Various/gallery` (202 byte-identical groups and 84 with differing bytes),
plus one exact-byte Various-only group. It finds no repeated explicit ID
across two named Gallery/Review paths. This is not the final normalized-ID
census; do not manufacture a named-only example in the real snapshot.
All 550 original inputs from the saved run10 preparation match Source by path
and hash. That is not complete preparation coverage: reuse also requires
recipe/artifact validation and a prepared result for every selected raw
keeper. Do not assume a partial preparation manifest can be used as if it
covers the new selection.

**Frozen replay baseline verified.** The original dry run stopped with exit 2
at a regular older Working proof file with a 260-character Windows path.
The new frozen-source mode stages only the manifest-bound Source, preserves
Working via same-volume rename without walking those proof files, and never
refreshes Source. Twelve baseline tests pass, including interruption between
renames. Baseline `simple-clean-20261119-14` dry-run/apply/check each exited
0. Working matches all 11,048 paths, hashes and Source modification times
(5,496,847,211 bytes). Run13 and run10 preparation were preserved under
`Working-before-simple-clean-20261119-14`; their applied receipt and
preparation manifest hashes are unchanged. The new baseline receipt SHA-256
is `0d5f3de8afe870983624a4bba0857df10da66642bae9900618b67b7efe593516`.

**Preview finished:** LEAN `simple-rebase-20261119-14` exited 0 after about
4 hours 20 minutes, including fresh preparation. All 3,287 selected
original paths and SHA-256 values match
both the frozen manifest and the preparation start receipt's input-set
binding. None matches a run10 prepared input by path and hash; at most 549
could match through hash-only aliases, before artifact validation. The
other 2,738 have no saved run10 source hash, so run10 cannot supply the
complete selected set. Replay uses the new core floors and duplicate
resolution with the unchanged 0.35 Review floor and no outgoing cast
reassignment.

The saved receipt SHA-256 is
`56fe6cc71b0637a40f96f2e6efa7d391081cbc855dc40bc1bdc12bcee8f067e5`.
All 5,469 source rows match frozen Source by path and hash. The preview
proposes 1,979 archives (1,799 exact copies, 180 different-byte versions):
1,966 from 1,954 named/Various groups and 13 from four Various-only groups.
No group has two named copies. The receipt verification found one keeper
per ID, distinct archive destinations, and no apply-blocking collision.
The early filename-only census did not count the full normalized population.
The 3,287 publication rows comprise 1,185 path changes and 2,102 in-place
preparations. Proposed cast arrivals include 96 Gallery and 286 Review;
no starting cast Gallery photo would leave or be archived. The browser
recap shows the collision decisions including the case now proposed for
Draknoxa Review. Its one Review-snapshot diagnostic correctly says a
preview is not installed Review evidence. No writer remains. Review these
proposals before apply; no replay move or archive has been published.

**Authorized raw-baseline cleanup (separate from SIMPLE publication).**
The reviewed run14 input hashes produced a portable cleanup plan
(`2a1a34699bf025560c3c4af79a9f0a46d8896df1458aaedf4685deaaa6e85914`).
Dry-run, apply and check passed on Sandbox Working and Production.
On each root, 1,795 verified exact Various copies were removed without a
second backup, 180 approved edits took the original named paths (including
30 blocked by the earlier protected-Gallery selection rule), and all 180
displaced originals were moved to `_archive/various-cleanup/2a1a34699bf02556`.
The exact-only follow-up found and removed four additional pool-only
copies per root (1,799 total), leaving 1,069 Various photos and zero
remaining candidates under this rule. Sealed Source was not changed.
As a result run14 is historical and cannot be applied to Working.
Keep the cleaned Working baseline for the next preview; a reset from old
Source would reintroduce the old inputs.

The post-cleanup inventory/classification selected all 180 installed edits
for fresh preparation, along with all 463 Angels and 803 Sisters Gallery
originals. It selected 3,285 raw inputs overall; no detector or matching
run was started. All 867 eligible Prospects and 267 eligible Potentials
in the cleaned census are included in those 3,285 raw inputs. Models
are supported by the same inventory; neither current live root has a
Models folder. The later exact-only pass removed the other four same-ID
archive candidates, not their keepers. The 21 named Gallery files with
identical bytes under different IDs were preserved without an extra vote
or preparation.

**Shared daily intake and rebase preflight:** `various-cleanup --scan-exact`
finds same-ID, same-current-byte arrivals before preparation or backup.
The discard plan is root- and hash-bound. Explicit apply rechecks a live
keeper and does not back up or archive the redundant arrival. Different
IDs with the same bytes, uncertain lineage and differing versions remain
visible to the normal path. An original alias of a different-byte prepared
native remains subject to retained-lineage rules. This preflight does not
silently delete on intake or rebase and is separate from the approved 180
raw-baseline edits.

**Cleaned-baseline execution:** The user authorized run/re-run and bound
Sandbox publication for review, then commit/push at a verified checkpoint.
Fresh LEAN `simple-rebase-20261119-15` passed preview, apply, check and repeat
on cleaned Working with no reset or Production rebase. The
[installed run15 evidence](../recap/2026-11-18-simple-foundation.md#nov-20-installed-cleaned-baseline-run15)
verifies all 180 replacement inputs, complete source accounting, no
unresolved IDs and no existing cast Gallery departures. Actual viewers
were browser checked. RA2d can now review identity placement and crop
quality in the installed result; no rerun is needed. Broader RA2j inventory
and T29/T30 performance work remain open. Do not invoke run14 or copy the
uncleaned Source back over Working.

### Nov 20 Review and Various dispositions

The user clarified that untouched Review is a candidate source, not a
membership lock. In a future SIMPLE rebase, let it qualify for the same
grouping as a new arrival. Do not use the old Review placement as
reference evidence. Preserve explicit photo decisions, negative evidence,
anchors and workflow locks. Review does not reopen cast Gallery departures.

Run15 intake left 184 unambiguous distinct-ID byte copies in Various while
excluding their extra votes. Archive the redundant Various copy, preserve
its ID and bytes, and disclose both IDs and paths in the recap. This is
separate from the same-ID exact-copy discard preflight. Conflicting named
owners and explicit decisions still require guarded handling.

One Various candidate had measured zero faces and no usable vector. Its
desired destination is recoverable `_junk`, not a silent Various hold.
Do not treat a read/model/cache failure, multi-face ambiguity or a failed
single-face quality gate as a verified no-face result.

Run15 suspended all lower-core authority within a matching round as soon
as any frozen member was routed away. In round one, 52 of 71 suspended
cores still had frozen members left; 19 lost all. Round two suspended 20
partial and 17 fully vacated cores. This did not delete an identity.
RA2d retains the residual-core decision: remove departing votes, measure
surviving support, and distinguish an unsupported residual from a
partially depleted core that still qualifies. Avoid forcing new fragments
or changing the approved cast Gallery rules. Two additional Draknara
Review cases had a stronger displayed lower contender in final Review;
one also had a stronger lower contender at decision time. They are
separate from the 25 late-created rival cases. Similarity alone does not
authorize a move or a global cast-priority change.

RA2j owns implementation and fixture/recap checks in the existing spine.
RA2d owns policy and human acceptance. Preserve run15, Production and
Source; use a read-only comparison before selecting any new replay.
The bounded implementation makes untouched Review eligible for the same
grouping batch as Various and transactionally archives safe exact copies
and confirmed no-face input with separate recap accounting. It does not
change the cast-first Review rule or regrant authority to a depleted core.
On the installed run15 bytes, 104 of the original 184 Various copies still
match the current keeper byte-for-byte. The other 80 match their keeper's
retained original exactly. The approved follow-up recognizes an exact match
to the verified original of one unambiguous keeper during SIMPLE inventory,
before preparation. Only an unbound `Various/gallery` copy under a different
ID is archived. The receipt and recap distinguish the retained-original
proof from a current-file match, and apply revalidates the proof. Neither
the keeper nor an intentional edit is replaced by this rule.

Read-only classification of installed run15 proposed all 80 retained-original
copies and 91 current-byte copies, with the original keeper IDs for all 171
and no additional archive proposals. The 13 other historical current-byte
pairs were not proposed by the installed-baseline classifier; do not infer
that a replay will archive all 184. No library files were moved.

An isolated FAST fixture passed hash-bound preview, apply, check, repeat
and recovery, with separate duplicate and junk rows and an unchanged
sealed preview. Retained preparation transfers and recovers with junk.
The historical run15 recap reader still accounts for all 3,490 sources
and Review snapshot rows. This is not a new installed/browser verification.

#### Later audit: leftover intake and stronger rivals

Keep SIMPLE as the placement flow. Reuse useful experimental checks later
as a read-only audit of a completed run, using its saved evidence first:

- **Various leftovers (RA2j):** account for every photo still in Various
  Gallery or Review. Show the recorded reason it stayed, such as a quality
  hold, an ambiguous match, or a duplicate that could not be archived. Flag
  missing reasons as audit gaps rather than treating them as normal holds.
- **Possible misplacements (RA2d):** show the current owner and bucket,
  the stronger rival and the score gap when comparable. Distinguish a rival
  that was already stronger at routing from one that only became stronger
  or available afterward. Include any rule or lock that explains the
  original decision. A higher score is a review flag, not proof of identity.

The audit should not move photos, relax Gallery protections, or put
experimental routing back into SIMPLE. This is deferred audit scope under
the existing owners, not a new run or a change to the queue.

## Next SIMPLE run: foundational corrective contract

**Current pre-run contract.** This section consolidates the Nov18 discussion;
dated selections/corrections below retain their history and evidence, not
competing instructions. RA2d owns outstanding rule/evidence acceptance;
RA2j owns selected implementation/tests/preview through the existing spine.
No new execution queue, threshold-only run or experimental reactivation.

**Nov18 15:03 implementation authorization:** the user accepts this direction
and authorizes starting foundational code changes, with questions if a
material choice emerges. Treat the proposed numerical package, two rounds/
one reference boundary and two-reference incoming cast support as selected
implementation targets, not already installed settings or run approval.
The 15:19 clarification below resolves the provisional conservatism question;
implementation and behavioral evidence still precede any library run.

**Outcome:** recover independently supported members of fragmented lower
identities into their rightful higher canonical identities. Rebuild the
eligible lower membership decisions across old folder boundaries, rather
than treating current Gallery/core membership as a permanent placement.
Preserve sound starting cast references, genuine distinct identities,
manual intent, history, true locks and source/recovery safeguards.
Improved counts alone do not prove improved identity accuracy.

### Implemented foundation: fixture proof, not a library run

The selected normal path now implements cast-priority receiving, the approved
close-pair exception, upward reconsideration of eligible lower Gallery/core
members, existing-first decisions, one qualified reference refresh and two
matching rounds. Repository policy defaults are updated as **draft**; Working
and Production have not been changed. The earlier diagnostic remains
evidence only and cannot veto an independently qualifying individual.

Verification: **296 focused tests pass** (105.505 seconds, after actual-run fixes)
across reconciliation, normal
import/rebase/finish, policy, legacy cast helper, metadata, maintenance,
protection, retained preparation and both maintained viewers. This includes
an actual isolated launcher preview, a composed lower-core/retained-source
recovery fixture, next-run unconfirmed protection exclusion, and retained
native staging in all three profiles with actual publication/exact recovery.
The combined rerun includes the same-owner Review-to-Gallery retained-history
regression: publication now creates a distinct generation rather than
overwriting the old manifest, and exact recovery passes. It also proves
optimistic Gallery is not reconsidered or silently promoted at the boundary.
Isolated quick validator mutations pass **19/19**; routine hygiene hooks pass.
Gallery's synthetic browser fixture visibly shows the warning border/badge
and rival scores; Review's rendered-page snapshot shows the same evidence.
Review screenshot scrolling timed out; do not describe that as screenshot
acceptance or installed real-photo acceptance.

Important details preserved by the implementation:

- The 0.50 threshold is candidate-to-frozen-core similarity. Two independent
  retained references are counted separately; do not add a new requirement
  that both individual reference comparisons also reach 0.50.
- Lower scores remain diagnostic evidence, not cast-entry vetoes. Every
  blocking cast rival must be an approved pair for optimistic Gallery.
- Moving a reference retires its old lower-core authority before later
  intake can recruit against it. An affected lower core is withheld until
  the one boundary; unresolved existing owners remain in place. At the cap,
  explicit holds are not reported as convergence or processing success.
- Review cannot create/recruit another fragment. Optimistic Gallery never
  contributes references or becomes automatically protected/anchored.
  A normal confident admission requires separate reference qualification.
- Verified retained natives are transferred with their checked lineage,
  without re-preparation. Membership-only updates do not retire an unchanged
  active preparation claim. Reference/rejection evidence uses source SHA-256,
  not the embedding cache's SHA-1 key.
- `--lock-cast-admission` is receiving-only, leaves cast rivals visible and
  must match preview/apply/check. Outgoing cast Gallery remains closed.
  Ordinary intake still considers only its selected Various arrivals.

RA2j remains open for cached real-case evidence, authorized whole-library
preview/apply, installed viewers and Various before/after accounting.
RA2d retains identity/crop acceptance and any later tuning; deeper unusable-
core analysis follows that run. No new run/reset, Production write,
publication, commit or push is authorized by this fixture closeout.

### Nov18 17:21 authorization: execute and deliver actual moves

The user now authorizes implementation, testing, execution and bounded
debugging through reviewable actual results, with delegated operational
decisions. RA2j selects **LEAN** normal rebase
`simple-rebase-20261118-10` directly on
`B:\Sovereign Territories Sandbox\Working`, using the updated repository
policy and default-open cast receiving. No reset, external overlay,
experimental controller or Production write is selected. Preserve run09
and baseline02 receipts; do not rebind historical evidence.

The bound preview supplies actual source dispositions, frozen references,
proposed moves and named-case evidence before publication. Verify source
conservation, guards, persistent optimistic membership and Various cohort
accounting; then apply that preview with scoped recovery and explicit
sandbox draft permission. Run installed check/repeat and movement recap
checks, and open actual Gallery/Overview/Review plus movement audit.
If blocked, preserve failure receipts/logs before a narrow fix and tested
new preview or supported recovery. Never launch competing writers or
edit hash-bound code during a run. Human identity/crop acceptance remains
RA2d; Production publication is not selected. A subsequent user instruction
authorizes properly grouped commits/push of outstanding updates once actual
run/debug/test/viewer readiness is verified. Complete day-hygiene checks,
review the complete diff and distinguish concurrent unrelated work before
staging; do not amend old commits or run formatting against frozen producers.
The user also requests today's recap and reconciliation of affected older
recaps, plans and docs as final cleanup. Keep unique historical evidence and
raw sources intact; update current handoffs/indexes and explicit residual
owners rather than bulk-archiving unfinished plans.

Run10 preview attempt01 (PID29992) was stopped before publication after
measured repeated retained-manifest reads; no preview receipt existed.
The source-inventory scope now reuses the existing content-sealed verification
session. A focused repro failed 9 versus 6 manifest reads, then the combined
**294 tests passed in 124.145 seconds**. Attempt02 (PID32520) completed
all 550 preparations but stopped safely before publication at an existing
destination. Actual hash/manifest inspection proves its Various original
was already the source of the catalogue-bound prepared Angelica native.
It was wrongly treated as a new version. Such verified original aliases
now remain preserved/non-voting without replacing their prepared owner;
genuine new versions retain strictly bound source/target/hash validation.
Two focused repros precede the fix; all 296 selected regressions then passed.
Durable phase logs/timing receipts and hash-verified copies of the
pre-run viewers are under
`Working\_reports\runs\normal-rebase-simple-rebase-20261118-10-execution`.
Run11, `simple-rebase-20261118-11`, used explicit verified subset reuse
of run10's completed preparation:
manifest SHA256
`7257e6a803b7f15611780d18d033778cdb113870d7d71d90bacab0691c092bce`.
It stopped safely before publication after 1506.668 seconds at the permission
check: Various pool filename normalization was incorrectly treated as
identity Gallery admission. An actual apply/undo regression reproduces the
`KeyError: Various`; the guard now excludes the pool just as existing source
and Review guards do, while still enforcing photo/workflow protection.
Its durable failure logs are in the corresponding run11 execution directory.
Keep run10's failed log/timing/origin/complete preparation evidence intact.
No library writer remains. Full isolated mutations passed **53/53**.
The changed-set offline run stopped at 1,038 library tests with four failures:
three expected old admission floors and one ambiguity fixture relied on the
old Model separation margin. Updated expectations retain the selected
defaults; the experimental ambiguity fixture explicitly binds its .15 margin
without changing production routing.

The bounded review also found prepared same-path Review admissions marked
metadata-only. A failing composed regression reproduced that incorrect plan;
the bound FULL/LEAN plan now retains preparation-only semantics but removes
membership-only semantics for newly prepared inputs, so staging publishes
selected native bytes and preparation/history evidence. FAST and unprepared
membership-only behavior is unchanged. **103 targeted tests passed in
12.904 seconds**, including the four repaired fixtures and new staging repro.
Ordinary selected intake now applies the same verified-original distinction
before version selection and preparation, including when a preserved alias
is older than a genuine new arrival. Alias sources remain untouched/non-voting
and hash-bound to transaction/receipt checks; catalogue/current-native/retained
link and anchor ownership must agree. Genuine updates keep their safeguards.
Its 40 tests pass; the parent also verified **94 intake/retained/frozen-audit
tests in 78.734 seconds**. Corrected library discovery passes **1,048 tests
in 198.497 seconds**. The remaining group exposed one queue test that assumed
the current focus always contains a user-only task; it now verifies ordering
against a controlled active-plan fixture, without changing queue generation.
That final group passes **290 tests in 103.471 seconds**, followed by all three
canonical audits. Earlier passing suites and 53/53 mutations are retained
rather than repeated; initial failed gate receipts remain preserved.
Routine hygiene/data checks and explicit new-document Markdown lint pass.
Run09 and the reused preparation manifest still match their original hashes.
Run12 is now selected to reuse the same verified preparation; do not reset
or re-prepare. Freeze runtime/policy/library inputs through preview and apply.
Preview started Nov18 20:19 local, Python PID38872, monitored by shell
`simple-run12-preview`. Its start/readiness/log/completion evidence lives in
`Working\_reports\runs\normal-rebase-simple-rebase-20261118-12-execution`.
Readiness confirms the exact process and active source-inventory phase.
Wait for this preview; do not start a duplicate writer or acceptance run.
Run12 planning completed after 1,493.401 seconds and saved its bound preview;
only automatic recap generation failed, because the reporter accepted exact
aliases but not a genuine incoming native replacement at the same path.
The preserved failure is not an applied transaction. A failing report fixture
preceded a report-only fix: validate old/new sources, IDs, hashes, classifications
and owner, then disclose the superseded native separately from exact aliases.
Previous native rows cannot borrow the new current Review score/thumbnail.
All 48 affected recap tests pass in 4.395 seconds. Supported recap preview/
apply/check each exit0, without changing the saved preview or rerunning matching.

Machine preview acceptance passes: all 5,454 inputs classified/hash-bound,
733 planned publication rows, 123 cast Gallery admissions and 271 cast Review
admissions, zero outgoing cast Gallery moves, zero floor/support/Review-voting
violations, and no retired round-one references in round two. There are
435 preserved non-voting original aliases, three exact-alias coalescences and
one genuine native update; the recap conserves 5,450 distinct destinations.
Actual preview browser rendering shows all 5,454 rows and the superseded
version. No optimistic close-pair exception was needed by these admissions.
The two-round cap was reached; unresolved holds remain explicit, not converged.
`preview-acceptance.json` and `recap-repair-01.json` preserve these checks.
Preview SHA256:
`a8226e9ad0775077f067fd46ba03640921637ac09b15e1bef2f876f0438bb633`.
The next selected gate at that checkpoint was scoped LEAN apply of that
exact preview, without rematching.
Apply started Nov18 20:52 local, Python PID29072, shell
`simple-run12-apply`; exact process/log readiness is verified. It uses the
same explicit root/cache/policy/profile/run and no preparation-reuse flags.
`apply-start.json`, `apply-readiness.json`, `apply.log` and completion evidence
remain in the run12 execution directory. Do not edit runtime/policy/library
inputs, launch competing jobs, commit or reset while publication is active.

Run12 apply then stopped during first-native isolated staging, before any
publication journal or applied receipt. No writer remains. The source native
still matches its expected hash; six staged files and the original failure
log remain preserved. A non-overwriting `apply-failure-observed.json` records
the state. The old wrapper terminated on native stderr before writing its
finish receipt; no completion timing is invented.
The demonstrated cause is Windows text newline conversion of transferred
retained detail: 206 CRLF sequences changed its sealed LF checksum, and LF
normalization exactly reproduces the expected SHA256. A multiline extension
of the existing publication/recovery test fails before the fix. Exact UTF-8
byte writes for both sealed transfer strings fix the producer; all **140
affected tests pass in 97.900 seconds**, with syntax and routine checks
passing. Crop/quality/lineage guards and admission policy remain unchanged.
Because this producer is runtime-bound, **run13 now requires a fresh preview**
with the same immutable run10 preparation. Preserve run12's preview, failed
staging and bindings; do not overwrite its directory, reset or re-prepare.
Run13 preview is active, Python PID49100/shell `simple-run13-preview`.
One exact process and an advancing inventory log establish readiness.
Start/readiness/log and failure-safe completion evidence belong to
`Working\_reports\runs\normal-rebase-simple-rebase-20261118-13-execution`.
Runtime/policy/inputs are frozen; wait for its completion notification.
Run13 preview completed exit0 in **1,567.457 seconds**. Complete recursive
comparison of both receipts finds exactly five differences: two
`normal_products.py` bindings, two run IDs and the creation timestamp.
Every input, assignment, score, core, protection and move is identical to
accepted run12. The persisted run13 `preview-acceptance.json` binds that
comparison and the original zero-violation acceptance; supported recap
check exits0. New preview SHA256:
`c962ccc03fa8fb008f648ba93834425f83e61f62cb4414bcce2fe873508c89ba`.
Exact bound LEAN apply is active, PID39288/shell `simple-run13-apply`,
with one responsive process and inventory log verified. Durable
start/readiness/log/completion receipts use the same run13 execution
directory. Preserve the runtime/policy/input freeze; no reset, reuse flag,
changed receipt or competing writer.

Today's [execution recap](../recap/2026-11-18-simple-foundation.md) owns
dated performance/debugging evidence; the gates above remain authoritative.

### Nov19 installed run13 closeout

**Delivered:** the selected SIMPLE foundation is installed in existing
Sandbox Working, machine-checked and browser-inspected. No writer remains.
Human identity/crop acceptance is still RA2d; Production remains read-only.
There was no reset, repeated preparation or experimental activation.

| Evidence | Observed result |
| --- | --- |
| Bound run13 preview | Exit0, 1,567.457 seconds; full parity with accepted run12 except five producer-binding/run-ID/time fields |
| Actual LEAN apply | Exit0, 13,237.457 seconds; journal `applied` |
| Installed check after report-only repair | Exit0, 50.681 seconds |
| No-op repeat | Exit0, 51.248 seconds; no rematching/republication |
| Applied recap preview/apply/check | Each exit0; 5,450 current snapshot matches, zero unavailable/stale diagnostics |
| Physical conservation | 5,454 source rows = 5,450 destinations + three exact coalescences + one superseded native version |
| Executed publication | 733 rows: 686 changed paths and 47 same-path updates, not 733 physical relocations |
| Cast recovery | 123 Gallery and 271 Review admissions; zero outgoing existing cast Gallery moves |
| Named cases | Drakness: 13 Gallery + 10 Review admissions; Nyxene: one Review admission |

Applied receipt SHA256:
`771b35e12a54336e15997995564fb0b0e39cf3bb767750a7af558da79bd62920`.
Journal SHA256:
`6bf9da6cb18d3254a4580077c1495feff6e66d8ddb96a81dbd89fca06156f6a6`.
The original run09/preparation/run12 evidence remains immutable.
All selected cast floors, independent support, non-recruiting Review and
reference-retirement checks retain the accepted preview proof. No new
optimistic close-pair exception triggered; no real flagged example is claimed.
The two-round cap was reached, not convergence.

**Report-only check repair:** the first installed check correctly exited1.
After the transaction sealed its outputs, the applied recap had overwritten
three same-named preview report files. A composed fixture reproduced that
strict checksum failure. Applied reports now use
`_reports/library/rebase-recap/applied/`, keeping their own index and leaving
sealed preview outputs unchanged; 87 affected tests pass in 13.665 seconds.
This reporter is outside runtime bindings. The original failure, receipt,
journal and three outputs were copied non-overwriting with byte/hash proof
under run13 execution's `installed-check-failure-01/`.
Only the three preview report files were restored from their exact verified
transaction-backup bytes using the existing atomic replacement helper.
The applied receipt/journal hashes are unchanged; no native, catalogue,
policy, source assignment or implementation binding was edited or blessed.
Strict installed check and repeat then passed. Never regenerate sealed
historical preview reports in place; use a separate output for new rendering.

**Actual browser proof:** People Gallery shows 467 identity records and
3,080 Gallery photos, with 1,113 loaded thumbnails and no broken loaded
images. Review contains 5,450 current physical records; Drakness filtering
renders the recovered `photo:image_7519497700463737885`, its supported
membership and verified preparation/alignment/native/framing links.
Nyxene Review shows its one admitted photo, non-core with verified preparation.
Overview, Native Gallery, immutable-generation history, retained detail and
applied movement recap/audit all open. The recap renders all 5,454 source
rows and applied status. Published native, Nyxene's thumbnail and a historical
previous native load directly with nonzero image dimensions.
The host reports the browser hidden: Nyxene's lazy thumbnails remain deferred,
and ordinary stable-scroll timed out. Direct asset loading succeeds; do not
claim every lazy image was rendered or human identity/crop approval.

**Various cohort:** 2,221 original physical rows (1,990 Gallery, 231 Review)
yield 218 admissions to named identities: 161 Gallery and 57 Review.
The original cohort retains 2,003 Various rows: 1,902 Gallery and 101 Review.
This is not 2,003 newly unmatched people: the input includes 435 preserved
retained-original versions, 1,193 exact-byte aliases and 107 same-content
non-voting rows. The 185 same-ID/ambiguous-owner holds and genuinely unresolved
candidate/core cases remain explicit next-run diagnostics under RA2d,
without new matching or higher-gate experiments here.

RA2j's bounded SIMPLE installed/movement/browser slice is delivered; broader
task obligations and human acceptance are not silently closed. T29/T30
retain whole-operation performance: shared viewer construction/sealing alone
took 5,783.68 seconds. No whole-run speedup is claimed.
RA2o retains wider historical-source reconciliation as recorded below.
Grouped repository publication and final day-hygiene checks follow this
verified review-readiness checkpoint, not another library run.
Final routine/data/new-document lint and code whitespace checks pass.
Eight trailing-space lines in this plan's exact feedback fence remain
unchanged; the existing hook excludes Markdown and its lint passes.
Coupled
runtime/policy/tooling/tests are committed as `903186be9`; the existing
workspace-only setting is separate in `e0b901bf3`. Documentation/handoffs
form the final group. Record the verified remote head in durable run13
execution evidence without rewriting any library receipt.

### Nov18 optimistic Gallery exception for approved close pairs

**16:23 implementation selection:** the user authorizes implementing the
foundation through its tests, stopping for material issues. Distinguish
strong-but-confusable membership from weak likeness. The selected
`approved-pairs-first` option starts with the verified folders
`Sisters/Drakness` and `Angels/Nyxene`; no automatic distance cutoff is
invented. Record frozen core similarity diagnostically, not as proof that
the two identities are the same person or permission to merge them.

An eligible individual meeting the 0.50 Gallery floor, two independent
destination references and every other Gallery safety/receiving gate may
enter the best cast Gallery **provisionally** when only the 0.10 cast-rival
lead fails and every rival that blocks that lead is an approved close pair
with the winner. An unrelated third rival still requires Review. Weaker
0.35-to-below-0.50 cases, insufficient independent support, and unrelated
cast ambiguity retain provisional best-cast Review. No quality, rejection,
true-lock or receiving restriction is bypassed.

Optimistic Gallery members stay explicitly unconfirmed, non-core and
unprotected until separate confirmation. Persist assignment-only membership,
exclude them from references/anchors/recruitment and automatic protection
on this and subsequent runs, and display a distinctive border plus a
text warning with alternative identities/scores. Neither physical Gallery
presence nor a later recomputation may silently upgrade their authority.
They have one provisional owner, with truthful history and recovery.
Review remains non-recruiting. This exception refines the cast-conflict
Review fallback below; it does not change ordinary confident Gallery entry,
lower-category exclusion, two-round limits or publication authorization.

### Nov18 selected cast priority and provisional ambiguity Review

**15:42 selection, authoritative over the earlier rival discussion below:**
for SIMPLE cleanup, assess entry into Sisters/Angels against other eligible
Sister/Angel identities, not against Models/Prospects/Potentials. Keep lower
scores visible in audit, but they cannot veto cast Gallery or cast Review
even when higher than the cast score. Do not first require proof that each
lower identity is a same-person fragment. This is a deliberate receiving
priority, not a declaration that all lower identities are the same person,
a whole-identity merge or a global removal of rival rules.

Cast competition includes different identities within either category as
well as Sister-versus-Angel competition. Explicit rejections/different-person
evidence, source safety, quality and true locks remain effective; a lower
similarity score alone is not such negative evidence. Artists remain a
separate domain. Promoting Models into this preferred competition tier later
is future selection, not current work.

| Eligible cast outcome | Selected disposition |
| --- | --- |
| Best cast score at least 0.50, lead over the next eligible cast identity at least 0.10, and other Gallery gates pass | Admit the individual to that cast Gallery; require two independent destination references, not source-group equivalence |
| Same Gallery score/support/safety gates pass, but every blocking cast rival is an explicitly approved close pair | Optimistic Gallery, persistently unconfirmed/non-core/unprotected with visible rival warning; no reference growth |
| Best cast score at least 0.35 with a valid frozen destination core, but Gallery gates do not pass and Review safety/receiving gates do | Place in the best-scoring cast identity's Review; retain thin-support or other Gallery-failure reasons |
| Cast near-tie, including lead below 0.05, otherwise eligible for cast Review | Same provisional best-cast Review, explicitly ambiguous; retain alternative IDs/scores and lead, not a confirmed identity decision |
| No eligible cast match reaches 0.35 | No cast-priority override; use the existing lower-category/unmatched policy and its safeguards |
| Quality, explicit rejection, true lock or receiving restriction prevents the proposed cast placement | Respect that guard and disclose the held candidate; this priority is not a guard bypass |

The user explicitly selected `provisional-best-cast-review` after being told
this is an exception to the earlier 0.05 named-Review lead. The 0.10 cast
Gallery lead is unchanged. For eligible cast ambiguity, 0.05 is no longer
a placement veto: keep the ambiguity visible instead of forming another
Model/Prospect/Potential merely because that lead fails. Lower-category
Review rules are unchanged by this exception.

A photo has one provisional physical Review placement, with links to all
plausible alternatives rather than copied memberships. An exact tie uses a
stable, disclosed storage-only tie break; it must not be presented as an
identity determination. Review photos do not enter any core, cast or lower,
cannot attract/recruit other photos, and cannot retain stale reference votes
under their previous source identity. Review placement must not itself form
a new identity or become a seed. Final eligible Gallery admissions still
need separate reference qualification at the single boundary.

Existing-first ordering, two rounds/one reference boundary, one publication,
receipt bindings, lineage/history and the reverse receiving-only cast lock
remain selected. Revisit provisional Review in round two before finalizing;
later reference improvement may resolve a case, but neither Review nor a
round-two arrival can start a third recruitment pass. This does not open
outgoing cast-Gallery reassignment. Ordinary intake retains selected-arrival
scope. These are implementation targets, not delivered runtime behavior or
authorization for a library run.

### Nov18 clarified permission: admit qualifying members, existing recovery first

**Selected behavior, not installed yet:** the user accepts permissive
individual upward moves under the agreed entry rules. For cast Gallery,
0.50 plus the agreed destination support, cast-only rival margin, quality,
negative-evidence and true-lock gates is sufficient. Do not add a 0.65
whole-fragment similarity requirement, two independent source references,
or an all-source-core-members-must-pass condition as another admission veto.
A singleton or the supported member of a mixed source can qualify on its
own destination evidence. Unsupported members keep their own dispositions.
This is not approval for score-only admission, ignoring other cast rivals,
arbitrary whole-identity merges or automatic reference authority.

The stricter implemented `conservative-direct-core-v1` output remains
diagnostic-only. A hold in that diagnostic is **not** an incoming Gallery
rejection and must not be used to hold a photo that passes the selected
member-entry gates. Separate whole-identity merge policy is not the rule
for an individual upward admission.

**Ordering explicitly selected:** `existing-first-with-qualified-arrival-seeds`.
Keep one SIMPLE execution, two frozen matching rounds, one qualified
reference boundary and one final publication:

1. Resolve eligible existing lower-category Gallery/core recovery and
   existing named Review candidates first against starting references.
   Record individually supported proposed ownership before Various
   assessment. Apply the selected cast-only receiving competition rather
   than requiring lower fragments to qualify for rival suppression first.
   Keep residual identities/evidence visible without letting their scores
   veto cast entry; retain other cast rivals and explicit negative evidence.
2. Assess Various next against the same starting reference snapshot,
   with the resolved fragment ownership accounted for. Merely moving a
   member on paper does not enlarge a core within this round.
3. At the single boundary, independently qualify new Gallery references
   from either source. Thus a Various photo admitted on starting evidence
   can help recover existing fragmented members in round two. A Various
   photo dependent on those new references must wait for that round;
   it cannot justify its own admission or retroactively supply its own
   first-round support. Review/tentative photos never recruit.
4. Reconsider unresolved existing/Various candidates in round two, then
   finalize residual dispositions. No third refresh/pass is implied; disclose
   credible unfinished recruitment at the cap.

"Existing recovery first" means logical decisions/proposed ownership before
new-arrival assessment, not an intermediate physical move, extra publication,
reset or separate full library run. Permissiveness changes the admission
decision, not the preparation/lineage/recovery safeguards. This clarification
authorizes continuing the foundational implementation; it does not authorize
a real-library preview/apply, Production write or blanket merge.

### Nov18 rival-bypass question: remove artificial competition, retain real ambiguity

**Earlier recommendation, superseded for cast entry by the 15:42 selection
above.** In particular, its requirement to resolve a lower fragment as the
same person before setting aside that lower rival is not the selected cast
admission rule. Preserve this discussion as decision history, not another gate.

**User priority reaffirmed:** cleanup of fragmentation left by earlier high
gates and closed cast admission is the SIMPLE rebase's primary outcome.
Do not defer that repair to later experimental refinement. The user asks
whether a temporary rival-rule bypass would help; this is a question, not
authorization to disable margins or run a score-only cleanup.

**Recommendation:** retain the selected margins between distinct canonical
identity hypotheses, but do not retain the old folder-level competition
unchanged. Ignoring all rivals could free some intended recoveries, but
would also force close calls between genuinely different cast identities
into Gallery. A score of 0.56 versus another identity's 0.54 meets the 0.50
floor but not the selected 0.10 Gallery lead. Disabling that lead removes
the distinction; it does not demonstrate which identity is correct.

The existing selected process needs this explicit implementation invariant:

- Establish provisional upward claims from independent starting-destination
  evidence, the selected individual score/support gates, quality, explicit
  negative evidence and true locks. A claim is not yet a final Gallery
  admission, identity merge or new reference.
- Do **not** require a photo to beat the unnormalized historical fragment
  folder margin before establishing its same-canonical claim. Otherwise two
  fragments can prevent each other's recovery, so cleanup never starts.
- Resolve direct independently supported same-target member claims before
  applying the final distinct-identity margin. Only the supported member/
  reference evidence may stop acting as separate fragment competition.
  Keep unsupported/ambiguous residual members, explicit different-person
  evidence and genuine other identities visible. Neither being lower
  category nor merely reaching 0.50 proves that every member is the same
  person. No blanket lower-category exemption or transitive identity chain.
- Final Gallery admissions still pass the selected genuine-rival margin.
  The one reference boundary remains separate: provisional claims and
  Review members cannot recruit or validate one another.

Thus a hypothetical Sister score of 0.58 need not lose to a 0.76 Model
score when that Model's relevant evidence is independently resolved as
the same Sister; a genuinely different Angel at 0.57 must still expose
ambiguity. These are illustrative cases, not observed library outcomes.
If the evidence cannot establish the fragment relationship, report that
exception rather than silently dropping the rival. The permissive floor
still carries false-admission risk; normalization is not proof of accuracy.

**Delivery gate:** existing-first ordering and the two-round outline are
not proof that this invariant works. Current shared routing still ranks
separate folders; the implemented fragment diagnostic neither rewrites
rivals nor enables cast admissions. RA2j must prove that two mutually
blocking same-canonical fragments recover without globally relaxing the
margin, a genuine cast near-tie stays out of automatic Gallery, and a
mixed source retains unsupported members. Keep those fixtures plus cached
real-case evidence before the next expensive run. Do not add a bypass
switch, change defaults or launch a comparison run merely to answer this
question. A blanket bypass remains unselected, not implemented.

### Selected targets and remaining activation evidence

The user has established the outcome and requested foundational
simplification; do not ask them to reconfirm upward recovery or justify
why existing lower core members must be considered. Current positions:

| Decision | Current position | Boundary |
| --- | --- | --- |
| Cast receiving competition | Selected cast-only rival set: lower-category scores cannot veto Sister/Angel entry; retain them as audit evidence | No extra 0.65 group-equivalence, source-support-count, all-members-pass or lower-fragment proof veto. Keep cast rivals, explicit negative evidence and all safety/lock gates; no whole-identity merge or transitive equivalence |
| Ambiguous cast disposition | Selected provisional best-cast Review at the 0.35 floor, with alternatives and no recruiting authority | Explicit exception to the earlier 0.05 cast Review lead; never bypass the 0.10 Gallery lead, create a new rival identity or treat provisional storage as confirmed identity |
| Reference-growth limit | Implemented and fixture-tested: two matching rounds with one independently qualified reference refresh | Review/optimistic photos never recruit; no within-round core growth, circular witnesses, repeated preparation or unlimited convergence loop. A reached cap is disclosed, not described as convergence |
| Incoming numerical package | Draft repository defaults implement the [entry matrix](#complete-proposed-entry-matrix---pending-user-finalization), refined by the current cast/close-pair rules | Cast0.50Gallery/0.35Review; cast Gallery0.10lead compares cast identities only, except approved optimistic pairs. Model0.40, Prospect0.35, Potential0.30Gallery; lower Gallery0.10lead and Review0.30floor/0.05lead. Not installed or human-accepted |
| Admission support versus protection | Implemented and fixture-tested: two independent retained references for cast Gallery; valid frozen core for named Review | Automatic protection stays at four; no new reference-count restriction on lower-category admission. Optimistic Gallery cannot gain protection |

### First implemented slice: diagnostic fragment qualification

**Delivered code, fixture-tested only:** shared
`reconciliation.fragment_proposals` and the normal rebase receipt's
`plan.fragmentQualification` now describe conservative direct upward
hypotheses. This is the first evidence slice, not completed upward routing.
No experiment import, membership action, canonical-owner substitution,
reference growth or policy-default change is enabled.

**After the 15:19 clarification:** the following stricter recipe describes
the delivered diagnostic, not approved admission logic. Do not wire its
`candidateLinks`/holds as a prerequisite for individual Gallery admission.

The implemented provisional recipe is `conservative-direct-core-v1`:

- Compare only an eligible lower category with a higher same-domain core.
  Require the stricter existing source/destination `mergeMinimum` (currently
  0.65 for cast targets), not the relaxed photo entry floor as proof of
  identity equivalence.
- Require the existing identity-action minimum independent photos (two)
  on both frozen sides. Reuse the shared content/correlation reduction
  once per identity. Each source-core member must separately meet the
  destination's installed individual Gallery floor and have two supporting
  witnesses from the frozen independent destination reference set.
- Missing/ambiguous reference IDs, shared content across identities,
  insufficient/correlated support, source locks/protection, explicit
  different-person pairs, rejected identities, stale rejection metadata,
  quality failure and mixed unsupported core members produce explicit
  holds. Multiple qualified higher hypotheses stay ambiguous.
- Output direct candidates/holds with scores, actual thresholds and
  supporting IDs. Do not infer transitive equivalence, suppress a rival,
  move every group member or make a candidate into a reference. The recipe
  uses the currently installed policy; selected future settings are not
  silently substituted into evidence.

**Earlier context, before the 15:19 answer:** a clarification question about this stricter equivalence rule was attempted;
the user was unavailable. The conservative option is therefore **provisional
and diagnostic-only**, not approval to activate automatic consolidation.
This intentionally separates safe implementation progress from an unverified
identity decision. Do not run a full library preview just to obtain this
diagnostic without the existing runtime authorization.

**Observed validation:** 90 combined shared reconciliation/normal rebase/
normal intake tests pass, including nine fragment-rule cases and two new
normal-rebase adapter/launcher cases. The actual `normal-rebase.cmd`
FAST dry-run on an empty isolated repository-tmp fixture exits 0, records
the diagnostic field and dependency hashes, preserves catalogue bytes and
creates no cache. This is launcher/output proof, not a real-photo run.
Pylance reports no syntax errors in the modified producers. An initial
launcher fixture used a nonstandard receipt directory and failed recap
path resolution; the fixture was corrected to the maintained reports/runs
layout, with no unrelated receipt-path implementation change.
Routine `bin\check.cmd`, focused markdownlint including this untracked plan,
and `git diff --check` pass; `bin\todo.cmd` regenerated the spine window.
Full policy/feedback hashes still match the preserved baseline. No real
library run, reset, inference campaign, commit or push was performed.

**Next implementation gate:** implement the clarified per-member admissions,
existing-first/qualified-arrival ordering, source expansion, canonical
competition, receiving permissions/defaults/run lock and single reference
boundary as a coherent slice. Prove the selected gates and rival safeguards
with positive/mixed/lookalike fixtures and cached evidence before a real run.
Do not wait for, activate or require the stricter diagnostic as an admission
prerequisite. These remaining steps are **not implemented** by this closeout.
The new direct dependency on `protection.py` is hash-bound in shared
implementation receipts; old baseline/run receipts remain immutable.

Keep the current core selection recipe/floors for this first correction.
Discuss only how independently qualified members enter the next snapshot,
not a simultaneous top-N/pose-diversity/reference-floor experiment.
User decisions concern intended behavior/acceptable conservatism; the AI
owns producing a concrete technical rule with observable consequences.
If the existing face evidence cannot distinguish a fragment from a real
lookalike, preserve/report that exception rather than inventing certainty
or silently adding a secondary model.

### Minimal proposed rebase sequence

1. **Inventory and starting evidence:** reuse verified preparation/current
   cached measurements. Bind candidate IDs, original owners, eligible
   references, permissions and rejections. Preserve trusted cast continuity
   and protected named intent; do not physically empty lower folders first.
2. **Cross-folder candidate and identity assessment:** include eligible
   Models/Prospects/Potentials Gallery members, including their core members,
   plus existing eligible Various/Review candidates. Process existing
   recovery before Various as selected above. For cast receiving, compare
   cast identities only and retain lower scores as diagnostic evidence;
   lower identities remain real records, not cast admission vetoes. Preserve
   other cast rivals and explicit negative evidence. Source membership is
   provenance, not a self-vote or proof against moving.
3. **First frozen matching round:** first propose existing-member Gallery
   admissions under the selected score/support/cast-rival margins, recording
   fragment ownership; then assess Various using the same frozen reference
   snapshot. A qualifying photo must not wait for a stronger whole-group
   test or require every source member to pass. Record provisional best-cast
   Review, including close cast ties; do not group those photos into another
   identity. Group qualification must not carry a wrong-person member into
   Gallery.
4. **One proposed reference boundary and second round:** independently
   qualify new Gallery references from both existing recovery and qualifying
   Various arrivals against the preceding evidence, preserve
   starting anchors/continuity, and freeze the next comparison snapshot.
   Reconsider unresolved candidates and provisional Review routes, including
   their identities/rivals; newly improved Gallery evidence may supersede
   a tentative Review disposition. New members cannot validate one another
   circularly or vote for themselves. Do not rebuild after every photo.
5. **Final dispositions:** finalize named Review for qualifying exceptions;
   keep eligible cast ambiguity in provisional best-cast Review with all
   alternatives, not another lower identity. Distinguish ambiguity from
   genuine nonmatch. Form genuine residual lower
   identities using the existing grouping/category rules, preserving
   supported name/identity continuity. Unresolved existing members retain
   their owners; usable genuinely unmatched arrivals may form provisional
   Potentials. Explicitly hold quality/identity ambiguity rather than force
   an apparent improvement. Do not automatically promote Gallery members
   into reference authority or delete partially absorbed fragment history.
6. **Single publication and acceptance:** preview old/new owners, canonical
   associations, initial/boundary/final reference IDs, genuine rivals,
   Gallery/Review/hold reasons and partial/full fragment absorption.
   Publish once through existing supported recovery machinery only after
   approval. Reuse the maintained Gallery/Review/recap/audit context; no
   repeated viewer generation between matching rounds.

The selected two-round mechanism still needs implementation/tests; it is not a promise
that two rounds recover every legitimate case. If the bound leaves credible
unfinished recruitment, expose it before installation and decide a bounded
extension; do not hide it as an ordinary score failure or auto-run another
full job. This contract does not open outgoing cast-member reassignment.

### Execution order and exact pre-run gates

1. **RA2d design closeout:** the permissive member-entry and ordering
   clarification is selected; do not ask again whether qualifying members
   may move or reinstate the stronger whole-group veto. Retain the selected
   gates and different-person controls as the implementation/acceptance
   contract; never substitute another long full-library run for this proof.
2. **RA2j focused implementation:** reuse shared scoring, eligibility,
   source lineage and transactions. Add only missing cross-folder candidate/
   canonical competition, directional receiving, separate Review controls,
   independent reference-boundary and reverse run-lock/binding integration.
   Preserve ordinary intake's selected-new-photo scope; shared primitives
   must not turn daily intake into an implicit whole-library rebase.
3. **Focused regression proof:** an eligible lower-core member moves upward;
   lower fragments no longer veto cast receiving even without group-level
   equivalence; a genuine other cast rival still blocks Gallery; a mixed source admits only
   supported members; one qualified reference boundary enables a second
   recovery; Review/self/duplicates cannot recruit; a capped or unchanged
   round terminates honestly; locks/unresolved owners/history survive.
   Test selected score/margin/support boundaries and default-open versus
   receiving-only run-lock parity, including saved-preview mismatch refusal.
   Specifically prove that a member scoring between 0.50 and 0.65 can enter
   cast Gallery when the other entry gates pass even if the stricter
   diagnostic holds; a singleton/mixed source does not veto that member.
   A genuine stronger cast rival still blocks Gallery. Prove existing recovery precedes
   Various, independently accepted Various references can support round-two
   existing recovery, and neither source gains within-round/circular votes.
   Prove cast receiving ignores a higher Model/Prospect/Potential score,
   while a genuine cast near-tie goes to provisional best-cast Review, not
   Gallery or a new identity, even below the earlier 0.05 Review lead.
   Prove the 0.35 floor, exact-tie disclosure and retained alternatives;
   Review cannot vote under its old source or new provisional owner, recruit,
   grow a core or bypass locks/rejections. Below the cast floor, ordinary
   lower-category competition remains effective. Preserve single ownership
   and do not claim a whole-group merge from individual recovery.
4. **Read-only evidence preview:** reuse valid saved measurements for
   representative real cases and gate counts where available, without
   missing-model inference or whole-viewer rebuilding. Disclose missing/
   incomparable evidence. Review proposed core changes and false-merge
   controls; fixtures are not a claim of installed accuracy.
5. **Authorize one next SIMPLE run:** use a new bound preview/run identity,
   retain original receipts/baseline02, verify source/recovery/runtime
   prerequisites, then seek the existing preview/apply approval. New
   preparation is only for genuinely required invalid/missing evidence,
   not a mandatory redo of unchanged images.

**Explicit exclusions:** no new embedding/secondary-cue models, appearance
subsystems, family-based matching, arbitrary whole-group merges, unlimited
refinement/growth loops, threshold sweeps, extra performance project,
schema redesign unrelated to selected controls, Production writes or
experimental command activation. Necessary permissions/config/schema/test
changes stay in the normal supported path and use its launchers.

## 1. Formalize the concrete work and establish review readiness

This contract is the concise next-session entry point. Earlier raw Q&A and
dated implementation evidence remain in their original homes:

| Source | Disposition here |
| --- | --- |
| [Protected Gallery/workflow-selection request](2026-11-12-member-refinement-scope-test.md#nov-16-post-apply-protected-member-and-workflow-selection-review) | Carry forward under RA2d; not delivered by retaining existing owners |
| [Incoming Angel/Sister gate question](2026-11-12-member-refinement-scope-test.md#nov-16-incoming-angelsister-admission-gates) | Carry forward under RA2d; separate admission from removal |
| [Category-threshold question](2026-11-12-member-refinement-scope-test.md#nov-16-incoming-threshold-hierarchy-for-the-next-review) | Carry forward under RA2d; latest ordering below supersedes uncertainty about the desired broad hierarchy, not the numerical defaults |
| [Timed SIMPLE recap](../recap/2026-11-16-simple-rebase-recap.md) | Single home for run counts, measured timings, core inventory and gate diagnostics |
| [Collaboration-efficiency audit](../audits/2026-11-05-copilot-efficiency/README.md) | Reuse its one-spine, bounded-context and evidence-reuse principles; no new tooling rollout |

### Current state: machine-complete run and reviewable saved-run reports

Run09 apply/check/repeat exited0; no writer remains. The
[timed completion and reconnection evidence](../recap/2026-11-16-simple-rebase-recap.md#nov-17-completion-and-report-reconnection)
owns timings, hashes, browser results and performance limitations.
Saved-run recap/audit and shared reader/proof/provenance wiring are
implemented and fixture-tested; the report-only baseline is installed and
browser-verified. Broader installed-viewer/human acceptance is not closed.
Do not restart intake/publication or rewrite old receipts.

### Historical publication failures and saved-preview continuation

**Nov17 continuation:** preview09 exited0, but its controller correctly
stopped before apply on different move destinations. A complete semantic
audit now proves the [naming-only exception](#selected-run09-provisional-naming-exception)
below. The same saved preview subsequently completed apply/check/repeat;
do not repeat preparation/preview, edit its receipt,
remove folders or treat an unexamined move difference as acceptable.
Controller32004 and preview child50016 have exited. Saved09apply is now
started07:30:49Z/01:30:49CST under attached shell
`run09-apply-continuation`, controller38120/cmd48936, using
`tmp/normal-flow-restoration/continue-simple-09-after-naming-audit.py`.
That job and its checks have completed; actual installed-viewer/human
acceptance remains open. This paragraph preserves the original start record.

**Earlier, Nov16at23:36CST:** run08 failed during Review generation at
23:07:59CST/05:07:59Z, exit1 after21135seconds; its journal reports
`rolled-back`, not applied. The actual held Various duplicate shares an ID
with a prepared native, but has no current-path preparation claim. The crop
guard correctly refused it; Review incorrectly let that refusal abort the
viewer instead of showing an actionable diagnostic. The narrow viewer fix
passes140affected tests and the actual-byte held-alias proof. Crop/admission
guards and policy are unchanged. The
[timed recap](../recap/2026-11-16-simple-rebase-recap.md#apply08-review-rollback-and-repair)
owns exact source names, preservation hashes and proof evidence.

Run09 `simple-rebase-20261117-09` started05:36:43Z/23:36CST under attached
`run09-controller`, controller32004/preview child50016. New preview reuses
verified preparation and must match audited08 sources/moves/protection
before apply/check/repeat. Reuse that job and freeze runtime/policy/inputs.
The old stage is preserved, not certified for resume; staging must rerun.
Final installed checks and actual browser acceptance remain open.

### Selected run09 provisional naming exception

The strict stop is preserved. Its destination differences are limited to
135new, uninstalled provisional identity names: empty directories left by
run08 rollback reserve those former generated names. No existing/user-named
identity is being renamed. All previous grouping members, categories,
buckets, stable photo IDs, scores, reasons, source hashes and protections
are unchanged. The full plan also compares equal after the explicit
bijective provisional-name/path/prefix mapping, except run metadata and the
two already-tested viewer module bindings.

RA2j accepts this **specific proved exception**, not a blanket relaxation
of source/move/policy parity. Preserve both proofs, the old stop and the
complete old/new name crosswalk linked from the
[timed recap](../recap/2026-11-16-simple-rebase-recap.md#run09-saved-preview-naming-exception).
Use the saved09preview unchanged with current binding checks; any further
difference/failure stops continuation. Old provisional directories are
verified empty and absent from frozen Source; new destinations are absent.
No directory is deleted, no existing identity/name is changed and no
historical receipt is rewritten.

**Residual disposition:** transaction-created empty-directory tracking/
cleanup remains a bounded RA2j recovery follow-up for later selection, with
proof that pre-existing/user-named folders are preserved. Do not invent a
generic cleanup framework or interrupt this installation for it.

**Historical restart, Nov16at17:04CST:** the publication boundary is repaired and71
composer/import/maintenance tests pass in23.890seconds, including regression
reproduction and exact undo with and without a local catalogue. Normal
rebase/import now let the transaction snapshot an existing staged target;
the repository catalogue fallback is not a root-relative source.
Run08 has restarted under the current code. Attached shell
`run08-controller`, controller35352/initial child9936, runs supported
preview -> source/move/protection parity audit -> apply -> check -> repeat.
Reuse that job; do not start a duplicate. Runtime/policy/inputs stay frozen.
The controller's status/log paths are in the ignored reboot handoff.
After machine checks, actual browser acceptance is still required.

Apply07 stopped at **15:08:05 CST / 21:08:05 UTC**, native exit **1**, after
**11,785.94 seconds (3h 16m 25.94s)**. Python43788 and parent32864 were absent
at the21:36UTC inspection. No applied receipt or publication journal exists.
The isolated staged catalogue exists with203people/3108photos; those are
staged records, not installed or human-confirmed identities. No task writer
remained at that inspection; run08 is the later authorized restart above.

The failure reports that repository `data/art/likeness-library.json` is not
under Sandbox Working. The apply path attempts to make the current catalogue
root-relative before starting its publication transaction;
`metadata.path_for_root` falls back to the repository catalogue when Working
has no local catalogue. Preserve this distinction: the absent journal means
no publication transaction began, not that staging/evidence wrote nothing.
The repository catalogue still matches the preview's bound SHA256.

Fifteen preview/audit/log/metrics/catalogue/producer/policy files are preserved
with exact byte/hash verification in Working:
`_reports/runs/normal-rebase-simple-rebase-20261116-07-publication-failure-01/`.
Evidence manifest SHA256:
`0ff0221188d31eef43b0adc73aa0f7fcb377012853fb97f51d625d34459a0fe7`.
The original start record's truncated preview SHA is preserved with an
explicit correction, not edited to look valid.

**RA2j repair/restart:** regression tests reproduced the catalogue/publication
boundary error before the fix, including a clean Working root lacking a
local catalogue. The71-test repair verification now passes.
Keep Production read-only and preserve the failed run/stage. Do not copy
the whole Sandbox to repository scratch, create a local catalogue merely to
bypass the error, reset Working, hand-publish staged files or edit receipts.
Reuse prepared/staged products only through a supported hash-bound path;
do not assume a stage-resume command exists. If implementation changes,
honor receipt bindings and document what must rerun before starting it.
The restart reuses the fully verified completed preparation, but preserves
run07's unsealed stage as evidence and must stage products again under
run08. This may take hours; do not claim a supported old-stage resume.
The controller stops on native failure or changed audited outcomes, preserving
per-step logs/timings in Working's run08 execution-evidence directory.

**Readiness exit:** successful applied receipt, separate supported installed
check/repeat, source/file/manifest conservation and actual Gallery/Overview/
Review/detail/history browser checks. Reuse those results across owners.
Machine acceptance does not approve identity/crop quality or current policy.

The exact initial Angel/Sister reference CSV and saved proposal diagnostics
can be inspected now; preparation reports show prepared pixels, not final
placements. Final grouped-Gallery human review remains blocked. Never offer
copied old viewers or isolated staging as the finished result.

### SIMPLE performance carry-forward: retained pieces versus missing integration

**Nov17 priority:** after current-run machine/browser acceptance, T29/T30's
bounded SIMPLE viewer/read-reuse work is the next AI implementation priority,
before another expensive replay or optional tuning/housekeeping. Human
placement review can proceed independently. The
[recovered log evidence and confirmed module/session split](2026-10-28-intake-performance.md#nov-17-recovered-timing-evidence-and-simple-reuse-boundary)
are preserved in the existing performance owner; no new performance plan
or live runtime change is needed.

The SIMPLE restoration was not a wholesale rollback of the shared tools,
but it did not retain every optimized orchestration path. Source inspection
finds concrete integration gaps, not evidence that every earlier threading
idea was production-ready. The
[performance contract and prior measurements](2026-10-28-intake-performance.md#nov-6-bounded-implementation-and-paired-evidence)
remain the historical evidence home; this table scopes their SIMPLE relevance.

| Mechanism | Verified current state | Bounded follow-up |
| --- | --- | --- |
| Preparation worker processes | Shared `image_preparation` still implements memory/CPU-bounded workers and per-worker thread allocation. `normal_products.prepare` explicitly supplies `workers=1`, bypassing that automatic worker selection | Compare the existing bounded worker policy against serial preparation on identical representative inputs before integrating it; no new parallel framework. Run08 already reuses preparation, so this is not its current viewer bottleneck |
| Shared scoring and prepared-input reuse | `normal_finish.viewers` passes the same scoring context to both viewers; normal preview/apply supports hash-bound prepared-input reuse | Preserve these delivered savings and their binding checks; do not describe SIMPLE as rebuilding everything |
| Shared report proof/provenance | Nov17 reconnection gives `normal_finish.viewers` one verification session and provenance index for both writers, retaining cache-only scoring and the final seal | Same-input index/read and output-parity tests pass; representative whole-operation timing remains T29/T30, not a claimed9-hour speedup |
| Per-operation read reuse and small write reductions | Shared verification caches, manifest batching and unchanged-detail write avoidance survive. Canonical readers now see the coordinator's session; the qualified-module split is reproduced by regression tests | Real bounded read-only pair and its limitations are in the timed recap; preserve standalone checks, independent seals and all invalidation guards |
| Parallel derivative/report jobs | Earlier two-thread derivative work has component/probe equivalence evidence, not a delivered whole-operation worker coordinator. Current Review processing remains serial | Do not call this lost production threading. Consider bounded disjoint-owner jobs only after measured duplicate-work fixes, with coordinator-wide integrity/failure/retry proof |

**Order and ownership:** RA2j owns this SIMPLE integration inventory and
current-run acceptance. Existing T29/T30/T20-T22/L18 contracts retain
measurement, repeated-work, derivative/detail and report ownership in the
spine; consulting them does not activate their whole backlog. The spine now
selects only T29/T30's representative viewer/read-reuse slice after current-
retry machine/browser acceptance. T20-T22/L18's broader inventory, workers
and detail contracts are references, not wholesale reactivation. Human
placement review need not wait for an exhaustive performance programme.

1. Reuse run08/run09 phase evidence to choose the dominant demonstrated cost.
   Record representative generation and unchanged/no-op cases, source/code/
   policy/profile bindings, wall time, reads/bytes, CPU and peak memory.
   Do not launch another whole-library rebase just to establish a benchmark.
2. Remove demonstrated duplicate indexing/verification/manifest or decoding
   work first, retaining same-operation mutation/path/owner checks and final
   integrity seals. Treat required standalone/reviewed-stage revalidation
   differently from artificial intermediate boundaries.
3. Reconnect the existing bounded preparation workers with focused parity
   and failure tests if beneficial. This is separate from accelerating the
   currently slow viewer path. Add viewer/derivative concurrency only if
   measured costs still justify it and ownership can remain disjoint.
4. Require the same placements, stable IDs, pixels/derivative hashes,
   provenance, diagnostics, recovery and browser behavior, allowing only
   explicitly identified volatile report fields. Record measured gains or
   no gain and stop when the selected problem is solved; do not rebuild
   experimental matching, a scheduler or a generic processing framework.

**Complexity/value check:** before expanding an intake/likeness proposal,
challenge what concrete user-visible problem it solves, the simplest
existing-path alternative, expected measurable benefit, added maintenance/
failure cost and a bounded stopping point. Recommend deferring mechanisms
without clear practical value rather than treating every idea as required.
This working guardrail is captured for this plan; permanent memory scope
remains unconfirmed because the user was unavailable for clarification.

### Nov 17 selected recap, audit and performance reconnection

Run09 apply/check/repeat exited0; controller state is
`machine-checks-passed` / `browser-acceptance-pending`, with no remaining
writer. The latest user explicitly selects implementation now, not another
planning-only pass. Existing receipt/code bindings remain historical truth:
do not rewrite run09 receipts or claim that old processing used new code.
Actual browser verification remains an acceptance obligation.

**Delivered bounded slice:** supported saved-receipt preview/apply/check,
movement recap, reference/placement diagnostics, same-source comparison,
per-photo audit links, shared proof/provenance and canonical reader scope.
Future normal preview/applied receipts automatically publish their reports.
Report failure after publication explicitly identifies the saved applied
receipt and requests report-only repair, never reset/republication.
The [timed evidence](../recap/2026-11-16-simple-rebase-recap.md#nov-17-completion-and-report-reconnection)
distinguishes actual browser/report checks, fixture parity and small-sample
measurements from remaining whole-viewer/human/performance gates.

**Next run order:** retain09 as the behavior/policy baseline; validate
whole-viewer/no-op performance without another rebase; then select cast
admission configuration, then Prospects/Potentials configuration in separate
attributable comparisons. Later rebuilding/group-to-group/refinement apply
needs its own selected contract. Named-folder protection remains the existing
bounded follow-on, not an implicit policy change in these reports.

### Selected timed viewer baseline before configuration changes

Nov17at15:33CST, the user accepts the reports-only baseline recommendation
and requests that plans stay current. RA2j/T29/T30 select
`simple-viewer-baseline-20261117-02` on unchanged Sandbox Working, profile
LEAN inherited from09. Production and frozen Source remain read-only.
Use existing `bin\people-gallery.cmd --reports-only` with explicit Working
root, cache, policy and library output: preview, timed apply, unchanged
timed apply repeat, then independent `--check`. This uses the maintained
shared-reader/provenance coordinator, not a new whole-library rebase or a
controlled before/after comparison against09's nine-hour apply.

Preflight found its report context can instantiate an embedder for cache
misses. The bounded prerequisite makes this path cache-only, as normal
viewers already are, with a regression forbidding model construction and
cache mutation. Missing measurements stay unavailable; do not infer them.
Then freeze runtime/configuration/policy/library inputs until completion.
Preserve old report and Review-data evidence before replacement, keep
per-step command/timing/read/byte/producer/input records, and verify physical
photo paths/hashes, catalogue, cache, policy and receipt conservation.
Evidence belongs in Working `_reports/runs/simple-viewer-baseline-20261117-02`.
Do not overwrite09 receipts, stage identity actions, change thresholds/
protections, prepare photos, reset/rebase or activate appearance work.

After both generation commands, compare Review membership/protection and
score/diagnostic changes explicitly; missing evidence is not success.
Refresh/check the saved09 recap/audit against the new Review snapshot,
then verify actual Overview/Review/recap/audit thumbnails, filters and
native/detail/history links. Record generation versus unchanged repeat
separately, their independent seal/check costs, and any residuals in the
existing timed recap. Human identity/crop acceptance and conditional
commit/push stay separate. No competing writer was found; the old09 job is
complete. Do not start a second baseline while this job exists.

**Complete:** generation/repeat/independent check and recap preview/apply/
check exited0; representative actual browser acceptance is recorded in
`browser-acceptance.json` beside the machine status. The
[timed closeout](../recap/2026-11-16-simple-rebase-recap.md#nov-17-timed-reports-only-baseline)
owns exact timings/read counts, source conservation and diagnostic changes.
No writer remains; do not restart this completed baseline.

**Start record,15:42:20CST /21:42:20Z:** attached shell
`viewer-baseline-02`, controller47772/cmd10932. All5,454 frozen native paths
and1,925,176,298bytes verified in5.843701s; actual generation started
21:42:28Z. Cache-only guard and shared viewer regressions pass68tests.
The exact preview passed before launch; the controller owns the only
generation/repeat/check sequence. Status:
`Working/_reports/runs/simple-viewer-baseline-20261117-02/status.json`.
Those runtime/cache/policy/library bindings and all native SHA256s stayed
unchanged through completion at19:00:23CST. No policy change was selected.
Attempt01 stopped in0.027508s on Windows command quoting before the launcher
ran. Its status/logs/source proof and byte/hash-verified original controller
remain in its separate01evidence directory. Corrected invocation passed
dry-run before02; no reset, receipt rewrite or failed report publication
was required.

**Comparison constraint:** original normal-generated pages are not
score-equivalent to this maintained baseline:4352diagnostic rows differ,
including495scores and134scores becoming unavailable. The old context
omitted Gallery paths from the ambiguity universe; three concrete Afton
West IDs go from one occurrence to two under unchanged duplicate-ID rules.
Physical membership/protections remain unchanged, and the unchanged repeat
has zero recorded diagnostic differences. Preserve both snapshots and
`report-context-analysis.json`; do not call this a threshold-change result.
For future cast/Prospect/Potential comparisons, regenerate with this same
maintained coordinator, or prove normal-viewer context equivalence first.
RA2j/T29 retain that context-parity residual and further measured performance
work; this baseline does not close their full contracts or human review.

RA2j owns the saved-run recap/audit adapter and report navigation; T29/T30
own bounded measured reader/proof/provenance reconnection. These are one
primary slice with an independent code-only companion, not competing
library jobs. Reuse existing renderer, audit evidence and launchers.

| Feedback/request | Selected disposition and exit |
| --- | --- |
| Recap of every stay/move/rename/Review transition | RA2j now: adapt saved SIMPLE source/move/native records, conserve physical source rows and explicitly account for exact-alias coalescence; preserve run IDs and compare compatible saved runs. No new likeness inference or rebase |
| Recap navigation | RA2j now: identity/Review/photo/detail links open separate tabs; in-recap section links stay local. Clearly label unavailable historical images and planned versus applied evidence |
| Useful automated audit | RA2j now: expose recorded consistency checks, corrections, protected recommendations, core/reference limits and available own/rival/workflow evidence. Show saved evidence scope and missing fields honestly; do not invent a fresh exhaustive final-state audit |
| Performance and older implementations | T29/T30 now: reuse existing operation-local readers and shared report provenance/proof, correct module-scope fragmentation, preserve independent seals/guards; measure representative same-input costs and output parity before claiming gains. No full-library rerun merely for timing |
| Chiara/Drakness, Sia/Drakniss, Zoe/Drakniya, Cressida/Drakniya and Aria/Draknora | RA2d next cast-admission comparison: user labels and group scores are review cases, not proof every member qualifies. Preserve Cressida photo7518413273886433101/person_92ded2807fcc461abe046b95f43fe213 |
| Cast Gallery and fallback Review thresholds | RA2d Nov18 selection below supersedes the earlier Review>=0.30 proposal: both cast categories Gallery>=0.50, named Review>=0.35 with all-category rivalry and the existing0.10margin. Defaults, not opt-in overrides; implementation/preview acceptance still required |
| Release low cast members, rebuild lower categories, configurable promotion hierarchy and recast residual groups | RA2j/RA2d later separately selected rebase/group-to-group contract. This changes current retention/group formation and is not authorized by restoring a viewer |
| Excess Prospects/Potentials | RA2d subsequent configuration-only comparison, distinct from cast-admission changes |
| Ongoing maintenance group-to-group and low-member refinement | Later RA2j/RA2d selected run after stable rebase; no automatic global regrouping on small arrivals |
| Audit recommendations applied automatically | Later explicit refinement/apply contract with normal source/destination protections, reference handling and recovery; report generation itself remains read-only with respect to membership |
| Appearance groups overcomplicated | Do not reconnect appearance experiments. RA2o retains their explicit holding/superseded disposition; no historical source/code deletion |

**Acceptance:** supported report preview/apply/check on saved09 without a
new rebase; current recap plus auditable baseline and comparison navigation;
focused equivalence/tamper/failure tests, measured read/index reductions and
actual browser link/thumbnail checks. No independent full hash campaign per
owner. Retain the feedback file in place while review/follow-on work is open.
Later policy runs change one selected family of gates at a time and retain
their own recap/audit evidence; new-machine migration remains deferred.

## 2. Human review, then bounded tuning

### Nov 18 sequencing: Various retention analysis after the next run

The user reports that visibly matching photos remain in anonymous
`Various/gallery` and considers the retained population unexpectedly large.
This is an unresolved processing/admission concern, not explained away by
the expected absence of a Various identity core. A missing own-core badge
does not establish that rival evaluation ran, that it succeeded, or why
admission failed. Do not conclude that the population is correct, or that a
processing defect is proved, from that label or the count alone.

**Earlier selected order (broadened by the full-hierarchy review below):**
proceed to RA2d's existing Angel/Sister admission
configuration comparison, before Prospects/Potentials tuning. Defer the
deep Various/core-label investigation until **after that next run**;
do not start another baseline or performance project as a prerequisite.
Existing category/individual-score/rival-margin/protection/last-resort
Review decisions still gate a configuration apply. The later selected
defaults below settle the cast thresholds, not permission to bypass true
locks or reset the installed baseline.

**Next-run acceptance, RA2d with RA2j evidence support:** carry the current
anonymous Various cohort forward by physical path/content hash and stable
photo ID where available; retain named Various intake as a separate cohort.
Use the already preserved baseline02 Review/receipt evidence, not another
image processing pass merely to count it. Report before/after totals,
admitted members, named Review placements, newly grouped photos and those
still unassigned, accounting for exact aliases and any applicable holds.
Keep the same maintained viewer context for comparable scores/diagnostics.

**Deferred post-run analysis, same owners:** for each remaining anonymous
Various photo, distinguish missing/invalid measurement, missing destination
core, duplicate-ID ambiguity, candidate/source eligibility, quality gates,
destination similarity, rival margin, rejection/protection blocks, and
grouping/processing failure or absent decision evidence. Use actual recorded
facts; leave unrecorded reasons explicitly unknown. Show eligible leading
identities and individual admission evidence, not group similarity alone.
Review residual examples against the user's expected matches. Investigate
demonstrated processing defects separately from intended gate behavior.
No automatic move, core fabrication or broad threshold relaxation follows
from the population being large.

**Separate presentation follow-up:** label anonymous Various as
"Unassigned pool - own-identity core not applicable", rather than treating
it as a named identity with a failed core. A named identity genuinely lacking
a usable core must retain its diagnostic. Label repair is deferred with
this analysis and is not a substitute for explaining retained candidates.
Capture the next-run cohort/evidence now as part of acceptance; perform the
deeper investigation afterward, without blocking the existing next step.
Open execution ownership remains spine RA2d/RA2j, not a second plan queue.

### Nov 18 selected cast defaults, rivalry and core explanation

**Earlier selection, not the final next-run package:** the subsequent
[full-hierarchy entry review](#nov-18-full-hierarchy-entry-review-before-final-tuning)
reopens the four-reference gate, proposes a separate0.05Review margin and
brings Models/Prospects/Potentials into the same pre-run review. Preserve
the earlier0.10Review and deferred-Models statements below as decision
history, not current instructions to implement them.

The user selects **both Sisters and Angels Gallery>=0.50 and named
Review>=0.35**. Retain the existing0.10rival margin for this comparison.
Models remains0.50for this iteration; the user explicitly defers lowering
Models to the next iteration. Temporary equality is intentional, not
permission to tune Models/Prospects/Potentials now. These are selected
defaults, not implemented settings or evidence of an applied policy run.

**Individual routing contract:** compare each eligible photo against the
same frozen qualified cores across all eligible categories. First consider
qualified Gallery destinations. Named cast Review is last-resort only:
the cast identity must meet0.35and lead every other eligible identity by
at least0.10. A higher-scoring rival, or an insufficient lead, must prevent
automatic named cast Review even if that rival cannot itself admit to
Gallery. Do not remove a rival from the comparison merely because it fails
its destination admission threshold. Real rejection/domain/eligibility
exclusions still apply and must be recorded. Ambiguous/no-qualified routes
remain explicit; no forced placement or whole-group admission.

Examples (scores alone do not waive quality/reference/protection checks):

| Cast score | Best other identity | Result |
| --- | --- | --- |
| 0.52 | 0.40 | Cast Gallery may qualify |
| 0.42 | 0.30 | Named cast Review may qualify only after Gallery alternatives are exhausted |
| 0.40 | 0.45 | No cast Review: another identity scores higher, even if its own Gallery gate is unmet |
| 0.40 | 0.34 | No automatic cast Review:0.06lead is below0.10 |

**Defaults and run lock:** persist category-specific Gallery and Review
admission settings in the canonical policy, with both receiving paths open
by default. Keep the global lower-category Review threshold unchanged.
Integrate the dedicated incoming gate through normal planner, publication
authorization and receipt validation; do not unlock protected membership
globally or simply flip broad automatic-routing flags. Identity/member
removal, merge/split, true locks, rejection and workflow-reference safeguards
remain unchanged. Shared admission behavior must not require experimental
commands or opt-in opening parameters.

Add a reverse per-run cast-admission lock (proposed CLI spelling
`--lock-cast-admission`, **not currently supported**) that closes incoming
Gallery and named Review for both Sisters/Angels while leaving their cores
visible as rival evidence. It must not remove existing members, modify
saved defaults, erase rivals to favor other destinations, or manufacture a
Review destination. Bind/record the effective lock in preview/apply/check
evidence, reject mismatched resumes and document/test normal entrypoints.
No new command line should be offered as executable before implementation.

**Core facts verified in current code:** `normal_finish.cores` takes
Gallery photos only, then `frozen_identity_cores`/`audit_person` use qualified
existing Gallery members, not every Gallery image and not a fixed top-N.
Usable, current, unambiguous membership/reference evidence is required.
Valid explicit anchors seed trusted cores; without anchors the eligible
Gallery cohort seeds a provisional coherent core. Existing cast core floor
is0.30, with leave-one-out pruning that retains valid anchors. Some protected
photos may be excluded from reference use; protection is not automatic
evidence of identity. Core floor and incoming admission thresholds are
different controls. The separate Gallery-admission evaluator also requires
four independent frozen destination references; raising/lowering the
admission score does not waive this check.

**Recommendation for next comparison, not a new core algorithm:** retain
the current core construction/floor, freeze one initial qualified roster
before routing, and expose its exact IDs/counts/anchor-versus-provisional
mode in preview/recap. New admissions and named Review must not expand the
casting core during that pass. The entire Gallery can therefore remain
physically present while only its qualified subset influences admission.
Changing to top-N or a stricter core floor now would conflate two experiments.
Exact next-run rosters require its preview; old scores are context-bound,
not a sufficient roster. Existing Gallery non-core members remain in the
separately selected audit scope, not silently released for global regrouping.

### Nov 18 full-hierarchy entry review before final tuning

**Current review scope, RA2d with RA2j evidence/implementation support:**
review the entire incoming hierarchy before finalizing one next-run package.
The user questions the four-independent-reference requirement, proposes a
Review rival margin of0.05rather than0.10and Model Gallery entry of0.40,
and brings Prospects/Potentials forward into this review because runs are
expensive. This supersedes the earlier cast-only/defer-Models sequencing.
It is permission to analyze the full entry package, not approval of every
number recommended below or permission to launch/apply a library run.

**Correction to the previous explanation:** four references are enforced by
`policy.evaluate_cast_admission`, currently called by legacy
`clean_rebase`, **not by the normal SIMPLE candidate planner**. The normal
planner bypasses cast entry and sends best-cast candidates to grouping.
Thus the four-reference gate could obstruct a newly connected admission
path, but must not be blamed for run09's existing Potential population.

#### Reference count and its distinct purposes

The helper reuses
`protection.automatic.minimumIndependentReferences=4` for cast admission.
Legacy callers reduce qualified frozen Gallery references by unique
content/ID and a0.95maximum mutual similarity, then exclude the candidate
itself/same bytes and candidate-reference similarities above0.95. This is
a heuristic for avoiding correlated votes, not proof of four different
people or statistical independence. A large Gallery can have fewer than
four counted references; near-duplicate burst photos need not be extra
votes. It is not a requirement for four new arrivals in one batch.
Nor is it four separate candidate-reference scores above the Gallery
threshold: admission compares the candidate with a core vector and checks
the independent reference count separately.

A constructed runtime check with score0.80and rival lead0.20held support
counts1/2/3and admitted4. Ten different hashes with near-identical vectors
reduced to one independent reference. These are fixture observations, not
measured affected-photo counts from this library. A small/visually narrow
identity can consequently fail to grow automatically, despite a high score.
Because references stay frozen, admitting candidates must not bootstrap
support for subsequent candidates in that same pass.

**Recommendation for discussion:** separate incoming cast admission support
from automatic protection. Require two independent retained references for
automatic cast Gallery entry; permit named Review with a valid frozen core
without imposing the four-reference count, and disclose single-reference
evidence. No core means no scored identity admission. Retain the existing
four-reference automatic-protection setting and established-identity guards.
Do not introduce a new two/four-reference entry gate into lower categories,
which currently use their qualified cores without this cast-only helper.
The proposed two-reference cast minimum is not approved or implemented.

#### Existing identity entry versus creating a new identity

These are different questions and different controls:

1. **Existing entry:** per-photo similarity to that destination's frozen
   core, lead over every other eligible identity, receiving permission,
   valid source/reference evidence and genuine protections/rejections.
2. **New group creation:** after genuinely unmatched photos are grouped,
   classify by final usable-photo count and cast resemblance. Current
   `categoryAssignmentRules` put1-4usable photos into Potentials regardless
   of cast similarity with group-cast Review disabled. At5+photos, cast
   resemblance>=0.40classifies Models; below0.40classifies Prospects.
   `groupCastReviewEnabled=false` also bypasses Models' configured0.55upper
   cast-resemblance band in the current classifier. This0.40classification
   boundary is not the0.50existing-Model photo-entry threshold.

Constructed normal-planner evidence: a singleton scoring0.80to a Sister
and0.60to a Model became a new Potential through the current cast bypass.
Conversely, an existing Model best match at0.45with next rival0.37was
held without named Review, not demoted into a new Potential. Changing only
Model entry0.50->0.40still held it because the shared Model margin is0.15.
The user's rival/fallback concern is plausible, but these distinct paths
must not be collapsed into a claim that every margin failure creates a
Potential. Actual before/after gate counts and retained-photo outcomes
remain next-run evidence work.

#### Complete proposed entry matrix - pending user finalization

**Historical base table:** the front contract now selects these entry floors
with cast-only rival comparison and provisional ambiguity Review. In
particular, the cast 0.05 Review lead below is not a veto for selected
ambiguous Review placement. The older all-category routing recommendations
following this table are superseded for cast receiving, not current authority.

Numbers below are an AI recommendation for discussion, not saved defaults.
Separate Gallery lead from Review lead rather than lowering the shared
`photoRouteMargin` and unintentionally relaxing automatic Gallery entry.

| Destination category | Current Gallery score / shared lead | Proposed Gallery score / lead | Current named Review floor / lead | Proposed named Review floor / lead |
| --- | --- | --- | --- | --- |
| Sisters | 0.50 / 0.10, normal cast entry blocked | 0.50 / 0.10 | 0.30 global; normal individual cast path absent | 0.35 / 0.05 |
| Angels | 0.55 / 0.10, normal cast entry blocked | 0.50 / 0.10 | 0.30 global; normal individual cast path absent | 0.35 / 0.05 |
| Models | 0.50 / 0.15 | 0.40 / 0.10 | 0.30 / 0.15 | 0.30 / 0.05 |
| Prospects | 0.40 / 0.10 | 0.35 / 0.10 | 0.30 / 0.10 | 0.30 / 0.05 |
| Potentials | 0.40 / 0.10 | 0.30 / 0.10 | 0.30 / 0.10 | 0.30 / 0.05 |
| Artists | Separate domain; general entry off | Unchanged, separate domain | Separate domain | Unchanged, separate domain |

Review values apply to automatic named placement, not suggestions/search.
Artist candidates remain outside general identity competition. Various is
an unassigned source/hold pool, not another identity with an entry score.
Similarity and score differences are not calibrated identity probabilities.
Prospect/Potential score reductions and Model Gallery-margin reduction are
new recommendations, not inferred user approvals. Keep the existing
new-group count/resemblance rules for this proposed package; changing those
too requires its own explicit selection rather than following from this
existing-entry matrix.

#### Proposed routing order and acceptance before any expensive run

- Rank each candidate against all eligible frozen same-domain identities
  before applying destination thresholds. A higher rival remains evidence
  even when its Gallery threshold or receiving permission blocks a move.
  Do not cherry-pick a weaker destination merely because its threshold is
  easier. Category hierarchy is destination-specific gates, not a waterfall
  that tries cast and automatically demotes through Models to Potentials.
- Apply Gallery gates to the leading identity; if none qualifies, consider
  eligible named Review against that same all-category rival evidence.
  Review needs its score floor and0.05lead. It cannot take a photo scoring
  higher elsewhere. Example: cast0.40/rival0.34can enter cast Review,
  cast0.40/rival0.38cannot, and cast0.40/Model0.45cannot.
  Model0.45/rival0.37would miss the proposed0.10Gallery margin but could
  enter that Model's Review with the proposed0.05Review margin.
- Distinguish genuinely unmatched photos from plausible but ambiguous
  existing matches. Insufficient rival lead should produce an explicit
  ambiguity hold with alternatives, not silently generate a new Potential
  solely because named admission failed. Run new-group creation only after
  the explicit unmatched disposition; apply the count rules separately.
- Retain frozen core construction/floors and existing-member scope, source/
  crop/measurement quality, true locks/rejections, removal/merge/split
  protections and the reverse receiving-only cast run-lock contract.
  Incoming Gallery membership is not immediate core promotion. Existing
  Gallery low members remain audit-only unless separately selected.
  The later [upward-recovery clarification](#nov-18-upward-recovery-and-competing-fragments)
  identifies this unchanged source scope as insufficient for the user's
  goal; resolve its bounded expansion before calling this the final package.
- Before a full next run: finalize this matrix and cast support count;
  implement directional normal-path admission, separate Review controls
  and receiving-lock bindings; exercise boundary and current-cast-bypass
  regression fixtures. Use existing cached evidence for a read-only gate
  census where available; do not generate missing measurements or rebuild
  all viewers merely to select thresholds. Report unknown evidence as
  unknown. Preview exact initial cores and representative proposed outcomes.
- Next-run recap/audit must disclose leading/rival scores, separate Gallery/
  Review margins, reference counts, routing disposition and actual hold/
  new-group reason, with Various before/after and per-category entry totals.
  Count overlapping failing gates as well as final reasons; one first-fail
  reason must not be claimed as the whole cause. A combined package is a
  versioned comparison, not isolated causal proof for each changed knob.

#### Nov 18 upward recovery and competing fragments

**Later purpose correction:** the
[rebase outcome clarification below](#nov-18-rebase-outcome-not-an-optional-upward-add-on)
supersedes framing upward recovery as an optional extra pass. It is the
existing rebase outcome, not a newly invented goal. The bounded mechanism
below remains a proposal and must not redefine rebase as frozen-folder
intake with a few extra moving candidates.

**User clarification:** the next run should recover existing photos from
Models/Prospects/Potentials that belong in higher existing Galleries or
named Review, including photos currently forming separate identities.
Sometimes an apparent rival is another fragment of that same intended
identity. Merely opening receiving gates must not be presented as delivering
this outcome. RA2d owns the source/equivalence decision; RA2j owns any
selected candidate/rival/publication implementation and evidence.

**Current-code limitation:** `normal_rebase` skips frozen core photos as
references, then marks every other existing identity Gallery photo
`single-low-member-audit-only`. Only Various/Review reach the candidate
path. Existing lower-category Gallery photos therefore do not flow upward
just because incoming thresholds change. This applies even to photos
human review identifies as clearly misplaced. It also means the proposed
step5new-group fallback concerns eligible candidates only, not a rescan of
all existing identities. A genuinely unmatched new candidate can form a
new coherent group under classification rules; an unresolved existing
Gallery member must not be ejected or renamed merely for lacking a route.

**Proposed bounded scope for finalization:** add an upward-recovery pass
over eligible existing Models/Prospects/Potentials Gallery members, not
just their weak/non-core photos. A coherent fragment can contain genuine
members of the intended higher identity and score highly against its own
core, so low-own-score selection alone would miss the problem. Include
otherwise eligible lower-category core members as candidates using
self/duplicate-excluded evidence; do not silently make true locks,
user-named protected groups, anchors or workflow references movable.
Freeze comparison evidence, retain original ownership until a qualified
route is selected, and preserve rollback/identity history. Keep outgoing
Angel/Sister Gallery reassessment outside this bounded proposal. Upward
means qualified higher-category destinations, not category-preference
overrides that defeat a genuinely better different-person match.

**Rival identity is the second issue:** lowering0.10to0.05cannot resolve
a target0.58versus another fragment0.62, nor a0.58/0.57tie-like result.
Distinguish the source's own leave-one-out evidence, a separately recorded
same-person fragment and a genuinely different competing identity.
Excluding the candidate's own folder from a destination list is not proof
that another rival folder is the same person. Do not ignore every lower
category, drop arbitrary rivals, merge on lookalike/family association, or
promote an entire group solely on its average score.

Before final per-photo margins, preview proposed fragment-to-canonical
identity associations with independent/member-level evidence and explicit
approval/eligibility rules. Only a verified/approved same-identity mapping
can consolidate duplicate identity competition; it is not permission to
pool all fragment photos into trusted cast references. Retain true
different-person rivals and hold unresolved cases explicitly. A source
fragment may lose all qualified members, but preserve its history and
account for held/rejected/locked leftovers; do not delete or bulk-merge its
folder merely because some members qualify.

**Required next-run acceptance:** demonstrate an existing lower Gallery
member admitted upward, a coherent lower-core member considered rather
than skipped, a separately identified fragment rival handled without
silently overriding identity evidence, a genuine rival still blocking,
and an unresolved member retaining its source. Account for core/reference/
workflow safety and partial versus fully absorbed fragment outcomes.
Without these source and rival semantics, the current incoming-only
proposal does not meet the clarified recovery goal. No new runtime scope,
automatic fragment merge, threshold matrix or library run is implemented
or authorized by recording this clarification.

#### Nov 18 rebase outcome, not an optional upward add-on

The user reiterates that opening gates is intended to recover fragmented
existing lower identities upward. Preserving those fragments as fixed
owners/cores can let them compete for photos that should reunite above.
Do not run a threshold-only comparison before resolving this behavioral
gap. This is a clarification of the existing rebase objective, **not a
new requirement to defer behind another incoming-only run**.

The [established outcome contract](2026-11-09-likeness-process-reassessment.md)
already requires upward recovery, strong-identity continuity, same-person
consolidation and independently qualified reference growth. Its
[Nov10 implementation-gap finding](2026-11-09-likeness-process-reassessment.md#nov-10-1514-outcome-correction-and-numbered-delivery-phases)
explicitly distinguishes full-population scoring from full-population
reformation and identifies fragments competing as separate rivals. Current
SIMPLE's retained Gallery partitions do not deliver that outcome. Do not
describe this as user confusion or treat the old experiment's extra
machinery as automatically required.

**Behavior to settle before the next run:**

- Reassess eligible lower-category members, including coherent/core
  members, across their old folder boundaries. Old automatic partitions
  are hypotheses/lineage, not permanent ownership or identity truth.
  Preserve genuine manual intent, locks, strong canonical continuity and
  distinct authored cast slots. Do not physically dismantle the library as
  a prerequisite to planning a recomposition.
- Resolve supported same-person fragment/canonical ownership before
  treating those fragments as distinct rivals in final admission margins.
  Retain genuinely different rivals and unresolved contradictory evidence;
  neither dropping all lower-category cores nor category preference alone
  is a valid shortcut. Same-person evidence selects the higher-ranked
  canonical owner, not the other way around. Do not make manual approval
  of every photo or fragment an unstated prerequisite for automatic
  evidence-qualified recovery.
- Separate admission from reference use. Independently qualified new
  Gallery members may improve a later reference snapshot and recover
  further supported members. Named Review/tentative membership cannot
  supply those votes. Current frozen-once casting does not provide this
  second-wave recruitment. Discuss/select a bounded boundary-refresh/
  reconsideration rule with self/duplicate/circular support, false-merge
  and oscillation checks; do not silently promise unlimited cascading
  growth or import the entire experimental lifecycle.
- Build lower identities from the unresolved remainder only after the
  selected recovery/reconsideration boundary. Preserve source/history and
  unresolved existing owners in installed state until qualified outcomes
  are published; a planning candidate pool is not a physical eviction.
- Preview must demonstrate a lower fragment recovered into a canonical
  Gallery/Review, a genuine lookalike kept separate, and the selected
  reference-growth/reconsideration behavior with before/after core IDs.
  Explicitly report unresolved gates instead of claiming the numerical
  matrix alone meets the rebase goal. Reuse preparation and cached
  measurements where valid; do not spend a full run to rediscover scope.

RA2d owns this pre-run behavioral/numerical finalization under the current
spine; RA2j owns selected shared normal/rebase integration and tests. The
remaining reformation/experimental backlog stays holding unless a bounded
dependency is explicitly selected. No policy edit, source reset, new run
or final algorithm selection follows from this discussion capture.

The user owns identity/crop judgments and exact rule selection. AI prepares
source-bound examples, records results and implements only the selected
contract after its gate. Keep the following concrete items together:

| Item | Required review/decision | Owner and exit |
| --- | --- | --- |
| Incoming threshold hierarchy | Full incoming hierarchy now under review: cast0.50Gallery/0.35Review, proposed0.05Review lead, Model0.40and Prospect/Potential entry recommendations above | RA2d finalizes matrix and cast support count before RA2j implementation/tests/preview; earlier defer-Models/cast-only sequencing superseded |
| Incoming versus outgoing protection | Allow qualified incoming cast photos without treating protection against removal as a ban on all additions; distinguish real locks/rejections, workflow selections, anchors and reference eligibility | RA2d: documented action permissions and boundary cases, not a blanket flag flip |
| Strong cast-like groups given new names | Review saved high-cast-similarity groups, their individual photos/rivals and disabled group-cast Review routing | RA2d: target admission versus named Review versus retain/new-group dispositions |
| Low existing Gallery members | Revisit qualified reassignment of low Sister/Angel members, including workflow-selected photos, while preserving genuine locks and safely updating references | RA2d: explicit eligibility, evidence and reference-update rules; not unconditional whole-Gallery regrouping |
| Existing lower-category fragments that should flow upward | Receiving gates alone are insufficient: review eligible Models/Prospects/Potentials Gallery/core candidates and separately resolve same-person fragment rivals without suppressing true rivals | RA2d finalizes bounded upward source/identity-equivalence semantics above; RA2j implements/tests only the selected contract before next-run preview |
| Excess Potential formation | Review fragmentation, duplicate identity groups, small-group/singleton rules, group coherence and withheld cast admission before choosing adjustments | RA2d: explain which formations are wrong and why; separate clustering/creation rules from admission thresholds |
| Named incoming subfolders | Every user-named identity folder under Various is protected named intake, not just Ela Model. Preserve its name/group, qualify its core and allow qualified incoming members or flagged matches, including eligible low members of existing identities | RA2j bounded discovery/registration and receiving-path integration after current-run acceptance; RA2d source-eligibility/category/admission rules. No input/runtime changes during publication |
| Review evidence and GUI | Show original/current-native, own core and eligible rivals, decision reasons, score type and actual initial/final reference snapshots | RA2j machine readiness, then RA2d human outcomes; no implication that group scores qualify every member |

The full-hierarchy entry review above supersedes temporary cast/Model
Gallery equality as the proposed next comparison; final tuning is pending. The
canonical [policy](../../data/art/likeness-engine-policy.json) still contains
the pre-change runtime values until the selected contract is implemented.
Do not present selected defaults as already installed. Incoming similarity, rival margin, core
construction, group clustering, category assignment and photo-count rules
are separate controls.

In particular, raising the Potential **admission** threshold alone does not
directly prevent the creation of new Potential groups. Review the saved
109new Potential destinations containing Various candidates, including their
small-group classifications, before choosing whether the cause is intended
small-group handling, fragmentation, blocked cast admission or another
demonstrated error. A high count alone is not a quality verdict.

### Selected contract: named incoming folders establish protected identities

The user distinguishes **every intentionally named identity folder under
Various**, such as `Various/Ela Model`, from anonymous `Various/gallery`
arrivals. Ela Model is an example, not a special case or allowlist entry.
Treat each named intake as an explicitly supplied identity group, not a
bag of unrelated candidates. Discovery must distinguish these user-named
folders from maintained Review, derivative, duplicate and system directories;
do not turn operational storage into identities or silently skip ambiguous
folder roles.

- Preserve the supplied identity name and register one stable identity ID.
  Keep the folder's photos together as its initial membership; do not invent
  replacement names or scatter them into automatically formed identities.
  Preserve original filenames/paths as provenance through normal stable-ID
  naming and preparation.
- Protect that identity against automatic splitting, merging and removal of
  its supplied members. Category placement may be Model or Prospect under
  the applicable classification rules without losing the supplied name or
  identity ID. A word such as "Model" in the name is not itself a category
  assignment rule.
- Continue normal quality, core qualification and rival scoring. Named
  membership is operator intent, not proof every image is a valid reference.
  Exclude weak/unusable images from the comparison core when appropriate;
  expose concerns for review without silently moving them out or dismantling
  the protected group. An unavailable/incoherent core is an explicit review
  state, not permission to fabricate scores or discard the named identity.
- Keep permission to receive later photos separate from protection against
  removal; do not inherit today's incoming-admission blockade as an unstated
  consequence of preserving this group. Its qualified core participates in
  normal rival comparisons and can attract eligible photos from anonymous
  intake **and any other existing identity/category eligible under the normal
  domain and protection rules**, not just Prospects. A low-scoring member
  from any such identity may qualify for the protected named recipient;
  recipient protection alone must not exclude the match or block qualified
  admission. The Prospect-to-Prospect case is an example, not a source filter.
  Exact admission/category thresholds remain subject to the selected review,
  with no numerical change here.
- In the selected existing-member reassessment scope, apply normal source
  eligibility, genuine photo/identity protection, rejection history, quality,
  destination similarity and rival-margin gates before any reassignment.
  Flag plausible but ambiguous or blocked matches for review, showing the
  source identity, own-core score, proposed named recipient, rival evidence
  and blocking reason. Do not silently drop such relationships, force moves
  through real locks or merge whole identities. Preserve names, stable IDs,
  lineage and the already-selected safe workflow-reference handling.
  The intended gradual alignment is individual qualified recovery over time,
  not unrestricted core growth or global regrouping on every small import.
  Keep comparison references frozen for each decision pass.
- Reuse ordinary preparation, stable IDs, catalogue/protection records,
  core/rival scoring, publication/recovery and viewers. This is a bounded
  discovery/registration extension, not another experimental matcher.
  Same-name or stable-ID ownership conflicts need explicit resolution,
  never an implicit identity merge or overwrite.

**RA2j entry/exit:** current publication and machine/browser acceptance first,
then the selected T29/T30 performance slice. Named-folder integration follows
without retroactively changing the current run's source population.
Test named-folder discovery alongside
the root Various Gallery for multiple differently named folders, supplied-
name/identity/protection persistence, independent core exclusions with
retained membership, category/name separation, conflicting ownership and
idempotent re-intake. Include eligible low-member transfers from multiple
source categories into a protected named identity, with Prospect-to-Prospect
as one example rather than the scope limit, plus ambiguous and genuinely
source-locked cases that remain flagged without moving. Verify actual named-
intake files/catalogue/viewer treatment, including Ela Model, before claiming
delivery. RA2d owns the reassessment eligibility/threshold acceptance;
ordinary incremental intake must not silently become a global library pass.
Any unresolved low-count category behavior remains an explicit decision,
not an invented forced Potential rule.

### Review protocol and implementation gate

1. Use the verified baseline and existing reference/candidate evidence;
   include the strong Drakness/Helena group and contrasting accepted,
   ambiguous, low-member and small-Potential cases. Do not ask the user to
   manually sort the whole library or infer labels from scores.
2. Record stable photo/group IDs, current and suggested placements, original/
   native/reference links, score type, relevant gates and the user's exact
   judgment. Distinguish correct, wrong, both-compatible and uncertain.
3. Keep the initial-reference snapshot distinct from final GUI cores, and
   group-to-core scores distinct from individual-photo scores and margins.
   Preserve existing raw feedback and historical decisions.
4. Propose the smallest policy/code adjustment justified by those cases.
   Record expected recoveries and false joins, churn and remaining
   uncertainty. Familiar examples are development diagnostics, not
   independent accuracy claims; RA2d retains its evaluation obligations.
5. After user selection: canonical rule/policy documentation, configuration/
   tooling, focused tests and a bounded preview comparison before another
   apply. A visually plausible score is not publication permission.

**Exit:** explicit review outcomes, selected rule changes and an ordered
implementation/validation contract, with unresolved decisions still owned.
No tuning was applied while writing this plan.

## 3. Documentation housekeeping and next-session publication

**RA2o entry:** this focused plan is formalized and the current run's failure/
readiness evidence and resume state are stable. Keep review/tuning outcomes
attached as they arrive. Full housekeeping is a later bounded pass, not an
excuse to restart old experiments or block failure preservation.

**Nov19 guideline-structure selection:** Copilot skills remain in
`.github/skills/` for host discovery. Their canonical supporting guidance and
cross-cutting agreements belong under `docs/guidelines/`; structured YAML
belongs in `docs/guidelines/config/`. Move the assistant decision policy,
archive guide, change-management guide, quality gates and release checklist
there, using uppercase kebab-case Markdown names and lowercase kebab-case
YAML. Keep the documentation map, status/todo, game bible, planning agreement,
domain contracts and agent/skill entry points in their existing homes. This
is a navigation/layout change, not a rewrite of the governed rules. Preserve
source content and update all incoming links and generated readers.

User source:

```text
I want the skills in the right place for Copilot, but the supporting docs can be in docs/guidelines and move existing files that align to that there and the .yaml could go to docs/guidelines/config so they aren't directly in the .md files directory (if that makes sense), custom_layout=Answered in previous response.  But validate this and let me know the consequences.
```

**Nov19 bounded layout result:** moved the archive, change-management,
quality-gates and release-checklist guides into `docs/guidelines/`, with
uppercase kebab-case Markdown names. The assistant policy is there too; its
lowercase YAML matrix is in `docs/guidelines/config/`. Copilot skills remain
in `.github/skills/`. Updated the documentation map, project entry point,
agent/skill links, contributor/root README links, plan/recap references and
the todo generator; regenerated `docs/todo.md`. The 13 todo-report tests,
data-scope tests and routine checks pass. PR7's preceding selector-change
validation passed with 1,051 regression tests (5 skipped) and 53/53 isolated
mutations.
Of 883 local links scanned across changed Markdown, one target is an
unrelated pre-existing missing ignored report in the pinned recap; all
reorganization targets resolve. This closes only the selected layout slice,
not RA2o's broader contradictory/outdated-plan review.

**Nov19 scoped Copilot-customization follow-up (RA2o):** selected to reduce
always-on and per-specialist context without dropping procedures, role
boundaries or frontmatter/model/tool settings. Retain all seven agent roles;
move their task-specific methods into four on-demand skills with narrowly
selected references, while keeping only universal authority and safety rules
in project instructions. Extend quality guards to those skill entries and
their local references. Limit plan changes to this RA2o record and the
efficiency audit's adoption record. Do not include agent roster/model/tool
changes, D4's checker, broad documentation reconciliation or a token-savings
claim. Fresh-session, equal-quality behavior and actual context/call savings
remain a separate acceptance trial.

**Nov19 result and validation:** retained seven roles and frontmatters; added
four on-demand skill families and extended guarded metadata/reference/routing
tests. Copilot instructions are 4,365 bytes versus 11,863 before this
refactor (63.2% fewer bytes); the seven agent files total 7,174 versus 21,749
(67.0% fewer). These are file-size comparisons, not measured prompt-token or
cost savings. Final focused quality validation passed (11 gate, 19 selector,
3 isolation tests); routine hygiene/data checks passed. Full change-based
validation passed 1,051 regression tests (5 skipped) and 53/53 isolated
mutations. Fresh-session discovery/behavior and accepted-task cost remain
unverified.

User source:

```text
Once you move and get the existing things setup.  We can then address adding new skills, updating copilot instructions, agents and simplifying how we work as per some of my analysis.  That will help with my large token usage ... which might mean simplifying my agent .md files and leveraing skills for many more things and not sending all that documentation in on a prompt where it's not needing that skill for the prompt and can load them on-demand when necessary.  That's the huge improvement I need.   So - simplifying the C:\Sovereign-Territories\.github\agents and leveraging more skills as well as simplifying the copilot instructions but not losing anything.  Hopefully this is just focused on skills and selective documentation and doesn't require a huge update across existing plans - if some of that happens, I want to know the blast-radius of those updates.
```

Classify each affected current plan/task as implemented-and-verified,
implemented-but-unverified, selected-pending, holding/experimental, or
superseded with an explicit destination. Preserve existing task IDs, raw
Q&A, technical contracts and unique recovery evidence. Keep one current
execution spine; do not copy all historical experiments into this contract.

For each proposed archive, first dispose of every residual request and
record its owner. Only wholly completed/superseded plans can move, using
`git mv` and the [archive guide](../guidelines/ARCHIVE-GUIDE.md), with incoming links,
physical indexes and generated readers repaired together. Do not bulk-delete
plans, feedback, legacy tmp notes, live photo sources or run evidence.
Current navigation/status repairs are not completion of this wider cleanup.

**Nov18 source-preservation check:** all four current feedback files were
compared with their existing primary owners, preserving exact words after
normalizing line endings only. No source was moved or deleted:

| Retained source | Existing owner and disposition |
| --- | --- |
| `feedback/copilot_usage_analysis.md` | Reset spine's Nov5 source and collaboration-efficiency work; remaining independent requests stay under their existing owners |
| `feedback/explain_existing_steps.md` | Scope-test plan's exact-source/coverage section; SIMPLE foundation is selected here, experiments stay holding |
| `feedback/image_processing_inplace.md` | Same scope-test source/coverage section; independent in-place processing remains unselected, not silently implemented by SIMPLE |
| `feedback/gallery_review_11172006.md` | This plan's exact source and request coverage; original SHA256 remains `f513493d08d0e1c9b3d25880736660d9c21b607272db575b303c75d15db73447` |
| `tmp/rebase_simple_finish.md` | Protected historical reboot/run09 handoff; current resume lives in the pinned recap and this execution contract, not its superseded process instructions |
| `tmp/10292026_chat_handoff.md` | Protected Oct29 history; initial baseline/CI context inspected only, complete residual/source reconciliation remains explicitly **review-pending RA2o** |

These are preservation/ownership dispositions, not a claim that all source
requests, historical notes or the wider RA2o review are complete. No plan is
archived: independent deferred tasks and unique evidence remain owned.

**Exit:** a concise current plan/index/resume path, an explicit residual/
experimental ledger, no orphaned selected tasks, and validated links/status/
generated queue. Report preserved, transferred, archived and unfinished
separately. Do not equate filing with implementation or human acceptance.

### Commit/push gate

The user requests commit/push **if successful and ready for review**.
The latest request reiterates publication once the final Gallery/viewers
are ready. Machine/browser review-readiness is now met by the
[run13 closeout](#nov19-installed-run13-closeout); final repository hygiene
and grouped publication remain required. Human acceptance is still separate.
Do not blindly publish the whole dirty worktree. At initial inspection the branch was
`work/sandbox-rebase-acceptance`, HEAD
`d65ad58b9d04daa62fca0eafe837c6329bd18d78`, with152dirty entries and
pre-existing staged moves. Preserve their ownership; never stage everything
indiscriminately, reset unrelated work or bypass validation.

Before any qualifying commit/push, reconcile covered changes, run the
relevant supported checks, confirm the applicable review gate, and include
the required co-author trailer. Do not infer remote CI success from a local
check or claim a failed install is ready because documentation lint passes.

### Next chat: start here

Read this plan, the [spine](2026-11-05-priority-reset.md), the pinned
[handoff](../recap/2026-11-11-1141-recap.md) and the
[timed recap](../recap/2026-11-16-simple-rebase-recap.md).
Recheck run/process/worktree state and reuse `run09-apply-continuation` if alive.
Await its completion/failure notification rather than polling or starting
another writer. On failure preserve the exact step/producer evidence, trace
and fix the demonstrated issue, then use a supported controlled retry.
After apply/check/repeat, verify actual Gallery/Overview/Review/history in
the browser before claiming review readiness. Then prioritize bounded
T29/T30 performance work while human review proceeds; selected tuning and
bounded housekeeping follow their gates. No automatic Production publication.

## Primary user source

This message owns the three-activity request and conditional publication
permission. Earlier chat sources remain in the linked original plan.

<!-- markdownlint-disable MD013 -->

```text
Is the process still running or can I review what did happen - and in the meantime, I feel like those threshold probably need some tuning since the way it should work is Sisters and Angels should require a higher threshold than Models, Models higher than Prospects, Prospects higher than Potentials - but Potentials may need adjustments as I see we had so many Potentials form up and that also feels wrong - but I can do the review and we can tune, but we need to keep track of this in our docs/plans so we don't forget.  These are more concrete items to address than all the experiments that are in the docs/plans - so it almost feels like we'll need to do some housekeeping on our documentation as a whole as well.  So - 3 key activities.  1) We document the items we have just discussed in a new or the respective docs/plan depending if there is an existing plan that makes sense and it's full of extra stuff.  2) I perform the human review and help tune the items in the plan for next steps.  3) We need to work on housekeeping the existing plans once we get the new plan formalized and ready to go for another chat session.  We'll want to commit and push the changes if we see it's successful and ready for review.
```

### Timed baseline authorization chat

```text
Did we re-run with the performance and viewers as a baseline on where things are before we adjust the gates and configurations?

Yes - let's go with your recommendation.  Make sure that our plan is updated as we move along with these updates if you haven't done that yet.
```

### Nov 18 Various retention and sequencing chat

```text
But I can tell that some of them should match existing groups ... so we need more analysis on what that means.  But I also want to get to the next step in the plan.  Let's just log the unusable core analysis for after the next run -and we can or should pay attention to what is happening for those that stayed in Various - there are far too many that remained there.   Makes me think we had some issue during the process with so many images.
```

### Nov 18 execution authorization - verbatim chat

```text
Go ahead and implement the changes and move ahead with coding, testing, executing, debuggings and getting to a point I can review the final results and actual moves that happened.  You have full control to make decisions and keep going if you get blocked.
```

### Nov 18 grouped publication authorization - verbatim chat

```text
When you're confident we're at a good spot - we should commit and push all the outstanding updates with proper groupings and updates.  Thanks, and keep going with the entire plan all the way through actual runs, assuming you get it written, tested, debugged and ready to run and monitor it through the entire process.
```

### Nov 18 recap and final documentation request - verbatim chat

```text
Lastly - you need to write up the recap for today as well as updating older recaps and plans and docs.  Whatever is needed for all this work as the final clean-up and documentation exercise.  We keep making progress, so I'm happy - but things are slow going.  So keep on working until you're done.
```

<!-- markdownlint-enable MD013 -->

### Nov 19 core and duplicate policy follow-up - verbatim non-case excerpt

<!-- markdownlint-disable MD013 -->

```text
1) I think we might want to bump those thresholds up to 0.38 and 0.20 in preparation for the next run, just to exclude some lower scoring images that could possibly move out if we make them eligible in Sisters and Angels in our next runs - meaning to move cross or downward.  But that will happen later, for now - I just want things excluded from the core that are lower scoring.  2) If we end up with duplicate ID's I thought the logic was supposed to check if they are identical and move one of them to _duplicates and process the other one based on the rules.  If they are same id, but not byte identical (I may have used tools to alter them and send them in again) we'd take the one with the newest date and process that one (it could be in Various/gallery with a generic name) and we'd put the other one into _duplicates.  We'd track that in the processing and the reports so we know we had id collisions and I can review those in the GUI as well.  Ultimately we can't have duplicates as that'll contaminate the system like it did in this run.    3) When you talk about raising the review floor - what are you recommending to help with that.  If we address these issues, I think that the next run will be even cleaner.
```

<!-- markdownlint-enable MD013 -->

The source chat retains the named-photo case at the end of the message.

### Explicit continuation and monitoring authority

```text
Did the run finish now?  Or did you fix it and restart it like you should?
```

```text
Keep monitoring this and if we have issues, track them down and fix them so that you know that it finishes and the final viewers are working properly.
```

### Named incoming folder coverage question

Read-only inspection during run08 publication found11direct images and no
Gallery/Review children in both Source and Working `Various/Ela Model`.
The preview contains zero matching source rows or planned moves. Current
`photo_folders` stops descending a root once it finds that root's Gallery;
the rebase inventories only discovered folders' Gallery/Review buckets.
This is an inventory-coverage gap, not a likeness rejection or evidence of
intentional named-identity handling. Existing conservation claims apply to
the scanned Gallery/Review population, not every image at any nested path.
Record this under the named-incoming item above without changing live
runtime/inputs or mixing these11photos into the current transaction.

```text
So, while that is running - what happens to the images in the Various/Ela Model folder - do those keep her name or did they get skipped in this process?
```

### Named incoming identity and protection decision

The selected contract above resolves whether the supplied folder name/group
is authoritative intake intent. It does not certify reference quality,
choose new numeric gates or authorize mutation of the running transaction.

```text
What I want for those is to keep those as an identity and protected - since I named them separately from a Various/gallery as an intake - they could end up as a Propsect or a Model - but should get clustered together into an indentity - will that complicate the likeness process?
```

### All named intakes and qualified recovery from existing identities

The clarification broadens the named-intake contract to every user-named
identity folder, not an Ela-only exception. Protection preserves that
identity while its qualified core can receive eligible members and flag
plausible matches from other identities under the normal accepted rules.
RA2j owns discovery/receiving-path implementation; RA2d owns member-
eligibility and numerical acceptance. No current-run mutation is selected.

```text
It would be any named folder in Various - not just Ela Model - so anything that isn't Various/gallery is a named intake and we'd want that protected and the core should be able to draw in images from other identities based on the normal protection rules and flag things that might belong to this identity.  That will help pull low scoring photos from one existing Prospect into another Prospect who I know is a specific person and maybe over time that will help align things.  So add that to the work we'll do in the latest plan.
```

The source is explicitly any other eligible identity/category under the
normal rules; Prospect-to-Prospect is illustrative, not a restriction.

```text
It could be low scoring from any other identity - not just a Prospect - based on our normal rules.
```

### SIMPLE performance, publication and complexity/value request

The carry-forward inventory above distinguishes retained implementations,
missing normal-path integration and earlier prototypes. RA2j retains the
current readiness gate; existing performance owners retain bounded follow-up.
Commit/push remains conditional on that readiness, not exhaustive tuning.
The complexity guardrail is recorded here without claiming that permanent
memory scope has been confirmed or that performance fixes are delivered.

<!-- markdownlint-disable MD013 -->

```text
Did we lose all our performance optimizations and threading improvements when we went back to the SIMPLE processing and not just lose experiments - but went far back?  If so, that's fine - we just need to understand what else we need to add into the plan to optimize for the simple flow we're starting over with.  We should also commit and push once we get the final gallery and viewer ready for this run.  It's just we've got a lot of work to do to figure out what to bring back into the simple flow and tune it without having me go overboard again.  I want you to add a note to memory to question me when I am asking for overly complicated things that might not actuallly add real value to image intake and likeness processing.
```

<!-- markdownlint-enable MD013 -->

### Nov 17 performance priority and surviving evidence request

Coverage: T29/T30 are now selected in the spine as the next bounded AI work
after current-run machine/browser acceptance. The existing performance plan
owns reopened log measurements, delivered/prototype distinctions and the
confirmed isolated cache-scope probe. Readiness remains RA2j; human review
RA2d and housekeeping RA2o remain open. No runtime optimization was applied
to the active job, and conditional commit/push is not yet satisfied.

<!-- markdownlint-disable MD013 -->

```text
So - performance improvements are definitely back at the top of the list as this is taking just far too long.  Can you read the output report or logs if anything is still in place from all the performance and timing work we did.  I'll be sad if we lost all that when we went back to the simple approach.
```

<!-- markdownlint-enable MD013 -->

### Nov 17 recap/performance implementation and separate policy runs

The selected coverage table above owns every request below. The original
feedback stays in place, review-pending; preserving it is not filing it or
implementing its policy/grouping proposals.

<!-- markdownlint-disable MD013 -->

```text
Can we do both the performance and the recap reconnections and re-implementation where necessary some of the aspects are in my feedback document, but there are other things to do there separately or on separate runs so we can track progress and how those are changing runs.  But reducing the run-time and having the recap and audit are necessary to see what is actually happening and help me quickly navigate to see what the results are.  I added the feedback in - C:\Soverign-Territories\soverign-territories\feedback\gallery_review_11172006.md
```

Verbatim source: `feedback/gallery_review_11172006.md`.

````text
# Overview

This document provides a detailed review and feedback for the "Angels and Sisters" gallery, highlighting key observations, critiques, and suggestions for improvement.

## Angels and Sisters

This section covers the review and feedback for the "Angels and Sisters" gallery.  It includes general observations, specific critiques, and recommendations for improvement.

### General Feedback

Here's a few things I noticed that indicate we need to open up the Angels and Sisters for allowing photos to be automatically added to the gallery or into review.

#### Chiara Easton

- Chiara Easton is Drakness from my perspective and the scoring at the group level confirms it as the group scores the Sisters: Drakness 0.93 which tells me that some or all of the photos in that group should have dropped into Drakness gallery or at a minimum review.  
  - I did not check each and every photo to see how it scores individually against Drakness, but I'd wonder what would have happened if the gallery had been open for Sisters and Angels.

#### Sia Abernathy

- Sia Abernathy is Drakniss - scoring Sisters: Drakniss 0.77
  - Similar to Chiara Easton, this indicates that some or all of Sia Abernathy's photos might belong in the Drakniss gallery or at least be reviewed for potential reclassification.


#### Zoe Bishop

- Zoe Biship is Drakniya - scoring Sisters: Drakniya 0.60
  - Similar to the previous cases, this suggests that some or all of Zoe Bishop's photos might be more appropriately placed in the Drakniya gallery or should be reviewed for potential reclassification.


#### Cressida Joycek

- Cressida Joycek is Drakniya - scoring Sisters: Drakniya 0.66
  - Similar to the previous cases, there is one photo in that group that is truly Drakniya as it scores Sisters: Drakniya 0.74 and that makes me think it would have landed with Drakniya instead of Cressida.  This also makes me think that other photos in Cressida would land somewhere else based on losing that image into the identity cluster.
    - Photo ID: 7518413273886433101 
    - Identity ID: person_92ded2807fcc461abe046b95f43fe213

#### Aria Ingram

- Aria Ingram is Draknora - scoring Sisters: Draknora 0.92
  - This is a much stronger case where I think all those photos would have landed in Draknora if we get the values to join the gallery or review set properly and allow admittance to those identities.

### Existing Cleanup

- In some cases there are photos in the Angels and Sisters that are there mistakenly and contribute to the core.  What I don't know is if those photos were released to pool and score separately if they would return to the Angel or Sister or find another identity.  And potentially that identity scores high enough to group and then they either end up there through that process OR they join or form a different group.

- It's sort of the phaseed process that I had always envisioned, where we'd release the lower scoring images in the Angels and Sisters galleries to the pool, allow them to be scored separately, and then see where they naturally group based on their identity scores.  This would help ensure that photos are correctly classified and that the core identities are not contaminated by misclassified images.  This would also include having all Models, Prospects and Potentials in the pool as well the rebase would "start fresh" for likeness and if based on the scoring and gates fall back to their own previous identities, that's fine - however, I know there are some that will move and I believe that'll have a larger impact on which groups do form and what their scores are. 
- Then while we're forming the closest by category for groups, we'd use those numbers to automatically re-assess the photos in that group against the highest rival group and instead of re-doing the entire pool we'd basically look at how we promote images from the group that is lower in the category hiearachy (Sisters, Angels, Models, Prospects, Potentials) to the higher group if they meet the necessary scoring thresholds.  This needs to be supported by the fact we can add other categories down the road and it's not a fixed hierarchy.  That was also capability we did add and could have lost in going back to the simple approach.  If we don't move all the photos - we need to recast that group and/or re-evaluate its composition to ensure it accurately reflects the identities it contains.
- Finally, I would do a review of all groups and look for the low scoring images that are potentially misclassified or do not strongly belong to the group they are in.  These images should be re-evaluated against other groups to see if they fit better elsewhere, ensuring that each group accurately represents the identities it contains.  The reason for this is that we might have photos that scored high in the group at one time and then lower over time as photos are added or removed (like in the group to group joining scenario and we don't move all images).  So that's where I thought we could identify those candidate photos and take action.

Basically, after the initial grouping and scoring of photos, we would go through the process of re-evaluating low scoring or potentially misclassified images, promoting images to higher categories if they meet the necessary thresholds, and ensuring that each group accurately reflects the identities it contains.  This iterative process helps maintain the integrity of the galleries and ensures that photos are correctly classified over time.

I feel like this approach still falls in line with the simple and doesn't have all the experimentation with family names and such.  If we support the logic for Models instead of just Prospects and Potentials, that's fine as it further will help identify group to group relationships for me without including all that experimental work we were doing with appearance groups and family names.  I think the appearance groups went to far and that was part of my over-complication of the process.  At least that's one thing we can likely abandon.


### Prospects and Potentials

In general, I feel like we have too many Prospects and it's likely we need to adjust those threshold and allow them to cluster together more than they are, which will also change the group to group scores against other identities and hence things could merge and/or split based on the second phase of the grouping and refinement.  Basically, I think that all of our gates need to be re-reviewd and updated through a series of runs.  Not all at the same time.   

### Recap View

Do we still have the recap of who-went-where GUI for a run so I can see who did go where based on the changes.  That's the easiest way for me to understand each step and what did happen.  There's some enhancements I needed to that recap view but at least it was helpful.  Basically the navigation links should be opening new tabs when clicking on a link about another identity and not linking within the document if the intent is to open up the Review page for the identity.  There are some links that should link within the recap document to the proper section.  So it's something we'd need to tackle on a case-by-case basis if you question whether or not the link should be within the recap or open up a separate review tab.  I think if you do analysis you'll figure out 90% of the cases and I can answer the ones you aren't sure about.  

### Automated Audit

I don't know if the automated audit exists any more and if it does what I really want.  Essentially, the automated audit should be looking at photos assigned to groups and whether or not their placement is appropriate based on the various rules we have in place.  Essentially, it can call out if we have protected photos in groups that are scoring low and might need to go elsewhere.  It can tell me if I am using a very low scoring workflow photo for an identity - which may also be influencing the core of a group OR it's not going to render in ComfyUI like the other photos for that identity.

There was more the audit was looking for - but essentially, it leads to the refinement of what the audit findings are and instead of me having to "manually" do the recommended adjustments, it could just apply the recommended changes from the audit instead of just a preview and report.  Then the audit would include what those changes are in the recap of who-when-where based on the audit.

### Summary

I did not do an exhaustive review as I feel like what we need to do is to address the issues one-by-one because the way groups are formed would likely be different once we get the Angels and Sisters setup to allow admittance of photos to the appropriate galleries or review sets.  That said, with the scoring - I am allowing for photos to be automatically added and if they score high enough they would be added directly and if their core score was very high they would also be included in the identity core and if lower they are in the non-core but automatically added and not put to Review.  Review is for the real exceptions where a photo doesn't score high enough elsewhere and hence it would land in Review for an identity that was closest instead of forming a potential.

From that perspective - I feel like the auto-admittance of photos that score 0.50 and higher directly into the gallery and other items that are 0.30 and higher into review if they aren't directly into another identity.  I know we have the gates and logic to allow that to happen, so we should be able to implement and do another run to see where things group after we open that up.

So I think we do the following in a series of runs:

- Reconnect the recap gui of who went where for a run so we can track the changes and understand each step of the process.  We don't need a re-run of this unless it's fast.  Otherwise we move onto next step.
- Address the performance implementation aspects and verify those are working the way we expect.  We'll need to be smart about how we make these implementations since the runs will still take a long time on this machine and until we get it working I don't feel like switching to a new machine that is not setup properly with tools and utilities is smart.  
  - If we have the recap gui here, we can then see the results of how things work in the current configuration and where the admittance of photos is occurring, allowing us to verify that the rules and thresholds are being applied correctly.
  - If we had the audit in place, it would also show us the key items I did find (and likely more places where the images and groups would change if we updated configuration settings).  Basically at this point I can use the audit and my own findings and compare the results in subsequent runs against this baseline to see how the changes are impacting the overall grouping and placement of images.
- Adjust the configuration for Angels and Sisters to support the findings above and allow for the admittance and automatic placement of images into the gallery and last resort to review - based on the rules.  We'd then rerun at this point to see just what impact that has with the groups as a whole and where images land, who would be retired, what would group with other Models, Prospects and Potentials differently. 
  - This is where the recap gui and audit will tell me what happened as well as if there are things where the refinement process might be useful.  We can compare this recap and audit against the one prior to see the differences and understand the impact of the changes made.
- Adjust the configuration for Prospects and Potentials to allow them to open up a bit more and see how those clusters form and if that also impacts the group to group relationships with other identities.
  - This is also where the recap and audit will be helpful to see what happened after we made those changes and whether things are "better" or "worse" for those groups now.  We can use this information to further refine the configurations and thresholds for Prospects and Potentials if needed.
- We might need to re-adjust things and rerun until we get things the way we like and we'd see just how many group to group relationships are changing and the group to group re-assessment as well as the image refinement within groups is necessary.  That said, in a non-rebase scenario, I feel like the group to group and refinement process are needed in cases where all I am doing is ongoing maintenance and bringing in new images.
  - Maybe the group to group and refinement aren't needed for the rebase directly, but longer term that is what was happening and why those came into existence.
- At this point we'd have a "stable" process for the rebase.  
- Then we could consider the group to group process and how that would adjust things as a whole if we did support the automatic group to group merging and splitting based on the updated configurations and thresholds.
- Finally, we'd look at the refinement and audit process


````

### Nov 18 cast defaults and core question - verbatim chat

```text
I honestly think that 0.50 is better for Gallery and 0.35 for Named review if not higher for another identity.  We'll lower the Models in the next iteration.  We don't want to pull images into an Identity review if they are matching higher elsewhere.  Only when they aren't matching else where with the margin.  What do you think of what and how do we adjust all the settings to allow this to happen.  I would like it as defaults and not have to override with parameters.  It should be a reverse command line override to lock the Sisters and Angels from a run.  I'm also curious about what images will make up the core when we do the next run - if it's the full existing gallery or it's the top scoring ones in the gallery.  That makes a difference in the formation of what will come in - I suspect, right?
```

### Nov 18 full-hierarchy entry review - verbatim chat

```text
I don't know if the gallery admission gate of four indepenent references is right either - how does that impact the scenario or explain that back to me as I think that it's a potentially an issue.  I also think the Review rival needs to be 5 instead of 10 ... especially if the model drops things, so maybe we also need to adjust the Model score to 0.40 for entry and then look at Prospects as well.  From what I can see the gates are pushing too many images out into Potentials that like did meet some other gates, but the rival forced them out.  At least that's what it feels like.  Let's re-review the entire set of change we would be making.  Focused on the entry and how it all works again.  Then we can finalize what tuning we'll do for the next run and let's include all the hierarchy in this next review - because the runs do take so long.
```

### Nov 18 upward recovery clarification - verbatim chat

```text
I think I agree with the flow, with one clarification.  In your step 5 of the entry, what happens to those images that so fall down and are unmatched? If there are existing Models, Prospects and Potentials and we open the gates up - will those images flow upwards and be admitted to the higher galleries.  The reason I am asking is that existing images that should land upwards have created separate identities and what I am trying to ensure in this run is that we open the gates for entry enough that those flow up into the Gallery where they below or into Review if they are close enough.  Sometimes the rival score that prevents entry is because that Rival should also be pulled upwards into either the Gallery or into Review.
```

### Nov 18 rebase purpose correction - verbatim chat

```text
So, the point of opening up the gates IS to allow those fragmented identities that fell down and formed new Models, Prospects and such to most upwards - that's the point of what the rebase is intended to do.  So if we don't unlock and allow that upward movement of those images they will pull other images downwards that should have moved upwards - especially once those images landed in the core of a high level category and that might attrach more lower ones.  So if that's not what a rebase will accomplish - even the SIMPLE one, then we need to keep discussing what needs to change before we open up the gates and do the run.
```

### Nov 18 foundational next-step refinement - verbatim chat

```text
So what do we need to discuss about next steps and get that plan refined so we can make those updates prior to the next SIMPLE run.  It should focus on these foundational issues we just discussed and not bring in all the experimental aspects.  If we can simplify how the rebase is working as you described, then hopefully the outcome will be a much better result and the fragmented rivals won't exist in the way they do now.  There may still be some based on the gates, but if we implement the plans you described we'll be in much better shape.
```

### Nov 18 implementation authorization - verbatim chat

```text
I like that - so what is next for us to discuss or have you written up the detailed steps and we can get the implementation started.  You can stop and ask questions while doing the work if we stumble on something as we go.
```

### Nov 18 permissive admission and sequencing clarification - verbatim chat

```text
Sorry I was away, but I would actually allow a permissive move based on the rules and gates we define.  Meaning if something does hit the 0.50 rule that I'd want it to enter and not be left outside.  I think that would be more prudent given the existing fragmentation and we'd not solve the downstream impacts of moving things.  So, this also makes me think that the first step to addressing the issues is to ensure in the first run we do move things out before attempting to assess the new Various items coming in, unless those items when added also support upwards movement.  I don't want to change the process we defined - just want to assert I am ok with allowing the images to move into the Gallery if they do meet the gate.
```

### Nov 18 ordering selection - verbatim form response

```text
existing-first-with-qualified-arrival-seeds
```

### Nov 18 cleanup priority and temporary rival-bypass question - verbatim chat

```text
Ultimately my goal is to take any fragmentation that exists and push them upwards and not let their existence create a conflicting rival score for other images because it exists already as a fragment that fell downward in a previous run with high gates and the fact that angels and sisters were locked and prevented admittance.  Some of those mistakes got us to this place and that's where the SIMPLE rebase run is targeted to just fix that as the priority.  All other experiments can come later to improve and advance things, but for now I am focused on cleaning things up and making sure we don't have artificial rivals that block entry due based on the gates.  One option I had consisted was to bypass the "rival rule" on a run and just use the base likeness score and only use those rules once we address the fragmentation.  Would that help in the situation we are in?  As a temporary push of images upwards?  Or does the process we just defined work well enough that we can leave those gates in place.
```

### Nov 18 cast-only rivalry and ambiguity Review question - verbatim chat

```text
I am ok if the Rival score is against Sisters to Angels so we then have to decide, but a rival against the fragmented Models, Prospects, etc... that needs to be unlocked to prevent that rival from blocking entry into a Sister or Angel.  In the future we could lock Models in the same way, but for now I agree that the conflict score between an Angel and Sister needs to be worked through and I guess the question is - does that become a rival or we put it into review of a Sister or Angel to prevent it from forming it's own fragment that attracts others like it and then prevents entry?  I guess that's the question.
```

### Nov 18 ambiguous cast Review selection - verbatim form response

```text
provisional-best-cast-review
```

### Nov 18 optimistic non-core Gallery and rival-distance question - verbatim chat

```text
I think that's the best plausable plan at this point and we can work the implementation all the way through - unless you figure out more issues.  If we find out way too many photos end up in review - then we'll have to adjust the rules.  That may happen with Drakness and Nyxene as they are very close and similar - on purpose for the story and I might just end up loosening the rules a bit on gallery admittance as a non-core image instead of review AND as I type this, it actually makes things easier of we do that - because at that point it's a toss-up on even if I can decide and my path is like just to approve the gallery admittance from Review and it makes things much more complicated.  So maybe the rule is about how the two identities score against eachother and if they are so close themselves then it might not matter.  But if for some reason the Sister and Angel aren't really that close - then a Review is in order.  If that makes some logical sense - look at the "distance" between the two Rivals for the image.  Maybe my brain isn't working and that's a complex cross-check.  But allowing for optimistic gallery entry is likely better as long as they are non-core members, not protected and flagged as having a high rival score with some border or icon to indicate that it might not belong to this identity and I need to confirm it.  The Review should be more much more tentative cases where there isn't a rival and we're just not sure if this is or is not the identity.
```

### Nov 18 close-identity rule selection - verbatim form response

```text
approved-pairs-first
```

### Nov 19 duplicate archive and protected-Gallery clarification - verbatim chat

```text
We definitely need to deal with duplicates and the process must move one of them out to _duplicates and not allow two to exist during a run.  That's my mistake in trying to replay a bunch of existing that I might have altered and just to force Various to have a bunch more things and check that our duplicate logic was working right - which apparently it's a gap right now as it forced fragments to be left behind.  It was always my expectation that we would never have two of the same id's co-existing in an ambigious state.  That's probably a conservative decision made while I was away and not able to answer.  Don't lose track of the work you're doing - but we do need to fix this and as long as something lands in _duplicates and it's in the recap and I can see that in the GUI somewhere - then we are ok.  That's why we're running this all in the sandbox to work out this minor kinks in our processing as a whole.  But that last round was so much better in terms of reducing some fragments.
```

```text
If it conflicts with a protected gallery photo, then I would still want one to be put into duplicates and not stop the run.
```

```text
I say that because as long as they have gone through image processing, they should get the clean-up that I might have done by hand and ultimately I get a single "good" photo to use.  Some existing ones that are protected might have had logos, icons and overlays - which I might have tried to fix by hand prior to the image processing.
```

### Nov 19 replay baseline and test coverage - verbatim chat

```text
If they weren't in Various/gallery at the very start of this rebase - then I would want them left where they were as part of this run.  Basically I want to get to a point where the results of the intake matched what was in the snapshot of the copy of Production and run from there.  If we had previous image id duplication in Production, then I want to see how this will clean that up as well as deal with the fact I put duplicate copies into Various/gallery - both scenarios are valid to prove out in handling the duplicates properly.
```

### Nov 19 approved baseline replacement and future intake - verbatim excerpts

```text
In terms of the duplicates, if the file is in Various Gallery and it does not match the original - then I did clean it up by hand and did intend for it to replace the original one, keeping a copy of that one.  Even if it was a protected one.
```

```text
So you are free to verify the script would preview and then apply it when you are done.
```

```text
Meaning, double check items in the Various/gallery for being exact duplicates and just "discard" them and not even store them ahead of time?
```

```text
So, even on a rebase with items in Various/gallery that are exact copies, we can discard those and not backup or make them duplicates.  Duplicates to me are different ID's but same bytes vs. same ID (different name) and same bytes.
```

```text
You are free to run and actually apply all changes if we need to run or re-run anything to get me to the point I can do the review of the outcome of all our updates.  Thanks again, commit and push when done and at a solid point - even if waiting for my review.
```

### Nov 20 Review and Various dispositions - verbatim excerpts

The image-specific identifiers remain in the local conversation and run
receipts; they are not duplicated in this tracked excerpt.

```text
We should allow review folders to group normally as a brand new photo.  If it's there and I haven't done anything with it - we don't need to lock it there in a fugure run.
```

```text
Identical bytes under a different ID should have been moved to _duplicates and not left in Various.  How can things lose their core - that seems like a major issue - does it not?  The one without a usable face should be _junk.  I thought we had rules to cover all these items and not to leave things in the Various folder.
```

```text
Do we need a rule to catch those 80 and move them into dups?
```

```text
Yes, let's do that we just need to keep fine tuning things
```

```text
Each run is getting a bit better than the last run ... I'm glad we stopped the experiments and went back to the basics and doing the SIMPLE flow ... I was too far off course with all the experiments at the time.  They will be useful later - like ensuring there is an audit to catch things like we're finding and flagging if something is left in Various and why, checking for images with higher rivals somewhere other than where they are at - mis-placed images.
```

The [new-PC handoff](../recap/2026-11-11-1141-recap.md#new-pc-simple-rehearsal)
records the replay recommendation and how to make a comparable timing run.

```text
Can we write up a hand-off for a new session, on my new machine to pick-up where we are at now and to run the next commands to re-run the rebase again and test out a few things - like checking on performance to compare against our runs and how long things take?  Or should we spend time to re-run on this machine before we do that?  I guess that's my question ... I suppose we could re-run things on both in parallel as well.  What do you think?
```

<!-- markdownlint-enable MD013 -->
