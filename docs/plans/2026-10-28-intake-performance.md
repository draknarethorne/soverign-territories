# Intake performance, the likeness face crop and generated-output storage

**Status:** holding (performance contracts/evidence; selected core execution transferred)

**Resume gate:** the reset spine selects a measured extra or new-PC tuning;
the current core package is executed from the spine after the live-run freeze.

## Nov 6 bounded implementation and paired evidence

The settled-run freeze ended before these changes. No full intake or
library installation is used as a benchmark.

### Nov 6: recap continuity row aggregation

The recap previously rescanned all photo rows three times per old identity
to count retained Gallery photos, Gallery arrivals and departures. It now
aggregates those same counts once while building the existing flow groups.
An executable fixture checks retained, moved and Review cases; all 28 recap
tests pass. Installed preview3 and uninstalled preview6 recaps were both
regenerated through the supported preview/apply/check launcher, with each
entire HTML file byte-identical to its prior version.

On the 3,290 saved preview6 rows, five isolated runs of the continuity
section with person/destination links mocked took 0.147..0.157 seconds
before and 0.022..0.033 seconds after; each returned the same 132,092 bytes
and SHA-256
`166c5affe3402af3c369bc5027253229b397514f5e7dd0daeb05355a0697c579`.
The runs were consecutive in separate processes, not controlled alternating
pairs, and exclude real link verification and page publication. This is a
small CPU-only repeated-work fix, not a measured full-report or intake
speedup; T29/T30 remain open for their complete evidence and contracts.

| Hotspot | Delivered change | Same-input proof and boundary |
| --- | --- | --- |
| Manifest serialization per framing, T21 | One loaded manifest per photo, reused during framing checks, published once after completed work | Reproduced three writes before the fix; one write after for all three framings, zero for a no-op. A second-framing failure still publishes the completed first framing, propagates failure and resumes the remaining two. Existing exact derivative/recovery/tamper tests pass |
| Duplicate report builds/history, L18 | The continuous report coordinator supplies one general-domain scoring context and one preparation index to sequential Review/Overview writers | Real generator fixture: two builds/two indexes become one/one, with every prior report/thumbnail byte identical under a fixed generation timestamp. Standalone entry points still build their own state |
| Duplicate proof scopes, L18 | Explicit same-root/same-seal-policy session reuse; one final full content/path/owner seal for the combined operation | Cross-root or different-seal reuse refuses. A same-size edit with restored mtime still fails; a changed input between page writers prevents publishing successful freshness state. A later invocation revalidates rather than inheriting trust |
| Unchanged retained detail, T22 | Verify current lineage, skip byte-identical detail/manifest writes and avoid the redundant post-write verification | Two writes become zero, two lineage verifications become one; returned hashes/bytes remain identical. Edited detail still refuses. Changed content retains the old transactional verification/recovery path |
| Report freshness correctness | Bind freshness to reader/rendering code and configuration, not just library bytes | A same-length code edit with restored mtime invalidates freshness; a missing dependency errors explicitly. `--check` remains read-only, not a hidden rebuild |

These are call/read/write-count improvements, not a claimed aggregate wall
speedup. The actual shared report refresh succeeds in 2,103.67 seconds:
its shared proof takes 1,950.51 seconds, reads 30,786 contents /
15,583,261,759 bytes, reuses 100,663 hashes, then independently seals
30,785 files / 15,534,493,437 bytes. The separate synchronized check passes
in 20.14 seconds, reading and sealing 3,545 files / 1,846,752,181 bytes.
Evidence: `tmp\session-logs\nov6-shared-reports.log`. Observed process
working sets were 393..744 MiB, not a sampled peak-memory guarantee.
The previous report repair's separate Review/Overview timings are
historical budgets, not a controlled same-code wall-time benchmark.

The no-op snapshot guard additionally binds read detail/manifest bytes back
to the just-verified lineage; an intervening manifest edit refuses instead
of returning a new unchecked checksum. That follow-up changes the
conservative reader fingerprint, so the final report refresh must follow
the combined preview before claiming synchronized latest-code reports.
The complete 171-test retained/provenance/recap/family/rebase/continuation
selection and 19 isolated validator smoke tests pass, as do syntax and
routine hygiene/data checks.

**Explicit remaining dispositions:** person-folder parallel writers,
decode-once across different framing APIs, dependency-selective prepared
cache invalidation and wider install inventory reuse are not silently
claimed delivered. The current serial owner model and full invalidation
remain safe; changing them needs exact pixel/dependency/partial-failure
proof and a measured benefit. They remain with T20/T21/T22 rather than
blocking this bounded **matching-only** continuation preview. Any later
installation/performance closeout must retain their explicit owner/gate.
No new worker pool, persistent trust cache, recipe change or weakened
independent installed acceptance is introduced.

### Nov 6: bounded decode-sharing trial

The current-code generation probe used five SHA-256-verified prepared
inputs from the frozen preview4/cache, one each from Angels, Sisters,
Potentials, Prospects and Various. It rendered all three framings with
the saved face boxes and `prepared=True`, in one process on the sandbox's
existing B: drive; it did not copy or mutate library inputs. The five
source files total 1,461,566 bytes. Python 3.14.3, Pillow 12.1.1,
Windows 11 and an AMD Ryzen 5 5500 (6 cores / 12 logical threads,
25,655,050,240 bytes physical memory) were used; no cache flush or
competing-load control was attempted.

The source IDs were `image_7514747935627264261`,
`image_7517962558582853855`, `image_7513274258273458465`,
`image_7500298447818601013` and `image_7513775101895217549`.
The original derivative module SHA-256 was
`4b86e27e8d3d01e5ec7014ded2c0bc060f333050913abaf4542fdc58741c5dd`;
preview4 run and frozen-cache hashes remain recorded in the spine.
Two instrumented baseline repetitions took 1.759 and 1.796 seconds and
opened source images 15 times for 15 output PNGs. The ordered aggregate
of per-output SHA-256 records was
`c8a7ebe19fb54b42f7d25cc828c93b9a373277a3b2b3627814928a5b5a1e815d`.

Three adjacent baseline/prototype pairs took respectively 1.7643/1.7156,
1.7666/1.6834 and 1.7614/1.6292 seconds; each pair's 15 PNG byte hashes
matched exactly. The prototype decoded each input once and supplied copies
in memory to the existing render functions. **It was a read-only hypothesis
trial, not a production implementation:** it omitted source mutation/
ownership guards and exercises prepared images only, not screenshot cleanup,
EXIF edge cases, no-op verification, error recovery or memory bounds.
Its apparent 0.05-0.13-second savings are not a full-phase speedup or
evidence that a safe implementation is faster.

T21 decode sharing remains open. Implementing it safely spans the separate
originals helpers, staging and standalone/recovery consumers and requires
the explicit mutation and output-equivalence contracts above. The small
trial alone does not justify silently discarding those checks or claiming
the decode-sharing slice complete. No policy, receipt or library image
changed for this probe.

### Nov 6: external inventory reuse trial

A bounded, read-only T20 comparison on the current installed
`Angels/sammara` owner used all 19 Gallery/Review originals and their
associated retained and derivative evidence. Both paths called the same
existing external-inventory collector against the same snapshot. The
standalone baseline took 35.893 seconds and made 2,092 instrumented
verification digest reads / 960,851,593 bytes. An explicit operation-local
verification session, including its independent content seal, took 9.565
seconds and made 352 digest reads / 198,501,039 bytes. Both returned the
same 186 path/digest entries (ordered inventory digest
`5c4104d720a08e81e8af774786287bb10e456c792751c8e4787aa8a2e7b4ef86`).
Session counters additionally recorded 186 content reads, 905 hash reuses,
20 JSON loads and 186 independent seal reads. Instrumented digest bytes
do not include every other application read.

These are single-owner trial timings while a separate read-only baseline
was active, not a controlled whole-install speedup. They establish a useful
candidate for operation-scoped reuse, not permission to reuse results across
the later staging/publication boundary or to omit the final independent
acceptance. The next implementation must reject source/manifest mutations,
preserve the complete inventory and old error behavior, and avoid changing
the active run's runtime bytes until the baseline finishes. Since
`clean_rebase.py` is bound into preview4, any engine change makes that
saved preview unsuitable for install/check on the new code; preserve it as
review evidence and require a new checked saved-input preview before install.

After the no-op baseline ended, `_prior_external_files` was changed to
reuse one root-bound verification session, check every returned native,
retained, derivative and legacy path against its expected digest, and seal
the content before returning. A compatible outer proof can own that seal;
an incompatible root or no-seal session refuses. It does not retain trust
across stages or replace independent publication checks.

Two paired real-owner reruns of the implemented path produced the same
186-entry inventory as the unoptimized collector:
37.009/10.549 seconds and 34.615/8.492 seconds, respectively. In each
pair, instrumented digest reads/bytes were
2,092 / 960,851,593 versus 352 / 198,501,039. The optimized session
performed 186 independent seal reads / 99,474,864 bytes. These are
warm-cache owner measurements, not a phase-wide claim; the first pair
overlapped other affected-path tests. All 107 rebase, continuation, read
session and maintenance tests passed (one Windows symlink-privilege
skip). The new tests cover mutation during collection, a changed
unprepared native with no derivatives, and compatible/incompatible
outer proof scopes. A first combined test command had an incorrect
continuation module name; the corrected complete selection passed.

The separate `postrun-review-preview5` now passes the saved-input
continuation and independent check using the same combined policy.
All 3,290 full per-photo records, family naming, both refinement records
and final audit are equal to preview4; preview5 remains uninstalled.
Browser review confirms its Lujan comparison contains eight member blocks
and 40 loaded images without broken images; the Noelle fragment opens its
96-photo detail. The separate read-only full installed-cast external
inventory completed and independently sealed 11,786 paths in 587.721
seconds. It read and sealed 5,854,285,911 bytes, reused 66,845 hashes,
loaded 1,317 JSON files, scanned 52 directories and performed 9,315 path
checks. Its ordered path/digest SHA-256 is
`2a7df1d706b2654037b5f29cb6ba8e07fbf1de35f208ff374db4a307b068899a`;
the log is `tmp\session-logs\nov6-external-inventory-full-check.log`.
This verifies the current collector on the real inventory; it is not a
paired whole-install speedup or an installed acceptance.

### Nov 6: installed no-op baseline

The supported `people-gallery.cmd --check --no-reports` ran read-only
against the installed preview3 root, saved cache and saved policy. It
returned zero with zero renames, pending derivatives or actionable
diagnostics and 143 intentional framing exclusions. The operation took
696.75 seconds, including its full independent seal: 30,780 content
reads / 15,485,247,284 bytes, 44,055 hash reuses, 3,541 JSON loads,
282 directory scans, 24,656 path checks and 30,780 seal reads of the
same byte count. Log:
`tmp\session-logs\nov6-noop-maintenance-baseline.log`.

This is the installed no-op/check path, not fresh derivative generation
or a paired before/after result for the external-inventory change.
One small external-inventory experiment overlapped the read-only run,
so elapsed time is observational rather than an isolated performance
claim. T29 remains open for its complete generation/no-op, memory,
cache-state and phase coverage.

### Nov 6: current-category attribution boundary

The shared install phase label "current category and external inventory"
does not identify the cost of either component. Preview5
records `recoveryMode: disposable`: in that mode `install` checks the
category roots for unsafe paths and enumerates their files, but skips
`_category_inventory` and its previous-category content hashes. It still
collects and seals the external cast inventory. FULL additionally records
the previous-category hashes and later independently checks those hashes
before publication; disposable recovery is reset-only, not FULL rollback.
These paths are in `tools/art/likeness_library/clean_rebase.py`.

The 587.721-second measurement above is the external collector alone, not
the entire labelled install phase or a current-category measurement.
A separate read-only run of the same LEAN root safety checks and
`_source_files` enumeration on preview5's installed Working roots counted
19,223 files in 7.090 seconds: Models 1,942 / 0.565 s, Prospects 4,659 /
1.323 s, Potentials 1,569 / 0.886 s, Various 157 / 0.046 s, and their
processing trees 2,553 / 1.010 s, 5,868 / 2.306 s, 2,233 / 0.865 s and
242 / 0.086 s respectively. The total includes root safety checks; per-root
times measure enumeration only. This did not hash file contents, install
or mutate anything; it followed other reads and is a warm-cache observation,
not a paired comparison or a FULL content-hashing duration. Log:
`tmp\session-logs\nov6-lean-category-enumeration.log`.

Do not remove the enumeration or the independent FULL recheck on this
evidence, and do not run a FULL installation merely to attribute the LEAN
result. T20/T29/T30 remain open for the outstanding affected-path
coverage and paired measurements.

### Nov 6: prepared-cache eviction attribution

The current verification session clears all prepared-lineage results on
every intentional write. A read-only paired trial used the installed
Sammara owner's 19 prepared natives and existing padded derivatives, three
passes in one operation, with a simulated derivative write guard and target
rehash for each photo. **No file was written.** Both sides performed the
same guards, rehashes and independent content seal; the comparison side
deliberately suppressed every prepared-cache eviction. It is an unsafe
hypothesis, not a proposed implementation.

The two warm-cache pairs took 5.798/2.674 and 5.732/2.651 seconds.
The existing path resolved prepared lineage 57 times versus 19 in the unsafe
comparison; all 57 results were true on both sides. Each operation recorded
186 content reads / 101,645,088 bytes and 148 independent seal reads /
62,568,532 bytes. Reused-hash calls fell from 511 to 97. Guard reads are
not all counted as `contentReads`; these numbers are not total I/O or a
full-phase speedup. Input native hashes match preview5's saved inputs;
the ordered JSON path/hash list SHA-256 is
`12cdb9bd3b79cdfe92b5c600610d244280a138a7051d3f0727025725e0b0788c`.
The trial log is `tmp\session-logs\nov6-prepared-eviction-paired.log`.

The trial demonstrates potential repeated lineage resolution, not a safe
invalidation boundary. Prepared results also depend on owner/legacy
layout, processing-store discovery, native and retained artifacts, all
owner manifests and directory membership. A correct selective change must
cover those dependencies, negative claims, configuration, external edits,
intentional writes, rollback and final seals; a derivative-looking path or
an unchanged timestamp alone is insufficient. T21/T22 cache invalidation
therefore remains open. No runtime code, preview binding or policy changed.
An added regression confirms that intentional writes to a native, retained
original or retained manifest invalidate the cached decision and refuse
stale lineage. Suppressing eviction in a test-only mutation makes all
three cases fail; this is a guard for future work, not the selective fix.
A separate negative-claim regression verifies that a manifest write making
the native prepared changes a cached false result to true; suppressing
eviction makes that regression fail too.

