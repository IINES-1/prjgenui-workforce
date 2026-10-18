"""Apply a Supabase migration file to the PRJGENUI Workforce database.

Usage (PowerShell):
  $env:PRJ_DB_PASSWORD = '<database password>'
  python tools/apply_migration.py supabase/migrations/0001_stage0_foundations.sql

The password is read from the PRJ_DB_PASSWORD environment variable and is
never written to the repository. Tries the direct database connection first,
then the Supavisor pooler (session and transaction modes).
"""
import os
import sys

import psycopg

PROJECT_REF = "houhfxugjgeyrmkmpvji"


def connection_targets():
    password = os.environ.get("PRJ_DB_PASSWORD")
    if not password:
        sys.exit("PRJ_DB_PASSWORD environment variable is not set")
    common = dict(password=password, dbname="postgres", sslmode="require",
                   connect_timeout=10)
    # Session mode (5432) first — safest for DDL. The project lives on the
    # aws-0-eu-west-2 (London) Supavisor pooler; the direct db.*.supabase.co
    # host is IPv6-only and unreachable from this network.
    yield "pooler aws-0-eu-west-2:5432 (session)", {
        **common, "host": "aws-0-eu-west-2.pooler.supabase.com", "port": 5432,
        "user": f"postgres.{PROJECT_REF}"}
    yield "pooler aws-0-eu-west-2:6543 (transaction)", {
        **common, "host": "aws-0-eu-west-2.pooler.supabase.com", "port": 6543,
        "user": f"postgres.{PROJECT_REF}"}


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    path = sys.argv[1]
    sql = open(path, encoding="utf-8").read()

    conn = None
    for label, kwargs in connection_targets():
        try:
            conn = psycopg.connect(**kwargs)
            print(f"connected via: {label}")
            break
        except psycopg.Error as exc:
            print(f"failed ({label}): {exc.__class__.__name__}")
    if conn is None:
        sys.exit("could not connect via any route")

    with conn:
        with conn.cursor() as cur:
            cur.execute(sql)  # single multi-statement batch
            cur.execute("""
                select count(*) from pg_tables
                where schemaname = 'public' and tablename <> 'kv'
            """)
            tables = cur.fetchone()[0]
            cur.execute("""
                select count(*) from pg_policies
                where schemaname = 'public'
            """)
            policies = cur.fetchone()[0]
            cur.execute("select id, name from schema_migrations order by id")
            applied = cur.fetchall()
    print(f"public tables (excl kv): {tables}")
    print(f"policies: {policies}")
    print(f"schema_migrations: {applied}")
    print("OK")


if __name__ == "__main__":
    main()
