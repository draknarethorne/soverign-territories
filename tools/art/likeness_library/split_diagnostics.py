"""Compatibility import; experimental implementation lives in likeness_experiments."""
import sys
from tools.art.likeness_experiments import split_diagnostics as _implementation
sys.modules[__name__] = _implementation
