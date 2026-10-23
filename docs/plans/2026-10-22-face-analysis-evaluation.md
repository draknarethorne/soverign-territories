# 2026-10-22: face-analysis explanations and secondary-model evaluation

**Status:** active (Oct 20 C9 transferred; explanation and measured evaluation remain)

## Review and questions: 2026-10-22 16:26 -05:00

The complete feedback below is preserved. Explain the existing pipeline first;
do not assume an explicit hair-color or makeup weight exists. M2 requires
user-confirmed labels for the named examples. Before M3, verify actual
checkpoint/commercial usage rights and agree candidate scope; no model download,
licence assumption or raw-score averaging is approved. Any routing change
requires the separate engine gate. No answer is needed to begin M1.

## Scope

Explain the current local face-analysis pipeline from code and measured cases.
Evaluate a secondary local model only against labelled evidence and verified
checkpoint licences. This is not a threshold change or a promise that hair,
makeup, pose or expressions are explicit weighted parameters.

This is the focused home for Oct 20 C9 and the complete
`image_analysis_question.md` note. Archival is transfer, not completion.
The [engine plan](2026-10-22-likeness-engine-acceptance.md) owns routing calibration;
keep similarity evidence separate from identity truth.

## Work

- [ ] **P1 ai** M1 Trace detection, alignment/cropping, embeddings, centering,
  core construction and similarity. Explain which inputs the model sees,
  which settings are configurable, and what cannot be inferred about learned
  hair/pose/makeup sensitivity without controlled measurements.
- [ ] **P1 either** M2 Build labelled comparisons for Florence Brookfield
  versus Angelica/Sandalyn, Arwen Ames/Rhiannon Frost photo
  `7515826497811991332`, hair changes, head tilt, lip expression, makeup,
  retouching and same-shoot pose duplication. Separate image quality,
  alignment errors and model disagreement; do not use current folders as truth.
- [ ] **P2 ai** M3 Compare suitable local secondary models only after checking
  code, checkpoint and training-data usage restrictions. InsightFace MIT
  code does not grant commercial use of its non-commercial-research weights;
  AdaFace checkpoint clearance remains unresolved. Record alignment, RGB/BGR,
  performance and labelled error rates. Do not average raw cross-model cosine
  scores, silently download weights, or patch individual names/scores.
- [ ] **P2 either** M4 Recommend whether secondary checking for ambiguous
  Review/new-identity cases improves measured errors enough to justify it.
  Keep blurry-photo retirement and subjective quality choices separate;
  any routing change goes through engine approval and tests.

## Raw feedback (verbatim)

Source: `feedback/image_analysis_question.md`, Oct 22.
Words and indentation preserved; trailing line whitespace normalized in this copy.


<!-- markdownlint-disable MD013 -->
```text
Is haircolor a significant item in the face analysis?  I am noticing some images where we have a person with different color hair falling down into Potential with another photo and the closest matches are all more aligned to hair color of others than the core face - at least in my visual reviews.  Florence Brookfield shows as closest angel: sandalyn when I would have expected Angelica to be closer - since it's actually her with dark hair.  Could it be that the system is weighting hair color too heavily in the analysis?

The same goes with the face/head angle as tilted heads seem to fall out of the main gallery or even lip expressions.  Maybe that's all fine as we don't want things to automatically clutter, but I'm just wanting to know the variables that impact how the images are matched and that may help be choose better photos to even start with and avoid images where the person is leaning back, tilting head in many directions, etc...

In some cases, many images have the same head, body and neck positioning so it easily matches them with high confidence.  When the images have more actions or poses or body positions - it seems like the face checking is different.

Is it the cropping position we use for the face id or what is up.  This feeds into having a secondary type check on the face if it's not immediately a very high confidence match.  Running the secondary analysis (if we can figure out who, what and how to do that) might be a better way to handle photos that have middle confidence that either result in a Review or even fall into their own identity and not group with anyone else.

In other cases, it looks like makeup on the face is also a driver for things dropping out - or maybe it's the fact that the image was "AI brushed" and the face might be smoother looking in those images than some of the ones with just normal makeup and photo cleaning.  Like having bold red lipstick seems to drive more to a new identity and group with other bold lipstick items (especially if I have a series of images of the same person in that same bold lipstick).

I can also see that a blurry photo or that the photo quality is a driver - but that's probably ok as if it's not a clean photo and it doesn't match well and drops to a Potential, I'll just retire those since they aren't as good as I thought they were when I pulled them into the Various/gallery for processing.  So blurry is less an issue than these other observations.

Again, this is more ideation and understanding of how the face identification is working and how we can tune it or do a secondary check on it.
```
<!-- markdownlint-enable MD013 -->
