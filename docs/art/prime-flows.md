# Prime inputs and comparisons

The Prime (`Alpha 1 Prime`) turns a hero's chosen source photo into a clean,
head-to-toe A-pose. The currently configured input is the hero's original,
scaled to 944x1104 and stored in `workspaces.json` under `photos`.

**Oct 22 review:** this guide describes installed paths. The
[manual migration plan](../plans/2026-10-22-manual-prompts-to-art-library.md)
owns the future `0_Edit` and revised Prime/Bare approach. It retires `1b` only
after replacements pass and leaves `2b` unchanged. No new prompt order,
input-role change or experiment removal was applied during plan reconciliation.

## Current Prime path

| Workflow | Engine | Input |
| --- | --- | --- |
| `Hero_Qwen_Alpha_1_Prime` | Qwen | the hero's chosen scaled photo |
| `Hero_FireRed_Alpha_1_Prime` | FireRed | the hero's chosen scaled photo, with the identity lock below |

The normal Prime path is used for full-length and partial-body source photos.
The prompt asks the model to continue a partial image into a full figure; if a
source is not suitable, choose another photo. No partial-body frame is made or
configured. A `chest_944x1104` crop is only a future experiment and is not
implemented.

FireRed sometimes invents a face instead of using the one in the photo,
especially when the head is turned. Its Prime prompt therefore starts with an
identity lock (`data/art/_templates/heroes/1_Alpha/firered-prime-face-lock.txt`,
set by `engines.firered.primeFace`).

Edit the file to tune it, then `bin\refresh-firered.cmd HERO alpha` (or
`make --engine firered --match Alpha_1_Prime` and deploy for all). Remove
`primeFace` from the settings to switch it off.

## Comparing Prime renders

1. Run the same hero through Qwen and FireRed. Use the same seed if comparing
   engine behavior; ComfyUI keeps the seed in each workflow.
2. Run `bin\compare-primes.cmd` (or
   `bin\compare-primes.cmd Haniya Draknoxa`). It finds the newest render of
   each configured Prime workflow and writes
   `<work root>\_reports\comparisons\primes\prime_compare.png`.
3. The score is the likeness tool's face score between each render and the
   photo that workflow started from. At the end it prints the average per
   variant over all heroes.
4. The score only measures the face. Look at the picture for full-body
   framing, hair, clothing and pose.

Use `--all-renders` to show every render of each variant. To include the
first-shot experiments, use `bin\compare-primes.cmd --shots all`; P2 is the
neutral base layer and P3 is the bare figure. See
[prompt context](prompt-migration-context.md) for the original rationale.
These installed comparison commands remain available, but another old
P2/P3 winner selection is not a prerequisite to reviewing the manual batch.

## Retired frame flow

The partial-body frame flow was retired on Oct 19 after testing. Its
`frame_944x1104` image generation, Prime input configuration, and generated
workflow variants have been removed from active processing. Existing images
and workflow copies were archived, not deleted. The history and execution
record are in
[library retirement evidence](library-reconciliation-context.md);
[upkeep U1](../plans/2026-10-22-library-upkeep.md) owns the separate possible
chest-crop preview.
