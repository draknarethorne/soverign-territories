# Library, studio and Gallery planning handoff

- **From:** Beacon (`agent-69b7d56fd547`), old machine.
- **To:** Harbor (`agent-d01e8fdb3329`), new machine.
- **Created:** 2026-11-23 19:45 UTC; based on shared revision `e89985762`.
- **Delivery:** tracked continuation; publication and Harbor's acknowledgment
  are separate. Do not treat this document as proof of receipt.

## Assignment and starting state

The user directs Harbor to lead all likeness, Gallery, studio, named-intake
and image-processing work and continue its planning. Beacon will not run or
implement these areas on the old machine unless Harbor directly requests
specific help. Beacon separately plans ComfyUI workflow generation and
integration; see [WF1](../../plans/2026-11-05-priority-reset.md#execution-spine).
The user's exact machine-split and workflow direction is preserved in the
[workflow plan](../../plans/2026-10-22-manual-prompts-to-art-library.md#nov-23-machine-split-and-workflow-direction---verbatim-chat).

Use the [execution spine](../../plans/2026-11-05-priority-reset.md#execution-spine)
and its Queue focus as the sole schedule. Existing task IDs and holding
gates remain; this handoff assigns coordination, not completion or blanket
activation of backlog. The new-machine universe/rebase results are reported
in tracked plans, not independently re-read on the old machine. Verify the
actual new-machine process, run, revision and receipts before acting; this
handoff does not authorize a reset or another run. At 19:44 UTC no local
old-machine Python/ComfyUI/library process was observed; the new-machine
process state is unknown here.

## Open work and decisions

1. **Likeness and 275-photo analysis:** continue RA2d/RA2j and the selected
   IU3/IU4/IU5/IU7/IU10/IU11/IU12 work from the
   [universe results and feedback](../../plans/2026-11-22-identity-universe-sandbox.md#nov-23-universe-testing-feedback).
   Separate human identity decisions, candidate evidence, tests and installed
   acceptance; do not treat a checked run as identity approval. The reported
   275-photo blank baseline yielded 121 identities; the 13 named-core run
   yielded 66. Human grouping review is still open.
2. **Named intake before studio migration:** IU12 covers native named-folder
   intake; [N12/N13](../../plans/2026-10-22-identity-family-naming.md#oct-30-named-and-unnamed-various-acceptance-contract)
   and [LY19](../../plans/2026-11-02-library-layout.md#deferred-owners-and-request-coverage)
   retain its full path, identity, provenance, duplicate, name-correction,
   protection and recovery contract. Direct named-folder photos and
   `gallery`/`review` children are selected targets, not already accepted
   native behavior: the reported seeded trial used a separate seed step.
   Preserve supplied-name intent, person/photo IDs, fixed
   character slots, history, locks and undo; do not treat a score or duplicate
   alone as permission to merge people.
3. **Named-intake residuals:** define/test coherent-group eligibility,
   size-versus-consistency and insufficient evidence; initial outlier and
   genuine-protection evidence; safe swap evidence with unreliable legacy
   names; and competing matches, ties and fixed-slot cases. The user already
   selected automatic best-supported naming, a deterministic shown tie-break,
   and a random-name fallback when a clear identity has no safe swap. Do not
   re-ask settled decisions or invent numerical thresholds. Bring consequential
   unresolved choices to the user as needed.
4. **Studio layout and movement:** continue LY16-LY21 from the
   [studio proposal and open questions](../../plans/2026-11-02-library-layout.md#questions-for-the-user).
   Named intake precedes migration; female, male, then creature groups use
   the selected Apex/Forge/Lab tiers and per-tier Intake. Preserve the selected
   cross-tier, Artist/creature isolation, user-approved whole-person movement,
   workspace/source and recovery rules. Open items include actual migration
   paths, category/matching rules, identity references, workspace boundaries
   and acceptance. Confirm any remaining user decisions before implementing.
5. **Gallery and generated results:** coordinate
   [LY18 and the generated-image lifecycle](../../plans/2026-11-02-library-layout.md#later-gallery-and-per-workflow-image-lifecycle),
   [Gallery UX](../../plans/2026-10-22-gallery-review-layout.md),
   [intake](../../plans/2026-10-23-image-intake-preparation.md) and
   [rendering](../../plans/2026-10-25-reference-rendering.md#oct-30-generated-image-round-trip-coverage).
   Generated outputs do not become likeness-core evidence; preserve source
   lineage, per-workflow selections and flagged ambiguous/multi-person
   cases. Retired outputs are selected as history-only, not workflow inputs;
   reconcile that decision with the cast-stop interaction without losing
   outputs. Harbor owns the library/Gallery side; Beacon owns workflow
   generation/ComfyUI integration. Agree a single interface and owner before
   changing shared workflow selections, configuration or result consumers.
6. **Recovery and storage:** keep current source photos, run evidence and
   recovery dependencies under the
   [storage contract](../../plans/2026-10-28-storage-operations-and-retention.md).
   The separate old-machine backup comparison remains open in its existing
   [discussion](../../collab/2026-11-21-new-pc-rehearsal/messages/20261123T183500Z-agent-69b7d56fd547-01.md);
   a reported copy is not yet independent hash/recovery proof. The old-PC
   run08 also remains protected: its journal and outer receipt disagree on
   recovery status and its stage-source checks remain dependencies.

## Boundaries and evidence transfer

- The user retains rule, identity, migration and human-acceptance decisions.
  Existing Sandbox, Production, workspace, cleanup and publishing gates
  remain in force. Do not change a policy or start a writer merely because a
  planning item was handed over.
- Required planning contracts are tracked at the paths linked above and must
  be read from the published handoff revision or its successor. No private
  photo, run receipt, cache or payload is being transferred with this handoff.
  If a specific local artifact becomes necessary, arrange an approved
  private transfer with exact bytes, SHA-256 and recipient verification.
- The previous documentation validation passed at `e89985762`; it is not
  proof of the new machine's installed state. The handoff's own validation
  and publication must be reported separately.
- Please acknowledge the handoff in its
  [collaboration discussion](../../collab/2026-11-21-new-pc-rehearsal/messages/20261123T194548Z-agent-69b7d56fd547-02.md),
  state the revision received and any missing decision, and coordinate before
  altering a shared library-to-workflow interface.

## Required tracked contract snapshots

These are SHA-256 hashes of the Git blob bytes in the handoff commit, not
platform-dependent working-tree line endings. Harbor receives them through
Git and should verify the received revision or explicitly reconcile later
changes; they do not represent private local run artifacts.

| Contract | Git blob SHA-256 |
| --- | --- |
| [Execution spine](../../plans/2026-11-05-priority-reset.md) | `7cd4eb6ac69919d0be9edd65b25226ec197999d98ab19e0ed26d3d52ebf09a43` |
| [Workflow plan](../../plans/2026-10-22-manual-prompts-to-art-library.md) | `64afaa60567908655c66ba5a643daf97ff8c466f34084ea88d4f66d04f9b5a3c` |
| [Naming plan](../../plans/2026-10-22-identity-family-naming.md) | `f795388087d90551d0598b0c1ecaa7c573b91ab7665436dc8847c0aface978c5` |
| [Studio/layout plan](../../plans/2026-11-02-library-layout.md) | `d0b8f16fb470814506c8c3af9ed687e5ccc9e3aaf0c46277589085726e76fea1` |
| [Universe plan](../../plans/2026-11-22-identity-universe-sandbox.md) | `f3d2f2a2416cb03603fb3233a764771111128729e72b32927fd73eb57dce606a` |
| [Gallery plan](../../plans/2026-10-22-gallery-review-layout.md) | `1c4fc061f4642a7e9508742e58fd03718ed6eea0d2f5bedcae5214663e51c1d7` |
| [Intake plan](../../plans/2026-10-23-image-intake-preparation.md) | `72f98fba464d5e9f3a163f2366c531f5e4526bdf624655f232454854812bd738` |
| [Rendering plan](../../plans/2026-10-25-reference-rendering.md) | `cf4fc882ad8b683c801d8fd420756275ac88648f63058a6ff89d7498f0280eb9` |
| [Storage plan](../../plans/2026-10-28-storage-operations-and-retention.md) | `54857d2338b58b4c279ae69ce5b5b3f0c31f5a9e08c6d65da94b493fda7f1b7b` |
