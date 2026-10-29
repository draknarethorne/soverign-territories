"""Recipe ids and step orders of published preparation runs, kept so their reports still verify.

New runs use the current recipe; nothing here produces images.
Published receipts keep their recorded step order and validation contracts.
"""

def ids(first, last):
    return frozenset(f"preparation-comparison-v{n}" for n in range(first, last + 1))


GEOMETRY = ids(5, 20)        # every row carries geometry and a recommendation
TRACED = ids(6, 20)          # rows carry a processing trace and face eligibility
SCOPED = ids(7, 20)          # rows carry a source/artist scope
SAME_MASK = ids(11, 15)      # an eraser came with a Navier-Stokes comparison on the same mask
V15_STEPS = ("first-crop", "eraser", "second-crop", "composition", "denoise", "tone")
OLD_STEPS = ("first-crop", "eraser", "second-crop", "denoise", "tone")


def step_names(recipe_id):
    if recipe_id in ids(17, 20):
        return ["first-crop", "eraser", "residual-crop", "reconstruction", "composition", "denoise", "tone"]
    if recipe_id == "preparation-comparison-v16":
        return ["first-crop", "second-crop", "eraser", "composition", "denoise", "tone"]
    return list(V15_STEPS if recipe_id == "preparation-comparison-v15" else OLD_STEPS)
