# Likeness curation and recovery foundations

**Reconciled:** 2026-10-22T16:34:08-05:00. Metadata, stable-ID, action and recovery context
retained from the Oct 20 foundation. [Runnable guide](likeness.md), schemas
and tested implementations determine shipped command/payload behavior.
The [action plan](../plans/2026-10-22-review-actions.md) owns remaining manual work;
[processing contract](likeness-processing-contract.md) owns tier-aware
automation and supersedes earlier audit-only lower-tier restrictions.

## Current precedence over historical proposals

- The versioned manifest uses the unified `actions` array. Earlier separate
  person-action delivery sketches are not a second payload contract.
- The tracked production catalogue and isolated sandbox-local catalogue
  are distinct. Production-root path assumptions below do not override
  root-local resolution or permit a sandbox write to production metadata.
- Rename is available for cast and non-cast through staged actions; fixed
  cast folders/keys stay fixed. Whole-person action coverage and protected
  unlock remain unfinished, rather than being forbidden by old category lists.
- Ordinary Reject-to-Various is nonpersistent; explicit `match-rejected`
  is a separate content-bound identity exclusion honored by grouped matching
  and merged successors. Stale bytes/unsupported migration fail explicitly.
- Individual photo retirement is delivered; whole-person retirement,
  rejection, merge, swap and family actions have independent remaining gates.
- Earlier numerical proposals are not approved automatic-action policy.
  Metadata/recovery safety does not substitute for labelled engine acceptance.

## Decisions and constraints from the discussion

| Topic | Agreed direction |
| --- | --- |
| ComfyUI source photo | Keep `workspaces.json` as the record of the photo currently loaded by a workflow. |
| Identity references | Store trusted identity-photo references separately from the ComfyUI photo in one git-tracked JSON file. |
| Keep versus identify | A photo may be protected because the user likes it without contributing to the identity core. A trusted identity photo may be an anchor without being a preferred art or workflow photo. |
| Angels and Sisters | Protect their galleries from automatic outlier movement. A user can explicitly send an individual photo to Review; any cast-wide force/rebaseline behavior requires a deliberate opt-in and preview. |
| Prospects | Use the Oct 21 tier-aware action policy: eligible unprotected identities may attach, merge/split and reclassify automatically under validated rules. Selective Review is for uncertainty, not a mandatory intermediate for every lower-tier action. |
| Potentials | Preserve valid pairs and unmatched singletons, keep them matchable, and allow configured organic growth. Group formation is separate from minimum evidence for destructive cleanup. The older minimum-three clustering gate is not a goal. |
| Review and incoming photos | Reconcile both in the same maintenance run. A bounded follow-up audit may use new clusters to resolve remaining same-run candidates, so they do not require a second user-triggered run. |
| Historical cast-audit priority (Oct 20) | The report-only cast audit was a diagnostic milestone, not a permanent prohibition on tier-aware automation. Current work belongs to the engine acceptance plan; selective cast Review never silently admits candidates to cast Gallery/core. Preserve former-identity history and do not classify from raw counts alone. |
| Retirement | Distinguish retiring one unusable photo from retiring an entire person. Photo retirement is a recoverable archive that does not re-enter matching; person retirement uses the existing command to return that person's photos to `Various` for normal reprocessing. Whole-folder archival remains a separately labeled operation. |
| User interface | Keep People Gallery as a concise overview and a separate review/maintenance gallery for large folders, scores and staged actions. The browser is a staging/export surface, never a direct filesystem writer. Photo and person changes use typed entries in the versioned manifest's unified `actions` array; the CLI validates, previews, backs up, applies and supports undo. The old separate `personActions` sketch is superseded. |
| Review gallery layout | Organize the review view category-first, then person; use a responsive left-to-right image grid with adjustable thumbnail size, face/chest-up framing, and click-through to the full image. Keep scores/actions and the primary identity/workflow reference visible. |
| Gallery consistency | Keep the overview and full review in the same category/person order and use the same selectable sort modes: Core identity first (anchors, then core members, then other scored photos) and Highest identity score. The overview's visible nine must match the filtered Gallery view in the review page. Both pages share the same cached Chest-up/Head crops; person links open the matching Gallery view in a new tab. Prime-start suitability remains a separate photo-quality signal, not identity confidence. |
| Identity naming | Let the user stage Prospect/Potential renames in the review UI. Reject collisions unless the user explicitly selects both people for a two-person name swap; preserve both stable identities and `z_` histories. Never rename fixed Angel/Sister slot folders. |
| Potential match context | Show Potentials' closest eligible same-side people and score evidence so the user can decide whether to stage a merge or return the person/photos to normal reprocessing. Never merge from score alone. |
| Report lifecycle | Keep dated report output available for inspection; after the user approves the workflow, support replacing one stable review-report directory. Link a person from the concise overview to their filtered review view when both local reports are available. |
| Metadata | Use machine-readable JSON tied to stable photo identity, not filename grades. Preserve an audit trail and keep user decisions distinct from inferred scores. |
| Tooling structure | Improve the workflow incrementally. Split likeness responsibilities into testable modules and simplify user-facing commands over time; do not combine this with a risky all-at-once rewrite. |
| Python package layout | Move related, low-risk modules and tests into domain packages as work proceeds; keep `bin/*.cmd` stable and audit direct references before moves. Broader `tools/art/` organization has its own [incremental plan](../plans/2026-10-20-art-tools-structure.md). |

