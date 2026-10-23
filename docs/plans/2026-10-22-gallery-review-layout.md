# 2026-10-22: gallery and Review information layout

**Status:** active (full feedback captured; implementation paused for plan reconciliation)

## Review and questions: 2026-10-22 16:26 -05:00

Retained with complete acceptance feedback. Before L6, ask one question:
what should relocking a protected identity do to already-staged actions?
No answer was assumed. Before ranking eligibility changes in L10, review
evidence with the engine/action owners; labels alone cannot change policy.
L11 now owns the transferred Oct 21 5.6 card-use guidance. These are planned
controls/layout, not a claim that the real-library GUI has passed user review.

## Scope and ownership

This plan owns presentation and information grouping across the gallery and
Review pages. Identity actions and their transaction semantics belong to the
[manual-action plan](2026-10-22-review-actions.md); automatic decisions follow
the [processing contract](../art/likeness-processing-contract.md).
It does not duplicate matching, calibration, family naming or production gates.
Keep closely related layout work together; split a genuinely independent
topic into its own plan with explicit links rather than expanding either
engine plan indefinitely.

## Agreed direction

- A person header is a readable summary, not one blended block of controls
  and diagnostic text.
- Separate the reference/workflow image, identity details/statistics, and
  manual actions into clearly labelled panels.
- Keep identity name, fixed cast slot and category distinct. Do not imply
  a person's recorded name is the character slot.
- Preserve overview/Review ordering and useful information consistently.
- Identity-level manual actions must be available across identity categories;
  protection adds a deliberate safeguard, not a blanket manual-action ban.
  Each action still validates ownership, conflicts, references and recovery.
  This does not silently change the separate photo-protection contract.
- Layout work is recorded now, not silently included in rename delivery.

## Protected identity actions: proposed interaction

Prefer an explicit per-identity checkbox in the Actions panel:
**Enable manual actions for this protected identity**. Protected identities
start with manual controls disabled and an explanation of how to unlock them.
Checking it enables manual controls without clearing protection, authorizing
automation or repeatedly asking the same protection-confirmation question.
The unlock is temporary UI state, scoped to that identity, and resets on reload.
Unprotected identities need no protection unlock. Action-specific validation,
preview, backup and undo remain mandatory; a protection unlock does not bypass
unsupported references or make unfinished actions executable.

This is a proposed replacement for the current protected-rename confirmation,
not a description of shipped behavior. Before implementation, settle how
relocking handles already-staged actions. Never silently discard staged work
or conceal pending decisions behind disabled controls.

## Work

- [ ] **P1 ai** L1 Inventory the current overview and Review person-header
  content against raw acceptance feedback. Map image, details, tags,
  diagnostics and actions into distinct panels without dropping existing
  information or duplicating its source.
- [ ] **P2 ai** L2 Implement a responsive reference-photo panel, identity
  details panel and actions panel. Align name/tags/stat order with the
  overview; stack cleanly on narrow screens and keep controls accessible.
- [ ] **P2 ai** L3 Audit photo-detail grouping and category/name repetition,
  clickable tags, history links, separators and visual hierarchy across both
  pages. Preserve scores and the distinction between evidence and actions.
- [ ] **P2 ai** L4 Validate both sort modes, filters, primary references,
  stage/cancel/export and protected-action safeguards after the layout
  changes, including narrow/wide synthetic browser checks.
- [ ] **P1 you** L5 Review the regenerated actual sandbox pages after L2-L4;
  confirm the image/details/actions separation is usable.
- [ ] **P2 either** L6 Settle relocking/staged-action behavior, then implement
  and test the per-identity manual-action unlock in L2's Actions panel.
  Cover disabled defaults, independent identities, reload reset, visible
  pending actions and unchanged automatic protection. Audit identity-level
  controls and backend handlers for blanket category/protection refusals;
  resolve these in the linked action-owner plans, not by bypassing validation.
