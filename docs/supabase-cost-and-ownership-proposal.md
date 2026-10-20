# PRJGENUI Workforce — Supabase Cost, Ownership and Backup Proposal

**Version:** 1.1 for approval · 20 October 2026
**For approval by:** Marizilena Silva Fortes
**Covers:** register 9.8 activation (plan cost, account ownership, backup
destination and key recovery, restoration test)

---

## 1. What you are approving

1. The **Supabase Pro plan and all-in monthly cost** (section 2) — approved
   by you 20 October 2026, with the spend cap required to stay on and no
   additional paid service (PITR, custom domains) activated without your
   written approval.
2. The **account ownership transfer** (section 3), to proceed only after
   your named Owner account and MFA have been tested successfully.
3. The **named encrypted backup destination and key-recovery procedure**
   (sections 4–5): AWS S3 London, approved by you 20 October 2026.

## 2. All-in monthly cost

The platform needs the **Supabase Pro** plan. On the free plan the project
pauses after a week without traffic, backups are minimal, and production
use is not appropriate. Pro prices (verified against supabase.com pricing;
the invoice is in USD; you activate the plan yourself from your account
after the transfer):

| Line | Amount | Notes |
|---|---|---|
| Pro plan subscription | **$25/month per organization** | Includes the first project; additional projects start at $10/month (we need one) |
| Compute | **$0 extra at pilot scale** | Pro includes a $10/month compute credit, which exactly covers the base Micro instance (1 GB RAM) the platform needs |
| Database size | **$0 at pilot scale** | 8 GB included per project; the platform database is well under this |
| File storage (worker documents) | **$0 at pilot scale** | 100 GB included |
| Bandwidth | **$0 at pilot scale** | 500 GB included (250 GB egress + 250 GB cached) |
| Auth users | **$0 at pilot scale** | 100,000 monthly active users included |
| Daily backups | Included | 7-day retention on Pro |
| Backup destination (AWS S3 London) | Measured estimate: see section 4 | Well inside the £5/month approval threshold |
| **Expected total at pilot scale** | **$25/month (≈ £20/month) plus any tax/VAT and pence-level backup charges** | Tax treatment is confirmed on the first invoice |

What is deliberately **not** included, stated plainly so nothing surprises
you later:

- If usage grows past the included quotas, the overage rates are:
  database size $0.125/GB-month, file storage $0.0213/GB-month, egress
  $0.09/GB-month (cached $0.03). At pilot scale we do not expect to touch
  any of them.
- The **spend cap stays enabled** (it is the Pro default, and your
  instruction), so if something runs away the service throttles rather
  than generating a surprise bill.
- Point-in-time recovery ($100/month) and custom domains ($10/month) are
  **not** being purchased; neither is needed, and none may be activated
  without your written approval.

## 3. Account ownership transfer

The transfer proceeds **only after your named Owner account and MFA have
been tested successfully**. Until then IINES remains the interim operator
at its own cost; the Pro plan and backups activate only after your
approval, at the same time as the transfer.

1. You create a Supabase account for
   `marizilena@prjgenuiworkforce.co.uk` (or we create it with you) and
   enable two-factor on it.
2. We create a **PRJGENUI organisation** in Supabase and make your account
   its **Owner**.
3. We **transfer the project** into that organisation (Supabase supports
   moving a project between organisations).
4. You add your payment method in Supabase billing and **you activate the
   Pro plan** from your account — IINES never sees your payment details
   and has **no billing access**.
5. Access for development and support continues only through **named
   IINES accounts with developer-level access** — individual named
   accounts only, no shared or temporary administrative access. All
   current shared or temporary administrative access (including the
   hello@ account) is **removed or demoted** as part of the transfer.
6. The **database password is rotated during the transfer**: you set the
   new one in the Supabase dashboard yourself (never by email), and it is
   stored only in the platform's protected secret storage. The current
   password stops working at that moment.
7. The **Vercel project is transferred to PRJGENUI ownership** on the
   same pattern: you are invited as owner, the project transfers to
   PRJGENUI's Vercel account, and IINES retains only deployment access
   through named accounts.
8. **Written confirmation is provided after each step**, as it completes.

## 4. Named backup destination and measured cost (register 9.8)

Approved by you 20 October 2026:

- **Provider:** Amazon Web Services S3, **London region (`eu-west-2`,
  UK)** — the same UK region as the production database, in a **dedicated
  AWS account owned by PRJGENUI**, used for nothing else.
- **Retention:** **12 weeks rolling** (your decision, 20 October 2026) —
  12 weekly exports, with the oldest deleted when the 13th is created;
  to be reviewed after the pilot if operational evidence shows a longer
  period is necessary.
