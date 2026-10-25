# PRJGENUI Workforce — Data Protection Impact Assessment (DPIA)

**Version:** 1.1 draft for review with Marizilena Silva Fortes · 25 October 2026
**Status:** to be completed and signed off before any real personal data is
processed (commitment approved 20 October 2026; production gate item).
Revised 25 October 2026 (IINES decision): backup destination moved from
AWS S3 London to Supabase Storage in the same project, free plan; the data
loss row reflects the interim residual risk.

---

## 1. Description of the processing

**Controller:** PRJGENUI Workforce Ltd (company number 13205257, registered
office 124 City Road, London EC1V 2NX). **Processor:** IINES Ltd
(development and support, Article 28 agreement to be executed before any
real personal data is processed).

**What the platform does:** holds Worker Passports (identity, Right to
Work checks, cards, qualifications, training, availability), matches
workers to workforce requests against site-specific requirements, records
assignments and their outcomes, and produces performance and reliability
evidence. Full data classes, lawful bases, retention periods and access
rules are the **GDPR retention and lawful-basis schedule** (sections 2–3);
data sources, recipients and rights are the **privacy notice** (sections
3–8).

**Nature and scope:** workers and crews in Hampshire, Surrey and the wider
South East; categories per the schedule's nine data classes; identity
evidence restricted to Owner/Compliance and the worker's own view; private
object storage with signed, short-lived access only.

**Technology:** Supabase (London, UK — AWS eu-west-2; database, sign-in,
documents and, from 25 October 2026, the weekly encrypted backup copies in
a private Storage bucket — client-side AES-256, 12-week rolling retention;
IINES decision, previously approved as AWS S3 London), Vercel hosting
(limited categories: IPs and request logs, global network, UK
Addendum/IDTA), Zoho email (EU data centre, adequate under UK law).
Processor register: processors.md.

**Profiling and automated processing:** the matching engine and
performance evidence are profiling for the purpose of matching workers to
work: qualification match (including validity), assignment history
(attendance, ratings, rehire decisions, feedback) and reliability factors
with a recorded weights version. **No decision about a person is made
solely automatically** — every compliance, selection and deployment
decision is reviewed and confirmed by a named person before it takes
effect; failed Right to Work checks cannot be overridden by any score or
reviewer (enforced in the platform, migration 0019).

## 2. Consultation

Marizilena Silva Fortes (founder/director and named Owner) has reviewed
and directed the privacy design at every stage: retention schedule and
lawful bases (provisional pending the employment-law opinion), consent
recorded as four categories plus a separate withdrawal record, identity
evidence restriction, audit scrubbing of secrets, MFA for admin roles,
backup standard (9.8), and this DPIA/LIA commitment. Workers are informed
through the versioned privacy notice with a recorded acknowledgement.

## 3. Necessity and proportionality

- **Lawful basis per purpose:** the schedule (section 2) — legal
  obligation for Right to Work, contract for delivery and assignment
  records, legitimate interests for performance evidence and re-matching
  (assessed in the LIA), accountability for audit and consent records.
- **Data minimisation:** fields are operational only; a scan is kept only
  where the scan itself is the record of the check; audit never copies
  secret values; contractors receive only the limited matching and
  assignment information (privacy notice section 8) and never identity
  documents.
- **Retention:** per class, with defined period starts and computed
  deletion-due dates; nothing auto-deleted — deletion is confirmed by
  Owner/Compliance under legal hold controls.
- **Rights:** access, portability, rectification, erasure, restriction,
  objection (separately signposted where legitimate interests apply),
  withdrawal of optional consent; a documented manual DSR process with
  response times (GDPR schedule section 6) and a record-challenge route
  with per-factor breakdowns.

## 4. Risk assessment and mitigations

| Risk to individuals | Assessment | Mitigation | Residual |
|---|---|---|---|
| Profiling/scoring used unfairly or opaquely | Medium — scores influence selection | Explainable per-factor output with recorded weights version; worker sees own breakdown; no solely-automated decisions; compliance failures never overridden by scores (AT-03/AT-24 controls); challenge route | Low |
| Identity document misuse or over-exposure | High impact if it occurred | Private bucket, per-worker storage policies, signed short-lived URLs only; identity evidence visible only to Owner/Compliance and the worker; scans deleted once the check is recorded unless the scan is the record | Low |
| Unlawful or premature live-data use | Medium | Production gate: no real worker data until all gates pass (reconciliation, 25 tests, DPIA/LIA, employment-law opinion, executed processing agreement, final documents, ownership/MFA, email tested, first backup, restoration test) | Controlled by the gate |
| Data loss | Medium | Weekly encrypted export stored in a private Supabase Storage bucket in the same UK project (12-week rolling, changed from AWS S3 London 25 October 2026), key held by the controller, backup and restore actions audited, restoration test before the pilot. Stated plainly: on the free plan this export is the **only** backup (no provider daily backups), and because it sits in the same Supabase account as the primary it does not protect against whole-account loss — residual risk accepted as interim for fictional-data operation | Medium (interim; returns to Low when a separate-provider destination or provider backups are restored) |
| Over-retention | Medium | Per-class retention with computed due dates, confirmed deletion, legal holds exceptional and time-limited, backups age out within 12 weeks | Low |
| Credential compromise | Medium | MFA enforced for admin roles; named accounts only; shared accounts demoted at transfer; no credentials by email | Low |
| International transfer without safeguards | Medium | Transfer mechanisms recorded per provider (processors.md): Supabase London primary, Vercel Addendum/IDTA, Zoho EEA adequacy; sub-processor lists verified before activation | Low |
| Unauthorized bulk extraction | Medium | Role-scoped, audited exports; contractor view scoped to own records; audit of every export; tenant isolation test in the acceptance catalogue | Low |

## 5. Outcome

No high residual risk is identified. The mitigations above are built into
the platform or gated before live use. This DPIA is reviewed with the
controller before any real personal data is processed, and re-reviewed on
any material change (new service, new processor, new automated decision,
or international expansion).

**Sign-off:** Marizilena Silva Fortes (controller) and the development
lead, before real personal data is processed.
