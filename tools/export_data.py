#!/usr/bin/env python3
"""Export the full platform data as JSON (register 9.5, 9.8).

Restricted to admin roles: the run must name an Owner profile (--by),
and that profile is recorded in the audit log as the exporter. Every
export is audited; the audit log itself is exported too.

The weekly separate export (register 9.8) is this same tool on a
schedule; a recovery test should restore from an export before the
pilot.

Usage:
  python tools/export_data.py --by hello@prjgenuiworkforce.co.uk \
      [--out research/exports/prjgenui-export-YYYY-MM-DD.json]
"""

import argparse
import datetime
import json
import os

import psycopg

# The demo's kv store is not platform data; it stays in the demo.
TABLES = [
    'profiles', 'role_grants', 'invitations', 'parties', 'engagements',
    'engagement_events', 'workers', 'worker_status_history', 'rtw_checks',
    'qualifications', 'training_certificates', 'work_history', 'proof_of_work',
    'worker_documents', 'rule_versions', 'readiness_evaluations',
    'readiness_snapshots', 'expiry_schedule', 'reminder_log', 'contractors',
    'projects', 'sites', 'site_requirements', 'workforce_requests',
    'match_generations', 'matches', 'assignment_offers', 'assignments',
    'assignment_events', 'assignment_outcomes', 'assignment_statements',
    'score_events', 'performance_scores', 'overrides', 'evidence_records',
    'audit_log', 'price_catalog', 'service_subscriptions', 'external_costs',
    'schema_migrations'
]


def dump_table(cur, table):
    cur.execute('select to_jsonb(t) from %s t' % table)
    return [row[0] for row in cur.fetchall()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--by', required=True,
                    help='email of the Owner profile responsible for the export')
    ap.add_argument('--out')
    args = ap.parse_args()

    conn = psycopg.connect(
        host='aws-0-eu-west-2.pooler.supabase.com', port=5432,
        dbname='postgres', user='postgres.houhfxugjgeyrmkmpvji',
        password=os.environ['PRJ_DB_PASSWORD'])
    conn.autocommit = False
    cur = conn.cursor()

    # Admin-only: the run must name an existing Owner profile.
    cur.execute("""
        select p.id from profiles p join auth.users u on u.id = p.id
        where u.email = %s and 'owner' = any(p.roles)
    """, (args.by,))
    row = cur.fetchone()
    if not row:
        print('refused: %s is not an Owner profile' % args.by)
        raise SystemExit(1)
    actor = row[0]

    data = {'exportedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'exportedBy': args.by, 'tables': {}}
    for table in TABLES:
        try:
            data['tables'][table] = dump_table(cur, table)
        except Exception as e:
            conn.rollback()
            print('export failed at %s: %s' % (table, e))
            raise SystemExit(1)

    # The export is audited: actor, action, scope, timestamp.
    cur.execute("""
        insert into audit_log (actor, actor_role, action, table_name, record_id, new_value)
        values (%s, 'owner', 'export', 'platform', 'full', %s)
    """, (actor, json.dumps({'tables': len(TABLES),
                             'rows': sum(len(v) for v in data['tables'].values())})))
    conn.commit()

    out = args.out or ('research/exports/prjgenui-export-' +
                       datetime.date.today().isoformat() + '.json')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=1, default=str)
    print('exported %d rows across %d tables to %s (audited, by %s)' %
          (sum(len(v) for v in data['tables'].values()), len(TABLES), out, args.by))
    cur.close()
    conn.close()


if __name__ == '__main__':
    main()
