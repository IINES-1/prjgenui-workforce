-- =====================================================================
-- PRJGENUI Workforce — migration 0005
-- Worker passport numbers, allocated automatically.
--
-- The approved design keeps the demo's PW-UK-000001 format. A sequence
-- allocates the next number on insert whenever one is not supplied, and
-- existing rows without a number are backfilled.
-- =====================================================================

create sequence if not exists worker_passport_seq start 1;

create or replace function app.assign_passport_no() returns trigger
language plpgsql as $$
begin
  if new.passport_no is null or new.passport_no = '' then
    new.passport_no := 'PW-UK-' ||
      lpad(nextval('worker_passport_seq')::text, 6, '0');
  end if;
  return new;
end $$;

create trigger assign_passport_no before insert on workers
  for each row execute function app.assign_passport_no();

-- Backfill any existing rows created without a number.
update workers
set passport_no = 'PW-UK-' || lpad(nextval('worker_passport_seq')::text, 6, '0')
where passport_no is null or passport_no = '';

insert into schema_migrations (id, name)
values (5, '0005_worker_passport_numbers');