## Metadata model and ownership

### Known core/membership cases to label

The user's Petra Cole example contains three screenshots they identify as
Angelica alongside other photos they believe are not Angelica. They also
reported known Angelica photos measuring about 0.19 and asked whether adding
appearance/expression variants as anchors would help. These are labelled
review leads, not proof of a particular historical bug or permission to
strengthen a mixed core. Test per-photo and subgroup evidence against frozen
cores, including expression/pose/makeup variation; don't let the suspect
group define the core judging itself.

The user also reconsidered Camaris after seeing her entire collection rather
than the nine-photo overview used for the Ruby Eden choice. A top-nine display
or a previous manual cast choice is not evidence that every member belongs.
Keep explicit correction/reassignment available while preserving fixed cast
slots, provenance and user intent. Engine E6 owns labelled calibration;
manual actions A6 owns supported correction scenarios.

### Production and isolated catalogues

Production uses one versioned, machine-readable JSON file tracked in the repository:
`data/art/likeness-library.json`, validated by
`data/art/_schema/likeness-library.schema.json`. Keep identity metadata and
photo-level decisions in that catalogue under Git versioning. An isolated
sandbox uses its own `.likeness-library.json`; actions resolve the chosen
root's catalogue rather than crossing into production. Keep path configuration
and ComfyUI workflow-photo selection in
`workflows/workspaces.json`; the two files have distinct ownership.

The schema must associate person identity with stable person identifiers and
photo decisions with stable photo identifiers, not only mutable folder names
or filenames. Before implementation, prove how identifiers survive moves,
renames, cropping, deduplication, restoration and backup. Store aliases or
content hashes as needed and reject ambiguous identities rather than guessing.

The existing `z_<name>.txt` remains the human-readable name and history file;
metadata does not migrate or replace it.

### Distinct concepts to represent

- **ComfyUI photo:** the workflow input selected in `workspaces.json`;
  automatically photo-protected, but not automatically an identity anchor.
- **Identity anchor:** a user-confirmed face reference that contributes to a
  person's trusted identity core.
- **Protected photo:** do not automatically move or reclassify this photo.
  Protection does not imply that it belongs in the identity core.
- **Ordinary photo:** available for scoring and conservative automatic review.
- **User-sent-to-review:** remove the photo from its current person gallery
  and active identity evidence; compare it against that person and every other
  candidate through the normal combined matching pass.
- **User-rejected-to-pool:** return the photo to `Various` and process it like
  new incoming material. Do not give its former folder priority, while still
  allowing a normal whole-library match to find that folder if the evidence
  independently supports it.
- **Photo retirement:** a user decision that a photo is unusable. Archive it
  recoverably under a photo-specific `_retired` subtree, remove it from active
  identity evidence and exclude it from matching. It is not Review,
  Reject-to-Various, or deletion.
- **Person retirement:** use the existing `likeness retire` operation to send
  the person's photos to `Various` for normal reprocessing. Label the
  destination in the preview. Keep `archive-list` whole-folder archival
  distinct; it must not be presented as the same action.
- **Observed match and score:** a generated suggestion, never user-authored
  identity truth.
- **Action history:** what was proposed, approved, applied, reversed, by which
  command and when.

The schema must support more than a fixed number of anchors. The user expects
to be able to protect a trusted core of roughly five to ten images when useful,
but some people may have fewer or more suitable references.

### Stable photo identity

Before finalizing the schema, prove that a photo keeps its metadata when it is
renamed, moved, scaled, cropped, deduplicated, restored, or found in a backup.
The current tools recognize several source IDs and cache face data by content;
neither fact alone proves that every transformation can be joined safely.
Reject ambiguous IDs and stale manifests rather than guessing. Record hashes
and aliases as needed, and test restoration and duplicate cases.