- **Encryption:** every export is encrypted **before it leaves the
  production account** (AES-256, client-side); AWS holds ciphertext only
  and never the key.
- **Audit:** bucket access is restricted to the named people in 9.8, and
  every access and restoration attempt is recorded through **AWS
  CloudTrail data events**, with those audit records **protected
  separately** from the backup objects (a separate log store with
  restricted access).
- AWS is recorded in the processor register (processors.md) as the backup
  storage provider, effective at activation.

**Measured cost estimate** (measured 20 October 2026; to be re-measured
and recorded after the first complete export):

| Component | Measured today | Realistic pilot projection |
|---|---|---|
| Database export | 14.5 MB (database size, platform currently empty) | ~50–150 MB |
| Document Storage files | 0 MB (no documents yet) | ~0.5–1 GB (e.g. 100 workers × ~5 documents at 1–2 MB) |
| One weekly export | ~15 MB | ~0.5–1 GB |
| 12 retained weekly copies | ~175 MB | ~6–12 GB |
| S3 storage, London ($0.024/GB-month) | < $0.01/month | ~$0.15–0.30/month (≈ £0.12–0.25) |
| S3 requests (PUT $0.005/1,000) | negligible | negligible |
| CloudTrail S3 data events ($1.50/100,000 events) | negligible (weekly export/restore volumes) | negligible |
| Encryption / key management | **$0** — client-side AES-256, the key never touches AWS (no AWS KMS) | $0 |
| **Total backup cost** | **< £0.01/month** | **≈ £0.12–0.25/month** |

- A **monthly cost alert** is established on the AWS bill; if the backup
  service is expected to exceed **£5 in any month**, you are asked for
  approval before it does.
- The estimate is re-measured after the first complete export (database +
  Storage files + 12 retained copies + storage, request, audit-logging and
  encryption charges) and recorded in this proposal and register 9.8.

## 5. Key custody and recovery (your five questions, answered exactly)

- **Where the controlling key is stored.** Each weekly export is encrypted
  with its own freshly generated passphrase (AES-256) before it leaves the
  production account. The passphrases are recorded in a **key record** held
  in exactly two places: the **Owner's own secure store** (your password
  manager, plus a printed copy in a sealed envelope at the registered
  office), and the **named IINES administrator's encrypted store during
  the interim**. The key is never stored with the export, never in the
  repository, never with AWS.
- **Who can use it.** Only the named Owner account (you) and, during the
  interim, the one named IINES administrator. Nobody else holds backup
  credentials or key material (9.8 point 6).
- **How PRJGENUI recovers the backups if the IINES administrator is
  unavailable.** The Owner's copy of the key record is **complete** — it
  contains every export passphrase — so decryption and restoration never
  depend on IINES being available. The restoration procedure (section 6)
  is written so a person holding only the Owner's key record and the
  backup account credentials can restore the platform.
- **How keys are rotated.** A fresh passphrase is generated for every
  export, so rotation is continuous by construction. The custodian list is
  re-confirmed quarterly; on any change of custodian the key record is
  transferred to the new custodian and the old copy's destruction is
  confirmed and recorded. At the ownership transfer, interim IINES custody
  ends: the sole custodian from then is PRJGENUI (your account), and the
  IINES copy is confirmed destroyed.
- **Decryption tested during the restoration exercise.** Yes — every
  restoration test begins by decrypting the most recent export with the
  key record, and the test is only a pass if decryption and full
  restoration both succeed; the test record states this (section 6).

## 6. Restoration test (before the pilot)

1. A fresh, temporary Supabase project is created (no cost — free tier is
   fine for a restore target).
2. The most recent weekly export is **decrypted with the key record** and
   **restored into it: the database records and the Storage files both**.
3. Verified: worker records, qualification and readiness statuses,
   documents openable, audit log intact — against a checklist derived from
   the acceptance catalogue (register section 16).
4. The test is recorded per your seven-point standard: **date, scope,
   outcome, and that decryption succeeded**, and the record is kept with
   the register (9.8).
5. The temporary project is deleted after the test (it contains a full
   copy of live data, so it is destroyed the same day and its deletion is
   recorded).

## 7. What we need from you

1. Your MFA enrolment and a successful test of your named Owner account —
   the transfers, the backup activation and the SMTP secret all follow it.
2. The Zoho actions in the email delivery setup (DKIM, DMARC, the
   `dmarc-reports@` alias, the `system@` mailbox and its app-specific
   password).
3. Your approval of the frozen Stage 2 build (register section 16), so
   the remaining acceptance tests can be implemented and the full
   catalogue executed.
