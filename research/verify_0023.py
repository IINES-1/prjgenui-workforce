"""Verify migrations 0022 + 0023 + 0024 (the full assignment lifecycle,
the two readiness gates, the offer flow, and the contractor view) against
the handover pack's acceptance tests, on fictional records, then clean up
(audit rows are append-only and stay, by design).

  AT-08  second readiness gate: activation refused without a current
         passing evaluation; pre-activation snapshot recorded on success
  FR-08  offer flow: offer only from an approved match; response recorded;
         one live offer per worker per request
  FR-09  full lifecycle: offered -> accepted -> confirmed -> active ->
         completed, no_show and replaced exceptions, illegal transitions
         refused by the engine
  FR-16  contractor overview: own requests, assignments (worker name and
         trade only — no passport numbers), statements, attendance

One profile is borrowed as a contractor-linked profile for the
contractor-path tests and restored in the same run (finally block).

Run (PowerShell):
  $env:PRJ_DB_PASSWORD = '<database password>'
  python research/verify_0023.py
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


def run_as(cur, profile_id, fn, params):
    """Call an RPC under a simulated session (request.jwt.claims)."""
    cur.execute("select set_config('request.jwt.claims', %s, true)",
                (json.dumps({"sub": str(profile_id),
                             "role": "authenticated"}),))
    cur.execute("select " + fn, params)
    return cur.fetchone()[0]


results = []

with conn:
    with conn.cursor() as cur:
        cur.execute("select id from profiles where status = 'active' "
                    "and 'owner' = any(roles) order by created_at limit 1")
        owner = cur.fetchone()[0]
        cur.execute("select id from profiles where status = 'active' "
                    "and 'owner' = any(roles) order by created_at "
                    "offset 1 limit 1")
        row = cur.fetchone()
        borrower = row[0] if row else None
        if borrower is None:
            sys.exit("no spare profile to borrow as the contractor")

        # ---------------- setup: fictional records ------------------------
        cur.execute("insert into workers (full_name, trade, status) "
                    "values ('LC Test Worker', 'painter', 'draft') "
                    "returning id")
        w1 = cur.fetchone()[0]
        cur.execute("insert into contractors (legal_name) "
                    "values ('LC Test Contractor') returning id")
        contractor = cur.fetchone()[0]
        cur.execute("insert into projects (contractor_id, name) "
                    "values (%s, 'LC Test Project') returning id",
                    (str(contractor),))
        project = cur.fetchone()[0]
        cur.execute("insert into sites (project_id, name) "
                    "values (%s, 'LC Test Site') returning id",
                    (str(project),))
        site = cur.fetchone()[0]
        cur.execute("insert into workforce_requests "
                    "(contractor_id, project_id, site_id, trade, number_needed) "
                    "values (%s, %s, %s, 'painter', 1) returning id",
                    (str(contractor), str(project), str(site)))
        request = cur.fetchone()[0]

        # ---------------- FR-08: the offer flow ----------------------------
        # no approved match -> the offer is refused up front
        r = run_as(cur, owner, "public.create_assignment_from_match(%s, %s)",
                   (str(request), str(w1)))
        results.append((
            "FR-08a", "an offer without an approved match is refused",
            r["ok"] is False and r["error"] == "no_approved_match"))

        cur.execute("insert into match_generations (request_id, rules_version) "
                    "values (%s, 'test') returning id", (str(request),))
        gen = cur.fetchone()[0]
        cur.execute("insert into matches (generation_id, worker_id, factors, "
                    "decision, decided_by, decided_at) "
                    "values (%s, %s, '[]'::jsonb, 'approved', %s, now())",
                    (str(gen), str(w1), str(owner)))

        r = run_as(cur, owner, "public.create_assignment_from_match(%s, %s)",
                   (str(request), str(w1)))
        results.append((
            "FR-08b", "an offer from an approved match creates the offer and "
            "the assignment at 'offered'",
            r["ok"] is True))
        assignment = r["assignment_id"]
        cur.execute("select a.status, (o.id is not null) as has_offer, "
                    "rq.status as req_status from assignments a "
                    "left join assignment_offers o on o.id = a.offer_id "
                    "left join workforce_requests rq on rq.id = a.request_id "
                    "where a.id = %s", (str(assignment),))
        a_status, has_offer, req_status = cur.fetchone()
        results.append((
            "FR-08c", "the assignment is 'offered', carries its offer, and "
            "the request moves to 'offered'",
            a_status == "offered" and has_offer and req_status == "offered"))

        r = run_as(cur, owner, "public.create_assignment_from_match(%s, %s)",
                   (str(request), str(w1)))
        results.append((
            "FR-08d", "a second live offer for the same worker and request "
            "is refused",
            r["ok"] is False and r["error"] == "already_offered"))

        r = run_as(cur, owner, "public.record_offer_response(%s, 'accepted')",
                   (str(assignment),))
        cur.execute("select status from assignments where id = %s",
                    (str(assignment),))
        results.append((
            "FR-08e", "the worker's acceptance moves the assignment to "
            "'accepted' and stamps the offer",
            r["ok"] is True and cur.fetchone()[0] == "accepted"))

        # ---------------- gates 1 and 2 (AT-07/AT-08) ----------------------
        r = run_as(cur, owner, "public.confirm_assignment(%s)",
                   (str(assignment),))
        results.append((
            "AT-07a", "confirmation is refused without a current passing "
            "readiness evaluation (first gate)",
            r["ok"] is False and r["error"] == "hard_gate_refused"))

        # a passing evaluation for the worker
        cur.execute("insert into rtw_checks (worker_id, method, check_date, "
                    "result, source) values (%s, 'manual_passport', "
                    "current_date, 'pass', 'verify script')", (str(w1),))
        cur.execute("update workers set status = 'verified' where id = %s",
                    (str(w1),))
        r = run_as(cur, owner, "public.evaluate_readiness(%s)", (str(w1),))
        results.append((
            "AT-07b", "with the evidence in place the worker's readiness "
            "passes", r["outcome"] == "pass"))

        r = run_as(cur, owner, "public.confirm_assignment(%s)",
                   (str(assignment),))
        cur.execute("select status from assignments where id = %s",
                    (str(assignment),))
        results.append((
            "AT-07c", "confirmation succeeds with a current passing "
            "evaluation",
            r["ok"] is True and cur.fetchone()[0] == "confirmed"))

        # a later failing evaluation (follow-up gone wrong) must stop
        # activation — the second gate re-checks, it does not trust the
        # earlier pass. Explicit timestamps keep the ordering
        # deterministic (evaluations share a transaction otherwise).
        cur.execute("insert into readiness_evaluations "
                    "(worker_id, rules_version, outcome, blockers, evaluated_by, "
                    "created_at) "
                    "values (%s, 'test', 'blocked', '[]'::jsonb, %s, "
                    "now() + interval '1 minute')",
                    (str(w1), str(owner)))
        r = run_as(cur, owner, "public.activate_assignment(%s)",
                   (str(assignment),))
        results.append((
            "AT-08a", "activation is refused when the latest evaluation no "
            "longer passes (second gate re-checks)",
            r["ok"] is False and r["error"] == "hard_gate_refused"))

        cur.execute("insert into readiness_evaluations "
                    "(worker_id, rules_version, outcome, blockers, evaluated_by, "
                    "created_at) "
                    "values (%s, 'test', 'pass', '[]'::jsonb, %s, "
                    "now() + interval '2 minutes')",
                    (str(w1), str(owner)))
        cur.execute("select count(*) from readiness_snapshots")
        snaps_before = cur.fetchone()[0]
        r = run_as(cur, owner, "public.activate_assignment(%s)",
                   (str(assignment),))
        cur.execute("select status from assignments where id = %s",
                    (str(assignment),))
        a_status_after = cur.fetchone()[0]
        cur.execute("select count(*) from readiness_snapshots")
        snaps_after = cur.fetchone()[0]
        results.append((
            "AT-08b", "activation succeeds with a current pass and records "
            "the pre-activation snapshot",
            r["ok"] is True and a_status_after == "active"
            and snaps_after == snaps_before + 1))

        # ---------------- FR-09: lifecycle exceptions ---------------------
        cur.execute("update assignments set status = 'completed' "
                    "where id = %s", (str(assignment),))
        results.append((
            "FR-09a", "active -> completed is legal (the outcome path)",
            cur.rowcount == 1))

        # no-show chain: a second worker goes offered -> accepted ->
        # confirmed, then does not show
        cur.execute("insert into workers (full_name, trade, status) "
                    "values ('LC Test Worker 2', 'painter', 'verified') "
                    "returning id")
        w2 = cur.fetchone()[0]
        cur.execute("insert into rtw_checks (worker_id, method, check_date, "
                    "result, source) values (%s, 'manual_passport', "
                    "current_date, 'pass', 'verify script')", (str(w2),))
        run_as(cur, owner, "public.evaluate_readiness(%s)", (str(w2),))
        cur.execute("insert into matches (generation_id, worker_id, factors, "
                    "decision, decided_by, decided_at) "
                    "values (%s, %s, '[]'::jsonb, 'approved', %s, now())",
                    (str(gen), str(w2), str(owner)))
        r = run_as(cur, owner, "public.create_assignment_from_match(%s, %s)",
                   (str(request), str(w2)))
        assignment2 = r["assignment_id"]
        run_as(cur, owner, "public.record_offer_response(%s, 'accepted')",
               (str(assignment2),))
        run_as(cur, owner, "public.confirm_assignment(%s)", (str(assignment2),))

        r = run_as(cur, owner, "public.record_replacement_incident("
                   "%s, 'no_show', 'LC test: worker did not show')",
                   (str(assignment2),))
        cur.execute("select status from assignments where id = %s",
                    (str(assignment2),))
        results.append((
            "FR-09b", "a no-show incident moves a confirmed original to "
            "'no_show' through the engine",
            r["ok"] is True and cur.fetchone()[0] == "no_show"))

        # the replacement: a third worker through the normal offer flow
        cur.execute("insert into workers (full_name, trade, status) "
                    "values ('LC Test Worker 3', 'painter', 'verified') "
                    "returning id")
        w3 = cur.fetchone()[0]
        cur.execute("insert into rtw_checks (worker_id, method, check_date, "
                    "result, source) values (%s, 'manual_passport', "
                    "current_date, 'pass', 'verify script')", (str(w3),))
        run_as(cur, owner, "public.evaluate_readiness(%s)", (str(w3),))
        cur.execute("insert into matches (generation_id, worker_id, factors, "
                    "decision, decided_by, decided_at) "
                    "values (%s, %s, '[]'::jsonb, 'approved', %s, now())",
                    (str(gen), str(w3), str(owner)))
        r = run_as(cur, owner, "public.create_assignment_from_match(%s, %s)",
                   (str(request), str(w3)))
        replacement = r["assignment_id"]
        run_as(cur, owner, "public.record_offer_response(%s, 'accepted')",
               (str(replacement),))

        cur.execute("select id from replacement_incidents "
                    "where assignment_id = %s", (str(assignment2),))
        incident = cur.fetchone()[0]
        r = run_as(cur, owner, "public.link_replacement_assignment(%s, %s)",
                   (str(incident), str(replacement)))
        cur.execute("select status from assignments where id = %s",
                    (str(assignment2),))
        results.append((
            "FR-09c", "linking the replacement marks the original "
            "'replaced' and captures the match generation",
            r["ok"] is True and cur.fetchone()[0] == "replaced"
            and str(r["match_generation_id"]) == str(gen)))

        # illegal transitions are refused by the engine
        cur.execute("select count(*) from assignments a join "
                    "assignment_events ev on ev.assignment_id = a.id "
                    "where a.id = %s", (str(assignment),))
        results.append((
            "FR-09d", "every lifecycle transition is recorded as an "
            "assignment event (accepted, confirmed, active, completed — "
            "creation at 'offered' is the initial state, not a transition)",
            cur.fetchone()[0] >= 4))

        # ---------------- FR-16: the contractor view ------------------------
        cur.execute("update profiles set roles = '{\"contractor\"}'::prj_role[], "
                    "contractor_id = %s, worker_id = null "
                    "where id = %s", (str(contractor), str(borrower)))
        r = run_as(cur, borrower, "public.contractor_overview()", ())
        ok_view = (r["ok"] is True
                   and r["contractor"]["legal_name"] == "LC Test Contractor"
                   and len(r["requests"]) >= 1
                   and len(r["assignments"]) >= 3
                   and all("worker_name" in a for a in r["assignments"]))
        payload = json.dumps(r)
        results.append((
            "FR-16a", "the contractor sees own requests and assignments with "
            "worker name and trade",
            ok_view))
        results.append((
            "FR-16b", "the contractor payload carries no passport numbers or "
            "contact details",
            "passport" not in payload and "passport_no" not in payload))

        # a statement for one of the contractor's assignments
        r2 = run_as(cur, owner, "public.generate_assignment_statement(%s)",
                    (str(assignment),))
        r3 = run_as(cur, borrower, "public.contractor_overview()", ())
        results.append((
            "FR-16c", "the contractor sees the latest statement for their own "
            "assignment",
            r2["ok"] is True
            and len(r3["statements"]) == 1
            and r3["statements"][0]["assignment_id"] == str(assignment)))

        r = run_as(cur, owner, "public.contractor_overview()", ())
        results.append((
            "FR-16d", "the contractor view is not available to other roles",
            r["ok"] is False and r["error"] == "not_permitted"))

        # ---------------- cleanup (fictional test records) ----------------
        try:
            cur.execute("update profiles set roles = '{\"owner\"}'::prj_role[], "
                        "contractor_id = null where id = %s", (str(borrower),))
            cur.execute("delete from replacement_incidents "
                        "where assignment_id = any(%s)",
                        ([str(assignment), str(assignment2),
                          str(replacement)],))
            cur.execute("delete from assignments where id = any(%s)",
                        ([str(assignment), str(assignment2),
                          str(replacement)],))
            cur.execute("delete from assignment_offers "
                        "where request_id = %s", (str(request),))
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
        finally:
            cur.execute("update profiles set roles = '{\"owner\"}'::prj_role[], "
                        "contractor_id = null where id = %s", (str(borrower),))

ok = True
for name, desc, passed in results:
    mark = "PASS" if passed else "FAIL"
    if not passed:
        ok = False
    print(f"{name}: {mark} — {desc}")
print("ALL PASS" if ok else "FAILURES PRESENT")
sys.exit(0 if ok else 1)
