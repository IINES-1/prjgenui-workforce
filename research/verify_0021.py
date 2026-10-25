"""Verify migration 0021 against the handover pack's acceptance tests, on
fictional records, then clean up (audit rows are append-only and stay, by
design — they are the evidence trail).

  AT-10  attendance provenance: reporter, timestamp, assignment retained;
         one authoritative record per assignment/date, duplicates refused
  AT-11  attendance dispute: the worker disputes their own record; the
         original is retained, resolution is audited, corrections append
         (never overwrite the original fact)
  AT-12  replacement incidents: cancellation moves the original through
         the normal status engine; the chain links a replacement created
         through the normal offer flow; approvals append; the site-pack
         acknowledgement is an explicit operator action; resolving closes
         the chain

One profile is borrowed as a worker-linked profile for the worker-path
tests and restored in the same run (finally block). Row-level security is
not exercised here (the session connects as the database superuser, which
bypasses RLS); the policies mirror the audited 0017 pattern.

Run (PowerShell):
  $env:PRJ_DB_PASSWORD = '<database password>'
  python research/verify_0021.py
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
            sys.exit("no spare profile to borrow as the worker")

        # ---------------- setup: fictional records -------------------------
        cur.execute("insert into workers (full_name, trade, status) "
                    "values ('AT-10 Test Worker', 'painter', 'verified') "
                    "returning id")
        w1 = cur.fetchone()[0]
        cur.execute("insert into workers (full_name, trade, status) "
                    "values ('AT-12 Test Worker', 'painter', 'verified') "
                    "returning id")
        w2 = cur.fetchone()[0]
        cur.execute("insert into contractors (legal_name) "
                    "values ('AT-10 Test Contractor') returning id")
        contractor = cur.fetchone()[0]
        cur.execute("insert into projects (contractor_id, name) "
                    "values (%s, 'AT-10 Test Project') returning id",
                    (str(contractor),))
        project = cur.fetchone()[0]
        cur.execute("insert into sites (project_id, name) "
                    "values (%s, 'AT-10 Test Site') returning id",
                    (str(project),))
        site = cur.fetchone()[0]
        cur.execute("insert into workforce_requests "
                    "(contractor_id, project_id, site_id, trade, number_needed) "
                    "values (%s, %s, %s, 'painter', 1) returning id",
                    (str(contractor), str(project), str(site)))
        request = cur.fetchone()[0]

        cur.execute("insert into assignments (request_id, worker_id, trade) "
                    "values (%s, %s, 'painter') returning id",
                    (str(request), str(w1)))
        a1 = cur.fetchone()[0]
        cur.execute("insert into assignments (request_id, worker_id, trade) "
                    "values (%s, %s, 'painter') returning id",
                    (str(request), str(w2)))
        a2 = cur.fetchone()[0]
        cur.execute("insert into assignments (request_id, worker_id, trade) "
                    "values (%s, %s, 'painter') returning id",
                    (str(request), str(w1)))
        a3 = cur.fetchone()[0]
        # a4 starts life completed (status on insert bypasses the
        # update-only engine, like a legacy record) — it tests the
        # refused transition.
        cur.execute("insert into assignments (request_id, worker_id, trade, "
                    "status) values (%s, %s, 'painter', 'completed') "
                    "returning id",
                    (str(request), str(w2)))
        a4 = cur.fetchone()[0]

        # ---------------- AT-10: attendance provenance ---------------------
        r = run_as(cur, owner, "public.record_attendance_evidence("
                   "%s, current_date, 'no_show', 'site_log', 'AT-10 test')",
                   (str(a1),))
        results.append((
            "AT-10a", "attendance recorded by the team (owner/operations)",
            r["ok"] is True))
        cur.execute("select reporter_id, worker_id, status from "
                    "attendance_evidence where assignment_id = %s",
                    (str(a1),))
        rep, wid, stat = cur.fetchone()
        results.append((
            "AT-10b", "provenance retained: reporter, worker link, status",
            str(rep) == str(owner) and str(wid) == str(w1)
            and stat == "verified"))

        r = run_as(cur, owner, "public.record_attendance_evidence("
                   "%s, current_date, 'attended', 'site_log', null)",
                   (str(a1),))
        results.append((
            "AT-10c", "a second record for the same assignment and date is "
            "refused (dispute the existing one)",
            r["ok"] is False and r["error"] == "duplicate_record"))

        # borrow a profile as the worker to test the worker's paths
        cur.execute("update profiles set roles = '{\"worker\"}'::prj_role[], "
                    "worker_id = %s where id = %s", (str(w1), str(borrower)))
        r = run_as(cur, borrower, "public.record_attendance_evidence("
                   "%s, current_date, 'attended', 'self', null)",
                   (str(a1),))
        results.append((
            "AT-10d", "a worker cannot record attendance evidence",
            r["ok"] is False and r["error"] == "not_permitted"))

        # ---------------- AT-11: attendance dispute ------------------------
        cur.execute("select id from attendance_evidence "
                    "where assignment_id = %s", (str(a1),))
        ev = cur.fetchone()[0]

        r = run_as(cur, borrower, "public.dispute_attendance_evidence("
                   "%s, 'AT-11 test: was on site')", (str(ev),))
        results.append((
            "AT-11a", "the worker disputes their own attendance record",
            r["ok"] is True))
        cur.execute("select status from attendance_evidence where id = %s",
                    (str(ev),))
        results.append((
            "AT-11b", "the disputed record is marked disputed",
            cur.fetchone()[0] == "disputed"))

        r = run_as(cur, borrower, "public.resolve_attendance_dispute("
                   "%s, 'corrected', 'excused', 'AT-11 test')", (str(ev),))
        results.append((
            "AT-11c", "the worker cannot resolve their own dispute",
            r["ok"] is False and r["error"] == "not_permitted"))

        cur.execute("select id from attendance_disputes "
                    "where attendance_evidence_id = %s", (str(ev),))
        disp = cur.fetchone()[0]

        r = run_as(cur, owner, "public.resolve_attendance_dispute("
                   "%s, 'corrected', 'no_show', 'identical test')",
                   (str(disp),))
        results.append((
            "AT-11d", "a correction identical to the original is refused",
            r["ok"] is False and r["error"] == "correction_identical"))

        r = run_as(cur, owner, "public.resolve_attendance_dispute("
                   "%s, 'corrected', 'excused', 'AT-11 test: evidence "
                   "checked, worker was excused')", (str(disp),))
        results.append((
            "AT-11e", "Compliance resolves with a correction appended",
            r["ok"] is True))
        cur.execute("select outcome, status from attendance_evidence "
                    "where id = %s", (str(ev),))
        outcome, stat = cur.fetchone()
        cur.execute("select corrected_outcome, status from "
                    "attendance_disputes where id = %s", (str(disp),))
        corrected, dstat = cur.fetchone()
        results.append((
            "AT-11f", "the original fact is retained; the correction is "
            "appended, not written over it",
            outcome == "no_show" and stat == "corrected"
            and corrected == "excused" and dstat == "resolved"))
        cur.execute("select count(*) from audit_log "
                    "where table_name in ('attendance_evidence', "
                    "'attendance_disputes')")
        results.append((
            "AT-11g", "dispute and resolution are audited",
            cur.fetchone()[0] >= 3))

        # ---------------- AT-12: replacement incidents ---------------------
        r = run_as(cur, owner, "public.record_replacement_incident("
                   "%s, 'cancellation', 'AT-12 test: client cancelled')",
                   (str(a1),))
        results.append((
            "AT-12a", "a cancellation incident is recorded",
            r["ok"] is True))
        cur.execute("select status from assignments where id = %s",
                    (str(a1),))
        status_a1 = cur.fetchone()[0]
        cur.execute("select count(*) from assignment_events "
                    "where assignment_id = %s and to_status = 'cancelled'",
                    (str(a1),))
        results.append((
            "AT-12b", "the original moves through the normal status engine "
            "(cancelled, event recorded)",
            status_a1 == "cancelled" and cur.fetchone()[0] == 1))

        cur.execute("select id, request_id from replacement_incidents "
                    "where assignment_id = %s", (str(a1),))
        inc_id, inc_request = cur.fetchone()
        results.append((
            "AT-12c", "the incident carries the assignment's request",
            str(inc_request) == str(request)))

        r = run_as(cur, owner, "public.record_replacement_incident("
                   "%s, 'no_show', 'AT-12 test: second incident')",
                   (str(a1),))
        results.append((
            "AT-12d", "a second open incident on the same assignment is "
            "refused",
            r["ok"] is False and r["error"] == "incident_already_open"))

        r = run_as(cur, owner, "public.record_replacement_incident("
                   "%s, 'no_show', 'AT-12 test: no-show')", (str(a2),))
        cur.execute("select status from assignments where id = %s",
                    (str(a2),))
        status_a2 = cur.fetchone()[0]
        results.append((
            "AT-12e", "a no-show incident records the fact without forcing "
            "a status change (NO_SHOW status arrives with the full-"
            "lifecycle build)",
            r["ok"] is True and status_a2 == "proposed"))

        r = run_as(cur, owner, "public.record_replacement_incident("
                   "%s, 'cancellation', 'AT-12 test: completed original')",
                   (str(a4),))
        results.append((
            "AT-12f", "an illegal transition is refused gracefully "
            "(completed cannot move to cancelled)",
            r["ok"] is False
            and r["error"] == "status_transition_refused"))

        # the replacement chain: a replacement created through the normal
        # offer flow (approved match -> offer -> assignment), per 0020
        cur.execute("insert into match_generations (request_id, rules_version) "
                    "values (%s, 'test') returning id", (str(request),))
        gen = cur.fetchone()[0]
        cur.execute("insert into matches (generation_id, worker_id, factors, "
                    "decision, decided_by, decided_at) "
                    "values (%s, %s, '[]'::jsonb, 'approved', %s, now())",
                    (str(gen), str(w2), str(owner)))
        cur.execute("insert into assignment_offers (request_id, worker_id, "
                    "offered_by) values (%s, %s, %s) returning id",
                    (str(request), str(w2), str(owner)))
        offer = cur.fetchone()[0]
        cur.execute("insert into assignments (request_id, worker_id, trade, "
                    "offer_id) values (%s, %s, 'painter', %s) returning id",
                    (str(request), str(w2), str(offer)))
        replacement = cur.fetchone()[0]

        r = run_as(cur, owner, "public.link_replacement_assignment("
                   "%s, %s)", (str(inc_id), str(a3)))
        results.append((
            "AT-12g", "a replacement without an offer behind it is refused "
            "(same-controls rule)",
            r["ok"] is False and r["error"] == "not_through_offer_flow"))

        r = run_as(cur, owner, "public.link_replacement_assignment("
                   "%s, %s)", (str(inc_id), str(a1)))
        results.append((
            "AT-12h", "the original assignment cannot be its own replacement",
            r["ok"] is False and r["error"] == "same_assignment"))

        r = run_as(cur, owner, "public.link_replacement_assignment("
                   "%s, %s)", (str(inc_id), str(replacement)))
        results.append((
            "AT-12i", "the replacement is linked and the approved-match "
            "generation is captured",
            r["ok"] is True and str(r["match_generation_id"]) == str(gen)))

        r = run_as(cur, owner, "public.record_replacement_approval("
                   "%s, 'approved', 'AT-12 test: contractor approved')",
                   (str(inc_id),))
        r2 = run_as(cur, owner, "public.record_replacement_approval("
                    "%s, 'refused', 'AT-12 test: then refused')",
                    (str(inc_id),))
        cur.execute("select decision from "
                    "replacement_incident_approvals where incident_id = %s "
                    "order by created_at", (str(inc_id),))
        decisions = [d[0] for d in cur.fetchall()]
        results.append((
            "AT-12j", "approvals append; history is never overwritten",
            r["ok"] is True and r2["ok"] is True
            and decisions == ["approved", "refused"]))

        r = run_as(cur, owner, "public.acknowledge_replacement_site_pack(%s)",
                   (str(inc_id),))
        r2 = run_as(cur, owner, "public.acknowledge_replacement_site_pack(%s)",
                    (str(inc_id),))
        results.append((
            "AT-12k", "the site-pack acknowledgement is an explicit action, "
            "refused when repeated",
            r["ok"] is True and r2["ok"] is False
            and r2["error"] == "already_acknowledged"))

        r = run_as(cur, owner, "public.resolve_replacement_incident("
                   "%s, 'AT-12 test: chain closed')", (str(inc_id),))
        r2 = run_as(cur, owner, "public.resolve_replacement_incident("
                    "%s, null)", (str(inc_id),))
        results.append((
            "AT-12l", "the chain closes with the elapsed time returned; a "
            "second resolve is refused",
            r["ok"] is True and "elapsed" in r
            and r2["ok"] is False and r2["error"] == "already_resolved"))

        # ---------------- cleanup (fictional test records) -----------------
        try:
            cur.execute("update profiles set roles = '{\"owner\"}'::prj_role[], "
                        "worker_id = null where id = %s", (str(borrower),))
            cur.execute("delete from replacement_incidents "
                        "where assignment_id = any(%s)",
                        ([str(a1), str(a2), str(a3), str(a4)],))
            cur.execute("delete from assignments where id = any(%s)",
                        ([str(a1), str(a2), str(a3), str(a4),
                          str(replacement)],))
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
            for wid in (w1, w2):
                cur.execute("delete from workers where id = %s", (str(wid),))
        finally:
            cur.execute("update profiles set roles = '{\"owner\"}'::prj_role[], "
                        "worker_id = null where id = %s", (str(borrower),))

ok = True
for name, desc, passed in results:
    mark = "PASS" if passed else "FAIL"
    if not passed:
        ok = False
    print(f"{name}: {mark} — {desc}")
print("ALL PASS" if ok else "FAILURES PRESENT")
sys.exit(0 if ok else 1)
