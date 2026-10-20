# Dual-input thoughts (external reference, not approved design)

An outside write-up of a two-image input for the Prime (a bare bust plus a reference), kept as written. Its frame-flow assumptions were retired with the Prime frame experiment on Oct 19; no frame-derived input is active. The optional dual-image face-pass idea is tracked in [the Oct 11 plan](../plans/2026-10-11-tidy-junk-organise.md). The mannequin and 512x768 proposals were not adopted.

## Executive Summary
Generating full-body character plates directly from raw photo inputs forces diffusion models to distribute their latent pixel budget across the entire figure. At standard generation resolutions (512x768), the face and eyes occupy less than 100x100 pixels, leading to plastic skin, flat cartoon irises, and blurred facial
features. Conversely, attempting to outpaint a full-body character from a tight headshot without constraints causes severe lower-body hallucination and inconsistent anatomy across seeds.

This specification establishes a **Reverse-Anchor Dual-Input Pipeline**. By decoupling **Identity/Cosmetics** from **Skeletal/Anatomical Architecture**, we resolve macro facial features first, then synthesize them onto standardized body mannequins.

---

## 1. System Architecture Diagram

    [ Raw Candidate Photo ]
               │
               ▼
    [ Step 1: Crop & Scale Headshot ]
               │
               ▼
    [ Step 2: Refine Master Head/Bust Plate ] ─────────────┐
       • Lock facial bone structure                        │ (Identity, Eyes,
       • Polish subdued violet irises & radial fibers      │  Hair, Melanin,
       • Establish hair cut/color & lip finish             │  Complexion)
                                                           │
    [ Standardized Body Archetype Library ] ───────────────┼──────────────┐
       • Neutral gray clay mannequins (No hair/face)       │              │
       • Pre-locked bone lengths, build & muscularity      │ (Skeletal    │
                                                           │  Geometry)   │
                                                           ▼              ▼
                                               [ Step 3: Synthesis Pass ]
                                                  • Condition on Head (Identity)
                                                  • Condition on Body (Structure)
                                                           │
                                                           ▼
                                               [ Clean Base A-Pose Plate ]
                                               (Ready for Wardrobe/Action Passes)

---

## 2. Core Pipeline Stages

### Stage 1: Master Head & Bust Refiner
Crop the raw source photo from the mid-chest/collarbone to the crown of the head and scale to 512x768. This allocates 100% of the model’s sampling capacity to facial optics.

* **Macro Eye Focus:** Explicitly targets biological ocular structures (radial collagen fibers, dark charcoal limbal rings, wet corneal catchlights) rather than flat color fills.
* **Hair Architecture:** Locks the hairline, framing bang length, and tonal color (obsidian-black with subtle plum/espresso micro-babylights) without risking unwanted bleaching or silver streaks.
* **Global Palette Master:** Establishes the ground-truth skin tone, undertones, and specular highlights that will later flood the entire figure.

#### Stage 1 Master Prompt Template
> Macro beauty portrait of the character from the reference image, cropped closely from mid-chest and collarbones to the top of the head against a seamless dark studio backdrop.
>
> Maintain exact facial bone structure, facial identity, skin tone, and hairstyle from the reference plate.
>
> Wardrobe visible at the bottom of the frame strictly matches the reference: the upper cups and sterling silver filigree trim of the midnight-violet plate armor top, accented with inlaid polished amethyst stones resting along the collarbones and upper chest.
>
> Facial features are rendered with razor-sharp macro lens fidelity:
> - Eyes: subdued deep violet-indigo irises with intricate radial collagen fibers, delicate iris crypts, defined charcoal limbal rings, and a sharp softbox corneal catchlight.
> - Lashes and Brows: individually defined, dark feathery eyelashes with natural separation, finely groomed arched dark eyebrows.
> - Lips: subtle natural berry-tinted satin lips with soft, realistic vertical lip lines, resting in a relaxed, confident composure.
> - Hair: rich obsidian-black hair with subtle plum and espresso micro-babylights, rendered with fine strand separation and realistic volume framing the face and shoulders exactly as in the reference.
>
> Shot on an 85mm prime portrait lens, f/2.0, softbox key lighting with subtle rim light defining the jawline and hair silhouette, crisp optical focus on the irises, high-end character avatar asset.

---

### Stage 2: Structural Body Mannequin Library
To prevent the model from guessing leg lengths, hip widths, and torso mass during full-body generation, maintain a shared asset library of **featureless clay mannequins**:

* **Visual Properties:** Monochrome neutral gray or beige, completely bald, featureless face, standing in a standardized studio A-pose on a neutral backdrop.
* **Color Rule:** Mannequins must contain **zero painted skin tones**. Neutral gray signals to the vision encoder that the plate represents pure spatial volume, forcing the model to inherit 100% of the skin complexion from the Stage 1 Headshot.
* **Core Archetypes:**
  1. *Athletic / Warrior:* Broad shoulder girdle, defined clavicles, visible abdominal wall separation, dense quads.
  2. *Lithe / Ethereal:* Tall statuesque frame, elongated limbs, narrow ribcage, graceful taper.
  3. *Curvaceous / Heavy Silhouette:* Substantial hourglass taper, wider hip shelf, pronounced bust line.

---

