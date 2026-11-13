#!/usr/bin/env python3
"""Generate Radium's branding files.

Writes, next to this script:
  branding/app_icon/raw.png (1024), branding/app_icon/file.png (512)
  branding/product_logo.svg, branding/product_logo.icon,
  branding/product_logo_color.icon, branding/product_logo_22_mono.png
  branding/product_logo{,_white}{,_200}.png  (wordmarks)
  generated/product_icon/NxN.png
  radium.svg (master app icon)

Needs: python3 with fontTools, rsvg-convert, Noto Sans Medium.
The mark: a glowing core, an orbit ring with a gap, and an electron
sitting in the gap.
"""

import math
import subprocess
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
BRANDING = HERE / 'branding'
GENERATED = HERE / 'generated' / 'product_icon'
FONT = Path('/usr/share/fonts/noto/NotoSans-Medium.ttf')

GAP_CENTER = -45.0  # degrees, screen coords (y down): upper right
GAP_WIDTH = 58.0

BG_TOP = '#12301F'
BG_BOTTOM = '#07140C'
GLOW = '#3DFF8F'
MARK = '#8DFFB9'
MARK_CORE = '#D9FFE8'
FLAT_BG = '#0F2A1B'
FLAT_MARK = '#7CF5A9'


def pt(cx, cy, r, deg):
    a = math.radians(deg)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def geometry(cx, cy, scale):
    """Mark geometry for a design whose orbit outer radius is `scale`."""
    t = 0.27 * scale  # ring thickness
    r_mid = scale - t / 2
    return {
        'cx': cx, 'cy': cy,
        'core': 0.40 * scale,
        'r_out': scale, 'r_in': scale - t, 'r_mid': r_mid, 't': t,
        'electron': 0.19 * scale,
        'start': GAP_CENTER + GAP_WIDTH / 2,
        'end': GAP_CENTER - GAP_WIDTH / 2 + 360,
    }


def ring_svg_path(g):
    cx, cy = g['cx'], g['cy']
    s, e = g['start'], g['end']
    o1, o2 = pt(cx, cy, g['r_out'], s), pt(cx, cy, g['r_out'], e)
    i1, i2 = pt(cx, cy, g['r_in'], s), pt(cx, cy, g['r_in'], e)
    c = g['t'] / 2
    f = lambda p: f'{p[0]:.2f} {p[1]:.2f}'
    return (f'M {f(o1)} A {g["r_out"]:.2f} {g["r_out"]:.2f} 0 1 1 {f(o2)} '
            f'A {c:.2f} {c:.2f} 0 0 1 {f(i2)} '
            f'A {g["r_in"]:.2f} {g["r_in"]:.2f} 0 1 0 {f(i1)} '
            f'A {c:.2f} {c:.2f} 0 0 1 {f(o1)} Z')


def mark_svg(g, fill, core_fill=None):
    ex, ey = pt(g['cx'], g['cy'], g['r_mid'], GAP_CENTER)
    core_fill = core_fill or fill
    return (f'<path d="{ring_svg_path(g)}" fill="{fill}"/>'
            f'<circle cx="{g["cx"]:.2f}" cy="{g["cy"]:.2f}" r="{g["core"]:.2f}" fill="{core_fill}"/>'
            f'<circle cx="{ex:.2f}" cy="{ey:.2f}" r="{g["electron"]:.2f}" fill="{fill}"/>')


def app_icon_svg(size=1024):
    s = size / 256
    g = geometry(128 * s, 128 * s, 82 * s)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="0.4" y2="1">
    <stop offset="0" stop-color="{BG_TOP}"/><stop offset="1" stop-color="{BG_BOTTOM}"/>
  </linearGradient>
  <radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="{GLOW}" stop-opacity="0.55"/>
    <stop offset="0.45" stop-color="{GLOW}" stop-opacity="0.18"/>
    <stop offset="1" stop-color="{GLOW}" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="core" cx="0.42" cy="0.38" r="0.65">
    <stop offset="0" stop-color="#FFFFFF"/><stop offset="0.5" stop-color="{MARK_CORE}"/>
    <stop offset="1" stop-color="{MARK}"/>
  </radialGradient>
  <filter id="soft" x="-30%" y="-30%" width="160%" height="160%">
    <feGaussianBlur stdDeviation="{6 * s:.1f}"/>
  </filter>
