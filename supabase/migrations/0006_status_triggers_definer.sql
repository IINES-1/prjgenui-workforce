-- =====================================================================
-- PRJGENUI Workforce — migration 0006
-- Status-enforcement triggers become security definer.
--
-- enforce_worker_status and enforce_assignment_status write their history
-- rows (worker_status_history, assignment_events) from inside the
-- trigger. Those history tables deliberately have no insert policy for
-- users, so the trigger running as the calling user was refused by
-- row-level security whenever a real (non-postgres) user changed a
-- status. Making the enforcement functions security definer — exactly
-- like the audit trigger — lets only the trigger write history, while
-- direct inserts by any user remain blocked.
-- =====================================================================

create or replace function app.enforce_worker_status() returns trigger
language plpgsql security definer set search_path = public as $$
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

create or replace function app.enforce_assignment_status() returns trigger
language plpgsql security definer set search_path = public as $$
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

  -- HARD DEPLOYMENT GATE: no confirmation without a current passing
  -- readiness evaluation for this worker — either for this assignment,
  -- or worker-level (assignment_id null), whichever is the latest.
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

insert into schema_migrations (id, name)
values (6, '0006_status_triggers_definer');
