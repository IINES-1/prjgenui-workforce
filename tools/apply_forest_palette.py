"""
Apply palette 1 from colours-2.html ("The mix") to the live site.

  Forest  #1F3A2E  replaces navy
  Sage    #7A9A7E  replaces steel blue
  Amber   #E8A33D  replaces gold

Variable names are kept (--navy, --steel, --gold) so no markup changes.
Amber and sage fail contrast as small text on light backgrounds, so two
darker text-only shades are added: --gold-text and a darker --steel-dark.
A backup of every touched file goes to tools/backup-navy-gold first.
"""
import os
import shutil
import sys

ROOT = r'C:\Users\is1lv\PRJGENUI-Workforce'
BACKUP = os.path.join(ROOT, 'tools', 'backup-navy-gold')

SITE_PAGES = ['index.html', 'about.html', 'contact.html', 'privacy.html', 'terms.html', 'thanks.html']
SITE_AND_APP = SITE_PAGES + ['dashboard.html', 'logos.html']
ALL_HTML = SITE_AND_APP + ['colours.html', 'colours-2.html']


def read(name):
    with open(os.path.join(ROOT, name), 'r', encoding='utf-8') as f:
        return f.read()


def write(name, text):
    with open(os.path.join(ROOT, name), 'w', encoding='utf-8', newline='') as f:
        f.write(text)


def sub(text, old, new, desc, expect=None):
    n = text.count(old)
    if n == 0 or (expect is not None and n != expect):
        print(f'  FAIL [{desc}]: found {n}, expected {expect if expect is not None else ">=1"}')
        sys.exit(1)
    print(f'  OK   [{desc}]: {n}')
    return text.replace(old, new)


# ---- backup (only once, so a re-run never overwrites the originals) ----
os.makedirs(BACKUP, exist_ok=True)
for name in ['styles.css'] + ALL_HTML:
    dst = os.path.join(BACKUP, name)
    if not os.path.exists(dst):
        shutil.copy2(os.path.join(ROOT, name), dst)
print('Backup in', BACKUP)

# ===================== styles.css =====================
print('\n=== styles.css ===')
css = read('styles.css')

css = sub(css, 'styles.css  v9', 'styles.css  v10', 'version comment', 1)

css = sub(css,
  '--navy:#1B2A4A; --navy-deep:#121E36; --navy-soft:#24365C; --navy-line:rgba(255,255,255,.12);',
  '--navy:#1F3A2E; --navy-deep:#14271E; --navy-soft:#2B4A3B; --navy-line:rgba(255,255,255,.12);',
  ':root forest', 1)
css = sub(css,
  '--gold:#C8933A; --gold-dark:#A67428; --gold-light:#F5E8C8; --gold-pale:#FBF5E4; --steel:#4A85B0; --steel-dark:#3A6B8F; --steel-light:#D9E8F3; --steel-pale:#EBF2F8;',
  '--gold:#E8A33D; --gold-dark:#C98A24; --gold-text:#9A6508; --gold-light:#FBE9C6; --gold-pale:#FDF6E7; --steel:#7A9A7E; --steel-dark:#567358; --steel-light:#DCE7DD; --steel-pale:#EEF3EE;',
  ':root amber + sage', 1)

# Links: sage fails 4.5:1 on paper, so the darker sage carries text links.
css = sub(css,
  'a{color:var(--steel);text-decoration-color:var(--gold);',
  'a{color:var(--steel-dark);text-decoration-color:var(--gold);', 'link colour', 1)
css = sub(css,
  'a:hover{text-decoration-color:var(--gold-dark);color:var(--steel-dark);}',
  'a:hover{text-decoration-color:var(--gold-dark);color:var(--navy);}', 'link hover', 1)

# Amber used as small/large text on light backgrounds -> darker amber text shade.
css = sub(css, 'em.gold{font-style:normal;color:var(--gold);}',
               'em.gold{font-style:normal;color:var(--gold-text);}', 'em.gold', 1)
css = sub(css, 'text-transform:uppercase;color:var(--gold);margin-bottom:14px;',
               'text-transform:uppercase;color:var(--gold-text);margin-bottom:14px;', 'kicker', 1)
css = sub(css, 'font-weight:600;color:var(--gold);margin-bottom:12px;',
               'font-weight:600;color:var(--gold-text);margin-bottom:12px;', 'step-label', 1)
css = sub(css, 'text-transform:uppercase;color:var(--gold);margin-top:4px;',
               'text-transform:uppercase;color:var(--gold-text);margin-top:4px;', 'brand word span', 1)
css = sub(css, 'font-variant-numeric:tabular-nums;color:var(--gold);line-height:1;padding-top:4px;',
               'font-variant-numeric:tabular-nums;color:var(--gold-text);line-height:1;padding-top:4px;', 'product num', 1)
css = sub(css, 'font-variant-numeric:tabular-nums;color:var(--gold);line-height:1.3;}',
               'font-variant-numeric:tabular-nums;color:var(--gold-text);line-height:1.3;}', 'steps counter', 1)
css = sub(css, 'font-variant-numeric:tabular-nums;color:var(--gold);font-size:1.0625rem;',
               'font-variant-numeric:tabular-nums;color:var(--gold-text);font-size:1.0625rem;', 'contact next span', 1)
css = sub(css, 'font-size:1.5rem;color:var(--gold);line-height:1;',
               'font-size:1.5rem;color:var(--gold-text);line-height:1;', 'faq plus', 1)
