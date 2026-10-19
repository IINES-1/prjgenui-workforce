"""Remove MFA factors and challenges for a user (admin cleanup).

Usage: python research/remove_test_mfa.py <email>
"""
import os
import sys

import psycopg

email = sys.argv[1] if len(sys.argv) > 1 else 'hello@prjgenuiworkforce.co.uk'

conn = psycopg.connect(
    host='aws-0-eu-west-2.pooler.supabase.com', port=5432, dbname='postgres',
    user='postgres.houhfxugjgeyrmkmpvji',
    password=os.environ['PRJ_DB_PASSWORD'], autocommit=True)
cur = conn.cursor()

cur.execute("select id from auth.users where email = %s", (email,))
row = cur.fetchone()
if not row:
    sys.exit('no such user: ' + email)
uid = row[0]

cur.execute("select count(*) from auth.mfa_factors where user_id = %s", (uid,))
print('factors before:', cur.fetchone()[0])
cur.execute("delete from auth.mfa_challenges where factor_id in "
            "(select id from auth.mfa_factors where user_id = %s)", (uid,))
cur.execute("delete from auth.mfa_factors where user_id = %s", (uid,))
cur.execute("select count(*) from auth.mfa_factors where user_id = %s", (uid,))
print('factors after:', cur.fetchone()[0])
conn.close()