### Nov 6: external derivative-manifest digest reuse

The external inventory already parses each derivative manifest through the
operation-scoped verification session, but subsequently reread it outside
the session for its inventory digest. The collector now reuses the parsed
document's verified digest; the independent content seal remains. A focused
test first reproduced the extra direct read, then confirmed it is absent.
A separate test edits the manifest after it is loaded and confirms the
operation still refuses at its final content seal even when the edit has
the same byte length and its original modification time is restored.

On the same 19-photo Sammara owner, two warm-cache baseline/reuse pairs
took 7.962/8.018 and 8.358/8.432 seconds. Each returned the same 186
entries and ordered inventory digest
`8e6ba4d24fb294aee04b11f2d180a1a3b9afa6ca41c9cfad1ed3ece4eb6549df`.
The change eliminates one direct manifest read of 27,954 bytes per
operation in this sample; these timings show **no measurable wall-time
improvement**. This is not a phase-wide gain. The 109-test rebase/
continuation/read-session/maintenance selection passes with one Windows
symlink-privilege skip. Log:
`tmp\session-logs\nov6-manifest-digest-paired.log`.

The engine binding changed, so preview5 is historical review evidence.
Separate preview6 creation, independent saved-input check and recap check
pass; all 3,290 photo records and the full family/refinement/final-audit
objects match preview5. It remains uninstalled. The combined run took
847.84 seconds; log `tmp\session-logs\nov6-manifest-digest-preview6.log`.
Preview6 run SHA-256:
`1a172a26bbdfc6f31eecd735fde1325492ce1a17f16f8a9f6c2271ed29dd9281`.
Do not install it on the basis of this measurement.

## Milestone transfer record

