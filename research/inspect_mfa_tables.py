import os
import psycopg

conn = psycopg.connect(
    host='aws-0-eu-west-2.pooler.supabase.com', port=5432, dbname='postgres',
    user='postgres.houhfxugjgeyrmkmpvji',
    password=os.environ['PRJ_DB_PASSWORD'])
cur = conn.cursor()
for t in ('mfa_factors', 'mfa_challenges', 'mfa_amr'):
    cur.execute("select column_name from information_schema.columns "
                "where table_schema='auth' and table_name=%s "
                "order by ordinal_position", (t,))
    print(t, [r[0] for r in cur.fetchall()])
conn.close()
