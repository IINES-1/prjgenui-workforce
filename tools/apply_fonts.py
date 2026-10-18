"""One-off: switch the site from Source Serif 4 + Public Sans to
Archivo (display) + IBM Plex Sans (text).

Every replacement is exact-match guarded. All new file contents are
computed first; nothing is written unless every guard passes.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PAGES = ['index.html', 'about.html', 'compare.html', 'faq.html',
         'contact.html', 'privacy.html', 'terms.html', 'thanks.html']

OLD_PRELOADS = (
    '<link rel="preload" href="fonts/source-serif-4.woff2" as="font" type="font/woff2" crossorigin>\n'
    '<link rel="preload" href="fonts/source-serif-4-italic.woff2" as="font" type="font/woff2" crossorigin>\n'
    '<link rel="preload" href="fonts/public-sans.woff2" as="font" type="font/woff2" crossorigin>\n'
)
NEW_PRELOADS = (
    '<link rel="preload" href="fonts/archivo.woff2" as="font" type="font/woff2" crossorigin>\n'
    '<link rel="preload" href="fonts/ibm-plex-sans.woff2" as="font" type="font/woff2" crossorigin>\n'
)

OLD_FACES = (
    "@font-face{font-family:'Source Serif 4';src:url('fonts/source-serif-4.woff2') format('woff2');font-weight:200 900;font-style:normal;font-display:swap;}\n"
    "@font-face{font-family:'Source Serif 4';src:url('fonts/source-serif-4-italic.woff2') format('woff2');font-weight:200 900;font-style:italic;font-display:swap;}\n"
    "@font-face{font-family:'Public Sans';src:url('fonts/public-sans.woff2') format('woff2');font-weight:100 900;font-style:normal;font-display:swap;}\n"
)
NEW_FACES = (
    "@font-face{font-family:'Archivo';src:url('fonts/archivo.woff2') format('woff2');font-weight:100 900;font-style:normal;font-display:swap;}\n"
    "@font-face{font-family:'IBM Plex Sans';src:url('fonts/ibm-plex-sans.woff2') format('woff2');font-weight:100 700;font-style:normal;font-display:swap;}\n"
)

OLD_FAVICON = "font-family='Georgia,serif'"
NEW_FAVICON = "font-family='Arial,Helvetica,sans-serif'"

OLD_FONT_FILES = ['source-serif-4.woff2', 'source-serif-4-italic.woff2', 'public-sans.woff2']


def rep(text, old, new, count=1, where=''):
    n = text.count(old)
    if n != count:
        raise SystemExit(f'{where}: expected {count} match(es) for {old[:80]!r}, found {n}')
    return text.replace(old, new)


def none_of(text, needles, where):
    for n in needles:
        if n in text:
            raise SystemExit(f'{where}: {n!r} still present after edits')


# ---------------------------------------------------------------- styles.css
def edit_styles(css):
    w = 'styles.css'
    css = rep(css,
              '   PRJGENUI Workforce - styles.css  v6\n'
              '   Single-page homepage with anchor sections, white\n'
              '   backgrounds, hairline borders, one intentional dark\n'
              '   section. No decorative arrows on buttons.\n',
              '   PRJGENUI Workforce - styles.css  v7\n'
              '   Single-page homepage with anchor sections, white\n'
              '   backgrounds, hairline borders, one intentional dark\n'
              '   section. No decorative arrows on buttons.\n'
              '   Type: Archivo for headings and display numerals,\n'
              '   IBM Plex Sans for text and UI. Self-hosted variable\n'
              '   fonts, latin subset, upright only (no italics shipped).\n',
              where=w)

    css = rep(css, OLD_FACES, NEW_FACES, where=w)

    css = rep(css,
              "  --serif:'Source Serif 4', Georgia, 'Times New Roman', serif;\n"
              "  --sans:'Public Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;\n",
              "  --display:'Archivo', 'Helvetica Neue', Arial, sans-serif;\n"
              "  --sans:'IBM Plex Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;\n",
              where=w)

    # Headings
    css = rep(css,
              'h1{font-family:var(--sans);font-size:clamp(2.25rem,4.5vw,3.5rem);font-weight:800;line-height:1.05;letter-spacing:-0.03em;}',
              'h1{font-family:var(--display);font-size:clamp(2.25rem,4.5vw,3.5rem);font-weight:800;line-height:1.05;letter-spacing:-0.03em;}',
              where=w)
    css = rep(css,
              'h2{font-family:var(--serif);font-size:clamp(1.75rem,3vw,2.25rem);}',
              'h2{font-family:var(--display);font-size:clamp(1.75rem,3vw,2.25rem);font-weight:700;letter-spacing:-0.02em;}',
              where=w)
    css = rep(css,
              'h3{font-family:var(--serif);font-size:1.375rem;line-height:1.3;}',
              'h3{font-family:var(--display);font-size:1.25rem;font-weight:700;letter-spacing:-0.02em;line-height:1.3;}',
              where=w)

    # Hero emphasis: colour alone carries it now, no italic or weight drop
    css = rep(css,
              'em.gold{font-style:italic;color:var(--gold);font-weight:500;}',
              'em.gold{font-style:normal;color:var(--gold);}',
              where=w)

    # Brand
    css = rep(css,
              "font-family:var(--serif);font-weight:700;font-size:1.25rem;flex:none;}",
              "font-family:var(--display);font-weight:800;font-size:1.25rem;flex:none;}",
              where=w)
    css = rep(css,
              '.brand .word{font-family:var(--serif);font-weight:600;font-size:1.25rem;letter-spacing:-0.01em;line-height:1;}',
              '.brand .word{font-family:var(--display);font-weight:700;font-size:1.1875rem;letter-spacing:-0.02em;line-height:1;}',
              where=w)

    # Display numerals (tabular so count-up animations and columns hold still)
    css = rep(css,
              '.hero-stats .hs strong{display:block;font-family:var(--sans);font-size:1.875rem;font-weight:800;color:var(--navy);line-height:1;letter-spacing:-0.02em;}',
              '.hero-stats .hs strong{display:block;font-family:var(--display);font-size:1.875rem;font-weight:800;color:var(--navy);line-height:1;letter-spacing:-0.02em;font-variant-numeric:tabular-nums;}',
              where=w)
    css = rep(css,
              '.readiness .score{font-family:var(--serif);font-size:2.75rem;font-weight:600;color:var(--navy);line-height:1;}',
              '.readiness .score{font-family:var(--display);font-size:2.75rem;font-weight:800;letter-spacing:-0.03em;color:var(--navy);line-height:1;}',
              where=w)
    css = rep(css,
              '.product .num{font-family:var(--serif);font-style:italic;font-size:1.75rem;color:var(--gold);line-height:1;padding-top:4px;}',
              '.product .num{font-family:var(--display);font-weight:800;font-size:1.75rem;letter-spacing:-0.02em;font-variant-numeric:tabular-nums;color:var(--gold);line-height:1;padding-top:4px;}',
              where=w)
    css = rep(css,
              '.steps li::before{counter-increment:step;content:counter(step,decimal-leading-zero);font-family:var(--serif);font-style:italic;font-size:1.25rem;color:var(--gold);line-height:1.3;}',
              '.steps li::before{counter-increment:step;content:counter(step,decimal-leading-zero);font-family:var(--display);font-weight:800;font-size:1.125rem;font-variant-numeric:tabular-nums;color:var(--gold);line-height:1.3;}',
              where=w)
    css = rep(css,
              '.metric .n{display:block;font-family:var(--serif);font-size:1.5rem;font-weight:600;color:var(--navy);line-height:1;}',
              '.metric .n{display:block;font-family:var(--display);font-size:1.5rem;font-weight:800;letter-spacing:-0.02em;font-variant-numeric:tabular-nums;color:var(--navy);line-height:1;}',
              where=w)
    css = rep(css,
              '.result .n{font-family:var(--serif);font-size:2rem;font-weight:600;color:var(--ok);line-height:1;}',
              '.result .n{font-family:var(--display);font-size:2rem;font-weight:800;letter-spacing:-0.02em;color:var(--ok);line-height:1;}',
              where=w)
    css = rep(css,
              '.gates .g{font-family:var(--serif);font-style:italic;color:#E4C883;font-size:1.125rem;line-height:1.3;white-space:nowrap;}',
              '.gates .g{font-family:var(--display);font-weight:800;font-variant-numeric:tabular-nums;color:#E4C883;font-size:1.125rem;line-height:1.3;white-space:nowrap;}',
              where=w)
    css = rep(css,
              '.timeline .time{font-family:var(--serif);font-style:italic;color:var(--gold-dark);font-size:1.0625rem;}',
              '.timeline .time{font-family:var(--display);font-weight:700;font-variant-numeric:tabular-nums;color:var(--gold-dark);font-size:1rem;}',
              where=w)
    css = rep(css,
              '.contact-copy .next li span{font-family:var(--serif);font-style:italic;color:var(--gold);font-size:1.125rem;}',
              '.contact-copy .next li span{font-family:var(--display);font-weight:800;font-variant-numeric:tabular-nums;color:var(--gold);font-size:1.0625rem;}',
              where=w)

    # Sub-headings that were serif
    css = rep(css,
              '.guarantee strong{font-family:var(--serif);font-size:1.25rem;font-weight:600;display:block;}',
              '.guarantee strong{font-family:var(--display);font-size:1.1875rem;font-weight:700;letter-spacing:-0.015em;display:block;}',
              where=w)
    css = rep(css,
              '.area h4{font-family:var(--serif);font-weight:600;font-size:1.25rem;',
              '.area h4{font-family:var(--display);font-weight:700;font-size:1.125rem;letter-spacing:-0.015em;',
              where=w)
    css = rep(css,
              'font-family:var(--serif);font-weight:600;font-size:1.1875rem;line-height:1.3;}',
              'font-family:var(--display);font-weight:600;font-size:1.0625rem;letter-spacing:-0.01em;line-height:1.35;}',
              where=w)

    # No italic face is shipped, so nothing may ask for one
    css = rep(css,
              'font-size:.9375rem;margin-bottom:14px;font-style:italic;color:var(--ink);}',
              'font-size:.9375rem;margin-bottom:14px;color:var(--ink);}',
              where=w)

    none_of(css, ['var(--serif)', 'font-style:italic', 'Source Serif', 'Public Sans',
                  'source-serif', 'public-sans'], w)
    return css


# ------------------------------------------------------------ dashboard.html
def edit_dashboard(html):
    w = 'dashboard.html'
    html = rep(html, OLD_PRELOADS, NEW_PRELOADS, where=w)
    html = rep(html,
               '  ' + OLD_FACES.replace('\n', '\n  ').rstrip(' '),
               '  ' + NEW_FACES.replace('\n', '\n  ').rstrip(' '),
               where=w)
    html = rep(html,
               "    --serif:'Source Serif 4', Georgia, 'Times New Roman', serif;\n"
               "    --sans:'Public Sans', -apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, Helvetica, Arial, sans-serif;\n",
               "    --display:'Archivo', 'Helvetica Neue', Arial, sans-serif;\n"
               "    --sans:'IBM Plex Sans', -apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, Helvetica, Arial, sans-serif;\n",
               where=w)
    html = rep(html,
               'h1{font-family:var(--serif);font-size:24px;font-weight:600;margin:0 0 4px;letter-spacing:-0.01em;}',
               'h1{font-family:var(--display);font-size:24px;font-weight:700;margin:0 0 4px;letter-spacing:-0.02em;}',
               where=w)
    html = rep(html, 'var(--serif)', 'var(--display)', count=2, where=w)
    html = rep(html, OLD_FAVICON, NEW_FAVICON, where=w)
    none_of(html, ['var(--serif)', 'Source Serif', 'Public Sans', 'source-serif', 'public-sans'], w)
    return html


# ------------------------------------------------------------------- pages
def edit_page(html, name):
    if name != 'thanks.html':
        html = rep(html, OLD_PRELOADS, NEW_PRELOADS, where=name)
    html = rep(html, 'styles.css?v=6', 'styles.css?v=7', where=name)
    html = rep(html, 'script.js?v=6', 'script.js?v=7', where=name)
    html = rep(html, OLD_FAVICON, NEW_FAVICON, where=name)
    none_of(html, ['source-serif', 'public-sans', '?v=6'], name)
    return html


# ---------------------------------------------------------- font-preview.html
def edit_preview(html):
    w = 'font-preview.html'
    # The old faces now come from Google Fonts so the "before" column still renders
    html = rep(html,
               '<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;800&family=Bitter',
               '<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;0,8..60,700;1,8..60,500&family=Public+Sans:wght@400;600;700;800&family=Archivo:wght@500;700;800&family=Bitter',
               where=w)
    html = rep(html,
               "  @font-face{font-family:'Source Serif 4';src:url('fonts/source-serif-4.woff2') format('woff2');font-weight:200 900;font-style:normal;}\n"
               "  @font-face{font-family:'Source Serif 4';src:url('fonts/source-serif-4-italic.woff2') format('woff2');font-weight:200 900;font-style:italic;}\n"
               "  @font-face{font-family:'Public Sans';src:url('fonts/public-sans.woff2') format('woff2');font-weight:100 900;font-style:normal;}\n",
               '',
               where=w)
    html = rep(html,
               '<div class="label"><div><span>Current</span> Source Serif 4 headings, Public Sans text</div><small>What is live today</small></div>',
               '<div class="label"><div><span>Previous</span> Source Serif 4 headings, Public Sans text</div><small>What was live before the change</small></div>',
               where=w)
    html = rep(html,
               '<div class="label"><div><span>Option A (recommended)</span> Newsreader headings',
               '<div class="label"><div><span>Option A</span> Newsreader headings',
               where=w)
    html = rep(html,
               '<div class="label"><div><span>Option B</span> Archivo headings, IBM Plex Sans text</div>',
               '<div class="label"><div><span>Option B (applied)</span> Archivo headings, IBM Plex Sans text</div>',
               where=w)
    html = rep(html,
               'Same content, same colours, four typefaces. Option A is the recommendation.',
               'Same content, same colours, four typefaces. Option B was chosen and is now live.',
               where=w)
    none_of(html, ['source-serif-4.woff2', 'public-sans.woff2'], w)
    return html


def main():
    pending = {}

    p = ROOT / 'styles.css'
    pending[p] = edit_styles(p.read_text(encoding='utf-8'))

    p = ROOT / 'dashboard.html'
    pending[p] = edit_dashboard(p.read_text(encoding='utf-8'))

    for name in PAGES:
        p = ROOT / name
        pending[p] = edit_page(p.read_text(encoding='utf-8'), name)

    p = ROOT / 'font-preview.html'
    pending[p] = edit_preview(p.read_text(encoding='utf-8'))

    # All guards passed: write everything
    for path, text in pending.items():
        path.write_text(text, encoding='utf-8', newline='\n')
        print(f'wrote {path.relative_to(ROOT)}')

    # Remove the old font files only once nothing deployable references them
    live = [q for q in ROOT.rglob('*') if q.suffix in ('.html', '.css', '.js')
            and 'tools' not in q.parts and 'research' not in q.parts]
    for fname in OLD_FONT_FILES:
        refs = [q.name for q in live if fname in q.read_text(encoding='utf-8', errors='ignore')]
        if refs:
            raise SystemExit(f'{fname} still referenced by {refs}; not deleting')
        target = ROOT / 'fonts' / fname
        if target.exists():
            target.unlink()
            print(f'removed fonts/{fname}')


if __name__ == '__main__':
    main()
