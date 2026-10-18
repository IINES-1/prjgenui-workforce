-- =====================================================================
-- PRJGENUI Workforce — Stage 0 foundations (migration 0001)
-- Approved schema design v1.0, 18 October 2026.
--
-- Creates table groups A (identity/access), B (party model, structure
-- only), C (worker records), D (readiness/gate), E (assignments/matching),
-- G (performance evidence), H (audit/overrides/provenance), with:
--   - row-level security, default deny
--   - an append-only audit log
--   - enforced status transitions
--   - the hard deployment gate (assignment cannot confirm without a pass)
--
-- Table groups F (incidents) and I (commercial) are Stage 1 and are NOT
-- created here, per the approved design.
-- The demo's `kv` table is untouched and stays working until cutover.
-- =====================================================================

create extension if not exists pgcrypto;

-- ---------------------------------------------------------------- enums
create type prj_role            as enum ('owner','operations','compliance','contractor','worker','supplier','auditor');
create type worker_status       as enum ('draft','in_review','verified','expiring_soon','blocked','archived');
create type evidence_status     as enum ('pending_review','verified','rejected');
create type assignment_status   as enum ('proposed','confirmed','completed','cancelled','legacy_recorded');
create type request_status      as enum ('open','matched','offered','filled','closed');
create type party_role          as enum ('engaging_party','paying_party','introducing_party','matching_operator','rtw_responsible','check_performer');

-- ---------------------------------------------------------------- schema app
create schema if not exists app;

-- Note: the helper functions (user_id, has_role, my_worker_id) are created
-- AFTER the tables, below, because Postgres validates LANGUAGE sql function
-- bodies (including table references) at CREATE FUNCTION time.

-- ---------------------------------------------------------------- A: identity and access

create table profiles (
  id            uuid primary key references auth.users(id) on delete cascade,
  full_name     text not null,
  roles         prj_role[] not null default '{}',
  contractor_id uuid,                       -- fk added after contractors exists
  worker_id     uuid,                       -- fk added after workers exists
  status        text not null default 'active' check (status in ('active','retired','invited')),
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now(),
  retired_at    timestamptz
);

create table role_grants (
  id          uuid primary key default gen_random_uuid(),
  grantee     uuid not null references profiles(id) on delete cascade,
  role        prj_role not null,
  granted_by  uuid references profiles(id),
  granted_at  timestamptz not null default now(),
  reason      text
);

create table invitations (
  id           uuid primary key default gen_random_uuid(),
  email        text not null,
  role         prj_role not null,
  contractor_id uuid,
  worker_id     uuid,
  token        uuid not null default gen_random_uuid(),
  invited_by   uuid not null references profiles(id),
  expires_at   timestamptz not null default now() + interval '7 days',
  used_at      timestamptz,
  created_at   timestamptz not null default now()
);

-- ---------------------------------------------------------------- B: party model (structure now, values after the legal opinion)

create table parties (
  id           uuid primary key default gen_random_uuid(),
  kind         text not null check (kind in ('company','worker','prjgenui','supplier')),
  name         text not null,
  company_no   text,
  created_at   timestamptz not null default now(),
  updated_at   timestamptz not null default now()
);

create table engagements (
  id          uuid primary key default gen_random_uuid(),
  assignment_id uuid,                       -- fk added after assignments exists
  party_id    uuid not null references parties(id),
  party_role  party_role not null,
  recorded_by uuid references profiles(id),
  recorded_at timestamptz not null default now(),
  unique (assignment_id, party_role, party_id)
);

create table engagement_events (
  id           uuid primary key default gen_random_uuid(),
  engagement_id uuid not null references engagements(id) on delete cascade,
  changed_by   uuid references profiles(id),
  changed_at  timestamptz not null default now(),
  note         text
);

-- ---------------------------------------------------------------- C: worker records

create table workers (
  id                uuid primary key default gen_random_uuid(),
  passport_no       text unique,            -- PW-UK-000001 format, allocated by app
  full_name         text not null,
  phone             text,
  email             text,
  trade             text,
  availability      text,
  status            worker_status not null default 'draft',
  status_reason     text,
  created_at        timestamptz not null default now(),
  updated_at        timestamptz not null default now()
);

create table worker_status_history (
  id          uuid primary key default gen_random_uuid(),
  worker_id   uuid not null references workers(id) on delete cascade,
  from_status worker_status,
  to_status   worker_status not null,
  reason      text,
  actor       uuid references profiles(id),
  created_at  timestamptz not null default now()
);

