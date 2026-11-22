---
name: documentation-maintenance
description: "Use when writing, reviewing, organizing or updating Sovereign Territories documentation, technical-debt records, plans, links and generated navigation."
---

# Documentation maintenance

Read [status](../../../docs/STATUS.md), the
[documentation map](../../../docs/README.md), the
[planning agreement](../../../docs/plans/README.md) and the affected
canonical contract. Identify the document's role: current rule/runbook,
plan, historical evidence, generated output or preserved raw feedback.
Keep one authoritative home per fact and link to it rather than copying it.
Ignore `_archive` except for explicitly authorized scoped archive work.

## Update and organize

1. Verify the actual code, launcher or decision before documenting it.
   Update directly affected examples, arguments, links and cross-references;
   distinguish proposed, implemented, tested, installed and human-approved
   states. Do not silently turn an observation into a rule.
2. Preserve other contributors' edits, historical prose and verbatim user
   sources. Reconcile concurrent machine updates rather than overwriting
   them. Use [feedback filing](../feedback-filing/SKILL.md) when recording
   chat or filing feedback; leave unresolved sources in place.
3. Record actionable debt in the existing owning plan with priority, owner,
   evidence and a next gate. Plans do not themselves activate holding work.
   Change Queue focus only through an authorized spine transfer; regenerate
   `bin\todo.cmd` after plan changes rather than editing its output.
4. For authorized moves, follow the
   [archive guide](../../../docs/guidelines/ARCHIVE-GUIDE.md): preserve
   history, fix incoming links and indexes, and verify any ignored-source
   move without overwriting. Never bulk-clear feedback or temporary notes.
5. Check changed links and anchors, relevant generated readers, and
   documentation lint/tests where applicable under
   [quality gates](../../../docs/guidelines/QUALITY-GATES.md). Report
   what was checked; do not claim a whole-document audit from a search or
   index alone.
