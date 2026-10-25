-- =====================================================================
-- PRJGENUI Workforce — migration 0022
-- Full assignment lifecycle: the new statuses (register 6.1, the
-- approved 0.3-E lifecycle).
--
-- This migration only extends the assignment_status enum. The value
-- additions are isolated in their own migration because a new enum
-- value cannot be used in the same transaction that creates it; the
-- transition engine, the second readiness gate and the offer flow that
-- use these statuses are migration 0023.
--
-- Lifecycle (with the two readiness gates):
--   proposed -> offered -> accepted -> confirmed -> active ->
--   completed
-- Exceptions: cancelled, no_show, replaced (a replacement chain's
-- original), legacy_recorded (migrated history, unchanged).
-- =====================================================================

alter type assignment_status add value if not exists 'offered';
alter type assignment_status add value if not exists 'accepted';
alter type assignment_status add value if not exists 'active';
alter type assignment_status add value if not exists 'no_show';
alter type assignment_status add value if not exists 'replaced';

insert into schema_migrations (id, name)
values (22, '0022_assignment_lifecycle_statuses');
