"""
Trace the chosen logo (crane, forest + amber) into clean SVG files.

Two layers, forest underneath and amber on top, each traced with potrace.
Amber that sits inside the circle is also filled into the forest layer so
there are no hairline gaps where the layers meet.

  images/brand/logo-crane-full.svg   mark + name
  images/brand/crane-mark.svg        round mark only
"""
import os

import numpy as np
from PIL import Image
import potrace

ROOT = r'C:\Users\is1lv\PRJGENUI-Workforce'
SRC = os.path.join(ROOT, 'images', 'logos', 'forest', 'logo-3-crane.png')
OUT = os.path.join(ROOT, 'images', 'brand')
FOREST, AMBER = '#1F3A2E', '#E8A33D'
UP = 2  # trace at 2x for smoother curves


def masks(img, circle):
    img = img.resize((img.width * UP, img.height * UP), Image.LANCZOS)
    a = np.asarray(img.convert('RGB')).astype(float)
    r, b = a[..., 0], a[..., 2]
    amber = np.clip((r - b) / 171, 0, 1) > 0.5
    forest = np.clip((255 - r) / 224, 0, 1) > 0.5
    if circle is not None:
        cx, cy, rad = [v * UP for v in circle]
        yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
        inside = (xx - cx) ** 2 + (yy - cy) ** 2 <= (rad - 1) ** 2
        forest = forest | (amber & inside)
    return forest, amber


def path_d(mask):
    bm = potrace.Bitmap(~mask)
    plist = bm.trace(turdsize=12, turnpolicy=potrace.POTRACE_TURNPOLICY_MINORITY,
                     alphamax=1.0, opticurve=True, opttolerance=0.3)
    s = 1 / UP
    f = lambda p: f'{p.x * s:.1f} {p.y * s:.1f}'
    parts = []
    for curve in plist:
        parts.append(f'M{f(curve.start_point)}')
        for seg in curve.segments:
            if seg.is_corner:
                parts.append(f'L{f(seg.c)}L{f(seg.end_point)}')
            else:
                parts.append(f'C{f(seg.c1)} {f(seg.c2)} {f(seg.end_point)}')
        parts.append('Z')
    return ''.join(parts)


def write_svg(name, img, circle, title, viewbox=None):
    forest, amber = masks(img, circle)
    vb = viewbox or (0, 0, img.width, img.height)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb[0]} {vb[1]} {vb[2]} {vb[3]}" '
           f'role="img" aria-label="{title}"><title>{title}</title>'
           f'<path fill="{FOREST}" fill-rule="evenodd" d="{path_d(forest)}"/>'
           f'<path fill="{AMBER}" fill-rule="evenodd" d="{path_d(amber)}"/></svg>\n')
    p = os.path.join(OUT, name)
    with open(p, 'w', encoding='utf-8', newline='') as f:
        f.write(svg)
    print(name, os.path.getsize(p) // 1024, 'KB')


full = Image.open(SRC).convert('RGB')
arr = np.asarray(full).astype(int)
nonwhite = arr.min(axis=2) < 235

# round mark = first contiguous band of non-white rows
rows = nonwhite.sum(axis=1) > 0
y = 0
while not rows[y]:
    y += 1
y0 = y
while rows[y]:
    y += 1
y1 = y
cols = np.where(nonwhite[y0:y1].any(axis=0))[0]
x0, x1 = cols.min(), cols.max() + 1
circle = ((x0 + x1) / 2, (y0 + y1) / 2, min(x1 - x0, y1 - y0) / 2)

# full lockup with small padding
ys, xs = np.where(nonwhite.any(axis=1))[0], np.where(nonwhite.any(axis=0))[0]
pad = 20
vb = (int(xs.min() - pad), int(ys.min() - pad), int(xs.max() - xs.min() + 2 * pad), int(ys.max() - ys.min() + 2 * pad))
write_svg('logo-crane-full.svg', full, circle, 'PRJGENUI Workforce', vb)

# mark only: crop to the circle's square, blank everything outside it
side = int(circle[2] * 2) + 4
mx0, my0 = int(circle[0] - side / 2), int(circle[1] - side / 2)
mark = full.crop((mx0, my0, mx0 + side, my0 + side))
write_svg('crane-mark.svg', mark, (side / 2, side / 2, circle[2]), 'PRJGENUI Workforce mark')
