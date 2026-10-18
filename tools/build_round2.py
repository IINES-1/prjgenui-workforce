"""Round 2: apply the client's brief (contractors first, her wording rules).

Regenerates index, about, contact, request and workers; swaps shared chrome and
fixes wording on terms, privacy and thanks. Backs up the old files first.
Run from anywhere:  python tools/build_round2.py
"""
import json
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKUP = os.path.join(ROOT, 'tools', 'backup-round1')
V = '26'
SITE = 'https://prjgenuiworkforce.co.uk'
EMAIL = 'hello@prjgenuiworkforce.co.uk'

PAGES = ['index.html', 'about.html', 'contact.html', 'terms.html', 'privacy.html', 'thanks.html']


def read(name):
    with open(os.path.join(ROOT, name), encoding='utf-8') as f:
        return f.read()


def write(name, text):
    with open(os.path.join(ROOT, name), 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)


def must_replace(text, old, new, label=''):
    if old not in text:
        sys.exit('NOT FOUND (%s): %r' % (label, old[:80]))
    return text.replace(old, new)


def soft_replace(text, old, new, label=''):
    """Replace if the old text is there; accept if the new text already is (re-runnable)."""
    if old in text:
        return text.replace(old, new)
    if new in text:
        return text
    sys.exit('NOT FOUND (%s): %r' % (label, old[:80]))


if not os.path.isdir(BACKUP):
    os.makedirs(BACKUP)
    for p in PAGES + ['script.js', 'styles.css']:
        shutil.copy2(os.path.join(ROOT, p), os.path.join(BACKUP, p))

# ---------------------------------------------------------------- shared chrome

LOGO = ('<img class="mark" src="images/brand/crane-mark-96.png" '
        'srcset="images/brand/crane-mark-96.png 1x, images/brand/crane-mark-192.png 2x" '
        'width="44" height="44" alt="">')

TOP = '''<a class="skip" href="#main">Skip to content</a>
<div class="progress" aria-hidden="true"><i></i></div>

<header class="site-header">
  <div class="wrap">
    <a href="index.html" class="brand" aria-label="PRJGENUI Workforce, home">
      LOGO
      <span class="word">PRJGENUI Workforce<span>Workforce certainty</span></span>
    </a>
    <nav class="nav" aria-label="Main">
      <a href="index.html">Home</a>
      <a href="workers.html">For workers</a>
      <a href="about.html">About</a>
      <a href="contact.html">Contact</a>
    </nav>
    <div class="header-cta">
      <a href="#" class="phone" data-phone style="display:none;"></a>
      <a href="request.html" class="btn btn-gold btn-sm">Request Workers or a Crew</a>
      <button class="nav-toggle" type="button" aria-label="Toggle navigation" aria-expanded="false">
        <span></span><span></span><span></span>
      </button>
    </div>
  </div>
</header>
<nav class="mobile-nav" aria-label="Mobile">
  <a href="index.html">Home</a>
  <a href="workers.html">For workers</a>
  <a href="about.html">About</a>
  <a href="contact.html">Contact</a>
  <a href="request.html" class="dash">Request Workers or a Crew</a>
</nav>

'''.replace('LOGO', LOGO)

FOOTER = '''<footer class="footer">
  <div class="hazard" aria-hidden="true" style="position:absolute;left:0;right:0;top:0;"></div>
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <a href="index.html" class="brand">
          LOGO
          <span class="word">PRJGENUI Workforce<span>Workforce certainty</span></span>
        </a>
        <p class="about">Verified workers, skilled operatives and work-ready crews for contractors across Hampshire, Surrey and the South East.</p>
      </div>
      <div>
        <h4>For contractors</h4>
        <ul>
          <li><a href="request.html">Request Workers or a Crew</a></li>
          <li><a href="index.html#how-it-works">How it works</a></li>
          <li><a href="index.html#checks">What we check</a></li>
          <li><a href="index.html#faq">FAQ</a></li>
        </ul>
      </div>
      <div>
        <h4>For workers</h4>
        <ul>
          <li><a href="workers.html">Register as a Worker</a></li>
          <li><a href="workers.html#passport">Worker Passport</a></li>
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
          <li><a href="mailto:EMAIL">EMAIL</a></li>
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
  <a href="request.html" class="btn btn-gold">Request Workers or a Crew</a>
</div>

<a href="#" class="wa" aria-label="Chat on WhatsApp" title="Chat on WhatsApp">
  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>
  </svg>
</a>

<script src="secrets.js"></script>
<script src="script.js?v=VV"></script>
</body>
</html>
'''.replace('LOGO', LOGO).replace('EMAIL', EMAIL).replace('VV', V)


def head(title, desc, path, og_title, og_desc, ld=()):
    ld_html = ''.join('<script type="application/ld+json">\n%s\n</script>\n' % json.dumps(b, indent=2, ensure_ascii=False) for b in ld)
    url = SITE + '/' if path == 'index.html' else SITE + '/' + path
    return '''<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, nofollow">
<title>TITLE</title>
<meta name="description" content="DESC">
<meta name="author" content="PRJGENUI Workforce Ltd">
<meta name="theme-color" content="#1F3A2E">
<link rel="canonical" href="URL">

<meta property="og:type" content="website">
<meta property="og:title" content="OGT">
<meta property="og:description" content="OGD">
<meta property="og:url" content="URL">
<meta property="og:image" content="SITE/images/og-image.jpg">
<meta property="og:locale" content="en_GB">
<meta property="og:site_name" content="PRJGENUI Workforce">

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="OGT">
<meta name="twitter:description" content="OGD">
<meta name="twitter:image" content="SITE/images/og-image.jpg">

<link rel="preload" href="fonts/archivo.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="fonts/ibm-plex-sans.woff2" as="font" type="font/woff2" crossorigin>

<link rel="stylesheet" href="styles.css?v=VV">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" type="image/png" sizes="32x32" href="/images/brand/favicon-32.png">
<link rel="icon" type="image/png" sizes="48x48" href="/images/brand/favicon-48.png">
<link rel="apple-touch-icon" href="/images/brand/apple-touch-icon.png">

LD<script>document.documentElement.className="js"</script>
</head>
<body>
'''.replace('TITLE', title).replace('DESC', desc).replace('URL', url).replace('OGT', og_title) \
       .replace('OGD', og_desc).replace('SITE', SITE).replace('VV', V).replace('LD', ld_html)


def page(path, title, desc, og_title, og_desc, main, ld=()):
    html = head(title, desc, path, og_title, og_desc, ld) + TOP + '<main id="main">\n' + main.strip() + '\n</main>\n\n' + FOOTER
    write(path or 'index.html', html)


def page_hero(eyebrow, h1, lede, img=None, alt=''):
    if img:
        return ('<section class="page-hero">\n  <div class="wrap">\n    <div class="ph-grid">\n      <div>\n'
                '        <p class="ey">%s</p>\n        <h1>%s</h1>\n        <p class="lede">%s</p>\n      </div>\n'
                '      <div class="ph-img"><img src="%s" alt="%s" width="1400" height="933" fetchpriority="high"></div>\n'
                '    </div>\n  </div>\n</section>\n' % (eyebrow, h1, lede, img, alt))
    return ('<section class="page-hero">\n  <div class="wrap">\n    <div>\n      <p class="ey">%s</p>\n'
            '      <h1>%s</h1>\n      <p class="lede">%s</p>\n    </div>\n  </div>\n</section>\n' % (eyebrow, h1, lede))


def cta_band(h2, text, href, label):
    return ('<section class="cta-band">\n  <div class="wrap">\n    <div class="cta-in">\n      <div>\n'
            '        <h2>%s</h2>\n        <p>%s</p>\n      </div>\n'
            '      <a href="%s" class="btn btn-navy">%s</a>\n    </div>\n  </div>\n</section>\n' % (h2, text, href, label))


