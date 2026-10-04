# Output QA Checklist — What to Watch For

A review table of every prompt improvement we made, so when you render you can confirm each one is
landing. If something's off, the **Lever** column says what to adjust. Companion to
[`prompt-pattern.md`](prompt-pattern.md).

## Identity & consistency

| Improvement | Watch for in the render | Lever if off |
| --- | --- | --- |
| Reference fidelity line | Face, body, and hair match the incoming image | Lower denoise; keep the fidelity line |
| **Eye persistence lock** | Eyes stay **violet** (don't drift to blue/brown) | Negative already has `recolored/blue/green/brown eyes`; lower denoise |
| **Bust persistence lock** | Bust **not shrunk** when armor is applied | Negative has `flat chest, small bust`; restate figure last |
| Skin set once (A-Pose) | Consistent **warm tan** across all stages | Set only at A-Pose; don't re-specify downstream |
| Figure phrasing | Consistent **full hourglass** silhouette | Restate figure line near the end |

## Makeup & grooming (the "catwalk makeup" ladder)

| Improvement | Watch for | Lever if off |
| --- | --- | --- |
| **A-Pose bare-face reset** | Heavy source makeup **normalized to natural**; fresh face | Strengthen "reset any heavy makeup"; lower denoise |
| Eyeshadow per outfit | **Soft shimmer** on light looks, **smoky amethyst** on dark armor | Adjust the `Makeup:` line in that file |
| Lipstick (light default) | **Light Violet** lips — except Bone/Raven/Iridescent/Elegant/Gown (Deep) and Kiss (Red) | Change the lipstick word in that file |
| **Toenails** | Painted toenails visible in **open-toed heels** | "fingernails and toenails"; already added |
| Blush + brows | Soft natural blush, groomed brows at base | A-Pose makeup line |

## Expression & pose

| Improvement | Watch for | Lever if off |
| --- | --- | --- |
| **Mouth state named** | Matches purpose: parted (editorial), softly together (Gown/regal), hint of teeth (High) | Set the mouth words in that file |
| **Body/head/gaze orientation** | Real angles (3/4, over-shoulder, profile) — **not flat forward** | Name concrete angles; **drop "face focused on camera"** |
| Forward-lock removed | Turned-head poses actually turn | Remove any "Face remains focused on camera" line |
| Glamour line | Long neck, shoulders back, contrapposto, pointed toes | Add a Glamour-boosters phrase |

## Outfit & scene

| Improvement | Watch for | Lever if off |
| --- | --- | --- |
| Background split | Clean **cream studio backdrop** (baseline stages) | Keep Background on its own line |
| Wardrobe slots | Every piece present (torso, arms, jewelry, back, legs, weapon) | Check the slot is filled in that file |
| Outfit movement (Gown) | Hem / slit **sways with the step** | Add a movement phrase |
| Stage-aware negatives | **No stray pauldrons** on Bikini; pauldrons **present** on Bone/Raven | Add/remove `pauldrons, shoulder armor` in the negative |

## Cleanliness (negatives)

| Improvement | Watch for | Lever if off |
| --- | --- | --- |
| Text/logo lock | **No rendered text, watermark, or logo** | Negative already has `text, wording, watermark, logo` |
| Hands | Clean hands, five fingers | Negative has `deformed hands, extra digits`; lower denoise |
| Catwalk dedup | (prompt cleanliness — removed a doubled walk block) | — |

## Pipeline / stage

| Improvement | Watch for | Lever if off |
| --- | --- | --- |
| Baseline = photoreal | Cream studio renders look like a **real photo** (not fantasy) | Keep fantasy out of baseline |
| Fantasy only at the end | Glowing eyes / necrotic glow **only** in Fantasy/Final | Move those cues to the Fantasy or Final prompt |
| Dynamism | Variety across runs | **Roll the seed**; raise denoise; lower CFG a notch |
