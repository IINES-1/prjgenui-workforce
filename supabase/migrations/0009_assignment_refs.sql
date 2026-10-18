-- =====================================================================
-- PRJGENUI Workforce — migration 0009
-- Assignment public references.
--
-- Assignments get a reference in the ASG-000001 style at insert time,
-- exactly like worker passport numbers (migration 0005) and workforce
-- request references (migration 0008).
-- =====================================================================

create sequence if not exists assignment_ref_seq start 1;

create or replace function app.assign_assignment_ref() returns trigger
language plpgsql as $$
begin
  if new.public_reference is null or new.public_reference = '' then
    new.public_reference := 'ASG-' ||
      lpad(nextval('assignment_ref_seq')::text, 6, '0');
  end if;
  return new;
end $$;

create trigger assign_assignment_ref before insert on assignments
  for each row execute function app.assign_assignment_ref();

insert into schema_migrations (id, name)
values (9, '0009_assignment_refs');
