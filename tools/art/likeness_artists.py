#!/usr/bin/env python3
"""Artist-only likeness entry point; shared intake, models and algorithms."""
import sys

import likeness


def main(argv=None, embedder=None):
    return likeness.main(argv, embedder=embedder, domain="artists")


if __name__ == "__main__":
    sys.exit(main() or 0)
