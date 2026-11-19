"""Compatibility import; experimental implementation lives in likeness_experiments."""
import sys
from tools.art.likeness_experiments import appearance_context as _implementation
sys.modules[__name__] = _implementation
