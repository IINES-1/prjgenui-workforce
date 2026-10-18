#!/usr/bin/env python3
"""Migrate the demo dashboard's kv data into the production schema.

Per docs/schema-design.md section 7: the demo's kv store is read once,
mapped to the new tables, and the result is checked against acceptance
tests before cutover. The demo stays available (read-only) until the
production system passes acceptance.

Sources (either, not both):
  --export FILE   a backup produced by the demo's "Export data" button
  --from-db       the demo's remote kv table in Supabase (key -> {data})

Mapped: contractors, projects, sites (+ site requirements), workers
(passport numbers, RTW, CSCS, training), workforce requests, match
generations + matches, assignments (historical ones as legacy_recorded,
with outcomes), readiness snapshots, and the passport/reference
sequences.

Not migrated, per the approved design: demo seed data (Easberg pilot
names: Christian, Marisa, Bene, Jepherson, Henry, Lucas; Easberg Ltd)
and crews (crew planning is a later stage).

The tool is idempotent: it skips anything already migrated (matched by
passport number or public reference) so it is safe to re-run. Everything
runs in one transaction; --dry-run rolls back at the end.

Usage:
  python tools/migrate_demo_kv.py --export prjgenui-backup.json [--dry-run]
  python tools/migrate_demo_kv.py --from-db [--dry-run]
"""

import argparse
import json
import os
import re
import sys
import uuid as uuidmod
from datetime import datetime

import psycopg

EASBERG_NAMES = {'Christian', 'Marisa', 'Bene', 'Jepherson', 'Henry', 'Lucas'}
EASBERG_CONTRACTOR = 'Easberg Ltd'

REQUEST_STATUS_MAP = {
    'OPEN': 'open', 'MATCHED': 'matched', 'OFFERED': 'offered',
    'FILLED': 'filled', 'CLOSED': 'closed'
}


def slug(text):
    if not text:
        return None
    s = re.sub(r'[^a-z0-9]+', '_', str(text).strip().lower()).strip('_')
    return s or None


def parse_date(value):
    if not value:
        return None
    s = str(value).strip()[:10]
    try:
        return datetime.strptime(s, '%Y-%m-%d').date()
    except ValueError:
        return None


