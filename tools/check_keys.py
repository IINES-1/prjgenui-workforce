"""Runtime key check: secrets.js must load, fill form keys, and connect Supabase.
python tools/check_keys.py            (local, BASE=http://127.0.0.1:8765/)
python tools/check_keys.py https://prjgenuiworkforce.co.uk/
"""
import os
import sys
from playwright.sync_api import sync_playwright

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8765/'

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME, headless=True)
    ctx = b.new_context(viewport={'width': 1280, 'height': 900})

    pg = ctx.new_page()
    errors = []
    pg.on('pageerror', lambda e: errors.append(str(e)))
    pg.goto(BASE + 'request.html', wait_until='load')
    pg.wait_for_timeout(1200)
    filled = pg.eval_on_selector('input[name="access_key"]', 'el => el.value.length')
    has_window = pg.evaluate('!!(window.PRJGENUI && window.PRJGENUI.web3formsKey)')
    print('request.html: PRJGENUI loaded: %s, access_key filled: %d chars, errors: %s' % (has_window, filled, errors or 'none'))

    errors = []
    pg2 = ctx.new_page()
    pg2.on('pageerror', lambda e: errors.append(str(e)))
    pg2.goto(BASE + 'dashboard.html', wait_until='load')
    pg2.wait_for_timeout(4000)
    tag = pg2.eval_on_selector('#storageTag', 'el => el.textContent')
    print('dashboard.html: storage tag: %r, errors: %s' % (tag, errors or 'none'))

    b.close()
