# Template Analysis — Findings

**Status:** Pass 1–3 complete · **Last updated:** 2026-09-30
**Companion to:** [`comfyui-art-pipeline.md`](comfyui-art-pipeline.md)
**Rig filter:** NVIDIA RTX 3050, **8 GB VRAM** (the deciding constraint)

Extracted from the 23 templates in `workflows/Templates/`. Values inside subgraphs are marked
*(sg)* where not exposed at the top level. Feasibility: ✅ fits 8 GB · ⚠️ borderline (offload/slow)
· ❌ too heavy.

---

## 1. Master comparison

### Qwen Image-Edit family (shares `qwen_image_vae` + a Qwen-VL text encoder)

| Template | Diffusion model | Quant | Task | Structure | Steps | denoise | Scaling | 8 GB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `image_qwen_image_edit` | qwen_image_edit fp8_e4m3fn | fp8 | edit | subgraph | **4** (Lightning) | 1.0 | 1.5 MP | ✅ fast |
| `image_qwen_image_edit_2509` | qwen_image_edit_2509 fp8 | fp8 | edit | subgraph | **4** (Lightning) | 1.0 | — | ✅ fast |
| `image_qwen_image_edit_2511` | qwen_image_edit_2511 bf16 | bf16 | edit (dual-ref) | subgraph | 40 | 1.0 | — | ⚠️ ~5–6 GB |
| `image_qwen_image_edit_2511_int8` | qwen_image_edit_2511 int8_convrot | **int8** | edit | subgraph | 40 *(→4 w/ Lightning)* | 1.0 | — | ✅ ~2–3 GB |
| `image_qwen_image_edit_2511_systms_action` | 2511 bf16 + **ACTION LoRA** | bf16 | edit + action ctrl | subgraph | 40 | 1.0 | — | ⚠️ ~5–6 GB |
| `image_qwen_edit_2511_lora_inflation` | 2511 bf16 + user LoRA | bf16 | edit + custom LoRA | subgraph | 40 | 1.0 | — | ⚠️ ~5–6 GB |
| `image_qwen_image_2_1_image_edit` | qwen_image **2.1** int8_convrot | **int8** | edit | subgraph | 25 | 1.0 | **ResolutionSelector** (1 MP) | ✅ ~2–3 GB |

*Text encoder is `qwen_2.5_vl_7b_fp8` for all except v2.1, which uses the newer `qwen3vl_8b` int8.*

### Flux family

| Template | Diffusion model | Text enc | Task | Structure | Steps | Scaling | 8 GB |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `image_flux2` | flux2_dev fp8mixed **+Turbo LoRA** | Mistral-3-sm bf16 | edit | subgraph | *(sg)* | ImageScaleToTotalPixels | ⚠️ ~8–10 GB |
| `image_flux2_fp8` | flux2_dev fp8mixed **+Turbo v2** | Mistral-3-sm fp8 | edit | subgraph | 20 | 1 MP (1024²) | ⚠️ ~8–10 GB |
| `image_flux2_klein_9b_kv_image_edit` | flux-2-klein-9b-kv fp8 | qwen_3_8b fp8 | edit | subgraph (large) | *(sg)* | *(sg)* | ⚠️ ~8–10 GB |
| `image_flux2_klein_image_edit_4b_base` | flux-2-klein-**4b**-base fp8 | qwen_3_4b | edit | subgraph | *(sg)* ~16–20 | small-dec | ✅ ~6–8 GB |
| `image_flux2_klein_image_edit_4b_distilled` | flux-2-klein-**4b** fp8 (distilled) | qwen_3_4b | edit | subgraph | *(sg)* ~8–12 | — | ✅ ~6–8 GB |
| `image_flux_kontext_dev_basic` | flux1-dev-**kontext** fp8_scaled | clip_l + t5xxl fp16 | **inpaint/edit** | subgraph | *(sg)* | FluxKontextImageScale | ⚠️/❌ ~10–12 GB |

### Other families

