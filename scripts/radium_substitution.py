#!/usr/bin/env python3
"""Radium rebrand: rename the visible product name from Helium to Radium.

Runs after Helium's own name substitution (Chrome/Chromium -> Helium) and
translation step. It reuses Helium's grit helpers, so translated strings are
renamed too and the .xtb fingerprints are re-keyed to the new English text.

Phrases about Helium's servers, project and authors keep the Helium name,
since those services are run by imput and the code is theirs.

Usage: radium_substitution.py --sub -t <chromium src> [--backup-path <tar>]
"""

import multiprocessing
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'helium-chromium' / 'utils'))

# pylint: disable=wrong-import-position
import name_substitution as namesub
import name_substitution_utils as util

RULES = [
    # keep: Helium's own services and project
    (r'\bHelium (services|push server|Partner)\b', r'Helium_unreplace \1'),
    (r'\bdevelopment of Helium\b', r'development of Helium_unreplace'),
    (r'\bThe Helium Authors\b', r'The Helium_unreplace Authors'),
    # main replacement
    (r'\bHelium\b', r'Radium'),
    # cleanup
    (r'_unreplace', r''),
]
util.REPLACEMENT_REGEXES = [(re.compile(src), dst) for src, dst in RULES]

_replace_grit_tree = util.replace_grit_tree


def replace_grit_tree(text):
    """Like Helium's, but don't add an XML declaration the file didn't have
    (the onboarding page's string generator needs <grit-part> first)."""
    out, fp_map = _replace_grit_tree(text)
    if not text.lstrip().startswith('<?xml'):
        out = re.sub(r'^<\?xml[^>]*\?>\s*', '', out)
    return out, fp_map


util.replace_grit_tree = replace_grit_tree


def sanity():
    """Make sure the rules do what we expect."""
    cases = [
        ('Helium', 'Radium'),
        ('About Helium', 'About Radium'),
        ("Helium's memory", "Radium's memory"),
        ('Helium Labs', 'Radium Labs'),
        ('Allow connecting to Helium services', 'Allow connecting to Helium services'),
        ('Helium push server', 'Helium push server'),
        ('support the development of Helium.', 'support the development of Helium.'),
        ('Copyright 2026 The Helium Authors.', 'Copyright 2026 The Helium Authors.'),
        ('helium://settings', 'helium://settings'),
        ('Chrome Web Store', 'Chrome Web Store'),
    ]
    for source, expected in cases:
        got, _ = util.replace_text(source)
        assert got == expected, f'sanity: {source!r} -> {got!r}, want {expected!r}'


namesub.replacement_sanity = sanity

if __name__ == '__main__':
    # Worker processes must inherit the patched rules above.
    multiprocessing.set_start_method('fork')
    namesub.main()