The initial helper generates opaque UUID-based person IDs and photo IDs from
`comfy_workflows.photo_key()` on originals-managed filenames. `originals.py`
preserves the embedded source ID when folder prefixes change, and the crop
command replaces a photo under the same name while archiving its uncropped
bytes. Thus a crop retains the filename-derived ID but changes the content
hash; metadata refresh and restore behavior still need explicit tests. Duplicate and backup-restore continuity were subsequently verified for
originals-managed IDs in A4; unsupported transformations still require
explicit mappings rather than guessed continuity.

## Matching and self-healing policy

### Action-specific validation, not a universal safety threshold

Treat the current scores as calibrated starting points, not universal weights.
Measure false assignments and missed matches separately for:

1. a photo assigned to an existing person;
2. a photo returned from Review to its source folder;
3. a photo sent from Review to another existing person;
4. several photos clustered into one new person;
5. two person folders merged;
6. a photo flagged as an outlier from its current Prospect.

Use user-confirmed examples, including laughter, unusual angles, expressions,
lighting, makeup and changes in appearance. Report precision and recall for
each action. Do not lower thresholds just to shrink Review counts. A cutoff
that is acceptable for a suggestion may be unsafe for an automatic move or
whole-folder merge.

### Build a robust identity core

- Use user-selected identity anchors as trusted evidence where present.
- Keep protected-only photos in the person's gallery, but exclude them from
  the identity core unless the user also marks them as anchors.
- For people without user-selected anchors, compute a provisional robust core
  from ordinary gallery photos. Show which images formed it and why.
- Do not let a suspected outlier shift the core used to judge itself.
- Preserve a minimum viable core. A cleanup pass must not move the last
  trusted anchor or reduce a Prospect below the agreed minimum core size.
- A low score alone is not sufficient to reassign a photo. Require evidence
  against the trusted core, a strong destination match with a clear margin, or
  otherwise stage it in Review.

### Scope by category

