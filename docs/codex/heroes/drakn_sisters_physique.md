# Sovereign Territories — Hero Card Roster: Transcendent Tier (ST-001 – ST-010)
## Character Architecture & Physical Specification Matrix (Revised Schema Alignment)

---

## 1. Master Bloodline Architecture: Shared Skeletal Core vs. Elemental Phenotype

Based on the authoritative `HERO_DRAKNARA_THORNE.json` schema, the Transcendent Drakn Sisters divide into two distinct layers:

### The Shared Skeletal & Foundation Core (Universal)
* **Bust Geometry:** Full, very voluptuous, noticeably enlarged bust lifted high and pressed firmly together at the center by a push-up contour; inner curves meet at the center line in a deep, tight, narrow cleavage with no gap; soft, naturally rounded, full shape throughout.
* **Frame & Silhouette:** Narrow, corseted waistline tapering cleanly into shapely feminine hips (gently curved, not wide); very long, elegant legs.
* **Studio Base Uniform:** High-gloss metallic triangle bikini underlayer, signature stiletto heels, high-gloss skin finish (`defaultSheen`).
* **Master Canvas Standard:** `944 × 1104` with studio cream padding (`#F5F0E6`), scaling to `1080 × 1350` (4:5) for final mobile card production.

### The Elemental Glamour Phenotype (Individualized)
* Each sister carries an individualized racial/elemental phenotype across **hair, eyes, skin tone, cosmetics, and metals**, complete with strict negative prompts to prevent cross-bleeding (e.g., Draknara explicitly banning violet eyes and pale skin in favor of malachite-hazel and terracotta tan).

---

## 2. Master Card Registry & Phenotype Alignment

| Card ID | Card Name | Element | Class | Race Presentation | Primary Colors & Metals | Eye / Hair Phenotype | Physical Preset Category |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ST-001** | Drakness Thorne | Darkness | Necromancer | Dark Elf | Void Violet, Obsidian, Smoked Chrome | Deep Violet Irises / Obsidian-Black Hair | Ethereal & Aristocratic (Predatory) |
| **ST-002** | Draknora Thorne | Fire | Magician | Human | Molten Crimson, Cinder Brass, Gold | Incandescent Amber / Warm Copper-Auburn | Ethereal & Aristocratic (Statuesque) |
| **ST-003** | Drakniya Thorne | Grass | Druid | Wood Elf | Forest Emerald, Living Copper, Moss | Leaf-Green / Deep Chestnut-Brunette | Agile & Gymnastic (Runner) |
| **ST-004** | Draknira Thorne | Ice | Wizard | High Elf | Glacial Cyan, Frosted Silver, Pearl | Frosted Ice-Blue / Platinum-White Hair | Ethereal & Aristocratic (Crystalline) |
| **ST-005** | Draknisa Thorne | Water | Enchanter | Human | Oceanic Blue, Deep Teal, Platinum | Deep Sea-Sapphire / Blue-Black Raven Hair | Ethereal & Aristocratic (Serpentine) |
| **ST-006** | Drakniss Thorne | Light | Cleric | Human | Solar Alabaster, Sun-Gold, Aurum | Radiant Golden-Amber / Warm Honey-Blonde | Grounded & Martial (Armored Endurance) |
| **ST-007** | Draknara Thorne | Earth | Shaman | Barbarian | Burnt Sienna, Turquoise, Antique Bronze | Malachite-Hazel / Bronze-Brown Hair | Grounded & Martial (Taut Core) |
| **ST-008** | Drakneta Thorne | Lightning | Summoner | Celestial | Arc Violet, Storm Cobalt, Silver | Electric Violet-Blue / Luminous Pale Silver | Ethereal & Aristocratic (Kinetic) |
| **ST-009** | Draknava Thorne | Wind | Bard | Wood Elf | Sky Cerulean, Wind-Brass, Ivory | Wind-Grey Cyan / Sun-Bleached Ash Brown | Agile & Gymnastic (Coiled Agility) |
| **ST-010** | Draknoxa Thorne | Poison | Alchemist | Dark Elf | Acid Malachite, Dark Iron, Black Steel | Toxic Yellow-Green / Midnight Jet Black | Agile & Gymnastic (Clinical/Predatory) |

