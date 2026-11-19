"""Compatibility import; experimental implementation lives in likeness_experiments."""
import sys
from tools.art.likeness_experiments import fragment_review as _implementation
sys.modules[__name__] = _implementation
