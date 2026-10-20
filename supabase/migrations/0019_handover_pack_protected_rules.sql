-- =====================================================================
-- PRJGENUI Workforce — migration 0019
-- Protected-rule enforcement from the 0.3-E technical handover pack
-- (reconciliation, 20 October 2026).
--
-- Two gaps found during the acceptance-catalogue reconciliation, both
-- closed here:
--
-- 1. AT-03 / protected rule "Compliance precedence": a failed Right to
--    Work check must not be overridable — by a score or by a reviewer.
--    Migration 0014 let any approved override waive any mandatory
--    blocker, including the RTW ones. evaluate_readiness now never
--    waives the RTW blockers (rtw_missing, rtw_not_pass,
--    rtw_followup_overdue). Overrides remain available for every other
--    requirement, exactly as before.
--
-- 2. AT-06 / protected rule "Human authority": an offer may only be
--    created from an approved match. Matches now carry a recorded
--    decision (approved/rejected, who, when — audited like everything
--    else), and assignment_offers refuses any offer for a worker and
--    request with no approved match, logging the refusal.
-- =====================================================================

-- ---------------------------------------------------------------- 1. RTW blockers are never waived

create or replace function public.evaluate_readiness(p_worker_id uuid)
returns jsonb
language plpgsql security definer set search_path = public as $$
declare
  v_rules text;
  v_status worker_status;
  v_rtw rtw_checks%rowtype;
  v_blockers jsonb := '[]'::jsonb;
  v_final jsonb;
  v_outcome text;
begin
  if auth.uid() is null then
    return jsonb_build_object('ok', false, 'error', 'not_signed_in');
  end if;
  if not app.has_role('owner') and not app.has_role('compliance') then
    return jsonb_build_object('ok', false, 'error', 'not_permitted');
  end if;

  select status into v_status from workers where id = p_worker_id;
  if v_status is null then
    return jsonb_build_object('ok', false, 'error', 'worker_not_found');
  end if;

  select version into v_rules
  from rule_versions
  where rule_set = 'readiness'
  order by effective_from desc, created_at desc
  limit 1;
  v_rules := coalesce(v_rules, '0.1');

  if v_status not in ('verified', 'expiring_soon') then
    v_blockers := v_blockers || jsonb_build_object(
      'code', 'worker_not_verified',
      'reason', 'Worker record is not verified (current status: '
                || v_status::text || ')',
      'mandatory', true);
  end if;

  select * into v_rtw
  from rtw_checks
  where worker_id = p_worker_id
  order by check_date desc, created_at desc
  limit 1;

  if v_rtw.id is null then
    v_blockers := v_blockers || jsonb_build_object(
      'code', 'rtw_missing',
      'reason', 'No Right to Work check has been recorded',
      'mandatory', true);
  else
    if v_rtw.result <> 'pass' then
      v_blockers := v_blockers || jsonb_build_object(
        'code', 'rtw_not_pass',
        'reason', 'The latest Right to Work check did not pass',
        'mandatory', true);
    end if;
    if v_rtw.follow_up_due is not null and v_rtw.follow_up_due < current_date then
      v_blockers := v_blockers || jsonb_build_object(
        'code', 'rtw_followup_overdue',
        'reason', 'A follow-up Right to Work check is overdue (was due '
                  || to_char(v_rtw.follow_up_due, 'DD Mon YYYY') || ')',
        'mandatory', true);
    end if;
  end if;

  -- Controlled overrides (register 7.4): an active approved override for
  -- this worker and this requirement waives the blocker. The blocker is
  -- kept in the record, marked not mandatory, with the approver named.
  -- Per the handover pack's protected rule (compliance precedence) the
  -- Right to Work blockers are never waivable (AT-03): a failed work-
  -- right check stands regardless of any override.
  select coalesce(jsonb_agg(
    case
      when (b ->> 'mandatory')::boolean and o.id is not null then
        jsonb_set(
          jsonb_set(b, '{mandatory}', 'false'::jsonb),
          '{reason}',
          to_jsonb(b ->> 'reason' || ' — waived by an approved override (' ||
                   o.reason || ')'))
      else b
    end
  ), '[]'::jsonb)
  into v_final
  from jsonb_array_elements(v_blockers) b
  left join overrides o
    on o.worker_id = p_worker_id
   and o.requirement = b ->> 'code'
   and (o.expires_at is null or o.expires_at > now())
   and (b ->> 'code') not in ('rtw_missing', 'rtw_not_pass',
                              'rtw_followup_overdue');

  if not exists (
    select 1 from jsonb_array_elements(v_final) f
    where (f ->> 'mandatory')::boolean
  ) then
    v_outcome := 'pass';
  else
    v_outcome := 'blocked';
  end if;

  insert into readiness_evaluations
    (worker_id, rules_version, outcome, blockers, evaluated_by)
  values (p_worker_id, v_rules, v_outcome, v_final, auth.uid());

  return jsonb_build_object('ok', true, 'outcome', v_outcome,
                            'blockers', v_final, 'rules_version', v_rules);
end $$;

-- ---------------------------------------------------------------- 2. match decisions are recorded

alter table matches
  add column decision   text check (decision in ('approved','rejected')),
  add column decided_by uuid references profiles(id),
  add column decided_at timestamptz;

-- ---------------------------------------------------------------- 3. offers require an approved match (AT-06)

create or replace function app.enforce_offer_approved_match() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if not exists (
    select 1
    from matches m
    join match_generations g on g.id = m.generation_id
    where g.request_id = new.request_id
      and m.worker_id = new.worker_id
      and m.decision = 'approved'
  ) then
    insert into audit_log (actor, action, table_name, record_id, new_value)
    values (auth.uid(), 'offer_refused_no_approved_match', 'assignment_offers',
            null,
            jsonb_build_object('request_id', new.request_id,
                               'worker_id', new.worker_id,
                               'rule', 'an offer can only be created from an '
                                       'approved match'));
    raise exception
      'offer_refused_no_approved_match: an offer can only be created from '
      'an approved match for this worker and request';
  end if;
  return new;
end $$;

create trigger enforce_offer_approved_match
before insert on assignment_offers
for each row execute function app.enforce_offer_approved_match();

insert into schema_migrations (id, name)
values (19, '0019_handover_pack_protected_rules');