---

## 3. Individual Character JSON-Ready Specifications

### ST-001: Drakness Thorne
* **Card ID:** `HERO_DRAKNESS_THORNE`
* **Element / Class / Race:** Darkness | Necromancer | Dark Elf
* **Physique Profile:** Aristocratic, predatory-lithe with sinewy tension.
* **Palette & Cosmetics:**
  * primaryColor: "Midnight Obsidian", accentColors: ["Void Violet", "Smoked Chrome"], metal: "smoked chrome"
  * eyeColor: "Deep glowing violet iris with pitch-black limbal ring and faint amethyst striae"
  * hairColor: "Obsidian-black hair, high-gloss lustrous finish"
  * skinTone: "Cool alabaster-pale porcelain complexion, faint lavender-cool undertone, unblemished"
  * eyeColorNegatives: ["blue eyes", "green eyes", "brown eyes", "amber eyes", "hazel eyes"]
  * skinColorNegatives: ["tanned skin", "bronze skin", "sun-weathered skin", "ruddy complexion"]
* **Physique Block:**
  * build: "Slender, long-limbed, aristocratic dark-elven posture with sinewy tension"
  * torso: "Ultra-narrow corseted waistline; smooth porcelain flat midriff with zero abdominal lines"
  * bust: "Full, very voluptuous, noticeably enlarged bust - lifted high and pressed firmly together at the centre by a push-up contour, the inner curves meeting at the centre line in a deep, tight, narrow cleavage with no gap between them; soft, naturally rounded, full shape throughout"
  * arms: "Slender arms with delicate wrists and elongated fingers; slight wiry tension in forearms"
  * hips: "Shapely feminine hips, gently curved (not wide), high hip-shelf taper"
  * legs: "Very long, porcelain-slender legs with elegant tapering down to slim ankles"
  * distinguishingMarks: []
  * raceAlignment: "Human presentation aligned to dark elf characteristics (sinewy elegance, aristocratic detachment) — glamour build stays family-standard for now"

---

### ST-002: Draknora Thorne
* **Card ID:** `HERO_DRAKNORA_THORNE`
* **Element / Class / Race:** Fire | Magician | Human
* **Physique Profile:** Warm, statuesque, and dignified.
* **Palette & Cosmetics:**
  * primaryColor: "Molten Crimson", accentColors: ["Cinder Brass", "Burnished Gold"], metal: "cinder brass"
  * eyeColor: "Incandescent amber-topaz iris with warm bronze limbal ring and gold radiant flecks"
  * hairColor: "Deep warm copper-auburn hair with fine bronze babylights"
  * skinTone: "Warm golden-ivory complexion, healthy radiant warmth, smooth and even"
  * eyeColorNegatives: ["blue eyes", "violet eyes", "grey eyes", "black eyes"]
  * skinColorNegatives: ["pale ghost skin", "cold blue skin", "chalky white skin"]
* **Physique Block:**
  * build: "Lithe, statuesque human presentation with balanced, dignified posture"
  * torso: "Smooth flat stomach with soft natural curvature into hips; narrow waistline, no abdominal cuts"
  * bust: "Full, very voluptuous, noticeably enlarged bust - lifted high and pressed firmly together at the centre by a push-up contour, the inner curves meeting at the centre line in a deep, tight, narrow cleavage with no gap between them; soft, naturally rounded, full shape throughout"
  * arms: "Slender, smooth arms with soft natural curvature; unblemished hands"
  * hips: "Shapely feminine hips, gently curved (not wide), natural hourglass silhouette"
  * legs: "Very long, gracefully proportioned legs; smooth contours and elegant vertical poise"
  * distinguishingMarks: []
  * raceAlignment: "Human presentation aligned to high human evoker characteristics (noble, poised, radiant warmth) — glamour build stays family-standard for now"

---

