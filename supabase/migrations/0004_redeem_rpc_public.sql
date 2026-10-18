-- =====================================================================
-- PRJGENUI Workforce — migration 0004
-- Move the invitation redemption RPCs into the public schema.
--
-- PostgREST (the /rest/v1/rpc endpoint) only exposes functions in the
-- schemas configured as exposed (public by default), so the client-side
-- calls to check_invitation and complete_invitation must live in public.
-- The internal helpers stay in the app schema (they are called from
-- policies and triggers, which do not go through PostgREST).
-- =====================================================================

create or replace function public.check_invitation(p_token uuid)
returns table (found boolean, usable boolean, email text, role prj_role,
               expires_at timestamptz)
language sql stable security definer set search_path = public as $$
  select true,
         (i.used_at is null and now() < i.expires_at),
         i.email, i.role, i.expires_at
  from invitations i
  where i.token = p_token
  union all
  select false, false, null::text, null::prj_role, null::timestamptz
  where not exists (select 1 from invitations i where i.token = p_token)
$$;

create or replace function public.complete_invitation(p_token uuid,
                                                      p_full_name text default null)
returns jsonb
language plpgsql security definer set search_path = public as $$
declare
  inv invitations%rowtype;
  v_user uuid := auth.uid();
  v_email text;
begin
  if v_user is null then
    return jsonb_build_object('ok', false, 'error', 'not_signed_in');
  end if;

  select * into inv from invitations where token = p_token;
  if not found then
    return jsonb_build_object('ok', false, 'error', 'not_found');
  end if;
  if inv.used_at is not null then
    return jsonb_build_object('ok', false, 'error', 'already_used');
  end if;
  if now() >= inv.expires_at then
    return jsonb_build_object('ok', false, 'error', 'expired');
  end if;
  if exists (select 1 from profiles where id = v_user) then
    return jsonb_build_object('ok', false, 'error', 'already_linked');
  end if;

  select lower(email) into v_email from auth.users where id = v_user;
  if v_email is null or v_email <> lower(inv.email) then
    return jsonb_build_object('ok', false, 'error', 'email_mismatch');
  end if;

  insert into profiles (id, full_name, roles, contractor_id, worker_id)
  values (v_user,
          coalesce(nullif(trim(p_full_name), ''), inv.email),
          array[inv.role]::prj_role[],
          inv.contractor_id, inv.worker_id);

  update invitations set used_at = now() where id = inv.id;

  return jsonb_build_object('ok', true, 'role', inv.role::text);
end $$;

grant execute on function public.check_invitation(uuid) to anon, authenticated;
grant execute on function public.complete_invitation(uuid, text)
  to anon, authenticated;

-- The app-schema copies from 0003 are superseded by these.
drop function if exists app.check_invitation(uuid);
drop function if exists app.complete_invitation(uuid, text);

insert into schema_migrations (id, name)
values (4, '0004_redeem_rpc_public');
