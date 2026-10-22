# Likeness library

`bin\likeness.cmd` analyzes faces in the local original-photo library. It helps
answer three different questions:

1. **Does a photo look like the person whose folder it is in?**
2. **Which other people or folders look similar?**
3. **Where should a new or held photo go?**

The tools can preview and, with explicit `--apply`, perform selected file
operations. Similarity is evidence for review, not proof of identity. The
people gallery and review gallery are local HTML reports; neither moves files.

For the authoritative current state and sandbox/production boundary, see
[STATUS.md](../STATUS.md) and the active
[likeness rebaseline plan](../plans/2026-10-21-likeness-rebaseline-and-family-naming.md).
The photo-library ingest routine is documented in
[original-photos.md](original-photos.md).

## Quick start

| Goal | Command |
| --- | --- |
| Inspect overall scoring reliability | `bin\likeness.cmd calibrate` |
| Save calibration and all eligible folder checks together | `bin\likeness.cmd --root "<library>" --cache "<cache>" diagnostics --out "<new-report-folder>"` |
| Preview restoring sandbox category roots | `bin\likeness.cmd --root "<sandbox>\Working" sandbox-reset` |
| Check one person's folder consistency | `bin\likeness.cmd folder "Drakness"` |
| Audit active-core scores and metadata decisions | `bin\likeness.cmd audit-core` |
| Build both review pages | `bin\people-gallery.cmd --root "<library>" --out "<reports>" --cache "<cache>"` |
| Build only the full Review page | `bin\people-gallery-review.cmd --root "<library>" --out "<reports>" --cache "<cache>"` |

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
using OpenCV YuNet and SFace. The two model files are downloaded once to
`%LOCALAPPDATA%\sovereign-territories\models`; photo data is not sent elsewhere.
Vectors are cached by image content, so moving or renaming a photo does not
require another face detection.

Displayed likeness is cosine similarity after subtracting the library's
average face. A clean run saves its centering mean in its cache, and subsequent
galleries and reconciliation reuse it: moving a photo does not silently change
its scoring space. Ordinary caches without a saved mean retain their existing
population-based behavior. Similarity is a ranking signal within this library,
not a universal identity probability.

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
[active plan](../plans/2026-10-21-likeness-rebaseline-and-family-naming.md).

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

Automatic lookalike association is disabled. Lower-tier routing, merge and
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

