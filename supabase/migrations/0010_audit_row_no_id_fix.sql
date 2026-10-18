-- =====================================================================
-- PRJGENUI Workforce — migration 0010
-- Fix audit trigger for tables without an "id" column.
--
-- app.audit_row() raised 'record "new" has no field "id"' for any insert
-- on assignment_outcomes (primary key assignment_id) and would do the
-- same on performance_scores (primary key worker_id). No outcome could
-- be recorded by anyone, including the database owner.
--
-- The fix keeps the audit writer generic and its semantics unchanged:
-- record_id now falls back through the id-like keys of the row.
-- =====================================================================

create or replace function app.audit_row() returns trigger
language plpgsql security definer set search_path = public as $$
declare
  v_record text;
begin
  v_record := coalesce(
    to_jsonb(new) ->> 'id',
    to_jsonb(old) ->> 'id',
    to_jsonb(new) ->> 'assignment_id',
    to_jsonb(old) ->> 'assignment_id',
    to_jsonb(new) ->> 'worker_id',
    to_jsonb(old) ->> 'worker_id'
  );
  insert into audit_log (actor, action, table_name, record_id, old_value, new_value)
  values (
    app.user_id(),
    lower(tg_op),
    tg_table_name,
    v_record,
    case when tg_op <> 'insert' then to_jsonb(old) end,
    case when tg_op <> 'delete' then to_jsonb(new) end
  );
  return coalesce(new, old);
end $$;

insert into schema_migrations (id, name)
values (10, '0010_audit_row_no_id_fix');
