"""Rotate the hello@ shared-account password (the old one was emailed).

Usage: python research/rotate_hello_password.py <new password>
"""
import os
import sys

import psycopg

new_password = sys.argv[1]
conn = psycopg.connect(
    host='aws-0-eu-west-2.pooler.supabase.com', port=5432, dbname='postgres',
    user='postgres.houhfxugjgeyrmkmpvji',
    password=os.environ['PRJ_DB_PASSWORD'], autocommit=True)
cur = conn.cursor()
cur.execute("update auth.users "
            "set encrypted_password = crypt(%s, gen_salt('bf')) "
            "where email = 'hello@prjgenuiworkforce.co.uk'", (new_password,))
print('hello@ password rotated, rows updated:', cur.rowcount)
cur.close(); conn.close()