The current `.4` draft adds a configurable `.95` near-duplicate similarity
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
library routine, `bin\library.cmd`, runs the photo-preparation, likeness,
sorting, and derived-image steps in order; see
[the routine](original-photos.md#the-routine). `likeness sort` routes the pool
is retained as a manual compatibility command, not the routine's primary
decision path.

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
The new rebase runner will consume this bundle and link its artifacts from
each run manifest; until then, run `diagnostics` explicitly to measure current
library cost and review the evidence.

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
membership/naming thresholds, saved family metadata and rename/apply/undo
remain separate unfinished work. The preview does not approve a draft policy,
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

This is a guarded baseline reset, not the classifier or the complete rebase.
The sandbox runner still needs to define and reset its run-scoped identity
state, write per-run manifests, route candidates, and link diagnostics.

## People Gallery and Review Gallery

Run `bin\people-gallery.cmd` to create the overview and full Review page in
the same report directory. Both are standalone local HTML pages; no server or
network access is needed.

### People Gallery: relationships and overview

The overview shows up to nine photos per person, ordered by core identity or
score. A relationship name opens that person in Review; its adjacent
score-colored marker jumps to that person within the overview. The page
surfaces closest category matches, Angel/Sister pairings, eligible Prospect
alternatives, and full rankings on demand. The score legend is display-only.

The category tags follow the library hierarchy: Sisters, Angels, Models,
Prospects, Potentials, then Artists. The card tags identify category,
workflow selection, photo count, and history. Angel and Sister cards show
their recorded `Person:` name when available. A linked Workflow photo shows
its likeness score; `(not shown)` means it is outside the nine visible
thumbnails.

Prime-start suitability is a photo-quality measure, separate from identity
likeness. Head and Chest-up framing use cached thumbnails. The page is intended
for relationship analysis, not full-library photo actions.

### Review Gallery: full library and staged actions

Run `bin\people-gallery-review.cmd` when only the full review page is needed.
It shows every Gallery and Review photo with category/person filters, a review
queue, low-score view, flat view, selectable ordering, and cached thumbnails.
The person's workflow photo, identity anchor, or provisional reference stays
visible even if filters hide it.

The person heading displays the name separately from category and photo
location. Each usable photo shows both its leave-one-out similarity to its
current identity core and its closest other eligible identity with that
photo's score. A closest-other match is diagnostic evidence, not proof that
the photo belongs to that identity or a move instruction. Each photo can show
its filename-derived Photo ID and stable catalogue Identity ID; an identity
without a catalogue record is labeled "not catalogued." A provisional core
is calculated from the folder's own photos when there are no trusted identity
anchors; it is not a confirmed identity. The page also exposes face
size/count, core size and type, core membership, centered-cosine method, and
applicable thresholds. Clicking the face metric opens its cached face crop.

Photo-level Protect, identity-anchor, Review, Reject-to-Various,
Review-approval, and eligible workflow-photo choices are **staged** in the
browser. The page downloads a versioned JSON manifest; it never moves photos
or edits the catalogue. Review/validate the downloaded manifest with
`bin\likeness-actions.cmd validate FILE.json` or `preview FILE.json`. Both are
read-only. Only use `apply FILE.json --apply` after reviewing the preview; it
revalidates, creates and verifies a backup, applies the actions, and records an
audit. `undo [BATCH_ID] --apply` restores the newest active batch only when
the recorded source files and metadata still match. Refresh derived outputs
after a successful apply/undo with `bin\library.cmd`.

The explicit **Move to another identity's Review** action preselects the
closest eligible identity and permits another existing destination. It
exports the destination's stable ID and folder, validates both against the
current catalogue, and always sends the photo to Review, never directly into
cast Gallery/core. Protected photos, anchors and workflow-selected photos
must have their restrictions resolved first. The audit retains the chosen
destination ID; undo refuses a replaced or relocated destination identity.
Unassigned Various holds and Artist sources do not offer this action.

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
recorded in the [library-management plan](../plans/2026-10-19-library-management-rebaseline.md).
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
visual lookalike/family-group suggestion, not same-person proof or automatic
association. Candidate grouping uses the separate draft 0.25 threshold.
Draft policy `2026-10-21.3` retains a 0.40 small-group cast
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
[active rebaseline plan](../plans/2026-10-21-likeness-rebaseline-and-family-naming.md)
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
clean-start operation. Both paths must be absolute and the new run directory
must be inside the isolated Working tree, outside category roots. The command:

1. Verifies the immutable Source inventory and starts an empty face-embedding
   cache in the new run directory. No old identity cache is loaded.
2. Treats Source Model/Prospect/Potential Gallery and Review photos as one
   unassigned pool. Artist, junk and retired trees are not candidates.
3. Builds initial identity references from Source Angels/Sisters Gallery
   only, honoring catalogue anchors and configured cast anchors. Old
   Prospect/Potential memberships are not reference identities.
4. Runs the shared reconciliation and draft category policy on the flattened
   pool, using the policy's candidate clustering threshold. Old names may be
   retained after matching, but never influence a match or cluster.
5. Saves the effective policy/settings, exact initial reference list, centering
   mean, implementation hashes, and every source/destination/hash/score/reason
   in `run.json` and `photos.csv`, with a readable `report.md`. `policy.json`
   and `catalog.json` preserve the exact run-local configuration and stable
   person IDs.

Repeat the same launcher/paths with `--apply` after inspecting the preview.
Only sandbox Working can be installed: a complete backup is verified, every
output image is staged and hash-checked, previous generated category trees
are retained under the run's `previous` directory, and installation failure
rolls the categories and cast Review additions back. Cast Gallery files are
never replaced. Suggested cast matches enter Review, not the cast core;
ambiguous/unusable candidates remain in `Various\review`, not artificial
Review-only Potential identities. Both galleries expose that hold location.
Protection keeps selected source photos in their existing locations. The
isolated `.likeness-library.json` is installed and restored with the run;
gallery actions against Working save there, never to production metadata.

Repeat with `--check` to verify the saved source decisions and installed image
hashes without changing files. Applying an already applied run is refused.
An unapplied preview can be recomputed with `--replan`: this reuses only that
run's freshly generated measurements, rebuilds cast references and all
candidate memberships, and preserves the initial preview. It does not import
old Prospect/Potential cores. The saved policy can be changed for this explicit
replan; apply requires the saved policy and implementation to match. Read-only
check and undo use the saved run even after the current policy has changed.
Use `--undo` to restore the retained categories and withdraw only that run's
unchanged cast Review additions; rebuilt outputs are retained under
`withdrawn`, not deleted. Undo a previous installed run before applying the
next experiment's cast Review additions. A new experiment needs a new run
directory; it never seeds from a previous run's generated identity folders.
Regenerate the galleries and derivatives
against Working after installation. This launcher is sandbox-only; the
separately approved clean-full production adapter remains unfinished.

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

The cache (`%LOCALAPPDATA%\sovereign-territories\likeness_cache.json`) stores
detected face data keyed by image content, not folder assignment or decisions.

- Moving or renaming a photo does not require a cache reset.
- Editing/cropping an image changes its content and causes fresh detection.
- Changed detector rules invalidate affected entries automatically.
- Clearing the cache by hand is rarely needed and makes the next scan slower.

Only the largest detected face is compared. A face under the configured
minimum (normally 60 px) or without a usable vector is not scored. Cropping can
remove app bars or separate other subjects when there is a clean boundary; it
leaves difficult overlaps for Review/Junk handling. No file is deleted by
these workflows; duplicates may be held in `gallery_org`.

## Further reading

- [Original photo library and ingest routine](original-photos.md)
- [Likeness reorganization, Oct 9](likeness-reorg-2026-10-09.md)
- [Likeness reorganization, Oct 10](likeness-reorg-2026-10-10.md)
- [Likeness library self-healing plan](../plans/2026-10-20-likeness-library-self-healing.md)
- [Likeness rebaseline and family-naming plan](../plans/2026-10-21-likeness-rebaseline-and-family-naming.md)