| Template | Model | Quant | Task | Structure | 8 GB | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `image_firered_image_edit1_1` | FireRed-1.1 transformer **+Lightning 8-step** | fp8 enc | edit | subgraph | ✅ ~6–7 GB | **Qwen-family VAE/encoder → low drift** |
| `image_longcat_image_edit` | longcat bf16 | bf16 | edit | subgraph | ✅ ~6–7 GB | long-context edit; `ImageCompare` node |
| `image_mage_flow_edit_turbo_int8` | mage_flow turbo **int8_convrot** | **int8** | edit | subgraph | ✅ ~5–6 GB | speed-built for small GPUs; 4B enc |
| `image_omnigen2_image_edit` | OmniGen2 (multi-ref) | — | edit (multi-ref) | **flat** | ⚠️ ~7–8 GB | accepts **multiple ref images** |
| `image_hidream_e1_1` | hidream_e1_1 bf16 | bf16 | edit | loose/groups | ❌ ~10–12 GB | heavy |
| `image_hidream_o1` | HiDream O1 checkpoint | full | edit | subgraph | ❌ ~12 GB+ | heavy |
| `image_chrono_edit_14B` | chrono_edit **14B** fp16 +distill | fp16 | edit (temporal) | subgraph | ❌ ~28 GB | **way too heavy** |
| `image_sd3.5_large_blur` | SD3.5-Large + blur ControlNet | — | **txt2img**+control | subgraph+groups | ❌ ~10–12 GB | not a portrait-edit flow |
| `image_simple3StepImage_v10` | generic SD base (unnamed) | — | txt2img/img2img | subgraph | ✅* | 3-step + upscale demo |
| `image_wan2.1_fun_control` | wan2.1_fun_control **1.3B** bf16 | bf16 | **txt2img**+control | groups | ✅ ~4–5 GB | video/control model, not portrait edit |

---

## 2. Feasibility tiers (the 8 GB filter)

- **✅ Comfortable:** Qwen fp8 (orig/2509), Qwen 2511 **int8**, Qwen **2.1** int8, MageFlow Turbo int8,
  FireRed, LongCat, Flux.2 **klein 4B** (base/distilled), WAN 2.1 (lightweight).
- **⚠️ Borderline (offload, slower):** Qwen 2511 bf16 (+action/inflation), Flux.2 dev fp8mixed (+Turbo),
  Flux.2 klein 9B, OmniGen2, Flux **Kontext** (dual CLIP is the weight).
- **❌ Skip on this rig:** ChronoEdit 14B, HiDream E1.1, HiDream O1, SD3.5-Large+ControlNet.

---

## 3. Structure — subgraph vs flat (why it matters)

- **Almost every template wraps sampling in a ComfyUI *subgraph*.** Loaders + a `LoadImage` +
  `SaveImage` sit at the top; KSampler/denoise/steps live *inside* the subgraph. To swap models or
  tune denoise/scaling you must **enter the subgraph** (or the template exposes a few widgets, like
  your Qwen turbo toggle).
- **Flat/open exceptions:** `image_omnigen2_image_edit` (ReferenceLatent visible), and the loosely
  grouped `image_hidream_e1_1` / `image_wan2.1_fun_control` / `image_simple3StepImage_v10`.
- **Implication for our custom set:** the cleanest bases to fork are the **Qwen subgraph templates**
  (you already know how their exposed widgets behave) — we keep the subgraph but standardise the
  widgets we expose (denoise, steps, scaling target).

---

## 4. Image scaling

- **Has a scaling node** (predictable output size): Qwen orig (1.5 MP), Qwen **2.1** (`ResolutionSelector`,
  best pattern), Flux.2 / Flux.2 fp8 (`ImageScaleToTotalPixels`, 1 MP), Flux Kontext (`FluxKontextImageScale`).
- **No scaling** (inherits input size): Qwen 2509 / 2511 / 2511-int8 / action / inflation, LongCat, as shipped by ComfyUI.
  Our own ST templates differ: ST1/ST2/ST4 Qwen carry `FluxKontextImageScale` (nearest bucket by aspect, then centre-crop;
  944x1104 is a bucket so it passes unchanged) and ST3 FireRed carries `ResizeImageMaskNode` (scale total pixels, 1 MP = 1,048,576 px,
  Lanczos; a 944x1104 input becomes 947x1107 and the VAE trims it back to 944x1104). The standard size is 944x1104 (Oct 2026, provisional).
