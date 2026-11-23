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

### Experiments

1. **Blank slate:** no history and no bias. Which Prospects and Potentials
   form, and how do Angelica's original members distribute?
2. **Gate variations:** rerun blank with alternative formation and entry gates
   (for example green formation for Potentials, a higher cast-entry bar,
   single-photo on or off) and compare the resulting groupings.
3. **Hand-picked core:** the user places chosen Angelica photos in
   `Various/Angelica/gallery`. Everything else stays in `Various/gallery`.
   Check whether a clean core attracts the right photos and repels lookalikes.
4. **Second identity:** repeat for another cast identity (for example
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
- **IU5 Findings report:** patterns, anomalies against the main Sandbox,
  causes and proposed configuration or rule changes for user review before the
  next full rebase.

## Acceptance

- The universe manifest and `--check` re-verify every copied byte; Production
  and the main Sandbox are unchanged.
- Each run's GUI pages and recap load in a browser with thumbnails.
- The findings report links every claim to run evidence; recommendations are
  proposals until the user accepts them.

## Open decisions for the user

- The default expansion band (yellow) and hop depth, after seeing the IU2
  universe size.
- Which photos form the IU4 hand-picked core.
- Which experiment's configuration, if any, carries into the next full
  rebase.

<!-- markdownlint-disable MD013 -->

## Primary user source

### Angelica universe sandbox - verbatim feedback

Source: `feedback/angelica_sandbox_testing.md`, retained in place until
IU1–IU5 are reviewed.

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

### Plan file request - verbatim chat

```text
Part of this is a docs/plans file as well - that should be something in the feedback documentation - so that we record the full docs/plan for this and then we can execute that.  Hope that is part of your work as well.
```

<!-- markdownlint-enable MD013 -->