- [ ] **P3 ai** L7 Review shared theme, colors, spacing, typography,
  placeholder/header treatment and optional sticky navigation across both
  pages. Style all tags consistently; give clickable history/review-count
  tags a clear hover target and proposed count-color ranges for user review.
- [ ] **P2 ai** L8 Add a presentation-only Mixed/Split grouping choice
  separate from Location and Order. Split Gallery/Review into labelled
  groups, or retain mixed score ordering with unmistakable Review styling.
  Preserve filters, staging and both existing sort modes.
- [ ] **P3 ai** L9 Make move selection category-first then identity while
  retaining stable destination IDs, validation and current stage/export behavior.
- [ ] **P2 either** L10 Audit ranking labels and explanations with the engine
  owner: who is compared to whom, adjusted fit versus identity similarity,
  Models/Potentials coverage and workflow-occupied eligibility driven by
  configuration. Do not change pairing or target eligibility as a cosmetic
  rename. Include concise Angel labels/order and requested visual separators.
- [ ] **P2 ai** L11 Show descriptive card-use guidance by category: Potentials
  can be browsed for common/uncommon, Prospects for broader use, and Models
  are not the user's common/uncommon choice. This is not automatic card
  assignment or a gameplay rarity rule. Verified destination for Oct 21 5.6;
  no separate engine implementation owns this presentation task.

## Raw feedback (verbatim)

Source: `feedback/feedback_on_acceptance_testing.md`, full snapshot, Oct 22.
This is the primary verbatim copy for a note spanning several workstreams.
The [coverage audit](../audits/2026-10-22-plan-feedback-audit.md) maps each
request to its active owner or clearly proposed successor. Sources stay intact.
Copied words and indentation are preserved; trailing line whitespace is
normalized only in the documentation copy for repository formatting checks.


