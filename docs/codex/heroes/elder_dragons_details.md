# Sovereign Territories — Elder Dragons: Visual Architecture (SD-021 – SD-030)
## Visual Architecture & Elemental Morphology Matrix

---

## 1. What the Identity JSON Holds

The dragon identity JSON (`data/art/dragons/elder-dragons/<name>.json`) holds the description and the structured morphology the image models need:

1. `description`: the one-sentence master description (it also gives the scale colours).
2. `silhouette`, `scaleTexture`, `wingMembrane`, `hornsAndCrest`, `elementalVenting`: explicit mechanical tokens so flight mechanics, membranes and vents render correctly.
3. `notes`: which sister the dragon is aligned to and why.

The dragon's name, element and sex are not in this file: they come from the card (`data/cards/sovereign-dawn/`, `UNIT_<NAME>`, `SD-021` to `SD-030`), and the card's `companion` field on the sister names the dragon. There is no separate palette field; the colours are in the description and echo the bonded sister's palette. The companion frames (`tools/art/dragon_companions.py`) place each dragon beside her.

---

## 2. Master Elder Dragon Registry (Mythic Tier SD-021 – SD-030)

| Card ID | Dragon Name | Element | Bonded Sister | Archetype | Sex | Scale colours (from the description) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| SD-021 | Umbrath | Darkness | Drakness (Necro) | Aerial / Flying | Male | obsidian-black and midnight-violet |
| SD-022 | Pyraxis | Fire | Draknora (Mage) | Aerial / Flying | Male | flame-red and burnished-gold |
| SD-023 | Sylvanya | Grass | Drakniya (Druid) | Aerial / Flying | Female | emerald-green and forest-sage |
| SD-024 | Glaciora | Ice | Draknira (Wizard) | Aerial / Flying | Female | glacial-cyan and frost-white |
| SD-025 | Aquaria | Water | Draknisa (Enchanter)| Aerial / Flying | Female | deep oceanic-blue and deep-teal |
| SD-026 | Lumira | Light | Drakniss (Cleric) | Aerial / Flying | Female | radiant rose-gold and radiant-gold |
| SD-027 | Terrador | Earth | Draknara (Shaman) | Aerial / Flying | Male | deep burnt-sienna and antique-bronze |
| SD-028 | Fulgora | Lightning| Drakneta (Summoner)| Aerial / Flying | Female | electric-gold and arc-white |
| SD-029 | Zephyros | Wind | Draknava (Bard) | Aerial / Flying | Male | windswept-jade and gossamer-silver |
| SD-030 | Venomis | Poison | Draknoxa (Alchem.) | Aerial / Flying | Female | toxic-orchid-magenta and tarnished-brass |

---

## 3. Individual Dragon Specifications & JSON Schemas

### SD-021: Umbrath (Darkness Elder Dragon)
* Bond: Drakness Thorne (SD-001)
* Master Description: An Elder Dragon of obsidian-black and midnight-violet scales, wreathed in creeping shadow, wings like tattered sheets of darkness edged in amethyst light.
* Morphology in short: Predatory, long-necked wyrm with high skeletal shoulder ridges and a razor-tapered tail; scales: overlapping matte obsidian plates with a faint midnight-violet sheen; wings: semi-translucent, tattered shadow-glass on slender razor-edged struts, edged in amethyst light; horns: swept-back crown of serrated obsidian horns with violet light in the fissures; venting: cold black shadow-mist curling from the throat and spine.
* Identity JSON (`data/art/dragons/elder-dragons/umbrath.json`):
  * id: "dragons/elder-dragons/umbrath"
  * kind: "dragon"
  * cardId: "UNIT_UMBRATH" (the card is SD-021)
  * description: "an Elder Dragon of obsidian-black and midnight-violet scales, wreathed in creeping shadow, wings like tattered sheets of darkness edged in amethyst light"
  * silhouette: "Predatory, long-necked wyrm with high skeletal shoulder ridges and a razor-tapered tail"
  * scaleTexture: "Overlapping matte obsidian plates with a faint midnight-violet sheen"
  * wingMembrane: "Semi-translucent, tattered shadow-glass on slender razor-edged struts, edged in amethyst light"
  * hornsAndCrest: "Swept-back crown of serrated obsidian horns with violet light in the fissures"
  * elementalVenting: "Cold black shadow-mist curling from the throat and spine"
  * notes: "Skeletal identity, first pass -- aligned to Drakness Thorne (Darkness) per docs/codex/heroes/sovereign_dawn_codex.md's Element Alignment table. No archived source material; colours grounded in Drakness's own palette (Midnight Violet / Vibrant Amethyst / Polished Silver)."

