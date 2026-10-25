/* PRJGENUI Workforce — invitation email sender (Vercel serverless).
 *
 * POST /api/email  { kind: 'invitation', token: <invitation uuid> }
 * Authorization: Bearer <the operator's Supabase session token>
 *
 * The function verifies the invitation server-side (it exists, is
 * unused and unexpired) before anything is sent, and the email only
 * ever goes to the address recorded on the invitation — there is no
 * arbitrary-recipient sending.
 *
 * Email goes through the platform sender (system@prjgenuiworkforce.co.uk
 * via Zoho SMTP) once SMTP_* variables are set in the hosting account.
 * Until then the function reports smtp_not_configured and the app keeps
 * its copy-the-link route, which works without any email infrastructure.
 */
const nodemailer = require('nodemailer');

const SUPABASE_URL = 'https://houhfxugjgeyrmkmpvji.supabase.co';
const SITE_ORIGIN = 'https://prjgenuiworkforce.co.uk';

function json(res, code, body) {
  res.statusCode = code;
  res.setHeader('Content-Type', 'application/json');
  res.end(JSON.stringify(body));
}

module.exports = async function (req, res) {
  if (req.method !== 'POST') {
    return json(res, 405, { ok: false, error: 'method_not_allowed' });
  }
  // Same-origin only: the app calls this from prjgenuiworkforce.co.uk.
  const origin = req.headers.origin;
  if (origin && origin !== SITE_ORIGIN) {
    return json(res, 403, { ok: false, error: 'forbidden_origin' });
  }
  const auth = req.headers.authorization || '';
  const jwt = auth.startsWith('Bearer ') ? auth.slice(7) : null;
  if (!jwt) {
    return json(res, 401, { ok: false, error: 'not_signed_in' });
  }

  let body = {};
  try {
    body = typeof req.body === 'string' ? JSON.parse(req.body) : (req.body || {});
  } catch (e) {
    return json(res, 400, { ok: false, error: 'bad_request' });
  }
  if (body.kind !== 'invitation' || !body.token) {
    return json(res, 400, { ok: false, error: 'bad_request' });
  }

  // Verify the invitation with the caller's own session: an invalid
  // session fails here, and the mail only ever goes to the invited
  // address on a valid, unused, unexpired invitation.
  let inv;
  try {
    const r = await fetch(SUPABASE_URL + '/rest/v1/rpc/check_invitation', {
      method: 'POST',
      headers: {
        // The gateway requires the publishable (anon) key as apikey;
        // the caller's session travels in Authorization.
        'apikey': process.env.SUPABASE_ANON_KEY || jwt,
        'Authorization': 'Bearer ' + jwt,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ p_token: body.token })
    });
    if (!r.ok) {
      return json(res, 401, { ok: false, error: 'not_signed_in' });
    }
    const rows = await r.json();
    inv = Array.isArray(rows) ? rows[0] : rows;
  } catch (e) {
    return json(res, 502, { ok: false, error: 'check_failed' });
  }
  if (!inv || !inv.found) {
    return json(res, 404, { ok: false, error: 'invitation_not_found' });
  }
  if (!inv.usable) {
    return json(res, 409, {
      ok: false,
      error: 'invitation_not_usable',
      reason: 'That invitation is already used or expired.'
    });
  }

  const smtp = {
    host: process.env.SMTP_HOST,
    port: parseInt(process.env.SMTP_PORT || '465', 10),
    user: process.env.SMTP_USER,
    pass: process.env.SMTP_PASSWORD,
    from: process.env.SMTP_FROM ||
          'PRJGENUI Workforce <system@prjgenuiworkforce.co.uk>'
  };
  if (!smtp.host || !smtp.user || !smtp.pass) {
    return json(res, 200, {
      ok: false,
      error: 'smtp_not_configured',
      reason: 'Platform email sending is not active yet. Copy the ' +
              'invitation link and send it yourself for now.'
    });
  }

  const link = SITE_ORIGIN + '/app/#invite=' + body.token;
  const mail = {
    from: smtp.from,
    to: inv.email,
    subject: 'Your PRJGENUI Workforce access',
    text:
      'Hello,\n\n' +
      'You have been invited to the PRJGENUI Workforce platform as: ' +
      (inv.role || 'user') + '\n\n' +
      'Open this link to set up your access (it expires on ' +
      new Date(inv.expires_at).toDateString() + '):\n\n' +
      link + '\n\n' +
      'If you were not expecting this invitation, ignore this email.\n\n' +
      'PRJGENUI Workforce\n' +
      'prjgenuiworkforce.co.uk\n',
    html:
      '<p>Hello,</p>' +
      '<p>You have been invited to the PRJGENUI Workforce platform as: ' +
      '<strong>' + (inv.role || 'user') + '</strong></p>' +
      '<p><a href="' + link + '">Set up your access</a></p>' +
      '<p>The link expires on ' + new Date(inv.expires_at).toDateString() +
      '.</p>' +
      '<p>If you were not expecting this invitation, ignore this email.</p>' +
      '<p>PRJGENUI Workforce — prjgenuiworkforce.co.uk</p>'
  };

  try {
    const transport = nodemailer.createTransport({
      host: smtp.host,
      port: smtp.port,
      secure: smtp.port === 465,
      auth: { user: smtp.user, pass: smtp.pass }
    });
    await transport.sendMail(mail);
  } catch (e) {
    return json(res, 502, {
      ok: false,
      error: 'send_failed',
      reason: 'The email could not be sent. Copy the invitation link ' +
              'and send it yourself for now.'
    });
  }

  return json(res, 200, { ok: true, from: smtp.from, to: inv.email });
};
