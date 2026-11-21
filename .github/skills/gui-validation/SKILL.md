---
name: gui-validation
description: "Use when validating Sovereign Territories Gallery, Overview, Review, reports or other web UI in a real browser, including local-page navigation, controls, thumbnails and Playwright evidence. Keep read-only checks separate from staged or applied actions."
---

# Browser and GUI validation

## Establish the target and authority

Read [status](../../../docs/STATUS.md), the affected task through the
[planning agreement](../../../docs/plans/README.md), and its runbook and
acceptance gate. Identify the exact environment, page URL, run/receipt,
expected counts, named cases and permitted interactions. Reuse an existing
shared browser page when suitable; do not assume a different tab, stale
report or fixture represents the installed result.

Discover the browser tools actually available in this session. Prefer their
page snapshot and element interactions; use a concise, self-contained
Playwright snippet only when those tools cannot prove the required behavior.
For the integrated Playwright tool, operate through its supplied `page`
object and access page DOM only inside `page.evaluate`; do not assume this
particular host API exists elsewhere. Do not install a browser or dependency
solely to make a check appear successful.

For example, after exposing the relevant rows, a self-contained tool snippet
can count loaded images without returning private image paths:

```js
return page.evaluate(() => ({
  title: document.title,
  loaded: [...document.images].filter(image => image.complete && image.naturalWidth > 0).length
}))
```

This count includes offscreen images and is not, by itself, the required
representative visual check.

## Inspect the real experience

1. Open or focus the authorized actual page and capture its URL/state. Wait
   for the relevant content, then inspect accessibility/DOM state and a
   screenshot when visual appearance matters. Use a snapshot to identify
   controls; never click based only on coordinates in a screenshot.
2. Verify the requested behavior, not merely file existence: counts against
   the bound receipt, representative visible thumbnails actually loaded,
   filters and pagination where relevant, and current native/detail/history
   links. For lazy-loaded images, first expose the relevant rows; image
   `complete` plus positive `naturalWidth` is loading evidence, not proof of
   visual quality. Check navigation targets and explicit missing/stale states.
3. Keep normal acceptance read-only. Distinguish filters/navigation from
   controls that stage, save, apply, undo, delete or contact a service.
   Never stage a real Gallery action during inspection. Exercise mutating
   interactions only on an authorized isolated fixture with known recovery.
4. Inspect console/page errors and failed requests when the host exposes
   them; note pre-existing issues and redact private paths from shared
   evidence. If instrumentation requires a reload or new page, first
   protect any shared or unsaved state. Record page/run, observed
   interactions, representative coverage, errors, screenshots if needed and
   what remains unchecked. Never claim a click, loaded image, identity
   decision or human acceptance from static HTML or a fixture test alone.

Keep temporary captures under ignored `tmp/`; preserve durable run evidence
in its documented location. Never upload private photos/screenshots to an
external service. If a browser, target or interaction is unavailable, state
the gap and the next check rather than inventing success. Use
[visual review](../visual-review/SKILL.md) for visual critique and
[long-run acceptance](../long-run-acceptance/SKILL.md) for installed-run
accounting and recovery.