---

### SD-022: Pyraxis (Fire Elder Dragon)
* Bond: Draknora Thorne (SD-002)
* Master Description: An Elder Dragon of flame-red and burnished-gold scales, wreathed in heat haze, wings like sheets of molten bronze.
* Morphology in short: Heavy, broad-chested colossus with an anvil-shaped skull and armoured haunches; scales: thick overlapping scutes in flame-red and burnished gold, with glowing seams between them; wings: broad, jagged membrane like cooling molten bronze, glowing near the joints and darkening toward the edges; horns: heavy crown of jagged horns glowing dull red at the tips; venting: heat haze and ember ribbons rising from the chest and shoulders.
* Identity JSON (`data/art/dragons/elder-dragons/pyraxis.json`):
  * id: "dragons/elder-dragons/pyraxis"
  * kind: "dragon"
  * cardId: "UNIT_PYRAXIS" (the card is SD-022)
  * description: "an Elder Dragon of flame-red and burnished-gold scales, wreathed in heat haze, wings like sheets of molten bronze"
  * silhouette: "Heavy, broad-chested colossus with an anvil-shaped skull and armoured haunches"
  * scaleTexture: "Thick overlapping scutes in flame-red and burnished gold, with glowing seams between them"
  * wingMembrane: "Broad, jagged membrane like cooling molten bronze, glowing near the joints and darkening toward the edges"
  * hornsAndCrest: "Heavy crown of jagged horns glowing dull red at the tips"
  * elementalVenting: "Heat haze and ember ribbons rising from the chest and shoulders"
  * notes: "Fire Elder Dragon (SD-022), the aligned companion of Draknora Thorne (Fire): her card's companion is Pyraxis, and the companion frames place him beside her. Skeletal identity grounded in the Element Alignment table of docs/codex/heroes/sovereign_dawn_codex.md."

---

### SD-023: Sylvanya (Grass Elder Dragon)
* Bond: Drakniya Thorne (SD-003)
* Master Description: An Elder Dragon of emerald-green and forest-sage scales, trailing drifting leaves and spores, wings like broad canopy leaves veined in moss-gold.
* Morphology in short: Slender, serpentine woodland dragon with a high crest and agile, runner-like limbs; scales: overlapping leaf-shaped scales in emerald green and forest sage, patched with moss; wings: broad, leaf-like membrane veined in moss-gold; horns: high-branching antlers like ironwood roots, wound with flowering vines; venting: drifting leaves, pollen and glowing spores around the wings.
* Identity JSON (`data/art/dragons/elder-dragons/sylvanya.json`):
  * id: "dragons/elder-dragons/sylvanya"
  * kind: "dragon"
  * cardId: "UNIT_SYLVANYA" (the card is SD-023)
  * description: "an Elder Dragon of emerald-green and forest-sage scales, trailing drifting leaves and spores, wings like broad canopy leaves veined in moss-gold"
  * silhouette: "Slender, serpentine woodland dragon with a high crest and agile, runner-like limbs"
  * scaleTexture: "Overlapping leaf-shaped scales in emerald green and forest sage, patched with moss"
  * wingMembrane: "Broad, leaf-like membrane veined in moss-gold"
  * hornsAndCrest: "High-branching antlers like ironwood roots, wound with flowering vines"
  * elementalVenting: "Drifting leaves, pollen and glowing spores around the wings"
  * notes: "Skeletal identity, first pass -- aligned to Drakniya Thorne (Grass) per docs/codex/heroes/sovereign_dawn_codex.md's Element Alignment table. No archived source material; colours grounded in Drakniya's own palette (Emerald Green / Forest Sage / Moss Gold)."

---

