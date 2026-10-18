"""Manage platform accounts for PRJGENUI Workforce.

Auth users are created through the Supabase dashboard (Authentication >
Users > Add user, with "Auto confirm user" on) — direct inserts into
auth.users do not work with the hosted auth service. This script then
links, unlinks or deletes the account's profile side.

Usage (PowerShell):
  $env:PRJ_DB_PASSWORD = '<database password>'
  python tools/accounts.py link --email hello@prjgenuiworkforce.co.uk --name "Marizilena Silva Fortes" --roles owner
  python tools/accounts.py unlink --email someone@example.com
  python tools/accounts.py delete --email someone@example.com
"""
import argparse
import sys

import psycopg

PROJECT_REF = "houhfxugjgeyrmkmpvji"
POOLER = "aws-0-eu-west-2.pooler.supabase.com"


def connect(password):
    return psycopg.connect(
        host=POOLER, port=5432, user=f"postgres.{PROJECT_REF}",
        password=password, dbname="postgres", sslmode="require")


def link(args, conn):
    """Attach a profile with roles to an existing auth user (created via the
    Supabase dashboard's Add user flow; direct inserts into auth.users do not
    work with the hosted auth service)."""
    with conn.cursor() as cur:
        cur.execute("select id from auth.users where email = %s", (args.email,))
        row = cur.fetchone()
        if not row:
            sys.exit(f"no auth user for {args.email} — create it first in the "
                     "Supabase dashboard (Authentication > Users > Add user)")
        user_id = row[0]
        cur.execute("select 1 from profiles where id = %s", (user_id,))
        if cur.fetchone():
            sys.exit(f"a profile already exists for {args.email}")
        roles = "{" + ",".join(args.roles.split(",")) + "}"
        cur.execute("""
            insert into profiles (id, full_name, roles)
            values (%s, %s, %s::prj_role[])
        """, (user_id, args.name, roles))
    conn.commit()
    print(f"linked: {args.email} (roles: {args.roles})")


def unlink(args, conn):
    with conn.cursor() as cur:
        cur.execute("""
            delete from profiles p using auth.users u
            where p.id = u.id and u.email = %s
            returning p.id
        """, (args.email,))
        row = cur.fetchone()
    conn.commit()
    if row:
        print(f"unlinked profile for {args.email} (auth user kept; "
              "audit history is kept)")
    else:
        print(f"no profile found for {args.email}")


def delete(args, conn):
    with conn.cursor() as cur:
        cur.execute("delete from auth.users where email = %s returning id",
                    (args.email,))
        row = cur.fetchone()
    conn.commit()
    if row:
        print(f"deleted: {args.email} (profile rows cascade; audit history "
              "is kept)")
    else:
        print(f"no auth user found for {args.email}")


def main():
    import os
    password = os.environ.get("PRJ_DB_PASSWORD")
    if not password:
        sys.exit("PRJ_DB_PASSWORD environment variable is not set")
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_link = sub.add_parser("link")
    p_link.add_argument("--email", required=True)
    p_link.add_argument("--name", required=True)
    p_link.add_argument("--roles", required=True,
                        help="comma-separated, e.g. owner,operations")
    p_unlink = sub.add_parser("unlink")
    p_unlink.add_argument("--email", required=True)
    p_delete = sub.add_parser("delete")
    p_delete.add_argument("--email", required=True)
    args = parser.parse_args()

    conn = connect(password)
    try:
        if args.cmd == "link":
            link(args, conn)
        elif args.cmd == "unlink":
            unlink(args, conn)
        else:
            delete(args, conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
