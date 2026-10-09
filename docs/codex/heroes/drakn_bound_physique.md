# Sovereign Territories — Hero Card Roster: Mythic Tier (SD-011 – SD-020)
## Male Heroes Character Architecture & Physical Specification Matrix (Schema-Aligned)

---

## 1. Master Bloodline Architecture: Shared Baseline vs. Elemental Phenotype

Aligning with the `HERO_*.json` schema structure established by the Transcendent tier, the Mythic Male Heroes represent distinct humanoid races, martial bloodlines, and combat roles. 

### The Foundational Male Core (Universal Studio Setup)
* **Master Studio Base Uniform:** a fitted swim brief in the hero's primary colour (`data/art/wardrobe/swimwear/trunks/swim-brief.json`), bare feet in the A-pose (`aPoseFootwear: barefoot` in `data/art/_settings/studio.json`).
* **Render Standards:** Master Canvas `944 × 1104` with studio cream background padding (`#F5F0E6`), scaling downstream to `1080 × 1350` (4:5) for mobile UI card frames.
* **Structural Archetypes:** broad shoulder-to-waist V-taper, a defined functional core, clear masculine neck and jawline geometry, grounded combat-ready A-pose. Unlike the sisters, the men are not one skeleton: each has his own build, from lean duelist to heavy juggernaut (section 5).

### The Elemental Glamour Phenotype (Individualized)
* Each hero possesses fully specified facial planes, eye coloration, skin undertone, hair styling, accent metals, and strict negative arrays to prevent cross-contamination in diffusion passes.

---

## 2. Master Card Registry & Phenotype Alignment

| Card ID | Hero Name | Element | Class | Race Presentation | Primary & Accent Colors | Eye / Hair / Skin Phenotype | Physical Preset Category |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **SD-011** | Draknare Thorne | Darkness | Shadow Knight | Human | Obsidian Black, Tarnished Silver, Deep Amethyst | Deep violet eyes / Rich black hair / Pale | Heavy Armor / Imposing Commander |
| **SD-012** | Ignis Emberstride | Fire | Warrior | Human | Ember Red, Burnished Bronze, Charcoal Black | Molten amber eyes / Dark auburn hair / Warm sun-bronzed | Lean Martial / Greatsword Striker |
| **SD-013** | Nizaras Featherstone | Grass | Rogue | Wood Elf | Forest Green, Moss Brown, Pale Gold | Verdant green eyes / Dark umber hair / Light olive | Wiry / Woodland Infiltrator |
| **SD-014** | Lyran Frostfall | Ice | Knight | High Elf | Glacial Cyan, Frost White, Steel Grey | Glacial cyan eyes / Platinum-blonde hair / Fair | Statuesque / Regal Bastion |
| **SD-015** | Corin Tidewalker | Water | Beast Lord | Human | Deep Oceanic Blue, Seafoam Green, Driftwood Tan | Deep teal eyes / Sun-streaked brown hair / Sun-weathered tan | Taut / Pelagic Vanguard |
| **SD-016** | Hauk Hammerfell | Light | Paladin | Human | Radiant Rose Gold, Ivory White, Polished Bronze | Radiant amber-gold eyes / Golden-blonde hair / Warm | Heavy Armor / Unyielding Bulwark |
| **SD-017** | Torvald Stonebreaker | Earth | Berserker | Barbarian | Deep Rust Brown, Iron Grey, Warm Sand | Deep umber eyes / Dark brown hair / Deep sun-weathered tan | Brutal / Dense Juggernaut |
| **SD-018** | Dorian Stormstrike | Lightning | Monk | Celestial | Storm Gold, Arc White, Storm Grey | Electric cobalt eyes / Jet-black hair / Warm golden-tan | Wiry / Kinetic Conduit |
| **SD-019** | Zephyr Galeheart | Wind | Warrior | High Elf | Windswept Jade, Cloud White, Pale Silver | Pale sky-blue eyes / Silvery-blonde hair / Fair | Lean Martial / Aerodynamic Duelist |
| **SD-020** | Malakor Venomcaller | Poison | Assassin | Orc | Toxic Orchid Magenta, Tarnished Brass, Charcoal Black | Acid-green eyes / Black hair / Deep olive-toned | Brutal / Coiled Stalker |