def parse_ts(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    except ValueError:
        return None


class Report:
    def __init__(self):
        self.inserted = {}
        self.skipped = []

    def add(self, table, n=1):
        self.inserted[table] = self.inserted.get(table, 0) + n

    def skip(self, table, why):
        self.skipped.append('%s: %s' % (table, why))

    def dump(self):
        print()
        print('=== migration report ===')
        for table in sorted(self.inserted):
            print('  inserted %-24s %d' % (table, self.inserted[table]))
        for line in self.skipped:
            print('  skipped  ' + line)
        if not self.inserted:
            print('  (nothing to migrate)')


def load_source(args):
    if args.export:
        with open(args.export, 'r', encoding='utf-8') as f:
            payload = json.load(f)
        return {
            'workers': payload.get('workers', []),
            'contractors': payload.get('contractors', []),
            'projects': payload.get('projects', []),
            'sites': payload.get('sites', []),
            'workforceRequests': payload.get('workforceRequests', []),
            'matchGenerations': payload.get('matchGenerations', []),
            'matches': payload.get('matches', []),
            'assignmentEntities': payload.get('assignmentEntities', []),
            'readinessSnapshots': payload.get('readinessSnapshots', []),
            'meta': {
                'passportCounter': payload.get('passportCounter', 0),
                'referenceCounters': payload.get('referenceCounters', {})
            }
        }
    conn = psycopg.connect(
        host='aws-0-eu-west-2.pooler.supabase.com', port=5432,
        dbname='postgres', user='postgres.houhfxugjgeyrmkmpvji',
        password=os.environ['PRJ_DB_PASSWORD'])
    store = {}
    with conn.cursor() as cur:
        for key in ['workers', 'contractors', 'projects', 'sites',
                    'workforceRequests', 'matchGenerations', 'matches',
                    'assignmentEntities', 'readinessSnapshots', 'meta']:
            cur.execute('select value from kv where key = %s', (key,))
            row = cur.fetchone()
            v = row[0] if row else {}
            if key == 'meta':
                store[key] = v
            else:
                store[key] = v.get('data', []) if isinstance(v, dict) else []
    conn.close()
    return store


def main():
    ap = argparse.ArgumentParser()
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument('--export')
    src.add_argument('--from-db', action='store_true')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    store = load_source(args)
    rep = Report()

    conn = psycopg.connect(
        host='aws-0-eu-west-2.pooler.supabase.com', port=5432,
        dbname='postgres', user='postgres.houhfxugjgeyrmkmpvji',
        password=os.environ['PRJ_DB_PASSWORD'])
    conn.autocommit = False
    cur = conn.cursor()

    try:
        migrate(cur, store, rep)
        sync_sequences(cur, store, rep)
        if args.dry_run:
            conn.rollback()
            print('dry run: changes rolled back')
        else:
            conn.commit()
            print('committed')
        rep.dump()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def migrate(cur, store, rep):
    contractor_map = migrate_contractors(cur, store, rep)
    project_map = migrate_projects(cur, store, rep, contractor_map)
    site_map = migrate_sites(cur, store, rep, project_map)
    worker_map = migrate_workers(cur, store, rep)
    request_map = migrate_requests(cur, store, rep, contractor_map,
                                   project_map, site_map)
    gen_map = migrate_generations(cur, store, rep, request_map)
    migrate_matches(cur, store, rep, gen_map, worker_map)
    migrate_assignments(cur, store, rep, worker_map, contractor_map,
                        project_map, site_map, request_map)
    migrate_snapshots(cur, store, rep, worker_map)


def migrate_contractors(cur, store, rep):
    out = {}
    for c in store['contractors']:
        name = c.get('legalName') or c.get('name') or ''
        if not name:
            rep.skip('contractors', 'no legal name')
            continue
        if name == EASBERG_CONTRACTOR:
            rep.skip('contractors', 'Easberg Ltd is demo seed data (excluded by design)')
            continue
        cur.execute('select id from contractors where legal_name = %s', (name,))
        row = cur.fetchone()
        if row:
            out[c['id']] = row[0]
            rep.skip('contractors', name + ' already present')
            continue
        cid = uuidmod.uuid4()
        cur.execute(
            'insert into contractors (id, legal_name, contact_name, email, phone, sector, notes) '
            'values (%s,%s,%s,%s,%s,%s,%s)',
            (cid, name, c.get('primaryContact') or None, c.get('email') or None,
             c.get('phone') or None, c.get('sector') or None, c.get('notes') or None))
        out[c['id']] = cid
        rep.add('contractors')
    return out


def migrate_projects(cur, store, rep, contractor_map):
    out = {}
    for p in store['projects']:
        cid = contractor_map.get(p.get('contractorId'))
        if not cid:
            rep.skip('projects', (p.get('name') or '?') + ': contractor not migrated')
            continue
        cur.execute('select id, contractor_id from projects where name = %s', (p.get('name') or '',))
        row = cur.fetchone()
        if row and row[1] == cid:
            out[p['id']] = row[0]
            rep.skip('projects', (p.get('name') or '?') + ' already present')
            continue
        pid = uuidmod.uuid4()
        notes = p.get('description') or None
        if p.get('publicReference'):
            notes = (('public ref ' + p['publicReference'] + '; ') if notes else 'public ref ' + p['publicReference'] + '; ') + (notes or '')
        cur.execute('insert into projects (id, contractor_id, name, sector, notes) values (%s,%s,%s,%s,%s)',
                    (pid, cid, p.get('name') or 'Unnamed project', None, notes))
        out[p['id']] = pid
        rep.add('projects')
    return out


def migrate_sites(cur, store, rep, project_map):
    out = {}
    for s in store['sites']:
        pid = project_map.get(s.get('projectId'))
        if not pid:
            rep.skip('sites', (s.get('name') or '?') + ': project not migrated')
            continue
        cur.execute('select id, project_id from sites where name = %s', (s.get('name') or '',))
        row = cur.fetchone()
        if row and row[1] == pid:
            out[s['id']] = row[0]
            rep.skip('sites', (s.get('name') or '?') + ' already present')
            continue
        sid = uuidmod.uuid4()
        location = ' '.join(x for x in [s.get('address'), s.get('postcode')] if x) or None
        cur.execute('insert into sites (id, project_id, name, location, notes) values (%s,%s,%s,%s,%s)',
                    (sid, pid, s.get('name') or 'Unnamed site', location, s.get('notes') or None))
        for req in (s.get('requirements') or []):
            label = req.get('label') if isinstance(req, dict) else str(req)
            req_slug = slug(label) or slug(req.get('value') if isinstance(req, dict) else label)
            if req_slug:
                cur.execute('insert into site_requirements (site_id, requirement, mandatory) values (%s,%s,true)',
                            (sid, req_slug))
                rep.add('site_requirements')
        out[s['id']] = sid
        rep.add('sites')
    return out


def migrate_workers(cur, store, rep):
    out = {}
    for w in store['workers']:
        ident = w.get('identity') or {}
        name = ident.get('fullName') or w.get('name') or ''
        if name in EASBERG_NAMES:
            rep.skip('workers', name + ' is Easberg demo seed data (excluded by design)')
            continue
        if not name:
            rep.skip('workers', 'no full name')
            continue
        passport = ident.get('passportId')
        wid = None
        if passport:
            cur.execute('select id from workers where passport_no = %s', (passport,))
            row = cur.fetchone()
            if row:
                out[w['id']] = row[0]
                rep.skip('workers', name + ' (' + passport + ') already present')
                continue
        wid = uuidmod.uuid4()
        rtw = w.get('rightToWork') or {}
        cscs = w.get('cscs') or {}
        trade = (w.get('tradeProfile') or {}).get('primaryTrade') or None
        if ident.get('status', 'active') != 'active':
            status = 'draft'
        elif rtw.get('status') == 'verified' and cscs.get('status') == 'verified':
            status = 'verified'
        else:
            status = 'in_review'
        cur.execute(
            'insert into workers (id, passport_no, full_name, phone, email, trade, availability, status) '
            'values (%s,%s,%s,%s,%s,%s,%s,%s)',
            (wid, passport, name, ident.get('phone') or None, ident.get('email') or None,
             trade, (w.get('commercial') or {}).get('availability') or None, status))
        rep.add('workers')

        if rtw.get('status') and rtw.get('status') != 'not_verified':
            result = 'pass' if rtw.get('status') == 'verified' else 'follow_up_required'
            cur.execute(
                'insert into rtw_checks (worker_id, method, check_date, result, reference_no, source) '
                'values (%s,%s,%s,%s,%s,%s)',
                (wid, rtw.get('method') or 'demo_record', parse_date(rtw.get('checkedDate')) or parse_date(rtw.get('expiryDate')),
                 result, rtw.get('reference') or None, 'demo migration'))
            rep.add('rtw_checks')

        if cscs.get('status') and cscs.get('status') != 'not_checked':
            cur.execute(
                'insert into qualifications (worker_id, kind, card_type, number, status, issue_date, expiry_date) '
                'values (%s,%s,%s,%s,%s,%s,%s)',
                (wid, 'cscs', cscs.get('cardType') or None, cscs.get('registrationNumber') or None,
                 'verified' if cscs.get('status') == 'verified' else 'pending_review',
                 parse_date(cscs.get('issueDate')), parse_date(cscs.get('expiryDate'))))
            rep.add('qualifications')

        for t in (w.get('trainingCertificates') or []):
            t_slug = slug(t.get('name'))
            if not t_slug:
                continue
            verified = bool(t.get('verified') or t.get('confirmedBy'))
            cur.execute(
                'insert into training_certificates (worker_id, training_type, status, issue_date, expiry_date) '
                'values (%s,%s,%s,%s,%s)',
                (wid, t_slug, 'verified' if verified else 'pending_review',
                 parse_date(t.get('issueDate')), parse_date(t.get('expiryDate'))))
            rep.add('training_certificates')
        out[w['id']] = wid
    return out


def migrate_requests(cur, store, rep, contractor_map, project_map, site_map):
    out = {}
    for r in store['workforceRequests']:
        cid = contractor_map.get(r.get('contractorId'))
        if not cid:
            rep.skip('workforce_requests', (r.get('publicReference') or r.get('tradeRequired') or '?') + ': contractor not migrated')
            continue
        ref = r.get('publicReference')
        if ref:
            cur.execute('select id from workforce_requests where public_reference = %s', (ref,))
            row = cur.fetchone()
            if row:
                out[r['id']] = row[0]
                rep.skip('workforce_requests', ref + ' already present')
                continue
        reqs = []
        for t in (r.get('requiredTraining') or []):
            label = t.get('label') if isinstance(t, dict) else t
            s = slug(label)
            if s:
                reqs.append(s)
        rid = uuidmod.uuid4()
        cur.execute(
            'insert into workforce_requests (id, contractor_id, project_id, site_id, public_reference, '
            'trade, number_needed, start_date, duration, essential_requirements, urgent, status) '
            'values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            (rid, cid, project_map.get(r.get('projectId')), site_map.get(r.get('siteId')),
             ref, r.get('tradeRequired') or 'unspecified', r.get('quantity') or 1,
             parse_date(r.get('startDate')), r.get('endDate') or None,
             json.dumps(reqs), False,
             REQUEST_STATUS_MAP.get(str(r.get('status', 'OPEN')).upper(), 'open')))
        out[r['id']] = rid
        rep.add('workforce_requests')
    return out


