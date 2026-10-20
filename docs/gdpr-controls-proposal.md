# PRJGENUI Workforce — GDPR retention and lawful-basis schedule (register 10.4)

**Version:** 2.3 draft for review · 20 October 2026 (backup retention 12 weeks rolling, per your decision; consent framed as four categories plus a separate withdrawal record, per your confirmation)
**For approval by:** Marizilena Silva Fortes
**Register item:** 10.4 — retention per data class, restricted access to identity
documents, recorded lawful basis and consent.

This revision follows the review framework you set out: every data category
now shows the type of information, its purpose, the proposed lawful basis, the
retention period and when it starts, what happens at the end, the
justification, who can access it, and how a legal hold works. Consent is
recorded as separate, specific events, never one general box.

Lawful bases below are **provisional** until the employment-law opinion; the
opinion may move individual entries, and where it does the basis is updated
and the record re-flagged rather than silently changed. No row should be
treated as settled legal advice.

---

## 1. What is already in place

- **Identity document access is restricted.** Only Owner and Compliance can
  open identity evidence. Workers see their own documents; Operations,
  contractors and auditors cannot open them.
- **Document metadata carries a retention class and a deletion due date** on
  every worker document row.
- **Every write is audited** — who, what, when, including overrides,
  approvals and status changes.
- **The audit log never copies sensitive values** (since migration 0018):
  invitation tokens, share codes, credentials and recovery codes are scrubbed
  from every audit entry before it is written, and earlier entries were
  cleaned in the same pass. The audit trail records that a change happened
  and to which row, not the secret values themselves.
- **Two-factor sign-in is enforced for admin accounts** (Owner, Operations,
  Compliance): an authenticator-app code is required before the dashboard
  unlocks, so worker data is not reachable on a password alone.
- **Qualifications without an expiry date are first-class records**: NVQs and
  similar permanent or renewable qualifications are recorded with an explicit
  validity marker and are never rejected for a missing expiry date.

## 2. Retention and lawful-basis schedule

Legend for "At end of period": **delete** = row and any Storage file removed
after Compliance confirms; **review** = flagged for a Compliance decision
before any deletion; nothing is ever auto-deleted.