---

## 3. Individual Character JSON-Ready Specifications

### SD-011: Draknare Thorne
* **Card ID:** `HERO_DRAKNARE_THORNE`
* **Element / Class / Race:** Darkness | Shadow Knight | Human
* **Physique Profile:** Imposing athletic tank build; broad-shouldered, tall, commanding warrior posture.
* **Palette & Cosmetics:**
  * primaryColor: "Obsidian Black", accentColors: ["Tarnished Silver", "Deep Amethyst"], magicColor: "violet shadow"
  * eyeColor: "Deep violet iris with obsidian limbal ring, faint shadow striations"
  * hairColor: "Rich black hair, short and neatly cropped"
  * skinTone: "Pale, cool-toned complexion, evenly toned"
  * eyeColorNegatives: ["blue eyes", "green eyes", "brown eyes", "hazel eyes", "amber eyes"]
  * skinColorNegatives: ["ruddy skin", "sunburnt skin", "overly tanned skin"]
  * hairColorNegatives: ["brown hair", "grey hair", "blonde hair"]
* **Physique Block:**
  * build: "Imposing athletic tank build; broad-shouldered, tall and commanding"
  * chest: "Deep, powerful chest tapering into a disciplined waist"
  * arms: "Broad, squared shoulders with defined deltoids; muscular forearms with prominent vascular definition"
  * waist: "Firm, flat athletic midsection with subtle core definition; narrow athletic hips"
  * legs: "Strong, heavily muscled legs"
  * distinguishingMarks: []
  * raceAlignment: "Human presentation aligned to heavy dread-knight characteristics (imposing, tactical, unyielding authority)"

---

### SD-012: Ignis Emberstride
* **Card ID:** `HERO_IGNIS_EMBERSTRIDE`
* **Element / Class / Race:** Fire | Warrior | Human
* **Physique Profile:** Chiseled athletic striker build; functional swordsman frame with high explosive power.
* **Palette & Cosmetics:**
  * primaryColor: "Ember Red", accentColors: ["Burnished Bronze", "Charcoal Black"], magicColor: "fiery orange"
  * eyeColor: "Molten amber iris with dark charcoal limbal ring, faint ember striations"
  * hairColor: "Dark auburn hair, short and windswept"
  * skinTone: "Warm sun-bronzed complexion, evenly tanned"
  * eyeColorNegatives: ["blue eyes", "green eyes", "grey eyes", "violet eyes"]
  * skinColorNegatives: ["pale skin", "fair skin", "washed-out skin"]
  * hairColorNegatives: ["black hair", "bright orange hair", "blonde hair"]
* **Physique Block:**
  * build: "Chiseled athletic striker build; functional swordsman frame with explosive power"
  * chest: "Pronounced athletic V-taper with defined pectorals"
  * arms: "Sculpted deltoids; powerful biceps and conditioned forearms"
  * waist: "Tight, flat core with visible upper abdominal tone and serratus definition; narrow, mobile hips"
  * legs: "Toned, spring-loaded thighs"
  * distinguishingMarks: ["faint forge-burn scars on the forearms"]
  * raceAlignment: "Human presentation aligned to frontline vanguard warrior characteristics (forged, explosive, high stamina)"

---

