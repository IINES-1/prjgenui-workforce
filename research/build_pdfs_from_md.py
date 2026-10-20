"""Build pdfmake specs for the governance/setup documents straight from
their markdown sources (supersedes the hand-embedded content in
build_pdfs_governance.py).

Reads:  docs/<name>.md
Writes: tmp/<name>.pdf.json  (render with research/render_pdfs.js)

Run:  python research/build_pdfs_from_md.py
"""
import json
import os
import re

DOCS = [
    ("baseline-register", "Baseline-to-Production Mapping Register",
     "0.3-E reconciliation and AT-01–AT-25 acceptance catalogue (v1.3)",
     "portrait"),
    ("gdpr-controls-proposal", "GDPR retention and lawful-basis schedule",
     "Retention, lawful basis, consent (v2.3) — landscape for the "
     "11-column schedule table", "landscape"),
    ("privacy-notice", "Platform Privacy Notice",
     "Data protection — privacy notice (v1.2)", "portrait"),
    ("platform-terms", "Platform Terms of Use",
     "Platform terms of use (v1.2)", "portrait"),
    ("processors", "Processors and sub-processors",
     "Processor list and international transfers (v1.2)", "portrait"),
    ("email-delivery-setup", "Email Delivery Setup (Zoho)",
     "DNS (SPF/DKIM/DMARC) and secure SMTP configuration", "portrait"),
    ("supabase-cost-and-ownership-proposal",
     "Supabase Cost, Ownership and Backup Proposal",
     "Register 9.8 activation — cost, ownership transfer, backup, key "
     "recovery, restoration", "portrait"),
    ("dpia", "Data Protection Impact Assessment",
     "DPIA draft (v1.0) — to be completed before real personal data",
     "portrait"),
    ("lia", "Legitimate Interests Assessment",
     "LIA draft (v1.0) — matching and performance evidence", "portrait"),
]

LAYOUT = "lightHorizontalLines"

styles = {
    "h1": {"fontSize": 18, "bold": True, "margin": [0, 0, 0, 6]},
    "h2": {"fontSize": 12, "bold": True, "margin": [0, 12, 0, 4]},
    "meta": {"fontSize": 9, "color": "#555555", "margin": [0, 0, 0, 2]},
    "body": {"fontSize": 9.5, "margin": [0, 0, 0, 6]},
}


def inline(text):
    """Markdown inline (bold + backticks) -> pdfmake text content."""
    text = text.replace('`', '')
    parts = text.split('**')
    if len(parts) == 1:
        return text
    out = []
    for i, part in enumerate(parts):
        if not part:
            continue
        if i % 2:
            out.append({"text": part, "bold": True})
        else:
            out.append(part)
    return out if out else text


def para(text, style="body"):
    return {"text": inline(text), "style": style}


def table(header, rows, ncols):
    if ncols <= 3:
        font, widths = 8.5, ["*"] * ncols
    elif ncols <= 5:
        font, widths = 7.5, ["*"] * ncols
    else:
        font, widths = 6.5, ["*"] * ncols
    body = [[{"text": inline(h), "bold": True, "fontSize": font}
            for h in header]]
    for r in rows:
        body.append([{"text": inline(c), "fontSize": font} for c in r])
    return {"table": {"headerRows": 1, "widths": widths, "body": body},
            "layout": LAYOUT, "margin": [0, 0, 0, 8]}


def split_row(line):
    line = line.strip()
    if line.startswith('|'):
        line = line[1:]
    if line.endswith('|'):
        line = line[:-1]
    return [c.strip() for c in line.split('|')]


SEP = re.compile(r'^\|[\s:|-]+$')


def ol_item(num, text):
    """Ordered-list item rendered with its source number, so numbering
    continues correctly across tables/paragraphs that interrupt a list
    (pdfmake's ol always restarts at 1)."""
    inner = inline(text)
    if isinstance(inner, str):
        inner = [inner]
    return {"text": [{"text": f"{num}. "}] + inner, "style": "body",
            "margin": [10, 0, 0, 4]}


def convert(md):
    lines = md.split('\n')
    content = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped or stripped == '---':
            i += 1
            continue
        if stripped.startswith('# ') and not stripped.startswith('## '):
            content.append({"text": inline(stripped[2:]), "style": "h1"})
            i += 1
            continue
        if stripped.startswith('## '):
            content.append({"text": inline(stripped[3:]), "style": "h2"})
            i += 1
            continue
        if stripped.startswith('|') and i + 1 < len(lines) \
                and SEP.match(lines[i + 1].strip()):
            header = split_row(lines[i])
            rows = []
            j = i + 2
            while j < len(lines) and lines[j].strip().startswith('|'):
                rows.append(split_row(lines[j]))
                j += 1
            content.append(table(header, rows, len(header)))
            i = j
            continue
        if stripped.startswith('- '):
            items = []
            while i < len(lines) and lines[i].strip().startswith('- '):
                items.append(inline(lines[i].strip()[2:]))
                i += 1
            content.append({"ul": items, "margin": [0, 0, 0, 8]})
            continue
        m = re.match(r'^(\d+)\.\s+(.*)$', stripped)
        if m:
            while i < len(lines):
                mm = re.match(r'^(\d+)\.\s+(.*)$', lines[i].strip())
                if not mm:
                    break
                content.append(ol_item(mm.group(1), mm.group(2)))
                i += 1
            continue
        # plain paragraph: join wrapped source lines
        buf = [stripped]
        i += 1
        while i < len(lines):
            nxt = lines[i].strip()
            if (not nxt or nxt == '---' or nxt.startswith('#')
                    or nxt.startswith('- ') or nxt.startswith('|')
                    or re.match(r'^\d+\.\s+', nxt)):
                break
            buf.append(nxt)
            i += 1
        content.append(para(' '.join(buf)))
    return content


os.makedirs('tmp', exist_ok=True)
for name, title, subject, orientation in DOCS:
    path = f'docs/{name}.md'
    with open(path, encoding='utf-8') as f:
        md = f.read()
    doc = {
        "pageSize": "A4",
        "pageMargins": [48, 48, 48, 48] if orientation == "portrait"
        else [30, 40, 30, 40],
        "defaultStyle": {"font": "Roboto", "fontSize": 9.5},
        "styles": styles,
        "info": {"title": f"PRJGENUI Workforce — {title}",
                 "author": "Ian", "subject": subject},
        "content": convert(md),
    }
    if orientation == "landscape":
        doc["pageOrientation"] = "landscape"
    out = f'tmp/{name}.pdf.json'
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    print('spec written:', out, os.path.getsize(out))
