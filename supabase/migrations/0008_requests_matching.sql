-- =====================================================================
-- PRJGENUI Workforce — migration 0008
-- Workforce request references and match generation (baseline rules).
--
-- public.generate_matches(request_id) evaluates every non-archived
-- worker against a request and records one generation with its rules
-- version. Every worker appears in the generation with per-factor
-- pass/fail/review results and reasons (explainability, register 5.2).
-- Only workers with every factor passing are put forward (ranked);
-- the rest are recorded with their blockers so Operations can see why.
--
-- Baseline factors (matching rules 0.1):
--   worker_verified — record is verified (or expiring soon)
--   rtw_current    — latest Right to Work check passed, no overdue follow-up
--   trade_match    — worker trade matches the requested trade
--   <requirement>  — one factor per essential requirement of the request
--                    (and per mandatory site requirement, once sites are used)
-- Requirement states: verified and current = pass; awaiting verification =
-- review; verified but expired = fail, with the approved wording (expired
-- evidence means the worker is not put forward until it has been renewed,
-- where the evidence is mandatory for that job or site); not recorded or
-- rejected = fail.
--
-- Only Owner and Operations can run generations (per the access matrix);
-- the guard is inside the function.
-- =====================================================================

-- Request references in the demo's REQ-000001 style, allocated on insert.
create sequence if not exists request_ref_seq start 1;

create or replace function app.assign_request_ref() returns trigger
language plpgsql as $$
begin
  if new.public_reference is null or new.public_reference = '' then
    new.public_reference := 'REQ-' ||
      lpad(nextval('request_ref_seq')::text, 6, '0');
  end if;
  return new;
end $$;

create trigger assign_request_ref before insert on workforce_requests
  for each row execute function app.assign_request_ref();

create or replace function public.generate_matches(p_request_id uuid)
returns jsonb
language plpgsql security definer set search_path = public as $$
declare
  v_req workforce_requests%rowtype;
  v_rules text;
  v_gen uuid;
  v_factors jsonb;
  v_reason text;
  v_result text;
  v_rank int := 0;
  v_put_forward int := 0;
  v_held int := 0;
  v_rtw rtw_checks%rowtype;
  w record;
  item text;
  v_ok boolean;
  v_expired boolean;
  v_pending boolean;
  v_expiry date;
  v_items text[];