### SD-013: Nizaras Featherstone
* **Card ID:** `HERO_NIZARAS_FEATHERSTONE`
* **Element / Class / Race:** Grass | Rogue | Wood Elf
* **Physique Profile:** Lithe, sinewy wood-elven scout build; ultra-lean, flexible, long-limbed silhouette.
* **Palette & Cosmetics:**
  * primaryColor: "Forest Green", accentColors: ["Moss Brown", "Pale Gold"], magicColor: "bright leaf-green"
  * eyeColor: "Verdant green iris with mossy-brown limbal ring, faint golden striations"
  * hairColor: "Dark umber hair with a faint mossy-green sheen, short and tousled"
  * skinTone: "Light olive complexion, evenly toned"
  * eyeColorNegatives: ["blue eyes", "brown eyes", "grey eyes", "red eyes"]
  * skinColorNegatives: ["pale skin", "ruddy skin", "overly tanned skin"]
  * hairColorNegatives: ["black hair", "all-over green hair", "blonde hair"]
* **Physique Block:**
  * build: "Lithe, sinewy wood-elven scout build; ultra-lean, flexible and long-limbed"
  * chest: "Lean chest over a light, agile ribcage"
  * arms: "Slender, defined shoulders; corded, fibrous forearms with pronounced tendons"
  * waist: "Compact, flat midriff with distinct oblique fluting; narrow waist and narrow, flexible hips"
  * legs: "Long, lean runner legs with high, springy calves"
  * distinguishingMarks: []
  * raceAlignment: "Wood elf presentation aligned to canopy tracker characteristics (whiplash agility, low body fat, corded sinew)"

---

### SD-014: Lyran Frostfall
* **Card ID:** `HERO_LYRAN_FROSTFALL`
* **Element / Class / Race:** Ice | Knight | High Elf
* **Physique Profile:** Tall, statuesque high-elven knight; aristocratic, perfectly symmetrical athletic frame.
* **Palette & Cosmetics:**
  * primaryColor: "Glacial Cyan", accentColors: ["Frost White", "Steel Grey"], magicColor: "icy cyan"
  * eyeColor: "Glacial cyan iris with deep navy limbal ring, faint frost striations"
  * hairColor: "Platinum-blonde hair, short and neatly combed"
  * skinTone: "Fair, cool-toned complexion, evenly toned"
  * eyeColorNegatives: ["brown eyes", "green eyes", "amber eyes", "red eyes"]
  * skinColorNegatives: ["ruddy skin", "sunburnt skin", "overly tanned skin"]
  * hairColorNegatives: ["yellow-gold hair", "grey hair", "white hair with blue tint"]
* **Physique Block:**
  * build: "Tall, statuesque high-elven knight; aristocratic, symmetrical athletic frame"
  * chest: "Firm, sculpted athletic chest with smooth contours"
  * arms: "Square, elevated shoulders; long, powerful arms with clean, elegant muscle and fine wrists"
  * waist: "Unblemished flat core with a clean vertical line; narrow, elegant hips"
  * legs: "Exceptionally long, straight legs"
  * distinguishingMarks: []
  * raceAlignment: "High elf presentation aligned to royal knight bastion characteristics (geometric balance, unyielding poise, crystalline nobility)"

---

### SD-015: Corin Tidewalker
* **Card ID:** `HERO_CORIN_TIDEWALKER`
* **Element / Class / Race:** Water | Beast Lord | Human
* **Physique Profile:** Lean, powerful swimmer build; broad back, wiry endurance frame conditioned by wind and tide.
* **Palette & Cosmetics:**
  * primaryColor: "Deep Oceanic Blue", accentColors: ["Seafoam Green", "Driftwood Tan"], magicColor: "aqua"
  * eyeColor: "Deep teal iris with dark navy limbal ring, faint seafoam striations"
  * hairColor: "Sun-streaked brown hair, short and wind-tousled"
  * skinTone: "Sun-weathered tan complexion, evenly toned"
  * eyeColorNegatives: ["brown eyes", "grey eyes", "amber eyes", "violet eyes"]
  * skinColorNegatives: ["pale skin", "fair skin", "washed-out skin"]
  * hairColorNegatives: ["all-over blonde hair", "grey hair", "black hair"]
