# Prime flows: running the Prime more than one way, and comparing the results

The Prime (`Alpha 1 Prime`) turns an original photo into a clean head-to-toe A-pose. How well it does depends on the photo and on the engine, so a hero can have more than one **flow**, side by side. The normal flow is never replaced.

## The flows

| Flow | Incoming image | When it helps |
| --- | --- | --- |
| normal | the hero's chosen photo (`photos` in `workflows/workspaces.json`, scaled to 944x1104) | a full-length or nearly full-length photo |
| frame | `frame_944x1104\<photo>_frame_944x1104.png`: the same photo shrunk so the face has the size of a standing figure's, at the top of the canvas, the rest empty (made by `bin\originals.cmd`, see [original-photos.md](original-photos.md)) | a head-and-shoulders or waist-up photo, where the model keeps the crop |

Each flow runs through each engine, so a hero has four Prime workflows, all saved to the same output folder (a different file name prefix):

| Workflow | Engine | Flow |
| --- | --- | --- |
| `Haniya_Qwen_Alpha_1_Prime` | Qwen | normal |
| `Haniya_FireRed_Alpha_1_Prime` | FireRed | normal |
| `Haniya_Qwen_Alpha_1_Prime_Frame` | Qwen | frame |
| `Haniya_FireRed_Alpha_1_Prime_Frame` | FireRed | frame |

They carry the same prompt text. The only differences are the incoming image and, for FireRed, the identity lock below. Every later stage (Bare and on) keeps working from the Prime image you choose, as before; a flow only changes how that Prime is made.

## What is stored where

In `workflows/workspaces.json`:

- `photos` is the normal flow's photo for each hero (unchanged).
- `flows.frame.photos` is the frame flow's image for each hero. `flows` can hold more flows later (each with its own `photos`).
- Each flow workflow loads its own image. `inputs status` lists both; `inputs reset` and `inputs pull` handle each flow's image separately and never mix them with the normal photo.

To add or change a flow image: `bin\inputs.cmd set HERO --flow frame --photo haniya_image_<id>_frame_944x1104.png`. Then build the workflows that are missing with `bin\refresh.cmd HERO alpha` (Qwen) and `bin\refresh-firered.cmd HERO alpha` (FireRed), which also deploy them. `originals` makes the frame images; the 18 heroes whose chosen photo is partial have one today.

## FireRed and the face

FireRed sometimes invents a face instead of using the one in the photo, especially when the head is turned. Its Prime prompt therefore starts with an identity lock (`data/art/_templates/heroes/1_Alpha/firered-prime-face-lock.txt`, set by `engines.firered.primeFace`): the face in the reference is the result's face, a turned head is turned to face the camera as the same person, and a partial photo is continued downward to the feet. Qwen's prompt is not touched. Edit the file to tune it, then `bin\refresh-firered.cmd HERO alpha` (or `make --engine firered --match Alpha_1_Prime` and deploy for all). Remove `primeFace` from the settings to switch it off.

## Comparing in tandem

1. Pick a subject, set the same seed in the four workflows (ComfyUI keeps the seed in the workflow), and run each. Use several heroes: some with a full-length photo, some with a head-and-shoulders photo, some with a turned head.
2. Run `bin\compare-primes.cmd` (or `bin\compare-primes.cmd Haniya Draknoxa`). It finds the newest render of each of the four workflows in the ComfyUI output folders and writes `<work root>\_reports\prime_compare.png`: the original, then each variant, with a score.
3. The score is the likeness tool's face score between the render and the photo that flow started from. 0.55 and up is the same person, 0.30 to 0.45 a close look-alike, below 0.15 someone else. At the end it prints the average per variant over all heroes, which is the number to compare. `--all-renders` shows every render of each variant (to see how much a seed varies).
4. The score only measures the face. Look at the picture for the rest: whether the body is full length, the hair, the clothing, the pose.

A render made before a hero's photo changed (a re-paired angel) scores against the new photo and comes out low or negative; run the Prime again first.

When the comparison is clear, drop what does not work: take a flow out of `flows` in the settings (its workflows stay in the repo and the workspaces until you delete them), and switch off the FireRed lock the same way.
