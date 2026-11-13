#!/usr/bin/env python3
"""Radium rebrand for Helium's first-run onboarding page.

Uses the Radium logo on the Welcome page and as the page's favicon. The
"Helium services" page keeps Helium's logo, since those services are imput's.
Fails loudly if Helium changes the Welcome page so this needs updating.

Usage: radium_onboarding.py <chromium src> <fork root>
"""

import shutil
import sys
from pathlib import Path


def main():
    src, root = Path(sys.argv[1]), Path(sys.argv[2])
    onboarding = src / 'components' / 'helium_onboarding'
    radium = root / 'resources' / 'radium'

    shutil.copyfile(radium / 'onboarding' / 'RadiumLogo.svelte',
                    onboarding / 'src' / 'components' / 'RadiumLogo.svelte')
    shutil.copyfile(radium / 'generated' / 'product_icon' / '128x128.png',
                    onboarding / 'public' / 'favicon.png')

    welcome = onboarding / 'src' / 'pages' / 'Welcome.svelte'
    text = welcome.read_text(encoding='utf-8')
    if 'RadiumLogo' in text:
        print('Welcome.svelte already uses RadiumLogo')
        return

    def replace(old, new, count):
        nonlocal text
        found = text.count(old)
        if found != count:
            raise SystemExit(f'Welcome.svelte: expected {count}x {old!r}, found {found}')
        text = text.replace(old, new)

    replace('        HeliumLogo,\n', '', 1)
    replace('<script lang="ts">\n',
            '<script lang="ts">\n    import RadiumLogo from "../components/RadiumLogo.svelte";\n', 1)
    replace('<HeliumLogo height=', '<RadiumLogo height=', 2)
    welcome.write_text(text, encoding='utf-8')
    print('Welcome.svelte now uses RadiumLogo')


if __name__ == '__main__':
    main()
