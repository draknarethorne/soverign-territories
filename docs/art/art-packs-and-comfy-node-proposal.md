# Art packs and dynamic prompts in ComfyUI (proposal)

**Status:** Proposal, not scheduled · **Decision needed:** whether to build the shared core and the ComfyUI nodes before the
desktop app · **Owner:** art pipeline

Two ideas that share one foundation: (1) ship the art JSON library as named, versioned **packs** (zip files), and (2) let
ComfyUI assemble prompts **at run time** from a template plus chosen JSON pieces, instead of only from prompts rendered ahead
of time. Both need the same thing: the prompt logic as a small reusable Python library.

## Verdict

- **Build the shared core first**, then the ComfyUI nodes, then the pack tool. The nodes are a shorter path than the Studio
  app and give the fast "try a combination" loop that the app was meant for. The app can follow later on the same core.
- **Keep both modes.** Pre-rendered prompts stay the home of hand-curated work (stable, reviewable in git, one workflow per
  card). Dynamic nodes are the lab: try combinations, then freeze the one you like back into a card.
- The core is stdlib-only Python (`json`, `re`, `pathlib`), so it runs inside ComfyUI's embedded Python with nothing to install.

## The shared core

Today `tools/generators/gen_prompt.py` loads a card **file** and writes a prompt **file**. The nodes need the middle part as
a function that takes data in memory. Refactor, without changing behaviour:

| Function | In | Out |
| --- | --- | --- |
| `assemble(card: dict) -> Prompt` | a card as a dict (stage, heroArt, template, components, overrides) | positive, negative, and which piece supplied each token |
| `list_pieces(kind=None, scope=None, tag=None)` | optional filters | piece ids with name, kind, tags, stages |
| `list_templates(stage=None)` | optional filter | template paths |
| `list_heroes()` | none | identity ids |
| `save_card(card: dict, group, slug)` | a card dict | writes `data/art/_sets/...` (the "freeze" step) |

The file-based `generate()` becomes a thin wrapper over `assemble()`, so the CLI, the validator, the Studio app and the nodes
all share one implementation. **The committed `prompts/` folder is the test oracle**: the refactor is correct when every
committed prompt regenerates byte-identical (the same bar used when moving pieces).

## ComfyUI custom nodes ("Thorne Art Nodes")

