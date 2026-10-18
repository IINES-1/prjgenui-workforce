"""List elements that extend past the viewport width.  python tools/overflow.py index.html 375"""
import sys
from playwright.sync_api import sync_playwright

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
name, w = sys.argv[1], int(sys.argv[2])
JS = """(w) => { const out = []; document.querySelectorAll('body *').forEach(e => {
  const r = e.getBoundingClientRect(); if (r.width && r.right > w + 1) out.push(e.tagName + '.' + e.className + ' right=' + Math.round(r.right));
}); return out.slice(0, 25); }"""
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME, headless=True)
    ctx = b.new_context(viewport={'width': w, 'height': 812}, is_mobile=True, has_touch=True)
    pg = ctx.new_page()
    pg.goto('http://127.0.0.1:8765/' + name, wait_until='load')
    pg.wait_for_timeout(1500)
    for line in pg.evaluate(JS, w):
        print(line)
    b.close()