### SD-024: Glaciora (Ice Elder Dragon)
* Bond: Draknira Thorne (SD-004)
* Master Description: An Elder Dragon of glacial-cyan and frost-white scales, wreathed in drifting ice crystals, wings like panes of frosted crystal edged in brushed chrome.
* Morphology in short: Statuesque, razor-edged dragon with a long, elegant neck and a needle-tipped tail; scales: faceted, crystalline scales in frost-white and glacial cyan; wings: rigid panes of translucent frosted crystal edged in brushed chrome, scattering light into prisms; horns: symmetrical crown of needle-sharp ice spires like a frozen diadem; venting: drifting ice crystals and cold mist from the jaw and wing claws.
* Identity JSON (`data/art/dragons/elder-dragons/glaciora.json`):
  * id: "dragons/elder-dragons/glaciora"
  * kind: "dragon"
  * cardId: "UNIT_GLACIORA" (the card is SD-024)
  * description: "an Elder Dragon of glacial-cyan and frost-white scales, wreathed in drifting ice crystals, wings like panes of frosted crystal edged in brushed chrome"
  * silhouette: "Statuesque, razor-edged dragon with a long, elegant neck and a needle-tipped tail"
  * scaleTexture: "Faceted, crystalline scales in frost-white and glacial cyan"
  * wingMembrane: "Rigid panes of translucent frosted crystal edged in brushed chrome, scattering light into prisms"
  * hornsAndCrest: "Symmetrical crown of needle-sharp ice spires like a frozen diadem"
  * elementalVenting: "Drifting ice crystals and cold mist from the jaw and wing claws"
  * notes: "Skeletal identity, first pass -- aligned to Draknira Thorne (Ice) per docs/codex/heroes/sovereign_dawn_codex.md's Element Alignment table. No archived source material; colours grounded in Draknira's own palette (Glacial Cyan / Frost White / Brushed Chrome)."

---

### SD-025: Aquaria (Water Elder Dragon)
* Bond: Draknisa Thorne (SD-005)
* Master Description: An Elder Dragon of deep oceanic-blue and deep-teal scales, trailing streams of seawater, wings like rippling sheets of tide-glass edged in polished platinum.
* Morphology in short: Supple, serpentine dragon with finned limbs and a broad tail fluke; scales: smooth, seamless fish-scale armour in oceanic blue and deep teal, catching rippling caustic light; wings: flexible tide-glass that ripples like manta-ray fins, edged in polished platinum; horns: sweeping crown of curved, nautilus-like horns and translucent fin-frills; venting: streams of seawater, floating droplets and sea-spray trailing the body.
* Identity JSON (`data/art/dragons/elder-dragons/aquaria.json`):
  * id: "dragons/elder-dragons/aquaria"
  * kind: "dragon"
  * cardId: "UNIT_AQUARIA" (the card is SD-025)
  * description: "an Elder Dragon of deep oceanic-blue and deep-teal scales, trailing streams of seawater, wings like rippling sheets of tide-glass edged in polished platinum"
  * silhouette: "Supple, serpentine dragon with finned limbs and a broad tail fluke"
  * scaleTexture: "Smooth, seamless fish-scale armour in oceanic blue and deep teal, catching rippling caustic light"
  * wingMembrane: "Flexible tide-glass that ripples like manta-ray fins, edged in polished platinum"
  * hornsAndCrest: "Sweeping crown of curved, nautilus-like horns and translucent fin-frills"
  * elementalVenting: "Streams of seawater, floating droplets and sea-spray trailing the body"
  * notes: "Skeletal identity, first pass -- aligned to Draknisa Thorne (Water) per docs/codex/heroes/sovereign_dawn_codex.md's Element Alignment table. No archived source material; colours grounded in Draknisa's own palette (Deep Oceanic Blue / Deep Teal / Polished Platinum)."

---

### SD-026: Lumira (Light Elder Dragon)
* Bond: Drakniss Thorne (SD-006)
* Master Description: An Elder Dragon of radiant rose-gold and radiant-gold scales, wreathed in soft solar glow, wings like panes of stained light edged in polished white gold.
* Morphology in short: Regal, proud-necked dragon with a broad, shield-like breastplate; scales: smooth, pearlescent rose-gold and gold scales with a soft inner radiance; wings: panes of stained light with segmented, feather-like ribs, edged in polished white gold; horns: halo-like corona of golden horns fanned out behind the head; venting: soft solar glow, floating golden motes and sun-dust drifting from the wings.
* Identity JSON (`data/art/dragons/elder-dragons/lumira.json`):
  * id: "dragons/elder-dragons/lumira"
  * kind: "dragon"
  * cardId: "UNIT_LUMIRA" (the card is SD-026)
  * description: "an Elder Dragon of radiant rose-gold and radiant-gold scales, wreathed in soft solar glow, wings like panes of stained light edged in polished white gold"
  * silhouette: "Regal, proud-necked dragon with a broad, shield-like breastplate"
  * scaleTexture: "Smooth, pearlescent rose-gold and gold scales with a soft inner radiance"
  * wingMembrane: "Panes of stained light with segmented, feather-like ribs, edged in polished white gold"
  * hornsAndCrest: "Halo-like corona of golden horns fanned out behind the head"
  * elementalVenting: "Soft solar glow, floating golden motes and sun-dust drifting from the wings"
  * notes: "Skeletal identity, first pass -- aligned to Drakniss Thorne (Light) per docs/codex/heroes/sovereign_dawn_codex.md's Element Alignment table. No archived source material; colours grounded in Drakniss's own palette (Radiant Rose Gold / Radiant Gold / Polished White Gold)."