A folder `ComfyUI/custom_nodes/thorne_art/` containing a small `__init__.py` that imports the shared core (a junction or
symlink to the repo's `tools/` keeps one copy). The repo location is read from one setting (an environment variable).

| Node | Inputs | Output |
| --- | --- | --- |
| **Thorne Hero** | identity (combo list from `data/art/heroes`, dragons) | hero reference |
| **Thorne Template** | template (combo list from `data/art/_templates`) | template reference |
| **Thorne Piece** (stackable, or one node with 10 optional slots) | slot name (`underlayer`, `wearing`, `pose`, `background`, ...), piece (combo filtered by kind) | a slot-to-piece pair |
| **Thorne Literal** | slot name, free text (supports the `+extend` prefix) | a slot-to-text pair |
| **Thorne Assemble** | hero, template, up to 10 pairs, optional overrides (palette/physique as JSON) | `positive`, `negative`, `recipe` (JSON text) |
| **Thorne Load Card** | an existing card from `_sets` | the same outputs, so a curated card can be opened and tweaked |
| **Thorne Freeze to Card** | recipe, group, slug, name | writes the card JSON; the next `gen_prompt` run turns it into a curated prompt |

`positive` and `negative` are plain strings and connect to the prompt inputs of the existing subgraph (for example the Qwen
edit text encode, or the MiniMax video prompt), exactly where the pre-rendered text is pasted today.

How the loop works:

1. Open a stage workflow (for example `ST3_Scene` from `workflows/_templates`) with the Thorne nodes ahead of the prompt.
2. Pick the hero, the template, then swap pieces: `underlayer = lace-bodysuit`, `wearing = mermaid-gown`, `pose = ...`.
3. Run. ComfyUI saves the whole graph, including the node values, inside the output PNG, so every render carries its own
   recipe and any image can be dragged back in to reproduce it.
4. When a combination is a keeper, either save the workflow as a curated workflow (it stays dynamic) or use **Freeze to Card**
   to write a real card, so it joins the pre-rendered, git-reviewed library.

Technical notes and limits:

- **Combo lists load when ComfyUI starts**; a new piece needs a refresh (the `r` key) or a restart. Typing a piece id into a
  literal slot is the workaround while testing.
- A node cannot grow its inputs freely in older versions; fixed optional slots (10 to 12) are the dependable approach, and newer
  dynamic-input support can replace them later.
- Piece lists get long (hundreds). Filter combos by kind per slot and sort by scope (core, race, theme, hero) so the useful
  ones are near the top; tags help search.
- Validation still matters: the nodes should call the same checks (unknown token, missing piece) and show the error in the
  node instead of producing a silently odd prompt.
- Videos work the same way: an **Animation** node set over `data/animation` (motions, sequences, cameras) can assemble the
  MiniMax prompt, reusing `gen_animation.py` as the second library module.

## Art packs

A pack is a named, versioned zip of art JSON that can be shared, installed or sold separately.

### Naming

| Part | Rule | Example |
| --- | --- | --- |
| Pack id | `<scope>.<subject>`, lowercase, hyphens inside a part | `core.dungeon-backgrounds`, `theme.danish`, `hero.drakness-romantic-scenes` |
| Scope | `core` (works anywhere), `race`, `theme`, `hero`, `scene`, `template` | |
| File name | `<subject>_<scope>_art_v<major>.<minor>.zip` | `dungeon-backgrounds_core_art_v1.0.zip`, `royal-clothing_human_art_v1.2.zip` |
| Display name | "Thorne Art Pack: <Subject>" | "Thorne Art Pack: Dungeon Backgrounds" |

The family name (Thorne Art Packs, short TAP) is a placeholder; pick the final brand when a user-facing product exists.

### What goes in a pack

A pack is a manifest plus the JSON it lists, laid out exactly as in the repo so installing is "unzip over `data/art`":

```text
pack.json                       manifest (below)
data/art/wardrobe/clothing/gowns/*.json
data/art/backgrounds/fantasy/dungeons/*.json
preview/                        optional contact sheet images
```

```json
{
  "id": "theme.danish",
  "name": "Thorne Art Pack: Danish Winter",
  "version": "1.0",
  "scope": "theme",
  "includes": ["data/art/themes/danish/**"],
  "requires": ["core.wardrobe-basics"],
  "notes": "Fantasy-adapted Danish winter pieces."
}
```

- **Closure check**: pieces reference other pieces by path. A tool computes the reference closure (the logic already exists in
  `tools/art/art_refs.py`) and fails if a pack uses a piece that is neither inside it nor in a pack listed under `requires`.
- **Packs carry data, not prompts.** Prompts, workflows and renders are regenerated after install; that keeps packs small and
  avoids stale text.
- **Hero packs** (for example `hero.drakness-romantic-scenes`) bundle the identity, her scene cards and any hero-signature
  pieces, and require the core packs those cards use.
- **Validation on install**: unzip into a scratch copy, run the validator, and only then merge.

### Tool

`tools/art/art_pack.py` with `list`, `build <id>`, `verify <zip>` and `install <zip>`; the manifests live in
`data/art/_packs/<id>.json` so a pack is defined once and rebuilt on demand. The Studio app and a ComfyUI "Install pack" node
can both call it later.

## Library inventory (today)

Roughly 200 wardrobe pieces were added in one pass so the packs have substance: A-pose underlayers (female and male, including the
backless set), about 40 dresses and gowns, about 30 outfits (catsuits, leather, spandex, harem and palazzo pants, skirts and
open-midriff sets, male tunics, doublets and coats), about 30 footwear and hosiery pieces, armor by material (plate, mail, scale,
lamellar, leather, bone, cloth and velvet, hide, padded, living wood, crystal, bronze, ceremonial, shadow, runic) in unisex,
female (including bikini cuts) and male cuts, plus arms, backs, headwear and jewelry. `tools/generators/scaffold_wardrobe_tests.py`
turns any folder of them into test cards for one hero.

## Suggested order

| Step | Work | Size |
| --- | --- | --- |
| 1 | Refactor `gen_prompt.py` into `assemble()` plus the list helpers; prove byte-identical prompts | S to M |
| 2 | `art_pack.py` and `data/art/_packs/` manifests; pack the Danish theme as the first test | S |
| 3 | The Thorne nodes (Hero, Template, Piece, Literal, Assemble, Load Card, Freeze) | M |
| 4 | Animation nodes over `gen_animation.py` | S |
| 5 | Studio app on the same core, only if the node workflow leaves gaps (browsing, refactors, image library) | L |

## Risks

- **Two implementations drifting**: avoided by the single core and the byte-identical oracle. Do not port the logic into
  JavaScript or C#.
- **Piece sprawl**: hundreds of pieces make combos hard to browse. Tags, scopes and the pack grouping are the answer.
- **Dynamic workflows hide the recipe in the graph**: the `recipe` output and the metadata in each PNG keep it reproducible;
  freeze keepers into cards so the library stays reviewable.
