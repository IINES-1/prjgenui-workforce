import re, pathlib

root = pathlib.Path(r"C:\Users\is1lv\PRJGENUI-Workforce")
src = (root / "colours.html").read_text(encoding="utf-8")

# name, tagline, primary, secondary, accent, page background
SCHEMES = [
    ("The mix", "Exactly what she picked: Forest primary and Sage secondary from B, Amber accent from C. The baseline to compare the rest against.",
     "#1F3A2E", "#7A9A7E", "#E8A33D", "#F6F5F0"),
    ("Pine & Honey", "A slightly deeper pine, a greener sage and a warmer honey amber. Richer, a touch more premium.",
     "#17302A", "#8FAE92", "#EDAF45", "#F7F6F1"),
    ("Forest & Marigold", "Same forest as B with a lighter, softer sage and a brighter marigold. Fresher and friendlier.",
     "#1F3A2E", "#A3B899", "#F2A93B", "#F8F6F0"),
    ("Bottle & Saffron", "Darker bottle green, a cooler sea-sage secondary and a golden saffron. Crisp and modern.",
     "#14332B", "#5F8F7E", "#F4B942", "#F4F6F3"),
    ("Moss & Burnt Amber", "Warmer moss green with a deeper, burnt amber accent. Earthy and closer to the trades.",
     "#25402F", "#8BA27A", "#D9922E", "#F6F4EC"),
    ("Evergreen & Apricot", "Blue-leaning evergreen with a soft sage-teal secondary and a gentle apricot accent. The calmest of the six.",
     "#1C3B34", "#86A89B", "#F0A35E", "#F7F5F1"),
]


def lum(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def ratio(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def darken(h, f):
    h = h.lstrip("#")
    c = [int(int(h[i:i + 2], 16) * f) for i in (0, 2, 4)]
    return "#%02X%02X%02X" % tuple(c)


css = []
cards = []
report = []
for i, (name, blurb, p, s, a, bg) in enumerate(SCHEMES):
    k = "x%d" % (i + 1)
    on_s = "#FFFFFF" if ratio("#FFFFFF", s) >= ratio(p, s) else p
    link = s
    while ratio(link, bg) < 4.5:
        link = darken(link, 0.92)
    css.append(
        f".{k} .bar{{background:{p};}} .{k} .bar span{{color:{a};}}\n"
        f".{k} .body{{background:{bg};}} .{k} .btn-primary{{background:{p};}} "
        f".{k} .btn-secondary{{background:{s};color:{on_s};}} .{k} .btn-accent{{background:{a};color:{p};}} "
        f".{k} .link{{color:{link};text-decoration-color:{a};}}\n"
        f".{k} .sw1 .dot{{background:{p};}} .{k} .sw2 .dot{{background:{s};}} .{k} .sw3 .dot{{background:{a};}}\n"
    )
    cards.append(f"""    <div class="scheme-card {k}">
      <div class="label">
        <div class="num">Palette {i + 1}</div>
        <h3>{name}</h3>
        <p>{blurb}</p>
      </div>
      <div class="preview">
        <div class="bar">PRJGENUI Workforce<span>Workforce certainty</span></div>
        <div class="body">
          <h4>Verified trades, on time</h4>
          <p>We check every card with the body that issued it, then hold the CV to what the site manager actually needs.</p>
          <div class="btn-row">
            <a class="btn btn-accent">Start a search</a>
            <a class="btn btn-primary">See how it works</a>
            <a class="btn btn-secondary">Register for shifts</a>
          </div>
          <p style="margin-top:12px;"><a class="link">Read the FAQs</a></p>
        </div>
      </div>
      <div class="swatches">
        <div class="sw sw1"><div class="dot"></div><div class="hex">{p}</div><div class="role">Primary</div></div>
        <div class="sw sw2"><div class="dot"></div><div class="hex">{s}</div><div class="role">Secondary</div></div>
        <div class="sw sw3"><div class="dot"></div><div class="hex">{a}</div><div class="role">Accent</div></div>
      </div>
    </div>
""")
    report.append((i + 1, name, round(ratio("#FFFFFF", p), 1), round(ratio(on_s, s), 1), round(ratio(p, a), 1), link))

# Replace the old scheme CSS, header copy and grid
out = re.sub(r"/\* ---- Scheme A:.*?(?=</style>)", "/* ---- New palettes ---- */\n.btn-accent{display:inline-block;}\n" + "".join(css), src, flags=re.S)
out = out.replace("<title>Colour scheme options", "<title>More colour palettes")
out = re.sub(r"<h1>Colour scheme options.*?</h1>", "<h1>More colour palettes</h1>", out, flags=re.S)
out = re.sub(r'<p class="lede">.*?</p>',
             '<p class="lede">Six palettes built from the ones she picked: forest green as the main colour, sage as the second colour and amber as the accent. Each one tweaks the shades slightly so you can see how they feel together.</p>',
             out, count=1, flags=re.S)
out = re.sub(r'(<div class="intro-note">\s*<p>).*?(</p>)',
             r"\1Same fonts and layout as before. Each card shows an amber button, a green button and a sage button, plus a link with an amber underline. The three swatches are the main colour, the second colour and the accent.\2",
             out, count=1, flags=re.S)
out = re.sub(r'<div class="scheme-grid">.*?\n  </div>\n\n  <div class="reply-note">',
             '<div class="scheme-grid">\n\n' + "\n".join(cards) + '\n  </div>\n\n  <div class="reply-note">', out, count=1, flags=re.S)
out = re.sub(r'(<div class="reply-note">\s*<p>).*?(</p>)',
             r"\1Reply with the number of the palette you like (1 to 6). We can make any colour lighter or darker, or swap one colour between palettes.\2",
             out, count=1, flags=re.S)

(root / "colours-2.html").write_text(out, encoding="utf-8", newline="\n")
print("n  name                    white/primary  btn text/sage  primary/amber  link")
for r in report:
    print(r)
