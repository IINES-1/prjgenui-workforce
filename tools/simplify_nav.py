"""Replace the header on every page with the simplified version.

Removes the top bar, swaps the nav for plain page links, drops the second
Dashboard link, and rebuilds the mobile menu to match. Each page must contain
exactly one of each block or the script stops.
"""
import io
import re
import sys

ROOT = r"C:\Users\is1lv\PRJGENUI-Workforce"
PAGES = ["index.html", "about.html", "contact.html", "compare.html",
         "faq.html", "privacy.html", "terms.html"]

NAV = """<nav class="nav">
      <a href="index.html">Home</a>
      <a href="about.html">About</a>
      <a href="compare.html">Compare</a>
      <a href="faq.html">FAQ</a>
      <a href="contact.html">Contact</a>
      <a href="dashboard.html">Dashboard</a>
    </nav>"""

HEADER_CTA = """<div class="header-cta">
      <a href="#" class="phone" data-phone style="display:none;"></a>
      <a href="{cta}" class="btn btn-gold btn-sm">Request a crew</a>
      <button class="nav-toggle" aria-label="Toggle navigation" aria-expanded="false">
        <span></span><span></span><span></span>
      </button>
    </div>"""

MOBILE_NAV = """<nav class="mobile-nav">
  <a href="index.html">Home</a>
  <a href="about.html">About</a>
  <a href="compare.html">Compare</a>
  <a href="faq.html">FAQ</a>
  <a href="contact.html">Contact</a>
  <a href="dashboard.html">Dashboard</a>
  <a href="{cta}" class="dash">Request a crew</a>
</nav>"""

TOPBAR_RE = re.compile(
    r'<!-- ====== Top bar ====== -->\r?\n<div class="topbar">.*?\r?\n</div>\r?\n\r?\n',
    re.S)
NAV_RE = re.compile(r'<nav class="nav">.*?</nav>', re.S)
CTA_RE = re.compile(r'<div class="header-cta">.*?</div>', re.S)
MOBILE_RE = re.compile(r'<nav class="mobile-nav">.*?</nav>', re.S)


def sub_once(pattern, repl, text, label, page):
    matches = pattern.findall(text)
    if len(matches) != 1:
        sys.exit("%s: expected 1 %s block, found %d" % (page, label, len(matches)))
    return pattern.sub(lambda m: repl, text, count=1)


def main():
    for page in PAGES:
        path = ROOT + "\\" + page
        with io.open(path, "r", encoding="utf-8", newline="") as f:
            text = f.read()
        cta = "#contact" if page == "contact.html" else "contact.html"

        text = sub_once(TOPBAR_RE, "", text, "topbar", page)
        text = sub_once(NAV_RE, NAV, text, "nav", page)
        text = sub_once(CTA_RE, HEADER_CTA.format(cta=cta), text, "header-cta", page)
        text = sub_once(MOBILE_RE, MOBILE_NAV.format(cta=cta), text, "mobile-nav", page)

        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        print("%-14s updated (CTA -> %s)" % (page, cta))


if __name__ == "__main__":
    main()
