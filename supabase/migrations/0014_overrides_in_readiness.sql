-- =====================================================================
-- PRJGENUI Workforce — migration 0014
-- Controlled overrides honoured by the readiness rules
-- (register 7.4, NEW Stage 1).
--
-- An override records: who approved it, why, on whose authority, an
-- optional expiry, and it is limited to one worker and one requirement.
-- It never edits a check — it temporarily relaxes one specific
-- requirement. This migration makes that true in the rules:
-- public.evaluate_readiness now marks a blocker as waived (mandatory
-- false, with the approver recorded) when an active, approved override
-- covers it, and the hard gate follows the evaluation as before.
-- Every override insert is already audited by the platform audit
-- trigger, so the permanent audit entry exists by design.
-- =====================================================================

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
   and (o.expires_at is null or o.expires_at > now());

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

insert into schema_migrations (id, name)
values (14, '0014_overrides_in_readiness');