* **Physique Block:**
  * build: "Lean, powerful swimmer build; broad back and a wiry endurance frame"
  * chest: "Wide latissimus taper over a strong chest"
  * arms: "Mobile, rounded deltoids; strong, rope-weathered forearms with prominent grip strength"
  * waist: "Lean, flat midriff with visible functional core definition and serratus; grounded athletic hips"
  * legs: "Dense, balanced legs built for steady footing"
  * distinguishingMarks: []
  * raceAlignment: "Human presentation aligned to pelagic vanguard characteristics (swimmer back, functional endurance, sea-weathered resilience)"

---

### SD-016: Hauk Hammerfell
* **Card ID:** `HERO_HAUK_HAMMERFELL`
* **Element / Class / Race:** Light | Paladin | Human
* **Physique Profile:** Massive, powerful tank physique; dense heavy-armor frame with broad structural mass.
* **Palette & Cosmetics:**
  * primaryColor: "Radiant Rose Gold", accentColors: ["Ivory White", "Polished Bronze"], magicColor: "warm golden-white"
  * eyeColor: "Radiant amber-gold iris with warm bronze limbal ring, faint golden striations"
  * hairColor: "Golden-blonde hair, short and neatly combed"
  * skinTone: "Warm, sun-kissed complexion, evenly toned"
  * eyeColorNegatives: ["blue eyes", "green eyes", "grey eyes", "violet eyes"]
  * skinColorNegatives: ["pale skin", "fair skin", "washed-out skin"]
  * hairColorNegatives: ["brown hair", "white hair", "red hair"]
* **Physique Block:**
  * build: "Massive, powerful tank physique; dense heavy-armor frame with broad structural mass"
  * chest: "Deep barrel chest"
  * arms: "Heavily developed trapezius and deltoids; thick forearms and broad hands"
  * waist: "Thick, powerful abdominal wall; solid, wide waistline and a sturdy pelvis"
  * legs: "Heavy, pillar-like thighs and dense calves"
  * distinguishingMarks: []
  * raceAlignment: "Human presentation aligned to holy bastion characteristics (unshakeable mass, dense muscle wall, radiant vanguard authority)"

---

### SD-017: Torvald Stonebreaker
* **Card ID:** `HERO_TORVALD_STONEBREAKER`
* **Element / Class / Race:** Earth | Berserker | Barbarian
* **Physique Profile:** Massive, raw-boned barbarian powerhouse; thick heavy frame with colossal functional mass.
* **Palette & Cosmetics:**
  * primaryColor: "Deep Rust Brown", accentColors: ["Iron Grey", "Warm Sand"], magicColor: "warm amber"
  * eyeColor: "Deep umber iris with dark iron limbal ring, faint rust striations"
  * hairColor: "Dark brown hair, short and rugged"
  * skinTone: "Deep sun-weathered tan complexion, evenly toned"
  * eyeColorNegatives: ["blue eyes", "green eyes", "grey eyes", "violet eyes"]
  * skinColorNegatives: ["pale skin", "fair skin", "washed-out skin"]
  * hairColorNegatives: ["black hair", "blonde hair", "red hair"]
* **Physique Block:**
  * build: "Massive, raw-boned barbarian powerhouse; thick, heavy frame with colossal functional mass"
  * chest: "Wide, dense ribcage and a heavy chest"
  * arms: "Massive neck and heavy trapezius merging into dense shoulders; thick, heavy forearms"
  * waist: "Thick powerlifter abdominal wall with massive oblique slabs; broad, heavy-boned hips"
  * legs: "Huge, tree-trunk thighs and dense calves"
  * distinguishingMarks: ["faint battle scars across the chest and left shoulder"]
  * raceAlignment: "Barbarian presentation aligned to primal mountain juggernaut characteristics (thick skeletal density, raw power, heavy mass)"

---