<!-- markdownlint-disable MD013 -->
```text
I have been using the GUI while you have been finishing and I have a large amount of initial feedback.  Not sure if we can tackle all these items or what needs to be done - but some are cosmetic and other address functional gaps.  I added a priority to them all, but I feel like we need to come up with a plan on addressing these items ... and as I continue to work there will be more.  We don't need to use a formal github issue and we can just document these items somewhere in the docs/plans and eventually archive the document when it's done.

Here's a few items I am curious about and what is going on in looking at the latest gallery GUI results.  This feedback was done on the GUI that was deployed for testing at 10/22/2026 1:00 am - so does not account for any work that was completed during you latest coding and testing cycle.  So we can simply document these items as fixed in the new plan document to address usability feedback.  I noticed you were working on the retirement aspects while doing the work - so that's just one case where I can use this as a not to re-test any items already completed.

# Feedback on Acceptance Testing

## Gallery Theme

Priority: Low
The overall gallery theme could be more visually cohesive.  Consider reviewing the color scheme, spacing, and typography to ensure a consistent and pleasant user experience throughout the gallery interface.

At some point I could get a banner for the gallery to make it more visually appealing and to reinforce the overall theme.  For now we can just use any standard placeholder image or simple design element to fill that space.  Or even just a solid color block that matches the gallery theme would work temporarily.

Basically, just trying to look at how we can improve the overall visual cohesion and user experience of the gallery interface and make it look like a professional page.  That might also mean leaving the header area present as we scroll through other sections below.  I think that might apply to both pages (and any future pages we need to add).

## CLI Triggering

Priority: Medium
I am wondering if it's actually possible to support triggering the CLI in a shell or to at least figure out what the actual command is to run when staging actions.  I'm also curious what happens if I stage many actions at once and how the system handles that scenario.  Especially if the actions are across many identities.  I know we are deferring making them directly actionable - but it seems more like an "Apply Actions" would be better than "Download Actions" which just stages the .json.  If we could stage it and run it - even if it takes a long time to run.  That might be useful to test and see whether it's better to just stick with the download and run batches in my own shell or whether we can do it more interactively.  This is probably more an ideation, thought and planning item than an immediate fix item.

I just find myself wanting to use items like Rename Identity to take immediate action vs. other actions where I do want to stage a bunch and Apply them in a batch - but I also would like for that to be more immediate action after I get a batch ready for processing.

If we have some simple things we could do so I can compare and contrast how it works that would be great - but I don't want to go down a rabbit hole on this until it's really a problem.  We have more immediate usability and visual cohesion items to address first.

# Gallery GUI

## Review Photos

Priority: Low
"X in review" should be a tag and showing a color based on how many are there.  It should follow the "x photos" tag.  We should also color "x photos" based on how many photos are present.  We can just make up a range for now, and use the green, yellow, orange, red level and be consistent.

We should make that tag clickable and take you to the Review Gallery with the preselected drop downs to see the review for that person.

## History Link

Priority: Low
Feels like the placement and color of the history link could be improved. It might be better to have it more prominent or in a consistent location across the interface.  Not sure if it should be front, but also removing the underscore from the clickable portion and just making it look like the entire thing is a clickable box instead of the standard hyperlink might be useful.

That formatting would apply to all tags that become clickable.  Just hover over them to see it's clickable item.

## Tags

Priority: Medium
Protected identity should have a background color to represent it's a tag.  Really ALL tags need a background color that is aligned to what the tag is about.

## Current Angel

Priority: Low
I think it should move up to be after Person: xxxxx in the layout.  We could also change it from "Current Angel: Angels: Nyxene" to just "Angel: Nyxene" to make it more concise and clear.

## Category / Name

Priority: Medium
We should review all places where we display "Category/Name" as a single field and determing if it's important to show the separation or not.  Sometimes it may be fine to keep them together, but other times it might be clearer to separate them visually.  Or just show the Name field only if all we're saying is name.  If we want Category: xxxxx and Name: xxxx on two lines that may be fine.  But I think many places we could just reference the Name only.

This item may need an audit and figure out what makes sense in each spot we see the combined Category/Name field used.

Sometimes it also shows up as Category: Name and the context of the Category is already clear - like in the following where Prospects: is repeated for each identity.

Top Prospect alternatives:
1. Prospects: Tove North ▶ 0.31 Fit -0.028 · Like 0.032 · Variety +0.06 · 63 photos
2. Prospects: Arden West ▼ 0.24 Fit 0.037 · Like 0.037 · Variety +0.00 · 7 photos
3. Prospects: Ruby Eden ▼ 0.21 Fit 0.047 · Like 0.067 · Variety +0.02 · 11 photos

This also makes me wonder if we shouldn't just be showing the Closest other lower tier matches instead of just Prospects - since we have Models and actually Potentials.  I would want to ensure that we cover all non-Prospect categories as well to give a complete picture of the available matches.  Basically, we want to show the closest other identities that do now have a workflow associated with them - since that identity is already in use.  In the future if we add Demons that get workflow, we'd want that configuration to drive it.  I'm sure we have something in the config to drive that already.

## Visual Separator

Priority: Low
I think we'd want a separator between Workflow Photo and Closest by Category line.  Similar to the one for Top Prospect alternatives.

## Full Rankings

Priority: Medium
We need to revisit the Angel-Prospect ranking and better understand what that is providing and ensure it's named properly because we now have Models category as well.  It may still be needed, but I want to revisit it's logic and what it's doing.  We'll need to better explain the purpose at the top and who is being compared to what.  It's not clear when I read it what I can glean from this because the names are confusing.

## Various Photos

Priority: High
I see photos in the Gallery Review section that are categorized under Various, but I don't see anything on the Gallery page about Various.  Probably need to understand why photos are in Various in first place as that should be empty after a run.  At a minimum each photo would be a Potential if no match - otherwise, it would be in junk if totally unusable.

This makes me think there's a gap in the entire process since photos are being left behind.

## Workflow Photo

Priority: Medium
I wonder if on the 3x3 grid if we couldn't alway ensure that the chosen workflow photo would show up.  If it's not part of top 9 photos, we could show it as the 9th photo in the grid.  But we'd want to ensure that it's border was dashed instead of solid.  We could also change "(not shown)" to "(shown last)" or something like that as one more visual indicator on the page that the 9th photo is not actually in the top 9.  The color of the border (likely showing different than green, based on many of my selections) will help with that as well - plus we call out the score of the workflow photo as well.

I also think the existing border around the workflow photo should be thicker than it is.  It's colored to match the existing score, but still a bit faint for some.  It's pretty close to being right thickness, so just maybe a bit thicker.

# Gallery Review GUI

## Identity Overview Section

If you can visually inspect the section you'll see that the section isn't very user friendly and doesn't have all the content that is on the Gallery page about the identity.  I think we'd want it more like the following (this is not formatting, just concept info):
    - Name
    - Tags
    - Photo (workflow selected with score)

    - To the right of the picture we have another box with all the same stats as in the gallery - following the same layout and order.

So it's two boxes side by side - the photo on the left and the stats on the right.

That identity overview is like a summary card for the identity, providing a quick glance at the key information and stats without having to navigate to the Gallery page.  Use your best judgement on formatting and layout to make it clear and easy to read.

## Image Details

We need to revisit the Image Details section and align it more closely with how we organize the image information in the Gallery page, ensuring consistency in the display of photo IDs, identity IDs, core similarity, core size, face size, and closest other matches.

Here's currently what I see and think it could use work.

Draknara
Photo ID: 7518021302486860967 · Identity ID: person_2224e4265e975dee9965132af6a01d6a
SistersReview photoReview
Core similarity: 0.44
Core size: 97 photos provisional · no trusted anchors
Face: 166 px / 1
Closest other: Models: Brielle Carter 0.36

We could show the Closest Other 3 (or maybe 5) matches instead of just one, to give a better sense of how this image compares to other identities.

This is a case where Category information could be useful to display alongside the identity, especially when showing closest other matches, to provide more context and clarity.

## Various Photos

Priority: High
I see some photos in Various after the run completed. Are these expected, or should they have been categorized differently?  Can you explain what is happening there?

Many should have matched existing identities, but for some reason they ended up in Various.

Photo ID: 7518027271200184433 · Identity ID: not catalogued
VariousReview photoHold
Core similarity: not scored
Core size: 0 photos no usable core
Face: 372 px / 1
Closest other: Prospects: Uma Merritt 0.53

## Image Text

Priority: Low
I see that Identity ID: is showing up in some places as "not catalogued" in the Image Text section, even for photos that should have an associated identity. Or is this because it's photos are in Various, or is there a bug in how the identity is being displayed?

I also noticed that it's showing up on same line as Photo ID and wrapping, we probably need a newline for that.

Photo ID: 7518027271200184433 · Identity ID: not catalogued

# Staged Actions

## Identity Actions

Priority: Medium-High
We need to start to work on the staged actions for Identity level so I can do some of the following:
    - Rename Identity
    - Protect Identity
    - Retire Identity
    - Reject Identity
    - Merge Identity (specify target identity to merge into)
    - what else is missing that we have CLI options for at identity?

Some of these are high priority and others are not.

## Review photos

I am wondering if we should have a separator in the box of images for the review photos to be in their own section within the same box of images if we are showing "all" images and not just Gallery or Review specific.  It's really just an easy way for me to view the gallery and review together and know which ones need review vs. which ones are alway accepted into the gallery.  If we mix them within the gallery and review photos together that makes it harder to see them.  Although maybe I do want to see that view as well if we can do something to highlight review vs. accepted.  Maybe all review images need a different border around them if we show them together in mixed as then they would position in order of other images with scores and make it easier for me to see if they are alike other images.  So - I guess I want to see it both ways as long as it's really easy for me to understand either in separate groups of gallery and review or mixed all together.
That should be some sort of option that we can pick apporpriately.
Maybe it's how we call out the sorting and grouping since it's really just a sub-sort for mixed or separated.
The Location defines which files and we have another option for Mixed or Split to define the group and the Order defines within that how to order them.

## Retire Photos

Priority: High
If I wanted to retire individual photos, I don't see a staged action selection to do that.  Some photos in Review need to be retired as part of the process as they aren't really usable and that's one thing we need to support.
    - Retire individual photos for an identity
    - Retire an entire identity

## Approve Photo

Priority: High
If I approve a photo from Review to the Gallery, does that protect that photo and how do I determine if I want it to be part of the core or not?  Is that based entirely on similarity score?  I guess, maybe that's the intended behavior, but I need confirmation on how core membership is determined upon approval.

This brings up an interesting thought, maybe we do need a threshold for automatically determining which photos are part of the core vs. part of the gallery, but not core identity.  That way, approval could automatically place photos into the correct category based on similarity score, reducing manual intervention.  We'd just need to define and configure that threshold appropriately and tune it by running some rebases after making changes to existing Sisters and Angels prior to a rebase.

This would also probably help the longer term growth and healing so I don't have to exclude low scoring photos manually, as the system could automatically categorize them appropriately based on the defined threshold.  I can always override it and manually adjust whether or not it's part of the core for any pictures in the gallery.  Doing that on some angels would probably also help how things are working.

## Protect Photos

Priority: High
If I protect a photo that is in Review, what happens?  Does that actually accept it into the identity it belongs to, or does it simply prevent it from being removed or rejected?  I need clarity on the behavior of protecting photos in the Review stage.
    - Protect individual photos for an identity

## Reject Photos

Priority: High
If I reject a review photo, what prevents it from returning to the identity on the next run?  I need a clear staged action to reject photos and ensure they are not reconsidered for the same identity.  We probably need to save that in meta-data about a photo which identity it was rejected from.  As I run each run

## Moving Photos

Priority: Low
Could we optimize the selecting for Moving photos to be a two stage drop-down where you first pick the category and then the identity.  It's not a huge deal

```
<!-- markdownlint-enable MD013 -->

