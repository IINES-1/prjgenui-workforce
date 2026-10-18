# PRJGENUI Workforce — Production Schema Design

**Version:** 1.0 (draft for approval) · 18 October 2026
**Stage:** 0 — Foundations
**Companion to:** Baseline-to-Production Mapping Register v1.0 (approved)
**For approval by:** Marizilena Silva Fortes, Founder and Director
**Prepared by:** Ian

---

## 1. Purpose and principles

This document defines the production database, roles, access rules, statuses and audit model that Stage 0 builds. It follows the approved register: every baseline function is retained or rebuilt as listed there, and the two approved changes (expiry blocking per job or site, and removal of the prototype notice) are reflected.

**Design principles**

1. **Parties are data, not code.** Who engages, pays, introduces and checks each worker is recorded per assignment. The commercial model can change without a rebuild. (Section 3B, LEGAL.)
2. **Default deny.** Row-level security denies everything unless a role is explicitly permitted.
3. **Nothing is deleted.** Records are archived with a reason and an audit entry. Identity documents are restricted-access files, never deleted before their retention date.
4. **Every state change is audited.** Who, what, old value, new value, when, and why. The prototype notice disclaiming audit is replaced by a real audit trail.
5. **Rules are versioned.** Readiness rules, scoring weights and matching rules each carry a version number, and every evaluation records the version used, so past decisions can be explained.
6. **A document alone never makes a worker READY.** Status changes are made by the system only when the recorded evidence conditions are met, and by a human where the rules require one.

**Platform:** Supabase (Postgres database, Auth, Storage, Edge Functions), as set out in the approved proposal. App hosting on Vercel at `app.prjgenuiworkforce.co.uk`. The existing public website and demo dashboard are unaffected until cutover.

---

## 2. Roles and access

Seven roles, mapped to Supabase Auth. A user can hold more than one role; the strictest rule applies.

| Role | Who | Can do |
|---|---|---|
| **Owner** | Marizilena | Everything, including price configuration, overrides approval, role grants and audit export |
| **Operations** | Ian / staff | Day-to-day: workers, requests, matches, assignments, worker contact; no price changes, no override approval |
| **Compliance** | Compliance lead | Verify and reject evidence, run checks, manage expiry, confirm hard-gate decisions; no commercial data |
| **Contractor** | Easberg users | Own contractors only: own requests, matches, assignments, statements, worker attendance and feedback; no worker identity documents |
| **Worker** | Registered workers | Own passport only: own checks, statuses, expiry dates, the reason for any block, own corrections and replacement evidence; no other worker's data |
| **Supplier** | Labour suppliers / subcontractors (Stage 2) | Own supplied workers' compliance view only, as scoped in the engagement |
| **Auditor** | External / legal | Read-only across compliance and audit, including exports; no personal document contents without Owner grant |

**Access matrix (summary).** Write access to identity documents: Compliance and Owner only. Worker self-view: worker's own row only, enforced by `worker_id = auth worker id`. Contractor scoping: `contractor_id = own`. Audit log: append-only for all roles except Auditor/Owner read; no updates or deletes for anyone.

**Worker access is deliberately one way:** workers can read their record and submit corrections and evidence, but nothing they submit changes a status directly. Every submission lands as *pending review* for Compliance. This is the worker's correction and dispute right from the register (10.2), and disputes escalate to the incident workflow.

---

## 3. Table groups

### A. Identity and access

| Table | Purpose |
|---|---|
| `profiles` | One per login: full name, role(s), contractor or worker link, status, created/retired timestamps |
| `role_grants` | Role assignments with granted-by, granted-at, reason (audited) |
| `invitations` | Time-limited, single-use invitations by email and role, issued by Owner/Operations |

### B. Party and engagement model (LEGAL — structure now, values after the opinion)

| Table | Purpose |
|---|---|
| `parties` | Every legal/commercial party: company, worker, PRJGENUI itself, suppliers |
| `engagements` | One per assignment relationship. Records: engaging party, paying party, introducing/supplying party, matching-service operator, party legally responsible for the Right to Work check, and the check performer. All are `party_id` references — no assumption that PRJGENUI holds any of them |
| `engagement_events` | Changes to an engagement (who changed which party role, when) — audited |

### C. Worker records

