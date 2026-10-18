# Supabase setup — PRJGENUI Workforce dashboard

The dashboard reads its credentials at runtime from `secrets.js` in the
project root. That file is **deployed** to the site but **never committed**
to the repository (it is listed in `.gitignore`), so the repo stays clean.

## Steps

1. **Sign up** at [supabase.com](https://supabase.com) (free plan, 500 MB, plenty for this).

2. **Create a new project.** Pick a name like `prjgenui-workforce`, choose the EU region (Frankfurt), and set a database password you'll remember. Record the database password somewhere safe — it cannot be recovered from the project.

3. **Run the SQL schema.** In the Supabase dashboard, go to **SQL Editor → New query**, paste the contents of `supabase_schema.sql`, and click **Run**. This creates the `kv` table and sets the permissions the dashboard needs.

4. **Copy your credentials.** Go to **Settings → API**:
   - Copy the **Project URL** (looks like `https://abcdefgh.supabase.co`)
   - Copy the **anon public** key (the long `eyJ...` string)

5. **Fill in `secrets.js`** in the project root. It looks like this:

   ```js
   window.PRJGENUI = {
     supabaseUrl: 'https://yourproject.supabase.co',   // ← paste Project URL
     supabaseAnonKey: 'eyJhbGciOi...',                 // ← paste anon key
     web3formsKey: 'your Web3Forms access key'
   };
   ```

   `dashboard.html` reads its Supabase credentials from this file, and the
   website forms get their Web3Forms key from it too. If the file is missing
   or empty, the dashboard falls back to browser storage and the forms will
   not send.

6. **Deploy** (`vercel --prod`) and open the dashboard. It reads `secrets.js`
   and uses Supabase instead of browser storage. Data persists across
   devices and browsers.

## How it works

Until the production platform replaces it, the dashboard stores workers,
crews and settings as key-value pairs in a single `kv` table. The `value`
column is JSON, so the structure is flexible.

Row Level Security is enabled but allows anonymous read/write, because the
dashboard is an internal tool with no login yet. When authentication is
added in Stage 0, the RLS policies are tightened and Supabase Auth is turned
on — that is the first job of the production build.

The anon key in `secrets.js` is public-by-design (it ships in the page either
way and the database is protected by RLS). Never put the service-role key or
the database password in `secrets.js`, in the repo, or in any page.