ORG = {
    "@type": "Organization",
    "name": "PRJGENUI Workforce",
    "legalName": "PRJGENUI Workforce Ltd.",
    "identifier": "13205257",
    "foundingDate": "2021-02-16",
    "description": "PRJGENUI Workforce helps contractors request, check and manage skilled operatives and work-ready crews across Hampshire, Surrey and the South East.",
    "url": SITE + "/",
    "email": EMAIL,
    "founder": {"@type": "Person", "name": "Marizilena Silva Fortes", "jobTitle": "Founder and Director"},
    "address": {"@type": "PostalAddress", "streetAddress": "124 City Road", "addressLocality": "London",
                "postalCode": "EC1V 2NX", "addressCountry": "GB"},
    "areaServed": ["Hampshire", "Surrey", "South East England"],
    "knowsAbout": ["Construction workforce supply", "CSCS card checks", "Right to Work checks",
                   "Painting and decorating labour", "Worker reliability records"],
    "logo": SITE + "/images/brand/crane-mark-512.png",
}


def ld_org():
    d = {"@context": "https://schema.org"}
    d.update(ORG)
    return d


# ---------------------------------------------------------------- FAQ (shared by html + JSON-LD)

PASSPORT_NOTE = ("A Worker Passport is a PRJGENUI workforce profile. It is not an official government passport "
                 "or identity document.")
SIXTY = ("If a confirmed worker reports a no-show or late cancellation, we aim to begin the replacement search "
         "within 60 minutes during our operating hours.")
CARD_CHECK = ("Where an official verification service or recognised database is available, card and qualification "
              "details are checked against the relevant source and the verification evidence is recorded.")

FAQ = [
    ("What does PRJGENUI Workforce do?", [
        "We help contractors request, check and manage skilled operatives and work-ready crews. We bring Right to Work, CSCS, training, experience and work history together in one record, so you can see who is suitable and available before they reach site.",
        "We're based on the realities of construction sites, so we do more than send people. We match against the actual job and site requirements, and keep a record after deployment."]),
    ("What is a Worker Passport?", [
        "A Worker Passport holds a worker's Right to Work evidence, CSCS and trade cards, qualifications, training, experience, work history and reliability record in one place. It takes the place of a CV that nobody can check.",
        PASSPORT_NOTE]),
    ("How are cards and qualifications checked?", [CARD_CHECK,
        "Expiry dates are tracked, and anything that has expired is flagged so the worker isn't put forward for jobs that need it."]),
    ("What happens if someone doesn't turn up?", [SIXTY,
        "That's a commitment to start the search quickly, not a promise that a replacement will be found. The no-show stays on the worker's record, so the next contractor sees an honest history."]),
    ("What counts as a work-ready crew?", [
        "We only call a group a crew when its members have genuinely worked together before. If we put forward individuals who haven't, we say so.",
        "A work-ready crew also means the cards and training you asked for have been checked before they arrive."]),
    ("How do I request workers or a crew?", [
        'Use the <a href="request.html">request form</a>. Tell us the trade, how many people, the site location, start date, how long you need them and any cards or training the site requires. We aim to respond within one business day.',
        "If it's urgent, tick the urgent box on the form. A phone and WhatsApp line for urgent requests is being set up."]),
    ("How much do painters and decorators cost in the UK?", [
        "Agency supply rates for painters and decorators usually sit between £15 and £24 an hour, with experienced decorators in the South East towards the top of that range.",
        "Day rates for agency labour tend to fall between £120 and £190, and specialist trades cost more. We confirm the exact rate in writing before every assignment."]),
    ("Do I need a CSCS card to work as a painter and decorator?", [
        "For almost all site work, yes. Most principal contractors won't let you through the gate without a valid CSCS card.",
        "We check cards against the relevant source where a verification service is available, and we track expiry dates so nobody gets caught out by a lapsed card."]),
    ("What areas does PRJGENUI Workforce cover?", [
        'Hampshire, Surrey and the wider South East, including Guildford, Woking, Farnborough, Basingstoke, Winchester, Reading and the towns around them. <a href="#coverage">See the full list above</a>.',
        "We're running a pilot with a small number of contractors, so we're growing the area steadily rather than spreading ourselves thin."]),
    ("I'm a painter or decorator looking for work. How do I join?", [
        'Use <a href="workers.html">Register as a Worker</a>. There is no fee. You\'ll need Right to Work in the UK and, for most site work, a valid CSCS card. We then set up your Worker Passport and match you to work by trade, area and record.']),
]


def strip_tags(s):
    return re.sub(r'<[^>]+>', '', s)


FAQ_HTML = ''
for i, (q, ans) in enumerate(FAQ):
    FAQ_HTML += '        <details%s>\n          <summary>%s</summary>\n          <div class="answer">\n%s\n          </div>\n        </details>\n' % (
        ' open' if i == 0 else '', q, '\n'.join('            <p>%s</p>' % a for a in ans))

FAQ_LD = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
    {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": ' '.join(strip_tags(a) for a in ans)}}
    for q, ans in FAQ]}

# ---------------------------------------------------------------- home

