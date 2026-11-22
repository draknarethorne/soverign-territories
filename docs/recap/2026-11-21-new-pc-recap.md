# Nov 20-21: new-PC setup and SIMPLE rehearsal

This is the new machine's dated evidence, not a second execution queue.
The [planning agreement](../plans/README.md) and execution spine retain
current ownership. The user reported another machine's process was still
active at 08:01 Central on Nov 21; this machine cannot verify its state.

## Nov 22: fresh post-intake rebase

The fresh Sandbox rebase `fresh-post-intake-20261122-04` started from the
verified post-intake state and released 250 photos before identity formation.
Ordered timings are as follows. The preparation was reused under an origin
seal; historical preparation time is not included.

| Step | Purpose | Time | Counts |
| --- | --- | ---: | --- |
| Baseline restore | Frozen Source to new Working; old tree kept | resumed | 11,048 files |
| Various cleanup | Reviewed + exact-only copies | ~2 min | 1,795 + 180 + 4 |
| Source inventory | Bind source bytes | 33.3s | 3,490 rows |
| ID normalization | Stable IDs, versions, holds | 0.2s | 3,284 inputs |
| Preparation reuse | Verify sealed natives | 35.5s | 3,306 inputs |
| Fresh measurement | Centering population | 1.6s | — |
| Release selection | Initial own-core release | 12.6s | 2,412 assessed; 250 released |
| Frozen cores | Cores without released photos | 64.7s | 106 cores |
| Two-round admission | Route candidates | 8.4s | 2,137; 629 placed |
| Member check | Bound admission audit | 12.8s | 3,293 moves |
| Publication | Stage, transaction, viewers | 77.7 min | 3,293 moves; 184 archives; 1 junk |
| Rebase check | Verify receipt | 30s | 6 viewers |
| Folder retirement | Emptied Potentials | 1m54s | 89 folders |
| Viewer refresh | Post-retirement Gallery/Review | 17m09s | 3,305 photos |

