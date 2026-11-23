# 2026-11-02: library directory layout - separate galleries from intake/processing

**Status:** holding (domain contracts and deferred layout backlog; current execution transferred)

**Resume gate:** select a remaining layout task through the reset spine;
do not reactivate this entire historical checklist.

## Milestone transfer record

Nov 5 16:45 authorization: LY4 and LY11 execution moves to the
[reset spine](2026-11-05-priority-reset.md#execution-spine), same task IDs.
The source entries below retain complete contracts, decisions, historical
commands and evidence, not open execution checkboxes. All other unfinished
LY tasks stay holding here, including cap, maintenance and retirement scope.
N15 installed-family/history acceptance is merged into the spine's LY4;
no extra reset/intake or snapshot retirement follows from that transfer.
Earlier scheduling is dated context, overridden by the spine.

## Nov 21: multiple studios and transition proposal

**Status: discussion proposal, not an approved architecture or active
execution lane.** This section owns the cross-studio layout and transition
discussion; the exact new request is preserved at the end of this plan.
Existing rules and the current Queue focus remain in force. No new intake,
directory creation, move, matching run, policy change, workspace deployment
or Production write is authorized by this proposal.

### The goal and current starting point

The user wants **female people, male people and creatures/animals as
top-level separations**, with three tiers for each and separate intake,
galleries, applicable rules and workspace use. The three tiers are a
developing concept, not yet three final names or nine approved directories.
The user's clarification below supersedes the earlier A/B framing. Moving
between tiers, comparing new images to existing likeness without changing
those existing identities, and routine processing without a Sandbox are
important goals.

The current Production-root top-level names were inspected read-only on
Nov 21: `Angels`, `Sisters`, `Prospects`, `Potentials`, `Artists` and
`Various` are peers alongside operational folders. This is a directory-name
observation, not a full inventory or permission to reorganize them. The
[likeness guide](../art/likeness.md#folders-and-categories) also describes
Models as a distinct sandbox category. `Various` is a mixed intake/hold
pool, not a person; `Artists/<Artist>/<Person>` is a separately scoped
domain. Existing Artist provenance is protected from automatic cross-artist
and general-library reassignment by the
[current runbook](../art/original-photos.md#the-library).

Today the selected normal intake described in
[likeness](../art/likeness.md#normal-selected-photo-intake) selects
pending/selected `Various\gallery` photos and uses the eligible current
identity inventory; it is not already a general multi-studio selector.
Current retained manifests bind photo ID, bytes, owner path and matching
domain. Cross-domain retained-set transfers and whole-person moves with
retained sets are held, not a supported studio migration
([original-photo runbook](../art/original-photos.md#the-library)).
Existing paths, caches, receipts and recovery journals therefore cannot be
assumed portable merely because a folder can be renamed.

### Working model: separate concepts, not decisions

| Concept | Proposed meaning | What remains to decide |
| --- | --- | --- |
| Studio | A user-facing collection with an intake, galleries and policy context | Names, physical roots, exclusive tier ownership and cross-tier conflict handling |
| Category | A role/status within a studio, such as Sister, Angel, Prospect or Potential | Which categories exist in each studio and whether they mean card rank, casting readiness or something else |
| Subject/comparison domain | The explicitly selected compatible population for detecting, grouping and matching | Female/male/creature and creature-kind boundaries, mixed-subject safeguards, and any authorized exceptions |
| Person/creature identity | A stable identity with names, evidence, history, protections and optional character-slot association | Shared versus studio-local identity IDs and how cross-studio references are resolved |
| Photo and source | Original bytes, photo ID, provenance, retained processing and membership decisions | Single canonical copy versus separately owned copies, and duplicate/version handling |
| Intake | A studio's loose pool plus optional named-person submissions | Display name `Intake` versus `Various`, exact folder syntax, and named-folder protection |

These are separable dimensions: a person's studio, category, character role,
subject type and card use need not all be encoded in one folder name.
This is a way to discuss the design, not a new schema. In particular,
changing a category must not silently change a person's identity or the
meaning of a chosen character slot.

### Requested planning order: named intake, studios, then Gallery/workflows

The user now prioritizes clarifying and accepting named incoming folders under
`Various` **before** restructuring the studio directories. First resolve the
named-intake contract for both `Various\<Person name>` and
`Various\<Person name>\gallery`. The user selected direct-root photos as
part of the named intake as well as the existing `gallery`/`review` children.
Keep child Review semantics distinct; acceptance for processing is not
automatic Gallery membership. Preserve source paths and treat duplicate
content under either location under the normal duplicate rules. Keep this
distinct from the unnamed `Various\gallery` pool. Reuse N12/N13, I24 and
I75; this is a target contract and acceptance priority, not a claim that the
current scanner supports direct-root photos or permission to run it.
The [decision source](#nov-22-named-intake-path-decision---verbatim-form-answer)
is preserved below.

After the named path behavior is defined, proceed with the proposed studio
organization in the user's intended order: split the female collection into
three tiers first, then work on males, then creatures. Category rules and
exact migration remain open. The user selects separate physical
folders for the three tiers within each subject group, rather than only
tier-specific views over a shared people library, and names them Apex, Forge
and Lab. Each tier has its own folder named `Intake`; the existing `Various`
layout remains in use until a separately authorized migration. Eligible
incoming photos may still route to an existing person in another tier under
the selected cross-tier matching rules below.
The user expects intake to work with the studio organization, but the path
rules should not wait for the full studio migration.

Per-workflow photo selection and generated-image intake are a later Gallery
evolution, not a single person-wide photo choice. The intended direction is
for each workflow to have its own selected source, which may be an accepted
Gallery image or a ComfyUI-generated image. A selected generated result may
later be shown alongside a person's Gallery with its generation/source
lineage. The user says generated images must never enter the likeness core and
selects an actual Generated directory inside each person's folder, visible
alongside Gallery and Review. Generation alone does not make an output a
trusted identity photo or automatically accepted Gallery original. Keep this
future need visible in the
intake/studio data contracts, then coordinate its detailed design and
implementation with manual-prompt P12/P19/P20, rendering R44, intake I21/I23,
and Gallery L12/L19. Those owners already cover output organization, workflow
routing, retained versions and Gallery navigation; this plan creates no
parallel path builder or Gallery implementation.

This sequence is a holding-plan priority, not a transfer into the active
spine. It does not authorize file intake, directory creation/movement,
workflow changes, generated-image publication or Production writes.

### Nov 21 clarification: three subject groups, three tiers

The user describes this **direction**, not a finished taxonomy or permission
to implement it. A simple discussion sketch is:

| Top-level group | 1. Apex | 2. Forge | 3. Lab |
| --- | --- | --- | --- |
| Female people | Established/signature characters, e.g. Sisters | People primarily intended for lower-tier cards | Image sets of uncertain card use and free-form experimentation in a separate workspace |
| Male people | Established/signature characters, e.g. Bound | People primarily intended for lower-tier cards | Separate intake and experimental workspace use |
| Creatures/animals | Established/signature creatures | Creatures primarily intended for lower-tier cards | Separate intake and experimental workspace use |

These are working descriptions, not a list of existing folders, a claim
that every subject has the same processing model, or a requirement to
duplicate source bytes. Each tier will have a separate
physical folder; exact paths and safe migration are not yet designed. The
user distinguishes tier 2 as
primarily intended for lower-tier cards and their `data/art`-supported
workflows, while tier 3 is for experimenting with image sets whose eventual
card use is uncertain and more free-form ComfyUI work. This is intent, not a
claim that every tier-2 person already has card data or that tier-3 images
can never become cards. The user selects `Apex` for the upper tier, `Forge`
for the lower-card tier and `Lab` for the experimental tier across female,
male and creature groups. Category rules, workspace mapping and promotion
criteria remain open. The
user wants to promote or demote between tiers; the
whole-person movement and cast replacement decisions are described below;
their transaction and other dependency details remain to be specified.

For people in Forge, the user selects Potentials and Prospects rather than
the cast-oriented Models category. Potentials are newer identities with a
small photo set; Prospects are more established identities for lower-card
work, not automatically Apex cast candidates. The current draft's one-to-four
versus five-or-more usable Gallery photos is a starting point to validate,
not an implemented Forge policy. Do not infer a tier move from category
classification. The user selects the same Potentials and Prospects
organization for Lab identities; in Lab, Prospect means an established
identity, not that it is planned for a card. Within Forge or Lab, transitions
between Potentials and Prospects are automatic under the applicable rules as
qualifying photo counts change; these are not tier moves. Design protection,
transaction and recovery handling. Creature-specific matching and
classification details remain open.

For creature studios, the user selects isolating matching by creature kind:
for example, horses compare with horses, not dragons. Define the kinds,
their selection, mixed/unknown handling and a suitable matching model
before implementation; do not infer species from similarity alone.
The user defers deciding whether creature-kind selection is manual,
automatic or a combination.

The user selects a separate Artists studio with its own rules rather than
treating Artist solely as provenance inside the three subject-tier groups.
Its categories, matching boundaries, relationship to people in other studios
and migration remain to be designed. The user confirms Artist collections
are a protected exception to the one-tier-per-person rule: the same person
may appear in an Artist's collection and a subject tier without moving
the Artist's photos. Artist-owned photos remain exclusive to the Artist
studio and are not usable in the person's subject-tier Gallery. The user
selects keeping Artists matching isolated:
do not compare its people against subject-tier identities, even for
advisory suggestions. Existing Artist provenance and protections remain in
force; this does not authorize moving Artist files or merging identities.

For normal subject-tier intake, the user selects the female, male or
creature/animal group manually by where photos are placed. Automatic
subject detection or routing is not selected. A photo containing subjects
from different groups may be processed when the intended main subject is
clear, for example a woman holding a dog in female intake. Apply the
applicable detection, crop and quality safeguards; do not treat incidental
subjects as identity evidence or silently cross matching domains. Specify
how to identify the intended subject before implementation. If the software
cannot reliably determine the intended subject, the user selects its best
automatic guess with a visible flag. Do not invent a measurement if no usable
subject is detected, or relax existing quality/core-vote rules; no new detector
or numeric threshold is selected.

The user selects **one tier at a time per real person**: promotion or
demotion moves that person's tier instead of leaving them in both. This
does not decide canonical-original storage or whether a person can serve
multiple card roles. Promotion or demotion moves the whole identity and all associated
photos together, including Gallery, Review and Generated, preserving name
and history. The user selects tier moves only when they initiate or approve
them, not autonomous movement based on matching scores. The selected
automatic promotion of their chosen cast replacement is part of that
user-initiated replacement, not an independent autonomous tier move. Design
the transaction, fixed-character conflicts, protections, workflow-selection
effects and recovery before implementation. The user restricts each workspace to original Gallery photos owned by
its tier: a top-tier person's original cannot be selected for a separate-
workspace-tier workflow. In contrast, ComfyUI-generated images may be selected
from other tiers, including after selected outputs are pulled back into a
person's Gallery. Preserve generated-source lineage and distinguish it from
originals regardless of Gallery presentation. Generated-image ownership and
subject boundaries remain open; this does not authorize any workspace change.
Cross-tier similarity remains advisory, not proof of identity. When photos arriving in the separate-
workspace tier are confirmed to be a person already in the top tier, the user
selects adding the incoming photos to that existing person in the top tier,
rather than moving the person or retaining another tier membership. Comparison
itself stays read-only; the subsequent addition changes the destination tier
and needs a safe, traceable transaction. Qualifying incoming photos may enter
the existing matching core under its normal core-quality rules; the comparison
alone never changes that core. For a new non-duplicate photo, the user
accepts all normal automatic matching rules, including the required rival
margin, as sufficient for this addition without separate human confirmation.
The naming-only rival-margin exception does not waive photo-admission gates.
The reverse direction follows the same approach: a top-tier arrival that
qualifies as a lower-tier person goes to that existing person, without
automatically promoting them. Define duplicate handling and the exact
operation/transaction before implementation; this decision does not
authorize a current library run.

If the person being demoted currently fills a Sister or Angel slot, the user
requires selecting a replacement before the move. Keep the character's fixed
name and history; do not silently unassign the slot or choose a replacement.
If the selected replacement is in a lower tier, automatically promote their
whole identity to the top tier as part of the replacement. Automatically
choose suitable photos of the replacement for affected workflow selections;
keep each workflow's own binding rather than assuming one photo for all.
If a workflow has no suitable replacement photo, the user selects proceeding
with that workflow explicitly unavailable and flagged, not retaining the
demoted person's now-ineligible photo as a usable selection. Preserve prior
bindings in history and undo. Specify selection criteria, eligibility, conflicts
with other fixed slots or protections, coherent publication and rollback.
This selected design does not authorize an actual tier move or workspace write
now.

The user selects exclusive character use for a person assigned to a Sister
or Angel: do not also assign that person to generic cards. Preserve their
single identity and tier. Define how the role restriction interacts with
generated-image inputs and existing workflow bindings; cross-tier selection
of a generated image is not, by itself, permission for a generic-card role.

For the third, separate-workspace tier, the user selects automatic identity
grouping for unnamed photos, as in the main library. Named submissions remain
supported; comparison against other tiers remains read-only, with qualifying
incoming-photo additions handled separately as above. This sets intended
behavior, not exact paths, a creature-matching model, run authorization or
an implemented capability.

The card documents offer useful **analogy, not an automatic rule**:
[deck rules](../design/deck-progression-rules.md#rarity-costs) identify
Transcendent Sisters and Mythic Bound/Elder Dragons, and Rare-Legendary
starter heroes. The [art direction](../../data/art/README.md#future-direction-organizing-templates-by-raritycard-type-documented-not-built-yet)
discusses richer signature art, simpler unit art and separate studio tests;
it explicitly defers a template taxonomy. Card rarity, hero versus unit,
the art pipeline's “studio” stage and this proposed photo-library studio are
different concepts. No rarity cutoff or automatic mapping of a photo/person
to a card tier is established. Angel Primes include both male and female
characters; do not assume every `Angels` entry belongs in one subject group
solely from its category name.

**Working recommendation:** present the three subject groups and their
three tiers simply in the library UI. A possible physical sketch is
`<library>\Females\<tier>\...`, with corresponding male and creature roots;
these paths are examples only. Each tier has a separate physical folder;
canonical storage and shared versus separate records remain open. Enforce
boundaries beyond folders; avoid building a shared-asset system or nine
independent engines merely to draw this chart.

### Routine work versus development and rebasing

- **Normal arrivals:** process only the selected arrivals in their chosen
  subject/tier, retaining source names and provenance. The user wants named
  sets kept out of unrelated pools and available to their own workspace.
  Cross-tier comparisons are advisory; for the confirmed same-person case
  above, the user selects adding incoming photos to the existing person
  whether the arrival is from a lower or the top tier. Similarity alone is
  not identity confirmation, and the actual
  addition remains subject to applicable admission, protection and recovery
  rules.
- **Scoped rebase:** if a tier needs reassessment, scope it to that tier
  rather than automatically reprocessing thousands of photos in all tiers.
  Design an optional, explicitly scoped read-only comparison against
  compatible existing reference identities. Preserve their photos, core,
  membership, names, protections and selected workflow inputs; changing a
  reference or moving a result requires a separate authorized operation; the
  confirmed incoming-photo addition above is a distinct selected target
  behavior, not a side effect of comparison.
  Report source, target, score, model/reference version, exclusions,
  conflicts and stale/missing evidence. The exact candidate policy and
  resulting review action remain user decisions.
- **Efficiency without silent gaps:** reuse verified, current reference
  evidence where possible and measure actual work, rather than promising
  constant-time comparison. If evidence is stale or unavailable, report it
  and require a scoped refresh or explicit incomplete result; never drop
  rivals silently. Compare unchanged incoming bytes, intended candidates,
  result quality, I/O and timing when assessing the approach.
- **Sandbox role:** the intended steady state is a protected normal library
  workflow without standing up a Sandbox for every intake or comparison;
  Sandbox remains for major development changes and separately selected
  rehearsals. This goal does not lift today's Production cutover gates.
  Existing `library.cmd` already scopes normal arrivals and reuses valid
  identity evidence, but its full-library/live acceptance is still gated;
  it does not establish a three-tier rebase, named-set protection, or
  cross-studio advisory comparison. No run is authorized here.
- **Separate ComfyUI workspace:** route explicitly selected source photos
  owned by that workspace's tier to the intended workflow, without
  repointing the main studio's character inputs or replacing its workflows.
  Cross-tier original Gallery-photo selection is not allowed, even though
  read-only likeness comparison remains possible; generated images may be
  selected from other tiers, including after Gallery pullback. Photo studios
  and ComfyUI workspaces are distinct; generated-image ownership and other
  pullback semantics remain open. Existing
  [workspace P19/P20](2026-10-22-manual-prompts-to-art-library.md#nov-5-1635-bounded-workspace-decisions-before-implementation)
  and [reference-rendering R44](2026-10-25-reference-rendering.md) own
  workspace mapping, source binding and deployment; their remaining gates
  still apply. The generic Females reference pilot is bounded, not a
  complete arbitrary-image runner.

### Named-intake clarification: original-name recovery

The user clarifies that a supplied folder name such as `Ela Model` asserts
the person's **original name**. It is also a way to repair a name lost in
earlier grouping or discovered later. A submission may contain both new
photos and exact copies of photos already in a differently named identity.
The desired outcome is the correct original name and the person's qualifying
photos/history together, not a new random name that absorbs Ela. Normal
Models/Prospects/Potentials classification still applies.

Use the existing [N12/N13 naming owner](2026-10-22-identity-family-naming.md#oct-30-named-and-unnamed-various-acceptance-contract):
a correction can retain an existing stable person ID while changing its
erroneous effective original name; the user-facing name need not determine
which internal ID survives. Retain the old name in history and undo, keep
fixed character slots distinct, and preserve photo IDs, content, retained
history, explicit rejections, locks and selected workflow inputs. Distinguish
an intentional named-folder correction from ordinary N14 oldest-original
merge continuity; do not silently let an older generated name defeat the
user-supplied original.

For a new named batch whose photos do not form one reliable core, the user
selects automatically choosing the best-supported group to carry the
supplied name rather than requiring review or a manually chosen anchor. In a
comparison between a coherent six-distinct-photo group and a coherent
two-photo group containing an existing exact duplicate, the user selects the
larger group for the name. An exact duplicate shows continuity but does not
by itself override the larger group's support; duplicate copies are not
independent votes. When an eligible smaller group is much more internally
consistent than a larger one, the user selects balancing group size and
matching strength rather than always preferring either. The balance has no
selected formula; calibrate and test it against representative cases without
changing normal formation gates. For equally large and similarly consistent
groups, the user selects the group with an existing exact duplicate as the
tie-breaker when only one has one. If equally supported groups have no
distinguishing duplicate, choose one automatically and show the choice. Specify a
deterministic, repeatable tie-break using stable source-bound evidence and
record the tie; do not present it as proof of identity. Route the other
groups' photos normally to an existing or new identity or Review as
appropriate, following matching, quality, protection and duplicate rules.
Define coherent-group eligibility, insufficient evidence and acceptance cases
before implementation. Preserve the submitted-name assertion and photo/source
history, and make the selection and reasons reviewable. This does not
authorize an indiscriminate merge of existing identities.

**Nov 21 decision:** a named folder expresses the user's correction intent:
create an identity with that original name or automatically correct the
original name of the established matching identity, without asking again in
a clear case. Preserve its previous names and history. This applies to the
person behind a Sister/Angel as well; their character names and fixed slots
remain locked. The user also reports a case where both original and current
person names were incorrectly altered. The user now selects changing the
person's current display name to the supplied original name as well in a
clear named-intake correction, including when a different family name was
previously assigned. Preserve the previous current/original names and family
history; do not change a fixed character name or slot.

Use normal evidence and preserve protections; a different recorded name is
not by itself a reason to ignore the user's explicit correction. A duplicate
proves photo continuity, not that every member of an old group is the same
person. When the chosen named group matches two established identities about
equally, the user selects automatically choosing the best-supported existing
identity for the name and showing the choice, without merging those people.
Where both match well but their lead is below the usual rival margin, the user
allows this automatic **name correction** despite that margin and wants the
close rival shown. This exception does not bypass photo-admission rules or
genuine protections, merge identities or change fixed character names.
Define the competing-match evidence, ties, minimum acceptable match and
no-evidence case before implementation; retain both candidates and the reason
for the choice. Record the correction and make it reversible; this is selected
target behavior, not a claim it is implemented or permission to run.

**Name collisions are different from identity ambiguity:** the user wants
the asserted name assigned to the identified person even if another identity
currently has that name. Resolve the name conflict by a name swap or a new
random name for the other identity; do not merge the people or reject the
asserted name just because it is occupied. Preserve each identity's ID,
photos, evidence, prior-name provenance and history; show both changes and
support all-or-nothing recovery and exact undo. Preserve fixed character
slots. The user prefers a **swap** over a random name, unless the prior name
is used with many other names; inspect identity/name history and choose the
best safe resolution rather than blindly swapping. The user clarifies that
the current Production snapshot can contain unreliable name history because
identities changed repeatedly through pre-Sandbox bugs and processing
issues. Therefore, a long or conflicting name history is not by itself
evidence that a previous name belongs to the identity that would receive it:
assess the reliability and continuity of the underlying records, not just
the number of names. Define the evidence and how original/current fields of
the displaced person change; no numeric threshold is selected. When the
person is clearly identified but history cannot support a safe swap, the
user selects assigning the other identity a new random name automatically,
not holding solely for unreliable name history. If that other identity's
recorded original name is also wrong and its real original is unknown, use
the new random name as both its current display name and recorded original;
mark it generated, not a verified real name, and retain the incorrect name in
history. Preserve both identities and fixed character names; never guess a
swap or merge people. Coordinate the existing confirmed two-person swap A3;
it is not proof that automatic named-intake collision handling is implemented.

For the future collision decision, review the history of **both** stable
identities and distinguish supplied, generated, current, original, family
and fixed character names. Record which previous name is considered for the
swap, its provenance and prior associations, the evidence supporting the
choice, and the proposed changes to each identity. A prior name appearing
in history does not by itself prove it is suitable for the other person.
Legacy Production history may reflect misnaming and identity churn rather
than trustworthy continuity; identify which evidence predates the known
issues and what can still be verified. Do not invent a count or treat
unreliable history as a basis for an automatic swap.

The acceptance matrix should cover a preferred swap with suitable history,
the automatic random-name fallback when a swap is unsuitable or history is
unreliable, and multiple occupants of an asserted name. It must also
cover a fixed cast character name, repeat intake, interruption and exact
undo. Near-equal existing matches follow the selected automatic choice above,
not the earlier blanket ambiguity hold; an occupied name is a separate name
collision, not an identity ambiguity. Define remaining unsafe or unsupported
cases and show any unresolved collision rather than silently merging.

The user wants the name to stay with the core and **high-scoring photos
protected**, while recognizing that a very low-scoring photo may be an
accidental inclusion. Do not equate every expression/pose variation with a
wrong person, or make every incoming photo an unquestioned core anchor.
Preserve the submitted set's source evidence and evaluate individual photos
against appropriate core/quality evidence. For ordinary named intake or later
normal processing, the user selects automatic reassignment of a very
low-scoring submitted photo to a stronger eligible match when normal matching
and protection rules allow. This is per-photo, not a whole-identity merge;
retain source/name history and make the move traceable and recoverable.
Existing explicit protections are not silently bypassed. The low-score
boundary and protection acquisition remain open. If a very low-scoring
photo has no eligible rival, the user selects normal unassigned-photo
routing, including a new identity when eligible, rather than a special
named-folder-only hold. Apply the relevant quality, routing, formation and
protection rules; preserve the asserted name and source history even if the
photo is assigned elsewhere or held. Name intent and a matching score do not
establish that every member of an existing mixed group is the same person.

For ordinary refinement of an established named identity, the user selects
a stricter eligibility boundary for its explicitly named non-core photos
than ordinary below-category-entry refinement: the own-identity score must
also be orange or red (strictly below 0.30). Both conditions apply, without
rounding the boundary; an unavailable score is not a low score. This does
not change initial named-intake eligibility, special rebase release,
destination gates or genuine protections. The selected no-rival normal
routing above is a named-photo exception to ordinary refinement's usual
requirement for a qualifying rival; specify its source/reference handling
and apply normal safety and recovery gates before implementation.

For later ordinary intake, the user also selects releasing a one-photo named
Potential for normal rescoring like other one-photo Potentials, despite its
unavailable own-identity score. Apply the selected small-Potential intake
policy and normal protection, matching and routing safeguards; preserve the
asserted name and source history regardless of the resulting placement.
This does not make an unavailable score low or bypass a genuine lock. Resolve
identity/name continuity and any emptied-folder retirement through their
existing contracts, not by silently discarding the name.

An illustrative acceptance case is a uniquely bound existing photo
duplicated in `Ela Model`, alongside new Ela photos. Show the duplicate,
existing owner and source-name provenance, eligible per-photo matches,
automatic correction and any conflicting or low-confidence members. Preserve
history and use the accepted duplicate/version disposition; do not create an
extra person just because a filename differs or delete source evidence.
Exercise same-person continuity without swallowing an entire mixed group,
and verify repeat intake and exact undo. Comparison across studio tiers stays
advisory; any cross-tier move or correction has its own authorization.

**Still to decide:** protection evidence and initial named-intake outlier
eligibility; the evidence for the preferred swap versus fallback and effects
on the other person's names; competing-identity minimum evidence, ties,
no-evidence cases and explicit locks. The named refinement cutoff and naming
margin exception are selected, not implemented.

### Matching, intake and identity safeguards to design

- Select each operation's studio, subject-compatible population, policy and
  profile explicitly. Do not compare or route female people, male people,
  Artists or creatures across an unapproved subject/provenance boundary.
  The intended cross-tier likeness comparison within a compatible subject
  group is advisory and does not change the referenced studio. When the main
  subject is unclear, use the best automatic guess and flag it, without
  relaxing quality or core-vote safeguards or inferring identity, gender or
  species from similarity alone; preserve Artist provenance. A separately
  transacted addition of qualifying incoming photos to their existing person
  in another tier follows the selected rules above.
- Keep each studio's loose intake distinct from a named-person submission.
  For a future named intake such as `Various\Ela Model`, record the supplied
  original-person name and source provenance, retain every submitted photo
  and show the asserted relationship, potential matches, duplicates and
  conflicts. A declared name is user intent, not proof that every detected
  face is the same person.
- **Important current distinction:** the legacy `seed` path scans
  `Various\<Name>\gallery` and `review`, matches an existing general person
  by name or creates a Prospect/Potential, and does not face-match the set.
  The legacy incremental flow is paused under the draft-policy gate.
  Prepared sandbox named intake exists, but
  [N13](2026-10-22-identity-family-naming.md#oct-30-named-and-unnamed-various-acceptance-contract)
  still owns the full Ela Model/name/duplicate/matching acceptance matrix.
  Neither fact proves that every submitted photo receives the requested
  persistent protection or that a direct `Various\<Name>` folder of loose
  files is accepted. Do not run that 11-photo trial without selection.
- Apply the user's clarified goal of protecting high-scoring named-intake
  photos, not a blanket claim that all photos must be locked. Specify
  protection acquisition, existing explicit overrides, low-score/mixed-face
  Review, core eligibility, duplicate/version and undo behavior. A protected
  photo can be retained without being a trusted matching anchor; no score
  alone should defeat an explicit lock.
- Define promotion/demotion as the selected **whole identity** move, with
  all associated photos. Individual photo reassignment remains a distinct
  operation, not a partial promotion. Preview the source/destination, reason,
  stable IDs, proposed membership/slot/category changes, name/history and
  protected or selected-workflow conflicts. Preserve originals, Review states,
  rejections, anchors, crop lineage, derivatives and prior history.
  Enforce the selected one-tier-per-person rule; design ownership and
  transaction details without assuming a physical copy model. Never infer a
  person is the same solely from a name or resemblance.
- Benchmark only after the comparison populations and equivalent desired
  behavior are defined. Smaller eligible populations may reduce matching
  work, but also change candidate recall; measure both runtime/resource use
  and missed or incorrect matches on the same bound inputs. No speedup or
  matching-quality improvement is claimed from folder separation alone.

### Proposed transition gates

1. **Settle named Various intake first.** Coordinate N12/N13 and I24/I75 to
   specify `Various\<Person name>` and its `gallery`/`review` children,
   including the selected acceptance of photos at the named-folder root.
   Also specify duplicates, mixed or ambiguous submissions, original-name
   correction, protection and exact undo. Keep the existing unnamed
   `Various\gallery` behavior distinct.
2. **Agree on the studio/tier model.** Resolve the questions below, including
   the three female tiers first, then the male and creature categories,
   comparison domains, exclusive tier ownership, promotion semantics and
   whether generic and cast roles may coexist. Keep per-workflow image source and future
   generated-image Gallery lineage as data-model constraints, not this
   migration's implementation.
3. **Inventory before designing migration.** Read-only, with exact roots and
   revision: enumerate active source folders and identities, named/loose
   intake, IDs and collisions, protections/rejections, character/workflow
   selections, Artist provenance, retained preparation, caches, reports,
   links, backups, receipts and old-format readers. Map every source to a
   proposed destination or explicit hold, including unknown and mixed cases.
   Never classify live source folders as disposable cleanup.
4. **Specify and fixture-test contracts.** Coordinate naming N12/N13 and
   intake I75, actions A1/A2/A6, current processing rules, workspace
   selection and storage S27 rather than inventing parallel engines.
   Preserve stable IDs and exact source bytes; make collisions, invalid
   lineage, unsupported domain transfers and occupied destinations explicit.
   Prove preview, interruption, recovery, undo and stale/external-edit refusal.
5. **Rehearse a small, separately authorized Sandbox slice.** Use a
   source-bound inventory and representative synthetic/approved cases:
   one named and one loose submission, a duplicate, a mixed/ambiguous folder,
   a protected item, a cast/generic promotion and demotion, an Artist boundary
   and a creature/people boundary. Exercise one scoped rebase with
   advisory comparison to a read-only compatible tier: reference photos,
   membership, names, protections and workspace bindings remain unchanged,
   with stale evidence explicitly surfaced. Confirm counts, names, original
   bytes, links, previews and rollback before any wider processing.
6. **Compare and review before any cutover.** Measure matching quality and
   runtime with comparable inputs; inspect actual studio Gallery/Review,
   intake and history in a browser. Keep human identity/crop acceptance
   separate from fixtures. A Production transition requires its own approved
   manifest, independent verified backup/restore, conflict plan, cutover and
   rollback authority. Preserve the old working library and historical
   evidence until their dependencies and dispositions are individually
   verified; no wholesale reset, deletion or shared-workspace retarget follows
   from accepting a sketch.

### Later Gallery and per-workflow image lifecycle

After named intake and studio/tier boundaries are established, refine the
Gallery beyond unassigned Intake and existing identity photos. Keep
per-workflow source assignments separate: one person may have different
inputs for different workflows, and each binding must identify the exact
source item and its lineage. Support a reviewed ComfyUI-generated item as a
possible source without replacing the workflow's binding to a Gallery photo
or another generated result implicitly.

Generated outputs need an explicit route back to a suitable Gallery or
review surface, with source workflow, input, recipe/settings, output bytes
and identity/studio association preserved. The user confirms generated images
must **never contribute to the likeness core** and selects a physical
Generated directory under each person's folder, shown by the viewer alongside
Gallery and Review. This is future target behavior: current pulled renders
remain in the existing separate synthetic store until an authorized,
verified migration. On promotion or demotion, the user selects moving the
Generated folder with the person while retaining valid workflow links and
history. When two identities are established to be the same person and
merged, generated images from both go into the surviving person's Generated
folder, preserving their original lineage and valid workflow links. Handle
name/content collisions without overwriting outputs or erasing history.
When an original photo is reassigned to another person, the user wants its
generated images to move with that photo. Generated-image filenames need to
include the source photo ID, with the binding also preserved in structured
lineage and generation history. Odd cases where the source is unclear from
the name or pullback need a decision. Check retained generation receipts and
other lineage; if the source remains unreliable, the user selects keeping the
generated image where it is and flagging it for their decision, not guessing
a photo or silently moving the output. Define how to handle
generated-on-generated, multiple-input and legacy outputs without inventing
an ID or rewriting historical receipts.
If an output uses photos of two people and a source photo is reassigned, the
user selects keeping the output in place and flagging it for their decision,
rather than automatically choosing an owner or copying it. Define multi-input
lineage and how to represent all source IDs.
If a person's Gallery and Review originals are empty but Generated still has
images, the user selects retiring the person while preserving the Generated
folder and history. Reconcile this with the existing special stop for an
emptied Sister/Angel; the answer does not explicitly change that cast
safeguard. Retired generated images are preserved as history, not selectable
for workflows; define how existing workflow bindings become unavailable
without losing history or silently choosing a replacement.
Design rebase, rename and retirement to preserve generated files, lineage and
existing workflow bindings too; current rebase behavior can rebuild person
folders. Do not equate generation with
identity evidence or automatic Gallery-original acceptance; define review, duplicate,
rejection, retention and recovery behavior first. Coordinate this later work
with P12 and R44 for generated-output and workflow routing, I21/I23 for
version lineage, and L12/L19 for Gallery and Intake navigation. In
particular, the current [R44 output decision](2026-10-25-reference-rendering.md#oct-27-category-aligned-workflows-and-source-faithful-recipes)
keeps pulled renders in a separate synthetic-results area, outside identity
folders and likeness intake. The user's integrated-Gallery direction needs
to reconcile with that boundary: per-person physical Generated storage
supersedes the separate-store location as the selected future target, not as
a claim of current implementation. Keep generated files out of original
Gallery membership and matching cores. Existing owners and any separately
approved task transfer govern implementation; this future direction does not
authorize rendering, output import, migration or a Gallery write now.

### Questions for the user

Answer in rounds; none of these are silently settled by this proposal.

1. **Studio shape:** female, male and animal/creature top-level separation
   with three tiers each is the user's direction. Tier 2 primarily supports
   planned lower-card work; tier 3 is experimental and more free-form.
   The tiers use separate physical folders named Apex, Forge and Lab across
   all three groups. How should views and workspaces map to the folders? The
   separate-workspace tier groups unnamed photos automatically.
2. **Presentation:** what should the Sisters/Angels collection be called,
   and should its Models/Prospects/Potentials belong to that studio even
   before they are selected for a character? For people in Forge, the user
   selects Potentials and Prospects; validate their maturity rules without
   making Forge Prospects automatic Apex cast candidates. Lab uses the same
   categories without implying intended card use. Within each tier,
   Potentials/Prospects transitions are automatic under applicable rules.
3. **Generic people:** one person may occupy only one tier at a time. A
   person assigned to a Sister or Angel is exclusive to that character, not
   also used for generic cards. Define other role boundaries and how that
   restriction interacts with generated inputs.
   Original Gallery-photo selection is restricted to the workspace's tier;
   generated inputs may cross tiers even after Gallery pullback. How should
   the browser show roles and generated-image ownership?
4. **Matching isolation:** within a subject group, how should advisory
   comparisons between tiers be selected and shown? Confirmed arrivals in the
   separate-workspace tier go to the existing top-tier person, and qualifying
   top-tier arrivals go to their existing lower-tier person, with normal
   automatic photo matching; define duplicate and transaction handling. The
   user selects the subject intake
   manually and allows mixed-group photos when the intended main subject is
   clear; if it is unclear, use the best automatic guess and flag it. Define
   subject selection under the existing quality and domain safeguards.
5. **Artists:** the user selects a separate Artists studio with its own
   rules and allows the same person in an Artist collection and a subject
   tier; likeness matching remains isolated from subject tiers and Artist-owned
   photos are exclusive to the Artist studio. Define categories, internal
   boundaries and any generated-image interactions without weakening this
   original-photo separation.
6. **Creatures:** matching stays within the same creature kind. What
   categories and kinds are in scope, how are they selected, and which model
   and rules are suitable? Human face-matching behavior is not automatically
   suitable.
7. **Promotion/demotion:** changing the person's tier leaves them in only
   one tier and moves the whole identity, including Gallery, Review and
   Generated. A Sister/Angel slot requires a user-selected replacement before
   demotion; selecting a lower-tier replacement promotes their whole identity.
   Affected workflows receive automatically selected suitable replacement
   photos; if none exists, the workflow is flagged unavailable. Tier moves
   are user-initiated or approved. How are photos selected and how are other
   roles and workspace restrictions handled?
8. **Named intake:** the priority is to resolve both the named folder
   `Various\<Person name>` and the current `Various\<Person name>\gallery`
   form before studio migration. The user selected accepting direct-root
   photos as named intake alongside the children. Each future tier has its
   own `Intake` folder; define safe migration and compatibility with the
   current `Various` paths without delaying the current named-intake work.
9. **Protection:** the user selects normal-rule automatic reassignment for a
   very low-scoring named photo with a stronger eligible match and normal
   unassigned routing without an eligible rival; named single-photo Potentials
   are released for normal rescoring during later intake. Established named
   non-core photos require both below-entry and orange/red own score in
   ordinary refinement. What protection evidence and initial-intake outlier
   eligibility apply? For an incoherent new named batch, automatic
   best-supported-group selection prefers a larger coherent group over a
   smaller group with an exact duplicate in the stated case, but balances
   size with matching strength. An existing exact duplicate breaks an
   equal-size, similarly consistent tie. If no duplicate breaks an otherwise
   equal tie, choose automatically and show the choice. Other photos route
   normally; define the balance, coherence and insufficient-evidence handling.
   Preserve source/name provenance; expression or pose alone is not proof of
   a mistake.
10. **Name conflicts:** given that pre-Sandbox Production history may
    contain repeated bug-driven identity/name changes, what evidence is
    reliable enough to choose a swap? With a clear identity, use a random
    name for the other person when a safe swap cannot be determined, and
    replace its wrong, unknown-real original with that generated name too.
    How should other field combinations and explicit locks be handled while
    character names stay fixed?
11. **Storage and identity:** prefer one canonical original with references,
    a recoverable physical move, or separate owned copies? How should
    cross-tier comparisons refer to a person who belongs to only one tier?
    Workspace original Gallery-photo selections stay within their owning tier;
    generated inputs may cross tiers even after Gallery pullback.
12. **Generated images in Gallery:** the user selects a physical per-person
    Generated directory and viewer section. Generated images must never vote
    in the likeness core and may feed another workflow across tiers. Their
    folder moves with the person across tiers, and outputs combine on a
    verified identity merge. Outputs follow a reassigned source photo; include
    its photo ID in generated filenames. If retained lineage cannot identify
    the source reliably, keep the output in place and flag it for user review.
    For outputs sourced from two people when a photo is reassigned, also keep
    the output in place and flag it rather than selecting an owner or copying.
    A generated-only person is retired with outputs/history preserved;
    retired outputs are history-only, not workflow-selectable. Reconcile the
    existing cast stop and define handling of existing workflow bindings.
    Define safe rebase handling, other review, matching, ownership and
    source-chain rules.
13. **Transition acceptance:** given the requested order of named intake,
    female tiers, male tiers, then creatures, what constitutes acceptable
    quality, speed and recovery before any Production change?

### Deferred owners and request coverage

- [ ] **P2 either** LY19 First specify the incoming named-intake contract for
  `Various\<Person name>` and its `gallery`/`review` children, including
  the selected direct-root acceptance. Specify protection/name recovery and
  exception semantics. Reuse N12/N13 and I24/I75 for Ela Model, combined
  root/child and duplicate/source-ID acceptance; keep this slice ahead of the
  studio directory transition.
- [ ] **P2 you** LY16 After the intake path rules, refine the three subject
  groups and tiers, names, categories and exclusive-person/membership choices.
  Follow the requested planning order: female tiers, then male, then creatures.
- [ ] **P2 either** LY17 Specify studio-scoped intake and matching boundaries,
  tier-scoped rebase, read-only cross-tier comparison, stale-evidence and
  unknown/mixed holds, automatic grouping of third-tier unnamed intake,
  isolation and comparison/quality evaluation. Coordinate the processing
  contract and performance T29/T30; do not activate them here.
- [ ] **P2 either** LY18 Define whole-identity promotion/demotion with all
  photos, and distinguish individual reassignment, slot and membership
  operations; preserve history, protection and workflow-selection handling.
  Future source binding is per workflow, not one person-wide photo;
  coordinate actions A1/A2/A6, P12/P19/P20 and rendering R44. Generated-result
  return and Gallery lineage remain with I21/I23 and L12/L19.
- [ ] **P2 ai** LY20 Produce the source-to-destination, reference and
  recovery inventory and an independently restorable Sandbox-first
  migration proposal, including independently scoped workspaces. Coordinate
  storage S27, workspace P19/P20, rendering R44 and existing layout owners.
- [ ] **P2 either** LY21 Select the pilot and verify the agreed acceptance
  cases, actual viewers, output/quality and comparable performance before
  any separately authorized Production transition.

The user's studio examples and naming ambiguity map to LY16; subject
isolation and processing-time concern to LY17/LY21; promotions and demotions
to LY18; named intake, original names and image protection to LY19 **first**;
directory restructure, independent workspaces and non-destructive transition
to LY20; all execution and acceptance remain separate from this planning
request. The Nov 21 clarification additionally maps three subject/tier
groups to LY16; scoped rebase, advisory comparison and ordinary no-Sandbox
operation to LY17/LY21; and a separate workspace for new images to LY20
with P19/P20 and R44. The later named-intake clarification maps name
recovery and duplicate/new-photo handling to N12/N13 and LY19, high-scoring
photo protection and outlier decisions to N13/LY19, and normal category
classification to the existing processing contract. The Nov 21 priority
clarification sequences named-folder behavior before studio reorganization;
female tiers before male tiers and creature tiers. Future per-workflow source
binding and generated-image return are coordinated through P12, P19/P20,
R44, I21/I23 and L12/L19, not a second Gallery or workflow engine.

## Nov 5 16:35: one run, separate acceptance gates

The current remaining operation is saved-input continuation acceptance,
not another full Production reset or intake. LY4 collects one shared set
of installation/check exit results, diagnostics, actual run/receipt
identifiers, phase times and Gallery/Overview/Review browser evidence.
Naming N15/N16, cast C12/C13, engine E18/E19 and gallery L21-L23 consume
the relevant portion instead of launching duplicate runs. Case-specific
missing evidence remains open; a successful generic check is not proof
that every labelled scenario passed. LY11/C7 human review stays separate.
No new final result is inferred from this planning reconciliation.

Storage S27 retains its separate FULL/materialized recovery scope; the
disposable run supplies shared route/viewer/timing evidence, not proof of
a backup/restore that this profile deliberately does not create. Snapshot
or run-state retirement in historical LY4 scope is separately gated by
dependency/unique-evidence checks and scoped approval, not automatic cleanup
after a green page. Keep failed attempts and active source folders intact.

## Nov 5 14:25: current authorization and planning-only lane

LY15c's visible process task is working and the user can see/monitor it.
`postrun-lean-preview3` passed saved-preview and recap checks after the
report-only overlay fix. At 13:19 the user authorized installation and final
checks through `gallery-check`, then Gallery/Overview/Review verification.
Earlier matching-only/no-install paragraphs below are dated history.
The install is in progress at this planning checkpoint; no final installed
or viewer acceptance is claimed.

- [x] **P1 you** LY15c Walk through visible VS Code terminal execution:
  use a `process` task invoking `cmd.exe`, not the configured Git Bash shell;
  the user confirms visible progress and owns live monitoring.
- [x] **P1 you** LY15a Authorize and complete the matching-only saved-input
  continuation; verify the preview and recap before installation.
  `postrun-lean-preview3` passes both read-only checks, with 3,290 photos.
  Subsequent explicit 13:19 authorization selects installation/checks;
  LY4/N15 and LY11 still own runtime and human acceptance.

While this installation runs, only planning/feedback reconciliation proceeds.
The approved downstream concurrency slices, historical phase times and
risks are owned by [performance T20-T28](2026-10-28-intake-performance.md#nov-5-approved-downstream-parallelism-and-bounded-speed-work);
gallery L18 retains cross-page history reuse. They do not change current
implementation bindings. LY14's derivative **cap** is a separate behavior/
storage decision, not implicitly approved by agreeing to exact-output
parallelism, and is not a new prerequisite for the current pickup.
The five active feedback notes are reconciled in the
[source ledger](README.md#nov-5-active-feedback-reconciliation); their
filing does not close this plan or its outstanding acceptance tasks.

## Nov 5 final pickup preflight; terminal walkthrough next

- [x] **P1 ai** LY15b Finish bounded progress/estimate and report-read changes:
  label Nov 5 LEAN versus Nov 3 historical references, bound timing and
  execution by `--until` even on completed-preview resume, provide full
  child output with `--verbose`, and reuse Overview collection/evidence
  reads within one fully sealed operation. Record explicit
  [preview/install acceptance gates](../art/likeness.md#pickup-acceptance-gates).
LY15c's visible-terminal walkthrough is complete; see the current
authorization above for actual preview/install sequencing.

No actual matching, installation, reset or intake is authorized here.
The installed sandbox and original receipts remain available for review.
The broader L18 cross-page history refactor stays open: its dependency
invalidation requires more than this narrow operation-local change.
LY3b artifact moves, derivative caps, FAST shortcuts and intake
instrumentation remain deferred, not new pickup prerequisites.

Nov 5 11:37 authorized visible-terminal attempt: the task must run as a
VS Code `process`, not through the configured Git Bash shell, which rewrote
`cmd /d /c` and stripped launcher backslashes. At 11:46 the matching-only
attempt stopped before publication: continuity rejected an installed
Angelica Review photo whose raw Facebook name had been normalized during
matching. The installed bytes equal the original plan's `preparedSHA256`;
the guard used only the narrower filename parser. Reuse the matching ID
resolver for immutable continuity, retaining missing/unknown/ambiguous-input
checks. Keep failed `postrun-lean-preview` evidence and use a separately
named `postrun-lean-preview2` after regression verification; no installation
is authorized.

## Nov 5 10:32: finish post-run fixes; make disposable LEAN genuinely reset-only

The user approves removing sandbox LEAN backup/transaction rollback work,
not weakening quality, membership or path correctness. FULL/Production
remains protective. Keep the existing installed baseline for review: this
request authorizes implementation/testing, **not an actual replay or intake**.
The [saved-input runbook](../art/likeness.md#saved-input-lean-continuation-sandbox-only)
owns the commands and exact skip/recompute boundary.

- [x] **P1 ai** LY15 Finish and verify a separately named saved-input LEAN continuation:
  no reset/intake or generated-identity reseeding; preserve explicit manual
  decisions by stable ID/content or refuse ambiguous migration. Publish
  without backup/previous trees, record reset-required on partial failure,
  avoid duplicate stage/output hashing and repeated space-tree walks.
  Include launcher/help/menu coverage and FULL regression tests.
LY15a's matching-only authorization and verified preview are complete;
actual runtime/space/browser acceptance stays with LY4/N15, not code tests.

Implementation verification: the frozen library selection passed all 54
modules (954 tests, one environment-dependent symlink skip). After the final
seed-snapshot serialization regression and logging clarification, 94 focused
tests passed (the same skip). Policy-schema isolated smoke passed 19/19;
routine hygiene/data checks passed. Launcher inventory previews were
read-only and did not create the proposed real continuation directory.
The installed baseline and original receipts remain unchanged.

The then-protected `feedback/priority_plans_review.md` was retained for the
requested later discussion: confident cast Gallery first; then selection
review/replacements; discuss backed-up Sandbox-to-Production promotion;
restore manual `0_Edit`/`1_Alpha`; discuss generic Sovereign Females naming
and removal of its female series from Angel Primes; return to character art
through animation/video; then reassess remaining automation/priorities.
The complete source is now preserved in the priority-reset plan. This is coverage
and sequencing context, not authorization for Production promotion, prompt
mutation, workspace deployment or a broad plan reorder. Preserve/incorporate
the raw source at that discussion before any archive move (verified during
the Nov 5 reconciliation above).

## Nov 5 09:44: hold the installed baseline; assess prepared-input reuse

The user explicitly says not to start a re-run yet. Complete and test all
selected post-run changes first, including engine E18 refinement; then
present an incremental matching-only preview option using the original
run's verified prepared inputs/cache and original catalogue. No new intake
is needed merely to change matching, family or workflow-selection logic.
Do not treat the current generated identities/automatic locks as fresh
source truth. An installed-results-only refinement would not test exclusion
from the initial cast cores.

The existing receipt is applied/disposable with rollback retired, so ordinary
`--undo`/`--replan` is not a supported restart route. Do not edit its status,
policy, hashes or receipt, run `--from matching` against it, or copy all of
Working into repository scratch. A separate bounded verified replay path
is required before offering an executable command. Retain the current
Gallery/Overview/Review for ongoing human review. Full fresh-run acceptance
remains separate from any saved-measurement preview.
Evidence and skip/recompute boundaries live in the
[pinned recap](../recap/2026-11-04-1130-recap.md#nov-5-0944-prepared-input-reuse-no-re-run-authorized).

## Nov 3: authorized new source rehearsal

The 12:46 request selects naming N14/LY13, cast C11/engine E13/E14 and
recap L21-L23 as tested prerequisites to a separate complete fresh rebase.
Copy current Production through full reset; do not use installed
`fresh-20261102` identities as inputs. The reset's processed-copy provenance
excludes old generated pixels when the original remains in Production;
genuinely unique sources and review metadata stay preserved. Compact prior
run/catalogue/policy JSON is carried into the reset-review bundle for
historical recap comparison only, never auto-applied or used as match seeds.

LY12 report-state integration now uses shared gallery publication after
install, in addition to the previously tested content-ID naming slice.
The core trial, bounded in-place refinement (engine E15, added 14:17) and
final-membership audit are explicit run-local behavior;
ordinary defaults stay unchanged. Broader convergence beyond the four-pass
refinement, surname-rule acceptance and Production true-up remain gated with their
owners. LY10 stays open through fresh reset, intake, actual release/name
preview, install and Gallery/Overview/Review/recap checks. See the
[exact runbook](../art/likeness.md#fresh-sandbox-from-production-step-by-step).

**Order:** LY2/LY3 (code + tests) -> LY5 -> LY4 clean sandbox reset and LEAN
rebase on the new layout, timed with Acronis off -> storage S32/S27 acceptance
-> retire the old sandbox `_backup` snapshot and `fresh-v23` run state. No full
intake runs on the old layout. Production writes remain gated by the existing
acceptance plans.

Owners kept elsewhere: storage
[S32/S33](2026-10-28-storage-operations-and-retention.md) (replay method and
`gallery_intake` compaction), gallery
[L19/L20](2026-10-22-gallery-review-layout.md) (navigation, intake-run
retention). This plan owns only *where* things live and the migration to it.

## Current structure (measured Nov 2, stat and manifest reads only)

Sandbox `B:\Sovereign Territories Sandbox\Working`, 282 person/pool folders:

| Per-person folder | Role | People | Files | GB |
| --- | --- | ---: | ---: | ---: |
| `gallery` | accepted native photos, `z_<name>.txt` profile/history | 273 | 3,213 | 1.39 |
| `review` | photos the matcher is unsure about | 15 | 99 | 0.06 |
| `gallery_944x1104`, `headshot_944x1104`, `chest_944x1104` | maintained 944x1104 ComfyUI/viewer copies | 269/261/202 | 8,522 | 7.93 |
| `review_gallery_`/`review_headshot_`/`review_chest_944x1104` | the same for Review photos | 15 | 286 | 0.27 |
| `.photo-derivatives.json` (file) | derivative source/output hashes and recipe | 203 | - | small |
| `gallery_org\<set-key>` | exact incoming original bytes | 203 | 2,793 | 0.45 |
| `gallery_intake\<set-key>` | per-photo processing history: variants, padded copies, masks, thumbnails, `manifest.json`, `detail.html` | 203 | 34,567 | 23.96 |

So one person folder can hold up to 10 entries; about 72% of the bytes and
76% of the files under person folders are processing history, not gallery.
`gallery_intake` is current functionality (written by every install), not
leftovers. By role: never-selected `tone`/`denoise` alternatives 14.8 GB,
`control` 4.11 GB (2,036 of 2,793 rows selected the unchanged original),
selected-step native/padded copies about 2 GB, masks/thumbnails/manifest/detail
under 0.6 GB (see storage S33).

Top level of the sandbox: `_backup` 42.0 GB (one FULL snapshot), `_sandbox-state`
33.0 GB (run `fresh-v23-20261029`, whose `inputs\_reports\preparation\all` holds
the same variants that install **copied** into `gallery_intake`), `_reports`
1.2 GB, `_retired` 0.5 GB, `_likeness` 0.07 GB.

Production `B:\Sovereign Territories` still has the **older** layout: per person
only `gallery` (0.48 GB), `gallery_944x1104` (2.43 GB), `headshot_944x1104`
(2.20 GB) and occasional `review`; no `gallery_org`, `gallery_intake` or chest
copies yet. Top level: `_backup` 14.0 GB, `_archive` 6.5 GB, `_reports` 0.3 GB,
`_retired` 0.5 GB. Production therefore needs no migration of processing
history: whatever layout we agree is what the first accepted install creates.

## Problems with the current layout

- Inputs, processing evidence and outputs are mixed per person; browsing a
  person shows 6-10 folders where the user cares about `gallery`/`review` and
  the 944x1104 workflow copies.
- Processing history is owned by a person folder although its key is not:
  the 32-hex set key covers source hash, source path, photo ID, domain and
  recipe, never the owner. Every move between people, Review approval, Junk,
  retirement or undo must therefore physically transfer the original and
  every artifact (`plan_transfer`/`execute_transfer`, about 12-25 files per
  photo) and rewrite manifest and detail. That is most of the move/undo
  complexity in `actions.py` and `maintenance.py`, and the reason whole-person
  renames/merges with retained sets are currently held.
- Install copies variants from the run tree into `gallery_intake`, so the same
  bytes exist in the run (`_sandbox-state`), the library and the backup.
- Backup scope has to special-case `gallery_org`/`gallery_intake` inside
  person folders (`library_backup.py`).

## Proposed target layout

```text
<library root>\
  Angels\Angelica\
    gallery\                    accepted photos + z_angelica.txt         (unchanged)
    review\                     photos to look at                        (unchanged)
    944x1104\                   [LY1-b] maintained workflow copies
      full\  head\  chest\        from gallery
      review\full\ head\ chest\   from review
      .photo-derivatives.json
  Various\gallery, review         unassigned pool (unchanged role)
  _processing\<domain>\<set-key>\ original.ext, variants, masks, thumbnails,
                                  manifest.json, detail.html   [LY1-a]
  _processing\<domain>\index.json  photo ID / current hash -> set key (rebuildable)
  _sandbox-state\<run>\           run workspaces (inputs, preparation reports)
  _reports\                       viewers and run reports (unchanged)
  _backup\ _likeness\ _actions\ _junk\ _retired\ _tmp\   (unchanged roles)
```

`_processing` becomes a new configured `storageRoots` entry like the others.
`<domain>` keeps the general/Artist matching boundary physical. A person folder
then holds only `gallery`, `review` and one derivative folder.

Effects:

- Moves, Review approval, Junk, retirement and undo touch only the gallery
  photo, its derivatives and one manifest field (`current`) plus detail
  navigation; no evidence bytes move. Whole-person renames/merges stop being
  blocked by retained sets.
- Backups can treat `_processing` as its own scope (back up once, then
  incrementally; it is append-only per set).
- Install can **move** the selected row's artifacts from the run into
  `_processing` on the same volume instead of copying (LY1-d), removing one of
  the three copies; the run receipt then points at the published set.
- S33 compaction (dropping unselected `tone`/`denoise`/`control` copies)
  applies in the same migration pass, so manifests and detail pages are
  rewritten once, not twice.

## Code impact (measured Nov 2)

Path construction is already centralised: `retained_preparation.py` (775
lines) builds every `gallery_org`/`gallery_intake` path and `derivatives.py`
(219 lines) builds every 944x1104 path through `relative_target`. Python under
`tools` is 189 files / 65k lines with 72 test files.

| Area | Modules (call sites) | Change | Size |
| --- | --- | --- | --- |
| Processing store paths, lookup, index | `retained_preparation.py` (`stage_photo`, `owned_files`, `claims_photo`, `verify_link`, `refresh_detail`, `rename_photo`, `plan/validate/execute_transfer`) | root-level paths, index, transfer reduced to manifest/detail update | medium-large |
| Moves and undo | `likeness_library/actions.py` (8), `maintenance.py` (10) | simplify; keep reading journals written in the old layout | medium |
| Install/replay | `clean_rebase.py` (6), `library_rebase_replay.py`, `library_storage_experiment.py` | publish into `_processing`; optional move-not-copy | medium |
| Backup/restore | `library_backup.py`, `library_backup_archive.py` | new scope; restore of old snapshots keeps old layout, then migrate | small-medium |
| Small path users | `originals.py`, `identity_maintenance.py`, `likeness.py` (`crop_guard`), `preparation_history.py`, `preparation_provenance.py` | follow new API | small |
| Derivative grouping (LY1-b only) | `derivatives.relative_target`, `gallery_maintenance.py`, `review_gallery.py`, `reference_gallery.py`/`reference_rendering.py` folder lists, `identity_maintenance.py`, `originals.py`, ComfyUI input sync | folder names only; workflow input names unchanged | small-medium |
| Tests | 5 files test intake/org/transfer directly; layout fixtures in more | update + new migration tests | medium |
| Migration tool | dropped (see Decisions): a clean reset and rebase builds the new layout; tools refuse the old one | - |
| Docs | `docs/art/original-photos.md` layout, `likeness.md`, gallery/storage plans | rewrite layout sections | small |

Rough effort: the processing-store move (LY2-LY4) is about three focused
working sessions including tests and the sandbox rehearsal; derivative
grouping (LY5) about one more. These are estimates, not measurements. The
migration itself is cheap on disk: same-volume renames, no new copies, and
S33 compaction frees roughly 19 GB in the same pass.

Risks: old backups and action journals use the old layout (keep a read-only
compatibility reader or migrate them explicitly); Acronis must exclude the
library scratch areas before ~37k renames; detail links change depth and need
the existing hash-checked rewrite.

## Decisions (LY1, Nov 2)

| | Decision |
| --- | --- |
| a | Processing history lives in `_processing\<domain>\<set-key>`, not in person folders |
| b | The six 944x1104 folders become one `944x1104\{full,head,chest,review\...}` folder per person |
| c | `Various\gallery` stays the drop zone |
| d | Install **moves** the selected run artifacts into `_processing` instead of copying |
| e | LEAN retention keeps only what a set needs: original, selected-step native/padded output (aliased when byte-identical), masks, thumbnails, manifest, detail. No never-selected `tone`/`denoise` alternatives and no `control` copy equal to the original |

**No migration of the 2,793 legacy sets.** Production has no retained sets, and
the existing `likeness sandbox-reset --full` rebuilds Working from production
while the 89 unique photos and 17 metadata files travel in
`_reports\reset-review-bundle`. A clean rebase therefore creates the new layout
directly. LY4 shrinks to refusing/detecting the old layout plus that reset and
rebase procedure; the separate migration tool is dropped.

**Implementation notes (Nov 2).**

- (a) as built: sets live at `_processing\<owner path>\<set-key>` (for example
  `_processing\Angels\Angelica\<32 hex>`), mirroring the person path instead of
  a `<domain>` index. Ownership stays obvious, clean-rebase install/undo moves
  `_processing\<category>` together with its category, and no separate lookup
  must be rebuilt. Whole-person rename/merge still holds while a person owns
  sets (unchanged behavior). The old in-person `gallery_org`/`gallery_intake`
  layout is refused (`LegacyLayoutError`), never migrated.
- (b) as built: `<person>\944x1104\{full,head,chest}` and
  `944x1104\review\{full,head,chest}`, with `.photo-derivatives.json` inside
  `944x1104` (keys still relative to the person folder). File names are
  unchanged (`<stem>_944x1104.png`, `<stem>_head_944x1104.png`), so the
  generated workflows and `sync-inputs` names are unaffected. Every
  `originals` run first moves the former folders by rename (byte-identical
  duplicates dropped, different files kept and reported, the manifest moved
  with rewritten keys), so production's 335 `gallery_944x1104`/
  `headshot_944x1104` folders move without regenerating about 5 GB.
  `originals --check` reports anything still to move. Workflow-input discovery
  (`photo_library`/`headshot_library`) falls back to the former folder names
  until then; viewers and likeness read only the new layout.
- (d) not yet built: install still copies the selected artifacts from the run
  into `_processing`; with LEAN only the selected/needed artifacts are copied,
  and the run's `inputs` mirror is retired after acceptance. Tracked as LY3b.

## Modes: two separate axes

| Axis | Values | Owner | Decides |
| --- | --- | --- | --- |
| Storage | FULL / LEAN / COMPACT / COLLAGE | [storage](2026-10-28-storage-operations-and-retention.md) | which computed bytes are **kept** |
| Processing | FULL / FAST / OVERLAY-ONLY | performance [T18](2026-10-28-intake-performance.md), intake [I70](2026-10-23-image-intake-preparation.md) | which steps are **computed** |

Decision (e) originally tightened LEAN retention without changing computation.
Nov 4 LY14a adds the approved exception: LEAN skips comparison-only
`tone`/`denoise` generation. It still runs the guarded person/composition
assessment. Further processing skips remain explicit T18/I70 decisions, not
automatic consequences of selecting LEAN.

## `_` directories (hash audit Nov 2, Acronis off)

All 70,913 files in production and the sandbox active stores were SHA-256
hashed (185 s; production 27 GB read at about 180 MB/s).

| Library | Folder | Finding | Action |
| --- | --- | --- | --- |
| Production | `_archive` 6.5 GB | 10k exact copies of active/backup photos, 1,330 old 944x1104/headshot copies, 195 unique `gallery_uncropped` pre-crop originals, Workflows, scripts, Oct 11 manifest | **Done Nov 2:** copies and scaled files removed; the 603 unique files stay in place (0.11 GB left) |
| Production | `_backup\library-20261014-162634` 2.7 GB | earlier "2,617 unique" now all matched in active galleries, regenerable scaled copies, or 174 unique metadata/report files | **Done:** removed; the 174 unique files are in the ZIP below |
| Production | `_backup\_packed` (Oct 19 bundle) 5.2 GB | 0 unique photos; 25 unique members | **Done:** removed; members in the ZIP below |
| Production | `_backup\library-20261020-222038` 5.6 GB | newest snapshot; now the **only** copy of about 2,100 older files (`Potentials`, `_reports`, ComfyUI inputs) | keep; never retire without its own audit |
| Production | `_reports`, `_retired`, `_junk` | current/user-dispositioned | keep |
| Sandbox | `_reports\library-performance-20261031` 231 MB | regenerable viewer from the timed run; timing recorded in the gallery plan | **Done:** HTML/thumbnails removed; manifest and `RETIRED.json` kept |
| Sandbox | `_backup\library-20261029-235003` 42 GB, `_sandbox-state\fresh-v23-20261029` 33 GB | sole FULL snapshot and run state of the current sandbox | retire after the clean rebase is accepted, keeping JSON receipts |
| Sandbox | `_reports\reset-review-bundle`, `storage-experiments` | carried metadata, durable evidence | keep |

Production went from about 27 GB to 10.9 GB: 12,988 files and 14,340,483,967
bytes were removed after re-hashing every target and survivor. The receipt,
plan, script and verified `retained-metadata.zip` (199 files) are in
`B:\Sovereign Territories\_reports\storage-retirement-20261102`; the read-only
check passed afterwards.

## Steps

- [x] **P1 you** LY1 Decide the layout: (a)-(e) accepted Nov 2, see Decisions.
- [x] **P1 ai** LY2 Implement the `_processing` store in `retained_preparation.py`
  (new `processing` storage root, per-set manifest with `current` path,
  manifest-only transfers, LEAN retention per (e)) and refuse the old in-person
  layout; focused regressions first. Done Nov 2 (owner-path layout, see notes).
- [x] **P1 ai** LY3 Update install/undo/check, backup scope and small path users
  to the new API; run the affected test files. Done Nov 2.
- [ ] **P2 ai** LY3b Install moves the selected run artifacts into `_processing`
  instead of copying (decision d), keeping the run's undo/replay receipts valid.
**Transferred contract: LY4 -> [reset LY4](2026-11-05-priority-reset.md#m1-execution-and-transfer-ledger); completion tracked only in the spine.** Complete the authorized continuation's install/check/
  viewer evidence and classify diagnostics; share it with acceptance owners.
  Do not repeat reset/intake solely to close this task. Historical scope:
  reset the sandbox from production (`sandbox-reset --full` plus
  the carried bundle), run the clean LEAN rebase in place with per-step timings
  (Acronis off), verify Gallery/Overview/Review, then hand to storage S32/S27
  and retire the old sandbox snapshot and run state.
  Nov 5 09:36 next-run prerequisites: approved naming N16 and cast C12/C13,
  engine E18/E19 residual-audit/Briar scenarios and gallery L23 provenance
  diagnostics, plus honest crop-status classification. Test before intake;
  inspect a saved-evidence preview of family links, Sisters admissions,
  workflow resets/replacements and residual route/holds. Then use a new
  run name for the full Production-based disposable sandbox rehearsal,
  preserve progress/timing logs and verify all three viewers. No immediate
  rerun, Production writes or automatic settlement is authorized by planning.
  Nov 5: fresh `fresh-20261104-lean2` is installed; installed-run, recap,
  reports-only and automated browser checks pass. The full gallery scan
  completed with exit 1 on 143 framing diagnostics (137 unreproducible
  heads; six unavailable framings for two small-face photos and one
  no-face photo), with zero
  held collisions, renames or pending derivatives. Keep LY4 open; no
  quality-policy bypass or further reset/intake. Resolve diagnostic
  acceptance from existing evidence first. Measurements and remaining
  speed/space proposals have one home in the
  [final verified baseline](../recap/2026-11-04-1130-recap.md#final-verified-baseline---nov-5-0448).
  Progress Nov 2 (run `fresh-20261102`, Acronis off), timings in seconds:
  reset preview 221, reset apply 314, `originals` migration 103, backup 83
  (10,550 files, 6.56 GB), rebase dry run 47; intake of 3,093 images started
  14:48 with 3 CPU-bound workers (about 17 images/min). Fixes found by the run:
  the full reset no longer carries regenerable output (43,623 files, 32.2 GB)
  or the 757 processed copies of production originals (`190c0e77f`), and
  directory publishes retry scanner locks for up to about 30 s after a
  repeatable `WinError 5` on the source-overlay rename (`deac77b52`). The first
  intake then stopped ordering rows after image 759: removing a worker's
  scratch folder hit the same scanner lock, and the process pool silently
  drained all queued images before reporting. Scratch removal now retries and
  a failed ordered publish cancels queued work (`0e50eb5f4`); the resumed run
  recovered all 1,267 per-image checkpoints (T6 recovery confirmed live).
  At 1,738 the same removal met `WinError 145` (a scanned file still pending
  delete leaves its folder "not empty"); that is now retried too
  (`dc019ce33`), and the second resume recovered 1,744 checkpoints.
  Intake took about 1,890 + 4,896 s; then check 225, preview 1,025 and replan
  485. The first apply refused an ambiguous ID for byte-identical copies
  (fixed `91a7a992a`); attempt 1 spent 77% of its time reloading the workflow
  configuration once per retained set (prefix hoisted, `030259282`) and was
  stopped; attempt 2 staged about 184 photos/min but died with a session
  restart (long runs are now detached). Both kept their `staged`/`previous`
  as `*-attemptN-interrupted` with a receipt; Working was untouched. Attempt
  3 started 21:16 with `--preserve-legacy-derivatives` and finished 04:49
  (exit 0, 27,180 s): about 25 min staging, 2 h 50 min scaled copies (8,000+
  `944x1104` files), 1 h 50 min detail-page refresh, 40 min hashing and safety
  checks, 2 h 15 min Review/People/intake gallery rebuild; 354 GB read in
  total for about 26 GB of data (LY9). Applied: 2,814 photos (stayed 1,904,
  moved 792, moved to Review 96, to Review 22), 749 renamed, 118 in Review,
  68 new identities, 73 emptied; person folders hold only
  `gallery`/`review`/`944x1104`, no `gallery_intake`/`gallery_org` remain,
  `_processing` holds all six categories. Diagnostics: 120 head crops not
  reproducible from the cached face box and 3 photos without a usable face
  (padded copy only). Cast: nothing left Angels/Sisters (all-seeds mode); all
  79 cast gains from Various/Potentials/Prospects are in that cast member's
  Review. Finding for review: a pre-existing `Potentials\Camaris` identity
  (5 photos, nearest Drakniss 0.20) was promoted to `Prospects\Camaris`, so
  two identities share the Angel name Camaris. After install, `--check` runs
  without `--preserve-legacy-derivatives` (with it the check selects the
  unpublished-plan recovery preview and is refused); runbook corrected.
  Decided Nov 2 (chat): the run must go all the way in the sandbox (every move
  and rename applied) so the outcome can be reviewed in the galleries; the
  review aid is automatic and repeatable, not one-off: every
  `sandbox-rebase.cmd` step writes `_reports\library\rebase-recap\<run>.html`
  plus an index (moves, renames, Review holds, cast gains/losses, new
  identities by surname with nearest cast member, comparison with other runs
  of the same inputs), and the user's look-alike picks and expected photo
  placements live in `rebase-expectations.json` beside Working, scored on
  every recap. Cast matches stay in Review for this run; tuning (whether
  low-score supplements join Angels/Sisters) follows the user's review.
- [x] **P2 ai** LY5 Group derivative folders (LY1-b) and update
  viewers and ComfyUI input sync; verify `sync-inputs` output names unchanged.
  Done Nov 2: names unchanged by construction; rename-only migration in
  `originals`.
- [ ] **P2 ai** LY6 Rewrite the layout sections in `docs/art/original-photos.md`
  and `likeness.md` (layout and retained-storage text updated Nov 2) and add the
  fresh-sandbox step-by-step runbook, confirmed by the LY4 run; production
  adopts the layout at its first accepted install.
- [x] **P1 ai** LY7 Leave Artists out of the sandbox: `sandbox-reset --full`
  neither copies Production `Artists` nor carries sandbox Artists forward
  (`--include-artists` opts back in), so they are never copied or prepared.
  Done Nov 2 for the next fresh sandbox; the current `fresh-20261102` run
  already prepared its 279 Artists images before the decision and matching
  ignores them. The Production-side Artist scope stays with intake I74.
- [ ] **P1 either** LY8 Production true-up before the first direct Production
  clean rebase: inventory Production for the old in-person layout
  (`gallery_944x1104`/`headshot_*`, `gallery_intake`, `gallery_org`,
  `.photo-derivatives.json`), stale `_` directories and fragmented or
  unnecessary files; decide per class (migrate by `originals`, move to
  `_processing`, retire with a backup, or leave); write the runbook for
  running directly in Production. Gate: the fresh sandbox run (LY4) accepted,
  so the same classification rules are proven there first.
- [ ] **P2 ai** LY9 Cut repeated verification in apply (attempt 3 read 354
  GB for about 26 GB of data and took 7.5 h): load the workflow configuration
  once per pass (`verify_link`, `_set_folder`, `_detail_navigation` still call
  `cw.load_cfg` per photo); memoise per-folder derivative manifests and
  `source_is_prepared` within a pass (detail refresh slowed from 40 to 20
  pages/min as folders grew); reuse digests already verified in the same
  transaction instead of re-hashing; hash person trees once per gallery build
  (`person_rename.tree_hash` per item); print one progress line per phase so
  a long apply is checkable without a profiler. Call-count regressions for each. The
  read-only `bin\people-gallery.cmd ... --check` (Nov 3, over 1.5 h, silent log) sits
  in the same `derivatives.maintain` -> `verified` -> `verify_link` -> `_manifests`
  chain, so it benefits too. Gate: attempt 3 checked (the engine is in the run's
  implementation hashes).
- [x] **P2 either** LY10 Read-only `--cast-seeds core` comparison in a
  separate run directory, so the recap shows who would leave Angels/Sisters
  under core seeds; first measure whether a new run must repeat intake (about
  1.9 h) or can reuse `fresh-20261102` inputs. Nov 3: with today's code a core run
  releases nothing, because 20 of 21 cast identities are catalog-protected; run it
  with [cast C11](2026-10-23-cast-seeded-library-rebase.md) semantics. Gate: attempt
  3 checked; C11 approved.
  Result (Nov 4): run `fresh-20261103-core` reset from Production, full intake
  (197 min), matched preview, refinement and audit, then installed (309 min) and
  checked (exit 0). 153 photos left cast members, 64 cast gains in cast Review,
  Drakness -> Nyxene 4. Recap/Gallery/Review pages verified in a browser (all
  images load; source links fixed). Outcome review continues in LY11; decisions
  in engine E16/E17. See the [Nov 4 recap](../recap/2026-11-04-0230-recap.md).
**Transferred contract: LY11 -> [reset LY11](2026-11-05-priority-reset.md#m2-human-acceptance), not completed.** Review the applied sandbox galleries and the recap; record
  look-alike picks and expected placements in `rebase-expectations.json`, and
  feedback on Review volume, cast joins, and the duplicate Camaris name
  (`Prospects\Camaris` versus the Angel).
- [ ] **P2 ai** LY12 Align gallery maintenance with the rebase. The Nov 3
  `bin\people-gallery.cmd ... --check` (97 min, EXIT 1) wants to rename 5
  `Various\review` "missing stable photo ID" holds that `clean_rebase` keeps
  under their original names on purpose, and it reports the galleries "out of
  sync" because the rebase's `_refresh_galleries` does not write
  `.gallery-maintenance-report-state.json`. User decision (Nov 3): any file in
  `Various\gallery` that does not follow the naming standard gets a stable ID and
  standard Various naming at intake; do not keep source names. Implement that in
  the rebase/intake, write the state after a rebase gallery rebuild, so a fresh
  install checks clean, and add a test for each.
  Filename slice implemented Nov 3: preserve recognized download IDs; assign
  ID-less non-cast inputs the existing originals content ID and normalize
  prepared destination prefixes without renaming frozen inputs. Exact byte
  copies are held with distinct `various_duplicate_*` names and explicit
  canonical-source reasons, not clustered twice; differing-byte ID collisions
  refuse explicitly. Manifest SHA-256 values are reused. Install/check/undo
  naming and duplicate recovery tests pass. This does not retroactively rename
  the installed review baseline. The maintenance report-state slice remains
  open; LY12 is not complete.
- [ ] **P1 ai** LY13 Cast-name collision. `Potentials\Camaris` is not a new
  identity: Production has had it since Oct 8 (two photos). Its `z_camaris_bloom.txt`
  says "Camaris Bloom", "returned to Potentials; replaced as Camaris by Ruby Eden"
  (Oct 19), but the folder kept the cast name. The rebase reused the folder name
  for a 5-photo cluster (nearest Drakniss 0.20) as `Prospects\Camaris`. Fix: the
  cast-replacement path renames the retired folder to its recorded display name;
  the rebase and intake refuse or rename any non-cast identity whose name matches
  an Angel/Sister (case-insensitive), preferring the recorded `name:`; a
  validator lists existing collisions. Correct the Production folder only through
  the LY8 true-up. Tests for each.
  Nov 3 extends this with [naming N14](2026-10-22-identity-family-naming.md#nov-3-name-continuity-and-character-slot-boundaries):
  non-character identities must have first and last names; valid merges keep
  the oldest original identity's name, including protected Prospect cores.
- [ ] **P2 you** LY14 Decide whether to cap maintained 944x1104
  derivatives (`gallery_944x1104`/headshots) to each identity's core,
  protected and workflow photos. Measured Nov 4 (table below): derivatives
  are 8,291 files / 7.2 GB in Working and cost about 1.15 s per photo
  (padded 0.39 s, head and chest the rest), roughly 54 serial minutes of a
  2,814-photo apply. A cap to core/protected/workflow photos would save most
  of that time and space plus the matching `_backup`/`previous` copies. Various
  held only about 115 Review photos (0.10 GB) after the previous install.
  That is not its pre-intake workload: the Nov 4 reset restored 3,048 Various
  inputs, so deferring Various derivatives before matching could matter
  substantially (see the live-run investigation below). If adopted:
  originals stay and still show in Review; protecting a
  photo generates its derivative; unprotecting or moving out removes them
  through the existing derivative manifest. Confirm the per-phase numbers with
  the timed N15 re-run before deciding. Source: user feedback below (Nov 4).
- [x] **P2 ai** LY14a LEAN intake no longer renders the comparison-only denoise
  and tone candidates (never auto-selected in 2,811 of 2,811 photos). Their
  steps are recorded as `skipped` with an explicit LEAN reason; FULL still
  renders them, and a FULL manifest with LEAN-skipped steps fails validation.
  The checkpoint binding gains `leanComparisons` so older LEAN checkpoints are
  never mixed in. Existing LEAN manifests with the renders still validate.
  The rebase install and apply now print per-phase seconds (`Install: ...`,
  `Plan: ...`, `Apply: ...`) for the next measurement. Takes effect on a new
  intake only; undo/replan/apply of an existing run reuses its old inputs.
- [x] **P2 ai** LY14b `bin\rebase-flow.cmd` runs the whole fresh rebase
  (full reset, originals and check, backup, intake and check, matched preview,
  install, checks) with live process-flow feedback. The console shows a
  start/finish line per step against the Nov 3 times and phase timings. Its
  heartbeat gives photos done, rate and ETA, a quiet-process warning and the
  remaining flow estimate. `tmp\session-logs\rebase-flow\RUN\flow.md` is
  rewritten after every event and records space after each step. Failed or
  interrupted steps resume with the same `--apply`. The flow replaces the
  manual N15 command list and fixes its missing backup `--apply`. The reset
  preview, intake dry-run and separate intake check are optional
  (`--with-previews`) because the apply steps repeat their guards. The matching
  plan and the backup of the fresh baseline stay, because the install requires
  both. A reports-only retry is selected when the run receipt is already
  `applied`; it never reapplies a hash-bound matching plan. Prior step logs and
  failed records are retained as numbered attempts and flow history.
- [x] **P1 ai** LY14c Before any further full re-run, fix early exact-content
  alias handling across incoming Various and the effective baseline. Reuse
  one prepared input per verified SHA/domain/recipe, prefer an existing
  assigned canonical, and record every arrival as an alias rather than a new
  matching vote. Preserve source/decision/history recovery and Artist scope;
  changed same-ID incoming bytes remain explicit reprocessing/replacement,
  not duplicates. Test raw Facebook/inferred IDs, distinct download IDs,
  arbitrary names, same-ID conflicts, protected/workflow decisions, source
  changes, install and undo. The installed run is a diagnostic baseline,
  not deduplication acceptance; do not rewrite its bound receipts.
- [x] **P1 ai** LY14d Implement/test the Nov 4 22:02 approved disposable
  sandbox recovery policy: no full baseline backup or pre-intake derivative
  generation, keep transaction rollback until publication is verified, then
  retire it. Retain source/alias evidence and movement/Families reports.
  Bind recovery mode to the saved run; refuse Production/FULL evidence and
  explicit undo. FULL retains its existing backup/undo contract. FAST's
  stronger omissions remain a separate unimplemented profile.
- [x] **P1 ai** LY14e Reuse operation-local verification through derivative
  and detail phases, with checked invalidation before intentional metadata
  writes and a final content/path seal. Cache only within the operation;
  tampered evidence must still refuse. Cover read-only gallery maintenance
  without extending a stale cache across its apply-time writes. New-run
  measurement transfers explicitly to LY4/N15, not an implementation claim.

**Prerequisite validation:** the 151-test targeted run's only failure was an
undersized synthetic headshot fixture, corrected and rerun. Final 17 focused
tests pass (one symlink-privilege skip), including byte-exact cached/uncached
derivatives, stale/tamper rejection, interrupted/unknown/edited rollback
cleanup, transactional publication failure and FULL exact undo.
All 399 likeness-library and 67 viewer/maintenance tests pass.
Supported launcher preview/help, generated todo and routine hygiene/data
checks pass. No subject-detection or crop/erase quality guard was removed.

- [x] **P1 ai** LY14f Resolve the fresh reset's changed `z_*.txt` history
  collision without losing either version or admitting old generated names
  as new seeds. The first reset refused at 22:28 after 3m27s, before mutation.
  The supported preview isolated one 75-byte
  `Potentials/Uma Rowe/gallery/z_uma_rowe.txt` sidecar, not an image conflict.
  A failing reproducer now passes: recognized gallery name-history sidecars
  use the existing hash-verified reset metadata bundle; current Production
  remains active, sandbox history stays in the bundle. Unknown metadata and
  image path conflicts still block. All 40 reset/flow tests pass.

- [x] **P1 ai** LY14g Keep the LEAN movement recap honest about the new
  contract: show explicit exact-arrival aliases with their canonical input
  and final destination, without adding photo/vote counts, and replace its
  old undo instruction in disposable runs with reset-only recovery.
  Bind displayed aliases to the saved overlay hash and canonical photo hash;
  edited evidence refuses. Historical compact runs do not invent missing
  alias data. The supported recap preview and all 14 recap tests pass.

**Nov 4 22:02 fresh-run authorization:** after LY14c/LY14d/LY14e's focused
tests and hygiene pass, reset the sandbox Working directory completely from
current Production and run `fresh-20261104-lean2` with
`--recovery-mode disposable`, keeping `--cast-seeds core
--record-core-protection`. N15/LY4 still own whole-run acceptance; LY10's
earlier core comparison is already complete. Do not
replay the installed diagnostic result as proof. Preserve only required
historical receipts/source evidence through the supported reset; no
baseline backup of the discarded sandbox. The last run did use core seeds:
209 cast photos were released and 1,057 retained. Non-core photos remain
eligible to leave; family surnames do not protect membership.

**Read-only Production preflight (22:18):** excluding Artists as the full
sandbox reset does, the revised overlay plans **3,290 outcomes and 3,290
distinct input SHA-256 values**, versus the diagnostic run's 3,517 outcomes.
The 2,421 assigned inputs plus 3,048 Various arrivals become 2,848 incoming
representatives with 200 aliases, 175 same-ID newer-byte replacements and
869 new canonical inputs. This removes all 227 extra matching/preparation
rows measured above without deleting Production sources. The scoped scan
took 24.84 s; it proves input enumeration, not full-run performance or
placement acceptance. Evidence:
`tmp/session-logs/2026-11-04/production-alias-preflight.json`.

**Nov 4 measured bottlenecks** (the `fresh-20261103-core` run; the apply log had
no timestamps outside verification, so derivative time is a 30-photo benchmark):

| Phase | Measure | Note |
| --- | --- | --- |
| Intake variant-labelled elapsed | about 587 worker-min | denoise-labelled 305 (52%), composition 71, head reconstruction 55, control 36, eraser 31.5, tone 20; includes deferred pipeline work, not isolated filter CPU |
| Run `inputs` on disk | 31,429 files / 17.9 GB | tone 4.6 GB, denoise 3.9 GB, control 3.8 GB; denoise/tone never selected |
| Apply: Review inputs verify | 1,619 s | 31,637 reads / 13.1 GB, mostly candidates |
| Apply: Overview thumbnails verify | 510 s | 13,681 reads / 4.5 GB |
| Apply: Overview evidence verify | 219 s | 11,311 reads / 2.5 GB |
| Apply: preparation history index (x2) | 268 s + 260 s | full artifact/source checks |
| Apply: 944x1104 derivatives | about 54 min (estimated) | 1.15 s per photo, 3 framings |
| Apply: preparation evidence verify (x2) | untimed until now | re-hashes run `inputs`; LEAN reduces candidate bytes, exact effect depends on workload |
| Sandbox state | 23 GB | `inputs` 17.9, `previous` 4.5, source overlay 0.6 |

The initial LY14a forecast was about 8.5 GB less run state, half the preparation
CPU and half the input-verification bytes. Only the historical comparison
render bytes were directly measured: variant timers include deferred pipeline
work, so the half-CPU claim was overstated. Current outcomes/size differ too.
Use the fresh-run observations and
[T17/T18 analysis](2026-10-28-intake-performance.md#nov-4-lean-optimization-proposals-from-the-fresh-run)
instead of treating that forecast as verified.

**Nov 4 live-run investigation (13:30; not final acceptance):**

- Reset finished in 4m06s; Working fell from 42.08 GB to 5.17 GB.
- Originals took 12m47s versus about 5 min previously, but generated 3,022
  full-size copies and 2,051 headshots versus 483 and 96. Current log timestamps
  isolate 7m09s for full-size copies and 3m49s for headshots after the final
  rename. This is a much larger generation workload, not evidence that the
  revised LEAN preparation is slower; originals precedes that preparation.
- The frozen overlay records 2,421 baseline inputs, 3,048 Various entries,
  1,096 new inputs and 175 replacements. Intake has 3,517 outcomes versus
  2,814 last time (25% more); normalize time and retained bytes per outcome
  and distinguish replacements before drawing optimization conclusions.
- The new baseline backup completed in 2m46s versus about 13 min, despite
  growing from 9,697 files / 6,044,502,114 bytes to 16,824 files /
  10,451,606,474 bytes. These are aggregate timings, not controlled disk
  benchmarks; cache state and concurrent work can affect them.
- Originals generates derivatives before matching; backup then copies them,
  while the installer maintains derivatives for the final prepared assignments.
  LY14 should consider deferring pre-intake derivative generation as well as
  the final core/protected/workflow cap. Do not remove normalization or the
  install's backup prerequisite, or change the engine during this measurement.
- The first intake sample is too small for a speed verdict. Capture later
  throughput and completed preparation timings; compare source workload and
  image-stage costs, not just the running ETA based on Nov 3 estimates.
- Active recovery binding confirms `storageMode: lean` and
  `leanComparisons: skipped`; all first 32 completed checkpoints have both
  denoise and tone skipped. Their guarded sequence averages 16.67 s, including
  10.98 s before the first step record (cumulative, not additive timers).
  Subject detection runs before that record even when the first crop is
  skipped; a skipped crop does not mean zero computation. This sample excludes
  other render/encoding/checkpoint work and is not the final per-image time.
- An eight-second resource sample shows the four intake workers consuming
  about 79% of total machine CPU, VS Code about 15%, and roughly 5.2 GB of
  physical memory free. Workers are active, not suspended. This supports
  investigating CPU-bound subject/composition assessment next, not assuming
  denoise is still running or claiming paging from working-set size alone.
- Intake ultimately passed in about 180 min for 3,517 outcomes; matching took
  13m52s. Install staging and retained preparation took 16m57s. At 18:33,
  derivative generation had produced 7,075 outputs for about 2,389 photos
  and was still running, so the earlier 54-minute benchmark is not an
  end-to-end forecast. Code tracing identifies repeated prepared-lineage
  checks: `derivatives.maintain` calls `render` and records `sourcePrepared`
  for each framing; both call `source_is_prepared`, whose uncached path scans
  owner manifests and verifies lineage/artifacts. The install loop does not
  establish a verification-read scope. Investigate reuse under a safe
  unchanged-evidence boundary after this run; do not disable verification or
  treat the pixel-render benchmark as a measurement of these checks.
- Final install phase timers: derivative generation 7,176.4 s, detail pages
  4,809.2 s, staged hashes 69.1 s, pre-publication rechecks 115.2 s and
  publication/checksums 38.4 s. The first apply published the files but failed
  during report refresh: a normalized cosine could round to
  `1.0000000000000002`, rejected by strict policy bounds. Audit output now
  clips normalized dot products to [-1, 1]; a reproducing regression plus
  audit/policy/Review and flow-recovery tests pass (65 tests). Resume uses the
  reports-only launcher, preserving the original matching receipt/hashes.

**Nov 3 recap feedback ownership:** the complete
`rebase_fresh_20261102_feedback.md` is preserved once in
[gallery L21-L24](2026-10-22-gallery-review-layout.md#nov-3-fresh-rebase-recap-feedback).
That scope owns consistent recap styling/navigation, final-destination links,
membership-flow tables, core/surname image comparisons, explicit reason/score
labels, No Change distinctions and the ranked-picker idea. N14 owns Harlow/
Sophie/name continuity; engine E14/E15 owns final-rival audits and bounded
recomparison. C11/engine E13 owns the approved core-protection trial. Reuse
the same saved run evidence and preserve the installed pages for ongoing
review; no new full intake or broad plan reorganization is authorized.

## Nov 4 copy and verification proposals

Analysis requested at 21:44; the verbatim request and processing-profile
trade-offs live in
[performance T17/T18](2026-10-28-intake-performance.md#nov-4-lean-optimization-proposals-from-the-fresh-run).
These proposals do not authorize a new storage architecture or waive recovery
checks. Keep LY14's derivative selection decision open.

### Duplicate correctness finding after the user's added context

The user deliberately re-added already-processed photos to Production Various.
The apparent 1,096 "new inputs" counts new target paths, **not new unique
photographs**. Do not treat all 703 additional outcomes as useful new work.
Read-only grouping of the frozen input SHA-256 receipts finds:

- 3,517 inputs, **3,290 unique hashes**, 207 repeated-byte groups and
  **227 extra exact copies**, all extra representatives in Various. Of those
  groups, 181 span Various and an assigned category.
- The overlay folds nine same-ID/same-byte aliases, but its no-ID path does
  not compare hashes across the baseline. Matching only byte-deduplicates
  content-derived IDs: inferred-ID collisions are set to no ID without
  recording duplicate provenance, and distinct explicit IDs bypass that
  byte check entirely. **209 of the 227 extra copies enter ordinary routing**;
  ten extra representatives are duplicate-held and eight missing-ID-held.
  Across all outcomes, eleven are duplicate-held and eleven missing-ID-held;
  those totals use different representatives/denominators.
- Concrete same-byte case: `camaris_image_7514748494547382365.jpg` remains core while
  `Various/gallery/various_image_7514748520288794438.jpg` gains cast Review.
  Distinct download IDs do not make those bytes different photos. This can
  inflate evidence/membership counts, not merely waste time.
- Raw extra input bytes are **30,524,910 (29.11 MiB)**. The frozen report's
  image paths are already digest-shared: removing those extra rows would
  remove **zero image files exclusively referenced by them**. Therefore the
  duplicates do not explain gigabytes of extra preparation candidate files,
  despite redundant per-source assessment work.
- Installation creates **227 additional per-photo retained sets** occupying
  **339,437,047 bytes (0.316 GiB)** and additional selected natives occupying
  **197,832,314 bytes (0.184 GiB)**, before derivatives. These are associated
  footprints, not an approved deletion list or a prediction of total savings.

The largest size increase is instead replicated pre-intake derivatives and
recovery retention, shown below. LY14c owns the exact-duplicate fix before
another expensive run. Do not auto-delete visually similar but byte-different
photos: matching processed/raw versions needs verified original lineage or
an explicit replacement decision. No source files or installed receipts were
changed by this investigation.

### What is copied today

1. Full reset copies the current Production baseline into sandbox Working;
   the historical Source snapshot is left unchanged.
2. Originals normalizes names and generates full/head derivatives before
   matching. A full baseline backup then copies Working plus configured
   ComfyUI inputs and repository configuration.
3. `source-overlay` freezes the baseline and Various input choices, retaining
   replaced/aliased source recovery copies. Intake copies frozen source inputs
   into its own `inputs` mirror.
4. Image workers retain originals and render candidates, padding, previews and
   details into recovery staging; publication consolidates the report.
5. Install copies selected natives into unpublished `staged`, and publishes
   per-photo retained evidence into its staged `_processing`. LEAN already
   aliases exact native/original roles within a photo and omits some
   unselected artifacts; it is not global cross-stage deduplication.
6. After verification, existing categories are **renamed** into `previous`,
   and staged categories are renamed into Working. This rollback data is not
   another full byte-copy at that boundary, but occupies disk alongside the
   full backup. The installed `_processing` and intake mirror both remain.

Measured after publication: intake mirror 11.319 GiB, `source-overlay`
0.808 GiB, rollback `previous` 8.568 GiB, baseline backup 9.740 GiB,
installed `_processing` 4.575 GiB. Those first three are within the 20.747 GiB
run state; **do not add run state again**. Working totals about 47.29 GiB.
Backup includes external inputs/config, so not every backup byte duplicates
`previous`. Historical run state was about 23.06 GiB for fewer inputs.

Approximate non-overlapping comparison (logical GiB; old run state rounded):

| Scope | Previous | Fresh LEAN | Change |
| --- | ---: | ---: | ---: |
| Active category trees, including derivatives | 8.84 | 11.28 | +2.44 |
| Baseline backup | 5.63 | 9.74 | +4.11 |
| Installed retained preparation | 3.73 | 4.58 | +0.85 |
| Run state, including inputs/overlay/rollback | 23.06 | 20.75 | -2.31 |
| Reports and other Working files | 0.82 | 0.95 | +0.13 |
| **Working total** | **42.08** | **47.29** | **+5.21** |

LEAN really reduced run state, but it does not prevent `originals` making
derivatives before backup, nor remove the backup/rollback duplication. Thus
the whole Working tree grew even after the LEAN reduction. Fix correctness
and unnecessary generation order before concluding that more disk or a new
full run is required.

### Prioritized proposals and disadvantages

| Priority | Proposal | Opportunity | Disadvantages / acceptance gate |
| --- | --- | --- | --- |
| 1 | Reuse verified lineage within a stable phase and index current-path claims | Derivatives took 119m36s; detail refresh 80m09s. Both repeatedly resolve manifests and verify prepared lineage. Avoid repeated whole-owner scans and repeated hashes for the same unchanged evidence. | Do not wrap mutable detail/manifests in an unmodified read-only cache: refresh writes them. Separate immutable image evidence from mutable metadata, invalidate writes, and seal paths/content before publication. Test stale bytes, conflicts, edits and failures. Savings are not yet measured. |
| 2 | Generate detail navigation once, after derivative availability is known | Detail HTML is created during preparation, adapted at staging, then refreshed for installed navigation. Avoid the expensive final second construction/check cycle where equivalent output can be built once. | Native/detail paths differ by stage; links and manifest hashes must remain correct and recoverable. Keep exact provenance and prove output/link equivalence. |
| 3 | Normalize names without creating pre-intake derivatives; decide final derivative scope afterward | Originals cost 12m47s and added about 4.25 GiB before backup. Those derivatives also enlarge backup/rollback. This is separate from the final LY14 core/protected/workflow cap. | Requires a tested normalize-only path and preserving selected workflow assets; cannot simply skip originals. Review must work from natives/thumbnails when a framing is absent. Final demand-generation and unprotect cleanup need design. |
| 4 | Share verified report input snapshots across Review/Overview/history | Review verification 23m02s, Overview thumbnails 8m09s, evidence 2m40s, two history audits about 4m54s together. Existing operation-local reuse still ends at each viewer/phase. | These are not pure hashing times. Publishing viewers mutates output files; share only stable source evidence, retain a final seal and refuse changed membership/content. No mtime-only trusted cache. |
| 5 | Sandbox-specific recovery policy instead of both a full baseline backup and rollback | Baseline backup 9.74 GiB plus `previous` 8.57 GiB is a large retention budget. Backup creation itself was only 2m46s. Source snapshot/overlay and rollback may support a narrower sandbox guarantee. | Existing install requires a full verified backup. Waiving it requires explicit policy/approval and tested crash/undo recovery, external-input coverage and source availability. Never generalize the waiver to Production. |
| 6 | One immutable artifact store, with stage manifests referencing hashes | Could avoid copies between overlay, input mirror, retained report originals, selected natives and installed evidence. Audit actual SHA overlap first; not all these images are identical. | Larger architectural change: reference tracking, garbage collection, undo/retention, exports, moving machines, crash recovery and standalone reports. Hard links share mutable bytes and violate current isolation/reparse assumptions; not a safe quick fix. |
| 7 | Retire reproducible run artifacts after explicit acceptance | Intake report artifacts and rollback need not all live forever once installed provenance and required source recovery are independently retained. | Existing reports and receipts reference run inputs. Use dependency-aware retirement; no blind deletion of `inputs`, backups or source folders. Recovery and historical comparison capability decrease. |

Recommendation: first tackle priorities 1-3 as bounded exact-behavior work,
then measured cross-viewer reuse. Backup creation and the 0.8 GiB overlay are
not the largest time hotspots. Defer the shared artifact-store redesign until
hash-overlap measurements show its value. Processing shortcuts belong to
T18, with separate visual-quality acceptance. No new full intake is needed to
test most install/report optimizations: use a small copied immutable fixture
and preserve this installed review baseline.

The final gallery-check trace adds a concrete priority-1 example:
`gallery_maintenance.run` invokes `derivatives.maintain` once to find pending
work and again in its changes/diagnostics loop, including read-only checks.
Each framing revalidates prepared lineage without an enclosing read session.
The resumed checker was actively using CPU, not suspended. Six held name
collisions guarantee the current check returns nonzero because diagnostics
are always a failure. The check was stopped at 21:59 after about 12m13s;
its full scan is incomplete, not passed. A shared read-only
verification session could reuse those reads and seal once; **do not** extend
that unchanged session across apply-time manifest writes. This is a proposed
exact-behavior optimization, not permission to bypass those diagnostics.

## User request (chat, verbatim)

Nov 2 11:48, coverage: separation of intake/processing from galleries and
reports -> target layout and LY1; analysis of current/future structure and
script effort -> the measured sections above; timing with the sandbox work ->
resume gate before S32/S27.

<!-- markdownlint-disable MD013 -->
````text
We may want to revisit the directory structure again - after you figure this out and possibly separate things out a bit in terms of what ends up in the gallery at the end.  I do think after we've been working on it that some of the generated files from intake or processing might need to be outside the person's directory and we focus on having just the gallery files.  Right now we're mixing up the intake/original and the output gallery files in a single structure.  I did want to revisit our structure as part of the sandbox work - so now seems like a good time to do that.  If we have some place for intake files and the processing of them separated from reports and from galleries - we can still move files around and we adapt things a bit.  But I need much more analysis of the current structure - future structure and just how big an effort this is with all the scripts we have.
````
<!-- markdownlint-enable MD013 -->

Nov 2, coverage: agreement -> LY1 checked and Decisions; old `_` directories
in sandbox and production -> the audit table and the Nov 2 retirement; clean
sandbox by full reset/re-run with timings while Acronis is off -> Order and
LY4; keep separation and only needed files (LEAN vs FULL/FAST) -> decision (e)
and the Modes section; plan alignment -> cross-links in storage, performance and
intake plans.

<!-- markdownlint-disable MD013 -->
````text
I agree with the recommendations - and we can also revisit existing _ directories in the sandbox and production for things that are also old and no longer used or useful due to all the changes.  So, we can get the sandbox into a clean state - and I know that might mean a full rebase and re-run, but that's what I want to see in the long run.  Since I have Acronis disabled now - I am hoping that the process is actually faster and all out timings will help.  Ultimately, keeping the separation, but still having files exist for references will help in the long run and only keep files generated we need.  That was all part of the LEAN type processing we were doing vs. FULL and FAST ... so we'll need to re-read and sync up all these items along with that existing plan and bring all the docs/plans into alignment and ensure directory structure makes more sense.
````
<!-- markdownlint-enable MD013 -->

Nov 2, coverage: move forward with the changes -> LY2, LY3, LY5 implemented and
tested; gallery holds only what is needed after the full process -> the
`gallery`/`review`/`944x1104` person layout and `_processing`; re-copy
production (with the new `Various\gallery` photos) into a fresh sandbox, run it
end to end, then redo the whole process from documented steps -> LY4 and the
LY6 runbook; status update -> the session reply and recap.

<!-- markdownlint-disable MD013 -->
````text
Let's move forward with those changes and then give me an update on where we are at - we need that we properly handle the structure so the gallery is cleaner and only has what we need after the full processes.  Basically - I want to re-replicate copying down the existing Production directory to the Sandbox.  I have files into the production Various/gallery so that when we snap things all from the start that things will work end-to-end in a fresh sandbox that isn't in the current state we're in.  So when we get things tested and verified are working - we'll need to step back and re-do that entire process and ensure all documentation and steps for executing it are in place and we can see the first runs working on a fresh sandbox and then we'll know how it processes, how it cleans things up that might not align or how the process works on that fresh sandbox set of galleries.
````
<!-- markdownlint-enable MD013 -->

Nov 2, coverage: commands and their order, and what copies exist at each step
of a fresh sandbox -> answered in chat as stages 0-5 and recorded as the LY6
runbook; workflow names injected at generation -> LY5 changes only code paths,
never the generated workflow JSON by hand, and keeps file names unchanged.

<!-- markdownlint-disable MD013 -->
````text
Before you start with a complete refresh of the sandbox - tell me what commands we run and in what order to get things going.  I want to understand just how it works when we snap the fresh and new copy of production down to the sandbox and all what we do run and what copies of things we do have in the sandbox at each step along the way.  More of a sandbox processing for dummies type step-by-step read out.
````

````text
Workflows are generated and the names get injected to them in the generation process.
````
<!-- markdownlint-enable MD013 -->

Nov 2 16:27, coverage: "Have we been finding issues" -> the lock fixes in LY4;
do not copy unneeded files into the sandbox -> the reset already leaves
regenerable output behind, and LY7 leaves Artists out; a concise, clean
sandbox on demand and a known way to run directly in Production with its
existing clutter -> LY8 true-up, gated on LY4 acceptance; clean break from
Artists (no copying or processing in the sandbox) -> LY7, with the Production
Artist scope kept at intake I74.

<!-- markdownlint-disable MD013 -->
````text
Have we been finding issues or what is going on?
````

````text
I hope this doesn't stop the background task ... but Yes - let's not copy forward files we don't need into the sandbox - which goes along with re-structuring things to make it easier to determine that in the future state as well as current state.  While we will have to deal with running a clean re-base directly into production - if we need to do something to clean it up ahead of time or to restructure things, I'll need to sort that out so we get a) a concise and clean sandbox when we want a new one and b) know exactly how to deal with production runs directly that may have a lot of existing structure and fragmented or unncessary files in many areas already.  That's a true-up that needs to happen in Production when we get the sandbox working the way we want it.
When running - we need to make a clean-break from doing anything with Artists - that was one of the plans and maybe we didn't finish that but it would save a lot of time in both copying files down to the Sandbox and processing them - if we don't actually want to process the Artists in the sandbox - which I do not want at this point.
````
<!-- markdownlint-enable MD013 -->

Nov 2 evening, coverage: run the sandbox to completion with every move and
rename applied, then review the galleries and trace back through intake,
comparisons and history -> LY4 attempt 3 (full apply) and the automatic recap;
an HTML page of what happened -> `rebase-recap\<run>.html`; who goes where,
renames, cast pulls, Review, who leaves, nearest identity, shared surnames ->
recap sections; "who do I think they look like" and the dropped-in test
images -> the Looks like picker and `rebase-expectations.json` (LY11);
protect Angels/Sisters while letting aligned supplements join, tune if too
many land in Review -> cast matches held in Review this run, tuning after
LY11, core-seed comparison LY10; repeatable automation, not one-off -> the
recap runs after every `sandbox-rebase.cmd` step; morning expectation of a
complete, clean rebase with docs and plans synced -> LY4 acceptance, this
plan, STATUS.md and the Nov 2 recap.

<!-- markdownlint-disable MD013 -->
````text
Since this is a sandbox - I'd actually like it to run to completion and actually move ahead with all the moves, renames of all files.  I want to see what does move in/out of the galleries, what is actually renamed, how does history look for those, etc... I do want a recap of what did happen - if we have a .html page that shows all that would be great.  I really want to check the final gallery UI and then drive backwards through what did happen and if needed review the intake processing work, see what the comparisons did and how things moved.  Hope this makes sense - we can have you check things for my human review - but when I come back, I want to see if we can't run it all the way and apply all changes and see what happened with the galleries.  I am doing this because I know some pictures for angels might fall out and some pictures in various SHOULD land in angels or sisters and that some things may end up in review, but if there are too many - then we need tuning.  As you know, I want protect the core identity of angels and sisters and if images supplement and align - they should be there, even with low scores so we don't create additional identities that ARE one of those - but if many fall out into a Model and the surname indicates the alignment - that'll help.  I can see when looking at a gallery just how close it aligns to other identities and that helps me see if it is or isn't someone else and it's just that our face scoring could use further improvements.  Does this all make sense on how far I want the rebase to run and how much I want to see all the actual changes applied?  Since it's sandbox - we can be aggressive in how we approach it since we can always make updates and re-run all or some pieces depending no my final feedback of the entire end-to-end run.
````

````text
Ultimately what I want to understand is who goes where in terms of the final end-to-end processing, who's renamed, who pulls from angels or sisters based on core, who is in review, who moves out - all that helps me understand what actually heppened in a run and why, who are they closest to, are they sharing surnames or not.  Who do I think they look like.  I know I have dropped in images to test this and that's what I want to see happen and how the entire system we have setup is or is not working to my visual reviews at the final outcome of the rebase.  Does that make sense and what questions do you have for me based on this comment?
````

````text
I want this to be repeatable and part of the automation, not a one time thing
````

````text
What I expect in the morning is a full and clean rebase completed and I can start to review the GUI and capture feedback about the GUI and results.  Don't forget to review and update docs/plans and to ensure you build all what we need and any late breaking things we decided that are not in the plans do get into the plans.  It's a complete end-to-end and sync up with docs and decisions.  So finish all what you know is needed for all this.
````
<!-- markdownlint-enable MD013 -->

## speed_and_space_optimization.md (Nov 4, verbatim)

Coverage: derivative cap, protect/unprotect generation and clean-up, Various
derivatives and the bottleneck question -> LY14 (measured Nov 4, decision
open); denoise/tone in LEAN -> LY14a (done); machine-transfer setup -> the main
README and the Nov 4 hand-off recap.

<!-- markdownlint-disable MD013 -->
````text
What if during the process we "cap" the number of 944x1104 images we generate for a single identity and focus on generating them for the core set of images based on score or any protected or workflow set?  Just wondering if that would actually speed up the end-to-end process and save on disk space.  We can still keep all the originals and show them in the review and if we protect one, it would auto generate the 944x1104 version.  We'd also need to ensure if we unprotect one and it moves out that we clean-up the various generated images.

I am wondering if this would have an improvement on overall processing, amount of files copied - checked etc... it would reduce the spwral of generting so many images - but I don't know if it would actually save time.  

I also don't think Various needs to generate all possible 944x1104 images that are left there for review as well.  Unless moving them would want to have those generated already.  

I guess - I want to know in the rebase process where the time is being spent and if capping the number of generated images would actually make a noticeable difference.

I'd want to know where the bottlenecks are in the processing overall.
````

Chat (Nov 4):

````text
I have this question in the speed and optimization - if you find somewhere else where we're taking so much time - how can we trim that down.  I also thought we were going to skip the denoise and tone images if we're running LEAN or was that in a different approach.  We've done a lot of optimization to save space and improve speed - but I see that the sandbox state is 17GB and looks like a lot of that is the denoise and tone images.  So please let's figure this out before one last re-run on this maching.  I am getting my other machine setup to run and we'll need to shift to being able to ensure we have a write-up on how to get that machine setup in the main README.md and setup instructions for the development environment - what tools we use when working and how it all works - and a hand-off with recap on where we are so I can pickup on that machine.   But first - we need to sort out these last enhancements we need to do while memory and context are up to date.
````

Chat (Nov 4, 12:07; coverage: full reset vs reuse -> recap "Last re-run"
answer; previous run removal approved -> the full reset removes it; live
progress and process-flow recap -> LY14b):

````text
Is there any point in doing a full re-run from the start and resetting the sandbox to the original state and not re-running on this existing one?  Or what is recommended as the next step?  I'm fine if the previous run and all it's files are removed - this is a sandbox for that purpose.  So what makes the most sense to run and how to test out the full space reduction and timings?  I'd also like to see more intermittent feedback as the processes are running so I know where we are, what finished, what those times were and what remains along the way.  More of a process flow recap as it goes along.
````

````text
The recap needs to be updated if we do different commands - they were already in the recap.
````

Chat (Nov 4, 12:29; coverage: optional previews -> LY14b `--with-previews`;
the backup of the fresh baseline is required by the install and never copies
the discarded run -> recap "Last re-run"):

````text
Also - I'm thinking the preview steps can be avoided - unless you are reading them to look for issues - otherwise, won't that also cut down on the time and we only worry about preview if we're actively concerned about the changes - but since we're in the sandbox and doing a full reset, I feel like we can skip those steps to save time as well.  Make sense?  Those are optional steps if we need to preview.  We don't need to backup the existing sandbox if we're starting the process all over and trying to see where the bottlenecks still exist and how much space we're taking up.  So both skipping preview and avoiding backing up an invalid run should help.
````

Chat (Nov 4, 13:28; coverage: live-run investigation above; reuse current run
evidence rather than competing benchmarks or changing the running engine):

````text
If we're seeing increases in time taken in our revised steps - I'd want to dig into those while we're waiting for the process to complete and understand what is going on as a whole.
````

Chat (Nov 4, duplicate context; coverage: exact-byte/ID gaps -> LY14c;
space reconciliation -> copy/verification proposals above; no source deletion):

````text
I also don't understand the increase in size from the previous run - I still feel like we're making too many copies or backups during the process or something is off in how we're handling things.  So we definitely have some issues along the way.  I did include a bunch more items on the Production Various/gallery that are duplicates of many already processed - I was planning on sending those in for complete re-processing in case I missed items - so our de-duplication of photos should be catching that and throwing them out as duplicates.  So maybe that's an issue that doesn't work well in our system.
````

Chat (Nov 4, 22:02 continuation; coverage: fresh-reset acceptance -> N15/LY4;
core-only retention -> existing cast/engine policy, not whole-folder protection;
disposable recovery and speed fixes -> LY14c/LY14d/LY14e. Production/FULL stay
protected; FAST is not silently implemented):

````text
Don't stop the analysis you are doing, just want to make sure that If we again need to start completely fresh sandbox working directory - that's what I expect after we find and fix the issues with the performance concerns, duplicates and space issues from the last run.  We need those identified so we can get to a clean run that meets my expectations.

And when we run we're just supposed to protect the core of the sisters and angels in the run as well - so that if some of their photos move out - that should be happening.  I don't know if that was part of the run we did this last time or not - but that was one of the key things we were working on testing before we worked on the family tree fixes.  So things are complicated, yes - but we'll get there eventually.

You can start the totally fresh run when you are satisfied you have address some of the key issues that are causing the major slowness and how it all works.  Adding checks or threading to places where it makes sense to speed things up when in LEAN mode and decrease the number of back-ups and extra copies.  Maybe we can skip some roll-backs since we are in the sandbox and don't need backups as we'll just start fresh again.  So that's the type of thinking I am looking for.  When it comes to production or a FULL run then we need those items, but LEAN should assume a positive outcome or a fresh rebase in the sandbox.  FULL is protective and still needs to exist - but LEAN is LEAN.  The FAST one is supposed to be even more aggressive at skipping all backups, rollbacks and cutting corners.  LEAN is the balance on quality and speed - but the rollbacks are actually less important.  Showing what went where and the report is a LEAN item - but maybe in FAST we don't even track all that and that's a key difference.  So, just more items to digest before you get through and re-run everything while I am asleep.
````
<!-- markdownlint-enable MD013 -->

## Nov 5 final-preflight requests (chat, verbatim)

Coverage: remaining bounded coding -> LY15b and gallery L18; visible
terminal walkthrough after coding -> LY15c; no processing before LY15a.

<!-- markdownlint-disable MD013 -->
````text
So, are there any other "low hanging fruit" items from our past iterations that we did not finish that we should couple into this work?  I guess, I want to ensure we don't leave out something prior to this next "pickup run" after intake.  I'd also like to know if you can run items in a terminal for me to see the progress as when you run in a background process - I cannot see output of something running - unless you can tell me how to get to see that from within VS Code.  Address these two questions and then tell me what remains to bundle with this work (if anything) and also how I can see the work running in real-time.

Let's proceed with the last few items we need to get done prior to running and then you and I can walk through how I could run commands in a terminal window directly or you can launch them into a terminal so I can see them.  We'll work on that after you get the final set of coding changes done.
````
<!-- markdownlint-enable MD013 -->

## Nov 21 studio request (chat, verbatim)

Coverage: proposed studio model and open questions -> LY16; scoped matching
and performance -> LY17/LY21; promotion/demotion -> LY18; named intake,
original name and protection -> LY19 with N12/N13; migration -> LY20.
This is planning-only, with no change to current Queue focus.

<!-- markdownlint-disable MD013 -->
````text
One thing I would like expanded on and fleshed out is actually that I'd like to have multiple Studios where a studio is the collection of the galleries.  Meaning, one studio has Drakn Sisters with categories (Sisters, Angels, Models, Prospects, Potentials).  The other studio would be for Artists (categories to be defined), another for Drakn Bound (Brothers, Demons, ... ) and another for Creatures (which would be for animal type cards) and another for Females (which would be lower level cards of people) another for Males (lower cards as well).  Each one would have their own set of categories, rules and such.  That would likely mean a total restructure of the B:\Sovereign Territories directories so it holds various studios (B:\Sovereign Territories\Drakn Sisters, B:\Sovereign Territories\Drakn Bound, etc...).  Maybe I also need to think about separation from males to females to animals, etc... as well so we don't get the likeness to be criss-crossing males and females.  So I need a plan written up with a proposal for how we'd transition to that state.  It's not immediate, but I have a bunch Female images to bring in that won't be part of the Drakn Sisters and likely I'd move a bunch of Prospects and Potentials to there as a "downgrade" if I don't see them used there and it would then reduce the time it takes to process images.  I'd also want to be able to promote and demote various images.  It might not be Drakn Sisters as that's a mix of Sisters and Angels - so maybe it's more a split of higher level cards and lower level cards with the Females.  I can't think of a good split - but the concept is formation of studios, each with their own Intake (currently called Various) and I'd also like it so that we handle the situation where we have an intake of something like Various/Ela Model and it uses Ela Model as the original name and protects all images for that instead of just Various/Gallery.  That's a lot to digest so we need a plan - series of questions - and work to refine just how we'll handle all my requirements.  Can you start to work on that while the other agent is doing his work?
````
<!-- markdownlint-enable MD013 -->

## Nov 21 subject and tier clarification (chat, verbatim)

Coverage: subject and three-tier direction -> LY16; independent incoming
comparison, scoped rebase and normal operation -> LY17/LY21; movement
between tiers -> LY18; named sets and protection -> LY19/N13; separate
workspace and transition -> LY20/P19/P20/R44. Card-tier references are
discussion context, not a new game rule.

<!-- markdownlint-disable MD013 -->
````text
I haven't reviewed all the questions - but ultimately I want to separate our males and females and animals as a top level.  The idea of studios is that I do want to have a place I can bring in new males and females and if I need to rebase, I don't want to run through all thousands of images again - so maybe what I am looking but I would like them compared against the likeness of existing but don't necessarily to pull or change those, but want to know their similarity against them without having go stand up the sandbox.  I have a bunch of images that will have a name assigned as I do know who those are and don't need them pooled with others - and want to make them available for another ComfyUI workspace without them going into the main studio.  So that's probably more my concerns is that I has a two-tier approach for males, female and animals.  It's more like the top-tier of cards and lower tier cards.  I think we drafted that boundary in the card documentation and maybe that's the split I am looking for in the studios.  But if I have someone in a top-tier studio and want to push them down or vice-versa, that's more like what I want.  Plus I also need a lower tier studio where I can just bring in any images and assign them to a totally separate workspace - so, I guess that's 3 tiers for each female, male and creature/animal.  Does that help - I don't want to overcomplicate, but once we get things working - I hope I don't need the sandbox, except when testing our major changes again.  So the sandbox is for major development changes.  The 3 tiers for the normal art processing.  It splits the things between the genders and animals to keep from criss-crossing.  We can answer named intakes, next.
````
<!-- markdownlint-enable MD013 -->

## Nov 21 named-intake clarification (chat, verbatim)

Coverage: supplied original-name recovery, duplicates and history -> N12/N13;
high-scoring protection and low-scoring exceptions -> N13/LY19; normal
category rules -> processing contract; cross-studio extension -> LY19.
Confirmation was resolved by the following response; thresholds and
outlier handling remain open.

<!-- markdownlint-disable MD013 -->
````text
In terms of named intake - if there is a named intake it means that IS the original name of a person and I'd want that to stick with the core and protect all high scoring photos - there's a chance I made a mistake and do have a really low scoring image that obviously doesn't belong, but ideally each one IS that and might contain different facial expressions and such.  The idea is that we try to keep from losing that original name of Ela Model, especially if it resembles an existing randomly genreated name - I'd want those photos pulled into Ela Model instead of the reverse.  How it's categories in Models, Prospects and Potentials would follow the normal rules - but this is a way for me to correct any existing identities that should be named based on a name that was lost in previous runs that where we had group-to-group combining and lost names.  OR I didn't know the name and eventually figured it out and not I might be replaying existing images (that duplicate others already in a gallery) and I am basically performing a renamed as well as potentially adding new images.  What else do I need to answer.
````
<!-- markdownlint-enable MD013 -->

## Nov 21 automatic name correction (chat, verbatim)

Coverage: automatic correction/new identity and history -> N12/N13/LY19;
fixed character names and correction of wrong current/original names -> N12/N13.
Implementation, acceptance and library publication remain separately gated.

<!-- markdownlint-disable MD013 -->
````text
Automatically - if I provide a named folder - that is what I expect to either be a new identity with that name or rename an existing one.  I still want to know the previous history of existing, but they take on that name original name.  In terms of sisters or angels those character names are locked.  There is at least one case where the original name and current name (not character name) of an identity is not right and was altered wrongly in past runs.
````
<!-- markdownlint-enable MD013 -->

## Nov 21 name-collision clarification (chat, verbatim)

Coverage: asserted original name and collision resolution -> N12/N13/LY19;
name swap transaction -> A3; preserve both identities and their history
-> N12/N13. Which resolution and person-name fields apply remains open.

<!-- markdownlint-disable MD013 -->
````text
If there is a conflict and that original name matches another existing identity - we'd name swap or assign a new random name to the other one to the other one.  The point is that I am asserting is that this identity is this person firstname lastname and we need to fix previous issues when mis-merges and mis-names happened.
````
<!-- markdownlint-enable MD013 -->

## Nov 21 swap preference (chat, verbatim)

Coverage: prefer a history-aware swap, with random-name fallback -> N12/N13
and LY19, coordinating A3. The Harbor question is handled in the existing
collaboration discussion; it does not authorize library or workspace writes.

<!-- markdownlint-disable MD013 -->
````text
Well, when it comes to swapping - I would prefer to swap names versus a random new name - unless that previous name is being used with many other names ... so check history of the identity and make the best choice can be th elogic.  Also, sounds like Harbor was looking for some input from your as well?
````
<!-- markdownlint-enable MD013 -->

## Nov 21 legacy name-history clarification (chat, verbatim)

Coverage: history-based name-conflict resolution -> N12/N13 and LY19.
Legacy name churn is a data-reliability concern, not a numeric fallback
threshold; do not ask the user to restate this clarification.

<!-- markdownlint-disable MD013 -->
````text
What I mean is that sometimes a person may have changed identity many times through our bugs and issues we're working through - prior to be creating a sandbox, so the current production snapshot has issues with what was or is the name of identities.  I think that clarifies, but not ask again.  I may not understand my long rambling earlier myself - lol.
````
<!-- markdownlint-enable MD013 -->

## Nov 21 intake, studio order and future Gallery clarification (chat, verbatim)

Coverage: named Various path rules before studio structure -> LY19/N13/I24/I75;
female, male, creature sequencing -> LY16/LY20; future per-workflow image
selection and generated-image Gallery lineage -> LY18/P12/P19/P20/R44/I21/I23/L12/L19.
The sequencing refines holding work and does not change the active Queue focus.

<!-- markdownlint-disable MD013 -->
````text
In terms of the library layout plan, I'd first like to handle the incoming Various/(person name) and Various/(person name)/gallery rules ahead of the Studio organization.  That is longer term but is still a priority since I am going to start splitting the females into the 3 tiers and working on the males and then creatures.  Adjusting Intake so it works right and the getting the Studios in place will help. Eventually we'll also get to the Workflow photo assignment and it's not one photo for all workflows, but will be each Workflow can have a photo tied to it - either from the Gallery or from a Comfy UI generated image.  So that's more to feed into the complexity of the Gallery and also Generated images coming back into a gallery.  That's when the real fun starts to build a Gallery with not just Intake but Generated images.
````
<!-- markdownlint-enable MD013 -->

## Nov 21 intake, studio order and future Gallery clarification (chat, verbatim)

Coverage: named Various path rules before studio structure -> LY19/N13/I24/I75;
female, male, creature sequencing -> LY16/LY20; future per-workflow image
selection and generated-image Gallery lineage -> LY18/P12/P19/P20/R44/I21/I23/L12/L19.
The sequencing refines holding work and does not change the active Queue focus.

<!-- markdownlint-disable MD013 -->
````text
In terms of the library layout plan, I'd first like to handle the incoming Various/(person name) and Various/(person name)/gallery rules ahead of the Studio organization.  That is longer term but is still a priority since I am going to start splitting the females into the 3 tiers and working on the males and then creatures.  Adjusting Intake so it works right and the getting the Studios in place will help. Eventually we'll also get to the Workflow photo assignment and it's not one photo for all workflows, but will be each Workflow can have a photo tied to it - either from the Gallery or from a Comfy UI generated image.  So that's more to feed into the complexity of the Gallery and also Generated images coming back into a gallery.  That's when the real fun starts to build a Gallery with not just Intake but Generated images.
````
<!-- markdownlint-enable MD013 -->

## Nov 22 named intake path decision - verbatim form answer

Coverage: direct-root and child intake -> LY19/N13/I24; distinct unnamed pool,
duplicate handling and Review semantics remain part of acceptance. This
decision does not change the active queue or authorize an intake run.

<!-- markdownlint-disable MD013 -->
```text
To restart the named-intake Q&A: should photos placed directly in `Various\<Person name>` count as part of that named identity intake, alongside any `gallery`/`review` children? The current conservative proposal is to accept only child folders and report/hold direct-root photos. The Nov 22 rebase work did not settle this intake-path rule.

accept
```
<!-- markdownlint-enable MD013 -->

## Nov 22 named intake outlier decision - verbatim form answer

Coverage: normal-rule automatic reassignment of a low-scoring named photo with
an eligible stronger match -> N13/LY19; numerical boundaries remain open.
This does not authorize an intake run or extend the separately scoped rebase
override.

<!-- markdownlint-disable MD013 -->
```text
Next, one important conflict: an older plan says every photo in a named folder must stay together, while your later clarification protects high-scoring photos but recognizes a very low-scoring photo might be a mistake. During ordinary named intake or later normal processing, what should happen when a submitted photo scores very low against the named person and has a stronger eligible match elsewhere? A score alone does not prove identity; the separately authorized Sandbox rebase remains a different case.

reassign
```
<!-- markdownlint-enable MD013 -->

## Nov 22 named intake without eligible rival - verbatim form answer

Coverage: normal unassigned-photo routing for a low-scoring named photo with
no eligible rival -> N13/LY19, subject to normal quality, formation and
protection rules; preserve name/source provenance and report the disposition.

<!-- markdownlint-disable MD013 -->
```text
Recorded: a very low-scoring named-intake photo can move automatically to a stronger eligible identity under normal matching and protection rules. What should happen if it scores very low against the named person but no other identity qualifies to receive it?

normal-routing
```
<!-- markdownlint-enable MD013 -->

## Nov 22 named-group duplicate tie-break - verbatim form answer

Coverage: among equally large, similarly consistent groups, select the only
group with an existing exact duplicate -> N13/LY19; no duplicate is an
independent vote or proof of the asserted person's identity.

<!-- markdownlint-disable MD013 -->
```text
If two coherent groups in a named folder are equally large and similarly consistent, but only one contains an exact duplicate already in an existing identity, should that duplicate break the tie? It establishes continuity with the existing photo, not proof of who the named person is.

duplicate
```
<!-- markdownlint-enable MD013 -->

## Nov 22 unresolved named-group tie - verbatim form answer

Coverage: choose automatically and show the decision when equally supported
groups have no distinguishing duplicate -> N13/LY19. Specify a repeatable
tie-break; preserve the tie and source evidence without claiming identity proof.

<!-- markdownlint-disable MD013 -->
```text
If the groups are still tied—same size and similar consistency, with no distinguishing existing duplicate—should the system pick one automatically or ask you which group carries the supplied name?

automatic
```
<!-- markdownlint-enable MD013 -->

## Nov 22 user-controlled tier moves - verbatim form answer

Coverage: whole-person promotion/demotion requires user initiation or
approval -> LY16/LY18. Automatic promotion of a user-selected cast replacement
is part of that initiated operation, not a separately autonomous move.

<!-- markdownlint-disable MD013 -->
```text
Should the system ever move a whole person between tiers on its own, or should tier promotion and demotion happen only when you initiate or approve it? This is separate from automatically routing a new photo to a person already in another tier.

manual
```
<!-- markdownlint-enable MD013 -->

## Nov 22 generated-only identity retirement - verbatim form answer

Coverage: retire a person with no Gallery/Review originals even if Generated
contains images -> LY18/R44 and RA2j retirement; preserve the Generated
folder and history. The existing emptied-cast stop is not explicitly changed.

<!-- markdownlint-disable MD013 -->
```text
The current rebase plan retires identities when their photo folders are emptied. With the new Generated folder, what should happen if a person has no Gallery or Review originals left but still has generated images?

retire
```
<!-- markdownlint-enable MD013 -->

## Nov 22 retired generated-image access - verbatim form answer

Coverage: retired generated images remain history-only, not selectable for
workflows -> LY18/R44. Preserve prior bindings and define their unavailable
state without silently replacing them.

<!-- markdownlint-disable MD013 -->
```text
Should generated images from a retired person remain available to select for workflows, or be preserved only as history?

history_only
```
<!-- markdownlint-enable MD013 -->

## Nov 22 multi-person generated-image ownership - verbatim form answer

Coverage: when a source photo of a two-person generated image is reassigned,
keep the output in place and flag it for the user's decision -> LY18/R44.
Define multi-input lineage without inventing a primary owner.

<!-- markdownlint-disable MD013 -->
```text
One lineage edge case: if a generated image uses photos of two different people and one source photo later moves to another identity, which person’s Generated folder should hold that image?

manual
```
<!-- markdownlint-enable MD013 -->

## Nov 22 Artist-owned photo isolation - verbatim form answer

Coverage: Artist-owned photos stay exclusive to the Artist studio, even when
the person also appears in a subject tier -> LY16/LY18. Do not infer identity
merges or permission to move Artist photos across domains.

<!-- markdownlint-disable MD013 -->
```text
Artists are isolated from the subject tiers, but the same person can appear in both. Should an Artist-owned photo ever be usable in that person’s subject-tier Gallery, or should Artist photos stay exclusively in the Artist studio?

isolated
```
<!-- markdownlint-enable MD013 -->

## Nov 22 physical tier folders - verbatim form answer

Coverage: each subject group's tiers use separate physical folders, not only
views over a shared library -> LY16/LY18. Folder names, exact paths, workspace
mapping and authorized migration remain open.

<!-- markdownlint-disable MD013 -->
```text
The studio plan still leaves one structural choice open: should the three tiers be actual separate folders, or views over one shared people library? Either way, a person belongs to one subject tier and the experimental tier can have its own workspace.

physical
```
<!-- markdownlint-enable MD013 -->

## Nov 22 reverse cross-tier intake - verbatim form answer

Coverage: qualifying top-tier arrivals go to the existing lower-tier person
-> LY16/LY17/LY18. Apply normal matching, protection and transaction rules;
do not promote the person without the user's initiation or approval.

<!-- markdownlint-disable MD013 -->
```text
We’ve settled that a matching photo arriving in a lower-tier intake can automatically join an existing top-tier person. What about the reverse: if you drop a photo into top-tier intake and it matches a person already in a lower tier, should the photo automatically join that lower-tier person, or be held for your decision? The person would not be promoted automatically.

route
```
<!-- markdownlint-enable MD013 -->

## Nov 22 female tier naming - verbatim feedback

Coverage: propose short, creative names not tied to existing cast categories;
`Lab` is liked for the experimental tier; the user selects `Apex` and `Forge`
for the upper and lower-card tiers -> LY16. A later answer applies all three
names to the male and creature tiers too.

<!-- markdownlint-disable MD013 -->
```text
Give me a proposal for the 3 names - not specific to Sisters/Angels as I may add more upper tier categories.  But I want them to be short names and still creative.

I like Lab for the bottom but the other two might need some more choices - give 5 choices for each and I'll settle on the names from that

Which names would you choose for the first two?

upper=Apex, lower=Forge
```
<!-- markdownlint-enable MD013 -->

## Nov 22 tier naming across subject groups - verbatim form answer

Coverage: use Apex, Forge and Lab for female, male and creature groups ->
LY16; exact directory paths and migration remain to be designed.

<!-- markdownlint-disable MD013 -->
```text
Apex and Forge it is, with Lab for the experimental tier. Should those same tier names also be used for males and creatures, or should each subject group have its own names?

same
```
<!-- markdownlint-enable MD013 -->

## Nov 22 per-tier intake - verbatim form answer

Coverage: each tier has its own intake folder -> LY16/LY19. Subject and
intake placement choose the starting tier, not permission to move a whole
person; qualifying arrivals can route across tiers under normal rules.

<!-- markdownlint-disable MD013 -->
```text
For each subject group, should Apex, Forge and Lab each have their own intake folder, or should there be one shared intake where you choose the destination tier?

per_tier
```
<!-- markdownlint-enable MD013 -->

## Nov 22 intake folder name - verbatim form answer

Coverage: name each future tier intake folder `Intake` -> LY16/LY19. Keep
current `Various` paths until an authorized migration; define compatibility.

<!-- markdownlint-disable MD013 -->
```text
What should each tier’s intake folder be called? Today the folder is `Various`; changing the name would be a future, verified migration—not an immediate rename.

Intake
```
<!-- markdownlint-enable MD013 -->

## Nov 22 Forge categories - verbatim feedback and form answer

Coverage: select Potentials and Prospects for people in Forge, using current
photo-count groupings as a starting point for validation; omit the cast-oriented
Models category -> LY16/LY17. This does not select creature rules, authorize
an automatic tier move, or implement a new policy.

<!-- markdownlint-disable MD013 -->
```text
I'm uncertain - do you have a recommendation on what makes sense based on how we have things setup and my goals?

I recommend **two Forge categories: Potentials and Prospects**.

- **Potentials:** newer identities with a small photo set.
- **Prospects:** established identities with a larger set, intended for lower-card work—not automatically candidates for Apex.

This builds on the current draft’s one-to-four versus five-or-more usable Gallery photos, while keeping tier moves under your control. I would **not automatically add Models**: today that draft category is tied to similarity to existing cast, which doesn’t naturally describe Forge’s purpose. See [likeness.md](C:/Soverign-Territories/soverign-territories/docs/art/likeness.md:1074).

The trade-off: this keeps familiar grouping without forcing cast-oriented categories into Forge, but the exact rules still need validation before implementation. Does that direction fit?

recommended
```
<!-- markdownlint-enable MD013 -->

## Nov 22 Lab categories - verbatim form answer

Coverage: Lab identities use Potentials and Prospects like Forge -> LY16/LY17,
without implying a card plan; validate the applicable rules and creature
handling before implementation.

<!-- markdownlint-disable MD013 -->
```text
For Lab, you’ve already chosen automatic grouping into identities. Should those identities also be split into Potentials and Prospects, like Forge, or sit directly under Lab without those extra categories?

same
```
<!-- markdownlint-enable MD013 -->

## Nov 22 within-tier category transitions - verbatim form answer

Coverage: automatically transition between Potentials and Prospects within
Forge or Lab under applicable rules -> LY16/LY17. Validate thresholds,
protections and recoverable movement; whole-person tier moves remain
user-initiated or approved.

<!-- markdownlint-disable MD013 -->
```text
Within Forge or Lab, should a person automatically move between Potentials and Prospects as their qualifying photo count changes, or should you approve those category changes? This stays within the same tier; moving between Apex, Forge and Lab remains user-controlled.

automatic
```
<!-- markdownlint-enable MD013 -->

## Nov 22 creature-kind matching isolation - verbatim form answer

Coverage: different creature kinds do not compare for likeness -> LY16/LY17.
Define the taxonomy, selection, uncertain cases and suitable model; this does
not authorize creature processing.

<!-- markdownlint-disable MD013 -->
```text
For the future creature studios, should likeness matching stay within a creature kind—for example, horses with horses and dragons with dragons—or may it compare different kinds within the creature group? This is a planning choice; we have not selected a creature-matching model.

isolated
```
<!-- markdownlint-enable MD013 -->

## Nov 22 creature-kind selection - verbatim form answer

Coverage: manual versus automatic creature-kind selection is deferred to
LY16/LY17; do not infer a choice from matching isolation.

<!-- markdownlint-disable MD013 -->
```text
How would you prefer to specify a creature’s kind at intake so that matching stays isolated?

later
```
<!-- markdownlint-enable MD013 -->

## Nov 22 cast-person role exclusivity - verbatim form answer

Coverage: a Sister/Angel's assigned person is exclusive to that character,
not also used for generic cards -> LY18 and workspace/cast owners. Define
generated-input and binding interactions without duplicating the identity.

<!-- markdownlint-disable MD013 -->
```text
One role question: if a person is assigned to a Sister or Angel in Apex, may that same person also be used for generic cards, or should their use be exclusive to that character? This would not create another identity or change the tier.

exclusive
```
<!-- markdownlint-enable MD013 -->

## Nov 22 workflow photos on cast replacement - verbatim form answer

Coverage: automatically choose suitable replacement-person photos for
affected workflow selections -> LY18 and workspace/cast owners. Each workflow
retains its own binding; the later answer selects explicit unavailability if
no suitable photo exists. Selection criteria remain open.

<!-- markdownlint-disable MD013 -->
```text
When a Sister or Angel gets a replacement person, what should happen to workflow photo selections that pointed to the demoted person? Each workflow can have its own selected photo.

automatic
```
<!-- markdownlint-enable MD013 -->

## Nov 22 missing cast-replacement workflow photo - verbatim form answer

Coverage: allow the character replacement to proceed while marking an
affected workflow unavailable if no suitable photo exists -> LY18 and
workspace/cast owners; retain prior binding history and recovery.

<!-- markdownlint-disable MD013 -->
```text
If the replacement person has no suitable photo for one of the affected workflows, should the character replacement wait until that photo is available, or proceed with that workflow marked unavailable?

proceed
```
<!-- markdownlint-enable MD013 -->

## Nov 22 named-group size and strength - verbatim form answer

Coverage: balance eligible group size and within-group matching strength ->
N13/LY19. The formula and calibration cases remain to be specified; this does
not change the normal formation gates or equate matching with identity proof.

<!-- markdownlint-disable MD013 -->
```text
One last detail about choosing the named group: if a larger group only just meets the normal coherence rules, but a smaller group matches itself much more strongly—and both are otherwise eligible—which should take the supplied name?

balance
```
<!-- markdownlint-enable MD013 -->

## Nov 22 competing existing identities - verbatim form answer

Coverage: automatic, shown selection between about-equally plausible existing
identities for a named group -> N12/N13/LY19. The later answer selects a
naming-only margin exception; define ties, evidence and safeguards. This does
not authorize merging the identities.

<!-- markdownlint-disable MD013 -->
```text
Next, an ambiguity involving existing identities rather than groups within the incoming folder: if the chosen named group matches two established identities about equally, should intake automatically choose one to receive the supplied name, or hold that identity correction for your review? The two existing people would not be merged.

automatic
```
<!-- markdownlint-enable MD013 -->

## Nov 22 named identity margin exception - verbatim form answer

Coverage: permit the shown person-name correction when well-matched rivals
do not meet the normal margin -> N12/N13/LY19. No photo-admission gate,
identity merge, character name or unrelated protection is overridden.

<!-- markdownlint-disable MD013 -->
```text
The automatic choice can conflict with the normal rival-margin rule: two identities may both match well but be too close for an ordinary automatic match. In that case, may intake still apply the supplied person name to the better-supported identity, even though the usual margin is not met? This concerns the name correction only; it would not merge identities or bypass photo-admission rules.

allow
```
<!-- markdownlint-enable MD013 -->

## Nov 22 pulled-back generated-image access - verbatim form answer

Coverage: a selected generated image stays available across tiers as a
workflow input after Gallery pullback -> LY18/P19/P20/R44. Preserve synthetic
lineage; identity-evidence status and ownership remain separate decisions.

<!-- markdownlint-disable MD013 -->
```text
If you later pull a generated image back into a person’s Gallery, should other-tier workspaces still be allowed to select it because it is generated, or should the Gallery-photo tier restriction take precedence?

generated
```
<!-- markdownlint-enable MD013 -->

## Nov 22 generated-image core and view - verbatim answer

Coverage: never add generated images to the likeness core -> LY18/R44 and
Gallery L12/L19. The next answer selects a physical per-person Generated
directory; other evidence semantics remain to be decided.

<!-- markdownlint-disable MD013 -->
```text
Never - maybe we don't put them direct into the  Gallery but in a Generated directory - I think that was a concept I thought about earlier, but the viewer would show them.  So, sort of like Review, Gallery, Generated.  Maybe that helps simplify things?
```
<!-- markdownlint-enable MD013 -->

## Nov 22 generated-image physical storage - verbatim form answer

Coverage: select a physical Generated folder inside each person's directory
-> LY18/R44 and Gallery L12/L19. Preserve the current synthetic store until a
separately authorized migration and protect generated files through rebases.

<!-- markdownlint-disable MD013 -->
```text
The older rendering plan already stores generated files separately because person folders can be rebuilt during a rebase. Would a per-person Generated section in the viewer be enough if its files stay safely in that separate store, or do you want an actual Generated folder inside each person’s directory?

person-folder
```
<!-- markdownlint-enable MD013 -->

## Nov 22 generated images on tier change - verbatim form answer

Coverage: move the Generated folder with the person during promotion or
demotion -> LY18/R44, preserving workflow links, lineage, bytes and history.
Migration and installed behavior remain separately gated.

<!-- markdownlint-disable MD013 -->
```text
When a person is promoted or demoted to another tier, should their Generated folder move with the rest of that person’s identity, while keeping existing workflow links and history valid?

move
```
<!-- markdownlint-enable MD013 -->

## Nov 22 generated images on identity merge - verbatim form answer

Coverage: combine generated images of identities established as the same
person into the survivor's Generated folder -> LY18/R44, preserving source
lineage, links, history and collision-safe recovery. This does not authorize
an identity merge or a workspace write.

<!-- markdownlint-disable MD013 -->
```text
If two identities are established to be the same person and are merged, should generated images from both identities be brought together under the surviving person’s Generated folder? Their original generation history and workflow links would be preserved.

combine
```
<!-- markdownlint-enable MD013 -->

## Nov 22 generated images on source-photo move - verbatim chat

Coverage: move generated outputs with a reassigned source photo; include the
source photo ID in generated filenames -> LY18/R44, coordinating P12/P19/P20
and Gallery L12/L19. The later answer selects user review if retained lineage
cannot identify the source; legacy receipts and workflow links stay recoverable.

<!-- markdownlint-disable MD013 -->
```text
We'd want to move them - which means the generated images need the photo id as part of their name for us to know about which image was the source.  But there will be odd cases and would need decision if it's not clear in the name or how we pull them into the Generated folder for the person
```
<!-- markdownlint-enable MD013 -->

## Nov 22 ambiguous generated-source decision - verbatim form answer

Coverage: check retained lineage; if it cannot reliably identify the source,
keep the output in place and flag it for user decision -> LY18/R44.

<!-- markdownlint-disable MD013 -->
```text
For those odd cases: if the filename lacks a photo ID, we can first check the generation receipt and other retained lineage. If those still cannot establish which source photo was used, should the generated image stay where it is and be flagged for your decision, or should the system make its best guess?

review
```
<!-- markdownlint-enable MD013 -->

## Nov 22 lower-tier distinction - verbatim answer

Coverage: tier 2 as primarily planned lower-card work, tier 3 as uncertain
card use and free-form experimentation -> LY16/LY17/LY18 and P19/P20. Later
answers select physical tier folders and names; categories, exact layout and
promotion criteria remain open.

<!-- markdownlint-disable MD013 -->
```text
It would be more for experimentation of different sets of images that I am not sure I would make into cards or not.  The 2nd tier would be primarily for things I do plan to use for lower tier cards.  It's more that within Comfy whether or not we have the data/art setup for workflows for cards or if it's more free-form and I might be experimenting with all sorts of things in that workspace.
```
<!-- markdownlint-enable MD013 -->

## Nov 22 Artists studio - verbatim form answer

Coverage: a separate Artists studio with its own rules -> LY16/LY17/LY20;
existing provenance and protections stay in force while its detailed
relationship to other studios and migration remain open.

<!-- markdownlint-disable MD013 -->
```text
Next big question: where do Artists fit in the new three-tier structure? You originally described an Artists studio, while the newer direction separates subjects into female, male and creature tiers.

separate
```
<!-- markdownlint-enable MD013 -->

## Nov 22 Artists matching isolation - verbatim form answer

Coverage: do not compare Artist people with subject-tier identities, even
advisory comparisons -> LY16/LY17. Existing internal Artist provenance and
matching protections remain unchanged.

<!-- markdownlint-disable MD013 -->
```text
Should the Artists studio compare its people against compatible subject-tier identities and show possible matches, while keeping both collections unchanged?

isolated
```
<!-- markdownlint-enable MD013 -->

## Nov 22 subject intake selection - verbatim form answer

Coverage: the user chooses the female, male or creature/animal intake group
by placement -> LY16/LY17. Automatic subject detection/routing is not
selected; mixed/unknown handling remains to be specified.

<!-- markdownlint-disable MD013 -->
```text
For new photos, who should choose whether they belong to the female, male or creature/animal group before likeness processing?

manual
```
<!-- markdownlint-enable MD013 -->

## Nov 22 mixed subject photo - verbatim form answer

Coverage: allow a mixed human/animal photo in the manually chosen intake
when the intended main subject is clear -> LY16/LY17. Existing quality and
domain safeguards remain; intended-subject selection needs specification.

<!-- markdownlint-disable MD013 -->
```text
For a mixed photo—for example, a woman holding a dog—may it be processed in the female intake when the woman is clearly the intended main subject, or should mixed human/animal photos always be held for review?

main-subject
```
<!-- markdownlint-enable MD013 -->

## Nov 22 uncertain mixed-photo subject - verbatim form answer

Coverage: use the best automatic subject guess and visibly flag it when the
intended subject cannot be identified reliably -> LY16/LY17. Existing
quality/core-vote and subject-domain safeguards remain; do not invent a
measurement when there is no usable subject.

<!-- markdownlint-disable MD013 -->
```text
The current face engine chooses the largest detected face, which may not always be the intended subject. If the software cannot reliably identify the intended subject in a mixed photo, should it hold the photo for you to identify the subject, or use its best automatic guess?

automatic
```
<!-- markdownlint-enable MD013 -->

## Nov 22 whole-identity tier movement - verbatim form answer

Coverage: promotion or demotion moves the entire person and all Gallery,
Review and Generated photos -> LY16/LY18. Preserve name/history; fixed
character, protections, workflow eligibility and recovery remain to design.

<!-- markdownlint-disable MD013 -->
```text
When you promote or demote a person between tiers, should their whole identity move together—including Gallery, Review and Generated—or should you be able to choose only certain photos to move? Their name and history would be preserved either way.

whole
```
<!-- markdownlint-enable MD013 -->

## Nov 22 cast replacement before demotion - verbatim form answer

Coverage: select a replacement for a Sister/Angel slot before demoting its
person -> LY18 and cast/workflow owners. Preserve fixed character names,
history, protections and recovery; this does not authorize an actual move.

<!-- markdownlint-disable MD013 -->
```text
If you demote someone currently assigned to a Sister or Angel character, what should happen to that character slot? The character name and history remain intact either way.

replace
```
<!-- markdownlint-enable MD013 -->

## Nov 22 cast replacement promotion - verbatim form answer

Coverage: a user-selected lower-tier Sister/Angel replacement is automatically
promoted as a whole identity during replacement -> LY18 and cast/workflow
owners. Preserve both identities, fixed character names, histories and recovery.

<!-- markdownlint-disable MD013 -->
```text
If the replacement you choose for a Sister or Angel is currently in a lower tier, should choosing them automatically promote their whole identity into the top tier as part of the replacement?

automatic
```
<!-- markdownlint-enable MD013 -->

## Nov 22 Artist and subject-tier overlap - verbatim form answer

Coverage: allow the same person in an Artist collection and a subject tier
as a protected exception -> LY16/LY17/LY20. Existing Artist provenance and
no-automatic-reassignment safeguards remain in force.

<!-- markdownlint-disable MD013 -->
```text
If the same person appears in an Artist’s collection and in a female or male tier, should the Artist collection remain a separate protected exception to the one-tier-per-person rule, or should that person exist in only one studio overall?

separate
```
<!-- markdownlint-enable MD013 -->

## Nov 22 separate-workspace tier grouping - verbatim form answer

Coverage: automatically group unnamed photos within the separate-workspace
tier -> LY16/LY17, with subject-domain isolation and advisory cross-tier
comparison. Physical storage, model selection and implementation remain open.

<!-- markdownlint-disable MD013 -->
```text
For the third, separate-workspace tier: when you drop in unnamed photos, should it automatically group them into identities like the main library, or keep them as separate images unless you supply a named folder? Either way, comparisons with other tiers remain advisory and must not change those tiers.

group
```
<!-- markdownlint-enable MD013 -->

## Nov 22 one tier per person - verbatim form answer

Coverage: each real person is in one tier at a time; promotion/demotion
changes tier -> LY16/LY18. Physical storage, other roles and workspace access
remain separate decisions; similarity alone is not identity proof.

<!-- markdownlint-disable MD013 -->
```text
Can the same real person appear in more than one tier at the same time—for example, as a Sister in the top tier and also in the separate-workspace tier—or should promoting/demoting them move them out of the previous tier? This is about what you can use, not yet how files are stored.

one
```
<!-- markdownlint-enable MD013 -->

## Nov 22 confirmed cross-tier incoming photos - verbatim form answer

Coverage: confirmed separate-workspace-tier photos of a top-tier person go to
that existing person -> LY16/LY17/LY18. Comparison remains read-only; later
answers select normal core eligibility and automatic matching for new photos.
Duplicate handling, recovery and workspace use need definition. No present
run is authorized.

<!-- markdownlint-disable MD013 -->
```text
Suppose photos arrive in the separate-workspace tier and are confirmed to be a person already in the top tier. Since each person belongs in only one tier, what should happen? Automatically adding photos to the top-tier identity would be a change to that tier, unlike the read-only comparison we discussed.

add-existing
```
<!-- markdownlint-enable MD013 -->

## Nov 22 cross-tier incoming core eligibility - verbatim form answer

Coverage: confirmed incoming photos added to an existing top-tier person may
enter its core under normal core-quality rules -> LY17/LY18. The comparison
alone is read-only; no existing library mutation is authorized now.

<!-- markdownlint-disable MD013 -->
```text
When those confirmed incoming photos are added to the existing top-tier person, may they also become part of that person’s matching core if they pass its normal core-quality rules, or should the existing core remain unchanged?

normal
```
<!-- markdownlint-enable MD013 -->

## Nov 22 generated-image tier access - verbatim form answer

Coverage: allow cross-tier generated-image selection as workflow input ->
LY18/P19/P20/R44. Original Gallery-photo inputs remain tier-restricted;
generated ownership and any subject-domain limits need definition. A later
answer retains generated access after Gallery pullback.

<!-- markdownlint-disable MD013 -->
```text
Should the same tier restriction apply to ComfyUI-generated images when you select one as a workflow input: a workspace can use generated images from its own tier, but not another tier?

allow
```
<!-- markdownlint-enable MD013 -->

## Nov 22 workspace Gallery-photo boundary - verbatim form answer

Coverage: each workspace selects original Gallery photos only from its own
tier -> LY16/LY17/LY18 and workspace P19/P20. Later answers permit generated
images across tiers even after pullback; lineage and ownership remain open.

<!-- markdownlint-disable MD013 -->
```text
If a person belongs to the top tier, should you still be able to select one of their Gallery photos for a workflow in the separate-workspace tier? That would not create a second tier membership or automatically change any workflow.

restrict
```
<!-- markdownlint-enable MD013 -->

## Nov 22 cross-tier automatic photo matching - verbatim form answer

Coverage: normal automatic photo matching, including rival margin, suffices
to add a non-duplicate arrival to its existing top-tier person -> LY17/LY18.
The naming-only margin exception does not change this photo gate.

<!-- markdownlint-disable MD013 -->
```text
How should a new, non-duplicate photo be confirmed as belonging to an existing person in another tier? If it passes all normal automatic matching rules—including the required rival margin—should that be enough to add it, or do you want to confirm it yourself first?

normal
```
<!-- markdownlint-enable MD013 -->

## Nov 22 named singleton decision - verbatim form answer

Coverage: later-intake release and normal rescoring of a named single-photo
Potential -> N13/LY19 and the existing small-Potential settle contract;
preserve name/source history and normal protections. No run is authorized.

<!-- markdownlint-disable MD013 -->
```text
Another plan conflict: normal intake is planned to release one-photo Potentials for rescoring, but a named folder asserts the person's identity. If a named intake has only one usable photo, it cannot yet have an own-identity score. During later ordinary intake, should that named singleton be released for normal rescoring like other singletons, or remain anchored to its supplied name?

release
```
<!-- markdownlint-enable MD013 -->

## Nov 22 named intake current-name decision - verbatim form answer

Coverage: use the asserted original name as the person's current display name
in a clear correction -> N12/N13/LY19; preserve prior names, family history
and fixed cast character names. This is planned behavior, not an intake run.

<!-- markdownlint-disable MD013 -->
```text
Next naming conflict: suppose `Ela Model` clearly matches an existing person whose current display name is different—for example, a previously assigned family name. You’ve said to correct the original name and keep any Sister/Angel character name fixed. Should the person's different current display name also change to `Ela Model`?

replace
```
<!-- markdownlint-enable MD013 -->

## Nov 22 unreliable name-history collision - verbatim form answer

Coverage: automatic random-name fallback for a clear identity when unreliable
history cannot support a safe swap -> N12/N13/LY19, coordinating A3. This
does not authorize an identity merge, change to fixed character names or run.

<!-- markdownlint-disable MD013 -->
```text
Next conflict: an older plan says to hold a name collision if past name history is unreliable, but you asked for automatic correction and a random-name fallback when a swap is unsuitable. Suppose the person is clearly identified, but another identity already uses the asserted name and the history is too unreliable to choose a safe swap. Should we automatically give the other identity a new random name, or hold the collision for your review? No people would be merged, and fixed character names remain unchanged.

random
```
<!-- markdownlint-enable MD013 -->

## Nov 22 named refinement boundary - verbatim form answer

Coverage: stricter ordinary-refinement eligibility for explicitly named
non-core photos in established named identities -> N13/LY19, coordinating RA2d
and targeted refinement; the next answer selects the exact cutoff.

<!-- markdownlint-disable MD013 -->
```text
For ordinary refinement, you previously chose to reconsider non-core photos only when their score is below their identity category’s entry threshold. Should an established named identity use that same eligibility boundary, or should its explicitly named photos have a stricter boundary before they can be reconsidered? Normal destination and protection rules would still apply.

stricter
```
<!-- markdownlint-enable MD013 -->

## Nov 22 named refinement cutoff - verbatim form answer

Coverage: orange/red own score, strictly below 0.30, in addition to the
ordinary below-entry test for named non-core refinement -> N13/LY19/RA2d.
Unavailable scores are not low scores; no runtime or policy is changed here.

<!-- markdownlint-disable MD013 -->
```text
What extra cutoff should make an explicitly named non-core photo eligible for ordinary refinement? The existing below-category-entry test, normal protections and destination rules would still apply; this would not change the separate Sandbox rebase release.

orange-red
```
<!-- markdownlint-enable MD013 -->

## Nov 22 ambiguous named batch - verbatim form answer

Coverage: automatic best-supported group selection for a new incoherent named
batch -> N13/LY19; support, ties, remaining-photo routing and safeguards need
specification. No new intake or identity merge is authorized by this decision.

<!-- markdownlint-disable MD013 -->
```text
Next edge case: a new named folder contains several photos that don't match one another, and the system cannot reliably tell which person the supplied name belongs to. Should it hold the ambiguous batch for your review, or automatically choose a group to carry the supplied name? This is different from a single low-scoring outlier against an established, reliable core.

automatic
```
<!-- markdownlint-enable MD013 -->

## Nov 22 competing named groups - verbatim form answer

Coverage: prefer the larger coherent group over a smaller group with an exact
duplicate in the stated case -> N13/LY19; avoid duplicate votes and preserve
the evidence and submitted-name provenance.

<!-- markdownlint-disable MD013 -->
```text
To define “best-supported,” consider a named folder with two internally consistent groups: six distinct photos in one group, and two in another. One of the two is an exact duplicate of a photo already in an existing identity. Which group should automatically carry the supplied name? A duplicate proves photo continuity, but not which person you intended to name.

largest
```
<!-- markdownlint-enable MD013 -->

## Nov 22 remaining named-batch photos - verbatim form answer

Coverage: normal routing of photos outside the group carrying the asserted
name -> N13/LY19; preserve source/name provenance, safeguards and duplicate
dispositions. The selected named group remains separately identifiable.

<!-- markdownlint-disable MD013 -->
```text
In that same mixed named folder, the larger coherent group takes the supplied name. What should happen to the smaller group’s photos?

normal-routing
```
<!-- markdownlint-enable MD013 -->

## Nov 22 displaced original-name decision - verbatim form answer

Coverage: a displaced person's wrong original with unknown real original ->
N12/N13/LY19; use the fallback random name for original and display, retain
provenance and history, and preserve fixed character names.

<!-- markdownlint-disable MD013 -->
```text
For that random-name fallback: suppose the other identity incorrectly records `Ela Model` as its original name, and we don't know its real original name. What should its original-name field become? The old incorrect name would remain in history, and the fixed character name, if any, would stay unchanged.

random
```
<!-- markdownlint-enable MD013 -->