| Table | Purpose |
|---|---|
| `workers` | Identity: name, contact, trade profile, availability, passport number (PW-UK format retained), status |
| `worker_status_history` | Every status change with reason, actor and timestamp |
| `rtw_checks` | Right to Work: method, check date, result, restrictions, follow-up due date, source, reference number, identity match, performer, evidence link, retention deadline |
| `qualifications` | CSCS and trade cards: type, number, status, evidence reference, issue and expiry dates |
| `training_certificates` | Training with the same evidence and expiry structure |
| `work_history` | Experience entries with references and supervisor feedback |
| `proof_of_work` | Skill evidence, supervisor-signed, per the register |
| `worker_documents` | Restricted file storage references: document type, storage path, uploaded by, visible to Compliance/Owner only, retention class and deletion due date |

### D. Readiness and the gate

| Table | Purpose |
|---|---|
| `rule_versions` | Versioned readiness rules, scoring weights, matching rules, each with effective dates and the rule text |
| `readiness_evaluations` | Every evaluation result: worker, assignment (if any), rules version, outcome, blockers with reasons |
| `readiness_snapshots` | The dated snapshot stored with each offer (register 3.3, retained) |
| `expiry_schedule` | Derived from all dated evidence; drives reminders at 60/30/14/7 days |
| `reminder_log` | Every reminder sent: worker, item, channel, date, sent-by |

The hard gate is a server-side function: an assignment cannot move to CONFIRMED unless a current `readiness_evaluations` row for that worker and assignment shows no mandatory blocker. The approved expiry change applies: expired evidence blocks only where it is mandatory for that job or site.

### E. Assignments and matching

| Table | Purpose |
|---|---|
| `contractors`, `projects`, `sites`, `site_requirements` | As in the baseline, plus Stage 2 commercial fields (deferred, flagged) |
| `workforce_requests` | Trade, numbers, dates, essential cards/training, urgency flag |
| `match_generations`, `matches` | Every generation kept; each match carries its pass/fail/review factors and the rules version (explainability retained, register 5.2) |
| `assignment_offers` | Offer + readiness snapshot + expiry of the offer |
| `assignments` | Status sequence retained: PROPOSED → CONFIRMED → COMPLETED, plus CANCELLED and LEGACY_RECORDED; worker and client rates retained (billing on top deferred, LEGAL) |
| `assignment_events` | Status history with actor and note (register 6.2) |
| `assignment_outcomes` | Attended, rating, rehire decision, client and supervisor feedback (register 6.3) |
| `assignment_statements` | Generated statements, one per assignment, versioned (NEW, register 6.6) |

### F. Incidents and complaints (NEW, register Stage 1)

| Table | Purpose |
|---|---|
| `incidents` | Type (no-show, late cancellation, accident, safeguarding, complaint, dispute), severity, status, all parties, resolution |
| `incident_events` | Full timeline of an incident |

### G. Performance evidence

| Table | Purpose |
|---|---|
| `score_events` | Each input event (outcome, feedback) feeding the record |
| `performance_scores` | Score per worker with weights version; "not yet scored" until evidence exists (register 4.1) |

### H. Audit, overrides, and evidence provenance

| Table | Purpose |
|---|---|
| `audit_log` | Append-only: actor, action, table, record, old value, new value, timestamp, reason. No updates or deletes, enforced by database permissions |
| `overrides` | Approver, reason, evidence reference, expiry, scope (one worker, one requirement); an override never edits a check, it temporarily relaxes a specific requirement (NEW, register 7.4) |
| `evidence_records` | Provenance for every verification: source system, method, checker, timestamp, evidence reference, result (register 7.2, extended) |

### I. Commercial records (Stage 1 build, per your pricing email)

| Table | Purpose |
|---|---|
| `price_catalog` | Standard and customer-specific prices, discounts with reasons, waivers, minimums, allowances, VAT treatment, billing frequency, start/review dates — all configurable, nothing hard-coded |
| `service_subscriptions` | Per-contractor switches: managed onboarding, compliance monitoring, training-request coordination |
| `external_costs` | Third-party costs (training providers, identity checks), approval status, agreed-by before incurred |
| `billing_records` | Line items per service period, approval status, Order Form reference |

Invoicing and accounting integration stays out (Stage 2). Prices remain unpublished on the website.

---

## 4. Status models and permitted transitions

