"""
Screenshot helper for design review (uses installed Chrome via Playwright).

  python tools/shoot.py <page> <width> <height> <step> [<step> ...]

step:  top | #id | y=1200 | seq=0.5 (scroll position inside the pinned sequence)
       | full (full-page image)
Writes research/shots/<page>-<w>-<step>.png
"""
import os
import sys
from playwright.sync_api import sync_playwright

ROOT = r'C:\Users\is1lv\PRJGENUI-Workforce'
OUT = os.path.join(ROOT, 'research', 'shots')
os.makedirs(OUT, exist_ok=True)
CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
BASE = os.environ.get('BASE', 'http://127.0.0.1:8765/')

page_name, w, h = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
steps = sys.argv[4:] or ['top']
reduced = os.environ.get('REDUCED') == '1'
nojs = os.environ.get('NOJS') == '1'

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME, headless=True)
    ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1,
                        reduced_motion='reduce' if reduced else 'no-preference',
                        java_script_enabled=not nojs, is_mobile=(w < 600), has_touch=(w < 600))
    pg = ctx.new_page()
    errs = []
    pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(BASE + page_name, wait_until='load')
    pg.wait_for_timeout(4200)
    for s in steps:
        tag = s.replace('#', '').replace('=', '').replace('.', '_').replace(':', '_')
        if s.startswith('#'):
            pg.evaluate("id => document.getElementById(id).scrollIntoView({behavior:'instant'})", s[1:])
        elif s.startswith('sel:'):
            sel, idx = s[4:].rsplit(':', 1)
            pg.evaluate("""([q, i]) => { const e = document.querySelectorAll(q)[i];
              window.scrollTo({top: e.getBoundingClientRect().top + window.scrollY - 90, behavior: 'instant'}); }""",
                        [sel, int(idx)])
        elif s.startswith('y='):
            pg.evaluate("y => window.scrollTo({top:y,behavior:'instant'})", int(s[2:]))
        elif s.startswith('seq='):
            f = float(s[4:])
            pg.evaluate("""f => { const s=document.querySelector('.seq'); const top=s.getBoundingClientRect().top+window.scrollY;
              const span=s.offsetHeight-window.innerHeight; window.scrollTo({top:top+span*f,behavior:'instant'}); }""", f)
        elif s == 'top':
            pg.evaluate("window.scrollTo({top:0,behavior:'instant'})")
        pg.wait_for_timeout(1700)
        path = os.path.join(OUT, '%s-%d-%s.png' % (page_name.replace('.html', ''), w, tag))
        pg.screenshot(path=path, full_page=(s == 'full'))
        print(path)
    sw = pg.evaluate('document.documentElement.scrollWidth')
    cw = pg.evaluate('document.documentElement.clientWidth')
    print('scrollWidth', sw, 'clientWidth', cw, 'errors', errs)
    b.close()
