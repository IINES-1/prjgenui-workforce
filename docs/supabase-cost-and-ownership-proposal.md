# PRJGENUI Workforce — Supabase Cost, Ownership and Backup Proposal

**Version:** 1.0 for approval · 3 March 2026
**For approval by:** Marizilena Silva Fortes
**Covers:** register 9.8 activation (plan cost, account ownership, backup
destination and restoration test)

---

## 1. What you are approving

1. The **Supabase plan and all-in monthly cost** (section 2).
2. The **account ownership transfer** so PRJGENUI owns and pays for its own
   platform (section 3).
3. The **named encrypted backup destination** and the restoration-test
   procedure (sections 4–5).

## 2. All-in monthly cost

The platform needs the **Supabase Pro** plan. On the free plan the project
pauses after a week without traffic, backups are minimal, and production
use is not appropriate. Pro prices (verified against supabase.com pricing,
current as at August 2026 reporting; the invoice is in USD):

| Line | Amount | Notes |
|---|---|---|
| Pro plan subscription | **$25/month per organization** | Includes the first project; additional projects start at $10/month (we need one) |
| Compute | **$0 extra at pilot scale** | Pro includes a $10/month compute credit, which exactly covers the base Micro instance (1 GB RAM) the platform needs |
| Database size | **$0 at pilot scale** | 8 GB included per project; the platform database is well under this |
| File storage (worker documents) | **$0 at pilot scale** | 100 GB included |
| Bandwidth | **$0 at pilot scale** | 500 GB included (250 GB egress + 250 GB cached) |
| Auth users | **$0 at pilot scale** | 100,000 monthly active users included |
| Daily backups | Included | 7-day retention on Pro |
| **Expected total at pilot scale** | **$25/month (≈ £20/month) plus any tax/VAT** | Tax treatment is confirmed on the first invoice; recent exchange rates put this near £20/month |

What is deliberately **not** included, stated plainly so nothing surprises
you later:

- If usage grows past the included quotas, the overage rates are:
  database size $0.125/GB-month, file storage $0.0213/GB-month, egress
  $0.09/GB-month (cached $0.03). At pilot scale we do not expect to touch
  any of them.
- The **spend cap stays enabled** (it is the Pro default), so if something
  runs away the service throttles rather than generating a surprise bill.
- Point-in-time recovery ($100/month) and custom domains ($10/month) are
  **not** being purchased; neither is needed for this platform.
- The backup destination (section 4) adds well under £1/month at pilot
  scale.

## 3. Account ownership transfer

Today the Supabase project sits in an organisation IINES controls, with
IINES paying. The transfer makes PRJGENUI the owner and the payer:

1. You create a Supabase account for
   `marizilena@prjgenuiworkforce.co.uk` (or we create it with you) and
   enable two-factor on it.
2. We create a **PRJGENUI organisation** in Supabase and make your account
   its **Owner**.
3. We **transfer the project** into that organisation (Supabase supports
   moving a project between organisations).
4. You add your payment method in Supabase billing and **you activate the
   Pro plan** from your account — IINES never sees your payment details.
5. Access for development and support continues only through **named
   IINES accounts with developer-level access**, no billing access, and
   every administrative action still goes through the audited platform
   functions.
6. The **database password** is rotated at transfer: you set the new one
   in the Supabase dashboard yourself (never by email), and it is stored
   only in the platform's protected secret storage. The current password
   stops working at that moment.
7. The Vercel hosting account follows the same pattern: you are invited as
   owner, the project transfers to PRJGENUI's Vercel account, and IINES
   retains only deployment access.

Until the transfer, IINES remains the interim operator at its own cost; the
Pro plan and backups activate only after your approval, at the same time as
the transfer.

## 4. Named backup destination (register 9.8, point 2)

Proposed, for your approval:

- **Provider:** Amazon Web Services S3, **London region (`eu-west-2`,
  UK)** — the same UK region as the production database, in a **dedicated
  AWS account owned by PRJGENUI**, used for nothing else.
- **Separation:** separate account from both the production Supabase
  account and its host; the backup account holds only the encrypted
  exports.
- **Encryption:** every weekly export is encrypted **before it leaves the
  production account** (AES-256, a fresh passphrase per export held by the
  named administrators only — see 9.8 points 5–6). AWS never holds the key
  and cannot read the contents.
- **Retention:** exactly **12 months rolling** — 52 weekly exports, oldest
  deleted when the 53rd lands (9.8 point 4).
- **Access and audit:** bucket access restricted to the named people in
  9.8 point 6; AWS **access logging enabled on the bucket** so every
  access and every restoration attempt is logged with who, what, when, and
  those logs are reviewable alongside the platform audit trail (9.8 point
  7).
- **Cost:** at pilot scale (a few GB per export) this is well under
  £1/month; it will be on the same AWS bill as nothing else — a standalone
  PRJGENUI bill.
- AWS is added to the processor list (processors.md) as the backup storage
  provider when you approve this.

Interim custody before the transfer completes: the same destination, with
one named IINES administrator holding access alongside your account, per
9.8 point 6.

## 5. Restoration test (before the pilot)

1. A fresh, temporary Supabase project is created (no cost — free tier is
   fine for a restore target).
2. The most recent weekly export is decrypted and **restored into it:
   the database records and the Storage files both**.
3. Verified: worker records, qualification and readiness statuses,
   documents openable, audit log intact — against a checklist derived from
   the acceptance catalogue.
4. The test is recorded per your seven-point standard: **date, scope,
   outcome**, and the record is kept with the register (9.8).
5. The temporary project is deleted after the test (it contains a full
   copy of live data, so it is destroyed the same day and its deletion is
   recorded).

The first restoration test runs before the pilot, once you approve this
proposal and the first weekly exports exist.

## 6. What we need from you

1. "Approved" on this proposal, or your amendments.
2. Your go-ahead to create the `marizilena@prjgenuiworkforce.co.uk`
   Supabase account and organisation (you set the password and MFA
   yourself; nothing is sent by email).
3. Confirmation of the DPIA/LIA commitment (privacy notice section 10) so
   the privacy notice can be finalised with it.
4. The technical handover pack, company/system manual and checksum record
   from your 0.3-E package, for the register's acceptance catalogue.