---

### SD-027: Terrador (Earth Elder Dragon)
* Bond: Draknara Thorne (SD-007)
* Master Description: An Elder Dragon of deep burnt-sienna and antique-bronze scales veined with vivid turquoise, trailing drifting dust and stone fragments, wings like slabs of weathered stone edged in antique bronze.
* Morphology in short: Massive, low-slung, heavily armoured dragon with a club-tipped tail and colossal shoulders; scales: coarse, stone-like plates in burnt sienna and antique bronze, veined with vivid turquoise; wings: heavy slabs of weathered stone joined by thick, flexible tendon, edged in antique bronze; horns: four forward-curving battering-ram horns of rough stone; venting: orbiting stone fragments and drifting dust.
* Identity JSON (`data/art/dragons/elder-dragons/terrador.json`):
  * id: "dragons/elder-dragons/terrador"
  * kind: "dragon"
  * cardId: "UNIT_TERRADOR" (the card is SD-027)
  * description: "an Elder Dragon of deep burnt-sienna and antique-bronze scales veined with vivid turquoise, trailing drifting dust and stone fragments, wings like slabs of weathered stone edged in antique bronze"
  * silhouette: "Massive, low-slung, heavily armoured dragon with a club-tipped tail and colossal shoulders"
  * scaleTexture: "Coarse, stone-like plates in burnt sienna and antique bronze, veined with vivid turquoise"
  * wingMembrane: "Heavy slabs of weathered stone joined by thick, flexible tendon, edged in antique bronze"
  * hornsAndCrest: "Four forward-curving battering-ram horns of rough stone"
  * elementalVenting: "Orbiting stone fragments and drifting dust"
  * notes: "Skeletal identity, first pass -- aligned to Draknara Thorne (Earth) per docs/codex/heroes/sovereign_dawn_codex.md's Element Alignment table. No archived source material; colours grounded in Draknara's own palette (Deep Burnt Sienna / Vivid Turquoise / Antique Bronze)."

---

### SD-028: Fulgora (Lightning Elder Dragon)
* Bond: Drakneta Thorne (SD-008)
* Master Description: An Elder Dragon of electric-gold and arc-white scales, wreathed in crackling static, wings like sheets of storm-cloud laced with lightning.
* Morphology in short: Sleek, needle-nosed dragon with swept delta wings and a forked tail; scales: overlapping polished scales in electric gold and arc-white with a metallic sheen; wings: swept membrane like storm cloud, with branching lightning running through it; horns: rearward-swept, lightning-rod horns arcing with static; venting: branching lightning forks along the spine and off the wingtips.
* Identity JSON (`data/art/dragons/elder-dragons/fulgora.json`):
  * id: "dragons/elder-dragons/fulgora"
  * kind: "dragon"
  * cardId: "UNIT_FULGORA" (the card is SD-028)
  * description: "an Elder Dragon of electric-gold and arc-white scales, wreathed in crackling static, wings like sheets of storm-cloud laced with lightning"
  * silhouette: "Sleek, needle-nosed dragon with swept delta wings and a forked tail"
  * scaleTexture: "Overlapping polished scales in electric gold and arc-white with a metallic sheen"
  * wingMembrane: "Swept membrane like storm cloud, with branching lightning running through it"
  * hornsAndCrest: "Rearward-swept, lightning-rod horns arcing with static"
  * elementalVenting: "Branching lightning forks along the spine and off the wingtips"
  * notes: "Skeletal identity, first pass -- aligned to Drakneta Thorne (Lightning) per docs/codex/heroes/sovereign_dawn_codex.md's Element Alignment table. No archived source material; colours grounded in Drakneta's own palette (Electric Gold / Bright Gold / Arc White)."

---

