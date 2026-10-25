"""Recipe ids and step orders of published v5-v15 preparation runs, kept only so their reports still verify.

New runs use the current recipe (`pipeline.STEPS`); nothing here produces images. When the last v5-v15 report is
deleted from the sandbox, this module and its branches in `image_preparation.validate` can go.
"""

def ids(first, last):
    return frozenset(f"preparation-comparison-v{n}" for n in range(first, last + 1))


GEOMETRY = ids(5, 15)        # every row carries geometry and a recommendation
TRACED = ids(6, 15)          # rows carry a processing trace and face eligibility
SCOPED = ids(7, 15)          # rows carry a source/artist scope
SAME_MASK = ids(11, 15)      # an eraser came with a Navier-Stokes comparison on the same mask
V15_STEPS = ("first-crop", "eraser", "second-crop", "composition", "denoise", "tone")
OLD_STEPS = ("first-crop", "eraser", "second-crop", "denoise", "tone")


def step_names(recipe_id):
    return list(V15_STEPS if recipe_id == "preparation-comparison-v15" else OLD_STEPS)
