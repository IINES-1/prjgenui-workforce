"""
Update about.html, contact.html, privacy.html, terms.html:
1. Remove Compare and FAQ from desktop nav
2. Remove Compare and FAQ from mobile nav
3. Change footer links from compare.html/faq.html to index.html#compare/index.html#faq
"""
import sys

FILES = [
    r'C:\Users\is1lv\PRJGENUI-Workforce\about.html',
    r'C:\Users\is1lv\PRJGENUI-Workforce\contact.html',
    r'C:\Users\is1lv\PRJGENUI-Workforce\privacy.html',
    r'C:\Users\is1lv\PRJGENUI-Workforce\terms.html',
]

# Exact-match replacements (old, new, description)
REPLACEMENTS = [
    # Desktop nav: remove Compare and FAQ lines
    (
        '      <a href="about.html">About</a>\n      <a href="compare.html">Compare</a>\n      <a href="faq.html">FAQ</a>\n      <a href="contact.html">Contact</a>',
        '      <a href="about.html">About</a>\n      <a href="contact.html">Contact</a>',
        'desktop nav: remove Compare+FAQ'
    ),
    # Mobile nav: remove Compare and FAQ lines
    (
        '  <a href="about.html">About</a>\n  <a href="compare.html">Compare</a>\n  <a href="faq.html">FAQ</a>\n  <a href="contact.html">Contact</a>',
        '  <a href="about.html">About</a>\n  <a href="contact.html">Contact</a>',
        'mobile nav: remove Compare+FAQ'
    ),
    # Footer: change compare.html to index.html#compare
    (
        '<li><a href="compare.html">Compare</a></li>',
        '<li><a href="index.html#compare">Compare</a></li>',
        'footer: compare.html -> index.html#compare'
    ),
    # Footer: change faq.html to index.html#faq
    (
        '<li><a href="faq.html">FAQ</a></li>',
        '<li><a href="index.html#faq">FAQ</a></li>',
        'footer: faq.html -> index.html#faq'
    ),
]

for fpath in FILES:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    for old, new, desc in REPLACEMENTS:
        count = content.count(old)
        if count == 0:
            print(f'  SKIP [{desc}] in {fpath.split(chr(92))[-1]}: pattern not found')
            # This is expected for some replacements if the pattern differs slightly
            continue
        if count > 1:
            print(f'  WARN [{desc}] in {fpath.split(chr(92))[-1]}: found {count} matches, replacing all')
        content = content.replace(old, new)
        print(f'  OK   [{desc}] in {fpath.split(chr(92))[-1]}: {count} replacement(s)')

    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)

# Verify: no remaining compare.html or faq.html references in updated files
print('\n=== Verification ===')
for fpath in FILES:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    fname = fpath.split('\\')[-1]
    has_compare = 'compare.html' in content
    has_faq = 'faq.html' in content
    has_hash_compare = 'index.html#compare' in content
    has_hash_faq = 'index.html#faq' in content
    print(f'{fname}: compare.html={has_compare} faq.html={has_faq} #compare={has_hash_compare} #faq={has_hash_faq}')

print('\nDone.')
