# ComfyUI API Automation — Remaining Proposal

**Status:** API runner and rendered-image delivery remain proposals · **Original analysis:** 2026-10-03 · **Reviewed:** 2026-10-25

> **Current state:** Prompt-to-workflow creation, refresh, and workspace deployment are implemented by
> `tools/workflows/comfy_workflows.py` and its launchers; see [`workflows/README.md`](../../workflows/README.md).
> The API runner, automated ComfyUI execution, and rendered-image delivery to card assets are not implemented.
> This proposal's option E is therefore built; options A–D remain ideas, not shipped features.

This note records the earlier API investigation and its unbuilt automation options. Do not treat its
file counts, workflow exports, node IDs, or proposed output paths as current inventory. Use the
workflow reference for supported commands and behavior.

## 1. What the ComfyUI API gives us

ComfyUI is an HTTP server (default `http://127.0.0.1:8188`). Start it headless with
`python main.py --disable-auto-launch`; add `--listen` only if you need another machine to reach it, because the API has
no authentication. Sources: [server routes](https://docs.comfy.org/development/comfyui-server/comms_routes),
[API examples](https://docs.comfy.org/development/comfyui-server/api-examples).

| Route | Use for us |
| --- | --- |
| `POST /prompt` | Queue a job. Body: `{"prompt": <API-format workflow>, "client_id": ...}`. Returns `prompt_id` and queue position, or `node_errors`. |
| `WS /ws?clientId=...` | Progress events (`executing`, `progress`, `executed`); `executing` with `node: null` means the job finished. |
| `GET /history/{prompt_id}` | Output file names (`filename`, `subfolder`, `type`) once finished. |
| `GET /view` | Download an output image. |
| `POST /upload/image` | Put an input image where `LoadImage` can find it (multipart: `image`, `subfolder`, `type`, `overwrite`). |
| `GET /queue`, `POST /interrupt` | Inspect or cancel. |
| `GET /object_info` | List every node type and its inputs, useful to validate a payload before sending. |

Three facts shape the design:

- **`/prompt` takes API format, not the workflow you save from the UI.** At the time of this
  investigation, the examined workflow files were UI-format (they contain `nodes` and `links`).
  That inventory was from October 2026 and is not a current file count.
- **A job is the whole graph.** The server executes exactly what was posted, so automation means "load template, change
  a few input values, post". The values we change are small: positive text, negative text, the `LoadImage` file name, the
  `SaveImage` prefix, and optionally the seed.
- **The server queues.** Many jobs can be posted at once and run one after another on the single GPU, so a script can
  enqueue a whole batch and walk away.

What we would patch in a typical workflow here (for example `Draknara_Qwen_Scene_Signature.json`): the prompt text sits in
a subgraph node's widget, the input is a `LoadImage` widget, and the output is a `SaveImage` prefix such as
`Draknara/scenes/Draknara_Qwen_Scene_Signature`. The export step must expose those three, which is the main practical
risk (see section 4).

## 2. Five approaches

### A. Template-and-patch runner (script outside ComfyUI)

A Python tool, `tools/art/comfy_run.py`, does the whole loop for a prompt file:

1. Read `prompts/.../Hero_Stage.txt`; split the `prompt:` and `negative prompt:` blocks.
2. Pick the API-format template for that stage from a small table (stage and model -> `workflows/api/<name>.json`) plus a
   node-id map saying where positive, negative, input image, output prefix and seed live.
3. Upload the input image, patch the four values, `POST /prompt`, wait on the WebSocket, then download the result.
4. Save to `assets/art/<same path as the prompt>.png` (the convention already in `data/art/README.md`).

```python
wf = json.load(open(template))
wf[ids["positive"]]["inputs"]["text"] = positive
wf[ids["negative"]]["inputs"]["text"] = negative
wf[ids["image"]]["inputs"]["image"] = uploaded_name
wf[ids["save"]]["inputs"]["filename_prefix"] = out_prefix
post(wf)
```

| Pros | Cons |
| --- | --- |
| Smallest build; standard library plus `websocket-client`. | Node ids are brittle: re-exporting a workflow can renumber them, so the id map needs a check. |
| Output lands at the derived path with no renaming. | One template per workflow shape (Qwen edit, Flux, text-to-image for dragons). |
| Batches overnight. | Does nothing about choosing the input image for later stages (see C). |

### B. Prompt-reader node inside ComfyUI (no patching)

Instead of patching text, give the workflow one node that reads the prompt file itself. Community packs have "load prompts
from file" nodes (verify which are installed before relying on one), or we write a ~50-line custom node, `STLoadPrompt`,
that takes a card id such as `Draknira_Scene_Glamour` and outputs positive text, negative text, the output prefix, and
the expected input image path, all derived from the repo's naming convention.

The workflows stay fully editable in the UI, and the API payload shrinks to "change one string". A script can then drive
it, which makes B a stronger version of A rather than a competitor.

| Pros | Cons |
| --- | --- |
| Works with or without the API server; fixes the copy-paste by itself. | A custom node lives in ComfyUI's folder, outside this repo's tests, unless we vendor it here. |
| No node-id map: the card id is the only varying input. | Workflows need a one-time edit to swap the text widget for the node. |

### C. Pipeline-as-graph with a human gate

Our stages are a dependency graph: A-pose -> head, hair, motion, armor, clothing, scene; staged scenes depend on an
armor or clothing render. Today a person carries each image forward. A runner that knows the graph (stage dependencies are
implied by the templates' "Incoming image" line) can:

- render all `N` seeds of the A-pose for a hero, build a **contact sheet**, and wait for one pick;
- fan out every dependent stage from the picked image;
- repeat at the next gate (for example the armor pick before the staged scenes).

This keeps the only judgement call that matters (does it still look like her?) and removes the carrying. It builds on A or B
and is the natural home for the shiny/foil and variant ideas in STATUS C2.

### D. Staleness tracking (an idea that pays off immediately)

Every re-run we do after a design change ("which prompts must I re-pull tonight?") is a manual diff. Store a sidecar next to
each rendered image: `{prompt_sha256, workflow, seed, model, rendered_at}`. A command, `art_stale.py`, compares the sidecar
hash with the current prompt text and lists exactly what is out of date, or feeds that list to the runner. Because prompts
are generated deterministically, this is cheap, and it turns the long re-pull lists in my change summaries into one command.

### E. Find-or-create workflows by naming convention (the workflow materializer)

Today a prompt and its workflow are matched by hand. The names already follow a rule: the prompt
`prompts/drakn-sisters/Draknara/5_Scenes/signature/Draknara_Scene_Signature.txt` pairs with
`workflows/Draknara/Draknara_Qwen_Scene_Signature.json` (insert `Qwen` after the hero), and its `SaveImage` prefix is
`Draknara/scenes/Draknara_Qwen_Scene_Signature`. A tool can apply that rule and either find the workflow or make it:

1. **Find.** Derive the workflow name from the prompt name. If the file exists, open it and refresh only what changed (the
   positive and negative text when the prompt hash differs). Anything you tuned by hand, such as seed, LoRA toggle, or the
   chosen input image, is kept.
2. **Create.** If it does not exist, copy the stage's template workflow and set the four values that must always agree:
   **positive prompt, negative prompt, `SaveImage` filename prefix, and the workflow file name.** The prefix ends in the
   workflow's own name (`<Hero>/<stage folder>/<WorkflowName>`, e.g. `Draknara/scenes/Draknara_Qwen_Scene_Signature`),
   so the file, its prefix and its rendered images can never drift apart. A fifth value, the `LoadImage` file, is set from
   the previous stage's output by convention (or an input named on the card). Write the result to `workflows/<Hero>/` so it
   opens in ComfyUI like any other workflow.
3. **Queue.** Open it and press Queue, or hand it to the runner in A.

What the earlier repository scan found (a point-in-time inventory, not current counts):

- **One template covers most work.** 58 of the 91 workflows have the same structure: a `LoadImage`, a `SaveImage` and one
  "Image Edit (Qwen-Image 2511)" subgraph node. In that node `widgets_values[0]` is the positive prompt and `[1]` the
  negative; model names, the Lightning toggle and the seed follow. The other 33 (Flux, FireRed, MageFlow polish) are
  one-offs that can stay manual.
- **Patching the UI-format file is enough for this approach.** It needs no API export, no running server, and keeps
  the workflow editable. The runner in A still needs an API-format twin of the same template, patched the same way.
- **Lookup by name rarely hits today.** Only 14 of the 297 current prompts have a same-named workflow, because most
  workflows were made for earlier prompt names. So "create" will be the common path at first, which is the argument for
  templates rather than hand-copied workflows.
- **The stage table is small.** One entry per stage type (pose, head, hair, motion, armor, clothing, scene, staged scene)
  maps to a template and a default input, for example: scene -> the hero's chosen A-pose; staged scene -> a named
  outfit render. Dragon prompts need a text-to-image template with no `LoadImage`.

| Pros | Cons |
| --- | --- |
| Removes the copy-paste with no server and no API export; the output is a normal workflow file. | Adds many generated workflow files to the repo; keep them out of git or in one folder. |
| Idempotent: re-running refreshes prompts and keeps your tweaks. | Needs the template and the widget positions pinned, and a check that they still match after a ComfyUI update. |
| Gives the runner (A) and the staleness check (D) one place to find each prompt's workflow. | Does not queue by itself. |

### Other options considered

| Option | Verdict |
| --- | --- |
| `comfy-cli` (`comfy run --workflow ...`) | Same as A with less code but little control over patching text or collecting outputs. Worth checking for batch support. |
| ComfyScript or "workflow to Python" converters | Replaces the template and id map with generated Python. More freedom, more dependency; revisit if A's id map becomes painful. |
| ComfyUI Cloud API | Useful for burst volume if the local GPU becomes the bottleneck; same payload shape, so A and B port to it. Not needed yet. |
| Fully automatic selection (an image-quality or face-similarity model picks the winner) | Tempting but unproven for identity; keep the human gate until a similarity check is validated against your own picks. |

## 3. Earlier recommendation and present status

The materializer in option E is now part of the supported workflow tooling. The API runner,
staleness sidecars, human-gated dependency graph, and rendered-asset delivery below remain
unimplemented. STATUS/C1 and the active plans own current asset-delivery decisions.

Build in this order; each step is useful on its own.

| Step | Earlier proposal | Current status |
| --- | --- | --- |
| 1 | **E then A, with D**: materializer, API runner, and staleness sidecars | E is built and documented in `workflows/README.md`; A and D are not built. |
| 2 | **B** (prompt-reader node), only if a node map proves fragile | Not built or approved. |
| 3 | **C**: stage graph, contact sheet, approval gate | Not built or approved. |
| 4 | Link outputs into cards and validate referenced assets | Still open; resolve through current STATUS and plans before implementation. |

## 4. Open questions and risks

- **Export format.** Confirm that `Export (API)` on a workflow with subgraphs produces a flat graph where the prompt text,
  `LoadImage` and `SaveImage` are patchable. If it does not, option B avoids the problem entirely.
- **Output names.** `SaveImage` appends a counter (`_00001_`), so the runner should read the real name from `/history`
  and copy it to the derived path instead of guessing.
- **Seeds.** Decide whether re-runs reuse a seed (reproducible) or draw new ones (more choice); the sidecar records either.
- **Model coverage.** The repo mixes Qwen, Flux and FireRed workflows. Start with the two Qwen shapes in daily use.
- **Security.** Keep the server on localhost unless the machine is firewalled; the API can run arbitrary workflows.
- **Dragons.** Their prompts are text-to-image, so they need no input image: a separate, simpler template in step 1.
