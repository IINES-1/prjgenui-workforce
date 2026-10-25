-- =====================================================================
-- PRJGENUI Workforce — migration 0024
-- Contractor access (FR-16 scoped view; access matrix: own requests,
-- assignments, statements, worker attendance and feedback; no worker
-- identity documents).
--
-- Row-level policies for contractors (own contractor row, own requests,
-- own assignments, own statements) have been in place since 0001. This
-- migration adds the two pieces the contractor view still needs:
--
--   1. attendance_evidence: contractors read the attendance recorded on
--      their own assignments (the reporting they receive; they do not
--      see any worker's other assignments)
--   2. public.contractor_overview(): one call for the contractor panel.
--      It returns own requests, own assignments with the worker's name
--      and trade ONLY (no passport numbers, no contact details, no
--      identity documents), own assignment statements (latest version
--      each) and the attendance summary per assignment.
--
-- The worker identity fields stay behind the team policies: the RPC is
-- the sanctioned contractor surface, exactly like the scoped statement.
-- =====================================================================

create policy attendance_contractor_read on attendance_evidence
  for select to authenticated
  using (exists (
    select 1 from assignments a
    where a.id = attendance_evidence.assignment_id
      and a.contractor_id = (select contractor_id from profiles
                             where id = auth.uid())));

create or replace function public.contractor_overview()
returns jsonb
language plpgsql security definer set search_path = public as $$
declare
  v_user uuid := auth.uid();
  v_contractor_id uuid;
  v_contractor contractors%rowtype;
  v_requests jsonb;
  v_assignments jsonb;
  v_statements jsonb;
  v_attendance jsonb;
begin
  if v_user is null then
    return jsonb_build_object('ok', false, 'error', 'not_signed_in');
  end if;
  if not app.has_role('contractor') then
    return jsonb_build_object('ok', false, 'error', 'not_permitted',
      'reason', 'this view is for contractor accounts');
  end if;

  select contractor_id into v_contractor_id from profiles where id = v_user;
  if v_contractor_id is null then
    return jsonb_build_object('ok', false, 'error', 'not_linked',
      'reason', 'this account is not linked to a contractor record');
  end if;

  select * into v_contractor from contractors where id = v_contractor_id;

  select coalesce(jsonb_agg(row_to_json(r) order by r.created_at desc), '[]'::jsonb)
  into v_requests
  from (
    select public_reference, trade, number_needed, start_date, duration,
           urgent, status::text as status, created_at
    from workforce_requests where contractor_id = v_contractor_id
  ) r;

  select coalesce(jsonb_agg(row_to_json(a) order by a.created_at desc), '[]'::jsonb)
  into v_assignments
  from (
    select a.id, a.public_reference, a.trade, a.start_date, a.end_date,
           a.status::text as status, a.created_at,
           w.full_name as worker_name, w.trade as worker_trade,
           rq.public_reference as request_reference
    from assignments a
    join workers w on w.id = a.worker_id
    left join workforce_requests rq on rq.id = a.request_id
    where a.contractor_id = v_contractor_id
  ) a;

  -- the latest statement version per own assignment
  select coalesce(jsonb_agg(row_to_json(s) order by s.generated_at desc), '[]'::jsonb)
  into v_statements
  from (
    select distinct on (st.assignment_id)
           st.assignment_id, st.version, st.content, st.generated_at
    from assignment_statements st
    join assignments a on a.id = st.assignment_id
    where a.contractor_id = v_contractor_id
    order by st.assignment_id, st.version desc
  ) s;

  select coalesce(jsonb_agg(row_to_json(att) order by att.shift_date desc), '[]'::jsonb)
  into v_attendance
  from (
    select ae.assignment_id, a.public_reference,
           ae.shift_date, ae.outcome::text as outcome,
           ae.status::text as status
    from attendance_evidence ae
    join assignments a on a.id = ae.assignment_id
    where a.contractor_id = v_contractor_id
  ) att;

  return jsonb_build_object(
    'ok', true,
    'contractor', jsonb_build_object(
      'legal_name', v_contractor.legal_name,
      'contact_name', v_contractor.contact_name,
      'phone', v_contractor.phone,
      'email', v_contractor.email),
    'requests', v_requests,
    'assignments', v_assignments,
    'statements', v_statements,
    'attendance', v_attendance);
end $$;

grant execute on function public.contractor_overview() to authenticated;

insert into schema_migrations (id, name)
values (24, '0024_contractor_access');
