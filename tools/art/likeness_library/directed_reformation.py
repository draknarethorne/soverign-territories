"""Compatibility import for the explicitly opted-in experimental reformation module."""
import sys

from tools.art.likeness_experiments import directed_reformation as _implementation

sys.modules[__name__] = _implementation
