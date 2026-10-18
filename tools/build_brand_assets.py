"""
Build brand assets from the chosen logo (concept 3, crane, forest + amber).

  images/brand/crane-mark-{96,192,512}.png   round mark, transparent
  images/brand/favicon-{32,48}.png, apple-touch-icon.png, ../favicon.ico
  images/brand/logo-crane-full.png           full lockup (mark + name) on white
  images/og-image.jpg                        1200x630 social share image
"""
import os
import shutil

import numpy as np
from PIL import Image, ImageDraw

ROOT = r'C:\Users\is1lv\PRJGENUI-Workforce'
SRC = os.path.join(ROOT, 'images', 'logos', 'forest', 'logo-3-crane.png')
BRAND = os.path.join(ROOT, 'images', 'brand')
os.makedirs(BRAND, exist_ok=True)

full = Image.open(SRC).convert('RGB')
a = np.asarray(full).astype(int)
nonwhite = (a.min(axis=2) < 235)

# first contiguous band of non-white rows = the round mark (name sits below a white gap)
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
print('mark bbox', x0, y0, x1, y1, 'size', x1 - x0, y1 - y0)
side = max(x1 - x0, y1 - y0)
cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
box = (round(cx - side / 2), round(cy - side / 2), round(cx + side / 2), round(cy + side / 2))
mark = full.crop(box)

# antialiased circular alpha, supersampled
S = 4
m = Image.new('L', (mark.width * S, mark.height * S), 0)
ImageDraw.Draw(m).ellipse((S, S, mark.width * S - S, mark.height * S - S), fill=255)
alpha = m.resize(mark.size, Image.LANCZOS)
mark = mark.convert('RGBA')
mark.putalpha(alpha)
mark.save(os.path.join(BRAND, 'crane-mark-source.png'))

for px in (96, 192, 512):
    mark.resize((px, px), Image.LANCZOS).save(os.path.join(BRAND, f'crane-mark-{px}.png'), optimize=True)
for px in (32, 48):
    mark.resize((px, px), Image.LANCZOS).save(os.path.join(BRAND, f'favicon-{px}.png'), optimize=True)

# favicon.ico (16/32/48) at site root
ico_src = mark.resize((256, 256), Image.LANCZOS)
ico_src.save(os.path.join(ROOT, 'favicon.ico'), sizes=[(16, 16), (32, 32), (48, 48)])

# apple touch icon: opaque (iOS fills transparency with black), mark on white
apple = Image.new('RGB', (180, 180), 'white')
inner = mark.resize((148, 148), Image.LANCZOS)
apple.paste(inner, (16, 16), inner)
apple.save(os.path.join(BRAND, 'apple-touch-icon.png'), optimize=True)

# full lockup, cropped to content
fb = np.where(nonwhite.any(axis=1))[0], np.where(nonwhite.any(axis=0))[0]
pad = 30
lock = full.crop((max(fb[1].min() - pad, 0), max(fb[0].min() - pad, 0),
                  min(fb[1].max() + pad, full.width), min(fb[0].max() + pad, full.height)))
lock.save(os.path.join(BRAND, 'logo-crane-full.png'), optimize=True)

# social share image
og_path = os.path.join(ROOT, 'images', 'og-image.jpg')
bk = os.path.join(ROOT, 'tools', 'backup-navy-gold', 'og-image.jpg')
if not os.path.exists(bk):
    shutil.copy2(og_path, bk)
W, H = 1200, 630
og = Image.new('RGB', (W, H), (255, 255, 255))
d = ImageDraw.Draw(og)
d.rectangle((0, 0, W, 12), fill=(0xE8, 0xA3, 0x3D))
d.rectangle((0, H - 12, W, H), fill=(0x1F, 0x3A, 0x2E))
target_h = 520
lw = round(lock.width * target_h / lock.height)
lk = lock.resize((lw, target_h), Image.LANCZOS)
og.paste(lk, ((W - lw) // 2, (H - target_h) // 2))
og.save(og_path, quality=92, optimize=True)
print('og', og.size, os.path.getsize(og_path) // 1024, 'KB')

# contact sheet for checking (kept out of the deploy via research/)
sheet = Image.new('RGB', (1200, 420), (0xFA, 0xF9, 0xF6))
x = 20
for px in (192, 96, 48, 32):
    t = mark.resize((px, px), Image.LANCZOS)
    sheet.paste(t, (x, 20), t)
    x += px + 24
dark = Image.new('RGB', (360, 120), (0x14, 0x27, 0x1E))
dd = ImageDraw.Draw(dark)
t = mark.resize((72, 72), Image.LANCZOS)
dd.ellipse((24 - 3, 24 - 3, 24 + 72 + 3, 24 + 72 + 3), outline=(0xE8, 0xA3, 0x3D), width=2)
dark.paste(t, (24, 24), t)
sheet.paste(dark, (20, 250))
sheet.paste(apple, (400, 230))
sheet.paste(og.resize((600, 315)), (600, 20))
sheet.save(os.path.join(ROOT, 'research', 'brand-assets-check.png'))
print('done')
