-- =====================================================================
-- PRJGENUI Workforce — migration 0018
--
-- 1. Qualification validity (register 3.5, review item 2):
--    NVQs and some City & Guilds qualifications have no expiry date.
--    The platform must support qualifications that are permanent
--    (never expire) or renewable (renewed before the next date),
--    and must never reject a record for a missing expiry date.
--    expiry_date stays nullable; validity records the intent:
--      'expiring'  — the qualification expires on expiry_date
--      'renewable' — renewed before expiry_date (next renewal date)
--      'permanent' — no expiry (NVQ, legacy City & Guilds, etc.)
--    Matching already treats a null expiry as current, and the expiry
--    schedule only picks up rows with a date, so no logic changes are
--    needed beyond the explicit marker.
--
-- 2. Audit-log sanitisation (GDPR review, item 4):
--    app.audit_row() wrote the full old/new row to audit_log. Rows on
--    audited tables can carry sensitive values (invitation tokens,
--    share codes, credentials). Those values must never be copied into
--    the audit trail. A scrub helper strips sensitive keys from any
--    row image before it is written, and existing audit_log rows are
--    cleaned in the same pass.
-- =====================================================================

-- 1a. Validity marker on qualifications and training certificates.
alter table qualifications
  add column if not exists validity text not null default 'expiring';
alter table training_certificates
  add column if not exists validity text not null default 'expiring';

alter table qualifications
  drop constraint if exists qualifications_validity_check;
alter table qualifications
  add constraint qualifications_validity_check
  check (validity in ('expiring', 'renewable', 'permanent'));

alter table training_certificates
  drop constraint if exists training_certificates_validity_check;
alter table training_certificates
  add constraint training_certificates_validity_check
  check (validity in ('expiring', 'renewable', 'permanent'));

-- A permanent qualification must not carry an expiry date (the marker
-- and the date would contradict each other).
alter table qualifications
  drop constraint if exists qualifications_permanent_no_expiry_check;
alter table qualifications
  add constraint qualifications_permanent_no_expiry_check
  check (validity <> 'permanent' or expiry_date is null);

alter table training_certificates
  drop constraint if exists training_permanent_no_expiry_check;
alter table training_certificates
  add constraint training_permanent_no_expiry_check
  check (validity <> 'permanent' or expiry_date is null);

-- 2a. Scrub helper: remove sensitive keys from a row image.
--     Never copies: invitation tokens, share codes, credentials,
--     recovery codes or API keys into the audit trail.
create or replace function app.audit_scrub(v jsonb) returns jsonb
language sql immutable as $$
  select case
    when v is null then null
    else (
      select coalesce(jsonb_object_agg(key, value), '{}'::jsonb)
      from jsonb_each(v)
      where lower(key) not in (
        'token', 'share_code', 'sharecode', 'secret', 'password',
        'passphrase', 'recovery_code', 'recoverycode', 'api_key',
        'apikey', 'otp_secret', 'client_secret'
      )
    )
  end
$$;

-- 2b. audit_row() writes scrubbed images only.
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
    case when tg_op <> 'insert' then app.audit_scrub(to_jsonb(old)) end,
    case when tg_op <> 'delete' then app.audit_scrub(to_jsonb(new)) end
  );
  return coalesce(new, old);
end $$;

-- 2c. Clean any sensitive values already written to the audit trail.
update audit_log
  set old_value = app.audit_scrub(old_value),
      new_value = app.audit_scrub(new_value)
  where old_value is not null or new_value is not null;

insert into schema_migrations (id, name)
values (18, '0018_validity_and_audit_scrub');