- **Action item:** card art wants a **fixed portrait target**. Copy Qwen 2.1's `ResolutionSelector` (or
  `ImageScaleToTotalPixels`) into any base that lacks scaling so every stage outputs a consistent size.

---

## 5. Recommendation — a short test list (save GPU time)

Instead of rendering all 23, test **five** against your A-pose bake-off:

| Priority | Template | Role it's competing for | Why |
| --- | --- | --- | --- |
| 1 | `image_qwen_image_edit_2511_int8` | A-pose + edit workhorse | Newest 2511 edit quality, int8 fits 8 GB; add Lightning for 4-step speed. |
| 2 | `image_qwen_image_2_1_image_edit` | A-pose + edit (modern) | Newest Qwen **2.1** + built-in `ResolutionSelector`; int8. Likely your best new base. |
| 3 | `image_mage_flow_edit_turbo_int8` | fast edit alt | Purpose-built for small-GPU speed; sanity-check its quality vs Qwen. |
| 4 | `image_firered_image_edit1_1` | **final render** | Qwen-family VAE/encoder → upgrades fidelity with minimal drift. |
| 5 | `image_flux2_klein_image_edit_4b_distilled` | Flux-look final that **fits 8 GB** | The Flux.2 dev/Kontext finals are borderline; klein-4B is the feasible Flux option. |

Everything else is either a heavier duplicate, off-task (control/txt2img), or ❌ on 8 GB.

---

## 6. Proposed *Sovereign Territories* template set

Target: `workflows/SovereignTerritories/` — one tuned template per pipeline step, forked from a
base above, with models + params locked. (Built in **Pass 4**, after you pick from §5.)

| ST template | Fork from | Model choice | denoise | steps | scaling |
| --- | --- | --- | --- | --- | --- |
| `ST_A_Pose` | Qwen 2.1 **or** 2511-int8 | int8 edit + Lightning | **1.0** | 4–8 | ResolutionSelector (portrait) |
| `ST_Edit` (hair/armor/stance) | same as A-pose | same | **0.4–0.7** | 4–8 | match A-pose |
| `ST_Final` | FireRed | FireRed + 8-step Lightning | **0.6–0.8** | 8 | + upscale |
| `ST_Polish` | Flux.2 klein-4B (or Qwen) | small/distilled | **0.2–0.4** | 8–12 | — |
| `ST_Inpaint` *(future)* | Flux Kontext *(aspirational)* | Kontext | region | *(sg)* | Kontext scale |

*Keeping A-pose and Edit on the **same** model/template (just different denoise) is the biggest
consistency win — no cross-model drift within the exploration chain.*

---

## 7. Open questions for you

1. Confirm the **base model** for A-pose + edit: **Qwen 2.1** (newest, built-in scaling) vs **2511-int8**
   (proven 2511 quality). A quick bake-off of these two decides it.
2. Final-render pick: **FireRed** (low-drift) vs **Flux.2 klein-4B** (different look) — test on one near-final image.
3. Do you want the **ST set built now** (I can fork/edit the JSON templates: set models, denoise, add
   scaling), or wait until you've run the §5 bake-off?

---

## 8. Disk clean-up (Oct 2026)

Every path is relative to `B:\Comfy-Desktop\ComfyUI-Shared\models` (388 GB in use). The lists come from scanning the ST templates in
`workflows/_templates` and every workflow in every ComfyUI workspace for the model files they load. Nothing here has been deleted. Do the stages
in order; each one is safe once the one before it is done.

### Stage 1: models no template or workflow uses (61.4 GB)

No ST template, generated workflow, stock template or experiment loads any of these, so there is nothing to break.

