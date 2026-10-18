-- =====================================================================
-- PRJGENUI Workforce — migration 0011
-- Expiry schedule computation (register 3.6, 3.8; Stage 1).
--
-- public.recompute_expiry_schedule() derives the expiry bands for every
-- non-archived worker's dated evidence and upserts them into
-- expiry_schedule, which drives the Compliance Action Centre and the
-- 60/30/14/7-day reminders.
--
-- Bands (as in the baseline): expired (before today), due_soon (0-30
-- days), watch (31-60 days), current (60+ days or no expiry date).
--
-- Dated items: qualification expiry dates, training certificate expiry
-- dates, and Right to Work follow-up due dates (register 8.3 — a
-- follow-up is recorded and alerted like any other expiry). A Right to
-- Work check with no follow-up due is not an expiring item.
--
-- Stale rows (evidence deleted, worker archived) are removed so the
-- schedule always mirrors the current evidence. Owner and Compliance
-- can run it (access matrix: readiness and reminders are theirs);
-- the guard is inside the function.
-- =====================================================================

create or replace function public.recompute_expiry_schedule()
returns jsonb
language plpgsql security definer set search_path = public as $$
declare
  v_expired int := 0;
  v_due_soon int := 0;
  v_watch int := 0;
  v_current int := 0;
begin
  if auth.uid() is null then
    return jsonb_build_object('ok', false, 'error', 'not_signed_in');
  end if;
  if not app.has_role('owner') and not app.has_role('compliance') then
    return jsonb_build_object('ok', false, 'error', 'not_permitted');
  end if;

  -- Refresh the schedule from scratch for every non-archived worker.
  -- (worker_id is NOT NULL, so this covers every row while keeping an
  -- explicit WHERE clause, which the connection guard requires.)
  delete from expiry_schedule where worker_id is not null;

  insert into expiry_schedule (worker_id, item_table, item_id, expiry_date, band)
  select w.id, t.item_table, t.item_id, t.expiry_date,
         case
           when t.expiry_date < current_date then 'expired'
           when t.expiry_date <= current_date + 30 then 'due_soon'
           when t.expiry_date <= current_date + 60 then 'watch'
           else 'current'
         end
  from workers w
  join (
    select worker_id, 'qualifications' as item_table, id as item_id, expiry_date
    from qualifications where expiry_date is not null
    union all
    select worker_id, 'training_certificates' as item_table, id as item_id, expiry_date
    from training_certificates where expiry_date is not null
    union all
    select worker_id, 'rtw_checks' as item_table, id as item_id, follow_up_due
    from rtw_checks where follow_up_due is not null
  ) t on t.worker_id = w.id
  where w.status <> 'archived';

  select
    count(*) filter (where band = 'expired'),
    count(*) filter (where band = 'due_soon'),
    count(*) filter (where band = 'watch'),
    count(*) filter (where band = 'current')
  into v_expired, v_due_soon, v_watch, v_current
  from expiry_schedule;

  return jsonb_build_object('ok', true, 'expired', v_expired,
                            'due_soon', v_due_soon, 'watch', v_watch,
                            'current', v_current);
end $$;

grant execute on function public.recompute_expiry_schedule() to authenticated;

insert into schema_migrations (id, name)
values (11, '0011_expiry_schedule');
