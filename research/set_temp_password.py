import psycopg
import os

conn = psycopg.connect(
    host='aws-0-eu-west-2.pooler.supabase.com', port=5432,
    dbname='postgres', user='postgres.houhfxugjgeyrmkmpvji',
    password=os.environ['PRJ_DB_PASSWORD'], autocommit=True)
cur = conn.cursor()

cur.execute("select email_confirmed_at, last_sign_in_at "
            "from auth.users where email='hello@prjgenuiworkforce.co.uk'")
print('confirmed_at, last_sign_in_at:', cur.fetchone())

cur.execute("update auth.users "
            "set encrypted_password = crypt('Prjgen-Temp-2026!', gen_salt('bf')) "
            "where email='hello@prjgenuiworkforce.co.uk'")
print('rows updated:', cur.rowcount)
cur.close(); conn.close()
