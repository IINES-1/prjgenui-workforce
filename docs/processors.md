# PRJGENUI Workforce — Processors and sub-processors

**Version:** 1.2 draft for review · 20 October 2026
**For approval by:** Marizilena Silva Fortes
**Register/GDPR item:** processor and sub-processor information (your
review, item 4)

---

## Who processes platform data, and where

**Controller:** PRJGENUI Workforce Ltd. Everyone in this table processes on
our documented instructions only, under a written processing agreement
(Article 28 UK GDPR).

| Processor | Role | What they process | Location | Contract position | Transfer safeguard |
|---|---|---|---|---|---|
| **Supabase** (Supabase Inc.) | Database, sign-in (authentication), document file storage | All platform records: worker data, evidence, documents, accounts, audit log | **London, UK** — the project runs in AWS region `eu-west-2`, which is a UK region (not an "EU region" as an earlier draft said; corrected) | Supabase's Data Processing Addendum applies to the project | **Two-part position, stated exactly:** the primary project data is hosted in London (UK region); support access, account metadata, service logs and sub-processor access fall under Supabase's DPA and its applicable transfer safeguards |
| **Zoho** (Zoho Corporation) | Email (Zoho Mail, EU data centre) | Transactional and account email: sign-in invitations, password resets, expiry reminders. Message content is limited to the minimum (name, the action needed, a link) | EU data centre (zoho.eu) | Zoho's EU data-processing terms apply | UK-to-EEA transfer: the EEA is designated adequate under UK law, and Zoho's EU terms apply |
| **Vercel** (Vercel Inc.) | Website and platform hosting | **Limited categories, stated plainly** (corrected from "no personal data" in the earlier draft, which was not accurate): IP addresses, request metadata and short-lived server/firewall logs generated when pages are served. These logs are used for operating and securing the platform. No worker records, documents or account data are stored by Vercel — the app sends data direct from the browser to Supabase. The exact log-retention setting in the Vercel account will be recorded here before activation | Global network, including locations outside the UK (including the US) | Vercel's Data Processing Addendum applies | UK Addendum/IDTA incorporated into Vercel's DPA |
| **Porkbun** | Domain registrar (registrar, not a processor of platform data) | Domain registration contact data only — PRJGENUI's own business data, for which PRJGENUI is the controller and Porkbun is the registrar under its registration terms. No worker or platform personal data is processed by Porkbun | US | Registrar registration terms | N/A for platform data; PRJGENUI's own registrar contact data is held under Porkbun's registration terms |
| **IINES Ltd** | Platform development and support (processor) | Administrative and support access to platform data through named, two-factor-protected accounts; scripted data changes kept as reviewable files; all data-touching actions performed through audited platform functions where one exists | UK | **Article 28 processing agreement between PRJGENUI Workforce Ltd and IINES Ltd — being drawn up now and to be executed before any live personal data is processed** | No international transfer (UK) |
| **AWS S3 (London)** — encrypted backup destination | Weekly encrypted export store (register 9.8) | The weekly encrypted export of platform records and documents — client-side encrypted (AES-256) before upload; AWS holds ciphertext only, never the key | **London, UK** (`eu-west-2`) — dedicated, access-restricted account, separate from the production account and host | Approved 20 October 2026; activated with the backup arrangement at the ownership transfer; AWS's processing terms recorded here then | UK region — no international transfer of the backup objects; account/service metadata falls under AWS's DPA and transfer safeguards |

Delivery logs for email are kept by Zoho; we review them for
troubleshooting only, and they do not contain document contents or
credentials.

## Sub-processors

- **Amazon Web Services** is the infrastructure sub-processor for Supabase,
  Vercel and the backup destination; for our Supabase project and the S3
  backup this is AWS UK (London, `eu-west-2`).
- Each provider publishes its full sub-processor list. Before production
  activation we verify each list, record the entries relevant to our
  configuration here, and record the completion of that review in this
  document; the review is re-run whenever a provider notifies a change.
- If any provider adds or replaces a sub-processor, the change is recorded
  in this document and reported to you before it takes effect, to the
  extent the provider's terms allow.

## International transfers, in one place

- **Supabase** — primary project data hosted in London (UK region);
  support access, account metadata, service logs and sub-processor access
  fall under Supabase's DPA and its applicable transfer safeguards.
- **Zoho** — EU data centre; transfer covered by the EEA's adequacy
  designation under UK law plus Zoho's EU terms.
- **Vercel** — global network including the US and other locations; the
  transfer is covered by the UK Addendum/IDTA incorporated into Vercel's
  DPA.
- **Porkbun** — US; holds only PRJGENUI's own registrar contact data
  (PRJGENUI is controller, Porkbun is the registrar), not platform data.
- **IINES Ltd and the AWS S3 London backup** — UK; no international
  transfer of the data; account/service metadata falls under the
  providers' DPAs and transfer safeguards.

## Developer and support access

- Development and support is provided by **IINES Ltd** (also listed in the
  processor table above), acting on documented instructions from PRJGENUI
  Workforce Ltd (the controller), under the Article 28 agreement noted
  above.
- Access is through **named accounts only** (no shared sign-ins), with
  **two-factor sign-in enforced** for admin roles.
- Direct database access for maintenance is possible only with the
  database credential, which is held in protected storage.
- Platform administration (adding workers, verifying evidence, generating
  statements) is performed by named PRJGENUI team accounts and audited like
  any other action.

## Backups (once activated per register 9.8)

The weekly encrypted export goes to the AWS S3 London destination in the
table above (approved 20 October 2026, activated with the backup
arrangement at the ownership transfer), access-restricted to the named
people in register 9.8, with its **12-week rolling retention** (12 weekly
exports, oldest deleted when the 13th is created), client-side AES-256
encryption with the documented key-recovery procedure, audited
access/restoration via AWS CloudTrail data events with those audit records
protected separately, and the monthly cost alert with the £5 approval
threshold, all as set out in register 9.8 and the backup and ownership
proposal.

## Changes

If a processor is added, replaced or given a new purpose, this list is
updated and the change reported to you before it takes effect.
