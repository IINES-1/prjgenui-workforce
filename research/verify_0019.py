"""Verify migrations 0019 + 0020 against the handover pack's acceptance
tests, on fictional records, then clean up (audit rows are append-only and
stay, by design — they are the evidence trail).

  AT-03  failed RTW check stays blocked even with an approved override
  AT-03b non-RTW blockers remain overridable (override function intact)
  AT-06a offer without an approved match is refused (no row created)
  AT-06b offer from a recorded approved match succeeds
  AT-06c refusals are logged in the audit trail

Run (PowerShell):
  $env:PRJ_DB_PASSWORD = '<database password>'
  python research/verify_0019.py
"""
import json
import os
import sys

import psycopg

PROJECT_REF = "houhfxugjgeyrmkmpvji"

password = os.environ.get("PRJ_DB_PASSWORD")
if not password:
    sys.exit("PRJ_DB_PASSWORD environment variable is not set")

conn = psycopg.connect(
    host="aws-0-eu-west-2.pooler.supabase.com", port=5432,
    user=f"postgres.{PROJECT_REF}", dbname="postgres",
    password=password, sslmode="require", connect_timeout=10)


def run_as(cur, owner_id, fn, params):
    """Call an RPC under a simulated owner session (request.jwt.claims)."""
    cur.execute("select set_config('request.jwt.claims', %s, true)",
                (json.dumps({"sub": str(owner_id), "role": "authenticated"}),))
    cur.execute("select " + fn, params)
    return cur.fetchone()[0]


results = []

with conn:
    with conn.cursor() as cur:
        cur.execute("select id from profiles "
                    "where status = 'active' and 'owner' = any(roles) limit 1")
        owner = cur.fetchone()[0]

        # ---------------- AT-03: RTW failure is never overridable ----------
        cur.execute("""insert into workers (full_name, trade, status)
                       values ('AT-03 Test Worker', 'painter', 'verified')
                       returning id""")
        w1 = cur.fetchone()[0]
        cur.execute("""insert into rtw_checks
                         (worker_id, method, check_date, result, source)
                       values (%s, 'manual_passport', current_date,
                               'fail', 'verification script')""",
                    (str(w1),))
        cur.execute("""insert into overrides
                         (worker_id, requirement, reason, approved_by)
                       values (%s, 'rtw_not_pass',
                               'AT-03 test: attempt to waive a failed RTW check',
                               %s)""",
                    (str(w1), str(owner)))
        r = run_as(cur, owner, "public.evaluate_readiness(%s)", (str(w1),))
        rtw = [b for b in r["blockers"] if b["code"] == "rtw_not_pass"]
        results.append((
            "AT-03",
            "failed RTW check stays blocked even with an approved override",
            r["outcome"] == "blocked" and rtw
            and rtw[0]["mandatory"] is True))

        # sanity: a non-RTW blocker is still waivable by an approved override
        cur.execute("""insert into workers (full_name, trade, status)
                       values ('AT-03b Test Worker', 'painter', 'draft')
                       returning id""")
        w2 = cur.fetchone()[0]
        cur.execute("""insert into rtw_checks
                         (worker_id, method, check_date, result, source)
                       values (%s, 'manual_passport', current_date,
                               'pass', 'verification script')""",
                    (str(w2),))
        cur.execute("""insert into overrides
                         (worker_id, requirement, reason, approved_by)
                       values (%s, 'worker_not_verified',
                               'AT-03b test: override still works elsewhere',
                               %s)""",
                    (str(w2), str(owner)))
        r2 = run_as(cur, owner, "public.evaluate_readiness(%s)", (str(w2),))
        wnv = [b for b in r2["blockers"] if b["code"] == "worker_not_verified"]
        results.append((
            "AT-03b",
            "non-RTW blockers remain overridable (override function intact)",
            r2["outcome"] == "pass" and wnv and wnv[0]["mandatory"] is False))

        # ---------------- AT-06: offer without approved match refused ------
        cur.execute("""insert into contractors (legal_name)
                       values ('AT-06 Test Contractor') returning id""")
        contractor = cur.fetchone()[0]
        cur.execute("""insert into projects (contractor_id, name)
                       values (%s, 'AT-06 Test Project') returning id""",
                    (str(contractor),))
        project = cur.fetchone()[0]
        cur.execute("""insert into sites (project_id, name)
                       values (%s, 'AT-06 Test Site') returning id""",
                    (str(project),))
        site = cur.fetchone()[0]
        cur.execute("""insert into workforce_requests
                         (contractor_id, project_id, site_id, trade, number_needed)
                       values (%s, %s, %s, 'painter', 1) returning id""",
                    (str(contractor), str(project), str(site)))
        request = cur.fetchone()[0]
        cur.execute("""insert into workers (full_name, trade, status)
                       values ('AT-06 Test Worker', 'painter', 'verified')
                       returning id""")
        w3 = cur.fetchone()[0]

        cur.execute("""select count(*) from audit_log
                       where action = 'offer_refused_no_approved_match'""")
        refusals_before = cur.fetchone()[0]

        # the refused offer: no exception, but no row is created either
        cur.execute("""insert into assignment_offers
                        (request_id, worker_id, offered_by)
                      values (%s, %s, %s)""",
                    (str(request), str(w3), str(owner)))
        cur.execute("""select count(*) from assignment_offers
                       where request_id = %s and worker_id = %s""",
                    (str(request), str(w3)))
        rows_created = cur.fetchone()[0]
        results.append((
            "AT-06a", "offer without an approved match is refused "
            "(no row created)", rows_created == 0))

        cur.execute("""select count(*) from audit_log
                       where action = 'offer_refused_no_approved_match'""")
        refusals_after = cur.fetchone()[0]
        results.append((
            "AT-06c", "the refusal is logged in the audit trail",
            refusals_after == refusals_before + 1))

        # with a recorded approved match, the same offer is accepted
        cur.execute("""insert into match_generations (request_id, rules_version)
                       values (%s, 'test') returning id""",
                    (str(request),))
        gen = cur.fetchone()[0]
        cur.execute("""insert into matches
                         (generation_id, worker_id, factors,
                          decision, decided_by, decided_at)
                       values (%s, %s, '[]'::jsonb, 'approved', %s, now())""",
                    (str(gen), str(w3), str(owner)))
        cur.execute("""insert into assignment_offers
                        (request_id, worker_id, offered_by)
                      values (%s, %s, %s) returning id""",
                    (str(request), str(w3), str(owner)))
        offer = cur.fetchone()[0]
        results.append((
            "AT-06b", "offer from a recorded approved match succeeds",
            offer is not None))

        # ---------------- cleanup (fictional test records) ------------------
        cur.execute("delete from assignment_offers where id = %s",
                    (str(offer),))
        cur.execute("delete from matches where generation_id = %s",
                    (str(gen),))
        cur.execute("delete from match_generations where id = %s",
                    (str(gen),))
        cur.execute("delete from workforce_requests where id = %s",
                    (str(request),))
        cur.execute("delete from sites where id = %s", (str(site),))
        cur.execute("delete from projects where id = %s", (str(project),))
        cur.execute("delete from contractors where id = %s",
                    (str(contractor),))
        for wid in (w1, w2, w3):
            cur.execute("delete from workers where id = %s", (str(wid),))

ok = True
for name, desc, passed in results:
    mark = "PASS" if passed else "FAIL"
    if not passed:
        ok = False
    print(f"{name}: {mark} — {desc}")
print("ALL PASS" if ok else "FAILURES PRESENT")
sys.exit(0 if ok else 1)
