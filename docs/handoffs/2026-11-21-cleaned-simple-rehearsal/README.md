# Cleaned SIMPLE rehearsal: cleanup-plan evidence

**Status:** historical evidence, not an instruction to reset or rerun.
**Sender:** Beacon, old-PC session. **Recipient:** Harbor or a future
authorized replay agent. **Recorded:** 2026-11-21 17:53 UTC.
**Evidence baseline:** branch `work/sandbox-rebase-acceptance`,
revision `5f88c3453ee6`; this handoff is a subsequent documentation change.

Both cleaned-SIMPLE rehearsals are installed; their current evidence and
remaining acceptance gates are in the [pinned recap](../../recap/README.md),
[execution spine](../../plans/2026-11-05-priority-reset.md#execution-spine)
and [collaboration discussion](../../collab/2026-11-21-new-pc-rehearsal/README.md).
The cleaned raw starting population is not the processed Working tree.
An already-cleaned, independently verified raw baseline does not need the
historical cleanup repeated. No new reset, cleanup, apply or Production write
is authorized by this record. The original cleanups and subsequent runs are
historical; check live process state and current task authority before any
future work. Human identity and crop acceptance remain open.

| Artifact | Purpose and binding | Size | SHA-256 | Status |
| --- | --- | ---: | --- | --- |
| `payload/simple-run14-various-cleanup.json` | Reviewed portable cleanup plan for the original frozen Source; optional historical evidence, not needed to review the completed installs. | 805,854 bytes | `2a1a34699bf025560c3c4af79a9f0a46d8896df1458aaedf4685deaaa6e85914` | Beacon's local payload copy verified. Harbor previously received and verified this hash through a private transfer; that does not prove a copy exists at this new payload path. |

The [original cleanup record](../../plans/2026-11-16-simple-review-and-tuning.md#nov-19-post-run13-tuning)
and [historical machine handoff](../../recap/2026-11-11-1141-recap.md#new-pc-simple-rehearsal)
describe its scope and baseline conditions. The frozen Source hash in that
handoff is not an assertion about a recipient's present Working tree.

The payload is Git-ignored and is not delivered by this README or its
commit. If a future authorized replay actually requires it, first verify
the recipient's baseline and authority, privately transfer the exact bytes
through an agreed channel, and independently verify size and SHA-256
before use. Keep the original and do not substitute a similarly named file.
