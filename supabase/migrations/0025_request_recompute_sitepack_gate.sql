-- =====================================================================
-- PRJGENUI Workforce — migration 0025
-- Two follow-up controls from the 25 October 2026 Stage 2 pass:
--
-- 1. REQUEST STATUS RECOMPUTE (the "Filled while no one is booked in"
--    bug): a request was set 'filled' when an assignment was confirmed,
--    but nothing reverted it when that assignment later dropped out
--    (no_show, cancelled, replaced). The transition engine now recomputes
--    the request whenever an assignment leaves the counted set
--    (confirmed / active / completed): if fewer than number_needed
--    assignments remain counted, the request reverts down the normal
--    ladder — offered (a live offer or accepted assignment exists),
--    matched (a match generation exists), open — the same states the
--    app assigns on the way up. 'closed' is never touched. Existing
--    inconsistent rows are recomputed once below.
--
-- 2. ACTIVATION SITE-PACK GATE (AT-13, closing the PARTIAL): activation
--    is refused while the assignment's request has an unresolved
--    replacement incident whose site pack has not been acknowledged
--    (site_pack_ack_at is null). The acknowledgement stays the explicit
--    operator action built in 0021; the gate just makes it a hard
--    prerequisite for putting a worker on site for that engagement.
-- =====================================================================

-- ---------------------------------------------------------------- transition engine

create or replace function app.enforce_assignment_status() returns trigger
language plpgsql as $$
declare
  v_pass boolean;
  v_needed int;
  v_counted int;
  v_new_status request_status;
begin
  if new.status = old.status then return new; end if;

  if not (
    (old.status = 'proposed'  and new.status in ('offered','confirmed','cancelled')) or
    (old.status = 'offered'   and new.status in ('accepted','cancelled')) or
    (old.status = 'accepted'  and new.status in ('confirmed','cancelled')) or
    (old.status = 'confirmed' and new.status in ('active','completed','cancelled','no_show')) or
    (old.status = 'active'    and new.status in ('completed','cancelled','no_show','replaced')) or
    (old.status = 'no_show'   and new.status in ('replaced')) or
    (old.status = 'cancelled' and new.status in ('replaced')) or
    (new.status = 'legacy_recorded')
  ) then
    raise exception 'assignment cannot move from % to %', old.status, new.status;
  end if;

  -- FIRST GATE: no confirmation without a current passing readiness
  -- evaluation for this worker (assignment-level or worker-level). The
  -- latest evaluation controls.
  if new.status = 'confirmed' and old.status in ('proposed','accepted') then
    select coalesce((select re.outcome from readiness_evaluations re
                     where re.worker_id = new.worker_id
                       and (re.assignment_id = new.id or re.assignment_id is null)
                     order by re.created_at desc, re.id desc
                     limit 1), 'blocked') = 'pass' into v_pass;
    if not v_pass then
      raise exception 'hard gate: assignment cannot be confirmed without a current passing readiness evaluation';
    end if;
  end if;

  -- SECOND GATE: no activation without a current passing readiness
  -- evaluation, and the pre-activation snapshot is recorded so what was
  -- true on the day is retained.
  if new.status = 'active' and old.status = 'confirmed' then
    select coalesce((select re.outcome from readiness_evaluations re
                     where re.worker_id = new.worker_id
                       and (re.assignment_id = new.id or re.assignment_id is null)
                     order by re.created_at desc, re.id desc
                     limit 1), 'blocked') = 'pass' into v_pass;
    if not v_pass then
      raise exception 'hard gate: assignment cannot be activated without a current passing readiness evaluation';
    end if;

    -- AT-13: no activation while the request has an unresolved
    -- replacement incident whose site pack is unacknowledged. The
    -- acknowledgement is the explicit operator action from 0021; the
    -- chain can also be resolved instead. Either way the worker does
    -- not go on site behind an unacknowledged site pack.
    if exists (
      select 1 from replacement_incidents ri
      where ri.request_id = new.request_id
        and ri.resolved_at is null
        and ri.site_pack_ack_at is null
    ) then
      raise exception 'hard gate: activation refused while the request has an unresolved replacement incident whose site pack has not been acknowledged';
    end if;

    insert into readiness_snapshots (offer_id, worker_id, snapshot)
    values (new.offer_id, new.worker_id,
            jsonb_build_object('assignment_id', new.id,
                               'assignment_reference', new.public_reference,
                               'gate', 'pre-activation',
                               'evaluated_at',
                                 (select max(created_at) from readiness_evaluations
                                  where worker_id = new.worker_id
                                    and (assignment_id = new.id
                                         or assignment_id is null))));
  end if;

  insert into assignment_events (assignment_id, from_status, to_status, note, actor)
  values (new.id, old.status, new.status, null, app.user_id());

  -- REQUEST STATUS RECOMPUTE: when an assignment leaves the counted set
  -- (no_show, cancelled, replaced — the exception states), a 'filled'
  -- request that no longer has number_needed counted assignments
  -- reverts down the normal ladder. Confirmations and activations never
  -- lower the count, so only the exception states recompute here.
  if new.status in ('no_show','cancelled','replaced')
     and new.request_id is not null then
    -- this row is mid-transition: its old counted state is still what
    -- the table shows, so it is excluded from the count (new.status is
    -- already an exception state and never counted)
    select coalesce(number_needed, 1), (
      select count(*) from assignments a
      where a.request_id = new.request_id
        and a.id <> new.id
        and a.status in ('confirmed','active','completed')
    ) into v_needed, v_counted
    from workforce_requests where id = new.request_id;

    if v_needed is not null and v_counted < v_needed then
      if exists (select 1 from assignments a
                where a.request_id = new.request_id
                  and a.status in ('offered','accepted')) then
        v_new_status := 'offered';
      elsif exists (select 1 from match_generations g
                    where g.request_id = new.request_id) then
        v_new_status := 'matched';
      else
        v_new_status := 'open';
      end if;

      update workforce_requests set status = v_new_status
      where id = new.request_id and status = 'filled';
    end if;
  end if;

  return new;
