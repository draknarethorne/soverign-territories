# 03: bounded secondary evidence, models and cache behavior

**Status:** holding (context diagnostic only; full stage incomplete)

**Resume gate:** record isolated face/reference/member results from
[02](02_identity_reformation.md), then select the bounded OST4
implementation/experiment in the
[spine](../2026-11-05-priority-reset.md#execution-spine).
No automatic model download or private-photo upload.

**Authority:** main
[series safeguards](../2026-11-09-likeness-process-reassessment.md#series-evidence-and-safeguards),
[performance experiment](../2026-11-09-likeness-process-reassessment.md#performance-experiment),
[apparent-age hypothesis](../2026-11-09-likeness-process-reassessment.md#apparent-age-consistency-hypothesis),
Q&A18,31,35,37-38,40 and
[local model disposition](../2026-11-09-likeness-process-reassessment.md#model-decision-assessed-option-not-a-hidden-prerequisite).

## Outcome and current limitation

**Nov 13 selection and current evidence boundary:** after face/reference
repair, the user selects bounded secondary/contextual tests before asking
them to resolve individual cases when face-only remains inadequate.
This does not activate automatic fusion or a full-library extraction.
The [A17 iteration gate](../2026-11-09-likeness-process-reassessment.md#iteration-acceptance-checklist)
owns the conditional check; the spine retains execution ownership.
The maintained `likeness-diagnostics.cmd --check` was run read-only against
`category-diagnostics-03`: it exits2 because its bound historical
`postrun-review-preview11\run.json` no longer exists after the clean reset.
Its old AUC/cold/warm figures remain historical, not current-image evidence.
Do not rewrite receipts or bypass bindings to make that old diagnostic pass.
Use current corrected face/multi-view decisions and a newly content-bound
bounded case selection for any new cue comparison. No descriptor extraction,
model download or fusion was performed at this checkpoint.

**Nov 13 bounded current-byte follow-through:** although the old transitive
receipt cannot pass as a complete current experiment, its24 descriptor source
SHA256 values all match current prepared inputs exactly. Parent verified
each current image's bytes plus historical `descriptors.json`/`cues.json`
output hashes, then recomputed current centered SFace pair scores alongside
the unchanged local context vectors on16 inherited development controls
(six same, six different, four uncertain). AUC is0.833333 face,
0.805556 below-face and1.000000 head-context. The inherited sample is not
reserved/blind evidence; head-context includes the face, not independent
hair. Below-face same/different ranges overlap0.6387-0.9687 versus
0.4722-0.7885, so it cannot safely override ambiguous face evidence.
Head-context separates this tiny familiar sample but has not demonstrated
general recovery or false-join safety. Zero new extractions/model calls,
zero identity changes, zero library writes. The failed historical command
remains failed; no old receipt was rewritten or bypassed for acceptance.
Disposition: do not activate uncalibrated fusion to force cast cores or
reduce fragmentation. Current hard cases require bounded broader independent
cue/control evaluation if face-geometry repairs remain insufficient.

Supply measured corroboration/conflict evidence where face-only behavior
cannot adequately recover same-person appearances or separate lookalikes.
When validated, this may automate non-core association, not merely create
another questionnaire. Appearance status still requires qualified person
evidence; shared outfit or a weak score does not supply it.

Existing RA4/RA7 below-face OpenCLIP comparisons are a **diagnostic**, not
series detection, hair evidence, calibrated identity fusion or completed
caching. Helpful human context and overlapping same/different context
scores do not validate an automatic decision threshold.

## Implementation and experiment sequence

1. Select unresolved members/appearance hypotheses and misleading controls
   from02 with all relevant identity competitors. Record image, pair, time,
   memory and extraction caps before work. Cap failure is incomplete scope,
   not a non-match. Avoid an all-library outfit pair matrix.
2. Define explicit observable cue records: outfit/series, hair and optional
   appearance-consistency flags, with crop geometry, content, model/recipe,
   quality, visibility and missingness. No physique/bust classifier, exact
   age or biological-family inference.
3. Start with an available local descriptor and suitable bounded crops.
   Test distinctive clothing/garment details, scene/lighting and reliable
   sequence evidence. Test hair from a suitable head-region crop, not an
   aligned face crop that omits it. Background/clothing agreement alone
   cannot establish a person; changed outfit alone cannot split them.
4. Decode each unchanged selected image once where practical and cache by
   content, geometry, preprocessing and exact model/recipe. Membership-only
   changes reuse descriptors; changed references/policy invalidate dependent
   **decisions**. Warm unchanged reruns extract zero new descriptors while
   preserving source checks. Report cold/warm cost and invalidations.
5. Compare face-only, face+series/outfit, added hair and separately justified
   appearance-consistency variants on identical development/reserved cases.
   Isolate correlated cues and each cue's damage/no-gain as well as gain.
   Several views from one session may be useful; they are not several
   independent identity proofs just because several cues agree.
6. Feed qualified corroboration and explicit conflict/missingness back to
   02's member/non-core decision record. Strong contradictory person
   evidence cannot be overridden by styling or a fluent model explanation.
   No recursive tentative-member admission or implicit core promotion.

## Model disposition, not an invisible dependency

### Bounded existing-CLIP region and cache ablation

The latest unattended continuation selects an existing-descriptor
comparison, not another unmotivated model download. Maintained launcher
[`likeness-diagnostics.cmd`](../../../bin/likeness-diagnostics.cmd), menu LG,
publishes this alongside
[own-core/category diagnostics](02_identity_reformation.md#own-core-retention-and-category-diagnostics)
in `category-diagnostics-03`.

The deterministic selection caps six same, six different and six uncertain
returned exact-pair labels, two pairs per label/folder combination, and
24 unique images. The executed sample is 16 pairs: six same, six different,
four uncertain. These are reused development controls, not independent
acceptance or AI-created human labels. Labels select/evaluate the sample;
they never enter descriptor extraction or identity decisions.

Two regions use the existing bound local OpenCLIP ViT-B-32 checkpoint:
face-excluding below-face context and a broader head-context crop.
**Head-context includes the face**; its score cannot be described as
isolated hair evidence or independent face corroboration. Geometry,
visibility/missingness, source content, model hash and preprocessing/runtime
versions bind each feature. No physique/age/kinship inference or score
fusion is implemented.

| Development measurement | Executed result |
| --- | --- |
| Face-only same-versus-different ranking AUC | `.833333` |
| Below-face ranking AUC | `.805556` |
| Head-context ranking AUC | `1.000000` |
| Cold decode/extraction | 24 originals decoded once; 48 features |
| Persistent JSON cache, reverse image order | Exact vector parity; zero decodes/extractions |
| Identity decisions / library writes | Zero / zero |

AUC compares the six same scores against the six different scores; uncertain
pairs are excluded and missing scores stay unavailable. It is **not**
membership accuracy, a join probability or reserved acceptance. Region
rankings are not directly calibrated to ArcFace thresholds. Final suffix03
cold extraction was 9.413s; warm reuse 0.571s including source checks.
The immutable receipt/cues record exact timings; CPU/four
threads, no background service or new model installation.

**Disposition:** head-context is a promising development signal worth
testing on broader hard controls; it is not demonstrated independent
identity recovery. Below-face does not beat face-only here and is not
selected for automatic fusion. SmolVLM remains coarse review assistance.
No classifier, new admission threshold or family/appearance verdict is
enabled. Missing steps remain explicit: separate hair/series evidence,
independent allocation, mixed/lookalike controls, calibrated fusion,
false-join/recovery/cost comparison and lifecycle integration.

The viewer shows all 48 inline crops with original filename links. Source,
model or crop changes invalidate reuse; the focused tests exercise those
invalidations and persistent serialization parity. Apply/check revalidates
receipt/transitive source hashes without calling the model again.

### Nov 10 local observer selected for feasibility

The user's continuation authorizes local setup and bounded trials, not a
private-photo upload or use of AI output as human confirmation.
[`likeness-observe.cmd`](../../../bin/likeness-observe.cmd) now previews an
optional local-only observation experiment. Setup uses a separate
system-site-packages environment under ignored `tmp\local-vlm\venv`;
ordinary library packages and CPU PyTorch are not replaced.

Selected public weights:
[HuggingFaceTB/SmolVLM-500M-Instruct](https://huggingface.co/HuggingFaceTB/SmolVLM-500M-Instruct),
Apache-2.0, pinned revision
`a7da5b986cb59b408707209984f360a5f4ad7e47`. The model card describes
approximately 1.23GB GPU memory for one image. This machine has a 6GB RTX
3050, but its maintained PyTorch is CPU-only; the test deliberately uses
CPU/four threads, with approximately 1GB of downloaded weights. No CUDA
replacement, background server or remote inference is needed.
The [optional requirements](../../../tools/art/local_observer_requirements.txt)
pin Transformers 4.57.6 inside that isolated runtime.

```bat
cmd /c bin\likeness-observe.cmd --setup --dry-run
cmd /c bin\likeness-observe.cmd --setup --apply
cmd /c bin\likeness-observe.cmd ^
 --source "ABS-ASSESSED-REFORMATION-REPORT" ^
 --out "ABS-NEW-REPORT-IN-reports\likeness-reassessment" --dry-run
```

Apply uses up to six content-bound, face-excluding crops, no identity names
or scores in prompts, deterministic generation capped at 72 tokens/image,
and reverse invocation order with independent single-image prompts.
The twelve-call maximum and 600-second worker timeout bound inference.
Model loading is offline, local-files-only, with remote code disabled.
Record exact runtime/model/source/crop hashes, raw observations,
missingness, order consistency and timing. Repeat apply verifies without
inference; `--check` verifies sources, crops, outputs and model hashes.
The HTML includes inline crops and original filename links.

Initial executed feasibility evidence (`local-cue-observer-01`): six crops,
twelve local calls in 303.036s on CPU, all six descriptions identical under
reverse invocation order, approximately 5.6GiB observed process working
set. This is measured warm/runtime cost, not the model card's GPU estimate.
The installed public weights occupy approximately 1GB; no private image
leaves the machine. The final rerun uses the same pinned weights with
transitive report/source bindings and current non-deprecated Transformers
entry points.

Final verified publication: `local-cue-observer-02`, twelve calls in
307.945s, six of six reverse-order observations identical, zero identity
decisions/library writes. Preview/apply/repeat/check pass; unchanged repeat
does not infer again. Its source bindings include the candidate outputs,
upstream saved inputs/code, selected originals and exact model files rather
than trusting an unchanged receipt alone. Browser checks confirm six inline
images, six original filename links, no broken images and no 390px overflow.

```bat
cmd /c bin\likeness-observe.cmd ^
 --source "C:\Soverign-Territories\soverign-territories\reports\likeness-reassessment\membership-reassessment-05" ^
 --out "C:\Soverign-Territories\soverign-territories\reports\likeness-reassessment\local-cue-observer-02" ^
 --check
```

**Assistant visual assessment, not human feedback:** the ambiguous sample
has visibly different patterned versus sports clothing; that difference
cannot establish different people. The supported sample shares a burgundy
palette but differs in garment texture/construction; similar colour is
insufficient series or identity evidence. One released sample has no useful
garment cues; preserve missingness rather than inventing a clothing match.
The model's coarse "long red dress" description omits observable
construction/length details; deterministic text is not calibrated accuracy.
These checks do not modify any existing same/different labels.

**Disposition:** locally feasible for coarse review assistance, but no
demonstrated identity recovery gain; do not activate matching fusion or
whole-library extraction. Three development pairs do not cover the
same-outfit/different-person hard controls or reserved acceptance cases.
Use descriptors and explicit visibility/series evidence in the next
selected experiment before scaling a generative observer. No unrequested
larger-model sweep is justified by repeatable prose.

This is a feasibility test, not a calibrated cue fusion rule or completed
series/hair detection. Human review remains explicitly not performed.
Descriptions may hallucinate; no observation alone supplies same-person,
appearance-membership or family evidence. A measured no-gain/insufficient
disposition is a legitimate result, not a reason to feed prose into identity
decisions. Qwen/InternVL remain separately assessed alternatives, not
silently installed follow-on dependencies.

| Option already recorded in the main plan | State and permitted use |
| --- | --- |
| Existing local OpenCLIP | Available diagnostic baseline; not an identity model |
| SmolVLM-500M (Nov 10 selected trial) | Installed in the isolated optional runtime; six-crop local observation feasibility executed, diagnostic-only/no demonstrated identity gain |
| DINOv2 / OSNet | Research options; no verified gallery benefit or installed weights assumed |
| Qwen3-VL / InternVL | Optional local observation experiment; not selected/installed or identity/kinship authority |

For any proposed new model, name exact weights/license, runtime/hardware/
memory feasibility, dependencies, structured observations, cost cap and
evaluation decision before requesting downloads. Do not imply this phase
must wait for a VLM, or that a VLM has already been used.

A VLM test, if selected, hides names/desired matches, binds exact image
regions, represents unavailable observations, tests swapped image order,
and includes similar clothes/backgrounds on different people. Confidence
text is not calibrated probability or independent face support.

## Tests, exit and defer gate

Test same person across outfits, different people sharing outfit/hair,
cropped/occluded regions, ambiguous/multiple people, generated/altered
series, duplicate views, scene bridges, contradictory faces and missing
metadata. Confirm cache key invalidation and zero unchanged extraction.

Exit is a measured integrate/revise/no-gain/defer disposition for each cue
and selected recipe, with added recovery/false-join/abstention and cost
compared to the same face-only state. Secondary cues are a conditional
**pre-rebase prerequisite** when face-only cannot meet the outcome; they
cannot simply be called optional and forgotten. If no available cue helps,
surface that limitation and retain uncertainty rather than inventing a
family classification or claiming all splits are repaired.
