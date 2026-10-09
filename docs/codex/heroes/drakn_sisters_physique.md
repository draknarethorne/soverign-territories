# Sovereign Territories — Hero Card Roster: Transcendent Tier (SD-001 – SD-010)
## Character Architecture & Physical Specification Matrix (Revised Schema Alignment)

---

## 1. Master Bloodline Architecture: Shared Skeletal Core vs. Elemental Phenotype

Based on the authoritative `HERO_DRAKNARA_THORNE.json` schema, the Transcendent Drakn Sisters divide into two distinct layers:

### The Shared Skeletal & Foundation Core (Universal)
* **Bust:** every sister has her own bust shape in her `bust` field (round, teardrop, conical, compact, soft and generous), all full, high and lifted, with a deep, crisp, clearly defined cleavage. The 1_Prime prompt carries a shared key detail (`bustKey` in `data/art/_settings/phrases.json`) that sets the bust before anything else, so it overrides a smaller bust in the source photo.
* **Frame & Silhouette:** narrow waist, shapely feminine hips (gently curved) and very long legs. This is the family standard, so ten sisters read as one bloodline. What differs is the build preset (section 5), the amount of visible tone in the abs, arms and legs, and the race.
* **Studio Base Uniform:** high-gloss metallic triangle bikini underlayer (`defaultUnderlayer`), bare feet in the A-pose (the studio default `aPoseFootwear: barefoot` in `data/art/_settings/studio.json`; each sister's signature heels are her `defaultFootwear` and appear in the Heels cards), high-gloss skin finish (`defaultSheen`).
* **Master Canvas Standard:** `944 × 1104` with studio cream padding (`#F5F0E6`), scaling to `1080 × 1350` (4:5) for final mobile card production.

### The Elemental Glamour Phenotype (Individualized)
* Each sister carries an individualized racial/elemental phenotype across **hair, eyes, skin tone, cosmetics, and metals**, complete with strict negative prompts to prevent cross-bleeding (e.g., Draknara explicitly banning violet eyes and pale skin in favor of malachite-hazel and terracotta tan).
* Hair, eye and skin colour are forced at 1_Prime (the Critical details block) so the photo is changed to match; the full individual build and bust are applied at 2_Bare (`python tools/art/identity_audit.py` checks this for every hero).

---

## 2. Master Card Registry & Phenotype Alignment

| Card ID | Card Name | Element | Class | Race Presentation | Primary Colors & Metals | Eye / Hair / Skin Phenotype | Physical Preset Category |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **SD-001** | Drakness Thorne | Darkness | Necromancer | Dark Elf | Midnight Violet, Vibrant Amethyst, Polished Silver | Deep violet eyes / Rich black hair / Warm deep sun-kissed golden-bronze tan | Ethereal & Aristocratic (Predatory) |
| **SD-002** | Draknora Thorne | Fire | Magician | Human | Flame Red, Burnished Gold, Vibrant Orange, Burnished Copper | Molten amber eyes / Vivid copper-red hair / Warm sun-bronzed olive tan | Ethereal & Aristocratic (Statuesque) |
| **SD-003** | Drakniya Thorne | Grass | Druid | Wood Elf | Emerald Green, Forest Sage, Moss Gold, Antique Gold | Deep forest-emerald eyes / Honey-blonde hair / Warm sun-kissed golden-olive tan | Agile & Gymnastic (Runner) |
| **SD-004** | Draknira Thorne | Ice | Wizard | High Elf | Glacial Cyan, Frost White, Brushed Chrome | Glacial cyan eyes / Icy platinum-ash blonde hair / Cool fair porcelain | Ethereal & Aristocratic (Crystalline) |
| **SD-005** | Draknisa Thorne | Water | Enchanter | Human | Deep Oceanic Blue, Deep Teal, Polished Platinum | Deep sapphire eyes / Dark chocolate-brown hair / Warm sun-kissed medium tan | Ethereal & Aristocratic (Serpentine) |
| **SD-006** | Drakniss Thorne | Light | Cleric | Human | Radiant Rose Gold, Radiant Gold, Polished White Gold | Radiant topaz-gold eyes / Pale luminous champagne-gold blonde hair / Warm radiant fair-golden tan | Grounded & Martial (Armored Endurance) |
| **SD-007** | Draknara Thorne | Earth | Shaman | Barbarian | Deep Burnt Sienna, Vivid Turquoise, Antique Bronze | Rich malachite-hazel eyes / Medium bronze-brown hair / Deep sun-weathered terracotta tan | Grounded & Martial (Taut Core) |
| **SD-008** | Drakneta Thorne | Lightning | Summoner | Celestial | Electric Gold, Arc White, Bright Gold | Dark storm-charcoal eyes / Light golden-brown dark-blonde hair / Warm golden tan | Ethereal & Aristocratic (Kinetic) |
| **SD-009** | Draknava Thorne | Wind | Bard | Wood Elf | Windswept Jade, Gossamer Silver, Polished Nickel | Silver-grey eyes / Soft silvery ash hair / Light sun-kissed fair tan | Agile & Gymnastic (Coiled Agility) |
| **SD-010** | Draknoxa Thorne | Poison | Alchemist | Dark Elf | Toxic Orchid Magenta, Vibrant Acid Lime, Tarnished Brass | Acid lime-emerald eyes / Deep dark burgundy-black hair / Pale olive | Agile & Gymnastic (Clinical/Predatory) |

---

## 3. Individual Character JSON-Ready Specifications

### SD-001: Drakness Thorne
* **Card ID:** `HERO_DRAKNESS_THORNE`
* **Element / Class / Race:** Darkness | Necromancer | Dark Elf
* **Physique Profile:** Aristocratic, predatory-lithe with sinewy tension.
* **Palette & Cosmetics:**
  * primaryColor: "Midnight Violet", accentColors: ["Vibrant Amethyst", "Polished Silver"], metal: "polished silver"
  * eyeColor: "Deep violet iris with obsidian limbal ring, radiating amethyst striations, and luminous lilac flecks"
  * hairColor: "Rich black hair with warm espresso depth"
  * skinTone: "Warm deep sun-kissed golden-bronze tan complexion, evenly tanned"
  * eyeColorNegatives: ["blue eyes", "green eyes", "brown eyes", "grey eyes", "hazel eyes", "amber eyes", "red eyes"]
  * skinColorNegatives: ["pale skin", "fair skin", "washed-out skin"]
  * hairColorNegatives: ["uniform flat one-tone hair", "fully dyed hair"]
* **Physique Block:**
  * build: "Slender, long-limbed build with an aristocratic dark-elven bearing and sinewy tension"
  * torso: "Ultra-narrow, tightly cinched waistline; smooth flat midriff"
  * bust: "Full, rounded, naturally heavy bust with a soft inner swell and a smooth, weighted curve, generous natural detail, lifted and pressed toward the centre; the inner curves meeting at the centre line in a deep, crisp, clearly defined cleavage, held firm and high; realistic skin texture and natural, anatomically accurate detail"
  * arms: "Slender arms with delicate wrists and elongated fingers; slight wiry tension in the forearms"
  * hips: "Shapely feminine hips, gently curved, with a high, tapering hip line"
  * legs: "Very long, slender legs with elegant tapering down to slim ankles"
  * distinguishingMarks: []
  * raceAlignment: "Human presentation aligned to dark elf characteristics (sinewy elegance, aristocratic detachment)"

---

### SD-002: Draknora Thorne
* **Card ID:** `HERO_DRAKNORA_THORNE`
* **Element / Class / Race:** Fire | Magician | Human
* **Physique Profile:** Warm, statuesque, and dignified.
* **Palette & Cosmetics:**
  * primaryColor: "Flame Red", accentColors: ["Burnished Gold", "Vibrant Orange"], metal: "burnished copper"
  * eyeColor: "Molten amber iris with dark charcoal limbal ring, radiating crimson striations, and fiery gold flecks"
  * hairColor: "Vivid copper-red hair, warm and glossy"
  * skinTone: "Warm sun-bronzed olive tan complexion, evenly tanned"
  * eyeColorNegatives: ["blue eyes", "green eyes", "brown eyes", "grey eyes", "hazel eyes", "violet eyes"]
  * skinColorNegatives: ["pale skin", "fair skin", "washed-out skin"]
  * hairColorNegatives: ["all-over blonde hair", "fully dyed hair"]
* **Physique Block:**
  * build: "Lithe, statuesque build with a balanced, dignified bearing"
  * torso: "Smooth flat stomach with soft natural curves into the hips; narrow waist"
  * bust: "Very full, generous bust, firm and lifted with a deep rounded curve, generous natural detail, pressed together at the centre; the inner curves meeting at the centre line in a deep, crisp, clearly defined cleavage, held firm and high; realistic skin texture and natural, anatomically accurate detail"
  * arms: "Slender, smooth arms with soft natural curves; unblemished hands"
  * hips: "Shapely feminine hips, gently curved, with a natural hourglass silhouette"
  * legs: "Very long, gracefully proportioned legs with smooth contours"
  * distinguishingMarks: []
  * raceAlignment: "Human presentation aligned to high human evoker characteristics (noble, poised, radiant warmth)"

---

### SD-003: Drakniya Thorne
* **Card ID:** `HERO_DRAKNIYA_THORNE`
* **Element / Class / Race:** Grass | Druid | Wood Elf
* **Physique Profile:** Wiry, low-fat runner build with trackless agility.
* **Palette & Cosmetics:**
  * primaryColor: "Emerald Green", accentColors: ["Forest Sage", "Moss Gold"], metal: "antique gold"
  * eyeColor: "Deep forest-emerald iris with dark pine limbal ring, radiating sage striations, and warm gold flecks"
  * hairColor: "Honey-blonde hair with rich chestnut-brown lowlights"
  * skinTone: "Warm sun-kissed golden-olive tan complexion, evenly tanned"
  * eyeColorNegatives: ["blue eyes", "brown eyes", "grey eyes", "hazel eyes", "amber eyes", "red eyes", "violet eyes"]
  * skinColorNegatives: ["pale skin", "fair skin", "washed-out skin"]
  * hairColorNegatives: ["all-over green hair", "fully dyed hair"]
* **Physique Block:**
  * build: "Lithe, wiry athletic build; low-fat runner physique with wood-elven agility"
  * torso: "Tight, lithe midriff with faint oblique fluting and subtle vertical definition; slender waist tapering cleanly into the hips"
  * bust: "Full, firm bust with a gently rounded, softly proportioned shape and fine, delicate natural detail, lifted high and pressed toward the centre line; the inner curves meeting at the centre line in a deep, crisp, clearly defined cleavage, held firm and high; realistic skin texture and natural, anatomically accurate detail"
  * arms: "Slender, lightly defined arms; subtle deltoid contours and lithe forearms"
  * hips: "Shapely feminine hips, gently curved, with an athletic pelvis"
  * legs: "Very long, lean athletic legs; subtly toned quadriceps and elongated calves"
  * distinguishingMarks: []
  * raceAlignment: "Human presentation aligned to wood elf characteristics (agile, trackless, low-fat runner vitality)"

---

### SD-004: Draknira Thorne
* **Card ID:** `HERO_DRAKNIRA_THORNE`
* **Element / Class / Race:** Ice | Wizard | High Elf
* **Physique Profile:** Crystalline, ethereal, and aloof.
* **Palette & Cosmetics:**
  * primaryColor: "Glacial Cyan", accentColors: ["Frost White", "Brushed Chrome"], metal: "brushed chrome"
  * eyeColor: "Glacial cyan iris with deep navy limbal ring, radiating frost-silver striations, and crystalline white flecks"
  * hairColor: "Icy platinum-ash blonde hair, sleek and sultry with a subtle silver-frost sheen"
  * skinTone: "Cool fair porcelain complexion, evenly toned, smooth and blemish-free"
  * eyeColorNegatives: ["green eyes", "brown eyes", "grey eyes", "hazel eyes", "amber eyes", "red eyes", "violet eyes"]
  * skinColorNegatives: ["ruddy skin", "sunburnt skin", "overly tanned skin"]
  * hairColorNegatives: ["all-over grey hair", "all-over cyan hair", "all-over blue hair", "fully dyed hair"]
* **Physique Block:**
  * build: "Ethereal, crystalline high-elven build; ultra-slender, with delicate bone structure"
  * torso: "Completely flat stomach; tight, elegant waist tapering cleanly into the hips"
  * bust: "Full, noticeably enlarged bust with a high, slightly conical, pointed shape - delicate natural detail, lifted high and pressed toward the centre line; the inner curves meeting at the centre line in a deep, crisp, clearly defined cleavage, held firm and high; realistic skin texture and natural, anatomically accurate detail"
  * arms: "Very slender, delicate arms; paper-fine wrists and long, slender fingers"
  * hips: "Shapely feminine hips, gently curved, narrow and elegant"
  * legs: "Extremely long, smooth, slender legs"
  * distinguishingMarks: []
  * raceAlignment: "Human presentation aligned to high elf characteristics (regal detachment, crystalline geometry)"

---

### SD-005: Draknisa Thorne
* **Card ID:** `HERO_DRAKNISA_THORNE`
* **Element / Class / Race:** Water | Enchanter | Human
* **Physique Profile:** Fluid, serpentine dancer with a supple hourglass.
* **Palette & Cosmetics:**
  * primaryColor: "Deep Oceanic Blue", accentColors: ["Deep Teal", "Polished Platinum"], metal: "polished platinum"
  * eyeColor: "Deep sapphire iris with oceanic indigo limbal ring, radiating deep teal striations, and pearl-white flecks"
  * hairColor: "Dark chocolate-brown hair, glossy and deep"
  * skinTone: "Warm sun-kissed medium tan complexion, evenly tanned"
  * eyeColorNegatives: ["green eyes", "brown eyes", "grey eyes", "hazel eyes", "amber eyes", "red eyes", "violet eyes"]
  * skinColorNegatives: ["pale skin", "fair skin", "washed-out skin"]
  * hairColorNegatives: ["all-over teal hair", "all-over blue hair", "fully dyed hair"]
* **Physique Block:**
  * build: "Lithe, supple dancer physique with flowing, serpentine human grace"
  * torso: "Soft, completely flat midriff tapering smoothly into an exceptionally narrow waist"
  * bust: "Full, firm, classically proportioned bust, softly rounded and well supported with natural medium detail, lifted high and pressed together at the centre; the inner curves meeting at the centre line in a deep, crisp, clearly defined cleavage, held firm and high; realistic skin texture and natural, anatomically accurate detail"
  * arms: "Smooth, slender arms with graceful wrists"
  * hips: "Shapely feminine hips, gently curved, with supple, pronounced curves"
  * legs: "Very long, smooth, slender legs with dancer-like fluid lines"
  * distinguishingMarks: []
  * raceAlignment: "Human presentation aligned to courtly enchanter characteristics (alluring, serpentine, hypnotic ease)"

---

### SD-006: Drakniss Thorne
* **Card ID:** `HERO_DRAKNISS_THORNE`
* **Element / Class / Race:** Light | Cleric | Human
* **Physique Profile:** Armored athletic endurance with regal martial poise.
* **Palette & Cosmetics:**
  * primaryColor: "Radiant Rose Gold", accentColors: ["Radiant Gold", "Polished White Gold"], metal: "radiant rose gold"
  * eyeColor: "Radiant topaz-gold iris with warm bronze limbal ring, radiating solar champagne striations, and ivory flecks"
  * hairColor: "Pale luminous champagne-gold blonde hair, soft and sultry with a gentle radiant sheen"
  * skinTone: "Warm radiant fair-golden tan complexion, evenly tanned"
  * eyeColorNegatives: ["blue eyes", "green eyes", "brown eyes", "grey eyes", "hazel eyes", "red eyes", "violet eyes"]
  * skinColorNegatives: ["pale skin", "fair skin", "washed-out skin"]
  * hairColorNegatives: ["all-over yellow hair", "all-over pink hair", "fully dyed hair"]
* **Physique Block:**
  * build: "Lithe yet taut athletic build; firm, disciplined warrior-cleric bearing"
  * torso: "Flat, firm midriff with subtle core tone and a faint vertical linea alba; tight waist tapering into the hips"
  * bust: "Very full, ample bust with a generous, softly rounded shape and a heavy natural swell, generous natural detail, lifted and pressed together at the centre; the inner curves meeting at the centre line in a deep, crisp, clearly defined cleavage, held firm and high; realistic skin texture and natural, anatomically accurate detail"
  * arms: "Slender, defined arms; light deltoid contours and firm forearms"
  * hips: "Shapely feminine hips, gently curved, square and grounded"
  * legs: "Very long, toned athletic legs with firm quadriceps contours"
  * distinguishingMarks: []
  * raceAlignment: "Human presentation aligned to holy crusader characteristics (disciplined, steadfast, enduring light)"

---

### SD-007: Draknara Thorne
* **Card ID:** `HERO_DRAKNARA_THORNE`
* **Element / Class / Race:** Earth | Shaman | Barbarian
* **Physique Profile:** Taut, grounded athletic core with primal tone.
* **Palette & Cosmetics:**
  * primaryColor: "Deep Burnt Sienna", accentColors: ["Vivid Turquoise", "Antique Bronze"], metal: "antique bronze"
  * eyeColor: "Rich malachite-hazel iris with dark umber limbal ring, radiating terracotta striations, and warm amber flecks"
  * hairColor: "Medium bronze-brown hair, rich and warm"
  * skinTone: "Deep sun-weathered terracotta tan complexion, evenly tanned"
  * eyeColorNegatives: ["blue eyes", "brown eyes", "grey eyes", "red eyes", "violet eyes"]
  * skinColorNegatives: ["pale skin", "fair skin", "washed-out skin"]
  * hairColorNegatives: ["all-over blonde hair", "fully dyed hair"]
* **Physique Block:**
  * build: "Lithe yet taut athletic build; slender, long-limbed, functionally fit with subtle warrior muscle tone"
  * torso: "Flat, firm midriff with subtle abdominal tone; faint vertical linea alba and soft oblique contours; tight waist tapering cleanly into the hips"
  * bust: "Full, noticeably enlarged bust with a high, youthful, perky lift - firm and upright, small refined natural detail, lifted and pressed toward the centre line; the inner curves meeting at the centre line in a deep, crisp, clearly defined cleavage, held firm and high; realistic skin texture and natural, anatomically accurate detail"
  * arms: "Slender, lightly defined arms; faint deltoid contours and toned forearms without bulk"
  * hips: "Shapely feminine hips, gently curved"
  * legs: "Very long, lean athletic legs; subtly toned thighs and slender calves with graceful definition"
  * distinguishingMarks: []
  * raceAlignment: "Human presentation aligned to barbarian characteristics (strong, grounded, sun-touched resilience)"

---

### SD-008: Drakneta Thorne
* **Card ID:** `HERO_DRAKNETA_THORNE`
* **Element / Class / Race:** Lightning | Summoner | Celestial
* **Physique Profile:** Statuesque, radiant, and kinetic.
* **Palette & Cosmetics:**
  * primaryColor: "Electric Gold", accentColors: ["Arc White", "Bright Gold"], metal: "bright gold"
  * eyeColor: "Dark storm-charcoal, almost black iris with a thin bright electric-gold limbal ring, radiating white-hot gold striations, and spark-white flecks"
  * hairColor: "Light golden-brown dark-blonde hair, sleek and sultry"
  * skinTone: "Warm golden tan complexion, evenly tanned"
  * eyeColorNegatives: ["blue eyes", "green eyes", "grey eyes", "hazel eyes", "red eyes", "violet eyes", "amber eyes", "topaz eyes", "light brown eyes"]
  * skinColorNegatives: ["pale skin", "fair skin", "washed-out skin"]
  * hairColorNegatives: ["all-over blue hair", "all-over cyan hair", "fully dyed hair"]
* **Physique Block:**
  * build: "Tall, statuesque celestial build; ultra-long-limbed, commanding and radiant"
  * torso: "Taut, perfectly flat midriff; narrow waistline with seamless transitions into the hips"
  * bust: "Full, generous, well-rounded bust, firm and high with a pronounced inner curve, generous natural detail, lifted and pressed toward the centre; the inner curves meeting at the centre line in a deep, crisp, clearly defined cleavage, held firm and high; realistic skin texture and natural, anatomically accurate detail"
  * arms: "Long, slender arms with fine, elegant hands"
  * hips: "Shapely feminine hips, gently curved, narrow and regal, with a high-waisted line"
  * legs: "Exceptionally long, statuesque legs with sharp, clean shin contours"
  * distinguishingMarks: []
  * raceAlignment: "Human presentation aligned to celestial herald characteristics (statuesque, kinetic, high-voltage presence)"

---

### SD-009: Draknava Thorne
* **Card ID:** `HERO_DRAKNAVA_THORNE`
* **Element / Class / Race:** Wind | Bard | Wood Elf
* **Physique Profile:** Gymnastic, coiled-spring agility.
* **Palette & Cosmetics:**
  * primaryColor: "Windswept Jade", accentColors: ["Gossamer Silver", "Polished Nickel"], metal: "polished nickel"
  * eyeColor: "Silver-grey iris with deep slate limbal ring, radiating pale jade striations, and breeze teal flecks"
  * hairColor: "Soft silvery ash hair, soft and sultry with a breezy, airy sheen"
  * skinTone: "Light sun-kissed fair tan complexion, evenly tanned"
  * eyeColorNegatives: ["blue eyes", "green eyes", "brown eyes", "hazel eyes", "amber eyes", "red eyes", "violet eyes"]
  * skinColorNegatives: ["pale skin", "fair skin", "washed-out skin"]
  * hairColorNegatives: ["all-over green hair", "all-over purple hair", "all-over lilac hair", "fully dyed hair"]
* **Physique Block:**
  * build: "Lithe, gymnastic wood-elven build; coiled-spring agility and athletic balance"
  * torso: "Narrow gymnastic torso; tight waistline with faint oblique lines and a firm core tapering cleanly into the hips"
  * bust: "Very full, generous, heavy bust with a soft natural weight and a gentle outward swell, broad natural detail, lifted and pressed together at the centre; the inner curves meeting at the centre line in a deep, crisp, clearly defined cleavage, held firm and high; realistic skin texture and natural, anatomically accurate detail"
  * arms: "Slender, toned arms; firm athletic triceps and slender, dexterous wrists"
  * hips: "Shapely feminine hips, gently curved, compact and agile"
  * legs: "Very long, springy athletic legs; defined calves and toned thighs"
  * distinguishingMarks: []
  * raceAlignment: "Human presentation aligned to wood elf bard characteristics (gymnastic, breath endurance, aerodynamic poise)"

---

### SD-010: Draknoxa Thorne
* **Card ID:** `HERO_DRAKNOXA_THORNE`
* **Element / Class / Race:** Poison | Alchemist | Dark Elf
* **Physique Profile:** Compact, clinical, and predatory.
* **Palette & Cosmetics:**
  * primaryColor: "Toxic Orchid Magenta", accentColors: ["Vibrant Acid Lime", "Tarnished Brass"], metal: "tarnished brass"
  * eyeColor: "Acid lime-emerald iris with blackened moss limbal ring, radiating toxic magenta striations, and chartreuse flecks"
  * hairColor: "Deep dark burgundy-black hair with a rich red tint and cool espresso depth"
  * skinTone: "Pale olive complexion with a faint cool-grey cast, evenly toned, smooth and blemish-free"
  * eyeColorNegatives: ["blue eyes", "brown eyes", "grey eyes", "hazel eyes", "amber eyes", "red eyes"]
  * skinColorNegatives: ["ruddy skin", "sunburnt skin", "overly tanned skin"]
  * hairColorNegatives: ["all-over lime-green hair", "all-over green hair", "all-over magenta hair", "all-over pink hair", "fully dyed hair"]
* **Physique Block:**
  * build: "Compact, wiry dark-elven build; predatory poise with clinical, measured precision"
  * torso: "Flat, tightly controlled midriff; narrow waistline tapering cleanly into the hips"
  * bust: "Very full, generous bust with a heavy, rounded shape and a pronounced inner swell, generous natural detail, lifted and pressed together at the centre; the inner curves meeting at the centre line in a deep, crisp, clearly defined cleavage, held firm and high; realistic skin texture and natural, anatomically accurate detail"
  * arms: "Slender, wiry arms with defined tendon lines at the wrists; steady, precise hands"
  * hips: "Shapely feminine hips, gently curved, narrow and agile"
  * legs: "Very long, wiry legs with slender calves"
  * distinguishingMarks: []
  * raceAlignment: "Human presentation aligned to dark elf apothecary characteristics (clinical precision, venomous focus)"

---

## 4. How the Fields Reach the Prompt

The real prompt is assembled from the shared templates in `data/art/_templates/heroes/` (not from a fixed concatenation), by `tools/generators/gen_prompt.py`. For a sister:

| Stage | What it carries |
| --- | --- |
| 1_Alpha / 1_Prime (`pose-female-human.txt`) | Critical details first (hair, bust, eyes, skin, legs), then the **standard figure** (`figureProfile: standard`: lithe, slender build, slim waist, shapely hips, very long legs), the underlayer, hair, eyes, lips and expression. Negatives come from her `eyeColorNegatives`, `skinColorNegatives` and `hairColorNegatives` |
| 1_Alpha / 2_Bare | Removes the clothing and applies her **individual build** (`build`, `torso`, `arms`, `hips`, `legs`) and bust, and sets her likeness for every later stage |
| 3 onward | Footwear, layers, armor and scenes edit the Bare image, so they carry the build instead of repeating it |

The text of each field is the identity JSON (`data/art/heroes/drakn-sisters/<name>-thorne.json`); the section 3 blocks above mirror it.

---

## 5. Build Rationale and Audit

The ten Drakn sisters are one bloodline (the Thorne family) and the Transcendent top of the set, so they share one silhouette on purpose:
a narrow waist, shapely hips and very long legs under the family bust (section 1). What makes each sister herself is her race, her
phenotype (hair, eyes, skin, metals) and one of three build presets, not a different body plan. The Angel Primes are not related, so their
builds vary much more (see [angel_primes_physique.md](./angel_primes_physique.md)). The sisters' bust and physique text is applied at the
2_Bare stage; the 1_Prime stage uses the standard figure so the original photo stays recognisable.

| Preset | Sisters | Reads as |
| --- | --- | --- |
| Ethereal & Aristocratic | Drakness, Draknora, Draknira, Draknisa, Drakneta | Elegant, long-lined, smooth |
| Agile & Gymnastic | Drakniya, Draknava, Draknoxa | Lithe and quick, lightly defined |
| Grounded & Martial | Drakniss, Draknara | Taut and athletic, with the most visible tone of the ten (toned abs, arms and legs) |

### Audit (Oct 9): nothing was changed

The identity JSON is the source, so this page now mirrors it (the palette, build and cosmetic text above were out of date and have been
synced). Each sister's build, torso, arms, hips and legs were scanned for bulk words (strong, muscular, sturdy, solid, powerful, thick,
bulk, muscle) and for tone vocabulary (toned, defined, athletic, wiry, firm and similar).

