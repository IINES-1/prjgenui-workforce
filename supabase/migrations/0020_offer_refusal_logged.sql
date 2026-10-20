-- =====================================================================
-- PRJGENUI Workforce — migration 0020
-- Offer refusal is logged, not just raised (follow-up to 0019).
--
-- 0019's trigger raised an exception after writing the refusal to the
-- audit log — but raising aborts the transaction, so the audit entry
-- died with it. The refusal is now recorded the way the platform's RPCs
-- already work: the audit entry persists, the insert is cancelled
-- (returning NULL from the BEFORE trigger), and a WARNING states the
-- rule. The Stage 2 offer flow (the only route that will create offers
-- through the app) checks the approved match first and returns an
-- explicit ok:false refusal to the operator, per the RPC pattern; this
-- trigger is the database-level backstop behind it.
-- =====================================================================

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
    raise warning 'offer_refused_no_approved_match: an offer can only be '
                  'created from an approved match for this worker and request '
                  '(attempt logged in audit_log)';
    return null;  -- the insert is refused; no offer row is created
  end if;
  return new;
end $$;

insert into schema_migrations (id, name)
values (20, '0020_offer_refusal_logged');
