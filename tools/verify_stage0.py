"""Stage 0 acceptance checks for the PRJGENUI Workforce schema.

Runs against the live Supabase database entirely inside one transaction that
is rolled back at the end, so no test data persists. Verifies:

  1. worker status cannot move backwards
  2. blocking a worker requires a reason
  3. the hard gate: an assignment cannot be confirmed without a passing
     readiness evaluation
  4. confirming with a pass works and writes an assignment event
  5. the audit log captures writes
  6. RLS: an authenticated user with no profile sees nothing (default deny)
  7. the audit log is not writable by the authenticated role
  8. a worker sees only their own worker row

Usage (PowerShell):
  $env:PRJ_DB_PASSWORD = '<database password>'
  python tools/verify_stage0.py
"""
import os
import sys
import uuid

import psycopg

PROJECT_REF = "houhfxugjgeyrmkmpvji"
POOLER = "aws-0-eu-west-2.pooler.supabase.com"

PASSED = []
FAILED = []


def check(name, ok):
    (PASSED if ok else FAILED).append(name)
    print(("PASS " if ok else "FAIL ") + name)


def expect_error(name, fn):
    try:
        fn()
    except psycopg.Error:
        check(name, True)
    else:
        check(name, False)


def main():
    password = os.environ.get("PRJ_DB_PASSWORD")
    if not password:
        sys.exit("PRJ_DB_PASSWORD environment variable is not set")
    conn = psycopg.connect(
        host=POOLER, port=5432, user=f"postgres.{PROJECT_REF}",
        password=password, dbname="postgres", sslmode="require")
    conn.autocommit = False
    cur = conn.cursor()
    w_id = a_id = None

    # -- setup: one worker and one assignment (rolled back at the end) ------
    cur.execute("insert into workers (full_name, trade) values (%s,%s) "
                "returning id", ("Test Worker", "painter"))
    w_id = cur.fetchone()[0]
    cur.execute("insert into assignments (worker_id, trade) values (%s,%s) "
                "returning id", (w_id, "painter"))
    a_id = cur.fetchone()[0]

    # 1. forward transition is fine
    with conn.transaction():
        cur.execute("update workers set status = 'in_review' where id = %s",
                    (w_id,))
    check("forward worker status (draft -> in_review)", True)

    # 2. backward transition is refused
    def backward():
        with conn.transaction():
            cur.execute("update workers set status = 'draft' where id = %s",
                        (w_id,))
    expect_error("backward worker status refused", backward)

    # 3. blocked without a reason is refused
    def no_reason():
        with conn.transaction():
            cur.execute("update workers set status = 'blocked' where id = %s",
                        (w_id,))
    expect_error("blocked without reason refused", no_reason)

    # 4. hard gate: confirm without a readiness evaluation is refused
    def confirm_no_eval():
        with conn.transaction():
            cur.execute("update assignments set status = 'confirmed' "
                        "where id = %s", (a_id,))
    expect_error("hard gate: confirm without evaluation refused",
                 confirm_no_eval)

    # 5. confirm with a worker-level passing evaluation succeeds
    with conn.transaction():
        cur.execute("insert into readiness_evaluations "
                    "(worker_id, rules_version, outcome, blockers) "
                    "values (%s,'0.1','pass','[]'::jsonb)", (w_id,))
        cur.execute("update assignments set status = 'confirmed' "
                    "where id = %s", (a_id,))
        cur.execute("select count(*) from assignment_events "
                    "where assignment_id = %s", (a_id,))
        events = cur.fetchone()[0]
    check("confirm with pass evaluation + assignment event written",
          events == 1)

    # 6. the audit log captured the writes above
    cur.execute("select count(*) from audit_log "
                "where table_name in ('workers','assignments')")
    audits = cur.fetchone()[0]
    check(f"audit log capturing writes ({audits} rows)", audits > 0)

    # -- RLS checks as authenticated (role switch reverts at rollback) ------
    # A user with no profile row: default deny everywhere.
    stranger = str(uuid.uuid4())
    cur.execute("select set_config('request.jwt.claims', %s, true)",
                ('{"sub":"%s","role":"authenticated"}' % stranger,))
    cur.execute("set local role authenticated")
    cur.execute("select count(*) from workers")
    check("RLS: no-profile user sees no workers", cur.fetchone()[0] == 0)
    cur.execute("select count(*) from rtw_checks")
    check("RLS: no-profile user sees no checks", cur.fetchone()[0] == 0)
    cur.execute("select count(*) from audit_log")
    check("RLS: no-profile user sees no audit log", cur.fetchone()[0] == 0)

    def write_audit():
        with conn.transaction():
            cur.execute("update audit_log set action = 'tamper' where false")
    expect_error("audit log not writable by authenticated", write_audit)

    # The role switch above only reverts at rollback, so the worker
    # self-view tests run in a second pass below.
    conn.rollback()

    # -- worker self-view, second pass ---------------------------------------
    cur.execute("insert into workers (full_name, trade) values (%s,%s) "
                "returning id", ("Self View Worker", "plasterer"))
    w2 = cur.fetchone()[0]
    cur.execute("insert into workers (full_name, trade) values (%s,%s) "
                "returning id", ("Other Worker", "plasterer"))
    w3 = cur.fetchone()[0]
    user_id = str(uuid.uuid4())
    cur.execute("insert into auth.users (id, email) values (%s, %s)",
                (user_id, f"selfview-{user_id[:8]}@example.invalid"))
    cur.execute("insert into profiles (id, full_name, roles, worker_id) "
                "values (%s, %s, %s, %s)",
                (user_id, "Self View Worker", "{worker}", w2))
    cur.execute("select set_config('request.jwt.claims', %s, true)",
                ('{"sub":"%s","role":"authenticated"}' % user_id,))
    cur.execute("set local role authenticated")
    cur.execute("select count(*) from workers")
    own = cur.fetchone()[0]
    check("RLS: worker sees exactly their own row", own == 1)
    cur.execute("select count(*) from workers where id = %s", (w2,))
    check("RLS: worker's visible row is their own", cur.fetchone()[0] == 1)

    # Stage 1 (register 10.2): workers CAN correct their own contact
    # details, trade and availability; the guard trigger refuses changes
    # to name, passport number, status or reasons.
    with conn.transaction():
        cur.execute("update workers set trade = 'painter' where id = %s", (w2,))
        touched = cur.rowcount
    check("RLS: worker corrects own trade (1 row updated)",
          touched == 1)
    cur.execute("select trade from workers where id = %s", (w2,))
    check("RLS: worker's trade corrected", cur.fetchone()[0] == "painter")

    def bad_name_edit():
        with conn.transaction():
            cur.execute("update workers set full_name = 'Someone Else' "
                        "where id = %s", (w2,))
    expect_error("Guard: worker cannot change their name", bad_name_edit)

    def bad_passport_edit():
        with conn.transaction():
            cur.execute("update workers set passport_no = 'PW-UK-999999' "
                        "where id = %s", (w2,))
    expect_error("Guard: worker cannot change their passport number",
                 bad_passport_edit)

    conn.rollback()
    print()
    print(f"passed: {len(PASSED)}  failed: {len(FAILED)}")
    for name in FAILED:
        print("  FAILED:", name)
    conn.close()
    sys.exit(1 if FAILED else 0)


if __name__ == "__main__":
    main()