### SD-029: Zephyros (Wind Elder Dragon)
* Bond: Draknava Thorne (SD-009)
* Master Description: An Elder Dragon of windswept-jade and gossamer-silver scales, trailing wisps of racing cloud, wings like vast sails of sea-glass silk.
* Morphology in short: Lithe, light-boned soaring dragon with a long streamer tail and high-aspect wings; scales: fine overlapping scales in windswept jade and gossamer silver, feathering toward the edges; wings: vast, translucent sails of sea-glass silk; horns: backward-swept, fluted crest; venting: spiralling wind eddies and wisps of racing cloud trailing the body.
* Identity JSON (`data/art/dragons/elder-dragons/zephyros.json`):
  * id: "dragons/elder-dragons/zephyros"
  * kind: "dragon"
  * cardId: "UNIT_ZEPHYROS" (the card is SD-029)
  * description: "an Elder Dragon of windswept-jade and gossamer-silver scales, trailing wisps of racing cloud, wings like vast sails of sea-glass silk"
  * silhouette: "Lithe, light-boned soaring dragon with a long streamer tail and high-aspect wings"
  * scaleTexture: "Fine overlapping scales in windswept jade and gossamer silver, feathering toward the edges"
  * wingMembrane: "Vast, translucent sails of sea-glass silk"
  * hornsAndCrest: "Backward-swept, fluted crest"
  * elementalVenting: "Spiralling wind eddies and wisps of racing cloud trailing the body"
  * notes: "Skeletal identity, first pass -- aligned to Draknava Thorne (Wind) per docs/codex/heroes/sovereign_dawn_codex.md's Element Alignment table. No archived source material; colours grounded in Draknava's own palette (Windswept Jade / Gossamer Silver / Polished Nickel)."

---

### SD-030: Venomis (Poison Elder Dragon)
* Bond: Draknoxa Thorne (SD-010)
* Master Description: An Elder Dragon of toxic-orchid-magenta and tarnished-brass scales, wreathed in drifting toxic mist, wings like tattered sheets veined in vibrant acid-lime.
* Morphology in short: Low-slung, hunched viper-dragon with a wide, flared neck hood; scales: segmented plates in toxic orchid magenta and tarnished brass; wings: tattered, perforated membrane veined in vibrant acid lime; horns: flared neck hood crowned with curved, venom-grooved spines; venting: drips of acid-lime venom and a sickly mist from the jaws.
* Identity JSON (`data/art/dragons/elder-dragons/venomis.json`):
  * id: "dragons/elder-dragons/venomis"
  * kind: "dragon"
  * cardId: "UNIT_VENOMIS" (the card is SD-030)
  * description: "an Elder Dragon of toxic-orchid-magenta and tarnished-brass scales, wreathed in drifting toxic mist, wings like tattered sheets veined in vibrant acid-lime"
  * silhouette: "Low-slung, hunched viper-dragon with a wide, flared neck hood"
  * scaleTexture: "Segmented plates in toxic orchid magenta and tarnished brass"
  * wingMembrane: "Tattered, perforated membrane veined in vibrant acid lime"
  * hornsAndCrest: "Flared neck hood crowned with curved, venom-grooved spines"
  * elementalVenting: "Drips of acid-lime venom and a sickly mist from the jaws"
  * notes: "Skeletal identity, first pass -- aligned to Draknoxa Thorne (Poison) per docs/codex/heroes/sovereign_dawn_codex.md's Element Alignment table. No archived source material; colours grounded in Draknoxa's own palette (Toxic Orchid Magenta / Vibrant Acid Lime / Tarnished Brass)."

---

## 4. How the Fields Reach the Prompt

The dragons are text-to-image (no incoming photo). The prompts come from the templates in `data/art/_templates/dragons/` through `tools/generators/gen_prompt.py`:

| Template | Card | What it uses |
| --- | --- | --- |
| `pose-dragon.txt` | `<Name>_X_Pose` (1_Alpha) | A full-body, head-to-tail studio shot on a cream backdrop: the dragon's name, `description`, then the morphology line (silhouette, scales, wings, horns and crest, venting), standing in a neutral three-quarter stance with wings folded |
| `head-dragon.txt` | `<Name>_X_Head` (2_Studies) | The head close-up; the morphology line uses only the head fields (`scaleTexture`, `hornsAndCrest`) |
| `scene-lair-dragon.txt` | `<Name>_Scene_Lair` (5_Scenes) | The dragon in its lair |

The negative prompt keeps out extra limbs, extra heads or wings, deformed anatomy, mismatched scales, humanoid features and text. The companion frames place the dragon beside her bonded sister (see `tools/art/dragon_companions.py`).
