# Sovereign Territories — Workflow Set

Forked from `workflows/Templates/` (analysis in
[`docs/art/template-analysis-findings.md`](../../docs/art/template-analysis-findings.md)).
One tuned workflow per pipeline step, named `ST_<Model>_<Stage>`. Tuned for an **8 GB RTX 3050**.

> These are **copies of the source templates, renamed.** Set the **defaults** below in the ComfyUI
> GUI (a few clicks) — the values live inside each graph's subgraph, so they're set in-app, not here.
> Pipeline context: [`docs/art/comfyui-art-pipeline.md`](../../docs/art/comfyui-art-pipeline.md).

---

## The set

| ST workflow | Forked from | Model | Pipeline role | denoise | steps | scaling |
| --- | --- | --- | --- | --- | --- | --- |
| **ST_Qwen_A_Pose** | `image_qwen_image_edit_2511` | Qwen-Image-Edit **2511** | A-pose base (your current) | **1.0** | 4 (Lightning) | add portrait target |
| **ST_Qwen_B_Pose** | `image_qwen_image_2_1_image_edit` | Qwen-Image **2.1** (int8) | A-pose base (new candidate) | **1.0** | 25 (or 4 w/ Lightning) | `ResolutionSelector` (built-in) |
| **ST_Qwen_Edit** | `image_qwen_image_edit_2511` | Qwen-Image-Edit **2511** | Edit: hair → armor → stance | **0.5** | 4–8 | match A-pose |
| **ST_FireRed_Final** | `image_firered_image_edit1_1` | FireRed-1.1 | Final render (low-drift) | **0.7** | 8 (Lightning) | + upscale |
| **ST_Flux_Polish** | `image_flux2_klein_image_edit_4b_distilled` | Flux.2 Klein **4B** | Polish (skin/texture) | **0.3** | 8–12 | — |
| **ST_Qwen_Polish** | `image_qwen_image_edit_2511_int8` | Qwen-Image-Edit **2511 int8** | Polish (Qwen alt) | **0.3** | 8 | — |

**Why these:** A-pose + Edit share the **same model** (only denoise differs) → no cross-model drift
in the exploration chain. FireRed shares Qwen's VAE/encoder → a faithful higher-fidelity final.
Flux Klein-4B is the only Flux "look" that fits 8 GB. Two polish options (Flux vs Qwen) to compare.

---

## Defaults to set per file (in ComfyUI)

- **ST_Qwen_A_Pose** — denoise **1.0** (full generation). Enable the **4-step Lightning LoRA** for
  ~1–2 min drafts. Add a scaling node (`ImageScaleToTotalPixels` ~1 MP, portrait) so output size is fixed.
- **ST_Qwen_B_Pose** — denoise **1.0**. It already has a `ResolutionSelector` — set a **portrait**
  target (e.g. 832×1216 ≈ 1 MP). This is the newer Qwen 2.1; compare its feel/speed vs A_Pose.
- **ST_Qwen_Edit** — denoise **~0.5** (change one thing, hold the rest). Same model as your A-pose
  choice. Use for hair → armor/clothing → stance passes.
- **ST_FireRed_Final** — denoise **~0.7**, 8-step Lightning. Feed your near-final image; prompt only
  background / spell / weapon / stance. Add an upscale after.
- **ST_Flux_Polish** — denoise **~0.3** (enhance, don't redraw). Klein-4B fits 8 GB; the full Flux.2
  dev polish is heavier/borderline — use this as the feasible version.
- **ST_Qwen_Polish** — denoise **~0.3**. int8, stays in the Qwen family (least drift for a polish pass).

## Parameters worth exposing (promote to the top level in the GUI)

For each graph, right-click the widget inside the subgraph → **convert to input / promote** so you
don't have to open the subgraph each run:

- **denoise** (most important — you'll change it per stage)
- **steps** and the **Lightning/Turbo toggle** (speed vs quality)
- **cfg / guidance**
- **scaling target** (megapixels or width/height)
- **seed** (to lock or roll)

---

## Suggested bake-off (minimise GPU time)

1. **A-pose base:** run **ST_Qwen_A_Pose** vs **ST_Qwen_B_Pose** on the same reference → pick the
   feel + speed you prefer. That locks your base model.
2. **Polish:** run **ST_Flux_Polish** vs **ST_Qwen_Polish** on one near-final image at low denoise →
   pick the finisher.
3. **Final:** confirm **ST_FireRed_Final** holds likeness on a near-final image.

Then we lock the winners, delete the losers, and this becomes the standard set for SD-001…SD-010.

*(Optional extra to test later: a MageFlow Turbo int8 edit — very fast on 8 GB. Say the word and
I'll add `ST_MageFlow_Edit`.)*
