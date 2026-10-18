-- =====================================================================
-- PRJGENUI Workforce — migration 0013
-- Assignment statements (register 6.6, NEW Stage 1).
--
-- public.generate_assignment_statement(assignment_id) builds a statement
-- in the house style from the live record — assignment reference,
-- worker and passport number, client, dates, status and any outcome —
-- and stores it as a new version. Earlier versions are kept, so what
-- was issued at any time can always be shown again.
--
-- Only Owner and Operations can generate statements (access matrix);
-- contractor and worker can read their own (policies already in place).
-- =====================================================================

create or replace function public.generate_assignment_statement(p_assignment_id uuid)
returns jsonb
language plpgsql security definer set search_path = public as $$
declare
  v_asg assignments%rowtype;
  v_worker workers%rowtype;
  v_contractor contractors%rowtype;
  v_request workforce_requests%rowtype;
  v_outcome assignment_outcomes%rowtype;
  v_version int;
  v_stmt_id uuid;
  v_content jsonb;
begin
  if auth.uid() is null then
    return jsonb_build_object('ok', false, 'error', 'not_signed_in');
  end if;
  if not app.has_role('owner') and not app.has_role('operations') then
    return jsonb_build_object('ok', false, 'error', 'not_permitted');
  end if;

  select * into v_asg from assignments where id = p_assignment_id;
  if v_asg.id is null then
    return jsonb_build_object('ok', false, 'error', 'assignment_not_found');
  end if;

  select * into v_worker from workers where id = v_asg.worker_id;
  select * into v_request from workforce_requests where id = v_asg.request_id;
  if v_asg.contractor_id is not null then
    select * into v_contractor from contractors where id = v_asg.contractor_id;
  elsif v_request.id is not null then
    select * into v_contractor from contractors where id = v_request.contractor_id;
  end if;
  select * into v_outcome from assignment_outcomes
  where assignment_id = p_assignment_id;

  v_content := jsonb_build_object(
    'title', 'Assignment statement',
    'reference', v_asg.public_reference,
    'worker', jsonb_build_object(
      'name', v_worker.full_name,
      'passport_no', v_worker.passport_no,
      'trade', coalesce(v_asg.trade, v_worker.trade)),
    'client', coalesce(v_contractor.legal_name,
                       v_asg.legacy_client_text, 'Not recorded'),
    'work', jsonb_build_object(
      'trade', v_asg.trade,
      'start_date', v_asg.start_date,
      'end_date', v_asg.end_date),
    'status', v_asg.status::text,
    'outcome', case when v_outcome.assignment_id is null then null
      else jsonb_build_object(
        'attended', v_outcome.attended,
        'rating', v_outcome.rating,
        'rehire_decision', v_outcome.rehire_decision,
        'client_feedback', v_outcome.client_feedback) end,
    'note', 'This statement is generated from the PRJGENUI Workforce record ' ||
            'at the time shown. It reflects the status and outcome recorded ' ||
            'on that date.',
    'generated_at', now()
  );

  select coalesce(max(version), 0) + 1 into v_version
  from assignment_statements where assignment_id = p_assignment_id;

  insert into assignment_statements (assignment_id, version, content,
                                     generated_by)
  values (p_assignment_id, v_version, v_content, auth.uid())
  returning id into v_stmt_id;

  return jsonb_build_object('ok', true, 'statement_id', v_stmt_id,
                            'version', v_version, 'content', v_content);
end $$;

grant execute on function public.generate_assignment_statement(uuid) to authenticated;

insert into schema_migrations (id, name)
values (13, '0013_assignment_statements');