INDEX_MAIN = r'''
<!-- ====== Hero ====== -->
<section class="hero">
  <svg class="crane" viewBox="0 0 520 540" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true" focusable="false">
    <defs><pattern id="lat" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M0 20L20 0M0 0L20 20"/></pattern></defs>
    <rect x="380" y="70" width="20" height="470" fill="url(#lat)"/>
    <rect x="366" y="516" width="48" height="20"/>
    <g class="jib">
      <rect x="30" y="46" width="470" height="20" fill="url(#lat)"/>
      <path d="M390 8V46M390 8L70 46M390 8L480 46"/>
      <rect x="456" y="66" width="38" height="46" fill="currentColor" stroke="none" opacity=".6"/>
      <rect x="374" y="40" width="32" height="30" fill="#14271E"/>
      <g class="hook"><path d="M110 66V190"/><rect x="102" y="190" width="16" height="14"/><rect x="62" y="204" width="96" height="62"/><path d="M80 236l12 12 24-26"/></g>
    </g>
  </svg>
  <div class="wrap">
    <div class="hero-grid">
      <div class="hero-text">
        <p class="ey">For contractors &middot; Hampshire &middot; Surrey &middot; South East</p>
        <h1>
          <span class="ln"><span style="--i:0">Workforce</span></span>
          <span class="ln"><span style="--i:1"><em>certainty,</em></span></span>
          <span class="ln"><span style="--i:2">not just CVs.</span></span>
        </h1>
        <p class="lede">We help you request, check and manage skilled operatives and work-ready crews. Right to Work, CSCS, training, experience and work history, brought together so you can see who is suitable and available before they reach your site.</p>
        <div class="hero-ctas">
          <a href="request.html" class="btn btn-gold">Request Workers or a Crew</a>
          <a href="workers.html" class="btn btn-ghost">Register as a Worker</a>
        </div>
      </div>
      <div class="hero-visual">
        <div class="hero-photo">
          <img src="images/hero-decorator-cutting-in.jpg" alt="Painter cutting in around a door frame on a school refurbishment site in Surrey" width="1600" height="900" fetchpriority="high">
        </div>
        <div class="pass" role="group" aria-label="Example Worker Passport, illustrative">
          <div class="pass-b">
            <p class="pass-tag">Worker Passport &middot; illustrative, not a real worker</p>
            <div class="pass-head">
              <span class="avatar" aria-hidden="true">JC</span>
              <div><strong>J. Carter</strong><span class="pid">Painter and decorator</span></div>
            </div>
            <ul class="pass-list">
              <li style="--i:0">Right to Work<span class="state"><span class="wait">Checking</span><span class="done">&#10003; Checked</span></span></li>
              <li style="--i:1">CSCS card<span class="state"><span class="wait">Checking</span><span class="done">&#10003; Checked</span></span></li>
              <li style="--i:2">Working at height<span class="state"><span class="wait">Checking</span><span class="done">&#10003; Checked</span></span></li>
              <li style="--i:3">Asbestos awareness<span class="state"><span class="wait">Checking</span><span class="done">&#10003; Checked</span></span></li>
            </ul>
            <div class="pass-foot">
              <div class="score"><b>46/47</b><span>Shifts attended</span></div>
              <span class="stamp">Site ready</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="hero-facts">
      <div class="hs">
        <strong data-count="41200">41,200</strong>
        <span>Extra construction workers the UK needs every year to 2030, according to CITB</span>
      </div>
      <div class="hs">
        <strong data-count="60" data-suffix=" min">60 min</strong>
        <span>Our aim for starting a replacement search after a no-show or late cancellation, during operating hours</span>
      </div>
      <div class="hs">
        <strong data-count="6" data-suffix=" checks">6 checks</strong>
        <span>Right to Work, CSCS, qualifications, training, work history and expiry dates, recorded for every worker</span>
      </div>
    </div>
  </div>
</section>

<!-- ====== Ticker ====== -->
<div class="ticker" aria-label="What we bring together for every worker">
  <div class="tk">
    <span>Right to Work</span><span>CSCS cards</span><span>Qualifications</span><span>Training certificates</span><span>Work history</span><span>Reliability record</span>
    <span aria-hidden="true">Right to Work</span><span aria-hidden="true">CSCS cards</span><span aria-hidden="true">Qualifications</span><span aria-hidden="true">Training certificates</span><span aria-hidden="true">Work history</span><span aria-hidden="true">Reliability record</span>
  </div>
</div>

<!-- ====== Audience split ====== -->
<section class="section" id="who">
  <div class="wrap">
    <div class="section-head reveal">
      <p class="ey">Two ways in</p>
      <h2>Contractors first, with a clear route for workers</h2>
      <p class="lede">Contractors tell us what the job needs. Workers build a record that shows what they can do. We match one to the other.</p>
    </div>
    <div class="split reveal">
      <div class="panel gold">
        <span class="kicker">For contractors</span>
        <h3>Know who is coming to site, and what they hold</h3>
        <p class="lede">Tell us the trade, how many people you need, where, when and for how long, plus any cards or training the site requires. We check the evidence, match against your actual requirements and keep a record after deployment.</p>
        <ul>
          <li>Compliance evidence checked and recorded before workers are put forward</li>
          <li>Experience backed by work history, not just a job title</li>
          <li>A reliability record for each worker</li>
          <li>Crews only where the people have genuinely worked together</li>
        </ul>
        <div class="actions"><a href="request.html" class="btn btn-navy">Request Workers or a Crew</a></div>
      </div>
      <div class="panel deep">
        <span class="kicker">For workers</span>
        <h3>Build a Worker Passport that shows what you can do</h3>
        <p class="lede">There is no fee for workers to register. Matching is based on the job requirements, recorded evidence and worker availability. Register once and your cards, training, experience and work history sit in one place. Every job you finish adds to your reliability record.</p>
        <ul>
          <li>One profile for your cards, training and experience</li>
          <li>No fee to join and no fee to be matched</li>
          <li>Work offered on the strength of your record</li>
          <li>Your record stays with you when you move on</li>
        </ul>
        <div class="actions"><a href="workers.html" class="btn btn-steel">Register as a Worker</a></div>
      </div>
    </div>
  </div>
</section>

<!-- ====== Problem: what contractors tell us ====== -->
<section class="section sage" id="problem">
  <div class="wrap">
    <div class="problem">
      <div class="problem-l reveal">
        <p class="ey">What contractors tell us</p>
        <h2>We know how these problems land on site</h2>
        <p class="lede" style="margin-top:20px;">These are the complaints we hear most from contractors, and what we do about each one.</p>
        <div class="problem-note">
          <strong>Most of it is avoidable</strong> when the evidence is checked and written down before the worker arrives.
        </div>
      </div>
      <ol class="qs reveal">
        <li><div>No-shows and last-minute cancellations<p>Attendance goes on every worker's record. If a confirmed worker doesn't show, we aim to begin the replacement search within 60 minutes.</p></div></li>
        <li><div>Agencies sending people who aren't really available<p>We check availability against your dates before anyone is put forward.</p></div></li>
        <li><div>"Experienced" workers who can't do the job<p>Experience is shown through work history, references and supervisor feedback, not a job title.</p></div></li>
        <li><div>Expired or missing CSCS and training<p>Cards and training are checked, expiry dates are tracked, and anything out of date is flagged.</p></div></li>
        <li><div>Agencies that don't check documents<p>Checks are made and the verification evidence is recorded, so you can see what was checked.</p></div></li>
        <li><div>Different workers from the ones agreed<p>You see the names before anyone travels, and any change is agreed with you first.</p></div></li>
        <li><div>Slow replacement<p>We start from a pool of workers already on file by trade and area, so the search doesn't begin from nothing.</p></div></li>
        <li><div>CVs with no attendance, performance or would-use-again evidence<p>A Worker Passport carries a reliability record: attendance, performance evidence and whether contractors would use the worker again.</p></div></li>
        <li><div>"Crews" who have never worked together<p>We only call a group a crew when its members have genuinely worked together.</p></div></li>
      </ol>
    </div>
  </div>
</section>

<!-- ====== What you get ====== -->
<section class="section" id="services">
  <div class="wrap">
    <div class="section-head reveal">
      <p class="ey">What you get</p>
      <h2>Five things a list of names can't give you</h2>
      <p class="lede">Each is useful on its own. Together they give you a clearer picture of who is coming to site.</p>
    </div>
    <div class="bento reveal">
      <article class="product">
        <span class="num">01</span>
        <svg viewBox="0 0 52 52" aria-hidden="true"><path d="M26 4l18 7v14c0 11-8 19-18 23C16 44 8 36 8 25V11z"/><path d="M17 26l7 7 12-14"/></svg>
        <h3>Compliance evidence</h3>
        <p>Right to Work, CSCS, trade cards and training certificates, with the evidence of each check recorded and expiry dates tracked.</p>
      </article>
      <article class="product">
        <span class="num">02</span>
        <svg viewBox="0 0 52 52" aria-hidden="true"><path d="M8 40V14h30v26z"/><path d="M14 22h18M14 29h12"/><path d="M34 44l4-8 8-12-4-3-8 12z"/></svg>
        <h3>Skilled operatives</h3>
        <p>Experience shown through work history, references and supervisor feedback on the specific work, such as cutting in on satinwood or spray finishing.</p>
      </article>
      <article class="product">
        <span class="num">03</span>
        <svg viewBox="0 0 52 52" aria-hidden="true"><path d="M6 44h40"/><path d="M12 44V30M22 44V20M32 44V26M42 44V10"/></svg>
        <h3>Reliability record</h3>
        <p>Attendance, performance evidence and whether contractors would use the worker again, built from real jobs and added to after every one.</p>
      </article>
      <article class="product">
        <span class="num">04</span>
        <svg viewBox="0 0 52 52" aria-hidden="true"><circle cx="26" cy="28" r="17"/><path d="M26 17v11l8 5"/><path d="M20 6h12"/></svg>
        <h3>Matching and deployment</h3>
        <p>We match against your actual job and site requirements, confirm the names with you, and keep a record after deployment.</p>
      </article>
      <article class="product">
        <span class="num">05</span>
        <svg viewBox="0 0 52 52" aria-hidden="true"><circle cx="16" cy="18" r="6"/><circle cx="36" cy="18" r="6"/><circle cx="26" cy="36" r="6"/><path d="M20 22l4 8M32 22l-4 8M22 18h8"/></svg>
        <h3>Work-ready crews</h3>
        <p>Where people have genuinely worked together before, we can put them forward as a crew, with the cards and training you asked for checked.</p>
      </article>
    </div>
  </div>
</section>

<!-- ====== What we check (static) ====== -->
<section class="seq nopin" id="checks" aria-labelledby="seq-h">
  <div class="seq-stage">
    <div class="seq-g">
      <div class="seq-text">
        <p class="ey">What we check</p>
        <h2 id="seq-h">Six things we check before anyone is put forward</h2>
        <p class="lede">CARD_CHECK</p>
        <ol class="gates">
          <li><span class="g">01</span><div><strong>Right to Work</strong><p>Right to Work evidence is checked and recorded before a worker is put forward.</p></div></li>
          <li><span class="g">02</span><div><strong>CSCS card</strong><p>Card type, status and expiry are checked against the CSCS source where available, and the evidence is recorded.</p></div></li>
          <li><span class="g">03</span><div><strong>Trade cards and qualifications</strong><p>NVQ, City &amp; Guilds, IPAF, PASMA and similar, checked with the awarding body where a service exists.</p></div></li>
          <li><span class="g">04</span><div><strong>Training certificates</strong><p>Asbestos awareness, working at height, manual handling and anything your site adds. Out-of-date training is flagged.</p></div></li>
          <li><span class="g">05</span><div><strong>Experience and work history</strong><p>Previous work, references and supervisor feedback, so "experienced" is something you can see.</p></div></li>
          <li><span class="g">06</span><div><strong>Expiry dates</strong><p>Every card and certificate is tracked, with reminders at 60 and 30 days. Where current evidence is mandatory for the job or site, expired evidence means the worker is not put forward until it has been renewed.</p></div></li>
        </ol>
      </div>
      <div class="sheet" role="group" aria-label="Example Worker Passport, illustrative">
        <div class="sheet-b">
          <div class="sheet-top">
            <span class="avatar" aria-hidden="true">JC</span>
            <div><strong>J. Carter</strong><span class="pid">Painter and decorator</span></div>
            <span class="tag">Illustrative<br>not a real worker</span>
          </div>
          <ul class="sp">
            <li><span class="n">01</span><div><b>Right to Work</b><small>Evidence recorded</small></div><span class="chip"></span></li>
            <li><span class="n">02</span><div><b>CSCS card</b><small>Type, status and expiry</small></div><span class="chip"></span></li>
            <li><span class="n">03</span><div><b>Trade cards and qualifications</b><small>NVQ, City &amp; Guilds, IPAF, PASMA</small></div><span class="chip"></span></li>
            <li><span class="n">04</span><div><b>Training certificates</b><small>Asbestos, height, manual handling</small></div><span class="chip"></span></li>
            <li><span class="n">05</span><div><b>Experience and work history</b><small>References and supervisor feedback</small></div><span class="chip"></span></li>
            <li><span class="n">06</span><div><b>Expiry dates</b><small>Reminders at 60 and 30 days</small></div><span class="chip"></span></li>
          </ul>
          <div class="sheet-foot">
            <div class="score"><b>46/47</b><span>Shifts attended</span></div>
            <span class="stamp">Site ready</span>
          </div>
        </div>
      </div>
    </div>
    <div class="seq-g" style="margin-top:28px;"><p class="disclaimer">PASSPORT_NOTE</p></div>
  </div>
</section>

<!-- ====== How it works ====== -->
<section class="section" id="how-it-works">
  <div class="wrap">
    <div class="section-head reveal">
      <p class="ey">How it works</p>
      <h2>Three steps, from a request to a crew on site</h2>
    </div>
    <div class="how-steps">

      <div class="feature reveal">
        <div class="feature-visual">
          <div class="photo">
            <img src="images/crew-surrey-school.jpg" alt="A crew of seven painters and decorators on a school refurbishment site in Surrey" width="1400" height="788" loading="lazy">
          </div>
          <div class="float">
            <div class="card">
              <span class="illustrative">Illustrative example</span>
              <div class="query">6 painters, 3 decorators, 1 supervisor. Guildford, Monday, education site</div>
              <div class="result">
                <span class="n">10 of 10</span>
                <span class="s">Illustrative shortlist: all ten hold the cards and training the site asked for</span>
              </div>
            </div>
          </div>
        </div>
        <div>
          <span class="step-label">Step 1</span>
          <h3>You send a workforce request</h3>
          <p class="lede">Tell us the trade, how many people, the site location, the start date, how long you need them and any cards or training that are essential.</p>
          <ol class="steps">
            <li><div><strong>A short form, read by a person</strong><p>It takes a couple of minutes. We aim to respond within one business day.</p></div></li>
            <li><div><strong>Urgent needs are flagged</strong><p>Mark the request as urgent and it is picked up first. A phone and WhatsApp line for urgent requests is being set up.</p></div></li>
          </ol>
        </div>
      </div>

      <div class="feature reverse reveal">
        <div class="feature-visual">
          <div class="photo">
            <img src="images/verify-cscs-card-check.jpg" alt="CSCS card being scanned at a construction site turnstile" width="1200" height="900" loading="lazy">
          </div>
          <div class="float">
            <div class="card">
              <span class="illustrative">Illustrative example, not a real worker</span>
              <div class="passport-head">
                <span class="avatar" aria-hidden="true">JC</span>
                <div>
                  <strong>J. Carter</strong>
                  <div class="sub">Painter and decorator</div>
                </div>
              </div>
              <div class="pills">
                <span class="pill">&#10003; Right to Work</span>
                <span class="pill">&#10003; CSCS</span>
                <span class="pill">&#10003; Working at height</span>
                <span class="pill">&#10003; Asbestos awareness</span>
              </div>
              <div class="metrics">
                <div class="metric"><span class="n">46/47</span><span class="s">Shifts attended</span></div>
                <div class="metric"><span class="n">9 of 10</span><span class="s">Would use again</span></div>
              </div>
              <p class="foot">PASSPORT_NOTE</p>
            </div>
          </div>
        </div>
        <div>
          <span class="step-label">Step 2</span>
          <h3>We check the evidence and match</h3>
          <p class="lede">Each worker has a Worker Passport. We match it against what your job and site actually require.</p>
          <ol class="steps">
            <li><div><strong>Compliance evidence first</strong><p>Anyone with an expired card or lapsed training isn't put forward for work that needs it.</p></div></li>
            <li><div><strong>Then experience and record</strong><p>Work history, supervisor feedback, attendance, and whether the people have worked together before.</p></div></li>
            <li><div><strong>Confirmed with you</strong><p>Names, rates and start time are agreed with you before anyone travels.</p></div></li>
          </ol>
        </div>
      </div>

      <div class="feature reveal">
        <div class="feature-visual">
          <div class="photo">
            <img src="images/deploy-dawn-van-hampshire.jpg" alt="A decorator stepping out of a van at dawn on a site in Hampshire" width="1400" height="788" loading="lazy">
          </div>
        </div>
        <div>
          <span class="step-label">Step 3</span>
          <h3>We deploy, and keep the record</h3>
          <p class="lede">After deployment, attendance and feedback go on each worker's record. That record is what you see next time.</p>
          <ol class="tl">
            <li><span class="time">Reported</span><strong>No-show or late cancellation</strong><p>You tell us through the dashboard or by phone. It goes on the worker's record.</p></li>
            <li><span class="time">Our aim: 60 min</span><strong>Replacement search begins</strong><p>Same trade and area, cards in date, within reach of the site.</p></li>
            <li><span class="time">Then</span><strong>We tell you who we propose</strong><p>Workers who have worked with the rest of the crew before come first.</p></li>
          </ol>
          <div class="guarantee">
            <strong>Our 60-minute aim</strong>
            <p>SIXTY That's a commitment to start the search, not a guarantee that a replacement will be found.</p>
          </div>
        </div>
      </div>

    </div>
  </div>
</section>

<!-- ====== Founder ====== -->
<section class="section sand" id="founder">
  <div class="wrap">
    <div class="founder">
      <div class="reveal">
        <p class="ey">Why we exist</p>
        <h2>Built by someone who has dealt with the problem</h2>
        <div class="founder-img"><img src="images/founder-marizilena.jpg" alt="Marizilena Silva Fortes, Founder and Director of PRJGENUI Workforce" width="765" height="1024" loading="lazy"></div>
      </div>
      <div class="reveal">
        <p class="lede">PRJGENUI Workforce grew out of Marizilena Silva Fortes's experience managing construction workers and subcontractors, and dealing with the compliance checks and last-minute problems that come with them.</p>
        <p>On real projects the same things kept happening. Someone didn't turn up, a card had expired, or a worker described as experienced couldn't do the job. Most of it could have been avoided if the right evidence had been in one place before the worker arrived.</p>
        <p>That is what we do. We bring the evidence together, match it to the job, and keep a record afterwards.</p>
        <div class="sig"><strong>Marizilena Silva Fortes</strong>Founder and Director, PRJGENUI Workforce Ltd.</div>
      </div>
    </div>
  </div>
</section>

<!-- ====== What to ask any supplier ====== -->
<section class="section" id="ask">
  <div class="wrap">
    <div class="section-head reveal">
      <p class="ey">Before you book anyone</p>
      <h2>What to ask any supplier, us included</h2>
      <p class="lede">These questions are worth asking whoever you use. Here is how we answer them.</p>
    </div>
    <div class="ask reveal">
      <div class="row"><h3>Are cards checked at source, or just looked at?</h3><p>CARD_CHECK</p></div>
      <div class="row"><h3>Can you show attendance and would-use-again evidence?</h3><p>Yes. Each Worker Passport carries a reliability record built from real jobs.</p></div>
      <div class="row"><h3>Have the "crew" actually worked together?</h3><p>We only call a group a crew when its members genuinely have. Otherwise we say they are individuals.</p></div>
      <div class="row"><h3>Will I know who is turning up before they travel?</h3><p>Yes. Names, rates and start time are agreed with you first.</p></div>
      <div class="row"><h3>What happens if someone doesn't show?</h3><p>SIXTY</p></div>
    </div>
  </div>
</section>

<!-- ====== Coverage ====== -->
<section class="section sage" id="coverage">
  <div class="wrap">
    <div class="coverage">
      <div class="reveal">
        <p class="ey">Coverage</p>
        <h2>Hampshire, Surrey and the South East</h2>
        <p class="lede" style="margin-top:20px;">The pilot is local on purpose. A small number of contractors, a tight area, and records that get richer with every job.</p>
        <p class="coverage-note">Not in one of these areas yet? Tell us where you are on the request form and we'll let you know when we get there.</p>
        <div class="radar" aria-hidden="true">
          <svg viewBox="0 0 300 300" focusable="false">
            <circle cx="150" cy="150" r="140"/><circle cx="150" cy="150" r="100" opacity=".7"/><circle cx="150" cy="150" r="60" opacity=".5"/><circle cx="150" cy="150" r="24" opacity=".4"/>
            <path d="M10 150h280M150 10v280" opacity=".35"/>
            <g class="sweep"><path d="M150 150V10"/><path d="M150 150V10A140 140 0 0 1 249 51Z" fill="currentColor" opacity=".13" stroke="none"/></g>
            <circle class="ring" cx="150" cy="150" r="140" fill="none"/>
            <circle class="ping" cx="150" cy="150" r="6"/>
          </svg>
        </div>
      </div>
      <div class="areas-grid reveal">
        <div class="area"><h4>Surrey</h4><ul><li>Guildford</li><li>Woking</li><li>Weybridge</li><li>Farnham</li><li>Reigate</li><li>Staines</li></ul></div>
        <div class="area"><h4>Hampshire</h4><ul><li>Farnborough</li><li>Aldershot</li><li>Basingstoke</li><li>Winchester</li><li>Andover</li><li>Fleet</li></ul></div>
        <div class="area"><h4>Berkshire and beyond</h4><ul><li>Reading</li><li>Bracknell</li><li>Wokingham</li><li>Newbury</li><li>South West London</li><li>Elsewhere by request</li></ul></div>
      </div>
    </div>
  </div>
</section>

<!-- ====== Pilot band ====== -->
<section class="section tight">
  <div class="wrap">
    <div class="pilot reveal">
      <div class="pilot-img">
        <img src="images/team-briefing-dawn.jpg" alt="Team of decorators having a morning briefing on a construction site in Hampshire" width="1400" height="933" loading="lazy">
      </div>
      <div class="pilot-content">
        <p class="ey">Pilot</p>
        <h2>Now taking on our first pilot partners</h2>
        <p>We're beginning with a small number of contractors across Hampshire, Surrey and the South East. If that's you, we'd rather have a conversation than send you a brochure.</p>
        <div class="actions"><a href="request.html" class="btn btn-gold">Request Workers or a Crew</a></div>
      </div>
    </div>
  </div>
</section>

<!-- ====== FAQ ====== -->
<section class="section sage" id="faq">
  <div class="wrap">
    <div class="faq-grid">
      <div class="reveal">
        <p class="ey">FAQ</p>
        <h2>Questions we get asked</h2>
        <p class="lede" style="margin-top:20px;">Straight answers for contractors and for workers. Where something depends on the job, we say so.</p>
        <p class="small muted" style="margin-top:20px;">Can't find what you're looking for? <a href="contact.html">Send us a message</a>.</p>
      </div>
      <div class="faq reveal">
FAQ_HTML      </div>
    </div>
  </div>
</section>

<section class="cta-band" id="contact">
  <div class="wrap">
    <div class="cta-in">
      <div>
        <h2>Tell us what you need</h2>
        <p>It's a short form and a person reads every one. We aim to respond within one business day.</p>
      </div>
      <a href="request.html" class="btn btn-navy">Request Workers or a Crew</a>
    </div>
  </div>
</section>
'''