| Path | GB |
| --- | --- |
| `checkpoints/ltx-2.3-22b-dev-fp8.safetensors` | 21.09 |
| `diffusion_models/z_image_turbo_bf16.safetensors` | 12.31 |
| `text_encoders/gemma_3_12B_it_fp4_mixed.safetensors` | 9.45 |
| `checkpoints/juggernautXL_ragnarok.safetensors` | 7.11 |
| `checkpoints/dreamshaperXL_lightningDPMSDE.safetensors` | 6.94 |
| `loras/ltx_2.3_22b_distilled_1.1_lora_dynamic_fro09_avg_rank_111_bf16.safetensors` | 2.74 |
| `latent_upscale_models/ltx-2.3-spatial-upscaler-x2-1.1.safetensors` | 1.00 |
| `loras/gemma-3-12b-it-abliterated_lora_rank64_bf16.safetensors` | 0.63 |
| `loras/JuggerCineXL2.safetensors` | 0.17 |
| `diffusion_models/flux-2-klein-base-9b-fp8.safetensors` (empty file, 0 bytes) | 0.00 |

Why: LTX is video and our video is MiniMax; Juggernaut, Dreamshaper and Z-Image have no ST template; the gemma files are the LTX text encoder and its LoRA.
If one of these returns to the plan, it needs a template first.

### Stage 2: stock templates and experiments to remove, and the models tied to them (127.7 GB)

The stock templates and the early `X_*` experiments live in the base `ComfyUI` workspace
(`B:\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\user\default\workflows`); the `Sovereign Territories` dev workspace holds only the ST templates.
Remove these workflow files from it:

- Stock templates: `image_chrono_edit_14B`, `image_flux_kontext_dev_basic`, `image_flux2`, `image_flux2_klein_9b_kv_image_edit`, `image_hidream_e1_1`,
  `image_hidream_o1`, `image_longcat_image_edit`, `image_mage_flow_edit_turbo_int8`, `image_omnigen2_image_edit`, `image_qwen_edit_2511_lora_inflation`,
  `image_qwen_image_edit`, `image_qwen_image_edit_2509`, `image_qwen_image_edit_2511_systms_action`, `image_sd3.5_large_blur`, `image_simple3StepImage_v10`,
  `image_wan2.1_fun_control`, `video_minimax_h3_r2v`.
- Early experiments: `X_Flux1_A_Pose`, `X_JoyAI_A_Pose`.
- Keep as references: `image_firered_image_edit1_1`, `image_qwen_image_edit_2511`, `image_qwen_image_edit_2511_int8`, `image_qwen_image_2_1_image_edit`,
  `image_flux2_fp8`, `image_flux2_klein_image_edit_4b_base`, `image_flux2_klein_image_edit_4b_distilled`, and your `X_FireRed_*`, `X_Qwen_*`, `X_Vid_*` workflows.

Once those are gone, these models are used by nothing else:

| Path | GB | Only used by |
| --- | --- | --- |
| `diffusion_models/flux1-fill-dev.safetensors` | 23.80 | `X_Flux1_A_Pose` |
| `diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors` | 20.97 | `video_minimax_h3_r2v` |
| `diffusion_models/joyai_image_edit_int8_convrot.safetensors` | 16.43 | `X_JoyAI_A_Pose` |
| `checkpoints/hidream_o1_image_bf16.safetensors` | 16.37 | `image_hidream_o1` |
| `text_encoders/qwen3vl_8b_joyimage_edit_int8_convrot.safetensors` | 10.06 | `X_JoyAI_A_Pose` |
| `text_encoders/t5xxl_fp16.safetensors` | 9.79 | `X_Flux1_A_Pose` |
| `text_encoders/gemma4_e4b_it_fp8_scaled.safetensors` | 9.06 | `image_hidream_o1` |
| `text_encoders/qwen_3_8b_fp8mixed.safetensors` | 8.66 | `image_flux2_klein_9b_kv_image_edit` |
| `text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors` | 6.70 | `image_chrono_edit_14B`, `image_wan2.1_fun_control` |
| `loras/minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors` | 1.96 | `video_minimax_h3_r2v` |
| `diffusion_models/wan2.1_fun_control_1.3B_bf16.safetensors` | 1.83 | `image_wan2.1_fun_control` |
| `clip_vision/clip_vision_h.safetensors` | 1.26 | `image_chrono_edit_14B`, `image_wan2.1_fun_control` |
| `vae/ae.safetensors` | 0.34 | `X_Flux1_A_Pose` and four stock templates |
| `vae/wan_2.1_vae.safetensors` | 0.25 | `X_JoyAI_A_Pose`, `image_chrono_edit_14B`, `image_wan2.1_fun_control` |
| `text_encoders/clip_l.safetensors` | 0.25 | `X_Flux1_A_Pose`, `image_flux_kontext_dev_basic` |

