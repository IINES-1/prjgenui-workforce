"""
Apply new palette to styles.css and dashboard.html.
- Gold: #9C7A2E -> #C8933A (brighter)
- Gold dark: #7C6224 -> #A67428
- Gold light: #F3ECDA -> #F5E8C8
- Gold pale: #FAF6EA -> #FBF5E4
- Add steel: #4A85B0, steel-dark: #3A6B8F, steel-light: #D9E8F3, steel-pale: #EBF2F8
- Section backgrounds: paper-deep -> steel-pale
- For-workers panel: steel border + steel-pale bg
- Hero stats: mixed steel/gold/navy
- Score bars: navy -> steel
- Metric numerals: navy -> steel
- Links: inherit -> steel with gold underline
- New btn-steel and pill.steel classes
- Bump ?v=7 -> ?v=8 on all pages
"""
import os
import sys

ROOT = r'C:\Users\is1lv\PRJGENUI-Workforce'

def apply_replacements(filepath, replacements):
    """Apply exact-match replacements. Fail if any pattern not found."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    for old, new, desc in replacements:
        count = content.count(old)
        if count == 0:
            print(f'  FAIL [{desc}]: pattern not found')
            sys.exit(1)
        content = content.replace(old, new)
        print(f'  OK   [{desc}]: {count} replacement(s)')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

# ===== styles.css =====
print('=== styles.css ===')
css_path = os.path.join(ROOT, 'styles.css')
apply_replacements(css_path, [
    # Version comment
    ('styles.css  v7', 'styles.css  v8', 'version comment v7->v8'),
    # Gold variables in :root
    ('--gold:#9C7A2E; --gold-dark:#7C6224; --gold-light:#F3ECDA; --gold-pale:#FAF6EA;',
     '--gold:#C8933A; --gold-dark:#A67428; --gold-light:#F5E8C8; --gold-pale:#FBF5E4; --steel:#4A85B0; --steel-dark:#3A6B8F; --steel-light:#D9E8F3; --steel-pale:#EBF2F8;',
     'gold + steel variables in :root'),
    # Link colour: inherit -> steel
    ('a{color:inherit;text-decoration-color:var(--gold);text-underline-offset:3px;}',
     'a{color:var(--steel);text-decoration-color:var(--gold);text-underline-offset:3px;}',
     'link colour -> steel'),
    # Link hover: add steel-dark colour
    ('a:hover{text-decoration-color:var(--gold-dark);}',
     'a:hover{text-decoration-color:var(--gold-dark);color:var(--steel-dark);}',
     'link hover colour -> steel-dark'),
    # Section paper-deep -> steel-pale
    ('.section.paper-deep{background:var(--paper-deep);}',
     '.section.paper-deep{background:var(--steel-pale);}',
     'section paper-deep -> steel-pale'),
    # Panel deep: background + border
    ('.panel.deep{background:var(--paper-deep);border-top:3px solid var(--navy);}',
     '.panel.deep{background:var(--steel-pale);border-top:3px solid var(--steel);}',
     'panel deep -> steel'),
    # Panel deep bullet colour
    ('.panel.deep li::before{background:var(--navy);}',
     '.panel.deep li::before{background:var(--steel);}',
     'panel deep bullets -> steel'),
    # Score bar fill: navy -> steel
    ('.score-parts .bar span{display:block;height:100%;background:var(--navy);}',
     '.score-parts .bar span{display:block;height:100%;background:var(--steel);}',
     'score bar fill -> steel'),
    # Metric numerals: navy -> steel
    ('.metric .n{display:block;font-family:var(--display);font-size:1.5rem;font-weight:800;letter-spacing:-0.02em;font-variant-numeric:tabular-nums;color:var(--navy);line-height:1;}',
     '.metric .n{display:block;font-family:var(--display);font-size:1.5rem;font-weight:800;letter-spacing:-0.02em;font-variant-numeric:tabular-nums;color:var(--steel);line-height:1;}',
     'metric numerals -> steel'),
])

# Add hero stats nth-child colours and new button/pill classes
# These are INSERTS, not replacements, so we append after specific rules
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

# Insert hero stat colour mix after the base hero-stats .hs strong rule
hero_stats_old = '.hero-stats .hs span{display:block;font-size:.8125rem;color:var(--slate);margin-top:6px;line-height:1.4;max-width:26ch;}'
hero_stats_new = hero_stats_old + '\n.hero-stats .hs:nth-child(1) strong{color:var(--steel);}\n.hero-stats .hs:nth-child(2) strong{color:var(--gold);}\n.hero-stats .hs:nth-child(3) strong{color:var(--navy);}'
if hero_stats_old in css:
    css = css.replace(hero_stats_old, hero_stats_new)
    print('  OK   [hero stats colour mix]: 1 insertion')
else:
    print('  FAIL [hero stats colour mix]: pattern not found')
    sys.exit(1)

# Insert btn-steel after btn-outline rules
btn_insert_point = '.btn-outline:hover{border-color:var(--navy);}'
btn_steel_rules = '\n.btn-steel{background:var(--steel);color:#fff;border-color:var(--steel);}\n.btn-steel:hover{background:var(--steel-dark);border-color:var(--steel-dark);}'
if btn_insert_point in css:
    css = css.replace(btn_insert_point, btn_insert_point + btn_steel_rules)
    print('  OK   [btn-steel class]: 1 insertion')
else:
    print('  FAIL [btn-steel class]: pattern not found')
    sys.exit(1)

# Insert pill.steel after pill.neutral
pill_insert_point = '.pill.neutral{background:var(--paper-deep);color:var(--ink-soft);}'
pill_steel_rule = '\n.pill.steel{background:var(--steel-light);color:var(--steel-dark);}'
if pill_insert_point in css:
    css = css.replace(pill_insert_point, pill_insert_point + pill_steel_rule)
    print('  OK   [pill.steel class]: 1 insertion')
else:
    print('  FAIL [pill.steel class]: pattern not found')
    sys.exit(1)

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)

# ===== dashboard.html =====
print('\n=== dashboard.html ===')
dash_path = os.path.join(ROOT, 'dashboard.html')
apply_replacements(dash_path, [
    # Gold variables
    ('--navy:#1B2A4A; --navy-dark:#121E36; --gold:#9C7A2E; --gold-light:#F3ECDA;',
     '--navy:#1B2A4A; --navy-dark:#121E36; --gold:#C8933A; --gold-light:#F5E8C8; --steel:#4A85B0; --steel-dark:#3A6B8F; --steel-light:#D9E8F3; --steel-pale:#EBF2F8;',
     'gold + steel variables in dashboard'),
    # Hardcoded gold-dark in badge
    ('.badge.gold{background:var(--gold-light);color:#7C6224;}',
     '.badge.gold{background:var(--gold-light);color:#A67428;}',
     'badge.gold text colour'),
    # Callout text colour
    ('color:#5C4A1E;',
     'color:#6B5424;',
     'callout text colour'),
    # Score bar fill: navy -> steel
    ('.score-bar div{background:var(--navy);height:100%;}',
     '.score-bar div{background:var(--steel);height:100%;}',
     'dashboard score bar -> steel'),
])

# ===== Version bump on all HTML pages =====
print('\n=== Version bump ?v=7 -> ?v=8 ===')
html_files = [
    'index.html', 'about.html', 'contact.html', 'privacy.html',
    'terms.html', 'thanks.html', 'dashboard.html',
]

for fname in html_files:
    fpath = os.path.join(ROOT, fname)
    if not os.path.exists(fpath):
        print(f'  SKIP {fname}: file not found')
        continue
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    # Bump CSS version
    css_count = content.count('styles.css?v=7')
    content = content.replace('styles.css?v=7', 'styles.css?v=8')
    # Bump JS version
    js_count = content.count('script.js?v=7')
    content = content.replace('script.js?v=7', 'script.js?v=8')
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'  OK   {fname}: css={css_count} js={js_count}')

# ===== Verification =====
print('\n=== Verification ===')

# Check no old gold values remain in styles.css
with open(css_path, 'r', encoding='utf-8') as f:
    css_check = f.read()
print(f'styles.css has #9C7A2E: {"#9C7A2E" in css_check}')
print(f'styles.css has #7C6224: {"#7C6224" in css_check}')
print(f'styles.css has --steel: {"--steel" in css_check}')
print(f'styles.css has btn-steel: {"btn-steel" in css_check}')
print(f'styles.css has pill.steel: {"pill.steel" in css_check}')
print(f'styles.css has nth-child steel: {":nth-child(1) strong{color:var(--steel)" in css_check}')

# Check dashboard
with open(dash_path, 'r', encoding='utf-8') as f:
    dash_check = f.read()
print(f'dashboard has #9C7A2E: {"#9C7A2E" in dash_check}')
print(f'dashboard has --steel: {"--steel" in dash_check}')

# Check version bump
for fname in html_files:
    fpath = os.path.join(ROOT, fname)
    if not os.path.exists(fpath):
        continue
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    has_v7_css = 'styles.css?v=7' in content
    has_v8_css = 'styles.css?v=8' in content
    print(f'{fname}: v7_css={has_v7_css} v8_css={has_v8_css}')

print('\nDone.')