Nov 5 16:45: T29/T30/T20/T21/T22 execution transfers with the same IDs to the
[reset spine](2026-11-05-priority-reset.md#m1-execution-and-transfer-ledger).
Complete continuous/standalone, ownership/invalidation, correctness,
resource and measurement contracts, findings, raw words and evidence stay
below. The old entries are contract references, not competing checkboxes.
Other open tasks stay holding, including conditional T23-T26, new-PC T27,
matching T28 and recipe statistics/profile work. Known cheap repeated-work
fixes remain core; transfer does not weaken the stopping or validation gates.

## Nov 5 16:05: small gains and continuous versus reviewed execution

Easy, bounded, behavior-preserving improvements are worthwhile even when
their immediate gain is small: library growth and later functionality can
amplify repeated work. Do not reject those fixes because they fail the
10-minute/20%/2-minute extras gate. That gate remains a prioritization rule
for substantial additional acceleration, not a minimum gain for every
simple improvement. Keep focused correctness tests and honest benefit
evidence; do not broaden a small fix into speculative infrastructure.

The pipeline must support both deliberate review boundaries and efficient
uninterrupted execution through the same stage logic:

| Execution boundary | Required behavior |
| --- | --- |
| Standalone step, resume, or review pause | Re-establish source/config/ownership bindings and validate evidence before reuse; do not assume memory from an earlier process is still valid |
| Back-to-back stages in one controlled operation | Carry validated inventory, immutable evidence and owned mutable state forward where dependencies remain valid; avoid rebuilding/re-reading/re-writing them solely to emulate separate invocations |
| Mutation within that operation | Invalidate changed dependencies and their consumers, verify newly produced artifacts, retain unrelated valid evidence; do not reset all caches merely for a stage label |
| External mutation possible, changed scope/config, process exit or unknown lineage | End the trust scope and revalidate affected inputs; continuous scheduling alone is not proof of immutability |
| Required independent acceptance, final publication or user approval gate | Preserve the check/approval and durable provenance; a faster continuous path cannot substitute an old cached success or bypass a requested stop |

T30 must map **artificial command/process boundaries** alongside per-photo
duplication. For each boundary, identify the necessary durable artifact and
verification versus avoidable intermediate materialization, repeated scans,
JSON parse/serialization, cache reconstruction or copying. Choose a bounded
in-process orchestration/context handoff using existing helpers where it
removes established overhead; subprocess boundaries cannot share ordinary
memory automatically. Do not introduce a daemon, global cache, unrelated
framework or persisted "trusted" cache without a demonstrated requirement.
Before sharing data across workers, retain disjoint ownership and explicit
mutation/dependency rules from the coordinator contract below.

The continuous path and standalone stages must agree on final outputs,
routes, manifest evidence, diagnostics and error semantics under equivalent
inputs. Test both a continuous sequence and stop/review/resume, including
input/config edits during the pause and a partial worker failure.
Bounded memory/flush boundaries are legitimate; measure them separately
from needless per-item disk round-trips. Preserve required receipts and
review previews; optimize how they are produced/consumed rather than
silently deleting them. Disposable LEAN remains reset-only and
FULL/Production retains its existing recovery contract.

This is an extension of T30's core work and T20-T22/L18's implementation
criteria, not another investigation prerequisite or permission to change
the current running installation.

### Nov 5 16:07: verified handoffs, not phase-by-phase re-proof

The fragmented standalone command design must not dictate continuous-run
cost. A verified result with explicit input/config/dependency bindings and
controlled ownership is consumable evidence, not a hint that the next
phase should scan/hash/decode the same inputs again. Within the valid
operation scope, reuse the result and common bounded caches directly.
Retain adapters for standalone/review/resume entry points; do not make the
continuous coordinator invoke their full rediscovery/preflight paths.

For T30's boundary ledger, classify each existing check:

- **Already established, dependencies unchanged:** consume the verified
  result; remove redundant read/hash/parse/rebuild from the internal handoff.
- **New output or dependency changed:** establish only the missing proof
  and invalidate affected consumers, not the entire run context.
- **Unknown ownership, external edit, resumed execution or failed producer:**
  re-establish the affected evidence or refuse; never manufacture success.
- **Distinct acceptance/publication property:** retain the check that proves
  that property, but reuse valid prerequisites instead of repeating their
  entire verification chain. Existing explicitly independent acceptance
  contracts remain until a reviewed contract change, not incidental removal.

Record which check was eliminated, which producer evidence replaces it,
its validity/invalidation boundary and the saved calls/bytes. "Non-stop"
alone is not the evidence: verified producer results plus unchanged
dependencies are. Tests must prove both that redundant checks are absent
in a continuous run and that pause/edit/failure paths still revalidate or
refuse correctly. This is core end-to-end integration work, not merely
optional tuning of individually correct commands. Implementation remains
after the active run settles.

## Nov 5 15:59: pipeline-wide repeated-work core and execution design

The user clarifies that avoidable thrashing anywhere in the process belongs
in the core assessment, not merely derivatives or optional parallelism.
This expands T29/T20's coverage under T30 below; it does not authorize
editing the active run or implementing a generic scheduling framework.
The previously agreed extras gate applies to **additional parallel
acceleration**, not to excluding demonstrated straightforward repeated-work
fixes merely because they occur in staging, hashing, reports or checks.
Still establish the cost and prove benefit: more threads doing redundant
work is not a successful optimization.

### Phase-by-phase work package

| Phase / existing owner | Core repeated-work investigation | Bounded execution design / constraint |
| --- | --- | --- |
| Preflight and current/external inventory, T20 | Repeated retained-link/ownership traversal, manifest loads and source/derivative hashes across callers | Build one operation-scoped verified inventory for the relevant immutable scope; consume its explicit records rather than independently reconstructing them per photo/framing |
| Staging, T30 with T24 | Repeated source validation/copying of an identical owned artifact; inventory facts discarded between plan and copy | Coordinator resolves destination/collision/ownership first; copy each required target once, prove resulting bytes; extra parallel copy workers remain measured-conditional |
| Derivatives, T21 | Manifest read/parse/verify/serialize per framing, repeated prepared-lineage resolution, repeated source opening/decoding | One folder owner loads mutable manifest state, processes its photos/framings and publishes coherent owned results; trial decode-once only with unchanged EXIF/orientation/cleanup/crop/PNG output; different folders can be worker jobs |
| Retained details, T22 | Verify/read/rewrite/reverify plus global cache invalidation when changing one detail/manifest | Partition by actual shared manifest/dependency ownership, not assumed one-photo independence; refresh only changed content where contract permits; invalidate affected evidence with complete dependency coverage |
| Review/Overview and other report generation, L18 with T30/T25 | Whole-history re-audits, repeated representative/thumbnail source reads and independently rebuilt evidence indexes | Coordinator supplies an immutable verified evidence view to consumers; publish whole pages in order. Image jobs may use bounded workers only after separating their measured cost |
| Installed/gallery checks, T30 with T26 | Duplicate reads within a check or between compatible checks, repeated decode/render and directory discovery | Reuse only within a declared unchanged scope; retain independent acceptance/seal checks where required. Independent check workers remain measured-conditional; never substitute install's cached success for a required independent check |
| Intake/matching, T30 with T27/T28 | Flag demonstrated redundant per-image/config/model/reference construction in the affected path | Reuse invariant evidence where exact behavior is proven; no full intake experiment, new recipe, model change or concurrent dependent refinement passes |

### Coordinator and worker contract

1. **Classify before scheduling.** Use phase and helper timings/call counts
   to distinguish CPU rendering/decoding, Python orchestration, disk reads/
   writes and repeated metadata work. Extend existing timing/read counters
   only where needed; count direct image opens/decodes, manifest loads/
   writes/bytes, cache hits/misses/invalidations and queue wait separately.
   Existing `contentReads` is not a unique-file or total-I/O counter.
2. **Remove duplication first.** Retain one authoritative mutable manifest
   per owner and reuse immutable verified facts within a bounded operation.
   Do not add a global persistent cache or timestamp-only trust.
   Cache keys include source bytes, recipe/config and dependencies;
   intentional writes invalidate the affected proof, not silently trust it.
   Current `ReadSession.invalidate` clears all prepared-cache entries:
   investigate the cost and dependency scope before narrowing invalidation.
3. **Choose execution per bottleneck.** Compare serial execution with a small
   bounded thread pool for I/O/native work that releases the GIL, or processes
   for demonstrated Python CPU bottlenecks where startup/serialization/model
   memory is justified. Do not select threads from CPU percentage alone.
   Do not send decoded full-resolution images through process queues without
   measuring transfer cost; prefer compact path/config/job specifications.
4. **Keep decisions and shared commits owned.** A coordinator freezes
   eligibility, routes, job IDs and disjoint output ownership before enqueue.
   A worker owns an entire folder/manifest dependency unit, or returns
   independent payloads for a single coordinator writer; never mix both
   writers for one manifest. Policy decisions, collision resolution,
   cross-owner aggregation and final publication remain ordered.
5. **Bound resources and state.** Limit workers and queued/in-flight payloads,
   decoded image lifetime, open files and native library threads. Apply
   backpressure rather than loading the full library into memory. Avoid
   nested executors and CPU oversubscription. Existing ContextVar-backed
   verification state is not automatically a safe shared worker cache:
   give workers explicit isolated sessions/evidence and reconcile results
   at the owner; do not copy/share a mutable session indiscriminately.
6. **Make failure/progress explicit.** Collect completion without waiting
   for earlier slow jobs just to show progress; restore deterministic output/
   diagnostic ordering by job ID. Report active/completed/failed counts,
   phase/rate/elapsed and queue pressure at existing progress boundaries.
   On failure stop new submissions, settle running writes safely, report
   the failed unit and leave no successful receipt for partial publication.
   Preserve reset-only disposable recovery and existing FULL guarantees.
7. **Prove then integrate.** Compare the serial baseline, repeated-work-only
   change and worker-enabled change separately on identical inputs/storage.
   Assert exact pixels/hashes, manifest entries, routes, reasons/exclusions,
   counts, links and edited/missing/path-change refusal. Exercise a large
   single folder, many small folders, shared manifests, mixed Gallery/Review,
   excluded framing, tampering and worker failure. Record peak memory,
   wall time and file operations; retain serial execution where faster.
   Finish with one combined affected-path acceptance, not one full intake
   per owner.

### Nov 5 16:01: established findings versus unresolved attribution

The existing source traces and historical phase timings already establish
the findings below. Do not send them back through an open-ended discovery
or profiling loop before implementing bounded fixes. Timings establish
phase budgets; they do not isolate every helper's contribution. Code proves
the repeated work/serial structure, not the eventual speedup.

| Established finding / source | Concrete implementation next step | Remaining proof, not rediscovery |
| --- | --- | --- |
| `derivatives.maintain` calls `save` for each created framing; `save` verifies the old manifest, serializes the whole document, then reloads it | T21: load and mutate one owner-scoped manifest in memory; batch coherent publication at a tested ownership boundary rather than per framing | Preserve ownership/tamper detection and safe behavior after partial failure; compare manifest writes/bytes and exact entries |
| `derivatives.render_pixels` opens the source for separate padded/head/chest rendering; install also directly reads it for the SHA-1 measurement lookup | T21: share a verified per-photo input/decoded representation across compatible framing helpers, with explicit lifetime; avoid redundant lookup reads where existing verified evidence can supply the correct digest | Preserve EXIF orientation, cleanup and framing behavior, exact output bytes and distinct SHA-1/SHA-256 meanings; quantify decode/read reduction |
| `ReadSession.invalidate` clears the entire prepared cache even for individual derivative/detail writes | T21/T22: replace global eviction with dependency-scoped invalidation where the dependency map proves it valid; separate unrelated derivative outputs from source-lineage dependencies | Prove relevant source/manifest mutations invalidate every dependent claim; no stale-success cache or weakening final checks |
| `refresh_detail` verifies lineage, reads detail/manifest bytes, writes updated files and verifies again; even unchanged resulting content takes the write path | T22: reuse verified owner-scoped data and skip byte-identical writes with explicit unchanged results; keep post-change verification for actual mutations | Preserve links, artifact hashes and invalidation/failure behavior; unchanged content does not imply unchanged external dependencies |
| Review and Overview repeat history verification; the narrow Overview-only session did not implement cross-page reuse | L18: provide a single bounded verified history/evidence view to compatible consumers, retaining page-specific dependencies and ordered publication | Complete dependency coverage, mutation refusal and full page/count/link equivalence; do not remove independent installed acceptance checks |
| Install derivative/detail orchestration is serial; existing intake pools do not parallelize these phases | T21/T22: bounded disjoint owner jobs, coordinator for cross-owner decisions/aggregation; no shared manifest writers | Select thread/process configuration with small comparative trials and measured memory/I/O, not another full rebase to establish that the loop is serial |

T20's external-inventory trace also establishes repeated retained/derivative
verification calls. Its operation-scoped reuse fix belongs in the queue;
the precise duration of the current post-preflight interval is **not**
established by that trace. Do not attribute the entire pause to one helper.
Staging/check/intake entries in T30's broader phase map remain audit coverage,
not claims that every proposed duplication or speedup there was verified.

**Execution rule:** reuse saved timing evidence and capture only missing
same-input baseline/call-count evidence needed for a reliable comparison.
Then implement the established bounded fix with a focused regression test
and compare before/after. Baseline capture can be a targeted fixture/phase
run; it is not permission or a requirement to repeat full intake/rebase.
No arbitrary savings threshold excludes these known core fixes. Retain the
extras gate for additional acceleration and report any fix whose safe
implementation expands substantially. Nothing in this finding ledger
authorizes runtime changes while the current installation is active.

### Ordered implementation handoff after the run

T29 captures baseline/contracts; T30 identifies and assigns repeated work
across the affected phases. Start with T20's established inventory path,
then T21/T22's manifest/decode/cache units and L18's history reuse. Each
slice is independently tested and benchmarked before the next builds on
it. Do not require finishing the entire audit before fixing a confirmed
bounded hotspot. Delegate no new benchmark I/O during installation.
T30 records every discovered hotspot as fixed/tested, measured-no-gain,
explicitly deferred with risk/reason, or awaiting evidence; no blanket
"cache added" or "parallelized" completion claim. Necessary shared helpers
follow existing mechanisms, not a new generalized engine.

**Transferred contract: T30 -> [reset T30](2026-11-05-priority-reset.md#m1-execution-and-transfer-ledger), not completed.** Audit and remove demonstrated avoidable repeated work
  across inventory, staging, derivatives, retained details, reports and
  checks, using T29's paired evidence and the coordinator/worker contract.
  Include affected intake/matching invariant-work observations without
  activating full intake or algorithm changes. Assign fixes to T20/T21/T22/
  L18 or the existing phase owner; preserve independent verification and
  mutation invalidation. Cheap redundant-work fixes are core regardless
  of phase; optional additional worker pools still use the extras gate.
  Publish per-hotspot cost, ownership, change/test evidence and disposition;
  no runtime mutation until the current run settles.

## Nov 5 14:41: bounded pre-new-PC benchmark bundle

**Decision:** core-conditional scope, with the measured-threshold stopping
rule. This refines the earlier approval of opportunities; it does not make
every approved candidate a prerequisite for the machine move.

| Before moving performance work to the new PC | Scope |
| --- | --- |
| Core investigation/implementation and same-machine evidence | T29 baseline/gates; T30 pipeline-wide repeated work; T20 inventory reuse; T21 person-folder derivatives; T22 independent details; gallery L18 cross-page history reuse |
| Conditional extras, not automatic prerequisites | T25 thumbnails after report cost split; T23 hashing, T24 staging and T26 verification only when the measured gate below passes |
| Later/new-PC work | T27 intake worker/thread tuning; FULL assessment on the new machine; T28 matching investigation remains holding |
| Not included | New intake just to benchmark each change, altered quality/processing policies, derivative caps, concurrent publication or Production mutation |

After the active installation settles and its evidence is recorded, capture
the current-code baseline **on this PC before runtime optimization or path
migration**. Historical run totals are context, not a paired benchmark.
Use the same frozen inputs, recipe/policy, evidence and output requirements,
ownership units and storage device for before/after comparisons. Measure
worker settings, RAM, wall time, reads/bytes and cache state; distinguish
fresh generation from already-current no-op checks. Do not mix regeneration
in the baseline with cached output reuse in the candidate and call it a
worker speedup. Isolate tests from active installed outputs without copying
the whole sandbox into repository scratch or adding LEAN recovery backups.
Bounded test artifacts are test fixtures, not a new rollback policy.

**Extras gate (15:59 clarification: additional parallel acceleration,
not straightforward demonstrated repeated-work fixes):** after the core
work, a remaining phase on this PC must
measure **at least 10 minutes**, and a bounded same-input candidate trial
must demonstrate **at least 20% wall-time improvement and at least 2 minutes
saved for that phase**, with unchanged output/check contracts. All three
conditions apply. Sample extrapolations must be labelled estimates, not
proof that the full phase passes; verify phase-level savings before claiming
acceptance. Split overlapping report costs before applying the gate; never
count the same saved history reads again as thumbnail-worker benefit.
Repeat comparisons when close/noisy and record workload/background load.
Do not deliberately flush system caches or disrupt other work.

Correctness fixes are not subject to the speed threshold. For core slices,
finish the investigation and evidence, not implementation at any cost:
if unsafe, substantially expanded or without repeatable benefit, report and
defer the slice rather than indefinitely blocking the move. No new full
intake per optimization; share paired phase evidence and run focused
correctness/equivalence tests, then one combined affected-path acceptance
when the bundle is ready and execution is approved.

Basic PC setup can proceed independently. Corrected-name cloning retains
the existing settled-run/spelling gates; finishing every conditional extra
is not a new prerequisite for the rename, clone or returning to character art.
Benchmarks on the new PC form a separate baseline, not evidence that the
software alone improved this PC.

**Transferred contract: T29 -> [reset T29](2026-11-05-priority-reset.md#m1-execution-and-transfer-ledger), not completed.** After the active run settles, freeze a representative
  same-machine phase benchmark specification and capture baseline evidence
  before runtime optimizations/path migration. Cover T20-T22 and gallery
  L18, separate report history versus thumbnail cost, record generation/
  no-op and warm/cache conditions, complete output/diagnostic contracts,
  input/config/code identifiers, worker/RAM/storage settings and phase wall
  times. Reuse this evidence for paired candidate trials and final combined
  acceptance. Apply the 10-minute/20%/2-minute gate to extras; report core
  slices deferred for risk/no repeatable gain and remaining unknowns.
  Leave the running terminal and mutable installation untouched.

## Nov 5: approved downstream parallelism and bounded speed work

The user approves the ranked opportunities, effort/risk assessment and
order from the timing discussion; at 14:25 they select documentation/feedback
reconciliation while the existing installation runs. **Do not change runtime
code, implementation hashes, policies or active inputs during that run.**
Implementation resumes after its results/evidence are recorded. This is
future work, not parallelism delivered by the earlier read-cache changes.

LEAN's finish line remains correctness and measured major bottlenecks,
not exhausting all possible optimizations. Use one shared benchmark/evidence
set across owners, not another full rebase for every task. LEAN processing
is the routine preference; disposable recovery is sandbox-only and
Production stays protective. More workers must not weaken FULL guarantees.

### Priority, benefit and risk

The last completed `fresh-20261104-lean2` run supplies historical wall times.
They are not forecasts for the current changed implementation or the new
machine. Subcomponents of a phase overlap; do not sum overlapping budgets.

| Scope / owner | Historical time affected | Effort / correctness risk | Benefit and urgency |
| --- | --- | --- | --- |
| External inventory reuse, T20 | Long post-preflight interval; no isolated baseline duration established | Small-medium / low-medium; cache invalidation and ownership checks remain mandatory | P1: remove repeated work before parallelizing it; establish current-run attribution first |
| Person-folder-parallel derivatives, T21 | 54m40s | Medium / medium; each person owns a shared derivative manifest | P1: largest separately measured CPU-oriented install target; more cores can help |
| Independent retained-detail work, T22 | 17m02s | Small-medium / low-medium; prove separate detail/manifest ownership | P1: bounded ownership-unit parallelism; verify versus HTML cost determines gain |
| Bounded parallel hashing, T23 | Parts of inventory/staging/checks, not separately timed | Small / low-medium; mutable files, handles, drive contention | P2, elevate if measured major hotspot; fast SSD/NVMe may benefit, saturated disks may not |
| Independent staging/copies, T24 | 17m30s including retained preparation | Medium / medium; duplicate retained targets and collisions | P2: storage-dependent; more CPU alone does not ensure improvement |
| Report thumbnail workers, T25 | Part of 41m16s total report refresh | Medium / medium; shared thumbnail/cache output ownership | P1 report target after separating image cost from history verification |
| Cross-page history reuse, gallery L18 | Another part of the same 41m16s | Medium / medium; complete dependency/mutation invalidation | P1: remove duplicate Review/Overview history work; do not run both whole publishers concurrently |
| Installed/gallery checks, T26 | 16m33s plus 9m38s | Medium / medium; freeze inputs, preserve diagnostics/seals | P2: independent decode/render/hash checks may scale; never reduce coverage |
| New-machine intake tuning, T27 | 2h44m32s intake; skipped in pickup | Small configuration experiment / low correctness, moderate memory/oversubscription risk | P1 at new-machine setup; supported workers already exist, benchmark rather than assume |
| Matching/refinement, T28 | 15m11s historical matching; algorithm has changed | Large / high; dependent passes and shared identity state | P3 holding: profile independent comparisons only after larger targets; no concurrent passes |
| Final publication/swaps | Not isolated from historical verification/recovery | High correctness risk | Keep ordered; no parallel publication proposal approved |

### Approved execution slices

**Transferred contract: T20 -> [reset T20](2026-11-05-priority-reset.md#m1-execution-and-transfer-ledger), not completed.** After the active run settles, isolate current-category/
  external inventory time and repeated retained/derivative verification
  calls. Reuse verified evidence within one operation and preserve path,
  hash, owner, scope and mutation invalidation. Do not waive input or
  publication checks. Compare call/read/byte counts and elapsed time on the
  same inputs; report any unresolved bottleneck explicitly.
**Transferred contract: T21 -> [reset T21](2026-11-05-priority-reset.md#m1-execution-and-transfer-ledger), not completed.** Implement bounded derivative workers partitioned by
  verified person-folder ownership, with sequential per-folder manifest
  updates and deterministic aggregation. Refuse overlapping/shared targets;
  preserve edited/unowned assets, quality holds, pixels and manifest entries.
  Prove serial/parallel equivalence, failure reporting and repeat behavior;
  benchmark the measured 54m40s phase before choosing worker defaults.
  **Nov 5 15:26 priority confirmation:** the user identifies the running
  derivative phase as a definite speed target. Include repeated per-framing
  source opening/decoding and per-person manifest verification/reload/write
  costs in T29's baseline and T21's implementation assessment, not worker
  count alone. Existing operation-local hash reuse does not eliminate those
  costs. The logged read count is cumulative counted operations, not unique
  files or all image/direct reads; 100-photo progress lines do not restart
  the loop. Isolate costs before attributing the slowdown or claiming gains.
  Preserve framing exclusions and exact pixels/ownership/failure behavior.
  No runtime edits or benchmark I/O during the active installation.
**Transferred contract: T22 -> [reset T22](2026-11-05-priority-reset.md#m1-execution-and-transfer-ledger), not completed.** Parallelize retained-detail refresh by proven independent
  ownership units, coordinating with T21's executor/error/progress patterns
  only where genuinely shared. No cross-worker manifest/cache writes or
  hidden stale verification positives. Test exact links/content/checksums,
  tampering, partial worker failure and deterministic diagnostics; benchmark
  the 17m02s phase.
- [ ] **P2 ai** T23 Benchmark bounded hash batches on representative library
  storage, then implement only where wall time improves. Keep verified path
  checks, stable output ordering, full file reads/seals and explicit errors.
  Limit open handles and queue memory; compare cold/warm runs and concurrent
  disk load. No timestamp-only trust or assumed SSD speedup.
- [ ] **P2 ai** T24 Benchmark ownership-partitioned native/retained staging
  copies, after T20 establishes redundant verification costs. Resolve
  duplicate/shared artifacts and destination collisions before submission;
  deterministic manifests and final hashes remain parent-owned. Keep
  byte-distinct originals, source evidence and the selected recovery policy.
  Test failed workers/partial stages; retain serial execution if faster.
- [ ] **P1 ai** T25 Split report image/thumbnail costs from history audit
  costs, then use bounded workers for independent thumbnail rendering with
  one coordinator for shared assets/manifests and ordered page publication.
  Consume gallery L18's history reuse rather than duplicate it. Compare
  source/row counts, output images/links, warnings and browser behavior;
  no simultaneous whole Review/Overview publisher writes.
- [ ] **P2 ai** T26 After verified publication, parallelize only independent
  installed/gallery verification units with deterministic complete results.
  Preserve every hash, path/scope, decode/render comparison, framing exclusion
  and edited/missing-asset failure; recheck input stability before success.
  Benchmark separate installed and gallery checks, not just worker CPU time.
- [ ] **P1 either** T27 On the new machine, benchmark existing intake worker/
  thread settings against a fixed representative cohort before selecting
  defaults. Record CPU/RAM/storage, peak memory, ComfyUI load, wall time and
  exact image/decision equivalence. Prior three-versus-four-worker results
  on this machine are not a cap for new hardware; more workers are not
  automatically faster. FULL validation remains separately scheduled there.
- [ ] **P3 ai** T28 Holding: after larger measured targets, profile matching/
  refinement and propose any independent comparison/vectorization slice.
  Resume only if it remains a major bottleneck and the user selects it.
  Frozen references, sequential pass/core rebuilding, deterministic ties,
  quality/rejection/protection gates and ordered publication remain intact.

Order (refined at 14:41): active-run evidence -> T29 baseline -> T20 ->
T21/T22 and gallery L18. T25 and T23/T24/T26 require the extras gate above;
T27 belongs to new-machine
setup, not the current install. T17 supplies missing measurements without
requiring a new broad instrumentation project before every bounded test.
No numerical speedup is promised. Acceptance is lower verified wall time
with unchanged pixels, routes, manifest entries and diagnostics, not 100% CPU.

**Scheduling:** T16 installed measurements and actual viewers passed.
The historical scheduling paragraph below is superseded for the newly
approved T20-T28 slices by the Nov 5 order above.
Next, after storage budget review: T17 statistics before bounded I68/I69 experiments.
T18/T19 profiles/CUSTOM and T13-T15 remain scheduled backlog, not today's
parallel implementation list.

Source: the user's Oct 28 notes (`feedback/random_thoughts.md`, preserved word for
word at the end). Three topics: faster intake preparation on this machine,
whether the likeness face crop should include the chin, and where the images
generated by all the runs should live.

## 1. Parallel intake preparation

### Measurements (Oct 28)

Machine: AMD Ryzen 5 5500 (6 cores, 12 threads), 24 GB RAM, RTX 3050 6 GB. Intake
runs on the CPU only (Mask R-CNN person detector, LaMa fill, OpenCV, NumPy,
Pillow); the GPU stays free for ComfyUI.

Where r20 spent its ~5 hours (sum of per-variant seconds, 2,741 images):

| Step | Images | Seconds | Note |
| --- | --- | --- | --- |
| denoise (incl. the pipeline tail before it) | 2,730 | 8,816 | Mostly the person detector and face pass, not the bilateral filter |
| composition | 472 | 2,051 | |
| head-overlay reconstruction | 316 | 1,227 | LaMa fill, ~6.5 s per filled image |
| control, first crop, masks, eraser, tone | | ~4,560 | |

A profile of four images showed torch convolutions, LaMa, NumPy reductions and
PNG encoding as the hot spots. A single process averaged only ~53% CPU: torch
uses up to 8 threads, but NumPy, Pillow, OpenCV filters and Python run on one.

Benchmark: a fixed 30-image mix (20 unchanged, 3 reconstruction, 3
composition, 2 first-crop, 2 Junk), `tmp\perf\bench.json`:

| Workers | Seconds/image | Peak memory | Mean CPU |
| --- | --- | --- | --- |
| 1 (old behaviour) | 6.97 | 1.9 GB | 53% |
| 2 | 4.94-5.44 | 3.7 GB | 67-77% |
| 3 | 4.51-4.77 | 5.1 GB | 69-74% |
| 4 | 4.56 | 6.5 GB | 72% |

One early 3-worker run (12.1 s/image at 37% CPU) coincided with other machine
load and was repeated twice. Every parallel run gave **byte-identical**
outputs: the same 30/30 outcomes and recommendations and all 126 variant files.

### Decisions

- **Process pool, whole images per task.** `image_preparation.publish` sends
  each image to a spawned worker; rows are written back in input order, so the
  report, manifest and progress lines are unchanged. Byte-identical inputs
  (same SHA-256) share retained and candidate paths, so each such group renders
  in one task, exactly as a serial run would.
- **Thread split.** Each worker gets `cpu_count / workers` torch and OpenCV
  threads (`ST_INTAKE_THREADS`), avoiding oversubscription.
- **Automatic worker count, capped at 3.** Four workers were no faster. The
  default is one worker per 2.5 GB of free memory, at most 3 and at most
  `cpu_count / 4`, so a run started while ComfyUI holds memory uses fewer
  workers instead of paging. `--workers N` (image preparation and
  `clean-rebase`) or `ST_INTAKE_WORKERS` overrides it. Batches under 16 images
  stay serial: each worker loads its own models (~10 s).
- **PNG compression level 3** instead of Pillow's 6: ~33% faster encoding for
  ~4% larger files, identical pixels. Not a recipe change (the recipe governs
  pixels; file hashes are recorded per run).
- **Likeness stays single-process**, as requested; matching is untouched.
- Not done: GPU inference for intake. ComfyUI owns the 6 GB card, and the
  models would contend with it; revisit only if intake becomes a bottleneck
  again.

Validation: 166 focused tests pass (`test_image_preparation` with new
`ParallelPreparationTests` for order, duplicate grouping and the worker count,
plus overlays, provenance, intake sequence, retained preparation,
`tools.art.test_clean_preparation` and `test_clean_rebase`).

Oct 29 continuation: the clean Working rehearsal and separately timed intake/
matching/report checks belong to storage S20. That run covers 3,072 current
inputs, not the previous 2,741-input population. Report both counts and
resource/load differences; a higher rate alone cannot isolate the effect of
removing old generated runs. The bounded input enumerators never ingest those
reports as additional photos.

- [x] **P1 ai** T1 Parallel preparation, automatic worker count, PNG level 3, tests.
- [x] **P1 ai** T2 Prove it at scale: the full v21 intake run
  `_sandbox-state\r21b-20261028` with 3 workers; compare wall time and outcome
  counts against r20 (5 h 02 min, ~9 images/min) and record the result here.

The full run started at 18:52:29 and published its intake receipt at 21:33:06
(2 h 40 m 37 s; 17.1 outcomes/minute), versus r20's 5 h 02 m (~9.1/minute),
about 1.9x the throughput. It verified all 2,741 outcomes. The outcome buckets
are unchanged from r20: 2,626 compared, 104 compared-overlay and 11
junk-candidate. Recommendations changed from r20's 2,382 original / 212
head-overlay-reconstruction to 2,372 / 222 respectively; composition (104),
first-crop (32), and none (11) stayed the same. This is the expected effect of
the new Dola AI reference: ten more images now use head-overlay reconstruction.

### Oct 29: bounded profile before another full run

The interrupted fresh run last reported 1,445/3,072 at 08:24:45,
about 14.4 ordered outcomes/minute since 06:44:17. Its Python processes were
absent at 08:27; no completed intake receipt or explicit error was present.
The cause is unproven. A restart reused the verified input mirror but
discarded orphaned preparation staging and began rendering again. That
restart was deliberately stopped at the user's profiling pivot. No full
intake or matching run is active at this checkpoint.

- [x] **P1 ai** T5 Profile the fixed 30-image mix on current v21 without
  concurrent tests/hooks; repeat old/new timings, prove exact artifacts and
  decisions, and retain only a bounded behavior-preserving optimization.
- [x] **P1 ai** T6 Before another full intake attempt, implement and test
  per-image checkpoint recovery bound to input hashes, recipe/configuration,
  and complete artifact hashes. Published reports remain immutable; never
  reuse incomplete or changed evidence as successful results. Show completed
  worker work independently of ordered report progress. Coordinate with
  storage S20 and intake I60; this is a reliability prerequisite, not another
  storage-layout refactor.

Implemented Oct 29. The report staging tree itself is durable across retries;
verified worker artifacts are removed as each row is materialized, avoiding a
second full copy of completed report output. A partial materialization can be
completed from its still-verified worker checkpoint. The 74 image-preparation
tests and 11 temporary-storage tests pass, including changed-input/artifact
rejection and OS-lock reacquisition after a subprocess exit.

- [x] **P1 ai** T7 Add a conservative overlay/border-first gate before
  person segmentation. Reuse body-independent pattern proposals, retain
  subject protection for potential repairs/crops and unknown states, and
  label misses as unassessed rather than clean. Intentionally omit
  composition-only suggestions on the no-proposal path. Version the recipe,
  preserve old reports, and measure unchanged-image savings against the same
  fixed sample without losing its selected repairs.
- **v23 follow-up (Oct 29):** the user clarified that no-proposal person
  composition is useful when it improves workflow framing. v23 now runs person
  detection on that path and recommends a composition only after the
  grown-subject mask-loss guard; hair/feet still require visual review.
  Composition suggestions on proposal paths remain comparison-only.
- [x] **P1 ai** T12 Before another full intake, close the v22 performance
  decision review: reconcile the paired 128-image profile with the eager
  behavior, identify any remaining behavior-preserving optimization worth a
  bounded test, and record each measured hotspot as optimized, retained or
  deferred with a reason. Explicitly account for the 48 composition
  comparison artifacts omitted in v22. v23 implements the user's clarification:
  the selected recommendation and denoise/tone alternatives are padded, while
  masks and interim candidates remain native-sized. Verify the regenerated
  composition evidence and visual output, and measure v23 cost before S15 or a
  full intake. The user has approved this behavior change; do not broaden it to
  other cleanup/reconstruction policies without asking. This gate remains
  closed for the authorized sandbox iteration by the Oct 29 measurements
  below; this is not production-quality acceptance or approval to install
  an unaudited matching preview.

The original fixed 30 paths were resolved against the fresh frozen input
mirror, with unique stable-photo-ID resolution when paths had moved. Both
baseline and optimized runs used those exact bytes and three workers.
The mix yielded 20 original recommendations, 3 reconstruction, 3 composition,
2 first-crop and 2 unusable recommendations.

Python 3.14 cProfile captured each image inside its actual spawned worker,
not merely the parent waiting on futures. The profiled pass took 131.91
seconds; summed image-worker time was 345.66 seconds. Worker times overlap
and cannot be added to wall time. This is deterministic function profiling,
not native-stack sampling or a pure CPU-time breakdown.

| Measured helper | Calls | Summed worker seconds | Seconds per input |
| --- | ---: | ---: | ---: |
| Mask R-CNN subject detection, including first-use setup | 28 | 152.42 | 5.081 |
| LaMa masked fill | 10 | 79.49 | 2.650 |
| White UI stroke/component helper | 252 | 30.26 | 1.009 |
| Watermark detection | 28 | 29.16 | 0.972 |
| Save/encode image artifacts | 378 | 19.31 | 0.644 |
| General clutter detection | 32 | 14.80 | 0.493 |
| Logo reference matching | 28 | 8.78 | 0.293 |
| Badge detection | 60 | 8.62 | 0.287 |
| Face detection | 30 | 5.67 | 0.189 |
| Original decoding | 30 | 0.80 | 0.027 |
| File hashing | 468 | 0.64 | 0.021 |
| Original copying | 30 | 0.12 | 0.004 |

These are inclusive helper times: watermark/component/clutter measurements
overlap and must not be summed as independent buckets. Person detection and
fill together account for about 67% of measured image-worker time. Mask
construction did not emerge as the main bottleneck. Saving includes encoding;
it is not a measurement of waiting for B: alone.

The profile attributed 49.8 seconds to NumPy channel min/max reductions.
The white-stroke helper repeatedly reduced three-channel RGB arrays with a
generic strided axis reduction. Explicit pairwise unsigned-channel extrema,
then conversion to signed 16-bit, preserve exact values and chroma arithmetic.
The 1080x2340 operation microbenchmark measured 97.7 ms versus 9.2 ms.
Only that measured helper changed; detector thresholds, model resolution,
recipe and masks/selection policy are unchanged.

| Unprofiled pass | Old helper | Exact pairwise helper |
| --- | ---: | ---: |
| First 30-image pass | 125.35 s | 119.06 s |
| Repeat | 127.28 s | 126.47 s |
| Mean | 126.32 s | 122.76 s |

Mean elapsed reduction is 2.8% (throughput +2.9%); the repeated gain is small
and variable, not evidence of a major end-to-end speedup. Old/new throughput
means approximately 14.25 versus 14.66 inputs/minute for this sample, not a
full-run forecast. All four runs have identical non-timing per-photo records,
recipe, and 408 retained/candidate/preview/padded artifact hashes. HTML hashes
vary because the pages display recorded elapsed times.

Validation: 133 overlay/preparation/intake-sequence tests pass, including RGB
extrema over all red/green values, representative blue extremes, strided views,
signed chroma, and component equivalence with/without contrast/vivid edges.
Report manifests and images remain under the fresh run input mirror's
`_reports\preparation\baseline-current-20261029`,
`optimized-current-20261029`, `baseline-repeat-20261029`, and
`optimized-repeat-20261029`. Disposable profiles/logs are in repository
`tmp\perf`; this plan retains the measured conclusions and acceptance evidence.

Brief late-sample system observations ranged from 36-55% machine CPU with
9.3-9.5 GB available RAM, disk activity about 26-157 MB/s and aggregate queue
length 1.1-1.3. These three snapshots are not whole-run averages and do not
isolate B: from other disks. No claim of disk saturation or cleanup-induced
speedup follows from them.

### Oct 29: overlay-first v22 and the larger paired profile

The historical recipe is **v22**. After face eligibility, border/letterbox/reel
and known-pattern proposals run before Mask R-CNN. No proposal triggers an
additional broad, body-agnostic glyph check. If that also finds nothing,
retain the original pixels as **unassessed**, skip subject segmentation and
composition-only suggestions, and still generate denoise/tone comparisons.
Any border, screenshot, pattern or uncertain glyph takes the protected path.
Pattern proposals are reused in original source coordinates. Body-sensitive
clutter is rechecked with the person mask and current crop; post-fill residual
detection is unchanged. Detection exceptions cannot become no-proposal success.
The experimental comparison command retains its eager behavior; published
v22 and older receipts keep their historical validation/step contracts.

The original 30-image sample avoided 20 of 28 subject calls, preserving all
recommendations, selected pixels and 354 shared candidate/preview/padded
hashes. Eight rejected, composition-only comparisons were intentionally
omitted. Unprofiled v22 repeats took **76.99 / 77.65 seconds** (mean 77.32),
versus the RGB-optimized eager repeats of 119.06 / 126.47 (mean 122.76):
**37.0% less elapsed time**, without claiming a full-run forecast.

The larger deterministic sample retains those 30 and adds 98 inputs:
18 Angels, 18 Sisters, 20 Artists, 22 Prospects, 21 Potentials, 29 Various.
Screenshot-named inputs were preferred before hash-ordered category
round-robin expansion; there are 14 such names and 16 detected screenshots.
This is a mixed stress sample, not a population-weighted quality dataset.
Both passes used the same 128 source hashes, three workers, current RGB
optimization, per-image cProfile and identical fill-call instrumentation;
no concurrent tests/hooks. The eager pass explicitly disables only the gate
and marks that benchmark override in its recipe. Neither run installs,
matches, changes sources, or touches Production.

| Metric | Eager | Overlay-first |
| --- | ---: | ---: |
| Elapsed including publish/verify | 524.48 s | 302.50 s |
| Outcomes/minute | 14.64 | 25.39 |
| Summed image-worker time (overlapping) | 1,525.90 s | 854.99 s |
| Subject calls | 125 | 35 |
| Guarded fill calls | 18 | 18 |
| Reconstruction fill calls | 25 | 25 |
| Neural fill patches across those 43 calls | 116 | 116 |

This larger instrumented pair is **42.3% less elapsed time / 1.73x throughput**.
Ninety usable images have no proposals; 35 require protection; three are
ineligible. All **128/128 recommendations, outcomes, source treatments,
eligibility and geometry** agree: 97 original, 16 reconstructed composition,
nine reconstruction, three crop-only, three unusable. All **1,569 shared
candidate/preview/padded artifact hashes** agree, as do the non-timing
edited-image candidate/decision/mask traces. Sixteen rejected composition-only
comparisons are omitted, accounting for 48 fewer saved image artifacts.
No claim that every optional comparison remains present. Fill-call and neural
patch counts are unchanged; their different measured duration reflects
scheduling/contention, not a fill-algorithm optimization.

#### Where current image-worker time goes

Inclusive helper times below overlap; do not sum them as exclusive percentages.
Each per-input figure divides by all 128 inputs, including skipped ones.

| Helper | Calls | Worker seconds | Seconds/input |
| --- | ---: | ---: | ---: |
| LaMa fill, both purposes | 43 | 289.86 | 2.26 |
| Person segmentation, first-use setup included | 35 | 184.09 | 1.44 |
| Known-pattern proposal bank | 125 | 114.85 | 0.90 |
| Encode/write candidate, preview and padded images | 1,569 | 80.45 | 0.63 |
| Glyph detection, across preflight/guarded/head checks | 171 | 59.30 | 0.46 |
| General guarded/residual clutter | 53 | 41.64 | 0.33 |
| Logo references (inside proposal bank) | 125 | 37.48 | 0.29 |
| Watermarks (inside proposal bank) | 125 | 25.49 | 0.20 |
| Tilted stickers (inside proposal bank) | 125 | 22.40 | 0.17 |
| Face detector's native detection | 128 | 16.29 | 0.13 |
| Original decode | 128 | 3.72 | 0.03 |
| File hashing | 1,953 | 2.74 | 0.02 |
| Original copy | 128 | 0.44 | <0.01 |

PNG/JPEG encoding itself accounts for 73.47 worker seconds within saving.
That is not a measurement of B: write latency alone. NumPy reductions still
consume 101.28 worker seconds across helpers. The glyph routine repeatedly
materializes full-image component masks; exact RGB extrema reuse, bounded
component operations and raw-proposal reuse are investigation candidates.
Do not silently remove safety checks or lower detector thresholds to save time.

| v22 path | Images | Median worker seconds | p90 worker seconds |
| --- | ---: | ---: | ---: |
| No proposals, including required outputs | 90 | 1.98 | 2.98 |
| Any proposal/protection | 35 | 14.79 | 33.74 |
| Original recommendation, including seven flagged but unchanged images | 97 | 2.01 | 3.34 |
| Crop-only | 3 | 8.51 | 12.66 |
| Reconstruction without selected picture composition | 9 | 11.22 | 14.95 |
| Reconstructed picture composition | 16 | 28.80 | 38.56 |
| Unusable | 3 | 0.27 | 0.29 |

These are individual worker latencies, not serial wall-time forecasts.
For routine intake, ordinary photos with no detected marks are cheapest;
screenshots needing several separate filled regions are most expensive.
Original recommendation alone does not mean no detector work.

### T12: current measured disposition

- **Optimized:** exact pairwise RGB extrema averaged 2.8% lower elapsed time
  across two repeats. The v22 preflight gate cut the paired 128-image elapsed
  time by 42.3%, with the same recommendations and 1,569 shared artifact
  hashes.
- **Retained:** detector thresholds/resizing, safety checks and both fill
  stages. Their output/context is behavior-sensitive; neither profile proves
  an equivalent substitute.
- **Validated targeted optimization:** a bounded A/B ran `clutter.glyphs`
  (`screenshot=False`) over the same 128 sandbox inputs, alternating execution
  order. The original axis reductions and repeated component-mask builds took
  25.806 s; exact pairwise RGB bounds plus one reused component mask took
  12.573 s (51.3% lower glyph-only time). All returned part types, boxes,
  reasons and mask hashes matched. Decode, proposal detection and full-run
  wall time were not measured by this A/B.
- **Still unproven:** the gated cProfile attributes 114.85 summed worker
  seconds to `overlay_proposals` (125 calls) and 59.30 to `clutter.glyphs`
  (171 calls, 28.69 self seconds). Nested detector times overlap. The glyph
  change is a confirmed local saving, not proof of a similar full-intake
  reduction. Further proposal-bank reuse/reordering needs its own exact-output
  A/B; no safe additional end-to-end saving is established.
- **Deferred:** person-inference resizing and LaMa fill internals need separate
  equivalence evidence before any change. Copy and hashing took under four
  summed worker seconds in the 128-image pass; encoding was measured, but disk
  write latency was not isolated.
- **Requested behavior; verified sandbox sample below:** assess useful person
  composition rather than assuming no proposals means no improvement.
  Padding belongs only on the chosen
  recommendation and denoise/tone alternatives. v23 implements guarded
  no-proposal composition selection and selective padding. The outputs were
  regenerated, inspected and measured below; full-run and final user
  acceptance remain separate.

#### Oct 29: verified v23 sample and disposition

The actual checkpoint worker, rather than the obsolete `rendered_rows` hook,
captured all 128 per-image profiles. Ordered source paths and SHA-256 values
exactly match the eager/v22 sample. The immutable report is
`fresh-r21-20261029\inputs\_reports\preparation\v23-profile-128-20261029`.

| Result | Verified value |
| --- | --- |
| Profiled elapsed, including publication verification | 974.34 s; not a speed improvement over historical v22 |
| Outcomes | 109 compared, 16 compared-overlay, 3 junk candidates; no assessment/decode errors |
| Changed recommendations | 14 originals become guarded person compositions; all other selections agree |
| Shared artifact checks | 1,286 matching hashes; 84 differences are exactly native/preview/padded denoise and tone derived from the 14 new compositions |
| Workflow padding versus eager sample | 539 -> 375 files: exactly three outputs for each of 125 usable photos; no mask/interim padding |
| Unprofiled repeat | Original fixed 30 images: 222.75 s, three workers, identical recommendations and 323 shared variant artifact hashes; separate padded originals also agree |

Historical unprofiled eager/gated results (122.76/77.32 s) are not current v23
throughput claims. The current policy deliberately restores person assessment;
checkpoint isolation/publication also changes I/O. No CPU resize, fill or
safety shortcut was adopted to recover the earlier timing.

Summed inclusive worker costs overlap: checkpoint 2,501.42 s, native render
1,945.03 s, person detection 624.94 s, fill 349.79 s (43 calls), proposal bank
134.69 s, glyph checks 43.10 s, encoding/write 739.59 s and padding 254.10 s.
Directory creation accounts for 639.03 worker seconds across 2,218 calls;
file opens also consume 207.00 s. This identifies real filesystem work, not
proof that PNG compression alone is the bottleneck. A 40-call existing-folder
probe took only 0.0051 s (`mkdir(exist_ok=True)`) versus 0.0020 s (directory
check first); it does not reproduce the creation workload, so no speculative
directory-check optimization was applied.

Disposition: retain person/face/crop guards, both fill stages, exact artifact
hashes and durable per-image recovery; keep the validated glyph optimization.
Further filesystem/layout and inference work stays with S11/T8/T11 after the
sandbox milestone unless a concrete failure blocks it. The slower current
throughput is measured and visible, not hidden behind the obsolete 42.3%
claim.

AI first pass reviewed all 32 source-identified sheets (128 photos), the 14
new selected compositions in context, and selected native files at full size.
No obvious new person truncation was identified at sheet resolution; this is
not a hair/feet completeness proof or the user's final inspection. Direct
native checks dismissed several thumbnail-level suspicions on clean originals.
One definite inherited failure is sample row 33,
`Various/gallery/Screenshot_20260902_204050_Facebook.jpg`: the selected
reconstruction/composition still contains the large lower translucent panel,
nested phone and corner text-search control. Its shared pixels match the
eager baseline; retain it as an I60 cleanup defect, not a clean success or a
new reason to redesign storage. Production acceptance remains open.

Current validation: 216 focused preparation/history/sequence/overlay/eraser/
temporary-storage tests pass, including original/selected padding tampering,
skipped/decode-failed rows, real-mask crop guards and v23 interrupted recovery.
The earlier 155-test integration pass had two provenance failures; their
sparse-path reader and genuine v6 fixture were corrected, and all 22
provenance tests now pass in the focused run. Other integration tests passed;
this is not a new whole-repository suite result. Isolated validator smoke
checks pass 19/19. Routine hygiene passed before these result notes and is
rerun after them.

S15's supported inventory preview names only sandbox Working and the new
`fresh-v23-20261029` run: 2,700 assigned images plus 372 current Various inputs
= 3,072 outcomes, with 75 IDs using newer Various bytes. It made no changes
and evaluated no moves or cast releases. Proceed only to the already
authorized intake-only sandbox iteration; audit full-run outputs and matching
before installation. Production and immutable Source remain untouched.

Execution result: `fresh-v23-20261029` intake-only completed successfully
with three workers. The separate supported launcher
`--baseline working --check` verifies all 3,072 outcomes and their artifacts;
`intake.json` reports `assessmentErrors: false`. Counts: 2,966 compared,
96 compared-overlay, 10 junk candidates. Recommendations: 2,225 original,
479 composition, 230 head-overlay-reconstruction, 96 head-overlay-composition,
32 first-crop and 10 none. The 3,062 usable rows produce 9,186 padded outputs.
Preparation manifest SHA-256:
`5b0c856c50153e413a99d7db8623666354ea8a8a46319ec18f6e3bf8352f2181`.
The progress log is `tmp\perf\fresh-v23-20261029-intake.log`; durable evidence
is the run's `intake.json` and verified preparation manifest. That checkpoint
preceded matching. Subsequent full-run output screening and the matching-only
incoming-ID correction are recorded in intake I60 and cast C8/C9. The revised
preview completed at 23:43 -05:00; installation/viewer acceptance remains.

Observed full-intake log lifetime was 16:49:03 to 21:35:41 (4 h 46 m 38 s),
including source overlay, rendering, publication and verification; it is not
an isolated worker-render timing. The initial matching command ran 22:06:46
to 22:30:23. The cache-reusing replan ran 23:03:16 to 23:43:54 with read-only
audit/snapshot-preview I/O alongside it. Verification and repeated file
access dominate its quiet phases; cache reuse does not skip artifact checks.
Do not attribute that comparison to model inference or storage cleanup alone.
Captured replan output is timestamped; its process was checked for progress
and was not suspended. T15 still owns useful producer-side phase diagnostics.

#### Oct 30: measured installation blocker

The first install was active, not suspended, but derivative progress was
only 376 of 2,793 sources after hours. A bounded live `py-spy` sample
(15 seconds, 10 Hz, 148 samples, no sampling errors) found
`source_is_prepared` in 141 samples, operational storage-root resolution in
100 and configuration loading/validation in 74. These categories overlap;
they are not additive or an isolated whole-install timing.

The repeated owner scan classified native category paths by loading and
resolving unrelated operational roots for every retained set. Native
categories cannot overlap those roots by the shared configuration contract.
The narrow fix classifies native paths directly; configured Junk/retired
wrappers still resolve through the validated shared configuration, now reusing
the configuration already loaded. No artifact/path/source/hash check, pixel,
recipe, matching threshold or assignment changes.

A failing regression reproduced configuration reads for all seven native
categories. It now proves zero reads; custom Junk/retired classification
still passes and loads configuration once per call. All **68 focused
retained/preparation/clean-rebase tests pass** (166.666 s). The first run
encountered a Windows directory-rename denial; the isolated test and complete
rerun passed without a behavior workaround.

The identical real Haniya retained-native check returns `True` before and
after: **5.602 s -> 0.597 s**. This is one representative guard check, not a
claim of a 9.4x full-install speedup. Live samples and benchmark outputs are
under `tmp/perf`; the intake/artifact manifest and preview remain unchanged.

The slow attempt was stopped only after confirming the stack remained inside
pre-publication derivative generation, plan `preview`, no publication fields,
and an empty `previous`. After termination, all **2,868 Working input hashes**
and the original catalogue hash were verified unchanged. No staged work was
deleted: it was renamed to `abandoned-staged-20261030-040207`, with the empty
previous directory similarly preserved. The durable run-local
`install-attempt-20261030-040207.json` records that proof and both locations.
The first retry correctly refused because the saved implementation hashes
predated the fix; no staging/publication occurred. Preserve that preview as
`pre-native-domain-preview.json` and use the supported measurement-reusing
`--replan` to rebind the engine, without repeating intake. Compare every
source/destination/reason/selected hash against the saved audited preview
before applying; do not hand-edit implementation hashes or bypass the guard.
The replan started at 04:15 -05:00 with timestamped, unbuffered capture.
It completed at 04:23:54 with exit 0. **All 2,793 photo rows are exactly
identical** to the saved audited preview, as are Working inputs, policy,
cast-seed mode, preparation and both catalogue bindings. Only the recorded
`retained_preparation.py` implementation hash changed. New preview SHA-256:
`ec72a3523ccce9f0d3b26cf1a915fe071b4d9355735d9fb483e500f1cc3f7fc1`.
The engine-bound apply began at 04:24:53; it independently reverified the full
72,991-file backup at 04:33:51. All 2,793 derivative sets (8,255 entries)
completed by 06:58:10; retained detail refresh followed. At 08:15:05 the
pre-publication collision guard refused 2,401 unowned legacy cast outputs.
`previous` remains empty and the saved plan remains `preview`; complete staging
must be recovered, not discarded. The old bytes are not proven reproducible.
Explicit exact-byte preservation and verified completed-stage resume are the
bounded prerequisite; actual install/viewer acceptance remains open.

At 09:22 the user requested a pause and recap. Completed-stage recovery and
explicit exact-byte legacy preservation are tested and pushed as `81325da1f`
(71 focused tests, the 20-test backup/recovery group with overlap, and two
additional tampering/owned-edit checks passed). The supported replan started
at 09:08:57 was stopped before replacing the preview. Its SHA remains
`ec72a3523ccce9f0d3b26cf1a915fe071b4d9355735d9fb483e500f1cc3f7fc1`;
`pre-stage-recovery-preview.json` preserves that checkpoint. Complete staging
and empty `previous` remain; no apply is running. T16 stays open until actual
full-stage check/recovery, publication and viewer verification. See the
[current reboot-resume recap](../recap/2026-10-30-1247-recap.md).

The user resumed the human-review milestone at 09:53. The supported replan
ran 09:54:17 to 10:03:30, preserving all 2,793 rows and every audited input,
policy, preparation, overlay and catalogue binding. Its preview SHA-256 is
`616893eabf7e73921291bbe6a4c82be435eeb3c41f2d5becee22af3f9ade458b`.
The real completed-stage `--resume-install --preserve-legacy-derivatives
--check` ran 10:03:45 to 10:45:35, exit 0: 2,793 photos and 48,792 files
verify, including exact retained artifacts and recipe-rendered derivative
hashes. This 41-minute check is measured integrity/render work, not a cheap
receipt lookup or a claim that installation I/O is solved.

The exact old-file preservation inventory is 2,402 (1,218 padded and 1,184
head), not just the 2,401 replacement conflicts. One additional old Drakniss
headshot has no staged replacement under the current quality gate; preserve
it for undo rather than advertise it as a valid new derivative.
Backed-up completed-stage apply began 10:53:34; the full 72,991-file snapshot
independently reverified at 11:02:06. Apply rechecks the stage before the swap;
publication and installed-viewer acceptance are still pending.

At 11:46:33 apply exited 1 during the category transaction: Explorer PID 12768
held two handles on `Working/Various/gallery`, blocking the rename into
`previous/Various`. The normal rollback restored prior categories and external
files; independent verification proves all 2,868 Working input hashes and the
source catalogue unchanged. `previous` contains no files, only external-file
directory scaffolding; complete staging is preserved and the plan is still
`preview`. Durable receipt: `install-attempt-20261030-114633.json`.

A graceful Explorer-window close did not release the handles; the final
11:57 query still shows them. No forced handle close, process termination or
desktop restart was performed. The user-question tool reported the user
unavailable, so installation is blocked until the lock can be safely released.
Do not repeat full intake or discard the completed stage.

The narrowly coupled recovery fix accepts directory-only rollback scaffolding
only after a no-follow walk proves zero files; linked paths and any retained
file still refuse. Two targeted recovery/tampering tests passed. The full
29-test preparation suite first encountered the previously observed transient
Windows fixture-publication denial, then passed unchanged on a complete rerun
(182.503 s). This source change needs supported replan before another apply.
T16 stays open; no installed/browser acceptance is claimed.

A matching 15-second/10-Hz live sample during the fixed derivative stage
collected 147 samples without errors: **zero configuration loading,
validation or operational-root resolution samples**. Retained-source
verification remains active (126 samples); this does not remove its path,
manifest or artifact hashing. The fixed sample is
`tmp/perf/fresh-v23-install-fixed-live.txt`. Remaining repeated owner scans
belong to later library I/O work, not another unmeasured restart.

- [x] **P1 ai** T16 Verify the config-free native-owner fix through the
  same backed-up install, independent check and actual viewers; record actual
  phase timings separately from the representative guard benchmark.

#### Oct 31: measured installed continuation

The same-stage apply completed successfully at 00:28:56 -05:00. No intake
was repeated; the original full backup was reverified and reused.

| Phase | Wall seconds | Interpretation |
| --- | --- | --- |
| Final completed-stage check | 2,577.37 | 2,793 photos / 48,792 files; includes integrity/render verification |
| Successful apply and viewer publication | 16,734.44 | Backup/stage checks, transaction and all viewers; not isolated swap time |
| Independent ordinary installed check | 1,764.78 | Supported launcher, exit 0; separate from subsequent rollback-byte audit |
| History-only repair | 1,148.85 | Artifact verification, one history page and ownership receipt; no photo-viewer rebuild |
| Independent history-only check | 2,262.19 | Read-only full saved-evidence verification, exit 0; strongly load-sensitive |

ComfyUI remained active; these are observed contended-machine timings, not a
controlled before/after speedup. Read-only live stack samples showed repeated
retained-manifest discovery in `write_thumbnails -> derivatives.verified ->
source_is_prepared -> crop_guard -> verify_link -> _manifests`.
Progress advanced from 641 to 884 of 2,793; the process was working, not
suspended. Review publication finished at 23:56:38; Overview followed.
One process observation reported about 376 GB read before completion, but
this is not a storage-device or isolated phase benchmark.

[Gallery L18](2026-10-22-gallery-review-layout.md) owns the bounded
verification-index optimization and its invalidation/hash/path invariants;
T15 owns timestamp/progress reporting. Do not remove provenance checks or
repeat the rebase to make the viewer seem faster. A distinct history-browser
49,709,196-byte manifest ceiling defect was reproduced during actual browser
acceptance; its bounded repair, 56 focused tests and strict 2,793-row browser
acceptance passed under C6/I59. Both history timing rows include full
artifact verification; a live check sample was in `verify -> path.read_bytes`
with an observed PageIn wait, not suspended execution. No cache/guard bypass
was introduced.

#### Oct 31: outcome-review speed priorities

**Implementation continuation:** the user's subsequent authorization is
preserved verbatim with [L18's delivered read-reuse slice and measured A/B](2026-10-22-gallery-review-layout.md#oct-31-l18-implementation).
It removes repeated retained-proof work within report operations and the
redundant staged-history mirror-input hash prepass; full content/path checks
remain. S24 also has an opt-in measured packing/restore experiment.
T15/T17 remain open for broader progress and recipe-aware processing statistics;
neither this bounded report optimization nor storage sampling is another intake
or approval to change parameters. The remainder below records the earlier audit.

The user's new request asks what worked, which cast/name outcomes need more
iterations, and where speed improvements are useful. The
[complete routing/name audit](2026-10-23-cast-seeded-library-rebase.md#oct-31-cast-routing-name-continuity-and-iteration-audit)
owns the verbatim request and per-slot results. This is measured analysis,
not a new intake, benchmark under load, recipe change or delivered speed fix.

**The next speed target is evidence/report I/O, not another segmentation
shortcut.** The applied state was observed by Oct 30, 21:04; the worker did not
exit until Oct 31, 00:28:56. At least about **3 h 25 min remained after that
observation**, approximately 73% of the successful 4 h 39 min apply. This
is a lower-bound remaining-viewer interval, not an instrumented swap/report
split; publication may have happened earlier. Contention remains a confounder,
but repeated work is visible in both the code and saved live stacks.

| Priority / existing owner | Evidence and bounded next experiment | Required guard |
| --- | --- | --- |
| P1 L18: reuse verification within a frozen report operation | A fully successful Review row calls `derivatives.verified` seven times: thumbnail and provenance for chest/head/face, then padded. Each calls `source_is_prepared`, which rediscovers owner sets and calls `crop_guard/verify_link`; the latter re-enumerates all owner manifests and hashes the matching artifact set. Reuse an explicit verified per-source result and owner index rather than independently proving the same source seven times | Operation-scoped immutable/locked inputs or explicit change detection; fail on stale, duplicate, linked or altered artifacts; never timestamp-only positive trust or unbounded process-global caching |
| P1 L18: separate whole-run audit from read-only presentation | The history-only repair still spent 1,148.85 s and its independent check 2,262.19 s because `_load_staged` validates every mirror input, artifact path and the complete original report. Static history generation isn't the expensive part. Measure one fully checked index reused across Overview/Review/history in the same frozen generation | Preserve complete explicit audit/check commands and source/domain/hash binding; cache invalidation/failed verification must be visible, not a success-shaped fallback |
| P2 T15: expose phase/progress | Multi-hour quiet periods caused repeated lock/stall investigations. Add elapsed time, verified/total files and phase boundaries to backup, stage verification, publication, thumbnail/evidence and history checks | Shared diagnostics; no semantic/recipe changes; report stalls/errors explicitly |
| P1 S24/S25: control file amplification | Metadata inventory: 48,792 published files for 2,793 people, about 17.5 files/photo. Retained evidence is 34,567 files, distinct from 2,793 retained originals and 8,255 maintained derivatives. Review adds 8,379 shared thumbnail files / 196,065,948 bytes | Measure bytes and restore cost before changing scope/format; no source pruning, archive-format assumption or collapsing distinct lineage |
| P1 T17 then I68-I70: measure useful processing | Existing paired profiles and checkpoint recovery worked, but speed must retain useful crop/mask/framing and explain attempted/skipped stages | Same frozen cases, recipe-aware counts and quality checks before another large recipe run |

Static amplification model, **not an observed call count or a promised
speedup**: with this run's destination-owner populations,
`sum(ownerPhotoCount^2) = 210,359`. Seven complete owner-manifest traversals
per successfully framed photo would visit about 1.47 million entries before
including source-location scans, preparation evidence, Overview or other
guards. Actual calls differ for unavailable derivatives and execution paths.
Drakniss alone contains 314 final Gallery/Review photos, making owner-wide
scans especially expensive. A bounded fixture benchmark should count
enumerations, manifest loads, artifact reads/bytes and wall time, not just
mock away the slow functions.

Suggested implementation acceptance: identical report records, evidence states,
links and derivative bytes on the same frozen fixture; fewer measured repeated
reads; rejection of a changed native/artifact/manifest and reparse paths; no
cross-root/domain reuse; explicit refresh/invalidation across mutation phases.
Then run one approved report-only scale check, not another intake/rebase.
No numerical speedup is claimed until that experiment runs.

#### Oct 30 review: observability and configurable processing

The complete 12:31 source and item ledger live in
[intake's reconciliation](2026-10-23-image-intake-preparation.md#oct-30-1231-full-human-review-feedback-reconciliation).
This adds next-round priorities, not changes to the bound v23 run.

- [ ] **P1 ai** T17 Capture recipe-aware run statistics and publish a compact
  intake summary with expandable/linked details: input/outcome counts, overlay
  types, each attempted/executed/skipped/failed step, reconstruction/composition,
  recommendation by variant, and enhancement choices. Include total wall time,
  stage timings, per-image/path averages and bottlenecks with denominators,
  unavailable fields and parallel worker sums clearly labelled. Derive fields
  from executed recipe/trace data, not fixed stage lists; don't double-count
  nested timings or compare pixel-change percentages across crop dimensions.
  Test totals/conservation and recipe evolution on saved data before new runs.
  **Oct 31 bounded increment:** preparation JSON/index now records actual
  image-role/unique-file/byte totals, worker count, invocation preparation
  wall time, outcome/recommendation counts and recipe-derived step/status
  counts, with verification/tamper tests. The mixed storage experiment adds
  complete external stage wall times and overlapping mirror, installed,
  backup, restore and history scopes. T17 remains open for finer executed
  stage timings, overlay-type/detail counts and per-image/bottleneck UX;
  preparation timing is not mislabeled as complete-run timing.
- [ ] **P2 ai** T18 Propose versioned data-driven recipe steps/order/branches
  and profile contracts: FULL preserves current behavior; FAST evaluates cheap
  size/aspect/overlay composition gates; OVERLAY-ONLY skips composition and
  reaches explicitly configured enhancements/exit sooner. Specify selective
  reprocessing for composition and enhancement on/off policy. Compare immutable
  same-input runs for missed overlays/composition, detail, recommendations,
  elapsed time and bytes; the suggested 90% control rate must be measured.
  Processing profiles and storage modes (LEAN/COLLAGE, storage S25) are
  orthogonal. Bind recipe/config hashes to checkpoints/resume and report
  experiment status; don't hard-code profile names as new branching logic.
  The Oct 31 duplicate-first direction and the first tested LEAN evidence
  slice live in [storage S25/S26](2026-10-28-storage-operations-and-retention.md#oct-31-lean-producer-proof).
  They precede this profile work: exact role reuse and omitted unselected
  padding do not skip enhancement/cleanup evaluation or implement FAST.
  Nov 2 ([library layout](2026-11-02-library-layout.md#modes-two-separate-axes)):
  LEAN no longer **keeps** unselected `tone`/`denoise` outputs, but they are
  still **computed** at that checkpoint although the recipe never selects
  enhancement. Nov 4 LY14a subsequently implements the approved LEAN skip;
  broader person/composition policy changes remain T18/I70 decisions.
- [ ] **P3 ai** T19 After T18's reviewed contract and bounded profile evidence,
  implement validated CUSTOM step/node definitions and versioned erase/
  reconstruction alternatives, reusing existing modules rather than rewriting
  the engine. Validate compatible inputs/outputs, allowed order/branches,
  acyclic execution, safety gates, unknown steps, failure and resume lineage.
  No arbitrary executable config, silent stage skipping or weakening protections.

The 12:31 feedback elevates the recurring mask-coordination problem into
intake I68/I69's **P1 next-round** work. T11's older P3 exploratory GMW
comparison is superseded in priority and covered there with I41; its raw
discussion remains preserved. T8's remaining background-only repair-policy
decision still needs its own evidence/approval; feedback does not silently
authorize larger repainted regions.

#### Nov 4: LEAN optimization proposals from the fresh run

Analysis only: no approval to change processing thresholds, skip person
detection, remove backups or introduce a shared blob store. T17 still owns
instrumentation and T18 owns processing-profile proposals; this does not
activate T19 or authorize another full run. Storage/copy implementation belongs
to [layout LY14](2026-11-02-library-layout.md#nov-4-copy-and-verification-proposals).

**22:02 authorization update:** LY14c/LY14d/LY14e now own approved
duplicate-first/verification reuse and explicit disposable sandbox recovery,
then a fresh measured run; the raw user messages remain in the layout plan.
Keep three separate axes: pixel-processing recipe, evidence storage
FULL/LEAN, and recovery full/disposable. The user's desired future FAST
profile can combine more aggressive processing, backup/rollback and reporting
omissions, but its exact contract and quality trade-offs still belong to T18.
Do not silently enable any FAST branch while implementing the approved
LEAN/disposable recovery shortcut. FULL/Production stays protective.

**Measured baseline:** 3,517 outcomes; four CPU workers. Intake end-to-end
10,854 s (180m54s), of which the recorded preparation invocation is 10,382 s
(173m02s). Previous intake was about 197 min for 2,814 outcomes: approximately
27% less wall time per outcome, not a controlled same-input speedup. This
denominator includes repeated inputs; it is not unique-photo throughput or
proof that all added work was useful (see layout LY14c). Current
original recommendations are 2,465 (70.1%); 1,048 (29.8%) select a changed
candidate and four have no usable recommendation. Changed selections comprise
402 reconstruction, 113 reconstructed composition, 498 composition and 35
first-crop. All 3,517 denoise/tone steps are skipped.

**Timing correction:** `image_preparation.render_photo` starts a timer between
generator yields. A variant's `seconds` includes pipeline work before its
yield plus encoding, not just its named filter. The earlier 305 denoise
worker-minute attribution therefore does not prove that removing denoise
removes 52% of CPU work. Skipping the filter/candidate does not skip guarded
person/composition assessment. T17 must distinguish exclusive helper timing,
inclusive pipeline timing, encoding and wall time before making a new forecast.
The existing 8.5 GiB historical comparison-render byte measurement is separate.

| Proposal | Benefit and evidence | Cost / downside / gate |
| --- | --- | --- |
| Reuse exact intermediate calculations in FULL and LEAN | Proposal masks, glyph components, RGB extrema and segmentation results can be reused within one immutable image evaluation. Earlier 128-image profiles identify these helpers; no pixel-policy change is intended. | Bound cache keys to bytes, geometry and detector/model config. Tests must prove identical pixels, masks, decisions and failures; no gain estimate yet. |
| Reuse verified prior preparation for exact unchanged inputs | Avoid rerunning models when source SHA, recipe/model/config and storage-output requirements match; reuse T6's exact checkpoint principles. | No basename/identity/mtime shortcuts. FULL cannot reuse a LEAN result lacking required comparisons. Verify artifacts and preserve cross-run provenance/retention dependencies. |
| FAST clean-photo branch | Cheap overlay/border/size/aspect checks could skip person segmentation and optional composition for apparently clean images. | Missed overlays and useful crops; 70% original recommendation is an outcome after assessment, not a safe classifier before it. This changes behavior and requires explicit approval and paired quality tests. |
| OVERLAY-ONLY branch | Preserve known-overlay cleanup, skip aesthetic composition on the clean branch. More narrowly targeted than removing all detection. | Still needs subject protection before any erase/crop; skips useful composition. Reconstruction may still need segmentation. Report skipped assessment, not a claim that the source is clean. |
| Lower-resolution or lighter subject detector | Potentially reduce the pre-first-step cost while retaining a subject estimate. | Hair, feet, small faces and mask boundaries may be lost; crop/erase guards depend on those masks. This is a new model/recipe experiment, not a transparent LEAN optimization. |
| Worker/thread tuning | Compare the established three-worker default with the explicit four-worker run on the same bounded input set. | Earlier tests found four no faster. Concurrent ComfyUI/VS Code load affects results; more workers may increase memory pressure. Do not tune against unrelated total-run times. |

**Recommended order:** first remove duplicate verification/navigation work
under layout's exact-behavior gates, then profile a bounded fixed cohort using
exclusive timers. Only then choose a FAST/OVERLAY-ONLY experiment. Keep separate
storage and processing axes: FULL versus LEAN tells us which evidence to keep;
it must not silently decide whether subject coverage is assessed. The approved
denoise/tone comparison skip is the explicit exception, not permission to skip
other stages.

**Bounded acceptance proposal:** reuse saved inputs; stratify at least 30
unchanged ordinary photos, 30 apparently clean photos with selected composition,
30 screenshots/overlays, and all four unusable cases, including first-crop,
reconstruction and difficult hair/body edges within those groups. Ensure
disjoint cohort membership and record actual counts. Compare unchanged-behavior
optimizations with exact hashes/decisions and stale/tampered evidence tests.
For altered processing profiles report missed cleanup, lost useful crops,
subject loss, artifacts and human review findings separately from speed/bytes.
No acceptance threshold for quality regressions has been approved.

#### Review composites and eventual production intake

The user's first-pass-review proposal is covered here, not a new storage or
viewer redesign prerequisite. Generate labeled sheets from the actual
manifest/PNG sequence, retaining source identity, stage names, selection and
links to exact evidence. AI inspection is a first pass; the user's inspection
and ability to change the recommendation remain separate acceptance steps.
Studio-grey padding and closer person framing can be desirable for ComfyUI;
background loss is not equivalent to losing hair, hands, clothing or feet.

- [x] **P2 ai** T13 Promote recurring report-to-sheet diagnostics into
  maintained tooling with a launcher, preview, read-only verification and
  tests. Reuse existing scratch sheets for current acceptance rather than
  blocking the rebase on a new viewer feature.
  Delivered Oct 31 as `preparation-history.cmd`: bounded COMPACT downsized
  stage diagnostics or COLLAGE labelled sheets, full role/provenance mapping,
  exact original/selected/padded payloads, preview/apply/independent check,
  atomic new publication, source recheck and 29 focused tests. Rebase input
  mirrors are supported; conversion never prunes its source report.
- [ ] **P2 either** T14 After the flow is accepted, agree detailed versus
  summary evidence retention with storage S10 and intake I60. Composites may
  replace disposable review previews, not exact originals, selected native
  and padded workflow inputs, source-coordinate masks, hashes, lineage or
  rollback dependencies. Keep full current evidence; no cleanup is authorized.
  Active standard-intake terminology is now owned by intake I73 and may be
  corrected independently of blanket quality acceptance; historical receipts
  and genuine experiment labels remain. This is not Production cutover.
  COMPACT/COLLAGE are now available as independent additive experiments.
  They do not replace any active masks, exact recipe inputs or rollback
  dependencies. Source report deletion and generic FULL-to-history PRUNE
  still require S24/S10's dependency inventory and explicit clearance;
  current conversion reclaims zero bytes.
- [ ] **P2 ai** T15 Add timestamped phase/progress diagnostics to the
  intake/rebase entry points, reusing a shared mechanism rather than a broad
  logging migration. Test formatting, errors and launcher output. Until then,
  timestamp captured output as documented in the long-rebase runbook.

Coverage: composition/padding and measurements -> T12; recurring AI-review
sheets -> T13; composite/configuration/cleanup idea and terminology -> T14,
storage S10 and intake I60. These last two tasks are deferred improvements,
not new prerequisites for the requested sandbox milestone.
Long-task output/resumption documentation -> the canonical
[long-rebase runbook](../art/likeness.md#running-and-observing-a-long-rebase):
launcher/log capture, same shell handle, fresh-shell absolute paths, phase
progress, receipt verification, lock-safe recovery and the remaining viewer
gates. Live v23 worker output and its saved log were verified; no second run
was started to obtain output.

#### Inside inference and the two fill stages: discussion, not policy changes

An isolated, warm-model CPU operator capture on the Cressida screenshot used
four threads, matching each worker's split. Person inference took 3.26 s;
guarded fill 8.81 s; reconstruction 8.87 s. Both fill outputs match the saved
candidate pixels exactly. Torch operator shapes/times show convolution-heavy
inference, including ROI/mask processing for the person, rather than mask
drawing or file copying as the dominant work. This isolated instrumented
capture is not a concurrent throughput result.

The nominal 800px person limit is only the outer resize: 1080x2340 becomes
369x800, then torchvision's own min-size 800 / max-size 1333 transform expands
it to 614x1333 (padded batch 640x1344). Removing or changing either resize is
**not** proved pixel/segmentation-equivalent; it needs separate outcome tests,
not an automatic performance tweak.

Each LaMa `fill` call can invoke the neural model several times: join nearby
mask components, expand each component's context, resize each patch to at most
768px, infer, then paste only masked pixels back. Thus **43 fill calls mean
116 neural patches**, not 43 model evaluations. Model inference consumes
284.04 of the fill helper's 289.86 worker seconds. Tiny marks widely separated
around a screenshot can cost several inferences even with low mask coverage.

The guarded eraser protects faces/body and caps coverage at 20%.
Reconstruction consumes the guarded final and makes a separate synthetic
pattern/pill repair, with a 30% cap and explicit outside-mask preservation.
It currently runs for confirmed overlay proposals **without requiring person
overlap**; a background watermark can also enter this branch. Its name must
not be taken as proof that every invocation repairs the person.

In this sample, 25 images use reconstruction and 18 of those first use guarded
erase. All 18 source-coordinate mask pairs overlap; none are identical.
Median overlap covers **100% of the guarded mask** and **44.5% of the
reconstruction mask** (guarded coverage range 86.5-100%).
Consequently some already-erased pixels are painted again. This is measured
overlap, **not proof that either pass is redundant**: subtracting masks,
merging fills or restricting reconstruction to subject overlap changes its
context/input and may change invented pixels and recommendations.

- [ ] **P2 you** T8 Discuss whether background-only confirmed marks should
  remain in general synthetic reconstruction or use guarded cleanup alone,
  and whether overlapping guarded/head masks should be combined or retained.
  Keep the existing rules until agreed; require exact-mask/selected-pixel and
  visual acceptance evidence for any proposed outcome-changing change.

Reproducibility: immutable manifests/images are under the frozen input mirror
`_reports\preparation\eager-profile-128-20261029` and
`preflight-profile-128-20261029`; the two unprofiled 30-image v22 runs are
`preflight-unprofiled-20261029` and `preflight-repeat-20261029`.
Repository `tmp\perf` holds per-input cProfile files, fill events, exact
source/hash lists, equivalence and nested/operator/resize/overlap measurements.
This section is the durable summary; scratch evidence is not a new library
storage convention. T6 recovery is implemented and tested; the full rebase
was held pending the v23 checks. Those are now recorded above, and the
intake-only iteration has completed and passed its independent read-only
check; full-run review, matching and installation remain open.

Validation: **237 related regression tests pass**, including preparation,
overlay/sequence/eraser comparisons, provenance, frozen preparation and
retained artifacts. The supported preparation launcher's Working-root
dry-run passed; nested frozen-input reports were verified through their
internal publisher/reader rather than weakening the launcher's root guard.
The isolated validator launcher passed **19/19 quick cases**, including the
baseline and mutations. Pylance reports compatible callers and no syntax errors;
markdownlint and whitespace checks pass.

### Oct 29: C: clutter and idle-system snapshot

- [x] **P2 ai** T9 Inventory known C: scratch/cache roots read-only and sample
  live memory, CPU, paging and disk activity. Separate file sizes, process
  private commit, resident working sets and measured image-worker costs.
- [ ] **P2 either** T10 Attribute high VS Code/extension memory through its
  Process Explorer and Running Extensions diagnostics, then compare a fresh
  chat/window under the same workload. Capture resource samples during any
  next controlled image benchmark; an idle snapshot cannot exclude pressure
  during processing. Cleanup execution belongs to storage S22, not this task.
- [x] T11 Transferred Oct 30, not implemented: intake I68/I69 with I41 now
  own this P1 next-round comparison after current sandbox acceptance: a tight
  translucent-GMW ring/letter/glow mask with the existing filled-disc mask.
  This is quality investigation only, not approval to change detection,
  mask growth, blending, or repair selection.

Read-only metadata enumeration completed without access errors for the named
roots, without following junctions. Logical sizes at this checkpoint:

| Location | GiB | Disposition |
| --- | ---: | --- |
| Repository `tmp` | 0.130 | Small; retain current profile/recovery evidence and this handoff. Old contact sheets and superseded logs are candidates only after ownership/reference checks |
| Current Copilot chat directory | 1.062 | Keep for now; `events.jsonl` alone is 1,010 MiB. Do not edit/prune a live chat or recovery/checkpoint history |
| User Windows Temp | 3.919 | 3.717 GiB is Visual Studio installer package staging, not photo-pipeline scratch; confirm setup/update is inactive before supported cleanup |
| pre-commit cache | 0.568 | Rebuildable environments, but retain the interrupted-hook patch until verified publication/recovery is no longer needed |
| VS Code cache / cached code / logs | 0.052 / 0.168 / 0.026 | Small relative to memory; deleting them is not a demonstrated memory fix |
| VS Code global storage | 0.074 | Extension state, not blanket disposable cache |

C: had **432.1 GiB free** (about 46% of its 930.5 GiB capacity).
Repository `tmp` contained 974 files and no Markdown files before the requested
handoff was written. It is not a large storage pressure source at present.
The Temp names `5ggitv0m` and `rzqjwhix.at5` contain Visual Studio package/setup
payloads; this is ownership evidence, not proof they are abandoned.
No whole-C: or all-AppData audit is claimed.

A five-second process sample plus Windows counters showed about 14% machine
CPU, 9.9 GiB available RAM, 43% commit usage, zero sampled page reads/input,
and zero queued disk requests. C: was doing about 0.28 MiB/s; B: was idle.
Those are idle/checkpoint observations, not the earlier benchmark's averages.
There is **no evidence in this snapshot of paging or disk saturation**.

Sixteen `Code` processes summed to about **9.0 GiB private commit**; summed
working sets were 6.6 GiB but include shared pages and are not unique physical
usage. The Copilot runtime separately held 3.3 GiB private commit / 1.16 GiB
working set. The largest Code roles included Node utility processes and a
renderer. Process role alone does not identify a particular extension or prove
a leak. The very large chat log makes a fresh-chat comparison reasonable,
but on-disk log size does not establish how much is loaded in memory.

Evidence: `tmp\perf\c-scratch-audit-20261029.json` and
`system-snapshot-20261029.json`. No files/caches, processes, galleries or
session histories were deleted or stopped. The safe next step is targeted
attribution and comparison, not speculative OS tuning or mass cache removal.

## 2. The chin in the likeness face crop

The face that goes into likeness is OpenCV's `FaceRecognizerSF.alignCrop`: a
fixed 112x112 crop aligned on five landmarks (eyes, nose tip, mouth
corners) to the ArcFace template SFace was trained on. In that template the
eyes sit at y=52 and the mouth at y=92, so only 20 px remain below the mouth.
With an ordinary face (chin about 0.8 of the eye-to-mouth distance below the
mouth) the chin ends near y=125, so roughly the bottom of the chin is outside
the crop. That is by design, not a bug.

**Decision: keep it.** The recognizer only gives comparable vectors for the
framing it was trained on; a taller crop would shift every face off that
distribution and lower the scores of true matches more than a chin outline
could add. Jaw and chin shape still enter through the landmark geometry, and
the forehead/hair band is likewise part of the fixed template.

- [ ] **P3 either** T3 For human review only, show a wider context crop (with
  the chin) beside the exact 112x112 likeness input in the gallery face
  evidence, clearly labelled, so the scored crop stays the one that was
  measured. Owner when picked up: the gallery layout plan.

## 3. Where generated images live

Measured Oct 28 in the sandbox: about 85 GB of run state under
`Working\_sandbox-state` (full intake runs are 24-29 GB each: Oct 27
full intake, r17, r20, the stopped r21) and ~8 GB of older pilot/proof reports
under `Working\_reports\preparation`; ComfyUI results go to `Working\_generation`
and are planned to return to `gallery_generated`.

This already has owners, so no new structure is invented here:

- Intake runs and reports: **L20** in
  [gallery review layout](2026-10-22-gallery-review-layout.md) (safe run
  inventory and pruning with dependency checks). The preparation history links
  into these runs, so nothing can be deleted until L20 defines the keep rules.
- ComfyUI outputs: **R9** in [reference rendering](2026-10-25-reference-rendering.md)
  (storage, backup and retention limits, safe run filing).

- [x] **P2 you** T4 Sandbox retention is now owned by storage S10: keep the
  latest accepted run and every unaccepted/incomplete run; older accepted
  runs need explicit review, undo/audit clearance and dependency checks before
  a separate delete apply. The user separately waived obsolete sandbox
  recovery and authorized the S14 whole-Working reset. That reset removed the
  old r17, Oct 27 and stopped r21 outputs while preserving all unique active
  photos. This is not authorization for Production pruning. See the
  [storage plan](2026-10-28-storage-operations-and-retention.md).

## Your words

Oct 28, 18:12 (chat): "I don't know if the task is still running or if I stopped it.  But when you get a chance, check out the random thoughts I have around multi-threading and other optimizations for what we're doing.  If you agree, just go ahead and come up with a plan, write it up in docs/plans - retire this one feedback item and just implement it all and test whether or not it provides improvements in the intake."

Oct 28 (chat): "Comfy is running now, but I can stop it. as well"

`feedback/random_thoughts.md`, word for word:

```markdown
# Random Thoughts for 10-28-2026

Just a few random thoughts and observations from the current state of the project.

## Performance Optimization

To increase speed in the process - can we multi-thread and run 2 threads, check utilization of this machine and see if it improves performance of the intake image processing.  Likeness would still be single threaded.  If that's easy to test and verify - might be worth some time

Basically looking for ideas on how to improve performance with balancing restrictions on capacity of current hardware.

## Chin Inclusion in Face Crop

It seems like the face crop for the likeness cuts off the chin a bit.  Just wondering if that's actually a good thing or if having a chin would help the likeness process compare?  It seems like it pull the full forhead and some hair, but stops short of including the entire chin.

## Generated Images

It seems like we're leaving a lot of generated images from all the runs in testing and we'll need to addess the location where they should be placed as it seems somewhat random in the various runs and long term we'll need to establish how that should be organized and managed.
```

Coverage: performance -> section 1 (T1 done, T2); chin -> section 2 (decision, T3);
generated images -> section 3 (routed to L20/R9, T4).

### Oct 29 chat follow-ups, word for word

<!-- markdownlint-disable MD013 MD028 -->

> I want to interrupt as the one thing that might not have been captured in the handoff is we were still testing some performance and profiling of the steps to understand where to make improvements before the full rebase and intake

> the process was actually just accessing the .png files directly - you can find the .py scripts in tmp as well

> I also just noticed we're padding so many variants of images and I don't think we want that - we just want the padded versions of the chosen/recommended photo - so the padding pieces should be looked at in what is fed into the padding of images in the report.  The tone, denoise are also fine I guess - since I do have to test with those variants - but the masks and interim images are not necessary as we only need images in the 944x1104 that are worthy of sending to a workflow for testing the actual output.

> You can create re-usable diagnostic scripts and keep them if it makes sense so we don't have to rebuild them if we blow away tmp scripts - but the ideal world is that we can run the intake process and use scripts to build the visual sheets for you inspection in the future.  So we can automate things that we think could be recurring or usable and keep in tools as well.  I'm not saying totally switch how you were doing it - we just need the most optimal way for you to be able to do the first pass review of the processing and ensure that the final images are the right ones.  The intake is supposed to ahve rules to handle that and I'll do the final inspection and review, but you can do it much faster and with better precision - so hence the partnership in you doing the reviews where it's necessary.

> Don't lose track of work.  But In composition if we strip away background and it pads the image for the gallery later - the padded portion is actually better for ComfyUI as we normally are not using any background from images and convert to the studio grey instead.  So, that's not as big a concern for me.  Having a closer up picture of a person can yield much better results in ComfyUI

> You stuck?

> As you're doing this - one idea I did have is that if the intake process generated a composite image with all the sequence of images in it along with text - we could use that as a reference instead of keeping all images separately and remove those.  Or maybe multiple composites to be displayed in the intake review pages.  Just thinking if that would be better or worse.  Also - if things are still reflected as pilot or evaluation - I think we'll need to address that once we approve the process is working - which for the most part it is not.  It was a pilot or evaluation at one point, but now it's going to be the initial production intake with processing to clean-up images and not just let them flow down into comfy without clean-up, recommendation on best (with me to adjust that later), padded and ready for me to experiement with in comfy workflow.  Ideally, in the long run we don't need so many intake images handing around for ones that were processed - but we do need them until we lock in on the flow - so maybe that's also part of this equation on being able to have a summary set of images vs. all the detailed ones as options in the configuration for the intake processing and clean-up when done.

> This was working in the past for previous agents to run the long running tasks and get the right output, so I am hoping you can figure it out and if it's complicated, we need to document it somewhere in the docs that need to explain how to rebase and run all these steps.

<!-- markdownlint-enable MD013 MD028 -->

Oct 29 (chat, overlay-first request), word for word:

> Could we first check if we see any potential junk on the screen before detecting a person for protecting it?  A slight improvement for when most images are clean - but some "may" have potential issues?  If we detect overlays first and don't find any then it's good image.  If we do, then we look for the person to protect it and if necessary have to re-check overlays or would we be able to use the information from the first check?

Oct 29 (chat, larger profile request), word for word:

<!-- markdownlint-disable-next-line MD013 -->
> As you do this, let's also analyze the performance and profile it a second time on a larger set and get more metrics of each step, what's happening and look for areas to optimize as well.  There might be a few additional pieces of logic to flex when we layout all the numbers again and if a single step is still a bottleneck, what within that step is taking time as there are likely many sub-steps and wondering the same about how to optimize.  The two separate erase and reconstruct serve a purpose and we can discuss that as well.  Maybe some logic is misplaced and how it was supposed to work from what it's doing.  The reconstruct should only happen if there is an overlay on the person we need to care about the type of reconstruction for.  But that's for us to discuss.  Knowing the details of this will help me decide how best to bring in new images and which ones will take time.  I understand doing the huge rebase will run log (but isn't a daily activitiy) but I still want to ensure we have optimized this code without changing the outcome.

Coverage: overlay-first -> T7 and v22 evidence above; larger profile,
substeps and optimization candidates -> paired 128-image/operator analysis;
two-stage reconstruction/person-overlap policy -> T8 (discussion only,
no rule change). Full-run checkpoint recovery remains T6.

Oct 29 (chat, mask-quality question), word for word:

> I'm also wondering about techniques for erasing when we do have an overlay like the GMW logo that is a see-through logo - if we have a different mask that is just the logo instead of a full circle, would the erasing/blending work better at leaving the underlying image in place - instead of a larger smudge because we're going after an entire circle?  This is just a question for consideration - not an approval to change things - optimizations first - then quality control on the final output.

Oct 29 (chat, system/clutter question), word for word:

> Finally, what files in our own tmp directory are worth still keeping around vs. what can be removed to also reduce clutter on C: drive ... we've left a lot of pieces in various temporary locations - maybe even my user/scotte/AppData/local ... would be good to know if there are large amounts of cluttering files on C: as that also impacts overall system performance.  I'm also seeing that VS Code it taking a ton of memory compared to what it used to be - so I'm unclear on that as well.  Just want to see if we can't determine the true performance bottlenecks on top of where the hot spots truly are at in our own code.  Whether it's system, disk, OS, memory, CPU or just expensive image processing calls.

Coverage: translucent-logo consideration -> T11 (not approved implementation);
C: inventory and resource snapshot -> T9 done; extension attribution and
under-load comparison -> T10; safe cleanup review -> storage S22.

Oct 29 (chat, performance decision clarification), word for word:

> I don't think we actually dug in and made sure that the changes and optimizations was complete - a comparison was done, but I guess I didn't think it was final, final on the decisions.

### Oct 29 autonomous continuation (chat, word for word)

<!-- markdownlint-disable MD013 MD028 -->

> Read the handoff’s FINAL VERIFIED BASELINE and the linked plans. Use the “chasing my tail” feedback to separate rebase prerequisites from work that can wait—without broadly reorganizing everything. Then implement T6 per-image recovery, complete the sandbox rebase, and verify Gallery/Overview/Review. Don’t start a full intake until recovery is tested.

> We'll need to commit and push when you get a change as well - at least when we know things are working.

> I'd like you to complete the entire likeness and matching and assignment process while I am gone.  You can preview the results and if it looks a major issue, dig into those ahead of running the complete process to apply the changes so that I can review the output when I return.  You have full authority to track down issues, find them in the code, make decisions and fix them.  You can inspect suspect images directly and do your own analysis or look writing tools to automate checking of various moves, assignment and major changes we have implemented that you will find as you run the process and see what moves to where.  This will be a great opportunity for you to get up to speed on how it works end-to-end and read through plans that may or may not know about issues, update them with new issues and decisions or even just complete plans where we find the issues that are still hanging.  You can inspect the full .html output pages as well looking for anything wrong with them.  It's a full blow authority to take this as far as you can and address any issues you find.  I'll be back in a few hours so you have time to let it run, inspect, fix, run again and just keep letting me know what you are doing every now and then.

> If you finish completely, just read through the plans, update them all, archive things, work on the recaps and archiving, also read through and open feedback/ .md files for additional thoughts work and things to take care of.  You have the docs that instruct how the feedback files work, how to handle the docs/plans and everything is should be clear

> If the logs have timestamps on all our logging entries it would be better - even using some logging framework would help understand timing and if things are active and when.  Just another housekeeping item.

> What is the logic behind recommending denoise or tone?  It seems to me in many cases the denoise looks better, so want to know if we ever implemented the final decision logic or if it always defaults to control if there aren't any erases ... I feel like the denoise has a crisper visual - but not sure it's better in terms of the pixles for comfy - but wondering what you think should be the logic and answer to how we decide?

<!-- markdownlint-enable MD013 MD028 -->

Coverage: tested checkpoint publication -> normal commit/push; autonomous
sandbox preview/audit/install and actual viewers -> cast C8/C9, intake
I59/I60 and storage S15. Existing Source/Production boundaries remain.
Post-milestone plan/feedback/recap reconciliation -> intake I61 and the
plan-index hygiene rules, not permission to remove unpreserved feedback.
Timestamp logging -> T15; the current matching capture prefixes each received
line with an ISO timestamp. Denoise/tone selection -> intake I10/I11: no
calibrated enhancement chooser exists. They are independent comparison-only
alternatives from the selected cleanup, not automatic recommendations.
Perceived crispness alone does not establish texture preservation or better
ComfyUI output; keep the conservative default pending representative evidence.

### Nov 4, 21:44 optimization feedback

Coverage: detection and profiles -> T18's Nov 4 analysis; timer attribution ->
T17; copying, backups and large install hotspots -> the linked layout analysis.
No broad plan reorganization.

<!-- markdownlint-disable MD013 -->
````text
So as we look at all the timings - there must be opportunities for looking at where we could optimize and improve further with LEAN processing vs. FULL processing policies/setup we have.  That needs some analysis and some proposals to consider and the cons to doing so.  I know some of the image was optimized, but still we were focused more on quality of the incoming image and thus had to find the person in the image - but we had considered other optimizations that would skip some of that extra work if we know that most images are not actually getting cropped or requiring erasing.  Since we're skipping denoise and tone - that should have cut things down ... but maybe thinking about other options would help as well.  The other question is are we copying files all around during the phases that we could do in a different way having a better structure and referencing files from previous stages and/or how is everything working behind the scenes.  Also, any uncessary backups, copies and such are probably something for us to look at with 3000+ files and different generated images during the process.  Wherever there are big hotspots in consuming time in the process.   LEAN was supposed to get us in better shape and it has - but it's still not truly LEAN in some cases.
````
<!-- markdownlint-enable MD013 -->

### Nov 5 14:41 pre-new-PC scope (verbatim)

Coverage: core-conditional bundle and measured stopping rule -> T29 and the
14:41 decision above; T20-T28/L18 keep implementation ownership.
The response tokens below identify the choices made in structured Q&A.

<!-- markdownlint-disable MD013 -->
````text
We might as well continue with planning activities while we work and sort out just how many of these performance improvements we should make ahead of the new PC setup - since this is the best benchmark for if it benefits this machine specifically or not.

core-conditional

measured-threshold
````
<!-- markdownlint-enable MD013 -->

### Nov 5 approval (chat, verbatim)

Coverage: approved effort/risk/benefit order and downstream parallelism ->
T20-T28 and gallery L18; feedback reconciliation -> priority PR1a and the
plan index's Nov 5 source ledger. No runtime change during installation.

<!-- markdownlint-disable MD013 -->
````text
Which of these are actually easy to implement to improve speed and performance - especially when we get to the new machine which has much more hardware capacity.  Seems like I mentioned doing this several times and we've neglected to achieve parallelism in all long running processes.  I want to know the risk associated with each one and also urgency and benefits for them due to the amount of time spent during each step.

I agree with all of these.  So, while you're waiting we need to update the docs/plans and also address all items in feedback and archive them if we have them in plans or stop and ask me questions about things not already in a plan.  We can do that while we're waiting on this parallel activity - so back to planning we go.
````
<!-- markdownlint-enable MD013 -->

### Nov 5 15:26 derivative priority confirmation (verbatim)

Coverage: derivative speed, manifest/source-read attribution and bounded
optimization remain T21 with baseline T29; no change to the running job.

````text
This derivative process is super slow - so yes, it's definitely a target
````

### Nov 5 15:59 pipeline-wide core clarification (verbatim)

Coverage: repeated-work assessment/fixes across phases -> T30 with T29,
existing phase owners and the coordinator/worker execution contract above.
Additional worker acceleration retains the measured extras gate.

<!-- markdownlint-disable MD013 -->
````text
It's really anyplace in the process that we're thrashing like this that should already be in that core of items to address.  These seem like easy things.  Even if it's a central thread doing the decisions and throwing items into queue for processing - it all depends on where the bottlenecks are and how threading is best achieved.  So I hope you are thinking about that while we're waiting to plan out that next phase of work in enough details we can execute and while we're waiting on this.
````
<!-- markdownlint-enable MD013 -->

### Nov 5 16:01 use established findings (verbatim)

Coverage: established-finding ledger and execution rule above; T20-T22/L18
retain fixes, T29/T30 avoid duplicate discovery while preserving comparison
and correctness evidence.

<!-- markdownlint-disable MD013 -->
````text
I would think the deep code analysis you did should have uncovered the various hot-spots along with the timings work.  Is that true?  I don't want to call out things you've already analyze, but do want to use this time while waiting to formalize places we KNOW need fixing and not just time them again to know it's a problem.
````
<!-- markdownlint-enable MD013 -->

### Nov 5 16:05 optimization philosophy and stage boundaries (verbatim)

Coverage: small-gain fixes and continuous versus stop/review/resume execution
-> T30 core contract above and the existing phase owners. No independent
acceptance or user-approval gate is waived.

<!-- markdownlint-disable MD013 -->
````text
I am always of the mind of optimizing even for small gains as you never know when you add more functionality to something that wasn't a problem and then it's now a problem.  So easy to fix things, even with a small margin to gain is always a key thing.  I understand we might be able to run processes in chunks and that leads to the re-reading and re-writing some same things or creating independent cache to ensure proper boundaries - but IF there are major performance issues, then that's still not a good approach when running things back-to-back without stops.  Hope that helps clarify how I think about the entire process.  It's both the ability to run pieces, do a review before applying and moving on to the next step - but a non-stop run doesn't need all those "extra" pieces when dealing with a huge image library.  So, not sure how that impacts the work we're doing - but it's an important thing to keep in mind.
````
<!-- markdownlint-enable MD013 -->

### Nov 5 16:07 verified continuous handoffs (verbatim)

Coverage: T30's handoff/check classification above, existing T20-T22/L18
implementation and continuous versus standalone regression contracts.

<!-- markdownlint-disable MD013 -->
````text
A correctness check is only really needed when the next step is unsure about the previous results - but if we know it's correct in the non-stop flow, then you can skip excessive re-checks, use common cache and not rebuild.  We built this all incrementally and in phases and hence the fragmented approach - which works in that model, but running it non-stop on the full rebase has show those end-to-end design flaws that came naturally in how it is built.
````
<!-- markdownlint-enable MD013 -->
