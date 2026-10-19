"""Build the pdfmake specs for the three governance draft documents.

Outputs (internal): tmp/privacy-notice.pdf.json, tmp/platform-terms.pdf.json,
tmp/processors.pdf.json
"""
import json
import os

os.makedirs('tmp', exist_ok=True)

LAYOUT = "lightHorizontalLines"


def table(header, rows, widths, font=8.5):
    body = [[{"text": h, "bold": True, "fontSize": font} for h in header]]
    for r in rows:
        body.append([{"text": c, "fontSize": font} for c in r])
    return {"table": {"headerRows": 1, "widths": widths, "body": body},
            "layout": LAYOUT}


styles = {
    "h1": {"fontSize": 18, "bold": True, "margin": [0, 0, 0, 6]},
    "h2": {"fontSize": 12, "bold": True, "margin": [0, 12, 0, 4]},
    "meta": {"fontSize": 9, "color": "#555555", "margin": [0, 0, 0, 2]},
    "body": {"fontSize": 9.5, "margin": [0, 0, 0, 6]},
}

DOC = {"pageSize": "A4", "pageMargins": [48, 48, 48, 48],
       "defaultStyle": {"font": "Roboto", "fontSize": 9.5},
       "styles": styles}


def dump(name, doc, content, subject):
    out = dict(DOC)
    out["info"] = {"title": doc, "author": "Ian", "subject": subject}
    out["content"] = content
    with open(f'tmp/{name}.pdf.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print('spec written:', f'tmp/{name}.pdf.json')


# ------------------------------------------------------------- privacy notice
p = [
    {"text": "PRJGENUI Workforce — Platform Privacy Notice", "style": "h1"},
    {"text": "Version 1.0 draft for review · 19 October 2026", "style": "meta"},
    {"text": "For approval by Marizilena Silva Fortes · shown at first sign-in "
             "(versioned, with a recorded acknowledgement event)", "style": "meta"},
    {"text": "This notice covers the team platform at prjgenuiworkforce.co.uk "
             "(workers, contractors and the PRJGENUI team). The public website "
             "has its own privacy policy. Lawful bases below are provisional "
             "pending the employment-law opinion, per the GDPR retention and "
             "lawful-basis schedule.", "style": "body"},
    {"text": "1. Who we are", "style": "h2"},
    {"text": "PRJGENUI Workforce Ltd is the controller for the personal data "
             "in the platform. Contact: hello@prjgenuiworkforce.co.uk.",
     "style": "body"},
    {"text": "2. What we hold about you, why, and for how long", "style": "h2"},
    {"text": "The full schedule — information held, purpose, lawful basis, "
             "retention period and when it starts, and who can access it — is "
             "the GDPR retention and lawful-basis schedule, which this notice "
             "summarises:", "style": "body"},
    table(["About you", "Why", "How long"],
          [["Right to Work check record and any scan that forms part of it",
            "Demonstrating the right-to-work check and its outcome (legal obligation)",
            "2 years after the relationship ends"],
           ["Identity document scans (where not part of the RTW record)",
            "Verification only", "Deleted once the check is verified"],
           ["Cards, qualifications, training (including permanent qualifications with no expiry)",
            "Confirming site and role requirements",
            "2 years after expiry; 2 years after the relationship ends for permanent ones"],
           ["Assignment history and outcomes", "Delivering and evidencing assignments",
            "6 years after the relationship ends (reviewed first)"],
           ["Performance and reliability evidence", "Matching quality and honest records",
            "6 years after the relationship ends (reviewed first)"],
           ["Consent and acknowledgement records", "Proving what was agreed",
            "6 years after the relationship ends"],
           ["Audit log entries (who changed what, when)", "Accountability", "6 years"]],
          ["*", "*", "*"]),
    {"text": "Relationship end is defined per data class in the schedule "
             "(section 2, Relationship end, defined per row).", "style": "body"},
    {"text": "3. Who can see your data", "style": "h2"},
    {"text": "Access is role-checked per record: identity evidence is "
             "restricted to Owner and Compliance; you can always see your own "
             "record. Every access-relevant action is audited, and the audit "
             "log never contains secret values (invitation tokens, share "
             "codes, credentials).", "style": "body"},
    {"text": "4. Who we share it with", "style": "h2"},
    {"text": "We use a small number of processors, listed in the processor "
             "and sub-processor document: Supabase (database, sign-in, "
             "document storage — EU region), Zoho (email delivery — EU "
             "region) and Vercel (website hosting — no personal data). "
             "Developer and support access is by named, two-factor-protected "
             "accounts and is audited. We never sell your data.",
     "style": "body"},
    {"text": "5. Your rights", "style": "h2"},
    {"text": "You can ask for a copy of your data, corrections, erasure, "
             "restriction or object to processing, and you can withdraw any "
             "optional consent at any time without affecting core functions. "
             "Email hello@prjgenuiworkforce.co.uk; we acknowledge within 3 "
             "working days and respond within one month. Where a legal "
             "obligation requires us to keep something (for example the "
             "right-to-work record), we will tell you what we are keeping, "
             "why and for how long. Where deletion happens, backup copies "
             "age out within their own retention period.", "style": "body"},
    {"text": "6. Security", "style": "h2"},
    {"text": "Per-record access control, encrypted connections, two-factor "
             "sign-in for admin accounts, an audited trail of every change, "
             "and backups held to the seven-point standard in the baseline "
             "register (9.8).", "style": "body"},
]
dump('privacy-notice', 'PRJGENUI Workforce — Platform Privacy Notice', p,
     'Platform privacy notice for first-sign-in display')

# -------------------------------------------------------------- platform terms
t = [
    {"text": "PRJGENUI Workforce — Platform Terms of Use", "style": "h1"},
    {"text": "Version 1.0 draft for review · 19 October 2026", "style": "meta"},
    {"text": "For approval by Marizilena Silva Fortes · note: for legal review "
             "alongside the employment-law opinion before the pilot; wording "
             "intentionally short and plain.", "style": "meta"},
    {"text": "1. What these terms cover", "style": "h2"},
    {"text": "These terms cover use of the PRJGENUI Workforce team platform "
             "at prjgenuiworkforce.co.uk (the platform) by the PRJGENUI team, "
             "contractors and registered workers. They do not replace any "
             "supply agreement, employment contract or worker contract, which "
             "govern the working relationship itself.", "style": "body"},
    {"text": "2. Accounts and access", "style": "h2"},
    {"ol": [
        "Access is by invitation only. Each person has a named account and must keep their password confidential; admin accounts require two-factor sign-in.",
        "Invitation links and codes are personal and expire. Tell us (hello@prjgenuiworkforce.co.uk) if you think access has been misused.",
        "We may suspend or remove access where an account is misused or the person leaves.",
    ]},
    {"text": "3. What we ask of you", "style": "h2"},
    {"ol": [
        "Give accurate information, and correct it in your own record (or tell us) when it changes.",
        "Upload only documents you are entitled to provide (your own cards, certificates and identity documents), and only via the platform.",
        "Do not attempt to access other people's records, share your sign-in, or copy data out of the platform without permission.",
    ]},
    {"text": "4. Records and evidence", "style": "h2"},
    {"ol": [
        "The platform is the record system for worker readiness, assignments and statements. Uploads do not become verified until PRJGENUI checks them.",
        "Every change is audited. Where something is wrong, tell us and we will correct it with the change recorded.",
    ]},
    {"text": "5. Availability", "style": "h2"},
    {"text": "We aim for continuous availability but do not promise "
             "uninterrupted service. Backups are taken to the standard in the "
             "baseline register (9.8). Nothing in these terms limits any "
             "statutory right you have.", "style": "body"},
    {"text": "6. Changes", "style": "h2"},
    {"text": "We will tell registered users before material changes take "
             "effect; the version you accepted is recorded with your account.",
     "style": "body"},
    {"text": "7. Governing law", "style": "h2"},
    {"text": "England and Wales.", "style": "body"},
]
dump('platform-terms', 'PRJGENUI Workforce — Platform Terms of Use', t,
     'Platform terms of use draft for review')

# ------------------------------------------------------------------ processors
r = [
    {"text": "PRJGENUI Workforce — Processors and sub-processors", "style": "h1"},
    {"text": "Version 1.0 draft for review · 19 October 2026", "style": "meta"},
    {"text": "For approval by Marizilena Silva Fortes · GDPR review item: "
             "processor and sub-processor information", "style": "meta"},
    {"text": "Who processes platform data, and where", "style": "h2"},
    table(["Processor", "Role", "What they process", "Location", "Contract position"],
          [["Supabase (Supabase Inc.)", "Database, sign-in (authentication), document file storage",
            "All platform records: worker data, evidence, documents, accounts, audit log",
            "EU region (aws-eu-west-2, London)",
            "Supabase's standard Data Processing Addendum applies; we enable it for the project"],
           ["Zoho (Zoho Corporation)", "Email (Zoho Mail, EU data centre)",
            "Transactional and account email: sign-in invitations, password resets, expiry reminders. Message content is limited to the minimum (name, the action needed, a link)",
            "EU data centre (zoho.eu)", "Zoho's EU data-processing terms apply"],
           ["Vercel (Vercel Inc.)", "Website and app hosting",
            "Serves the website and app pages only. No personal data is stored by Vercel — the app sends data direct from the browser to Supabase",
            "Global CDN, static assets only",
            "No personal-data processing beyond serving pages"],
           ["Porkbun", "Domain registrar",
            "Domain registration contact data only (no worker or platform data)",
            "US", "Registrar terms"]],
          ["auto", "*", "*", "auto", "*"], font=8),
    {"text": "Delivery logs for email are kept by Zoho; we review them for "
             "troubleshooting only, and they do not contain document contents "
             "or credentials.", "style": "body"},
    {"text": "Developer and support access", "style": "h2"},
    {"ol": [
        "Development and support is provided by IINES Ltd, acting on documented instructions from PRJGENUI Workforce Ltd (the controller).",
        "Access is through named accounts only (no shared sign-ins), with two-factor sign-in enforced for admin roles.",
        "Direct database access for maintenance is possible only with the database credential, which is held in protected storage, and every maintenance action that touches data is performed through audited platform functions where one exists; scripted data changes are kept as reviewable files in the project repository.",
        "Platform administration (adding workers, verifying evidence, generating statements) is performed by named PRJGENUI team accounts and audited like any other action.",
    ]},
    {"text": "Backups (once activated per register 9.8)", "style": "h2"},
    {"text": "The weekly encrypted export is stored off-site with access "
             "restricted to named administrators; the destination and its "
             "location will be added to this list before activation, for "
             "your approval as part of the 9.8 approval.", "style": "body"},
    {"text": "Changes", "style": "h2"},
    {"text": "If a processor is added, replaced or given a new purpose, this "
             "list is updated and the change reported to you before it "
             "takes effect.", "style": "body"},
]
dump('processors', 'PRJGENUI Workforce — Processors and sub-processors', r,
     'Processor and sub-processor list for GDPR review')
