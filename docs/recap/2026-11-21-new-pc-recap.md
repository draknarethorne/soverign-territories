# Nov 20-21: new-PC setup and SIMPLE rehearsal

This is the new machine's dated evidence, not a second execution queue.
The [planning agreement](../plans/README.md) and execution spine retain
current ownership. The user reported another machine's process was still
active at 08:01 Central on Nov 21; this machine cannot verify its state.

## Setup and synchronization

1. Set up Python 3.14.10, the processing virtual environment, Node,
   pre-commit, PSScriptAnalyzer and local face/intake model weights.
   Earlier full validation passed; at the time of writing, setup and
   documentation edits were local, not in this recap's original commit.
2. Developed project-local decision guidance and a bounded on-demand skill/
   agent simplification. At the time of writing, those changes were local;
   fresh-session discovery and actual token savings were not measured.
3. Pulled the other machine's branch changes through commit `4439368f2`,
   preserving local work and reconciling overlapping documentation. The
   original four staged guideline renames and backup stashes were preserved.
4. Configured this machine's ComfyUI roots on B: and deployed 252 existing
   Drakness workflow JSONs to each of the Drakness and Drakn Sisters
   workspaces. This deployed existing files; it did not regenerate workflows
   or render images.
5. Before committing, full validation exposed workflow tests inheriting
   those real root overrides rather than their throwaway paths. Isolated the
   test module's root environment, added a hostile-override regression, and
   reran all 80 workflow tests successfully with the machine overrides set.
   The test fixture workspace names did not exist in the real installs root.
   The full regression run then found an unchanged baseline test expecting
   an Angels core threshold of 0.30 while the checked-in policy is 0.38.
   It also failed in isolation. A follow-up corrected the test to check the
   configured policy threshold; runtime code and policy were not changed.
   The rerun of `bin\validate.cmd` exited 0, including 1,076 library tests;
   machine-root overrides were removed only from that test process. The
   earlier isolated mutation pass was 53/53.

## Clean Sandbox rehearsal

The copied run15 was preserved separately. The frozen Source manifest matched
the historical SHA-256 and all 11,048 files passed the frozen replay check.
The cleanup plan initially failed its expected hash; after the user recopied
it, its SHA-256 matched. The Sandbox-only cleanup passed preview/apply/check
for 1,795 exact copies and 180 replacements, followed by a reviewed four-copy
exact-only cleanup and a zero-candidate rescan. Displaced originals were
retained. The resulting 1,069 Various Gallery inputs and all 3,490 input
paths and SHA-256 values matched the run15 preview inventory.

The first fresh preview was stopped for the user's shutdown request after
161/3,285 preparation rows. Its log and interrupted state were preserved.
After restart, fresh-cache LEAN `simple-newpc-lean-20261120-02` completed
preview in **1h47m47s**, exit 0.

The user then authorized Sandbox apply after preview validation. The first
apply exited 1 after **56m10s**, before the publication transaction:
the direct-script launcher encountered a package-relative import error.
The failed log and staged publication files were preserved. A narrow local
import fix reproduced and resolved the error; 89 affected rebase/recap tests
and routine checks passed. The code fix was uncommitted when this recap was
written; check the shared revision to confirm whether it has been transferred.

Because the fix changed the implementation binding, new preview
`simple-newpc-lean-20261121-03` reused the origin-sealed preparation under
its recorded manifest hash. It completed in **6m28s**, exit 0, and its
assignments, moves, holds and dispositions matched the previous preview.
The validated Sandbox apply completed in **1h15m29s**, and check/repeat in
**30.9s/29.6s**, all exit 0.

The applied report conserves 3,490 sources to 3,490 distinct destinations.
It records 184 recoverable distinct-ID duplicate dispositions and one
recoverable zero-face junk disposition, with no cast Gallery departures,
unresolved duplicate IDs or stale snapshot diagnostics. The applied Review
snapshot matched 3,305 destinations; the other 185 are those dispositions.
An isolated local browser loaded representative Gallery, Overview, Review
and recap thumbnails, a current Nyxene native, Draknara intake detail and
native history. Human identity and crop acceptance remains open.

## Performance and limits

Run15 on the other machine recorded 4h39m preview and 4h33m36s apply. Those
are historical context, not a paired hardware comparison: code revision,
machine, cache state and other bindings differ.

Three sequential LEAN sidecar trials used the same 24 installed images and
passed their checks. Compared image hashes and outcomes matched:

| Workers | Wall time | Scope |
| --- | ---: | --- |
| 1 | 43.7s | 24-image sidecar preparation |
| 2 | 28.7s | Same installed inputs |
| 3 | 24.5s | Same installed inputs |

These are small, sequential trials on installed images, not whole-rebase
measurements. SIMPLE still explicitly uses one preparation worker; no default
or GPU setting was changed. Broader tuning and paired measurements remain
with the existing performance owners.

## Evidence and boundaries

- Run logs, timings and preserved failure evidence:
  `B:\Sovereign Territories Sandbox\_baseline-state\evidence\simple-clean-newpc-20261120-01`.
- Installed receipt and publication journal are under
  `Working\_reports\runs\normal-rebase-simple-newpc-lean-20261121-03`.
  The applied recap/audit and tuning reports remain under `Working\_reports`.
- The copied run15 and failed staging remain preserved; no reset, intake,
  Production mutation or promotion is implied by these results.
- No local rehearsal or tuning process remained at the final check. Do not
  infer that the other machine's separate process has completed.
- The [collaboration thread](../collab/2026-11-21-new-pc-rehearsal/README.md)
  asks the other agent for its actual status, code binding and transfer needs.