begin
  if auth.uid() is null then
    return jsonb_build_object('ok', false, 'error', 'not_signed_in');
  end if;
  if not app.has_role('owner') and not app.has_role('operations') then
    return jsonb_build_object('ok', false, 'error', 'not_permitted');
  end if;

  select * into v_req from workforce_requests where id = p_request_id;
  if v_req.id is null then
    return jsonb_build_object('ok', false, 'error', 'request_not_found');
  end if;
  if v_req.status not in ('open', 'matched') then
    return jsonb_build_object('ok', false, 'error', 'request_not_open');
  end if;

  select version into v_rules
  from rule_versions
  where rule_set = 'matching'
  order by effective_from desc, created_at desc
  limit 1;
  v_rules := coalesce(v_rules, '0.1');

  -- Requirements: the request's essentials plus any site requirements.
  select array_agg(r) into v_items
  from (
    select jsonb_array_elements_text(coalesce(v_req.essential_requirements, '[]'::jsonb)) as r
    union
    select sr.requirement
    from site_requirements sr
    where sr.site_id = v_req.site_id and sr.mandatory
  ) reqs;
  v_items := coalesce(v_items, '{}');

  insert into match_generations (request_id, rules_version, generated_by)
  values (p_request_id, v_rules, auth.uid())
  returning id into v_gen;

  for w in select * from workers
           where status <> 'archived'
           order by full_name
  loop
    v_factors := '[]'::jsonb;

    -- worker_verified
    if w.status in ('verified', 'expiring_soon') then
      v_factors := v_factors || jsonb_build_object(
        'code', 'worker_verified', 'result', 'pass',
        'reason', 'Worker record is verified');
    else
      v_factors := v_factors || jsonb_build_object(
        'code', 'worker_verified', 'result', 'fail',
        'reason', 'Worker record is not verified (status: ' || w.status::text || ')');
    end if;

    -- rtw_current
    select * into v_rtw from rtw_checks
    where worker_id = w.id
    order by check_date desc, created_at desc
    limit 1;
    if v_rtw.id is null then
      v_result := 'fail'; v_reason := 'No Right to Work check has been recorded';
    elsif v_rtw.result <> 'pass' then
      v_result := 'fail'; v_reason := 'The latest Right to Work check did not pass';
    elsif v_rtw.follow_up_due is not null and v_rtw.follow_up_due < current_date then
      v_result := 'fail'; v_reason := 'A follow-up Right to Work check is overdue';
    else
      v_result := 'pass'; v_reason := 'Right to Work check is current';
    end if;
    v_factors := v_factors || jsonb_build_object(
      'code', 'rtw_current', 'result', v_result, 'reason', v_reason);

    -- trade_match
    if w.trade is null then
      v_result := 'fail'; v_reason := 'No trade recorded on the worker record';
    elsif lower(w.trade) = lower(v_req.trade) then
      v_result := 'pass'; v_reason := 'Trade matches the request (' || w.trade || ')';
    else
      v_result := 'fail';
      v_reason := 'Trade is ' || w.trade || '; the request needs ' || v_req.trade;
    end if;
    v_factors := v_factors || jsonb_build_object(
      'code', 'trade_match', 'result', v_result, 'reason', v_reason);

    -- one factor per requirement
    foreach item in array v_items loop
      v_ok := false; v_expired := false; v_pending := false; v_expiry := null;
      select
        exists (select 1 from qualifications q
                where q.worker_id = w.id and q.kind = item
                  and q.status = 'verified'
                  and (q.expiry_date is null or q.expiry_date >= current_date))
        or exists (select 1 from training_certificates t
                   where t.worker_id = w.id and t.training_type = item
                     and t.status = 'verified'
                     and (t.expiry_date is null or t.expiry_date >= current_date))
      into v_ok;
      if not v_ok then
        select
          exists (select 1 from qualifications q
                  where q.worker_id = w.id and q.kind = item
                    and q.status = 'verified' and q.expiry_date < current_date)
          or exists (select 1 from training_certificates t
                     where t.worker_id = w.id and t.training_type = item
                       and t.status = 'verified' and t.expiry_date < current_date)
        into v_expired;
        select
          exists (select 1 from qualifications q
                  where q.worker_id = w.id and q.kind = item
                    and q.status = 'pending_review')
          or exists (select 1 from training_certificates t
                     where t.worker_id = w.id and t.training_type = item
                       and t.status = 'pending_review')
        into v_pending;
        select min(x.expiry_date) into v_expiry
        from (
          select q.expiry_date from qualifications q
          where q.worker_id = w.id and q.kind = item and q.expiry_date < current_date
          union all
          select t.expiry_date from training_certificates t
          where t.worker_id = w.id and t.training_type = item
            and t.expiry_date < current_date
        ) x;
      end if;

      if v_ok then
        v_result := 'pass'; v_reason := 'Recorded and current';
      elsif v_pending then
        v_result := 'review'; v_reason := 'Evidence recorded and awaiting verification';
      elsif v_expired then
        v_result := 'fail';
        v_reason := 'Expired on ' || to_char(v_expiry, 'DD Mon YYYY') ||
                    ' — not put forward until it has been renewed (required for this job or site)';
      else
        v_result := 'fail'; v_reason := 'Not recorded';
      end if;
      v_factors := v_factors || jsonb_build_object(
        'code', item, 'result', v_result, 'reason', v_reason);
    end loop;

    if not exists (
      select 1 from jsonb_array_elements(v_factors) f
      where f->>'result' <> 'pass'
    ) then
      v_rank := v_rank + 1;
      v_put_forward := v_put_forward + 1;
    else
      v_rank := 0;
      v_held := v_held + 1;
    end if;

    insert into matches (generation_id, worker_id, factors, rank)
    values (v_gen, w.id, v_factors, nullif(v_rank, 0));
  end loop;

  if v_put_forward > 0 then
    update workforce_requests set status = 'matched', updated_at = now()
    where id = p_request_id;
  end if;

  return jsonb_build_object('ok', true, 'generation_id', v_gen,
                            'put_forward', v_put_forward, 'held', v_held,
                            'rules_version', v_rules);
end $$;

grant execute on function public.generate_matches(uuid) to authenticated;

insert into schema_migrations (id, name)
values (8, '0008_requests_matching');
