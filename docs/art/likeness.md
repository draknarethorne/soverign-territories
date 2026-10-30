# Likeness library

`bin\likeness.cmd` analyzes faces in the local original-photo library. It helps
answer three different questions:

1. **Does a photo look like the person whose folder it is in?**
2. **Which other people or folders look similar?**
3. **Where should a new or held photo go?**

The tools can preview and, with explicit `--apply`, perform selected file
operations. Similarity is evidence for review, not proof of identity. The
people gallery and review gallery are local HTML reports; neither moves files.

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
use 0.15 as the minimum core similarity and 0.30 as the Review-suggestion
boundary; Models use 0.30 for both; Angels and Sisters use 0.30 for core
membership and 0.15 for red-band Review suggestions. Candidate grouping uses a
separate 0.25 average-linkage threshold and retains pairs and singletons.
Robust provisional cores exclude red outliers. Photo-to-core attachment and
group-to-core attachment use distinct tier thresholds; an action-support
minimum does not erase a small candidate group.

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

### Established-identity maintenance

`likeness reconcile` plans incoming/Review routing and qualified Gallery
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
The bundle is runnable now. Earlier sandbox trials linked separately generated
diagnostics, but the prepared clean-start runner does not automatically execute
the full bundle or publish its timing. Run `diagnostics` explicitly against the
saved sandbox root/cache/policy; automated bundling remains plan work.

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

A visible Explorer tab is not sufficient evidence that the path is unlocked:
hidden tabs can retain directory handles. In the Oct 29 rehearsal, Microsoft's
Handle utility identified two Explorer handles to `_reports\library`; gracefully
closing that window released them. Do not force-close individual handles.
Rollback cleanup uses Windows extended-length paths because moving old nested
backups into staging can exceed MAX_PATH even when their original paths did not.
If the journal says `committed`, rerunning the same apply finishes cleanup and
returns the existing receipt; it does not reset Working a second time or discard
the carried metadata bundle.

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

Draft policy `draft-2026-10-25.1` adds automatic protection to ordinary
`likeness reconcile` previews and its existing explicit apply/undo transaction.
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
| `retire-empty` | Preview empty Prospect/Potential folders for intact retirement under `_retired`. |
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
$command = 'bin\sandbox-rebase.cmd "{0}" "{1}" --baseline working --intake-only --apply --workers 3' -f $root, $run
& $env:ComSpec /c $command 2>&1 |
    ForEach-Object { '[{0}] {1}' -f (Get-Date -Format o), $_ } |
    Tee-Object -FilePath $log
$code = $LASTEXITCODE
if ($code -ne 0) { throw "Intake exited $code; inspect $log and the run diagnostics." }
```

These are output-receipt timestamps, not precise worker-operation timings:
buffered lines can arrive together. Keep the report's measured durations for
profiling. The prefix also applies to captured error output.

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
| All workers/rows reported | Rendering is finished, but report verification and receipt publication may still be running. Do not start matching yet. |
| Process exited and `intake.json` exists | Candidate completion only: run the launcher's read-only `--check` against the same root/run/baseline. Inspect assessment errors as well as hashes. |
| Intake check passes | Review actual selected outputs and unresolved cleanup; then resume the same run without `--intake-only --apply` to create the matching preview. This is not permission to install it. |

Durable intake evidence is `RUN\intake.json` plus
`RUN\inputs\_reports\preparation\all\manifest.json`, its exact native/padded
images and per-photo details. Logs and contact sheets are observation aids,
not substitutes for those receipts or source-coordinate masks. The shared
Intake runs browser exposes verified staged receipts; incomplete work must not
be presented as accepted Gallery evidence.

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
hashes across staging. It stages prepared natives, exact `gallery_org` originals,
checked `gallery_intake` alternatives and standard derivatives. Prepared natives
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
installs twice. `--replan` works only on an unapplied preview, reuses that run's
measurements and preserves its initial preview; changed inputs/recipe need a
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