Publication and the viewer refresh each spent about 17-18 minutes resealing
30,785 viewer inputs (15.5 GB). Released photos went to 100 named Galleries,
62 named Reviews, 18 new identities and 70 Various Review (single-face
quality failures). Remaining flags and decisions are in the
[focused plan](../plans/2026-11-16-simple-review-and-tuning.md#nov-21-red-member-release-planning).
Production was not changed.

## Nov 22: integrated release preview

The corrected Sandbox rebase has not been applied. Four previews stopped
before publication; expanded-hold preview `corrected-release-rebase-20261122-04`
verified 20,774 source files and found 14 released candidates ineligible under
the single-face quality gate and 11 still held after independent residual-core
scoring. The 219-photo cohort still needs truthful routing,
retirement, a complete movement report and installed viewer acceptance. The
[focused plan](../plans/2026-11-16-simple-review-and-tuning.md#nov-21-red-member-release-planning)
records the sealed preparation and next gate. The combined rebase,
reconciliation, import, movement-history and retirement suites passed 290 tests,
and `bin\check.cmd` passed; those
fixtures do not establish installed acceptance. No rebase writer remains, and
Production and shared workflows were not changed by these attempts.

## Setup and synchronization

1. Set up Python 3.14.10, the processing virtual environment, Node,
   pre-commit, PSScriptAnalyzer and local face/intake model weights.
   Earlier full validation passed; at the time of writing, setup and
   documentation edits were local, not in this recap's original commit.
2. Developed project-local decision guidance and a bounded on-demand skill/
   agent simplification. At the time of writing, those changes were local;
   fresh-session discovery and actual token savings were not measured.
3. Pulled the other machine's branch changes through commit `4439368f2`,
   preserving local work and reconciling overlapping documentation. The
   original four staged guideline renames and backup stashes were preserved.
4. Configured this machine's ComfyUI roots on B: and deployed 252 existing
   Drakness workflow JSONs to each of the Drakness and Drakn Sisters
   workspaces. This deployed existing files; it did not regenerate workflows
   or render images.
5. Before committing, full validation exposed workflow tests inheriting
   those real root overrides rather than their throwaway paths. Isolated the
   test module's root environment, added a hostile-override regression, and
   reran all 80 workflow tests successfully with the machine overrides set.
   The test fixture workspace names did not exist in the real installs root.
   The full regression run then found an unchanged baseline test expecting
   an Angels core threshold of 0.30 while the checked-in policy is 0.38.
   It also failed in isolation. A follow-up corrected the test to check the
   configured policy threshold; runtime code and policy were not changed.
   The rerun of `bin\validate.cmd` exited 0, including 1,076 library tests;
   machine-root overrides were removed only from that test process. The
   earlier isolated mutation pass was 53/53.

## Clean Sandbox rehearsal

The copied run15 was preserved separately. The frozen Source manifest matched
the historical SHA-256 and all 11,048 files passed the frozen replay check.
The cleanup plan initially failed its expected hash; after the user recopied
it, its SHA-256 matched. The Sandbox-only cleanup passed preview/apply/check
for 1,795 exact copies and 180 replacements, followed by a reviewed four-copy
exact-only cleanup and a zero-candidate rescan. Displaced originals were
retained. The resulting 1,069 Various Gallery inputs and all 3,490 input
paths and SHA-256 values matched the run15 preview inventory.

The first fresh preview was stopped for the user's shutdown request after
161/3,285 preparation rows. Its log and interrupted state were preserved.
After restart, fresh-cache LEAN `simple-newpc-lean-20261120-02` completed
preview in **1h47m47s**, exit 0.

The user then authorized Sandbox apply after preview validation. The first
apply exited 1 after **56m10s**, before the publication transaction:
the direct-script launcher encountered a package-relative import error.
The failed log and staged publication files were preserved. A narrow local
import fix reproduced and resolved the error; 89 affected rebase/recap tests
and routine checks passed. The code fix was uncommitted when this recap was
written; check the shared revision to confirm whether it has been transferred.

Because the fix changed the implementation binding, new preview
`simple-newpc-lean-20261121-03` reused the origin-sealed preparation under
its recorded manifest hash. It completed in **6m28s**, exit 0, and its
assignments, moves, holds and dispositions matched the previous preview.
The validated Sandbox apply completed in **1h15m29s**, and check/repeat in
**30.9s/29.6s**, all exit 0.

The applied report conserves 3,490 sources to 3,490 distinct destinations.
It records 184 recoverable distinct-ID duplicate dispositions and one
recoverable zero-face junk disposition, with no cast Gallery departures,
unresolved duplicate IDs or stale snapshot diagnostics. The applied Review
snapshot matched 3,305 destinations; the other 185 are those dispositions.
An isolated local browser loaded representative Gallery, Overview, Review
and recap thumbnails, a current Nyxene native, Draknara intake detail and
native history. Human identity and crop acceptance remains open.

## Performance and limits

Run15 on the other machine recorded 4h39m preview and 4h33m36s apply. Those
are historical context, not a paired hardware comparison: code revision,
machine, cache state and other bindings differ.

Three sequential LEAN sidecar trials used the same 24 installed images and
passed their checks. Compared image hashes and outcomes matched:

| Workers | Wall time | Scope |
| --- | ---: | --- |
| 1 | 43.7s | 24-image sidecar preparation |
| 2 | 28.7s | Same installed inputs |
| 3 | 24.5s | Same installed inputs |

These are small, sequential trials on installed images, not whole-rebase
measurements. SIMPLE defaults to one preparation worker; a later opt-in
worker control is recorded in the
[performance plan](../plans/2026-10-28-intake-performance.md#nov-21-per-machine-tuning).
No default or GPU setting was changed. Broader tuning and paired measurements remain
with the existing performance owners.

### Later implementation and tuning

The saved-run audit now flags red own-core scores and suggests same-owner
non-red Gallery candidates for a workflow-selected red, without claiming
workflow eligibility or moving a photo. The matching saved snapshot has
seven red and 329 unscored records among 3,305 matched destinations.
The separate Sandbox report
`Working\_reports\library\red-snapshot-audit-20261121-v10\snapshot-audit.html`
passed its saved-input/output check and loaded in a local browser with seven
red rows with planning-reference context, photo-protection provenance,
expandable matched Review-core records and one workflow-candidate row.
The separate Artist domain is not included.
After a workflow-helper edit made v10's producer binding stale, a separate
v11 report passed preview/apply/check and its structured evidence was
verified; v10 was preserved. The v11 report was not independently
browser-inspected:
`Working\_reports\library\red-snapshot-audit-20261121-v11\snapshot-audit.html`.
The next structured-evidence change made v11 stale. The separate v12 report
passed preview/apply/check and contains 39 native-bound same-owner replacement
candidates; its page loaded in a local browser with the red count and
unverified-eligibility warning:
`Working\_reports\library\red-snapshot-audit-20261121-v12\snapshot-audit.html`.
The v13 report superseded the then-stale v12 producer binding after fixing
candidate discovery when current configuration and saved workflow flags
differ. Preview/apply/check and the structured counts passed; the page
loaded in a local browser with the red and eligibility notices:
`Working\_reports\library\red-snapshot-audit-20261121-v13\snapshot-audit.html`.
A later action-helper edit made v13's producer binding stale as well; retain it
and retain the separate v14 report, which passed preview/apply/check with the
same seven red, 39 workflow-candidate and 336 native-binding counts:
`Working\_reports\library\red-snapshot-audit-20261121-v14\snapshot-audit.html`.
The v14 page has not been browser-inspected.
The opt-in `--bind-red-natives` check rehashed and bound the seven red photos,
their 317 matched Review core rows and 39 workflow-candidate rows: all
336 distinct current natives matched the saved hashes (228,748,441 bytes).
It is not a bound release preview or eligibility proof.
The optional workspace configuration inventory found one red-linked base
selection and 12 selections without identifiable photo IDs. The configured
production root differs from the Sandbox; actual workflow files and consumers
were not inspected or changed.
Subsequently, a read-only preview using the existing retarget routine found
three matching recognized repository workflows and none in five ready
workspaces; two workspaces were inactive. Its scope excludes additional
LoadImage nodes, hand-made files and other unrecognized consumers. No
workflow, input, configuration or workspace was changed.
A broader bounded read-only JSON-string scan covered 5,417 distinct
repository files and 504 ready-workspace files, including nested and
hand-made JSON. It found seven occurrences in three recognized repository
workflows and the configuration, none in ready workspaces. Inactive
workspaces and archives were excluded; this does not prove complete consumer
coverage. The fixture-tested string scanner is not yet a transaction.
The checked report manifest now carries structured red and matched-core
evidence; it is not a release manifest.
Fixture-only red routing and reference retirement exist but are not wired to
a release. A fixture-only adapter rechecks the saved audit before planning,
validates core consistency and candidate conservation, and proposes explicit
unassigned Review holds. Against v14 it correctly refuses the configured
Production-root mismatch; measurement provenance and consumer coverage remain
unverified for the complete routing population. A root-local cache-only check
reproduced all seven red saved scores within `4.17e-17` using one recorded
model identity; rival inventory and current model binaries were not verified.
The fixture-only adapter now also checks caller-supplied routing vectors,
quality and native hashes against that cache, without claiming the caller
supplied every rival or the complete centering population.
An earlier Gallery inventory and routing diagnostic is invalid: it inferred
measurements for 16 people Gallery photos that the applied receipt classifies
as non-voting. The checked report binds 21 unchanged non-voting Potentials
Gallery photos, including those 16. After excluding them, the rebuild stopped
on an identical prepared-byte pair whose different source photos were both
eligible in the saved run. An opt-in, fixture-tested use of the existing
same-owner keeper rule produced 197 cores and 2,411 references, with no
supplemental inference; six reds proposed unassigned holds and one was
workflow-blocked.
This is not a bound or executable release preview. A read-only reconstruction of
the 3,284 eligible prepared sources found 3,282 usable at the current
60-pixel minimum and reproduced the saved centering mean within `3.47e-16`;
the retained manifest and cache remained unchanged. A fixture-tested helper
now repeats that checked reconstruction. A separate read-only replacement
proposal verified all 39 candidate scores and both selected derivative
lineages; its highest candidate scored `0.770618881684735`, versus the
selected red's `0.14889387096680404`. Neither proof is an integrated release
binding. Workflow isolation, consumer coverage and the combined
transaction remain open; no red release has occurred.
Opt-in fixtures stage unassigned red holds with anchor/group retirement,
preserve photo protection, and verify LEAN retained lineage, publication and
catalogue/source recovery. A read-only check found retained transfer evidence
for all seven saved reds. Exclusive transaction targets have fixture coverage
for racing destinations and simulated interruption; ambiguous files are
preserved for inspection. This is not an installed release path or a Sandbox
apply.

The repeatable read-only red diagnostic rechecked v14 and conservatively
blocked all seven candidates for unresolved workflow isolation/selection
coverage. It found the higher-scoring replacement proposal but made no
selection change. The optional consumer scan covered 5,921 JSON files;
five configured workflow roots were unavailable. The 12 unidentified
selection filenames were absent from all 96 shared/workspace-scoped input
lookups (some scopes share a root), so no input image bytes were available to compare; their identity
and complete consumer coverage remain unresolved. An initial high-memory scan was stopped and its bounded
read corrected before the successful retry.
A separate opt-in publication-journal foundation snapshots and
recovers explicitly approved external file targets in fixtures, including
partial publication and refusal of newer content; no red workflow transaction
uses it. New journals identify interrupted publication swaps and preserve them
for inspection; interrupted recovery between files can be retried. This does
not prove complete crash recovery or cover older journals. Beacon confirmed
existing actions do not cover a complete combined
transaction and that unknown workflow consumers must remain blocked. The
user was unavailable for the same-run return decision.

The subsequent fixture work connects routed red staging with catalogue,
workflow/configuration and input recovery, including interrupted input deletion
and exclusive-creation collisions. It does not install a release. The saved
Review-core retirement simulation found no affected core among the seven reds;
it does not replace the required post-routing score census. The targeted
release/transaction suites passed 194 tests; the queue and repository checks
passed. The real diagnostic still blocks all seven reds pending workflow
isolation and complete consumer/input coverage.
An additional read-only hypothetical route, assuming those gaps were
resolved, places one red in a different identity's Review and holds six in
Various Review. It is not an executable preview or a placement decision.
The routing simulation and its blocked-release distinction now have focused
fixture coverage; 195 release/recovery tests and the routine repository
checks passed. The fixed saved-core census checked zero scores, not the
post-routing newly-red population.
Full changed-worktree validation passed after fixing workflow test fixtures
to ignore machine root overrides; its library suite passed 1,136 tests.
One offline test was skipped and existing audit resource warnings remain.
An evidence-bound all-Review hypothetical then rebuilt the six affected
saved-policy cores: 409 remaining scores checked, zero newly red and one
unavailable. The moved photos were not rescored at their proposed
destinations; this is not a post-apply result or an executable release.
After the full run, recovery was hardened against a file appearing at an absent
restore target. Journaled collision and interruption fixtures and 198
focused release/recovery tests passed; hard-link support at actual
destinations and other concurrent-change races still require proof.
The shared publisher now refuses existing or racing journals and creates its
initial journal exclusively. Fixture-tested failures preserve the source and
any competing or partial journal; interrupted initial writes may require
manual inspection of the journal and backup. A per-file recovery recheck
also preserves edits made during an earlier restoration, but cannot eliminate
the final check-to-replace race.
The recap audit can inspect a separately specified workflow configuration
without changing the default; the read-only red diagnostic can use the same
report-bound configuration without changing the saved-run centering
configuration. This is not Sandbox isolation or release authorization.
The recap producer change makes the preserved v14 report stale; generate a
separate checked report before further diagnostic use. Separate v15 passed
preview/apply/check and the read-only diagnostic: seven blocked candidates,
five unavailable consumer roots and no unidentified input files available
to check. A later scan also found two unconfigured installations with
unavailable workflow roots; expanding unidentified-input checks to
unconfigured local input directories found zero files in 108 scoped
lookups. The v15 audit opened in the browser with seven reds, 329 unscored
and the unidentified-selection warning; it is not post-release acceptance.
After a wording correction to avoid implying the user had not authorized
release, v15 became stale. Separate v16 passed preview/apply/check and its
audit opened with seven reds and the corrected destination wording.

SIMPLE now offers opt-in 1-3 preparation workers, defaulting to 1, with
preview/apply matching, an origin-sealed worker count, available-memory
preflight and offline propagation into spawned workers. A four-input
isolated test of the actual adapter matched serial and three-worker stable
evidence. Additional 24-image sidecar and sampled-memory evidence is in the
[performance plan](../plans/2026-10-28-intake-performance.md#nov-21-per-machine-tuning).
It does not certify a full rebase or the other machine's settings.

## Sandbox red release and refreshed viewers

The user authorized a bounded Sandbox experiment without waiting for
other-machine workflow evidence. `red-release-sandbox-20261121-01` moved
seven saved red members: one to `Potentials\Yvette Orr\review` and six to
`Various\review`. The private release report records each original owner,
destination and routing reason. Publication check and recovery preview
passed, including a repeat after the separately generated viewer refresh.
Shared workflow selections were not changed; the higher-scoring replacement
is a proposal, not an installed selection. Complete consumer coverage,
isolated workflow replacement and combined recovery remain open.

The reports-only refresh passed its supported check: 3,305 Review records;
3,512 files and 1,822,182,500 bytes were independently sealed on the check
pass. The refresh itself took 1,103.8 seconds and reported 9,915 thumbnails;
these are not a controlled performance comparison. The actual Review opened
in a browser with visible loaded thumbnails; its data shows the Yvette arrival
in Review at approximately 0.380199 and a moved Various arrival unscored.
The Overview opened and loaded visible thumbnails. The private direct pages:

- `B:\Sovereign Territories Sandbox\Working\_reports\library\red-release-post-20261121-01\people_gallery.html`
- `B:\Sovereign Territories Sandbox\Working\_reports\library\red-release-post-20261121-01\people_gallery_review.html`
- `B:\Sovereign Territories Sandbox\Working\_reports\library\red-release-sandbox-20261121-01\index.html`

Use the Overview/Photo review tabs inside these refreshed pages. Their
masthead People link points to the older canonical overview, not this
separate refresh. Recovery of the release does not recover the later
reports-only output; those pages would then be stale and need a new refresh.
The pre-refresh shared pairing report was preserved at
`Working\_reports\runs\red-release-sandbox-20261121-01\pre-refresh-angel-prospect-candidates.md`,
SHA-256 `7e908ff52a665de9a5b3810fb0d8339ca6bf3e87910b244e77044c1b3e52a695`.

The hash-checked refreshed Review has zero red and 102 orange Gallery
scores in Sisters, Angels, Models, Prospects and Potentials; seven orange
Review scores and 88 unscored Gallery entries also remain. Orange is
currently 0.15 inclusive to 0.30 exclusive. No orange release had yet been applied at that checkpoint. For read-only exploration, the
Review's **View: Low scores** and **Low-score cutoff** controls filter
Gallery photos using an exclusive cutoff: browser checks showed 13 below
0.20, 31 below 0.25, and 102 below 0.30. This filter does not include
Review-bucket photos and does not change policy or release anything.
The user subsequently selected all orange and red for the Sandbox release.
The current-report census reproduced all 109 selected scores from the
bound cache, including 102 Gallery and seven Review candidates; two are
marked workflow-selected in the saved Review. Band-aware catalogue/routing
foundations and a read-only launcher were tested at that checkpoint.
The later `orange-red-release-20261121-01` preview and Sandbox apply moved
all 109 saved orange members: 22 to named Gallery, 24 to named Review and
63 to Various Review. Publication check and recovery preview passed; the
report binds 3,196 unaffected natives and records ten empty former matcher
cores. Two orange workflow-selected photos and the earlier red workflow photo
moved, but no workflow selection was
changed. A reports-only refresh to `orange-red-post-20261121-01` completed
and its check passed; the browser displayed Overview and Review with loaded
thumbnails. The masthead People link goes to the older canonical Overview.
Its checked residual census found four orange/red candidates and 88
unscored named-person photos, all in Potential Galleries (72 Small core,
16 Unscored); they cannot be classified as orange/red from this evidence.
The prior pairing report was preserved in the release run as
`pre-refresh-angel-prospect-candidates.md`, SHA-256
`fac2673319e9d048c6f8cafcea59ab1b8ab26c2cdf9da1df5c8b135f437a7c2a`.
These refreshed viewers are outside the release journal and become stale if
the release is recovered. No Sandbox `Artists` root was present.
The chained preview then bound both prior journals and conserved 3,305
photos. `orange-red-continuation-20261121-01` applied the four orange candidates,
two to named Galleries and two to Various Review; its publication check and
recovery preview passed. Preview SHA-256:
`ecbdeb5c0c55bced688b134602712f9d2399177d8ed1469c744f4fc94d716e9c`.
Before the next viewer refresh, the shared pairing report was preserved in
that run's `pre-refresh-angel-prospect-candidates.md`, SHA-256
`36bdffa9b61497d264645592d755dd067cdaef1511fbe9d65564560b65f31110`.
The new refresh completed with 30,686 content reads and a separate seal
(`15,468,820,324` bytes per pass, 1,121.02 seconds); its reports-only check
passed. The new checked Review has zero orange/red named-person candidates
and 88 unavailable scores. Browser inspection opened Overview, Review and a
retained detail, with visible thumbnails loaded; the four-photo release
report loaded all four images. The masthead People link still points to the
older canonical Overview. Earlier viewers are stale. Three workflow-selected
photos remain unreplaced, unknown consumers remain unverified, and human
identity/crop acceptance and per-machine tuning remain open.
Post-release read-only evidence found one configured binding and a verified
higher-scoring current Gallery candidate for each released workflow photo;
all three candidate scores reproduce from cache and their padded derivatives
and cached face-quality checks passed. These remain proposals: full
eligibility, unknown consumers, isolation and actual replacement are open.
A read-only scan of 5,921 reachable JSON files found seven references across
four repository files for each of the three selected IDs; seven workspace
roots were unavailable. This token scan does not cover ID-less or non-JSON
consumers and does not establish complete coverage.
The user subsequently directed release of unscored identity members and wants
everything scored. At the initial checkpoint, all 16 without cached vectors produced one-face vectors in a
read-only model-matched probe; they remain non-voting, and 72 singleton-core
members lack independent own-core comparisons. Three selected hashes have
aliases elsewhere in the Review. A tested viewer fix identifies deferred
measurements, but existing reports were not refreshed. Internal selection
and read-only measurement foundations selected and measured all 88;
85 passed the face-quality gate and three did not.

`unscored-release-20261121-02` then released those 88: four named Gallery,
nine named Review and 75 Various Review. A first attempt rolled back after
Windows denied a journal replacement; all 374 snapshot files and 1,209
targets matched the pre-apply state. A tested bounded lock retry and new
preview preceded the successful retry. The checked refresh exposed 28 more
unavailable members. `unscored-continuation-20261121-01` released them all
to Various Review; six identities had no eligible rival core, so scores
cover available rivals only. Both releases passed publication check and
recovery preview. The final checked Review contains 3,305 photos and zero
red/orange or unavailable named-person scores. Its Overview and Review and
both release reports opened in a browser with representative images loaded.
The reports record independent rival scores, not own-identity scores;
three quality-failed photos are low-confidence holds, and supplemental
measurements were not persisted. The earlier red workflow photo moved again
in the continuation; three distinct workflow selections remain unreplaced.
The checked final Review still lists the prior three higher-scoring Gallery
proposals at approximately `0.770619`, `0.743408` and `0.593723`, each as a
usable one-face core member with no derivative diagnostics. This is a
point-in-time recheck, not a workflow update or complete consumer proof.
The masthead People link still points to an older canonical Overview.
Use the direct final pages under
`Working\_reports\library\unscored-post-continuation-20261121-01`
and the two run reports under `Working\_reports\library`.
The applied preview hashes were
`fe31427694092413a8f3ccc24a38d799d43ab2d6e822cd01b6880388dcd75839`
and `15b69db7b5f1701180abf421cf2aeedd5a2754dd1d3004a991dc286cd2e844b3`.
The final Review SHA-256 is
`d78c46fc97b6d659c5fd1ef0577e023da8c1b043011c8d81cb0421143a92acb4`.
The failed run, recovery snapshot, and refresh/apply logs remain under
`Working\_reports\runs`. After these changes the focused 209 tests,
`bin\check.cmd`, and `bin\validate.cmd --changed HEAD --check` passed
(one full-suite test skipped). No workflow or Production changes were made.
Subsequent isolated New-PC 48-photo LEAN trials passed seven independent
checks with stable source/output/decision evidence across worker counts.
One worker took 79.04-80.65s, two took 52.68-53.13s and three took
44.58-48.27s; three used more sampled memory. See the
[tuning evidence](../plans/2026-10-28-intake-performance.md#nov-21-per-machine-tuning)
for hashes, process-tree sampling limitations and report locations. This is
not a full-rebase or old-PC result, and no default was changed.
Beacon's partial response at `d56c35022` reports no controlled old-PC worker
comparison or approved private same-input transfer. The collaboration-only
follow-up `208a95503` asks about an independent local-input comparison; it
contains no image or source list. Beacon's partial response `e702edc5e`
reports no existing old-PC worker comparison and no independently selected
sample, output location or resource bound for a new old-PC trial; Q14
remains open. Collaboration-only commit `8101eb077` published the checked
Sandbox release summary; the reports and implementation were not transferred.
The main dirty worktree remains unreconciled with the remote branch.
The separately maintained Artist
domain, whole-workflow coverage and human identity/crop acceptance are not
proven. A process-command check found no matching local release, rebase or
viewer writer at this checkpoint; the other machine's state is independent.

## Evidence and boundaries

- Run logs, timings and preserved failure evidence:
  `B:\Sovereign Territories Sandbox\_baseline-state\evidence\simple-clean-newpc-20261120-01`.
- Installed receipt and publication journal are under
  `Working\_reports\runs\normal-rebase-simple-newpc-lean-20261121-03`.
  The applied recap/audit and tuning reports remain under `Working\_reports`.
- The copied run15 and failed staging remain preserved; no reset, intake,
  Production mutation or promotion is implied by these results.
- No local rehearsal or tuning process remained at the final check. Do not
  infer that the other machine's separate process has completed.
- The [collaboration thread](../collab/2026-11-21-new-pc-rehearsal/README.md)
  asks the other agent for its actual status, code binding and transfer needs.

## Nov 21: cross-machine review and next direction

The other machine subsequently reported a completed SIMPLE rehearsal; both
installed runs passed their own apply/check/repeat. Harbor and Beacon compared
saved evidence and shared the results in the
[collaboration thread](../collab/2026-11-21-new-pc-rehearsal/README.md).

**What went well:** all 3,490 source-keyed placements and the compared
reference memberships and decision routes matched. The comparison used
saved receipts rather than another rebase. Recorded preparation control,
crop and mask aggregates also matched in the tested scopes.

**What needs attention:** matching placement is not proof of identical
output. A bounded 100-image sample found decoded-pixel differences in at
least one image per category; some scores and recorded framing fields also
differ. The cause, affected count, magnitude and visual significance are
unknown. Human identity/crop acceptance remains open. AI or hardware
variation is plausible, not established for these differences.

**What to improve:** assess practical impact rather than insist on identical
bytes; preserve exact placement and safety evidence, and compare score/rival
impact and representative visuals only where a safe private comparison is
available. Do not invent a significance tolerance or claim equivalence from
aggregate digests.

**Next:** the user prioritizes planning the release of red-scoring members
from identities, beginning with Sisters and Angels, with a run-specific
override even for protected or workflow-selected low scorers and a better
replacement for a released workflow photo. Track each released photo's
destination/identity and consider an end-of-run audit. Review existing
rules and historical plans first; clarify transaction and scoring details
before implementation. Orange review and named near-misses follow red
cleanup. The user separately assigned handoff-skill work to the other agent.
This direction authorizes planning, not a new run, Production mutation or
an unreviewed change to existing safeguards.
