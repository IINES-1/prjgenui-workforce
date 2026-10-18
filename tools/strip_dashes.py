"""Remove every em dash from dashboard.html.

Visible UI strings get a hand-written rewrite. Code comments fall back to a
plain hyphen. Each UI replacement must match exactly once, otherwise we stop
so nothing is silently skipped.
"""
import io
import sys

PATH = r"C:\Users\is1lv\PRJGENUI-Workforce\dashboard.html"

UI = [
    # <title> and prototype banner
    ("<title>PRJGENUI Workforce — Verified Workforce Operating System</title>",
     "<title>PRJGENUI Workforce | Verified Workforce Operating System</title>"),
    ("Prototype environment — local browser storage only. Do not use as the sole legal compliance record.",
     "Prototype environment. Data is stored in this browser only. Do not use as the sole legal compliance record."),

    # Placeholders rendered into tables and headers
    ("if(!dateStr) return '—';",
     "if(!dateStr) return 'Not set';"),
    ("<span class=\"passport-tag\">${esc(w.identity.passportId||'—')}</span></div>",
     "<span class=\"passport-tag\">${esc(w.identity.passportId||'Pending')}</span></div>"),
    ("${sc.score===null?'<span style=\"color:var(--slate);font-weight:400;\">—</span>':sc.score+'%'}<span class=\"u\">trust score</span>",
     "${sc.score===null?'<span style=\"color:var(--slate);font-weight:400;\">Not yet scored</span>':sc.score+'%<span class=\"u\">trust score</span>'}"),
    ("${r.score===null?'—':r.score+'%'}<span class=\"u\">trust score</span>",
     "${r.score===null?'<span style=\"color:var(--slate);font-weight:400;\">Not yet scored</span>':r.score+'%<span class=\"u\">trust score</span>'}"),
    ("<span class=\"passport-tag\">${esc(w.identity.passportId||'—')}</span> · Last updated ${w.auditLog&&w.auditLog[0]?esc(formatAuditTimestamp(w.auditLog[0].timestamp)):'—'}",
     "<span class=\"passport-tag\">${esc(w.identity.passportId||'Pending')}</span> · Last updated ${w.auditLog&&w.auditLog[0]?esc(formatAuditTimestamp(w.auditLog[0].timestamp)):'not recorded'}"),
    ("${sc.score===null?'—':sc.score+'% · '+sc.band}",
     "${sc.score===null?'Not yet scored':sc.score+'% · '+sc.band}"),

    # Score breakdown and readiness messages
    ("Insufficient data — no verification, compliance or history recorded yet.",
     "Insufficient data. No verification, compliance or history recorded yet."),
    ("Not yet scored: ${sc.missingComponents.join(', ')} — no data recorded.",
     "Not yet scored: ${sc.missingComponents.join(', ')} (no data recorded)."),
    ("`${name} required by workforce policy — not held`",
     "`${name} required by workforce policy but not held`"),
    ("`${name} required by workforce policy — ${reason}`",
     "`${name} required by workforce policy: ${reason}`"),
    ("issue:`${e.item} — due ${fmtDate(e.expiryDate)}`",
     "issue:`${e.item}, due ${fmtDate(e.expiryDate)}`"),

    # Name / trade separators in rows and dropdowns
    ("<span class=\"who\">${esc(w.identity.fullName)}</span> — <span class=\"what\">${esc(w.tradeProfile.primaryTrade)}</span>",
     "<span class=\"who\">${esc(w.identity.fullName)}</span> · <span class=\"what\">${esc(w.tradeProfile.primaryTrade)}</span>"),
    ("<span class=\"who\">${esc(workerName(i.worker))}</span> — <span class=\"what\">${esc(i.issue)}</span>",
     "<span class=\"who\">${esc(workerName(i.worker))}</span> · <span class=\"what\">${esc(i.issue)}</span>"),
    ("${c.memberIds.includes(w.id)?'selected':''}>${esc(w.identity.fullName)} — ${esc(w.tradeProfile.primaryTrade)}</option>",
     "${c.memberIds.includes(w.id)?'selected':''}>${esc(w.identity.fullName)} · ${esc(w.tradeProfile.primaryTrade)}</option>"),
    ("${ids.includes(w.id)?'selected':''}>${esc(w.identity.fullName)} — ${esc(w.tradeProfile.primaryTrade)}</option>",
     "${ids.includes(w.id)?'selected':''}>${esc(w.identity.fullName)} · ${esc(w.tradeProfile.primaryTrade)}</option>"),

    # Passport form copy
    ("Identity &amp; compliance — kept separate from performance history",
     "Identity &amp; compliance (kept separate from performance history)"),
    (">Manual — British/Irish passport</option>",
     ">Manual check: British or Irish passport</option>"),
    ("Confirm via CSCS Smart Check or cscssmartcheck.co.uk — never rely on the card alone.",
     "Confirm via CSCS Smart Check or cscssmartcheck.co.uk. Never rely on the card alone."),
    ("<b>${esc(formatAuditTimestamp(a.timestamp))}</b> — ${esc(a.category)}${a.field?' ('+esc(a.field)+')':''}: ${esc(a.newValue===null?'—':a.newValue)}${a.oldValue?' (was '+esc(a.oldValue)+')':''}${a.note?' — '+esc(a.note):''}",
     "<b>${esc(formatAuditTimestamp(a.timestamp))}</b> · ${esc(a.category)}${a.field?' ('+esc(a.field)+')':''}: ${esc(a.newValue===null?'cleared':a.newValue)}${a.oldValue?' (was '+esc(a.oldValue)+')':''}${a.note?'. '+esc(a.note):''}"),
    ("Performance history — what the Trust Score is built from",
     "Performance history: what the Trust Score is built from"),
    ("The one score component that's a judgment call — base it on specific evidence, not a default number.",
     "This is the one score component that's a judgement call. Base it on specific evidence rather than a default number."),
    ("<h2>Trust score — how it's calculated</h2>",
     "<h2>Trust score: how it's calculated</h2>"),
    ("Shown openly to keep this defensible and appealable — not a hidden number.",
     "Shown openly so the score can be explained and appealed. It isn't a hidden number."),
    ("placeholder=\"e.g. Prestige Coast — Guildford\"",
     "placeholder=\"e.g. Prestige Coast, Guildford\""),

    # Crews, clients, deploy
    ("A crew is a group of workers with a track record of working well together — add one once you've seen it happen.",
     "A crew is a group of workers with a track record of working well together. Add one once you've seen it happen."),
    ("Track who works well together — Verified Crew Intelligence.",
     "Track who works well together: Verified Crew Intelligence."),
    ("on file — this is your Contractor Memory.",
     "on file. This is your Contractor Memory."),
    ("${trade?' — '+esc(trade):''}</span>",
     "${trade?' for '+esc(trade):''}</span>"),
    ("Short by ${Number(qty)-eligible.length} — check the reserve or widen the search",
     "Short by ${Number(qty)-eligible.length}. Check the reserve or widen the search."),

    # Toasts, confirms and integrity messages
    ("Storage switched to local storage fallback after an IndexedDB error — re-saving everything now.",
     "Storage switched to local storage fallback after an IndexedDB error. Re-saving everything now."),
    ("`${issues.length} integrity issue(s) detected — see browser console.`",
     "`${issues.length} integrity issue(s) detected. See the browser console.`"),
    ("'Easberg pilot already initialised — nothing to add.'",
     "'Easberg pilot already initialised. Nothing to add.'"),
    ("No compliance data will be invented — you'll fill each in as it's confirmed. Continue?",
     "No compliance data will be invented. You'll fill each in as it's confirmed. Continue?"),
    ("`Easberg pilot ready — ${namesToAdd.length} shell${namesToAdd.length===1?'':'s'} added. Primary trade left blank on purpose — fill it in when confirmed.`",
     "`Easberg pilot ready. ${namesToAdd.length} shell${namesToAdd.length===1?'':'s'} added. Primary trade left blank on purpose; fill it in when confirmed.`"),
    ("w.id and identity.workerUUID do not match — should always be the same internal UUID",
     "w.id and identity.workerUUID do not match; they should always be the same internal UUID"),
    ("is behind the highest assigned Passport ID (${maxAssignedPassportNumber}) — future IDs could collide",
     "is behind the highest assigned Passport ID (${maxAssignedPassportNumber}), so future IDs could collide"),
    ("`${issues.length} integrity issue(s) found — see browser console.`",
     "`${issues.length} integrity issue(s) found. See the browser console.`"),
    ("'Integrity check passed — no issues found.'",
     "'Integrity check passed. No issues found.'"),
    ("'Could not read that file — is it a valid backup?'",
     "'Could not read that file. Is it a valid backup?'"),
    ("This cannot be undone — export a backup first if you want to keep a copy.",
     "This cannot be undone. Export a backup first if you want to keep a copy."),
]


def main():
    with io.open(PATH, "r", encoding="utf-8") as f:
        text = f.read()
    before = text.count("\u2014")

    for old, new in UI:
        n = text.count(old)
        if n != 1:
            sys.exit("Expected exactly 1 match, found %d for:\n  %s" % (n, old))
        text = text.replace(old, new)

    after_ui = text.count("\u2014")
    # Everything left is in code comments: a plain hyphen is the natural form.
    text = text.replace(" \u2014 ", " - ").replace("\u2014", "-")

    with io.open(PATH, "w", encoding="utf-8", newline="") as f:
        f.write(text)

    print("em dashes before: %d" % before)
    print("rewritten in UI strings: %d" % (before - after_ui))
    print("replaced in comments: %d" % after_ui)
    print("remaining: %d" % text.count("\u2014"))


if __name__ == "__main__":
    main()