css = sub(css, 'color:var(--gold-dark);display:grid;place-items:center;font-weight:700;font-size:.9375rem;',
               'color:var(--gold-text);display:grid;place-items:center;font-weight:700;font-size:.9375rem;', 'avatar', 1)
css = sub(css, 'color:var(--gold-dark);font-size:1rem;',
               'color:var(--gold-text);font-size:1rem;', 'timeline time', 1)

# Hero stats
css = sub(css, '.hero-stats .hs:nth-child(1) strong{color:var(--steel);}',
               '.hero-stats .hs:nth-child(1) strong{color:var(--steel-dark);}', 'hero stat 1', 1)
css = sub(css, '.hero-stats .hs:nth-child(2) strong{color:var(--gold);}',
               '.hero-stats .hs:nth-child(2) strong{color:var(--gold-text);}', 'hero stat 2', 1)
css = sub(css, 'letter-spacing:-0.02em;font-variant-numeric:tabular-nums;color:var(--steel);line-height:1;}',
               'letter-spacing:-0.02em;font-variant-numeric:tabular-nums;color:var(--steel-dark);line-height:1;}', 'metric numerals', 1)

# Buttons: amber and sage both take dark text; hover states keep contrast.
css = sub(css, 'color:#fff;box-shadow:0 2px 8px rgba(200,147,58,.3);',
               'color:var(--navy-deep);box-shadow:0 2px 8px rgba(200,147,58,.3);', 'gold hover text (btn + mobile nav)', 2)
css = sub(css,
  '.btn-steel{background:var(--steel);color:#fff;border-color:var(--steel);',
  '.btn-steel{background:var(--steel);color:var(--navy-deep);border-color:var(--steel);', 'btn-steel text', 1)
css = sub(css,
  '.btn-steel:hover{background:var(--steel-dark);border-color:var(--steel-dark);',
  '.btn-steel:hover{background:var(--steel-dark);border-color:var(--steel-dark);color:#fff;', 'btn-steel hover', 1)

# Hardcoded colours on dark backgrounds / shadows / select arrow.
for old, new, desc in [
    ('#E4C883', '#F3C77A', 'light amber on dark'),
    ('#D9BE72', '#F3C77A', 'light amber step label on dark'),
    ('#CBD3E3', '#CBD8CF', 'lede on dark'),
    ('#C9D2E4', '#CBD8CF', 'body text on dark'),
    ('#B7C0D6', '#B5C4B9', 'footer text'),
    ('#8492AC', '#8DA194', 'footer small text'),
    ('rgba(18,30,54,', 'rgba(20,39,30,', 'shadow tint'),
    ('rgba(27,42,74,', 'rgba(31,58,46,', 'focus ring tint'),
    ('rgba(200,147,58,', 'rgba(232,163,61,', 'amber glow'),
    ('rgba(74,133,176,', 'rgba(122,154,126,', 'sage glow'),
    ('%239C7A2E', '%239A6508', 'select arrow'),
]:
    css = sub(css, old, new, desc)

write('styles.css', css)

# ===================== site pages =====================
print('\n=== site pages (favicon, theme-color) ===')
for name in SITE_AND_APP:
    t = read(name)
    t = t.replace('content="#1B2A4A"', 'content="#1F3A2E"')
    t = t.replace('fill=\'%231B2A4A\'', 'fill=\'%231F3A2E\'')
    t = t.replace('fill=\'%23E4C883\'', 'fill=\'%23F3C77A\'')
    t = t.replace('fill=\'%23C8933A\'', 'fill=\'%23E8A33D\'')
    if name == 'index.html':
        t = sub(t, 'style="color:#C9D2E4;margin-top:20px;', 'style="color:#CBD8CF;margin-top:20px;', 'index inline text', 1)
    write(name, t)
    print('  OK  ', name)

# ===================== dashboard =====================
print('\n=== dashboard.html ===')
d = read('dashboard.html')
d = sub(d,
  '--navy:#1B2A4A; --navy-dark:#121E36; --gold:#C8933A; --gold-light:#F5E8C8; --steel:#4A85B0; --steel-dark:#3A6B8F; --steel-light:#D9E8F3; --steel-pale:#EBF2F8;',
  '--navy:#1F3A2E; --navy-dark:#14271E; --gold:#E8A33D; --gold-light:#FBE9C6; --steel:#7A9A7E; --steel-dark:#567358; --steel-light:#DCE7DD; --steel-pale:#EEF3EE;',
  'dashboard :root', 1)
d = sub(d, '.badge.gold{background:var(--gold-light);color:#A67428;}',
           '.badge.gold{background:var(--gold-light);color:#9A6508;}', 'dashboard gold badge', 1)
d = sub(d, '.breadcrumb a{cursor:pointer;color:var(--steel);',
           '.breadcrumb a{cursor:pointer;color:var(--steel-dark);', 'dashboard breadcrumb', 1)
d = sub(d, 'color:#D8DEEA;', 'color:#D3DED6;', 'dashboard notice text', 1)
d = sub(d, 'color:#B9C2D6;', 'color:#B5C4B9;', 'dashboard brand sub', 1)
d = sub(d, 'color:#CBD3E1;', 'color:#CBD8CF;', 'dashboard tab text', 1)
write('dashboard.html', d)

# ===================== cache-bust =====================
print('\n=== cache bust styles.css?v=9 -> v=10 ===')
for name in ALL_HTML:
    t = read(name)
    n = t.count('styles.css?v=9')
    write(name, t.replace('styles.css?v=9', 'styles.css?v=10'))
    print(f'  {name}: {n}')

print('\nDone.')