create table rtw_checks (
  id                uuid primary key default gen_random_uuid(),
  worker_id         uuid not null references workers(id) on delete cascade,
  method            text not null,          -- e.g. home_office_share_code, manual_passport
  check_date        date not null,
  result            text not null check (result in ('pass','fail','follow_up_required')),
  restrictions      text,
  follow_up_due     date,                   -- when a follow-up check is required
  source            text not null,          -- system/service used
  reference_no      text,
  identity_match    boolean not null default false,
  performer         uuid references profiles(id),   -- who carried it out
  evidence_id       uuid,                   -- fk added after evidence_records exists
  retention_until   date,                   -- 2 years after relationship ends
  created_at        timestamptz not null default now(),
  updated_at        timestamptz not null default now()
);

create table qualifications (
  id                uuid primary key default gen_random_uuid(),
  worker_id         uuid not null references workers(id) on delete cascade,
  kind              text not null,           -- 'cscs', 'nvq', 'city_guilds', 'ipaf', 'pasma', ...
  card_type         text,
  number            text,
  status            evidence_status not null default 'pending_review',
  evidence_id       uuid,
  issue_date        date,
  expiry_date       date,
  created_at        timestamptz not null default now(),
  updated_at        timestamptz not null default now()
);

create table training_certificates (
  id                uuid primary key default gen_random_uuid(),
  worker_id         uuid not null references workers(id) on delete cascade,
  training_type     text not null,          -- 'asbestos_awareness','working_at_height', ...
  status            evidence_status not null default 'pending_review',
  evidence_id       uuid,
  issue_date        date,
  expiry_date       date,
  created_at        timestamptz not null default now(),
  updated_at        timestamptz not null default now()
);

create table work_history (
  id                uuid primary key default gen_random_uuid(),
  worker_id         uuid not null references workers(id) on delete cascade,
  period_start      date,
  period_end        date,
  description       text,
  reference_contact text,
  supervisor_feedback text,
  created_at        timestamptz not null default now()
);

create table proof_of_work (
  id                uuid primary key default gen_random_uuid(),
  worker_id         uuid not null references workers(id) on delete cascade,
  skill             text not null,          -- e.g. 'cutting in on satinwood'
  description       text,
  supervisor        text,
  confirmed_by      uuid references profiles(id),
  status            evidence_status not null default 'pending_review',
  created_at        timestamptz not null default now()
);

create table worker_documents (
  id                uuid primary key default gen_random_uuid(),
  worker_id         uuid not null references workers(id) on delete cascade,
  document_type     text not null,          -- 'passport','cscs_card','certificate', ...
  storage_path      text not null,          -- private bucket; access via signed URL only
  uploaded_by       uuid references profiles(id),
  status            evidence_status not null default 'pending_review',
  retention_class   text,
  deletion_due      date,
  created_at        timestamptz not null default now()
);

-- ---------------------------------------------------------------- D: readiness and the gate

create table rule_versions (
  id            uuid primary key default gen_random_uuid(),
  rule_set      text not null check (rule_set in ('readiness','scoring','matching')),
  version       text not null,
  rules         jsonb not null,
  effective_from timestamptz not null default now(),
  created_by    uuid references profiles(id),
  created_at    timestamptz not null default now(),
  unique (rule_set, version)
);

create table readiness_evaluations (
  id             uuid primary key default gen_random_uuid(),
  worker_id      uuid not null references workers(id) on delete cascade,
  assignment_id  uuid,                     -- fk added after assignments exists
  rules_version  text not null,
  outcome        text not null check (outcome in ('pass','blocked')),
  blockers       jsonb not null default '[]',   -- [{code, reason, mandatory}]
  evaluated_by   uuid references profiles(id),
  created_at     timestamptz not null default now()
);

create table readiness_snapshots (
  id            uuid primary key default gen_random_uuid(),
  offer_id      uuid,                      -- fk added after assignment_offers exists
  worker_id     uuid not null references workers(id) on delete cascade,
  snapshot      jsonb not null,
  created_at    timestamptz not null default now()
);

create table expiry_schedule (
  id            uuid primary key default gen_random_uuid(),
  worker_id     uuid not null references workers(id) on delete cascade,
  item_table    text not null,              -- 'rtw_checks','qualifications','training_certificates'
  item_id       uuid not null,
  expiry_date   date not null,
  band          text not null check (band in ('expired','due_soon','watch','current')),
  computed_at   timestamptz not null default now(),
  unique (item_table, item_id)
);

create table reminder_log (
  id            uuid primary key default gen_random_uuid(),
  worker_id     uuid not null references workers(id) on delete cascade,
  item_table    text not null,
  item_id       uuid not null,
  milestone     text not null check (milestone in ('60d','30d','14d','7d')),
  channel       text not null,
  sent_at       timestamptz not null default now(),
  sent_by       text not null
);

