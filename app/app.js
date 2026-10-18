/* PRJGENUI Workforce — team platform (Stage 0, slice 2).
   Static app: sign-in via Supabase Auth, profile and roles from the
   database, invitations for Owner and Operations. Everything else is
   refused by row-level security in the database, not by this page. */
(function () {
  'use strict';

  var cfg = window.PRJGENUI_APP || window.PRJGENUI || {};
  var ROLE_LABELS = {
    owner: 'Owner', operations: 'Operations', compliance: 'Compliance',
    contractor: 'Contractor', worker: 'Worker', supplier: 'Supplier',
    auditor: 'Auditor'
  };

  var els = {
    loginView: document.getElementById('login-view'),
    appView: document.getElementById('app-view'),
    loginForm: document.getElementById('login-form'),
    loginError: document.getElementById('login-error'),
    forgot: document.getElementById('forgot'),
    greeting: document.getElementById('greeting'),
    profileLine: document.getElementById('profile-line'),
    noProfile: document.getElementById('no-profile'),
    invitations: document.getElementById('invitations'),
    inviteForm: document.getElementById('invite-form'),
    inviteEmail: document.getElementById('invite-email'),
    inviteRole: document.getElementById('invite-role'),
    inviteStatus: document.getElementById('invite-status'),
    inviteRows: document.getElementById('invite-rows'),
    signout: document.getElementById('signout')
  };

  if (!cfg.supabaseUrl || !cfg.supabaseAnonKey || !window.supabase) {
    // Local preview without keys: show the shell, do nothing else.
    els.loginView.hidden = false;
    els.loginError.hidden = false;
    els.loginError.textContent =
      'Configuration is missing, so sign-in is not available here.';
    return;
  }

  var sb = window.supabase.createClient(cfg.supabaseUrl, cfg.supabaseAnonKey);
  var profile = null;

  function showLogin(message) {
    els.appView.hidden = true;
    els.loginView.hidden = false;
    if (message) {
      els.loginError.hidden = false;
      els.loginError.textContent = message;
    } else {
      els.loginError.hidden = true;
    }
  }

  function render(session) {
    if (session) {
      els.loginView.hidden = true;
      els.appView.hidden = false;
      els.loginError.hidden = true;
      loadProfile(session.user);
    } else {
      profile = null;
      showLogin();
    }
  }

  function roleList(roles) {
    return roles.map(function (r) {
      return ROLE_LABELS[r] || r;
    }).join(', ');
  }

  function loadProfile(user) {
    els.noProfile.hidden = true;
    els.profileLine.textContent = 'Loading your profile…';
    sb.from('profiles')
      .select('id, full_name, roles')
      .eq('id', user.id)
      .maybeSingle()
      .then(function (res) {
        if (!res.data) {
          profile = null;
          els.greeting.textContent = 'Hello';
          els.profileLine.textContent = user.email;
          els.noProfile.hidden = false;
          els.invitations.hidden = true;
          return;
        }
        profile = res.data;
        var first = profile.full_name.split(' ')[0];
        els.greeting.textContent = 'Hello, ' + first;
        els.profileLine.textContent = profile.full_name + ' · ' +
          roleList(profile.roles || []);
        var canInvite = (profile.roles || []).some(function (r) {
          return r === 'owner' || r === 'operations';
        });
        els.invitations.hidden = !canInvite;
        if (canInvite) loadInvitations();
      })
      .catch(function () {
        els.noProfile.hidden = false;
      });
  }

  function fmtDate(iso) {
    if (!iso) return '—';
    return new Date(iso).toLocaleDateString('en-GB',
      { day: 'numeric', month: 'short', year: 'numeric' });
  }

  function loadInvitations() {
    sb.from('invitations')
      .select('id, email, role, expires_at, used_at')
      .order('created_at', { ascending: false })
      .limit(50)
      .then(function (res) {
        els.inviteRows.innerHTML = '';
        (res.data || []).forEach(function (inv) {
          var tr = document.createElement('tr');
          var status;
          if (inv.used_at) status = 'used';
          else if (new Date(inv.expires_at) < new Date()) status = 'expired';
          else status = 'pending';

          [inv.email, ROLE_LABELS[inv.role] || inv.role,
            fmtDate(inv.expires_at), status].forEach(function (text) {
            var td = document.createElement('td');
            td.textContent = text;
            tr.appendChild(td);
          });
          var td = document.createElement('td');
          td.className = 'right';
          if (!inv.used_at) {
            var btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'btn small danger';
            btn.textContent = 'Revoke';
            btn.addEventListener('click', function () { revoke(inv.id); });
            td.appendChild(btn);
          }
          tr.appendChild(td);
          els.inviteRows.appendChild(tr);
        });
      });
  }

  function revoke(id) {
    sb.from('invitations').delete().eq('id', id)
      .then(function () { loadInvitations(); });
  }

  els.loginForm.addEventListener('submit', function (e) {
    e.preventDefault();
    els.loginError.hidden = true;
    var email = document.getElementById('email').value.trim();
    var password = document.getElementById('password').value;
    if (!email || !password) {
      els.loginError.hidden = false;
      els.loginError.textContent = 'Enter your email and password.';
      return;
    }
    sb.auth.signInWithPassword({ email: email, password: password })
      .then(function (res) {
        if (res.error) {
          els.loginError.hidden = false;
          els.loginError.textContent =
            'That email and password did not match an account. ' +
            'Check both and try again.';
        }
      })
      .catch(function () {
        els.loginError.hidden = false;
        els.loginError.textContent =
          'Sign-in could not be reached. Check your connection and try again.';
      });
  });

  els.forgot.addEventListener('click', function () {
    var email = document.getElementById('email').value.trim();
    if (!email) {
      els.loginError.hidden = false;
      els.loginError.textContent = 'Enter your email above first, then try again.';
      return;
    }
    sb.auth.resetPasswordForEmail(email).then(function (res) {
      els.loginError.hidden = false;
      els.loginError.textContent = res.error
        ? 'That request could not be sent. Try again in a little while.'
        : 'If that email has an account, a link to set a new password is on its way.';
    });
  });

  els.inviteForm.addEventListener('submit', function (e) {
    e.preventDefault();
    els.inviteStatus.hidden = true;
    var email = els.inviteEmail.value.trim();
    var role = els.inviteRole.value;
    if (!email) {
      els.inviteStatus.hidden = false;
      els.inviteStatus.textContent = 'Enter an email address.';
      return;
    }
    sb.from('invitations')
      .insert({ email: email, role: role, invited_by: profile.id })
      .then(function (res) {
        if (res.error) {
          els.inviteStatus.hidden = false;
          els.inviteStatus.textContent =
            'The invitation could not be saved. Try again.';
          return;
        }
        els.inviteEmail.value = '';
        els.inviteStatus.hidden = false;
        els.inviteStatus.className = 'ok';
        els.inviteStatus.textContent = 'Invitation saved.';
        loadInvitations();
      });
  });

  els.signout.addEventListener('click', function () {
    sb.auth.signOut();
  });

  sb.auth.getSession().then(function (res) { render(res.data.session); });
  sb.auth.onAuthStateChange(function (_event, session) { render(session); });
})();