| Sister | Element / race | Preset | Bulk words | Tone words | Why it fits |
| --- | --- | --- | --- | --- | --- |
| Draknara | Earth, Barbarian | Grounded & Martial | bulk, muscle | 10 | Barbarian shaman: the most athletic of the ten, with visible tone that stays feminine |
| Draknava | Wind, Wood Elf | Agile & Gymnastic | none | 5 | Wood-elf bard: gymnastic, coiled agility |
| Drakness | Darkness, Dark Elf | Ethereal & Aristocratic | none | 2 | Dark-elf aristocrat and necromancer: slender and sinewy reads as cold and precise |
| Drakneta | Lightning, Celestial | Ethereal & Aristocratic | none | 1 | Celestial summoner: the tallest, most statuesque build |
| Draknira | Ice, High Elf | Ethereal & Aristocratic | none | 0 | High-elf wizard: the most delicate and crystalline build |
| Draknisa | Water, Human | Ethereal & Aristocratic | none | 0 | Water enchanter: dancer's lines and flowing, serpentine curves |
| Drakniss | Light, Human | Grounded & Martial | none | 8 | Warrior-cleric: taut and grounded, a healer who can stand in a line |
| Drakniya | Grass, Wood Elf | Agile & Gymnastic | none | 8 | Wood-elf druid: a lean runner's build suits a nimble forest healer |
| Draknora | Fire, Human | Ethereal & Aristocratic | none | 0 | Human fire-mage: the statuesque hourglass is the warm, dignified one of the family |
| Draknoxa | Poison, Dark Elf | Agile & Gymnastic | none | 3 | Dark-elf alchemist: compact and wiry, clinical rather than glamorous |

| Finding | Detail |
| --- | --- |
| No body-builder wording | None of the ten uses strong, muscular, sturdy, solid or powerful. Toned abs, arms and legs are wanted, so the tone vocabulary is kept; the line is a body-builder look, not tone |
| One to fix later | Draknara's arms say "toned forearms without bulk". The negation names bulk, so it can push the model toward it. A positive wording such as "lean, toned forearms" says the same without naming it (not changed yet) |
| Tone vocabulary | Draknara, Drakniss and Drakniya carry the most (subtle abs, toned thighs, deltoid contours) and Draknava and Draknoxa some. It keeps their abs, arms and legs from looking identical, and it fits their presets. Keep it soft ("subtle", "faint", "lightly") so it does not tip into a body-builder |
| Every build makes sense for its race and class | See the last column; each preset follows the sister's race and role |
| Little variety in height and legs | All ten have very long legs and a narrow waist. This is the family standard by design; if more variety is wanted, height and leg proportion are the levers, as with the angels |

Check any time with `python tools/art/identity_audit.py` (it lists the same notes for the sisters without failing).
