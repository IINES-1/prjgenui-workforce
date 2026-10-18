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
    redeemView: document.getElementById('redeem-view'),
    appView: document.getElementById('app-view'),
    loginForm: document.getElementById('login-form'),
    loginError: document.getElementById('login-error'),
    forgot: document.getElementById('forgot'),
    showRedeem: document.getElementById('show-redeem'),
    backToLogin: document.getElementById('back-to-login'),
    redeemForm: document.getElementById('redeem-form'),
    redeemInfo: document.getElementById('redeem-info'),
    redeemEmail: document.getElementById('redeem-email'),
    redeemPassword: document.getElementById('redeem-password'),
    redeemToken: document.getElementById('redeem-token'),
    redeemStatus: document.getElementById('redeem-status'),
    greeting: document.getElementById('greeting'),
    profileLine: document.getElementById('profile-line'),
    noProfile: document.getElementById('no-profile'),
    finishForm: document.getElementById('finish-form'),
    finishToken: document.getElementById('finish-token'),
    finishStatus: document.getElementById('finish-status'),
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
    els.redeemView.hidden = true;
    els.loginView.hidden = false;
    if (message) {
      els.loginError.hidden = false;
      els.loginError.textContent = message;
    } else {
      els.loginError.hidden = true;
    }
  }

  function showRedeem() {
    els.appView.hidden = true;
    els.loginView.hidden = true;
    els.redeemView.hidden = false;
    els.redeemStatus.hidden = true;
  }

  function render(session) {
    if (session) {
      els.loginView.hidden = true;
      els.redeemView.hidden = true;
      els.appView.hidden = false;
      els.loginError.hidden = true;
      loadProfile(session.user);
    } else {
      profile = null;
      // Leave the redeem view alone: an invitee may be mid-flow when
      // the initial (signed-out) session event arrives.
      if (els.redeemView.hidden) showLogin();
    }
  }

  function roleList(roles) {
    return roles.map(function (r) {
      return ROLE_LABELS[r] || r;
    }).join(', ');
  }

  function completeInvitation(token, statusEl, after) {
    sb.rpc('complete_invitation', { p_token: token })
      .then(function (res) {
        var r = res.data || {};
        if (!r.ok) {
          statusEl.hidden = false;
          statusEl.className = 'error';
          statusEl.textContent = {
            not_found: 'That invitation code is not recognised.',
            already_used: 'That invitation has already been used.',
            expired: 'That invitation has expired. Ask for a new one.',
            email_mismatch: 'This invitation was issued to a different email address.',
            already_linked: 'Your account is already linked.'
          }[r.error] || 'The invitation could not be completed. Try again or ask for a new one.';
          return;
        }
        statusEl.hidden = false;
        statusEl.className = 'ok';
        statusEl.textContent = 'Your access is set up.';
        if (after) after();
      })
      .catch(function () {
        statusEl.hidden = false;
        statusEl.className = 'error';
        statusEl.textContent = 'The invitation could not be completed right now. Try again.';
      });
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
          // A just-confirmed invitee: finish their setup automatically.
          var stashed = null;
          try { stashed = sessionStorage.getItem('prjgenui_invite'); } catch (e) {}
          if (stashed) {
            try { sessionStorage.removeItem('prjgenui_invite'); } catch (e) {}
            completeInvitation(stashed, els.finishStatus, function () {
              loadProfile(user);
            });
          }
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
      .select('id, email, role, token, expires_at, used_at')
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
            var copy = document.createElement('button');
            copy.type = 'button';
            copy.className = 'btn small';
            copy.textContent = 'Copy link';
            copy.addEventListener('click', function () {
              var link = location.origin + '/app/#invite=' + inv.token;
              if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(link).then(function () {
                  copy.textContent = 'Copied';
                  setTimeout(function () { copy.textContent = 'Copy link'; }, 2000);
                });
              } else {
                window.prompt('Copy this link and send it to ' + inv.email + ':', link);
              }
            });
            td.appendChild(copy);
            var revoke = document.createElement('button');
            revoke.type = 'button';
            revoke.className = 'btn small danger';
            revoke.textContent = 'Revoke';
            revoke.addEventListener('click', function () { revokeInvitation(inv.id); });
            td.appendChild(revoke);
          }
          tr.appendChild(td);
          els.inviteRows.appendChild(tr);
        });
      });
  }

  function revokeInvitation(id) {
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

  els.showRedeem.addEventListener('click', function () {
    showRedeem();
  });
  els.backToLogin.addEventListener('click', function () {
    showLogin();
  });

  els.redeemForm.addEventListener('submit', function (e) {
    e.preventDefault();
    els.redeemStatus.hidden = true;
    var email = els.redeemEmail.value.trim();
    var password = els.redeemPassword.value;
    var token = els.redeemToken.value.trim();
    if (!email || !password || !token) {
      els.redeemStatus.hidden = false;
      els.redeemStatus.className = 'error';
      els.redeemStatus.textContent =
        'Enter your email, a password and the invitation code.';
      return;
    }
    if (password.length < 8) {
      els.redeemStatus.hidden = false;
      els.redeemStatus.className = 'error';
      els.redeemStatus.textContent = 'Choose a password of at least 8 characters.';
      return;
    }
    sb.auth.signUp({ email: email, password: password })
      .then(function (res) {
        if (res.error) {
          els.redeemStatus.hidden = false;
          els.redeemStatus.className = 'error';
          els.redeemStatus.textContent =
            res.error.message &&
            res.error.message.indexOf('already registered') !== -1
              ? 'An account already exists for this email. Sign in with your ' +
                'password instead, then finish setup with the code.'
              : 'The account could not be created. ' +
                'Check the email address and try again.';
          return;
        }
        try { sessionStorage.setItem('prjgenui_invite', token); } catch (e) {}
        els.redeemStatus.hidden = false;
        els.redeemStatus.className = 'ok';
        if (res.data && res.data.session) {
          els.redeemStatus.textContent = 'Account created — finishing setup…';
        } else {
          els.redeemStatus.textContent =
            'Account created. Check your email to confirm your address, ' +
            'then sign in here — your access will finish setting up on its own.';
        }
      })
      .catch(function () {
        els.redeemStatus.hidden = false;
        els.redeemStatus.className = 'error';
        els.redeemStatus.textContent =
          'The account could not be created right now. Try again in a moment.';
      });
  });

  els.finishForm.addEventListener('submit', function (e) {
    e.preventDefault();
    els.finishStatus.hidden = true;
    var token = els.finishToken.value.trim();
    if (!token) {
      els.finishStatus.hidden = false;
      els.finishStatus.textContent = 'Enter your invitation code.';
      return;
    }
    completeInvitation(token, els.finishStatus, function () {
      sb.auth.getSession().then(function (res) {
        if (res.data && res.data.session) loadProfile(res.data.session.user);
      });
    });
  });

  els.signout.addEventListener('click', function () {
    sb.auth.signOut();
  });

  // Opening an invitation link: /app/#invite=<token>
  (function () {
    var m = (location.hash + '&' + location.search)
      .match(/invite=([0-9a-f-]{36})/i);
    if (!m) return;
    var token = m[1];
    showRedeem();
    sb.rpc('check_invitation', { p_token: token })
      .then(function (res) {
        var r = (res.data || [])[0];
        if (!r || !r.found) {
          els.redeemInfo.textContent =
            'This invitation link is not recognised. Ask for a new one.';
          els.redeemToken.value = token;
          return;
        }
        if (!r.usable) {
          els.redeemInfo.textContent =
            'This invitation has expired or was already used. Ask for a new one.';
          els.redeemToken.value = token;
          return;
        }
        els.redeemInfo.textContent = 'You have been invited as ' +
          (ROLE_LABELS[r.role] || r.role) + ' for ' + r.email +
          '. Set a password to create your account.';
        els.redeemEmail.value = r.email;
        els.redeemToken.value = token;
        els.redeemPassword.focus();
      });
  })();

  sb.auth.getSession().then(function (res) { render(res.data.session); });
  sb.auth.onAuthStateChange(function (_event, session) { render(session); });
})();
