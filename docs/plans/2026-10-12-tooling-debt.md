# 2026-10-12: tooling debt from the day

**Status:** active (what the day showed about our tools; none of it blocks the photo work)

Found while building and running the artists reset, the crop and the routine, written up in [../recap/2026-10-12-1700-recap.md](../recap/2026-10-12-1700-recap.md). Each box is small and independent.

## Steps

- [ ] **P2 ai** D1 `likeness status`: for every root and every artist, what is left loose and why (no usable face, a second person, an animal, bars over her head, held for clean-up), plus the pool, the review folders and `_junk`. The question "why are there still photos in this gallery" took a diagnostic script today; it should be one command.
- [ ] **P2 ai** D2 Split `tools/art/likeness.py` (2,500 lines, 30 subcommands, one file) into modules: the face reader and cache, the plans (sort, group, artists, crop), the commands. Behaviour unchanged, the 38 tests are the net.
- [ ] **P2 ai** D3 One place for the thresholds. `assign`, `margin`, `cluster`, `minCluster`, `singles`, `rematch`, `rematchCast`, `castMerge`, `odd`, `alike`, `multiFace`, and the per-command options (`--join`, `--cohesion`, `--single-join`, `--keep`) are scattered. List them in one table in `likeness.md`, add `likeness settings` to print the values in effect, and calibrate the new ones (`castMerge`, `--join`, `--cohesion`) on the library as `calibrate` does for `assign`.
- [ ] **P2 ai** D4 `bin\day-close.cmd`: the day's hygiene as one read-only check (tmp empty, every plan has a status and tagged boxes, `todo.md` is current, lint, tests, validators), so it is a command and not a memory.
- [ ] **P3 ai** D5 A person detector for `crop` instead of the face box widened to the sides (wings, a wide stance and a low head are guesses today), and the other reel layouts (a paused video with a play button, a caption at the bottom). See also A4 in the artists plan.
- [ ] **P3 ai** D6 Write every file the tools change whole and swap it in (a temporary name, then a rename), and log each change as it is made, as `crop` now does: the scaled copies, headshots, frames, `workspaces.json` writes, the move log. A killed process must never leave half a file or an unlogged change.
- [ ] **P3 ai** D7 One line-ending rule in `.gitattributes`: the repo mixes CRLF and LF files, which turns a one-line edit into a whole-file diff and git warns on every command.
- [ ] **P3 either** D8 Background processes were suspended by Windows after about a minute (every thread "Suspended"; resuming them with `NtResumeProcess` finished the job). Find out why (power or efficiency mode, a security tool) and, if it recurs, have `library.cmd` say so instead of hanging.
