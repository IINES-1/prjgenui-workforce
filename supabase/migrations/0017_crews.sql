-- =====================================================================
-- PRJGENUI Workforce — migration 0017
-- Crews (register 2.5 and 5.4, RETAINED Stage 0).
--
-- Copies the approved dashboard's crew model exactly:
--   crews              name, specialism, supervisor (a worker), notes
--   crew_members       which workers make up the crew
--   crew_deployments  the crew's deployment history: date, client,
--                      project and whether they worked well together
--
-- A crew only exists where people have genuinely worked together:
-- the confidence status (new crew / limited evidence / proven crew)
-- and the "worked well" percentage are derived from the recorded
-- deployments, exactly as in the dashboard.
--
-- assignments can record the crew they were made for (crew_id),
-- carried from the dashboard model. No assignment logic depends on
-- it yet; crew matching as a unit follows with the matching engine.
--
-- Access: Owner and Operations manage crews; Compliance and Auditor
-- read them (workforce group, access matrix). Workers and contractors
-- do not see crews. All three tables are audited like the platform.
-- =====================================================================

create table crews (
  id            uuid primary key default gen_random_uuid(),
  name          text not null,
  specialism    text,
  supervisor_id uuid references workers(id) on delete set null,
  notes         text,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);

create table crew_members (
  crew_id    uuid not null references crews(id) on delete cascade,
  worker_id  uuid not null references workers(id) on delete cascade,
  added_at   timestamptz not null default now(),
  primary key (crew_id, worker_id)
);

create table crew_deployments (
  id          uuid primary key default gen_random_uuid(),
  crew_id     uuid not null references crews(id) on delete cascade,
  deploy_date date,
  client      text,
  project     text,
  worked_well boolean,
  recorded_at timestamptz not null default now()
);

alter table assignments add column crew_id uuid references crews(id) on delete set null;

alter table crews           enable row level security;
alter table crew_members    enable row level security;
alter table crew_deployments enable row level security;

-- Owner and Operations manage crews.
create policy crews_write on crews for all to authenticated
  using (app.has_role('owner') or app.has_role('operations'))
  with check (app.has_role('owner') or app.has_role('operations'));
create policy crew_members_write on crew_members for all to authenticated
  using (app.has_role('owner') or app.has_role('operations'))
  with check (app.has_role('owner') or app.has_role('operations'));
create policy crew_deployments_write on crew_deployments for all to authenticated
  using (app.has_role('owner') or app.has_role('operations'))
  with check (app.has_role('owner') or app.has_role('operations'));

-- Compliance and Auditor read the crew register.
create policy crews_read on crews for select to authenticated
  using (app.has_role('compliance') or app.has_role('auditor'));
create policy crew_members_read on crew_members for select to authenticated
  using (app.has_role('compliance') or app.has_role('auditor'));
create policy crew_deployments_read on crew_deployments for select to authenticated
  using (app.has_role('compliance') or app.has_role('auditor'));

create trigger set_updated_at_crews before update on crews
  for each row execute function app.set_updated_at();

create trigger audit_crews after insert or update or delete on crews
  for each row execute function app.audit_row();
create trigger audit_crew_members after insert or update or delete on crew_members
  for each row execute function app.audit_row();
create trigger audit_crew_deployments after insert or update or delete on crew_deployments
  for each row execute function app.audit_row();

insert into schema_migrations (id, name)
values (17, '0017_crews');
