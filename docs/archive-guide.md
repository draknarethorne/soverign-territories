# Archive guide

Start here to find history **by purpose**, not by guessing a date.
Current instructions are in the [documentation map](README.md), current work
in [Now / next / holding](plans/README.md#now-next-and-holding), and the
post-reboot handoff in the [recap index](recap/README.md).

## What each archive means

| Looking for | Location / index | Meaning |
| --- | --- | --- |
| Older project design, roadmap and documentation audits | [Project archive index](_archive/README.md) | Historical/superseded design and audit records, not current rules |
| Old art-library operation reports | [Art report archive](art/_archive/README.md) | Dated evidence; use current runbooks for commands |
| Finished or superseded execution plans | [Plan archive index](plans/_archive/README.md) | `done` and `dropped` are distinct; transferred tasks may still be open |
| Earlier daily checkpoints | [Recap chronological transfer ledger](recap/README.md#archived-recaps-chronological-ledger) | Superseded resume states; each entry identifies current context owners |
| Incorporated raw feedback | Local `feedback/_archive/`; [source-to-plan ledger](plans/README.md#oct-27-feedback-disposition-and-intake-restart) | Original notes filed after complete preservation/coverage; not a claim their tasks are done |

Feedback remains git-ignored; tracked plans preserve the full source wording.
The local feedback archive physically groups all 24 filed notes into seven
topic folders: `planning-and-recaps`, `intake-quality`, `identity-and-matching`,
`storage-and-configuration`, `gallery-and-actions`, `prompts-and-rendering`,
and `code-maintainability`. Its README gives counts and owning work.
Original filenames/bytes are retained; filing dates remain in tracked
preservation records. None of these folders is an unfinished inbox.

## Physical layout and ongoing filing

The folders now match their indexes:

| Archive | Physical groups |
| --- | --- |
| `docs/_archive` | `data-audits`, `documentation-housekeeping`, `mvp-and-roadmap`, `document-reorganization` |
| `docs/art/_archive` | `library-operations` |
| `docs/plans/_archive` | `completed`, `superseded-prompts`, `superseded-library` |
| `docs/recap/_archive` | `YYYY-MM` folders; currently `2026-10`, with the topic/reason/current-owner ledger in the recap index |
| Local `feedback/_archive` | Seven topic folders listed above; no loose notes or competing date-batch folder |

For every future filing: choose the appropriate physical group, preserve the
record, update the index/transfer ledger and incoming links, and verify any
generated readers in the same change. A new group needs an index entry, not
just a directory. Keep only the archive index itself at the archive root.
Tracked files use `git mv`; ignored feedback uses non-overwriting moves and
byte/hash verification. Historical prose and fenced raw source remain intact;
only link destinations may change to retain the same intended targets.

## Filing and retrieval rules

- Keep archives beside their domain. Do not merge art reports, execution plans
  and raw feedback into one date-only bucket.
- Use topic/status folders for domain history and month folders for inherently
  chronological recaps, with matching purpose/topic indexes. Dates support
  context; they do not replace topic or live ownership.
- Do not move historical files merely to make the tree look uniform. A move
  requires reviewed reference updates, preserved prose/source bytes and an
  explicit current owner for every unfinished request.
- Indexes explain **why archived**, **current replacement/owner**, and whether
  the record is evidence, superseded scope, or completed work. Archive does
  not mean trash, a retention deadline or permission to delete.
- Read historical content only for an explicitly requested historical question
  or a scoped preservation/link repair. Current work must not resurrect old
  commands, counts or priorities from it.

This pass physically organized 46 historical documentation records and 24
raw-feedback notes. It is not a fresh content audit or acceptance of every old
claim. Original filenames remain stable; feedback bytes and historical
documentation prose/fenced source are preserved, with link destinations
rebased for the new folders.
