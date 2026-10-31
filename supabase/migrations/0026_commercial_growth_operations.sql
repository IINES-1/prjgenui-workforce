-- =====================================================================
-- PRJGENUI Workforce — migration 0026
-- Commercial and growth layer (one sweep, five parts):
--
--   1. Structured hourly rates on assignments (pay, overtime, weekend,
--      charge) alongside the existing free-text rate notes, and
--      default rates / location / travel range on workers.
--   2. Timesheets: one row per assignment per week, hours split into
--      basic / overtime / weekend, generated from attendance, approved
--      by the team. Pay and charge totals are recorded at approval
--      time so later rate changes never rewrite history.
--   3. Invoices and invoice lines for contractors, with payment status.
--   4. Contractor pipeline: stage, credit limit and payment terms on
--      contractors, plus a communication log.
--   5. Worker availability dates (the worker can mark their own; the
--      team can too), feeding capacity views.
--
-- The platform does not process payments; invoices record what is owed
-- and what has been paid. Exports (payroll CSV) are produced by the
-- app from these tables.
--
-- Access follows the existing matrix: commercial records are Owner
-- (timesheets also Operations), contractors read their own invoices
-- and timesheets, workers read their own timesheets and mark their own
-- unavailable dates. Everything is audited like the rest of the
-- platform.
-- =====================================================================

-- ---------------------------------------------------------------- 1. rates

alter table assignments
  add column pay_rate              numeric check (pay_rate >= 0),
  add column overtime_pay_rate     numeric check (overtime_pay_rate >= 0),
  add column weekend_pay_rate      numeric check (weekend_pay_rate >= 0),
  add column charge_rate           numeric check (charge_rate >= 0),
  add column overtime_charge_rate  numeric check (overtime_charge_rate >= 0),
  add column weekend_charge_rate   numeric check (weekend_charge_rate >= 0);

alter table workers
  add column default_pay_rate      numeric check (default_pay_rate >= 0),
  add column default_overtime_rate numeric check (default_overtime_rate >= 0),
  add column default_weekend_rate  numeric check (default_weekend_rate >= 0),
  add column base_location         text,
  add column travel_range_km       int check (travel_range_km >= 0);

-- ---------------------------------------------------- 2. timesheets

create type timesheet_status as enum ('draft','submitted','approved','rejected');

create table timesheets (
  id              uuid primary key default gen_random_uuid(),
  assignment_id   uuid not null references assignments(id) on delete cascade,
  week_start      date not null,              -- Monday of the week
  basic_hours     numeric not null default 0 check (basic_hours >= 0),
  overtime_hours  numeric not null default 0 check (overtime_hours >= 0),
  weekend_hours   numeric not null default 0 check (weekend_hours >= 0),
  pay_total       numeric not null default 0,
  charge_total    numeric not null default 0,
  status          timesheet_status not null default 'draft',
  from_attendance boolean not null default true,
  approved_by     uuid references profiles(id),
  approved_at     timestamptz,
  notes           text,
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now(),
  unique (assignment_id, week_start)
);

alter table timesheets enable row level security;

-- The team (Owner, Operations) manages timesheets; Compliance and
-- Auditor read them.
create policy timesheets_team_all on timesheets for all to authenticated
  using (app.has_role('owner') or app.has_role('operations')
         or app.has_role('compliance') or app.has_role('auditor'))
  with check (app.has_role('owner') or app.has_role('operations'));

-- Contractors read the timesheets recorded on their own assignments.
create policy timesheets_contractor_read on timesheets
  for select to authenticated
  using (exists (
    select 1 from assignments a
    where a.id = timesheets.assignment_id
      and a.contractor_id = (select contractor_id from profiles
                             where id = auth.uid())));

-- Workers read their own timesheets.
create policy timesheets_worker_read on timesheets
  for select to authenticated
  using (exists (
    select 1 from assignments a
    where a.id = timesheets.assignment_id
      and a.worker_id = app.my_worker_id()));

create trigger set_updated_at_timesheets before update on timesheets
  for each row execute function app.set_updated_at();
create trigger audit_timesheets after insert or update or delete on timesheets
  for each row execute function app.audit_row();

-- ---------------------------------------------------- 3. invoices

create type invoice_status as enum ('draft','sent','paid','void');

create table invoices (
  id            uuid primary key default gen_random_uuid(),
  contractor_id uuid not null references contractors(id) on delete cascade,
  invoice_no    text not null unique,        -- INV-000001, allocated by the app
  period_start  date,
  period_end    date,
  status        invoice_status not null default 'draft',
  subtotal      numeric not null default 0,
  vat_rate      numeric not null default 20,
  vat_total     numeric not null default 0,
  total         numeric not null default 0,
  due_date      date,
  sent_at       timestamptz,
  paid_at       timestamptz,
  notes         text,
  created_by    uuid references profiles(id),
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);

