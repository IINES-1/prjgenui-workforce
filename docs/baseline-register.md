# PRJGENUI Workforce — Baseline-to-Production Mapping Register

**Version:** 1.0 · 18 October 2026
**Baseline being mapped:** Dashboard 0.2C (schema version 7), as approved
**Prepared by:** Ian
**For approval by:** Marizilena Silva Fortes, Founder and Director

---

## 1. Purpose

The approved dashboard is the functional baseline. Nothing in it is removed or materially changed without a recorded change request and your approval. This register lists every function in the baseline and states exactly what happens to it in production.

Where a change is more than a like-for-like rebuild, it is marked **IMPROVED** or **NEW** and needs your approval. Your reply of "approved", or a list of item numbers you want discussed, closes each stage's sign-off.

**Legend**

| Mark | Meaning |
|---|---|
| RETAINED | Kept as-is, moved onto the production platform |
| REBUILT | Same behaviour, rebuilt on real database, logins and audit |
| IMPROVED | Behaviour kept, with a stated addition — approval item |
| DEFERRED | Stays working in the demo; built into production in a later stage |
| NEW | Not in the baseline; part of Stages 0–2 |
| LEGAL | Depends on the employment-law opinion; flagged, not built until resolved |

---

## 2. Screens (the seven tabs)

| # | Baseline function | Current behaviour | Production plan | Status / Stage |
|---|---|---|---|---|
| 2.1 | Dashboard overview | Worker counts, passports verified, compliance action centre preview, top ready workers | Same views, fed by the production database, per-role | REBUILT — Stage 0 |
| 2.2 | Workers list & search | Search and filter across the register | Same, plus role-based visibility (workers see only themselves) | REBUILT — Stage 0 |
| 2.3 | Worker Passport form | Identity, Right to Work, CSCS, training, verification history, trade, availability, competence, proof of work, assignment history, performance breakdown | Same form, real records, restricted access to identity evidence | REBUILT — Stage 0 |
| 2.4 | Compliance Action Centre | Critical / due soon (30 days) / watch (31–60) / missing evidence / workforce development, each with a recommended action | Same groups, plus automated alerts and emails | REBUILT + IMPROVED (alerts) — Stage 1 |
| 2.5 | Crews | Crew list and form: supervisor, members, specialism, deployment history; a crew only exists where people have genuinely worked together | Same, unchanged meaning of "crew" | RETAINED — Stage 0 |
| 2.6 | Contractors, projects, sites | Contractor details, worker preferences, standard requirements, projects, sites and site-specific requirements | Same, plus Stage 2 extensions (supplier controls, commercial flags) | REBUILT — Stage 0; extended Stage 2 |
| 2.7 | Workforce requests & match results | Create a request (trade, numbers, dates, requirements), run the match, see explainable pass/fail/review factors per worker | Same engine, enforced server-side, hard filters first, explanations kept | REBUILT — Stage 0 |
| 2.8 | Assignments | List and detail: status stepper, history, outcome, references | Same, plus generated assignment statements | REBUILT + NEW (statements) — Stage 1 |

---

## 3. Compliance and readiness logic

| # | Baseline function | Current behaviour | Production plan | Status / Stage |
|---|---|---|---|---|
| 3.1 | General readiness | Pure compliance pass/blocked, with a reason for every blocker | Same rules, enforced by the server, not just the screen | REBUILT — Stage 0 |
| 3.2 | Assignment readiness | Layers project, site and contractor requirements on top of general readiness | Same, enforced at deployment — the hard gate | REBUILT — Stage 0 |
| 3.3 | Readiness snapshots | A dated snapshot of readiness is stored with each offer | Same | RETAINED — Stage 0 |
| 3.4 | Blocker reasons | Every blocker carries a plain-English reason and recommended action | Same wording, carried through to worker self-view ("why am I blocked") | REBUILT — Stage 0/1 |
| 3.5 | Evidence completeness | A certificate only counts as valid with status, evidence reference and a current expiry date | Same — a document upload alone never produces READY. **Changed per your review:** qualifications without an expiry date (permanent, e.g. NVQ; some City & Guilds; renewable) are supported with an explicit validity marker and are never rejected for a missing expiry — the record is valid with status and evidence alone | RETAINED + AMENDED — Stage 0 (migration 0018) |
| 3.6 | Expiry bands | Expired / due soon (0–30) / watch (31–60) / current (60+) | Same bands | RETAINED — Stage 0 |
| 3.7 | Expired-evidence blocking | Expired evidence blocks a worker across the board | **Changed per your instruction of 16 October:** expired evidence creates a hard block only where that evidence is mandatory for the job or site (by law, role, contractor or site), not automatically for every assignment | IMPROVED — approval item — Stage 0 |
| 3.8 | Expiry reminders | None — bands are visible but nothing is sent | Automated reminders at 60/30/14/7 days, to the worker and to us | NEW — Stage 1 |

