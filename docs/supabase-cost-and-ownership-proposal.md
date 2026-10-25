# PRJGENUI Workforce — Supabase Cost, Ownership and Backup Proposal

**Version:** 1.2 revised · 25 October 2026
**For:** Marizilena Silva Fortes (positions 1 and 3 below were approved by
you on 20 October 2026; on 25 October 2026 IINES Ltd, which now controls
the project, decided to run on the **free plan** with **Supabase-stored
backups and no AWS** — the differences are stated plainly in sections 2
and 4 and should be confirmed with you)
**Covers:** register 9.8 activation (plan cost, account ownership, backup
destination and key recovery, restoration test)

---

## 1. What is decided and what is approved

1. The **Supabase plan** — you approved the **Pro plan ($25/month)** on
   20 October 2026. **Changed 25 October 2026 (IINES decision): the
   platform stays on the free plan ($0/month)** for now. The consequences
   are stated in section 2. The upgrade to Pro is to be revisited before
   any real worker data is processed.
2. The **account ownership transfer** (section 3), unchanged, to proceed
   only after your named Owner account and MFA have been tested
   successfully.
3. The **encrypted backup destination and key-recovery procedure**
   (sections 4–5) — you approved **AWS S3 London** on 20 October 2026.
   **Changed 25 October 2026 (IINES decision): backups are stored in a
   Supabase Storage bucket in the same project as the database — no AWS
   account is used.** Retention stays **12 weeks rolling** and the
   client-side encryption and key-custody procedure you approved is
   unchanged. The trade-off is stated plainly in section 4.

## 2. All-in monthly cost and what the free plan means

**Cost: $0/month.** Nothing is paid, so the spend cap and the
written-approval rule for paid extras are satisfied by construction; they
still apply if a paid service is ever considered.

What the free plan does **not** include, stated plainly so nothing
surprises anyone later:

- **No provider backups at all.** Pro's daily backups (7-day retention)
  do not exist on the free plan, so the weekly encrypted export
  (section 4) is the **only** backup. There is no second line of
  recovery until the plan is upgraded.
- **The project pauses after about a week without activity** (free-plan
  behaviour; the dashboard would go offline until someone unpauses it).
  Mitigation: a scheduled keep-alive check runs daily against the
  database so the project stays active. This is a workaround, not a
  guarantee.
- **File storage is capped at 50 MB.** Worker documents (Right to Work
  evidence, cards, certificates) live in Storage, and at a realistic
  ~1–2 MB per document the cap is reached after a few dozen documents —
  long before a pilot of 100 workers. The backup copies (section 4)
  share the same 50 MB. **This is the first thing that forces the Pro
  upgrade.**
- Database (500 MB), bandwidth (5 GB) and auth-user quotas are ample at
  pilot scale.

Upgrade trigger, recorded exactly: **the plan is upgraded to Pro when
real worker data begins, when document storage approaches the free cap,
or at your instruction — whichever comes first.**

## 3. Account ownership transfer

Unchanged from v1.1: the transfer proceeds **only after your named Owner
account and MFA have been tested successfully**.

1. You create a Supabase account for
   `marizilena@prjgenuiworkforce.co.uk` (or we create it with you) and
   enable two-factor on it.
2. We create a **PRJGENUI organisation** in Supabase and make your
   account its **Owner**.
3. We **transfer the project** into that organisation.
4. If and when a paid plan is activated, **you add the payment method and
   activate it yourself** — IINES never sees payment details and has no
   billing access.
5. Access for development and support continues only through **named
   IINES accounts with developer-level access** — no shared or temporary
   administrative access. All current shared or temporary administrative
   access (including the hello@ account) is **removed or demoted** as part
   of the transfer.
6. The **database password is rotated during the transfer**: you set the
   new one in the Supabase dashboard yourself (never by email). The
   current password stops working at that moment.
7. The **Vercel project is transferred to PRJGENUI ownership** on the
   same pattern.