**Worker passport:** `DRAFT → IN REVIEW → VERIFIED → EXPIRING SOON → BLOCKED`, plus `ARCHIVED`. A worker can never move backwards except to BLOCKED or ARCHIVED, and only with a recorded reason. VERIFIED requires: identity recorded, RTW recorded with evidence reference, mandatory checks passed per rules version, and human confirmation by Compliance.

**Assignment:** `PROPOSED → CONFIRMED → COMPLETED`, plus `CANCELLED` (from PROPOSED or CONFIRMED) and `LEGACY_RECORDED` (migrated history, read-only). CONFIRMED requires the hard gate. COMPLETED requires an outcome record or an explicit skip with reason.

**Request:** `OPEN → MATCHED → OFFERED → FILLED / CLOSED`. Matches expire (offers carry an expiry), which is the existing offer-snapshot behaviour retained.

**Evidence/check:** `PENDING REVIEW → VERIFIED / REJECTED`, with rejection reason. Worker-submitted evidence always enters as PENDING REVIEW.

Every transition is written by a server function that also writes the audit entry and, where relevant, notifies the parties. Direct table writes are blocked for every role except the server.

---

## 5. Access rules in the database (RLS)

Default deny on every table. Summary of the policy matrix that Stage 0 implements:

| Table group | Owner | Operations | Compliance | Contractor | Worker | Supplier | Auditor |
|---|---|---|---|---|---|---|---|
| Worker identity & documents | full | no documents | full incl. documents | none | own, no documents | scoped view | read |
| Checks, qualifications, training | full | read + submit | verify/reject | own-assignment view | own | scoped | read |
| Readiness, gate, reminders | full | read | full | own-assignment view | own result + reasons | scoped | read |
| Requests, matches, offers | full | full | read | own only | none | scoped (Stage 2) | read |
| Assignments, outcomes, statements | full | full | read | own only + feedback entry | own only | scoped | read |
| Incidents | full | full | full | own-assignment incidents | own cases | scoped | read |
| Performance scores | full | read | read | aggregate only | own | aggregate | read |
| Audit log | read | none | read | none | none | none | read |
| Overrides | approve | request | request | none | none | none | read |
| Commercial (prices, billing) | full | none | none | own subscriptions view | none | none | none |

Identity document *files* live in a private storage bucket; access is via short-lived signed URLs granted only where the matrix allows. Downloads are logged as audit events.

---

## 6. Data protection and retention

| Data class | Retention |
|---|---|
| Right to Work documents | 2 years after the working relationship ends (Home Office guidance), then deleted on schedule |
| Assignment history and reliability record | Lifetime of the passport (register 9, retained) |
| Worker identity documents (non-RTW) | While the passport is active + stated notice period |
| Incident records | Per legal requirement for the incident type |
| Audit log | Indefinite, append-only |
| Contact details of non-joiners | Deleted after an agreed period with notice |

A scheduled job flags approaching retention deadlines to the Owner; nothing is auto-deleted without the Owner's confirmation, and each deletion is audited.

---

## 7. Migration from the demo

The demo's `kv` store is read once, mapped to the new tables, and the result is checked against acceptance tests before cutover. The demo stays available (read-only) until the production system passes acceptance. Migration covers: workers, crews, contractors, projects, sites, workforce requests, match generations, assignments (including LEGACY_RECORDED flags), snapshots and the passport/reference sequences. Demo seed data (Easberg pilot names) is not migrated.

---

## 8. What Stage 0 delivers, in build order

1. Supabase Auth, the seven roles, `profiles`, invitations
2. The schema above (table groups A, C, D, E, G, H) with RLS policies
3. The audit layer on every write path
4. RTW check records with the full field set and evidence provenance
5. The party/engagement structure (values after the opinion)
6. The status engine and the hard deployment gate
7. Migration of the demo data, verified against the register's acceptance tests

**Stage 0 excludes:** billing workflows, statements generation, incidents UI, reminders sending, commercial tables (all Stage 1), integrations (Stage 2), and any AI layer.

---

## 9. Approval

Approving this document approves the schema, roles, statuses, access matrix and retention rules above. Two sections are explicitly open:

- **Section 3B (LEGAL):** the engagement/party *structure* is built now; the *values* (who is the engaging party in the pilot, supplier-statement wording) are finalised after the employment-law opinion, by change request.
- **Section 6 retention periods:** confirm or adjust the periods; they are set as config, not hard-coded.

Reply "approved", or send section numbers you want changed.