STATUS = '<p class="form-status" role="alert" hidden></p>'


def fill(s):
    return (s.replace('CARD_CHECK', CARD_CHECK).replace('PASSPORT_NOTE', PASSPORT_NOTE)
             .replace('SIXTY', SIXTY).replace('FAQ_HTML', FAQ_HTML).replace('STATUS', STATUS).replace('EMAIL', EMAIL))


page('index.html',
     'PRJGENUI Workforce | Verified workers and work-ready crews for contractors in the South East',
     'PRJGENUI Workforce helps contractors across Hampshire, Surrey and the South East request, check and manage skilled operatives and work-ready crews. Right to Work, CSCS, training and work history in one record.',
     'PRJGENUI Workforce | Workforce certainty, not just CVs',
     'Request, check and manage skilled operatives and work-ready crews across Hampshire, Surrey and the South East.',
     fill(INDEX_MAIN),
     [ld_org(), FAQ_LD])

# ---------------------------------------------------------------- forms

FORM_TOP = '''<form class="form" id="NAME" action="https://api.web3forms.com/submit" method="POST" data-redirect="thanks.html">
          <!-- access_key is filled at runtime by script.js from secrets.js (deployed, not committed) -->
          <input type="hidden" name="access_key" value="">
          <input type="hidden" name="subject" value="SUBJECT">
          <input type="hidden" name="from_name" value="PRJGENUI Workforce website">
          <input type="hidden" name="redirect" value="SITE/thanks.html">
          <input type="checkbox" name="botcheck" class="hp" tabindex="-1" autocomplete="off">
'''