-- ---------------------------------------------------------------- E: contractors, projects, requests, assignments

create table contractors (
  id           uuid primary key default gen_random_uuid(),
  legal_name   text not null,
  contact_name text,
  email        text,
  phone        text,
  sector       text,
  notes        text,
  created_at   timestamptz not null default now(),
  updated_at   timestamptz not null default now()
);

alter table profiles add constraint profiles_contractor_fk
  foreign key (contractor_id) references contractors(id);
alter table invitations add constraint invitations_contractor_fk
  foreign key (contractor_id) references contractors(id);

create table projects (
  id            uuid primary key default gen_random_uuid(),
  contractor_id uuid not null references contractors(id) on delete cascade,
  name          text not null,
  sector        text,
  notes         text,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);

create table sites (
  id            uuid primary key default gen_random_uuid(),
  project_id    uuid not null references projects(id) on delete cascade,
  name          text not null,
  location      text,
  notes         text,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);

create table site_requirements (
  id            uuid primary key default gen_random_uuid(),
  site_id       uuid not null references sites(id) on delete cascade,
  requirement   text not null,             -- e.g. 'cscs_blue','asbestos_awareness'
  mandatory     boolean not null default true,
  created_at    timestamptz not null default now()
);

create table workforce_requests (
  id             uuid primary key default gen_random_uuid(),
  contractor_id  uuid not null references contractors(id),
  project_id     uuid references projects(id),
  site_id        uuid references sites(id),
  public_reference text unique,
  trade          text not null,
  number_needed  int not null default 1,
  start_date     date,
  duration       text,
  essential_requirements jsonb not null default '[]',
  urgent         boolean not null default false,
  status         request_status not null default 'open',
  created_by     uuid references profiles(id),
  created_at     timestamptz not null default now(),
  updated_at     timestamptz not null default now()
);

create table match_generations (
  id            uuid primary key default gen_random_uuid(),
  request_id    uuid not null references workforce_requests(id) on delete cascade,
  rules_version text not null,
  generated_by  uuid references profiles(id),
  created_at    timestamptz not null default now()
);

create table matches (
  id             uuid primary key default gen_random_uuid(),
  generation_id  uuid not null references match_generations(id) on delete cascade,
  worker_id      uuid not null references workers(id) on delete cascade,
  factors        jsonb not null default '[]',  -- [{code,label,result:pass|fail|review}]
  rank           int,
  created_at     timestamptz not null default now()
);

create table assignment_offers (
  id            uuid primary key default gen_random_uuid(),
  request_id    uuid not null references workforce_requests(id),
  worker_id     uuid not null references workers(id),
  offered_by    uuid references profiles(id),
  expires_at    timestamptz,
  accepted_at   timestamptz,
  created_at    timestamptz not null default now()
);

create table assignments (
  id                uuid primary key default gen_random_uuid(),
  public_reference  text unique,
  request_id        uuid references workforce_requests(id),
  offer_id          uuid references assignment_offers(id),
  worker_id         uuid not null references workers(id),
  contractor_id     uuid references contractors(id),
  project_id        uuid references projects(id),
  site_id           uuid references sites(id),
  trade             text,
  role              text,
  start_date        date,
  end_date          date,
  worker_pay_rate   text,
  client_charge_rate text,
  status            assignment_status not null default 'proposed',
  legacy_record     boolean not null default false,
  legacy_client_text text,
  legacy_project_label text,
  created_at        timestamptz not null default now(),
  updated_at        timestamptz not null default now()
);

alter table engagements add constraint engagements_assignment_fk
  foreign key (assignment_id) references assignments(id) on delete cascade;
alter table readiness_evaluations add constraint readiness_evaluations_assignment_fk
  foreign key (assignment_id) references assignments(id) on delete cascade;
alter table readiness_snapshots add constraint readiness_snapshots_offer_fk
  foreign key (offer_id) references assignment_offers(id) on delete cascade;

create table assignment_events (
  id            uuid primary key default gen_random_uuid(),
  assignment_id uuid not null references assignments(id) on delete cascade,
  from_status   assignment_status,
  to_status     assignment_status not null,
  note          text,
  actor         uuid references profiles(id),
  created_at    timestamptz not null default now()
);

create table assignment_outcomes (
  assignment_id     uuid primary key references assignments(id) on delete cascade,
  attended         boolean,
  rating           int check (rating between 1 and 5),
  rehire_decision   text,
  client_feedback   text,
  supervisor_feedback text,
  recorded_by      uuid references profiles(id),
  recorded_at      timestamptz not null default now()
);

