# PRJGENUI Workforce

Workforce compliance and matching platform for the UK construction
industry: worker passports with Right to Work and readiness gates,
explainable matching, the full assignment lifecycle with two readiness
gates, attendance evidence with a dispute path, replacement incidents,
and a scoped contractor view.

- **Live site:** https://prjgenuiworkforce.co.uk — app at `/app/`
- **Database:** Supabase (Postgres with row-level security), migrations
  in `supabase/migrations/` in numbered order
- **App:** plain JS single-page app in `app/` (no build step)
- **Email:** serverless function in `api/`, sending through Resend
- **Docs:** `docs/` — baseline register, privacy notice, platform terms,
  email delivery setup

Runtime keys live in a gitignored `secrets.js` (public-by-design values
only); real secrets are hosting environment variables, never committed.
