"""Delete a worker record and everything attached to it (test cleanup).

Usage: python research/delete_worker_by_name.py "<full name>"
"""
import os
import sys

import psycopg

name = sys.argv[1]
conn = psycopg.connect(
    host='aws-0-eu-west-2.pooler.supabase.com', port=5432,
    dbname='postgres', user='postgres.houhfxugjgeyrmkmpvji',
    password=os.environ['PRJ_DB_PASSWORD'], autocommit=True)
cur = conn.cursor()

cur.execute("select id from workers where full_name = %s", (name,))
row = cur.fetchone()
if not row:
    sys.exit('no worker named ' + name)
worker_id = row[0]

# Children first (FK ordering learned the hard way):
# evidence_records references the CHECKER, not worker_id, so it is not here.
dependents = ['rtw_checks', 'qualifications', 'training_certificates',
              'work_history', 'proof_of_work', 'readiness_evaluations',
              'worker_documents', 'crew_members',
              'assignments', 'performance_scores', 'overrides',
              'assignment_offers']
attached = []
for t in dependents:
    cur.execute(f'select count(*) from {t} where worker_id = %s', (worker_id,))
    n = cur.fetchone()[0]
    if n:
        attached.append(f'{t}:{n}')
print('attached rows:', attached or 'none')

for t in dependents:
    cur.execute(f'delete from {t} where worker_id = %s', (worker_id,))
cur.execute('delete from workers where id = %s', (worker_id,))
print('worker deleted, rows affected:', cur.rowcount)

cur.execute('select count(*) from workers')
print('workers remaining:', cur.fetchone()[0])
cur.close(); conn.close()
