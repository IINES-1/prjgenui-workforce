import psycopg
import os

conn = psycopg.connect(
    host='aws-0-eu-west-2.pooler.supabase.com', port=5432,
    dbname='postgres', user='postgres.houhfxugjgeyrmkmpvji',
    password=os.environ['PRJ_DB_PASSWORD'], autocommit=True)
cur = conn.cursor()
cur.execute("insert into contractors (legal_name, contact_name, email, phone) values ('Southwark Builds Ltd','Dan Reyes','dan@southwarkbuilds.example','020 7946 0000') returning id")
cid = cur.fetchone()[0]
print('contractor id:', cid)

# Owner test user
cur.execute("select id from auth.users where email='owner.test@prjgenuiworkforce.co.uk'")
owner = cur.fetchone()
if not owner:
    print('owner.test missing - create via dashboard first')
    raise SystemExit(1)
owner = owner[0]
cur.execute("insert into profiles (id, full_name, roles) values (%s,'Owner Test','{owner}') on conflict (id) do nothing", (owner,))

# Contractor test user (dashboard-created)
cur.execute("select id from auth.users where email='contractor.test@prjgenuiworkforce.co.uk'")
cu = cur.fetchone()
if not cu:
    print('contractor.test missing - create via dashboard first')
    raise SystemExit(1)
cu = cu[0]
cur.execute("insert into profiles (id, full_name, roles, contractor_id) values (%s,'Dan Reyes','{contractor}',%s)", (cu, cid))
print('contractor profile linked')

# Worker + verified evidence + assignment confirmed for the contractor
cur.execute("insert into workers (full_name, trade, status) values ('Wanda Worker','painter and decorator','verified') returning id")
w1 = cur.fetchone()[0]
cur.execute("insert into rtw_checks (worker_id, method, result, check_date, reference_no, identity_match, source, performer) values (%s,'home_office_share_code','pass',current_date,'T-W1',true,'test',%s)", (w1, owner))
cur.execute("insert into qualifications (worker_id, kind, card_type, status, issue_date, expiry_date) values (%s,'cscs','green','verified',current_date - 100,current_date + 300)", (w1,))
cur.execute("insert into training_certificates (worker_id, training_type, status, issue_date, expiry_date) values (%s,'asbestos_awareness','verified',current_date - 100,current_date + 300)", (w1,))
cur.execute("insert into work_history (worker_id, period_start, period_end, description) values (%s,current_date - 200,current_date - 100,'painter at Test Co')", (w1,))
cur.execute("insert into readiness_evaluations (worker_id, rules_version, outcome, blockers, evaluated_by) values (%s,'0.1','pass','[]'::jsonb,%s)", (w1, owner))
cur.execute("insert into workforce_requests (contractor_id, trade, number_needed, status) values (%s,'painter and decorator',1,'filled') returning id, public_reference", (cid,))
r = cur.fetchone()
rid = r[0]
cur.execute("insert into assignments (request_id, worker_id, contractor_id, trade, start_date, status) values (%s,%s,%s,'painter and decorator',current_date + 7,'confirmed') returning id, public_reference", (rid, w1, cid))
a = cur.fetchone()
print('request:', r[1], 'assignment:', a[1])
cur.close(); conn.close()
print('seeded OK')
