"""Build the pdfmake specs for the two review documents.

Outputs (internal): tmp/baseline-register.pdf.json, tmp/gdpr-controls-proposal.pdf.json
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
    "h1": {"fontSize": 20, "bold": True, "margin": [0, 0, 0, 6]},
    "h2": {"fontSize": 13, "bold": True, "margin": [0, 14, 0, 4]},
    "meta": {"fontSize": 9, "color": "#555555", "margin": [0, 0, 0, 2]},
    "body": {"fontSize": 9.5, "margin": [0, 0, 0, 6]},
}

# ----------------------------------------------------------------- register
c = [
    {"text": "PRJGENUI Workforce — Baseline-to-Production Mapping Register", "style": "h1"},
    {"text": "Version 1.2 · 3 March 2026 · Baseline mapped: Dashboard 0.3-E (schema version 10), as approved · Read-only copy of record: docs/baseline-0.3-E/ (MD5 a612d51e6d8e09b7707246f2e06a9db3, SHA-256 106a9c535d...d0db71, 5,969 lines — both verified on receipt)", "style": "meta"},
    {"text": "Prepared by Ian · For approval by Marizilena Silva Fortes, Founder and Director", "style": "meta"},
    {"text": "Purpose", "style": "h2"},
    {"text": "The approved dashboard is the functional baseline. Nothing in it is removed or materially changed without a recorded change request and your approval. This register lists every function in the baseline and states exactly what happens to it in production. Where a change is more than a like-for-like rebuild, it is marked IMPROVED or NEW and needs your approval. Your reply of approved, or a list of item numbers you want discussed, closes each stage's sign-off.", "style": "body"},
    table(["Mark", "Meaning"],
          [["RETAINED", "Kept as-is, moved onto the production platform"],
           ["REBUILT", "Same behaviour, rebuilt on real database, logins and audit"],
           ["IMPROVED", "Behaviour kept, with a stated addition — approval item"],
           ["DEFERRED", "Stays working in the demo; built into production in a later stage"],
           ["NEW", "Not in the baseline; part of Stages 0–2"],
           ["LEGAL", "Depends on the employment-law opinion; flagged, not built until resolved"]],
          ["auto", "*"]),
    {"text": "2. Screens (the seven tabs)", "style": "h2"},
    table(["#", "Baseline function", "Current behaviour", "Production plan", "Status / Stage"],
          [["2.1", "Dashboard overview", "Worker counts, passports verified, compliance action centre preview, top ready workers", "Same views, fed by the production database, per-role", "REBUILT — Stage 0"],
           ["2.2", "Workers list & search", "Search and filter across the register", "Same, plus role-based visibility (workers see only themselves)", "REBUILT — Stage 0"],
           ["2.3", "Worker Passport form", "Identity, Right to Work, CSCS, training, verification history, trade, availability, competence, proof of work, assignment history, performance breakdown", "Same form, real records, restricted access to identity evidence", "REBUILT — Stage 0"],
           ["2.4", "Compliance Action Centre", "Critical / due soon (30 days) / watch (31–60) / missing evidence / workforce development, each with a recommended action", "Same groups, plus automated alerts and emails", "REBUILT + IMPROVED (alerts) — Stage 1"],
           ["2.5", "Crews", "Crew list and form: supervisor, members, specialism, deployment history; a crew only exists where people have genuinely worked together", "Same, unchanged meaning of crew", "RETAINED — Stage 0 (built, October 2026)"],
           ["2.6", "Contractors, projects, sites", "Contractor details, worker preferences, standard requirements, projects, sites and site-specific requirements", "Same, plus Stage 2 extensions (supplier controls, commercial flags)", "REBUILT — Stage 0; extended Stage 2"],
           ["2.7", "Workforce requests & match results", "Create a request (trade, numbers, dates, requirements), run the match, see explainable pass/fail/review factors per worker", "Same engine, enforced server-side, hard filters first, explanations kept", "REBUILT — Stage 0"],
           ["2.8", "Assignments", "List and detail: status stepper, history, outcome, references", "Same, plus generated assignment statements", "REBUILT + NEW (statements) — Stage 1"]],
          ["auto", "*", "*", "*", "*"]),
    {"text": "3. Compliance and readiness logic", "style": "h2"},
    table(["#", "Baseline function", "Current behaviour", "Production plan", "Status / Stage"],
          [["3.1", "General readiness", "Pure compliance pass/blocked, with a reason for every blocker", "Same rules, enforced by the server, not just the screen", "REBUILT — Stage 0"],
           ["3.2", "Assignment readiness", "Layers project, site and contractor requirements on top of general readiness", "Same, enforced at deployment — the hard gate", "REBUILT — Stage 0"],
           ["3.3", "Readiness snapshots", "A dated snapshot of readiness is stored with each offer", "Same", "RETAINED — Stage 0"],
           ["3.4", "Blocker reasons", "Every blocker carries a plain-English reason and recommended action", "Same wording, carried through to worker self-view (why am I blocked)", "REBUILT — Stage 0/1"],
           ["3.5", "Evidence completeness", "A certificate only counts as valid with status, evidence reference and a current expiry date", "Same — a document upload alone never produces READY. Changed per your review: qualifications without an expiry date (permanent, e.g. NVQ; some City & Guilds; renewable) are supported with an explicit validity marker and are never rejected for a missing expiry — the record is valid with status and evidence alone", "RETAINED + AMENDED — Stage 0 (migration 0018)"],
           ["3.6", "Expiry bands", "Expired / due soon (0–30) / watch (31–60) / current (60+)", "Same bands", "RETAINED — Stage 0"],
           ["3.7", "Expired-evidence blocking", "Expired evidence blocks a worker across the board", "Changed per your instruction of 16 October: expired evidence creates a hard block only where that evidence is mandatory for the job or site (by law, role, contractor or site), not automatically for every assignment", "IMPROVED — approval item — Stage 0"],
           ["3.8", "Expiry reminders", "None — bands are visible but nothing is sent", "Automated reminders at 60/30/14/7 days, to the worker and to us", "NEW — Stage 1 (in-app done; email delivery in progress)"]],
          ["auto", "*", "*", "*", "*"]),
    {"text": "4. Performance evidence", "style": "h2"},
    table(["#", "Baseline function", "Current behaviour", "Production plan", "Status / Stage"],
          [["4.1", "Weighted score", "Competence, reliability and client feedback weights; not yet scored until evidence exists", "Same weights, versioned (rules version stays recorded)", "RETAINED — Stage 0"],
           ["4.2", "Score bands and breakdown", "Band label plus visible per-factor breakdown on the passport", "Same, visible to the worker about their own record", "RETAINED — Stage 0"],
           ["4.3", "Naming", "The list row now reads performance score (changed 16 October, per your wording rule)", "Consistent performance evidence / reliability record wording throughout", "RETAINED — Stage 0"]],
          ["auto", "*", "*", "*", "*"]),
    {"text": "5. Matching engine", "style": "h2"},
    table(["#", "Baseline function", "Current behaviour", "Production plan", "Status / Stage"],
          [["5.1", "Match generation", "Each request creates a recorded generation of matches", "Same, permanent record", "RETAINED — Stage 0"],
           ["5.2", "Explainable factors", "Every match shows pass/fail/review factors", "Same — no unexplained ranking", "RETAINED — Stage 0"],
           ["5.3", "Availability options", "To confirm / available / within 24h / unavailable / booked", "Same", "RETAINED — Stage 0"],
           ["5.4", "Crew matching", "Crews can be matched as a unit where genuinely worked together", "Same", "RETAINED — Stage 0 (crew register built; unit matching follows the matching engine)"]],
          ["auto", "*", "*", "*", "*"]),
    {"text": "6. Assignment lifecycle", "style": "h2"},
    table(["#", "Baseline function", "Current behaviour", "Production plan", "Status / Stage"],
          [["6.1", "Status sequence", "PROPOSED → CONFIRMED → COMPLETED, plus LEGACY_RECORDED for migrated history", "Same sequence, transitions enforced and audited server-side", "REBUILT — Stage 0"],
           ["6.2", "Status history", "Every status change with timestamp, note and who made it", "Same, plus login-backed identity", "REBUILT — Stage 0"],
           ["6.3", "Outcome recording", "Attended, rating, rehire decision, client and supervisor feedback", "Same — feeds the reliability record", "RETAINED — Stage 0"],
           ["6.4", "Rates", "Worker pay rate and client charge rate recorded per assignment", "Kept as records (built, October 2026); billing built on top in Stage 2", "RETAINED; billing LEGAL — Stage 2"],
           ["6.5", "Legacy records", "History migrated from the old model, flagged for review", "Migration repeated onto the production database with the same flags", "REBUILT — Stage 0"],
           ["6.6", "Assignment statements", "None", "Generated statements per assignment, in your house style", "NEW — Stage 1"]],
          ["auto", "*", "*", "*", "*"]),
    {"text": "7. Audit and provenance", "style": "h2"},
    table(["#", "Baseline function", "Current behaviour", "Production plan", "Status / Stage"],
          [["7.1", "Worker audit trail", "Every field change with old and new values, timestamp and author", "Same, plus author tied to a real login", "REBUILT — Stage 0"],
           ["7.2", "Evidence provenance", "Evidence references and verifiers recorded on checks", "Same, plus source system and check method per evidence type", "REBUILT — Stage 0"],
           ["7.3", "Platform-wide audit", "None — only worker records are audited", "Views, exports, approvals, overrides and status changes all audited platform-wide. Added per your GDPR review (migration 0018): the audit log never copies sensitive values — invitation tokens, share codes, credentials and recovery codes are scrubbed from every entry, and earlier entries were cleaned in the same pass", "NEW — Stage 0"],
           ["7.4", "Controlled overrides", "None", "Override with approver, reason, expiry and permanent audit entry", "NEW — Stage 1"]],
          ["auto", "*", "*", "*", "*"]),
    {"text": "8. Right to Work records (LEGAL flag)", "style": "h2"},
    table(["#", "Baseline function", "Current behaviour", "Production plan", "Status / Stage"],
          [["8.1", "RTW check record", "Status, method, verifier, evidence note, expiry, restrictions", "Same fields, plus the full record set you specified: who engages the worker, who pays, who introduces/supplies, who operates the matching service, who is legally responsible for the check, who carried it out, method, date, result, evidence, and whether/when a follow-up is required", "REBUILT + NEW — Stage 0"],
           ["8.2", "Party model", "Not present — the demo implicitly assumes PRJGENUI is the engaging party", "Every worker and assignment records the parties as data, so the commercial model can change without rebuilding. This is the item your employment-law opinion affects most", "NEW — LEGAL — Stage 0 (structure) / finalised after opinion"],
           ["8.3", "Follow-up checks", "Not present", "Follow-up date recorded and alerted like any other expiry", "NEW — Stage 1"]],
          ["auto", "*", "*", "*", "*"]),
    {"text": "9. Storage, migration and data", "style": "h2"},
    table(["#", "Baseline function", "Current behaviour", "Production plan", "Status / Stage"],
          [["9.1", "Storage", "Supabase kv single-table store, IndexedDB and browser fallbacks", "Approved replacement: real Postgres schema with row-level security. You approved this on 16 October as preserving the baseline", "REBUILT — Stage 0"],
           ["9.2", "Schema versioning", "Schema version 7 with a migration log", "Same discipline, formal migrations", "RETAINED — Stage 0"],
           ["9.3", "Legacy migrations", "Clients→contractors, embedded assignments, integrity checks", "Re-run against the production schema with the same outcomes", "REBUILT — Stage 0"],
           ["9.4", "IDs and references", "PW-UK passport numbers, public assignment references, counters", "Same format and sequence", "RETAINED — Stage 0"],
           ["9.5", "Data export", "JSON export of everything", "Same, restricted to admin roles, every export audited", "RETAINED + IMPROVED — Stage 0"],
           ["9.6", "Demo data", "Easberg pilot seed names", "Stays in the demo only; production starts clean", "RETAINED (demo only) — demo removed from production October 2026"],
           ["9.7", "Prototype notice", "Prototype environment… not the sole legal compliance record banner", "Removed in production, because production will carry the real audit trail this notice currently disclaims", "IMPROVED — approval item — Stage 0 (done)"],
           ["9.8", "Backups", "None (single shared store)", "Backups to your seven-point standard, with the details stated exactly: (1) what and how often — an encrypted export of the records and the Storage files (worker documents are inside the export, because Supabase daily backups do not cover Storage), taken weekly; (2) destination and jurisdiction — a separate, access-restricted encrypted storage location in the United Kingdom, in an account dedicated to backups only, separate from the production account and its host; the named provider is in the backup and ownership proposal awaiting your approval, and activation does not proceed until you have approved it (interim custody: IINES Ltd; permanent custody: PRJGENUI after the ownership transfer); (3) controller of the destination — the backup account is controlled by the same controller as the production data (PRJGENUI), operated on its behalf until the ownership transfer completes; (4) retention and rotation — exactly 12 months, rolling: 52 weekly exports; when the 53rd lands, the oldest is deleted, so no export is ever older than 12 months and deleted live data ages out of the backup chain within at most 12 months; (5) encryption and key control — every export is encrypted before it leaves the production account (AES-256), with the encryption key held only by the controller's named administrators and never stored with the export itself or by the provider; (6) authorised people — the named Owner account and one named IINES administrator during the interim; nobody else holds backup credentials; (7) audited — every access to the backup location and every restoration attempt (successful or not) is logged with who, what, when and outcome, and those logs are reviewable alongside the platform audit trail. Two points stated plainly: the weekly export does not reduce the data-loss window below the Supabase daily-backup window — the daily backups (7-day retention) remain the first line of recovery and the export is the independent second copy; and Supabase's daily backups do not cover Storage files, so worker documents are included in the weekly export itself. A restoration test before the pilot covers both the records and the worker document files, with the date, scope and outcome recorded (point 7 of your standard). Activation waits for your written approval of the all-in monthly cost (compute, VAT, usage), the account-ownership transfer plan, and the named backup provider", "NEW — awaiting your approval — Stage 0"]],
          ["auto", "*", "*", "*", "*"]),
    {"text": "10. Access and roles", "style": "h2"},
    table(["#", "Baseline function", "Current behaviour", "Production plan", "Status / Stage"],
          [["10.1", "Logins", "None — anyone with the URL has full access", "Login with the seven roles; every record and action permission-checked. Added per your review: two-factor (authenticator app) is enforced for admin accounts (Owner, Operations, Compliance) before the dashboard unlocks, and a named Owner account (marizilena@) replaces shared sign-in for admin use; the shared hello@ account will be demoted once you confirm your named account and MFA work", "NEW — Stage 0"],
           ["10.2", "Worker self-view", "None", "Workers see their own passport, the reason for any block, their expiry dates; can correct details and upload replacement evidence", "NEW — Stage 1"],
           ["10.3", "Contractor view", "None", "Contractors see their own requests, matches and assignments only", "NEW — Stage 1/2 (built, October 2026)"],
           ["10.4", "GDPR controls", "None", "Retention dates per data class, restricted access to identity documents, and consent recorded as four separate events, never one general box (per the GDPR schedule, section 4): (1) privacy-notice acknowledgement — the notice version and the date it was acknowledged; (2) platform-terms acceptance — the terms version and the date accepted; (3) legal/contractual declarations — the confirmations required to enter the arrangement (accuracy of submissions, right to work), which are declarations, not consent; (4) genuinely optional consent — separately prompted, unticked by default, withdrawable at any time without affecting any other function. Each event records its own version, timestamp and wording", "NEW — Stage 1 (proposal attached)"]],
          ["auto", "*", "*", "*", "*"]),
    {"text": "11. Commercial records (your pricing structure)", "style": "h2"},
    table(["#", "Function", "Production plan", "Status / Stage"],
          [["11.1", "Price configuration", "Standard prices, customer-specific prices, discounts with recorded reasons, fee waivers, minimum monthly charges, allowances, VAT treatment, billing frequency, start and review dates, approval status, Order Form references — all configurable, nothing hard-coded", "NEW — Stage 1"],
           ["11.2", "Service switches", "Managed onboarding, compliance monitoring and training-request coordination activatable separately per contractor", "NEW — Stage 1"],
           ["11.3", "External costs", "Third-party fees (training providers, identity checks, verification) recorded separately and approved before incurred", "NEW — Stage 1"],
           ["11.4", "Invoicing/accounting integration", "Deferred", "NEW — Stage 2"]],
          ["auto", "*", "*", "*"]),
    {"text": "12. Items that wait for the employment-law opinion", "style": "h2"},
    {"ol": [
        "8.2 party model — structure built now, legal values finalised after the opinion",
        "6.4 rate/billing workflows on top of assignment records",
        "Supplier-statement wording and any AWR-dependent logic (Stage 2)",
        "Nothing else in Stages 0 or 1 is blocked. All of section 3, 4, 5, 7, 9 and 10 proceeds regardless.",
    ]},
    {"text": "13. Acceptance", "style": "h2"},
    {"text": "Acceptance tests for each stage are derived from this register: every RETAINED item must behave as it does today, every REBUILT item must pass the same scenario with a real login and an audit entry, and every NEW/IMPROVED item must pass the tests you sign off. A stage is complete when its tests pass and you have approved.", "style": "body"},
    {"text": "Approval: reply approved to accept this register as the mapping, or list the item numbers you want discussed first.", "style": "body"},
]

register = {
    "pageSize": "A4", "pageOrientation": "landscape",
    "pageMargins": [36, 40, 36, 40],
    "defaultStyle": {"font": "Roboto", "fontSize": 9.5},
    "styles": styles,
    "info": {"title": "PRJGENUI Workforce — Baseline-to-Production Mapping Register",
             "author": "Ian", "subject": "Stage 0-2 baseline mapping register"},
    "content": c,
}

# ------------------------------------------------------------------- gdpr
g = [
    {"text": "PRJGENUI Workforce — GDPR retention and lawful-basis schedule", "style": "h1"},
    {"text": "Version 2.2 draft for review · 3 March 2026 · Register item 10.4 · backup retention period stated exactly, per your review", "style": "meta"},
    {"text": "For approval by Marizilena Silva Fortes", "style": "meta"},
    {"text": "This revision follows the review framework you set out: every data category shows the information held, its purpose, the proposed lawful basis, the retention period and when it starts, what happens at the end, the justification, who can access it, and how a legal hold works. Consent is recorded as separate, specific events, never one general box. Lawful bases below are provisional until the employment-law opinion; the opinion may move individual entries, and where it does the basis is updated and the record re-flagged rather than silently changed. No row should be treated as settled legal advice.", "style": "body"},
    {"text": "1. What is already in place", "style": "h2"},
    {"ol": [
        "Identity document access is restricted. Only Owner and Compliance can open identity evidence. Workers see their own documents; Operations, contractors and auditors cannot open them.",
        "Document metadata carries a retention class and a deletion due date on every worker document row.",
        "Every write is audited — who, what, when, including overrides, approvals and status changes.",
        "The audit log never copies sensitive values (since migration 0018): invitation tokens, share codes, credentials and recovery codes are scrubbed from every audit entry before it is written, and earlier entries were cleaned in the same pass.",
        "Two-factor sign-in is enforced for admin accounts (Owner, Operations, Compliance): an authenticator-app code is required before the dashboard unlocks, so worker data is not reachable on a password alone.",
        "Qualifications without an expiry date are first-class records: permanent and renewable qualifications are recorded with an explicit validity marker and never rejected for a missing expiry date.",
    ]},
    {"text": "2. Retention and lawful-basis schedule", "style": "h2"},
    {"text": "At end of period: delete = row and any attached file removed after Compliance confirms; review = flagged for a Compliance decision before any deletion. Nothing is ever auto-deleted.", "style": "body"},
    table(["#", "Data class", "Information held", "Purpose", "Proposed lawful basis", "Retention", "Period starts", "At end", "Justification", "Access", "Legal hold"],
          [["1", "Right to Work evidence", "Share-code result, method, date, restrictions, follow-up date; scan where unavoidable", "Demonstrating the check and its outcome", "Legal obligation (right-to-work legislation)", "Relationship end + 2 years", "End of the worker's engagement with PRJGENUI", "delete", "Home Office right-to-work evidence guidance", "Owner, Compliance; worker sees own record", "Hold suspends deletion during a dispute, claim or investigation"],
           ["2", "Identity documents (scans)", "Passport/ID scans in Storage", "Supporting verification; the evidence itself where the scan forms part of the right-to-work record", "Legal obligation, plus contract; kept only where unavoidable", "Deleted once the check is recorded and verified — except where the scan itself is part of the right-to-work record you must keep (for example, where a Home Office share code could not be used and the document scan is the evidence of the check). Those scans are retained under row 1 and deleted with it", "Verification of the check (row 1's rule where the scan is the record)", "delete immediately after verification; with row 1 where the scan is the record", "Data minimisation: the recorded check, not the scan, is the evidence wherever a share code is available", "Owner, Compliance only", "Follows row 1 where the scan is part of the record"],
           ["3", "Cards, qualifications, training", "CSCS and trade cards, certificates, status, expiry, validity (expiring / renewable / permanent)", "Confirming site and role requirements", "Contract; legitimate interests for re-matching", "Expiry + 2 years. Qualifications with no expiry (permanent, e.g. NVQ; some City & Guilds) are never rejected for a missing expiry date — for them the period is relationship end + 2 years; renewable qualifications run from the next renewal date", "Expiry date; relationship end for permanent qualifications; next renewal date for renewable ones", "delete", "Re-issue and dispute defence", "Owner, Operations, Compliance; worker sees own", "Yes"],
           ["4", "Assignment history and outcomes", "Attendance, rating, rehire decision, client and supervisor feedback", "Delivering and evidencing the assignment", "Contract (the supply agreement)", "Relationship end + 6 years", "End of the worker's engagement", "review, then delete", "Contract and wage-claim limitation periods", "Owner, Operations, Compliance, Auditor; contractor sees own assignment statement", "Yes"],
           ["5", "Performance and reliability evidence", "Scores, bands, per-factor breakdown, weights version", "Matching quality and honest records", "Legitimate interests, balanced against the worker's rights", "Relationship end + 6 years", "End of the worker's engagement", "review, then delete", "Matching quality; the worker sees their own breakdown", "As row 4; worker sees own record", "Yes"],
           ["6", "Commercial records", "Prices, discounts and reasons, waivers, service switches, external costs", "Contract administration and billing", "Contract; legal obligation for tax records", "6 years", "Creation of the record, or invoice period end where later", "delete", "Tax (HMRC) and contract limitation periods", "Owner only", "Yes"],
           ["7", "Party records and engagements", "Who engages, pays, introduces, operates the check, performs it", "Evidencing who did what, per the party model", "Legal obligation (right-to-work defence); contract", "Relationship end + 2 years", "End of the relevant relationship", "delete", "Mirrors the right-to-work defence period", "Owner, Compliance, Auditor", "Yes"],
           ["8", "Consent and acknowledgement records", "The events in section 4, with statement versions and timestamps", "Accountability (UK GDPR record-keeping)", "Legal obligation (accountability); legitimate interests", "Life of the relationship + 6 years", "The recorded event", "delete", "Proving the lawful basis and what was agreed", "Owner, Compliance; the person sees their own record", "Yes"],
           ["9", "Audit log", "Every write: old and new values, who, when", "Platform-wide accountability", "Legal obligation (accountability); legitimate interests", "6 years", "The audited event", "delete", "Same limitation as the records described", "Owner, Compliance, Auditor (read-only)", "Yes — never deleted during a hold"]],
          ["auto", "*", "*", "*", "*", "*", "*", "auto", "*", "*", "*"], font=8),
    {"text": "Where a legal minimum exceeds these periods (for example an HMRC or employment-law requirement), the longer period wins and the class is re-flagged with the justification.", "style": "body"},
    {"text": "Relationship end, defined per row", "style": "h2"},
    {"text": "Relationship end is not one date for every class. Where a row above runs from relationship end, it means:", "style": "body"},
    {"ol": [
        "Rows 1, 2 (where the scan is the record), 3 (permanent qualifications) and 7 — the last of: the end date of the worker's last assignment, or, if the worker was never assigned, the date the worker record was archived or declined.",
        "Rows 4 and 5 (assignment history, performance evidence) — the end date of the worker's last assignment, or, if never assigned, the date the worker record was archived or declined. If an assignment ends but the worker stays active, the clock does not start.",
        "Row 8 (consent records) — the same date as rows 4-5, so the consent evidence outlives the engagement it evidences.",
        "Row 7 for contractor and party records — the end of the relevant commercial relationship: the termination or expiry of the supply agreement or framework.",
    ]},
    {"text": "The platform records the trigger date on the record when it happens, so the retention date is computed, not re-interpreted later.", "style": "body"},
    {"text": "3. How retention works mechanically", "style": "h2"},
    {"ol": [
        "Every class above has, or gets, a deletion-due date; those already exist on worker documents.",
        "The Compliance Action Centre gains a Retention due group: class, record, due date, recommended action (delete document, confirm retention).",
        "Nothing is deleted automatically. Deletion is confirmed by Owner or Compliance and audited.",
        "A legal hold is set by Owner or Compliance on a worker, contractor or class. Holds are exceptional: each one needs a recorded reason tied to a live dispute, claim or investigation, is time-stamped, and is reviewed at least every 6 months and lifted as soon as it is no longer needed. A hold hides the item from the Retention due group and blocks the delete action until it is lifted. Holds are audited like everything else.",
        "Backups sit inside the retention framework. The weekly export (register 9.8) has its own exact retention period: 12 months, rolling — 52 weekly exports, with the oldest deleted when the 53rd lands, so no export is ever older than 12 months. When live records are deleted under this schedule, the corresponding rows leave the next and subsequent exports, so deleted data ages out of the backup chain within at most 12 months rather than persisting indefinitely. The data-subject-rights process in section 6 states this plainly to anyone who asks.",
        "The weekly export (register 9.8) lists what exists per class, so data-subject requests can be answered from a current inventory.",
    ]},
    {"text": "4. Consent, acknowledgement and declarations — recorded as separate events", "style": "h2"},
    {"text": "You are right that one general consent box cannot carry the processing. The system records five distinct, separately-timestamped events, each with its own statement version, and none of them is treated as the lawful basis on its own — the lawful basis per purpose is the schedule in section 2.", "style": "body"},
    table(["Event", "What it records", "Where it happens", "Withdrawable?"],
          [["Privacy-notice acknowledgement", "The worker was shown the privacy notice (versioned text, timestamp)", "First sign-in", "No — it evidences that notice was given"],
           ["Platform terms acceptance", "The worker accepted the terms of use of the platform", "First sign-in", "Withdrawal closes the account; the terms govern use of the platform"],
           ["Legal/contractual declaration", "Confirmations required to enter the arrangement (accuracy of what they submitted, right to work)", "Invitation acceptance and first sign-in", "No — a declaration, not consent"],
           ["Optional consent", "Genuinely optional processing only, e.g. updates, if ever offered", "Separate prompt, unticked by default, plain language", "Yes, at any time, without affecting any other function"],
           ["Withdrawal of consent", "The withdrawal itself, and which consent it applied to", "A control in the worker's own passport", "Records the withdrawal"]],
          ["auto", "*", "*", "*"]),
    {"text": "No optional consent is required for registration, matching, assignments, statements or any core function. Withdrawing it never blocks a worker from exercising unrelated rights.", "style": "body"},
    {"text": "5. What this proposal deliberately does not do yet", "style": "h2"},
    {"ol": [
        "No automated deletion or auto-expiry of accounts.",
        "No in-platform data-subject-request workflow — the manual process in section 6 covers requests until volumes justify tooling.",
        "No special-category data beyond what right-to-work lawfully requires.",
    ]},
    {"text": "6. Data-subject rights — the manual process", "style": "h2"},
    {"text": "Requests (access, rectification, erasure, restriction, objection, portability) arrive by email to hello@prjgenuiworkforce.co.uk or through the contact page. Until request volumes justify an in-platform workflow, each one is handled manually, and every step is recorded in the audit log:", "style": "body"},
    {"ol": [
        "Acknowledge within 3 working days; the 1-month statutory clock and the request text are recorded in a request log (who asked, when, for what).",
        "Verify identity against the worker record — never by collecting new copies of identity documents beyond what is already held.",
        "Compile the response from the platform inventory: the per-class export (register 9.5) plus the worker's own documents, filtered to the requester. Owner or Compliance compiles; Owner approves the response.",
        "Answer within 1 month, extending by up to 2 further months only with a written reason sent inside the first month.",
        "Erasure requests are honoured where no lawful basis or legal obligation (rows 1, 6, 8, 9) requires retention; where retention is required, the response says which rows are retained, why, and for how long. Nothing is erased while a legal hold is live.",
        "Rectification requests can be actioned by the worker directly for their own details (worker self-service); other corrections are made by Operations or Compliance with the change audited.",
        "Backups: erasure applies to live data immediately; the corresponding rows leave the next weekly export and age out of the backup chain within at most 12 months (the backup retention period, section 3). This is stated plainly in the response.",
    ]},
    {"text": "Approval: reply approved to accept the schedule and the five-event consent model, or list the row numbers (1-9) or sections (3-6) you want discussed first. Lawful bases stay provisional until the employment-law opinion, as stated in the introduction.", "style": "body"},
]

gdpr = {
    "pageSize": "A4", "pageOrientation": "landscape",
    "pageMargins": [30, 40, 30, 40],
    "defaultStyle": {"font": "Roboto", "fontSize": 9.5},
    "styles": styles,
    "info": {"title": "PRJGENUI Workforce — GDPR retention and lawful-basis schedule",
             "author": "Ian", "subject": "Register item 10.4 — retention, lawful basis, consent"},
    "content": g,
}

with open('tmp/baseline-register.pdf.json', 'w', encoding='utf-8') as f:
    json.dump(register, f, ensure_ascii=False, indent=1)
with open('tmp/gdpr-controls-proposal.pdf.json', 'w', encoding='utf-8') as f:
    json.dump(gdpr, f, ensure_ascii=False, indent=1)
print('specs written:', os.path.getsize('tmp/baseline-register.pdf.json'),
      os.path.getsize('tmp/gdpr-controls-proposal.pdf.json'))
