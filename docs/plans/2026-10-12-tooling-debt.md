# 2026-10-12: tooling debt from the day

**Status:** active (what the day showed about our tools; none of it blocks the photo work)

## Oct 25: Python processing runtime

The launchers already run Python 3.14.3. No global interpreter replacement or
ComfyUI environment change is needed to use the installed modern image stack.
D14 records repeatable dependency setup and expanded CI, not an unmeasured
performance claim. Python 3.12 compatibility remains; new 3.12/3.13 CI jobs
must pass before claiming local-equivalent validation on those interpreters.
Canonical setup lives in the
[photo-library runtime guide](../art/original-photos.md#python-runtime-and-dependencies).

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

- [x] **P2 ai** D14 Audit the actual Python/image stack; recommend regular 64-bit
  3.14, declare tested direct core/CPU-intake requirements and extend Windows CI
  beyond 3.12 without dropping the compatibility baseline. Validate the existing
  3.14 runtime and native CPU operators; do not upgrade ComfyUI or invent speedups.
- [ ] **P2 ai** D1 `likeness status`: for every root and every artist, what is left loose and why (no usable face, a second person, an animal, bars over her head, held for clean-up), plus the pool, the review folders and `_junk`. The question "why are there still photos in this gallery" took a diagnostic script today; it should be one command.
- [x] **P2 ai** D2 Transferred, not implemented by this checkbox: behavior-preserving modularization belongs to the [structure plan](2026-10-20-art-tools-structure.md), including former self-healing H2. Keep existing tests as the behavior contract.
- [x] **P2 ai** D3 Transferred: one effective settings inventory and action-specific calibration belong to [engine E3/E6](2026-10-22-likeness-engine-acceptance.md). Do not change production thresholds without measured results and a documented decision.
- [ ] **P2 ai** D4 `bin\day-close.cmd`: the day's hygiene as one read-only check (feedback coverage, plan status/index consistency, tagged tasks, explicit transfer owners, current queue, lint, tests and validators). Flag competing owners for review; never auto-archive a plan, clear notes or require an empty feedback/tmp directory.
- [x] **P3 ai** D5 Transferred, not a new legacy-crop implementation: v16 now
  has person-mask framing. Remaining limb/overlay acceptance and cutover belong
  to intake I27/I29/I12 and upkeep U7. Do not add a second person detector to
  the legacy crop route being retired.
- [ ] **P3 ai** D6 Write every file the tools change whole and swap it in (a temporary name, then a rename), and log each change as it is made, as `crop` now does: scaled copies, headshots, `workspaces.json` writes and the move log. A killed process must never leave half a file or an unlogged change.
- [ ] **P3 ai** D7 One line-ending rule in `.gitattributes`: the repo mixes CRLF and LF files, which turns a one-line edit into a whole-file diff and git warns on every command.
- [ ] **P3 either** D8 Background processes were suspended by Windows after about a minute (every thread "Suspended"; resuming them with `NtResumeProcess` finished the job). Find out why (power or efficiency mode, a security tool) and, if it recurs, have `library.cmd` say so instead of hanging.
- [ ] **P2 either** D9 Calibrate a report-only prospect-readiness ranking from face quality, usable-photo quantity and distinct framing; validate a pose-diversity signal and compare rankings against human review before using the score to recommend replacements.
- [ ] **P2 you** D10 Review the refreshed gallery and Angel-to-Prospect rankings; confirm candidate ordering, fit-score explanation and preview-only promotion command are useful.
  The four current Angel choices were made manually: Aria Muse → Gavrielle, Ruby Eden → Camaris, Amethyst Montgomery → Ravaelle, and Sabine Vale → Nyxene. Do not revisit the superseded Dara Ives suggestion or infer that photo count establishes identity.
- [ ] **P3 either** D11 Design a safe, archive-first way to deactivate an entire Prospect or Artist folder identified as a false face match. Keep the HTML static unless a trusted local action flow is approved; never delete source files.
- [x] **P2 either** D12 Transferred to the [manual-action owner](2026-10-22-review-actions.md): staged Review/Reject-to-Various, versioned manifest, validated CLI, backup, history and undo cover individual-photo reprocessing. Retain recoverability and actual-user scenario acceptance.
- [ ] **P2 ai** D13 Continue the non-archive documentation review outside
  `docs/art`, using current-guide/proposal/evidence/superseded classifications.
  The complete art-directory slice is D15 below, not an unfinished reread.
  Preserve unique context and incoming references before any further archival;
  a repository-wide inventory is not proof each other document was read.
- [x] **P2 ai** D15 Read every active `docs/art` document in full before the
  review-first recap; reconcile current commands/authority, classify all 21,
  combine enduring reorganisation rationale into curation and archive only
  the two superseded reports. Preserve proposal/rationale/evidence references,
  raw feedback, explicit sandbox/production limits and outstanding plan work.

## Oct 25: full art-document reconciliation

The audit covered all 21 starting documents (5,677 lines), excluding every
existing archive. Full contiguous reads, with truncated gaps filled, were
divided between the two operational guides, six likeness contracts/evidence
documents and thirteen prompt/workflow documents. Searches were used afterward
for implementation/link verification, not as a substitute for reading.

| Starting document under `docs/art` | Disposition and retained home |
| --- | --- |
| `original-photos.md` | Update current runbook: flow chooser, v16 selection/downloads, retained storage, recovery and paused incremental path; explicitly bound old v5-v13 report descriptions as history |
| `likeness.md` | Update command/gallery guide: prepared stop/resume, enabled draft families, core/protection distinction, exact retained lineage, diagnostics and legacy reset boundaries |
| `likeness-curation-contract.md` | Keep foundations; combine enduring reorganisation preferences, cache/membership rationale, Artist isolation, history and recoverability here |
| `likeness-processing-contract.md` | Update target contract; distinguish delivered sandbox flow/current draft from remaining acceptance and historical experiments |
| `likeness-sandbox-trial.md` | Keep dated reproducibility/diagnostic evidence; clarify chronology and that the new prepared rebase has not run |
| `library-reconciliation-context.md` | Keep dated evidence and independent pairing rationale; remove misleading current-state claims |
| `likeness-reorg-2026-10-09.md` | Archive superseded report after folding enduring rationale into curation; complete dated outcomes/raw notes remain preserved |
| `likeness-reorg-2026-10-10.md` | Archive superseded Oct 10/11 report; enduring boundaries live in curation, all dated evidence stays preserved |
| `tutorial-art.md` | Update active JSON/prompt tutorial and supported launcher/master references; proposed manual migration remains gated |
| `tutorial-video.md` | Keep active video tutorial; no unsupported new rendering/acceptance claim |
| `prompt-pattern.md` | Update wording guidance; distinguish historical examples from current data/tool ownership |
| `output-qa-checklist.md` | Update active human QA with hero-specific identity/appearance guidance |
| `prime-flows.md` | Keep current Prime/input reference and retired-frame distinction; no silent `0_Edit` migration |
| `minimax-h3-video-templates.md` | Keep focused MiniMax template analysis/reference, not a new execution plan |
| `prompt-migration-context.md` | Keep scoped render/rationale evidence; active migration plan owns unfinished changes |
| `dual-input-thoughts.md` | Keep historical two-input rationale, not approved current behavior |
| `comfyui-art-pipeline.md` | Update and label historical design context; current workflow masters/launchers own execution |
| `template-analysis-findings.md` | Update and retain explicitly dated analysis; unique examples/observations are not superseded merely by age |
| `comfyui-automation-proposal.md` | Update proposal boundaries/commands; API queueing and automatic image delivery remain unimplemented |
| `art-packs-and-comfy-node-proposal.md` | Keep independent unimplemented pack/custom-node proposal, not a user runbook |
| `thorne-art-studio-proposal.md` | Keep independent unimplemented Studio proposal; no implied GUI execution backend |

Result: 19 documents remain active or explicitly labelled proposal/evidence;
two superseded reports move to the nearest archive. No unique user notes are
discarded. Current references point to curation/current guides, not the archive.
The broad pipeline and template analyses stay available because they retain
independent rationale; archiving them would not simplify ownership safely yet.

The operational guides now explicitly distinguish the prepared installer/
maintained-derivative cleanup guard from direct legacy `originals` callers.
That incomplete cutover is already intake I12/upkeep U7, not an undocumented
new feature. Production remains draft-policy blocked; no new processing ran.

The requested daily recap is written only after this reconciliation. Its first
sections prioritize user verification and key remaining owning-plan work;
deliveries, earlier test evidence and reflection follow. Remaining non-art
documentation work stays in D13 rather than falsely closing the whole audit.

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

## Raw chat: Python runtime (Oct 25)

```text
We can upgrade python if that's a good thing to do to use newer libraries and functionality in the processing to optimize our work.  Just another thing you can do and let me know if that's done and update the requirements to use a newer version.
```

## Raw chat: full art-doc audit before the recap (Oct 25)

Coverage: D15's full-read/disposition ledger, current guide/index/plan updates,
then the new review-first daily recap and validation/publication. D13 retains
the separate remaining non-art documentation scope. No source feedback is removed.

```text
We've done a lot lately - can you create a daily recap following the instructions and at the top focus on all the things I need to verify and what remains from the plans that's a key item for this work.  Then you can document all that's been done.  I still see a lot of docs in docs/art that may not all be up to date and accurate any more.  Do that before the recap - read each one line-by-line instaead of scanning/searching and determine what to combine, what to archive and what to update.  Thanks again. Don't stop until we've at a solid and clean-state with all docs and coding.  Then write the recap in the manner I described.
```
