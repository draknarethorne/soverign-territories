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
| **ST_Qwen_A_Pose** | your `X_Qwen_A_Pose` = `image_qwen_image_edit_2511` (Turbo toggle) | Qwen-Image-Edit **2511** fp8mixed + Lightning | A-pose base (your current) | **1.0** | 4 (Turbo) / 40 (off) | add portrait target |
| **ST_Qwen_B_Pose** | `image_qwen_image_2_1_image_edit` | Qwen-Image **2.1** (int8) | A-pose base (new candidate) | **1.0** | 25 (or 4 w/ Lightning) | `ResolutionSelector` (built-in) |
| **ST_Qwen_Edit** | your `X_Qwen_A_Pose` (= `image_qwen_image_edit_2511`) | Qwen-Image-Edit **2511** fp8mixed | Edit: hair → armor → stance | **0.5** | 4 (Turbo) | match A-pose |
| **ST_FireRed_Final** | `image_firered_image_edit1_1` | FireRed-1.1 | Final render (low-drift) | **0.7** | 8 (Lightning) | + upscale |
| **ST_Flux_Polish** | `image_flux2_klein_image_edit_4b_distilled` | Flux.2 Klein **4B** | Polish (skin/texture) | **0.3** | 8–12 | — |
| **ST_Qwen_Polish** | `image_qwen_image_edit_2511_int8` | Qwen-Image-Edit **2511 int8** | Polish (Qwen alt) | **0.3** | 8 | — |
| **ST_MageFlow_Edit** | `image_mage_flow_edit_turbo_int8` | MageFlow Turbo **int8** | Fast edit alt (8 GB speed) | **0.5** | Turbo | — |
| **ST_Flux_Final** | `image_flux2_fp8` | Flux.2 dev fp8mixed +Turbo v2 | Final (max quality) ⚠️ borderline 8 GB | **0.7** | 20 | 1 MP |

**Why these:** A-pose + Edit share the **same model** (only denoise differs) → no cross-model drift
in the exploration chain. **ST_Qwen_A_Pose / ST_Qwen_Edit are copies of your working 2511 workflow —
which is the same as the downloaded `image_qwen_image_edit_2511` template** (same `cdb2cf24` subgraph
+ **Turbo toggle**: 4-step draft ↔ 40-step overnight). Your saved copy just also carries your A-pose
prompt. FireRed shares Qwen's VAE/encoder → a faithful higher-fidelity final. Flux Klein-4B is the
only Flux "look" that comfortably fits 8 GB; Flux.2 fp8 is the aspirational max-quality final.

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
- **ST_MageFlow_Edit** — denoise **~0.5**. int8 Turbo, built for speed on small GPUs; a fast alternative
  to ST_Qwen_Edit — test its quality vs Qwen.
- **ST_Flux_Final** — denoise **~0.7**, 20 steps. ⚠️ fp8mixed Flux.2 is **borderline on 8 GB** (expect
  offload/slower); use for a max-quality final only if it fits, else stick with FireRed.

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

---

## Models to download (check what you already have)

Most templates embed Hugging Face URLs in their in-graph "Model Links" note, so ComfyUI desktop can
often auto-fetch missing files. Full list by type:

**Diffusion / UNet**

- `qwen_image_edit_2511_fp8mixed.safetensors` — ST_Qwen_A_Pose, ST_Qwen_Edit *(you have this)*
- `qwen_image_2.1_int8_convrot.safetensors` — ST_Qwen_B_Pose
- `qwen_image_edit_2511_int8_convrot.safetensors` — ST_Qwen_Polish
- `FireRed-Image-Edit-1.1-transformer.safetensors` — ST_FireRed_Final
- `flux-2-klein-4b-fp8.safetensors` — ST_Flux_Polish
- `mage_flow_edit_turbo_int8_convrot.safetensors` — ST_MageFlow_Edit
- `flux2_dev_fp8mixed.safetensors` — ST_Flux_Final

**Text encoders**

- `qwen_2.5_vl_7b_fp8_scaled.safetensors` — all Qwen 2511 + FireRed *(you have this)*
- `qwen3vl_8b_int8_convrot.safetensors` — ST_Qwen_B_Pose (2.1)
- `qwen_3_4b.safetensors` — ST_Flux_Polish (klein-4B)
- `qwen3vl_4b_bf16.safetensors` — ST_MageFlow_Edit
- `mistral_3_small_flux2_fp8.safetensors` — ST_Flux_Final

**VAE**

- `qwen_image_vae.safetensors` — all Qwen 2511 + FireRed *(you have this)*
- `qwen_image_2.1_vae_bf16.safetensors` — ST_Qwen_B_Pose
- `flux2-vae.safetensors` — ST_Flux_Polish, ST_Flux_Final
- `mage_flow_vae_bf16.safetensors` — ST_MageFlow_Edit

**LoRA**

- `Qwen-Image-Edit-2511-Lightning-4steps-V1.0-bf16.safetensors` — ST_Qwen_A_Pose/Edit *(you have this)*
- `FireRed-Image-Edit-1.0-Lightning-8steps-v1.0.safetensors` — ST_FireRed_Final
- `Flux2TurboComfyv2.safetensors` — ST_Flux_Final

*Already covered by your current Qwen workflow: the 2511 fp8mixed model, `qwen_2.5_vl_7b`, `qwen_image_vae`,
and the 4-step Lightning LoRA. The **new** downloads are the 2.1, FireRed, Flux Klein-4B, MageFlow, and
Flux.2-fp8 stacks.*