</defs>
<rect width="{size}" height="{size}" rx="{67 * s:.1f}" fill="url(#bg)"/>
<circle cx="{128 * s}" cy="{128 * s}" r="{110 * s}" fill="url(#glow)"/>
{f'<g filter="url(#soft)" opacity="0.9">{mark_svg(g, GLOW)}</g>' if size >= 48 else ''}
{mark_svg(g, MARK, 'url(#core)')}
</svg>
'''


def flat_logo_svg():
    g = geometry(128, 128, 82)
    return (f'<svg width="256" height="256" viewBox="0 0 256 256" fill="none" '
            f'xmlns="http://www.w3.org/2000/svg"><rect width="256" height="256" '
            f'rx="67" fill="{FLAT_BG}"/>{mark_svg(g, FLAT_MARK)}</svg>\n')


def icon_cmds(g, color=None):
    """Chromium .icon commands for the mark (ARC_TO follows SVG semantics)."""
    cx, cy = g['cx'], g['cy']
    s, e = g['start'], g['end']
    o1, o2 = pt(cx, cy, g['r_out'], s), pt(cx, cy, g['r_out'], e)
    i1, i2 = pt(cx, cy, g['r_in'], s), pt(cx, cy, g['r_in'], e)
    c = g['t'] / 2
    ex, ey = pt(cx, cy, g['r_mid'], GAP_CENTER)
    n = lambda v: f'{v:.2f}f'
    col = []
    if color:
        r, gg, b = (int(color[i:i + 2], 16) for i in (1, 3, 5))
        col = [f'PATH_COLOR_ARGB, 0xFF, 0x{r:02X}, 0x{gg:02X}, 0x{b:02X},']
    lines = ['NEW_PATH,'] + col + [
        f'MOVE_TO, {n(o1[0])}, {n(o1[1])},',
        f'ARC_TO, {n(g["r_out"])}, {n(g["r_out"])}, 0, 1, 1, {n(o2[0])}, {n(o2[1])},',
        f'ARC_TO, {n(c)}, {n(c)}, 0, 0, 1, {n(i2[0])}, {n(i2[1])},',
        f'ARC_TO, {n(g["r_in"])}, {n(g["r_in"])}, 0, 1, 0, {n(i1[0])}, {n(i1[1])},',
        f'ARC_TO, {n(c)}, {n(c)}, 0, 0, 1, {n(o1[0])}, {n(o1[1])},',
        'CLOSE,',
        'NEW_PATH,'] + col + [
        f'CIRCLE, {n(cx)}, {n(cy)}, {n(g["core"])},',
        'NEW_PATH,'] + col + [
        f'CIRCLE, {n(ex)}, {n(ey)}, {n(g["electron"])},',
    ]
    return lines


HEADER = ('// Radium branding, generated by resources/radium/make_branding.py\n'
          '// You can use, redistribute, and/or modify this source code under\n'
          '// the terms of the GPL-3.0 license that can be found in the LICENSE file.\n\n')


def mono_icon():
    g = geometry(28, 28, 23.5)
    return HEADER + 'CANVAS_DIMENSIONS, 56,\n' + '\n'.join(icon_cmds(g)) + '\n'


def color_icon():
    g = geometry(128, 128, 82)
    lines = ['CANVAS_DIMENSIONS, 256,', 'NEW_PATH,']
    r, gg, b = (int(FLAT_BG[i:i + 2], 16) for i in (1, 3, 5))
    lines += [f'PATH_COLOR_ARGB, 0xFF, 0x{r:02X}, 0x{gg:02X}, 0x{b:02X},',
              'ROUND_RECT, 0, 0, 256, 256, 67,']
    lines += icon_cmds(g, FLAT_MARK)
    return HEADER + '\n'.join(lines) + '\n'


def text_path(text, x, baseline, px):
    font = TTFont(FONT)
    glyphs = font.getGlyphSet()
    cmap = font.getBestCmap()
    upm = font['head'].unitsPerEm
    sc = px / upm
    out = []
    pen_x = x
    for ch in text:
        gname = cmap[ord(ch)]
        pen = SVGPathPen(glyphs)
        glyphs[gname].draw(TransformPen(pen, (sc, 0, 0, -sc, pen_x, baseline)))
        out.append(pen.getCommands())
        pen_x += glyphs[gname].width * sc
    return ' '.join(out), pen_x


def wordmark_svg(w, h, color):
    k = h / 32
    g = geometry(15.5 * k, 16 * k, 13.5 * k)
    d, _ = text_path('Radium', 35 * k, 24.5 * k, 23 * k)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}">{mark_svg(g, color)}'
            f'<path d="{d}" fill="{color}"/></svg>\n')


def mono22_svg():
    g = geometry(11, 11, 10)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" '
            f'viewBox="0 0 22 22">{mark_svg(g, "#3C4043")}</svg>\n')


def ntp_favicon_svg(size):
    """New tab page favicon, grey like Helium's other page favicons."""
    g = geometry(size / 2, size / 2, size * 0.47)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
            f'viewBox="0 0 {size} {size}">{mark_svg(g, "#3C4043")}</svg>\n')


def onboarding_logo_svelte():
    """Drop-in for the onboarding page's HeliumLogo (currentColor mark)."""
    g = geometry(128, 128, 120)
    return f'''<script lang="ts">
    // Radium branding, generated by resources/radium/make_branding.py
    let {{ height = "28px" }}: {{ height?: string }} = $props();