### SD-018: Dorian Stormstrike
* **Card ID:** `HERO_DORIAN_STORMSTRIKE`
* **Element / Class / Race:** Lightning | Monk | Celestial
* **Physique Profile:** Hyper-conditioned celestial martial artist build; ultra-dense, razor-defined kinetic silhouette.
* **Palette & Cosmetics:**
  * primaryColor: "Storm Gold", accentColors: ["Arc White", "Storm Grey"], magicColor: "white-hot electric"
  * eyeColor: "Electric cobalt iris with midnight-indigo limbal ring, faint arc-white striations"
  * hairColor: "Jet-black hair, short and neatly cropped"
  * skinTone: "Warm golden-tan complexion, evenly toned"
  * eyeColorNegatives: ["brown eyes", "green eyes", "grey eyes", "red eyes"]
  * skinColorNegatives: ["pale skin", "fair skin", "washed-out skin"]
  * hairColorNegatives: ["brown hair", "grey hair", "blonde hair"]
* **Physique Block:**
  * build: "Hyper-conditioned celestial martial artist build; ultra-dense, razor-defined silhouette"
  * chest: "Carved chest with deep serratus contours"
  * arms: "Striated deltoids and triceps; calloused, conditioned hands"
  * waist: "Tight midriff with chiselled abdominal definition; narrow waist and narrow hips"
  * legs: "Tightly coiled athletic legs"
  * distinguishingMarks: []
  * raceAlignment: "Celestial presentation aligned to barehanded kinetic conduit characteristics (zero body fat, wire-taut muscle, electric stillness)"

---

### SD-019: Zephyr Galeheart
* **Card ID:** `HERO_ZEPHYR_GALEHEART`
* **Element / Class / Race:** Wind | Warrior | High Elf
* **Physique Profile:** Tall, aerodynamic high-elven swordsman; lithe, graceful athletic frame with long reach.
* **Palette & Cosmetics:**
  * primaryColor: "Windswept Jade", accentColors: ["Cloud White", "Pale Silver"], magicColor: "pale silver-jade"
  * eyeColor: "Pale sky-blue iris with silver limbal ring, faint cyan striations"
  * hairColor: "Silvery-blonde hair, short and windswept"
  * skinTone: "Fair, cool-toned complexion, evenly toned"
  * eyeColorNegatives: ["brown eyes", "green eyes", "amber eyes", "red eyes"]
  * skinColorNegatives: ["ruddy skin", "sunburnt skin", "overly tanned skin"]
  * hairColorNegatives: ["golden-yellow hair", "grey hair", "white hair"]
* **Physique Block:**
  * build: "Tall, aerodynamic high-elven swordsman; lithe, graceful athletic frame with long reach"
  * chest: "Smooth pectoral contours without bulk"
  * arms: "Broad, flexible shoulders; long, slender arms"
  * waist: "Clean, flat athletic stomach with a natural narrow waist taper; slender hips"
  * legs: "Long, elegant duelist legs"
  * distinguishingMarks: []
  * raceAlignment: "High elf presentation aligned to wind duelist characteristics (aerodynamic reach, parrying leverage, unforced grace)"

---

### SD-020: Malakor Venomcaller
* **Card ID:** `HERO_MALAKOR_VENOMCALLER`
* **Element / Class / Race:** Poison | Assassin | Orc
* **Physique Profile:** Dense yet agile orcish assassin build; heavy bone structure stripped down to corded predator muscle.
* **Palette & Cosmetics:**
  * primaryColor: "Toxic Orchid Magenta", accentColors: ["Tarnished Brass", "Charcoal Black"], magicColor: "sickly lime-green"
  * eyeColor: "Acid-green iris with blackened limbal ring, faint toxic-violet striations"
  * hairColor: "Black hair, short and slicked back"
  * skinTone: "Deep olive-toned complexion, evenly toned"
  * eyeColorNegatives: ["blue eyes", "brown eyes", "grey eyes", "amber eyes"]
  * skinColorNegatives: ["pale skin", "fair skin", "washed-out skin"]
  * hairColorNegatives: ["brown hair", "purple hair", "grey hair"]
