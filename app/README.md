# PRJGENUI Workforce — team platform (Stage 0, slice 2)

The internal platform: sign-in, profiles with the seven roles, and
invitations. Served from this folder, currently at
`prjgenuiworkforce.co.uk/app/` on the existing Vercel project.

## How it works

- Static HTML/CSS/JS; no build step. Talks to Supabase (Auth + database)
  using the anon key only. Every permission is enforced by row-level
  security in the database, not by this front end.
- Keys are injected at runtime: `index.html` loads `/secrets.js` from the
  site root (gitignored, deployed, never committed) and `app.js` reads
  `window.PRJGENUI_APP || window.PRJGENUI`. If the app is ever moved to
  its own Vercel project, give that project its own runtime key file
  instead — the code needs no change.
- The whole app stays noindex (page meta plus the sitewide header).

## What slice 2 includes

- Email and password sign-in (Supabase Auth)
- Profile display: name, roles
- Default deny in practice: a working sign-in with no profile row sees
  nothing but a "not linked yet" note
- Invitations (Owner and Operations): create, list, revoke; each expires
  after seven days

## Deliberately not in this slice

- Invitation redemption emails (the link that lets an invited person set
  their own password). Next step: a small server function, then optionally
  Zoho SMTP so mail comes from hello@prjgenuiworkforce.co.uk.
- Worker, readiness, request and assignment screens (slice 3+).

## Local preview

From the repository root (so `/secrets.js` resolves):

    python -m http.server 8765

then open http://localhost:8765/app/

## Account bootstrap

`tools/accounts.py` creates accounts directly in the database (an auth
user plus a profile row with roles). For a real account, omit the
password flag: a random password is generated locally, never recorded,
and the person sets their own password through the app's "Forgot your
password?" link.
