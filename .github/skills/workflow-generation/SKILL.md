---
name: workflow-generation
description: "Use when preparing Sovereign Territories art or video prompts, generating ComfyUI workflows, inspecting workspace inputs, or planning authorized deployment and pullback. Preserve manual sources and respect preview side effects."
---

# Prompt and workflow generation

Read [status](../../../docs/STATUS.md), the current Queue focus via the
[planning agreement](../../../docs/plans/README.md), the
[art-data reference](../../../data/art/README.md),
[workflow runbook](../../../workflows/README.md) and
[launcher help](../../../bin/help.cmd). Consult the affected active contract;
historical art-pipeline design notes are not current operational authority.
Identify the approved hero/set, stage, sources, target workspace and allowed
repository/workspace writes before using a generator or deployment.

1. Follow the source chain: gameplay/art identity and assembly data ->
   generated prompts -> stage templates -> repo workflows -> chosen workspace.
   The supported ST templates are masters; curated workflows, workspace
   `zz_` work and `prompts/_edit` manual migration sources are not disposable
   generated files. Do not hand-edit generated prompt output.
2. Check the actual launcher, arguments and destination before calling it.
   Prompt generation writes files. In particular, `refresh.cmd`,
   `refresh-group.cmd`, `refresh-firered.cmd` and `animate.cmd` invoke prompt
   generation even with `--dry-run`; that flag only previews their subsequent
   workflow/deployment steps. Do not use those composite commands as a
   read-only preview. Several convenience launchers add `--apply` by default.
3. Use supported status/preview commands and inspect exact pending changes
   before an authorized regeneration or workspace deployment. Preserve
   hand-tuned workflows, input selections, previous outputs and backups;
   never overwrite or retarget another workspace silently. Source selection,
   copying inputs, deployment and pulling chosen results are separate actions.
4. Validate the affected prompts/workflows and supported launcher as required
   by the [quality gates](../../../docs/guidelines/QUALITY-GATES.md). Distinguish
   generated, deployed, rendered and human-reviewed states.

For frozen reference batches, server compatibility and existing execution
receipts, use [ComfyUI rendering](../comfyui-rendering/SKILL.md). Preparing
workflows does not authorize creating art assets or queuing rendering.