</script>

<span class="radium-logo" style:height aria-hidden="true">
    <svg viewBox="0 0 256 256" fill="none" xmlns="http://www.w3.org/2000/svg">{mark_svg(g, 'currentColor')}</svg>
</span>

<style>
    .radium-logo {{
        display: inline-flex;
        color: currentColor;
        flex: 0 0 auto;
        width: auto;
    }}

    .radium-logo svg {{
        display: block;
        width: auto;
        height: 100%;
    }}
</style>
'''


def render(svg_text, out_png, size=None):
    out_png.parent.mkdir(parents=True, exist_ok=True)
    cmd = ['rsvg-convert', '-o', str(out_png)]
    if size:
        cmd += ['-w', str(size), '-h', str(size)]
    subprocess.run(cmd, input=svg_text.encode(), check=True)


def main():
    (BRANDING / 'app_icon').mkdir(parents=True, exist_ok=True)
    master = app_icon_svg(1024)
    (HERE / 'radium.svg').write_text(master)
    render(master, BRANDING / 'app_icon' / 'raw.png', 1024)
    render(master, BRANDING / 'app_icon' / 'file.png', 512)
    for n in (16, 24, 32, 48, 64, 128, 256):
        # Render small sizes from a matching-size SVG so the blur scales too.
        render(app_icon_svg(n), GENERATED / f'{n}x{n}.png')
    (BRANDING / 'product_logo.svg').write_text(flat_logo_svg())
    (BRANDING / 'product_logo.icon').write_text(mono_icon())
    (BRANDING / 'product_logo_color.icon').write_text(color_icon())
    render(mono22_svg(), BRANDING / 'product_logo_22_mono.png')
    for suffix, color in (('', '#000000'), ('_white', '#FFFFFF')):
        render(wordmark_svg(140, 32, color), BRANDING / f'product_logo{suffix}.png')
        render(wordmark_svg(280, 64, color), BRANDING / f'product_logo{suffix}_200.png')
    for n in (16, 32):
        render(ntp_favicon_svg(n), HERE / 'favicons' / f'favicon_ntp_{n}.png')
    (HERE / 'onboarding').mkdir(exist_ok=True)
    (HERE / 'onboarding' / 'RadiumLogo.svelte').write_text(onboarding_logo_svelte())
    print('branding written to', HERE)


if __name__ == '__main__':
    main()
