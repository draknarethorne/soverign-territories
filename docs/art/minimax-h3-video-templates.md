# MiniMax H3 video templates: what we have, what ComfyUI ships now, and what to do

Analysis of Oct 9, 2026. Sources: the former ST6 video template; ComfyUI's then-current templates `video_minimax_h3_i2v` (the "iv2" saved to a local ComfyUI workspace) and `video_minimax_h3_r2v` (the "rv2"); and the node sources `nodes_minimax_h3.py` and `nodes_resolution.py`.

## Which is which

| Template | Task | Core node | Model and LoRA | Images in |
| --- | --- | --- | --- | --- |
| **Ours, ST6** | Image to video (first and last frame) | `MiniMaxH3ImageToVideo`, in a subgraph | `minimax_h3_fl2va_pruned_int8_convrot`, turbo LoRA 8 steps | first frame (we feed one) |
| **iv2** (`video_minimax_h3_i2v`) | the same task, newer version of the template | the same node, in a subgraph | the same model and LoRA, but the video VAE is `minimax_h3_video_vae_int8_convrot` | first frame, optional last frame |
| **rv2** (`video_minimax_h3_r2v`) | Reference to video | `MiniMaxH3ReferenceToVideo`, flat, no subgraph | `minimax_h3_ref2va_pruned_int8_convrot`, turbo LoRA 4 steps v0.1 | several reference images (2 in the template) |

So our ST6 is not the rv2: it is the older image-to-video template. The iv2 is its newer version. The rv2 is a different task and is interesting for something else (below).

## iv2 against ST6, line by line

| Aspect | ST6 (ours) | iv2 (new) | Effect |
| --- | --- | --- | --- |
| Size control | `width` and `height` typed in | a `ResolutionSelector` node (aspect ratio, megapixels, multiple of 32) feeds width and height | friendlier, but see the limits below |
| Default size | 640x960 (2:3) | 1344x768 (16:9, "official 768p") | iv2 defaults to landscape |
| Default length | 6 s | 5 s | |
| Turbo LoRA | on | off | |
| Video VAE | `minimax_h3_video_vae_fp16` (installed) | `minimax_h3_video_vae_int8_convrot` (not in your models folder) | download needed to run iv2 unchanged |
| Helper nodes | none | `ImageScaleToTotalPixels` (0.9 MP, step 32) and `GetImageSize`, **not connected** | could drive the size from the input image (see below) |
| Notes | none | three notes: what H3 is, model links, a size table | documentation only |
| Outer node | all promoted widgets are inputs (prompt, seed, models) | a short list of inputs (frames, width, height, seconds, turbo, steps) | cleaner for hand use |
| `make` compatibility | `set_video` sets `width`, `height`, `value_1` (seconds) and `value` (turbo) by name | the same names exist, but `width` and `height` are linked from the selector, so values typed into them are ignored | `make` would have to set the selector instead |

## What the node source says (this is what matters for our stills)

- `MiniMaxH3ImageToVideo` takes `width` and `height` in **steps of 32**. Our stills are 944x1104, which are multiples of 16 but not of 32 (29.5 and 34.5 steps), so a video cannot use the still's size unchanged.
- The **first frame is stretched to the canvas** (`_resize(first_frame, width, height, "disabled")`, the comment says "plain stretch"). The last frame, by contrast, is cover-cropped. So the aspect of the video must match the first frame, or the picture is distorted.
- Today's default 640x960 is 2:3 (0.667) and the stills are 0.855, so the first frame is squeezed horizontally by about 22%. This is the biggest finding.
- `ResolutionSelector` offers 1:1, 2:3, 3:2, 3:4, 4:3, 9:16, 16:9 and 21:9. There is no 0.855 option; the closest portrait choices are 3:4 (0.75) and 2:3, so it distorts by 12% at best.
- `length` is a frame count at 24 fps on a 17k+5 grid (5, 22, 39 ... 124 is about 5 s). The note says the trained range is about 124 to 362 frames, **5 to 15 s**; shorter is untested. Our cards run 7 to 9 s (inside the range) and the template default is 6 s.
- The dangling `ImageScaleToTotalPixels` (0.9 MP, step 32) into `GetImageSize` is exactly what is needed to read a width and height at multiples of 32 from the image. Connected (LoadImage to scale to size to width and height), a 944x1104 still comes out at 896x1056 (0.848) at the template's 0.9 MP, or 928x1088 (0.853) at 0.95, within 1% of its aspect, and any other still follows automatically. (ComfyUI counts a megapixel as 1024 x 1024 pixels, which these figures use.)

