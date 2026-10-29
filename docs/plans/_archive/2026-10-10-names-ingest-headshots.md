# Plan: names that follow the photos, the new Various batch, headshots, look-alike guard

**Status:** done, Oct 10, 2026 (Phases 0 to 4 and 6 built; Phase 5, the variant Primes, was replaced by the Prime flows and is dropped unless you say otherwise: see T11 in the Prime plan)

Source: your brain-dump, copied word for word at the end of this plan ("Your brain dump, word for word").

Result report: [../art/likeness-reorg-2026-10-10.md](../../art/likeness-reorg-2026-10-10.md). How-to: [../art/likeness.md](../../art/likeness.md), [../art/original-photos.md](../../art/original-photos.md).

## Threads, in your order

1. **Remember who everyone was.** Every person folder keeps a record of her name and where she has been.
2. **Models becomes Sisters** (Angels, Sisters, Prospects, Artists).
3. **The new Various batch** is compared with every sister, angel and prospect; then re-pair **Seraphine**, and check **Sophie Lloyd**.
4. **Headshots:** `gallery_944x1104` gets a sibling `headshot_944x1104`, made for everyone, usable as a Prime input.
5. **A looser comparison?** And a guard so prospects do not look like a top-tier sister or angel.
6. **Review photos:** clearly not her goes to Prospects as a new character; close ones stay.
7. **Alternate Primes:** more than one Prime per hero, each feeding its own 2_Bare.

## Decisions

| ID | Question | Answer |
| --- | --- | --- |
| D1 | Rename `Models` to `Sisters` | Yes (Oct 10). The root name is a setting (`paths.photoRoots`); `Models` is still read as an alias for one cycle (`SISTER_ROOTS`); tests cover both names. The real folder is renamed. |
| D2 | Where is the original name kept? | A `z_first_last.txt` in every person folder (Oct 10). First line `name: First Last`; then dated history lines the tools write. An unknown name is the invented one the tool gave. The file travels with the folder. |
| D3 | Headshots | Made for everyone by `originals`, `--no-headshots` to skip. 1,121 files, 0.86 GB (520 GB free). |
| D4 | Loosening the comparison | Not changed. `likeness loosen` measured it: lowering the thresholds by 0.10 frees only 3 more review photos, so the settings stay. |
| D5 | Look-alike guard | `likeness lookalikes` writes `reserved:` lines into the `z_` file of every prospect or artist person scoring 0.30 or more against a sister or angel (23 folders). Cards below the top tier should avoid them (the card-data rule is still to write). |
| D6 | Alternate Primes | Design below; **needs your approval before any code**. |

## Steps

### Phase 0: safety and a place for Various

- [x] 0.1 Backup `_backup/2026-10-10-before-names-ingest` (Various, `z_` files, `workspaces.json`, a manifest of 3,546 files).
- [x] 0.2 `Various` is a pool at the top level (`likeness.pool_home`, photo roots, `originals`), with tests.

### Phase 1: names that follow the photos

- [x] 1.1 `tools/art/people.py` (read, write, note, adopt, reserved) and `likeness names`; tests in `test_people.py`. The `z_` file lives in each folder's `gallery`.
- [x] 1.2 `likeness` writes history when it moves, merges, pairs or retires.
- [x] 1.3 Backfill: 99 `z_` files written from the move log and invented names.
- [x] 1.4 `Models` renamed to `Sisters` in config, code, tests, docs and help; the real folder renamed.

### Phase 2: the new Various batch

- [x] 2.1 199 photos renamed (`various_image_*`, `various_shot_*`), scaled and scanned; 2 have no usable face.
- [x] 2.2 `sort --singles` preview and apply: 1 to Angelica, 1 to Azaline, 1 to Drakniss, 1 to Draknoxa, the rest into about 50 new prospect folders with invented names.
- [x] 2.3 `pairs` for every angel: Seraphine, Gavrielle and Sandalyn re-paired (Anya Sloane, Wren Thorn, Cleo Park); Azaline and Camaris left (no candidate in the band). Sophie Lloyd fits no slot (closest sister Drakneta at 0.08).

### Phase 3: review, looseness and the look-alike guard

- [x] 3.1 `likeness loosen` (D4).
- [x] 3.2 `likeness review --out`: 40 photos became new prospects; about 40 stay in review.
- [x] 3.3 `likeness lookalikes --apply` (D5). `merge` now retires the emptied folder to `_retired`; four duplicate people merged.

### Phase 4: headshots

- [x] 4.1 `originals` writes `headshot_944x1104/<name>_head_944x1104.png` (face box widened 2.5 times, standard 944:1104 shape, never letterboxed); no face or a face under 60 px gets none.
- [x] 4.2 `inputs set HERO --photo <headshot>` works (`find_image` reads the headshot folders; `inputs photos` never swaps a headshot back for the full photo); test added.
- [x] 4.3 Disk check: 0.86 GB for the whole library.

### Phase 5: alternate Primes (design, no code)

- [x] 5.1 Design written (below).
- 5.2 Dropped: the Prime flows, P2, P3 and the FireRed lock replaced the variant-Prime idea (see the reconcile table of the Prime plan). Closed with this plan.

### Phase 6: close

