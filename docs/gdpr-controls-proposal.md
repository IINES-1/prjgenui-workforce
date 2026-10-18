# PRJGENUI Workforce — GDPR controls proposal (register 10.4)

**Version:** draft for review · 18 October 2026
**For approval by:** Marizilena Silva Fortes
**Register item:** 10.4 — retention dates per data class, restricted access to
identity documents, recorded consent.

This is the proposal you asked for. Nothing here is built until you approve
the periods; the mechanisms are described so the review can be about the
policy, not the plumbing.

---

## 1. What is already in place

- **Identity document access is already restricted.** Only Owner and
  Compliance can open identity evidence. Workers see their own documents;
  Operations, contractors and auditors cannot open them.
- **Document metadata already carries a retention class and a deletion due
  date** on every worker document row.
- **Every document upload is already audited** (who, what, when).

## 2. Proposed retention periods, per data class

Retention starts when the relationship (assignment, engagement or contract)
ends, unless noted. "Flag" means the action centre shows it as due for
deletion; deletion itself is always confirmed by a person, never automatic.

| # | Data class | Proposed retention | Basis |
|---|---|---|---|
| 1 | Right to Work evidence (share-code records, passport/ID scans) | Relationship end + 2 years, then flagged | Home Office right-to-work guidance |
| 2 | Identity documents retained in full (scans) | Deleted once the check is recorded and verified; the record, not the scan, is the evidence | Data minimisation |
| 3 | CSCS cards, qualifications, training certificates | Expiry + 2 years, then flagged | Re-issue and dispute defence |
| 4 | Assignment history and outcomes (attendance, rating, rehire) | Relationship end + 6 years, then flagged | Contract and wage-claim limitation |
| 5 | Performance and reliability evidence | Relationship end + 6 years, then flagged | Same as 4 |
| 6 | Commercial records (prices, costs, subscriptions) | 6 years from creation | Tax and contract limitation |
| 7 | Party records and engagements (who paid, who supplied) | Relationship end + 2 years, then flagged | Mirrors RTW defence period |
| 8 | Consent records (section 4) | Life of the record + 6 years | Proof of lawful basis |
| 9 | Audit log entries | 6 years | Same as the records they describe |

Where a legal minimum exceeds these (for example an employment-law opinion
or HMRC requirement), the longer period wins and the class is re-flagged.

## 3. How retention would work mechanically

- Every data class above already has, or gets, a `deletion_due` style date.
- The Compliance Action Centre gains a "Retention due" group: each item
  shows the class, the worker or record, and the due date, with a
  recommended action ("delete document", "confirm record retention").
- Nothing is deleted automatically. Deletion is a confirmed action by
  Owner or Compliance, and the confirmation is audited.
- The weekly export (register 9.8) documents what exists per class, so a
  data-subject request can be answered from a current list.

## 4. Recorded consent — proposal

Consent is recorded once, at invitation acceptance, when the worker first
signs in:

- The finish-setup screen shows a short consent statement: who PRJGENUI
  is, what data is kept, the classes above, and that they can ask for a
  copy or deletion at any time.
- Accepting stores: who consented (profile id), the exact statement text
  version, and the timestamp. Changing the statement later re-prompts on
  next sign-in and records the new version.
- A consent record is never editable by anyone through the app; only a new
  accepted version is added. This is audited like everything else.
- Contractor accounts get the same prompt on their invitation acceptance
  (they see request and assignment data only).

## 5. What this proposal deliberately does not do yet

- No automated deletion, no auto-expiry of accounts.
- No data-subject request workflow (export covers it for now).
- No processing of special-category data beyond what RTW lawfully requires.

---

## Approval

Reply "approved" to accept the periods and the consent statement approach,
or list the item numbers (1-9 or sections 3-5) you want discussed first.
