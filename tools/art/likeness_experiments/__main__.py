"""Explicit entrypoint for experimental likeness compositions."""

import argparse
import importlib
import pathlib
import sys


ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
PACKAGE = "tools.art.likeness_experiments"


OPERATIONS = {
    "candidate-replay": "likeness_candidate_replay",
    "character-packet": "likeness_character_packet",
    "disposition-trial": "likeness_disposition_trial",
    "entrance-trial": "likeness_entrance_trial",
    "fragment-trial": "likeness_fragment_trial",
    "hypothesis-trial": "likeness_hypothesis_trial",
    "legacy-reconcile": "reconcile_command",
    "observe": "likeness_observe",
    "reconcile-trial": "likeness_reconcile_trial",
    "reference-trial": "likeness_reference_trial",
    "review-packet": "likeness_review_packet",
    "shadow": "likeness_shadow",
    "view-associations": "likeness_view_associations",
}


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "Experimental likeness compositions and explicit legacy controllers only. "
            "These flows reuse stable "
            "FULL/LEAN/FAST primitives and add explicitly selected trial steps. "
            "legacy-reconcile preserves an explicit legacy command outside normal intake."
        ),
    )
    parser.add_argument(
        "operation",
        choices=("directed-rebase", *OPERATIONS),
        help="run one explicit experimental composition or compatibility controller",
    )
    args, forwarded = parser.parse_known_args(argv)
    if args.operation == "directed-rebase":
        if "--directed" not in forwarded or "--directed-recipe" not in forwarded:
            parser.error("directed-rebase requires explicit --directed and --directed-recipe")
        from tools.art import rebase_flow

        return rebase_flow.main(forwarded)
    module = importlib.import_module(f"{PACKAGE}.{OPERATIONS[args.operation]}")
    return module.main(forwarded)


if __name__ == "__main__":
    sys.exit(main())
