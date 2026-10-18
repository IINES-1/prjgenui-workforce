"""
Apply the v20 redesign to every public page.

Heads (SEO, JSON-LD, noindex) are kept as they are. This script swaps
the body chrome (banner, header, footer) and converts each page's
opening block into the new hero. Run once from the repo root; originals
are in tools/backup-v1-design.
"""
import os
import re

ROOT = r'C:\Users\is1lv\PRJGENUI-Workforce'
CSS_OLD = re.compile(r'styles\.css\?v=\d+')
JS_TAG = '<script>document.documentElement.className="js"</script>'

TOP = '''<a class="skip" href="#main">Skip to content</a>
<div class="progress" aria-hidden="true"><i></i></div>

<div class="banner" role="region" aria-label="Announcement">
  <div class="wrap">
    <span class="dot" aria-hidden="true"></span>
    <span><strong>Pilot open.</strong> We're taking on our first contractors across Hampshire, Surrey and the South East.</span>
    <a href="contact.html">Request a crew</a>
  </div>
</div>

<header class="site-header">
  <div class="wrap">
    <a href="index.html" class="brand" aria-label="PRJGENUI Workforce, home">
      <img class="mark" src="images/brand/crane-mark-96.png" srcset="images/brand/crane-mark-96.png 1x, images/brand/crane-mark-192.png 2x" width="44" height="44" alt="">
      <span class="word">PRJGENUI Workforce<span>Workforce intelligence</span></span>
    </a>
    <nav class="nav" aria-label="Main">
      <a href="index.html">Home</a>
      <a href="about.html">About</a>
      <a href="contact.html">Contact</a>
      <a href="dashboard.html">Dashboard</a>
    </nav>
    <div class="header-cta">
      <a href="#" class="phone" data-phone style="display:none;"></a>
      <a href="contact.html" class="btn btn-gold btn-sm">Request a crew</a>
      <button class="nav-toggle" type="button" aria-label="Toggle navigation" aria-expanded="false">
        <span></span><span></span><span></span>
      </button>
    </div>
  </div>
</header>
<nav class="mobile-nav" aria-label="Mobile">
  <a href="index.html">Home</a>
  <a href="about.html">About</a>
  <a href="contact.html">Contact</a>
  <a href="dashboard.html">Dashboard</a>
  <a href="contact.html" class="dash">Request a crew</a>
</nav>
'''

FOOTER = '''<footer class="footer">
  <div class="hazard" aria-hidden="true" style="position:absolute;left:0;right:0;top:0;"></div>
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <a href="index.html" class="brand">
          <img class="mark" src="images/brand/crane-mark-96.png" srcset="images/brand/crane-mark-96.png 1x, images/brand/crane-mark-192.png 2x" width="44" height="44" alt="">
          <span class="word">PRJGENUI Workforce<span>Workforce intelligence</span></span>
        </a>
        <p class="about">Verified painters and decorators, proven crews and reliability data for contractors across Hampshire, Surrey and the South East.</p>
      </div>
      <div>
        <h4>For contractors</h4>
        <ul>
          <li><a href="index.html#services">Services</a></li>
          <li><a href="index.html#how-it-works">How it works</a></li>
          <li><a href="index.html#compare">Compare</a></li>
          <li><a href="contact.html">Request a crew</a></li>
        </ul>
      </div>
      <div>
        <h4>For workers</h4>
        <ul>
          <li><a href="index.html#how-it-works">Workforce Passport</a></li>
          <li><a href="index.html#faq">FAQ</a></li>
          <li><a href="contact.html">Register for shifts</a></li>
        </ul>
      </div>
      <div>
        <h4>Company</h4>
        <ul>
          <li><a href="about.html">About</a></li>
          <li><a href="contact.html">Contact</a></li>
          <li><a href="dashboard.html">Dashboard demo</a></li>
          <li><a href="privacy.html">Privacy Policy</a></li>
          <li><a href="terms.html">Terms</a></li>
          <li><a href="mailto:hello@prjgenuiworkforce.co.uk">hello@prjgenuiworkforce.co.uk</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span>PRJGENUI Workforce Ltd. is registered in England and Wales, company number 13205257</span>
      <span>Registered office: 124 City Road, London EC1V 2NX</span>
    </div>
    <div class="footer-word" aria-hidden="true">PRJGENUI</div>
  </div>
</footer>

<div class="sticky-cta">
  <a href="contact.html" class="btn btn-gold">Request a crew</a>
</div>

<a href="#" class="wa" aria-label="Chat on WhatsApp" title="Chat on WhatsApp">
  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>
  </svg>
</a>

<script src="script.js?v=20"></script>
</body>
</html>
'''


