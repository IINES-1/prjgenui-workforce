import psycopg
import os

conn = psycopg.connect(
    host='aws-0-eu-west-2.pooler.supabase.com', port=5432,
    dbname='postgres', user='postgres.houhfxugjgeyrmkmpvji',
    password=os.environ['PRJ_DB_PASSWORD'], autocommit=True)
cur = conn.cursor()

emails = ['owner.test@prjgenuiworkforce.co.uk',
          'contractor.test@prjgenuiworkforce.co.uk']
cur.execute("select id, email from auth.users where email = any(%s)", (emails,))
users = cur.fetchall()
print('auth users to remove:', users)
uids = [u[0] for u in users] or ['00000000-0000-0000-0000-000000000000']

cur.execute("select id from contractors where legal_name='Southwark Builds Ltd'")
row = cur.fetchone()
cid = row[0] if row else None
print('test contractor id:', cid)

cur.execute("select id from workers where full_name='Wanda Worker'")
row = cur.fetchone()
wid = row[0] if row else None
print('test worker id:', wid)

# Worker-scoped rows first (rtw_checks reference the owner profile as performer)
if wid:
    for t in ['readiness_evaluations', 'work_history', 'training_certificates',
              'qualifications', 'rtw_checks', 'worker_documents']:
        cur.execute(f"delete from {t} where worker_id=%s", (wid,))
cur.execute("delete from evidence_records where checker = any(%s)", (uids,))

# Assignment-scoped rows for the test contractor's assignments
if cid:
    cur.execute("select id from assignments where contractor_id=%s", (cid,))
    for (aid,) in cur.fetchall():
        cur.execute("delete from assignment_outcomes where assignment_id=%s", (aid,))
        cur.execute("delete from assignment_statements where assignment_id=%s", (aid,))
    cur.execute("delete from assignments where contractor_id=%s", (cid,))
    cur.execute("delete from workforce_requests where contractor_id=%s", (cid,))
    cur.execute("delete from price_catalog where contractor_id=%s", (cid,))
    cur.execute("delete from service_subscriptions where contractor_id=%s", (cid,))

# Profiles, then contractors, then workers, then auth users
cur.execute("delete from profiles where id = any(%s)", (uids,))
if cid:
    cur.execute("delete from contractors where id=%s", (cid,))
if wid:
    cur.execute("delete from workers where id=%s", (wid,))
cur.execute("delete from auth.users where id = any(%s)", (uids,))

# Verify
cur.execute("select count(*) from auth.users where email = any(%s)", (emails,))
print('auth users remaining:', cur.fetchone()[0])
cur.execute("select count(*) from profiles where id = any(%s)", (uids,))
print('profiles remaining:', cur.fetchone()[0])
cur.execute("select count(*) from contractors where legal_name='Southwark Builds Ltd'")
print('test contractor remaining:', cur.fetchone()[0])
cur.execute("select count(*) from workers where full_name='Wanda Worker'")
print('test worker remaining:', cur.fetchone()[0])
cur.execute("select count(*) from workforce_requests")
print('total requests:', cur.fetchone()[0])
cur.execute("select count(*) from assignments")
print('total assignments:', cur.fetchone()[0])
cur.close(); conn.close()
print('cleanup OK')