### ST-003: Drakniya Thorne
* **Card ID:** `HERO_DRAKNIYA_THORNE`
* **Element / Class / Race:** Grass | Druid | Wood Elf
* **Physique Profile:** Wiry, low-fat runner build with trackless agility.
* **Palette & Cosmetics:**
  * primaryColor: "Deep Forest Emerald", accentColors: ["Living Briar Copper", "Muted Moss"], metal: "living copper"
  * eyeColor: "Luminous emerald-peridot iris with dark jade limbal ring and gold moss specks"
  * hairColor: "Rich deep chestnut-brown hair with subtle warm copper lowlights"
  * skinTone: "Light golden sun-kissed tan complexion, outdoor healthy vitality, even finish"
  * eyeColorNegatives: ["violet eyes", "blue eyes", "red eyes", "black eyes"]
  * skinColorNegatives: ["pale porcelain skin", "ghostly pale skin", "grey skin"]
* **Physique Block:**
  * build: "Lithe, wiry athletic build; low-fat runner physique with wood-elven agility"
  * torso: "Tight lithe midriff; faint oblique fluting and subtle vertical definition; slender waist tapering cleanly into hips"
  * bust: "Full, very voluptuous, noticeably enlarged bust - lifted high and pressed firmly together at the centre by a push-up contour, the inner curves meeting at the centre line in a deep, tight, narrow cleavage with no gap between them; soft, naturally rounded, full shape throughout"
  * arms: "Slender, lightly defined arms; subtle deltoid contours and lithe forearms"
  * hips: "Shapely feminine hips, gently curved (not wide), athletic pelvis alignment"
  * legs: "Very long, lean athletic legs; subtly toned quadriceps and elongated calves"
  * distinguishingMarks: []
  * raceAlignment: "Human presentation aligned to wood elf characteristics (agile, trackless, low-fat runner vitality) — glamour build stays family-standard for now"

---

### ST-004: Draknira Thorne
* **Card ID:** `HERO_DRAKNIRA_THORNE`
* **Element / Class / Race:** Ice | Wizard | High Elf
* **Physique Profile:** Crystalline, ethereal, and aloof.
* **Palette & Cosmetics:**
  * primaryColor: "Glacial Cyan", accentColors: ["Frosted Silver", "Deep Arctic Navy"], metal: "frosted silver"
  * eyeColor: "Piercing ice-cyan iris with navy limbal ring and crystalline diamond striae"
  * hairColor: "Pure platinum-white hair with cool silver sheen"
  * skinTone: "Pristine alabaster-permafrost complexion, exceptionally fair, cool translucent tone"
  * eyeColorNegatives: ["brown eyes", "amber eyes", "violet eyes", "hazel eyes", "green eyes"]
  * skinColorNegatives: ["tanned skin", "terracotta skin", "bronze skin", "warm peach skin"]
* **Physique Block:**
  * build: "Ethereal, crystalline high-elven build; ultra-slender, delicate bone structure"
  * torso: "Completely flat porcelain stomach with zero muscle definition; tight, elegant waist tapering cleanly into hips"
  * bust: "Full, very voluptuous, noticeably enlarged bust - lifted high and pressed firmly together at the centre by a push-up contour, the inner curves meeting at the centre line in a deep, tight, narrow cleavage with no gap between them; soft, naturally rounded, full shape throughout"
  * arms: "Very slender, delicate arms; paper-fine wrists and long, unworked arcane fingers"
  * hips: "Shapely feminine hips, gently curved (not wide), narrow and elegant"
  * legs: "Extremely long, porcelain-smooth slender legs; light, weightless stance"
  * distinguishingMarks: []
  * raceAlignment: "Human presentation aligned to high elf characteristics (regal detachment, crystalline geometry) — glamour build stays family-standard for now"

---