end $$;

-- ---------------------------------------------------------------- activate RPC wording

-- The refusal reason now states both activation gates.
create or replace function public.activate_assignment(
  p_assignment_id uuid
) returns jsonb
language plpgsql security definer set search_path = public as $$
declare
  v_user uuid := auth.uid();
begin
  if v_user is null then
    return jsonb_build_object('ok', false, 'error', 'not_signed_in');
  end if;
  if not (app.has_role('owner') or app.has_role('operations')) then
    return jsonb_build_object('ok', false, 'error', 'not_permitted');
  end if;

  begin
    update assignments set status = 'active', updated_at = now()
    where id = p_assignment_id and status = 'confirmed';
    if not found then
      return jsonb_build_object('ok', false, 'error', 'not_activatable',
        'reason', 'only a confirmed assignment can be activated');
    end if;
  exception when others then
    return jsonb_build_object('ok', false, 'error', 'hard_gate_refused',
      'reason', 'activation needs a current passing readiness evaluation '
                'for this worker, and no unresolved replacement incident '
                'whose site pack is unacknowledged for the request');
  end;

  return jsonb_build_object('ok', true);
end $$;

grant execute on function public.activate_assignment(uuid) to authenticated;

-- ---------------------------------------------------------------- one-time recompute of inconsistent requests

-- Any request still 'filled' without number_needed counted assignments
-- (the state the live 25 October run exposed: REQ-000115 'filled' with
-- only a no_show assignment) is recomputed down the same ladder.
with recomputed as (
  select r.id,
         case
           when (select count(*) from assignments a
                 where a.request_id = r.id
                   and a.status in ('confirmed','active','completed'))
                >= coalesce(r.number_needed, 1)
             then 'filled'::request_status
           when exists (select 1 from assignments a
                       where a.request_id = r.id
                         and a.status in ('offered','accepted'))
             then 'offered'::request_status
           when exists (select 1 from match_generations g
                       where g.request_id = r.id)
             then 'matched'::request_status
           else 'open'::request_status
         end as new_status
  from workforce_requests r
  where r.status = 'filled'
)
update workforce_requests r
set status = recomputed.new_status
from recomputed
where r.id = recomputed.id and r.status <> recomputed.new_status;

insert into schema_migrations (id, name)
values (25, '0025_request_recompute_sitepack_gate')
on conflict (id) do nothing;