The later
[tier behavior and protection contract](likeness-processing-contract.md#tier-behavior-not-a-global-caution-switch)
is authoritative. Earlier report-only Prospect cleanup and cautious Potential
handling were delivery stages, not permanent limits on lower-tier automation.
Cast Gallery protection does not forbid separately permitted incoming cast
Review or impose a clustering threshold on unrelated candidates. A protected
photo must not move automatically, but may stay outside the core.

### One reconciliation plan for Review and incoming photos

The primary routine now calls shared reconciliation instead of its former
Review/sort/singles/rematch decision chain. Its established maintenance paths
are implemented, but labelled real-batch acceptance is still outstanding. The
[ordered decision flow](likeness-processing-contract.md#ordered-decision-flow)
now specifies one planner for rebase and incremental maintenance. This plan
supplies its metadata, review actions and recoverable execution foundation;
it does not define a second matching sequence.

Keep established and provisional reference vectors frozen during bounded
same-run matching. Retain small-group evidence, keep unresolved holds distinct
from new identities, and separate proposed destinations from write
authorization. The later plan owns category transitions, merge/split planning,
effective configuration, source modes and full-path behavioral tests.

## Review interface and action manifest

### Two complementary gallery views

- Keep `people_gallery.html` concise and useful for browsing identities,
  pairings and readiness.
- Add a separate local `people_gallery_review.html` for maintenance. It should
  surface Gallery and Review photos together, show scores/order and reasons,
  and distinguish trusted core, protected, ordinary, Review and suggested
  outlier items.
- Support large libraries with filtering, pagination or incremental display,
  lazy thumbnail work and cached derivatives. Do not require generating or
  embedding every full-size image just to inspect a 100+ photo person.
- Show which comparison was used: own trusted core, current person candidate,
  another person, or provisional cluster. Keep the numerical score
  interpretable and do not present it as certainty.
- The report is local and read-only. It must not run filesystem operations or
  fetch images or scripts from third-party services.

### Staged actions

The page should export a versioned JSON action manifest for a CLI to inspect
and apply. The supported actions should be explicit and separate, such as:

- mark/unmark identity anchor;
- protect/unprotect from automatic movement;
- send a selected photo from a person gallery to Review (remove it from that
  person's active identity core);
- reject a selected photo to `Various` for normal incoming-photo processing,
  without preferring its former person;
- approve a Review photo back to its person;
- request reprocessing through the combined Review/Various planner;
- accept or reject a proposed match or cluster.
- stage a Prospect/Potential name change, or explicitly pair two people for a
  collision-resolving name swap.
- later, retire one unusable photo to the photo archive, or retire a Potential
  or Prospect through the existing CLI operation that returns its photos to
  `Various`. Keep retirement out of the first Review/Reject delivery.

The manifest should use stable photo IDs, expected content hashes, current
source locations, destination intent, actor/reason and schema version. The CLI
must reject stale or ambiguous entries, show a dry-run summary, create and
verify a backup before moves, log each action, and support undo. Applying a
manifest must never mean “trust the old score”; recalculate current evidence
and enforce current protections and category boundaries.

The interface must make **Review** and **Reject to Various** distinct. Review
means compare the photo against all people including its former person.
Reject-to-Various means start the normal incoming-photo path, without giving
the former folder priority; a strong whole-library match may still return it
there. Neither action deletes the photo, retires a person, nor claims identity
truth.

Sending a protected photo to Review is a deliberate, photo-specific override
of the automatic-move protection; it does not authorize changes to any other
protected photo. A photo sent to Review or Reject-to-Various stops being an
active identity anchor for its former person. Preserve the previous decision
in history and require confirmation in the staged-action preview.

### Review-folder location

Initially retain person-local physical Review folders to avoid a risky library
migration. The review interface should aggregate them into one navigable
maintenance view. Evaluate a root such as `Review/Prospects/<name>` only if
the interface exposes a concrete limitation that cannot be solved by
aggregation; if needed, migrate with a verified backup and reversible mapping.

## Safety and acceptance criteria

- No automatic deletion. Every source remains recoverable from its original
  location, archive, backup or action history.
- Identity anchors, protection, workflow-photo choice and inferred match are
  independent fields and visibly explained.
- Routine processing never moves protected photos or Angel/Sister gallery
  photos without an explicit user-staged action.
- Cleanup cannot remove trusted anchors or violate the applicable minimum
  core. Ambiguous outliers go to Review/hold; qualified lower-tier actions
  follow the later tier-aware contract, not a blanket no-reassignment rule.
- Review and pool candidates are considered together against existing people
  and same-run provisional clusters; bounded iteration is deterministic and
  cannot oscillate or reassign a candidate more than once.
- The user can audit exactly why a photo was held, returned, moved to Review,
  or matched elsewhere.
- A preview and verified backup precede every batch with file changes.
- Production thresholds remain unchanged until action-specific validation
  and approval. Explicit sandbox overrides may vary thresholds for real
  trials; record them without creating a second matching engine.
- Large-gallery UI performance and the action-manifest workflow have focused
  tests, including stale hashes, missing files, duplicate IDs and undo.

## Approved design decisions

| ID | Decision |
| --- | --- |
| D1 | Store identity metadata and photo decisions in one versioned, git-tracked `data/art/likeness-library.json`, validated by a schema beside the art schemas. Keep workflow paths and selected ComfyUI photos in `workflows/workspaces.json`; do not replace `z_<name>.txt`. |
| D2 | Keep identity anchors, keep/protect preferences, and workflow-photo choice distinct. A photo can be protected but not an anchor. |
| D3 | Sending an image to Review or Reject-to-Various removes it from its former person's active identity evidence. Review compares it against all people, including its former person. Reject follows the regular incoming pool path without a special preference for the former folder. |
| D4 | Permit a bounded, deterministic same-run follow-up using provisional clusters to resolve eligible candidates. Do not mutate existing identity cores mid-run, reassign candidates repeatedly, or loop without a convergence condition. |
| D5 | Keep current person-local Review folders and aggregate them in a separate, efficient review gallery. Do not move the physical Review tree unless later evidence requires it. |
| D6 | Add photo- and person-level retirement to the GUI after Review/Reject works. Photo retirement archives one unusable image recoverably and excludes it from matching. Person retirement uses the existing CLI behavior and returns that person's photos to `Various` for reprocessing. Keep both distinct from Review, Reject-to-Various and whole-folder archival. |
| D7 | Implement and commit validated increments. Keep larger art-authoring and ComfyUI execution UI as future scope, while preserving integration paths. |
| D8 | Keep the photo archive in a separate `_retired/photos/` subtree; preview the path, preserve content and history, and support restore. Treat `archive-list` as a separately named whole-folder archive operation. |
| D13 | Keep a person's recorded identity name separate from fixed Angel/Sister slot folders. Prospect/Potential name changes must preserve `z_` history, reject collisions by default, and permit a two-person swap only when both identities are explicitly selected. |
| D14 | Keep the existing category roots and use virtual, stable-identity family/lookalike groups; no physical family/twin root is added in this iteration. |
| D15 | Use shared surnames only for explicitly associated identities, keep first names distinct, and never use names or family links as matching evidence. Audit `z_` first/last names and surname collisions before any rename. |
