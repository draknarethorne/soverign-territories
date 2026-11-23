# Likeness library

`bin\likeness.cmd` analyzes faces in the local original-photo library. It helps
answer three different questions:

1. **Does a photo look like the person whose folder it is in?**
2. **Which other people or folders look similar?**
3. **Where should a new or held photo go?**

The tools can preview and, with explicit `--apply`, perform selected file
operations. Similarity is evidence for review, not proof of identity. The
people gallery and review gallery are local HTML reports; neither moves files.

Review keeps held photos with stale or conflicting retained-preparation
claims visible with diagnostic placeholder thumbnails and their original
file links. It does not treat them as FAST inputs, use another photo's
prepared pixels, or describe the refusal as an intentional framing exclusion.
The preparation/crop guard still refuses processing those claims; a viewer
diagnostic is not approval to repair or reassign the photo.

## Normal selected-photo intake

`bin\library.cmd` provides the selected normal FULL/LEAN/FAST pipeline,
including frozen audit/family metadata, recoverable publication and
Gallery/Overview/Review viewers. The bounded three-profile mini-library proof
is complete; full-current-library compatibility, fresh-baseline and human
identity/crop acceptance remain gated. It is not the whole-library rebase and
does not invoke likeness experiments. Without
`--photo-id` it previews pending originals in `Various\gallery`;
repeat `--photo-id` to select a smaller batch. Plain filenames receive IDs
from the original bytes through the existing content-name convention; valid
embedded IDs remain unchanged. Full original hashes guard short-ID collisions.
Preview reports normalization without renaming primary inputs; apply journals
it with publication, including held arrivals. Invalid or ambiguous prepared
lineage is explicit, not silently omitted. The launcher previews by default; only add
`--apply` after reviewing the assignments and holds:

```cmd
bin\library-preview.cmd --profile lean --photo-id photo:ONE --photo-id photo:TWO
bin\library.cmd --profile lean --photo-id photo:ONE --photo-id photo:TWO --apply --run-id arrivals-001
bin\library-check.cmd --run-id arrivals-001
bin\library.cmd --undo --run-id arrivals-001
bin\library.cmd --undo --run-id arrivals-001 --apply
```

Independent selected framing is supported without reassignment:

```cmd
bin\originals.cmd --root "ABSOLUTE-LIBRARY-ROOT" --photo-id photo:ONE --no-repoint --dry-run
bin\originals.cmd --root "ABSOLUTE-LIBRARY-ROOT" --photo-id photo:ONE --no-repoint --apply
bin\originals.cmd --root "ABSOLUTE-LIBRARY-ROOT" --photo-id photo:ONE --no-repoint --check
```

This explicit framing scope does not rename native inputs, migrate layouts,
prune other images' products, perform native cleanup, reassign identities, or
retarget workflow inputs. It can generate explicitly requested products for
FAST inputs without relabeling those native pixels as clean. Missing/duplicate
selected IDs and rendering failures are surfaced; preview uses local
read-only face inference without model downloads or cache persistence.

FULL, LEAN and FAST use the same matcher, policy thresholds, complete
eligible identity inventory and cast-priority receiving rules. Every mode limits candidates to the
selected/pending `Various\gallery` arrivals and reuses unchanged cached identity
evidence; missing or stale identity evidence stops the plan rather than
truncating rivals or starting a library-wide inference run. FULL stores the
complete identity-core score evidence with its plan. LEAN stores the compact
plan. On apply, both prepare only the selected inputs with the accepted native
recipe, match the actual recommended native bytes, retain original/evidence
products, and generate supported 944 framings. Unsafe/unavailable head framing
is explicitly recorded, not invented or counted as clean. Preparation runs
serially with offline pinned-model loading: no model download is allowed.
Native preparation and framing remain independently available through
`prepare-images.cmd` and `originals.cmd`. FAST uses original-byte matching and explicitly defers image
editing and 944 products; it does not certify that source pixels are clean.
The profile never relaxes a threshold, changes reference eligibility, or
changes identity/name/lineage records.

An unambiguous genuine incoming original whose ID is already in an identity
gallery is recognized automatically as an owner-preserving replacement.
Content-derived `pic_<8 hex>` IDs remain bound to the full original SHA-256:
different original bytes are refused as a short-ID collision, even for a
pixel-identical re-encoding. A platform/source ID such as `image_<id>` is
the mutable-version case; collision checks are not bypassed by explicit update.
Original-only unique-newest selection never lets an older-source prepared
native win merely because its processed mtime is newer. A prepared claimant
requires verified lineage and recoverable retirement with its retained set.
Tied original versions, invalid lineage, true locks, workflow selections and
unsafe content-bound decisions hold automatic updates explicitly.
`--update-photo-id ID` retains its existing deliberate-update checks.
Replacement retains the current owner/name/ID/lineage, refuses true photo locks, validates
the old content binding, and backs up both old native and incoming original
plus metadata before replacing anything. It never silently promotes
membership/reference flags. Prepared replacements retain exact previous native
generations and immutable preparation manifests/artifacts. A content-bound
`.normal-history.json` index retires old active claims; separate historical
HTML resolves older LEAN native aliases to the exact previous generation.
Old manifests, recipe details and receipts are not rewritten. Invalid history
stops replacement rather than reviving a reference. A stale, incomplete, or experimental
membership record is reported and preserved, not silently restored or promoted.
Review those diagnostics against the read-only library before any separate,
explicit metadata decision. No routine profile rewrites unrelated images.

Applied file moves create a verified **scoped** backup of only the selected
originals, any retained-preparation files transferred with them, and the
catalogue; they do not snapshot the whole library or shared ComfyUI inputs.
The move journal, catalogue seal, and exact undo machinery remain bound to that
batch. `--check --run-id` verifies the applied receipt without rescoring. If an
apply fails, retain its receipt and journal and use their status and hashes to
choose recovery; do not start a second run with the same run ID.
Repeat apply rejects a different explicit selection/profile or changed
policy, configuration, or bound shared implementation. Persistent inference
requires authorization before any evidence write. Current cached unusable or
zero-face measurements remain unavailable evidence, not missing-inference
requests. Old hash-bound receipts are preserved, never rewritten to bless a
changed implementation.
Native publication journals support `--recover --run-id ID` (preview) and
`--recover --run-id ID --apply` for interrupted publication even when no final
receipt exists. Recovery verifies snapshot hashes and refuses unexpected
newer content. Injected publication-copy failure is fixture-tested to restore
old native, incoming original and exact catalogue bytes.
Publication staging writes an explicit local `.likeness-library.json`;
the existing-catalogue reader's global fallback is never a staging destination.
Publication snapshots an existing local catalogue as an overwritten staged
target, or installs a new local catalogue when absent. The global fallback
is read-only input, never a root-relative transaction source. Exact undo
restores the prior local catalogue bytes or its prior absence.
Short content-derived batch folder names keep SHA-named preparation files
within Windows path limits; human run IDs stay in receipts. Legacy normal
journals remain recoverable by their original paths and exact run IDs.

Normal publication validates bound normal admissions against their receiving
gates rather than undoing them with legacy initial-core reclassification.
Legacy/unmodified owner-audit rows retain the frozen low-member check;
explicit updates retain their owner. Complete eligible rivals remain
available for evidence, while Review and tentative members cannot recruit.
Final family actions cannot rename existing
owners or alter unrelated people. Gallery, Overview, Review and native-history
HTML are published inside the recovery transaction; a viewer failure rolls
back sources, metadata and prior viewer files together. Unmeasured arrivals
outside an explicit selection remain unmeasured in Review, without inference
or fake cached measurements. FAST labels native editing/944 outputs deferred.

Dry-run matches current raw input evidence. FULL/LEAN preparation and
native-content rescoring happen on apply, so a raw preview cannot promise the
same routing after preparation. Inspect the actual receipt and recipe report.
Draft policy requires sandbox authorization for publication. Receiving
permissions and thresholds come from policy, not from that override.

### SIMPLE foundational recovery

`bin\normal-rebase.cmd` applies the normal matcher to a whole explicitly
selected sandbox Working root. Unlike ordinary intake, it reconsiders
eligible existing Models/Prospects/Potentials Gallery/core members for
upward entry. Existing recovery is assessed before Various, with a single
independently qualified reference boundary and a second matching round.
Publication happens once. Unresolved existing Gallery owners are retained;
Review cannot form or recruit another fragment.

The draft [policy](../../data/art/likeness-engine-policy.json) owns the
receiving floors and approved close pairs. Cast admission compares against
other Angels/Sisters; lower scores remain audit evidence, not vetoes.
Gallery support counts independent retained references separately from
candidate-to-core similarity; it is not a per-reference Gallery-score floor.
Otherwise qualifying approved close-pair conflicts can enter optimistic
Gallery with a **High rival / unconfirmed** warning and rival scores.
These members remain non-core/unprotected, excluded from anchors, reference
growth and automatic protection until separate confirmation. Pair core
similarity is diagnostic only. Weak matches and unapproved ambiguity stay
in provisional Review with alternatives, not another recruiting identity.