Source: chat, Oct 22, 2026; current clarification (verbatim).

<!-- markdownlint-disable MD013 -->
```text
I should be able to update a protected sisters, angel or any identity name - I want to rename a few sisters identity for instance Drakinsa - Sweet Beauty is actuall Amelia Morgan.  Somehow it was mis-named a while ago and I want to try to correct that and verify in the sandbox that renaming works.  There are a few others as well I can test with to see how it works in general.  I also had some feedback in general about the header section and making separate boxes for the image, details and now the actions.  Basically making that section better.  I'm sure you saw that in my feedback.  So I am just curious where everything is at right now.  We really need to address formatting of various areas and separate different types of information, functionality and such into their own sections so it's not all one blended big blob of data.  We don't need to take immediate action, but want to ensure we have those things ironed out and into a plan somewhere.  AND if the plans are overly complex we'd need to break them down into smaller and more managable plans to cover topics.  But if they are inter-related topics they can stay in one plan.  I have some feedback on that as well.  But first, I just want to make sure I can rename a sister properly, even if she's protected.  A rename is still ok.  The protection should prevent "automatic" actions from happening - but not things I want to do manually.  We could always introduce a warning "Draknisa is protected - are you sure you want to xxxxx?"
```
<!-- markdownlint-enable MD013 -->

The recorded-name correction is shipped as described in the
[manual-action checkpoint](2026-10-22-review-actions.md#delivered-checkpoint).
This does not implement every protected manual action; L1-L5 cover presentation.

Source: chat, Oct 22, 2026; broader manual-action clarification (verbatim).

<!-- markdownlint-disable MD013 -->
```text
Basically any identity level manual action should be allowed for all identities.  We just want to gate the ones for protected a little more to ensure I understand it is protected.  One other option would be to have a selection of somekind to enable the actions for protected.  So if they were in a section for actions - I'd see them disabled and have to select something to enable them.  That would prevent always using a pop-up - are you sure.
```
<!-- markdownlint-enable MD013 -->
