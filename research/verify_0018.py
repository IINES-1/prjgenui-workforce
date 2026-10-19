import os
import psycopg

conn = psycopg.connect(
    host='aws-0-eu-west-2.pooler.supabase.com', port=5432, dbname='postgres',
    user='postgres.houhfxugjgeyrmkmpvji',
    password=os.environ['PRJ_DB_PASSWORD'])
cur = conn.cursor()

cur.execute("select count(*) from audit_log "
            "where old_value ? 'token' or new_value ? 'token'")
print('audit rows still containing token:', cur.fetchone()[0])

cur.execute("select count(*) from audit_log where table_name = 'invitations'")
print('invitation audit rows:', cur.fetchone()[0])

cur.execute("select column_name, data_type, column_default "
            "from information_schema.columns "
            "where table_name = 'qualifications' and column_name = 'validity'")
print('qualifications.validity:', cur.fetchone())

cur.execute("select conname from pg_constraint "
            "where conrelid = 'qualifications'::regclass and contype = 'c'")
print('qual check constraints:', [r[0] for r in cur.fetchall()])

conn.close()
