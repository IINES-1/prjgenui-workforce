/* PRJGENUI Workforce — runtime config endpoint (Vercel serverless).
 *
 * GET /api/secrets  (rewritten from /secrets.js via vercel.json)
 *
 * Serves the public-by-design runtime keys (Supabase URL +
 * RLS-protected anon key, Web3Forms key) from the hosting account's
 * environment variables, so no key ever lives in the repository and
 * deployments are self-contained. Real secrets stay in environment
 * variables only. In local development the gitignored secrets.js file
 * in the repository root serves the same purpose instead.
 */
module.exports = async function (req, res) {
  const anon = process.env.SUPABASE_ANON_KEY;
  const web3 = process.env.WEB3FORMS_KEY;
  if (!anon || !web3) {
    res.statusCode = 500;
    res.setHeader('Content-Type', 'text/plain');
    return res.end('runtime config not configured');
  }
  res.statusCode = 200;
  res.setHeader('Content-Type', 'application/javascript');
  res.setHeader('Cache-Control', 'public, max-age=60');
  res.end(
    '/* Generated at runtime from hosting environment variables. */\n' +
    'window.PRJGENUI = {\n' +
    "  supabaseUrl: 'https://houhfxugjgeyrmkmpvji.supabase.co',\n" +
    "  supabaseAnonKey: '" + anon + "',\n" +
    "  web3formsKey: '" + web3 + "'\n" +
    '};\n'
  );
};
