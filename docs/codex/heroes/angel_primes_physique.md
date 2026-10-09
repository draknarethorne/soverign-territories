# Angel Primes Physique: Build Rationale

Why each of the 22 Angel Primes has the build in their art identity. Companion to [angel_primes_codex.md](./angel_primes_codex.md);
the identity JSON in [data/art/heroes/angel-primes/](../../../data/art/heroes/angel-primes/) is the source and wins over this page.

## Rules

| Rule | Detail |
| --- | --- |
| No body-builder women | Variety comes from height, leg length, softness, curve and how much tone shows (petite, tall, curvy, lean; soft to visibly toned abs, arms and legs), never from bulk. Words such as strong, muscular, sturdy or powerful are not used for the women, so none reads as an ape or a body builder. Slender is one option among several, not the rule |
| The men are a mixture | Lean and agile (Elarion, Zadriel, Metrael, Vexiel, Judiel), heroic (Auriel, Luzariel, Angelo) and heavy (Urael, Verael, Baracel), chosen by element and archetype |
| Two steps | 1_Prime uses the standard figure (female: lithe and slender; male: athletic and well-proportioned) so the original photo stays recognisable. 2_Bare applies the individual build |
| Colours are forced | Hair, eye and skin colour are defined for each angel and forced at 1_Prime, so the photo is changed to match |
| Same pair, different silhouettes | A pair shares an element, not a body. The woman and the man differ in height and weight so the two read apart |

## Why the women vary, and have no body-builder look

Angels read as graceful and otherworldly. A heavily muscled woman reads as an athlete or a fighter and loses that. Strength is shown
through the wings, the weapon, the pose and the element's magic. The women are different from each other instead: Haniya is petite and
compact, Gavrielle, Nyxene, Seraphine and Azaline are tall, Camaris, Ravaelle and Sandalyn are curvy with fuller hips, Angelica is
medium and balanced, Remiah and Sammara are lean and agile. Tone varies too, so abs, arms and legs do not all look the same: Remiah and
Nyxene show crisp, visible abs, Camaris softly visible abs, Azaline, Sammara and Angelica faint tone, and Ravaelle and Seraphine stay soft.
Camaris, Sandalyn and Remiah were rewritten from fighter's frames; the limit is a body-builder look, not tone.

## Why the men vary

The men carry the weight range the angel set needs. Earth and Grass are the heavy, immovable pair (Baracel, Verael); Fire is the
warrior (Urael); Ice, Wind, Water and Poison are lean and fast; Light and Darkness are tall and striking. This gives male cards a
wide silhouette range from one set.

## Builds

| Angel | AP | Build |
| --- | --- | --- |
| Angelica | AP-001 | Medium height, balanced, well-proportioned build; a natural, approachable presence |
| Seraphine | AP-002 | Tall, graceful, elegant build; long-limbed with a regal bearing |
| Ravaelle | AP-003 | Soft, curvy, gently rounded build of medium height; warm and approachable |
| Haniya | AP-004 | Petite, short, compact build with a youthful, springy frame |
| Gavrielle | AP-005 | Tall, willowy, long-limbed build with a dancer's poise |
| Sandalyn | AP-006 | Medium-tall, soft hourglass build with a grounded, steady bearing |
| Remiah | AP-007 | Slender, lean, agile build of average height; quick and light |
| Azaline | AP-008 | Tall, slim, poised, elegant build with precise posture |
| Camaris | AP-009 | Medium height, curvy hourglass build; light and quick, with a dancer's poise |
| Sammara | AP-010 | Slender, sinuous, flexible build; sleek and sensual |
| Nyxene | AP-011 | Tall, statuesque, commanding build with long lines |
| Angelo | AP-012 | Athletic, broad-shouldered, well-proportioned build |
| Auriel | AP-013 | Tall, radiant, heroic build; broad-shouldered and noble |
| Zadriel | AP-014 | Lean, gentle, swimmer's build; long and fluid |
| Verael | AP-015 | Big, broad, powerfully built; bear-strong and solid |
| Elarion | AP-016 | Slim, agile, long-limbed build; light on his feet |
| Baracel | AP-017 | Stocky, thick-set, immovably strong build |
| Judiel | AP-018 | Athletic, wiry-muscular, sharp and angular build |
| Metrael | AP-019 | Tall, slim, poised, scholarly-athletic build |
| Urael | AP-020 | Heavily muscled, broad warrior build |
| Vexiel | AP-021 | Lean, sinewy, sly build; fluid and predatory |
| Luzariel | AP-022 | Tall, commanding, perfectly proportioned build; striking beauty and menace |

## How the pipeline uses this

| Stage | Figure | Colours |
| --- | --- | --- |
| 1_Prime | Standard figure (`figureProfile: standard`) | Forced from the identity palette |
| 2_Bare | Individual build from this page | Forced from the identity palette |
| 3 onward | The Bare image carries the build | Palette |

Check any time with `python tools/art/identity_audit.py`; it also fails if a female angel's build uses a strength word.
