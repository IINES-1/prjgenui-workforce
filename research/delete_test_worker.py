import psycopg
import os

WORKER_ID = '7deb48d7-35fe-46ce-a711-2851c49c6f5d'

conn = psycopg.connect(
    host='aws-0-eu-west-2.pooler.supabase.com', port=5432,
    dbname='postgres', user='postgres.houhfxugjgeyrmkmpvji',
    password=os.environ['PRJ_DB_PASSWORD'], autocommit=True)
cur = conn.cursor()

# What is attached to the test worker?
dependents = ['rtw_checks', 'qualifications', 'training_certificates',
              'work_history', 'proof_of_work', 'readiness_evaluations',
              'worker_documents', 'crew_members',
              'assignments', 'performance_scores', 'overrides',
              'assignment_offers']
attached = []
for t in dependents:
    cur.execute(f'select count(*) from {t} where worker_id = %s', (WORKER_ID,))
    n = cur.fetchone()[0]
    if n:
        attached.append(f'{t}:{n}')
print('attached rows:', attached or 'none')

# Delete attached rows first, then the worker itself.
for t in dependents:
    cur.execute(f'delete from {t} where worker_id = %s', (WORKER_ID,))
cur.execute('delete from workers where id = %s', (WORKER_ID,))
print('worker deleted, rows affected:', cur.rowcount)

cur.execute('select count(*) from workers')
print('workers remaining:', cur.fetchone()[0])
cur.close(); conn.close()
