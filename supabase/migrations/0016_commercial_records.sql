-- =====================================================================
-- PRJGENUI Workforce — migration 0016
-- Commercial records (register 11.1-11.3, NEW Stage 1).
--
-- Per the approved schema design section I:
--   price_catalog        standard and customer-specific prices, discounts
--                        with recorded reasons, waivers, minimums,
--                        allowances, VAT treatment, billing frequency,
--                        start/review dates, approval status and Order
--                        Form references — configurable, nothing
--                        hard-coded
--   service_subscriptions per-contractor switches: managed onboarding,
--                        compliance monitoring, training-request
--                        coordination
--   external_costs      third-party costs (training providers, identity
--                        checks, verification), recorded separately and
--                        approved before they are incurred
--
-- billing_records (line items per service period) belong to the billing
-- workflows, which wait for the employment-law opinion (Stage 2, LEGAL)
-- — the table is deliberately not created yet.
--
-- Access: prices and external costs are Owner only (access matrix,
-- commercial group); contractors can read their own service switches.
-- All three tables are audited like the rest of the platform.
-- =====================================================================

create table price_catalog (
  id                uuid primary key default gen_random_uuid(),
  scope             text not null check (scope in ('standard','customer')),
  contractor_id     uuid references contractors(id) on delete cascade,
  service           text not null,           -- e.g. 'compliance_monitoring'
  price             numeric not null,
  unit              text not null,            -- e.g. 'per worker per month'
  vat_rate          numeric,
  billing_frequency text,                    -- e.g. 'monthly','quarterly'
  minimum_monthly   numeric,
  allowances        jsonb not null default '[]',
  discount_pct      numeric,
  discount_reason   text,
  waived            boolean not null default false,
  waived_reason     text,
  start_date        date not null default current_date,
  review_date       date,
  approval_status   text not null default 'draft'
                    check (approval_status in ('draft','approved')),
  order_form_ref    text,
  notes             text,
  created_at        timestamptz not null default now(),
  updated_at        timestamptz not null default now(),
  -- A discount or a waiver always carries a recorded reason.
  check (discount_pct is null or discount_reason is not null),
  check (not waived or waived_reason is not null)
);

create table service_subscriptions (
  id                      uuid primary key default gen_random_uuid(),
  contractor_id           uuid not null references contractors(id) on delete cascade,
  managed_onboarding      boolean not null default false,
  compliance_monitoring  boolean not null default false,
  training_coordination   boolean not null default false,
  effective_from         date not null default current_date,
  notes                   text,
  created_at              timestamptz not null default now(),
  updated_at              timestamptz not null default now()
);

create table external_costs (
  id            uuid primary key default gen_random_uuid(),
  description   text not null,
  category      text not null,                -- 'training_provider','identity_check','verification','other'
  amount        numeric not null,
  worker_id     uuid references workers(id) on delete set null,
  contractor_id uuid references contractors(id) on delete set null,
  status        text not null default 'proposed'
                check (status in ('proposed','approved','incurred')),
  approved_by   uuid references profiles(id),
  approved_at   timestamptz,
  agreed_by     text,                        -- who agreed the cost, outside the platform
  incurred_on   date,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);

alter table price_catalog        enable row level security;
alter table service_subscriptions enable row level security;
alter table external_costs      enable row level security;

-- Prices and external costs: Owner only (commercial group, access matrix).
create policy price_catalog_all on price_catalog for all to authenticated
  using (app.has_role('owner'))
  with check (app.has_role('owner'));
create policy external_costs_all on external_costs for all to authenticated
  using (app.has_role('owner'))
  with check (app.has_role('owner'));

-- Service switches: Owner manages; the contractor sees their own.
create policy service_subscriptions_all on service_subscriptions
  for all to authenticated
  using (app.has_role('owner')
         or (app.has_role('contractor')
             and contractor_id = (select contractor_id from profiles where id = auth.uid())))
  with check (app.has_role('owner'));

create trigger set_updated_at_price_catalog before update on price_catalog
  for each row execute function app.set_updated_at();
create trigger set_updated_at_service_subscriptions before update on service_subscriptions
  for each row execute function app.set_updated_at();
create trigger set_updated_at_external_costs before update on external_costs
  for each row execute function app.set_updated_at();

create trigger audit_price_catalog after insert or update or delete on price_catalog
  for each row execute function app.audit_row();
create trigger audit_service_subscriptions after insert or update or delete on service_subscriptions
  for each row execute function app.audit_row();
create trigger audit_external_costs after insert or update or delete on external_costs
  for each row execute function app.audit_row();

insert into schema_migrations (id, name)
values (16, '0016_commercial_records');
