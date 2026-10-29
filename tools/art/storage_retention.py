#!/usr/bin/env python3
"""Command-line entry point for sandbox run retention."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.art.likeness_library.storage_retention import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