- [x] 6.1 Report, guides, STATUS line and the todo.
- [x] 6.2 Tests, validator, markdownlint, commit.

## Phase 5 design: more than one Prime per hero

Why: a different original can bring in other facial features better than the one picked for Prime, so a hero may want a Prime B built from another photo (or a headshot), and each Prime must drive its own 2_Bare, 3_Barefoot and so on, so the two chains never mix.

Today a hero has one photo (`photos[Hero]`), one set of role images (`inputs[Hero]`: prime, bare, apose, heels, scene, polish) and one chain of workflows named `<Hero>_Qwen_Alpha_1_Prime` -> `Alpha_2_Bare_*` -> `Alpha_3_*`.

| Option | Idea | Cost |
| --- | --- | --- |
| A (recommended) | A variant is a suffix on the hero: `Seraphine_B`. It is a second entry in `photos` and `inputs`, with its own generated workflows (`Seraphine_B_Qwen_Alpha_1_Prime` ...), input files and finals. Every command that takes `--hero` already works on it. | The prompts and workflows are generated for each variant; `finals` and `inputs` list it as its own hero. Cards still point at the hero, with `art.variant` choosing the final chain. |
| B | Variants inside one hero: `inputs[Hero].primes = {"B": {...}}` and every role image gets a letter. | Touches every command that reads `inputs`; more places to get wrong. |

What option A needs, in the normal order:

1. Rule: a variant name is `<Hero>_<Letter>`; its photo defaults to the hero's; its chain is separate; the card's final is the hero's unless `art.variant` says otherwise (a design rule in `docs/art`).
2. Schema: an optional `variant` on the art identity.
3. Tooling: `inputs variant HERO B --photo NAME` creates the entry in `workspaces.json` and generates its workflows (preview unless `--apply`); `finals` and `status` show variants under their hero.
4. Tests, then your first run with a headshot as the Prime input.

Questions for you before it is built: which hero gets a Prime B first (Seraphine?), and should a variant share the hero's input folder or have its own.

## Result

Done Oct 10, 2026. The library is reorganised again (see the report); every person folder has a `z_` name file; `Various` is empty apart from 2 photos with no face; three angels have new faces; headshots exist for every photo with a usable face. What is left is yours: the review folders (about 40 photos), the reserved look-alike list, Azaline and Camaris, trying a headshot as a Prime, and approving Phase 5.

## Your brain dump, word for word

As we move photos around - how are we tracking their original names?  In the models folder, I did have their originals names in "z_first_last.txt" (the z_ is so it's at the end of the list of files)
so maybe that's a good idea to have something like that so when we do take a prospect and put it into an angel or model (which I should rename to Sisters instead of Models) but we have a bunch of scripts that might be impacted in doing that, so not sure if what that changes if we do that - so we'd have Angels, Sisters, Prospects and Artists as the folders?
If you think that's a good idea in terms of how we move things around - let me know or if you have a better way we can do that.  I think each model directory should have that and would be good for angels and prospects - if we can remember who the angels were and if we shifted any sisters - I'd want that as well.  Or we just make up a name if we can't remember, but we need a convention for that somehow - so if we move someone out of an angel and into prospects - we know what the name to use is.
I also moved the Various directory out of Prospects/Various to the same level as Prospects and I have a ton of new images that need to be compared to the existing set of all sisters, angels and prospects - some images should match existing and others are completely new.
I'd like them analyzed and update.  I'm also wondering if since we doing all this if the process that generates the gallery_944x1104 images could also create headshot_944x1104 with a good scaled up images of just the faces?  I'm wondering if those might also be used as a test into the Prime workflow and see how that works as well?  Sometimes, I'd like to be able to do that if possible and do some tests.
We can make that an option and right now just do it for everyone, unless I see a huge disk space problem and it doesn't work out.  Again, alot to do ... but I know you can handle it.
Lastly - what if we loosen the comparison up a little - would that take things from review and put them back into a sister and would that also help when I dump in random images into Various and pair things better or even combine some of the Prospects into a single "ficticious" person?
I'm fine if we stick with it how it is - what I want to avoid is having Prospects that are so close to a sister or angel that I use them for a common/uncommon/rare tier card as a likeness and it looks like a top tier one.
There's probably some setup or way to figure that out since we're doing all the compares and understand who looks-like-who in the process.
Ultimately - we can review these new images, put them into their "designated spot" and then what I would like is another analysis if we find a better pair for a sister.
I brought up Seraphine as there's only one image to choose from and I wan't thrilled with the output.
So that's why I pulled a ton of new photos to look for her.
I'd also love to use Sophie Lloyd as an angel if she scores high to pair with a sister - if not, I'll find another place to use her somewhere.
For the review images - if we really think they are not the sister, then I'd just want to move them into Prospects as a new character.
If they are so close that I do need to eye-ball them - then it's fine to leave them.   Pulling them out helps me to not accidentally use them for a sister and then end up with a generated file that doesn't align to the sister.
The reason I do want more images to feed into Prime is that I might find that other originals help bring in some facial features or other aspects just a bit better than what I pick for Prime and I need another (alternate Prime) of the sister.  So - in the scheme of things, we might end up with more than a single prime workflow - and each one would drive into 2_Bare, etc... Sorry for so much, but I've been away and all these things came up