def read(name):
    with open(os.path.join(ROOT, name), encoding='utf-8') as f:
        return f.read()


def write(name, text):
    with open(os.path.join(ROOT, name), 'w', encoding='utf-8', newline='') as f:
        f.write(text)


def must_sub(pattern, repl, text, flags=re.S, count=1):
    new, n = re.subn(pattern, repl, text, count=count, flags=flags)
    if n == 0:
        raise SystemExit('pattern not found: ' + pattern[:70])
    return new


def head_fix(html):
    html = CSS_OLD.sub('styles.css?v=20', html)
    if JS_TAG not in html:
        html = html.replace('</head>', JS_TAG + '\n</head>', 1)
    return html


def split_chrome(html):
    """Return (head_through_body_tag, rest_after_nav_and_before_footer_removed)."""
    i = html.index('<body>') + len('<body>')
    return html[:i]


def page_hero(eyebrow, h1, lede, img=None, alt=''):
    pic = ''
    grid_open = '<div>'
    if img:
        pic = ('\n      <div class="ph-img"><img src="%s" alt="%s" width="1400" height="933" fetchpriority="high"></div>'
               % (img, alt))
        grid_open = '<div class="ph-grid">\n      <div>'
    close = '\n      </div>' + pic + '\n    </div>' if img else '\n    </div>'
    if img:
        return ('<section class="page-hero">\n  <div class="wrap">\n    %s\n        <p class="ey">%s</p>\n'
                '        <h1>%s</h1>\n        <p class="lede">%s</p>%s\n  </div>\n</section>\n'
                % (grid_open, eyebrow, h1, lede, close))
    return ('<section class="page-hero">\n  <div class="wrap">\n    <div>\n      <p class="ey">%s</p>\n'
            '      <h1>%s</h1>\n      <p class="lede">%s</p>\n    </div>\n  </div>\n</section>\n'
            % (eyebrow, h1, lede))


def cta_band(h2, text, href, label):
    return ('<section class="cta-band">\n  <div class="wrap">\n    <div class="cta-in">\n      <div>\n'
            '        <h2>%s</h2>\n        <p>%s</p>\n      </div>\n'
            '      <a href="%s" class="btn btn-navy">%s</a>\n    </div>\n  </div>\n</section>\n'
            % (h2, text, href, label))


def inner_page(name, hero_html, mutate):
    html = read(name)
    html = head_fix(html)
    body_i = html.index('<body>') + len('<body>')
    head = html[:body_i]
    foot_i = html.index('<!-- ====== Footer ====== -->')
    middle = html[body_i:foot_i]
    # drop the old chrome (top rule, header, mobile nav) up to the first page section
    mi = middle.index('<nav class="mobile-nav">')
    middle = middle[middle.index('</nav>', mi) + len('</nav>'):].lstrip('\n')
    middle = mutate(middle, hero_html)
    write(name, head + '\n' + TOP + '\n<main id="main">\n' + middle + '</main>\n\n' + FOOTER)
    print('built', name)