def form_top(name, subject):
    return (FORM_TOP.replace('NAME', name).replace('SUBJECT', subject)
            .replace('SITE', SITE))



REQUEST_MAIN = page_hero(
    'Contractors', 'Request Workers or a Crew',
    "Tell us what the job needs. We'll check the evidence, match against your site requirements and come back to you. We aim to respond within one business day.",
    'images/crew-surrey-school.jpg',
    'A crew of painters and decorators on a school refurbishment site in Surrey') + '''
<section class="section" id="request">
  <div class="wrap">
    <div class="contact">
      <div class="contact-copy reveal">
        <h2>What happens next</h2>
        <ol class="next">
          <li><span>1</span><div><strong>You send the request.</strong> Trade, numbers, location, start date, duration and essential cards or training.</div></li>
          <li><span>2</span><div><strong>We check and match.</strong> We match against what the job and site actually require, and check the evidence.</div></li>
          <li><span>3</span><div><strong>We come back to you.</strong> We aim to respond within one business day. Urgent requests are picked up first.</div></li>
          <li><span>4</span><div><strong>You confirm.</strong> Nobody travels until names, rates and start time are agreed with you.</div></li>
        </ol>
        <p class="side-note"><strong>Need someone urgently?</strong> Tick the urgent box and add a phone number so we can call you. A phone and WhatsApp line for urgent requests is being set up.</p>
      </div>
      <div class="reveal">
        ''' + form_top('requestForm', 'New workforce request') + '''
          <div class="f">
            <label for="kind">What do you need?</label>
            <select id="kind" name="Request type" required>
              <option value="" selected disabled>Select one</option>
              <option>Individual workers</option>
              <option>A crew</option>
              <option>Not sure yet</option>
            </select>
          </div>
          <div class="f-row">
            <div class="f">
              <label for="trade">Trade or role</label>
              <input id="trade" name="Trade or role" type="text" placeholder="e.g. painter and decorator" required>
            </div>
            <div class="f">
              <label for="count">How many?</label>
              <input id="count" name="Number of people" type="number" min="1" inputmode="numeric" required>
            </div>
          </div>
          <div class="f">
            <label for="loc">Site location</label>
            <input id="loc" name="Site location" type="text" placeholder="Town and postcode" required>
          </div>
          <div class="f-row">
            <div class="f">
              <label for="start">Start date</label>
              <input id="start" name="Start date" type="date" required>
            </div>
            <div class="f">
              <label for="dur">How long for?</label>
              <input id="dur" name="Duration" type="text" placeholder="e.g. 3 weeks, ongoing" required>
            </div>
          </div>
          <div class="f">
            <label for="cards">Essential cards and training <span class="opt">(optional)</span></label>
            <textarea id="cards" name="Essential cards and training" placeholder="e.g. CSCS blue card, working at height, asbestos awareness, site induction"></textarea>
          </div>
          <div class="consent">
            <input id="urgent" type="checkbox" name="Urgent" value="Yes">
            <label for="urgent">This is urgent. We need to start within a couple of days.</label>
          </div>
          <div class="f">
            <label for="name">Your name</label>
            <input id="name" name="Name" type="text" autocomplete="name" required>
          </div>
          <div class="f">
            <label for="company">Company</label>
            <input id="company" name="Company" type="text" autocomplete="organization" required>
          </div>
          <div class="f-row">
            <div class="f">
              <label for="email">Email</label>
              <input id="email" name="Email" type="email" autocomplete="email" required>
            </div>
            <div class="f">
              <label for="phone">Phone <span class="opt">(for urgent)</span></label>
              <input id="phone" name="Phone" type="tel" autocomplete="tel">
            </div>
          </div>
          <div class="f">
            <label for="more">Anything else? <span class="opt">(optional)</span></label>
            <textarea id="more" name="Anything else" placeholder="Site type, working hours, access, anything that would help"></textarea>
          </div>
          <button type="submit" class="btn btn-gold">Send request</button>
          STATUS
          <p class="form-note">We only use your details to reply to you and handle your request. We don't add you to a marketing list or pass your details to anyone else. See our <a href="privacy.html">privacy policy</a>.</p>
        </form>
      </div>
    </div>
  </div>
</section>
'''

