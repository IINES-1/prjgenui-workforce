-- =====================================================================
-- PRJGENUI Workforce — migration 0015
-- Worker self-service and restricted evidence storage
-- (register 10.2, 10.4; NEW Stage 1).
--
-- Workers can now correct their own contact details, trade and
-- availability, and upload replacement evidence:
--   - a new update policy lets a worker update their own row; a guard
--     trigger restricts what they may change (contact, trade,
--     availability only — never name, passport number, status or
--     reasons, which stay with the team), and every change is audited
--     by the platform audit trigger as before
--   - a private storage bucket 'worker-documents' with policies:
--     workers upload/read only their own folder; Owner and Compliance
--     read everything (GDPR: identity documents are restricted-access)
--   - workers can insert their own worker_documents metadata rows;
--     the metadata row keeps document type, retention class and
--     deletion due date, and Compliance verifies status as usual
--
-- Downloads happen through signed URLs only; nothing in the bucket is
-- public. The worker's passport shows their own documents' status.
-- =====================================================================

create policy workers_self_update on workers for update to authenticated
  using (id = app.my_worker_id())
  with check (id = app.my_worker_id());

create or replace function app.guard_worker_self_edit() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  -- No signed-in actor means server-side maintenance (no PostgREST user);
  -- the guard applies only to a signed-in worker editing their own record.
  if auth.uid() is null then
    return new;
  end if;
  -- Team roles are governed by the status engine and the worker-detail
  -- forms; this guard applies to the worker editing their own record.
  if app.has_role('owner') or app.has_role('operations')
     or app.has_role('compliance') then
    return new;
  end if;
  if new.id <> old.id then
    raise exception 'a worker record cannot be reassigned';
  end if;
  if new.full_name <> old.full_name
     or new.passport_no <> old.passport_no
     or new.status <> old.status
     or new.status_reason is distinct from old.status_reason
     or new.created_at <> old.created_at then
    raise exception 'workers may correct only their contact details, trade and availability';
  end if;
  return new;
end $$;

create trigger guard_worker_self_edit before update on workers
  for each row execute function app.guard_worker_self_edit();

-- Worker-document metadata: the worker can add their own rows
-- (replacement evidence), pending verification as usual.
create policy worker_documents_self_insert on worker_documents
  for insert to authenticated
  with check (worker_id = app.my_worker_id());

-- Private bucket for identity and evidence documents.
insert into storage.buckets (id, name, public)
values ('worker-documents', 'worker-documents', false)
on conflict (id) do nothing;

create policy "worker documents: worker own folder"
on storage.objects for select to authenticated
using (bucket_id = 'worker-documents'
       and app.my_worker_id() is not null
       and (storage.foldername(name))[1] = app.my_worker_id()::text);

create policy "worker documents: worker uploads to own folder"
on storage.objects for insert to authenticated
with check (bucket_id = 'worker-documents'
            and app.my_worker_id() is not null
            and (storage.foldername(name))[1] = app.my_worker_id()::text);

create policy "worker documents: owner and compliance read"
on storage.objects for select to authenticated
using (bucket_id = 'worker-documents'
       and (app.has_role('owner') or app.has_role('compliance')));

insert into schema_migrations (id, name)
values (15, '0015_worker_self_service');
