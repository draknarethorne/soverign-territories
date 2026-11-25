"""Shared assembly and first-phase scaffolding for generic and named heroes."""
from scaffold_sister_studio import norm
from template_paths import template_path

BAREFOOT = "data/art/wardrobe/footwear/barefoot/barefoot.json"
DEFAULT_HEELS = "data/art/wardrobe/footwear/heels/matching-open-toed-heels.json"


def card_factory(ident, out):
    """A base-set card for this hero: card(art_id, stage, folder, stem, template, comps, ...) with the hero's identity and output folder filled in."""
    def card(art_id, stage, folder, stem, template, comps=None, denoise="~0.5-0.7", note=None, **extra):
        body = {"artId": art_id, "kind": "base-set", "stage": stage, "heroArt": ident, "template": template_path(template),
                "output": out(folder, stem), "denoise": denoise, **extra}
        if comps:
            body["components"] = comps
        if note:
            body["notes"] = note
        return body
    return card


def alpha_chain(wr, card, slug, hero, female, heels):
    """1_Alpha, the creation chain every angel has: Prime (A-pose from the photo), Bare (the figure), and for women the Footwear step
    (Barefoot and Heels A-poses fed the Bare image). Men stay barefoot in every A-pose, so they have no footwear step."""
    sex = "female" if female else "male"
    wr.write("alpha", f"{slug}-alpha-prime", card(f"{slug}-alpha-prime", "alpha", "alpha", f"{hero}_Alpha_1_Prime", f"pose-{sex}-human.txt", denoise="~1.0",
             note=f"{hero} Prime A-pose, built from the original photo.", figureProfile="standard"))
    bare_tpl = "bare-human.txt" if female else "bare-male-human.txt"
    study = "bare-skin-study" if female else "bare-skin-study-male"
    wr.write("alpha", f"{slug}-alpha-bare-figure", card(f"{slug}-alpha-bare-figure", "alpha", "alpha", f"{hero}_Alpha_2_Bare_Figure", bare_tpl,
             {"wearing": f"data/art/wardrobe/swimwear/base/edit/{study}.json"}, name="Bare edit: bare skin figure",
             note="Alpha 2 Bare: fed the Prime, sets the individual build and likeness."))
    if female:
        wr.write("alpha", f"{slug}-alpha-barefoot", card(f"{slug}-alpha-barefoot", "alpha", "alpha", f"{hero}_Alpha_3_Barefoot", "pose-female-human.txt",
                 {"footwear": "data/art/wardrobe/footwear/barefoot/barefoot-a-pose.json"}, note="Alpha 3 Barefoot A-pose, fed the Bare image."))
        wr.write("alpha", f"{slug}-alpha-heels", card(f"{slug}-alpha-heels", "alpha", "alpha", f"{hero}_Alpha_3_Heels", "pose-female-human.txt",
                 {"footwear": norm(heels)}, note="Alpha 3 Heeled A-pose, fed the Bare image."))
