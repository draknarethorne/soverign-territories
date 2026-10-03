# Thorne Art Studio (proposal)

**Status:** Proposal, not scheduled · **Decision needed:** whether and when to build · **Owner:** art pipeline

A Windows tool to create and manage the `data/art/` JSON files, preview the assembled prompt, and send prompts to ComfyUI,
instead of doing that by hand in VS Code. This page assesses it honestly: what it is, how big it is, what to build first,
and when it stops being a distraction.

## Verdict

- **Not needed for MVP cards.** Everything it would do is already possible with the generator, validator and VS Code.
- **Worth building once friction shows up**: hundreds of pieces, frequent moves/renames, and copy-pasting prompts into
  ComfyUI. Both are already felt (the theme work needed a safe-move tool; prompt copy-paste is on the deferred list).
- **Build the plumbing as command-line tools first.** Each is useful on its own and becomes a backend for the app, so
  none of the work is wasted if the app is never built or is built later.

## What it would do

| Capability | Needs | Size |
| --- | --- | --- |
| Browse and search pieces by scope, theme, kind and tag; "where used" | Read the tree and an index of references | S |
| Prompt preview: pick a card (or template + slots), see the assembled positive and negative prompt, and which piece supplied each token | The generator exposing token provenance | M |
| Create and edit pieces, cards, identities and themes with forms | The JSON Schemas (they already exist and are strict) | M |
| Move, rename, delete with every reference updated | A reference index (the `art_refs.py` logic) | M |
| Validate as you type: schema, template-vs-slot alignment, realm rules | The validator as a library or CLI with JSON output | S |
| Send prompts to a ComfyUI workflow: single run, a whole batch, or only cards whose prompt changed | ComfyUI HTTP API, a per-workflow node map, a "last rendered" manifest | L |
| Image library: link each PNG to its card, contact sheets of views, side-by-side compare | The `assets/art/` path convention | M |

## Architecture options

| Option | Pros | Cons |
| --- | --- | --- |
| **A. C# UI over the existing Python tools (recommended start)** | One source of truth for prompt logic; the app stays thin | Needs Python installed; process calls |
| B. Port the generator to C# | Single self-contained app | Two implementations that can drift. If chosen, use `prompts/` as a byte-exact test oracle: the C# output must match the committed prompts |
| C. Local web UI (Python backend + browser) | Fastest to build, no second stack | Not the C# desktop app you prefer |
| D. VS Code extension | Lives where you already work | TypeScript, and weaker for image-heavy work |

**UI framework.** WinForms is quickest if you know it: tree view, grids, a text box with highlighting, and form editors
cover phases 1 to 4. WPF is better if the image library and prompt preview with rich formatting become central
(virtualised galleries, data binding). Avalonia or MAUI only matter if cross-platform does, and it does not. A WinForms
MVP that grows into WPF screens is a reasonable path.

## What to build first (each stands alone)

1. **`gen_prompt.py --explain <card>`**: print the prompt plus JSON of which piece or default filled each token. This is the
   core of the preview and also makes debugging prompts in VS Code much easier.
2. **ComfyUI injection CLI**: given a workflow in API format and a small `workflows/<name>.map.json` (which node IDs take
   positive, negative, seed and input image), queue a card, a group, or "everything changed since the last render", and
   save results to the `assets/art/` path. This removes the copy-paste with far less work than a GUI and is the riskiest
   part, so it should be proven before wrapping it.
3. **Stable JSON formatting** (a formatter hook): a GUI that saves files must produce the same key order and indent as
   hand edits, or every save becomes a noisy diff.
4. **A card/reference index export** (JSON): lets a UI start fast without re-scanning the tree.
5. **Decide STATUS item C1** (asset naming and how cards point at PNGs). Image features depend on it. The path convention
   is already proposed in `data/art/README.md`.

Already done: `art_refs.py` (where-used and safe move), the validator, the generator and the shot-library scaffold.

## Risks

- **Scope creep.** A tool that edits everything tends to grow without end. Keep each phase shippable on its own.
- **Two writers.** The app and VS Code will both edit files. Watch the folder for changes and never hold stale copies.
- **ComfyUI variability.** Workflows differ in node layout and models; the node map isolates that, but API changes can
  break injection. Keep it behind one small module.
- **Time spent on tooling versus cards.** Gate the GUI on real pain: build it when moves, edits or render queuing are
  slowing content work, not before.

## Recommended path

Do items 1 to 3 above as command-line tools while the library grows. Build a read-only browser and prompt preview
(phases 1 and 2) next, since they need no editing safety. Add editing, safe moves and the ComfyUI bridge once the
command-line versions have proven the logic.