Candidate sizes that keep the still's aspect (all multiples of 32):

| Size | Aspect | Megapixels | Note |
| --- | --- | --- | --- |
| 864x1024 | 0.844 | 0.88 | smallest, fastest |
| 896x1056 | 0.848 | 0.95 | what the auto-size chain gives at 0.9 MP |
| 928x1088 | 0.853 | 1.01 | closest to 0.855, about the "official 768p" pixel count (1344x768 = 1.03 MP) |
| 960x1120 | 0.857 | 1.08 | largest of the four |

## What we built (Oct 9, you delegated V1 to V5; the clips are for Facebook reels)

Facebook reels are **9:16** (1080x1920 at best), which the 0.855 stills are not, so one size cannot serve both a reel and a clip that keeps the whole picture. There are two templates, built from the earlier project template by `tools/workflows/video_templates.py`, which also checks every link. The current masters are listed in [`workflows/README.md`](../../workflows/README.md#stage-templates).

| Template | Canvas | How | When |
| --- | --- | --- | --- |
| `ST6_MiniMax_Reel` (default) | 640x1152 (9:16, 0.7 MP, steps of 32) | a Resolution Selector sets width and height; a Scale Image node cover-crops the still to that canvas (centre), so nothing is stretched | Facebook reels and feeds |
| `ST6_MiniMax_Match` | 928x1088 for a 944x1104 still | Scale Image to Total Pixels (lanczos, 0.95 MP, step 32) feeds the first frame and, through Get Image Size, the width and height | cut-scenes, the title and key-art clips, anything that keeps the whole picture |

| ID | Decision |
| --- | --- |
| V1 | Option C in spirit, our template as the base (the iv2's subgraph is the same); the helper chain is used for `Match`, the selector for `Reel` |
| V2 | 0.95 MP for `Match` (928x1088); 0.7 MP for `Reel` (640x1152, about the size the 8-step turbo model handles comfortably; upscale for posting) |
| V3 | 8 s default; the card's own length (the sum of its actions, 7 to 9 s) replaces it, never below 5 s |
| V4 | Turbo on in both (this machine), off for a slower, better run |
| V5 | No int8 VAE download needed: both templates keep the installed fp16 video VAE |

A card chooses with `"format": "reel" | "match"` (default `reel`); the prompt header shows `Format:`. The card `size` field is retired. Caveat: a 9:16 crop of a 944x1104 still drops about a third of the width (the centre is kept), so for reels frame the hero centrally, or later outpaint the stills to 9:16.

## Options considered

| Option | What it is | Good | Costs |
| --- | --- | --- | --- |
| A | Keep ST6, add the auto-size chain (LoadImage, scale to total pixels with step 32, get size, width and height) | one change, size follows every still, no distortion | keeps the older template and VAE |
| B | Adopt iv2 as it is and teach `make` to set the selector | the shipped template, notes and exposure | selector has no 0.855, so distortion stays; needs the int8 VAE |
| C | Adopt iv2 as the new ST6 base, delete the `ResolutionSelector`, connect the helper chain, keep our turbo and defaults | friendly outer node and the right size for our stills | one template rebuild and a `set_video` change |

`make` no longer writes width and height (the template's size nodes decide, and a wired input is left alone); it still sets the seconds (the card's total) and turbo.
## The rv2 and the multi-image phase

The reference-to-video template takes several reference images (two in the sample) and a prompt, with its own model (`ref2va`, installed) and a 4-step turbo LoRA (v0.1, installed). That is the "background, bare skin, armor and weapon as separate images" idea of the next art phase (plan Phase 3.8), done directly in video. Worth a test later, after the still pipeline is settled; nothing to build now.
