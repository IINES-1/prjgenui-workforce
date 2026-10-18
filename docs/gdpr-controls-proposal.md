# PRJGENUI Workforce — GDPR retention and lawful-basis schedule (register 10.4)

**Version:** 2.0 draft for review · 18 October 2026
**For approval by:** Marizilena Silva Fortes
**Register item:** 10.4 — retention per data class, restricted access to identity
documents, recorded lawful basis and consent.

This revision follows the review framework you set out: every data category
now shows the type of information, its purpose, the proposed lawful basis, the
retention period and when it starts, what happens at the end, the
justification, who can access it, and how a legal hold works. Consent is
recorded as separate, specific events, never one general box.

Lawful bases below are proposals; the employment-law opinion may move
individual entries, and where it does the basis is updated and the record
re-flagged rather than silently changed.

---

## 1. What is already in place

- **Identity document access is restricted.** Only Owner and Compliance can
  open identity evidence. Workers see their own documents; Operations,
  contractors and auditors cannot open them.
- **Document metadata carries a retention class and a deletion due date** on
  every worker document row.
- **Every write is audited** — who, what, when, including overrides,
  approvals and status changes.

## 2. Retention and lawful-basis schedule

Legend for "At end of period": **delete** = row and any Storage file removed
after Compliance confirms; **review** = flagged for a Compliance decision
before any deletion; nothing is ever auto-deleted.

| # | Data class | Information held | Purpose | Proposed lawful basis | Retention | Period starts | At end | Justification | Access | Legal hold |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Right to Work evidence | Share-code result, check method, date, restrictions, follow-up date; scan where a scan was unavoidable | Demonstrating the right-to-work check and its outcome | Legal obligation (right-to-work legislation) | Relationship end + 2 years | End of the worker's engagement with PRJGENUI | delete | Home Office right-to-work evidence guidance | Owner, Compliance; worker sees own record | Hold suspends deletion while a dispute, claim or investigation is live |
| 2 | Identity documents (scans) | Passport/ID scans in Storage | Supporting verification only | Legal obligation, plus contract; kept only where unavoidable | Deleted once the check is recorded and verified | Verification of the check | delete (immediately after verification) | Data minimisation: the recorded check, not the scan, is the evidence | Owner, Compliance only | N/A — not retained |
| 3 | Cards, qualifications, training | CSCS and trade cards, certificates, status, expiry | Confirming site and role requirements | Contract; legitimate interests for re-matching | Expiry + 2 years | Expiry date of the card or certificate | delete | Re-issue and dispute defence | Owner, Operations, Compliance; worker sees own | Yes |
| 4 | Assignment history and outcomes | Attendance, rating, rehire decision, client and supervisor feedback | Delivering and evidencing the assignment | Contract (the supply agreement) | Relationship end + 6 years | End of the worker's engagement | review, then delete | Contract and wage-claim limitation periods | Owner, Operations, Compliance, Auditor; contractor sees own assignment statement | Yes |
| 5 | Performance and reliability evidence | Scores, bands, per-factor breakdown, weights version | Matching quality and honest records | Legitimate interests, balanced against the worker's rights | Relationship end + 6 years | End of the worker's engagement | review, then delete | Matching quality; worker sees their own breakdown | As above; worker sees own record | Yes |
| 6 | Commercial records | Prices, discounts and reasons, waivers, service switches, external costs | Contract administration and billing | Contract; legal obligation for tax records | 6 years | Creation of the record, or invoice period end where later | delete | Tax (HMRC) and contract limitation periods | Owner only | Yes |
| 7 | Party records and engagements | Who engages, pays, introduces, operates the check, performs it | Evidencing who did what, per your party model | Legal obligation (right-to-work defence); contract | Relationship end + 2 years | End of the relevant relationship | delete | Mirrors the right-to-work defence period | Owner, Compliance, Auditor | Yes |
| 8 | Consent and acknowledgement records | The events in section 4, with statement versions and timestamps | Accountability (UK GDPR record-keeping) | Legal obligation (accountability); legitimate interests | Life of the relationship + 6 years | The recorded event | delete | Proving the lawful basis and what was agreed | Owner, Compliance; the person sees their own record | Yes |
| 9 | Audit log | Every write: old and new values, who, when | Platform-wide accountability | Legal obligation (accountability); legitimate interests | 6 years | The audited event | delete | Same limitation as the records described | Owner, Compliance, Auditor (read-only) | Yes — audit entries are never deleted during a hold |

Where a legal minimum exceeds these periods (for example an HMRC or
employment-law requirement), the longer period wins and the class is
re-flagged with the justification.

## 3. How retention works mechanically

- Every class above has, or gets, a `deletion_due`-style date; those already
  exist on worker documents.
- The Compliance Action Centre gains a "Retention due" group: class, record,
  due date, recommended action ("delete document", "confirm retention").
- Nothing is deleted automatically. Deletion is confirmed by Owner or
  Compliance and audited.
- A **legal hold** is set by Owner or Compliance on a worker, contractor or
  class: it hides the item from the "Retention due" group and blocks the
  delete action until the hold is lifted, with the reason recorded. Holds
  are audited like everything else.
- The weekly export (register 9.8) lists what exists per class, so
  data-subject requests can be answered from a current inventory.

## 4. Consent, acknowledgement and declarations — recorded as separate events

You are right that one general consent box cannot carry the processing. The
system records five **distinct, separately-timestamped events**, each with
its own statement version, and none of them is treated as the lawful basis
on its own — the lawful basis per purpose is the schedule in section 2.

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
- No data-subject-request workflow (the export inventory covers it for now).
- No special-category data beyond what right-to-work lawfully requires.

---

## Approval

Reply "approved" to accept the schedule and the five-event consent model, or
list the row numbers (1-9) or sections (3-5) you want discussed first.
