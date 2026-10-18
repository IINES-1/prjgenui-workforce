"""Resize and compress the generated PNGs into web-ready progressive JPEGs.

Mirrors the homerenovationguides pipeline: max 1600px wide for the hero,
1200px for supporting photos, JPEG quality 82, progressive, EXIF stripped.
Also crops a 1200x630 OG image from the hero.
"""
from pathlib import Path
from PIL import Image

SRC = Path(r"C:\Users\is1lv\.factory\generated-images")
OUT = Path(r"C:\Users\is1lv\PRJGENUI-Workforce\images")
OUT.mkdir(exist_ok=True)

JOBS = [
    ("hyperrealistic-editorial-photograph-shot-on-a-ca.png", "hero-decorator-cutting-in.jpg", 1600),
    ("hyperrealistic-group-photograph-shot-on-a-sony-a.png", "crew-surrey-school.jpg", 1400),
    ("hyperrealistic-close-up-photograph-macro-style-s.png", "proof-satin-door-supervisor.jpg", 1200),
    ("hyperrealistic-photograph-shot-on-a-fujifilm-gfx.png", "verify-cscs-card-check.jpg", 1200),
    ("hyperrealistic-photograph-shot-on-a-leica-sl2-wi.png", "deploy-dawn-van-hampshire.jpg", 1400),
]


def save_jpeg(img: Image.Image, dest: Path, max_w: int) -> None:
    img = img.convert("RGB")
    if img.width > max_w:
        ratio = max_w / img.width
        img = img.resize((max_w, round(img.height * ratio)), Image.LANCZOS)
    img.save(dest, "JPEG", quality=82, optimize=True, progressive=True)
    print(f"{dest.name:40s} {img.width}x{img.height}  {dest.stat().st_size // 1024} KB")


for src_name, out_name, max_w in JOBS:
    with Image.open(SRC / src_name) as im:
        save_jpeg(im, OUT / out_name, max_w)

# OG image: 1200x630 centre-weighted crop of the hero
with Image.open(SRC / JOBS[0][0]) as im:
    im = im.convert("RGB")
    target_ratio = 1200 / 630
    w, h = im.size
    if w / h > target_ratio:
        new_w = round(h * target_ratio)
        left = (w - new_w) // 2
        im = im.crop((left, 0, left + new_w, h))
    else:
        new_h = round(w / target_ratio)
        top = (h - new_h) // 2
        im = im.crop((0, top, w, top + new_h))
    im = im.resize((1200, 630), Image.LANCZOS)
    dest = OUT / "og-image.jpg"
    im.save(dest, "JPEG", quality=85, optimize=True, progressive=True)
    print(f"{dest.name:40s} 1200x630  {dest.stat().st_size // 1024} KB")
