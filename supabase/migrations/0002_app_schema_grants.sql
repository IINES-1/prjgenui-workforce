-- =====================================================================
-- PRJGENUI Workforce — migration 0002
-- Grants for the app helper schema.
--
-- Supabase's default privileges cover the public schema only, so the
-- anon/authenticated roles need explicit USAGE on schema app and EXECUTE
-- on the helper functions that the RLS policies call (app.has_role etc).
-- Without these, every policy-protected query fails instead of filtering.
-- =====================================================================

grant usage on schema app to anon, authenticated, service_role;

grant execute on function app.user_id() to anon, authenticated, service_role;
grant execute on function app.has_role(prj_role) to anon, authenticated, service_role;
grant execute on function app.my_worker_id() to anon, authenticated, service_role;

insert into schema_migrations (id, name) values (2, '0002_app_schema_grants');