HiDream, ChronoEdit and SD3.5 are the "skip on this rig" templates from section 2. MageFlow: no MageFlow model was ever downloaded, so only the templates go
(`image_mage_flow_edit_turbo_int8` here, and `ST2_MageFlow_Edit` in `workflows/_templates` if you drop that stage).

### Stage 3: Flux.2 dev (a decision, 38.3 GB plus the base model)

`ST3_Flux_Final` uses Flux.2 dev, which section 2 rates borderline on 8 GB, while `ST4_Flux_Polish` uses the klein 4B model that fits. If you drop the dev final
(and `image_flux2`, `X_Flux_A_Pose`, `X_Flux_Polish`), these become free:

| Path | GB |
| --- | --- |
| `diffusion_models/flux2_dev_fp8mixed.safetensors` | 35.46 |
| `text_encoders/mistral_3_small_flux2_bf16.safetensors` | 35.58 |
| `loras/Flux_2-Turbo-LoRA_comfyui.safetensors` | 2.76 |

If you keep the dev final instead, still delete the bf16 Mistral: `ST3_Flux_Final` wants `mistral_3_small_flux2_fp8`, `Flux2TurboComfyv2` and `flux2-vae`, none of which are on disk.

### Keep (about 125 GB)

`diffusion_models/FireRed-Image-Edit-1.1-transformer`, `diffusion_models/qwen_image_edit_2511_fp8mixed`, `diffusion_models/minimax_h3_fl2va_pruned_int8_convrot`,
`text_encoders/qwen_2.5_vl_7b_fp8_scaled`, `text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq`, `text_encoders/qwen_3_4b`, the Qwen, FireRed and MiniMax Lightning/turbo LoRAs
(`loras/Qwen-Image-Edit-2511-Lightning-4steps-V1.0-bf16`, `loras/FireRed-Image-Edit-1.0-Lightning-8steps-v1.0`, `loras/minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16`),
`vae/qwen_image_vae`, `vae/minimax_h3_video_vae_fp16`, `vae/minimax_h3_audio_vae_fp32`, and `vae/full_encoder_small_decoder` (klein 4B base template).

### Still to download for the ST templates

- `ST4_Flux_Polish`: `diffusion_models/flux-2-klein-4b-fp8`, `vae/flux2-vae` (the encoder `qwen_3_4b` is already on disk).
- `ST3_Flux_Final` (only if kept): `text_encoders/mistral_3_small_flux2_fp8`, `loras/Flux2TurboComfyv2`, `vae/flux2-vae`.
- `ST4_Qwen_Polish`: `diffusion_models/qwen_image_edit_2511_int8_convrot`.
- `ST1_Qwen_B_Pose`: `diffusion_models/qwen_image_2.1_int8_convrot`, `text_encoders/qwen3vl_8b_int8_convrot`, `vae/qwen_image_2.1_vae_bf16`.
- `ST2_MageFlow_Edit` (only if kept): the MageFlow model, its VAE and `text_encoders/qwen3vl_4b_bf16`.

To prune a stage from PowerShell, run from the models folder, for example for stage 1:

```powershell
cd B:\Comfy-Desktop\ComfyUI-Shared\models
Remove-Item checkpoints\ltx-2.3-22b-dev-fp8.safetensors, diffusion_models\z_image_turbo_bf16.safetensors -WhatIf
```

`-WhatIf` only prints what would be removed; take it off to delete.

