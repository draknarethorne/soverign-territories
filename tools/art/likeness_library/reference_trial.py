"""Compatibility import; experimental implementation lives in likeness_experiments."""
import sys
from tools.art.likeness_experiments import reference_trial as _implementation
sys.modules[__name__] = _implementation