-- Statement structure now; generation workflow is Stage 1.
create table assignment_statements (
  id            uuid primary key default gen_random_uuid(),
  assignment_id uuid not null references assignments(id) on delete cascade,
  version       int not null default 1,
  content       jsonb not null,
  generated_at  timestamptz not null default now(),
  generated_by  uuid references profiles(id),
  unique (assignment_id, version)
);

-- ---------------------------------------------------------------- G: performance evidence

create table score_events (
  id            uuid primary key default gen_random_uuid(),
  worker_id     uuid not null references workers(id) on delete cascade,
  assignment_id uuid references assignments(id) on delete set null,
  factor        text not null,             -- 'competence','reliability','client_feedback'
  value         numeric,
  source_table  text,
  source_id     uuid,
  created_at    timestamptz not null default now()
);

create table performance_scores (
  worker_id     uuid primary key references workers(id) on delete cascade,
  score         numeric,
  band          text,
  weights_version text not null,
  updated_at    timestamptz not null default now()
);

-- ---------------------------------------------------------------- H: audit, overrides, provenance

create table evidence_records (
  id            uuid primary key default gen_random_uuid(),
  source_system text not null,             -- 'cscs_smart_check','home_office','manual', ...
  method        text not null,
  checker       uuid references profiles(id),
  reference    text,
  result        text not null,
  payload       jsonb,                      -- verification response summary
  created_at    timestamptz not null default now()
);

alter table rtw_checks add constraint rtw_checks_evidence_fk
  foreign key (evidence_id) references evidence_records(id);
alter table qualifications add constraint qualifications_evidence_fk
  foreign key (evidence_id) references evidence_records(id);
alter table training_certificates add constraint training_certificates_evidence_fk
  foreign key (evidence_id) references evidence_records(id);

create table audit_log (
  id           bigint generated always as identity primary key,
  actor        uuid,
  actor_role   prj_role,
  action       text not null,               -- 'insert','update','status_change','override', ...
  table_name   text not null,
  record_id    text,
  old_value    jsonb,
  new_value    jsonb,
  reason       text,
  created_at   timestamptz not null default now()
);
revoke update on audit_log from anon, authenticated;
revoke delete on audit_log from anon, authenticated;

create table overrides (
  id            uuid primary key default gen_random_uuid(),
  worker_id     uuid not null references workers(id) on delete cascade,
  assignment_id uuid references assignments(id) on delete cascade,
  requirement   text not null,
  reason        text not null,
  evidence_id   uuid references evidence_records(id),
  approved_by   uuid not null references profiles(id),
  expires_at    timestamptz,
  created_at    timestamptz not null default now()
);

-- ---------------------------------------------------------------- migrations bookkeeping
create table if not exists schema_migrations (
  id          int primary key,
  name        text not null,
  applied_at  timestamptz not null default now()
);

-- ---------------------------------------------------------------- helper functions
-- (created here, after the tables, because LANGUAGE sql bodies are validated
-- at CREATE time; see note above)

create or replace function app.user_id() returns uuid
language sql stable as $$ select auth.uid() $$;

-- The current user's roles, from their profile row.
create or replace function app.has_role(r prj_role) returns boolean
language sql stable security definer set search_path = public as $$
  select coalesce(exists (
    select 1 from profiles p
    where p.id = auth.uid() and p.status = 'active' and r = any(p.roles)
  ), false)
$$;

-- The worker record linked to the current user (for worker self-view).
create or replace function app.my_worker_id() returns uuid
language sql stable security definer set search_path = public as $$
  select worker_id from profiles where id = auth.uid()
$$;

-- =================================================================
-- Triggers: updated_at, audit, status enforcement, hard gate
-- =================================================================

create or replace function app.set_updated_at() returns trigger
language plpgsql as $$
begin
  new.updated_at := now();
  return new;
end $$;

