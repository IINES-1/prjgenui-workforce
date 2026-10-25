# -*- coding: utf-8 -*-
"""Generate the multilingual site for PRJGENUI Workforce.

Steps (run from the repo root, after tools/bump_asset_version.py):
  1. Patch the EN pages: remove the noindex meta from the public pages,
     add an hreflang cluster after the canonical, add a language switcher
     (EN/ES/PT) to the footer.
  2. Generate /es/ and /pt/ copies of all pages: translated body copy,
     lang attribute, title/description/OG/Twitter, canonical and og:url
     pointing at the language URL, og:locale, ../ asset paths, and a
     language-mapped web3forms redirect.
  3. Write sitemap.xml (7 public pages x 3 languages, hreflang alternates).
  4. Add the Sitemap line to robots.txt.
  5. Remove the X-Robots-Tag noindex header from vercel.json.
  6. Append the .lang-switch styles to styles.css (idempotent).

Usage:
  python tools/build_i18n.py --check   validate only, write nothing
  python tools/build_i18n.py           build everything (idempotent)
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from i18n_es import HEADS as ES_HEADS, BODY as ES_BODY
from i18n_pt import HEADS as PT_HEADS, BODY as PT_BODY

SITE = 'https://prjgenuiworkforce.co.uk'
PAGES = ['index.html', 'about.html', 'workers.html', 'request.html',
         'contact.html', 'privacy.html', 'terms.html', 'thanks.html']
PUBLIC = [p for p in PAGES if p != 'thanks.html']
TODAY = '2026-10-25'
NOINDEX_META = '<meta name="robots" content="noindex, nofollow">'
THANKS_TITLES = {'es': 'Gracias | PRJGENUI Workforce',
                 'pt': 'Obrigado | PRJGENUI Workforce'}
LANGS = [
    ('en', 'en-GB', 'en_GB', None),
    ('es', 'es-ES', 'es_ES', (ES_HEADS, ES_BODY)),
    ('pt', 'pt-PT', 'pt_PT', (PT_HEADS, PT_BODY)),
]


def read(path):
    with open(path, encoding='utf-8', newline='') as f:
        return f.read()


def write(path, text):
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(text)


def page_url(lang, page):
    if page == 'index.html':
        return f'{SITE}/{lang}/' if lang != 'en' else f'{SITE}/'
    return f'{SITE}/{lang}/{page}' if lang != 'en' else f'{SITE}/{page}'


def hreflang_cluster(page):
    lines = []
    for code, hlang, _, _ in LANGS:
        lines.append(f'<link rel="alternate" hreflang="{hlang}" href="{page_url(code, page)}">')
    lines.append(f'<link rel="alternate" hreflang="x-default" href="{page_url("en", page)}">')
    return '\n'.join(lines)


def lang_switcher(current, page):
    parts = []
    for code, hlang, _, _ in LANGS:
        label = code.upper()
        if code == current:
            parts.append(f'<span aria-current="true">{label}</span>')
        else:
            parts.append(f'<a href="{page_url(code, page)}" hreflang="{hlang}" rel="alternate">{label}</a>')
    return '<p class="lang-switch">' + ' &middot; '.join(parts) + '</p>'


SWITCHER_RE = re.compile(r'<p class="lang-switch">.*?</p>', re.S)


def patch_en_pages():
    """Remove noindex, add hreflang cluster and footer switcher to EN pages."""
    for page in PAGES:
        html = read(page)
        orig = html
        if page in PUBLIC:
            if NOINDEX_META in html:
                html = html.replace(NOINDEX_META + '\n', '').replace(NOINDEX_META, '')
            if 'hreflang=' not in html:
                cluster = hreflang_cluster(page)
                html, n = re.subn(r'(<link rel="canonical" href="[^"]*">)',
                                  lambda m: m.group(1) + '\n' + cluster, html, count=1)
                if n != 1:
                    print(f'WARN: no canonical link found in {page}')
        if page != 'thanks.html' and 'lang-switch' not in html:
            switch = lang_switcher('en', page)
            html, n = re.subn(r'(\n    </div>)(\n    <div class="footer-word")',
                             lambda m: '\n      ' + switch + m.group(1) + m.group(2),
                             html, count=1)
            if n != 1:
                print(f'WARN: no footer-bottom marker found in {page}')
        if html != orig:
            write(page, html)
            print(f'patched EN {page}')


def apply_translations(html, body):
    """Apply exact-string replacements, longest old string first.

    Sorting by length keeps tag-context and full-sentence pairs ahead of
    the short shared terms they contain (e.g. 'Right to Work' must not
    be replaced inside a longer sentence before that sentence's own
    pair has run).
    """
    applied = 0
    for old, new in sorted(body, key=lambda p: len(p[0]), reverse=True):
        if new == 'NEVERMATCH':
            continue
        if old in html:
            html = html.replace(old, new)
            applied += 1
    return html, applied


def sub_attr(html, pattern, value):
    """Replace the captured attribute value in a single tagged element."""
    return re.sub(pattern, lambda m: m.group(1) + value + m.group(2), html, count=1)


def generate_language(lang):
    code, hlang, og_locale, data = [l for l in LANGS if l[0] == lang][0]
    heads, body = data
    os.makedirs(lang, exist_ok=True)
    for page in PAGES:
        html = read(page)
        html, applied = apply_translations(html, body)

        # lang attribute
        html = html.replace('<html lang="en-GB">', f'<html lang="{hlang}">')

        # head strings
        if page == 'thanks.html':
            title = THANKS_TITLES[lang]
            html = sub_attr(html, r'(<title>).*?(</title>)', title)
        else:
            h = heads[page]
            html = sub_attr(html, r'(<title>).*?(</title>)', h['title'])
            html = sub_attr(html, r'(<meta name="description" content=").*?(">)', h['desc'])
            html = sub_attr(html, r'(<meta property="og:title" content=").*?(">)', h['og_title'])
            html = sub_attr(html, r'(<meta property="og:description" content=").*?(">)', h['og_desc'])
            html = sub_attr(html, r'(<meta name="twitter:title" content=").*?(">)', h['og_title'])
            html = sub_attr(html, r'(<meta name="twitter:description" content=").*?(">)', h['og_desc'])
            url = page_url(lang, page)
            html = sub_attr(html, r'(<link rel="canonical" href=").*?(">)', url)
            html = sub_attr(html, r'(<meta property="og:url" content=").*?(">)', url)
        html = sub_attr(html, r'(<meta property="og:locale" content=").*?(">)', og_locale)

        # relative asset paths -> ../
        for old, new in [('href="styles.css?v=', 'href="../styles.css?v='),
                         ('src="secrets.js"', 'src="../secrets.js"'),
                         ('src="script.js?v=', 'src="../script.js?v='),
                         ('href="fonts/', 'href="../fonts/'),
                         ('src="images/', 'src="../images/'),
                         ('srcset="images/', 'srcset="../images/')]:
            html = html.replace(old, new)

        # web3forms redirect -> language thanks page
        html = html.replace('value="https://prjgenuiworkforce.co.uk/thanks.html"',
                            f'value="{page_url(lang, "thanks.html")}"')

        # language switcher for this page's context
        if page != 'thanks.html':
            html = SWITCHER_RE.sub(lambda m: lang_switcher(lang, page), html, count=1)

        write(os.path.join(lang, page), html)
        print(f'generated {lang}/{page} ({applied} replacements)')


def write_sitemap():
    entries = []
    for page in PUBLIC:
        alternates = []
        for code, hlang, _, _ in LANGS:
            alternates.append(
                f'    <xhtml:link rel="alternate" hreflang="{hlang}" href="{page_url(code, page)}"/>')
        alternates.append(
            f'    <xhtml:link rel="alternate" hreflang="x-default" href="{page_url("en", page)}"/>')
        entries.append(
            '  <url>\n    <loc>' + page_url('en', page) + '</loc>\n'
            + '\n'.join(alternates) + '\n'
            + f'    <lastmod>{TODAY}</lastmod>\n  </url>')
        for lang in ('es', 'pt'):
            entries.append(
                '  <url>\n    <loc>' + page_url(lang, page) + '</loc>\n'
                + '\n'.join(alternates) + '\n'
                + f'    <lastmod>{TODAY}</lastmod>\n  </url>')
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
           '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
           + '\n'.join(entries) + '\n</urlset>\n')
    write('sitemap.xml', xml)
    print(f'wrote sitemap.xml ({len(entries)} urls)')


def update_robots():
    txt = read('robots.txt')
    if 'Sitemap:' not in txt:
        if not txt.endswith('\n'):
            txt += '\n'
        txt += '\nSitemap: ' + SITE + '/sitemap.xml\n'
        write('robots.txt', txt)
        print('updated robots.txt')
    else:
        print('robots.txt already has a Sitemap line')


def patch_vercel():
    cfg = json.loads(read('vercel.json'))
    if 'headers' in cfg:
        del cfg['headers']
        write('vercel.json', json.dumps(cfg, indent=2) + '\n')
        print('removed X-Robots-Tag header from vercel.json')
    else:
        print('vercel.json already has no headers block')


CSS_BLOCK = """
/* Language switcher (footer) */
.footer-bottom .lang-switch{width:100%;margin:0;padding-top:10px;font-size:.75rem;letter-spacing:.12em;}
.footer-bottom .lang-switch span{color:rgba(255,255,255,.5);}
.footer-bottom .lang-switch a{min-height:auto;}
"""


def add_switcher_css():
    css = read('styles.css')
    if '.lang-switch' not in css:
        if not css.endswith('\n'):
            css += '\n'
        css += CSS_BLOCK
        write('styles.css', css)
        print('added .lang-switch styles to styles.css')
    else:
        print('styles.css already has .lang-switch styles')


def check():
    """Validate that every translation source string exists somewhere."""
    ok = True
    sources = {p: read(p) for p in PAGES}
    combined = '\n'.join(sources.values())
    for name, body in (('es', ES_BODY), ('pt', PT_BODY)):
        missing = [old for old, new in body
                   if new != 'NEVERMATCH' and old not in combined]
        if missing:
            ok = False
            print(f'{name}: {len(missing)} source strings not found:')
            for s in missing:
                print(f'  - {s[:90]}')
        else:
            print(f'{name}: all {len(body)} source strings found')
        # simulate the ordered application over the combined sources:
        # any pair that never matches indicates ordering/coverage trouble
        text = combined
        unapplied = []
        for old, new in sorted(body, key=lambda p: len(p[0]), reverse=True):
            if new == 'NEVERMATCH':
                continue
            if old in text:
                text = text.replace(old, new)
            else:
                unapplied.append(old)
        if unapplied:
            print(f'{name}: WARN {len(unapplied)} pairs never match after ordering:')
            for s in unapplied:
                print(f'  - {s[:90]}')
    for page in PUBLIC:
        html = sources[page]
        for pat, label in [(r'<title>', 'title'), (r'name="description"', 'description'),
                           (r'og:title', 'og:title'), (r'og:description', 'og:description'),
                           (r'twitter:title', 'twitter:title'),
                           (r'rel="canonical"', 'canonical'), (r'og:locale', 'og:locale')]:
            if not re.search(pat, html):
                ok = False
                print(f'WARN: {page} is missing {label}')
    print('check', 'PASSED' if ok else 'FAILED')
    return ok


def main():
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
    if '--check' in sys.argv:
        sys.exit(0 if check() else 1)
    check() or sys.exit(1)
    patch_en_pages()
    for lang in ('es', 'pt'):
        generate_language(lang)
    write_sitemap()
    update_robots()
    patch_vercel()
    add_switcher_css()
    print('done')


if __name__ == '__main__':
    main()