def migrate_generations(cur, store, rep, request_map):
    out = {}
    for g in store['matchGenerations']:
        rid = request_map.get(g.get('requestId'))
        if not rid:
            rep.skip('match_generations', 'request not migrated')
            continue
        created = parse_ts(g.get('generatedAt'))
        # Idempotency: a generation is identified by its request and the
        # moment it was generated.
        cur.execute(
            'select id from match_generations where request_id = %s and created_at = coalesce(%s, created_at)',
            (rid, created))
        row = cur.fetchone()
        if row:
            out[g['id']] = row[0]
            rep.skip('match_generations', 'generation for this request and time already present')
            continue
        gen_id = uuidmod.uuid4()
        cur.execute(
            'insert into match_generations (id, request_id, rules_version, created_at) '
            'values (%s,%s,%s,coalesce(%s, now()))',
            (gen_id, rid, '0.1', created))
        out[g['id']] = gen_id
        rep.add('match_generations')
    return out


def migrate_matches(cur, store, rep, gen_map, worker_map):
    rank_by_gen = {}
    for m in store['matches']:
        gen_id = gen_map.get(m.get('generationId'))
        wid = worker_map.get(m.get('workerId'))
        if not gen_id or not wid:
            rep.skip('matches', 'generation or worker not migrated')
            continue
        # Idempotency: one match per worker per generation.
        cur.execute('select 1 from matches where generation_id = %s and worker_id = %s',
                    (gen_id, wid))
        if cur.fetchone():
            rep.skip('matches', 'worker already has a match in this generation')
            continue
        eligible = bool(m.get('eligible'))
        rank = None
        if eligible:
            rank_by_gen[gen_id] = rank_by_gen.get(gen_id, 0) + 1
            rank = rank_by_gen[gen_id]
        cur.execute('insert into matches (generation_id, worker_id, factors, rank) values (%s,%s,%s,%s)',
                    (gen_id, wid, json.dumps(m.get('factors') or []), rank))
        rep.add('matches')


