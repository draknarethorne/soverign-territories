# 2026-10-22: gallery and Review information layout

**Status:** active (feedback captured; implementation deferred while manual rename is validated)

## Scope and ownership

This plan owns presentation and information grouping across the gallery and
Review pages. Identity actions and their transaction semantics remain in the
[self-healing plan](2026-10-20-likeness-library-self-healing.md) and
[rebaseline/family plan](2026-10-21-likeness-rebaseline-and-family-naming.md).
It does not duplicate matching, calibration, family naming or production gates.
Keep closely related layout work together; split a genuinely independent
topic into its own plan with explicit links rather than expanding either
engine plan indefinitely.

## Agreed direction

- A person header is a readable summary, not one blended block of controls
  and diagnostic text.
- Separate the reference/workflow image, identity details/statistics, and
  manual actions into clearly labelled panels.
- Keep identity name, fixed cast slot and category distinct. Do not imply
  a person's recorded name is the character slot.
- Preserve overview/Review ordering and useful information consistently.
- Protection means automatic-change restrictions; explicit actions retain
  their own validation and, where appropriate, confirmation.
- Layout work is recorded now, not silently included in rename delivery.

## Work

- [ ] **P1 ai** L1 Inventory the current overview and Review person-header
  content against raw acceptance feedback. Map image, details, tags,
  diagnostics and actions into distinct panels without dropping existing
  information or duplicating its source.
- [ ] **P2 ai** L2 Implement a responsive reference-photo panel, identity
  details panel and actions panel. Align name/tags/stat order with the
  overview; stack cleanly on narrow screens and keep controls accessible.
- [ ] **P2 ai** L3 Audit photo-detail grouping and category/name repetition,
  clickable tags, history links, separators and visual hierarchy across both
  pages. Preserve scores and the distinction between evidence and actions.
- [ ] **P2 ai** L4 Validate both sort modes, filters, primary references,
  stage/cancel/export and protected-action confirmation after the layout
  changes, including narrow/wide synthetic browser checks.
- [ ] **P1 you** L5 Review the regenerated actual sandbox pages after L2-L4;
  confirm the image/details/actions separation is usable.

## Raw feedback (verbatim)

Source: `feedback/feedback_on_acceptance_testing.md`, Identity Overview Section.
The full source is retained; this excerpt does not consume its other requests.

```text
If you can visually inspect the section you'll see that the section isn't very user friendly and doesn't have all the content that is on the Gallery page about the identity.  I think we'd want it more like the following (this is not formatting, just concept info):
    - Name
    - Tags
    - Photo (workflow selected with score)

    - To the right of the picture we have another box with all the same stats as in the gallery - following the same layout and order.

So it's two boxes side by side - the photo on the left and the stats on the right.

That identity overview is like a summary card for the identity, providing a quick glance at the key information and stats without having to navigate to the Gallery page.  Use your best judgement on formatting and layout to make it clear and easy to read.
```

Source: chat, Oct 22, 2026; current clarification (verbatim).

<!-- markdownlint-disable MD013 -->
```text
I should be able to update a protected sisters, angel or any identity name - I want to rename a few sisters identity for instance Drakinsa - Sweet Beauty is actuall Amelia Morgan.  Somehow it was mis-named a while ago and I want to try to correct that and verify in the sandbox that renaming works.  There are a few others as well I can test with to see how it works in general.  I also had some feedback in general about the header section and making separate boxes for the image, details and now the actions.  Basically making that section better.  I'm sure you saw that in my feedback.  So I am just curious where everything is at right now.  We really need to address formatting of various areas and separate different types of information, functionality and such into their own sections so it's not all one blended big blob of data.  We don't need to take immediate action, but want to ensure we have those things ironed out and into a plan somewhere.  AND if the plans are overly complex we'd need to break them down into smaller and more managable plans to cover topics.  But if they are inter-related topics they can stay in one plan.  I have some feedback on that as well.  But first, I just want to make sure I can rename a sister properly, even if she's protected.  A rename is still ok.  The protection should prevent "automatic" actions from happening - but not things I want to do manually.  We could always introduce a warning "Draknisa is protected - are you sure you want to xxxxx?"
```
<!-- markdownlint-enable MD013 -->

The manual-name/protection request is implemented under
[task 5.3a](2026-10-21-likeness-rebaseline-and-family-naming.md#phase-5--family-gallery-and-safe-naming-workflow)
in the engine/action owner plan; L1-L5 cover the presentation requests.
