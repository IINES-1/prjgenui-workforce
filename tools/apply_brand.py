"""
Swap the placeholder "P" mark and SVG favicon for the chosen crane logo.
Run tools/build_brand_assets.py first.
"""
import re
import sys

ROOT = r'C:\Users\is1lv\PRJGENUI-Workforce'
PAGES = ['index.html', 'about.html', 'contact.html', 'privacy.html', 'terms.html', 'thanks.html',
         'dashboard.html', 'logos.html', 'logos-forest.html', 'colours.html', 'colours-2.html']

MARK_OLD = '<span class="mark">P</span>'
MARK_NEW = ('<img class="mark" src="images/brand/crane-mark-96.png" '
            'srcset="images/brand/crane-mark-96.png 1x, images/brand/crane-mark-192.png 2x" '
            'width="44" height="44" alt="">')
ICON_RE = re.compile(r'<link rel="icon" href="data:image/svg\+xml[^"]*">')
ICON_NEW = ('<link rel="icon" href="/favicon.ico" sizes="48x48">\n'
            '<link rel="icon" type="image/png" sizes="32x32" href="/images/brand/favicon-32.png">\n'
            '<link rel="icon" type="image/png" sizes="48x48" href="/images/brand/favicon-48.png">\n'
            '<link rel="apple-touch-icon" href="/images/brand/apple-touch-icon.png">')


def read(n):
    with open(f'{ROOT}\\{n}', 'r', encoding='utf-8', newline='') as f:
        return f.read()


def write(n, t):
    with open(f'{ROOT}\\{n}', 'w', encoding='utf-8', newline='') as f:
        f.write(t)


for name in PAGES:
    t = read(name)
    marks = t.count(MARK_OLD)
    t = t.replace(MARK_OLD, MARK_NEW)
    t, icons = ICON_RE.subn(ICON_NEW, t)
    t, logo = re.subn(r'("logo": ")https://prjgenuiworkforce\.co\.uk/images/og-image\.jpg',
                      r'\1https://prjgenuiworkforce.co.uk/images/brand/crane-mark-512.png', t)
    t = t.replace('styles.css?v=10', 'styles.css?v=11')
    write(name, t)
    print(f'{name}: marks={marks} icons={icons} jsonld-logo={logo}')

css = read('styles.css')
pairs = [
    ('.brand .mark{width:36px;height:36px;border-radius:var(--radius);background:var(--navy);color:#F3C77A;display:grid;place-items:center;font-family:var(--display);font-weight:800;font-size:1.25rem;flex:none;}',
     '.brand .mark{width:44px;height:44px;border-radius:50%;flex:none;object-fit:contain;display:block;}'),
    ('.footer .brand .mark{background:var(--gold);color:var(--navy-deep);}',
     '.footer .brand .mark{box-shadow:0 0 0 2px var(--gold);margin:2px;}'),
    ('styles.css  v10', 'styles.css  v11'),
]
for old, new in pairs:
    if old not in css:
        print('FAIL css:', old[:50])
        sys.exit(1)
    css = css.replace(old, new)
write('styles.css', css)

d = read('dashboard.html')
old = '.brand .mark{width:26px;height:26px;border-radius:var(--radius);background:var(--gold);color:var(--navy-dark);display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;font-family:var(--display);}'
if old not in d:
    print('FAIL dashboard css')
    sys.exit(1)
d = d.replace(old, '.brand .mark{width:30px;height:30px;border-radius:50%;box-shadow:0 0 0 1.5px var(--gold);flex:none;display:block;}')
write('dashboard.html', d)
print('done')
