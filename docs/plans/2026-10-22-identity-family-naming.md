# 2026-10-22: identity families and safe naming

**Status:** holding (Oct 30 scheduling; existing migration retained, broader naming/family acceptance open)

**Resume gate:** after installed baseline and intake tuning, then explicitly
select N12 corrections/family acceptance. Existing approved decisions and
stable-name/protection guards remain binding; no bulk renaming during install.

## Oct 31: what the installed rebase did and did not verify

The [installed outcome audit](2026-10-23-cast-seeded-library-rebase.md#oct-31-cast-routing-name-continuity-and-iteration-audit)
found 202 identity records but zero structured `names` or `family` entries.
The source catalogue was empty; populated stable-ID family/name migration,
family reconciliation and original-name correction were not exercised.
All 21 cast name/history files and 133 non-cast same-label history copies
verify byte-for-byte; 48 other non-cast summaries are generated stubs.
There are no duplicate recorded full-name labels, but 45 repeated surnames
span 118 folders without accepted family metadata. Surname reuse alone is
not an organizational-family association or a biological relationship.

This closes no N7/N9/N12/N13 gate. In particular, 61 old non-cast folders
split and 105 new non-cast destinations mix source-folder provenance; name
file preservation is not proof of correct membership or original name.
Use the audit's name-lineage table with the user's review, then prepare
explicit reversible corrections/family proposals under existing contracts.
Do not silently re-label the current frozen baseline or run automatic
family reconciliation as part of this read-only audit.

## Oct 30: named and unnamed Various acceptance contract

- [ ] **P2 either** N13 Cover `Various/<supplied person name>` as explicit
  original-name intent, distinct from unnamed `Various/gallery`. With N12,
  preview matching/merge/history/name correction and exact de-duplication,
  preserve fixed cast slots, and compare every photo against normal core/
  Review thresholds. A folder assertion does not make all its faces identical:
  detect mixed people, ambiguity and conflicts before mutating.
  Test new plus duplicate arrivals, existing cast/core membership, matches
  elsewhere in the library, optional identity retirement after verified merge,
  low-score Gallery versus Review, rejection back to eligible routing and
  retirement exclusion with action A2/A6 and engine E4-E8/E13. No unsupported
  global self-healing or original-name overwrite is claimed today.
  Unnamed arrivals may create identities under established rules; preserve
  original source names and allocate stable unique photo IDs for arbitrary
  supported filenames (intake I75), not only download IDs. Reconcile summary
  `z_` text versus authoritative durable history for moves, naming, cast
  assignment/demotion, retirement and rejection, with exact undo. This is
  one cross-owner acceptance matrix, not a second naming/matching engine.

## Oct 27 feedback reconciliation: names and family status

The family-status question is answered: draft family metadata, reversible
name presentation and direct-reference suggestions are implemented; real
calibration/acceptance, leave/reassignment and broader name migration remain
open under N7/N9. Rendered resemblance is separate advisory evidence, not
kinship or permission to rename/merge automatically.

The new `person_names_folders.md` asks for named-folder intake, correction of
historical original names, three-name display without duplicate labels, GUI
rename/swap and preserved cast slots. Named intake is implemented in the
prepared sandbox route, but is not a generally accepted production promise.
It preserves explicit supplied-name intent with ambiguity/rejection guards;
a folder drop is not permission to overwrite another stable person's history.
Existing names distinguish character/current/original; original provenance
is currently preserved through rename/swap rather than freely corrected.

**Oct 27 decision, clarified by the user:** an explicit forced correction
must replace a misassigned original name with the person's proper original
identity/name, including bugs from earlier promotion/swaps and random
Various intake names. It is not merely another alias beside an authoritative
wrong original name. This supersedes immutability of the effective original
name for that explicit correction only; ordinary rename/swap and automatic
likeness processing must not silently rewrite it. Retain the old erroneous
value in correction history/undo, not as the person's displayed original.
Stable person IDs and cast slot keys remain fixed; a name correction does not
silently merge people or move mixed-person photos.

Work order: intake crop/erase/framing first, original-name correction next,
then family/current-name presentation and acceptance. Family naming may
change the current first/last name without overwriting the corrected
original name. Named-folder corrections and GUI corrections need the same
explicit intent, conflict preview and reversible transaction; merely
re-dropping files is not claimed to implement that behavior today.

Later Oct 27 clarification schedules the full sandbox grouping/near-match
family preview before the user's original-name cleanup, then validates all
of it before production cutover (rebase C8/C9). This changes the review order,
not the separate original/current/character-name contracts. Near matches
that fail same-person merge rules may be proposed as Models with a family
relationship to an Angel/Sister, subject to existing direct-reference,
ambiguity and user-acceptance gates; do not auto-merge them or rename cast
slots to satisfy presentation. N12 remains required before that name cleanup.

- [x] N11 User resolved the conflict: explicit forced correction replaces the
  erroneous effective original name, retaining audit history and exact undo.
  Update the enduring naming contract under N12 before implementation.
- [ ] **P2 ai** N12 After intake tuning, update the naming contract and
  implement/test the approved correction through
  existing stable-ID name transactions, GUI rename/swap and named intake.
  Keep cast keys fixed, distinguish source evidence from generated names,
  replace the effective original name on explicit correction (not alias-only),
  deduplicate equivalent current/original display labels without deleting audit
  history, and test conflicts, repeat intake, mixed identities, later family
  first/last-name changes, rebase and exact undo. Do not promise that re-dropping
  existing photos currently corrects their established original names.

### Family-status question (verbatim)

Source: `feedback/family_naming_question.md`. Answer and remaining scope above;
incorporation, not acceptance of unfinished implementation.

```text
# Family Naming Question

## Question

- Where are we at with the family naming at this point?  I am losing track of some things, but do want to start to review that process and ensure we have a clear understanding of the current status and any next steps needed.
```

### Person names and folders (verbatim)

Source: `feedback/person_names_folders.md`; N11 resolved by the clarification
below; individually archived after exact preservation and coverage verification.

<!-- markdownlint-disable MD013 MD009 -->
```text
# Person Names and Folders

## Question

- Are we setup that if I drop a named person folder into Various/[person name] will it pull those images and assign that persons name automatically?  
- I also want to know where we are at with the names overall, I believe we have the Character Name if assigned to a slot of a character.  Person Name (currently assigned person name and potentially the family name if we change or assign first or last name to align with family likeness) and the Original Person Name (either automatically assigned during an intake with photos in Varous/Gallery without a name or assigned based on the Various[Person Name] folder being present so we keep that original name).
- I want to clarify if the system will automatically update the Person Name when images are added to a Various/[person name] folder, and how it handles conflicts with existing names or Original Person Names.

Ultimately, I want to make sure we've got this handled properly in the meta-data.  Because, I could take some existing images of a Prospect or Potential and place them in a Various/[person name] folder and re-process them to get that Original Person Name assigned properly - even if already assigned a ficticious name, and I want to ensure that the system correctly assigns the person's name and maintains the original name for reference.

Does this all make sense in how I might want to re-baseline the original person names of someone vs. the assigned Person Name?

I know it's documented somewhere, but I think things may be fragmented and as part of a rebase, I want to ensure we have a clear understanding of how the system handles Person Names, Original Person Names, and any interactions with Various/[person name] folders.

We know the character slots and people assigned to them are "locked for sisters and angels", but some of the original person names are not correct and I was thinking of how to get that original person name updated as well as any assigned names along the way.  Sometimes the original person name and current/assigned person name are the same and sometimes different.  Once they are promoted to a character, then they take on the character name "Angelica, Drakness, etc.." but would still retain and show their other names.  I wouldn't want to duplicate them if both the original person name and the assigned person name are the same on the GUI.  Only if things changed during the process.

Hope this all makes sense in how we have the naming and if I want to rename the assigned person name or the original person name (or both) during either the intake process using the Various/[person name] folder or the GUI rename or swap names between two.  I have a lot of clean-up I need to do over time and just want to ensure our naming meta-data, gui and handling of intake assignment of names is correct and working the way we intended it. 

It's organically grown and names have swapped in early versions of the processing - so once we lock down all the functionality, I will handle the renaming and name assignements of all the existing people in the library.
```
<!-- markdownlint-enable MD013 MD009 -->

## Oct 25 implementation continuation

The user explicitly requested implementation rather than another planning stop.
Working defaults are selected for isolated draft-policy previews, not declared
calibrated or production-approved. The earlier approval questions remain
acceptance work, not blockers to building schema/helpers/tests.

Implemented for draft-policy preview/apply/undo:

- Optional catalogue `names` records preserve original/current person name and
  original-name source. Earliest recognizable explicit rename history is retained;
  an unknown original is labelled unavailable, never replaced by a cast key.
- Optional per-person `family` metadata records stable family/reference IDs,
  surname, similarity, policy version, previous person name and explanation.
  Families are organizational direct-reference groups, not biological assertions.
- New family groups require reciprocal, unambiguous direct references and five
  independent current core photos per identity. The draft automatic band starts
  at 0.40 and ends below 0.55 or either identity's stricter merge threshold.
  Reference lead is at least 0.05. Same-person ambiguity, stale evidence,
  insufficient diversity, pending membership changes or name collisions hold.
- Existing-family joins require direct evidence to the established founder;
  no surname-based or transitive association. Preserve first names rather than
  invent shared-initial replacements; collisions remain diagnostic.
- Family surnames change catalogue current-person presentation, not physical
  folders/history/workflow keys. Manual rename/swap retains immutable original
  provenance and exact undo. Galleries display character/current/original names
  separately, with family surnames appended to character display only.

Shared reconciliation composes protection, names and families into one full-record
metadata patch per stable ID, with source/hash checks and an existing backup/
journal transaction. Names-only migrations use that same path. No independent
family writer or alternate scoring engine is added.

Overview, Review (including mixed-photo grids), identity detail and family preview
use the shared presentation helper. Explicit protection reasons and persistent
manual-unprotect opt-outs are visible. Earliest recorded pre-rename catalogue
snapshots can recover original names; missing evidence stays unavailable.

N7's real labelled acceptance and broader migration remain open. Do not represent
an unrun library batch or a guarded rebase as completed identity continuity.

## Oct 25, 12:33: established identities, family names and original-name continuity

The user requests automatic protection of sufficiently supported identities and
their high-confidence photos, coordinated with reversible family naming and
gallery presentation. The full message is preserved below. Automatic protection
belongs to [engine E13](2026-10-22-likeness-engine-acceptance.md);
manual override/undo belongs to [actions](2026-10-22-review-actions.md).

Agreed direction, with numerical and override decisions still to be approved:

- Keep separate stable person IDs for distinct lookalikes. A family association
  is an organizational resemblance group, not confirmed kinship or a merge.
  Ambiguous same-person cases must be resolved/held before family auto-naming;
  a score below a merge gate alone does not establish distinctness.
- Preserve the earliest reliably recorded supplied or generated person name,
  its provenance and subsequent rename history. Do not overwrite it on family
  join/leave or replace it with a cast slot. Missing/conflicting history must
  remain explicit, not be reconstructed from a surname or folder guess.
- Show **character name** (where assigned), **current person name** (including
  assigned family surname), and **original person name** as separate labelled
  facts. Non-cast identities need no fabricated character name.
- Family assignments must retain prior names, stable IDs and exact recovery.
  Shared-initial first-name generation must never destroy the original name.
  Existing explicit name approvals and collision checks still apply.
- Family/name changes and protection must not influence matching evidence.
  Do not let family naming silently rename fixed cast directories/workflow keys,
  or let a rebase discard original names, overrides or family history.

Before implementation, the verified gaps were: the catalogue person schema had `displayName`,
folder history, anchors and protection, but no original/current-person-name or
family-membership fields. The read-only family preview uses direct reference
suggestions and flags possible same-person matches; automatic association is
disabled in the current draft policy. These are prerequisites, not delivered
behavior at that planning checkpoint. The implementation above closes the
schema/display gap; N2/N3's calibration and historical migration questions remain.

- [ ] **P1 ai** N9 Specify original/current/character-name provenance and
  migration in the existing catalogue contract; inventory reliable history and
  conflicts before populating fields. Extend schema/validators, rename/swap/
  undo and family transitions without losing original supplied/generated names.
  Test repeated rename, family join/leave, cast swaps, missing history and rebase.
- [x] N10 Wire the three-name display and family/protection reasons
  into Overview, Review and identity detail through shared payload helpers.
  Display unknown provenance explicitly; keep Artist domain boundaries.
  Coordinate layout parity instead of adding another independent name resolver.

N9 progress: schema, history recovery, rename/swap provenance, exact undo and
combined metadata transactions are implemented and unit-tested. Stable-ID
clean-rebase migration is now implemented for verified one-to-one continuity.
Ambiguous split/merged destinations still refuse; broader real-curation
migration and explicit family leave/reassignment acceptance remain open.

## Review and questions: 2026-10-22 16:26 -05:00

Verified successor to the family portion of the former umbrella.
Approved D1-D7/D12 and Q4/Q5 remain in the
[processing contract](../art/likeness-processing-contract.md).
Before N2/N3 ask one at a time: may one-to-four-photo Potentials receive
automatic family names, or only suggestions? Which incomplete names can be
recovered from history, versus supplied by the user? What threshold/evidence
creates a reversible relationship rather than just a suggestion?
Preserve existing user-approved names (including Angelica Vale) until resolved.
No family relationship or rename is inferred merely from surname reuse.

## Scope and decisions

**Oct 26, 21:48 clarification:** virtual-family/casting review also needs to
show when distinct source people become lookalikes after matched Prime
rendering. The [rendering plan](2026-10-25-reference-rendering.md#oct-26-2148-character-auditions-not-faithful-body-restoration)
owns the verbatim request and R41's rendered comparison. These suggestions
inform deliberate casting or virtual-family choices, not source-person merges,
kinship claims or automatic surname changes. Existing original-photo family
evidence rules remain unchanged; rendered resemblance must be labelled
separately and confirmed by the user before metadata changes.

This plan owns virtual family/lookalike relationships, threshold-assigned
family naming, collisions, stable metadata and their gallery presentation.
Keep category folders: no physical Families/Twins root. Shared surnames and
preferably distinct first names with a shared initial are naming outputs,
never identity evidence. Family resemblance never permits a same-person merge.
Fixed cast slots remain separate from the recorded real-person name.
Production naming still requires the [engine acceptance gates](2026-10-22-likeness-engine-acceptance.md).

Manual rename is shipped through staged JSON, backup/apply/undo. Protected cast
renames change only the recorded name/history; non-cast folder renames refuse
unsupported references. Swaps and broad action availability belong to
[manual actions](2026-10-22-review-actions.md); presentation structure belongs
to [layout](2026-10-22-gallery-review-layout.md).

## Evidence, not acceptance

The full-name audit corrected four incomplete records and reported 265 complete
names at that historical stage; it is not today's catalogue count.
`family-preview` is read-only. The saved `.3` scenario inventory had 232 people,
138 closest-reference suggestions, 52 reused surnames, 71 Artist-person
exclusions and no current full-name/folder collisions. One proposed name
conflicted with an existing name; two proposals conflicted with each other.
Surname reuse is not confirmed kinship. The preview neither saves accepted
family metadata nor performs automatic naming.

## Remaining work

| Live task | Oct 21 source tasks | Retained work |
| --- | --- | --- |
| N1 | 2.3 | Classify surname reuse, not just count it |
| N2 | 2.4, 2.5 | Relationship contract and stable-ID schema |
| N3 | 2.6 | Approved collision-safe migration |
| N4 | 2.7 | Schema/helpers/tests after contract approval |
| N5 | 5.1, 5.1a, 5.2 | Family viewer, classification filters and naming preview |
| N6 | 5.3 (family-link/name portion) | Staged family changes; manual swaps owned separately |
| N7 | 5.4 | Actual family/name acceptance |
| N8 | 5.5 | Refresh index/reports/references without changing cast keys |

- [ ] **P1 ai** N1 Classify surname reuse as confirmed resemblance,
  unrelated or unresolved, and inventory case-insensitive name/folder collisions.
- [ ] **P1 either** N2 Specify and approve suggested versus threshold-assigned
  family links, evidence/version/history, reversibility and naming thresholds.
  Use stable IDs; cover splits/joins, promotion/demotion and changed cast
  occupants without making slots or names identity keys.
- [ ] **P1 either** N3 Approve a deterministic naming/migration table,
  preserving existing names until resolved and rejecting collisions.
- [ ] **P2 ai** N4 Implement approved family schema, validators and helpers
  in contract-first order. Preserve exact prior name/history on undo and test
  stale decisions, collisions and rollback.
- [ ] **P1 ai** N5 Show suggested/assigned family links, members, current
  and proposed names, evidence and source-history mismatches in the gallery.
  Preserve flat/category/person views, classification/family filters and
  cast-likeness evidence without implying identity confirmation.
- [ ] **P1 ai** N6 Wire approved family-link and family-name changes through
  the existing manifest/preview/verified-backup/apply/undo boundary, not browser
  filesystem writes or a second naming engine.
- [ ] **P1 you** N7 Review actual sandbox family groups, exceptions and
  proposed names; accept thresholds before the production batch.
- [ ] **P2 ai** N8 Refresh the people index, galleries and documented
  workflow-facing references after apply/undo, preserving fixed cast keys.

## Closure

Close only when family metadata, viewer, reversible writes and user acceptance
are complete. Existing manual rename and the read-only preview do not close it.
The retired umbrella retains the original family discussions verbatim; current
rules, rationale, definitions and open decisions have live homes above.

## Follow-up chat, Oct 25, 2026, 12:33 -05:00 (verbatim)

Coverage: E13 owns automatic protection and calibration; N2-N6/N9-N10 own
family naming, provenance, migration and display; actions owns override/undo;
cast C2 preserves the decisions across rebase. No live batch is authorized here.

<!-- markdownlint-disable MD013 -->
```text
I would like to auto-protect photos in a protected person that reach a high enough likeness score so that I don't have to manually do that.  For an unprotected identity - if we determine that we have enough photos to establish an itentity, we should also auto-protect that person and the photos.  It'll be easier for me to unprotect and move images out and rebase if that's required in order to keep things clean - but I feel like that's a solid enough plan - and that would go along with the family relationships we establish for high likeness to another person, but not enough to merge them but establish the family name.  When we do that - I think we need to keep the original name of the person that was either provided and/or randomly assigned as well as the new person with their family name.  We display character name (with family) along with a note on the original name.  Sort of like we do with the sisters, but if we also have the person join a family we'd have the character name, person name (now) and original person name.  We'll need to update plans and get this work going as I think all this is critical in order to complete the intake and likeness process as a whole and retain the proper identities along the way and show them in the gallery views where it makes the most sesnse.  Think deeply and let's get this going.
```
<!-- markdownlint-enable MD013 -->

## Original-name correction clarification, Oct 27, 2026 (verbatim)

Coverage: N11 decision and N12 implementation above; intake remains first.
No live identity metadata is changed by recording this clarification.

<!-- markdownlint-disable MD013 -->
```text
If I am forcing a change to the original name - which was mis-assigned due to bugs in our previous processing automation, I want that to replace any original name that was mis-assigned and re-establish the persons proper original identity and name.  Hope that clarifies my intent.  The reason things were mis-assigned or swapped were either early bugs in the likeness promotion process to swap prospects to angels or sisters - or I simply just dumped things into Various/gallery and let random assignments happen and now want to correct that because I was being lazy and now I know a person's real identity - even if we assigned them a random one.  Does this make sense on why I am wanting to be able to do that - after we get this intake processing for images working?  Both the image processing and re-establishment of original names is important and then making sure the family naming can happen which may change their first/last names based on how we want that to work?
```
<!-- markdownlint-enable MD013 -->


## Oct 30 source snapshot: various_people_names.md

Source: `feedback/various_people_names.md`. Coverage: N12/N13. SHA-256: `dbe7ade104af67ddee7f4235cf7108b24c63887f8c4bc6102d620b25ca2ea1fc`.
Captured for planning; open tasks are not implementation acceptance.

<!-- markdownlint-disable MD013 MD009 -->
````text
# Various People Names

## High Level Understanding

I want to ensure that if I send in a photo through a Various/[people name] - such as Various/Ela Model that what I am asserting is all the images in here are in fact Ela Model as the name and that if they match up with someone else that's already in the library/gallery as another name - most likely just a random chosen name - that I am asserting the following:
    - This IS the original name of the person in the images
    - I want the name of this person to be Ela Model (in this case)
    - If it pairs with existing photos I would want to merge these and history to make the identity know as Ela Model.
    - If this person is already assigned to a character slot, that's great - we'll bring all these into the gallery and de-dupe them as part of the process.
    - I would assume if there is already a core identity we'd bring these into that mix and ideally the score of all of them will align.
    - If some scores are low they can either stay in the gallery with a low score or end up in review based on thresholds.
    - This is a scenario, where I have pulled images (maybe made a mistake where I put it - hence a review photo) and they all should be that person
    - If other images are spread out across the gallery that are matching the likeness, I would hope that we'd also pull them into Ela Model's gallery and use thresholds where to put them.
    - That could retire a likeness/name already or just pull a few images.
    - If I reject them, then can go back through and land somewhere else
    - If I retire them, I just don't want them in the pool

There's probably more I'm missing so ask me some questions about it as we go along.

In my mind, this is one way to rename or re-claim the proper original name for a person in the gallery, even if I supply some duplicate photos as well as new ones.  I can use this process over time to self-heal, organically grow and fix names of people.

## Photo Matching

On the other hand, if I just dump a bunch of photos into the Various/gallery directly - then I am assuming they will just match where they match and possible drive a new core identity and pull other images of likeness to them and I am not caring so much about the original name as I may not know what it is and allow the likeness process to assign a random name based on the rules we have in place.

## Photo Naming

I also have a scenario, where the .jpg or .png files don't follow a hard-and-fast naming convention.  I would still want to be able to process those and assign a unique id for the image and get it into the flow and named properly.  This happens if I pull camera photos instead of downloads or I pull them from somewhere else.  So we'll have to adapt the intake so it can handle various names of any .png or .jpg (or other image files) that I might want to ingest over time.

## History Tracking

I am thinking that the z_ .txt file might be useful for summarizing images moving in/out of an identity as well as renamed, assignments to slots, demotions from slots, retirements, and rejections.  This would give a historical record of how images have been managed and allow for better tracking and auditing of changes over time.  I can't recall what we already track so this might be an area to revisit - unless there is another place we can look at an identity and see what has happened in the past.

````
<!-- markdownlint-enable MD013 MD009 -->
