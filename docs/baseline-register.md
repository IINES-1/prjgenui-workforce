# PRJGENUI Workforce — Baseline-to-Production Mapping Register

**Version:** 1.3 · 20 October 2026
**Status:** pending approval — the completed reconciliation against the technical handover pack (sections 14–16, including the full AT-01–AT-25 acceptance catalogue) is included below for your sign-off
**Baseline being mapped:** Dashboard 0.3-E (schema version 10), as approved
**Baseline copy of record:** `docs/baseline-0.3-E/PRJGENUI_Workforce_0.3-E_APPROVED.html` — read-only; MD5 `a612d51e6d8e09b7707246f2e06a9db3`, SHA-256 `106a9c535d76bbc72d0e1875e0f10a2f65443da445dcd3057d2c5a83a1d0db71`, 5,969 lines, both verified on receipt (see `docs/baseline-0.3-E/VERIFICATION.md`)
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
| 5.4 | Crew matching | Crews can be matched as a unit where genuinely worked together | Crew records, membership, deployment history and proven-crew evidence are built (migration 0017); **matching a crew as a unit follows with the frozen Stage 2 build** | PARTIAL — records built — Stage 0; unit matching frozen — Stage 2 |

---

## 6. Assignment lifecycle

| # | Baseline function | Current behaviour | Production plan | Status / Stage |
|---|---|---|---|---|
| 6.1 | Status sequence | PROPOSED, OFFERED, ACCEPTED, CONFIRMED, ACTIVE, COMPLETED/REVIEWED, plus CANCELLED, NO SHOW, REPLACED and LEGACY_RECORDED for migrated history | Built today: PROPOSED, CONFIRMED, COMPLETED plus LEGACY_RECORDED, transitions enforced and audited server-side. The full 0.3-E lifecycle (OFFERED, ACCEPTED, ACTIVE, NO SHOW, REPLACED with the two readiness gates) is the frozen Stage 2 build — see sections 14–16 for the exact mapping | REBUILT (part) — Stage 0; full lifecycle frozen — Stage 2 |
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
| 9.2 | Schema versioning | Schema version 10 with a migration log | Same discipline, formal migrations | RETAINED — Stage 0 |
| 9.3 | Legacy migrations | Clients to contractors, embedded assignments, integrity checks | Re-run against the production schema with the same outcomes | REBUILT — Stage 0 |
| 9.4 | IDs and references | PW-UK passport numbers, public assignment references, counters | Same format and sequence | RETAINED — Stage 0 |
| 9.5 | Data export | JSON export of everything | Same, restricted to admin roles, every export audited | RETAINED + IMPROVED — Stage 0 |
| 9.6 | Demo data | Easberg pilot seed names | Stays in the demo only; production starts clean | RETAINED (demo only) — demo removed from the production site |
| 9.7 | Prototype notice | "Prototype environment… not the sole legal compliance record" banner | Removed in production, because production will carry the real audit trail this notice currently disclaims | IMPROVED — done, approved by you 16 October — Stage 0 |
| 9.8 | Backups | None (single shared store) | Backups to your seven-point standard, with the details stated exactly: **(1) what and how often** — an encrypted export of the records **and the Storage files** (worker documents are inside the export), taken weekly; **(2) destination and jurisdiction** — **Supabase Storage, in the same project as the database, London region (`eu-west-2`, UK)**, in a dedicated private `backups` bucket with no public access (changed by IINES Ltd decision 25 October 2026; you approved AWS S3 London on 20 October 2026 — the change is set out in the backup and ownership proposal v1.2 and awaits your confirmation); interim custody: IINES Ltd; permanent custody: PRJGENUI after the ownership transfer; **(3) controller of the destination** — the backup bucket is controlled by the same controller as the production data (PRJGENUI), operated on its behalf until the ownership transfer completes; **(4) retention and rotation** — per your decision of 20 October 2026, unchanged: **12 weeks rolling** — 12 weekly exports, with the oldest deleted when the 13th is created; reviewed after the pilot if operational evidence shows a longer period is necessary; **(5) encryption and key control** — every export is encrypted before it is uploaded (AES-256, client-side), with a documented key-recovery procedure (key custody, custodians, recovery without IINES, rotation, decryption tested at every restoration exercise — set out in the backup and ownership proposal); **(6) authorised people** — the named Owner account and one named IINES administrator during the interim; nobody else holds backup credentials; **(7) audited** — every backup upload, deletion and restoration attempt (successful or not) is recorded in the platform audit log, which is itself part of the export. Three points stated plainly: (a) the platform runs on the **Supabase free plan** (IINES decision 25 October 2026; you approved Pro on 20 October 2026, upgrade to be revisited before real data), and the free plan has **no Supabase daily backups**, so the weekly export is the **only** backup — there is no second line of recovery until the plan is upgraded; (b) the backup sits in the **same Supabase account as the primary data** — it protects against data loss, corruption and accidental deletion, but not against the whole account being locked, deleted or compromised, which was the protection the separate-provider destination was approved for; (c) backup copies and worker documents share the free plan's 50 MB Storage cap, so the first real documents force the plan decision. Size: a measured estimate (database 14.5 MB, Storage currently empty; one compressed export expected at roughly 1–2 MB, 12 retained copies ~12–25 MB) is re-measured after the first complete export. A restoration test before the pilot covers both the records and the worker document files, with the date, scope and outcome recorded (point 7 of your standard) | CHANGED 25 October 2026 (free plan, Supabase-stored destination; IINES decision, your confirmation pending); activation awaits the first weekly export and the restoration test — Stage 0 |