do $$
declare t text;
begin
  foreach t in array array['profiles','parties','workers','rtw_checks','qualifications',
    'training_certificates','contractors','projects','sites','workforce_requests','assignments']
  loop
    execute format('create trigger set_updated_at_%s before update on %I
      for each row execute function app.set_updated_at()', t, t);
  end loop;
end $$;

-- Generic audit writer: every insert/update on audited tables lands in audit_log.
create or replace function app.audit_row() returns trigger
language plpgsql security definer set search_path = public as $$
declare
  v_record text;
begin
  v_record := coalesce(new.id::text, old.id::text);
  insert into audit_log (actor, action, table_name, record_id, old_value, new_value)
  values (
    app.user_id(),
    lower(tg_op),
    tg_table_name,
    v_record,
    case when tg_op <> 'insert' then to_jsonb(old) end,
    case when tg_op <> 'delete' then to_jsonb(new) end
  );
  return coalesce(new, old);
end $$;

do $$
declare t text;
begin
  foreach t in array array['profiles','role_grants','invitations','parties','engagements',
    'engagement_events','workers','worker_status_history','rtw_checks','qualifications',
    'training_certificates','work_history','proof_of_work','worker_documents',
    'rule_versions','readiness_evaluations','readiness_snapshots','expiry_schedule',
    'reminder_log','contractors','projects','sites','site_requirements',
    'workforce_requests','match_generations','matches','assignment_offers','assignments',
    'assignment_events','assignment_outcomes','assignment_statements','score_events',
    'performance_scores','overrides','evidence_records']
  loop
    execute format('create trigger audit_%s after insert or update or delete on %I
      for each row execute function app.audit_row()', t, t);
  end loop;
end $$;

-- Worker status: forward-only except to blocked/archived, always with a reason.
-- (Enum comparison uses declaration order: draft < in_review < verified <
-- expiring_soon < blocked < archived, which is the approved sequence.)
create or replace function app.enforce_worker_status() returns trigger
language plpgsql as $$
begin
  if new.status = old.status then return new; end if;
  if new.status not in ('blocked','archived') and new.status < old.status then
    raise exception 'worker status cannot move backwards from % to %', old.status, new.status;
  end if;
  if new.status in ('blocked','archived') and coalesce(new.status_reason,'') = '' then
    raise exception 'blocking or archiving a worker requires a reason';
  end if;
  insert into worker_status_history (worker_id, from_status, to_status, reason, actor)
  values (new.id, old.status, new.status, new.status_reason, app.user_id());
  return new;
end $$;

create trigger enforce_worker_status before update on workers
  for each row execute function app.enforce_worker_status();

-- Assignment status: permitted transitions only, and the hard gate on confirm.
create or replace function app.enforce_assignment_status() returns trigger
language plpgsql as $$
declare
  v_pass boolean;
begin
  if new.status = old.status then return new; end if;

  if not (
    (old.status = 'proposed'  and new.status in ('confirmed','cancelled')) or
    (old.status = 'confirmed' and new.status in ('completed','cancelled')) or
    (new.status = 'legacy_recorded')
  ) then
    raise exception 'assignment cannot move from % to %', old.status, new.status;
  end if;

  -- HARD DEPLOYMENT GATE: no confirmation without a current passing readiness
  -- evaluation for this worker — either for this assignment, or worker-level
  -- (assignment_id null), whichever is the latest evaluation.
  if new.status = 'confirmed' and old.status = 'proposed' then
    select exists (
      select 1 from readiness_evaluations re
      where re.worker_id = new.worker_id
        and (re.assignment_id = new.id or re.assignment_id is null)
        and re.outcome = 'pass'
        and re.created_at = (
          select max(created_at) from readiness_evaluations
          where worker_id = new.worker_id
            and (assignment_id = new.id or assignment_id is null)
        )
    ) into v_pass;
    if not v_pass then
      raise exception 'hard gate: assignment cannot be confirmed without a current passing readiness evaluation';
    end if;
  end if;

  insert into assignment_events (assignment_id, from_status, to_status, note, actor)
  values (new.id, old.status, new.status, null, app.user_id());
  return new;
end $$;

create trigger enforce_assignment_status before update on assignments
  for each row execute function app.enforce_assignment_status();

-- =================================================================
-- Row-level security: default deny, then grant per the approved matrix
-- =================================================================

alter table profiles            enable row level security;
alter table role_grants         enable row level security;
alter table invitations         enable row level security;
alter table parties             enable row level security;
alter table engagements         enable row level security;
alter table engagement_events   enable row level security;
alter table workers             enable row level security;
alter table worker_status_history enable row level security;
alter table rtw_checks          enable row level security;
alter table qualifications      enable row level security;
alter table training_certificates enable row level security;
alter table work_history        enable row level security;
alter table proof_of_work       enable row level security;
alter table worker_documents    enable row level security;
alter table rule_versions       enable row level security;
alter table readiness_evaluations enable row level security;
alter table readiness_snapshots enable row level security;
alter table expiry_schedule     enable row level security;
alter table reminder_log        enable row level security;
alter table contractors         enable row level security;
alter table projects            enable row level security;
alter table sites               enable row level security;
alter table site_requirements   enable row level security;
alter table workforce_requests  enable row level security;
alter table match_generations   enable row level security;
alter table matches             enable row level security;
alter table assignment_offers   enable row level security;
alter table assignments         enable row level security;
alter table assignment_events   enable row level security;
alter table assignment_outcomes enable row level security;
alter table assignment_statements enable row level security;
alter table score_events        enable row level security;
alter table performance_scores  enable row level security;
alter table evidence_records    enable row level security;
alter table audit_log           enable row level security;
alter table overrides           enable row level security;
alter table schema_migrations   enable row level security;

-- Everyone authenticated can see a minimal profile directory.
create policy profiles_read on profiles for select to authenticated
  using (true);
create policy profiles_write on profiles for all to authenticated
  using (app.has_role('owner')) with check (app.has_role('owner'));

create policy role_grants_all on role_grants for all to authenticated
  using (app.has_role('owner')) with check (app.has_role('owner'));

create policy invitations_all on invitations for all to authenticated
  using (app.has_role('owner') or app.has_role('operations'))
  with check (app.has_role('owner') or app.has_role('operations'));

create policy parties_all on parties for all to authenticated
  using (app.has_role('owner') or app.has_role('operations') or app.has_role('compliance') or app.has_role('auditor'))
  with check (app.has_role('owner') or app.has_role('operations'));

create policy engagements_rw on engagements for all to authenticated
  using (app.has_role('owner') or app.has_role('operations') or app.has_role('auditor'))
  with check (app.has_role('owner') or app.has_role('operations'));
create policy engagement_events_rw on engagement_events for all to authenticated
  using (app.has_role('owner') or app.has_role('operations') or app.has_role('auditor'))
  with check (app.has_role('owner') or app.has_role('operations'));

-- Workers: internal roles read/write (owner/ops write, compliance verify);
-- workers see ONLY their own row; contractors never read this table directly.
create policy workers_internal on workers for all to authenticated
  using (app.has_role('owner') or app.has_role('operations') or app.has_role('compliance') or app.has_role('auditor'))
  with check (app.has_role('owner') or app.has_role('operations'));
create policy workers_self on workers for select to authenticated
  using (id = app.my_worker_id());

create policy worker_status_history_internal on worker_status_history for select to authenticated
  using (app.has_role('owner') or app.has_role('operations') or app.has_role('compliance') or app.has_role('auditor'));
create policy worker_status_history_self on worker_status_history for select to authenticated
  using (worker_id = app.my_worker_id());

-- Compliance-heavy tables: internal roles read; owner+ops write; compliance verify;
-- workers read their own.
create policy rtw_checks_rw on rtw_checks for all to authenticated
  using (app.has_role('owner') or app.has_role('operations') or app.has_role('compliance') or app.has_role('auditor'))
  with check (app.has_role('owner') or app.has_role('operations') or app.has_role('compliance'));
create policy rtw_checks_self on rtw_checks for select to authenticated
  using (worker_id = app.my_worker_id());

create policy qualifications_rw on qualifications for all to authenticated
  using (app.has_role('owner') or app.has_role('operations') or app.has_role('compliance') or app.has_role('auditor'))
  with check (app.has_role('owner') or app.has_role('operations') or app.has_role('compliance'));
create policy qualifications_self on qualifications for select to authenticated
  using (worker_id = app.my_worker_id());

create policy training_rw on training_certificates for all to authenticated
  using (app.has_role('owner') or app.has_role('operations') or app.has_role('compliance') or app.has_role('auditor'))
  with check (app.has_role('owner') or app.has_role('operations') or app.has_role('compliance'));
create policy training_self on training_certificates for select to authenticated
  using (worker_id = app.my_worker_id());

create policy work_history_rw on work_history for all to authenticated
  using (app.has_role('owner') or app.has_role('operations') or app.has_role('compliance') or app.has_role('auditor'))
  with check (app.has_role('owner') or app.has_role('operations'));
create policy work_history_self on work_history for select to authenticated
  using (worker_id = app.my_worker_id());

create policy proof_of_work_rw on proof_of_work for all to authenticated
  using (app.has_role('owner') or app.has_role('operations') or app.has_role('compliance') or app.has_role('auditor'))
  with check (app.has_role('owner') or app.has_role('operations') or app.has_role('compliance'));
create policy proof_of_work_self on proof_of_work for select to authenticated
  using (worker_id = app.my_worker_id());

-- Identity documents: owner + compliance only (plus the worker's own metadata row).
create policy worker_documents_all on worker_documents for all to authenticated
  using (app.has_role('owner') or app.has_role('compliance'))
  with check (app.has_role('owner') or app.has_role('compliance'));
create policy worker_documents_self on worker_documents for select to authenticated
  using (worker_id = app.my_worker_id());

create policy rule_versions_all on rule_versions for all to authenticated
  using (app.has_role('owner') or app.has_role('operations') or app.has_role('compliance') or app.has_role('auditor'))
  with check (app.has_role('owner'));

create policy readiness_evaluations_rw on readiness_evaluations for all to authenticated
  using (app.has_role('owner') or app.has_role('operations') or app.has_role('compliance') or app.has_role('auditor'))
  with check (app.has_role('owner') or app.has_role('compliance'));
create policy readiness_evaluations_self on readiness_evaluations for select to authenticated
  using (worker_id = app.my_worker_id());

create policy readiness_snapshots_rw on readiness_snapshots for all to authenticated
  using (app.has_role('owner') or app.has_role('operations') or app.has_role('compliance') or app.has_role('auditor'))
  with check (app.has_role('owner') or app.has_role('operations'));

create policy expiry_schedule_rw on expiry_schedule for all to authenticated
  using (app.has_role('owner') or app.has_role('operations') or app.has_role('compliance') or app.has_role('auditor'))
  with check (app.has_role('owner') or app.has_role('operations') or app.has_role('compliance'));
create policy expiry_schedule_self on expiry_schedule for select to authenticated
  using (worker_id = app.my_worker_id());

create policy reminder_log_rw on reminder_log for all to authenticated
  using (app.has_role('owner') or app.has_role('operations') or app.has_role('compliance'))
  with check (app.has_role('owner') or app.has_role('operations'));

-- Contractors/projects/sites: internal read-write, contractor sees own.
create policy contractors_all on contractors for all to authenticated
  using (app.has_role('owner') or app.has_role('operations') or app.has_role('compliance') or app.has_role('auditor')
         or (app.has_role('contractor') and id = (select contractor_id from profiles where id = auth.uid())))
  with check (app.has_role('owner') or app.has_role('operations'));

create policy projects_all on projects for all to authenticated
  using (app.has_role('owner') or app.has_role('operations') or app.has_role('compliance') or app.has_role('auditor')
         or (app.has_role('contractor') and contractor_id = (select contractor_id from profiles where id = auth.uid())))
  with check (app.has_role('owner') or app.has_role('operations'));

create policy sites_all on sites for all to authenticated
  using (app.has_role('owner') or app.has_role('operations') or app.has_role('compliance') or app.has_role('auditor')
         or (app.has_role('contractor') and project_id in (
              select p.id from projects p
              where p.contractor_id = (select contractor_id from profiles where id = auth.uid()))))
  with check (app.has_role('owner') or app.has_role('operations'));

create policy site_requirements_all on site_requirements for all to authenticated
  using (app.has_role('owner') or app.has_role('operations') or app.has_role('compliance') or app.has_role('auditor')
         or (app.has_role('contractor') and site_id in (
              select s.id from sites s join projects p on p.id = s.project_id
              where p.contractor_id = (select contractor_id from profiles where id = auth.uid()))))
  with check (app.has_role('owner') or app.has_role('operations'));

-- Requests/matches/offers: internal full; contractor own only.
create policy workforce_requests_all on workforce_requests for all to authenticated
  using (app.has_role('owner') or app.has_role('operations') or app.has_role('compliance') or app.has_role('auditor')
         or (app.has_role('contractor') and contractor_id = (select contractor_id from profiles where id = auth.uid())))
  with check (app.has_role('owner') or app.has_role('operations'));

create policy match_generations_all on match_generations for all to authenticated
  using (app.has_role('owner') or app.has_role('operations') or app.has_role('compliance') or app.has_role('auditor')
         or (app.has_role('contractor') and request_id in (
              select id from workforce_requests
              where contractor_id = (select contractor_id from profiles where id = auth.uid()))))
  with check (app.has_role('owner') or app.has_role('operations'));

create policy matches_all on matches for all to authenticated
  using (app.has_role('owner') or app.has_role('operations') or app.has_role('compliance') or app.has_role('auditor')
         or (app.has_role('contractor') and generation_id in (
              select mg.id from match_generations mg join workforce_requests r on r.id = mg.request_id
              where r.contractor_id = (select contractor_id from profiles where id = auth.uid()))))
  with check (app.has_role('owner') or app.has_role('operations'));

create policy assignment_offers_all on assignment_offers for all to authenticated
  using (app.has_role('owner') or app.has_role('operations') or app.has_role('compliance') or app.has_role('auditor')
         or (app.has_role('contractor') and request_id in (
              select id from workforce_requests
              where contractor_id = (select contractor_id from profiles where id = auth.uid()))))
  with check (app.has_role('owner') or app.has_role('operations'));

-- Assignments: internal full; contractor own; worker own.
create policy assignments_all on assignments for all to authenticated
  using (app.has_role('owner') or app.has_role('operations') or app.has_role('compliance') or app.has_role('auditor')
         or (app.has_role('contractor') and contractor_id = (select contractor_id from profiles where id = auth.uid()))
         or (app.has_role('worker') and worker_id = app.my_worker_id()))
  with check (app.has_role('owner') or app.has_role('operations'));
create policy assignments_self on assignments for select to authenticated
  using (worker_id = app.my_worker_id());

create policy assignment_events_all on assignment_events for select to authenticated
  using (app.has_role('owner') or app.has_role('operations') or app.has_role('compliance') or app.has_role('auditor')
         or (app.has_role('contractor') and assignment_id in (
              select id from assignments
              where contractor_id = (select contractor_id from profiles where id = auth.uid())))
         or (app.has_role('worker') and assignment_id in (
              select id from assignments where worker_id = app.my_worker_id())));

-- Outcomes: internal write; contractor can insert feedback on own assignments.
create policy assignment_outcomes_rw on assignment_outcomes for all to authenticated
  using (app.has_role('owner') or app.has_role('operations') or app.has_role('compliance') or app.has_role('auditor'))
  with check (app.has_role('owner') or app.has_role('operations'));
create policy assignment_outcomes_contractor_write on assignment_outcomes for insert to authenticated
  with check (app.has_role('contractor') and exists (
    select 1 from assignments a
    where a.id = assignment_outcomes.assignment_id
      and a.contractor_id = (select contractor_id from profiles where id = auth.uid())));
create policy assignment_outcomes_contractor_read on assignment_outcomes for select to authenticated
  using (app.has_role('owner') or app.has_role('operations') or app.has_role('compliance') or app.has_role('auditor')
         or (app.has_role('contractor') and exists (
    select 1 from assignments a
    where a.id = assignment_outcomes.assignment_id
      and a.contractor_id = (select contractor_id from profiles where id = auth.uid())))
         or (app.has_role('worker') and exists (
    select 1 from assignments a
    where a.id = assignment_outcomes.assignment_id and a.worker_id = app.my_worker_id())));

-- Statements: internal read/write; contractor and worker see their own.
create policy assignment_statements_rw on assignment_statements for all to authenticated
  using (app.has_role('owner') or app.has_role('operations') or app.has_role('compliance') or app.has_role('auditor')
         or (app.has_role('contractor') and exists (
    select 1 from assignments a
    where a.id = assignment_statements.assignment_id
      and a.contractor_id = (select contractor_id from profiles where id = auth.uid())))
         or (app.has_role('worker') and exists (
    select 1 from assignments a
    where a.id = assignment_statements.assignment_id and a.worker_id = app.my_worker_id())))
  with check (app.has_role('owner') or app.has_role('operations'));

-- Scores: internal read; worker own; contractor aggregate only (app queries aggregate).
create policy score_events_all on score_events for all to authenticated
  using (app.has_role('owner') or app.has_role('operations') or app.has_role('compliance') or app.has_role('auditor'))
  with check (app.has_role('owner') or app.has_role('operations'));
create policy score_events_self on score_events for select to authenticated
  using (worker_id = app.my_worker_id());

create policy performance_scores_all on performance_scores for all to authenticated
  using (app.has_role('owner') or app.has_role('operations') or app.has_role('compliance') or app.has_role('auditor'))
  with check (app.has_role('owner') or app.has_role('operations'));
create policy performance_scores_self on performance_scores for select to authenticated
  using (worker_id = app.my_worker_id());

-- Provenance, audit, overrides: per the approved matrix.
create policy evidence_records_all on evidence_records for all to authenticated
  using (app.has_role('owner') or app.has_role('compliance') or app.has_role('auditor')
         or app.has_role('operations'))
  with check (app.has_role('owner') or app.has_role('compliance') or app.has_role('operations'));

create policy audit_log_read on audit_log for select to authenticated
  using (app.has_role('owner') or app.has_role('compliance') or app.has_role('auditor'));
-- audit_log inserts happen via the audit_row trigger (security definer); no direct policies.

create policy overrides_all on overrides for all to authenticated
  using (app.has_role('owner') or app.has_role('auditor'))
  with check (app.has_role('owner'));

create policy schema_migrations_all on schema_migrations for select to authenticated
  using (app.has_role('owner'));

-- =================================================================
-- Seed: the initial rule versions (register baseline, versions retained)
-- =================================================================

insert into rule_versions (rule_set, version, rules) values
  ('readiness', '0.1', '{"description":"Baseline readiness rules as approved in the demo 0.2C and mapping register v1.0"}'::jsonb),
  ('scoring',   '0.1', '{"weights":{"competence":0.20,"reliability":0.20,"client_feedback":0.15},"description":"Baseline scoring weights from the approved demo"}'::jsonb),
  ('matching',  '0.1', '{"description":"Baseline matching rules: hard filters first, explainable factors kept"}'::jsonb);

insert into schema_migrations (id, name) values (1, '0001_stage0_foundations');