| # | Data class | Information held | Purpose | Proposed lawful basis | Retention | Period starts | At end | Justification | Access | Legal hold |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Right to Work evidence | Share-code result, check method, date, restrictions, follow-up date; scan where a scan was unavoidable | Demonstrating the right-to-work check and its outcome | Legal obligation (right-to-work legislation) | Relationship end + 2 years | End of the worker's engagement with PRJGENUI | delete | Home Office right-to-work evidence guidance | Owner, Compliance; worker sees own record | Hold suspends deletion while a dispute, claim or investigation is live |
| 2 | Identity documents (scans) | Passport/ID scans in Storage | Supporting verification; the evidence itself where the scan forms part of the right-to-work record | Legal obligation, plus contract; kept only where unavoidable | Deleted once the check is recorded and verified — **except where the scan itself is part of the right-to-work record you must keep** (for example, where a Home Office share code could not be used and the document scan is the evidence of the check). Those scans are retained under row 1 and deleted with it | Verification of the check (row 1's rule where the scan is the record) | delete (immediately after verification; with row 1 where the scan is the record) | Data minimisation: the recorded check, not the scan, is the evidence wherever a share code is available | Owner, Compliance only | Follows row 1 where the scan is part of the record |
| 3 | Cards, qualifications, training | CSCS and trade cards, certificates, status, expiry, validity (expiring / renewable / permanent) | Confirming site and role requirements | Contract; legitimate interests for re-matching | Expiry + 2 years. **Qualifications with no expiry (permanent, e.g. NVQ; some City & Guilds) are never rejected for a missing expiry date** — for them the period is relationship end + 2 years; renewable qualifications run from the next renewal date | Expiry date of the card or certificate; relationship end for permanent qualifications; next renewal date for renewable ones | delete | Re-issue and dispute defence | Owner, Operations, Compliance; worker sees own | Yes |
| 4 | Assignment history and outcomes | Attendance, rating, rehire decision, client and supervisor feedback | Delivering and evidencing the assignment | Contract (the supply agreement) | Relationship end + 6 years | End of the worker's engagement | review, then delete | Contract and wage-claim limitation periods | Owner, Operations, Compliance, Auditor; contractor sees own assignment statement | Yes |
| 5 | Performance and reliability evidence | Scores, bands, per-factor breakdown, weights version | Matching quality and honest records | Legitimate interests, balanced against the worker's rights | Relationship end + 6 years | End of the worker's engagement | review, then delete | Matching quality; worker sees their own breakdown | As above; worker sees own record | Yes |
| 6 | Commercial records | Prices, discounts and reasons, waivers, service switches, external costs | Contract administration and billing | Contract; legal obligation for tax records | 6 years | Creation of the record, or invoice period end where later | delete | Tax (HMRC) and contract limitation periods | Owner only | Yes |
| 7 | Party records and engagements | Who engages, pays, introduces, operates the check, performs it | Evidencing who did what, per your party model | Legal obligation (right-to-work defence); contract | Relationship end + 2 years | End of the relevant relationship | delete | Mirrors the right-to-work defence period | Owner, Compliance, Auditor | Yes |
| 8 | Consent and acknowledgement records | The events in section 4, with statement versions and timestamps | Accountability (UK GDPR record-keeping) | Legal obligation (accountability); legitimate interests | Life of the relationship + 6 years | The recorded event | delete | Proving the lawful basis and what was agreed | Owner, Compliance; the person sees their own record | Yes |
| 9 | Audit log | Every write: old and new values, who, when | Platform-wide accountability | Legal obligation (accountability); legitimate interests | 6 years | The audited event | delete | Same limitation as the records described | Owner, Compliance, Auditor (read-only) | Yes — audit entries are never deleted during a hold |

Where a legal minimum exceeds these periods (for example an HMRC or
employment-law requirement), the longer period wins and the class is
re-flagged with the justification.

### "Relationship end", defined per row

"Relationship end" is not one date for every class. Where a row above runs
from relationship end, it means:

- **Rows 1, 2 (where the scan is the record), 3 (permanent qualifications)
  and 7** — the last of: the end date of the worker's last assignment, or,
  if the worker was never assigned, the date the worker record was archived
  or declined.
- **Rows 4 and 5** (assignment history, performance evidence) — the end date
  of the worker's last assignment, or, if never assigned, the date the
  worker record was archived or declined. If an assignment ends but the
  worker stays active, the clock does not start.
- **Row 8** (consent records) — the same date as rows 4–5, so the consent
  evidence outlives the engagement it evidences.
- **Row 7 for contractor and party records** — the end of the relevant
  commercial relationship: the termination or expiry of the supply
  agreement or framework.

The platform records the trigger date on the record when it happens, so the
retention date is computed, not re-interpreted later.

## 3. How retention works mechanically

- Every class above has, or gets, a `deletion_due`-style date; those already
  exist on worker documents.
- The Compliance Action Centre gains a "Retention due" group: class, record,
  due date, recommended action ("delete document", "confirm retention").
- Nothing is deleted automatically. Deletion is confirmed by Owner or
  Compliance and audited.
- A **legal hold** is set by Owner or Compliance on a worker, contractor or
  class. Holds are **exceptional**: each one needs a recorded reason tied to
  a live dispute, claim or investigation, is time-stamped, and is reviewed
  at least every 6 months and lifted as soon as it is no longer needed. A
  hold hides the item from the "Retention due" group and blocks the delete
  action until it is lifted. Holds are audited like everything else.
- **Backups sit inside the retention framework.** The weekly export
  (register 9.8) has its own exact retention period, per your decision of
  20 October 2026: **12 weeks, rolling** — 12 weekly exports, with the
  oldest deleted when the 13th is created, so no export is ever older
  than 12 weeks (to be reviewed after the pilot if operational evidence
  shows a longer period is necessary). When live records are deleted
  under this schedule, the corresponding rows leave the next and
  subsequent exports, so deleted data ages out of the backup chain
  within at most 12 weeks rather than persisting indefinitely. The
  data-subject-rights process in section 6 states this plainly to anyone
  who asks.
- The weekly export (register 9.8) lists what exists per class, so
  data-subject requests can be answered from a current inventory.

## 4. Consent, acknowledgement and declarations — recorded as separate events

You are right that one general consent box cannot carry the processing. The
system records **four acceptance/declaration categories plus a separate
withdrawal record** — five distinct, separately-timestamped records, each
with its own statement version and account identity, and none of them is
treated as the lawful basis on its own — the lawful basis per purpose is
the schedule in section 2.

| Event | What it records | Where it happens | Withdrawable? |
|---|---|---|---|
| **Privacy-notice acknowledgement** | The worker was shown the privacy notice (versioned text, timestamp) | First sign-in | No — it evidences that notice was given |
| **Platform terms acceptance** | The worker accepted the terms of use of the platform | First sign-in | Withdrawal closes the account; the terms govern use of the platform |
| **Legal/contractual declaration** | Confirmations required to enter the arrangement (e.g. confirming the accuracy of what they submitted, and their right to work) | Invitation acceptance and first sign-in | No — it is a declaration, not consent |
| **Optional consent** | Genuinely optional processing only, e.g. being included in marketing/news updates, if ever offered | Separate prompt, unticked by default, plain language | Yes, at any time, without affecting any other function |
| **Withdrawal of consent** | The withdrawal itself, and which consent it applied to | A control in the worker's own passport | Records the withdrawal |

No optional consent is required for registration, matching, assignments,
statements or any core function. Withdrawing it never blocks a worker from
exercising unrelated rights.

## 5. What this proposal deliberately does not do yet

- No automated deletion or auto-expiry of accounts.
- No in-platform data-subject-request workflow — the manual process in
  section 6 covers requests until volumes justify tooling.
- No special-category data beyond what right-to-work lawfully requires.

## 6. Data-subject rights — the manual process

Requests (access, rectification, erasure, restriction, objection, portability)
arrive by email to hello@prjgenuiworkforce.co.uk or through the contact page.
Until request volumes justify an in-platform workflow, each one is handled
manually, and every step is recorded in the audit log:

1. **Acknowledge** within 3 working days; the 1-month statutory clock and the
   request text are recorded in a request log (who asked, when, for what).
2. **Verify identity** against the worker record — never by collecting new
   copies of identity documents beyond what is already held.
3. **Compile the response** from the platform inventory: the per-class
   export (register 9.5) plus the worker's own documents, filtered to the
   requester. Owner or Compliance compiles; Owner approves the response.
4. **Answer within 1 month**, extending by up to 2 further months only with
   a written reason sent inside the first month.
5. **Erasure requests** are honoured where no lawful basis or legal
   obligation (rows 1, 6, 8, 9) requires retention; where retention is
   required, the response says which rows are retained, why, and for how
   long. Nothing is erased while a legal hold is live.
6. **Rectification requests** can be actioned by the worker directly for
   their own details (worker self-service); other corrections are made by
   Operations or Compliance with the change audited.
7. **Backups**: erasure applies to live data immediately; the corresponding
   rows leave the next weekly export and age out of the backup chain within
   at most 12 weeks (the backup retention period, section 3). This is
   stated plainly in the response.

---

## Approval

Reply "approved" to accept the schedule and the consent model (four
acceptance/declaration categories plus a separate withdrawal record), or
list the row numbers (1-9) or sections (3-6) you want discussed first.
Lawful bases stay provisional until the employment-law opinion, as stated in
the introduction.