### ST-005: Draknisa Thorne
* **Card ID:** `HERO_DRAKNISA_THORNE`
* **Element / Class / Race:** Water | Enchanter | Human
* **Physique Profile:** Fluid, serpentine dancer with a supple hourglass.
* **Palette & Cosmetics:**
  * primaryColor: "Deep Oceanic Blue", accentColors: ["Deep Teal", "Polished Platinum"], metal: "polished platinum"
  * eyeColor: "Vivid sapphire-blue iris with deep navy limbal ring and radiating cerulean ripples"
  * hairColor: "Blue-black raven hair with high-gloss liquid mirror sheen"
  * skinTone: "Porcelain-cream complexion with soft cool-neutral undertones, smooth and supple"
  * eyeColorNegatives: ["brown eyes", "amber eyes", "hazel eyes", "violet eyes", "red eyes"]
  * skinColorNegatives: ["dark tan skin", "rough skin", "sun-weathered skin"]
* **Physique Block:**
  * build: "Lithe, supple dancer physique with flowing, serpentine human grace"
  * torso: "Soft, completely flat midriff tapering smoothly into an exceptionally narrow waist; no muscle cuts"
  * bust: "Full, very voluptuous, noticeably enlarged bust - lifted high and pressed firmly together at the centre by a push-up contour, the inner curves meeting at the centre line in a deep, tight, narrow cleavage with no gap between them; soft, naturally rounded, full shape throughout"
  * arms: "Smooth, slender arms held in fluid, relaxed gestures; graceful wrists"
  * hips: "Shapely feminine hips, gently curved (not wide), supple and pronounced curves"
  * legs: "Very long, smooth slender legs with dancer-like fluid alignment and relaxed stance"
  * distinguishingMarks: []
  * raceAlignment: "Human presentation aligned to courtly enchanter characteristics (alluring, serpentine, hypnotic ease) — glamour build stays family-standard for now"

---

### ST-006: Drakniss Thorne
* **Card ID:** `HERO_DRAKNISS_THORNE`
* **Element / Class / Race:** Light | Cleric | Human
* **Physique Profile:** Armored athletic endurance with regal martial poise.
* **Palette & Cosmetics:**
  * primaryColor: "Solar Alabaster", accentColors: ["Sun-Forged Gold", "Radiant Pearl"], metal: "sun-forged gold"
  * eyeColor: "Radiant golden-amber iris with light bronze limbal ring and brilliant sunburst striations"
  * hairColor: "Warm honey-blonde hair with radiant golden highlights"
  * skinTone: "Cream-tan complexion with warm luminous undertones, clear, smooth, and vibrant"
  * eyeColorNegatives: ["blue eyes", "violet eyes", "green eyes", "black eyes"]
  * skinColorNegatives: ["cold grey skin", "corrupted skin", "ashen skin"]
* **Physique Block:**
  * build: "Lithe yet taut athletic build; firm, disciplined warrior-cleric poise"
  * torso: "Flat, firm midriff with subtle core tone; faint vertical linea alba; tight tapered waist into hips"
  * bust: "Full, very voluptuous, noticeably enlarged bust - lifted high and pressed firmly together at the centre by a push-up contour, the inner curves meeting at the centre line in a deep, tight, narrow cleavage with no gap between them; soft, naturally rounded, full shape throughout"
  * arms: "Slender, defined arms; light deltoid contours and firm forearms built for weapon leverage"
  * hips: "Shapely feminine hips, gently curved (not wide), square and grounded martial alignment"
  * legs: "Very long, toned athletic legs; firm quadricep contours and stable combat stance"
  * distinguishingMarks: []
  * raceAlignment: "Human presentation aligned to holy crusader characteristics (disciplined, steadfast, enduring light) — glamour build stays family-standard for now"

---

### ST-007: Draknara Thorne
* **Card ID:** `HERO_DRAKNARA_THORNE`
* **Element / Class / Race:** Earth | Shaman | Barbarian
* **Physique Profile:** Taut, grounded athletic core with primal tone.
* **Palette & Cosmetics:**
  * primaryColor: "Deep Burnt Sienna", accentColors: ["Vivid Turquoise", "Antique Bronze"], metal: "antique bronze"
  * eyeColor: "Rich malachite-hazel iris with dark umber limbal ring, radiating terracotta striations, and warm amber flecks"
  * hairColor: "Medium bronze-brown hair, rich and warm with warm caramel babylights"
  * skinTone: "Deep sun-weathered terracotta tan complexion, evenly tanned, no pale areas"
  * eyeColorNegatives: ["blue eyes", "brown eyes", "grey eyes", "red eyes", "violet eyes"]
  * skinColorNegatives: ["pale skin", "fair skin", "washed-out skin"]