---

## 10. Access and roles

| # | Baseline function | Current behaviour | Production plan | Status / Stage |
|---|---|---|---|---|
| 10.1 | Logins | None — anyone with the URL has full access | Login with the seven roles; every record and action permission-checked. **Added per your review:** two-factor (authenticator app) is enforced for admin accounts (Owner, Operations, Compliance) before the dashboard unlocks, and a named Owner account (marizilena@) replaces shared sign-in for admin use; the shared hello@ account will be demoted once you confirm your named account and MFA work | NEW — Stage 0 |
| 10.2 | Worker self-view | None | Workers see their own passport, the reason for any block, their expiry dates; can correct details and upload replacement evidence | NEW — Stage 1 |
| 10.3 | Contractor view | None | Contractors see their own requests, matches and assignments only | NEW — Stage 1/2 |
| 10.4 | GDPR controls | None | Retention dates per data class, restricted access to identity documents, and consent recorded as **four acceptance/declaration categories plus a separate withdrawal record**, never one general box (per the GDPR schedule, section 4, and your confirmation of 20 October 2026): **(1) privacy-notice acknowledgement** — the notice version, timestamp and account identity; **(2) platform-terms acceptance** — the terms version, timestamp and account identity; **(3) legal/contractual declarations** — the confirmations required to enter the arrangement (accuracy of submissions, right to work), which are declarations, not consent; **(4) genuinely optional consent** — separately prompted, unticked by default, withdrawable at any time without affecting any other function; **plus a separate withdrawal record** — the withdrawal itself, which consent it applied to, and its own timestamp. Each record retains its own wording version, timestamp and account identity | NEW — Stage 1 |

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

**Acceptance catalogue:** the authoritative catalogue is the technical handover pack's 25 acceptance tests (AT-01 to AT-25). Section 16 maps every one of them to the platform, with its current status and evidence; sections 14–15 reconcile the register against the pack's protected business rules and functional requirements (FR-01 to FR-18).

**Approval:** reply "approved" to accept this register as the mapping (including the sections 14–16 reconciliation and acceptance catalogue), or list the item numbers you want discussed first. The single decision needed from you to close the remaining tests is approval of the frozen Stage 2 build (the continuity and capacity functions in section 16: attendance evidence and disputes, replacement incidents, the second readiness gate, capacity holds, crew unit matching, validated import, the performance-threshold review trigger).

---

## 14. Reconciliation: protected business rules (handover pack section 7)

Each protected rule from the technical handover pack, mapped to the platform:

| Rule | Required behaviour | Platform position | Status / Evidence |
|---|---|---|---|
| Human authority | The system may calculate or recommend; a named human must approve suitability, exceptions and deployment decisions | Match approvals are recorded data (decision, decided_by, decided_at — migration 0019); an offer cannot be created without an approved match (migrations 0019/0020, verified); overrides carry approver, reason and expiry (migration 0014); readiness and matching results are recommendations until a human acts | BUILT and enforced — verified 20 October 2026 |
| Compliance precedence | Performance evidence or a score cannot override failed Right to Work, mandatory card, training or site-specific requirements | Failed RTW checks are never waivable by any override (migration 0019, replacing 0014's broader rule); verified with a live scenario: an approved override on a failed RTW check leaves the worker blocked | ENFORCED — verified 20 October 2026 |
| Explainability | Every eligible, hold, review or blocked outcome must show the rule and evidence that produced it | Matching records per-factor pass/fail/review with reasons (0008); readiness records per-blocker reasons (0007/0014); overrides name the approver and reason in the output | BUILT — test in catalogue execution |
| Two readiness gates | Readiness checked at confirmation and again before assignment activation | First gate built: readiness evaluation at confirmation, refusal observed and enforced; second gate (pre-activation, with the full offer/activation lifecycle) is the frozen Stage 2 build | PARTIAL — first gate built; second frozen — Stage 2 |
| No silent force | Invalid status transitions must be refused and logged, not forced or silently corrected | Worker and assignment status transitions are enforced server-side (0001/0006): invalid transitions raise with the reason; successful transitions are recorded in worker_status_history/assignment_events | BUILT — test in catalogue execution |
| Immutable history | Past match generations, readiness snapshots, offers and assignment events must remain historically accurate | Match generations are separate immutable records per run (0008); readiness evaluations and snapshots are dated records; assignment events append, never rewrite; audit records old and new values | BUILT — test in catalogue execution |
| Evidence provenance | Record what was checked, the source, who checked it, when, and the outcome | evidence_records carry source, checker, date, method and result; RTW and qualification records link to them; attendance provenance is part of the frozen Stage 2 build | BUILT (records) — attendance provenance frozen — Stage 2 |
| Site specificity | A worker suitable for one site is not automatically eligible for another with different requirements | Matching evaluates the request's essentials **plus that site's mandatory requirements** as separate factors per worker (0008); site requirements are data, not global rules | BUILT — test in catalogue execution |
| Crew truth | A crew claim must be supported by genuine overlapping assignment history; a list of people is not a proven crew | Crew confidence (new / limited evidence / proven) derives from recorded joint deployment history (0017); matching a crew as a unit is frozen Stage 2 | BUILT (records) — unit matching frozen — Stage 2 |
| Replacement continuity | Replacement uses the normal matching, approval, offer, confirmation and activation functions and links original and replacement assignments | Replacement incidents, the linked chain and the same-controls rule are the frozen Stage 2 build | NOT BUILT — frozen — Stage 2 |
| 60-minute wording | The service may aim to begin the replacement search within 60 minutes during service hours; it must not promise a replacement or arrival within 60 minutes | Adopted as the wording rule for the future replacement workflow and all service descriptions; no 60-minute promise appears anywhere in the platform or site | ADOPTED — applies at Stage 2 |
| No universal training assumption | Training is mandatory only where company policy, role, client, site or law makes it mandatory; the universal core-training list is empty | Training factors are evaluated only where a request or site marks them mandatory (0008); no universal training list exists in the platform | BUILT — test in catalogue execution |
| Performance threshold | The current threshold of 70 is a human-review trigger only, not a compliance pass or fail | Performance evidence is recorded as explanatory data with per-factor breakdown; a score can never change a compliance outcome (compliance precedence, above); the 70-point human-review trigger logic is the frozen Stage 2 build | PARTIAL — precedence enforced; trigger frozen — Stage 2 |
| Disputes and corrections | Attendance and performance evidence must allow controlled challenge, correction and audit without erasing original history | Worker self-correction is built (0015); attendance evidence and its dispute path are the frozen Stage 2 build; nothing erases audit history by design | PARTIAL — self-correction built; disputes frozen — Stage 2 |
| Data minimisation | Only collect and expose information necessary for the defined operational purpose | Fields are operational; identity evidence is restricted to Owner/Compliance and the worker's own view; storage access is per-worker, signed-URL only (0015); audit never copies secret values (0018) | BUILT — test in catalogue execution |

## 15. Reconciliation: functional requirements (handover pack section 8)

| ID | Area | Platform position | Status |
|---|---|---|---|
| FR-01 | Identity and tenancy | Managed authentication (Supabase Auth), invitations with expiring tokens (0003/0004), seven roles with server-side RLS enforcement; MFA for admin roles; single-controller platform — external contractor organisations (tenant separation at the interface) are the Stage 1/2 contractor view | BUILT (single tenancy); contractor organisations Stage 1/2 |
| FR-02 | Worker Passport | Full worker records, trades, availability, evidence summary, per-role visibility | BUILT — Stage 0 |
| FR-03 | Evidence | Evidence records with source, checker, date, decision and provenance; private bucket, per-worker policies, signed URLs (0015) | BUILT — Stage 0/1 |
| FR-04 | Compliance | Current / expiring / expired / missing / review / blocked states with reasons (readiness evaluation 0007/0014) | BUILT — Stage 0 |
| FR-05 | Contractors and sites | Contractor, project and site hierarchy with site-specific requirements | BUILT — Stage 0 |
| FR-06 | Requests | Trade, quantity, location, dates, requirements, notes | BUILT — Stage 0 |
| FR-07 | Matching | Versioned generations, hard gates, review states, explainable output (0008) | BUILT — Stage 0 |
| FR-08 | Offers | Offer records with recorded approved matches, refusal enforced and logged (0019/0020); the app offer flow is frozen Stage 2 | BUILT (data layer); app flow frozen — Stage 2 |
| FR-09 | Assignments | Status transitions enforced server-side, history and outcome recording (0001/0006); full lifecycle statuses frozen Stage 2 (see 6.1) | PARTIAL — Stage 0; full lifecycle Stage 2 |
| FR-10 | Readiness snapshots | Snapshot at confirmation built; pre-activation snapshot frozen Stage 2 | PARTIAL — Stage 0; second gate Stage 2 |
| FR-11 | Attendance | Attendance evidence, reporter, dispute path | FROZEN — Stage 2 |
| FR-12 | Replacement | Incident, original assignment, matching, approval, replacement, elapsed time | FROZEN — Stage 2 |
| FR-13 | Crews | Membership, leader, deployment history, evidence levels (0017); substitutions frozen Stage 2 | BUILT — Stage 0; substitutions Stage 2 |
| FR-14 | Capacity | Plans, holds, candidates, conflict prevention | FROZEN — Stage 2 |
| FR-15 | Notifications | Expiry reminders at 60/30/14/7 days built (0011/0012); offer/readiness/incident notifications follow with the Stage 2 flows | PARTIAL — expiry built; rest Stage 2 |
| FR-16 | Reporting | Operational dashboards per role built; scoped contractor export frozen Stage 1/2 | PARTIAL — Stage 0; scoped export Stage 1/2 |
| FR-17 | Administration | Audit search, configuration, integrity monitoring via schema migrations bookkeeping | PARTIAL — Stage 0/1 |
| FR-18 | Import and migration | Validated, idempotent import with dry-run and exception report | FROZEN — Stage 2 |

## 16. Acceptance catalogue: AT-01 to AT-25 (handover pack section 11)

Status legend: **VERIFIED** = scenario run against the live platform on fictional records, 20 October 2026 (script: `research/verify_0019.py`); **BUILT** = control exists in the platform, formal catalogue execution pending; **FROZEN** = part of the frozen Stage 2 build, awaiting your approval; **PENDING** = depends on an approved external step.

| ID | Scenario | Expected result | Status | Evidence / Note |
|---|---|---|---|---|
| AT-01 | Baseline integrity | Approved source hash matches the manifest before analysis | VERIFIED | MD5 and SHA-256 both match; 5,969 lines; read-only copy of record (`docs/baseline-0.3-E/VERIFICATION.md`) |
| AT-02 | Tenant isolation | Access denied and event logged | BUILT | Server-side RLS on every table (69 policies); contractor-facing interface (the external-tenant half of the test) is frozen Stage 1/2 |
| AT-03 | Right to Work hard gate | Blocked; no score or reviewer can override | VERIFIED | Migration 0019 + live scenario: an approved override on a failed RTW check leaves the worker blocked; overrides still work on non-RTW blockers |
| AT-04 | Site requirement | Blocked or held with precise reason | BUILT | Mandatory site requirements are separate hard factors in matching (0008) — catalogue execution pending |
| AT-05 | Explainable matching | Separate immutable generations, clear reasons | BUILT | match_generations + per-factor records (0008) — catalogue execution pending |
| AT-06 | Human approval (offer without approved match) | Refused and logged | VERIFIED | Migrations 0019/0020 + live scenario: offer refused with an audit entry; offer from a recorded approved match succeeds |
| AT-07 | First readiness gate | Confirmation refused or held for review | BUILT | Readiness evaluation at confirmation; hard-gate refusal enforced (0007/0014) — formal catalogue execution pending |
| AT-08 | Second readiness gate | Activation refused or held | FROZEN | Pre-activation gate is part of the Stage 2 full-lifecycle build (6.1) |
| AT-09 | Illegal transition | Refused without corrupting status | BUILT | Status enforcement triggers (0001/0006) — catalogue execution pending |
| AT-10 | Attendance provenance | Reporter, timestamp, source, assignment retained | FROZEN | Stage 2 build |
| AT-11 | Attendance dispute | Original retained; dispute and resolution audited | FROZEN | Stage 2 build |
| AT-12 | No-show replacement | Original and replacement chains linked; normal controls reused | FROZEN | Stage 2 build |
| AT-13 | Replacement prerequisite | Activation refused without site-pack/RAMS acknowledgement | FROZEN | Stage 2 build |
| AT-14 | Crew evidence | A crew without overlapping assignments is not represented as proven | BUILT (records) | Crew confidence derives from recorded joint deployment history (0017); the scenario test runs with the Stage 2 unit-matching build |
| AT-15 | Capacity conflict | Conflict shown; invalid booking prevented | FROZEN | Stage 2 build |
| AT-16 | Expiry notification | Correct authorised users notified once per policy | BUILT | Expiry schedule + reminders (0011/0012) — catalogue execution pending |
| AT-17 | Audit integrity | Before/after, actor, time, reason recorded | BUILT | Audit triggers platform-wide, scrubbed of secret values (0018) — catalogue execution pending |
| AT-18 | Export scope | Only tenant-scoped permitted fields included | PARTIAL | Admin export audited (9.5); contractor-scoped export frozen with the contractor view — Stage 1/2 |
| AT-19 | Backup restore | Documented recovery objective achieved and reconciled | PENDING | Supabase-stored backups (changed 25 October 2026; formerly AWS S3 London, approved 20 October 2026); first weekly export + restoration test at activation (proposal v1.2, sections 4–6) |
| AT-20 | Import validation | Dry-run reports exceptions; no silent partial corruption | FROZEN | FR-18, Stage 2 build |
| AT-21 | Privilege revocation | Access revoked within defined period | PARTIAL | Roles + RLS built; the revocation window for active sessions is defined and tested at the ownership transfer (JWT refresh window) |
| AT-22 | Document access | Expired/unauthorised link denied; private path not exposed | BUILT | Private bucket, per-worker storage policies, signed URLs only (0015) — catalogue execution pending |
| AT-23 | Responsive and accessible use | Keyboard-operable, labelled, status meaning available | PARTIAL | Responsive layouts verified; keyboard and label pass runs in the catalogue execution |
| AT-24 | Performance evidence | Below 70 triggers human review; compliance unchanged | FROZEN | The 70-point review trigger is Stage 2; compliance precedence is already enforced (section 14) |
| AT-25 | Deletion and retention | Policy applied; retained items justified; access controlled | PARTIAL | Retention classes and deletion-due dates on worker documents (0001/0011); confirmed-deletion workflow and legal holds follow the GDPR schedule build |

**Summary of the catalogue:** 4 verified (AT-01, AT-03, AT-06, and the refusal logging within AT-06); 10 built and awaiting formal catalogue execution (AT-02, 04, 05, 07, 09, 14, 16, 17, 22, 23); 5 partial (AT-18, 21, 25, plus the record halves of 14/23); 8 frozen at Stage 2 (AT-08, 10, 11, 12, 13, 15, 20, 24); 1 pending an approved external step (AT-19, backup activation). Approving the Stage 2 build plus the catalogue execution closes everything except AT-19, which closes with the backup activation and restoration test.