page('request.html',
     'Request Workers or a Crew | PRJGENUI Workforce',
     'Send a workforce request: trade, how many, site location, start date, duration and essential cards or training. We aim to respond within one business day.',
     'Request Workers or a Crew | PRJGENUI Workforce',
     'Tell us what the job needs. We check the evidence, match against your site requirements and come back to you.',
     fill(REQUEST_MAIN), [{"@context": "https://schema.org", "@type": "ContactPage", "name": "Request Workers or a Crew",
                    "url": SITE + "/request.html", "mainEntity": ORG}])

WORKERS_MAIN = page_hero(
    'Workers', 'Register as a Worker',
    "Register once and your cards, training, experience and work history sit in one Worker Passport. There is no fee to join and no fee to be matched.",
    'images/team-briefing-dawn.jpg',
    'A team of decorators having a morning briefing on a construction site in Hampshire') + '''
<section class="section sage" id="passport">
  <div class="wrap">
    <div class="section-head reveal">
      <p class="ey">Worker Passport</p>
      <h2>One place for everything a contractor wants to see</h2>
      <p class="lede">PASSPORT_NOTE</p>
    </div>
    <div class="grid-3 reveal">
      <div class="tile"><h3>What goes in it</h3><p>Right to Work evidence, CSCS and trade cards, qualifications, training certificates, experience and work history.</p></div>
      <div class="tile"><h3>What it builds</h3><p>A reliability record: attendance, performance evidence and whether contractors would use you again. It grows with every job.</p></div>
      <div class="tile"><h3>Who sees it</h3><p>Contractors who are considering you for a job. See the <a href="privacy.html">privacy policy</a> for what is shared and how long it is kept.</p></div>
    </div>
  </div>
</section>

<section class="section" id="register">
  <div class="wrap">
    <div class="contact">
      <div class="contact-copy reveal">
        <h2>Tell us about you</h2>
        <p class="lede" style="margin-top:18px;">This starts your Worker Passport. It takes a few minutes.</p>
        <ol class="next">
          <li><span>1</span><div><strong>You register.</strong> The form on this page.</div></li>
          <li><span>2</span><div><strong>We get in touch.</strong> We aim to respond within one business day to talk through your experience.</div></li>
          <li><span>3</span><div><strong>We check your evidence.</strong> We'll ask for your Right to Work evidence, cards and certificates and check them where a verification service is available.</div></li>
          <li><span>4</span><div><strong>We match you to work.</strong> By trade, area and record.</div></li>
        </ol>
        <p class="side-note"><strong>Please don't send ID or card photos through this form.</strong> We'll tell you how to share documents safely when we speak.</p>
      </div>
      <div class="reveal">
        ''' + form_top('workerForm', 'New worker registration') + '''
          <div class="f">
            <label for="wname">Full name</label>
            <input id="wname" name="Name" type="text" autocomplete="name" required>
          </div>
          <div class="f-row">
            <div class="f">
              <label for="wphone">Phone</label>
              <input id="wphone" name="Phone" type="tel" autocomplete="tel" required>
            </div>
            <div class="f">
              <label for="wemail">Email <span class="opt">(optional)</span></label>
              <input id="wemail" name="Email" type="email" autocomplete="email">
            </div>
          </div>
          <div class="f-row">
            <div class="f">
              <label for="wtrade">Main trade</label>
              <input id="wtrade" name="Main trade" type="text" placeholder="e.g. painter and decorator" required>
            </div>
            <div class="f">
              <label for="wexp">Experience</label>
              <select id="wexp" name="Experience" required>
                <option value="" selected disabled>Select one</option>
                <option>Under 2 years</option>
                <option>2 to 5 years</option>
                <option>5 to 10 years</option>
                <option>Over 10 years</option>
              </select>
            </div>
          </div>
          <div class="f">
            <label for="wskills">Other skills <span class="opt">(optional)</span></label>
            <input id="wskills" name="Other skills" type="text" placeholder="e.g. spray finishing, wallpapering, supervising">
          </div>
          <div class="f-row">
            <div class="f">
              <label for="wloc">Where you live</label>
              <input id="wloc" name="Home town or postcode" type="text" placeholder="Town or postcode" required>
            </div>
            <div class="f">
              <label for="wtravel">How far will you travel?</label>
              <select id="wtravel" name="Travel distance" required>
                <option value="" selected disabled>Select one</option>
                <option>Up to 10 miles</option>
                <option>Up to 25 miles</option>
                <option>Up to 50 miles</option>
                <option>Further, if the job suits</option>
              </select>
            </div>
          </div>
          <div class="f-row">
            <div class="f">
              <label for="wrtw">Right to Work in the UK</label>
              <select id="wrtw" name="Right to Work in the UK" required>
                <option value="" selected disabled>Select one</option>
                <option>Yes</option>
                <option>Not sure</option>
                <option>No</option>
              </select>
            </div>
            <div class="f">
              <label for="wcscs">CSCS card</label>
              <select id="wcscs" name="CSCS card" required>
                <option value="" selected disabled>Select one</option>
                <option>Green</option>
                <option>Blue</option>
                <option>Gold</option>
                <option>Black</option>
                <option>White</option>
                <option>Other</option>
                <option>I don't have one</option>
              </select>
            </div>
          </div>
          <fieldset>
            <legend>Training you hold <span class="opt" style="text-transform:none;font-weight:500;letter-spacing:0;">(tick any)</span></legend>
            <div class="chk">
              <label><input type="checkbox" name="Training: working at height" value="Yes"> Working at height</label>
              <label><input type="checkbox" name="Training: asbestos awareness" value="Yes"> Asbestos awareness</label>
              <label><input type="checkbox" name="Training: manual handling" value="Yes"> Manual handling</label>
              <label><input type="checkbox" name="Training: IPAF" value="Yes"> IPAF</label>
              <label><input type="checkbox" name="Training: PASMA" value="Yes"> PASMA</label>
              <label><input type="checkbox" name="Training: first aid" value="Yes"> First aid</label>
            </div>
          </fieldset>
          <div class="f">
            <label for="wavail">When can you start? <span class="opt">(optional)</span></label>
            <input id="wavail" name="Availability" type="text" placeholder="e.g. now, from 3 March, weekends only">
          </div>
          <div class="f">
            <label for="wmore">Anything else? <span class="opt">(optional)</span></label>
            <textarea id="wmore" name="Anything else" placeholder="Types of site you've worked on, supervisors who would vouch for you"></textarea>
          </div>
          <div class="consent">
            <input id="wconsent" type="checkbox" name="Consent" value="Yes" required>
            <label for="wconsent">I agree that PRJGENUI Workforce can use these details to set up my Worker Passport and contact me about work. I've read the <a href="privacy.html">privacy policy</a>.</label>
          </div>
          <button type="submit" class="btn btn-gold">Register as a Worker</button>
          STATUS
          <p class="form-note">No fee to join and no fee to be matched. We don't pass your details to anyone without telling you.</p>
        </form>
      </div>
    </div>
  </div>
</section>
'''

