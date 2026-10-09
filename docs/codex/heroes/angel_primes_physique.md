# Angel Primes Physique: Build Rationale

Why each of the 22 Angel Primes has the build in their art identity. Companion to [angel_primes_codex.md](./angel_primes_codex.md);
the identity JSON in [data/art/heroes/angel-primes/](../../../data/art/heroes/angel-primes/) is the source and wins over this page.

## Rules

| Rule | Detail |
| --- | --- |
| No bulky women | Variety comes from height, leg length, softness and curve (petite, tall, curvy, lean), never from muscle. Words such as strong, muscular, sturdy or powerful are not used for the women, so none reads as an ape. Slender is one option among several, not the rule |
| The men are a mixture | Lean and agile (Elarion, Zadriel, Metrael, Vexiel, Judiel), heroic (Auriel, Luzariel, Angelo) and heavy (Urael, Verael, Baracel), chosen by element and archetype |
| Two steps | 1_Prime uses the standard figure (female: lithe and slender; male: athletic and well-proportioned) so the original photo stays recognisable. 2_Bare applies the individual build |
| Colours are forced | Hair, eye and skin colour are defined for each angel and forced at 1_Prime, so the photo is changed to match |
| Same pair, different silhouettes | A pair shares an element, not a body. The woman and the man differ in height and weight so the two read apart |

## Why the women are not bulky

Angels read as graceful and otherworldly. A heavily muscled woman reads as an athlete or a fighter and loses that. Strength is shown
through the wings, the weapon, the pose and the element's magic. The women are different from each other instead: Haniya is petite and
compact, Gavrielle, Nyxene, Seraphine and Azaline are tall, Camaris, Ravaelle and Sandalyn are curvy with fuller hips, Angelica is
medium and balanced, Remiah and Sammara are lean and agile. Camaris, Sandalyn and Remiah were rewritten from fighter's frames.

## Why the men vary

The men carry the weight range the angel set needs. Earth and Grass are the heavy, immovable pair (Baracel, Verael); Fire is the
warrior (Urael); Ice, Wind, Water and Poison are lean and fast; Light and Darkness are tall and striking. This gives male cards a
wide silhouette range from one set.

## Builds

| Angel | Sex | Build |
| --- | --- | --- |
| Angelica | Female | Medium height, balanced, well-proportioned build; a natural, approachable presence |
| Angelo | Male | Athletic, broad-shouldered, well-proportioned build |
| Seraphine | Female | Tall, graceful, elegant build; long-limbed with a regal bearing |
| Auriel | Male | Tall, radiant, heroic build; broad-shouldered and noble |
| Ravaelle | Female | Soft, curvy, gently rounded build of medium height; warm and approachable |
| Zadriel | Male | Lean, gentle, swimmer's build; long and fluid |
| Haniya | Female | Petite, short, compact build with a youthful, springy frame |
| Verael | Male | Big, broad, powerfully built; bear-strong and solid |
| Gavrielle | Female | Tall, willowy, long-limbed build with a dancer's poise |
| Elarion | Male | Slim, agile, long-limbed build; light on his feet |
| Sandalyn | Female | Medium-tall, soft hourglass build with a grounded, steady bearing |
| Baracel | Male | Stocky, thick-set, immovably strong build |
| Remiah | Female | Slender, lean, agile build of average height; quick and light |
| Judiel | Male | Athletic, wiry-muscular, sharp and angular build |
| Azaline | Female | Tall, slim, poised, elegant build with precise posture |
| Metrael | Male | Tall, slim, poised, scholarly-athletic build |
| Camaris | Female | Medium height, curvy hourglass build; light and quick, with a dancer's poise |
| Urael | Male | Heavily muscled, broad warrior build |
| Sammara | Female | Slender, sinuous, flexible build; sleek and sensual |
| Vexiel | Male | Lean, sinewy, sly build; fluid and predatory |
| Nyxene | Female | Tall, statuesque, commanding build with long lines |
| Luzariel | Male | Tall, commanding, perfectly proportioned build; striking beauty and menace |

## How the pipeline uses this

| Stage | Figure | Colours |
| --- | --- | --- |
| 1_Prime | Standard figure (`figureProfile: standard`) | Forced from the identity palette |
| 2_Bare | Individual build from this page | Forced from the identity palette |
| 3 onward | The Bare image carries the build | Palette |

Check any time with `python tools/art/identity_audit.py`; it also fails if a female angel's build uses a strength word.