def migrate_assignments(cur, store, rep, worker_map, contractor_map,
                        project_map, site_map, request_map):
    for a in store['assignmentEntities']:
        wid = worker_map.get(a.get('workerId'))
        if not wid:
            rep.skip('assignments', (a.get('publicReference') or '?') + ': worker not migrated')
            continue
        ref = a.get('publicReference')
        if ref:
            cur.execute('select id from assignments where public_reference = %s', (ref,))
            row = cur.fetchone()
            if row:
                rep.skip('assignments', ref + ' already present')
                continue
        legacy = bool(a.get('legacyRecord')) or a.get('attended') is not None or a.get('rating')
        # A demo assignment is historical by definition: anything not a
        # live proposal is recorded as legacy_recorded (no gate on insert
        # is relied on for these; the flag marks them as pre-production).
        demo_status = str(a.get('status', 'PROPOSED')).upper()
        status = 'proposed' if (not legacy and demo_status == 'PROPOSED') else 'legacy_recorded'
        asg_id = uuidmod.uuid4()
        cur.execute(
            'insert into assignments (id, public_reference, request_id, worker_id, contractor_id, '
            'project_id, site_id, trade, start_date, end_date, worker_pay_rate, client_charge_rate, '
            'status, legacy_record, legacy_client_text, legacy_project_label) '
            'values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            (asg_id, ref, request_map.get(a.get('requestId')), wid,
             contractor_map.get(a.get('contractorId')), project_map.get(a.get('projectId')),
             site_map.get(a.get('siteId')), a.get('trade') or None,
             parse_date(a.get('startDate')) or parse_date(a.get('date')),
             parse_date(a.get('endDate')), a.get('workerPayRate') or None,
             a.get('clientChargeRate') or None, status, legacy,
             a.get('legacyClientText') or None, a.get('legacyProjectLabel') or None))
        rep.add('assignments')
        if legacy and (a.get('attended') is not None or a.get('rating')):
            rehire = a.get('rehireDecision')
            rehire = rehire if rehire in ('yes', 'no') else 'undecided'
            cur.execute(
                'insert into assignment_outcomes (assignment_id, attended, rating, rehire_decision, '
                'client_feedback, supervisor_feedback) values (%s,%s,%s,%s,%s,%s)',
                (asg_id, bool(a.get('attended')), a.get('rating'), rehire,
                 a.get('clientFeedback') or None, a.get('supervisorFeedback') or None))
            rep.add('assignment_outcomes')


