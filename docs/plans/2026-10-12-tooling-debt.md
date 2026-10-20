# 2026-10-12: tooling debt from the day

**Status:** active (what the day showed about our tools; none of it blocks the photo work)

Found while building and running the artists reset, the crop and the routine, written up in [../recap/2026-10-12-1700-recap.md](../recap/2026-10-12-1700-recap.md). Each box is small and independent.

## Steps

- [ ] **P2 ai** D1 `likeness status`: for every root and every artist, what is left loose and why (no usable face, a second person, an animal, bars over her head, held for clean-up), plus the pool, the review folders and `_junk`. The question "why are there still photos in this gallery" took a diagnostic script today; it should be one command.
- [ ] **P2 ai** D2 Split `tools/art/likeness.py` (2,500 lines, 30 subcommands, one file) into modules: the face reader and cache, the plans (sort, group, artists, crop), the commands. Behaviour unchanged, the 38 tests are the net.
- [ ] **P2 ai** D3 One place for the thresholds. `assign`, `margin`, `cluster`, `minCluster`, `singles`, `rematch`, `rematchCast`, `castMerge`, `odd`, `alike`, `multiFace`, and the per-command options (`--join`, `--cohesion`, `--single-join`, `--keep`) are scattered. List them in one table in `likeness.md`, add `likeness settings` to print the values in effect, and calibrate the new ones (`castMerge`, `--join`, `--cohesion`) on the library as `calibrate` does for `assign`.
- [ ] **P2 ai** D4 `bin\day-close.cmd`: the day's hygiene as one read-only check (tmp empty, every plan has a status and tagged boxes, `todo.md` is current, lint, tests, validators), so it is a command and not a memory.
- [ ] **P3 ai** D5 A person detector for `crop` instead of the face box widened to the sides (wings, a wide stance and a low head are guesses today), and the other reel layouts (a paused video with a play button, a caption at the bottom). See also A4 in the artists plan.
- [ ] **P3 ai** D6 Write every file the tools change whole and swap it in (a temporary name, then a rename), and log each change as it is made, as `crop` now does: scaled copies, headshots, `workspaces.json` writes and the move log. A killed process must never leave half a file or an unlogged change.
- [ ] **P3 ai** D7 One line-ending rule in `.gitattributes`: the repo mixes CRLF and LF files, which turns a one-line edit into a whole-file diff and git warns on every command.
- [ ] **P3 either** D8 Background processes were suspended by Windows after about a minute (every thread "Suspended"; resuming them with `NtResumeProcess` finished the job). Find out why (power or efficiency mode, a security tool) and, if it recurs, have `library.cmd` say so instead of hanging.
- [ ] **P2 either** D9 Calibrate a report-only prospect-readiness ranking from face quality, usable-photo quantity and distinct framing; validate a pose-diversity signal and compare rankings against human review before using the score to recommend replacements.
- [ ] **P2 you** D10 Review the organized library gallery and Angel-to-Prospect rankings; confirm whether the candidate ordering and preview-only promotion command are useful for choosing Angel replacements. After reviewing the refreshed results, revisit the Oct 12 request to promote Dara Ives to Nyxene and return the current Nyxene to Prospects; use a fresh preview and confirm before applying if the updated evidence changes the choice.
- [ ] **P3 either** D11 Design a safe, archive-first way to deactivate a Prospect or Artist folder identified as a false face match from the gallery. Keep the HTML static unless a trusted local action flow is approved; never delete the source files.

**Oct 14 update:** The people-gallery HTML now shows each prospect's closest sister-face matches and observable readiness evidence. The full library routine previews and archives Prospect folders that have no gallery or review originals; folders with review photos and `Various` are preserved. D9 remains open: pose diversity is not inferred from framing, and no combined readiness score is used yet.

**Oct 14 report update:** Reports are grouped under `_reports\library`, `runs`, `comparisons` and `analysis`. Each paired Angel now shows its Sister, canonical hair wording and three eligible Prospect alternatives; a separate report ranks all eligible candidates per Angel. The gallery keeps promotion preview-only and does not invoke Explorer or mutate files. D10 is the next review.

**Oct 19 gallery navigation update:** The People Gallery now starts with Sisters, links each Sister to her current Angel pairing and that
Angel's top three eligible Prospect alternatives, and links those candidates to their Prospect cards. Angel cards link to their paired
Sister and ranked Prospect alternatives; Prospect cards link to their best-fitting Angel. Angels are ordered by best eligible pairing fit;
Prospects remain ordered by descending gallery photo count, with name as the tie-breaker. Pairing rankings remain visible on Sister and
Angel cards and in the full candidate report. The currently paired Angel is shown explicitly on the Sister card; Prospect alternatives
remain candidates, not automatic assignments. Review the refreshed report under D10 before choosing or promoting anyone.