* **Physique Block:**
  * build: "Lithe yet taut athletic build; slender, long-limbed, functionally fit with subtle warrior muscle tone"
  * torso: "Flat, firm midriff with subtle abdominal tone; faint vertical linea alba and soft oblique contours; tight waist tapering cleanly into hips"
  * bust: "Full, very voluptuous, noticeably enlarged bust - lifted high and pressed firmly together at the centre by a push-up contour, the inner curves meeting at the centre line in a deep, tight, narrow cleavage with no gap between them; soft, naturally rounded, full shape throughout"
  * arms: "Slender, lightly defined arms; faint deltoid contours and toned forearms without bulk"
  * hips: "Shapely feminine hips, gently curved (not wide)"
  * legs: "Very long, lean athletic legs; subtly toned thighs and slender calves with graceful definition"
  * distinguishingMarks: []
  * raceAlignment: "Human presentation aligned to barbarian characteristics (strong, grounded, sun-touched resilience) — glamour build stays family-standard for now"

---

### ST-008: Drakneta Thorne
* **Card ID:** `HERO_DRAKNETA_THORNE`
* **Element / Class / Race:** Lightning | Summoner | Celestial
* **Physique Profile:** Statuesque, radiant, and kinetic.
* **Palette & Cosmetics:**
  * primaryColor: "Electric Arc Violet", accentColors: ["Storm Cobalt", "Conductive Silver"], metal: "conductive silver"
  * eyeColor: "Electric violet-indigo iris with bright silver limbal ring and branching lightning filaments"
  * hairColor: "Luminous pale silver hair with subtle violet reflection"
  * skinTone: "Luminous celestial-alabaster complexion with high-clarity specular reflectivity"
  * eyeColorNegatives: ["brown eyes", "hazel eyes", "green eyes", "dark eyes"]
  * skinColorNegatives: ["ruddy skin", "tanned skin", "earthy brown skin"]
* **Physique Block:**
  * build: "Tall, statuesque celestial posture; ultra-long-limbed, commanding and radiant"
  * torso: "Taut, perfectly flat midriff held with high stillness; narrow waistline, seamless transitions into hips"
  * bust: "Full, very voluptuous, noticeably enlarged bust - lifted high and pressed firmly together at the centre by a push-up contour, the inner curves meeting at the centre line in a deep, tight, narrow cleavage with no gap between them; soft, naturally rounded, full shape throughout"
  * arms: "Long, slender arms held in charged, authoritative arcs; fine, luminous hands"
  * hips: "Shapely feminine hips, gently curved (not wide), narrow and regal high-waisted alignment"
  * legs: "Exceptionally long, statuesque legs with sharp, clean shin contours and commanding poise"
  * distinguishingMarks: []
  * raceAlignment: "Human presentation aligned to celestial herald characteristics (statuesque, kinetic, high-voltage presence) — glamour build stays family-standard for now"

---

### ST-009: Draknava Thorne
* **Card ID:** `HERO_DRAKNAVA_THORNE`
* **Element / Class / Race:** Wind | Bard | Wood Elf
* **Physique Profile:** Gymnastic, coiled-spring agility.
* **Palette & Cosmetics:**
  * primaryColor: "Sky Cerulean", accentColors: ["Burnished Wind-Brass", "Cloud Ivory"], metal: "burnished wind-brass"
  * eyeColor: "Atmospheric teal-grey iris with soft slate limbal ring and bright cerulean flecks"
  * hairColor: "Sun-bleached ash brown hair with light sand babylights"
  * skinTone: "Light golden-ivory complexion, outdoor wind-kissed clarity, smooth and clean"
  * eyeColorNegatives: ["violet eyes", "brown eyes", "red eyes", "black eyes"]
  * skinColorNegatives: ["corrupted skin", "ashen skin", "chalky white skin"]
