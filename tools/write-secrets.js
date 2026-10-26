/* Build-time generator for secrets.js.
   Runs during the Vercel build: writes the public-by-design runtime keys
   (Supabase URL + RLS-protected anon key, Web3Forms key) from the
   project's environment variables. Keeps the keys out of the repository
   while making git-triggered deployments self-contained.
   If secrets.js already exists (local development), it is left alone. */
const fs = require('fs');

if (fs.existsSync('secrets.js')) {
  console.log('secrets.js already present; leaving it in place.');
  process.exit(0);
}

const anon = process.env.SUPABASE_ANON_KEY;
const web3 = process.env.WEB3FORMS_KEY;
if (!anon || !web3) {
  console.error('SUPABASE_ANON_KEY and WEB3FORMS_KEY must be set for the build.');
  process.exit(1);
}

fs.writeFileSync('secrets.js', `/* Generated at build time from hosting environment variables. */
window.PRJGENUI = {
  supabaseUrl: 'https://houhfxugjgeyrmkmpvji.supabase.co',
  supabaseAnonKey: '${anon}',
  web3formsKey: '${web3}'
};
`);
console.log('secrets.js generated.');
