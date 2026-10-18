-- PRJGENUI Workforce — Supabase schema
-- Run this in the Supabase SQL Editor (Dashboard > SQL > New query)
-- after creating a free project at supabase.com.

-- 1. Table -----------------------------------------------------------
create table if not exists public.kv (
  key   text primary key,
  value jsonb
);

-- 2. Row Level Security ---------------------------------------------
alter table public.kv enable row level security;

-- Allow anonymous reads (the dashboard only uses the anon key,
-- so we scope policies to the anon role).
create policy "anon can read kv"
  on public.kv
  for select
  to anon
  using (true);

-- Allow anonymous inserts / updates (upserts).
create policy "anon can write kv"
  on public.kv
  for insert
  to anon
  with check (true);

create policy "anon can update kv"
  on public.kv
  for update
  to anon
  using (true)
  with check (true);

-- Allow anonymous deletes.
create policy "anon can delete kv"
  on public.kv
  for delete
  to anon
  using (true);

-- 3. Helpful index ---------------------------------------------------
create index if not exists kv_key_idx on public.kv (key);
