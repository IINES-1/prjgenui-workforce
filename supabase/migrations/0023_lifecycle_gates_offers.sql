-- =====================================================================
-- PRJGENUI Workforce — migration 0023
-- The full assignment lifecycle with the two readiness gates, and the
-- offer flow (register 6.1, FR-08/09/10, AT-08; the approved 0.3-E
-- lifecycle).
--
-- Transitions (proposed by the operator, enforced server-side):
--   proposed  -> offered, confirmed, cancelled
--   offered   -> accepted, cancelled
--   accepted  -> confirmed, cancelled
--   confirmed -> active, completed, cancelled, no_show
--   active    -> completed, cancelled, no_show, replaced
--   no_show   -> replaced
--   cancelled -> replaced          (a replacement chain's original)
--   legacy_recorded is reachable from anywhere, as before (migrated
--   history only).
--
-- FIRST GATE (unchanged in spirit): no confirmation without a current
-- passing readiness evaluation — now applying to accepted -> confirmed
-- as well as proposed -> confirmed.
--
-- SECOND GATE (new): no activation without a current passing readiness
-- evaluation, and a pre-activation readiness snapshot is recorded at
-- activation (readiness_snapshots), so what was true on the day is
-- retained historically.
--
-- OFFER FLOW (the only route the app uses):
--   create_assignment_from_match  an approved match (per the 0020
--                                  approved-match rule) becomes an
--                                  offer + assignment at 'offered' in
--                                  one recorded operator action
--   record_offer_response         the worker's answer (accepted /
--                                  declined), recorded by the operator
--                                  like the approved dashboard's
--                                  recordOfferResponse
--   confirm_assignment            gate 1 -> 'confirmed'
--   activate_assignment           gate 2 + snapshot -> 'active'
--   complete stays the outcome path (assignment_outcomes + update)
--
-- record_replacement_incident from 0021 is updated: a no_show incident
-- now moves a confirmed/active original to 'no_show' through the normal
-- engine, and link_replacement_assignment marks the original
-- 'replaced' where the engine allows it (the chain's outcome).
-- =====================================================================

-- ---------------------------------------------------------------- transition engine

create or replace function app.enforce_assignment_status() returns trigger
language plpgsql as $$
declare
  v_pass boolean;
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
  return new;
end $$;

-- ---------------------------------------------------------------- offer flow RPCs

-- An approved match becomes an offer and its assignment in one recorded
-- operator action. The offer insert itself is guarded by the 0020
-- approved-match backstop; this RPC refuses early with a clear reason
-- instead of relying on the silent backstop.
create or replace function public.create_assignment_from_match(
  p_request_id uuid,
  p_worker_id  uuid
) returns jsonb
language plpgsql security definer set search_path = public as $$
declare
  v_user uuid := auth.uid();
  v_worker workers%rowtype;
  v_request workforce_requests%rowtype;
  v_offer assignment_offers%rowtype;
  v_assignment_id uuid;
  v_ref text;
begin
  if v_user is null then
    return jsonb_build_object('ok', false, 'error', 'not_signed_in');
  end if;
  if not (app.has_role('owner') or app.has_role('operations')) then
    return jsonb_build_object('ok', false, 'error', 'not_permitted',
      'reason', 'offers are made by the platform team');
  end if;

  select * into v_worker from workers where id = p_worker_id;
  if not found then
    return jsonb_build_object('ok', false, 'error', 'worker_not_found');
  end if;
  select * into v_request from workforce_requests where id = p_request_id;
  if not found then
    return jsonb_build_object('ok', false, 'error', 'request_not_found');
  end if;
  if v_request.status in ('filled','closed') then
    return jsonb_build_object('ok', false, 'error', 'request_not_open',
      'reason', 'the request is ' || v_request.status::text);
  end if;

  if not exists (
    select 1 from matches m
    join match_generations g on g.id = m.generation_id
    where g.request_id = p_request_id
      and m.worker_id = p_worker_id
      and m.decision = 'approved'
  ) then
    return jsonb_build_object('ok', false, 'error', 'no_approved_match',
      'reason', 'an offer can only be made from an approved match');
  end if;

  -- one live offer per worker per request
  if exists (
    select 1 from assignment_offers o
    join assignments a on a.offer_id = o.id
    where o.request_id = p_request_id and o.worker_id = p_worker_id
      and a.status in ('offered','accepted','confirmed','active')
  ) then
    return jsonb_build_object('ok', false, 'error', 'already_offered',
      'reason', 'this worker already has a live offer or assignment '
                'for this request');
  end if;

  insert into assignment_offers (request_id, worker_id, offered_by, expires_at)
  values (p_request_id, p_worker_id, v_user, now() + interval '7 days')
  returning * into v_offer;

  insert into assignments (public_reference, request_id, offer_id, worker_id,
                            contractor_id, project_id, site_id, trade,
                            role, start_date, end_date, status)
  values (null, p_request_id, v_offer.id, p_worker_id,
          v_request.contractor_id, v_request.project_id, v_request.site_id,
          v_request.trade, 'worker', v_request.start_date, null, 'offered')
  returning id into v_assignment_id;

  -- request status: offered once an offer exists
  update workforce_requests set status = 'offered'
  where id = p_request_id and status in ('open','matched');

  return jsonb_build_object('ok', true, 'assignment_id', v_assignment_id,
                           'offer_id', v_offer.id);
end $$;

-- The worker's answer to the offer, recorded by the operator (the
-- approved dashboard's recordOfferResponse). Declining cancels the
-- assignment through the normal engine.
create or replace function public.record_offer_response(
  p_assignment_id uuid,
  p_response     text
) returns jsonb
language plpgsql security definer set search_path = public as $$
declare
  v_user uuid := auth.uid();
  v_assignment assignments%rowtype;
begin
  if v_user is null then
    return jsonb_build_object('ok', false, 'error', 'not_signed_in');
  end if;
  if not (app.has_role('owner') or app.has_role('operations')) then
    return jsonb_build_object('ok', false, 'error', 'not_permitted');
  end if;
  if p_response not in ('accepted','declined') then
    return jsonb_build_object('ok', false, 'error', 'invalid_response');
  end if;

  select * into v_assignment from assignments where id = p_assignment_id;
  if not found then
    return jsonb_build_object('ok', false, 'error', 'assignment_not_found');
  end if;
  if v_assignment.status <> 'offered' then
    return jsonb_build_object('ok', false, 'error', 'not_offered',
      'reason', 'the assignment is at ' || v_assignment.status::text);
  end if;

  if p_response = 'accepted' then
    update assignment_offers set accepted_at = now()
    where id = v_assignment.offer_id;
    update assignments set status = 'accepted', updated_at = now()
    where id = p_assignment_id;
  else
    update assignments set status = 'cancelled', updated_at = now()
    where id = p_assignment_id;
  end if;

  return jsonb_build_object('ok', true);
end $$;

-- Confirm (gate 1). The engine enforces the readiness gate; this RPC
-- converts the engine's refusal into an explicit ok:false.
create or replace function public.confirm_assignment(
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
    update assignments set status = 'confirmed', updated_at = now()
    where id = p_assignment_id and status in ('proposed','accepted');
    if not found then
      return jsonb_build_object('ok', false, 'error', 'not_confirmable',
        'reason', 'only a proposed or accepted assignment can be confirmed');
    end if;
  exception when others then
    return jsonb_build_object('ok', false, 'error', 'hard_gate_refused',
      'reason', 'confirmation needs a current passing readiness '
                'evaluation for this worker');
  end;

  return jsonb_build_object('ok', true);
end $$;

-- Activate (gate 2). The engine enforces the readiness gate and records
-- the pre-activation snapshot; this RPC converts refusals explicitly.
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
      'reason', 'activation needs a current passing readiness '
                'evaluation for this worker');
  end;

  return jsonb_build_object('ok', true);
end $$;

grant execute on function public.create_assignment_from_match(uuid, uuid) to authenticated;
grant execute on function public.record_offer_response(uuid, text) to authenticated;
grant execute on function public.confirm_assignment(uuid) to authenticated;
grant execute on function public.activate_assignment(uuid) to authenticated;

-- ---------------------------------------------------------------- replacement incident update (0021)

-- A no_show incident now moves a confirmed/active original to 'no_show'
-- through the normal engine; any other status records the fact without
-- forcing a change (the same rule as before, extended to the new
-- lifecycle).
create or replace function public.record_replacement_incident(
  p_assignment_id uuid,
  p_incident_type replacement_incident_type,
  p_notes         text default null
) returns jsonb
language plpgsql security definer set search_path = public as $$
declare
  v_user uuid := auth.uid();
  v_assignment assignments%rowtype;
  v_incident_id uuid;
begin
  if v_user is null then
    return jsonb_build_object('ok', false, 'error', 'not_signed_in');
  end if;
  if not (app.has_role('owner') or app.has_role('operations')) then
    return jsonb_build_object('ok', false, 'error', 'not_permitted',
      'reason', 'replacement incidents are recorded by the platform team');
  end if;

  select * into v_assignment from assignments where id = p_assignment_id;
  if not found then
    return jsonb_build_object('ok', false, 'error', 'assignment_not_found');
  end if;

  if exists (select 1 from replacement_incidents
             where assignment_id = p_assignment_id and resolved_at is null) then
    return jsonb_build_object('ok', false, 'error', 'incident_already_open',
      'reason', 'an unresolved incident already exists for this '
                'assignment — resolve the chain or record a new incident '
                'afterwards');
  end if;

  -- status moves only where the lifecycle maps the incident to an
  -- exception state, and only through the engine (never bypassed)
  if p_incident_type = 'cancellation'
     and v_assignment.status <> 'cancelled' then
    begin
      update assignments set status = 'cancelled'
      where id = p_assignment_id;
    exception when others then
      return jsonb_build_object('ok', false, 'error', 'status_transition_refused',
        'reason', 'the assignment cannot move to cancelled from its '
                  'current status (the status engine refused it)');
    end;
  elsif p_incident_type = 'no_show'
     and v_assignment.status in ('confirmed','active') then
    begin
      update assignments set status = 'no_show'
      where id = p_assignment_id;
    exception when others then
      return jsonb_build_object('ok', false, 'error', 'status_transition_refused',
        'reason', 'the assignment cannot move to no_show from its '
                  'current status (the status engine refused it)');
    end;
  end if;

  insert into replacement_incidents
    (assignment_id, request_id, incident_type, recorded_by, notes)
  values (p_assignment_id, v_assignment.request_id, p_incident_type,
          v_user, p_notes)
  returning id into v_incident_id;

  return jsonb_build_object('ok', true, 'incident_id', v_incident_id);
end $$;

-- Linking the replacement now also closes the original's chain outcome:
-- where the engine allows it, the original becomes 'replaced'.
create or replace function public.link_replacement_assignment(
  p_incident_id            uuid,
  p_replacement_assignment_id uuid
) returns jsonb
language plpgsql security definer set search_path = public as $$
declare
  v_user uuid := auth.uid();
  v_incident replacement_incidents%rowtype;
  v_replacement assignments%rowtype;
  v_generation uuid;
begin
  if v_user is null then
    return jsonb_build_object('ok', false, 'error', 'not_signed_in');
  end if;
  if not (app.has_role('owner') or app.has_role('operations')) then
    return jsonb_build_object('ok', false, 'error', 'not_permitted');
  end if;

  select * into v_incident from replacement_incidents where id = p_incident_id;
  if not found then
    return jsonb_build_object('ok', false, 'error', 'incident_not_found');
  end if;
  if v_incident.resolved_at is not null then
    return jsonb_build_object('ok', false, 'error', 'incident_resolved',
      'reason', 'the chain is closed; a further replacement is a new incident');
  end if;
  if v_incident.replacement_assignment_id is not null then
    return jsonb_build_object('ok', false, 'error', 'replacement_already_linked',
      'reason', 'this incident already links its replacement assignment');
  end if;

  select * into v_replacement from assignments
  where id = p_replacement_assignment_id;
  if not found then
    return jsonb_build_object('ok', false, 'error', 'assignment_not_found');
  end if;
  if v_replacement.id = v_incident.assignment_id then
    return jsonb_build_object('ok', false, 'error', 'same_assignment',
      'reason', 'a replacement cannot be the original assignment');
  end if;
  if v_replacement.request_id is distinct from v_incident.request_id then
    return jsonb_build_object('ok', false, 'error', 'different_request',
      'reason', 'the replacement must be for the same request');
  end if;
  if v_replacement.offer_id is null then
    return jsonb_build_object('ok', false, 'error', 'not_through_offer_flow',
      'reason', 'the replacement assignment must be created through the '
                'normal offer flow (same controls as any assignment)');
  end if;

  select m.generation_id into v_generation
  from matches m
  join match_generations g on g.id = m.generation_id
  where g.request_id = v_incident.request_id
    and m.worker_id = v_replacement.worker_id
    and m.decision = 'approved'
  order by m.created_at desc
  limit 1;

  update replacement_incidents
  set replacement_assignment_id = v_replacement.id,
      replacement_match_generation_id = coalesce(v_generation,
        v_incident.replacement_match_generation_id),
      updated_at = now()
  where id = p_incident_id;

  -- the original's chain outcome: 'replaced' where the engine allows it
  update assignments set status = 'replaced', updated_at = now()
  where id = v_incident.assignment_id
    and status in ('no_show','cancelled');

  return jsonb_build_object('ok', true, 'match_generation_id', v_generation);
end $$;

insert into schema_migrations (id, name)
values (23, '0023_lifecycle_gates_offers');