Receiving is open by default. `--lock-cast-admission` locks incoming
Angels/Sisters Gallery/Review only, keeps cast rivals visible and must match
preview/apply/check. Outgoing cast Gallery and genuine source locks remain
closed. Verified retained natives reuse their checked preparation/immutable
history; a membership-only update cannot retire unchanged native lineage.
Receipts bind code, policy, source bytes, reference snapshots and this lock.
For new FULL/LEAN preparation, `--preparation-workers 1`, `2` or `3` selects
the number of workers for that preview; the default remains `1`. Repeat
the same value on apply so the request matches the preview. The origin seal
records the worker count. For two or three workers, preparation refuses
to start if available memory is unknown or below 3.5 GiB per worker; this
is a preflight estimate, not a hard runtime memory limit. This option is not
a cache size, does not alter
matching, and a non-default value is not accepted with `--reuse-preparation`,
FAST or check/recovery. Choose it separately on each machine only after its bounded
measurements, resource and parity checks. Small sidecar trials do not certify
a whole rebase.
The [implementation/acceptance ledger](../plans/2026-11-16-simple-review-and-tuning.md#implemented-foundation-fixture-proof-not-a-library-run)
distinguishes fixture/browser proof from installed and human acceptance.

### Code ownership and evidence

Native-transaction stage: `normal_products.py` composes the accepted preparation
and retained-evidence helpers; `normal_transaction.py` seals and publishes only
the selected files and supports exact recovery. Real six-copy mini-library
receipts `native-full-006`, `native-lean-007`, `native-fast-007` and
`same-photo-009` passed apply/check/repeat/recovery. FULL and LEAN published
the same changed native hash for one input; FAST retained raw hashes and
deferred products. The same-photo proof preserved Angelica's owner/name and
restored both old native and incoming original. These receipts are
revision-bound, not proof of final audit/family/viewer completion or prepared
history replacement. Preparation comparison HTML exists in their frozen
input report bundles. A later ten-copy isolated integration produced actual
Gallery/Overview/Review with exact undo; it remains historical integration
evidence, not final acceptance. Earlier native-stage checks did not assert
installed local-catalogue presence and cannot prove transaction isolation.

Final bounded machine acceptance uses ten copied inputs at
`Working\_sandbox-state\normal-flow-proof-20261115-r02`. Frozen runs
`final-full-025`, `final-lean-025` and `final-fast-025` passed
preview/apply/check/repeat/undo; all ten source hashes and catalogue bytes
restored exactly. A qualified known-name match reached Angelica Vale's Review
under the unchanged draft routing policy; the unrelated owner stayed unchanged.
`prepared-failure-027` restored a real replaced prepared native after an injected
post-native copy failure. `prepared-update-028` passed apply/check/repeat/undo,
preserving six previous manifest/artifact bindings. The final
`prepared-update-view-029` remains applied for viewer inspection; prior receipts
remain generation-bound, not rewritten. Native Gallery/Overview loaded seven
images, Review loaded thirteen displayed/supporting images, and historical
LEAN aliases loaded the exact previous native. These are workflow/browser
checks, not human identity or crop-quality approval.

`normal_finish.py` owns the scoped frozen check, complete rivals, final family
metadata and viewer composition. `normal_history.py` owns immutable generations
and content-bound retirement, including historical LEAN alias views.
`normal_transaction.py` owns native/metadata/viewer rollback together.

SIMPLE rebase previews now include `plan.fragmentQualification`: conservative
direct lower-to-higher identity hypotheses from frozen references, with
independent witness IDs and explicit holds. Its activation is
`diagnostic-only`. The proposal requires the stricter existing identity-merge
threshold and individual source-core member support; it does not suppress
rivals, authorize whole-group moves or grow reference cores. Its holds are
not photo-admission vetoes: the selected per-member Gallery gates do not
require this stronger whole-fragment diagnostic to pass. Selected
upward-recovery/default/run-lock/reference-boundary behavior is implemented
and fixture-tested as recorded in the
[current foundational contract](../plans/2026-11-16-simple-review-and-tuning.md#next-simple-run-foundational-corrective-contract).
Old receipts retain their original code/policy bindings.

| Area | Owned path | Evidence label and boundary |
| --- | --- | --- |
| Normal pipeline and shared matching | `tools\art\likeness_library\normal_import.py`, `normal_products.py`, `normal_finish.py`, `normal_history.py`, `normal_transaction.py`; shared reconciliation/engine/maintenance | Fixture-tested selection, complete rivals, shared policy, cache/authorization guards, immutable history and rollback. Final 172-test selected suite passed. Operationally verified final three-profile and prepared-owner cycles above; browser-loaded sources/thumbs/history links. No full-library or human identity acceptance. |
| Independent selected framing | `tools\art\originals.py` via `originals.cmd --photo-id ... --no-repoint` | Fixture-tested selection, ambiguous/missing-source guards, no unrelated pruning/rename and surfaced render failures. One real copied arrival produced full/head 944x1104 products; preview/apply/check/repeat passed while source/catalogue bytes remained unchanged. This is explicit framing, not normal-profile preparation or identity acceptance. |
| Existing cache, core, policy, and recovery helpers | `tools\art\likeness_library\` stable modules | Historically tested by their existing focused test suite; tests must still be run for the current change before claiming this revision is accepted. |
| Rebase orchestration | `tools\art\rebase_flow.py`, `tools\art\likeness_library\clean_rebase.py` | A deliberate whole-library reassessment path, not normal intake. Rebase checks and receipts do not certify a normal-flow batch. |
| Optional trial algorithms, compositions, reports, and adapters | `tools\art\likeness_experiments\` | Experimental, even when a fixture or saved-receipt test passes. Explicit compatibility launchers/wrappers route here; normal intake must not import these modules. |
| Active standalone diagnostics/utilities | `tools\art\likeness_utils\diagnostics.py`, `family_preview.py` | The explicit `likeness diagnostics` and `family-preview` report commands use these modules; both are outside normal intake and import stable core helpers only. `audit.py` stays core because planner/reconciliation and Gallery readers share it; `review_gallery.py` stays core because active Gallery/maintenance consumers share it. Directory role does not certify diagnostics or family suggestions as identity truth. |
| Shared transaction and retained-receipt services | `tools\art\likeness_library\actions.py`, `storage_retention.py` | `actions.py` supplies the guarded apply/undo engine used by quality-disposition receipts and recovery. `storage_retention.py` registers run receipts from preparation and rebase flows. Both also retain explicit compatibility CLIs; shared transaction, recovery, and receipt services stay in core. |
| Legacy reconciliation experiment | `tools\art\likeness_experiments\reconcile_command.py` | `likeness-experiments legacy-reconcile` is the explicit entrypoint. `likeness reconcile` remains a lazy compatibility alias; the controller composes merge/category transitions, protection, and family augmentation and is not imported by normal intake. |
| Current-Sandbox compatibility | Frozen-code read-only preview; one explicit arrival | Latest default-cache preview stopped safely: 3,268 unchanged identity photos lacked current cached vectors (Angels 465, Potentials 933, Prospects 1,012, Sisters 858). Existing membership/protection/rejection provenance remains preserved. Earlier 1,525-photo diagnostics are historical, not the current count. Current Working needs content-bound accepted measurements or the separately approved fresh-baseline preflight; no migration, current catalogue/Gallery mutation or full inference campaign occurred. |

Promotion from `likeness_experiments` is an explicit module/import/test change
after review of the relevant evidence. Folder placement alone does not mean
that a module or workflow has been tested or accepted. Avoid scanning
`_archive` directories for active code.

**Review navigation:** Overview intentionally shows up to nine photos per
person (plus a pinned workflow selection where applicable); use Photo review
for the full Gallery and Review cohorts. The who-went-where report is under
`_reports/library/rebase-recap/index.html`, not the Intake runs preparation
viewer. A successful maintenance check does not rebuild stale HTML. After
a report/retained-reader fix, preview `bin\people-gallery.cmd --reports-only
--dry-run` with explicit sandbox root/cache/output/policy, then use `--apply`
and `--check`. This refreshes reports without matching, photo moves, new
intake, derivative maintenance or backups; reload the browser afterward.
The shared refresh is cache-only: missing face measurements remain
unavailable instead of constructing a model or persisting new measurements.
Generation, unchanged generation repeat and independent `--check` are
separate baseline measurements; this is not a complete intake/rebase timing.

Overview repeats each person's linked name above and below the photo grid.
Individual thumbnails have no visible filename or appearance captions;
filenames and recorded appearance details remain in image tooltips and
accessible text. Other report pages retain their detailed captions.

## Directed reformation shadow

The entrance-trial harness has an opt-in `--directed` comparison mode for
saved, own-membership-assessed reports. It pairs the existing
`ordered-middle` entrance/core/retention control with four explicit directed
recipes. Preview first, then publish only to a new ignored report directory:

```cmd
bin\likeness-entrance-trial.cmd --source "ABS-ASSESSED-REPORT" --out "ABS-NEW-REPORT" --directed --dry-run
bin\likeness-entrance-trial.cmd --source "ABS-ASSESSED-REPORT" --out "ABS-NEW-REPORT" --directed --apply
bin\likeness-entrance-trial.cmd --source "ABS-ASSESSED-REPORT" --out "ABS-NEW-REPORT" --directed --check
```

The report compares category-specific admission, frozen source-core
continuity, own-membership retention, independent reference eligibility, and
strong wrong-identity release as separate evidence axes. The `.60` core
diagnostic and `.30/.60/.30` release example are comparison values, not
selected or installed defaults. Candidate upward ownership is considered
only after an individual has independently qualified as the same-identity
appearance. Distinct cast slots remain rivals; full relevant rival evidence,
including close and overlapping-reference rivals and exact negative or
uncertain conflicts, remains in the report. Reference inventories are stored
once per appearance; each rival preserves reference/overlap counts and support
witnesses, with exact conflict IDs retained.

Before admission, each historical reference inventory is independently
core-validated. Withdrawn/unstable views remain explicit in the validation
ledger; their members retain physical placement and frozen core diagnostics.
An unestablished pooled hypothesis is not a named destination. Reconciled
same-rank appearances use a deterministic existing owner, separately labelled
from upward promotions; distinct assigned cast slots never merge.

Tentative and residual clusters have stable report IDs/names and lineage;
tentative links preserve their physical source home and provide no reference
authority. Mutual subset reconciliation validates both sides, coherent
reference cores and every outside rival before removing a proven duplicate
subset from distinct-person competition; mixed exceptions remain rivals.
The existing higher-ranked owner receives a named appearance, not a folder.
Repeated frozen recovery boundaries may add only independently accepted,
content-distinct members with original-base admission/core witnesses.
Each growth cohort is jointly core-validated without invalidating its
frozen-base prerequisites; rejected additions are held with reasons and
cannot oscillate back into the same run's reference inventory.
The same recipe records no-growth versus staged-growth upward admission.
There is no tentative-member certification or chained identity union. Caps fail as incomplete,
not as a successful report. `index.html` and `directed.json` provide a
browsable decision summary; `directed-details.json.gz` contains the complete
candidate/rival evidence and is hash-checked with the report receipt. The
output is a saved-measurement shadow only:
it enumerates only active Gallery/Review filenames to locate current originals
by unique stable ID, checking their current catalogue content bindings.
This location manifest is receipt-bound; missing, ambiguous and changed
bindings are explicit, not wrong-image fallbacks. It does not copy library photos, read images, call models, change
files, install policy, or activate `group_lifecycle`.

The saved evidence does not encode the newly requested overrideable **Keep**
control, so existing placement locks/intents are preserved and Keep behavior
is deferred, not simulated. Fictional-family eligibility is a candidate
assessment only when distinctness and independently supported resemblance
coexist; no family fact, default story role, or live GUI action is inferred.
The report's reviewed positive fixtures are development controls, not blind
accuracy. Independent rule selection and acceptance remain separate gates.

## Sandbox score-band release experiment

`bin\sandbox-red-release.cmd` is an isolated Sandbox experiment, not normal
intake or a workflow replacement. Its current Review mode selects the
requested `--release-band` values using the saved policy, verifies the
Review and cached scores, and defaults to a read-only census. The supported
arguments are listed in `bin\help.cmd`. A routed preview additionally binds
the original receipt and audit, previous release and current Review; apply
requires the exact `--expected-plan-sha256` from that preview. Use repeated
`--continuation-run` arguments in chronological order for later releases:
the verifier checks each journal and its historical state against subsequent
recovery snapshots, and binds their hashes to the new preview.
`--include-unscored` also selects unavailable own-core scores. The preview
binds independently measured candidates and rival assessments; former
non-voters and quality-ineligible photos are held unassigned. If any
identity lacks an eligible rival core, the release holds every candidate
unassigned and labels rival scores as covering available cores only. Other
frozen-core diagnostics still block the release. Supplemental read-only
measurements are not persisted to the cache.

The report records former owners, destinations, scores and workflow flags.
Apply journals the Sandbox file changes, but does not update workflows or
prove consumer coverage; an affected selection may still need replacement.
Use the run's `--check` and recovery preview before considering recovery;
`--recover-apply` changes the Sandbox and remains an explicit operation.
Check for later edits and dependent releases before recovering an earlier run.
A separate reports-only viewer refresh is outside the release journal and
becomes stale after recovery; preserve shared report outputs before refresh,
then verify the refreshed reports and actual browser separately. Human
identity acceptance and shared-workspace or Production changes remain
separate gates.

## Maintained directed Sandbox reformation

The saved-report shadow and the maintained runtime are separate surfaces.
The maintained path is opt-in through `clean-rebase --regroup --directed`;
`--directed-recipe` is mandatory and there is no selected default. The
historical regroup path remains unchanged when `--directed` is omitted.
Supported recipe names are `directed-core-continuity`,
`directed-lower-category-admission`, `directed-stricter-retention`, and
`directed-stronger-release`. Their values are experimental and must be
reviewed with the source-core candidates before matching:

| Recipe axis | Core continuity Sisters/Angels/Models/Prospects/Potentials | Admission Sisters/Angels/Models/Prospects/Potentials | Retention | Strong release source/destination/margin |
| --- | --- | --- | --- | --- |
| directed-core-continuity | .60/.60/.50/.45/.40 | .50/.45/.40/.35/.35 | existing ordered-middle recipe | .30/.60/.30 |
| directed-lower-category-admission | .60/.60/.50/.45/.40 | .50/.45/.35/.30/.25 | existing ordered-middle recipe | .30/.60/.30 |
| directed-stricter-retention | .60/.60/.50/.45/.40 | .50/.45/.40/.35/.35 | .35/.30/.25/.20/.20 | .30/.60/.30 |
| directed-stronger-release | .60/.60/.50/.45/.40 | .50/.45/.40/.35/.35 | existing ordered-middle recipe | .25/.65/.35 |

The bounded corrective comparison adds three opt-in recipes:

| Recipe | Starting Sisters/Angels selection minimum | Reference core floor / support | Admission / join / tentative support | Strong source correction | Cohort |
| --- | --- | --- | --- | --- | --- |
| directed-corrective-starting-045 | .45 | .40/.35/.30/.25/.25; 3 independent witnesses | .50/.45/.40/.35/.35; 4 join, 2 tentative cast | source ≤.30 + 2 independent refs; destination uses qualified category admission/margin | constrained average-link ≥.25; 2 neighbors/member |
| directed-corrective-starting-050 | .50 | .40/.35/.30/.25/.25; 3 independent witnesses | .50/.45/.40/.35/.35; 4 join, 2 tentative cast | source ≤.30 + 2 independent refs; destination uses qualified category admission/margin | constrained average-link ≥.25; 2 neighbors/member |
| directed-corrective-starting-060 | .60 | .40/.35/.30/.25/.25; 3 independent witnesses | .50/.45/.40/.35/.35; 4 join, 2 tentative cast | source ≤.30 + 2 independent refs; destination uses qualified category admission/margin | constrained average-link ≥.25; 2 neighbors/member |

The starting cutoff selects a content-bound subset of eligible references in
each original Sisters/Angels view; it does not apply the same floor to every
member or replace the separate qualification gate. Core qualification uses
the previously tested `ordered-three-core-support` value (three independent
other witnesses), rather than the historical directed core's four. Strong
continuity still uses a separate `.80` own-score minimum and is not the seed
exclusion cutoff. Candidate inventory, selected references, score basis,
exclusions, and qualified-reference counts remain explicit. Admission floors
and category distinct-rival margins remain the ordered-middle values
(.12/.10/.08/.06/.06); retention remains .25/.22/.18/.15/.15. Measured source
incompatibility uses a frozen own score ≤.30 plus two independent source
references, or an exact human `different` pair. Exact `different` and
`uncertain` conflicts, configured identity negatives, placement locks, and
distinct authored cast slots remain hard blockers where applicable; they are
not numeric similarity floors. A two-witness cast association may grant a quality- and
margin-gated tentative Gallery placement when the full independent-member
reference gate is not met, but it never grants core/reference authority.
Likewise, source-incompatible weak members may be evaluated with a coherent
cohort for a provisional non-core owner; low score alone does not release a
source member, and a provisional owner is not a confirmed identity. Cohort
formation requires independent nonconflicting neighbors and retains explicit
negative-identity and authored-cast-slot barriers rather than using
unconstrained connectivity. Readers retain frozen-source/current scores,
candidate and qualified reference inventories, exact blockers, and
assignment-versus-reference provenance. These recipes are comparison
candidates only: they do not change defaults or independently certify visual
identity accuracy.

Corrective strong-source release has no absolute destination `.60` or margin
`.30` gate: the destination must be an individually qualified option, meet its
normal category admission floor and distinct-rival margin, and retain a
qualified stable reference view plus the full four-witness join. This cannot
promote a tentative two-support assignment. The historical
`directed-core-continuity` recipe continues to require its original absolute
`.60/.30` destination gates.

For exact runtime parity, a supported LEAN continuation may opt into
`--capture-regroup-call` on `--apply --regroup --directed`; repeat the flag on
`--check` and `--install` so the saved continuation mode remains bound. It writes
`regroup-call-input.json.gz` beside that run's `run.json`; `run.json` binds the
capture file and input digest. Format `group-lifecycle-regroup-call-v1`
records the exact pre-call rows, measured `Photo` properties (including raw
and centered vectors), catalogue, policy, selected IDs, fixed timestamp,
human pairs, reference exclusions, recipe and dominant-provisional flag. It
also records the first call's rows, catalogue and report. Name generation is
captured as an ordered transcript of each seed, sorted `taken` names, and
returned name. For both replay calls, return the recorded name only when the
seed and sorted `taken` set match the next transcript entry; fail if a call
differs or entries remain. Deep-copy the captured initial catalogue for each
execution, use the same fixed timestamp and all other inputs, reverse only the
input row order for the third call, and compare canonical outputs and catalogues.
Rehydrate each measured entry with `engine.Photo` from its saved path, group,
folder, hash, and raw-measurement fields, then restore its saved centered
`vec`; no source image reads are needed.
This is evidence capture for the existing runtime call, not a second matcher or
a full-population acceptance claim.

These are selectable experiments, not routine policy. A read-only
pre-intake candidate review can enumerate current Sandbox Working
Angels/Sisters Gallery rows and their authored anchor, saved supported
core-use, content-matched protection-provenance, and legacy protected
placement metadata:

```cmd
bin\sandbox-rebase.cmd "SANDBOX\Working" "SANDBOX\Working\_sandbox-state\RUN" --baseline working --cast-seeds core --regroup --directed --directed-recipe directed-core-continuity --dry-run --core-selection-preview
```

The command writes `RUN\core-selection-preview\core-selection-preview.json`
and an HTML viewer that links directly to current source Gallery images. It
counts Gallery/Review originals separately from regenerable derivatives;
duplicate-ID diagnostics use original-source files only. Various is incoming
mixed intake and is reported as direct Gallery/Review files plus nested
incoming files, not as unexplained fragmentation or a core/reference source.
The JSON inventory and candidate list are complete and uncapped. The HTML
viewer shows 24 original-backed cards per page, with category and identity
filters in a responsive layout; long duplicate diagnostics are collapsed and
show at most 50 entries in-page, with the full list in JSON. If Working has no local
`.likeness-library.json`, the preview does not fall back to the repository
catalogue. Candidate rows show authored anchors, content-matched supported
memberships and protection provenance, and legacy protected placement holds
separately. Every row is `candidate only`; face quality, independent support,
measurement eligibility, and workflow selection remain unevaluated. Legacy
protected placement is not evidence that a photo is a trusted reference. This
command hashes the displayed cast Gallery inputs but does not prepare images,
detect faces, invoke a model, write a catalogue, or match. Human gate 1 must
choose the trusted references and recipe; no inferred measurement is implied
by the metadata tiers.

After that gate, `rebase-flow.cmd --regroup --directed
--directed-recipe NAME --dry-run` binds the selected mode and recipe into
every matching preview, resume, install and check command. Saved flows and
clean-rebase previews reject recipe changes. Maintained stage pages and the
recap distinguish same-home, upward, same-rank, correction, and held rows;
assignment disposition is separate from reference qualification.
Residual cohorts are classified using their independent centroid against
authoritative qualified cast-view centroids (best score per distinct cast
owner), not an absent cast score. The existing category and visual-review
gates remain unchanged for confirming independent identities.
`residualClassifications` records
their stable candidate names, measured cast scores, core floors, pair-support
counts and explicit hold reasons; appearance/publication pages expose the
candidate name and qualification blocker separately from physical assignment.
Only independently qualified, non-review-held cohorts create confirmed
independent identities.

Various is transient intake. After supported matching, a credible unambiguous
parent may receive a **tentative/non-core Gallery assignment** using the
existing admission floor, reference-support count, full distinct-rival margin,
quality, negative, rejection and placement checks. Independent cast admission
is not bypassed. Otherwise usable, safe unmatched photos receive named
**provisional Potentials**, grouped by the existing bounded coherent-cohort
routine; a singleton container is allowed. Needing an output folder does not
certify a distinct person or satisfy a visual-review/core gate. Existing cast
uncertainty does not authorize ejecting its members. Explicit locks and
unavailable/ineligible quality remain enumerated intake exceptions rather than
forced assignments.

Catalogue `identityStatus=provisional` and membership
`assignmentDisposition`, `sourcePersonIds` and content-bound `assignmentEvidence`
preserve this distinction and configured-negative lineage. Tentative/provisional
members always have `coreUse=false`; Gallery location cannot restore their
reference eligibility after serialization, reload or later directed runs.
They cannot vote, grow reference views or attract arrivals. Readers label
provisional containers as uncertified, and `assignmentSummary` separately counts
supported/tentative/provisional photos, confirmed new identities, provisional
containers, Review, Junk and remaining Various exceptions.

Quality exceptions preserve measured reasons separately: possible additional
faces and unavailable measurements are not automatically unusable. Measured
small faces/head obstruction are recorded as recoverable-Junk candidates.
The immutable rebase proposal retains these as explicit exceptions. After
installation, use the existing action launcher for a separately bound
recoverable disposition; no storage destination is added to clean-rebase:

```bat
bin\likeness-actions.cmd quality "ABSOLUTE_APPLIED_SANDBOX_RUN" --dry-run
bin\likeness-actions.cmd quality "ABSOLUTE_APPLIED_SANDBOX_RUN" --apply
bin\likeness-actions.cmd quality "ABSOLUTE_APPLIED_SANDBOX_RUN" --check
bin\likeness-actions.cmd quality "ABSOLUTE_APPLIED_SANDBOX_RUN" --undo --dry-run
bin\likeness-actions.cmd quality "ABSOLUTE_APPLIED_SANDBOX_RUN" --undo --apply
```

Only recorded small-face measurements with one detected face, or recorded
head-obstructing screenshot bars with one detected face, qualify. Multiface,
unknown/no-face measurements, identity scores and an unverified candidate flag
never qualify automatically. Existing action validation still rejects protected,
anchored, workflow-selected, changed or colliding photos. Automatic preparation
quarantine is not reused: it deliberately refuses catalogue-owned photos.

The wrapper uses the existing `photo-junked` transaction, configured Junk root,
retained-preparation transfer journal and guarded undo. The same transaction's
verified recovery backup is scoped to the catalogue and affected photo/retained
files; it does not copy the full library or create a second recovery snapshot.
`RUN\quality-disposition.json` binds the applied run hash, installed/current
catalogue hashes, exact batch/action records, original and prepared tuple digest,
source/destination content hashes and backup-manifest hash. Check verifies every
run photo exactly once across active and quarantined locations, unchanged
catalogue/action bindings, recoverability and retained evidence. Apply/check and
undo repeat safely; an interrupted prepared receipt fails explicitly for recovery
inspection rather than blindly repeating a possibly completed transaction.
Run receipts remain unchanged; their ordinary publication check describes the
pre-disposition state. After quarantine use the disposition check for current
active-plus-quarantine acceptance; undo restores the original routes. Refresh
reports separately using the supported reports-only launcher. Remaining quality
exceptions retain explicit measured/unknown reasons and are not claimed as Junk.

Family naming runs once over all final qualified lower-owner clusters against
final qualified cast references, never pre-validation seed cores or provisional
members. `familyNaming.ownerAssessment` covers every active catalogue owner,
including empty owners and provisional containers, with canonical folder,
reference count and explicit insufficient/no-authority/name-ineligible status.
The recap exposes this coverage separately from actual family assignments;
an absent family score is not a negative match or permission to fabricate one.

The continuity recipe requires four independent pair witnesses for each
core member, hence at least five independent photos. A two-to-four-photo
Potential candidate cannot bootstrap itself into a qualified core. Initial
reference reconstruction preserves coherent subsets at the same gates; it
does not convert a pooled historical seed-centroid score into pair evidence.
Alongside complete-link candidate subsets, reconstruction tries deterministic
per-anchor independent-support neighbourhoods. Each neighbourhood must
independently pass the unchanged core qualifier; overlapping qualified views
remain separate hypotheses. No connected-component union, promoted-reference
bootstrap, or transitive identity merge is performed. The existing per-call
two-million-operation bound also limits neighbourhood construction and
qualification; exceeding it fails explicitly rather than publishing a partial
result.

Configured `runtimeSettings.different` folder pairs are separate from human
reviewed photo pairs. Directed matching resolves them case-insensitively
against active catalogue folders and their recorded folder histories, then
enforces stable person-ID exclusions across canonical reconciliation,
destination admission, reference qualification and residual source lineage.
Ambiguous aliases or both endpoints resolving to the same owner fail.
Absent owners are explicitly nonparticipating, not guessed from similar names.
`configuredIdentityNegatives` records the resolution, including absent folders;
boundary witness policies retain the resolved ID pairs. Renaming a destination
cannot remove its exclusion. Final row reasons replace pre-directed routing
prose, and residual holds distinguish no qualifying cluster, classification
review and insufficient independent references.
Strong correction still requires affirmative source incompatibility, an
independently qualified destination, and the full distinct-rival margin.
The mode is experimental and proposes destinations only; installation,
Production changes, Keep transactions, live GUI controls and independent
accuracy acceptance remain separate human gates.

The main Photo review browser includes unassigned `Various/gallery` and
`Various/review` originals. Overview's **Unassigned Various holds (all
locations)** link selects `person=Various` without a bucket restriction.
Each card retains its actual Gallery/Review location and source lineage;
Various is not a person and its Gallery holds never establish an identity
core or primary reference. An unavailable requested person remains an empty
explicit selection instead of silently showing unrelated photos. Empty
catalogue identity warnings remain visible; retained history is not deleted
to silence missing-folder diagnostics.

The bounded dominant-face adaptation is opt-in on the existing continuation
launcher: `lean-continue.cmd --regroup --directed --directed-recipe NAME
--dominant-provisional ...`. It uses the unchanged configured strict
`secondaryFaceRatio < multiFace` guard and minimum usable face pixels, with an
explicitly available secondary ratio and the saved largest-human-face embedding.
Only safe Various intake may use it, only for coherent provisional Potentials.
It does not enable parent admission, cast/correction matching, references or
reference growth. Missing ratios, substantial second faces, unavailable vectors,
quality holds, negatives and placement locks retain their independent safeguards.
These are dominant-face candidates, not assertions that other detections are ads
or UI. `assignmentPolicy` binds the opt-in, floors, measurement basis and exact
assigned IDs; content-bound membership evidence retains the face-count/ratio
provenance across export/reload. Named provisional Gallery members remain
reference-ineligible and cannot attract later arrivals.

After guarded quality undo, original prepared-source continuation may additionally
select `--undone-quality-run ABSOLUTE_APPLIED_RUN`. Before matching it verifies the
exact undone disposition once, including run/input tuples, restored catalogue
hash, quarantine/undo action populations, retained bytes, conservation and recovery
backups. Only those verified Junk/undo record IDs bypass the existing intervening
placement-action refusal; unrelated placements still refuse. Later supported
authored protections/rejections continue through normal content-bound migration,
not the exemption. The original catalogue bytes are never restored manually or
discarded. New continuation receipts bind the recovery receipt/run hashes and
reject drift or changed grouping/opt-in options on resume/check/install.

Maintained directed receipts keep scalar decisions and compact stage rows
readable. Complete per-photo witness/rival diagnostics are stored once in
`groupLifecycle.decisionEvidence` as deterministic gzip/base64 JSON, bound
by uncompressed byte count and SHA-256. The versioned interned representation
stores identical nested view/reference/witness structures once, losslessly.
Version `gzip-base64-interned-json-v2` also shares scalar strings (including
photo/view IDs) and dictionary key schemas. Overlapping but nonidentical
reference inventories therefore reuse their ID vocabulary and option field
names without deleting any inventory, hypothesis or per-member score.
String-only inventories store their ordered numeric vocabulary indices once
per distinct list; decoding restores the exact original order and full IDs.
`unpack_runtime_decisions` resolves
the evidence by photo ID; route verification and recap generation validate
the content binding and materializes independent mutable objects for consumers;
legacy receipts remain readable. Interned **uncompressed stored evidence** and
the ordinary run manifest retain their 64 MiB limits; compression does not waive
either. Expanded consumer JSON may exceed that stored limit because it repeats
the shared evidence. Receipts record exact stored/expanded byte counts and
per-section expanded serialization bytes, stored node/string/schema bytes and
shared-table counts; an over-limit refusal includes those
diagnostics. No rivals, reference IDs, blockers or witnesses are truncated.
Fresh Various inputs may qualify against existing destinations, but are
never reference seeds merely because they are incoming. Cast arrivals
additionally require the unchanged shared frozen-reference admission gates.

The selected directed recipe produces a copied, versioned experimental policy:
its admission floors/margins are shared with route verification, and missing
Sister/Angel Gallery admission flags are enabled for this experiment. Explicit
`false` refusals remain refusals. Quality, independent-witness, rejection,
content-binding, protection and distinct-rival checks are unchanged; the
standard draft policy file is not modified. The receipt exposes this effective
`admissionPolicy`, rather than treating a directed score as admission approval.

Fresh catalogues reconstruct every existing source owner across the category
ladder. Gallery rows are reference **candidates**, not trusted by folder.
Initial inventories and coherent reconstructed subviews must independently
qualify at the selected recipe's unchanged core floors. Qualified references,
including certified staged additions, are exported once in
`groupLifecycle.qualifiedReferences`; membership `coreUse`, group reference
IDs and packed decisions are checked against this ledger. Explicit withdrawals
cannot re-enter through growth or serialized resume. Owners with insufficient
references remain visible in `sourceCoreSelection.referenceUnavailablePersonIds`;
reference loss alone does not eject members.
Exact different/uncertain pairs inside one source owner create an explicit
source-reference hold: splitting them into two appearances cannot silently
certify contradictory people as the same owner.

Verified starting Sister/Angel references with independent own-seed scores
of **0.80+** form the strong baseline backbone. This score is recomputed from
eligible, content-bound, independently selected own-seed witnesses, excluding
self, identical-content and near-duplicate votes. It is not a calibrated
probability, arrival threshold, sole seed cutoff or physical lock. Other
qualified subviews remain usable below .80; a singleton or invalid saved high
score cannot certify itself. Strong members can still be corrected only with
independently qualified destination evidence, affirmative source contradiction
and the existing exceptional-correction gates.

Eligible parentless residual cohorts reuse the maintained stable identity/name
machinery and existing category classification. They become actual person
records, named supported or tentative appearance groups and Gallery/Review
routes; ambiguous, singleton and quality-held exceptions are not forced into
people. Creative naming and configured family surnames run after identity
decisions and do not establish same-person evidence or fictional roles.

Directed phase pages retain immutable computational boundary rows for qualified
references, reconciliation, initial admission-option evaluation, each accepted
growth boundary, settled membership, appearance hypotheses, named runtime groups
and final publication. Each captures its actual frozen reference inventory and
witness policy; the reference boundary includes withdrawals. Initial reference/
option rows explicitly say membership is not yet decided and retain source paths,
rather than copying final routes or claiming reference eligibility is membership.
Final canonical/family renames update only the publication snapshot. Combined
boundary evidence is capped at 64 MiB; exceeding it refuses incomplete output.
Serialized stage rows keep a readable photo/status/core index plus lossless
`boundaryEvidence`; `lifecycle_stage` restores the full immutable boundary.
Repeated paths, views, witness structures and inventories are interned instead
of copying all expanded rows into the run manifest. Legacy full-row receipts
remain readable; recap pages resolve the same full rows through this helper.
The reference boundary records initial independent own-centroid scores,
pair-support counts/floors, conflicts and candidate inventories separately from
qualified inventory. Qualification uses centered normalized cached face vectors:
the centroid score and pair-support count are distinct gates. A historical
cast-seed score is not interchangeable with a pair similarity or independently
qualified score; the actual recognizer/cache binding belongs to the source run,
not an assumed ArcFace model or calibrated probability.
Older receipts with final projections retain that explicit warning.
Bounded recap pages show exact sources/destinations, withdrawal reasons,
admission blockers and unavailable-reference holds with verified original links.

Cached continuation preserves the same explicit selection:

```cmd
bin\lean-continue.cmd --root "SANDBOX\Working" --source-run "ABS-PREPARED-RUN" --run "ABS-NEW-CANDIDATE" --regroup --directed --directed-recipe directed-core-continuity --dry-run
```

Repeat `--regroup --directed --directed-recipe NAME` and any `--review-source`
on resume/check. The continuation receipt binds these flags and refuses changed
mode/evidence; cached rebase-flow continuation must not fall back to legacy
matching. This preview does not authorize applying a new candidate or installation.

## Fictional relationship editor

The maintained **Fictional relationships** navigation opens
`_reports/library/fictional_relationships.html`. This is a separate manual
story editor, not a facial matching tool or a replacement for existing
family surnames. Choose two catalogue characters, a fictional role and a
narrative note. A successfully saved new assignment is active immediately:
there is no pending-approval status. Edit, reject with a reason, or undo the
latest change on a relationship; history is retained. Editing a rejected
record does not silently reactivate it.

Roles currently include ally, rival, mentor, student, companion, spouse,
sibling, parent, child and other. Use parent/child/sibling with a narrative
note for fictional mother/daughter/sister wording; there is no separate
custom-role field or automatic reciprocal-edge creation.

On each page session, **Connect library narrative file** and choose the
library root shown on the page. Desktop Chromium with File System Access
and Web Locks writes only that root's `.fictional-relationships.json`.
Directory permission is a browser safety requirement, not approval of
individual relationships. A verified successful write is explicitly shown;
failed writes and stale-file conflicts do not advance the displayed saved
state. Reload the connected file after a conflict. Avoid concurrent edits
from other applications: browser locking is not an operating-system atomic
compare-and-swap.

Import is read-only inspection; export downloads a copy and is **not** a
library save. Nothing is persisted in localStorage. The editor loads its
mutable history when connected, so a report refresh never overwrites it.
Normal report-only checks verify the generated editor and catalogue
snapshot; connecting validates the narrative file. Regenerate reports if
the catalogue changes: selectors validate against the generated snapshot.

Assignments are shown on the dedicated page. Overview and Photo review
link to it; they do not yet render these story edges in every identity
panel or the existing family tree. Existing generated family links,
surnames, identity ownership, photo paths, matching, core use and action
undo are unchanged. No story roles are inferred from images and this
increment does not supply automatic AI-authored relationship suggestions.

## Rebase recap navigation

The recap's person links open a new tab: current people go to filtered
Photo review; previous/emptied names go to saved continuity evidence.
Cast/Other-identities links open their expandable recap details. Families
keep compact score/path tables and offer collapsed comparisons with up to
five saved Gallery samples per member (Review fallback if no Gallery).
These deterministic samples are not a measured core ranking. Missing
supplementary reports are labelled unavailable rather than linked.
The final audit separately shows saved eligible automatic moves and blocked
follow-up reasons. Legacy `nextPassNeeded` is not proof another automatic
pass can move a photo; policy/margin/protection holds remain visible.

Explicit staged Gallery admission can be enabled for both Sisters and
Angels. `galleryAdmissionMinimumSimilarity` optionally separates that gate
from `photoRouteMinimum`; omitting it preserves existing behavior.
Sisters cannot have a lower Gallery minimum than Angels when both enable
admission. This capability does not enable Angels in an existing policy
or install a preview; the
[cast comparison](../plans/2026-10-23-cast-seeded-library-rebase.md#nov-6-shared-gate-implementation-and-frozen-comparison)
owns the proposed minima and saved-evidence results.

Combined Overview/Review refresh shares a general-domain scoring context,
preparation-history index and operation-local verification session.
The pages still publish sequentially; successful freshness state is
recorded only after a full content/path/owner seal. Standalone commands
rebuild their own context. Freshness includes reader/rendering code and
configuration changes, so a report-reader fix requires a report refresh
even when the photos are unchanged.

For current state and the sandbox/production boundary, see
[STATUS.md](../STATUS.md), the
[processing contract](likeness-processing-contract.md) and the active
[engine acceptance plan](../plans/2026-10-22-likeness-engine-acceptance.md).
The photo-library ingest routine is documented in
[original-photos.md](original-photos.md).

**Current boundary (Oct 25):** the prepared sandbox clean-start flow is
implemented, including intake-only review/resume and retained detail. Real
recipe/identity/gallery acceptance and the incremental production cutover are
not complete. The repository policy remains draft. Use the
[clean-start sequence](#clean-sandbox-rebuild-versus-category-reclassification),
not a historical reset or legacy sorter, for the next reviewed experiment.

## Sandbox processing profiles

`bin\sandbox-rebase.cmd W RUN --profile fast|lean|full` selects the processing
path. `bin\rebase-flow.cmd --root W --run NAME --profile fast|lean|full`
forwards the same choice to intake, matching, install and checks.
Preview first; a flow's `--apply` includes reset and installation and is
**not** implied by selecting FAST. Continue to require separate approval
for an actual library run.

| Profile | Image processing | Evidence and recovery |
| --- | --- | --- |
| FAST | Safe source decode, matching's normal face measurements, original-byte native publication; editing and 944x1104 products deferred | LEAN evidence by default; `--storage-mode full` can retain richer evidence independently. Recovery defaults to full backup/undo |
| LEAN | Existing balanced preparation and selected padding, then normal installed derivatives | LEAN evidence; explicit disposable sandbox recovery remains optional |
| FULL | Existing complete preparation/diagnostic products and installed derivatives | FULL evidence; full recovery required |

Omitting the profile resumes the saved intake; a new omitted-profile run
still starts standard LEAN. Explicit profile/storage/recovery mismatches
refuse rather than reinterpreting a checkpoint. FAST has its own versioned
recipe and fresh matching cache; it never reuses a prepared image's scores
as raw-image evidence.

FAST Photo review uses the original image with its filename link.
Overview's small display thumbnails are resized originals, not generated
head/chest crops. Retained details and history label editing as deferred,
not clean, missing or complete. Gallery maintenance and `originals.cmd`
honor verified FAST lineage rather than silently generating 944x1104 files.
FAST does not change matching thresholds, protections, names or artist scope.

Keep FAST/LEAN/FULL runs separate while comparing them. The existing
`lean-continue.cmd` accepts standard LEAN evidence only, not FAST.
Selective completion into LEAN/FULL and changed-pixel grouping-delta
acceptance are still open under
[phase07](../plans/likeness_process/07_rebase_and_acceptance.md#nov-11-selected-flow-increment-fast-first-compatible-lean-and-full).
FAST first, then LEAN, then FULL acceptance precedes any separately approved
final Sandbox-to-Production snapshot; this feature performs no snapshot.

## General and artist entry points

`bin\likeness.cmd` now discovers only Angels, Sisters, Models, Prospects,
Potentials and Various. `bin\likeness-artists.cmd` discovers only configured
Artists folders. It is a thin entry point into the same implementation, not a
second intake, detector, embedding model, cropper, Junk rule or grouping engine.
Source layout remains `Artists/<artist>/gallery` and
`Artists/<artist>/<person>/gallery`; no files were relocated by the split.
The shared preparation launcher still handles either source scope explicitly.

```bat
bin\likeness-artists.cmd --root "B:\Sovereign Territories Sandbox\Working" --dry-run group --singles
bin\likeness-artists.cmd --root "B:\Sovereign Territories Sandbox\Working" --check
```

Global `--dry-run` comes before the command, refuses apply flags, and supports
scan/group/artists/junk/crop/undo/policy and clean-rebase inventory. It suppresses cache/origin writes and
model downloads. With no explicit command, `--check` is a read-only scan: exit 1 if an unusable image is
found; it does not certify identity correctness, derivative freshness or
automatic cleanup quality. Ordinary reporting commands may write requested
reports and cache data; use their documented output paths.

`family-preview` returns a successful process exit after writing its JSON/HTML
report. It does not apply surnames or modify the catalogue. Missing qualifying
family evidence produces an explicit empty suggestion list, not invented
relationships. Recorded original/current person names remain separate from
fixed Angel/Sister character slots.

In the prepared rebase, incoming Angel/Sister candidates go to Review.
Inspection and an explicit `review-approved` action admit a candidate to
Gallery; similarity alone does not bypass this protected-cast boundary.
Approval/undo preserve the slot, recorded original/current names and history.

Both domains use the same YuNet/SFace weights and cache format, but default
state is library-local: `<work>/_likeness/general/` versus
`<work>/_likeness/artists/`, each with its own cache and move/crop history.
Explicit `--cache` overrides are supported; sandbox caches must remain under
Working. Cache centering is domain-stamped: an unstamped or different-domain
saved mean is diagnosed and recomputed, never silently borrowed. Existing
content embeddings are still reusable. Artist centering uses only usable
artist photos (including incoming mixed galleries); adding general/cast photos
cannot change artist scores. This deliberately changes the old all-library
artist scoring baseline; real threshold/quality acceptance remains open.
New clean general rebases stamp their saved mean for later reuse.

Artist grouping still assigns only within each source artist. Read-only
inspection/diagnostics can compare artist people; no general identities enter
their candidate set. General `group`/`artists` calls fail with the new launcher
name rather than quietly running artist operations. Artist cast/reconcile/
merge/retire commands are not enabled as general-routing backdoors; use guarded
staged photo actions where appropriate. Artist `folder` is inspection-only.
Artists write `artists_index.csv`/`.md`, not the general `people_index` files.

The move executor checks the whole batch's source and destination boundary
before moving anything, including `force` moves and reconciliation recovery.
An old general-pool artist return or cast-replacement batch that would write
Artists now stops; it requires a deliberately reviewed transfer, not an
automatic exception. Known artist-origin pool photos stay held rather than
being transferred by legacy `sort`. Test copies in Various remain general
inputs when their artist provenance is unknown.

Undo uses its domain-local history. If only legacy history exists, it is read
for recovery, but every recorded path must belong to this work root and domain
before any restoration; mixed-domain batches fail intact. Historical logs and
retained originals are not removed. Post-move originals naming/scaling/head
generation receives the same scoped roots and `--no-repoint`: a domain command
does not retarget selected workflows or persist a filtered workspace config.
Run the separately reviewed full-library/input refresh when that is intended.
No new chest/ComfyUI integration or preparation crop cutover is implied.

## Quick start

| Goal | Command |
| --- | --- |
| Inspect overall scoring reliability | `bin\likeness.cmd calibrate` |
| Save calibration and all eligible folder checks together | `bin\likeness.cmd --root "<library>" --cache "<cache>" diagnostics --out "<library>\_reports\diagnostics\<run>"` |
| Preview restoring sandbox category roots | `bin\likeness.cmd --root "<sandbox>\Working" sandbox-reset` |
| Check one person's folder consistency | `bin\likeness.cmd folder "Drakness"` |
| Preview artist-only grouping using the same engine | `bin\likeness-artists.cmd --root "<sandbox>\Working" --dry-run group --singles` |
| Audit active-core scores and metadata decisions | `bin\likeness.cmd audit-core` |
| Maintain derivatives and build both review pages (preview without `--apply`) | `bin\people-gallery.cmd --root "<library>" --out "<reports>" --cache "<cache>" --apply` |
| Build only the full Review page | `bin\people-gallery-review.cmd --root "<library>" --out "<reports>" --cache "<cache>"` |
| Preview separate Artist pages without decoding images | `bin\artists-gallery.cmd --root "<library>" --cache "<existing-cache>" --dry-run` |
| Publish/check only Artist HTML and small thumbnails | `bin\artists-gallery.cmd --root "<library>" --cache "<existing-cache>" --apply` then `--check` |

Diagnostics output must be a new directory under the selected work root's
configured `storageRoots.reports`; arbitrary external `--out` paths are refused.
The report includes a storage-configuration receipt.

People, Review and Prime comparison `--out` overrides must also stay within
that library's configured reports root. Escaping paths and reparse-point
destinations are refused; configure the reports root instead of writing
arbitrary external report copies.

### Separate Artist browser

Artist overview and photo review are generated at
`<work>/_reports/artists/artists_gallery.html` and
`artists_gallery_review.html`. Search/filter by artist, source group and
Gallery/Review; overview links open the corresponding filtered photo list.
Both pages share one content-addressed 240x300 JPEG per distinct source, load
images lazily and show at most 60 cards initially. Thumbnails fit/pad the full
oriented source, not a new identity crop or maintained ComfyUI derivative.
Click through to the current original at full size. No original copy is made.

The browser never runs matching, model inference, source cleanup, staged actions,
renaming or metadata updates. Cached face results are informational; missing
results are unassessed, not a successful face check. Readable/corrupt input
errors appear as explicit diagnostics and a nonzero result. Preview writes
nothing; `--apply` publishes reports only; `--check` recomputes expected report
bytes in memory and writes nothing. Exact repeats preserve report mtimes.
Generated byte counts are printed; unknown or edited obsolete assets are kept.

People overview/Review builds now use only the general scoring domain and do
not save the face cache. A supplied mixed Artist/general space is refused, not
made safe merely by hiding Artist cards. Old `--artists` options explicitly
direct callers to the separate browser. Normal report orchestrators no longer
pass them. People and Artist pages share basic navigation/footer styling;
the broader people layout/protection redesign remains separately planned.

The browser ownership manifests support narrow routine-backup omissions; see
[report backup treatment](original-photos.md#generated-browser-reports-and-backups).
They do not replace raw-source archives, face caches or identity metadata.

### Shared gallery theme and banner

`tools/art/likeness_library/gallery_chrome.py` is the one shared stylesheet and
page frame: colour/spacing variables, the banner masthead with People and Artists
links, the page-header card, navigation and footer. People overview, People
Review, Artist pages, the family preview and intake preparation reports all put
it before their own page rules, so a look change belongs there.

Badge sizes and category/score palettes also belong to this shared stylesheet;
page-specific semantic state badges retain their existing meanings. Linked
tags are underlined and show a hover border plus keyboard focus. Plain count
labels do not become links or gain new color thresholds. On screens wider than
760px and taller than 500px the compact page-navigation bar stays visible while
scrolling; the large banner scrolls away. Narrow/short screens and printed pages
use ordinary non-sticky navigation. Tiles shrink to their container when their
preferred size would overflow, including the Large Review setting.

The banner is `<work>/_reports/_assets/gallery-banner.jpg`, a 1024x360 crop
(about 54 KB) of the ComfyUI title art
`ST/title/SovereignTerritories_Title_00001_.png`. People and Artist `--apply`
runs copy the packaged `likeness_library/assets/gallery-banner.jpg` there only
when the file is missing. To use your own banner, replace that file with a wide
JPEG of about 1024x360; it is never overwritten. Without it, pages show a plain
gradient. The file is small and is kept in backups.

Commands that can move files preview by default. Review the output first and
add `--apply` only when you intend to make the described change. `--sheet
FILE.png` writes a labeled contact sheet for commands that support visual
inspection. After an approved photo move, run the normal library routine to update
derived images and selected-photo references. While the policy is draft,
production intake is paused before housekeeping; use previews and the isolated
sandbox instead.

## Scoring and folder structure

### Face vectors and similarity

The local pipeline detects the main face and turns it into an identity vector
using OpenCV YuNet and SFace. The two model files are downloaded once to the
configured `modelCacheRoot\models` (default
`%LOCALAPPDATA%\sovereign-territories\models`); photo data is not sent elsewhere.
Vectors are cached by image content, so moving or renaming a photo does not
require another face detection.

Displayed likeness is cosine similarity after subtracting the library's
average face. A clean run saves its centering mean in its cache, and subsequent
galleries and reconciliation reuse it: moving a photo does not silently change
its scoring space. Ordinary caches without a saved mean retain their existing
population-based behavior. Similarity is a ranking signal within this library,
not a universal identity probability.

For each scored human face, the engine also saves the lossless PNG returned by
the same `FaceRecognizerSF.alignCrop` call whose array is passed directly to
`feature()`. The library Review gallery links this exact input beside the
photo's score; it never substitutes a headshot derivative or an intake preview.
Evidence is stored locally under
`<work>\_likeness\<general-or-artists>\face-evidence\`, excluded from Git, and
bound to the scored source SHA-256, aligned-crop SHA-256, YuNet/SFace model-file
SHA-256 values, model identity and OpenCV version. The gallery verifies those
hashes before exposing a link and shows the scored source path/hash and model
provenance without embedding image data in the report. When a retained
preparation set is published, the current gallery photo is the verified
selected native image; the existing Preparation detail remains the source for
recipe and variant history.

On Windows, aligned-evidence persistence and verification use extended
filesystem paths, so nested Sandbox paths do not require enabling long paths
in the OS. Full source/model hashes and artifact names remain unchanged;
report links keep ordinary relative URLs, not filesystem-only prefixes.

Older cache entries are re-embedded when a normal likeness command encounters
missing or invalid alignment evidence, updating the vector and crop together.
The read-only Review gallery may recompute a missing crop in memory to report
the current model/source provenance, but it does not persist it; run a normal
`bin\likeness.cmd scan` to save it. `--check` and all other read-only scans
write neither cache nor evidence. An absent/invalid crop is labelled explicitly
and is never replaced with a proxy.

| Score | Gallery color | Interpretation |
| --- | --- | --- |
| 0.55 and up | Green | Strong resemblance; some same-person workflows use this as a candidate threshold. A cross-folder score alone does not prove identity. |
| 0.30 to below 0.55 | Yellow | Noticeable resemblance; inspect context before grouping or casting. |
| 0.15 to below 0.30 | Orange | Weak resemblance. |
| Below 0.15 | Red | Little measured resemblance. |

These colors are display bands. A separate adjusted-fit score is used for
Angel/Prospect alternatives; its lower-is-better bands and components are
described under [Pairing score details](#pairing-score-details).

### Folders and categories

A **person folder** holds one person's Gallery and Review photos. Current
person roots include Angels, Sisters, Prospects, Potentials, and individual
people inside Artists (`Artists\<Artist>\<Person>`). The artist folders
themselves, top-level `Artists`, and `Various` are mixed/source folders, not
person identities.

Prospects normally have at least five usable Gallery photos; Potentials have
one to four and remain active for future matching. Only eligible Prospects are
Angel replacement candidates. The sandbox policy treats `Models` as a
distinct active category; historical Model paths still need an explicit
migration rule. See the
[processing contract](likeness-processing-contract.md).

### Draft sandbox likeness policy

The versioned source is
[`likeness-engine-policy.json`](../../data/art/likeness-engine-policy.json).
It keeps the gallery bands above and currently classifies one-to-four usable
photos as Potentials, five-or-more with cast similarity below 0.40 as
Prospects, and five-or-more with cast similarity from 0.40 to below 0.55 as
Models. Similarity of 0.55 or higher remains a cast-review threshold, not
proof of identity.

The draft core/action values are category-specific: Prospects and Potentials
use 0.20 as the minimum core similarity and 0.30 as the Review-suggestion
boundary; Models use 0.38 for core similarity and 0.30 for Review suggestions;
Angels and Sisters use 0.38 for core membership and 0.15 for red-band Review
suggestions. These are core-selection floors, not Gallery admission or
removal thresholds. Eligible anchors and the provisional single-reference
fallback still apply. Existing cast Gallery placements are not eligible to
move cross-cast or down. Candidate grouping uses a
separate 0.25 average-linkage threshold and retains pairs and singletons.
Robust provisional cores exclude red outliers. Photo-to-core attachment and
group-to-core attachment use distinct tier thresholds; an action-support
minimum does not erase a small candidate group.

SIMPLE resolves same-ID collisions after inventory and lineage verification,
before preparation, initial cores or matching. Exact copies yield one keeper.
A verified prepared native and its exact retained raw original are one version,
not two edits. Otherwise newest filesystem modification time wins and routes
normally. A tie favors a catalogue-bound version, then the stable keeper
order. A protected Gallery copy wins over an unprotected edit; when more than
one protected Gallery has the ID, prefer existing anchor, workflow or
catalogue evidence, then the stable keeper order. Archive the other copies
and report the decision without stopping the run. Invalid lineage that
cannot be archived reliably still blocks apply.
The LEAN/FULL keeper uses the standard preparation recipe if still raw, or
preserves its verified prior preparation. Neither age nor protection certifies
a clean crop or complete overlay removal.
Preview records the decision, source hashes and dates, and proposed archive
paths. Apply moves only proven redundant copies to `_duplicates` in the same
recoverable transaction as placements. Use **ID collisions** in the saved
movement recap for keeper decisions, holds and archive links. This contract
does not redefine the separate legacy duplicates command or normal intake.

Automatic organizational-family association is enabled in the current draft
under the independent-evidence gates described
[below](#automatic-protection-and-original-names); this is not approved production
behavior. Lower-tier routing, merge and
split permissions are configured independently of cast Gallery protection.
The shared planner now proposes usable incoming/Review destinations even
under a draft policy; write authorization is checked separately. Operational
whole-identity merges, red-outlier splits and existing-identity category
transitions now have executable, reversible transaction paths. Their labelled
calibration and real incremental-batch acceptance remain open.
The sandbox clean installer can add cast Review photos, never cast Gallery
members. Production requires an approved policy and separate acceptance.

### Legacy reconciliation experiment (explicit only)

`likeness-experiments legacy-reconcile` runs the explicit legacy controller;
`likeness reconcile` remains its compatibility alias. This experimental
composition is not a normal intake stage and is not imported by default. It
plans incoming/Review routing and qualified Gallery
outliers together, then proposes disjoint reciprocal identity merges and
category transitions from final planned usable membership. A folder cannot
participate in a merge chain in the same pass. Category transitions preserve
the identity ID; merges retain the source ID with `mergedInto` pointing to the
survivor. Name histories, Review photos and derivatives travel with the
identity rather than being discarded. Empty directory shells are left intact
and can be reused by a later category transition.

The current draft retains a configurable `.95` near-duplicate similarity
ceiling for independent action support. This is a diversity heuristic, not
labelled proof of identity or independence. A single unmatched red outlier
may form a Potential only when its category explicitly permits it, the
source is large enough, and its retained core has enough diverse support.
The category split threshold and global outlier limit both apply. Alternative
identity reassignment still has its own match, margin and support requirements.
`smallGroupMaximumUsablePhotos` externalizes the cast-review size gate;
its current value is four, separate from clustering and action support.
Saved older policies retain the old four-photo gate, and missing new action
controls do not enable these new automatic actions.

Approved apply validates complete source/merge-target inventories again after
backup and journals every moved file and catalogue change. It then performs
one read-only affected-identity check using final membership in the same
saved scoring space. Its `check-reconcile_*.json` receipt explicitly reports
further maintenance candidates; it never cascades additional moves or claims
convergence merely because the first transaction succeeded. Undo uses the
original `reconcile_*.json` journal, not the check receipt.

`Various` is the incoming pool beside Prospects and Potentials. The standard
incremental routine, `bin\library.cmd`, still has legacy cleanup before shared
reconciliation and is draft-policy blocked before writes; see
[the routine](original-photos.md#the-routine). It has not adopted the prepared
intake sequence. `likeness sort` remains a manual compatibility command, not
the routine's primary decision path.

## Diagnostics: calibrate and folder

These commands complement one another; their scores and conclusions are not
interchangeable.

### `likeness calibrate`: library-wide reliability

`bin\likeness.cmd calibrate` is a non-moving diagnostic of the current library
and settings. Like other scans, it may populate the local embedding cache. It
leaves each photo out in turn, compares it against folders with at least two
usable photos, and reports:

- how often the correct folder ranks first;
- the distribution of own-folder and best-other-folder scores;
- how many photos would be confidently assigned correctly or incorrectly
  under the configured `assign` score and `margin`;
- same-folder and different-folder score distributions.

Use it to evaluate the behavior of thresholds across the library. Results are
computed from the current library each run; fixed percentages in old notes
should not be treated as current calibration.

### `likeness folder NAME`: one-person consistency

`bin\likeness.cmd folder "Drakness"` requires at least three usable photos.
For each photo, it compares that photo with the remaining photos in its
folder, then reports:

- **agree:** score at or above 0.25;
- **borderline:** from the configured `odd` threshold up to but not including
  0.25;
- **look like someone else:** below the configured `odd` threshold;
- an overall folder verdict, the photos to inspect, and each photo's closest
  match elsewhere with a possible destination.

`--all` lists every photo, not just the ones flagged for inspection.
`--outside` always lists outside-library matches. A one-person folder gets
those matches by default. The contact sheet option helps inspect flagged
photos. With `--apply`, only the photos judged to look like someone else are
moved; confirm the preview before using it.

### What the Review page already shows

The Review page scores each photo against the person's trusted-anchor or
provisional identity core, shows the core mode/size and photo state, and
surfaces closest cross-category matches. Prospect outlier states are available
for inspection. This is related evidence, but it is **not** the exact
`likeness folder` leave-one-out summary: core construction and scoring context
can differ.

Neither gallery currently presents the full library-wide `calibrate` report
or a single aggregate `folder` verdict. The rebase workflow is intended to run
these diagnostics against each completed sandbox result, measure their
runtime, and publish per-photo/per-identity CSV evidence plus a human-readable
Markdown report linked from that run's manifest. Include eligible active
identities across Sisters, Angels, Models, Prospects, and Potentials, while
recording exclusions and thresholds. Compare diagnostic time with rebase time
before deciding whether any stage needs an on-demand option.

The galleries should consume saved run evidence rather than rerunning
diagnostics on page load. The People Gallery should summarize library-wide
calibration and quality; each identity card and Review heading should repeat
the key per-person consistency/quality summary; Review should expose
separately labelled per-photo evidence and thresholds in its detail view.
Different diagnostics can score the same photo differently, so preserve each
measure under its own name and do not combine them into an unexplained score.
These results are diagnostic evidence, not automatic move instructions or
proof of identity/family relationships. This is an agreed rebase/gallery
requirement; implementation and timing measurements remain open in the active
rebaseline plan.

### `likeness diagnostics`: one-pass report bundle

`bin\likeness.cmd --root "<library>" --cache "<cache>" diagnostics --out
"<new-report-folder>"` calculates calibration and per-folder evidence from
one in-memory library scan. The output directory must not already exist. The
command is read-only apart from validating/populating the specified embedding
cache and writing the requested report files.
When `--root` is the named sandbox `Working` directory, both `--cache` and
`--out` are required to resolve inside that directory; the command refuses
global-cache defaults and outside report paths.

The bundle contains:

- `diagnostics.md`: human-readable calibration, eligible-folder counts,
  timings, and the lowest-scoring photos to inspect;
- `calibration.csv` and `calibration-photos.csv`: library-wide metrics and
  individual leave-one-out comparisons;
- `folder-consistency.csv` and `folder-consistency-photos.csv`: person-level
  verdicts and per-photo scores for eligible Sisters, Angels, Models,
  Prospects, and Potentials folders. Folders with fewer than three usable
  photos are listed as not evaluated. Artists are outside this active-category
  folder report.

Calibration includes folders with at least two usable photos; the folder
verdict uses at least three, matching `likeness folder`. The two evidence sets
are kept separate, even where both contain a photo's leave-one-out score.
Similarity never proves identity and these reports do not move photos.
The bundle is runnable now. It is a standalone support report, not a required
normal-import stage or identity proof. Run `diagnostics` explicitly against the
intended sandbox root/cache/policy; report writing and any permitted cache
population are separate from source and identity changes.

### `likeness family-preview`: direct references and naming collisions

`bin\likeness.cmd --root "<library>" --cache "<cache>" family-preview
--policy "<policy.json>" --out "<report-folder>"` writes `family-preview.json`
and a static `family-preview.html` with links to the existing review gallery.
Without `--out`, a timestamped directory is created under `_reports/analysis`.
Repeating the command safely replaces its two report files. Sandbox cache
and report paths must stay inside the named sandbox Working directory.

The preview uses the shared engine's frozen Gallery cores, stable person IDs
and recorded `z_` names. It lists each identity's closest direct reference
above the policy's `lookalikeGroups.suggestionMinimumSimilarity`, runner-up
and score lead; the JSON also contains qualifying alternatives and core
evidence. Artists are inventoried for name collisions but are never family
references. Unregistered/merged identities and identities without a usable
core are explicitly excluded from scoring suggestions.

These are **suggestions, not accepted families**. Reciprocal links may occur;
they are not followed into chains or collapsed into one group. High-scoring
pairs are flagged for possible same-person review before treating them as
distinct family members. Surname reuse is unresolved until reviewed; sharing
a name alone is not relationship evidence.

Non-cast naming proposals keep the current first name and borrow the direct
reference's surname. Existing and proposed full-name collisions are reported
case-insensitively, including names in Artist-person folders. Fixed cast
names have no rename proposal. Shared-initial alternatives, approved
membership/naming acceptance and manual family editing remain separate work.
Automatic family metadata and reconcile apply/undo now exist under the
[draft gates](#automatic-protection-and-original-names). The preview does not approve a draft policy,
change `automaticAssociationEnabled`, rename anything, save the catalogue or
move photos. It may populate the specified embedding cache.

### `likeness sandbox-reset`: restore the sandbox baseline categories

`bin\likeness.cmd --root "B:\Sovereign Territories Sandbox\Working"
sandbox-reset` verifies every file in the sibling immutable `Source` snapshot
against `source-manifest.json`, then previews the exact allowlisted category
restore. Add `--apply` to replace only `Working\Models`, `Working\Prospects`,
and `Working\Potentials` with their snapshot versions. If a category is absent
from `Source`, its generated `Working` directory is removed. The command
refuses roots outside the named sandbox layout, production/source overlap,
manifest path traversal, source drift, and unsafe category paths. It does not
change `Source`, Artists, Sisters, Angels, cache files, reports, workspace
configuration, or any path outside `Working`. It verifies the full snapshot
before every preview or apply, so expect time proportional to the source
library size.

This is a legacy guarded category reset, not the classifier or the complete
rebase; it does not rebuild catalogue decisions or retained photo lineage.
Do not run it over a prepared installation. Use the intake-aware
[clean-start runner](#clean-sandbox-rebuild-versus-category-reclassification)
for that implemented sandbox flow; its automatic diagnostics bundling is
still separate acceptance work.

For a read-only full-Working reset boundary preview, run:

```cmd
bin\likeness.cmd --root "B:\Sovereign Territories Sandbox\Working" sandbox-reset --full
```

`--full` verifies the immutable Source manifest and hashes the managed
Production baseline, reporting the exact Working target and Production
changes since the snapshot. It excludes configured operational storage roots
and reserved `_archive` from the proposed baseline. `_junk` and `_retired`
remain part of Production because they hold user-dispositioned photos with
provenance and deliberate restore semantics. Unclassified Production roots,
active-path byte conflicts, or an unfinished reset transaction make
`resetReady` false. The preview inventories Working without changing either
tree and classifies active-file content absent from Production. Unique photos
stay at their current relative paths. Unique non-image metadata goes to the
non-active `_reports\reset-review-bundle`; identical content already active in
Production needs no carry-forward, and same-path byte conflicts block apply.
Generated per-person output is rebuilt rather than carried and never blocks:
scaled/headshot/chest copies (former `*_944x1104` and grouped `944x1104`
folders), `.photo-derivatives.json` and legacy `gallery_intake` history
(`regenerable-not-carried`, not hashed). An installed prepared photo whose
retained-set manifest names an original already in Production is
`processed-copy-of-production-original`; a legacy `gallery_org` original not in
Production goes to the review bundle (`review-bundle-original`), never back
into the person folder. `carryForwardBytes` totals each class.
Production `Artists` are left out of the sandbox (decided Nov 2: Artists are a
separate later workflow), so they are neither copied nor prepared; sandbox
Artists files are not carried forward. `currentProduction.excludedCategories`
reports what was left out; `--include-artists` restores the old behaviour.
Production, Source, and Working reparse points are refused.

After reviewing a fresh preview with `resetReady: true`, add `--apply` to
replace exactly `Working` with the current Production baseline. The apply
revalidates the preview, copies and hashes every staged file, carries forward
the approved unique active photos and metadata, and writes a configuration
receipt under `_reports\reset-review-bundle`. A same-volume transaction journal
and owner lock allow an interrupted swap to roll back or finish cleanup on the
next apply. Sandbox-only generated reports, backups, run evidence, undo data,
and old `_junk`/`_retired` contents are not carried forward; the current
Production `_junk` and `_retired` contents are. Production, the immutable
Source snapshot, and sibling `ST-v9` are outside the target. An apply can still
be blocked by Windows handles or permissions; close report viewers before
retrying rather than bypassing the transaction guard.

**Clean-test limitation:** this implemented full reset copies current
Production directly into Working, leaves the older Source snapshot unchanged,
and carries unique Working photos forward. It is not the selected
[Production -> Source -> clean Working procedure](#clean-production-source-refresh-and-working-reset).
Do not use it to claim that Source has been refreshed or experimental Working
inputs have been excluded.

A visible Explorer tab is not sufficient evidence that the path is unlocked:
hidden tabs can retain directory handles. In the Oct 29 rehearsal, Microsoft's
Handle utility identified two Explorer handles to `_reports\library`; gracefully
closing that window released them. Do not force-close individual handles.
On Nov 3 the handles belonged to no open window: Explorer watches folders
listed as recent in Quick Access. Removing those folders from Quick Access
("Remove from Quick access") released them; restarting Explorer alone did
not, because it re-registers the same recent folders. The full reset now
rename-probes each top-level entry before staging and stops with a "close
windows, editor tabs or terminals" message instead of failing hours later.
Rollback cleanup uses Windows extended-length paths because moving old nested
backups into staging can exceed MAX_PATH even when their original paths did not.
If the journal says `committed`, rerunning the same apply finishes cleanup and
returns the existing receipt; it does not reset Working a second time or discard
the carried metadata bundle.

### Saved-input LEAN continuation (sandbox only)

Use `bin\lean-continue.cmd --root W --source-run ORIGINAL --run NEW
--dry-run` to inspect the restart boundary without starting matching.
`W` is the absolute sandbox Working path; run arguments are sibling folder
names under `_sandbox-state`, not paths. The original applied receipt,
prepared pixels, cache and current Gallery/Overview/Review stay untouched
while a separate preview is built.

- `--apply` creates **only a matching preview**. It verifies and references
  the original intake, copies compact face measurements, and recomputes
  initial cast cores, workflow exclusion, routing, refinement and names.
  It does not reset Working, repeat intake or install.
  If matching saved `run.json` but recap generation failed, repeat the same
  `--apply` to verify the original preparation/snapshots and refresh only
  the recap. It neither rematches nor installs. Incomplete runs without
  `run.json` still require a separately named continuation. Recap aliases
  reference the original sibling run's hash-bound source overlay; no
  overlay pixels are copied into the continuation.
- `--check` verifies the original saved preparation if NEW does not exist,
  otherwise the preview or installed publication; it does not write.
- `--install` publishes the reviewed preview, regenerates maintained
  derivatives and refreshes Gallery/Overview/Review.
- There is **no backup, previous tree, previous catalogue or rollback**.
  Partial publication records `reset-required`; recover by a clean sandbox
  reset/rebase, not by resuming publication or undoing it.
- The original catalogue is reconstructed from its exact checksum, never
  from generated identities/automatic locks in the installed result.
  Explicit intervening protection, anchors and rejection decisions are
  content-bound; ambiguous/new-identity or placement-history changes refuse
  rather than silently disappear. Shared workflow configuration is not
  updated; proposed selection replacements remain sandbox-local.
  Refreshed automatic protection provenance or generated name/family
  metadata is not itself a new manual decision when the identity's
  anchors/override and manual protection remain unchanged. Actual new
  anchors, overrides or manual protection still require explicit migration.
  Cheap catalogue/policy refusals precede full preparation verification.
- An uninstalled recap links proposed people to its own expandable photo
  evidence, not the installed Photo review roster. Photo links use the
  original SHA-256-verified prepared input, never a nonexistent proposed
  destination. Applied recaps retain filtered current Photo review links.
- Missing cached measurements refuse rather than loading models or quietly
  repeating intake. Prepared bytes, recipe, receipt and source bindings are
  still checked: reset-only recovery does not waive image-quality or path
  correctness.

The timed launcher supports the same path:
`bin\rebase-flow.cmd --root W --run NEW --reuse-run ORIGINAL
--recovery-mode disposable --dry-run`. Add `--apply --until match-preview`
only when matching is authorized; inspect the new preview before later
installation. Reset, originals, backup and intake steps are explicitly
skipped, including when `--with-previews` is selected.

Add `--verbose` to stream every child-process line to the terminal; the
timestamped per-step logs are always complete, even without that flag.
`--heartbeat 30` adds a summary every 30 seconds. References use the measured
Nov 5 LEAN durations for disposable steps where available, and explicitly
label the older Nov 3 references elsewhere. They are **not forecasts for
changed code**. `--until match-preview` bounds both the remaining-time
reference and execution, including a resume whose preview is already done;
it cannot continue into installation.

Disposable installs omit the two additional staging-content seals and
rollback inventories/retirement. They still hash final staged output and
verify installed publication; operation-local reuse never carries a stale
positive across commands. Space accounting walks Working once instead of
rescanning run/input subtrees. FULL retains its existing backup, rollback,
content-seal and undo contract. No detector/crop threshold or FULL behavior
is relaxed. End-to-end improvement must be measured on the next authorized
run; historical estimates are not a benchmark of these changes.

#### Pickup acceptance gates

Code tests are not saved-run or human visual acceptance. Run only the
separately authorized matching preview first; installation needs a later
explicit go-ahead. Keep the original run, installed viewers, Production
and shared selections untouched before that decision.

| Stage | Required evidence | Owning tasks |
| --- | --- | --- |
| Preview | Original prepared pixels/cache and exact pre-run catalogue bind correctly; no reset/intake, models, backup or rollback; generated identities/automatic locks are not seeds | Layout LY15a |
| Preview | Family direct links >=0.40, secondary links >0.35, chain explanation and unchanged display colours; trace broad Lujan membership rather than guessing from colour | Naming N16 |
| Preview | Sisters admission >=0.50 with >=0.10 rival margin plus independent support, quality/rejection/manual gates; Angels remain Review-only | Cast C12 |
| Preview | Reset selected cast workflow photos out of initial cores except explicitly manually protected photos; record releases and eligible highest-own-core replacement proposals without changing shared configuration | Cast C13 |
| Preview | Account for every one of the 35 old follow-ups with exact move/hold reasons; show new core evidence, refinement outcomes and post-continuity residuals; do not treat all 270 higher-rival rows as wrong placements | Engine E18/E19 |
| Preview | Inspect mixed Briar/Sammara photos individually with measured face/core coverage and routing sequence; no whole-Briar merge or unapproved Angel threshold change | Engine E19 |
| After install | Installed-run check, source/alias/destination count conservation and hash-bound final links; verify the reported Jade photo and its original intake comparison without obsolete-path warnings | Gallery L23, layout LY4 |
| After install | Gallery/Overview/Review load correctly, with matching counts, working thumbnails/detail/current-native links and no broken images; human review still owns placement/quality approval | Naming N15, layout LY4 |
| After install | Confirmed intentional unavailable framings are explained; missing/stale/corrupt expected derivatives remain actionable; no crop guard relaxation | Gallery L23 |
| Measured run | Record phase/wall timings, stage/read-reuse evidence, space layers and zero new backup/previous/rollback bytes; compare only equivalent scopes, retaining distinct raw originals and original reuse evidence | Layout LY14/LY15a |

Retiring external cast evidence can leave empty set directories. These are
not retained claims: enumeration ignores only a missing-manifest folder
verified empty, and an operation-local seal detects any new contents.
Nonempty folders with missing/invalid manifests still block processing;
this is not permission to hide damaged lineage or remove source folders.

Overview now shares retained/derivative verification between collection and
per-photo evidence within one operation, followed by the full content seal
before publication. Whole-history verification across Review and Overview
still repeats: gallery L18 remains open. Cross-page sharing needs dependency
and mutation invalidation tests; it is not bundled speculatively. Moving
away retained input evidence, derivative caps, FAST/detector shortcuts and
intake instrumentation remain deferred, not pickup prerequisites.

### Clean Production Source refresh and Working reset

The selected clean test uses this source chain:

```text
B:\Sovereign Territories                         read-only Production
    -> B:\Sovereign Territories Sandbox\Source   verified run baseline
    -> B:\Sovereign Territories Sandbox\Working  disposable execution/output
```

Old Working is contaminated test output, not a second source library.
Do not add its photos, prepared versions, catalogue memberships, cores or
caches to this rebase's active population. Normal incoming replacement/ID
handling is a separate flow; it does not make old experimental Working
authoritative for a clean test.

| Step | Required action | Exit evidence |
| --- | --- | --- |
| 1. Freeze the boundary | Stop or wait for exact root-specific library writers; resolve the Production, Source, Working and recovery paths. Preview managed categories and excluded operational storage. Artists remain outside this test unless separately selected. | No competing writers; explicit paths, exclusions and Production inventory. |
| 2. Account for old test state | Identify genuinely unique originals, explicit manual decisions and necessary recovery receipts before deleting obsolete outputs. Preserve only necessary material in a separately verified non-active recovery location outside the cleanup boundary; do not copy all Working into repository scratch or carry it into the test. | Exact preservation/disposition list and verified bytes/hashes. Old reports/caches/experimental outputs may be removed when verified disposable. |
| 3. Establish Source | Compare the existing Source and its manifest with the selected current Production scope. Reuse it only if it represents that exact baseline; otherwise stage a fresh Production copy and matching `source-manifest.json`, verify every listed file and publish the pair coherently. Freeze Source for the run. | Production origin, relative paths, lengths, SHA-256 values, source/manifest identity, scope exclusions and successful verification. |
| 4. Start clean Working | Preview the exact obsolete Working contents to remove, then replace managed contents from verified Source with checked staging/recovery. Keep the Working/Sandbox root directories; never use a broad root-recursive deletion. Do not retain old generated reports, caches, `_processing`, run staging or experimental catalogue state as active inputs. | Working baseline matches Source for the selected scope, with no undocumented carry-forward. Production and Source are unchanged. |
| 5. Prepare and run SIMPLE | Run the approved FULL/LEAN/FAST preparation and stable rebase composition on that fresh baseline. Record the profile, source/code/policy identities and real prepared-pixel measurements. Do not substitute legacy repeated refinement or experimental merges/appearances. | One input population from Source, one frozen consistency/refinement step, final rivals/family results and recoverable output publication. |
| 6. Verify before acceptance | Check input conservation, stable IDs/names/manual decisions, prepared/history bindings and actual Gallery/Overview/Review pages. | Explicit command exits/counts and loaded-page proof; human identity/image-quality acceptance remains distinct. |

Photo-source counts must come from the selected Source inventory. A combined
Production/old-Working diagnostic count is not the rebase input count; physical
copies, distinct byte versions and unique photo IDs must be reported separately.
An older Source snapshot may be internally valid yet differ from current
Production. Its age or existence alone does not establish suitability.

The user explicitly authorizes unattended clean Sandbox execution, including
discarding all old Working history and repeating intake from original inputs.
No old Working history is required in the new library. Production remains
read-only, and human identity/image-quality acceptance is not delegated.

The guarded baseline launcher implements steps 3-4:

```cmd
bin\sandbox-baseline.cmd --root "B:\Sovereign Territories Sandbox\Working" --dry-run
bin\sandbox-baseline.cmd --root "B:\Sovereign Territories Sandbox\Working" --run-id simple-clean-001 --apply
bin\sandbox-baseline.cmd --root "B:\Sovereign Territories Sandbox\Working" --run-id simple-clean-001 --check
```

Preview first and inspect `resetReady`, the exact replaced Working entries,
Source refresh/counts/exclusions and empty carry-forward. Apply stages and
verifies Production bytes, refreshes Source and its manifest together, then
uses the existing reset journal to build Working from verified Source with
explicit no-history mode. Its fixed OS-locked transaction and compact receipt
live outside Working under Sandbox `_baseline-state`; this is durable
baseline recovery evidence, not another active source library. It retains
neither old Working catalogue/history nor unique experimental photos. It
requires an existing valid Sandbox layout; it is not an arbitrary-directory
initialization/deletion command. Interrupted source publication rolls back;
an interrupted Working reset resumes the existing journal. Repeat apply with
the same run ID verifies the completed baseline rather than resetting twice.
Use a new run ID for a deliberately new baseline.

To replay an existing frozen Source instead of refreshing it, pass its
recorded `--frozen-source-sha256` and a new `--run-id` to
`bin\sandbox-baseline.cmd`. Start with `--dry-run`, then use the same arguments
for `--apply` and `--check`. This mode stages and verifies a Source copy,
preserves file modification times, and publishes it as Working. The prior
Working tree remains intact at `Working-before-<run-id>` (its absolute links
refer to the original Working path). Source and Production stay unchanged.
After an interruption during the switch, resume with the exact same apply
command; do not rename the staged or preserved roots by hand.

`--check` verifies the untouched baseline before intake, not a fully processed
library afterward. End-to-end SIMPLE output has its own check. Preserve each
baseline receipt's original implementation binding; a later helper change
does not authorize rewriting that receipt or resetting an installed baseline
solely to make its code hash current.

### Clean exact Various copies and replace approved originals before a rebase

Use `bin\various-cleanup.cmd` with the reviewed cleanup JSON and its SHA-256
on a matching raw copy of Production or Sandbox Working. The JSON uses
library-relative paths, so the drive can change. Preview first, close other
library writers, and run from the repository root:

```cmd
set "LIBRARY=B:\Sovereign Territories"
set "PLAN=C:\path\simple-run14-various-cleanup.json"
set "SHA=EXACT-PLAN-SHA256"
bin\various-cleanup.cmd --root "%LIBRARY%" --plan "%PLAN%" --sha256 "%SHA%" --dry-run
bin\various-cleanup.cmd --root "%LIBRARY%" --plan "%PLAN%" --sha256 "%SHA%" --apply --backup-confirmed
bin\various-cleanup.cmd --root "%LIBRARY%" --plan "%PLAN%" --sha256 "%SHA%" --check
```

Apply with `--backup-confirmed` only if the redundant incoming copies need
no additional backup. The command checks the old original and incoming
SHA-256 values before changes. It deletes only listed exact Various copies
and moves each approved different-byte version into the existing named
path. It moves the displaced original (without re-encoding) to
`_archive\various-cleanup\<plan-hash-prefix>` under its original relative
path. Protected cast placement and the photo's filename/ID are unchanged.
This tool refuses catalogue-managed roots rather than invalidating a
content-bound protection or retained preparation. Unlisted files are not
touched, and an ambiguous edit or mismatched hash stops preflight.

After an interruption, repeat the same apply command to finish with the
verified archive. Keep the sealed `Source` and its manifest unchanged;
apply against its Working copy, or create a new baseline from newly cleaned
Production using the normal baseline launcher. Existing rebase previews are
historical after cleanup; do not apply them against changed inputs.

For routine intake or rebase, scan the current library instead of supplying
the historical replacement plan. Save the JSON and its SHA-256 as the
discard record. Run this before preparation, backup, or rebase preview:

```cmd
bin\various-cleanup.cmd --root "%LIBRARY%" --scan-exact > "%PLAN%"
certutil -hashfile "%PLAN%" SHA256
```

Review the listed source and keeper paths, then use the same `--apply
--backup-confirmed` and `--check` commands above with that JSON and hash.
The exact-only scan works on raw or catalogue-managed libraries. It
matches stable ID and full bytes, and never backs up or archives a discarded
incoming file. A verified active file must remain; a pool-only group with
identical bytes keeps one incoming copy. Different bytes, different IDs,
ambiguous owners and incoming files with retained preparation or configured
selection stay for normal processing and review. A prepared native with
different current bytes is not an exact match and is handled by the
retained-lineage rules instead. Neither intake nor rebase silently discards
files: the preflight is a separate opt-in step.

### Stable whole-library SIMPLE preview, apply and check

Use `bin\normal-rebase.cmd` for step 5, not the legacy repeated-refinement
controller. It is an explicit whole-library operation; ordinary daily arrivals
continue through bounded `bin\library.cmd`. Consult the current pinned handoff
first and reuse its running job instead of starting another writer.

From the repository root, after the baseline gate and with no other writer:

```cmd
set "W=B:\Sovereign Territories Sandbox\Working"
set "RUN=simple-rebase-001"
set "POLICY=%CD%\data\art\likeness-engine-policy.json"
bin\normal-rebase.cmd --root "%W%" --cache "%W%\_likeness\general\cache.json" --policy "%POLICY%" --profile lean --run-id "%RUN%" --dry-run
```

Preview performs real preparation and measurement and writes root-local
sidecars, but does not publish assignments. FULL/LEAN prepare eligible named
references and candidates before freezing cores; FAST uses raw pixels and
explicitly defers editing, so it is not a substitute for fresh prepared-pixel
acceptance. Required model weights must already exist locally. Missing weights
fail explicitly; neither preview nor apply may download replacements.

A fresh FULL/LEAN rebase assesses eligible originals across the general
Gallery/Review domain, including established Angels and Sisters; no duplicate
submission is needed. It assesses one eligible source per logical input,
not every physical file. Archived duplicates, non-voting holds, and Artists
are outside this pass, and verified retained preparations can be reused.
Assessment can keep the original bytes if no edit passes the recipe.

SIMPLE treats untouched Review as eligible for ordinary candidate grouping
alongside new arrivals, not as a lock or as a vote for the previous owner.
Explicit Review placements, photo and workflow locks, and rejected matches
remain respected. This does not change cast admission priority or allow
automatic departures from an existing Angel or Sister Gallery.

SIMPLE reports two recoverable dispositions separately: safe distinct-ID
Various copies whose bytes match a keeper go to `_duplicates`; unbound
Various inputs with a decoded zero-face result go to `_junk/<original-path>`.
For `Various/gallery`, an exact match to a single keeper's verified retained
original also qualifies. The duplicate recap names both IDs and paths, and
distinguishes current keeper bytes from a verified retained original.
A failed measurement or ambiguous face quality is not a confirmed no-face
result. Same-ID, same-byte discard remains a separate opt-in preflight.
These changes do not expand daily intake scope.

For FULL/LEAN, a newly prepared same-path Review admission still publishes
the selected native and fresh preparation/history evidence; unchanged
ownership does not make it metadata-only. FAST and verified unprepared
retained-native admissions keep their membership-only behavior.
Retained manifest/detail transfers write the exact sealed UTF-8 bytes;
platform newline conversion must not invalidate their content checksums.

Inspect `_reports\runs\normal-rebase-RUN-preview.json` and its bound manifest:
every physical input needs a disposition, duplicate-content aliases cannot
cast extra votes, known names/true decisions must be preserved, and holds
must remain explicit. Review actual qualified cores, preparation coverage,
rivals and planned outputs. Keep Source, Working inputs, implementation,
configuration and policy frozen between preview and apply.

Once those gates pass, use the same run/profile/cache/policy:

```cmd
bin\normal-rebase.cmd --root "%W%" --cache "%W%\_likeness\general\cache.json" --policy "%POLICY%" --profile lean --run-id "%RUN%" --apply --sandbox-apply-draft
bin\normal-rebase.cmd --root "%W%" --run-id "%RUN%" --check
```

The draft-policy override is scoped to the authorized Sandbox, not Production.
Apply verifies preview/input/code bindings and reuses the complete preparation
manifest rather than preparing the whole library twice. If a custom preview
receipt was selected, pass its exact path with `--preview-receipt`. Applied
receipt is `_reports\runs\normal-rebase-RUN.json`; actual viewers are under
`_reports\library`. Open Gallery, Overview and Review and verify loaded images,
counts and native/detail/history/source links; file existence alone is not
GUI acceptance. Human identity and crop-quality approval remain separate.

`--repeat` checks an applied run without repeating mutations. For a genuine
partial publication, preserve the failure evidence first, inspect supported
`--recover`, and use `--recover-apply` only for its exact bound recovery.
Do not overwrite receipts, bypass changed-code bindings, reset Source or rerun
intake merely to repair a viewer/check failure. Real installed/viewer acceptance
remains open until the selected run supplies that evidence; legacy reset and
repeated-refinement commands below are not SIMPLE.

For an authorized Sandbox replay of prior journalled releases, add
`--release-receipt`, `--release-audit`, `--release-review` and one
`--release-run` per release in chronological order to both preview and apply.
Add `--reconsider-holds` to both preview and apply when the authorized rebase
must reassess prior Review holds and non-voting duplicate candidates. This
Sandbox-only option records prior explicit Review placements rather than
deleting user-action history. Explicitly accepted matches and current quality,
rejection, protection and independent-reference checks still apply.
The receipt, audit, checked final Review and complete release chain must verify
against the current Working state. Released photos enter ordinary matching
before identity formation; exact-content duplicates do not cast extra votes.
The source bindings, decisions and release lineage are bound to the preview.
These options are not valid for check or recovery and do not authorize
Production changes or workflow replacement.

For an authorized fresh post-intake Sandbox baseline, use
`--fresh-source-release` on both preview and apply instead of the historical
release-lineage options. It assesses initial named Gallery members against
independent own-identity evidence, selects red, orange and unscored members,
and retires selected source authority before freezing cores and matching.
It also enables hold reconsideration. Evidence and selections are bound to
the preview; duplicate content, including byte-identical prepared natives,
gets one reference vote. A descriptive filename binds only through its
inventory-verified standard name. A released photo without an unambiguous
placement goes to its highest-scoring eligible rival's Review. If the photo
fails the single-face quality gate or has no eligible rival, it goes to
Various Review. Review adds no reference vote. Stale rejection evidence or
an explicit user Review placement still stops the run. Admission moves
without a reference version fail at preview. First verified on the Sandbox
as `fresh-post-intake-20261122-04`.

#### Settle passes and intake small-Potential release

Every SIMPLE rebase with normal two-round admission then runs bounded settle
passes before publication (`identityActions.settlePassMaximum`, default 3;
0 disables). Each pass rebuilds every identity from its final planned
Gallery members, existing and admitted. Match-only dominant-face photos,
non-voters, optimistic cast placements and Review placements never vote, and
duplicate content gets one vote. Each planned Gallery member is rescored
against its identity's other voters (leave-one-out). Red and orange members
are released and rematched together through the shared planner against the
identities rebuilt without them: an existing Gallery or Review, a
band-aligned new identity, the single-photo gate, or else the highest
rival's Review or Various Review. An identity this run reduced to one photo
follows the single-photo rule. Passes stop when a pass moves nothing.

Photos the run placed can be released unless a protection, explicit Review
placement or stale rejection exempts them. Original named-Gallery members
that stayed in place are releasable only with `--fresh-source-release`, whose
release already covers every bindable named-Gallery member. Such a member
joins the bound release cohort with its source path and SHA-256, so its
membership and anchors are retired and the release permission override
covers its move. When the opt-in cast seed is enabled
(`castAdmission.seedEnabled`, default false), its top-N seeds stay exempt.
Settle releases only red and orange members; yellow members stay, and the
user rejects any that belong elsewhere. In any other rebase original
members are scored and reported, never released. Members still red or
orange after the last pass are listed
as "did not settle". Each pass records a `settle-pass-N` phase with its
timing, released, moved and still-flagged counts. The recap adds "Settle
passes" and "Did not settle" sections. The settle evidence and resulting
decisions are fingerprinted, and apply refuses a changed outcome.

Normal intake (`bin\library.cmd`) first releases existing Potentials with at
most `identityActions.intakeReleasePotentialMaxPhotos` Gallery photos
(default 1; 0 disables). Protected Potentials and those holding a protected,
anchored, workflow-selected or update-target photo are skipped and reported.
Released Potentials lend no core. Their photos are rescored with the
incoming batch and may move to another identity's Gallery or a rival's
Review (single-photo gate). A new group that contains them joins the
Potential holding most of its released photos instead of forming another
identity, which merges matching arrivals and other released Potentials into
it. Otherwise a photo stays where it is. The plan records each outcome, the
emptied Galleries and the selection, shared routing and resolution timings.
Emptied identity folders are retired inside the intake transaction (see
below). Previews remain read-only.

#### Recoverable retirement of emptied identity folders

Retirement is automatic inside SIMPLE rebase (`bin\normal-rebase.cmd`) and
normal intake (`bin\library.cmd`). The preview lists each Models, Prospects
or Potentials folder that would keep no `gallery` or `review` original after
the planned moves. Derivative folders such as `944x1104` do not count and
move with the folder. The rebase preview binds this list in
`emptiedIdentityFingerprint`, and apply refuses a different list. Intake has
no saved preview, so its apply recomputes the list from the final checked
moves.

Apply moves each listed folder intact to the configured `retired` storage
(`_retired\<Category>\<Name>`) after the photos move and before the viewers
are rebuilt. The Gallery, Overview and Review viewers therefore no longer
list those identities. Each rename is one journalled step in the run's
existing publication journal (`retiredFolders`), together with the folder's
exact inventory. This keeps a single recovery point: `--recover-apply` (rebase) or
`--undo --apply` and `--recover --apply` (intake) move the folder back first,
then restore the photos. If the folder changed after retirement, recovery
stops for inspection. An existing retired destination, or an original that
is still in the folder when the rename runs, stops the run, which then
rolls back. Nothing is deleted.

The applied receipt records `retiredIdentityFolders`. `--check` (rebase) and
`library.cmd --check --run-id` (intake) verify that each folder is at its
retired location and absent from its source. The rebase recap section
"Emptied identities retired" links each retired folder and lists the photos
that left it. In both flows, the catalogue keeps the emptied person record
with no member photos; moved photos record the former person in
`sourcePersonIds`.

A Sisters or Angels folder is never retired automatically. If a run would
empty one, the preview and apply stop with a report listing the folder and
the photos that would leave it.

`bin\retire-empty.cmd` stays available for manual catch-up. Use it to retire
folders emptied by an applied rebase that ran before this behaviour existed,
again as a journalled and recoverable Sandbox transaction. The legacy
`likeness.cmd retire-empty` is a direct move with no journal or recovery.

```cmd
set "RECEIPT=_reports\runs\normal-rebase-RUN.json"
bin\retire-empty.cmd --root "%W%" --receipt "%RECEIPT%" --run-id RID
bin\retire-empty.cmd --root "%W%" --receipt "%RECEIPT%" --run-id RID --apply
bin\retire-empty.cmd --root "%W%" --run-id RID --check
bin\retire-empty.cmd --root "%W%" --run-id RID --recover
bin\retire-empty.cmd --root "%W%" --run-id RID --recover-apply
```

The preview (default, or `--dry-run`) reads the receipt's source-row owners
and lists those Angels, Sisters, Models, Prospects or Potentials folders that
now have no `gallery` or `review` image. It saves the plan and its digest as
a new `_reports\runs\empty-retirement-RID-preview.json`; nothing moves.
`--folder CATEGORY/Name` (repeatable) narrows the selection to discovered
folders. `--apply` publishes exactly that saved plan to the journal
`_reports\runs\empty-retirement-RID.json`, then checks it. A changed folder,
receipt or predecessor publication journal makes the plan stale and stops
before any move; run a new preview with a new run ID. `--check` verifies the
applied journal. `--recover` previews exact recovery and `--recover-apply`
moves the intact folders back.

Safety rules: the root must be the Sandbox Working folder; Production is
refused. An existing plan or journal is never overwritten. An emptied
Sisters or Angels folder stops the command with a report (exit code 3); cast
folders are never retired automatically. Stop other library writers first.
Folders are moved intact under the configured `_retired` storage; pruning
retired folders stays manual.

#### Saved SIMPLE movement recap and placement audit

For an applied receipt followed by Sandbox releases, use the separate
per-source movement history. Supply the original bound audit, the final
reports-only Review directory and **every** release ID in chronological order:

```cmd
bin\movement-history.cmd --root "%W%" --receipt "%RECEIPT%" --audit "%AUDIT%" --current-review "%FINAL_REVIEW%" --report-id HISTORY_ID --release FIRST --release NEXT --dry-run
bin\movement-history.cmd --root "%W%" --receipt "%RECEIPT%" --audit "%AUDIT%" --current-review "%FINAL_REVIEW%" --report-id HISTORY_ID --release FIRST --release NEXT --apply
bin\movement-history.cmd --root "%W%" --receipt "%RECEIPT%" --audit "%AUDIT%" --current-review "%FINAL_REVIEW%" --report-id HISTORY_ID --release FIRST --release NEXT --check
```

Repeat `--release` for each release; the example is not the current run list.
Preview and check are read-only. Apply creates only a new
`_reports\library\movement-history\HISTORY_ID` report; an identical repeat is
safe, and different or incomplete existing evidence is refused. It verifies
the original receipt/audit, release journals and historical snapshots, and
the final Review census; missing, ambiguous, incomplete or changed lineage
stops the report. It does not repair or bypass a failed chain. Every physical
source row is shown; archive, alias and superseded rows are not presented as
additional current photos. Images are linked only at their exact recorded
paths when their bytes match; missing or changed historical images are
explicit, not replaced by a current image. Image states are as of report
generation and browser loading is a separate check. This is not human identity
acceptance or permission to move photos.
The history records what happened, not the intended routing: released photos
are to be reconsidered as normal candidates at the start of a rebase, and
recorded Review holds do not establish intended placements. A missing
continuation binding is accepted only when a later verified continuation
explicitly binds the entire preceding journal sequence.

To attempt to extend this history after a corrected rebase is applied, add
`--corrected-receipt "APPLIED-RECEIPT.json"` to each command. The required
cohort is derived from distinct verified released photo IDs; optionally add
`--expected-cohort COUNT` to reject a different count. The current historical
preview observed 219 distinct released photos; this is not a generic default.
The corrected receipt and
journal must pass their existing applied check, and every cohort photo must
match exactly by last released path, photo ID and source hash, with a bound
publication and recovery snapshot. Unmatched non-cohort source rows remain
visible without an inferred placement. Ambiguous IDs or changed cohort bytes
stop the report. The original full release-chain checks remain mandatory:
for paths the verified successor overwrote or removed, they use its
hash-bound recovery snapshot; untouched paths are checked live. Missing,
ambiguous, unrelated or changed successor evidence stops verification.
For a checked, explicit retirement following that rebase, also supply
`--retirement-journal WORKING_RELATIVE_PATH --retirement-digest PREVIEW_SHA256`
to each command. The bound retirement journal, folder inventory and predecessor
are verified; this does not authorize or perform retirement. Other subsequent
transactions remain unsupported. Retirement-aware history is fixture-tested,
not yet verified against an installed corrected rebase. Existing reports retain
their original producer hashes; after implementation changes use a new report
ID rather than overwriting old evidence.

Normal preview/applied receipts now publish report-only recap/audit pages
under `_reports\library\rebase-recap` for previews and its `applied`
subdirectory for applied receipts. Each directory has its own index:
post-transaction reporting must not overwrite preview artifacts sealed by
publication. Do not regenerate sealed historical previews in place; use
`--out` to select a separate report path if new rendering is needed.
The movement recap lists ordered phases and their purposes, recorded counts
and measured elapsed seconds. Reused preparation reports only current reuse
verification time, not its historical preparation time. Publication timing
ends after the transaction, viewers and cache save; receipt and recap writing
are excluded. Preview publication remains apply-only. Older receipts without
timings display them as unavailable rather than estimating them.
To reconnect an older saved run
without preparing, matching or moving anything:

```cmd
set "RECEIPT=%W%\_reports\runs\normal-rebase-RUN.json"
bin\rebase-recap.cmd "%RECEIPT%" --dry-run
bin\rebase-recap.cmd "%RECEIPT%" --apply
bin\rebase-recap.cmd "%RECEIPT%" --check
bin\rebase-recap.cmd "%RECEIPT%" --compare "OTHER-SAVED-RECEIPT.json" --apply
```

Default is preview; menu option `RR` also previews before offering report
publication. `--compare` requires identical frozen source paths/hashes.
The directory index links each run's recap and audit. Checks bind receipt/
Review bytes, report producers, exact recap/audit outputs and this run's
index navigation. Missing/stale saved evidence stays explicit.
Each recap conserves physical source rows, distinguishing exact-alias
coalescences, strictly bound incoming native replacements and distinct
current destinations. Superseded native versions remain visible as history,
not extra current members or borrowers of the replacement's Review evidence.
Review links open separate
tabs; section anchors remain local and per-photo audit links reveal hidden
nonfinding rows. Reports use existing cached thumbnails only.

Audit findings combine recorded consistency evidence with a path/native-
hash-bound **saved** Review snapshot; they are not fresh inference, an
exhaustive final-refinement pass or authorization to move members. Group/
core similarities are not individual admission scores. Missing Review IDs
are disclosed and paired only by exact path/native hash; conflicting IDs
refuse pairing. Current-photo links do not certify freshly rehashed bytes.
An applied receipt survives later report failure: use this report-only
repair path, never repeat publication or reset the library.

If preparation completed but the whole preview failed, use a new run ID and
explicitly select the old preparation output and its preserved manifest hash:

```cmd
set "PREP=%W%\_reports\runs\normal-rebase-PRIOR-preview\preparation\inputs\_reports\preparation\selected"
set "PREP_SHA=EXACT-PRESERVED-MANIFEST-SHA256"
bin\normal-rebase.cmd --root "%W%" --cache "%W%\_likeness\general\cache.json" --policy "%POLICY%" --profile lean --run-id "%RUN%" --reuse-preparation "%PREP%" --reuse-preparation-sha256 "%PREP_SHA%" --dry-run
```

Reuse verifies containment, profile, recipe, configuration, every original
source/hash and every required artifact in the complete parent preparation.
If corrected source-ID classification selects fewer inputs, explicit external
reuse may select a byte-verified subset. A newly selected physical alias may
reuse a prepared source only with the same full original SHA-256 and one
unambiguous selected-native hash. The receipt separately binds selected inputs,
unused verified inputs and source aliases; the parent manifest and historical
rows are not rewritten. Normal same-run reuse remains exact by default.
Apply revalidates the new preview and these bindings; reuse never approves an
old failed preview.

A clean rebase may select a pool original whose byte-identical same-ID alias
already occupies the planned identity destination. The preview explicitly
records these `exactAliasTargets`. Only that source/target/full-hash binding
permits replacement; other existing destinations still fail closed. Apply
rechecks both files and retains both pre-publication paths in its transaction
backup. This coalesces a physical alias, not a logical photo or a different
version. Source conservation reports the coalesced target count separately.

A Various original whose full source SHA-256 matches the verified retained
original of the one catalogue-bound prepared Gallery native is not a new
incoming version merely because preparation changed its current pixels.
Preserve that original as an explicit non-voting version and keep the
prepared native as the canonical input. Do not prepare it again, replace
its sound owner or count it as another independent reference. These
preserved physical originals are not newly unmatched logical identities.
A genuine different incoming version still requires accepted version
selection and exact old/new source, destination and hash bindings; it is
not authorized by the exact-byte-alias collision exception.

Ordinary selected intake makes this distinction before incoming version
selection and preparation too. Such originals stay preserved even beside a
genuinely newer arrival; transaction and receipt checks bind their bytes and
the verified current-owner/retained lineage rather than routing or archiving
them as new photos.

The single low-member audit distinguishes a Review recommendation from
permission to remove an existing Gallery member. Protected identities and
categories with automatic splitting disabled keep those photos in Gallery;
the receipt records recommendation-only evidence. Unprotected, permitted
corrections still route to Review. Preview checks publication permissions
before approving its plan; apply checks them again without relaxing policy.

New generation records exclusive `preparation-origin.start.json` before
preparation and a matching completion seal afterward; changed producer code
or an incomplete/mismatched pair fails closed. Older preparation may have
sealed input/output/recipe/configuration without recording its generator-code
hash. Selected legacy reuse reports that generation hash as unknown and keeps
the current validation-code hash separate. This provenance exception is
visible; it never waives source/artifact checks or human image-quality review.

### Fresh sandbox from production: step by step

**Legacy procedure, not the selected SIMPLE clean test.** These existing
commands are retained to explain historical runs and recovery. Their
Production-to-Working reset with unique-photo carry-forward does not establish
the freshly verified Source/no-old-Working boundary above. Do not execute this
table as the next clean acceptance run.

The FULL-recovery procedure for a new end-to-end rehearsal. For an explicitly
disposable sandbox LEAN run, the timed launcher's `--recovery-mode disposable`
skips originals/baseline backup and creates no transaction rollback; recover
only by a new reset. `W` stands for
`"B:\Sovereign Territories Sandbox\Working"` and `RUN` for
`"B:\Sovereign Territories Sandbox\Working\_sandbox-state\<new run name>"`.
**Always pass `--root W`**: without it `originals`, `library-backup` and the
gallery launchers act on production. Every step previews first. Keep Acronis
off (or the library excluded) during the long steps. Production is only read.

| # | Command (preview, then apply) | What it does | Copies in the sandbox afterwards |
| --- | --- | --- | --- |
| 1 | `bin\likeness.cmd --root W sandbox-reset --full`, then add `--apply` once `resetReady: true` | Replaces Working with a verified copy of production, without `Artists`. Unique sandbox photos stay; unique metadata goes to `_reports\reset-review-bundle` | One copy of production people: person `gallery`/`review` (plus former `gallery_944x1104`/`headshot_944x1104`), `_junk`, `_retired`, the bundle. Old sandbox backups, runs and reports are gone |
| 2 | `bin\originals.cmd --root W --no-repoint --dry-run`, then without `--dry-run` | Moves legacy scaled folders into `<person>\944x1104` and fills maintained-copy gaps. `--check` must say IN SYNC. `--no-repoint` preserves the shared workflow configuration during this isolated rehearsal | Existing copies move by rename; missing maintained copies are generated |
| 3 | `bin\library-backup.cmd --root W`, then `--apply` | Dated LEAN snapshot in `W\_backup` (derivatives omitted, regenerable) | Production photos twice: live and `_backup` |
| 4 | `bin\sandbox-rebase.cmd W RUN --baseline working --cast-seeds core --record-core-protection --dry-run` | Read-only inventory of the newly reset Production inputs; the flags bind approved core-only rebase behavior | Unchanged |
| 5 | Same with `--intake-only --apply` (timed log, see below), then `--check` | Freezes the inputs and prepares every photo (control, geometry, padding, masks) | Plus `RUN\inputs` (frozen input mirror) and `RUN\...\preparation` evidence |
| 6 | Same without flags (matched preview), then `--preserve-legacy-derivatives --apply`, then plain `--check` (after install the flag is refused: it selects the unpublished-plan recovery preview) | Matches and installs: people get `gallery`/`review`/`944x1104`; LEAN processing history goes to `W\_processing\<person path>\<set-key>`; the replaced categories go to `RUN\previous` for `--undo`. The flag is expected on a fresh copy: production's scaled copies collide with the regenerated ones and are journalled byte-for-byte into `RUN\previous\external` | Plus `_processing` (LEAN) and `RUN\previous` (the pre-install categories and replaced scaled copies) |
| 7 | `bin\people-gallery.cmd --root W --cache RUN\likeness-cache.json --policy RUN\policy.json --check`; the recap is automatic | Install publishes both Gallery/Overview and Review through shared report-state publication. Every successful matched `sandbox-rebase.cmd` step also rewrites the recap and run index; inventory/intake-only steps do not. Check with this run's explicit local cache/policy, then open the actual pages. **Looks like** picks save `rebase-expectations.json` beside Working (survives resets) | Plus viewer thumbnails, report-state receipt and recap pages under `_reports`; the expectations file beside Working |
| 8 | After acceptance only: storage retention for `RUN\previous`, staged and `inputs`, and the step-3 backup | Leaves one live library plus `_processing` and a new backup | Back to about one copy plus LEAN history |

Each person folder then contains only `gallery` (with its `z_<name>.txt`
profile), `review` (when needed) and `944x1104`. A person with old `gallery_org` or
`gallery_intake` folders means the reset was skipped; the rebase refuses that
layout. `--undo` at step 6 restores exactly the step-5 state. Use one run name
per rehearsal and record the per-step durations from the logs in the owning
plan.

For the approved core trial, keep all three run flags on every step. In a
Command Prompt, after completing reset, originals and backup above:

```bat
set "W=B:\Sovereign Territories Sandbox\Working"
set "RUN=%W%\_sandbox-state\fresh-20261103-core"
set "CORE=--baseline working --cast-seeds core --record-core-protection"
bin\sandbox-rebase.cmd "%W%" "%RUN%" %CORE% --dry-run
bin\sandbox-rebase.cmd "%W%" "%RUN%" %CORE% --intake-only --apply --workers 4
bin\sandbox-rebase.cmd "%W%" "%RUN%" %CORE% --intake-only --check
bin\sandbox-rebase.cmd "%W%" "%RUN%" %CORE%
bin\sandbox-rebase.cmd "%W%" "%RUN%" %CORE% --preserve-legacy-derivatives --apply
bin\sandbox-rebase.cmd "%W%" "%RUN%" %CORE% --check
bin\people-gallery.cmd --root "%W%" --cache "%RUN%\likeness-cache.json" --policy "%RUN%\policy.json" --check
```

Do not run the apply line until the saved matched preview has been audited.
Keep `--no-repoint` on sandbox originals steps; refresh chosen workflow inputs
only through their separately reviewed command, never against this rehearsal.
`--baseline working` here means the **freshly reset Production copy**, not
the previous rebase's output. The reset excludes verified processed copies
whose originals remain in Production; genuinely unique sandbox photos and
metadata are preserved through the documented reset bundle. Check the exact
carry-forward inventory before applying reset.

`--record-core-protection` requires `--cast-seeds core`. It records a distinct
run-local policy with inclusive minima Angels/Sisters 0.40, Models 0.50,
Prospects 0.60, and no automatic Potential locks. Identity/slot protection
does not freeze every source photo in this explicit mode. Photo locks,
anchors, workflow selections, rejects and manual opt-outs remain binding;
complete verified identity merges retain oldest-original name continuity.
Independent leave-one-out support, quality and rival gates still apply, and
their holds are shown rather than treating a category score as proof.
Ordinary defaults and all-seeds runs are unchanged.

Matching uses frozen initial cast and provisional grouping references. A
bounded in-place refinement (engine E15) then runs inside the plan before
naming, so install, undo, history and the recap all use its result. Each pass
freezes provisional cluster cores and fixed cast cores and:

- moves an unlocked photo only when the normal `auto-route` gate passes for
  another cluster; a cast lookalike goes to that cast's `review` folder only;
- attaches held `Various\review` rows to a cluster under the same gate;
- merges a reciprocal-best pair of clusters when similarity reaches the
  survivor category's merge minimum with the route margin and every loser
  photo meets the route minimum; the larger cluster survives and naming keeps
  the oldest original name;
- reclassifies changed clusters (Potentials/Prospects/Review) and dissolves
  a cluster that no longer qualifies.

Category-protected cores, anchors, workflow inputs and rejection history are
frozen; a merge is refused while the loser holds them. Passes stop when
stable or after four, and oscillations are reported unresolved. The plan's
`membershipRefinement` and the recap's refinement section list every move,
merge and unresolved case.

In the explicit core-protection trial, an additional photo-only
`finalMembershipRefinement` pass uses the audit's `frozen_identity_cores`
recipe, leave-one-out own scores and all same-domain rivals. It includes
retained cast and preserved/Review rows, with an explicit admission or hold
reason; meeting a category's own-score minimum is not an early exit.
No new protection is acquired during these comparisons. Destination evidence
must meet the existing independent-reference, quality, rejection and route
gates. Cast gains still enter Review, not Gallery; the separate approved
Sisters auto-admission change is not implemented by this pass.

Each frozen pass applies simultaneous moves, then rebuilds references.
Four passes maximum, visited-membership oscillation holds, filename-collision
refusal and per-photo residual reasons bound the operation. Name/family
selection follows the changed membership. After continuity migration, a fresh
comparison identifies any newly qualifying residuals before protection;
these cannot acquire automatic protection and block installation until a
resolved preview is reviewed. The recap shows this separately from the
earlier provisional refinement. This does not claim global convergence or
approve a mixed identity's whole-cluster transfer.

A separate final-membership audit then compares each eligible Gallery photo
with its final own core (leave-one-out for core members) and the top three
rivals. It records protection/support/quality evidence, higher-rival flags
and margin-qualified follow-up candidates. The recap labels those scores
separately from initial photo/cluster scores and links recorded top-ten cast
core references. **The audit itself applies no moves and does not claim
convergence; it reports what refinement left.** A higher rival score can
reveal a mixed cluster, but can also reflect genuine relatives/lookalikes.

New prepared rebase previews recognize standard download IDs and give
non-standard non-cast files the existing content-derived `pic_<8 hex>` ID.
Only final destination filenames are normalized; frozen inputs and original
recovery paths stay unchanged. Exact byte copies do not become independent
matching candidates: they are held under distinct `various_duplicate_*` names
with an explicit canonical-source reason. Different bytes claiming the same
content-derived ID refuse rather than overwrite or silently merge. Existing
installed runs are not renamed by this change; their saved outcome maps remain
the review baseline.

## People Gallery and Review Gallery

Preview with `bin\people-gallery.cmd --dry-run`, then use `--apply` to
maintain folder-prefixed originals and standard derivatives and create both pages in
the same report directory. Both are standalone local HTML pages; no server or
network access is needed to view them. The
[post-action maintenance runbook](original-photos.md#post-action-gallery-maintenance-no-matching)
owns the read-only check, sandbox syntax and explicit action-undo settlement
gate. Use the Review-only launcher when preserving an active undo window.

### People Gallery: relationships and overview

The overview shows up to nine photos per person, ordered by core identity or
score. A relationship name opens that person in Review; its adjacent
score-colored marker jumps to that person within the overview. The page
surfaces closest category matches, Angel/Sister pairings, eligible Prospect
alternatives, and full rankings on demand. The score legend is display-only.

The category tags follow the general library hierarchy: Sisters, Angels, Models,
Prospects and Potentials. Artists have their own browser. The card tags identify category,
workflow selection, photo count, and history. Angel and Sister cards show
their recorded `Person:` name when available. A linked Workflow photo shows
its likeness score; an otherwise hidden workflow original is pinned last
with a dashed border, as described below.
An amber `in review` badge follows the photo count and opens that person's
Review-only filter. Its color means Review, not a new count/quality threshold.
Potentials, Prospects and Models also show descriptive card-use guidance; it
does not assign cards, change rarity rules or affect identity matching.

Prime-start suitability is a photo-quality measure, separate from identity
likeness. Head and Chest-up framing use cached thumbnails. The page is intended
for relationship analysis, not full-library photo actions.

### Review Gallery: full library and staged actions

Run `bin\people-gallery-review.cmd` when only the full review page is needed.
It shows every Gallery and Review photo with category/person filters, a review
queue, low-score view, flat view, selectable ordering, and cached thumbnails.
The person's workflow photo, identity anchor, or provisional reference stays
visible even if filters hide it.

For a history-only repair, use the same launcher with `--root "<library>"`
and `--history-only --dry-run`, then `--history-only --apply` and
`--history-only --check`. This verifies saved preparation artifacts and
atomically replaces `intake_runs.html` and updates its report-ownership receipt;
it does not rebuild photo viewers,
thumbnails, matching, or intake. Preview is the default in this mode.
Preparation manifests remain bounded to 64 MiB, 5,000 rows per run and
32 discovered runs; oversized or tampered evidence stays explicitly unverified.
The former 8 MiB ceiling rejected the actual 49,709,196-byte v23 manifest,
leaving a run label with zero photos. Check verified photo counts and detail
links, not just the presence of the run name.

Report generation reuses retained/derivative verification only within an
explicit operation. Before page publication, it rechecks the owner-directory
membership, linked/reparse-path guards and **full SHA-256 of every recorded
input**; original size/mtime alone never authorizes reuse. A failed final
check refuses the page update. Review/Overview evidence and thumbnails share
this mechanism; standalone checks and source-changing maintenance do not use
it. History still audits every declared artifact and current mirror source;
the duplicate staged-input hash prepass is removed, not the full audit.
Progress output identifies the input and final-seal phases and their read counts.
Do not run source-changing commands concurrently: these are full before/after
content checks, not a filesystem lock or an immutable-snapshot guarantee.

For an isolated report-only comparison while reviewing the installed baseline:

```powershell
cmd /c bin\people-gallery-review.cmd --root "B:\Sovereign Territories Sandbox\Working" --cache "B:\Sovereign Territories Sandbox\Working\_sandbox-state\fresh-v23-20261029\likeness-cache.json" --policy "B:\Sovereign Territories Sandbox\Working\_sandbox-state\fresh-v23-20261029\policy.json" --out library-performance-20261031 --no-renders
```

This writes a separate report/thumbnail cache under configured reports, not a
new intake or rebase. Use a new output name for another comparison; the existing
installed pages remain the human-review baseline. Whole-run history verification
still runs and can be slow; bounded timings are not full-run speedup estimates.
The report includes the existing aligned-face and retained-detail links.
This isolated output contains Review/history only: its local Overview target is
not generated. Use the existing installed Overview rather than treating this
comparison folder as a new complete gallery publication.

In grouped views the header has separate **Reference photo**, **Identity details**
and **Manual actions** panels. The read-only reference stays visible even when
the same photo is in the grid; only the grid copy has photo staging controls.
Details distinguish recorded person name, fixed cast slot (where applicable),
stable identity ID, core size/mode, full-report counts and currently shown counts.
Unavailable recorded-name snapshots are labelled, never inferred from a slot name.
Closest-category evidence and full rankings stay in Details. Actions retain the
existing confirmation, conflict, download and separate CLI validation behavior.
Panels stack on narrow screens. Full profile/history/overview-stat parity remains
unfinished; historical reports acquire this layout only on a supported refresh.

**Grouping** is independent of Location and Order. Mixed (the default) keeps
the existing combined ordering; Split Gallery / Review places the currently
shown photos in labelled location groups within each person, or in two groups
for the flat view. Each group retains the selected order. Pagination still
adds at most 100 photos at a time; group headings say how many are currently
shown, not the person's full library count. Review cards have an amber left
border as well as their explicit Review badge. Changing grouping or filters
does not clear staged actions.

For **Move to another identity's Review**, choose Destination category first,
then Destination identity. The closest eligible existing target stays
preselected, even when it belongs to another category. Only catalogued
destinations in the supported general categories are listed; the source
identity is excluded. The exported folder and stable person ID are unchanged
by shorter option labels. Existing protection/rename conflicts still refuse
staging; a refused destination change restores the prior selection. Choosing
a destination stages a proposal only, not a file move or approval.

### Preparation evidence: what happened and why

People overview/Review and the separate Artist browser can show preparation
comparison evidence without running intake. Each photo's current source
path/hash, available stable photo ID and general/artist scope are checked
against bounded existing reports. A verified entry links directly to its
per-image comparison trace and shows recipe, cleanup decision and explanation.
Artists never borrow preparation evidence from general or another artist's
scope. Existing standard derivative links remain separate from native-source
cleanup comparisons.

One checked run offers **Open intake detail** directly; multiple exact runs offer
**N intake runs**, opening a separate run browser scoped to that exact source
path and hash, rather than an expanding list. **Intake runs** in the gallery
navigation opens the whole domain's history. Select a run from the run list,
search names/recipes/source filenames, filter by recipe or verification state,
then filter its photos. A source-scoped run list still shows all photos in the
selected run, marks the linked photo, and offers **Linked photo only** for focused
comparison. Photos display 60 at a time with **Show next 60 photos**.
Run URLs retain the selected run; the source-scoped page has a link back to all
photos' history. No run is ranked as best or accepted.

Each verified historical entry opens its original run overview (only when the
entire run belongs to the current domain) and individual photo traces.
The destination shows retained input, crops, masks, skipped steps
and recommendation in that recipe's recorded order. People and Artist Review
share this evidence renderer; Overview lists evidence for its displayed photos.
Artist overview opens the group's photo browser for individual detail links.
These features appear on supported report regeneration, not retroactively in old
HTML. The prepared installer now supplies verified post-assignment lineage
through owner-local retained sets; older unlinked reports do not acquire it.

The history browser checks all discovered runs independently, including runs
beyond the continuity index's global 32-run/5,000-row budget. Each run still has
an 8 MiB manifest / 5,000-photo safety budget. Unverifiable or oversized runs
remain named with an explicit diagnostic and no report links. This independent
historical-artifact check does not assert current-source continuity or relax the
gallery's fail-closed evidence rules. Artist/general photo scopes remain separate.
Large histories still require reading and checking retained artifacts during
regeneration; the UI's search and paged rendering do not eliminate that I/O.
Browsing never prunes runs or regenerates images. Retention/pruning policy is
still to be agreed; historical experiments are not the accepted retained set.

| State | Meaning |
| --- | --- |
| Verified | Exactly one checked trace matches current source evidence; this does not mean its recommendation was applied |
| Ambiguous | Several checked runs match; all verified alternatives are offered without inventing a latest/best winner |
| Stale | Recorded source evidence no longer matches; do not treat that comparison as current |
| Unverified | Evidence could not be fully checked or discovery limits/errors prevent a safe claim; links are withheld |
| Missing | No matching preparation evidence is available; this is not proof of a clean image |

The bridge does not guess continuity after a rename/move from a basename or
identical bytes alone. Checked retained manifests now bridge exact current
native path/hash, stable photo ID and domain to original/selected/kept variants,
with gallery/run/maintained-derivative return navigation. Supported individual
photo actions and same-owner normalization transfer that lineage; overlapping
whole-identity moves hold explicitly. Real end-to-end visual acceptance remains open.
Opening a trace never processes, replaces, approves or assigns a photo.
An original retained by a comparison may already have been cropped; it is not
automatically a pristine camera source. The index is built once per report
render and caches source hashes, but full verification of large existing runs
can add substantial I/O (about 99 seconds in the current saved-evidence preview).
No second image library is created for the bridge.

Historical sandbox preview pages disable staged actions and warn that their
evidence is not current action authority. Use supported current reports and
fresh CLI validation for actual staged decisions; previews do not authorize apply.

### Identity and photo evidence

#### Automatic protection and original names

Draft policy `draft-2026-10-25.1` adds automatic protection to explicit
legacy-reconcile previews and its existing apply/undo transaction.
It does not enable production use of a draft policy. Run `bin\likeness.cmd policy`
to inspect the effective settings; existing sandbox root/cache and draft-apply
guards still apply.

- A qualifying Gallery photo needs own-core similarity **at least 0.55**, a rival
  lead **at least 0.10**, and **four independent other core observations**.
  Its own image, identical bytes and near-duplicate references do not certify it.
- **Five independently qualifying Gallery observations** establish an unprotected
  identity. The identity and qualifying photos are protected, not every file.
  An already protected identity can acquire qualifying photo locks without
  requiring all its photos to qualify.
- Review, rejected, stale, ambiguous, multi-face and membership-changing evidence
  is held with reasons. A membership change needs a fresh subsequent reconcile;
  it is not certified using the old frozen core in the same pass.
- Explicit **Unprotect** disables auto-protection persistently for that item;
  a person opt-out also suppresses new automatic photo locks within it. Existing
  photo/workflow locks are not removed in bulk. Explicit **Protect** re-enables
  the item. Action undo restores the prior lock/provenance/override.
- Automatic locks preserve previously eligible core status, without creating
  anchors or making a previously excluded photo into reference truth. Manual
  protection remains a separate membership guard.

Automatic organizational-family naming uses at least five independent current
core photos per identity. New pairs must be reciprocal direct references with a
0.05 lead over alternatives; the automatic band is **0.40 inclusive** to
**min(0.55, either category's merge threshold) exclusive**. Existing-family joins
need direct evidence to the founder; no transitive surname matching. Possible
same-person matches, collisions and uncertain evidence are held.

Families are catalogue metadata, not biological claims or physical directories.
They preserve first names and change only the catalogue current-person surname;
fixed cast folders, workflow keys, source filenames and history files are not
retargeted. The gallery shows **character name**, **current person name** and
**original person name** separately, including original-name provenance and
family/protection explanations. Missing original names are explicitly unavailable.
Manual rename/swap preserves original names; reconciliation undo restores exact
prior names/family metadata. The read-only family preview remains diagnostic.

These are conservative configurable working defaults, **not calibrated accuracy
claims**. No real library is changed by generating a report. The reconcile JSON
contains `metadataActions`, `protectionEvidence` and `familyEvidence`; metadata-only
changes use the same backup, stale-state checks and journal as file moves.
The intake-aware sandbox rebuild migrates manual override/name/family provenance
only through verified one-to-one stable-ID continuity after matching. Ambiguous
destinations refuse rather than discard or guess those decisions. Legacy
matcher-only previews cannot install. Ordinary incremental reconciliation
retains the same decisions.

The person heading displays the name separately from category and photo
location. Each usable photo shows both its leave-one-out similarity to its
current identity core and its three closest other same-side identity cores,
ranked by that photo's own unrounded similarity (category/name breaks ties).
Unusable photos have no alternatives. A closest-other match is diagnostic evidence, not proof that
the photo belongs to that identity or a move instruction. Each photo can show
its filename-derived Photo ID and stable catalogue Identity ID; an identity
without a catalogue record is labeled "not catalogued." A provisional core
is calculated from the folder's own photos when there are no trusted identity
anchors; it is not a confirmed identity. The page also exposes face
size/count, core size and type, core membership, centered-cosine method, and
applicable thresholds. Clicking the face metric opens its cached face crop.
Photo ID and Identity ID appear on separate lines. Various holds explicitly
show an unassigned identity, because the holding area is not a person.
The single-match label remains available for existing report consumers and
move-target preselection; displayed alternatives do not override exclusions,
protection or action-policy checks.

The scoring/action details explicitly distinguish approval, protection and
identity-core evidence. **Approve back to Gallery** moves the original; it
does not add photo protection or an anchor. **Protect photo** does not approve
a Review photo, and Review never contributes to core. A protected Gallery
photo is normally excluded from core unless it is also a valid anchor.
Automatically protected photos may retain their recorded prior core eligibility;
protection itself never makes an excluded photo into a reference. Eligible Gallery
photos are reevaluated using the category's configured core threshold and
iterative leave-one-out checks; the old displayed Review score alone does not
guarantee membership after approval. Identity protection is a separate
automatic-change gate, not a scoring override.

The overview always includes the chosen workflow photo when its Gallery
original is available. If it falls outside the current top nine, the grid
shows the top eight plus that photo in slot nine, with a **dashed** score-colored
5px outline and a "shown last; outside top nine" note. If it qualifies within
the top nine, its outline is solid and its natural position is retained.
Switching between core-first and highest-score order recalculates that
display-only pin; it does not alter scores, rankings, core membership or
workflow selection. Head/chest framing preserves the chosen photo's place.
The Markdown overview uses the same nine-photo display selection.

Photo-level Protect, identity-anchor, Review, Reject-to-Various,
Review-approval, photo retirement, and eligible workflow-photo choices are **staged** in the
browser. The page downloads a versioned JSON manifest; it never moves photos
or edits the catalogue. Review/validate the downloaded manifest with
`bin\likeness-actions.cmd validate FILE.json` or `preview FILE.json`. Both are
read-only. Only use `apply FILE.json --apply` after reviewing the preview; it
revalidates, creates and verifies a backup, applies the actions, and records an
audit. `undo [BATCH_ID] --apply` restores the newest active batch only when
the recorded source files and metadata still match. Refresh through the
[bounded gallery maintenance command](original-photos.md#post-action-gallery-maintenance-no-matching),
not global ingest/matching. Keep undo available with a Review-only refresh,
or explicitly settle applied batches before normalizing their inventories.

The explicit **Move to another identity's Review** action preselects the
closest eligible identity and permits another existing destination. It
exports the destination's stable ID and folder, validates both against the
current catalogue, and always sends the photo to Review, never directly into
cast Gallery/core. Protected photos, anchors and workflow-selected photos
must have their restrictions resolved first. The audit retains the chosen
destination ID; undo refuses a replaced or relocated destination identity.
Unassigned Various holds and Artist sources do not offer this action.

**Reject identity permanently; return to Various** is distinct from the
ordinary **Reject to Various** pool operation. For a registered identity,
the permanent action records that identity's stable ID against the current
photo bytes. Normal intake must exclude it, including its merged successor,
from automatic Gallery or Review destinations; grouping must not bypass the
decision. Other identities remain eligible. Ordinary pool rejection retains
its existing reprocessing semantics and does not create an exclusion.
The permanent decision is auditable and reversible through action undo.
Stale photo bytes must be held rather than silently discarding an exclusion.
Metadata/protection changes cannot silently rebind that decision to new bytes.
The intake-aware clean rebuild preserves rejected stable person IDs and requires
verified one-to-one identity continuity. Split/merged/ambiguous decisions refuse.
Current prepared bytes may bind back to immutable originals only through exact
retained lineage, never basename/hash similarity alone. This does not approve
a new real rebuild.
Installing a saved rebuild preview rechecks the source catalogue hash;
pre-exclusion previews are refused when persistent decisions now exist.
Legacy likeness move commands refuse photos with persistent exclusions
instead of bypassing them; use the shared policy-driven `reconcile` or staged
action path. The action does not silently reinterpret older pool rejections.

**Retire photo** is a separate, recoverable archive action for an unusable
Gallery or Review original. Its preview shows the exact destination:
`_retired/photos/<category>/<identity>/<gallery-or-review>/<original-name>`.
It preserves the bytes, records the source/hash/person ID and catalogue
snapshots in the audit, and excludes the original from active matching.
It neither deletes the image nor returns it to Various. Whole-person
retirement and whole-folder archival remain different operations; neither
is implied by this photo action.

Remove a photo's protection or anchor in a separately applied batch before
retiring it; workflow-selected originals cannot be retired. Protection and
retirement cannot be combined for one photo in the same manifest. Identity
protection blocks **automatic** changes, not this explicit user decision on
an otherwise movable photo. Existing archive files are never overwritten.
Undo uses the normal verified-backup transaction and restores the exact
original path only if its archived bytes and catalogue state still match
and no replacement occupies that path. As with other actions, audit-required
unprotected photo metadata remains after undo even when it was first
registered by the action. Derived images/reports are refreshed separately;
the retirement transaction moves only the original.

Staging a workflow-photo change updates the configured base photo and
repoints generated workflows when applied. Workflow-specific overrides remain
separate. The action does not promote or move the selected photo. Applying or
undoing against an isolated sandbox root is refused; sandbox experiments must
not update production workflow inputs.

Photo-level and catalogue identity protection are respected by automatic
planning and apply. In People view, registered Models/Prospects have a separate
**Identity protection (not photo protection)** control in their Review heading.
It stages `person-protected` or `person-unprotected` with the stable person ID,
current folder and expected protection state; no photo ID or hash is borrowed.
It prevents automatic Gallery-membership and category changes, not scoring,
workflow use or separately permitted incoming Review. Cast protection cannot
be removed with this control. Photo protection and core membership remain
separate decisions.

Stage a person's protection change separately from photo actions involving
that identity, including moves into its Review. Conflicting batches, stale
ownership/protection and merged identities are rejected. Apply and undo check
catalogue changes across backup, preserve the complete identity record and
record a person-only audit entry without creating a photo record. Undo refuses
later person-state changes rather than overwriting them.

### Whole-person rename

In **People view**, registered Angels, Sisters, Models, Prospects and Potentials expose
**Rename identity (standalone batch)** in the person heading. Enter a new name,
choose **Stage rename**, then download, validate and preview through the same
action launcher. **Cancel rename** removes that decision. Apply one rename
alone; it cannot share a manifest with photo actions, identity protection or
another rename. If the entered name belongs to exactly one other eligible
registered identity, the same control offers a **TWO-PERSON NAME SWAP**
confirmation showing both identities, protection states and folder/name effects.
Declining stages nothing; confirming stages one standalone action containing
both guarded identity snapshots. Cancel removes the entire decision.
Ambiguous owners, unsupported references and unrelated collisions are refused.

A confirmed swap exchanges recorded names, not photos or memberships.
Angels/Sisters keep their fixed slot/folder/display/workflow references;
non-cast folders/display names follow the exchanged names. Both history records
explicitly record the swap. The catalogue stores both sides under one batch.
Apply and undo validate both inventories and protection snapshots, snapshot
the catalogue/history write set and recovery move maps, and execute both sides
as one transaction with checked rollback. This also handles crossed non-cast
folder destinations without overwriting either collection. An unconfirmed
occupied-name rename is still rejected by the CLI.

For Models/Prospects/Potentials this explicit user action renames the entire person folder within its current
category and updates its catalogue display name, preserving the stable person
ID, photo filenames/bytes, anchors, protection, exclusions and all derived
files. The old folder is appended to folder history. The name/history record
gets the new first-line name and filename; its existing history/profile text
is retained with an appended rename event. A missing record is created.
Automatic identity protection does not prohibit this explicit user rename.

For Angels/Sisters it changes only the **recorded person's name** in the
`z_` name/history record. The fixed character slot, catalogue slot display name,
folder, filenames, workflow photo and workspace references remain unchanged.
For example, `Sisters/Draknisa` can keep that slot while correcting its
recorded person from Sweet Beauty to Amelia Morgan. The field starts with
the actual recorded name, not the slot name. History records the prior name.
Protection remains enabled; the browser asks for confirmation before staging
an explicit rename of a protected identity. It is not an automatic operation.

Windows reserved/unsafe names,
case-only changes, case-insensitive catalogue or filesystem collisions,
ambiguous/multiple history records and linked folders are refused. Non-cast identities
containing a workflow-selected photo or a folder-based workspace exclusion
are refused until those references can be safely migrated; the heading explains
that restriction. No shared workspace config is rewritten by this action.

The exported decision includes the current slot/display name, recorded person name and complete folder
inventory hash. Changed files, empty directories or history require a fresh
gallery export; backup revalidation detects intervening changes. Apply/undo
use the existing verified backup and catalogue guards. Undo restores exact
original name-record bytes and folder only if the renamed inventory and
catalogue state still match and the old destination remains free. Save failures
roll back the rename/history; rollback failures are surfaced with the backup.
Regenerate reports after applying or undoing; old HTML links do not update.

Fixed-slot Angel/Sister renames use a verified **transaction snapshot**:
the affected `z_` record (if present), the pre-change catalogue, and a manifest
with the before/after history bytes, fixed folder mapping and complete identity
tree hash. Images are not rewritten or copied into this snapshot. Apply and
undo revalidate the catalogue and entire affected identity before mutation.
Undo also takes a fresh transaction snapshot. These snapshots cannot serve as
full-library/rebase backups. Confirmed swaps use transaction snapshots covering
both histories, catalogue and guarded recovery folder/staging maps; unchanged
images move with their identity folder, without being rewritten. Other action types and ordinary non-cast folder renames
still use the full snapshot; broader scope optimization remains planned.
Use `bin\library-backup.cmd --verify SNAPSHOT` to recheck either kind.
No snapshot pruning is automatic.

For a name-only correction, refresh the index and galleries with the same root,
cache and saved policy; do not run global matching or normalize images merely
to refresh a name. `likeness index --policy FILE` selects that report policy.
In the overview, the history link opens the renamed record. The Review page's
rename field reflects the updated recorded name; user visual acceptance is
separate from successful apply and payload validation.

Whole-person merge, retirement, rejection and saved family-link
changes remain separate unfinished work.

### Testing exported actions safely

The Review page downloads JSON; it never launches a shell. Use
`bin\likeness-actions.cmd`, not the matching/sorting commands, to execute it.
For the installed sandbox, run from the repository terminal:

```powershell
cmd /c bin\likeness-actions.cmd validate "C:\Users\scott\Downloads\YOUR-ACTIONS.json" --root "B:\Sovereign Territories Sandbox\Working"
cmd /c bin\likeness-actions.cmd preview "C:\Users\scott\Downloads\YOUR-ACTIONS.json" --root "B:\Sovereign Territories Sandbox\Working"
cmd /c bin\likeness-actions.cmd apply "C:\Users\scott\Downloads\YOUR-ACTIONS.json" --root "B:\Sovereign Territories Sandbox\Working" --apply
```

Replace the manifest filename with the actual download. Always supply `--root`:
omitting it selects the configured library. Inspect the preview's exact
destinations, especially the configured Various pool. Start with one action,
then test an independent multi-photo/multi-identity batch. Invalid or conflicting
entries reject the batch before execution; apply backs up and revalidates.
The printed batch ID identifies the undo:

```powershell
cmd /c bin\likeness-actions.cmd undo BATCH_ID --root "B:\Sovereign Territories Sandbox\Working"
cmd /c bin\likeness-actions.cmd undo BATCH_ID --root "B:\Sovereign Territories Sandbox\Working" --apply
```

Undo the newest active batch before testing another isolated action. Regenerate
the gallery after apply/undo before staging further decisions: HTML is a
snapshot, and old locations, hashes or protection state can be stale.
Keep workflow-photo selection out of sandbox batches; it is deliberately
restricted to the configured library. Identity protection must be staged
separately from that identity's photo actions. Whole-person rename is available
as a standalone batch; merge, retirement and rejection are not yet Review controls.

Automated tests round-trip every non-workflow photo action through saved JSON,
validation, temporary-file apply and undo. Separate tests cover identity
protection/unprotection, workflow selection and sandbox refusal, conflict
handling and rollback. Backup callbacks in these unit tests are controlled
fixtures; they do not replace real-library backup or user acceptance testing.

## Command reference

The launcher is `bin\likeness.cmd`; the command name below follows it. All
file-moving commands preview unless marked `--apply`.

### Inspect scores, matches, and reports

| Command | Purpose |
| --- | --- |
| `calibrate` | Library-wide leave-one-out threshold and ranking reliability. |
| `folder NAME [--all] [--outside] [--sheet FILE.png] [--apply]` | Per-person leave-one-out consistency, flagged photos, and outside matches; `--apply` moves only flagged outliers. |
| `audit-core [NAMES] [--group ROOT] [--policy FILE]` | Read-only score ordering against trusted anchors or a provisional core; explains stale/ambiguous catalogue handling. Use the saved run policy and cache to reproduce a sandbox audit. |
| `compare NAME_A NAME_B [--sheet FILE.png]` | Pair similarity and closest individual photo pairs. |
| `alike [--min SCORE] [--sheet FILE.png]` | Similar person-folder pairs and lookalike families. |
| `like PATH` | Rank library folders against a new photo. |
| `scan` | Scan the library and list photos without a usable face. |
| `sisters [--md FILE] [--sheet FILE.png]` | Compare Sisters to the anchor and report closest matches and pairing context. |
| `loosen` | Read-only estimate of the effect of more permissive assignment thresholds. |
| `crosscheck [--min SCORE] [--out FILE]` | Report similarities across otherwise separate artist/prospect groups. |
| `rebaseline [--apply-categories]` | Report category boundaries, routing/Junk candidates and Prospect/Potential cast scores; the optional apply only migrates complete Prospect/Potential folders over the five-usable-photo threshold. |

`rebaseline` also writes a Prospect/Potential per-photo cast audit with
leave-one-out source-folder scores, Angel/Sister centroid scores, suggested
person-local Review paths, and Potential count/history flags. It is evidence
for review, not an identity claim or photo-move instruction.

### Sort and route photos

| Command | Purpose |
| --- | --- |
| `seed [--apply]` | Named-folder drop: every photo in `Various\<Name>\gallery` is that person. Moves the folder's photos to the existing person `<Name>`, or creates a new Prospect/Potential; preview by default. `library.cmd` runs it as step 0, before the pool scan. |
| `sort [--singles] [--assign SCORE] [--plan FILE] [--sheet FILE.png]` | Route `Various` photos to known people or new Prospects/Potentials under current rules. |
| `reconcile [--out FILE.json] [--policy FILE] [--apply]` | Shared incoming/Review proposal; preview by default. Apply requires an approved policy, verified backup, revalidation and a move/catalogue journal. Sandbox draft experiments require `--sandbox-apply-draft`. |
| `reconcile --undo JOURNAL.json [--apply]` | Preview or reverse a verified reconciliation journal. Changed photos or later catalogue decisions block automatic undo; retain the full backup. |
| `review [NAMES] [--out]` | Resolve photos in person Review folders: return likely matches, route clear other-person matches, or leave uncertain photos held. |
| `singles [--min SCORE]` | Preview joining one-photo Prospect/Potential folders to a matching person with the required margin. |
| `rematch [--min SCORE]` | Find likely same-person Prospect/Potential folder merges; cast matches remain for review. |
| `pullback NAME... [--small N] [--all]` | Return selected Prospect folders to `Various` for a fresh sort; chosen-photo folders are protected. |
| `clean [NAMES] [--group ROOT]` | Review person folders against chosen photos/renders; doubtful photos go to Review, clear strangers may be routed elsewhere. |
| `junk [--keep-multi] [--recheck] [--reset]` | Set aside photos unable to feed a Prime; recheck usable files or return all files through current crop/rules. |
| `retire-empty` | Legacy: preview empty Prospect/Potential folders; `--apply` moves them directly under `_retired` with no journal or recovery. After a SIMPLE rebase use `bin\retire-empty.cmd`. |
| `undo` | Preview reversal of the most recent move batch. |

The routine now calls `reconcile`, not the old `review`/`sort`/`singles`/`rematch`
chain. Those commands remain manual compatibility tools; artist-scoped
`group` remains separate because artist provenance must not enter the general
identity pool. The shared minimum now preserves genuine small identities in
these grouping tools too. An ambiguous photo already in Review stays there
unless a specific destination qualifies; a hold is not a rejection to Various.
Check [STATUS.md](../STATUS.md) before running rebaseline work against a real
library.

### Artists and image cleanup

| Command | Purpose |
| --- | --- |
| `group [ARTISTS] [--singles]` | Split loose Artist Gallery photos into same-Artist people; Artist boundaries are never crossed. |
| `artists --from BACKUP\Artists` | Rebuild Artist folders from a flat backup, using `_origins.json` to preserve each photo's Artist. |
| `crop [--no-background] [--undo]` | Crop bars, other subjects, animals and optionally surrounding background; uncropped originals are archived for undo. |
| `crops [--out FILE]` | Build the crop-review page. |

When a second face overlaps the main subject, cropping may not resolve it. A
Prospect photo can remain in that person's Review folder; an Artist photo
returns to its Artist's gallery; a Various photo is handled by Junk rules.
`junk --recheck` returns newly usable photos; `--reset` repeats crop and
current rules.

### Pairing, photos, and identity management

| Command | Purpose |
| --- | --- |
| `pairs [--sister NAME] [--low-photo-only]` | Preview eligible Prospect candidates for configured Angel/Sister pairs. Applying changes Angel photos/workflow inputs; current Angel choices remain user-decided. |
| `photos [NAMES] [--sisters]` | Preview suitable Angel Prime-source photos; Sisters are report-only unless `--sisters` is used. |
| `merge NAME_A NAME_B` | Merge two folders when they are the same person; the emptied folder is retired with history. |
| `retire NAME` | Return a person's photos to `Various` for later casting. |
| `promote PROSPECT ANGEL` | Preview a Prospect-to-Angel swap; applying preserves both histories and updates photo/workflow inputs. |
| `rename OLD_NAME NEW_NAME` | Preview a Prospect folder rename; apply creates a snapshot, preserves history, updates exclusions and repoints photo inputs. |
| `names` | Audit folder names/history and preview missing `z_` files. |
| `lookalikes [--min SCORE]` | Find Prospect/Artist people resembling Angels/Sisters; applying records a reservation in history. |
| `archive-list FILE.md` | Preview/retire complete listed Prospect or Artist-person folders under `_retired`. |

Angel-to-Sister counterpart assignments are fixed by configuration. The
People Gallery and pairing report provide recommendations only. Do not apply
an Angel replacement from a score alone. The existing four selections are
recorded in the [library-management plan](../plans/2026-10-22-library-upkeep.md).
Revisit automatic pairing/swapping only for the future Demon phase after its
counterpart map and direction-specific rules are agreed.

### Names and profile data

Each person folder can have a `z_<name>.txt` in its `gallery`: the first line
is `name: First Last`, followed by dated history entries for operations such
as creation, merge, pairing, retirement or reservation. The file moves with
the folder. Photo splits do not inherit the source person's identity. Names
are descriptive, not matching evidence.

| Command | Purpose |
| --- | --- |
| `index [--import FILE.csv]` | Export the people table (`people_index.csv` and Markdown); optionally preview importing profile edits. |
| `profile NAME... --type "dark elf" --roles rogue,assassin --elements Darkness` | Set profile fields (`sex`, `type`, `roles`, `elements`, `tier`, `tags`); `-` clears a field. |
| `who --roles rogue --elements Darkness` | Find people matching all requested profile filters. |

The versioned identity catalogue is
[`likeness-library.json`](../../data/art/likeness-library.json), validated by
[`likeness-library.schema.json`](../../data/art/_schema/likeness-library.schema.json).
Person IDs persist across folder renames/promotions. Photo IDs use normalized
source IDs; SHA-256 detects stale content and is not an identity key.

## Configuration

Behavioral defaults and tier thresholds are owned by
[`likeness-engine-policy.json`](../../data/art/likeness-engine-policy.json)
and validated by its
[schema](../../data/art/_schema/likeness-engine-policy.schema.json).
The runtime settings resolver rejects conflicting legacy workspace values;
the former assignment/singles/rematch overrides and explicit `different` pair
have been migrated into policy. Workspace
[`workspaces.json`](../../workflows/workspaces.json) retains trusted anchors,
selected workflow photos and pairing/workflow configuration. Explicit anchors
are resolved consistently in clean planning, ordinary reconciliation, audits
and both galleries; choosing a workflow photo does not create an anchor. Run
`bin\likeness.cmd policy` to validate and inspect every configured value.

The current policy is explicitly **draft**: the familiar gallery bands remain
green >=0.55, yellow >=0.30, orange >=0.15, red <0.15. A score >=0.30 is a
visual lookalike/family suggestion, not same-person proof or sufficient evidence
for automatic association. Automatic family metadata has the stronger
[separate gates](#automatic-protection-and-original-names).
Candidate grouping uses the separate draft 0.25 threshold.
The policy retains a 0.40 small-group cast
review boundary: groups with one to four usable photos and a best Angel/Sister
score of at least 0.40 are held for review of that cast match before they can
be classified as Potentials. Groups with five or more usable photos in the
0.40–<0.55 band remain eligible for Model classification. The review candidate
is a suggested destination only; category rebaseline does not move individual
photos into Review. The clean installer can perform the proposed Review
placements. The candidate must satisfy the configured Review permission and
margin; otherwise the report holds the group as an
ambiguous cast match without choosing one identity. Groups below 0.40 still
follow the Potential rule, while scores at or above 0.30 can remain flagged
for visual review. This threshold is an experiment, not a final identity
rule. Draft status blocks production writes, not qualified proposal evidence.
See the
[processing contract](likeness-processing-contract.md)
for the full configuration and remaining acceptance gates.

### Clean sandbox rebuild versus category reclassification

The stable entry point remains `tools/art/likeness.py`; new rebuild logic is
in `tools/art/likeness_library/clean_rebase.py`, not added to the CLI monolith.
Shared core construction and input validation live in `reconciliation.py`,
proposal/group planning in `planner.py`, verified ordinary execution in
`maintenance.py`, configurable decisions in `policy.py`, and
embedding/cache/vector primitives in `engine.py`.
`sandbox.py` owns snapshot/isolation validation. These modules are shared
library code; a second engine under `tools/art/likeness/` is not introduced.

`likeness rebaseline` inspects/reclassifies existing identity folders. It does
**not** flatten or rebuild their memberships. It must not be described as a
clean rebase.

Use `bin\sandbox-rebase.cmd "SANDBOX\Working" "RUN-DIR" --dry-run` for the
clean-start operation. Add `--include-current-various` when the authorized
input set includes current `Working\Various\gallery` and `review`: the preview
then reports the unique union of immutable inputs and current inputs.
Preparation builds a dated run-local `source-overlay`, leaves immutable
`Source` untouched, and records raw recovery copies plus hash-bound ID/path
mapping for every newer or newly added Various file. Exact duplicate bytes are
prepared once but each original path is recovered. Conflicting timestamp IDs
are isolated rather than attached to another image's identity. Carry the flag
through the stages for an auditable command history; a saved overlay is still
verified and reused on resume. Both paths must be absolute and the new run
directory must be inside the isolated Working tree, outside category roots.
Prefer `Working\_sandbox-state\<run>` so the gallery's intake-run browser discovers it.

**For a newly reset Production-gallery rehearsal, use `--baseline working`.**
The default above intentionally replays historical Source; it cannot represent
arbitrary newer Gallery/Review additions, edits or removals outside Various.
The Working mode freezes all current assigned Gallery/Review inputs, including
Artists in their separate scope, then overlays current Various with the same
stable-ID, duplicate and raw-recovery checks. It does not resurrect Source-only
photos or modify Source. Generated reports, backups and derivatives are not
intake candidates. The saved overlay records `baselineMode: working`, and its
hash binds preparation and matching; an explicit conflicting mode on resume
is refused. Source remains verified historical boundary evidence.

Overlay construction and initial input copying publish from owner-locked
configured temporary staging. A failed copy does not publish a partial mirror.
A retry can reuse a byte-verified complete mirror and a verified published
preparation report after a receipt interruption, without rendering it again.
Unknown, changed or incomplete mirrors are refused rather than silently reused.
During preparation, per-image checkpoints also bind the ordered source paths
and hashes, recipe, configuration receipt and every artifact hash. A retry of
the same run reuses only complete, verified image results, including partially
materialized report output; changed or corrupt artifacts are rerendered.
Keep the recipe/configuration and implementation stable during a live run.
An intentional behavior change requires a versioned recipe and a new run,
not rewriting the old receipt or discarding its recovery evidence.

For the fresh-baseline path, substitute `--baseline working` for
`--include-current-various` throughout the sequence below. Include
`--cast-seeds core` on preview, matching and apply when auditing eligible
non-core releases under the existing protected/core/workflow-selected rules.
Use the **same run directory** at each stage:

The matching preview recognizes incoming download IDs using the existing
originals filename-normalization rules, including leading-dot Facebook names,
without renaming frozen source files. Inferred IDs must be unique against
both existing and inferred IDs across the input population. Ambiguous IDs
and descriptive names with no recognized ID remain explicit Review holds.
Installed non-cast destination names use the recorded stable ID; source
paths and original hashes remain in the receipt.

```bat
rem Read-only inventory: no models, cache, report or directory creation.
bin\sandbox-rebase.cmd "SANDBOX\Working" "SANDBOX\Working\_sandbox-state\prepared-run" --include-current-various --dry-run
rem Optional stop after preparing every immutable input; no matching or assignment.
bin\sandbox-rebase.cmd "SANDBOX\Working" "SANDBOX\Working\_sandbox-state\prepared-run" --include-current-various --intake-only --apply
bin\sandbox-rebase.cmd "SANDBOX\Working" "SANDBOX\Working\_sandbox-state\prepared-run" --include-current-various --check
rem Prepare, or resume verified preparation, then save the matching preview.
bin\sandbox-rebase.cmd "SANDBOX\Working" "SANDBOX\Working\_sandbox-state\prepared-run" --include-current-various
rem Only after reviewing that preview and verifying a complete Working backup.
bin\sandbox-rebase.cmd "SANDBOX\Working" "SANDBOX\Working\_sandbox-state\prepared-run" --include-current-various --apply
bin\sandbox-rebase.cmd "SANDBOX\Working" "SANDBOX\Working\_sandbox-state\prepared-run" --include-current-various --check
rem Recover exactly; never delete the rebuilt outputs.
bin\sandbox-rebase.cmd "SANDBOX\Working" "SANDBOX\Working\_sandbox-state\prepared-run" --include-current-various --undo
```

Replace `SANDBOX` with its absolute path. This sequence is documentation, not
approval to run the next real acceptance experiment.

#### Running and observing a long rebase

The launcher is the entry point; do not replace it with a direct Python
invocation or start another copy because an agent's tool wait expired.
Start only one owner for a run. Keep its absolute Working/run paths, command,
log path and returned shell handle/PID in the handoff. A tool timeout that
says the command is still running is not a failed command.

For a current-Working intake-only iteration, this PowerShell pattern captures
both output streams while preserving the launcher's exit code. Choose the run
name deliberately; on a recovery attempt keep that same run name, but only
after confirming its previous process has stopped. Use a separate timestamped
log for each attempt so recovery does not erase the earlier diagnostic.

```powershell
$repo = 'C:\Soverign-Territories\soverign-territories'
$root = 'B:\Sovereign Territories Sandbox\Working'
$runName = 'choose-a-new-run'
$run = Join-Path $root ('_sandbox-state\' + $runName)
$logDir = Join-Path $repo 'tmp\session-logs'
Set-Location $repo
git check-ignore --quiet $logDir
if ($LASTEXITCODE -ne 0) { throw 'Log directory must be git-ignored.' }
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$log = Join-Path $logDir ($runName + '-intake-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.log')
$env:PYTHONUNBUFFERED = '1'
$command = 'bin\sandbox-rebase.cmd "{0}" "{1}" --baseline working --intake-only --apply --workers 3' -f $root, $run
& $env:ComSpec /c $command 2>&1 |
    ForEach-Object { '[{0}] {1}' -f (Get-Date -Format o), $_ } |
    Tee-Object -FilePath $log
$code = $LASTEXITCODE
if ($code -ne 0) { throw "Intake exited $code; inspect $log and the run diagnostics." }
```

These are output-receipt timestamps, not precise worker-operation timings:
`PYTHONUNBUFFERED` avoids Python delaying ordinary progress lines when output
is piped, but parallel-worker messages can still arrive together. Keep the
report's measured durations for profiling. The prefix also applies to captured
error output. Do not restart a live operation just to change its buffering.

In an assistant session, run that bounded command using the shell tool's
long-running/background facility and retain the returned handle. Read further
output through that same handle rather than relaunching the command. Confirm
the specific child process is alive and making progress. If console output is
offloaded or too large, inspect a bounded log tail instead of repeatedly
dumping the whole transcript. Later shell-tool calls may start fresh processes:
do not assume `$run`, `$log` or the working directory survived. Use the
recorded absolute log path (replace `CHOSEN-LOG.log` below):

```powershell
Get-Content -LiteralPath 'C:\Soverign-Territories\soverign-territories\tmp\session-logs\CHOSEN-LOG.log' -Tail 20
```

Interpret the stages separately:

| Observed state | Meaning and next check |
| --- | --- |
| Initial quiet interval | Snapshot validation, hashing, overlay construction or input copying can precede worker output. Check the exact process and run-local files; do not infer a stall from silence alone. |
| `source overlay: copied N/...` | Current Working inputs are being frozen, not yet rendered or matched. |
| `Preparing N images with W worker process(es)` | Preparation workers have started on the frozen mirror. |
| `Completed worker ... (input I)` | An image worker finished; completion can be out of input order. |
| `Ordered report rows: K/N` | Those rows have been safely materialized in inventory order. It may lag completed workers while an earlier input is still running. |
| `DIAGNOSTIC: temporary file lock ...; retrying` | Antivirus or the indexer still holds a freshly written file (`WinError 5`, or `145` "directory is not empty" while its deletion is pending); publishes and scratch removal retry for about 30 s. Repeated lines across many images point at a scanner to exclude, not a code fault. |
| Neither line advances for many minutes while workers burn CPU | Check the run's `inputs\_tmp\prep-*\checkpoints` count. Since Nov 2 a failed ordered publish cancels queued images and exits; rerunning the same run reuses every completed checkpoint. |
| All workers/rows reported | Rendering is finished, but report verification and receipt publication may still be running. Do not start matching yet. |
| Process exited and `intake.json` exists | Candidate completion only: run the launcher's read-only `--check` against the same root/run/baseline. Inspect assessment errors as well as hashes. |
| Intake check passes | Review actual selected outputs and unresolved cleanup; then resume the same run without `--intake-only --apply` to create the matching preview. This is not permission to install it. |
| Quiet matching/apply interval | Input, report and backup hash verification can precede another progress line. Inspect the exact Python process; do not start a duplicate. |
| Backup manifest exists | Not sufficient: the snapshot writer publishes it before its final full-file verification. Wait for successful verification and launcher exit. |
| `RUN\staged` exists; plan still `preview` | Installation is copying retained evidence and building derivatives before its guarded directory swap. Do not remove staging or retry a live owner. |
| Plan becomes `applied` | The library swap committed; viewer generation may still be running. Preserve `previous`, catalogue and publication hashes for undo, then verify the completed command and actual pages. |

For a quiet command, inspect its recorded Python PID (replace `12345`):

```powershell
Get-Process -Id 12345 | Select-Object Id, CPU, StartTime
Get-CimInstance Win32_Process -Filter 'ProcessId=12345' |
    Select-Object ProcessId, ReadTransferCount, WriteTransferCount
```

Compare observations over time. Hash verification can read without writing;
directory enumeration/creation can advance without large transferred-byte
counts. A large snapshot can spend substantial time creating directories
before copying files. Check thread suspension before diagnosing a hung
process, and avoid repeatedly walking the whole tree just to measure progress.

Durable intake evidence is `RUN\intake.json` plus
`RUN\inputs\_reports\preparation\all\manifest.json`, its exact native/padded
images and per-photo details. Logs and contact sheets are observation aids,
not substitutes for those receipts or source-coordinate masks. The shared
Intake runs browser exposes verified staged receipts; incomplete work must not
be presented as accepted Gallery evidence.

For an interrupted **installation**, intake checkpoints are not an install
resume mechanism. Never clear a live owner's `staged`/`previous` directories.
If a measured blocker requires stopping before the swap, first prove the
owner is gone, plan remains `preview`, publication fields are absent,
`previous` is empty, every bound Working input and source catalogue hash is
unchanged, and the full backup still verifies. A **completed** unpublished
stage can now be checked with `--resume-install --check`, then installed with
`--resume-install --apply` on the same launcher/run. Verification binds every
native and retained row/recipe to the frozen preparation, checks all artifacts,
reproduces standard derivative hashes in memory, enforces existing unavailable
head/face gates, and refuses extra/missing/edited files or a nonempty `previous`.
It does not recopy evidence, rewrite outputs, or resume a partial stage.
A failed transaction may leave directory-only rollback scaffolding; this is
allowed only when a no-follow walk proves that `previous` contains no files.
Any retained rollback file or linked directory still blocks stage reuse.

Pass the original seed mode explicitly when replanning or applying:
`--baseline working --cast-seeds core` for a Working/core run. A bare
`--replan` uses the CLI's `all` default, not the saved seed policy. Compare
all photo rows and frozen bindings against a preserved audited preview before
installing; timestamp and implementation-hash rebinding are not new approval.

Full install journals contain published and rollback inventories and may
exceed 16 MiB. Retention readers/writers support a bounded 64 MiB run receipt;
the writer rejects larger receipts without replacing the prior journal.
If retention registration fails after a journal swap, the old journal is
restored and the install transaction rolls files back, including only empty
directories it created. A legacy failed receipt marked `applied` is not proof
of installation: verify live/staged/rollback hashes, preserve the failed
receipt and reconcile state before any supported replan/resume. Never force
an apply or undo based on that status alone.

Existing unowned cast derivative collisions require the separate explicit
`--preserve-legacy-derivatives` option on check/apply. These bytes are **not**
claimed reproducible: every replaced file is hashed and moved into
`previous/external`, participates in the normal transaction rollback, and is
restored exactly by `--undo`. Modern owned but edited/stale outputs still
refuse, even with this option. Default apply detects these legacy collisions
before expensive rendering. The complete verified backup remains mandatory.

For partial staging, preserve the staged and empty previous directories under
distinct attempt names and record a durable run-local receipt before retrying.
Retain all evidence;
do not rerun intake just to bypass an interrupted attempt. If implementation
hashes changed, preserve the audited preview and run supported `--replan`
to rebind it using saved measurements; compare every resulting route,
reason and selected hash before applying. Never hand-edit the engine hashes.
If any
publication or prior-category move exists, stop and inspect the journal's
exact state instead; this pre-publication procedure does not apply.

After an interruption, first confirm the recorded process is no longer
running. Repeat the same intake-only launcher command with unchanged inputs,
recipe and configuration. Let its lock/checkpoint checks decide reuse; do not
delete `_tmp\prep-*`, checkpoints or staged artifacts by hand. A second live
owner must be allowed to fail its lock check, not have the lock removed.
Do not use `--replan` to recover rendering: it resumes matching only when
verified intake and saved measurements already exist.

Then follow the sequence above: intake `--check`, actual image review,
matching preview, move/core/Review audit, approved backed-up apply, installed
`--check`, and actual Gallery/Overview/Review plus exact-face/history checks.
Keep undo evidence. Completion of a shell command alone does not close these
acceptance gates or authorize Production.

Sandbox run history has a separate, dependency-aware retention ledger under
`Working\_sandbox-state\retention-manifest.json`. New intake/rebase receipts
register automatically as review/keep. Inventory and check it with:

```bat
bin\storage-retention.cmd --root "SANDBOX\Working" preview
bin\storage-retention.cmd --root "SANDBOX\Working" check
```

Legacy receipt-backed runs can be registered with `register --all --apply`;
directories without supported receipts remain unregistered and are never
prune candidates. Accept only a reviewed, successfully applied run with
`accept RUN --reason "..." --review-cleared --audit-cleared --apply`.
The newest accepted run per pipeline and every unaccepted/incomplete run stay
retained. Only an older accepted run can be superseded, and prune approval
requires explicit review, undo and audit clearance:

```bat
bin\storage-retention.cmd --root "SANDBOX\Working" supersede RUN --reason "..." --review-cleared --undo-cleared --audit-cleared --apply
bin\storage-retention.cmd --root "SANDBOX\Working" preview
bin\storage-retention.cmd --root "SANDBOX\Working" delete RUN --apply
bin\storage-retention.cmd --root "SANDBOX\Working" repair-history RUN --apply
```

Superseding fingerprints the complete run tree. Preview and deletion recheck
that fingerprint and scan Working text files for dependencies; generated intake
history pages are refreshed after deletion. Each deletion is a separate
explicit apply and writes a receipt under `_reports\storage-retention`.
If deletion completes but history publication fails, `repair-history` retries
only the report refresh and receipt closure; it never restores or deletes run
data.
Production, `Source`, active galleries, and trees outside the exact sandbox
`Working` root are out of scope.

1. Preparation copies immutable Gallery/Review inputs to the run-local `inputs`
   mirror and uses the ordinary renderer. The receipt binds source inventory,
   all artifacts and the full recipe. Reusing the run verifies and resumes;
   it never quietly recomputes reviewed output. An unfinished mirror refuses.
2. All cast images receive preparation outcomes. By default,
   `--cast-seeds all` retains existing cast membership. The explicit
   `--cast-seeds core` preview can release unprotected, unselected cast Gallery
   photos outside their current configured identity cores for fresh matching;
   existing cast Review images remain staged. Artists receive preparation
   evidence but are excluded from general matching and publication.
   Junk/retired trees are not candidates.
3. A fresh run-local cache measures **selected prepared bytes**. Initial cores
   use only Source Angels/Sisters Gallery, with verified anchors/decisions.
   Model/Prospect/Potential and loose Various candidates are flattened; old
   non-cast cores are never reference truth. `Various\<Name>\gallery` reuses
   explicit named-person seeding, not inferred face-score identity.
   Core-seed release uses the configured core similarity and minimum usable
   photo gates without changing them. Protected identities/photos, identity
   anchors, and workflow-selected photos stay in place. Unusable prepared faces
   are excluded from reference cores; unresolved anchors or insufficient
   evidence refuse release rather than inventing a threshold.
4. Shared reconciliation and draft category policy produce routes. Old names
   are display provenance after scoring. Verified one-to-one membership can
   retain stable IDs, original/current names, family and manual opt-outs.
   Ambiguous split/merged decisions, missing catalogued inputs, unknown current
   photos or mismatched decision bytes refuse before reset.
5. `run.json`, `photos.csv`, `report.md`, `policy.json` and `catalog.json` record
   policy, centering, reference folders, implementation/source/prepared hashes,
   outcomes and routes. A reviewed matching preview is required before apply;
   legacy matcher-only previews cannot install.

Apply verifies a complete backup and freezes current native/category/auxiliary
hashes across staging. It stages prepared natives, exact originals and checked
alternatives in the `_processing` store, and standard derivatives under each
person's `944x1104` folder; install and undo move `_processing/<category>`
together with its category. Prepared natives
skip legacy source cropping/screenshot stripping, but keep face-quality and
head/chest framing gates. See [retained storage](original-photos.md) for backup
and move behavior.

By default, cast Gallery **membership** is retained, not raw pixels: cast natives
now receive the same preparation. With `--cast-seeds core`, each source image's
retained/released status, source score, configured thresholds, protection and
workflow-selection reasons, and final Review/routing outcome are previewed in
`run.json`, `photos.csv` and `report.md` before apply. Released candidates use
ordinary matching and category thresholds; inferred cast additions enter Review,
never the cast core. Ambiguous/unusable candidates remain in `Various\review`.
Existing owned cast outputs and generated categories (including Various) are
retained under `previous`; unknown/edited managed outputs refuse. The isolated
catalogue is installed/restored with the run. No workflow inputs are
automatically retargeted.
People/Review are regenerated after installation; their retained detail links
return to gallery/run browsing and expose available maintained derivatives.

`--check` verifies saved input evidence and installed hashes without writes.
Repeat apply verifies the installed result and refreshes galleries, never
installs twice. `--replan` works on an unapplied preview or an undone install,
reuses that run's measurements and preserves its initial preview; an undone
attempt's `staged`, `previous`, `withdrawn` and prior catalogue move to
`RUN\superseded\<UTC stamp>\` as evidence first. Changed inputs/recipe need a
new run. Apply requires saved policy and implementation hashes to match.
Check/undo remain available after policy changes.

Undo verifies installed outputs and saved prior bytes, restores categories,
replaced cast originals/auxiliaries and catalogue, and keeps rebuilt outputs
under `withdrawn`. Edited artifacts block automatic undo. Another experiment
uses a new run and immutable Source, not previous generated identity cores;
verified retained lineage allows current prepared decisions to survive.
This launcher is sandbox-only. Cast release is implemented as an opt-in preview
mode, but its sample acceptance and the separately approved
incremental/production cutover remain unfinished.

The first installed clean run was
`Working\_sandbox-state\clean-rebase-20261021-2210`. It accounts for 1,155
candidate photos, with 52 cast Review additions and no cast Gallery additions.
At its then-configured 0.55 clustering threshold it produced 27 Prospect and 698
Potential folders, no Models, and substantial Review fragmentation. Treat it
as a calibration baseline, not production approval. Its report links the
post-run diagnostics, identity-core audit, and read-only ordinary
reconciliation preview. Do not run the originals-renaming pipeline before
checking the saved manifest: changing image basenames invalidates its recorded
destination paths. Gallery regeneration itself does not rename originals.

That fragmentation run has been undone and replaced by the unified-policy
trial. Current measured results and remaining gates are recorded in
[STATUS.md](../STATUS.md), not inferred from the historical folder counts above.

## Pairing score details

The configured `pairs` map in `workflows/workspaces.json` defines each fixed
Angel-to-Sister counterpart. A Prospect candidate needs at least five usable
photos and folder cohesion of at least 0.45; Potentials and Artist people are
not eligible.

The likeness-fit cost measures distance from target 0.28, with a penalty
outside the preferred 0.15–0.40 likeness band. A bounded variety bonus lowers
the adjusted cost: +0.02 at 10 usable photos, +0.04 at 15, and +0.06 at 20 or
more. The bonus is a proxy for available material, not a measurement of unique
poses or outfits. Global pairing avoids assigning one person twice and
penalizes clashes, so global assignments can differ from independent
per-Angel candidate ranks.

Gallery colors on this adjusted cost are lower-is-better: green through 0.05,
yellow through 0.10, orange through 0.20, then red. The People Gallery shows
the candidate's likeness score, adjusted Fit, likeness-fit component, and
variety bonus separately. The configured Current Angel's centroid score is
independent of the closest Angel match above.

## Cache, photos, and limits

The cache (`modelCacheRoot\likeness_cache.json`) stores detected face data keyed
by image content, not folder assignment or decisions; the default root is
`%LOCALAPPDATA%\sovereign-territories`.

- Moving or renaming a photo does not require a cache reset.
- Editing/cropping an image changes its content and causes fresh detection.
- Changed detector rules invalidate affected entries automatically.
- Clearing the cache by hand is rarely needed and makes the next scan slower.

Only the largest detected face is compared. A face under the configured
minimum (normally 60 px) or without a usable vector is not scored. Legacy cropping can remove app bars or separate other subjects when there is a
clean boundary. Prepared v16 adds person-aware crops and provisional LaMa repair;
unsafe/unavailable stages remain explained holds, not guarantees of clean pixels.
Supported actions preserve originals and recovery data. `gallery_org` is retained
source provenance, not a generic duplicate holding folder.

## Further reading

- [Original photo library and ingest routine](original-photos.md)
- [Curation and recovery foundations](likeness-curation-contract.md)
- [Dated library reconciliation and pairing context](library-reconciliation-context.md)
- [Likeness library self-healing plan](../plans/2026-10-22-review-actions.md)
- [Likeness rebaseline and family-naming plan](likeness-processing-contract.md)