create table invoice_lines (
  id            uuid primary key default gen_random_uuid(),
  invoice_id    uuid not null references invoices(id) on delete cascade,
  description   text not null,
  quantity      numeric not null default 1,
  unit          text not null default 'hours',
  unit_price    numeric not null default 0,
  amount        numeric not null default 0,
  assignment_id uuid references assignments(id) on delete set null,
  timesheet_id  uuid references timesheets(id) on delete set null,
  created_at    timestamptz not null default now()
);

alter table invoices      enable row level security;
alter table invoice_lines enable row level security;

-- Invoices are Owner territory (commercial group, access matrix);
-- Operations reads them so the team can answer "what do we owe / what
-- are we owed" questions.
create policy invoices_owner_all on invoices for all to authenticated
  using (app.has_role('owner'))
  with check (app.has_role('owner'));
create policy invoices_operations_read on invoices for select to authenticated
  using (app.has_role('operations'));

create policy invoice_lines_owner_all on invoice_lines for all to authenticated
  using (app.has_role('owner'))
  with check (app.has_role('owner'));
create policy invoice_lines_operations_read on invoice_lines for select to authenticated
  using (app.has_role('operations'));

-- Contractors read their own invoices with their lines.
create policy invoices_contractor_read on invoices
  for select to authenticated
  using (contractor_id = (select contractor_id from profiles
                          where id = auth.uid()));
create policy invoice_lines_contractor_read on invoice_lines
  for select to authenticated
  using (exists (
    select 1 from invoices i
    where i.id = invoice_lines.invoice_id
      and i.contractor_id = (select contractor_id from profiles
                             where id = auth.uid())));

create trigger set_updated_at_invoices before update on invoices
  for each row execute function app.set_updated_at();
create trigger audit_invoices after insert or update or delete on invoices
  for each row execute function app.audit_row();
create trigger audit_invoice_lines after insert or delete on invoice_lines
  for each row execute function app.audit_row();

-- ------------------------------------------- 4. contractor pipeline

alter table contractors
  add column pipeline_status    text not null default 'enquiry'
    check (pipeline_status in
           ('enquiry','in_review','approved','active','paused','declined')),
  add column credit_limit       numeric check (credit_limit >= 0),
  add column payment_terms_days int not null default 14
    check (payment_terms_days >= 0);

create table contractor_comms (
  id            uuid primary key default gen_random_uuid(),
  contractor_id uuid not null references contractors(id) on delete cascade,
  channel       text not null default 'email'
                check (channel in ('email','phone','meeting','whatsapp','other')),
  note          text not null,
  recorded_by   uuid references profiles(id),
  created_at    timestamptz not null default now()
);

alter table contractor_comms enable row level security;

create policy contractor_comms_team_all on contractor_comms
  for all to authenticated
  using (app.has_role('owner') or app.has_role('operations')
         or app.has_role('compliance') or app.has_role('auditor'))
  with check (app.has_role('owner') or app.has_role('operations'));

create policy contractor_comms_contractor_read on contractor_comms
  for select to authenticated
  using (contractor_id = (select contractor_id from profiles
                          where id = auth.uid()));

create trigger audit_contractor_comms
  after insert or delete on contractor_comms
  for each row execute function app.audit_row();

-- ------------------------------------------- 5. worker availability

create table worker_unavailability (
  id          uuid primary key default gen_random_uuid(),
  worker_id   uuid not null references workers(id) on delete cascade,
  date        date not null,
  note        text,
  created_by  uuid references profiles(id),
  created_at  timestamptz not null default now(),
  unique (worker_id, date)
);

alter table worker_unavailability enable row level security;

-- The team manages availability; workers mark their own dates.
create policy worker_unavailability_team_all on worker_unavailability
  for all to authenticated
  using (app.has_role('owner') or app.has_role('operations')
         or app.has_role('compliance') or app.has_role('auditor'))
  with check (app.has_role('owner') or app.has_role('operations'));

create policy worker_unavailability_worker_insert on worker_unavailability
  for insert to authenticated
  with check (worker_id = app.my_worker_id());

create policy worker_unavailability_worker_delete on worker_unavailability
  for delete to authenticated
  using (worker_id = app.my_worker_id());

create policy worker_unavailability_worker_read on worker_unavailability
  for select to authenticated
  using (worker_id = app.my_worker_id());

create trigger audit_worker_unavailability
  after insert or delete on worker_unavailability
  for each row execute function app.audit_row();

-- ---------------------------------------------------------------- bookkeeping

insert into schema_migrations (id, name)
values (26, '0026_commercial_growth_operations');