# ---------------------------------------------------------------- about
def about(middle, hero):
    middle = must_sub(r'<!-- ====== Page hero ====== -->.*?(?=<!-- ====== Why we exist)', hero + '\n', middle)
    middle = middle.replace('<section class="section paper-deep">', '<section class="section sage">')
    middle = middle.replace('<div class="products reveal">', '<div class="pairs reveal">')
    middle = middle.replace('<div class="product">', '<div class="product-row">')
    middle = must_sub(r'<!-- ====== CTA ====== -->.*?</section>\n',
                      cta_band('Talk to us',
                               "We're taking on our first pilot partners across Hampshire, Surrey and the South East. If you'd like to be one of them, get in touch and we'll arrange a call.",
                               'contact.html', 'Get in touch'), middle)
    middle = middle.replace('<div class="section-head reveal">\n      <h2>', '<div class="section-head reveal">\n      <h2>')
    return middle


# -------------------------------------------------------------- contact
def contact(middle, hero):
    middle = must_sub(r'<!-- ====== Page hero ====== -->.*?(?=<!-- ====== Contact ====== -->)', hero + '\n', middle)
    middle = middle.replace('<section class="section paper-deep">', '<section class="section sage">')
    middle = middle.replace('<ol class="next">', '<ol class="next">')
    middle = must_sub(r'<!-- ====== CTA ====== -->.*?</section>\n',
                      cta_band('Want to see the dashboard first?',
                               'The demo uses sample data and shows how the compliance checks, Trust Score and replacement process work.',
                               'dashboard.html', 'View the dashboard'), middle)
    return middle


# ---------------------------------------------------------- legal pages
def legal(middle, hero_unused):
    m = re.search(r'<section class="section">\s*<div class="wrap">\s*<div class="section-head reveal">\s*<h2>(.*?)</h2>\s*<p class="lede">(.*?)</p>\s*</div>\s*<div class="reveal">', middle, re.S)
    if not m:
        raise SystemExit('legal header not found')
    title, lede = m.group(1), m.group(2)
    new_open = (page_hero('Legal', title, lede) +
                '\n<section class="section">\n  <div class="wrap">\n    <div class="prose">')
    return middle[:m.start()] + new_open + middle[m.end():]


inner_page('about.html',
           page_hero('About',
                     'How PRJGENUI started',
                     "PRJGENUI Workforce began on a painting and decorating project in the South East. We watched contractors ring round agencies on a Friday afternoon and hope somebody would turn up on Monday. We thought there had to be a better way of doing it.",
                     'images/about-hero-team.jpg',
                     'Two PRJGENUI Workforce team members reviewing site reports in their office'),
           about)

inner_page('contact.html',
           page_hero('Contact',
                     'Get in touch',
                     'Fill in the short form below and a person will reply within one business day.',
                     'images/contact-hero-office.jpg',
                     'PRJGENUI Workforce office reception area with a map of Surrey and Hampshire on the wall'),
           contact)

inner_page('privacy.html', None, legal)
inner_page('terms.html', None, legal)

# ---------------------------------------------------------------- index
html = head_fix(read('index.html'))
body_i = html.index('<body>') + len('<body>')
main = read(os.path.join('tools', 'parts', 'index-main.html'))
write('index.html', html[:body_i] + '\n' + TOP + '\n' + main + '\n' + FOOTER)
print('built index.html')

# --------------------------------------------------------------- thanks
t = head_fix(read('thanks.html'))
body_i = t.index('<body>') + len('<body>')
thanks_main = '''
<main id="main" class="utility">
  <div class="wrap">
    <p class="ey">Message sent</p>
    <h1>Thanks. We've got it.</h1>
    <p>Someone will reply within one business day. If you need us sooner, email <a href="mailto:hello@prjgenuiworkforce.co.uk" style="color:#fff;">hello@prjgenuiworkforce.co.uk</a>.</p>
    <div class="actions">
      <a href="index.html" class="btn btn-gold">Back to home</a>
      <a href="dashboard.html" class="btn btn-ghost">View the dashboard</a>
    </div>
  </div>
</main>

<script src="script.js?v=20"></script>
</body>
</html>
'''
write('thanks.html', t[:body_i] + thanks_main)
print('built thanks.html')
