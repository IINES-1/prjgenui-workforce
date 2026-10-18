"""
Recolour the six logo concepts from navy/gold to forest/amber (palette 1)
and build logos-forest.html to review them.

Pixels are classified by tint (blue-ish = navy, orange-ish = gold, neutral
greys and white are left alone). Each class is remapped with a per-channel
affine map anchored at white, so anti-aliased edges blend correctly.
The source navy/gold are measured from each image, not assumed.
"""
import glob
import os
import re

import numpy as np
from PIL import Image

ROOT = r'C:\Users\is1lv\PRJGENUI-Workforce'
SRC = os.path.join(ROOT, 'images', 'logos')
OUT = os.path.join(SRC, 'forest')
OUT_WEB = os.path.join(OUT, 'web')
os.makedirs(OUT_WEB, exist_ok=True)

FOREST = np.array([0x1F, 0x3A, 0x2E], float)
AMBER = np.array([0xE8, 0xA3, 0x3D], float)


def remap_from_white(p, src, dst):
    k = (255 - dst) / np.maximum(255 - src, 1)
    return 255 - (255 - p) * k


def recolour(img):
    p = np.asarray(img.convert('RGB'), float)
    r, g, b = p[..., 0], p[..., 1], p[..., 2]
    navy_w = np.clip((b - r - 3) / 10, 0, 1) * (b >= g)
    gold_w = np.clip((r - b - 8) / 20, 0, 1) * (r >= g)

    def solid(mask, thresh):
        m = mask > thresh
        return np.median(p[m], axis=0) if m.sum() > 50 else None

    navy_src = solid(navy_w * (255 - r) / 255, 0.6)
    gold_src = solid(gold_w * (r - b) / 255, 0.55)
    out = p.copy()
    if navy_src is not None:
        mapped = remap_from_white(p, navy_src, FOREST)
        out = out * (1 - navy_w[..., None]) + mapped * navy_w[..., None]
    if gold_src is not None:
        mapped = remap_from_white(p, gold_src, AMBER)
        out = out * (1 - gold_w[..., None]) + mapped * gold_w[..., None]
    return Image.fromarray(np.clip(out, 0, 255).astype('uint8'), 'RGB'), navy_src, gold_src


for f in sorted(glob.glob(os.path.join(SRC, 'logo-*.png'))):
    name = os.path.splitext(os.path.basename(f))[0]
    img = Image.open(f)
    new, navy_src, gold_src = recolour(img)
    new.save(os.path.join(OUT, name + '.png'), optimize=True)
    w = 900
    web = new.resize((w, round(new.height * w / new.width)), Image.LANCZOS)
    web.save(os.path.join(OUT_WEB, name + '.webp'), quality=88, method=6)
    print(name, 'navy', None if navy_src is None else navy_src.astype(int).tolist(),
          'gold', None if gold_src is None else gold_src.astype(int).tolist(), web.size)

# ---- review page, built from logos.html so styling stays identical ----
src_html = open(os.path.join(ROOT, 'logos.html'), encoding='utf-8').read()
head = src_html[:src_html.index('<!-- ====== Intro ====== -->')]
head = head.replace('Logo options and a few questions', 'Logo options in the new colours')

cards = [
    ('01', 'Shield', 'logo-1-shield', 900, 900,
     'Forest shield with an amber P, the company name underneath and the tagline in amber. Reads as protection and vetting, which is the business. The shield works on its own as an icon.'),
    ('02', 'Paint roller', 'logo-2-paint-roller', 900, 494,
     'The P is built around a paint roller, so the trade is in the mark itself. The wide layout suits a website header and letterhead. The most specific to painting and decorating, which is a strength now and a limit if you add other trades later.'),
    ('03', 'Crane', 'logo-3-crane', 900, 900,
     'A tower crane forms the stem of the P inside a round forest badge. Says construction broadly rather than one trade. The round layout suits social media profiles and the browser tab.'),
    ('04', 'Crew badge', 'logo-4-badge', 900, 900,
     'A round seal with three workers in hard hats and hi-vis, the full company name around the edge and the founding year. The most established look of the six, and the busiest, so it needs room and the text gets small on a phone.'),
    ('05', 'PW monogram', 'logo-5-monogram', 900, 494,
     'An amber PW in a forest square, with the name alongside and the tagline under a thin amber rule. The most corporate of the six. The monogram stands on its own at small sizes.'),
    ('06', 'Hard hat and tick', 'logo-6-hardhat-tick', 900, 450,
     'A forest hard hat with an amber tick cut into it, next to the name in heavy capitals. The tick says checked and approved, which is the promise the website makes. The simplest of the six, so it stays sharp at any size.'),
]
card_html = ''.join(f'''
      <div class="logo-card">
        <div class="img"><img src="images/logos/forest/web/{slug}.webp" alt="Logo concept {n}: {title}, in forest green and amber" width="{w}" height="{h}" loading="lazy"></div>
        <div class="body">
          <div class="num">{n}</div>
          <h3>{title}</h3>
          <p>{desc}</p>
          <a class="open" href="images/logos/forest/{slug}.png" target="_blank" rel="noopener">Open full size</a>
        </div>
      </div>
''' for n, title, slug, w, h, desc in cards)

body = f'''<!-- ====== Intro ====== -->
<section class="review-head">
  <div class="wrap">
    <h1>The six logos in the new colours</h1>
    <p class="lede">This page isn't part of the public website. These are the same six concepts as before, shown in the forest green and amber the website now uses.</p>
  </div>
</section>

<section class="section" id="logos">
  <div class="wrap">
    <div class="section-head">
      <h2>Logo concepts</h2>
      <p class="lede">These are recoloured versions of the concepts, so you can judge them against the website. Whichever you pick gets redrawn as a clean vector file so it stays sharp everywhere, from the browser tab to the side of a van. Text, spacing and colour can all be adjusted.</p>
    </div>
    <div class="logo-grid">
{card_html}
    </div>
    <div class="reply-note">Reply with the number of the logo you prefer, or what you would take from each.</div>
  </div>
</section>

<footer class="wrap review-footer">
  <span>PRJGENUI Workforce Ltd. Company number 13205257. Registered office: 124 City Road, London EC1V 2NX.</span>
  <a href="index.html">Back to the website</a>
</footer>

</body>
</html>
'''
open(os.path.join(ROOT, 'logos-forest.html'), 'w', encoding='utf-8', newline='').write(head + body)
print('wrote logos-forest.html')
