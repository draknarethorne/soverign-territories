# Nov 22: identity-universe sandboxes (Angelica first)

**Status:** holding (executed through spine tasks
[IU1–IU5](2026-11-05-priority-reset.md#execution-spine); not another active queue)

**Owner:** RA2d analysis and rule decisions; RA2j tooling. Production and the
main Sandbox are read-only inputs. The user authorized overnight tooling and
experiments in a separate disposable universe sandbox. No Production or main
Sandbox mutation, no new intake from Production, and no commit or push of
private images.

## Problem

Angelica was never brought in as a named identity. Various photos were added
incrementally, grouped under the lower gates of the time, and that Prospect
was promoted to Angels/Angelica. Later Various photos landed wherever they
scored. The result is a contaminated "Angelica universe": genuine Angelica
photos are spread across other identities (for example Fia Hadley), and
lookalikes sit inside Angelica at 0.5–0.6.

The Nov 22 feedback rebase showed that releasing members and rescoring them
against a top-9 seed does not untangle this. Most released photos returned
to the Gallery or filled Angelica's and Drakniss's Review. The user reverted
that rule (`castAdmission.seedEnabled: false`); see the
[focused SIMPLE contract](2026-11-16-simple-review-and-tuning.md#nov-21-red-member-release-planning).
The face model scores facial structure similarity; it cannot separate
0.5–0.6 lookalikes reliably. Human selection or rejection is the reliable
signal there.

## Goal

Provide a repeatable, fast, bias-free way to study any named identity's
universe on a small subset. That makes it possible to try gates and seeding
strategies in minutes, compare results against the main Sandbox, and carry
proven changes back to the full rebase. Angelica is the first case study.

## Proposal

### Universe selection (generic for any identity)

1. **Seeds:** the named identity, plus user-listed related identities.
2. **Seed photos:** photos whose pre-rebase (post-intake) owner is a seed
   identity, plus photos currently placed in a seed identity's Gallery or
   Review in the latest main-Sandbox rebase. Photos are mapped by stable
   photo ID to their pre-rebase source rows.
3. **Expansion:** add identities whose centroid or any member scores at the
   configured band (default yellow, ≥0.30) or better against the seed
   centroid or members. A bounded second hop uses green only, unless
   configured otherwise. Unassigned Various photos at the band are included.
   Orange-band identities are listed as interesting but not included by
   default, because orange covers most of the library.
4. **Evidence:** every included identity and photo records its reason, hop and
   best score. The original bytes are verified by SHA-256 against the
   pre-rebase inventory before copying.

### Universe sandbox layout

- **Location:**
  `B:\Sovereign Territories Universes\<ID>\Sovereign Territories Sandbox\Working`.
  It is outside the main Sandbox, but the existing Sandbox-only tools accept
  it.
- **Contents:** pre-rebase originals; the sealed LEAN preparation, reused by
  content hash so intake does not rerun; the face cache and evidence; a
  universe manifest; and an HTML membership report with thumbnails grouped by
  original and current owner.
- **Reports:** the full SIMPLE GUI set (Gallery, Overview, Review, history),
  the rebase recap and the audit, the same as in the main Sandbox.
- **Modes:**
  - *blank:* all photos go to `Various/gallery` with no catalogue or history;
    every identity name is new.
  - *named:* the same, plus empty `Various/<Seed>/gallery` staging folders for
    the user's hand-picked core (protected named intake under the existing
    named-incoming contract).
  - *empty:* a brand-new sandbox with the valid layout, configuration and
    report roots, but no photos, catalogue, cache or history. The user drops
    originals into `Various/gallery`, or named folders, and the ordinary intake
    or SIMPLE rebase then prepares and processes them from scratch. Its first
    use is the user's own set of 345 originals, which includes Angelica photos.

### Experiments

1. **Blank slate:** no history and no bias. Which Prospects and Potentials
   form, and how do Angelica's original members distribute?
2. **Gate variations:** rerun blank with alternative formation and entry gates
   (for example green formation for Potentials, a higher cast-entry bar,
   single-photo on or off) and compare the resulting groupings.
3. **Hand-picked core:** the user places chosen Angelica photos in
   `Various/Angelica/gallery`. Everything else stays in `Various/gallery`.
   Check whether a clean core attracts the right photos and repels lookalikes.
4. **User-supplied original set:** in an *empty* universe sandbox, the user
   drops in their 345 originals; intake and rebase process them with no
   history. This gives a bias-free run on genuine source files alongside the
   automatic snapshot.
5. **Second identity:** repeat for another cast identity (for example
   Sisters/Nyxene) once the tool is proven.

### Systematic outputs

- A per-run comparison: universe photo → original owner → main-Sandbox owner
  → universe-run owner, with scores and thumbnails.
- Patterns and anomalies, such as smiles or expressions splitting one person,
  lookalike pairs at 0.5–0.6, and photos that move between runs. Each is
  compared with the main Sandbox and paired with suggested corrective rules.
- Before the next full rebase, the configuration changes the evidence
  supports. Each change remains the user's decision.

## Tasks

These are executed through spine tasks IU1–IU5 and listed here as the contract:

- **IU1 Universe builder:** `tools\art\likeness_library\universe_sandbox.py`
  and `bin\universe-sandbox.cmd`, with preview/apply/check, selection report,
  byte-verified copy, sealed-preparation reuse and help entry. Tests are
  required.
- **IU2 Blank-slate Angelica run:** build `angelica-20261122`, then run SIMPLE
  preview, apply and check. Publish the GUI reports and recap.
- **IU3 Gate variations:** at least two alternative gate sets on the same
  universe; compare the runs.
- **IU4 Hand-picked core:** prepare the named staging and a candidate sheet;
  the user selects; then run and compare.
- **IU6 Empty universe sandbox:** `--mode empty` creates a ready-to-intake
  sandbox (layout, configuration, report roots, no photos). The user supplies
  the 345-original set, and ordinary intake or rebase processes it from scratch.
- **IU5 Findings report:** patterns, anomalies against the main Sandbox,
  causes and proposed configuration or rule changes for user review before the
  next full rebase.

## Acceptance

- The universe manifest and `--check` re-verify every copied byte; Production
  and the main Sandbox are unchanged.
- Each run's GUI pages and recap load in a browser with thumbnails.
- The findings report links every claim to run evidence; recommendations are
  proposals until the user accepts them.

## Nov 22–23 results (IU1, IU2, IU6 done; IU3–IU5 open)

**IU1** `bin\universe-sandbox.cmd` (`universe_sandbox.py`) supports blank,
named and empty modes, `--source-folder`, a separate `--hop2-band`, a
membership report and `--check`. A copied sealed preparation can be reused in
another Sandbox Working at the same relative path; apply checks it against
the originally recorded path. 1,372 likeness tests and `bin\check.cmd` passed.

**IU2 automatic Angelica universe** (`angelica-20261122`): all 11 listed
names resolved. 67 identities (12 named plus 55 at hop 1) and 1,200 photos
were included, 105 near-misses listed and 35 exact copies excluded. The
blank SIMPLE run `universe-blank-01` reused the preparation (preview 65 s,
apply 28 min, mostly report publication) and formed **163 Potentials, no
Prospects**: 43 single-photo, 76 of 2–4 photos, 21 of 5–9, 11 of 10–19 and
12 of 20 or more. Angelica's 61 original members split across 28 Potentials
(largest share 14). No Angelica core formed.

**IU6 Most Wanted** (`most-wanted-20261122`): all 345 originals from
`B:\Most Wanted` were copied byte-verified (275 distinct; 69 duplicates
archived). The fresh LEAN run `most-wanted-blank-01` (preview 19 min, apply
8 min) formed 121 identities (119 Potentials, 2 Prospects; largest 10).
Angelica's 59 originals split across 35 Potentials. One photo was held out
because it is the Angelica workflow photo, which the rebase refuses to
rename; it is preserved under `Held-Out\` with a README.

**Comparison:** 273 of the 275 distinct Most Wanted photos exist in the
library. Their original owners were Various 117, Angelica 59, Draknoxa 19,
Jacinta Alden 13, and about 30 others in ones to sixes. The automatic
universe contains 199 of the 273. The 74 missing ones all score below yellow
against the Angelica seed (22 orange, 52 red); in the main Sandbox, 13 of
them sit in Draknoxa and 7 in Cleo Reyes. The automatic universe also adds
1,001 photos not in Most Wanted (Drakniss 322, Ione Brantley 160, Harlow
Chase 100, haniya 94, Ravaelle 79, ...), so yellow against any single seed
photo is far too broad. The small clusters are stable across both runs; for
example, Lena Lockwood's 6 all land together in the other run's Paige Pryce.

**Early findings for IU5:**

- With no history, the confirmed formation gates (Potential needs every
  member yellow, Prospect needs every member green) shatter one person into
  many small Potentials. Even groups of 20+ stayed Potentials because not
  every member reached green against the group. The model consistently finds
  the same small sub-clusters, such as expression, angle or lighting sets,
  but the all-members gate never joins them.
- Universe expansion needs a tighter rule, for example a green threshold
  against the seed centroid or at least N seed photos matching at yellow.
- Workflow-selected photos block blank runs; a sandbox-only exemption is a
  user decision.

## Nov 23 universe-testing feedback

The user's [universe-testing note](#universe-testing-feedback---verbatim) adds
decisions and tasks. Request coverage:

| Request | Disposition / owner |
| --- | --- |
| Workflow photo may be renamed or moved; then auto-select the identity's highest-scoring Gallery photo | **Decision recorded (user).** Supersedes the earlier "propose only, never change configuration" rule for this case. Implementation: IU7 |
| Lessons from automatic and manual universes inform grouping/scoring rules | IU5 findings, then IU10 |
| Most Wanted: clean up duplicates in `B:\Most Wanted`, the universe source and the universe Working, as **first priority** | IU8 |
| Most Wanted holds about 10–15 distinct identities (the roster lists 7–10) | Recorded as user knowledge for IU9 and IU10 evaluation |
| User builds a Most Wanted variation with hand-named "known for sure" folders as seed cores, the rest in `gallery`, and runs it under current rules | IU9 (user staging, then run) |
| Discuss new grouping rules: the earlier loose rules let rivals into Angelica, while the current strict rules fragment | IU10 (RA2d decision, one question at a time) |
| Angelica universe: tighten selection, for example traverse at yellow by group, then require a stricter per-image score against Angelica's top 9; other suggestions welcome; abandon if it cannot be made reliable | IU11 experiment |

Tasks (executed through spine tasks of the same IDs):

- **IU7 Workflow auto-replacement:** when a workflow-selected photo is
  renamed or moved by a rebase, update the workflow selection to the
  highest-scoring Gallery photo of that identity. Record it in the receipt
  and recap, keep it recoverable, and remove the blank-run refusal.
- **IU8 Most Wanted duplicate cleanup:** remove the exact byte duplicates
  (70 files, 275 distinct) from `B:\Most Wanted`, the universe
  `Universe-Source` and the universe Working. Moves must be recoverable,
  hash-verified and logged, never deleted. This is the first priority.
- **IU9 Named-core Most Wanted variation:** the user creates named folders;
  the tooling builds and runs a universe from them under the current rules,
  then compares it with `most-wanted-blank-01`.
- **IU10 Grouping-rule review:** from IU3, IU5 and IU9 evidence, propose rule
  changes that neither fragment one person nor absorb rivals; the user
  decides.
- **IU11 Tighter universe selection:** for example, group-level traversal
  at yellow plus a per-image score against the seed's top 9 at a stricter
  bar. Measure precision and recall against the Most Wanted set, or abandon
  if unreliable.

## Nov 23 IU8 cleanup and Most Wanted baseline

`B:\Most Wanted` now holds 275 distinct images. The 70 exact copies moved
recoverably to `B:\Most Wanted-duplicates\` with a hash-verified
`duplicate-cleanup-log.json`, keeping the oldest copy, or the
workflow-selected photo where present. Universe `most-wanted-20261123` was
rebuilt from it.

The first baseline preview stopped safely because the workflow-selected
Angelica photo cannot move. Inside the universe only, it was swapped for its
byte-identical duplicate, with the original kept in `Held-Out\` and a
README. Baseline `most-wanted-baseline-02` used the current rules and one
preparation worker: preview 15m42s, apply 7m00s, check passed. It formed
**121 identities (119 Potentials, 2 Prospects)** from 275 photos, with 6
left in Various and nothing in Review. Sizes were 45 singles, 42 pairs, 17
triples, 5 of 4, 8 of 5, 2 of 6, 1 of 7 and 1 of 10. The user expects 7?15
real people, so the current rules fragment heavily. This is the baseline for
IU9 and IU10.

## Open decisions for the user

- The default expansion band (yellow) and hop depth, after seeing the IU2
  universe size.
- Which photos form the IU4 hand-picked core.
- Which experiment's configuration, if any, carries into the next full
  rebase.

<!-- markdownlint-disable MD013 -->

## Primary user source

### Angelica universe sandbox - verbatim feedback

Source: `feedback/angelica_sandbox_testing.md` (filed to the local feedback archive on Nov 23 after coverage verification).

````text
It's sort of a mess right now and with the rules the way they are right now - moving things into another model, prospect or potential's gallery won't hold them there and I do want to see them.  I almost feel like that I need a separate Sandbox where I'd just focus on using Angelica and the related high-scoring photos to do some investigation and runs with a much smaller set of photos.  Because, there are some things I don't quite understand - like Fia Hadley photos aren't Angelica - that I know now and several that are in Anglica Review I would have expected to land with Fia - except that Fia has several with smiles that don't bring them together.  So, maybe what I actually need to work on is the work Beacon is laying out around the Various/[person name] processing and if I re-stage the photos with better hand-picked grouping,  instead of trying to release them and hope they land somewhere else, that I could drive that into a new core identity and it could then build better and attract more image?

I guess here's the people that I think are part of the Angelica universe problem to solve.

- Angelica
- Fia Hadley
- Cecily Radcliffe
- Jacinta Alden
- Delia Foster
- Petra Cole
- Delia Ames
- Delia Foster
- Francesca Rothwell
- Belen Rathbone
- Belen Thorne
- Lorelei Fletcher
- Elva Olander

and more I possibly missed.  I know there are a few other key images that are part of Angelica that I am missing and need to identify to properly resolve the Angelica universe problem.

Once I better understand this, it'll probably help with other identities as well and improve the overall accuracy of the system in grouping and identifying related images.

Basically - I am looking for ideas and strategies on how I could create a smaller sandbox of all the images that were originally part of my Angelica universe and then got split out later and some left behind and use that sandbox to better understand the relationships and improve the grouping and identification of related images.

If we can create this sandbox with all the images that are part of this Angelica universe, it would allow us to experiment and analyze the relationships between the images more effectively, and potentially improve the overall grouping and identification process.

Additionally, having a dedicated sandbox would make it easier to test different strategies for grouping and identifying related images without affecting the main dataset, providing a controlled environment for experimentation and refinement.

Ultimately, the goal is to improve the accuracy and reliability of the system in recognizing and grouping images that belong to the same identity, starting with the Angelica universe as a focused case study.

Can you give me ideas on how to handle that - we do have the original set of Angelica from a point in Production - but that was after some of the photos had split out and formed other identities already.  Some valid being separate and some not.  So what is in production is really a contaminated set of the Angelica universe.  Honestly, I didn't bring in Angelica on her own.  I incrementally brought in Various images that started to group and I just assumed it was all working well and then I promoted that Prospect up to Angelica - so it was formed with much lower bars at the time and hence why I didn't realize that some of the images weren't actually Angelica.  I then brought in more Various images and just let them land where they landed vs. forcing them into Angelica - but even if I had done that, I would have continued the contamination. 

So - does this make sense in where we are at, but where I want to get to?  Please offer me up a proposal for creating the smaller sandbox where we can focus on the Angelica universe and moving ahead.  I am open to all options - even just starting out a brand new sandbox with Various and throwing all the images that I think are part of the Angelica universe - not having history, basically brandnew and just focus on seeing what Prospects and Potentials are created if we don't keep anything at all.  Basically, it would be all new names and a fresh start for analyzing the Angelica universe.  Just so I can see how things work without any bias.  We could then alter gates and see how things change in each run - without any existing bias at all.

Another is we create a new Sandbox and I then force certain photos into Angelica/gallery and we use that as the core from my hand-selected ones.  We then process all the other images from her universe and see how that processes.  

What other ideas and what systematic system could be build so we could take any named identity (Angels/Angelica, Sisters/Nyxene, etc...) and then create a new sandbox and automatically pull the related images from the universe that score high enough to be of interests as well as images from other identities that score high enough from those.  So, being able to see the other identities that we need, plus identities related to those identities that might also be in the right scoring range.  It basically looks like any identities that an image scores Green, Yellow and even Orange against are interesting subjects for that Sandbox.

I feel like this is a recurring problem and I just see it with the way things play out with Angelica ... and hence the desire for an automated way to snap a sandbox in that manner, so that we can systematically analyze and refine the grouping and identification of related images for any given identity without the contamination and bias present in the main dataset.

Does this all make sense?  Give my your recommendation based on all this.  

Also, feel free to work on the recommendation while I am away.  I will return in the morning and we can review your proposal, results and any insights you have gathered from the sandbox experiments.  Additionally, if you identify any patterns or recurring issues during the sandbox testing, please include those in your report so we can address them systematically.

Finally, please provide a summary of the key findings and any actionable steps that can be taken to improve the overall accuracy and reliability of the system in grouping and identifying related images, both within the Angelica universe and for other identities in the future.

Lastly, I want all the GUI reports, recap, etc... that would execute in this smaller sandbox.  Basically, it's just a smaller sub-set of the Production sandbox so that things can run faster when we're making adjustments and such.  This will help us quickly iterate on different approaches and validate the effectiveness of our sandbox strategies without the overhead of the full dataset.
Additionally, please ensure that any insights or anomalies observed in this smaller sandbox are clearly documented and compared against the results from the main Production sandbox to understand the impact of the reduced dataset on the system's performance.
Furthermore, if any discrepancies or unexpected behaviors are identified, please provide a detailed analysis of the potential causes and suggest possible corrective actions to mitigate these issues in future sandbox experiments.
````

### Empty-sandbox option - verbatim chat

```text
I actually have one place I could use to start a brand new universe from and it only has 345 images in it - not all are Angelica, so it might actually prove useful for me to just have a brand new sandbox and drop in those 345 images into Various/gallery and let it process them.  That's one additional option we can do - but I also like the automatic snap-back.  But being able to generate certain sandboxes - either completely empty and ready for intake or based on the automation we discussed.   Both could serve a purpose in moving us ahead to get this done.  I like having the universe tool as well as the option I just realized I could do since I have that group of originals all together - along with a few others.
```

### Universe-testing feedback - verbatim

Source: `feedback/universe_testing_feedback.md` (filed to the local feedback archive after this incorporation).

````text
# Universe Testing Feedback

I have serveral items to address accross the universe testing.

## General

- I think that we should allow a workflow photo to be renamed, moved and if that happens we'd just auto-select the higher scoring photo in the gallery for the identity that the workflow is assigned to.

- I also feel like the lessons we're learning in both the automatic and manual processing of these universes should inform how we adjust our grouping and scoring rules moving forward.  

## Most Wanted Universe

### 1. Clean Up

Can we clean-up the duplicates in the B:\Most Wanted, universe source directory and universe working.  I want to do this as first priority and get that done so I can move onto the next couple steps. 

### 2. Distinct Identities in Most Wanted Universe

In this universe there are probably 10-15 distinct identities that we need to account for (at most).  The actual source for those only indicates 7-10, but I think that his roster isn't up to date and may be missing some entries.  

I'm going to work on another variation of the B:\Most Wanted where I will hand create a few of the "I know these for sure" named directories (giving them my own names) and then leave other photos in the B:\Most Wanted\gallery for processing - and then we see how the system behaves.

These will be seed cores for the processing and then I'll see how things work with the current rules in that universe before moving onto the next step.

### 3. New Group Rule Changes

I'd like to discuss how we change the grouping rules - I think this run with only the 300 images proves that we have issues in how we form identities and we need to re-adjust our approach to grouping.  Originally it was much looser, but then I saw that it was doing the opposite and bringing in photos that weren't the same person - which lead to Angelica having the rivals in her gallery instead of their own.

## Angelica Universe

### 1. Tightening the Scoring

How can we tighten the scoring so that we only pull more accurate or suspected results that match angelica.  Could we change to still traverse using the yellow scoring on groups, but then apply stricter comparison on an image by image to Angelica's top-9 to see how they score against each image?  Then choose based on a stricter score there?

Or what can you suggest we can try to improve the accuracy of the Angelica universe source creation?

If we can't do this reliably to trim down the number, then maybe we abandon this - but I feel like it's also a good exercise in understanding how photos relate to each other.
````

### Plan file request - verbatim chat

```text
Part of this is a docs/plans file as well - that should be something in the feedback documentation - so that we record the full docs/plan for this and then we can execute that.  Hope that is part of your work as well.
```

<!-- markdownlint-enable MD013 -->