---

## 4. Performance evidence

| # | Baseline function | Current behaviour | Production plan | Status / Stage |
|---|---|---|---|---|
| 4.1 | Weighted score | Competence, reliability and client feedback weights; "Not yet scored" until evidence exists | Same weights, versioned (rules version stays recorded) | RETAINED — Stage 0 |
| 4.2 | Score bands and breakdown | Band label plus visible per-factor breakdown on the passport | Same, visible to the worker about their own record | RETAINED — Stage 0 |
| 4.3 | Naming | The list row now reads "performance score" (changed 16 October, per your wording rule) | Consistent "performance evidence" / "reliability record" wording throughout | RETAINED — Stage 0 |

---

## 5. Matching engine

| # | Baseline function | Current behaviour | Production plan | Status / Stage |
|---|---|---|---|---|
| 5.1 | Match generation | Each request creates a recorded generation of matches | Same, permanent record | RETAINED — Stage 0 |
| 5.2 | Explainable factors | Every match shows pass/fail/review factors | Same — no unexplained ranking | RETAINED — Stage 0 |
| 5.3 | Availability options | To confirm / available / within 24h / unavailable / booked | Same | RETAINED — Stage 0 |
| 5.4 | Crew matching | Crews can be matched as a unit where genuinely worked together | Same | RETAINED — Stage 0 |

---

## 6. Assignment lifecycle

| # | Baseline function | Current behaviour | Production plan | Status / Stage |
|---|---|---|---|---|
| 6.1 | Status sequence | PROPOSED → CONFIRMED → COMPLETED, plus LEGACY_RECORDED for migrated history | Same sequence, transitions enforced and audited server-side | REBUILT — Stage 0 |
| 6.2 | Status history | Every status change with timestamp, note and who made it | Same, plus login-backed identity | REBUILT — Stage 0 |
| 6.3 | Outcome recording | Attended, rating, rehire decision, client and supervisor feedback | Same — feeds the reliability record | RETAINED — Stage 0 |
| 6.4 | Rates | Worker pay rate and client charge rate recorded per assignment | Kept as records; billing built on top in Stage 2 | RETAINED; billing LEGAL — Stage 2 |
| 6.5 | Legacy records | History migrated from the old model, flagged for review | Migration repeated onto the production database with the same flags | REBUILT — Stage 0 |
| 6.6 | Assignment statements | None | Generated statements per assignment, in your house style | NEW — Stage 1 |

---

## 7. Audit and provenance

| # | Baseline function | Current behaviour | Production plan | Status / Stage |
|---|---|---|---|---|
| 7.1 | Worker audit trail | Every field change with old and new values, timestamp and author | Same, plus author tied to a real login | REBUILT — Stage 0 |
| 7.2 | Evidence provenance | Evidence references and verifiers recorded on checks | Same, plus source system and check method per evidence type | REBUILT — Stage 0 |
| 7.3 | Platform-wide audit | None — only worker records are audited | Views, exports, approvals, overrides and status changes all audited platform-wide. **Added per your GDPR review (migration 0018):** the audit log never copies sensitive values — invitation tokens, share codes, credentials and recovery codes are scrubbed from every entry, and earlier entries were cleaned in the same pass | NEW — Stage 0 |
| 7.4 | Controlled overrides | None | Override with approver, reason, expiry and permanent audit entry | NEW — Stage 1 |

---

## 8. Right to Work records (LEGAL flag)

| # | Baseline function | Current behaviour | Production plan | Status / Stage |
|---|---|---|---|---|
| 8.1 | RTW check record | Status, method, verifier, evidence note, expiry, restrictions | Same fields, plus the full record set you specified: who engages the worker, who pays, who introduces/supplies, who operates the matching service, who is legally responsible for the check, who carried it out, method, date, result, evidence, and whether/when a follow-up is required | REBUILT + NEW — Stage 0 |
| 8.2 | Party model | Not present — the demo implicitly assumes PRJGENUI is the engaging party | Every worker and assignment records the parties as data, so the commercial model can change without rebuilding. This is the item your employment-law opinion affects most | NEW — LEGAL — Stage 0 (structure) / finalised after opinion |
| 8.3 | Follow-up checks | Not present | Follow-up date recorded and alerted like any other expiry | NEW — Stage 1 |

---

## 9. Storage, migration and data