### Stage 3: Dual-Input Synthesis (Base A-Pose Plate)
Using ComfyUI, merge the two reference inputs into a unified, clean A-pose:
1. **Identity Conditioning:** The Master Headshot drives facial likeness, eyes, hair, and overall skin complexion.
2. **Structural Conditioning:** The Neutral Mannequin (via secondary image conditioning, ControlNet Depth, or OpenPose) locks the limb positions and physical build.
3. **Apparel Target:** Render the character in a minimal, neutral matte studio two-piece athletic set and open-toed heels.

> **Rationale:** Keeping the torso, midriff, and limbs bare at this stage prevents "wardrobe ghosting." Downstream action prompts can generate ornate midnight-violet plate armor, filigree, or spell effects onto a clean anatomical surface without fighting preexisting hemlines or armor seams.

#### Stage 3 Synthesis Prompt Template
> Full-body standing A-pose character concept plate on a seamless solid studio backdrop.
>
> The character's facial likeness, facial bone structure, subdued deep violet-indigo eyes, obsidian-black hair with subtle plum babylights, and natural fair skin tone strictly match the master headshot reference image.
>
> Her physical build, stance width, limb length, and anatomical proportions strictly follow the body mannequin reference plate.
>
> She wears a minimal, neutral matte studio two-piece athletic set with clean edges, leaving her torso, midriff, arms, and legs completely bare. On her feet are minimal neutral studio high-heel sandals firmly planted on the floor plane.
>
> High-key diffused commercial studio softbox lighting, perfectly balanced fill with zero harsh drop shadows, ultra-sharp edge definition around all limbs, clean master anatomical base plate ready for armor equipping.

---

## 3. Downstream Deliverables & Action Passes

Once the clean Base A-Pose is locked, subsequent card illustrations are derived without structural drift:

| Deliverable | Source Anchor | Method | Production Target |
| :--- | :--- | :--- | :--- |
| **Card Avatar / Dialogue Portrait** | Stage 1 Master Headshot | Direct crop + FaceDetailer (`denoise: 0.30`) | Microscopic iris fibers, crisp eyelashes, sharp limbal borders. |
| **Dynamic Action Cards** | Stage 3 Base A-Pose | Qwen/FireRed image-to-image with pose prompt | Dynamic stances while preserving silhouette, armor layout, and palette. |
| **Photorealistic Texture Polish** | Stage 3 or Action Pass | FLUX.1 [dev] GGUF pass (`denoise: 0.30–0.34`) | Natural skin pores, authentic specular falloff, physical light scatter. |

### Universal Action Shot Prompt Template
> Dynamic full-body game card illustration of the sorceress from the reference image, captured mid-action in an expressive dynamic stance.
>
> Strict fidelity to the reference plate's facial identity, athletic silhouette, and wardrobe: ornate midnight-violet lacquered plate and sterling silver filigree bikini armor with open-toed high heel footwear.
>
> Palette and features are locked to the reference:
> - Eyes: Subdued deep violet-indigo irises with crisp dark limbal rings, intense focused gaze.
> - Hair: Obsidian-black hair with subtle plum and espresso babylights, reacting dynamically to motion with loose strands catching the air, maintaining its cut and volume from the reference.
> - Skin & Lips: Natural fair skin tone with soft natural lip tint.
>
> Dramatic studio key lighting, subtle atmospheric crossbreeze, clean neutral background plane, high dynamic range, sharp character clarity.

---

## 4. Model Selection & Compute Allocation Matrix

| Stage | Target Model Mode | Step Count | Target Resolution | Primary Objective |
| :--- | :--- | :--- | :--- | :--- |
| **Headshot Refinement** | Non-Turbo (Full Steps) | 25–30 | 512x768 (Cropped) | Macro eye depth, iris crypts, skin undertone. |
| **Body Mannequin Library** | Turbo Mode | 6–8 | 512x768 | Fast anatomical proportion library generation. |
| **A-Pose Synthesis** | Turbo Mode | 8–10 | 512x768 | Clean, artifact-free baseline canvas. |
| **Action Shot Gen** | Turbo (Audition) / Full Step (Final) | 8–10 / 25 | 512x768 | Silhouette and kinetic composition. |
| **Surface Detail Pass** | FLUX.1 [dev] GGUF (`denoise: 0.32`) | 20–25 | 512x768 | Optical skin pores, specular physics, gem refractions. |

---

## 5. Actionable Verification & Execution Checklist

1. [ ] **Establish Mannequin Repository:** Generate and save 3 neutral gray, hairless, featureless A-pose mannequin plates (Athletic, Lithe, Curvaceous) at 512x768 into `Templates/Mannequins/`.
2. [ ] **Process Candidate Headshot:** Crop candidate image to collarbones-up, scale to 512x768, and execute the Stage 1 refiner prompt. Inspect at 100% zoom to verify round pupils, distinct limbal rings, and zero unwanted bleached hair streaks.
3. [ ] **Run Dual-Input Synthesis:** Execute Stage 3 synthesis combining the approved Headshot with the designated Mannequin. Inspect the jawline-to-neck boundary at 100% zoom to confirm uniform skin tone and seamless edge alignment.
4. [ ] **Archive Master A-Poses:** Store approved full-body bare-canvas plates into `Templates/[HeroName]/` for downstream armor equipping and action card generation.