* **Physique Block:**
  * build: "Lithe, gymnastic wood-elven build; coiled-spring agility and athletic balance"
  * torso: "Narrow gymnastic torso; tight waistline with faint oblique lines and firm core control tapering cleanly into hips"
  * bust: "Full, very voluptuous, noticeably enlarged bust - lifted high and pressed firmly together at the centre by a push-up contour, the inner curves meeting at the centre line in a deep, tight, narrow cleavage with no gap between them; soft, naturally rounded, full shape throughout"
  * arms: "Slender, toned arms; firm athletic triceps and hyper-dexterous, slender wrists"
  * hips: "Shapely feminine hips, gently curved (not wide), compact and agile"
  * legs: "Very long, springy athletic legs; defined calves and toned thighs primed for rapid steps"
  * distinguishingMarks: []
  * raceAlignment: "Human presentation aligned to wood elf bard characteristics (gymnastic, breath-endurance, aerodynamic poise) — glamour build stays family-standard for now"

---

### ST-010: Draknoxa Thorne
* **Card ID:** `HERO_DRAKNOXA_THORNE`
* **Element / Class / Race:** Poison | Alchemist | Dark Elf
* **Physique Profile:** Compact, clinical, and predatory.
* **Palette & Cosmetics:**
  * primaryColor: "Toxic Malachite", accentColors: ["Dark Iron", "Blackened Steel"], metal: "dark iron"
  * eyeColor: "Acidic yellow-green iris with dark umber limbal ring and venom-drop striations"
  * hairColor: "Midnight jet-black hair with faint petroleum-green specular sheen"
  * skinTone: "Cool pale alabaster complexion with faint olive-neutral undertones, smooth and clinical"
  * eyeColorNegatives: ["blue eyes", "violet eyes", "hazel eyes", "brown eyes"]
  * skinColorNegatives: ["warm bronze skin", "golden tan skin", "sun-weathered skin"]
* **Physique Block:**
  * build: "Compact, wiry dark-elven build; predatory poise with clinical, measured precision"
  * torso: "Flat, tightly controlled midriff; narrow waistline held in a subtle coiled posture tapering cleanly into hips"
  * bust: "Full, very voluptuous, noticeably enlarged bust - lifted high and pressed firmly together at the centre by a push-up contour, the inner curves meeting at the centre line in a deep, tight, narrow cleavage with no gap between them; soft, naturally rounded, full shape throughout"
  * arms: "Slender, wiry arms with defined tendon lines at wrists; steady, razor-precise hands"
  * hips: "Shapely feminine hips, gently curved (not wide), narrow and agile predatory alignment"
  * legs: "Very long, wiry legs with slender calves; quiet, balanced stalking stance"
  * distinguishingMarks: []
  * raceAlignment: "Human presentation aligned to dark elf apothecary characteristics (clinical precision, venomous focus) — glamour build stays family-standard for now"

---

## 4. Master Prompt Assembly Algorithm for Studio A-Pose Plates

When the pipeline generates a master plate from any of the 10 sister JSON files, it dynamically concatenates tokens following this strict order:

```text
[Master Shot & Camera]: 
"Full-body master portrait, neutral studio A-pose character plate, single female hero, centered composition, front view, eye-level framing, 944x1104 resolution"

+ [Bloodline Core Physique]:
"{physique.build}, {physique.torso}, {physique.bust}, {physique.arms}, {physique.hips}, {physique.legs}"

+ [Elemental Phenotype & Cosmetics]:
"{palette.skinTone}, {palette.eyeColor}, {palette.hairColor}, {palette.lipColor} lips, {palette.eyeshadowColor} eyeshadow, {palette.nailColor} polished nails"

+ [Underlayer Uniform & Finish]:
"wearing metallic triangle bikini underlayer in {palette.primaryColor} with {palette.metal} hardware and signature high stiletto heels in {palette.primaryColor}, {defaultSheen} finish on swimwear and smooth skin"

+ [Studio Environment & Lighting]:
"neutral cream studio background (#F5F0E6), clean soft studio ambient lighting with subtle directional rim highlights carving muscle contours, sharp focus, 8k resolution, photorealistic masterwork"