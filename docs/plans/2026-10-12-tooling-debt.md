# 2026-10-12: tooling debt from the day

**Status:** active (what the day showed about our tools; none of it blocks the photo work)

## Review and questions: 2026-10-22 16:26 -05:00

Retained independent diagnostics, hygiene, atomic writes, line endings,
suspended-process investigation and readiness/quality evidence.
Ask D10 ranking acceptance from actual current pages; don't reapply old cast
choices or assume photo count measures pose diversity. D11 owns recoverable
false-identity deactivation/archive design, distinct from person retirement
returning photos to Various in manual actions A2.
Structure owns package moves; engine E3/E6 owns settings/calibration; manual
actions own individual-photo handling. D2/D3/D12 are transfers, not old work
to reimplement. Historical counts and line counts below are dated evidence.

Found while building and running the artists reset, the crop and the routine, written up in [../recap/2026-10-12-1722-recap.md](../recap/2026-10-12-1722-recap.md). Each box is small and independent.

## Steps

- [ ] **P2 ai** D1 `likeness status`: for every root and every artist, what is left loose and why (no usable face, a second person, an animal, bars over her head, held for clean-up), plus the pool, the review folders and `_junk`. The question "why are there still photos in this gallery" took a diagnostic script today; it should be one command.
- [x] **P2 ai** D2 Transferred, not implemented by this checkbox: behavior-preserving modularization belongs to the [structure plan](2026-10-20-art-tools-structure.md), including former self-healing H2. Keep existing tests as the behavior contract.
- [x] **P2 ai** D3 Transferred: one effective settings inventory and action-specific calibration belong to [engine E3/E6](2026-10-22-likeness-engine-acceptance.md). Do not change production thresholds without measured results and a documented decision.
- [ ] **P2 ai** D4 `bin\day-close.cmd`: the day's hygiene as one read-only check (feedback coverage, plan status/index consistency, tagged tasks, explicit transfer owners, current queue, lint, tests and validators). Flag competing owners for review; never auto-archive a plan, clear notes or require an empty feedback/tmp directory.
- [ ] **P3 ai** D5 A person detector for `crop` instead of the face box widened to the sides (wings, a wide stance and a low head are guesses today), and the other reel layouts (a paused video with a play button, a caption at the bottom). See also A4 in the artists plan.
- [ ] **P3 ai** D6 Write every file the tools change whole and swap it in (a temporary name, then a rename), and log each change as it is made, as `crop` now does: scaled copies, headshots, `workspaces.json` writes and the move log. A killed process must never leave half a file or an unlogged change.
- [ ] **P3 ai** D7 One line-ending rule in `.gitattributes`: the repo mixes CRLF and LF files, which turns a one-line edit into a whole-file diff and git warns on every command.
- [ ] **P3 either** D8 Background processes were suspended by Windows after about a minute (every thread "Suspended"; resuming them with `NtResumeProcess` finished the job). Find out why (power or efficiency mode, a security tool) and, if it recurs, have `library.cmd` say so instead of hanging.
- [ ] **P2 either** D9 Calibrate a report-only prospect-readiness ranking from face quality, usable-photo quantity and distinct framing; validate a pose-diversity signal and compare rankings against human review before using the score to recommend replacements.
- [ ] **P2 you** D10 Review the refreshed gallery and Angel-to-Prospect rankings; confirm candidate ordering, fit-score explanation and preview-only promotion command are useful.
  The four current Angel choices were made manually: Aria Muse → Gavrielle, Ruby Eden → Camaris, Amethyst Montgomery → Ravaelle, and Sabine Vale → Nyxene. Do not revisit the superseded Dara Ives suggestion or infer that photo count establishes identity.
- [ ] **P3 either** D11 Design a safe, archive-first way to deactivate an entire Prospect or Artist folder identified as a false face match. Keep the HTML static unless a trusted local action flow is approved; never delete source files.
- [x] **P2 either** D12 Transferred to the [manual-action owner](2026-10-22-review-actions.md): staged Review/Reject-to-Various, versioned manifest, validated CLI, backup, history and undo cover individual-photo reprocessing. Retain recoverability and actual-user scenario acceptance.

