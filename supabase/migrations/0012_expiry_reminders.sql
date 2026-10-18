-- =====================================================================
-- PRJGENUI Workforce — migration 0012
-- Expiry reminders at 60/30/14/7 days (register 3.8, NEW Stage 1).
--
-- public.run_expiry_reminders() reads the expiry schedule (migration 0011)
-- and logs the reminder due for each item, once per milestone:
--   60d when 31-60 days remain, 30d when 15-30 remain,
--   14d when 8-14 remain, 7d at 7 or fewer (including overdue).
-- Reminders go to the worker (their passport shows them) and to the team
-- (the action centre lists them). Right to Work follow-up dates are
-- reminded like any other expiry (register 8.3).
--
-- The channel is 'in_app' until email sending is switched on (Zoho SMTP
-- agreed with Ian; the reminder log is the record of what was sent).
-- Runs are idempotent: each worker + item + milestone is logged once.
--
-- Only Owner and Compliance can run it (access matrix: readiness and
-- reminders). Workers can now read their own reminders (new policy).
-- =====================================================================

create or replace function public.run_expiry_reminders()
returns jsonb
language plpgsql security definer set search_path = public as $$
declare
  v_by text;
  v_days int;
  v_milestone text;
  v_count int := 0;
  r record;
  v_by_milestone jsonb := '{}'::jsonb;
begin
  if auth.uid() is null then
    return jsonb_build_object('ok', false, 'error', 'not_signed_in');
  end if;
  if not app.has_role('owner') and not app.has_role('compliance') then
    return jsonb_build_object('ok', false, 'error', 'not_permitted');
  end if;

  select email into v_by from auth.users where id = auth.uid();
  v_by := coalesce(v_by, 'system');

  for r in
    select s.worker_id, s.item_table, s.item_id, s.expiry_date,
           (s.expiry_date - current_date) as days_left
    from expiry_schedule s
    join workers w on w.id = s.worker_id
    where w.status <> 'archived'
  loop
    v_days := r.days_left;
    if v_days > 60 then
      continue; -- not yet within any reminder window
    elsif v_days > 30 then v_milestone := '60d';
    elsif v_days > 14 then v_milestone := '30d';
    elsif v_days > 7 then v_milestone := '14d';
    else v_milestone := '7d';
    end if;

    if not exists (
      select 1 from reminder_log l
      where l.worker_id = r.worker_id
        and l.item_table = r.item_table
        and l.item_id = r.item_id
        and l.milestone = v_milestone
    ) then
      insert into reminder_log (worker_id, item_table, item_id, milestone,
                                 channel, sent_by)
      values (r.worker_id, r.item_table, r.item_id, v_milestone,
              'in_app', v_by);
      v_count := v_count + 1;
      v_by_milestone := jsonb_set(v_by_milestone, array[v_milestone],
        to_jsonb(coalesce((v_by_milestone ->> v_milestone)::int, 0) + 1));
    end if;
  end loop;

  return jsonb_build_object('ok', true, 'reminders', v_count,
                            'by_milestone', v_by_milestone);
end $$;

grant execute on function public.run_expiry_reminders() to authenticated;

-- Workers can read their own reminders (register 3.8: reminders go to
-- the worker and to us).
create policy reminder_log_self on reminder_log for select to authenticated
  using (worker_id = app.my_worker_id());

insert into schema_migrations (id, name)
values (12, '0012_expiry_reminders');
