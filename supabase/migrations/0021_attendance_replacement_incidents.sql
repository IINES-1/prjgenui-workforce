-- =====================================================================
-- PRJGENUI Workforce — migration 0021
-- Attendance evidence with a dispute path, and replacement incidents
-- (register FR-11, FR-12; AT-10, AT-11, AT-12 data layer; the approved
-- 0.3-E release "live evidence and replacement incidents").
--
-- ATTENDANCE (FR-11, AT-10, AT-11)
--   attendance_evidence   one record per assignment and shift date:
--                         outcome (attended/late/no_show/excused/
--                         not_recorded), reporter, source, note — the
--                         original fact, never edited after the fact
--   attendance_disputes  the worker's dispute right (register 10.2):
--                         a dispute appends, it never deletes or edits
--                         the original; resolution is audited and either
--                         the original stands or a correction is
--                         appended with the corrected outcome
--
--   One record per assignment/date is the authoritative one: a second
--   record for the same shift is refused (the dashboard's rule) —
--   dispute the existing record instead of layering a second one.
--
-- REPLACEMENT (FR-12, AT-12 chain, AT-13 acknowledgement fields)
--   replacement_incidents          incident on an existing assignment:
--                                   cancellation / no_show /
--                                   replacement_required, recorded_by,
--                                   elapsed time derivable
--                                   (recorded_at -> resolved_at)
--   replacement_incident_approvals append-only approval history; the
--                                   controlling decision is the most
--                                   recent entry, never overwritten
--
--   The replacement chain reuses the normal controls only: the
--   replacement assignment must be for the same request and must have
--   been created through the normal offer path (offer_id set), which
--   0020 already backstops with the approved-match rule. Nothing here
--   bypasses matching, approval or the offer flow. A cancellation
--   incident transitions the original assignment through the existing
--   status engine (proposed/confirmed -> cancelled); NO_SHOW and
--   REPLACED assignment statuses arrive with the Stage 2 full-lifecycle
--   build, so no_show / replacement_required incidents record the fact
--   now and do not force a status change yet.
--
--   Site-pack acknowledgement (AT-13) is carried on the incident
--   (actor + timestamp); it is refused until an explicit operator
--   action records it.
--
-- Access: Owner and Operations record and manage; Compliance and
-- Auditor read everything; workers read their own attendance evidence
-- and raise disputes on it (their correction and dispute right).
-- Writes to these tables happen through the RPCs below — the
-- attendance original is not directly editable by anyone.
-- =====================================================================

-- ---------------------------------------------------------------- types

create type attendance_outcome    as enum ('attended','late','no_show','excused','not_recorded');
create type attendance_status     as enum ('verified','disputed','corrected');
create type attendance_dispute_status as enum ('open','resolved');
create type attendance_dispute_resolution as enum ('original_stands','corrected','withdrawn');
create type replacement_incident_type as enum ('cancellation','no_show','replacement_required');
create type replacement_approval_decision as enum ('approved','refused');

-- ---------------------------------------------------------------- attendance

create table attendance_evidence (
  id            uuid primary key default gen_random_uuid(),
  assignment_id uuid not null references assignments(id) on delete cascade,
  worker_id     uuid not null references workers(id) on delete cascade,
  shift_date    date not null,
  outcome       attendance_outcome not null,
  status        attendance_status not null default 'verified',
  reporter_id   uuid references profiles(id),
  source        text,
  note          text,
  file_reference text,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now(),
  unique (assignment_id, shift_date)
);

-- The evidence row always mirrors the assignment's worker: the link is
-- set at insert and cannot silently diverge.
create or replace function app.guard_attendance_worker() returns trigger
language plpgsql security definer set search_path = public as $$
declare
  v_worker uuid;
begin
  select worker_id into v_worker from assignments where id = new.assignment_id;
  if v_worker is null then
    raise exception 'attendance evidence requires an existing assignment';
  end if;
  if v_worker <> new.worker_id then
    raise exception 'attendance evidence must record the assignment''s own worker';
  end if;
  return new;
end $$;

create trigger guard_attendance_worker before insert on attendance_evidence
  for each row execute function app.guard_attendance_worker();

-- Disputes append to the original; the original row's status is the
-- only thing that ever changes (verified -> disputed -> verified/corrected).
create table attendance_disputes (
  id                 uuid primary key default gen_random_uuid(),
  attendance_evidence_id uuid not null references attendance_evidence(id) on delete cascade,
  raised_by          uuid references profiles(id),
  note               text,
  status             attendance_dispute_status not null default 'open',
  resolution         attendance_dispute_resolution,
  corrected_outcome  attendance_outcome,
  resolution_note    text,
  resolved_by        uuid references profiles(id),
  resolved_at       timestamptz,
  created_at         timestamptz not null default now()
);

-- ---------------------------------------------------------------- replacement

create table replacement_incidents (
  id            uuid primary key default gen_random_uuid(),
  assignment_id uuid not null references assignments(id) on delete cascade,
  request_id    uuid references workforce_requests(id),
  incident_type replacement_incident_type not null,
  recorded_by   uuid references profiles(id),
  recorded_at   timestamptz not null default now(),
  notes         text,
  replacement_match_generation_id uuid references match_generations(id),
  replacement_assignment_id uuid references assignments(id),
  site_pack_ack_by uuid references profiles(id),
  site_pack_ack_at timestamptz,
  resolved_at    timestamptz,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now(),
  constraint replacement_not_original
    check (replacement_assignment_id is null
           or replacement_assignment_id <> assignment_id)
);

-- One open incident per original assignment; a new fact needs a new
-- incident after the previous chain is resolved.
create unique index one_open_replacement_incident
  on replacement_incidents (assignment_id) where resolved_at is null;

-- Append-only approval history: the controlling decision is the most
-- recent entry, never an edit of an earlier one.
create table replacement_incident_approvals (
  id          uuid primary key default gen_random_uuid(),
  incident_id uuid not null references replacement_incidents(id) on delete cascade,
  approver_id uuid references profiles(id),
  decision    replacement_approval_decision not null,
  notes       text,
  created_at  timestamptz not null default now()
);

-- ---------------------------------------------------------------- RPCs

-- Record attendance evidence (Owner/Operations; contractor reporting
-- arrives with the contractor view).
create or replace function public.record_attendance_evidence(
  p_assignment_id uuid,
  p_shift_date    date,
  p_outcome       attendance_outcome,
  p_source        text default null,
  p_note          text default null
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
    return jsonb_build_object('ok', false, 'error', 'not_permitted',
      'reason', 'attendance is recorded by the platform team');
  end if;

  select * into v_assignment from assignments where id = p_assignment_id;
  if not found then
    return jsonb_build_object('ok', false, 'error', 'assignment_not_found');
  end if;

  if exists (select 1 from attendance_evidence
             where assignment_id = p_assignment_id and shift_date = p_shift_date) then
    return jsonb_build_object('ok', false, 'error', 'duplicate_record',
      'reason', 'an attendance record already exists for this assignment '
                'and date — dispute it first if it needs correcting; the '
                'existing record is the authoritative one until then');
  end if;

  insert into attendance_evidence
    (assignment_id, worker_id, shift_date, outcome, reporter_id, source, note)
  values (p_assignment_id, v_assignment.worker_id, p_shift_date, p_outcome,
          v_user, p_source, p_note);

  return jsonb_build_object('ok', true);
end $$;

-- The worker's dispute right on their own attendance (register 10.2);
-- Compliance and Owner can raise one on the worker's behalf.
create or replace function public.dispute_attendance_evidence(
  p_evidence_id uuid,
  p_note        text
) returns jsonb
language plpgsql security definer set search_path = public as $$
declare
  v_user uuid := auth.uid();
  v_evidence attendance_evidence%rowtype;
begin
  if v_user is null then
    return jsonb_build_object('ok', false, 'error', 'not_signed_in');
  end if;

  select * into v_evidence from attendance_evidence where id = p_evidence_id;
  if not found then
    return jsonb_build_object('ok', false, 'error', 'record_not_found');
  end if;

  if not (app.my_worker_id() = v_evidence.worker_id
          or app.has_role('owner') or app.has_role('compliance')) then
    return jsonb_build_object('ok', false, 'error', 'not_permitted',
      'reason', 'attendance is disputed by the worker it records, or by '
                'Compliance on their behalf');
  end if;
  if v_evidence.status = 'disputed' then
    return jsonb_build_object('ok', false, 'error', 'already_disputed',
      'reason', 'this attendance record already has an open dispute');
  end if;

  insert into attendance_disputes (attendance_evidence_id, raised_by, note)
  values (p_evidence_id, v_user, p_note);

  update attendance_evidence set status = 'disputed', updated_at = now()
  where id = p_evidence_id;

  return jsonb_build_object('ok', true);
end $$;

-- Resolve a dispute (Compliance/Owner): the original fact is retained
-- whatever the outcome — it either stands, or a correction is appended.
create or replace function public.resolve_attendance_dispute(
  p_dispute_id       uuid,
  p_resolution       attendance_dispute_resolution,
  p_corrected_outcome attendance_outcome default null,
  p_note             text default null
) returns jsonb
language plpgsql security definer set search_path = public as $$
declare
  v_user uuid := auth.uid();
  v_dispute attendance_disputes%rowtype;
  v_evidence attendance_evidence%rowtype;
begin
  if v_user is null then
    return jsonb_build_object('ok', false, 'error', 'not_signed_in');
  end if;
  if not (app.has_role('owner') or app.has_role('compliance')) then
    return jsonb_build_object('ok', false, 'error', 'not_permitted',
      'reason', 'disputes are resolved by Compliance');
  end if;

  select * into v_dispute from attendance_disputes where id = p_dispute_id;
  if not found then
    return jsonb_build_object('ok', false, 'error', 'dispute_not_found');
  end if;
  if v_dispute.status <> 'open' then
    return jsonb_build_object('ok', false, 'error', 'already_resolved');
  end if;
  if p_resolution = 'corrected' and p_corrected_outcome is null then
    return jsonb_build_object('ok', false, 'error', 'correction_required',
      'reason', 'a correction must state the corrected outcome');
  end if;
  if p_resolution = 'corrected' then
    select * into v_evidence from attendance_evidence
    where id = v_dispute.attendance_evidence_id;
    if p_corrected_outcome = v_evidence.outcome then
      return jsonb_build_object('ok', false, 'error', 'correction_identical',
        'reason', 'the corrected outcome is the same as the original — '
                  'resolve as original_stands instead');
    end if;
  end if;

  update attendance_disputes
  set status = 'resolved',
      resolution = p_resolution,
      corrected_outcome = p_corrected_outcome,
      resolution_note = p_note,
      resolved_by = v_user,
      resolved_at = now()
  where id = p_dispute_id;

  update attendance_evidence
  set status = (case when p_resolution = 'corrected'
                    then 'corrected'::attendance_status
                    else 'verified'::attendance_status end),
      updated_at = now()
  where id = v_dispute.attendance_evidence_id;

  return jsonb_build_object('ok', true);
end $$;

-- Record a replacement incident (Owner/Operations). A cancellation
-- moves the original assignment through the normal status engine;
-- no_show / replacement_required record the fact without forcing a
-- status change (the NO_SHOW/REPLACED statuses arrive with the Stage 2
-- full-lifecycle build).
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

  -- A cancellation moves the original through the normal status engine.
  -- An already-cancelled assignment needs no transition (the incident is
  -- still a record); anything else (completed, legacy) that cannot legally
  -- move to cancelled is refused — no silent force, the engine decides.
  if p_incident_type = 'cancellation' and v_assignment.status <> 'cancelled' then
    begin
      update assignments set status = 'cancelled'
      where id = p_assignment_id;
    exception when others then
      return jsonb_build_object('ok', false, 'error', 'status_transition_refused',
        'reason', 'the assignment cannot move to cancelled from its '
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

-- Append a contractor-approval decision (Owner/Operations record it;
-- contractor-side entry arrives with the contractor view). History is
-- append-only; the most recent entry controls.
create or replace function public.record_replacement_approval(
  p_incident_id uuid,
  p_decision    replacement_approval_decision,
  p_notes       text default null
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

  if not exists (select 1 from replacement_incidents where id = p_incident_id) then
    return jsonb_build_object('ok', false, 'error', 'incident_not_found');
  end if;

  insert into replacement_incident_approvals (incident_id, approver_id, decision, notes)
  values (p_incident_id, v_user, p_decision, p_notes);

  return jsonb_build_object('ok', true);
end $$;

-- Link the replacement assignment to the incident (an explicit,
-- separate operator action). The same-controls rule: the replacement
-- must be for the same request and must have come through the normal
-- offer path (offer_id set — 0020's backstop already guarantees the
-- offer came from an approved match).
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

  -- The generation of the approved match behind the replacement's offer,
  -- so the chain points at the normal matching controls that produced it.
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

  return jsonb_build_object('ok', true, 'match_generation_id', v_generation);
end $$;

-- Site-pack acknowledgement (AT-13): an explicit operator action,
-- refused if already acknowledged or after the chain is closed.
create or replace function public.acknowledge_replacement_site_pack(
  p_incident_id uuid
) returns jsonb
language plpgsql security definer set search_path = public as $$
declare
  v_user uuid := auth.uid();
  v_incident replacement_incidents%rowtype;
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
  if v_incident.site_pack_ack_at is not null then
    return jsonb_build_object('ok', false, 'error', 'already_acknowledged');
  end if;

  update replacement_incidents
  set site_pack_ack_by = v_user,
      site_pack_ack_at = now(),
      updated_at = now()
  where id = p_incident_id;

  return jsonb_build_object('ok', true);
end $$;

-- Close the chain (Owner/Operations). Elapsed time is recorded_at to
-- resolved_at. Resolving without a linked replacement is allowed — the
-- incident is the record either way.
create or replace function public.resolve_replacement_incident(
  p_incident_id uuid,
  p_notes       text default null
) returns jsonb
language plpgsql security definer set search_path = public as $$
declare
  v_user uuid := auth.uid();
  v_incident replacement_incidents%rowtype;
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
    return jsonb_build_object('ok', false, 'error', 'already_resolved');
  end if;

  update replacement_incidents
  set resolved_at = now(),
      notes = case when p_notes is null then notes
                   else notes || E'\n' || p_notes end,
      updated_at = now()
  where id = p_incident_id;

  return jsonb_build_object('ok', true,
    'elapsed', extract(epoch from (now() - v_incident.recorded_at)));
end $$;

grant execute on function public.record_attendance_evidence(uuid, date, attendance_outcome, text, text) to authenticated;
grant execute on function public.dispute_attendance_evidence(uuid, text) to authenticated;
grant execute on function public.resolve_attendance_dispute(uuid, attendance_dispute_resolution, attendance_outcome, text) to authenticated;
grant execute on function public.record_replacement_incident(uuid, replacement_incident_type, text) to authenticated;
grant execute on function public.record_replacement_approval(uuid, replacement_approval_decision, text) to authenticated;
grant execute on function public.link_replacement_assignment(uuid, uuid) to authenticated;
grant execute on function public.acknowledge_replacement_site_pack(uuid) to authenticated;
grant execute on function public.resolve_replacement_incident(uuid, text) to authenticated;

-- ---------------------------------------------------------------- RLS

alter table attendance_evidence        enable row level security;
alter table attendance_disputes        enable row level security;
alter table replacement_incidents      enable row level security;
alter table replacement_incident_approvals enable row level security;

-- Attendance: team roles read and record; the original row is never
-- directly editable (resolution happens through the RPC).
create policy attendance_team_read on attendance_evidence for select to authenticated
  using (app.has_role('owner') or app.has_role('operations')
         or app.has_role('compliance') or app.has_role('auditor'));
create policy attendance_team_insert on attendance_evidence for insert to authenticated
  with check (app.has_role('owner') or app.has_role('operations'));

-- The worker reads their own attendance evidence (the dispute right
-- needs the record).
create policy attendance_worker_read on attendance_evidence for select to authenticated
  using (worker_id = app.my_worker_id());

-- Disputes: team reads all; the worker reads their own (through the
-- evidence row). Inserts and updates happen through the RPCs only.
create policy attendance_disputes_team_read on attendance_disputes for select to authenticated
  using (app.has_role('owner') or app.has_role('operations')
         or app.has_role('compliance') or app.has_role('auditor'));
create policy attendance_disputes_worker_read on attendance_disputes for select to authenticated
  using (exists (select 1 from attendance_evidence e
                 where e.id = attendance_evidence_id
                   and e.worker_id = app.my_worker_id()));

-- Replacement incidents and approvals: team records, compliance and
-- auditor read. Workers meet incidents through their assignment record,
-- not this table.
create policy replacement_incidents_team on replacement_incidents for all to authenticated
  using (app.has_role('owner') or app.has_role('operations'))
  with check (app.has_role('owner') or app.has_role('operations'));
create policy replacement_incidents_read on replacement_incidents for select to authenticated
  using (app.has_role('compliance') or app.has_role('auditor'));
create policy replacement_approvals_team on replacement_incident_approvals for all to authenticated
  using (app.has_role('owner') or app.has_role('operations'))
  with check (app.has_role('owner') or app.has_role('operations'));
create policy replacement_approvals_read on replacement_incident_approvals for select to authenticated
  using (app.has_role('compliance') or app.has_role('auditor'));

-- ---------------------------------------------------------------- audit

create trigger set_updated_at_attendance before update on attendance_evidence
  for each row execute function app.set_updated_at();
create trigger set_updated_at_replacement before update on replacement_incidents
  for each row execute function app.set_updated_at();

create trigger audit_attendance_evidence after insert or update or delete on attendance_evidence
  for each row execute function app.audit_row();
create trigger audit_attendance_disputes after insert or update or delete on attendance_disputes
  for each row execute function app.audit_row();
create trigger audit_replacement_incidents after insert or update or delete on replacement_incidents
  for each row execute function app.audit_row();
create trigger audit_replacement_approvals after insert or update or delete on replacement_incident_approvals
  for each row execute function app.audit_row();

insert into schema_migrations (id, name)
values (21, '0021_attendance_replacement_incidents');