8. **Written confirmation is provided after each step**, as it completes.

## 4. Backup destination, retention and measured size (register 9.8)

Changed 25 October 2026 (IINES decision; previously approved as AWS S3
London, 20 October 2026):

- **Provider:** **Supabase Storage, same project as the database** — a
  dedicated `backups` bucket, private, no public access. No AWS account
  is used.
- **Retention:** **12 weeks rolling** (your decision, 20 October 2026,
  unchanged) — 12 weekly exports, with the oldest deleted when the 13th
  is created; to be reviewed after the pilot.
- **Encryption:** unchanged — every export is encrypted **before upload**
  (AES-256, client-side); Supabase holds ciphertext only and never the
  key. The key record is held per section 5.
- **Audit:** every backup upload, deletion and restoration attempt is
  recorded in the platform's **audit log** (who, when, what), which is
  itself part of the export. There is no CloudTrail equivalent because
  there is no AWS account.
- **Cost:** $0 within the free quota. The copies share the 50 MB free
  storage cap with worker documents (section 2), so the export size is
  re-measured after the first complete export.

**The trade-off, stated plainly:** the backup sits in the **same Supabase
account as the primary data**. It protects against data loss, corruption
and accidental deletion, and it survives a database-level failure. It
does **not** protect against the whole Supabase account being locked,
deleted or compromised — that protection was the reason for the approved
separate-provider destination, and it is given up until the plan and
destination are revisited. This is accepted as an interim position for a
platform holding fictional data only.

**Measured size** (measured 20 October 2026; database 14.5 MB, Storage
empty): one compressed export is expected at roughly 1–2 MB today, so 12
retained copies are ~12–25 MB — inside the free cap now, tight once real
documents exist. Re-measured after the first complete export.

## 5. Key custody and recovery (your five questions, answered exactly)

Unchanged from v1.1, with the destination references updated:

- **Where the controlling key is stored.** Each weekly export is encrypted
  with its own freshly generated passphrase (AES-256) before upload. The
  passphrases are recorded in a **key record** held in exactly two places:
  the **Owner's own secure store** (your password manager, plus a printed
  copy in a sealed envelope at the registered office), and the **named
  IINES administrator's encrypted store during the interim**. The key is
  never stored with the export, never in the repository, and never in the
  platform's own storage alongside the backup copies.
- **Who can use it.** Only the named Owner account (you) and, during the
  interim, the one named IINES administrator. Nobody else holds backup
  credentials or key material (9.8 point 6).
- **How PRJGENUI recovers the backups if the IINES administrator is
  unavailable.** The Owner's copy of the key record is **complete** — it
  contains every export passphrase — so decryption and restoration never
  depend on IINES being available. The restoration procedure (section 6)
  is written so a person holding only the Owner's key record and the
  platform account credentials can restore the platform.
- **How keys are rotated.** A fresh passphrase is generated for every
  export, so rotation is continuous by construction. The custodian list is
  re-confirmed quarterly; on any change of custodian the key record is
  transferred and the old copy's destruction is confirmed and recorded.
  At the ownership transfer, interim IINES custody ends and the IINES
  copy is confirmed destroyed.
- **Decryption tested during the restoration exercise.** Yes — every
  restoration test begins by decrypting the most recent export with the
  key record, and the test is only a pass if decryption and full
  restoration both succeed (section 6).

## 6. Restoration test (before the pilot)

1. A fresh, temporary Supabase project is created (free tier is fine for
   a restore target).
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
   the transfers and the SMTP secret follow it.
2. The Zoho actions in the email delivery setup (DKIM, DMARC, the
   `dmarc-reports@` alias, the `system@` mailbox and its app-specific
   password).
3. Your confirmation of the changed positions in sections 1 and 3 of
   this document (free plan, Supabase-stored backups), and your approval
   of the frozen Stage 2 build (register section 16).
