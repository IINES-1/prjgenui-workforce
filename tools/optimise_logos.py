"""
Make web-sized WebP copies of the logo concepts for the review page.
Originals stay in images/logos/ for full-size viewing.
"""
import os
from PIL import Image

SRC = r'C:\Users\is1lv\PRJGENUI-Workforce\images\logos'
OUT = os.path.join(SRC, 'web')
os.makedirs(OUT, exist_ok=True)

for name in sorted(os.listdir(SRC)):
    if not name.lower().endswith('.png'):
        continue
    path = os.path.join(SRC, name)
    im = Image.open(path)
    # Flatten any transparency onto white so the thumbnail matches the original look
    if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info):
        rgba = im.convert('RGBA')
        bg = Image.new('RGB', rgba.size, (255, 255, 255))
        bg.paste(rgba, mask=rgba.split()[3])
        im = bg
    else:
        im = im.convert('RGB')
    im.thumbnail((900, 900), Image.LANCZOS)
    dest = os.path.join(OUT, os.path.splitext(name)[0] + '.webp')
    try:
        im.save(dest, 'WEBP', quality=84, method=6)
    except Exception as e:
        dest = os.path.join(OUT, os.path.splitext(name)[0] + '.png')
        im.quantize(256).save(dest, 'PNG', optimize=True)
        print('WebP failed, saved PNG instead:', e)
    print(f'{name}: {im.size} {os.path.getsize(path)//1024}KB -> {os.path.basename(dest)} {os.path.getsize(dest)//1024}KB')
