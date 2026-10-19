"""Bump the styles.css/script.js cache-busting version across pages.

Usage: python tools/bump_asset_version.py 26 27
"""
import glob
import sys

old, new = sys.argv[1], sys.argv[2]
changed = []
for path in glob.glob('*.html'):
    with open(path, encoding='utf-8') as f:
        html = f.read()
    updated = html.replace(f'styles.css?v={old}', f'styles.css?v={new}') \
                  .replace(f'script.js?v={old}', f'script.js?v={new}')
    if updated != html:
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(updated)
        changed.append(path)
print('updated:', ', '.join(changed) or 'none')
