# Template Analysis Plan — ComfyUI Workflow Templates

**Status:** Plan (Pass 0) · **Last updated:** 2026-09-30
**Goal:** Sort the 23 pre-built templates in `workflows/Templates/` into a shortlist we can
actually use on this rig, then design a small **Sovereign Territories** template set (one per
pipeline step) by picking a base template, swapping in the best models, and tuning
denoise / scaling / steps.

This is the *plan* only. Findings and recommendations land in a companion doc
(`template-analysis-findings.md`) after the passes below.

---

## Hard constraint: the rig

- **GPU: NVIDIA RTX 3050, 8 GB VRAM.** This is the primary filter. A "better" model that
  won't fit (or takes 10–20 min/image) is **not** better for this workflow.
- Practical implication: favour **4B / int8 / fp8 / gguf** variants and models with **Turbo /
  Lightning / distilled** step reduction. Flag 14B / full-precision / large models as
  *aspirational only* (cloud or a future GPU).
- Every template gets a **Feasibility** rating: ✅ fits 8 GB · ⚠️ borderline (offload/slow) ·
  ❌ too heavy.

---

## The 23 templates (grouped by apparent family)

| Family | Files |
| --- | --- |
| **Qwen Image-Edit** | `image_qwen_image_edit`, `_2509`, `_2511`, `_2511_int8`, `_2511_systms_action`, `image_qwen_edit_2511_lora_inflation`, `image_qwen_image_2_1_image_edit` |
| **Flux.2** | `image_flux2`, `image_flux2_fp8`, `image_flux2_klein_9b_kv_image_edit`, `image_flux2_klein_image_edit_4b_base`, `image_flux2_klein_image_edit_4b_distilled` |
| **Flux Kontext** | `image_flux_kontext_dev_basic` |
| **FireRed** | `image_firered_image_edit1_1` |
| **HiDream** | `image_hidream_e1_1`, `image_hidream_o1` |
| **ChronoEdit 14B** | `image_chrono_edit_14B` |
| **Others** | `image_longcat_image_edit`, `image_mage_flow_edit_turbo_int8`, `image_omnigen2_image_edit`, `image_sd3.5_large_blur`, `image_simple3StepImage_v10`, `image_wan2.1_fun_control` |

*(Family is a guess from filenames; confirmed in Pass 1.)*

---

## What we extract per template

| Field | Notes |
| --- | --- |
| **Model family + exact files** | UNet/diffusion, text encoder(s), VAE, LoRA(s) — verbatim filenames (encode version/quant). |
| **Task type** | txt2img (EmptyLatent) vs **img2img/edit** (LoadImage → VAEEncode). We mostly want edit. |
| **Structure** | **Subgraph-wrapped** vs **open/flat** graph. Open = easier to swap models/params. |
| **Tunable params exposed** | denoise, steps, cfg/guidance, sampler, scheduler — and whether they're editable widgets vs buried in a subgraph. |
| **Image scaling** | Present? (`ImageScale`, `ImageScaleToTotalPixels`) and target resolution / megapixels. |
| **Step-reduction** | Turbo / Lightning / distilled / gguf — affects speed on 8 GB. |
| **Feasibility (8 GB)** | ✅ / ⚠️ / ❌ with reason. |
| **Pipeline fit** | Which of our stages it could serve (see mapping below). |

---

## Pipeline-stage mapping (what we're shopping for)

From [`comfyui-art-pipeline.md`](comfyui-art-pipeline.md), we need a model/template for each step:

1. **A-pose base** — clean full-body generation from a real/AI reference. (img2img edit, denoise high.)
2. **Edit steps** (hair → armor/clothing → stance/motion) — change one thing, hold the rest.
   (img2img edit, denoise ~0.4–0.7.)
3. **Final render** — fidelity pass (FireRed sibling or Flux).
4. **Polish** — skin/texture/eyes (denoise ~0.2–0.4).
5. **Inpaint** (future) — swap a weapon/armor region (Fill/Kontext-style).

Each template is scored on which of these it best serves on this rig.

---

## Pass structure (how the analysis runs)

- **Pass 1 — Model extraction.** For all 23: family, exact model files, task type, LoRAs,
  step-reduction. Output: raw model table.
- **Pass 2 — Structure & params.** Subgraph vs open, which params are editable, image-scaling
  nodes + resolution, sampler/scheduler/denoise defaults.
- **Pass 3 — Feasibility + fit scoring.** Apply the 8 GB filter; map each to pipeline stages;
  mark ✅/⚠️/❌ and a "focus / maybe / skip" verdict.
- **Pass 4 — Recommendations & ST set design.** Shortlist to test, then propose the
  **Sovereign Territories template set**: for each pipeline step, pick a base template, state
  which models to load and why, and the denoise/scaling/steps to set.

---

## Deliverables

1. `template-analysis-findings.md` — the filled comparison tables (Pass 1–3).
2. A **shortlist** of templates worth generating test images with (minimise wasted GPU time).
3. A proposed **`workflows/SovereignTerritories/`** set: one tuned template per pipeline step,
   with documented model choices and parameters.

---

## Working principles

- **Minimise your GPU time.** The point of this analysis is to hand you a *short* list to test,
  not make you render all 23.
- **Prefer open/flat templates** as bases for our custom set — easier to swap models and expose
  denoise/scaling than subgraph-wrapped ones.
- **Model choice is expensive to change later** — lock the base once, via the A-pose harness.