**Oct 20 evidence check:** The saved Oct 12 gallery requests for up to nine photos in a three-column grid, clickable photos and folder links, descending Prospect photo-count order, short identity context, and an explanation of fit scores are implemented in `people_gallery.py`. Sisters and Angels now sort alphabetically, while Prospects and Potentials sort by photo count. The current tests and generated report cover that presentation. The remaining gallery review is D10; image-level exclusion is D12.

`tools/art/likeness.py` was 3,153 lines at that checkpoint. Shared modules have since been extracted; broader structure work remains open. The historical inspection did not find the proposed status/day-close/person-detector features; re-inventory before implementing them. Its `.gitattributes` observation was CRLF for `.cmd`/`.bat`, not a repository-wide policy.

**Oct 14 update:** The people-gallery HTML now shows each prospect's closest sister-face matches and observable readiness evidence. The full library routine previews and archives Prospect folders that have no gallery or review originals; folders with review photos and `Various` are preserved. D9 remains open: pose diversity is not inferred from framing, and no combined readiness score is used yet.

**Oct 14 report update:** Reports are grouped under `_reports\library`, `runs`, `comparisons` and `analysis`. Each paired Angel now shows its Sister, canonical hair wording and three eligible Prospect alternatives; a separate report ranks all eligible candidates per Angel. The gallery keeps promotion preview-only and does not invoke Explorer or mutate files. D10 is the next review.

**Oct 19 gallery navigation update:** The People Gallery now starts with Sisters, links each Sister to her current Angel pairing and that
Angel's top three eligible Prospect alternatives, and links those candidates to their Prospect cards. Angel cards link to their paired
Sister and ranked Prospect alternatives; Prospect cards link to their best-fitting Angel. Angels are ordered by best eligible pairing fit;
Prospects remain ordered by descending gallery photo count, with name as the tie-breaker. Pairing rankings remain visible on Sister and
Angel cards and in the full candidate report. The currently paired Angel is shown explicitly on the Sister card; Prospect alternatives
remain candidates, not automatic assignments. Review the refreshed report under D10 before choosing or promoting anyone.

## Raw note: continued progress (Oct 12)

The Oct 12 note is preserved below as written. Its gallery layout and sorting requests are now implemented; the Dara Ives pairing request was later superseded by the user's explicit Sabine Vale → Nyxene choice. The photo-level exclusion request remains in D12.

I would give the cropping a A+ on the Angels, Sisters and Prospects, but for Artists - where some had angel wings and devil wings it cropped those quite a bit.  So, for real people in normal outfits, the cropping did get rid of text and much of the extras.
I noticed that some photos that have the "text" about the reels on the hairline that it also left text on the bottom and right side for things in the shots - many of the screenshots might have overlay items that ideally are cropped and if I need to manually clean-up the top lines with AI or something I can do that - if there were another library to blend those away that would also be awesome.  So mostly the cropping is awesome, but still has a few things to improve on.

Also in the people_gallery, we should show up to 9 photos in a 3x3 grid instead of just 1 photo.  That way I can see for the ones that have more than 1 or 2 photos a larger collection and also turn the "x photo" line into a hyperlink into the directory where I can view them all.
Ideally we'd also sort that by the number of photos descending so that the ones with many photos are at the top and the ones with just one photo at the bottom.
Not that a single photo can't make a great piece of art - but it gives me less choices for our Angels.  I also don't know what "best guess 0.xx" means specifically - but having additional summary about the person is fine - just not more than a few words summarized - if that can't be done, then change the name to a hyper link to the z_xxxx.txt file to open and read more about the person.

I want to promote Dara Ives to Nyxene and bring the person who is currently Nyxene back to prospects.  There should be .cmd files or .py files that handle this for us so we keep track of the history in the z_xxx.txt file of the people involved.  More deep analysis of the tools and various .py files needed.

Additionally - in the people_gallery, is there a way I could have the ability to push a button or link on a Prospect or Artist and have it simply just remove that image?  As long as it's backed up in the archive, but I no longer want it active in the list.
Most likely is someone from a odd/side angle or in a rainstorm or some other environment and I know it's actually another person, but the facial recognition doesn't detect it - so I'd want to de-activate them from the directory and all images in that folder for ther person.

I noticed that males and dragons were given female names - we haven't actually gotten to a point where our directory structure needs to handle the males, females, animals, dragons and assortment for the likeness, cropping and such.  That's one key item to address after we get to those cards.  For now, it's fine - I'll just ignore it until we get there.
