"""Measure the current database and Storage sizes for the backup cost
estimate (Marizilena's email 4, item 3).

Run (PowerShell):
  $env:PRJ_DB_PASSWORD = '<database password>'
  python research/measure_backup_size.py
"""
import os
import sys

import psycopg

PROJECT_REF = "houhfxugjgeyrmkmpvji"

password = os.environ.get("PRJ_DB_PASSWORD")
if not password:
    sys.exit("PRJ_DB_PASSWORD environment variable is not set")

conn = psycopg.connect(
    host="aws-0-eu-west-2.pooler.supabase.com", port=5432,
    user=f"postgres.{PROJECT_REF}", dbname="postgres",
    password=password, sslmode="require", connect_timeout=10)

with conn:
    with conn.cursor() as cur:
        cur.execute("select pg_database_size(current_database())")
        db_bytes = cur.fetchone()[0]
        cur.execute("""
            select count(*), coalesce(sum((metadata->>'size')::bigint), 0)
            from storage.objects
            where bucket_id = 'worker-documents'
        """)
        n_objects, storage_bytes = cur.fetchone()
        cur.execute("select count(*) from workers")
        n_workers = cur.fetchone()[0]
        cur.execute("select count(*) from assignments")
        n_assignments = cur.fetchone()[0]

gb = 1024 ** 3
print(f"database size:            {db_bytes/1024/1024:10.1f} MB")
print(f"storage objects:          {n_objects:10d}")
print(f"storage bytes:            {storage_bytes/1024/1024:10.1f} MB")
print(f"workers:                  {n_workers:10d}")
print(f"assignments:              {n_assignments:10d}")
weekly = db_bytes + storage_bytes
print(f"one weekly export:        {weekly/1024/1024:10.1f} MB (db + storage)")
print(f"12 retained copies:       {12*weekly/1024/1024:10.1f} MB total")