| # | Baseline function | Current behaviour | Production plan | Status / Stage |
|---|---|---|---|---|
| 9.1 | Storage | Supabase "kv" single-table store, IndexedDB and browser fallbacks | Approved replacement: real Postgres schema with row-level security. You approved this on 16 October as preserving the baseline | REBUILT — Stage 0 |
| 9.2 | Schema versioning | Schema version 7 with a migration log | Same discipline, formal migrations | RETAINED — Stage 0 |
| 9.3 | Legacy migrations | Clients→contractors, embedded assignments, integrity checks | Re-run against the production schema with the same outcomes | REBUILT — Stage 0 |
| 9.4 | IDs and references | PW-UK passport numbers, public assignment references, counters | Same format and sequence | RETAINED — Stage 0 |
| 9.5 | Data export | JSON export of everything | Same, restricted to admin roles, every export audited | RETAINED + IMPROVED — Stage 0 |
| 9.6 | Demo data | Easberg pilot seed names | Stays in the demo only; production starts clean | RETAINED (demo only) — demo removed from the production site |
| 9.7 | Prototype notice | "Prototype environment… not the sole legal compliance record" banner | Removed in production, because production will carry the real audit trail this notice currently disclaims | IMPROVED — done, approved by you 16 October — Stage 0 |
| 9.8 | Backups | None (single shared store) | Backups to your seven-point standard: **(1)** an encrypted export of the records, taken weekly; **(2)** stored off-site, separate from the production database and its host; **(3)** access-restricted to named administrators; **(4)** access and restoration attempts audited; **(5)** kept for its own retention period, defined in the GDPR schedule (section 3), separate from live-data retention; **(6)** a restoration test before the pilot that covers both the records and the worker document files; **(7)** a documented restoration procedure recording the date, scope and outcome of the last test. Two points stated plainly: the weekly export does **not** reduce the data-loss window below the Supabase daily-backup window — the daily backups (7-day retention) remain the first line of recovery and the export is the independent second copy, and Supabase's daily backups do not cover Storage files, so worker documents are included in the weekly export itself. Activation waits for your written approval of the all-in monthly cost (compute, VAT, usage) and the account-ownership transfer plan | NEW — awaiting your approval — Stage 0 |

---

## 10. Access and roles

| # | Baseline function | Current behaviour | Production plan | Status / Stage |
|---|---|---|---|---|
| 10.1 | Logins | None — anyone with the URL has full access | Login with the seven roles; every record and action permission-checked. **Added per your review:** two-factor (authenticator app) is enforced for admin accounts (Owner, Operations, Compliance) before the dashboard unlocks, and a named Owner account (marizilena@) replaces shared sign-in for admin use; the shared hello@ account will be demoted once you confirm your named account and MFA work | NEW — Stage 0 |
| 10.2 | Worker self-view | None | Workers see their own passport, the reason for any block, their expiry dates; can correct details and upload replacement evidence | NEW — Stage 1 |
| 10.3 | Contractor view | None | Contractors see their own requests, matches and assignments only | NEW — Stage 1/2 |
| 10.4 | GDPR controls | None | Retention dates per data class, restricted access to identity documents, recorded consent | NEW — Stage 1 |

---

## 11. Commercial records (your pricing structure)

| # | Function | Production plan | Status / Stage |
|---|---|---|---|
| 11.1 | Price configuration | Standard prices, customer-specific prices, discounts with recorded reasons, fee waivers, minimum monthly charges, allowances, VAT treatment, billing frequency, start and review dates, approval status, Order Form references — all configurable, nothing hard-coded | NEW — Stage 1 |
| 11.2 | Service switches | Managed onboarding, compliance monitoring and training-request coordination activatable separately per contractor | NEW — Stage 1 |
| 11.3 | External costs | Third-party fees (training providers, identity checks, verification) recorded separately and approved before incurred | NEW — Stage 1 |
| 11.4 | Invoicing/accounting integration | Deferred | NEW — Stage 2 |

---

## 12. Items that wait for the employment-law opinion

- 8.2 party model — structure built now, legal values finalised after the opinion
- 6.4 rate/billing workflows on top of assignment records
- Supplier-statement wording and any AWR-dependent logic (Stage 2)
- Nothing else in Stages 0 or 1 is blocked. All of section 3, 4, 5, 7, 9 and 10 proceeds regardless.

---

## 13. Acceptance

Acceptance tests for each stage are derived from this register: every RETAINED item must behave as it does today, every REBUILT item must pass the same scenario with a real login and an audit entry, and every NEW/IMPROVED item must pass the tests you sign off. A stage is complete when its tests pass and you have approved.

**Approval:** reply "approved" to accept this register as the mapping, or list the item numbers you want discussed first.