* **Physique Block:**
  * build: "Dense yet agile orcish assassin build; heavy bone structure stripped down to corded muscle"
  * chest: "Broad chest with a heavy ribcage"
  * arms: "Thick, muscular shoulders; long, heavy arms with knotty forearm cords"
  * waist: "Tight, conditioned midsection; heavy, low-slung hips"
  * legs: "Powerful, bowed legs with thick calves"
  * distinguishingMarks: ["subtle ritual scarification lines along the jaw and forearms"]
  * raceAlignment: "Orcish presentation aligned to predatory stalker characteristics (dense jaw and neck architecture, leathery hide, silent lethal momentum)"

---

## 4. How the Fields Reach the Prompt

The real prompt is assembled from the shared templates in `data/art/_templates/heroes/` by `tools/generators/gen_prompt.py`, not from a fixed concatenation. The Drakn Bound men still use the older single Prime card (`<Name>_X_Pose`, template `pose-male-human.txt`), not the 1_Alpha chain the sisters and angels use:

| Field | Where it goes |
| --- | --- |
| `build`, `chest`, `arms`, `waist`, `legs`, `distinguishingMarks` | The `Figure:` line of the Prime, so the whole individual build is set at the first pass |
| `skinTone`, `hairColor`, `eyeColor` | The `Skin:`, `Hair:` and `Eyes:` lines, with the three negative lists in the negative prompt |
| Underlayer | The fitted swim brief in `primaryColor`, bare feet |

Moving the Drakn Bound set to the 1_Alpha chain (standard figure at 1_Prime, individual build at 2_Bare, like the angels) is an open item in `docs/STATUS.md`. The text of each field is the identity JSON (`data/art/heroes/drakn-bound/`); the section 3 blocks above mirror it.

---

## 5. Build Rationale

Unlike the sisters, who share one family skeleton, the ten Drakn Bound men are separate people of different races and roles, so their
builds are a deliberate range from lean to massive. Each build follows race and class; none of them is left to the photo. Tone and mass
are welcome here, because the men are fighters (the limit that applies to the women, no body-builder look, does not apply to them).

| Hero | Race, class | Build | Why |
| --- | --- | --- | --- |
| Draknare | Human, Shadow Knight | Imposing athletic tank, tall, heavily muscled legs | The commander of the line; heavy armor needs a heavy frame |
| Ignis | Human, Warrior | Chiseled athletic striker | A greatsword striker: explosive, not massive |
| Nizaras | Wood Elf, Rogue | Lithe, sinewy, ultra-lean | A woodland infiltrator: light, flexible, quiet |
| Lyran | High Elf, Knight | Tall, statuesque, symmetrical | An aristocratic bastion: long and regal rather than bulky |
| Corin | Human, Beast Lord | Lean swimmer, broad back, wiry endurance | A pelagic vanguard: endurance over mass |
| Hauk | Human, Paladin | Massive tank, pillar-like thighs | The unyielding bulwark; the heaviest of the humans |
| Torvald | Barbarian, Berserker | Massive, raw-boned powerhouse, tree-trunk thighs | The juggernaut of the set |
| Dorian | Celestial, Monk | Hyper-conditioned, razor-defined, coiled legs | A kinetic martial artist: dense but not bulky |
| Zephyr | High Elf, Warrior | Tall, aerodynamic, long reach | An aerial duelist: lithe and graceful |
| Malakor | Orc, Assassin | Dense yet agile, corded muscle, bowed legs | A coiled stalker: orcish mass stripped down to speed |

The same mixture (lean, heroic, heavy by element and role) is used for the Angel Primes men; see
[angel_primes_physique.md](./angel_primes_physique.md). The sisters' rationale is in [drakn_sisters_physique.md](./drakn_sisters_physique.md).