page('workers.html',
     'Register as a Worker | PRJGENUI Workforce',
     'Register as a worker with PRJGENUI Workforce and build your Worker Passport: cards, training, experience and a reliability record in one place. No fee to join.',
     'Register as a Worker | PRJGENUI Workforce',
     'Build a Worker Passport that shows your cards, training, experience and reliability record. No fee to join.',
     fill(WORKERS_MAIN), [{"@context": "https://schema.org", "@type": "WebPage", "name": "Register as a Worker",
                    "url": SITE + "/workers.html", "publisher": ORG}])

# ---------------------------------------------------------------- about

ABOUT_MAIN = page_hero(
    'About', 'Why PRJGENUI exists',
    "PRJGENUI Workforce grew out of Marizilena Silva Fortes's experience managing construction workers and subcontractors, and dealing with the compliance checks and last-minute problems that come with them.",
    'images/about-hero-team.jpg',
    'Two PRJGENUI Workforce team members reviewing site reports in their office') + '''
<section class="section sage">
  <div class="wrap">
    <div class="section-head reveal">
      <h2>The problem we set out to fix</h2>
      <p class="lede">Most recruitment stops at finding someone who is free. Before a contractor lets a worker on site, they need to know a good deal more than that.</p>
    </div>
    <div class="reveal">
      <div class="grid-2">
        <div>
          <h3>What goes wrong</h3>
          <p>Workers don't turn up, or cancel at the last minute. Cards and training have expired or are missing. People described as experienced can't do the job. The workers who arrive aren't the ones that were agreed, and a "crew" turns out to be strangers.</p>
        </div>
        <div>
          <h3>What we do about it</h3>
          <p>We bring Right to Work, CSCS, training, experience and work history together in one Worker Passport. We match it against what the job actually needs. We keep a reliability record after deployment, so the next contractor sees what really happened.</p>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head reveal">
      <h2>How we work</h2>
    </div>
    <div class="pairs reveal">
      <div class="product-row"><div class="num">01</div><div><h3>Compliance evidence comes first</h3><p>Nobody with an expired card or lapsed training is put forward for work that needs it. We check that before anything else.</p></div></div>
      <div class="product-row"><div class="num">02</div><div><h3>Reliability is recorded</h3><p>Every job a worker does, or doesn't turn up for, goes on their record. It belongs to the worker and is added to after every job.</p></div></div>
      <div class="product-row"><div class="num">03</div><div><h3>A crew means people who have worked together</h3><p>We only call a group a crew when its members genuinely have. Otherwise we say so.</p></div></div>
      <div class="product-row"><div class="num">04</div><div><h3>A quick start on replacements</h3><p>SIXTY That is a commitment to start the search, not a promise that a replacement will be found.</p></div></div>
    </div>
  </div>
</section>

<section class="section sage">
  <div class="wrap">
    <div class="section-head reveal">
      <h2>What we check</h2>
      <p class="lede">CARD_CHECK</p>
    </div>
    <div class="reveal">
      <div class="grid-3">
        <div class="tile"><h4>Right to Work</h4><p>Evidence checked and recorded before a worker is put forward.</p></div>
        <div class="tile"><h4>CSCS cards</h4><p>Type, status and expiry checked at source where a service is available.</p></div>
        <div class="tile"><h4>Qualifications</h4><p>NVQ, City &amp; Guilds, IPAF and PASMA, with expiry dates recorded.</p></div>
        <div class="tile"><h4>Training certificates</h4><p>Asbestos awareness, working at height, manual handling and site-specific training.</p></div>
        <div class="tile"><h4>Work history</h4><p>Previous work, references and supervisor feedback.</p></div>
        <div class="tile"><h4>Reliability record</h4><p>Attendance, performance evidence and whether contractors would use the worker again.</p></div>
      </div>
      <p class="small muted" style="margin-top:24px;">We're working towards CHAS, SafeContractor, Constructionline and REC membership. We'll add each one here once it's confirmed. We don't show badges we don't hold.</p>
      <p class="disclaimer">PASSPORT_NOTE</p>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head reveal">
      <h2>Who is behind it</h2>
    </div>
    <div class="grid-split reveal">
      <div class="tile">
        <img class="person" src="images/founder-marizilena.jpg" alt="Marizilena Silva Fortes, Founder and Director of PRJGENUI Workforce" width="765" height="1024" loading="lazy">
        <h4>Marizilena Silva Fortes</h4>
        <p class="muted" style="margin-top:2px;">Founder and Director</p>
        <p>Marizilena has managed construction workers and subcontractors, and dealt with the compliance and last-minute problems that come with them. PRJGENUI is built around the things she kept having to fix on site.</p>
      </div>
      <div class="tile">
        <h4>Company details</h4>
        <ul class="details-list">
          <li><strong>Registered name</strong>PRJGENUI Workforce Ltd.</li>
          <li><strong>Company number</strong>13205257, registered in England and Wales</li>
          <li><strong>Incorporated</strong>February 2021</li>
          <li><strong>Registered office</strong>124 City Road, London EC1V 2NX</li>
          <li><strong>Where we work</strong>Hampshire, Surrey and the South East</li>
        </ul>
      </div>
    </div>
  </div>
</section>

''' + cta_band('Talk to us',
               "We're taking on our first pilot partners across Hampshire, Surrey and the South East. Tell us what you need and we'll come back to you.",
               'request.html', 'Request Workers or a Crew')

