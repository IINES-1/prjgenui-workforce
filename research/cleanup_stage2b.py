import psycopg
import os

conn = psycopg.connect(
    host='aws-0-eu-west-2.pooler.supabase.com', port=5432,
    dbname='postgres', user='postgres.houhfxugjgeyrmkmpvji',
    password=os.environ['PRJ_DB_PASSWORD'], autocommit=True)
cur = conn.cursor()

emails = ['owner.test@prjgenuiworkforce.co.uk',
          'compliance.test@prjgenuiworkforce.co.uk']
cur.execute("select id, email from auth.users where email = any(%s)", (emails,))
users = cur.fetchall()
print('auth users to remove:', users)
uids = [u[0] for u in users] or ['00000000-0000-0000-0000-000000000000']

cur.execute("select id from contractors where legal_name='Southwark Builds Ltd'")
row = cur.fetchone()
cid = row[0] if row else None
print('test contractor id:', cid)

cur.execute("select id from workers where full_name in ('Wanda Worker','Wesley Worker')")
wids = [r[0] for r in cur.fetchall()]
print('test worker ids:', wids)

# Crew-scoped rows (crews cascade to members and deployments)
cur.execute("delete from crews where name='Painting crew A'")

# Worker-scoped rows first (rtw_checks reference the owner profile as performer)
for wid in wids:
    for t in ['readiness_evaluations', 'work_history', 'training_certificates',
              'qualifications', 'rtw_checks', 'worker_documents']:
        cur.execute(f"delete from {t} where worker_id=%s", (wid,))
cur.execute("delete from evidence_records where checker = any(%s)", (uids,))

# Assignment-scoped rows for the test contractor
if cid:
    cur.execute("select id from assignments where contractor_id=%s", (cid,))
    for (aid,) in cur.fetchall():
        cur.execute("delete from assignment_outcomes where assignment_id=%s", (aid,))
        cur.execute("delete from assignment_statements where assignment_id=%s", (aid,))
    cur.execute("delete from assignments where contractor_id=%s", (cid,))
    cur.execute("delete from workforce_requests where contractor_id=%s", (cid,))

cur.execute("delete from profiles where id = any(%s)", (uids,))
if cid:
    cur.execute("delete from contractors where id=%s", (cid,))
for wid in wids:
    cur.execute("delete from workers where id=%s", (wid,))
cur.execute("delete from auth.users where id = any(%s)", (uids,))

# Verify
cur.execute("select count(*) from auth.users where email = any(%s)", (emails,))
print('auth users remaining:', cur.fetchone()[0])
cur.execute("select count(*) from profiles where id = any(%s)", (uids,))
print('profiles remaining:', cur.fetchone()[0])
cur.execute("select count(*) from crews")
print('crews remaining:', cur.fetchone()[0])
cur.execute("select count(*) from crew_members")
print('crew members remaining:', cur.fetchone()[0])
cur.execute("select count(*) from crew_deployments")
print('crew deployments remaining:', cur.fetchone()[0])
cur.execute("select count(*) from workers")
print('workers remaining:', cur.fetchone()[0])
cur.execute("select count(*) from assignments")
print('assignments remaining:', cur.fetchone()[0])
cur.close(); conn.close()
print('cleanup OK')