def migrate_snapshots(cur, store, rep, worker_map):
    for s in store['readinessSnapshots']:
        wid = worker_map.get(s.get('workerId'))
        if not wid:
            rep.skip('readiness_snapshots', 'worker not migrated')
            continue
        created = parse_ts(s.get('capturedAt'))
        # Idempotency: one snapshot per worker per capture time.
        cur.execute('select 1 from readiness_snapshots where worker_id = %s and created_at = coalesce(%s, created_at)',
                    (wid, created))
        if cur.fetchone():
            rep.skip('readiness_snapshots', 'snapshot for this worker and time already present')
            continue
        cur.execute(
            'insert into readiness_snapshots (worker_id, snapshot, created_at) '
            'values (%s,%s,coalesce(%s, now()))',
            (wid, json.dumps({k: v for k, v in s.items() if k != 'id'}),
             created))
        rep.add('readiness_snapshots')


def sync_sequences(cur, store, rep):
    meta = store.get('meta') or {}
    def nextval_of(seq):
        cur.execute("select last_value from %s" % seq)
        return cur.fetchone()[0]
    def set_seq(seq, value):
        if value and value > nextval_of(seq):
            cur.execute("select setval(%s, %s, false)", (seq, value))
    set_seq('worker_passport_seq', meta.get('passportCounter', 0))
    counters = meta.get('referenceCounters') or {}
    set_seq('request_ref_seq', counters.get('request', 0))
    set_seq('assignment_ref_seq', counters.get('assignment', 0))


if __name__ == '__main__':
    sys.exit(main())
