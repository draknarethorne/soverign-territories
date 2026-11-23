# Agent handoffs

Use **handoff** for the noun and **hand off** for the verb. A handoff is a
specific continuation for another session, agent or machine. It is not a
new plan, a grant of authority or proof that the recipient has received it.
The [planning agreement](../plans/README.md), current user instructions and
canonical task owners remain authoritative.

## Layout

Create one uniquely named folder per handoff, for example
`docs/handoffs/2026-11-21-example/`:

```text
docs/handoffs/<handoff-id>/
  README.md             reviewed, shareable continuation and artifact ledger
  payload/              private required files; Git ignores this directory
```

Name folders for the topic and time, adding a unique suffix on collision;
never overwrite an existing handoff. The handoff README can be tracked only
after review for sensitive content. Keep payload files under `payload/`,
not next to the tracked README. The repository ignore rule protects that
specific directory at this depth; verify it with `git check-ignore` before
copying anything and use `git ls-files` to ensure nothing under the payload
is already tracked. Never force-add a private payload. An ignore rule is not
encryption, access control, a backup or a transfer mechanism.

Do not use a session folder or disposable `tmp/` as the sole copy of a
required handoff artifact. Copy only the exact required files from verified
sources; do not move originals, copy whole libraries or treat recovery
receipts as disposable. Use a user-approved private channel or durable shared
location when another machine needs the payload. This repository does not
provide one automatically: an ignored local folder is still local and Git
does not carry its contents. Without an approved available channel, mark
transfer pending and stop only work that depends on those files.

## Write the continuation

Use the [milestone-handoff procedure](../../.github/skills/milestone-handoff/SKILL.md)
to verify current authority, actual process/worktree state and the active
plan. Keep the handoff compact and link to canonical contracts and evidence
instead of duplicating plans. A communication-only handoff does not change
task ownership or Queue focus. Record:

- Sender, intended recipient, creation time, branch/revision and status;
  distinguish a local draft, published document and recipient acknowledgment.
- Current work, exact starting state and next entry gate; identify what is
  observed, historical, pending or unknown. Do not prescribe cleanup/reset
  when the recipient already has the desired baseline.
- Allowed and prohibited roots/actions, user-only decisions, live run IDs,
  processes, receipts, failed stages and recovery boundaries. State when
  no writer was observed, with its observation time, rather than assuming it.
- Test/validation evidence, open exceptions and canonical task owners. A
  successful run does not imply human identity, crop or Production approval.
- Each required artifact's safe alias, purpose, exact byte length and SHA-256,
  source/baseline binding, intended recipient and expected relative payload
  path. Mark optional or historical artifacts separately from prerequisites.
  Avoid publishing sensitive paths, filenames, photo inventories or private
  data; if metadata is sensitive, keep its detailed ledger private too and
  publish only a safe pointer/status.
- Whether each artifact was locally verified, transferred and independently
  received/verified. Record the approved channel or a safe reference to it
  without exposing credentials. A hash or Git commit is not delivery.

Keep related questions and answers together under the
[collaboration protocol](../collab/README.md), linking the handoff rather
than creating a competing conversation. Never assume the other agent has
read a pushed revision.

## Copy and verify

1. Determine exactly which files the recipient needs for the actual starting
   state. Check the original bytes and SHA-256 against the reviewed authority;
   a stale or mismatched source is a blocker, not a plan to reconstruct.
2. Resolve the specific source and intended `payload/` paths. Refuse linked
   paths, traversal, unexpected existing destinations and unsafe sources.
   Use non-overwriting copies; preserve originals and all competing copies.
   Verify each copied file's size and SHA-256 against the reviewed value.
3. Transfer the verified bytes by the agreed private channel. The receiver
   independently checks the exact file, size and SHA-256 at its intended
   destination before use, reports received/missing/mismatch, and checks
   that its actual baseline and permissions match the handoff. A prior
   verified copy does not establish that a new destination exists.
4. On mismatch, missing file, unavailable channel or changed baseline,
   preserve evidence, report the discrepancy and stop dependent work.
   Do not substitute similarly named files, reformat JSON, overwrite a
   competing version or silently re-run cleanup.

## Handoff index

| Handoff | State |
| --- | --- |
| [Library, studio and Gallery planning](2026-11-23-library-studio-planning/README.md) | Harbor continuation; acknowledgment and unresolved decisions remain open. |
| [Cleaned SIMPLE rehearsal](2026-11-21-cleaned-simple-rehearsal/README.md) | Historical cleanup-plan evidence; both rehearsals completed, no new replay authorized. |

Keep an active or transfer-pending handoff in place. Archiving or deletion
requires explicit disposition of every needed payload, recipient and
canonical owner; an archive is not permission to discard private evidence.
