-- =====================================================================
-- PRJGENUI Workforce — migration 0007
-- Readiness evaluation (baseline rules, worker level).
--
-- public.evaluate_readiness(worker_id) runs the baseline readiness check
-- (rules version from rule_versions, currently 0.1) and records the
-- result in readiness_evaluations, which the hard gate reads before an
-- assignment can be confirmed. Job- and site-level requirements join
-- the rules with the request/matching build (Stage 0 later slices).
--
-- Baseline conditions (worker level):
--   1. the worker record is verified (or expiring soon)
--   2. a Right to Work check is recorded
--   3. the latest Right to Work check passed
--   4. any Right to Work follow-up is not overdue
-- Every blocker carries a reason and is mandatory by definition; the
-- approved expiry rule (expired evidence blocks only where mandatory
-- for the job or site) is applied when job requirements are evaluated.
--
-- Only Owner and Compliance can run evaluations (per the access matrix);
-- Operations read the results. The guard is inside the function.
-- =====================================================================

create or replace function public.evaluate_readiness(p_worker_id uuid)
returns jsonb
language plpgsql security definer set search_path = public as $$
declare
  v_rules text;
  v_status worker_status;
  v_rtw rtw_checks%rowtype;
  v_blockers jsonb := '[]'::jsonb;
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

  if v_blockers = '[]'::jsonb then
    v_outcome := 'pass';
  else
    v_outcome := 'blocked';
  end if;

  insert into readiness_evaluations
    (worker_id, rules_version, outcome, blockers, evaluated_by)
  values (p_worker_id, v_rules, v_outcome, v_blockers, auth.uid());

  return jsonb_build_object('ok', true, 'outcome', v_outcome,
                            'blockers', v_blockers, 'rules_version', v_rules);
end $$;

grant execute on function public.evaluate_readiness(uuid) to authenticated;

insert into schema_migrations (id, name)
values (7, '0007_readiness_evaluation');
