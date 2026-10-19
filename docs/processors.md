# PRJGENUI Workforce — Processors and sub-processors

**Version:** 1.0 draft for review · 19 October 2026
**For approval by:** Marizilena Silva Fortes
**Register/GDPR item:** processor and sub-processor information (your
review, item 4)

---

## Who processes platform data, and where

| Processor | Role | What they process | Location | Contract position |
|---|---|---|---|---|
| **Supabase** (Supabase Inc.) | Database, sign-in (authentication), document file storage | All platform records: worker data, evidence, documents, accounts, audit log | EU region (aws-eu-west-2, London) | Supabase's standard Data Processing Addendum applies; we enable it for the project |
| **Zoho** (Zoho Corporation) | Email (Zoho Mail, EU data centre) | Transactional and account email: sign-in invitations, password resets, expiry reminders. Message content is limited to the minimum (name, the action needed, a link) | EU data centre (zoho.eu) | Zoho's EU data-processing terms apply |
| **Vercel** (Vercel Inc.) | Website and app hosting | Serves the website and app pages only. No personal data is stored by Vercel — the app sends data direct from the browser to Supabase | Global CDN, static assets only | No personal-data processing beyond serving pages |
| **Porkbun** | Domain registrar | Domain registration contact data only (no worker or platform data) | US | Registrar terms |

Delivery logs for email are kept by Zoho; we review them for
troubleshooting only, and they do not contain document contents or
credentials.

## Developer and support access

- Development and support is provided by **IINES Ltd**, acting on
  documented instructions from PRJGENUI Workforce Ltd (the controller).
- Access is through **named accounts only** (no shared sign-ins), with
  **two-factor sign-in enforced** for admin roles.
- Direct database access for maintenance is possible only with the
  database credential, which is held in protected storage, and every
  maintenance action that touches data is performed through audited
  platform functions where one exists; scripted data changes are kept as
  reviewable files in the project repository.
- Platform administration (adding workers, verifying evidence, generating
  statements) is performed by named PRJGENUI team accounts and audited
  like any other action.

## Backups (once activated per register 9.8)

The weekly encrypted export is stored off-site with access restricted to
named administrators; the destination and its location will be added to
this list before activation, for your approval as part of the 9.8
approval.

## Changes

If a processor is added, replaced or given a new purpose, this list is
updated and the change reported to you before it takes effect.
