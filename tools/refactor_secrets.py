"""Refactor: move runtime keys out of tracked files.

1. Extracts the Supabase URL/anon key from dashboard.html and the Web3Forms
   key from tools/build_round2.py (without printing them).
2. Writes them to secrets.js at the project root - a file that is DEPLOYED
   (Vercel) but NOT COMMITTED (gitignored).
3. Rewrites dashboard.html to read the keys at runtime from window.PRJGENUI.
4. Scrubs every remaining copy of both keys from all text files in the repo.

Both values are public-by-design (anon key is RLS-protected and already ships
in the live page; the Web3Forms key is required in public form HTML). Moving
them keeps the repository clean while the deployed site works exactly as now.
Run from anywhere:  python tools/refactor_secrets.py
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_NAMES = {'secrets.js'}

# --- 1. extract ---
with open(os.path.join(ROOT, 'dashboard.html'), encoding='utf-8') as f:
    dash = f.read()
url = re.search(r"url:\s*'(https://[^']+)'", dash).group(1)
anon = re.search(r"anonKey:\s*'(eyJ[^']+)'", dash).group(1)
with open(os.path.join(ROOT, 'tools', 'build_round2.py'), encoding='utf-8') as f:
    build = f.read()
w3f = re.search(r"KEY\s*=\s*'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})'", build).group(1)

# --- 2. write secrets.js (deployed, not committed) ---
SECRETS = """/* Runtime keys for the deployed PRJGENUI Workforce site.
   This file is DEPLOYED but NOT COMMITTED to the repository (see .gitignore).
   The values are public-by-design: the Supabase anon key is protected by
   row-level security, and the Web3Forms key is required in the public form
   pages. Real secrets (service-role key, database password, mailbox password)
   must NEVER go in this file. */
window.PRJGENUI = {
  supabaseUrl: '%s',
  supabaseAnonKey: '%s',
  web3formsKey: '%s'
};
""" % (url, anon, w3f)
with open(os.path.join(ROOT, 'secrets.js'), 'w', encoding='utf-8', newline='\n') as f:
    f.write(SECRETS)

# --- 3. dashboard.html reads keys at runtime ---
SB_TAG = '<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>'
assert SB_TAG in dash, 'supabase script tag not found'
dash = dash.replace(SB_TAG, SB_TAG + '\n<script src="secrets.js"></script>')
dash = dash.replace("url: '%s'" % url, "url: (window.PRJGENUI && window.PRJGENUI.supabaseUrl) || ''")
dash = dash.replace("anonKey: '%s'" % anon, "anonKey: (window.PRJGENUI && window.PRJGENUI.supabaseAnonKey) || ''")
with open(os.path.join(ROOT, 'dashboard.html'), 'w', encoding='utf-8', newline='\n') as f:
    f.write(dash)

# --- 4. scrub every remaining copy from all text files ---
EXTS = ('.html', '.py', '.js', '.css', '.md', '.json', '.txt', '.sql', '.xml')
scrubbed = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d != '.git']
    for fn in filenames:
        if fn in SKIP_NAMES or not fn.endswith(EXTS):
            continue
        p = os.path.join(dirpath, fn)
        with open(p, encoding='utf-8', errors='ignore') as f:
            t = f.read()
        n = t.replace(anon, 'REDACTED-IN-REPO').replace(w3f, 'REDACTED-IN-REPO')
        if n != t:
            with open(p, 'w', encoding='utf-8', newline='\n') as f:
                f.write(n)
            scrubbed.append(os.path.relpath(p, ROOT))

print('secrets.js written (%d bytes)' % len(SECRETS))
print('scrubbed %d file(s): %s' % (len(scrubbed), ', '.join(scrubbed) or 'none'))
