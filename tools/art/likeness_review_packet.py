"""Compatibility entrypoint; implementation is in likeness_experiments."""
import sys
from tools.art.likeness_experiments import likeness_review_packet as _implementation
sys.modules[__name__] = _implementation
if __name__ == "__main__":
    raise SystemExit(_implementation.main())
