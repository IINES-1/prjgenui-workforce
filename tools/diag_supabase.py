"""Diagnose the dashboard's Supabase connection chain.
python tools/diag_supabase.py [base-url]
"""
import sys
from playwright.sync_api import sync_playwright

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8765/'

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME, headless=True)
    ctx = b.new_context(viewport={'width': 1280, 'height': 900})
    pg = ctx.new_page()
    logs = []
    pg.on('console', lambda m: logs.append('%s: %s' % (m.type, m.text)))
    pg.on('pageerror', lambda e: logs.append('pageerror: %s' % e))
    pg.goto(BASE + 'dashboard.html', wait_until='load')
    pg.wait_for_timeout(6000)
    print('typeof window.supabase:', pg.evaluate('typeof window.supabase'))
    print('PRJGENUI.supabaseUrl set:', pg.evaluate('!!(window.PRJGENUI && window.PRJGENUI.supabaseUrl)'))
    print('PRJGENUI.supabaseAnonKey set:', pg.evaluate('!!(window.PRJGENUI && window.PRJGENUI.supabaseAnonKey)'))
    print('secrets.js script loaded (200?):', pg.evaluate("(function(){var s=document.querySelector('script[src=\"secrets.js\"]');return !!s;})()"))
    print('storage tag:', pg.eval_on_selector('#storageTag', 'el => el.textContent'))
    print('--- console (first 12) ---')
    for line in logs[:12]:
        print(line)
    b.close()
