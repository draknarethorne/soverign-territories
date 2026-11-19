"""Compatibility import for explicitly opted-in experimental lifecycle regrouping."""
import sys

from tools.art.likeness_experiments import group_lifecycle as _implementation

sys.modules[__name__] = _implementation