ABOUT_MAIN = fill(ABOUT_MAIN)
page('about.html',
     'About | PRJGENUI Workforce',
     'PRJGENUI Workforce grew out of first-hand experience managing construction workers and subcontractors. Find out who we are, what we check and how we work.',
     'About PRJGENUI Workforce',
     'A construction workforce company founded by Marizilena Silva Fortes, built around the problems contractors face on site.',
     ABOUT_MAIN, [{"@context": "https://schema.org", "@type": "AboutPage", "name": "About PRJGENUI Workforce",
                  "url": SITE + "/about.html", "mainEntity": ORG}])

# ---------------------------------------------------------------- contact

CONTACT_MAIN = page_hero(
    'Contact', 'Get in touch',
    "For general questions, use the form below. We aim to respond to general enquiries within one business day.",
    'images/contact-hero-office.jpg',
    'PRJGENUI Workforce office reception area with a map of Surrey and Hampshire on the wall') + '''
<section class="section" id="contact">
  <div class="wrap">
    <div class="contact">
      <div class="contact-copy reveal">
        <h2>General enquiries</h2>
        <p class="lede" style="margin-top:18px;">Questions about how we work, the pilot or anything else.</p>
        <p class="side-note"><strong>Need workers or a crew?</strong> Use the <a href="request.html">request form</a>, which asks for the details we need to get started.<br><br><strong>Looking for work?</strong> Go to <a href="workers.html">Register as a Worker</a>.</p>
      </div>
      <div class="reveal">
        ''' + form_top('contactForm', 'New general enquiry') + '''
          <div class="f">
            <label for="need">What is it about?</label>
            <select id="need" name="Enquiry about" required>
              <option value="" selected disabled>Select one</option>
              <option>A general question</option>
              <option>The pilot</option>
              <option>Working with us</option>
              <option>Something else</option>
            </select>
          </div>
          <div class="f">
            <label for="name">Name</label>
            <input id="name" name="Name" type="text" autocomplete="name" required>
          </div>
          <div class="f">
            <label for="company">Company <span class="opt">(if applicable)</span></label>
            <input id="company" name="Company" type="text" autocomplete="organization">
          </div>
          <div class="f-row">
            <div class="f">
              <label for="email">Email</label>
              <input id="email" name="Email" type="email" autocomplete="email" required>
            </div>
            <div class="f">
              <label for="phone">Phone <span class="opt">(optional)</span></label>
              <input id="phone" name="Phone" type="tel" autocomplete="tel">
            </div>
          </div>
          <div class="f">
            <label for="details">Your message</label>
            <textarea id="details" name="Message" required></textarea>
          </div>
          <button type="submit" class="btn btn-gold">Send</button>
          STATUS
          <p class="form-note">We only use your details to reply to you. We don't add you to a marketing list or pass your details to anyone else.</p>
        </form>
      </div>
    </div>
  </div>
</section>

<section class="section sage">
  <div class="wrap">
    <div class="section-head reveal">
      <h2>Other ways to reach us</h2>
    </div>
    <div class="grid-3 reveal" style="gap:24px;">
      <div class="tile"><h3>Email</h3><p><a href="mailto:EMAIL">EMAIL</a></p></div>
      <div class="tile"><h3>Phone and WhatsApp</h3><p>A business line for urgent requests is being set up. Until then, use the urgent box on the request form or email us.</p></div>
      <div class="tile"><h3>Where we work</h3><p>Hampshire, Surrey and the South East, including Guildford, Woking, Farnborough, Basingstoke, Winchester and Reading. <a href="index.html#coverage">See the full list</a>.</p></div>
    </div>
  </div>
</section>
'''

page('contact.html',
     'Contact | PRJGENUI Workforce',
     'Get in touch with PRJGENUI Workforce. We aim to respond to general enquiries within one business day.',
     'Contact PRJGENUI Workforce',
     'General enquiries about PRJGENUI Workforce. We aim to respond within one business day.',
     fill(CONTACT_MAIN), [{"@context": "https://schema.org", "@type": "ContactPage", "name": "Contact PRJGENUI Workforce",
                    "url": SITE + "/contact.html", "mainEntity": ORG}])

# ---------------------------------------------------------------- terms, privacy, thanks


def swap_chrome(html):
    html, n = re.subn(r'<a class="skip".*?(?=<main id="main")', lambda m: TOP, html, count=1, flags=re.S)
    if n != 1:
        sys.exit('top chrome not found')
    html, n = re.subn(r'</main>\s*<footer.*?</html>\s*', lambda m: '</main>\n\n' + FOOTER, html, count=1, flags=re.S)
    if n != 1:
        sys.exit('footer chrome not found')
    return re.sub(r'\?v=\d+', '?v=' + V, html)


terms = swap_chrome(read('terms.html'))
for old, new in [
    ('build reliability scores, and supply crews to painting and decorating contractors. We also build Workforce Passports for individual workers.',
     'keep reliability records, and put forward workers and crews to painting and decorating contractors. We also build Worker Passports for individual workers. ' + PASSPORT_NOTE),
    ('The Workforce Passport belongs to the worker.', 'The Worker Passport belongs to the worker.'),
    ('The Trust Score depends on honest feedback.', 'The reliability record depends on honest feedback.'),
    ('<h3>6. The 60-minute replacement guarantee</h3>', '<h3>6. Replacement searches</h3>'),
    ("<p>If a replacement search does not start within 60 minutes of a confirmed no-show, the day's supply charge for the absent worker is waived. This applies to confirmed no-shows reported through the dashboard or by phone.</p>",
     '<p>' + SIXTY + ' This is a commitment to begin the search. It is not a guarantee that a replacement will be found or will be available.</p>'),
]:
    terms = soft_replace(terms, old, new, 'terms')
write('terms.html', terms)

privacy = swap_chrome(read('privacy.html'))
for old, new in [
    ('build reliability scores and supply crews to painting and decorating contractors.',
     'keep reliability records and put forward workers and crews to painting and decorating contractors.'),
    ('build Trust Scores from what happened on real assignments', 'build reliability records from what happened on real assignments'),
    ("compliance status and Trust Score.", 'compliance status and reliability record.'),
    ('We share information with issuing bodies such as CSCS and awarding bodies for verification purposes.',
     'We share information with verification services and awarding bodies, such as CSCS, for verification purposes.'),
    ('Worker passports are kept', 'Worker Passports are kept'),
    ('Assignment history and Trust Score data', 'Assignment history and reliability record data'),
]:
    privacy = soft_replace(privacy, old, new, 'privacy')
write('privacy.html', privacy)

thanks = re.sub(r'\?v=\d+', '?v=' + V, read('thanks.html'))
thanks = soft_replace(thanks, 'Someone will reply within one business day. If you need us sooner, email',
                      'We aim to respond within one business day. If it is urgent, email', 'thanks')
thanks = soft_replace(thanks, '<a href="dashboard.html" class="btn btn-ghost">View the dashboard</a>',
                      '<a href="workers.html" class="btn btn-ghost">Register as a Worker</a>', 'thanks')
write('thanks.html', thanks)

print('round 2 built')


