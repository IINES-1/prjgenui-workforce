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
  var WORKER_STATUS = {
    draft: 'Draft', in_review: 'In review', verified: 'Verified',
    expiring_soon: 'Expiring soon', blocked: 'Blocked', archived: 'Archived'
  };
  var EVIDENCE_STATUS = {
    pending_review: 'Pending review', verified: 'Verified',
    rejected: 'Rejected'
  };
  var ASSIGNMENT_STATUS = {
    proposed: 'Proposed', confirmed: 'Confirmed', completed: 'Completed',
    cancelled: 'Cancelled', legacy_recorded: 'History'
  };
  var RTW_METHODS = {
    home_office_share_code: 'Home Office share code',
    manual_passport: 'Manual passport check'
  };
  var RTW_RESULTS = {
    pass: 'Pass', fail: 'Fail', follow_up_required: 'Follow-up required'
  };
  var QUAL_KINDS = {
    cscs: 'CSCS card', nvq: 'NVQ', city_guilds: 'City & Guilds',
    ipaf: 'IPAF', pasma: 'PASMA'
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
    passport: document.getElementById('passport'),
    passportStatus: document.getElementById('passport-status'),
    passportReason: document.getElementById('passport-reason'),
    rtwCard: document.getElementById('passport-rtw'),
    rtwRows: document.getElementById('rtw-rows'),
    qualsCard: document.getElementById('passport-quals'),
    qualsRows: document.getElementById('quals-rows'),
    evidenceCard: document.getElementById('passport-evidence'),
    evidenceRows: document.getElementById('evidence-rows'),
    readinessCard: document.getElementById('passport-readiness'),
    readinessBox: document.getElementById('readiness-box'),
    assignmentsCard: document.getElementById('passport-assignments'),
    assignRows: document.getElementById('assign-rows'),
    perfCard: document.getElementById('passport-perf'),
    perfLine: document.getElementById('perf-line'),
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

  function hidePassport() {
    els.passport.hidden = true;
  }

  function badge(status, label) {
    var cls = 'badge';
    if (status === 'verified' || status === 'pass' || status === 'completed') cls += ' ok';
    else if (status === 'blocked' || status === 'rejected' || status === 'fail') cls += ' bad';
    else if (status === 'expiring_soon' || status === 'pending_review' ||
             status === 'follow_up_required') cls += ' warn';
    return '<span class="' + cls + '">' + label + '</span>';
  }

  function miniTable(rows, headers) {
    if (!rows.length) return '<p class="footnote">Nothing recorded yet.</p>';
    var html = '<table><thead><tr>';
    headers.forEach(function (h) { html += '<th>' + h + '</th>'; });
    html += '</tr></thead><tbody>';
    rows.forEach(function (cells) {
      html += '<tr>';
      cells.forEach(function (c) { html += '<td>' + c + '</td>'; });
      html += '</tr>';
    });
    return html + '</tbody></table>';
  }

  function loadPassport(workerId) {
    els.passport.hidden = false;

    sb.from('workers').select('passport_no, full_name, trade, status, status_reason')
      .eq('id', workerId).maybeSingle()
      .then(function (res) {
        var w = res.data;
        if (!w) {
          els.passportStatus.textContent = 'Your record is being set up by the team.';
          return;
        }
        els.passportStatus.innerHTML = (w.passport_no ? w.passport_no + ' · ' : '') +
          (w.trade ? w.trade + ' · ' : '') + badge(w.status, WORKER_STATUS[w.status] || w.status);
        if ((w.status === 'blocked' || w.status === 'archived') && w.status_reason) {
          els.passportReason.hidden = false;
          els.passportReason.textContent = 'Reason: ' + w.status_reason;
        } else {
          els.passportReason.hidden = true;
        }
      });

    sb.from('rtw_checks')
      .select('method, check_date, result, restrictions, follow_up_due')
      .eq('worker_id', workerId).order('check_date', { ascending: false })
      .then(function (res) {
        var rows = (res.data || []).map(function (c) {
          return [fmtDate(c.check_date),
            RTW_METHODS[c.method] || c.method,
            badge(c.result, RTW_RESULTS[c.result] || c.result),
            c.restrictions || '—',
            c.follow_up_due ? 'Follow-up by ' + fmtDate(c.follow_up_due) : '—'];
        });
        els.rtwRows.innerHTML = '';
        els.rtwCard.hidden = false;
        els.rtwRows.innerHTML = miniTable(rows,
          ['Checked', 'Method', 'Result', 'Restrictions', 'Next']);
      });

    var quals = [];
    sb.from('qualifications')
      .select('kind, number, status, expiry_date')
      .eq('worker_id', workerId)
      .then(function (res) {
        (res.data || []).forEach(function (q) {
          quals.push({
            label: QUAL_KINDS[q.kind] || q.kind,
            number: q.number, status: q.status,
            expiry: q.expiry_date ? fmtDate(q.expiry_date) : '—'
          });
        });
        return sb.from('training_certificates')
          .select('training_type, status, expiry_date')
          .eq('worker_id', workerId);
      })
      .then(function (res) {
        (res.data || []).forEach(function (t) {
          quals.push({
            label: (t.training_type || '').replace(/_/g, ' '),
            number: null, status: t.status,
            expiry: t.expiry_date ? fmtDate(t.expiry_date) : '—'
          });
        });
        quals.sort(function (a, b) { return (a.expiry || '') < (b.expiry || '') ? -1 : 1; });
        els.qualsRows.innerHTML = '';
        els.qualsCard.hidden = false;
        els.qualsRows.innerHTML = miniTable(quals.map(function (q) {
          return [q.label, q.number || '—',
            badge(q.status, EVIDENCE_STATUS[q.status] || q.status), q.expiry];
        }), ['Card or training', 'Number', 'Status', 'Expires']);
      });

    var evidence = [];
    sb.from('proof_of_work')
      .select('skill, supervisor, status')
      .eq('worker_id', workerId)
      .then(function (res) {
        (res.data || []).forEach(function (p) {
          evidence.push([p.skill + (p.supervisor ? ' (supervisor: ' + p.supervisor + ')' : ''),
            badge(p.status, EVIDENCE_STATUS[p.status] || p.status)]);
        });
        return sb.from('work_history')
          .select('period_start, period_end, description')
          .eq('worker_id', workerId).order('period_start', { ascending: false });
      })
      .then(function (res) {
        (res.data || []).forEach(function (h) {
          evidence.push([(h.period_start ? fmtDate(h.period_start) : '—') +
            ' – ' + (h.period_end ? fmtDate(h.period_end) : 'ongoing'),
            h.description || '—']);
        });
        els.evidenceRows.innerHTML = '';
        els.evidenceCard.hidden = false;
        els.evidenceRows.innerHTML = miniTable(evidence, ['What', 'Detail']);
      });

    sb.from('readiness_evaluations')
      .select('outcome, blockers, rules_version, created_at')
      .eq('worker_id', workerId).order('created_at', { ascending: false }).limit(1)
      .then(function (res) {
        els.readinessBox.innerHTML = '';
        var ev = (res.data || [])[0];
        if (!ev) {
          els.readinessCard.hidden = false;
          els.readinessBox.innerHTML = '<p class="footnote">No readiness check has been run yet.</p>';
          return;
        }
        var html = '<p class="profile-line">' + badge(ev.outcome,
          ev.outcome === 'pass' ? 'Ready' : 'Blocked') +
          ' — checked ' + fmtDate(ev.created_at) +
          ' (rules ' + ev.rules_version + ')</p>';
        var blockers = ev.blockers || [];
        if (blockers.length) {
          html += '<ul class="blockers">';
          blockers.forEach(function (b) {
            html += '<li>' + (b.reason || b.code) +
              (b.mandatory ? ' (required for this job)' : '') + '</li>';
          });
          html += '</ul>';
        }
        els.readinessCard.hidden = false;
        els.readinessBox.innerHTML = html;
      });

    sb.from('assignments')
      .select('trade, start_date, end_date, status')
      .eq('worker_id', workerId).order('created_at', { ascending: false }).limit(20)
      .then(function (res) {
        els.assignRows.innerHTML = '';
        els.assignmentsCard.hidden = false;
        els.assignRows.innerHTML = miniTable((res.data || []).map(function (a) {
          return [a.trade || '—', fmtDate(a.start_date), fmtDate(a.end_date),
            badge(a.status, ASSIGNMENT_STATUS[a.status] || a.status)];
        }), ['Trade', 'Start', 'End', 'Status']);
      });

    sb.from('performance_scores')
      .select('score, band, weights_version')
      .eq('worker_id', workerId).maybeSingle()
      .then(function (res) {
        els.perfCard.hidden = false;
        var s = res.data;
        els.perfLine.textContent = s && s.score !== null
          ? 'Performance record: ' + s.score + (s.band ? ' (' + s.band + ')' : '') +
            ', weights ' + s.weights_version
          : 'Not yet scored — the record builds from completed assignments and feedback.';
      });
  }

  function loadProfile(user) {
    els.noProfile.hidden = true;
    els.profileLine.textContent = 'Loading your profile…';
    sb.from('profiles')
      .select('id, full_name, roles, worker_id')
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
        if (profile.worker_id) {
          loadPassport(profile.worker_id);
        } else if ((profile.roles || []).indexOf('worker') !== -1) {
          els.passport.hidden = false;
          els.passportStatus.textContent = 'Your worker record is being set up by the team.';
          els.passportReason.hidden = true;
        } else {
          hidePassport();
        }
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
