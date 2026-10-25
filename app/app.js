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
    proposed: 'Proposed', offered: 'Offered', accepted: 'Accepted',
    confirmed: 'Confirmed', active: 'Active', completed: 'Completed',
    cancelled: 'Cancelled', no_show: 'No show', replaced: 'Replaced',
    legacy_recorded: 'History'
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
  var FACTOR_LABELS = {
    worker_verified: 'Worker record', rtw_current: 'Right to Work',
    trade_match: 'Trade', working_at_height: 'Working at height',
    manual_handling: 'Manual handling'
  };
  function factorLabel(code) {
    return FACTOR_LABELS[code] || QUAL_KINDS[code] ||
      (code || '').replace(/_/g, ' ').replace(/\b\w/g, function (c) {
        return c.toUpperCase();
      });
  }
  var REQUEST_STATUS = {
    open: 'Open', matched: 'Matched', offered: 'Offered',
    filled: 'Filled', closed: 'Closed'
  };
  var ASSIGN_STATUS = {
    proposed: 'Proposed', offered: 'Offered', accepted: 'Accepted',
    confirmed: 'Confirmed', active: 'Active', completed: 'Completed',
    cancelled: 'Cancelled', no_show: 'No show', replaced: 'Replaced',
    legacy_recorded: 'Legacy'
  };
  var BLOCKER_ACTIONS = {
    rtw_missing: 'Verify via share code, manual check or Employer Checking Service',
    rtw_not_pass: 'Verify via share code, manual check or Employer Checking Service',
    rtw_followup_overdue: 'Verify via share code, manual check or Employer Checking Service',
    worker_not_verified: 'Mark verified once evidence is checked, not before',
    cscs_expired: 'Verify via CSCS Smart Check',
    cscs_missing: 'Verify via CSCS Smart Check'
  };
  var ITEM_TABLE_LABELS = {
    qualifications: 'qualification', training_certificates: 'training certificate',
    rtw_checks: 'Right to Work follow-up'
  };
  var ASSIGN_BADGE = {
    proposed: 'pending', offered: 'pending', accepted: 'pending',
    confirmed: 'pass', active: 'verified', completed: 'verified',
    cancelled: 'fail', no_show: 'fail', replaced: 'fail',
    legacy_recorded: 'pending'
  };
  var ATTEND_OUTCOME = {
    attended: 'Attended', late: 'Late', no_show: 'No show',
    excused: 'Excused', not_recorded: 'Not recorded'
  };
  var ATTEND_STATUS = {
    verified: 'Recorded', disputed: 'Disputed', corrected: 'Corrected'
  };
  var INCIDENT_TYPE = {
    cancellation: 'Cancellation', no_show: 'No show',
    replacement_required: 'Replacement required'
  };
  var currentRequest = null;

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
    mfaView: document.getElementById('mfa-view'),
    mfaTitle: document.getElementById('mfa-title'),
    mfaLede: document.getElementById('mfa-lede'),
    mfaQr: document.getElementById('mfa-qr'),
    mfaSecretLine: document.getElementById('mfa-secret-line'),
    mfaSecret: document.getElementById('mfa-secret'),
    mfaForm: document.getElementById('mfa-form'),
    mfaCode: document.getElementById('mfa-code'),
    mfaStatus: document.getElementById('mfa-status'),
    mfaSignout: document.getElementById('mfa-signout'),
    invitations: document.getElementById('invitations'),
    inviteForm: document.getElementById('invite-form'),
    inviteEmail: document.getElementById('invite-email'),
    inviteRole: document.getElementById('invite-role'),
    inviteContractorField: document.getElementById('invite-contractor-field'),
    inviteContractor: document.getElementById('invite-contractor'),
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
    workersPanel: document.getElementById('workers-panel'),
    workersRows: document.getElementById('workers-rows'),
    crewsPanel: document.getElementById('crews-panel'),
    crewsToolbar: document.getElementById('crews-toolbar'),
    crewsCount: document.getElementById('crews-count'),
    crewsTable: document.getElementById('crews-table'),
    crewsRows: document.getElementById('crews-rows'),
    crewsStatus: document.getElementById('crews-status'),
    addCrewBtn: document.getElementById('add-crew-btn'),
    crewFormCard: document.getElementById('crew-form-card'),
    crewFormTitle: document.getElementById('crew-form-title'),
    crewForm: document.getElementById('crew-form'),
    crewFormStatus: document.getElementById('crew-form-status'),
    crName: document.getElementById('cr-name'),
    crSpecialism: document.getElementById('cr-specialism'),
    crSupervisor: document.getElementById('cr-supervisor'),
    crMembers: document.getElementById('cr-members'),
    crNotes: document.getElementById('cr-notes'),
    deployRows: document.getElementById('deploy-rows'),
    addDeployBtn: document.getElementById('add-deploy-btn'),
    deleteCrewBtn: document.getElementById('delete-crew-btn'),
    cancelCrewBtn: document.getElementById('cancel-crew-btn'),
    addWorkerForm: document.getElementById('add-worker-form'),
    addWorkerStatus: document.getElementById('add-worker-status'),
    workerDetail: document.getElementById('worker-detail'),
    wdTitle: document.getElementById('wd-title'),
    wdStatusLine: document.getElementById('wd-status-line'),
    wdReason: document.getElementById('wd-reason'),
    wdReasonInput: document.getElementById('wd-reason-input'),
    wdActions: document.getElementById('wd-actions'),
    wdAdvance: document.getElementById('wd-advance'),
    wdBlock: document.getElementById('wd-block'),
    wdArchive: document.getElementById('wd-archive'),
    wdInvite: document.getElementById('wd-invite'),
    wdActionStatus: document.getElementById('wd-action-status'),
    wdInviteLink: document.getElementById('wd-invite-link'),
    wdClose: document.getElementById('wd-close'),
    wdRtw: document.getElementById('wd-rtw'),
    wdReadinessBox: document.getElementById('wd-readiness-box'),
    wdReadinessActions: document.getElementById('wd-readiness-actions'),
    wdReadiness: document.getElementById('wd-readiness'),
    wdReadinessStatus: document.getElementById('wd-readiness-status'),
    rtwForm: document.getElementById('rtw-form'),
    rtwStatus: document.getElementById('rtw-status'),
    wdQuals: document.getElementById('wd-quals'),
    qualForm: document.getElementById('qual-form'),
    qualStatus: document.getElementById('qual-status'),
    requestsPanel: document.getElementById('requests-panel'),
    requestForm: document.getElementById('request-form'),
    requestStatus: document.getElementById('request-status'),
    requestRows: document.getElementById('request-rows'),
    contractorForm: document.getElementById('contractor-form'),
    contractorStatus: document.getElementById('contractor-status'),
    contractorDetails: document.getElementById('contractor-details'),
    rqContractor: document.getElementById('rq-contractor'),
    matchesView: document.getElementById('matches-view'),
    matchesTitle: document.getElementById('matches-title'),
    matchesSummary: document.getElementById('matches-summary'),
    matchesRows: document.getElementById('matches-rows'),
    matchesClose: document.getElementById('matches-close'),
    assignmentsPanel: document.getElementById('assignments-panel'),
    assignmentRows: document.getElementById('assignment-rows'),
    assignmentStatus: document.getElementById('assignment-status'),
    attendancePanel: document.getElementById('attendance-panel'),
    atAssignment: document.getElementById('at-assignment'),
    atDate: document.getElementById('at-date'),
    atOutcome: document.getElementById('at-outcome'),
    atSource: document.getElementById('at-source'),
    atNote: document.getElementById('at-note'),
    attendanceForm: document.getElementById('attendance-form'),
    attendanceStatus: document.getElementById('attendance-status'),
    attendanceRows: document.getElementById('attendance-rows'),
    resolveDisputeForm: document.getElementById('resolve-dispute-form'),
    resolveDisputeTitle: document.getElementById('resolve-dispute-title'),
    rdResolution: document.getElementById('rd-resolution'),
    rdOutcome: document.getElementById('rd-outcome'),
    rdNote: document.getElementById('rd-note'),
    resolveDisputeStatus: document.getElementById('resolve-dispute-status'),
    incidentsPanel: document.getElementById('incidents-panel'),
    inAssignment: document.getElementById('in-assignment'),
    inType: document.getElementById('in-type'),
    inNotes: document.getElementById('in-notes'),
    incidentForm: document.getElementById('incident-form'),
    incidentStatus: document.getElementById('incident-status'),
    incidentRows: document.getElementById('incident-rows'),
    incidentDetail: document.getElementById('incident-detail'),
    incidentDetailTitle: document.getElementById('incident-detail-title'),
    incidentDetailLine: document.getElementById('incident-detail-line'),
    iaDecision: document.getElementById('ia-decision'),
    iaNotes: document.getElementById('ia-notes'),
    iaReplacement: document.getElementById('ia-replacement'),
    incidentActionStatus: document.getElementById('incident-action-status'),
    contractorPanel: document.getElementById('contractor-panel'),
    contractorTitle: document.getElementById('contractor-title'),
    contractorLine: document.getElementById('contractor-line'),
    coRequestRows: document.getElementById('co-request-rows'),
    coAssignmentRows: document.getElementById('co-assignment-rows'),
    coAttendanceRows: document.getElementById('co-attendance-rows'),
    coStatements: document.getElementById('co-statements'),
    passportAttendance: document.getElementById('passport-attendance'),
    passportAttendanceRows: document.getElementById('passport-attendance-rows'),
    passportAttendanceStatus: document.getElementById('passport-attendance-status'),
    actionCentre: document.getElementById('action-centre'),
    acSummary: document.getElementById('ac-summary'),
    acGroups: document.getElementById('ac-groups'),
    acStatus: document.getElementById('ac-status'),
    recomputeBtn: document.getElementById('recompute-btn'),
    outcomeForm: document.getElementById('outcome-form'),
    outcomeTitle: document.getElementById('outcome-title'),
    outcomeStatus: document.getElementById('outcome-status'),
    outcomeCancel: document.getElementById('outcome-cancel'),
    ratesForm: document.getElementById('rates-form'),
    ratesTitle: document.getElementById('rates-title'),
    ratesStatus: document.getElementById('rates-status'),
    rtPay: document.getElementById('rt-pay'),
    rtCharge: document.getElementById('rt-charge'),
    ratesCancel: document.getElementById('rates-cancel'),
    remindersBtn: document.getElementById('reminders-btn'),
    acReminders: document.getElementById('ac-reminders'),
    statementView: document.getElementById('statement-view'),
    statementTitle: document.getElementById('statement-title'),
    statementBody: document.getElementById('statement-body'),
    statementGenerate: document.getElementById('statement-generate'),
    statementStatus: document.getElementById('statement-status'),
    statementClose: document.getElementById('statement-close'),
    pricesPanel: document.getElementById('prices-panel'),
    priceForm: document.getElementById('price-form'),
    priceStatus: document.getElementById('price-status'),
    priceRows: document.getElementById('price-rows'),
    prContractor: document.getElementById('pr-contractor'),
    subscriptionForm: document.getElementById('subscription-form'),
    subscriptionStatus: document.getElementById('subscription-status'),
    subscriptionRows: document.getElementById('subscription-rows'),
    ssContractor: document.getElementById('ss-contractor'),
    costForm: document.getElementById('cost-form'),
    costStatus: document.getElementById('cost-status'),
    costRows: document.getElementById('cost-rows'),
    overrideForm: document.getElementById('override-form'),
    overrideStatus: document.getElementById('override-status'),
    overrideRows: document.getElementById('wd-overrides-rows'),
    overridesCard: document.getElementById('wd-overrides-card'),
    documentsCard: document.getElementById('wd-documents-card'),
    documentRows: document.getElementById('wd-doc-rows'),
    passportReminders: document.getElementById('passport-reminders'),
    remindersRows: document.getElementById('reminders-rows'),
    remindersLine: document.getElementById('reminders-line'),
    passportDetails: document.getElementById('passport-details'),
    selfDetailsForm: document.getElementById('self-details-form'),
    selfDetailsStatus: document.getElementById('self-details-status'),
    passportDocuments: document.getElementById('passport-documents'),
    selfDocRows: document.getElementById('self-doc-rows'),
    selfDocForm: document.getElementById('self-doc-form'),
    selfDocStatus: document.getElementById('self-doc-status'),
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

  // Two-factor (TOTP) for admin accounts. Owner, Operations and
  // Compliance see worker data, so they must pass a second factor
  // (an authenticator app code) before the dashboard unlocks.
  var MFA_ROLES = ['owner', 'operations', 'compliance'];
  var mfaPassed = false;
  var mfaFactor = null;
  var mfaChallengeId = null;

  function showLogin(message) {
    els.appView.hidden = true;
    els.redeemView.hidden = true;
    els.mfaView.hidden = true;
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
    els.mfaView.hidden = true;
    els.redeemView.hidden = false;
    els.redeemStatus.hidden = true;
  }

  function mfaSetStatus(ok, text) {
    els.mfaStatus.hidden = false;
    els.mfaStatus.className = ok ? 'ok' : 'error';
    els.mfaStatus.textContent = text;
  }

  function mfaStartChallenge() {
    return sb.auth.mfa.challenge({ factorId: mfaFactor.id })
      .then(function (res) {
        if (res.error) throw res.error;
        mfaChallengeId = res.data.id;
      });
  }

  function mfaEnroll() {
    els.mfaTitle.textContent = 'Set up two-factor';
    els.mfaLede.textContent =
      'Admin accounts need an authenticator app (Google Authenticator, ' +
      'Microsoft Authenticator or similar). Scan the code with the app, ' +
      'then enter the 6-digit code it shows.';
    els.mfaQr.hidden = false;
    els.mfaSecretLine.hidden = false;
    els.mfaCode.value = '';
    els.mfaStatus.hidden = true;
    sb.auth.mfa.enroll({ factorType: 'totp', friendlyName: 'PRJGENUI Workforce' })
      .then(function (res) {
        if (res.error) {
          mfaSetStatus(false, 'Two-factor setup could not start. ' +
            'Sign out and try again.');
          return;
        }
        mfaFactor = res.data;
        var totp = res.data.totp || {};
        els.mfaQr.innerHTML = totp.qr_code || '';
        els.mfaSecret.textContent = totp.secret || '';
        mfaStartChallenge().catch(function () {
          mfaSetStatus(false, 'Could not start verification. Try again.');
        });
      });
  }

  function mfaChallengeExisting(factor) {
    els.mfaTitle.textContent = 'Two-factor verification';
    els.mfaLede.textContent =
      'Enter the 6-digit code from your authenticator app.';
    els.mfaQr.hidden = true;
    els.mfaQr.innerHTML = '';
    els.mfaSecretLine.hidden = true;
    els.mfaCode.value = '';
    els.mfaStatus.hidden = true;
    mfaFactor = factor;
    mfaStartChallenge().catch(function () {
      mfaSetStatus(false, 'Could not start verification. Try again.');
    });
  }

  function mfaGate(user) {
    els.appView.hidden = true;
    els.mfaView.hidden = false;
    sb.auth.mfa.getAuthenticatorAssuranceLevel()
      .then(function (res) {
        if (res.error || !res.data) {
          mfaSetStatus(false, 'Could not check two-factor status. Try again.');
          return;
        }
        if (res.data.currentLevel === 'aal2') {
          mfaPassed = true;
          els.mfaView.hidden = true;
          els.appView.hidden = false;
          loadProfile(user);
          return;
        }
        sb.auth.mfa.listFactors().then(function (fres) {
          var verified = ((fres.data && fres.data.totp) || []).filter(
            function (f) { return f.status === 'verified'; });
          if (verified.length) mfaChallengeExisting(verified[0]);
          else mfaEnroll();
        });
      });
  }

  els.mfaForm.addEventListener('submit', function (e) {
    e.preventDefault();
    var code = (els.mfaCode.value || '').replace(/\s+/g, '');
    if (!/^\d{6}$/.test(code)) {
      mfaSetStatus(false, 'Enter the 6-digit code from your app.');
      return;
    }
    if (!mfaFactor || !mfaChallengeId) {
      mfaSetStatus(false, 'Verification is not ready yet. Try again in a moment.');
      return;
    }
    sb.auth.mfa.verify({
      factorId: mfaFactor.id,
      challengeId: mfaChallengeId,
      code: code
    }).then(function (res) {
      if (res.error) {
        if (/expired/i.test(res.error.message || '')) {
          mfaStartChallenge().then(function () {
            mfaSetStatus(false, 'That code took too long. Enter a fresh one.');
          });
        } else {
          mfaSetStatus(false, 'That code was not accepted. Check the app and try again.');
        }
        return;
      }
      mfaPassed = true;
      mfaChallengeId = null;
      els.mfaView.hidden = true;
      els.appView.hidden = false;
      sb.auth.getSession().then(function (sres) {
        var u = sres.data && sres.data.session && sres.data.session.user;
        if (u) loadProfile(u);
      });
    });
  });

  els.mfaSignout.addEventListener('click', function () {
    mfaPassed = false;
    mfaFactor = null;
    mfaChallengeId = null;
    sb.auth.signOut();
    showLogin();
  });

  function render(session) {
    if (session) {
      els.loginView.hidden = true;
      els.redeemView.hidden = true;
      els.appView.hidden = false;
      els.loginError.hidden = true;
      loadProfile(session.user);
    } else {
      profile = null;
      mfaPassed = false;
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

    sb.from('workers')
      .select('passport_no, full_name, phone, email, trade, availability, status, status_reason')
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
        loadSelfDetails(w);
      });
    loadWorkerReminders(workerId);
    loadSelfDocuments(workerId);

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
      .select('kind, number, status, expiry_date, validity')
      .eq('worker_id', workerId)
      .then(function (res) {
        (res.data || []).forEach(function (q) {
          quals.push({
            label: QUAL_KINDS[q.kind] || q.kind,
            number: q.number, status: q.status,
            expiry: q.expiry_date ? fmtDate(q.expiry_date) :
              (q.validity === 'permanent' ? 'Permanent' : '—')
          });
        });
        return sb.from('training_certificates')
          .select('training_type, status, expiry_date, validity')
          .eq('worker_id', workerId);
      })
      .then(function (res) {
        (res.data || []).forEach(function (t) {
          quals.push({
            label: (t.training_type || '').replace(/_/g, ' '),
            number: null, status: t.status,
            expiry: t.expiry_date ? fmtDate(t.expiry_date) :
              (t.validity === 'permanent' ? 'Permanent' : '—')
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

    // The worker's own attendance evidence, with the dispute right. A
    // dispute goes to the team for review; the original stays on record.
    sb.from('attendance_evidence')
      .select('id, shift_date, outcome, status, note, ' +
              'assignments(public_reference, trade)')
      .eq('worker_id', workerId)
      .order('shift_date', { ascending: false }).limit(20)
      .then(function (res) {
        els.passportAttendance.hidden = false;
        els.passportAttendanceRows.innerHTML = '';
        (res.data || []).forEach(function (ev) {
          var tr = document.createElement('tr');
          var a = ev.assignments || {};
          [(a.public_reference || a.trade || 'Assignment'),
           fmtDate(ev.shift_date),
           ATTEND_OUTCOME[ev.outcome] || ev.outcome,
           badge(ev.status === 'verified' ? 'verified'
             : ev.status === 'disputed' ? 'pending_review' : 'pass',
             ATTEND_STATUS[ev.status] || ev.status)].forEach(function (t) {
            var td = document.createElement('td');
            td.textContent = t === null || t === undefined ? '—' : t;
            tr.appendChild(td);
          });
          var td = document.createElement('td');
          if (ev.status !== 'disputed') {
            var btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'btn small';
            btn.textContent = 'Dispute';
            btn.addEventListener('click', function () {
              var note = window.prompt(
                'What is wrong with this attendance record? ' +
                'The team will review it; the original stays on record.',
                '');
              if (note === null) return;
              sb.rpc('dispute_attendance_evidence',
                     { p_evidence_id: ev.id, p_note: note })
                .then(function (r) {
                  var d = r.data || {};
                  if (!d.ok) {
                    showActionStatus(els.passportAttendanceStatus, false,
                      d.reason || 'The dispute could not be raised.');
                    return;
                  }
                  showActionStatus(els.passportAttendanceStatus, true,
                    'Dispute raised. The team must review it before the ' +
                    'record changes.');
                  loadPassport(workerId);
                });
            });
            td.appendChild(btn);
          }
          tr.appendChild(td);
          els.passportAttendanceRows.appendChild(tr);
        });
      });
  }

  function showActionStatus(el, ok, message) {
    el.hidden = false;
    el.className = ok ? 'ok' : 'error';
    el.textContent = message;
  }

  function friendlyDbError(err) {
    var msg = (err && err.message) || '';
    msg = msg.replace(/^.*?:\s*/, '');
    if (msg.indexOf('row-level security') !== -1) {
      return 'Your role is not permitted to do that.';
    }
    return msg || 'That change was not accepted. Check the details and try again.';
  }

  var currentWorker = null;
  var workersCache = [];
  var canWriteWorkers = false;
  var canRecordEvidence = false;
  var canRunReadiness = false;
  var canManageRequests = false;
  var canSeeWorkerDocs = false;
  var canGiveFeedback = false;
  var canSeeCrews = false;
  var canWriteCrews = false;

  var NEXT_STATUS = { draft: 'in_review', in_review: 'verified' };

  function renderReadiness(ev) {
    if (!ev) {
      els.wdReadinessBox.innerHTML =
        '<p class="footnote">No readiness check has been run yet.</p>';
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
          (b.mandatory ? ' (required)' : '') + '</li>';
      });
      html += '</ul>';
    }
    els.wdReadinessBox.innerHTML = html;
  }

  function loadWorkerReadiness(id) {
    sb.from('readiness_evaluations')
      .select('outcome, blockers, rules_version, created_at')
      .eq('worker_id', id).order('created_at', { ascending: false }).limit(1)
      .then(function (res) {
        renderReadiness((res.data || [])[0]);
      });
  }

  function runReadiness() {
    if (!currentWorker) return;
    showActionStatus(els.wdReadinessStatus, true, 'Running the check…');
    sb.rpc('evaluate_readiness', { p_worker_id: currentWorker.id })
      .then(function (res) {
        var r = res.data || {};
        if (!r.ok) {
          showActionStatus(els.wdReadinessStatus, false, {
            not_signed_in: 'Your sign-in has expired — sign in again.',
            not_permitted: 'Your role cannot run readiness checks.',
            worker_not_found: 'That worker record no longer exists.'
          }[r.error] || 'The check could not be run. Try again.');
          return;
        }
        showActionStatus(els.wdReadinessStatus, true,
          r.outcome === 'pass'
            ? 'Ready — no blockers.'
            : 'Blocked — every blocker above needs resolving.');
        loadWorkerReadiness(currentWorker.id);
      })
      .catch(function () {
        showActionStatus(els.wdReadinessStatus, false,
          'The check could not be run right now. Try again.');
      });
  }

  els.wdReadiness.addEventListener('click', runReadiness);

  function loadWorkers() {
    sb.from('workers')
      .select('id, passport_no, full_name, trade, status')
      .order('updated_at', { ascending: false })
      .limit(100)
      .then(function (res) {
        els.workersRows.innerHTML = '';
        workersCache = res.data || [];
        workersCache.forEach(function (w) {
          var tr = document.createElement('tr');
          [w.passport_no || '—', w.full_name, w.trade || '—'].forEach(function (t) {
            var td = document.createElement('td');
            td.textContent = t;
            tr.appendChild(td);
          });
          var tdStatus = document.createElement('td');
          tdStatus.innerHTML = badge(w.status, WORKER_STATUS[w.status] || w.status);
          tr.appendChild(tdStatus);
          var td = document.createElement('td');
          td.className = 'right';
          var btn = document.createElement('button');
          btn.type = 'button';
          btn.className = 'btn small';
          btn.textContent = 'Open';
          btn.addEventListener('click', function () { openWorker(w.id); });
          td.appendChild(btn);
          tr.appendChild(td);
          els.workersRows.appendChild(tr);
        });
      });
  }

  function openWorker(id) {
    currentWorker = null;
    els.workerDetail.hidden = false;
    els.wdInviteLink.hidden = true;
    els.wdActionStatus.hidden = true;
    els.wdReadinessStatus.hidden = true;
    els.wdReasonInput.value = '';
    sb.from('workers').select('*').eq('id', id).maybeSingle()
      .then(function (res) {
        currentWorker = res.data;
        renderWorkerDetail();
        loadWorkerEvidence(id);
        loadWorkerReadiness(id);
        loadWorkerOverrides(id);
        if (canSeeWorkerDocs) loadWorkerDocuments(id);
        els.workerDetail.scrollIntoView({ behavior: 'smooth' });
      });
  }

  function renderWorkerDetail() {
    var w = currentWorker;
    if (!w) return;
    els.wdTitle.textContent = w.full_name;
    els.wdStatusLine.innerHTML =
      (w.passport_no ? w.passport_no + ' · ' : '') +
      (w.trade ? w.trade + ' · ' : '') +
      badge(w.status, WORKER_STATUS[w.status] || w.status) +
      ' — contact: ' + (w.email || w.phone || 'not recorded');
    if ((w.status === 'blocked' || w.status === 'archived') && w.status_reason) {
      els.wdReason.hidden = false;
      els.wdReason.textContent = 'Reason: ' + w.status_reason;
    } else {
      els.wdReason.hidden = true;
    }
    els.wdAdvance.hidden = !canWriteWorkers || !NEXT_STATUS[w.status];
    els.wdInvite.hidden = !canWriteWorkers || !w.email;
  }

  function loadWorkerEvidence(id) {
    sb.from('rtw_checks')
      .select('method, check_date, result, restrictions, follow_up_due, source')
      .eq('worker_id', id).order('check_date', { ascending: false })
      .then(function (res) {
        els.wdRtw.innerHTML = miniTable((res.data || []).map(function (c) {
          return [fmtDate(c.check_date),
            RTW_METHODS[c.method] || c.method,
            badge(c.result, RTW_RESULTS[c.result] || c.result),
            c.source || '—',
            c.follow_up_due ? 'Follow-up by ' + fmtDate(c.follow_up_due) : '—'];
        }), ['Checked', 'Method', 'Result', 'Source', 'Next']);
      });

    var quals = [];
    sb.from('qualifications')
      .select('id, kind, number, status, expiry_date, validity')
      .eq('worker_id', id)
      .then(function (res) {
        (res.data || []).forEach(function (q) {
          quals.push({ id: q.id, table: 'qualifications',
            label: QUAL_KINDS[q.kind] || (q.kind || '').replace(/_/g, ' '),
            number: q.number, status: q.status,
            expiry: q.expiry_date ? fmtDate(q.expiry_date) :
              (q.validity === 'permanent' ? 'Permanent' : '—') });
        });
        return sb.from('training_certificates')
          .select('id, training_type, status, expiry_date, validity')
          .eq('worker_id', id);
      })
      .then(function (res) {
        (res.data || []).forEach(function (t) {
          quals.push({ id: t.id, table: 'training_certificates',
            label: (t.training_type || '').replace(/_/g, ' '),
            number: null, status: t.status,
            expiry: t.expiry_date ? fmtDate(t.expiry_date) :
              (t.validity === 'permanent' ? 'Permanent' : '—') });
        });
        quals.sort(function (a, b) { return (a.expiry || '') < (b.expiry || '') ? -1 : 1; });
        if (!quals.length) {
          els.wdQuals.innerHTML = '<p class="footnote">Nothing recorded yet.</p>';
          return;
        }
        var html = '<table><thead><tr><th>Card or training</th><th>Number</th>' +
          '<th>Status</th><th>Expires</th><th></th></tr></thead><tbody>';
        quals.forEach(function (q) {
          html += '<tr><td>' + q.label + '</td><td>' + (q.number || '—') + '</td><td>' +
            badge(q.status, EVIDENCE_STATUS[q.status] || q.status) +
            '</td><td>' + q.expiry + '</td><td class="right">';
          if (canRecordEvidence) {
            if (q.status === 'pending_review') {
              html += '<button type="button" class="btn small" data-verify="' +
                q.table + ':' + q.id + '">Verify</button> ';
            }
            if (q.status !== 'rejected') {
              html += '<button type="button" class="btn small danger" data-reject="' +
                q.table + ':' + q.id + '">Reject</button>';
            }
          }
          html += '</td></tr>';
        });
        els.wdQuals.innerHTML = html + '</tbody></table>';
        Array.prototype.forEach.call(
          els.wdQuals.querySelectorAll('button[data-verify]'), function (b) {
            b.addEventListener('click', function () {
              setEvidenceStatus(b.getAttribute('data-verify').split(':'), 'verified');
            });
          });
        Array.prototype.forEach.call(
          els.wdQuals.querySelectorAll('button[data-reject]'), function (b) {
            b.addEventListener('click', function () {
              setEvidenceStatus(b.getAttribute('data-reject').split(':'), 'rejected');
            });
          });
      });
  }

  function setEvidenceStatus(parts, status) {
    var table = parts[0], id = parts[1];
    sb.from(table).update({ status: status }).eq('id', id)
      .then(function (res) {
        if (res.error) {
          showActionStatus(els.qualStatus, false, friendlyDbError(res.error));
          return;
        }
        els.qualStatus.hidden = true;
        loadWorkerEvidence(currentWorker.id);
      });
  }

  function changeWorkerStatus(target) {
    var reason = els.wdReasonInput.value.trim();
    var patch = { status: target };
    if (target === 'blocked' || target === 'archived') patch.status_reason = reason;
    sb.from('workers').update(patch).eq('id', currentWorker.id)
      .then(function (res) {
        if (res.error) {
          showActionStatus(els.wdActionStatus, false, friendlyDbError(res.error));
          return;
        }
        showActionStatus(els.wdActionStatus, true,
          target === 'blocked' || target === 'archived'
            ? 'Status set to ' + (WORKER_STATUS[target] || target) + '.'
            : 'Status advanced to ' + (WORKER_STATUS[target] || target) + '.');
        currentWorker.status = target;
        currentWorker.status_reason = patch.status_reason || null;
        renderWorkerDetail();
        loadWorkers();
      });
  }

  function inviteCurrentWorker() {
    sb.from('invitations')
      .insert({ email: currentWorker.email, role: 'worker',
                worker_id: currentWorker.id, invited_by: profile.id })
      .select('token, expires_at')
      .then(function (res) {
        if (res.error) {
          showActionStatus(els.wdActionStatus, false, friendlyDbError(res.error));
          return;
        }
        var inv = (res.data || [])[0];
        var link = location.origin + '/app/#invite=' + inv.token;
        showActionStatus(els.wdActionStatus, true, 'Invitation saved.');
        els.wdInviteLink.hidden = false;
        els.wdInviteLink.textContent = 'Send this link to ' + currentWorker.email +
          ' (expires ' + fmtDate(inv.expires_at) + '): ' + link;
        loadInvitations();
      });
  }

  els.addWorkerForm.addEventListener('submit', function (e) {
    e.preventDefault();
    els.addWorkerStatus.hidden = true;
    var name = document.getElementById('w-name').value.trim();
    if (!name) {
      showActionStatus(els.addWorkerStatus, false, 'Enter the full name.');
      return;
    }
    sb.from('workers').insert({
      full_name: name,
      trade: document.getElementById('w-trade').value.trim() || null,
      email: document.getElementById('w-email').value.trim() || null
    }).then(function (res) {
      if (res.error) {
        showActionStatus(els.addWorkerStatus, false, friendlyDbError(res.error));
        return;
      }
      document.getElementById('w-name').value = '';
      document.getElementById('w-trade').value = '';
      document.getElementById('w-email').value = '';
      showActionStatus(els.addWorkerStatus, true, 'Worker record created as a draft.');
      loadWorkers();
    });
  });

  els.wdClose.addEventListener('click', function () {
    els.workerDetail.hidden = true;
    currentWorker = null;
  });
  els.wdAdvance.addEventListener('click', function () {
    if (currentWorker && NEXT_STATUS[currentWorker.status]) {
      changeWorkerStatus(NEXT_STATUS[currentWorker.status]);
    }
  });
  els.wdBlock.addEventListener('click', function () { changeWorkerStatus('blocked'); });
  els.wdArchive.addEventListener('click', function () { changeWorkerStatus('archived'); });
  els.wdInvite.addEventListener('click', inviteCurrentWorker);

  /* ------------- Crews (register 2.5 and 5.4; the approved
     dashboard's crew model, unchanged) ------------- */

  var currentCrew = null;

  function crewConfidence(count) {
    if (count === 0) return badge('new', 'New crew');
    if (count < 3) return badge('pending_review', 'Limited evidence');
    return badge('pass', 'Proven crew');
  }

  function loadCrews() {
    sb.from('crews')
      .select('id, name, specialism, supervisor_id, notes')
      .order('created_at', { ascending: false })
      .limit(100)
      .then(function (res) {
        if (res.error) {
          showActionStatus(els.crewsStatus, false, friendlyDbError(res.error));
          return;
        }
        var crews = res.data || [];
        sb.from('crew_members').select('crew_id, worker_id').limit(2000)
          .then(function (rm) {
            var members = rm.data || [];
            return sb.from('crew_deployments')
              .select('id, crew_id, deploy_date, client, project, worked_well')
              .order('deploy_date', { ascending: false })
              .limit(2000)
              .then(function (rd) {
                renderCrews(crews, members, rd.data || []);
              });
          });
      });
  }

  function renderCrews(crews, members, deployments) {
    els.crewsCount.textContent = crews.length +
      (crews.length === 1 ? ' crew' : ' crews') +
      ' with a working history together.';
    els.crewsTable.hidden = crews.length === 0;
    els.crewsRows.innerHTML = '';
    crews.forEach(function (c) {
      var memberIds = members.filter(function (m) { return m.crew_id === c.id; })
        .map(function (m) { return m.worker_id; });
      var deps = deployments.filter(function (d) { return d.crew_id === c.id; });
      var worked = deps.filter(function (d) { return d.worked_well; }).length;
      var pct = deps.length
        ? Math.round(worked / deps.length * 100) + '% worked well' : 'New';
      var entry = { crew: c, members: memberIds, deployments: deps };
      var tr = document.createElement('tr');
      [c.name, String(memberIds.length), c.specialism || '—'].forEach(function (t) {
        var td = document.createElement('td');
        td.textContent = t;
        tr.appendChild(td);
      });
      var tdE = document.createElement('td');
      tdE.innerHTML = crewConfidence(deps.length) +
        ' <span class="profile-line">' + pct + '</span>';
      tr.appendChild(tdE);
      var td = document.createElement('td');
      td.className = 'right';
      if (canWriteCrews) {
        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'btn small';
        btn.textContent = 'Edit';
        btn.addEventListener('click', function () { openCrewForm(entry); });
        td.appendChild(btn);
      }
      tr.appendChild(td);
      els.crewsRows.appendChild(tr);
    });
  }

  function crewWorkerOptions(select, selectedIds, includeNone) {
    select.innerHTML = '';
    if (includeNone) {
      var o = document.createElement('option');
      o.value = '';
      o.textContent = 'None set';
      select.appendChild(o);
    }
    workersCache.forEach(function (w) {
      var opt = document.createElement('option');
      opt.value = w.id;
      opt.textContent = w.full_name +
        (w.trade ? ' · ' + w.trade : '') +
        (w.passport_no ? ' · ' + w.passport_no : '');
      if (selectedIds && selectedIds.indexOf(w.id) !== -1) opt.selected = true;
      select.appendChild(opt);
    });
    if (!workersCache.length && !includeNone) {
      var hint = document.createElement('option');
      hint.value = '';
      hint.textContent = 'Add workers first, then build a crew from them.';
      select.appendChild(hint);
    }
  }

  function addDeployRow(d) {
    var tr = document.createElement('tr');
    function cell(child) {
      var td = document.createElement('td');
      td.appendChild(child);
      tr.appendChild(td);
    }
    var date = document.createElement('input');
    date.type = 'date';
    date.className = 'cd-date';
    if (d && d.deploy_date) date.value = d.deploy_date;
    cell(date);
    var client = document.createElement('input');
    client.type = 'text';
    client.className = 'cd-client';
    client.placeholder = 'Client';
    if (d && d.client) client.value = d.client;
    cell(client);
    var project = document.createElement('input');
    project.type = 'text';
    project.className = 'cd-project';
    project.placeholder = 'Project';
    if (d && d.project) project.value = d.project;
    cell(project);
    var worked = document.createElement('select');
    worked.className = 'cd-worked';
    [['', '—'], ['yes', 'Worked well'], ['no', 'Problems']].forEach(function (pair) {
      var opt = document.createElement('option');
      opt.value = pair[0];
      opt.textContent = pair[1];
      worked.appendChild(opt);
    });
    if (d && d.worked_well === true) worked.value = 'yes';
    if (d && d.worked_well === false) worked.value = 'no';
    cell(worked);
    var rm = document.createElement('button');
    rm.type = 'button';
    rm.className = 'btn small danger';
    rm.textContent = 'Remove';
    rm.addEventListener('click', function () { tr.remove(); });
    cell(rm);
    els.deployRows.appendChild(tr);
  }

  function openCrewForm(entry) {
    currentCrew = entry ? entry.crew : null;
    els.crewFormStatus.hidden = true;
    els.crewFormTitle.textContent = entry ? 'Edit crew' : 'Add crew';
    els.deleteCrewBtn.hidden = !entry;
    els.crName.value = entry ? entry.crew.name : '';
    els.crSpecialism.value = entry ? (entry.crew.specialism || '') : '';
    els.crNotes.value = entry ? (entry.crew.notes || '') : '';
    crewWorkerOptions(els.crSupervisor,
      entry && entry.crew.supervisor_id ? [entry.crew.supervisor_id] : [], true);
    crewWorkerOptions(els.crMembers, entry ? entry.members : [], false);
    els.deployRows.innerHTML = '';
    if (entry) entry.deployments.forEach(addDeployRow);
    els.crewFormCard.hidden = false;
    els.crewFormCard.scrollIntoView({ behavior: 'smooth' });
  }

  els.addCrewBtn.addEventListener('click', function () { openCrewForm(null); });
  els.cancelCrewBtn.addEventListener('click', function () {
    els.crewFormCard.hidden = true;
    currentCrew = null;
  });
  els.addDeployBtn.addEventListener('click', function () { addDeployRow(null); });

  els.deleteCrewBtn.addEventListener('click', function () {
    if (!currentCrew) return;
    if (!window.confirm('Delete this crew? This cannot be undone.')) return;
    sb.from('crews').delete().eq('id', currentCrew.id)
      .then(function (res) {
        if (res.error) {
          showActionStatus(els.crewFormStatus, false, friendlyDbError(res.error));
          return;
        }
        els.crewFormCard.hidden = true;
        currentCrew = null;
        showActionStatus(els.crewsStatus, true, 'Crew deleted.');
        loadCrews();
      });
  });

  els.crewForm.addEventListener('submit', function (e) {
    e.preventDefault();
    els.crewFormStatus.hidden = true;
    var name = els.crName.value.trim();
    if (!name) {
      showActionStatus(els.crewFormStatus, false, 'Enter the crew name.');
      return;
    }
    var memberIds = Array.prototype.map.call(
      els.crMembers.selectedOptions || [], function (o) { return o.value; })
      .filter(function (v) { return v; });
    var deployments = Array.prototype.map.call(
      els.deployRows.querySelectorAll('tr'), function (row) {
        return {
          deploy_date: row.querySelector('.cd-date').value || null,
          client: row.querySelector('.cd-client').value.trim() || null,
          project: row.querySelector('.cd-project').value.trim() || null,
          worked_well: row.querySelector('.cd-worked').value === ''
            ? null : row.querySelector('.cd-worked').value === 'yes'
        };
      }).filter(function (d) { return d.deploy_date || d.client || d.project; });
    var crew = {
      name: name,
      specialism: els.crSpecialism.value.trim() || null,
      supervisor_id: els.crSupervisor.value || null,
      notes: els.crNotes.value.trim() || null
    };
    var save = currentCrew
      ? sb.from('crews').update(crew).eq('id', currentCrew.id).select('id')
      : sb.from('crews').insert(crew).select('id');
    save.then(function (res) {
      if (res.error) {
        showActionStatus(els.crewFormStatus, false, friendlyDbError(res.error));
        return;
      }
      var id = (res.data || [])[0].id;
      sb.from('crew_members').delete().eq('crew_id', id)
        .then(function () {
          if (!memberIds.length) return null;
          return sb.from('crew_members').insert(memberIds.map(function (wid) {
            return { crew_id: id, worker_id: wid };
          }));
        })
        .then(function () {
          return sb.from('crew_deployments').delete().eq('crew_id', id);
        })
        .then(function () {
          if (!deployments.length) return null;
          return sb.from('crew_deployments').insert(deployments.map(function (d) {
            return {
              crew_id: id,
              deploy_date: d.deploy_date,
              client: d.client,
              project: d.project,
              worked_well: d.worked_well
            };
          }));
        })
        .then(function (r) {
          if (r && r.error) {
            showActionStatus(els.crewFormStatus, false, friendlyDbError(r.error));
            return;
          }
          els.crewFormCard.hidden = true;
          currentCrew = null;
          showActionStatus(els.crewsStatus, true, 'Crew saved.');
          loadCrews();
        });
    });
  });


  els.rtwForm.addEventListener('submit', function (e) {
    e.preventDefault();
    els.rtwStatus.hidden = true;
    var date = document.getElementById('rtw-date').value;
    if (!date) {
      showActionStatus(els.rtwStatus, false, 'Enter the check date.');
      return;
    }
    sb.from('rtw_checks').insert({
      worker_id: currentWorker.id,
      method: document.getElementById('rtw-method').value,
      check_date: date,
      result: document.getElementById('rtw-result').value,
      follow_up_due: document.getElementById('rtw-followup').value || null,
      source: document.getElementById('rtw-source').value.trim() || 'recorded in platform'
    }).then(function (res) {
      if (res.error) {
        showActionStatus(els.rtwStatus, false, friendlyDbError(res.error));
        return;
      }
      els.rtwStatus.hidden = true;
      document.getElementById('rtw-followup').value = '';
      document.getElementById('rtw-source').value = '';
      loadWorkerEvidence(currentWorker.id);
    });
  });

  els.qualForm.addEventListener('submit', function (e) {
    e.preventDefault();
    els.qualStatus.hidden = true;
    var type = document.getElementById('qual-type').value.trim();
    if (!type || !currentWorker) {
      showActionStatus(els.qualStatus, false, 'Enter the card or training type.');
      return;
    }
    var slug = type.toLowerCase().replace(/\s+/g, '_');
    var category = document.getElementById('qual-category').value;
    var validity = document.getElementById('qual-validity').value || 'expiring';
    var expiry = document.getElementById('qual-expiry').value || null;
    if (validity === 'permanent') expiry = null;
    var payload = {
      worker_id: currentWorker.id,
      validity: validity,
      expiry_date: expiry
    };
    var table;
    if (category === 'training') {
      table = 'training_certificates';
      payload.training_type = slug;
    } else {
      table = 'qualifications';
      payload.kind = slug;
      payload.number = document.getElementById('qual-number').value.trim() || null;
    }
    sb.from(table).insert(payload).then(function (res) {
      if (res.error) {
        showActionStatus(els.qualStatus, false, friendlyDbError(res.error));
        return;
      }
      els.qualStatus.hidden = true;
      document.getElementById('qual-type').value = '';
      document.getElementById('qual-number').value = '';
      document.getElementById('qual-expiry').value = '';
      document.getElementById('qual-validity').value = 'expiring';
      loadWorkerEvidence(currentWorker.id);
    });
  });

  function loadContractors() {
    return sb.from('contractors')
      .select('id, legal_name')
      .order('legal_name')
      .limit(100)
      .then(function (res) {
        [els.rqContractor, els.prContractor, els.ssContractor,
         els.inviteContractor].forEach(function (sel) {
          if (!sel) return;
          var keep = sel.value;
          var placeholder = sel.options[0] && sel.options[0].value === ''
            ? sel.options[0].textContent : 'Choose…';
          sel.innerHTML = '<option value="">' + placeholder + '</option>';
          (res.data || []).forEach(function (c) {
            var o = document.createElement('option');
            o.value = c.id;
            o.textContent = c.legal_name;
            sel.appendChild(o);
          });
          if (keep && Array.prototype.some.call(sel.options, function (o) {
            return o.value === keep;
          })) sel.value = keep;
        });
      });
  }

  els.contractorForm.addEventListener('submit', function (e) {
    e.preventDefault();
    els.contractorStatus.hidden = true;
    var name = document.getElementById('co-name').value.trim();
    if (!name) {
      showActionStatus(els.contractorStatus, false, 'Enter the company name.');
      return;
    }
    sb.from('contractors').insert({
      legal_name: name,
      contact_name: document.getElementById('co-contact').value.trim() || null,
      phone: document.getElementById('co-phone').value.trim() || null,
      email: document.getElementById('co-email').value.trim() || null
    }).then(function (res) {
      if (res.error) {
        showActionStatus(els.contractorStatus, false, friendlyDbError(res.error));
        return;
      }
      els.contractorStatus.hidden = true;
      document.getElementById('co-name').value = '';
      document.getElementById('co-contact').value = '';
      document.getElementById('co-phone').value = '';
      document.getElementById('co-email').value = '';
      loadContractors().then(function () {
        var opts = els.rqContractor.options;
        for (var i = 0; i < opts.length; i++) {
          if (opts[i].textContent === name) {
            els.rqContractor.value = opts[i].value;
            break;
          }
        }
      });
    });
  });

  function loadRequests() {
    sb.from('workforce_requests')
      .select('id, public_reference, trade, number_needed, start_date, urgent, status, contractor_id')
      .order('created_at', { ascending: false })
      .limit(50)
      .then(function (res) {
        els.requestRows.innerHTML = '';
        (res.data || []).forEach(function (r) {
          var tr = document.createElement('tr');
          [r.public_reference || '—', r.trade, r.number_needed,
            fmtDate(r.start_date)].forEach(function (t) {
            var td = document.createElement('td');
            td.textContent = t;
            tr.appendChild(td);
          });
          var tdS = document.createElement('td');
          tdS.innerHTML = (r.urgent ? '<span class="badge bad">Urgent</span> ' : '') +
            badge(r.status === 'open' ? 'pending' : 'pass',
              REQUEST_STATUS[r.status] || r.status);
          tr.appendChild(tdS);
          var td = document.createElement('td');
          td.className = 'right';
          if (canManageRequests) {
            var run = document.createElement('button');
            run.type = 'button';
            run.className = 'btn small';
            run.textContent = 'Run matching';
            run.addEventListener('click', function () { runMatching(r); });
            td.appendChild(run);
            td.appendChild(document.createTextNode(' '));
          }
          var view = document.createElement('button');
          view.type = 'button';
          view.className = 'btn small ghost';
          view.textContent = 'View matches';
          view.addEventListener('click', function () { loadMatches(r); });
          td.appendChild(view);
          tr.appendChild(td);
          els.requestRows.appendChild(tr);
        });
      });
  }

  function runMatching(r) {
    sb.rpc('generate_matches', { p_request_id: r.id })
      .then(function (res) {
        var d = res.data || {};
        if (!d.ok) {
          showActionStatus(els.requestStatus, false, {
            not_signed_in: 'Your sign-in has expired — sign in again.',
            not_permitted: 'Your role cannot run matching.',
            request_not_found: 'That request no longer exists.',
            request_not_open: 'Matching has run for this request; it is ' +
              (REQUEST_STATUS[r.status] || r.status) + '.'
          }[d.error] || 'Matching could not run. Try again.');
          return;
        }
        showActionStatus(els.requestStatus, true,
          d.put_forward > 0
            ? d.put_forward + ' worker' + (d.put_forward === 1 ? '' : 's') +
              ' put forward; ' + d.held + ' held back.'
            : 'No worker currently meets every requirement.');
        loadRequests();
        loadMatches(r);
      })
      .catch(function () {
        showActionStatus(els.requestStatus, false,
          'Matching could not run right now. Try again.');
      });
  }

  function loadMatches(r) {
    currentRequest = r;
    els.matchesView.hidden = false;
    els.matchesTitle.textContent = 'Matches — ' +
      (r.public_reference || r.trade);
    sb.from('match_generations')
      .select('id, rules_version, created_at')
      .eq('request_id', r.id).order('created_at', { ascending: false }).limit(1)
      .then(function (res) {
        var gen = (res.data || [])[0];
        if (!gen) {
          els.matchesSummary.textContent = 'No matching run yet for this request.';
          els.matchesRows.innerHTML = '';
          return;
        }
        els.matchesSummary.textContent = 'Generated ' + fmtDate(gen.created_at) +
          ' (rules ' + gen.rules_version + ')';
        return sb.from('matches')
          .select('id, decision, rank, factors, workers(id, full_name, passport_no, trade)')
          .eq('generation_id', gen.id)
          .order('rank', { ascending: false, nullsFirst: false });
      })
      .then(function (res) {
        if (!res) return;
        var rows = (res.data || []);
        els.matchesRows.innerHTML = '';
        rows.forEach(function (m) {
          var w = m.workers || {};
          var div = document.createElement('div');
          div.className = 'match';
          var head = document.createElement('p');
          head.className = 'profile-line';
          head.innerHTML = (w.passport_no ? w.passport_no + ' · ' : '') +
            (w.full_name || 'Worker') +
            (m.rank
              ? ' ' + badge('pass', 'Put forward #' + m.rank)
              : ' ' + badge('fail', 'Held back')) +
            (m.decision === 'approved'
              ? ' ' + badge('verified', 'Approved match')
              : '');
          if (m.rank && canManageRequests && w.id) {
            if (m.decision !== 'approved') {
              var approve = document.createElement('button');
              approve.type = 'button';
              approve.className = 'btn small';
              approve.textContent = 'Approve match';
              approve.addEventListener('click', function () {
                sb.from('matches')
                  .update({ decision: 'approved', decided_by: profile.id,
                            decided_at: new Date().toISOString() })
                  .eq('id', m.id)
                  .then(function (r) {
                    if (r.error) {
                      showActionStatus(els.matchesSummary, false,
                        friendlyDbError(r.error));
                      return;
                    }
                    loadMatches(currentRequest);
                  });
              });
              head.appendChild(document.createTextNode(' '));
              head.appendChild(approve);
            } else {
              var offer = document.createElement('button');
              offer.type = 'button';
              offer.className = 'btn small';
              offer.textContent = 'Send offer';
              offer.addEventListener('click', function () { sendOffer(w); });
              head.appendChild(document.createTextNode(' '));
              head.appendChild(offer);
            }
          }
          div.appendChild(head);
          var tbl = document.createElement('table');
          tbl.innerHTML = '<thead><tr><th>Factor</th><th>Result</th><th>Reason</th></tr></thead><tbody>' +
            (m.factors || []).map(function (f) {
              return '<tr><td>' + factorLabel(f.code) + '</td><td>' +
                badge(f.result === 'pass' ? 'verified' :
                  f.result === 'review' ? 'pending_review' : 'fail',
                  f.result === 'pass' ? 'Pass' :
                  f.result === 'review' ? 'Review' : 'Fail') +
                '</td><td>' + (f.reason || '—') + '</td></tr>';
            }).join('') + '</tbody>';
          div.appendChild(tbl);
          els.matchesRows.appendChild(div);
        });
        els.matchesView.scrollIntoView({ behavior: 'smooth' });
      });
  }

  els.requestForm.addEventListener('submit', function (e) {
    e.preventDefault();
    els.requestStatus.hidden = true;
    var trade = document.getElementById('rq-trade').value.trim();
    var number = parseInt(document.getElementById('rq-number').value, 10);
    var contractorId = els.rqContractor.value;
    if (!contractorId) {
      showActionStatus(els.requestStatus, false,
        'Choose the contractor making the request (add one first if needed).');
      return;
    }
    if (!trade || !number || number < 1) {
      showActionStatus(els.requestStatus, false,
        'Enter the trade and the number of workers needed.');
      return;
    }
    var reqs = Array.prototype.map.call(
      document.querySelectorAll('#rq-requirements input:checked'),
      function (c) { return c.value; });
    sb.from('workforce_requests').insert({
      contractor_id: contractorId,
      trade: trade,
      number_needed: number,
      start_date: document.getElementById('rq-start').value || null,
      duration: document.getElementById('rq-duration').value.trim() || null,
      urgent: document.getElementById('rq-urgent').checked,
      essential_requirements: reqs
    }).then(function (res) {
      if (res.error) {
        showActionStatus(els.requestStatus, false, friendlyDbError(res.error));
        return;
      }
      els.requestStatus.hidden = true;
      document.getElementById('rq-trade').value = '';
      document.getElementById('rq-start').value = '';
      document.getElementById('rq-duration').value = '';
      document.getElementById('rq-urgent').checked = false;
      Array.prototype.forEach.call(
        document.querySelectorAll('#rq-requirements input'),
        function (c) { c.checked = false; });
      loadRequests();
    });
  });

  els.matchesClose.addEventListener('click', function () {
    els.matchesView.hidden = true;
  });

  /* The offer flow (the only route the app creates assignments): an
     approved match becomes an offer and its assignment at 'offered' in
     one recorded operator action. The database refuses anything that is
     not an approved match, and a second live offer for the same worker
     and request. */

  function sendOffer(w) {
    if (!currentRequest) return;
    els.matchesSummary.hidden = false;
    sb.rpc('create_assignment_from_match',
           { p_request_id: currentRequest.id, p_worker_id: w.id })
      .then(function (res) {
        var d = res.data || {};
        if (!d.ok) {
          showActionStatus(els.matchesSummary, false,
            d.reason || ({
              no_approved_match: 'Only an approved match can be offered.',
              already_offered: 'This worker already has a live offer for this request.'
            })[d.error] || 'The offer could not be created.');
          return;
        }
        showActionStatus(els.matchesSummary, true,
          'Offer created for ' + (w.full_name || 'the worker') +
          '. Record their answer in the assignments panel.');
        loadRequests();
        loadAssignments();
      });
  }

  /* Assignment rates (register 6.4): records only, kept as in the
     dashboard. Billing on top waits for the employment-law opinion. */

  var ratesAssignment = null;

  function openRates(a) {
    ratesAssignment = a;
    els.ratesForm.hidden = false;
    els.ratesStatus.hidden = true;
    els.ratesTitle.textContent = 'Assignment rates — ' +
      (a.public_reference || '') + ' · ' +
      ((a.workers || {}).full_name || 'worker');
    els.rtPay.value = a.worker_pay_rate || '';
    els.rtCharge.value = a.client_charge_rate || '';
    els.ratesForm.scrollIntoView({ behavior: 'smooth' });
  }

  els.ratesCancel.addEventListener('click', function () {
    els.ratesForm.hidden = true;
    ratesAssignment = null;
  });

  els.ratesForm.addEventListener('submit', function (e) {
    e.preventDefault();
    if (!ratesAssignment) return;
    els.ratesStatus.hidden = true;
    sb.from('assignments')
      .update({
        worker_pay_rate: els.rtPay.value.trim() || null,
        client_charge_rate: els.rtCharge.value.trim() || null
      })
      .eq('id', ratesAssignment.id)
      .then(function (res) {
        if (res.error) {
          showActionStatus(els.ratesStatus, false, friendlyDbError(res.error));
          return;
        }
        els.ratesForm.hidden = true;
        ratesAssignment = null;
        showActionStatus(els.assignmentStatus, true, 'Rates recorded.');
        loadAssignments();
      });
  });

  function loadAssignments() {
    sb.from('assignments')
      .select('id, public_reference, status, trade, start_date, request_id, ' +
        'worker_pay_rate, client_charge_rate, ' +
        'workers(full_name, passport_no), workforce_requests(public_reference, number_needed)')
      .order('created_at', { ascending: false })
      .limit(50)
      .then(function (res) {
        els.assignmentRows.innerHTML = '';
        (res.data || []).forEach(function (a) {
          var w = a.workers || {};
          var req = a.workforce_requests || {};
          var tr = document.createElement('tr');
          [a.public_reference || '—',
            (w.passport_no ? w.passport_no + ' · ' : '') + (w.full_name || 'Worker'),
            a.trade || '—', fmtDate(a.start_date)].forEach(function (t) {
            var td = document.createElement('td');
            td.textContent = t;
            tr.appendChild(td);
          });
          var tdS = document.createElement('td');
          tdS.innerHTML = badge(ASSIGN_BADGE[a.status] || 'pending',
            ASSIGN_STATUS[a.status] || a.status) +
            (req.public_reference ? ' <span class="profile-line">' +
              req.public_reference + '</span>' : '') +
            (canManageRequests && (a.worker_pay_rate || a.client_charge_rate)
              ? ' <span class="profile-line">pay ' + (a.worker_pay_rate || '—') +
                ' · charge ' + (a.client_charge_rate || '—') + '</span>' : '');
          tr.appendChild(tdS);
          var td = document.createElement('td');
          td.className = 'right';
          if (canManageRequests) {
            if (a.status === 'offered') {
              var acc = document.createElement('button');
              acc.type = 'button';
              acc.className = 'btn small';
              acc.textContent = 'Accepted';
              acc.title = 'Record the worker\'s acceptance of the offer';
              acc.addEventListener('click', function () {
                recordResponse(a, 'accepted');
              });
              td.appendChild(acc);
              td.appendChild(document.createTextNode(' '));
              var dec = document.createElement('button');
              dec.type = 'button';
              dec.className = 'btn small ghost';
              dec.textContent = 'Declined';
              dec.addEventListener('click', function () {
                recordResponse(a, 'declined');
              });
              td.appendChild(dec);
              td.appendChild(document.createTextNode(' '));
            }
            if (a.status === 'proposed' || a.status === 'accepted') {
              var conf = document.createElement('button');
              conf.type = 'button';
              conf.className = 'btn small';
              conf.textContent = 'Confirm';
              conf.addEventListener('click', function () { confirmAssignment(a); });
              td.appendChild(conf);
              td.appendChild(document.createTextNode(' '));
            }
            if (a.status === 'confirmed') {
              var act = document.createElement('button');
              act.type = 'button';
              act.className = 'btn small';
              act.textContent = 'Activate';
              act.title = 'Second readiness gate — the worker goes on site';
              act.addEventListener('click', function () { activateAssignment(a); });
              td.appendChild(act);
              td.appendChild(document.createTextNode(' '));
            }
            if (a.status === 'proposed' || a.status === 'offered' ||
                a.status === 'accepted' || a.status === 'confirmed' ||
                a.status === 'active') {
              var can = document.createElement('button');
              can.type = 'button';
              can.className = 'btn small ghost';
              can.textContent = 'Cancel';
              can.addEventListener('click', function () { cancelAssignment(a); });
              td.appendChild(can);
              td.appendChild(document.createTextNode(' '));
            }
          }
          if (a.status === 'confirmed' || a.status === 'active') {
            if (canManageRequests) {
              var out = document.createElement('button');
              out.type = 'button';
              out.className = 'btn small';
              out.textContent = 'Record outcome';
              out.addEventListener('click', function () { openOutcome(a); });
              td.appendChild(out);
              td.appendChild(document.createTextNode(' '));
            }
            if (canGiveFeedback) {
              var fb = document.createElement('button');
              fb.type = 'button';
              fb.className = 'btn small';
              fb.textContent = 'Record feedback';
              fb.addEventListener('click', function () { openOutcome(a, 'feedback'); });
              td.appendChild(fb);
              td.appendChild(document.createTextNode(' '));
            }
          }
          var stmt = document.createElement('button');
          stmt.type = 'button';
          stmt.className = 'btn small ghost';
          stmt.textContent = 'Statement';
          stmt.addEventListener('click', function () { openStatement(a); });
          td.appendChild(stmt);
          if (canManageRequests) {
            td.appendChild(document.createTextNode(' '));
            var rt = document.createElement('button');
            rt.type = 'button';
            rt.className = 'btn small ghost';
            rt.textContent = 'Rates';
            rt.addEventListener('click', function () { openRates(a); });
            td.appendChild(rt);
          }
          tr.appendChild(td);
          els.assignmentRows.appendChild(tr);
        });
      });
    loadAttendance();
    loadIncidents();
  }

  function refreshAfterAssignmentChange(a) {
    els.assignmentStatus.hidden = true;
    sb.from('assignments')
      .select('id', { count: 'exact', head: true })
      .eq('request_id', a.request_id)
      .in('status', ['confirmed', 'active', 'completed'])
      .then(function (cnt) {
        var req = a.workforce_requests || {};
        if ((cnt.count || 0) >= (req.number_needed || 1)) {
          sb.from('workforce_requests')
            .update({ status: 'filled' })
            .eq('id', a.request_id)
            .in('status', ['offered', 'matched', 'open'])
            .then(function () { loadRequests(); loadAssignments(); });
        } else {
          loadRequests();
          loadAssignments();
        }
      });
  }

  function confirmAssignment(a) {
    sb.rpc('confirm_assignment', { p_assignment_id: a.id })
      .then(function (res) {
        var d = res.data || {};
        if (!d.ok) {
          showActionStatus(els.assignmentStatus, false,
            d.error === 'hard_gate_refused'
              ? (d.reason || 'The readiness gate refused confirmation — ' +
                  'this worker needs a current passing readiness check first.')
              : d.reason || friendlyDbError(res.error));
          return;
        }
        refreshAfterAssignmentChange(a);
      });
  }

  function activateAssignment(a) {
    sb.rpc('activate_assignment', { p_assignment_id: a.id })
      .then(function (res) {
        var d = res.data || {};
        if (!d.ok) {
          showActionStatus(els.assignmentStatus, false,
            d.error === 'hard_gate_refused'
              ? (d.reason || 'The second readiness gate refused activation — ' +
                  'run a fresh readiness check for this worker first.')
              : d.reason || friendlyDbError(res.error));
          return;
        }
        showActionStatus(els.assignmentStatus, true,
          'Activated — the worker is on site. A pre-activation readiness ' +
          'snapshot was recorded.');
        loadAssignments();
      });
  }

  function recordResponse(a, response) {
    sb.rpc('record_offer_response',
           { p_assignment_id: a.id, p_response: response })
      .then(function (res) {
        var d = res.data || {};
        if (!d.ok) {
          showActionStatus(els.assignmentStatus, false,
            d.reason || 'The response could not be recorded.');
          return;
        }
        showActionStatus(els.assignmentStatus, true,
          response === 'accepted'
            ? 'Acceptance recorded. Confirm the assignment when it is booked in.'
            : 'Decline recorded — the assignment is cancelled.');
        refreshAfterAssignmentChange(a);
      });
  }

  /* ---- Attendance (FR-11, AT-10/AT-11): one authoritative record per
     assignment and shift date; a dispute appends, it never overwrites
     the original; resolution is Compliance's ---- */

  var disputeEvidence = null;

  function loadAttendance() {
    if (els.attendancePanel.hidden) return;
    sb.from('assignments')
      .select('id, public_reference, status, workers(full_name)')
      .in('status', ['confirmed', 'active', 'completed'])
      .order('created_at', { ascending: false }).limit(50)
      .then(function (res) {
        var current = els.atAssignment.value;
        els.atAssignment.innerHTML = '<option value="">Choose…</option>';
        (res.data || []).forEach(function (a) {
          var opt = document.createElement('option');
          opt.value = a.id;
          opt.textContent = (a.public_reference || 'Assignment') + ' · ' +
            (((a.workers || {}).full_name) || 'worker') +
            ' (' + (ASSIGN_STATUS[a.status] || a.status) + ')';
          els.atAssignment.appendChild(opt);
        });
        if (current) els.atAssignment.value = current;
      });
    sb.from('attendance_evidence')
      .select('id, shift_date, outcome, status, note, source, ' +
              'assignments(public_reference), workers(full_name), ' +
              'attendance_disputes(id, status, note, resolution, ' +
              'corrected_outcome)')
      .order('shift_date', { ascending: false }).limit(50)
      .then(function (res) {
        els.attendanceRows.innerHTML = '';
        (res.data || []).forEach(function (ev) {
          var a = ev.assignments || {};
          var w = ev.workers || {};
          var disp = (ev.attendance_disputes || [])[0];
          var tr = document.createElement('tr');
          [(a.public_reference || '—'),
           (w.full_name || '—'), fmtDate(ev.shift_date),
           ATTEND_OUTCOME[ev.outcome] || ev.outcome,
           disp && disp.status === 'open'
             ? 'Disputed' + (disp.note ? ': ' + disp.note : '')
             : ATTEND_STATUS[ev.status] || ev.status].forEach(function (t) {
            var td = document.createElement('td');
            td.textContent = t;
            tr.appendChild(td);
          });
          var td = document.createElement('td');
          if (disp && disp.corrected_outcome) {
            td.textContent = 'Corrected to ' +
              (ATTEND_OUTCOME[disp.corrected_outcome] || disp.corrected_outcome);
          }
          tr.appendChild(td);
          var tda = document.createElement('td');
          if (disp && disp.status === 'open' &&
              (profile && profile.roles.indexOf('compliance') !== -1)) {
            var rs = document.createElement('button');
            rs.type = 'button';
            rs.className = 'btn small';
            rs.textContent = 'Resolve';
            rs.addEventListener('click', function () {
              disputeEvidence = disp;
              els.resolveDisputeForm.hidden = false;
              els.resolveDisputeTitle.textContent = 'Resolve dispute — ' +
                (a.public_reference || '') + ' · ' + fmtDate(ev.shift_date) +
                ' (recorded: ' + (ATTEND_OUTCOME[ev.outcome] || ev.outcome) +
                '; worker says: ' + (disp.note || '—') + ')';
              els.rdResolution.value = 'original_stands';
              els.rdOutcome.value = '';
              els.rdNote.value = '';
              els.resolveDisputeForm.scrollIntoView({ behavior: 'smooth' });
            });
            tda.appendChild(rs);
          }
          tr.appendChild(tda);
          els.attendanceRows.appendChild(tr);
        });
      });
  }

  els.attendanceForm.addEventListener('submit', function (e) {
    e.preventDefault();
    els.attendanceStatus.hidden = true;
    if (!els.atAssignment.value || !els.atDate.value) {
      showActionStatus(els.attendanceStatus, false,
        'Choose the assignment and the shift date.');
      return;
    }
    sb.rpc('record_attendance_evidence', {
      p_assignment_id: els.atAssignment.value,
      p_shift_date: els.atDate.value,
      p_outcome: els.atOutcome.value,
      p_source: els.atSource.value.trim() || null,
      p_note: els.atNote.value.trim() || null
    }).then(function (res) {
      var d = res.data || {};
      if (!d.ok) {
        showActionStatus(els.attendanceStatus, false,
          d.reason || ({
            duplicate_record: 'A record already exists for this assignment ' +
              'and date — dispute it first if it needs correcting.'
          })[d.error] || 'The record could not be saved.');
        return;
      }
      showActionStatus(els.attendanceStatus, true, 'Attendance recorded.');
      els.atDate.value = '';
      els.atNote.value = '';
      loadAttendance();
    });
  });

  els.resolveDisputeForm.addEventListener('submit', function (e) {
    e.preventDefault();
    if (!disputeEvidence) return;
    els.resolveDisputeStatus.hidden = true;
    var resolution = els.rdResolution.value;
    var corrected = resolution === 'corrected'
      ? (els.rdOutcome.value || null) : null;
    sb.rpc('resolve_attendance_dispute', {
      p_dispute_id: disputeEvidence.id,
      p_resolution: resolution,
      p_corrected_outcome: corrected,
      p_note: els.rdNote.value.trim() || null
    }).then(function (res) {
      var d = res.data || {};
      if (!d.ok) {
        showActionStatus(els.resolveDisputeStatus, false,
          d.reason || ({
            correction_required: 'Choose the corrected outcome.',
            correction_identical: 'That is the same as the original — ' +
              'resolve as "original stands" instead.'
          })[d.error] || 'The dispute could not be resolved.');
        return;
      }
      showActionStatus(els.resolveDisputeStatus, true,
        'Dispute resolved. The original record and the resolution are ' +
        'both on file.');
      els.resolveDisputeForm.hidden = true;
      disputeEvidence = null;
      loadAttendance();
    });
  });

  /* ---- Replacement incidents (FR-12, AT-12/AT-13): the chain reuses
     the normal controls; approvals append; the site-pack
     acknowledgement is an explicit operator action ---- */

  var currentIncident = null;

  function loadIncidents() {
    if (els.incidentsPanel.hidden) return;
    sb.from('assignments')
      .select('id, public_reference, status, workers(full_name)')
      .in('status', ['confirmed', 'active'])
      .order('created_at', { ascending: false }).limit(50)
      .then(function (res) {
        var current = els.inAssignment.value;
        els.inAssignment.innerHTML = '<option value="">Choose…</option>';
        (res.data || []).forEach(function (a) {
          var opt = document.createElement('option');
          opt.value = a.id;
          opt.textContent = (a.public_reference || 'Assignment') + ' · ' +
            (((a.workers || {}).full_name) || 'worker') +
            ' (' + (ASSIGN_STATUS[a.status] || a.status) + ')';
          els.inAssignment.appendChild(opt);
        });
        if (current) els.inAssignment.value = current;
      });
    sb.from('replacement_incidents')
      .select('id, incident_type, recorded_at, notes, resolved_at, request_id, ' +
              'site_pack_ack_at, replacement_assignment_id, ' +
              'assignments!replacement_incidents_assignment_id_fkey' +
                '(public_reference, status), ' +
              'replacement_incident_approvals(decision, notes, created_at)')
      .order('recorded_at', { ascending: false }).limit(30)
      .then(function (res) {
        var incidents = res.data || [];
        // replacement references resolved separately: two FK paths to
        // assignments cannot be embedded in one query
        var repIds = incidents
          .map(function (inc) { return inc.replacement_assignment_id; })
          .filter(function (id) { return !!id; });
        var render = function (repRefs) {
          els.incidentRows.innerHTML = '';
          incidents.forEach(function (inc) {
            var a = inc.assignments || {};
            var repRef = inc.replacement_assignment_id
              ? (repRefs[inc.replacement_assignment_id] || 'linked') : '—';
            var tr = document.createElement('tr');
            [(a.public_reference || '—'),
             INCIDENT_TYPE[inc.incident_type] || inc.incident_type,
             fmtDate(inc.recorded_at),
             repRef,
             inc.resolved_at ? 'Resolved' : 'Open'].forEach(function (t) {
              var td = document.createElement('td');
              td.textContent = t;
              tr.appendChild(td);
            });
            var td = document.createElement('td');
            td.className = 'right';
            if (!inc.resolved_at && canManageRequests) {
              var open = document.createElement('button');
              open.type = 'button';
              open.className = 'btn small';
              open.textContent = 'Manage';
              open.addEventListener('click', function () {
                openIncident(inc);
              });
              td.appendChild(open);
            }
            tr.appendChild(td);
            els.incidentRows.appendChild(tr);
          });
        };
        if (repIds.length) {
          sb.from('assignments')
            .select('id, public_reference')
            .in('id', repIds)
            .then(function (r2) {
              var map = {};
              (r2.data || []).forEach(function (x) { map[x.id] = x.public_reference; });
              render(map);
            });
        } else {
          render({});
        }
      });
  }

  function openIncident(inc) {
    currentIncident = inc;
    els.incidentDetail.hidden = false;
    var a = inc.assignments || {};
    var approvals = (inc.replacement_incident_approvals || []);
    var last = approvals.length
      ? approvals[approvals.length - 1] : null;
    els.incidentDetailTitle.textContent =
      'Incident — ' + (a.public_reference || '') +
      ' · ' + (INCIDENT_TYPE[inc.incident_type] || inc.incident_type);
    els.incidentDetailLine.innerHTML =
      'Recorded ' + fmtDate(inc.recorded_at) +
      (inc.notes ? ' — ' + inc.notes : '') +
      (last ? ' · last approval: ' + last.decision +
        (last.notes ? ' (' + last.notes + ')' : '') : '') +
      (inc.site_pack_ack_at
        ? ' · site pack acknowledged ' + fmtDate(inc.site_pack_ack_at)
        : ' · site pack NOT acknowledged') +
      (inc.resolved_at ? ' · resolved ' + fmtDate(inc.resolved_at) : '');
    // replacement candidates: live assignments for the same request that
    // came through the offer flow
    sb.from('assignments')
      .select('id, public_reference, status, workers(full_name)')
      .eq('request_id', inc.request_id)
      .in('status', ['offered', 'accepted', 'confirmed', 'active'])
      .order('created_at', { ascending: false }).limit(20)
      .then(function (res) {
        els.iaReplacement.innerHTML = '<option value="">Choose…</option>';
        (res.data || []).forEach(function (c) {
          if (c.id === inc.assignment_id) return;
          var opt = document.createElement('option');
          opt.value = c.id;
          opt.textContent = (c.public_reference || 'Assignment') + ' · ' +
            (((c.workers || {}).full_name) || 'worker') +
            ' (' + (ASSIGN_STATUS[c.status] || c.status) + ')';
          els.iaReplacement.appendChild(opt);
        });
      });
    els.iaDecision.value = 'approved';
    els.iaNotes.value = '';
    els.incidentActionStatus.hidden = true;
    els.incidentDetail.scrollIntoView({ behavior: 'smooth' });
  }

  els.incidentForm.addEventListener('submit', function (e) {
    e.preventDefault();
    els.incidentStatus.hidden = true;
    if (!els.inAssignment.value) {
      showActionStatus(els.incidentStatus, false, 'Choose the assignment.');
      return;
    }
    sb.rpc('record_replacement_incident', {
      p_assignment_id: els.inAssignment.value,
      p_incident_type: els.inType.value,
      p_notes: els.inNotes.value.trim() || null
    }).then(function (res) {
      var d = res.data || {};
      if (!d.ok) {
        showActionStatus(els.incidentStatus, false,
          d.reason || ({
            incident_already_open: 'An unresolved incident already exists ' +
              'for this assignment.'
          })[d.error] || 'The incident could not be recorded.');
        return;
      }
      showActionStatus(els.incidentStatus, true,
        'Incident recorded.' +
        (els.inType.value === 'cancellation'
          ? ' The assignment was cancelled through the status engine.'
          : els.inType.value === 'no_show'
            ? ' The assignment is marked no-show.'
            : ''));
      els.inNotes.value = '';
      loadAssignments();
    });
  });

  document.getElementById('ia-approval-btn').addEventListener('click', function () {
    if (!currentIncident) return;
    sb.rpc('record_replacement_approval', {
      p_incident_id: currentIncident.id,
      p_decision: els.iaDecision.value,
      p_notes: els.iaNotes.value.trim() || null
    }).then(function (res) {
      var d = res.data || {};
      if (!d.ok) {
        showActionStatus(els.incidentActionStatus, false,
          d.reason || 'The approval could not be recorded.');
        return;
      }
      showActionStatus(els.incidentActionStatus, true,
        'Approval appended to the history.');
      els.iaNotes.value = '';
      loadIncidents();
    });
  });

  document.getElementById('ia-link-btn').addEventListener('click', function () {
    if (!currentIncident) return;
    if (!els.iaReplacement.value) {
      showActionStatus(els.incidentActionStatus, false,
        'Choose the replacement assignment (same request, through the ' +
        'offer flow).');
      return;
    }
    sb.rpc('link_replacement_assignment', {
      p_incident_id: currentIncident.id,
      p_replacement_assignment_id: els.iaReplacement.value
    }).then(function (res) {
      var d = res.data || {};
      if (!d.ok) {
        showActionStatus(els.incidentActionStatus, false,
          d.reason || 'The replacement could not be linked.');
        return;
      }
      showActionStatus(els.incidentActionStatus, true,
        'Replacement linked. The original is marked replaced where its ' +
        'status allows.');
      loadAssignments();
    });
  });

  document.getElementById('ia-ack-btn').addEventListener('click', function () {
    if (!currentIncident) return;
    sb.rpc('acknowledge_replacement_site_pack',
           { p_incident_id: currentIncident.id })
      .then(function (res) {
        var d = res.data || {};
        if (!d.ok) {
          showActionStatus(els.incidentActionStatus, false,
            d.reason || 'The acknowledgement could not be recorded.');
          return;
        }
        showActionStatus(els.incidentActionStatus, true,
          'Site pack acknowledged.');
        loadIncidents();
      });
  });

  document.getElementById('ia-resolve-btn').addEventListener('click', function () {
    if (!currentIncident) return;
    sb.rpc('resolve_replacement_incident', {
      p_incident_id: currentIncident.id,
      p_notes: null
    }).then(function (res) {
      var d = res.data || {};
      if (!d.ok) {
        showActionStatus(els.incidentActionStatus, false,
          d.reason || 'The chain could not be resolved.');
        return;
      }
      showActionStatus(els.incidentActionStatus, true,
        'Chain closed. Elapsed time: ' +
        Math.round((d.elapsed || 0) / 60) + ' minutes.');
      els.incidentDetail.hidden = true;
      currentIncident = null;
      loadAssignments();
    });
  });

  /* ---- Contractor view (FR-16): own requests, assignments,
     attendance and statements — worker name and trade only ---- */

  function loadContractorOverview() {
    sb.rpc('contractor_overview')
      .then(function (res) {
        var d = res.data || {};
        if (!d.ok) {
          els.contractorLine.textContent =
            d.reason || 'Your contractor view could not be loaded.';
          return;
        }
        els.contractorTitle.textContent = d.contractor.legal_name || 'Your company';
        els.contractorLine.textContent =
          (d.contractor.contact_name ? d.contractor.contact_name + ' · ' : '') +
          (d.contractor.email || '') + (d.contractor.phone
            ? ' · ' + d.contractor.phone : '');
        els.coRequestRows.innerHTML = miniTable(
          (d.requests || []).map(function (r) {
            return [r.public_reference || '—', r.trade || '—',
                    r.number_needed, fmtDate(r.start_date),
                    (REQUEST_STATUS[r.status] || r.status)];
          }), ['Ref', 'Trade', 'Needed', 'Start', 'Status']);
        els.coAssignmentRows.innerHTML = miniTable(
          (d.assignments || []).map(function (a) {
            return [a.public_reference || '—', a.worker_name || '—',
                    a.worker_trade || a.trade || '—', fmtDate(a.start_date),
                    ASSIGN_STATUS[a.status] || a.status];
          }), ['Ref', 'Worker', 'Trade', 'Start', 'Status']);
        els.coAttendanceRows.innerHTML = miniTable(
          (d.attendance || []).map(function (att) {
            return [att.public_reference || '—',
                    fmtDate(att.shift_date),
                    ATTEND_OUTCOME[att.outcome] || att.outcome];
          }), ['Assignment', 'Date', 'Outcome']);
        els.coStatements.innerHTML = '';
        (d.statements || []).forEach(function (s) {
          var c = s.content || {};
          var w = c.worker || {};
          var work = c.work || {};
          var box = document.createElement('div');
          box.className = 'note';
          box.innerHTML =
            '<p class="profile-line"><strong>' + (c.title || 'Statement') +
            ' v' + s.version + '</strong> · ' + fmtDate(s.generated_at) + '</p>' +
            '<p>' + (c.reference || '') + ' · ' + (w.name || '') +
            (w.trade ? ' · ' + w.trade : '') + '</p>' +
            '<p>' + (work.start_date ? fmtDate(work.start_date) : '—') +
            (work.end_date ? ' – ' + fmtDate(work.end_date) : '') + '</p>' +
            '<p>Status: ' + (ASSIGN_STATUS[c.status] || c.status || '—') + '</p>' +
            '<p class="footnote">' + (c.note || '') + '</p>';
          els.coStatements.appendChild(box);
        });
        if (!(d.statements || []).length) {
          els.coStatements.innerHTML =
            '<p class="footnote">No statements generated yet.</p>';
        }
      });
  }

  function cancelAssignment(a) {
    sb.from('assignments').update({ status: 'cancelled' })
      .eq('id', a.id)
      .then(function (res) {
        if (res.error) {
          showActionStatus(els.assignmentStatus, false, friendlyDbError(res.error));
          return;
        }
        els.assignmentStatus.hidden = true;
        loadAssignments();
        loadRequests();
      });
  }

  var outcomeAssignment = null;
  var outcomeMode = 'team';

  function openOutcome(a, mode) {
    outcomeAssignment = a;
    outcomeMode = mode || 'team';
    var w = a.workers || {};
    els.outcomeTitle.textContent =
      (outcomeMode === 'feedback'
        ? 'Record worker feedback — '
        : 'Record outcome — ') +
      (a.public_reference || '') + ' · ' + (w.full_name || 'worker');
    els.outcomeForm.hidden = false;
    els.outcomeStatus.hidden = true;
    document.getElementById('oc-attended').value = 'yes';
    document.getElementById('oc-rating').value = '';
    document.getElementById('oc-rehire').value = '';
    document.getElementById('oc-feedback').value = '';
    els.outcomeForm.scrollIntoView({ behavior: 'smooth' });
  }

  els.outcomeCancel.addEventListener('click', function () {
    els.outcomeForm.hidden = true;
    outcomeAssignment = null;
  });

  els.outcomeForm.addEventListener('submit', function (e) {
    e.preventDefault();
    if (!outcomeAssignment) return;
    els.outcomeStatus.hidden = true;
    var rating = document.getElementById('oc-rating').value;
    var rehire = document.getElementById('oc-rehire').value;
    if (!rating || !rehire) {
      showActionStatus(els.outcomeStatus, false,
        'Choose the rating and the rehire decision.');
      return;
    }
    sb.from('assignment_outcomes').upsert({
      assignment_id: outcomeAssignment.id,
      attended: document.getElementById('oc-attended').value === 'yes',
      rating: parseInt(rating, 10),
      rehire_decision: rehire,
      client_feedback: document.getElementById('oc-feedback').value.trim() || null
    }).then(function (res) {
      if (res.error) {
        var msg = (res.error.message || '');
        if (outcomeMode === 'feedback' &&
            (msg.indexOf('duplicate') !== -1 || msg.indexOf('security') !== -1)) {
          showActionStatus(els.outcomeStatus, false,
            'Feedback is already recorded for this assignment.');
        } else {
          showActionStatus(els.outcomeStatus, false, friendlyDbError(res.error));
        }
        return;
      }
      if (outcomeMode === 'feedback') {
        els.outcomeForm.hidden = true;
        outcomeAssignment = null;
        showActionStatus(els.assignmentStatus, true,
          'Feedback recorded. The team completes the outcome.');
        loadAssignments();
        return;
      }
      sb.from('assignments').update({ status: 'completed' })
        .eq('id', outcomeAssignment.id)
        .then(function (res2) {
          if (res2.error) {
            showActionStatus(els.outcomeStatus, false, friendlyDbError(res2.error));
            return;
          }
          els.outcomeForm.hidden = true;
          outcomeAssignment = null;
          loadAssignments();
        });
    });
  });

  function blockerAction(code, reason) {
    if (BLOCKER_ACTIONS[code]) return BLOCKER_ACTIONS[code];
    var text = (reason || '') + ' ' + code;
    if (/right to work/i.test(text)) return BLOCKER_ACTIONS.rtw_missing;
    if (/cscs/i.test(text)) return BLOCKER_ACTIONS.cscs_missing;
    if (/training/i.test(text)) return 'Add training certificates';
    if (/expired/i.test(text)) return 'Renew and re-verify';
    if (/not verified/i.test(text)) return BLOCKER_ACTIONS.worker_not_verified;
    if (/available/i.test(text)) return 'Confirm availability';
    return 'Review the reason and record what is needed';
  }

  function loadActionCentre() {
    var workersQ = sb.from('workers')
      .select('id, passport_no, full_name, status')
      .neq('status', 'archived')
      .order('full_name')
      .limit(200);
    var evalsQ = sb.from('readiness_evaluations')
      .select('worker_id, outcome, blockers, created_at')
      .order('created_at', { ascending: false })
      .limit(500);
    var schedQ = sb.from('expiry_schedule')
      .select('worker_id, item_table, item_id, expiry_date, band')
      .limit(1000);
    var rtwQ = sb.from('rtw_checks')
      .select('worker_id, result')
      .limit(1000);
    var qualQ = sb.from('qualifications')
      .select('worker_id, kind')
      .limit(1000);
    var trainQ = sb.from('training_certificates')
      .select('worker_id, training_type')
      .limit(1000);
    var histQ = sb.from('work_history')
      .select('worker_id')
      .limit(1000);

    Promise.all([workersQ, evalsQ, schedQ, rtwQ, qualQ, trainQ, histQ])
      .then(function (rs) {
        if (rs.some(function (r) { return r.error; })) {
          showActionStatus(els.acStatus, false,
            'The action centre could not load. Try again.');
          return;
        }
        var workers = rs[0].data || [];
        var evals = rs[1].data || [];
        var sched = rs[2].data || [];
        var rtws = rs[3].data || [];
        var quals = rs[4].data || [];
        var trains = rs[5].data || [];
        var history = rs[6].data || [];

        var byId = {};
        workers.forEach(function (w) { byId[w.id] = w; });

        // Latest evaluation per worker.
        var latestEval = {};
        evals.forEach(function (e) {
          if (!latestEval[e.worker_id]) latestEval[e.worker_id] = e;
        });

        var rtwByWorker = {};
        rtws.forEach(function (r) {
          rtwByWorker[r.worker_id] = rtwByWorker[r.worker_id] || [];
          rtwByWorker[r.worker_id].push(r.result);
        });
        var qualByWorker = {};
        quals.forEach(function (q) {
          qualByWorker[q.worker_id] = true;
        });
        var trainByWorker = {};
        trains.forEach(function (t) {
          trainByWorker[t.worker_id] = true;
        });
        var histByWorker = {};
        history.forEach(function (h) { histByWorker[h.worker_id] = true; });

        // Evidence labels for schedule rows.
        var critical = [];
        var dueSoon = [];
        var watch = [];
        var missingEv = [];
        var devGaps = [];

        workers.forEach(function (w) {
          var ev = latestEval[w.id];
          if (w.status === 'blocked') {
            critical.push({
              worker: w, text: 'Worker record is blocked',
              action: 'Review the reason and record what is needed'
            });
          } else if (ev && ev.outcome === 'blocked') {
            (ev.blockers || []).forEach(function (b) {
              critical.push({
                worker: w, text: b.reason || b.code,
                action: blockerAction(b.code, b.reason)
              });
            });
          }
          if (!rtwByWorker[w.id]) {
            missingEv.push({
              worker: w, text: 'Right to Work check not recorded',
              action: 'Complete evidence pack'
            });
          } else if (rtwByWorker[w.id].indexOf('pass') === -1) {
            missingEv.push({
              worker: w, text: 'No passing Right to Work check on record',
              action: 'Complete evidence pack'
            });
          }
          if (!qualByWorker[w.id]) {
            missingEv.push({
              worker: w, text: 'No qualification recorded',
              action: 'Complete evidence pack'
            });
          }
          if (!trainByWorker[w.id]) {
            devGaps.push({
              worker: w, text: 'No training certificates yet',
              action: 'Add training certificates'
            });
          }
          if (!histByWorker[w.id]) {
            devGaps.push({
              worker: w, text: 'No work history yet',
              action: 'Log first verified job'
            });
          }
        });

        sched.forEach(function (s) {
          if (!byId[s.worker_id]) return;
          var label = ITEM_TABLE_LABELS[s.item_table] || s.item_table;
          var text = label.charAt(0).toUpperCase() + label.slice(1) +
            ', due ' + fmtDate(s.expiry_date);
          var item = { worker: byId[s.worker_id], text: text,
            action: 'Renew ' + label };
          if (s.band === 'expired') {
            critical.push({ worker: byId[s.worker_id],
              text: text + ' (expired)',
              action: 'Renew and re-verify' });
          } else if (s.band === 'due_soon') {
            dueSoon.push(item);
          } else if (s.band === 'watch') {
            watch.push(item);
          }
        });

        renderActionCentre(critical, dueSoon, watch, missingEv, devGaps);
      });
  }

  function renderActionCentre(critical, dueSoon, watch, missingEv, devGaps) {
    var open = critical.length +
      dueSoon.length + watch.length + missingEv.length + devGaps.length;
    els.acSummary.textContent = open + ' open action' +
      (open === 1 ? '' : 's') + ' across the workforce.';
    els.acGroups.innerHTML = '';

    function group(title, items, cls) {
      if (!items.length) return;
      var div = document.createElement('div');
      div.className = 'ac-group';
      var h = document.createElement('h3');
      h.textContent = title + ' (' + items.length + ')';
      if (cls) h.className = cls;
      div.appendChild(h);
      items.forEach(function (i) {
        var p = document.createElement('p');
        p.className = 'profile-line';
        p.innerHTML = (i.worker.passport_no ? i.worker.passport_no + ' · ' : '') +
          (i.worker.full_name || 'Worker') + ' — ' +
          badge(cls || 'pending', i.text) + ' <span class="ac-action">' +
          i.action + '</span>';
        div.appendChild(p);
      });
      els.acGroups.appendChild(div);
    }

    group('Critical', critical, 'fail');
    group('Due soon (30 days)', dueSoon, 'pending');
    group('Watch (31–60 days)', watch, 'pending_review');
    group('Missing evidence', missingEv, 'pending');
    group('Workforce development', devGaps, 'pending');
  }

  els.recomputeBtn.addEventListener('click', function () {
    sb.rpc('recompute_expiry_schedule')
      .then(function (res) {
        var d = res.data || {};
        if (!d.ok) {
          showActionStatus(els.acStatus, false,
            d.error === 'not_permitted'
              ? 'Your role cannot recompute the schedule.'
              : 'The schedule could not be recomputed. Try again.');
          return;
        }
        showActionStatus(els.acStatus, true,
          'Schedule recomputed: ' + d.expired + ' expired, ' +
          d.due_soon + ' due soon, ' + d.watch + ' on watch.');
        loadActionCentre();
      })
      .catch(function () {
        showActionStatus(els.acStatus, false,
          'The schedule could not be recomputed. Try again.');
      });
  });

  var MILESTONE_LABELS = { '60d': '60 days', '30d': '30 days',
    '14d': '14 days', '7d': '7 days' };
  var OVERRIDE_LABELS = {
    worker_not_verified: 'Worker record not verified',
    rtw_missing: 'Right to Work check missing',
    rtw_not_pass: 'Right to Work check did not pass',
    rtw_followup_overdue: 'Right to Work follow-up overdue'
  };
  var PRICE_SERVICES = {
    managed_onboarding: 'Managed onboarding',
    compliance_monitoring: 'Compliance monitoring',
    training_coordination: 'Training-request coordination',
    rtw_check: 'Right to Work check',
    other: 'Other'
  };
  var COST_CATEGORIES = {
    training_provider: 'Training provider', identity_check: 'Identity check',
    verification: 'Verification', other: 'Other'
  };
  var DOC_TYPES = {
    cscs_card: 'CSCS card', passport: 'Passport or ID',
    certificate: 'Certificate', other: 'Other'
  };

  function loadAcReminders() {
    sb.from('reminder_log')
      .select('milestone, item_table, sent_at, workers(passport_no, full_name)')
      .order('sent_at', { ascending: false })
      .limit(20)
      .then(function (res) {
        var rows = res.data || [];
        if (!rows.length) {
          els.acReminders.innerHTML = '';
          return;
        }
        var html = '<h3>Recent reminders</h3>';
        rows.forEach(function (r) {
          var w = r.workers || {};
          html += '<p class="profile-line">' +
            (w.passport_no ? w.passport_no + ' · ' : '') +
            (w.full_name || 'Worker') + ' — ' +
            (ITEM_TABLE_LABELS[r.item_table] || r.item_table) +
            ' reminder (' + (MILESTONE_LABELS[r.milestone] || r.milestone) +
            '), ' + fmtDate(r.sent_at) + '</p>';
        });
        els.acReminders.innerHTML = html;
      });
  }

  els.remindersBtn.addEventListener('click', function () {
    sb.rpc('run_expiry_reminders')
      .then(function (res) {
        var d = res.data || {};
        if (!d.ok) {
          showActionStatus(els.acStatus, false,
            d.error === 'not_permitted'
              ? 'Your role cannot run reminders.'
              : 'Reminders could not run. Try again.');
          return;
        }
        var by = d.by_milestone || {};
        var parts = ['60d', '30d', '14d', '7d'].filter(function (m) {
          return by[m];
        }).map(function (m) {
          return by[m] + ' at ' + (MILESTONE_LABELS[m] || m);
        });
        showActionStatus(els.acStatus, true, d.reminders > 0
          ? d.reminders + ' reminder' + (d.reminders === 1 ? '' : 's') +
            ' recorded' + (parts.length ? ': ' + parts.join(', ') : '') + '.'
          : 'No new reminders due — everything within its window is already recorded.');
        loadAcReminders();
      })
      .catch(function () {
        showActionStatus(els.acStatus, false, 'Reminders could not run. Try again.');
      });
  });

  function loadWorkerReminders(workerId) {
    sb.from('reminder_log')
      .select('milestone, item_table, sent_at')
      .eq('worker_id', workerId)
      .order('sent_at', { ascending: false })
      .limit(20)
      .then(function (res) {
        var rows = res.data || [];
        els.passportReminders.hidden = false;
        els.remindersLine.textContent = rows.length
          ? 'Reminders about your expiring evidence:'
          : 'No reminders yet.';
        els.remindersRows.innerHTML = rows.map(function (r) {
          return '<p class="profile-line">' +
            (ITEM_TABLE_LABELS[r.item_table] || r.item_table) +
            ' — ' + (MILESTONE_LABELS[r.milestone] || r.milestone) +
            ' reminder, ' + fmtDate(r.sent_at) + '</p>';
        }).join('');
      });
  }

  function loadSelfDetails(worker) {
    els.passportDetails.hidden = false;
    document.getElementById('sd-phone').value = worker.phone || '';
    document.getElementById('sd-email').value = worker.email || '';
    document.getElementById('sd-trade').value = worker.trade || '';
    document.getElementById('sd-availability').value = worker.availability || '';
  }

  els.selfDetailsForm.addEventListener('submit', function (e) {
    e.preventDefault();
    els.selfDetailsStatus.hidden = true;
    sb.from('workers')
      .update({
        phone: document.getElementById('sd-phone').value.trim() || null,
        email: document.getElementById('sd-email').value.trim() || null,
        trade: document.getElementById('sd-trade').value.trim() || null,
        availability: document.getElementById('sd-availability').value.trim() || null
      })
      .eq('id', profile.worker_id)
      .then(function (res) {
        if (res.error) {
          showActionStatus(els.selfDetailsStatus, false,
            /may only correct/i.test(res.error.message || '')
              ? 'Only your contact details, trade and availability can be changed.'
              : friendlyDbError(res.error));
          return;
        }
        showActionStatus(els.selfDetailsStatus, true,
          'Corrections saved — the team can see them straight away.');
      });
  });

  function loadSelfDocuments(workerId) {
    sb.from('worker_documents')
      .select('document_type, status, created_at')
      .eq('worker_id', workerId)
      .order('created_at', { ascending: false })
      .limit(20)
      .then(function (res) {
        var rows = res.data || [];
        els.passportDocuments.hidden = false;
        els.selfDocRows.innerHTML = rows.length ? rows.map(function (d) {
          return '<p class="profile-line">' +
            (DOC_TYPES[d.document_type] || d.document_type) + ' — ' +
            (EVIDENCE_STATUS[d.status] || d.status) + ', uploaded ' +
            fmtDate(d.created_at) + '</p>';
        }).join('') : '<p class="profile-line">No documents uploaded yet.</p>';
      });
  }

  els.selfDocForm.addEventListener('submit', function (e) {
    e.preventDefault();
    els.selfDocStatus.hidden = true;
    var file = document.getElementById('sd-doc-file').files[0];
    var type = document.getElementById('sd-doc-type').value;
    if (!file) {
      showActionStatus(els.selfDocStatus, false, 'Choose a file to upload.');
      return;
    }
    var path = profile.worker_id + '/' + Date.now() + '-' +
      file.name.replace(/[^a-zA-Z0-9._-]/g, '_');
    sb.storage.from('worker-documents')
      .upload(path, file)
      .then(function (res) {
        if (res.error) {
          showActionStatus(els.selfDocStatus, false,
            'The upload failed. Try again.');
          return;
        }
        return sb.from('worker_documents')
          .insert({ worker_id: profile.worker_id, document_type: type,
                    storage_path: path })
          .then(function (r2) {
            if (r2.error) {
              showActionStatus(els.selfDocStatus, false, friendlyDbError(r2.error));
              return;
            }
            showActionStatus(els.selfDocStatus, true,
              'Uploaded — the team will verify it.');
            document.getElementById('sd-doc-file').value = '';
            loadSelfDocuments(profile.worker_id);
          });
      });
  });

  function loadWorkerOverrides(workerId) {
    sb.from('overrides')
      .select('requirement, reason, expires_at, created_at')
      .eq('worker_id', workerId)
      .order('created_at', { ascending: false })
      .limit(20)
      .then(function (res) {
        var rows = res.data || [];
        els.overrideRows.innerHTML = rows.length ? rows.map(function (o) {
          return '<p class="profile-line">' +
            (OVERRIDE_LABELS[o.requirement] || o.requirement) + ' — ' +
            o.reason + (o.expires_at ? ' (expires ' + fmtDate(o.expires_at) + ')' : '') +
            ', approved ' + fmtDate(o.created_at) + '</p>';
        }).join('') : '<p class="profile-line">No overrides on record.</p>';
      });
  }

  els.overrideForm.addEventListener('submit', function (e) {
    e.preventDefault();
    els.overrideStatus.hidden = true;
    var reason = document.getElementById('ov-reason').value.trim();
    if (!reason) {
      showActionStatus(els.overrideStatus, false,
        'An override needs a reason — it is recorded permanently.');
      return;
    }
    sb.from('overrides')
      .insert({
        worker_id: currentWorker.id,
        requirement: document.getElementById('ov-requirement').value,
        reason: reason,
        approved_by: profile.id,
        expires_at: document.getElementById('ov-expires').value || null
      })
      .then(function (res) {
        if (res.error) {
          showActionStatus(els.overrideStatus, false, friendlyDbError(res.error));
          return;
        }
        showActionStatus(els.overrideStatus, true,
          'Override approved and recorded. Re-run the readiness check to apply it.');
        document.getElementById('ov-reason').value = '';
        document.getElementById('ov-expires').value = '';
        loadWorkerOverrides(currentWorker.id);
      });
  });

  function loadWorkerDocuments(workerId) {
    sb.from('worker_documents')
      .select('id, document_type, storage_path, status, created_at')
      .eq('worker_id', workerId)
      .order('created_at', { ascending: false })
      .limit(20)
      .then(function (res) {
        var rows = res.data || [];
        els.documentRows.innerHTML = rows.length ? rows.map(function (d) {
          return '<p class="profile-line">' +
            (DOC_TYPES[d.document_type] || d.document_type) + ' — ' +
            (EVIDENCE_STATUS[d.status] || d.status) + ', uploaded ' +
            fmtDate(d.created_at) +
            ' <button type="button" class="btn small ghost doc-open" data-path="' +
            d.storage_path + '">Open</button></p>';
        }).join('') : '<p class="profile-line">No documents uploaded.</p>';
        Array.prototype.forEach.call(
          els.documentRows.querySelectorAll('.doc-open'),
          function (btn) {
            btn.addEventListener('click', function () {
              sb.storage.from('worker-documents')
                .createSignedUrl(btn.getAttribute('data-path'), 600)
                .then(function (r) {
                  if (r.error || !r.data) {
                    showActionStatus(els.overrideStatus, false,
                      'The document could not be opened. Try again.');
                    return;
                  }
                  window.open(r.data.signedUrl, '_blank');
                });
            });
          });
      });
  }

  var statementAssignment = null;

  function openStatement(a) {
    statementAssignment = a;
    els.statementView.hidden = false;
    var w = a.workers || {};
    els.statementTitle.textContent = 'Assignment statement — ' +
      (a.public_reference || '') + ' · ' + (w.full_name || 'worker');
    els.statementStatus.hidden = true;
    sb.from('assignment_statements')
      .select('version, content, generated_at')
      .eq('assignment_id', a.id)
      .order('version', { ascending: false })
      .limit(1)
      .then(function (res) {
        renderStatement((res.data || [])[0]);
      });
  }

  function renderStatement(stmt) {
    if (!stmt) {
      els.statementBody.innerHTML =
        '<p class="profile-line">No statement generated yet.</p>';
      return;
    }
    var c = stmt.content || {};
    var o = c.outcome || {};
    els.statementBody.innerHTML =
      '<p class="profile-line">Version ' + stmt.version + ', generated ' +
      fmtDate(stmt.generated_at) + '</p>' +
      '<p><strong>' + (c.title || 'Assignment statement') + '</strong></p>' +
      '<p class="profile-line">Reference: ' + (c.reference || '—') + '</p>' +
      '<p class="profile-line">Worker: ' +
      ((c.worker && c.worker.name) || '—') +
      (c.worker && c.worker.passport_no ? ' (' + c.worker.passport_no + ')' : '') + '</p>' +
      '<p class="profile-line">Client: ' + (c.client || '—') + '</p>' +
      '<p class="profile-line">Work: ' + ((c.work && c.work.trade) || '—') +
      ', from ' + fmtDate(c.work && c.work.start_date) +
      ' to ' + fmtDate(c.work && c.work.end_date) + '</p>' +
      '<p class="profile-line">Status: ' + (ASSIGN_STATUS[c.status] || c.status || '—') + '</p>' +
      (c.outcome
        ? '<p class="profile-line">Outcome: attended ' + (o.attended ? 'yes' : 'no') +
          (o.rating ? ', rating ' + o.rating + ' of 5' : '') +
          (o.rehire_decision ? ', would rehire ' + o.rehire_decision : '') + '</p>'
        : '') +
      '<p class="footnote">' + (c.note || '') + '</p>';
    els.statementView.scrollIntoView({ behavior: 'smooth' });
  }

  els.statementClose.addEventListener('click', function () {
    els.statementView.hidden = true;
    statementAssignment = null;
  });

  els.statementGenerate.addEventListener('click', function () {
    if (!statementAssignment) return;
    els.statementStatus.hidden = true;
    sb.rpc('generate_assignment_statement',
      { p_assignment_id: statementAssignment.id })
      .then(function (res) {
        var d = res.data || {};
        if (!d.ok) {
          showActionStatus(els.statementStatus, false,
            d.error === 'not_permitted'
              ? 'Your role cannot generate statements.'
              : 'The statement could not be generated. Try again.');
          return;
        }
        renderStatement({ version: d.version, content: d.content,
          generated_at: new Date().toISOString() });
        showActionStatus(els.statementStatus, true,
          'Statement version ' + d.version + ' generated and kept.');
      })
      .catch(function () {
        showActionStatus(els.statementStatus, false,
          'The statement could not be generated. Try again.');
      });
  });

  function loadPrices() {
    sb.from('price_catalog')
      .select('id, scope, contractor_id, service, price, unit, approval_status')
      .order('created_at', { ascending: false })
      .limit(100)
      .then(function (res) {
        els.priceRows.innerHTML = '';
        (res.data || []).forEach(function (p) {
          var tr = document.createElement('tr');
          [PRICE_SERVICES[p.service] || p.service,
            p.scope === 'customer' ? 'Customer' : 'Standard',
            '£' + p.price + ' ' + p.unit].forEach(function (t) {
            var td = document.createElement('td');
            td.textContent = t;
            tr.appendChild(td);
          });
          var tdS = document.createElement('td');
          tdS.innerHTML = badge(p.approval_status === 'approved' ? 'pass' : 'pending',
            p.approval_status === 'approved' ? 'Approved' : 'Draft');
          tr.appendChild(tdS);
          var td = document.createElement('td');
          td.className = 'right';
          if (p.approval_status !== 'approved') {
            var b = document.createElement('button');
            b.type = 'button';
            b.className = 'btn small';
            b.textContent = 'Approve';
            b.addEventListener('click', function () {
              sb.from('price_catalog')
                .update({ approval_status: 'approved' })
                .eq('id', p.id)
                .then(function (r) {
                  if (r.error) {
                    showActionStatus(els.priceStatus, false, friendlyDbError(r.error));
                    return;
                  }
                  loadPrices();
                });
            });
            td.appendChild(b);
          }
          tr.appendChild(td);
          els.priceRows.appendChild(tr);
        });
      });
  }

  els.priceForm.addEventListener('submit', function (e) {
    e.preventDefault();
    els.priceStatus.hidden = true;
    var scope = document.getElementById('pr-scope').value;
    var contractorId = scope === 'customer' ? els.prContractor.value : null;
    if (scope === 'customer' && !contractorId) {
      showActionStatus(els.priceStatus, false,
        'Choose the contractor for a customer-specific price.');
      return;
    }
    var price = parseFloat(document.getElementById('pr-price').value);
    if (!price || price < 0) {
      showActionStatus(els.priceStatus, false, 'Enter the price.');
      return;
    }
    var discount = parseFloat(document.getElementById('pr-discount').value);
    var discountReason = document.getElementById('pr-discount-reason').value.trim();
    if (discount && !discountReason) {
      showActionStatus(els.priceStatus, false,
        'A discount needs a recorded reason.');
      return;
    }
    sb.from('price_catalog').insert({
      scope: scope,
      contractor_id: contractorId,
      service: document.getElementById('pr-service').value,
      price: price,
      unit: document.getElementById('pr-unit').value.trim() || 'per unit',
      vat_rate: parseFloat(document.getElementById('pr-vat').value) || null,
      billing_frequency: document.getElementById('pr-frequency').value.trim() || null,
      minimum_monthly: parseFloat(document.getElementById('pr-minimum').value) || null,
      discount_pct: discount || null,
      discount_reason: discount ? discountReason : null
    }).then(function (res) {
      if (res.error) {
        showActionStatus(els.priceStatus, false, friendlyDbError(res.error));
        return;
      }
      els.priceStatus.hidden = true;
      loadPrices();
    });
  });

  function loadSubscriptions() {
    sb.from('service_subscriptions')
      .select('id, contractor_id, managed_onboarding, compliance_monitoring, training_coordination, effective_from, contractors(legal_name)')
      .order('created_at', { ascending: false })
      .limit(100)
      .then(function (res) {
        els.subscriptionRows.innerHTML = '';
        (res.data || []).forEach(function (s) {
          var c = s.contractors || {};
          var tr = document.createElement('tr');
          [c.legal_name || '—',
            s.managed_onboarding ? 'On' : 'Off',
            s.compliance_monitoring ? 'On' : 'Off',
            s.training_coordination ? 'On' : 'Off',
            fmtDate(s.effective_from)].forEach(function (t) {
            var td = document.createElement('td');
            td.textContent = t;
            tr.appendChild(td);
          });
          els.subscriptionRows.appendChild(tr);
        });
      });
  }

  els.subscriptionForm.addEventListener('submit', function (e) {
    e.preventDefault();
    els.subscriptionStatus.hidden = true;
    var contractorId = els.ssContractor.value;
    if (!contractorId) {
      showActionStatus(els.subscriptionStatus, false, 'Choose the contractor.');
      return;
    }
    var patch = {
      contractor_id: contractorId,
      managed_onboarding: document.getElementById('ss-onboarding').checked,
      compliance_monitoring: document.getElementById('ss-monitoring').checked,
      training_coordination: document.getElementById('ss-training').checked
    };
    sb.from('service_subscriptions')
      .select('id')
      .eq('contractor_id', contractorId)
      .limit(1)
      .then(function (res) {
        var existing = (res.data || [])[0];
        var op = existing
          ? sb.from('service_subscriptions').update(patch).eq('id', existing.id)
          : sb.from('service_subscriptions').insert(patch);
        return op;
      })
      .then(function (res) {
        if (res.error) {
          showActionStatus(els.subscriptionStatus, false, friendlyDbError(res.error));
          return;
        }
        showActionStatus(els.subscriptionStatus, true, 'Service switches saved.');
        loadSubscriptions();
      });
  });

  function loadCosts() {
    sb.from('external_costs')
      .select('id, description, category, amount, status')
      .order('created_at', { ascending: false })
      .limit(100)
      .then(function (res) {
        els.costRows.innerHTML = '';
        (res.data || []).forEach(function (c) {
          var tr = document.createElement('tr');
          [c.description, COST_CATEGORIES[c.category] || c.category,
            '£' + c.amount].forEach(function (t) {
            var td = document.createElement('td');
            td.textContent = t;
            tr.appendChild(td);
          });
          var tdS = document.createElement('td');
          tdS.innerHTML = badge(c.status === 'approved' ? 'pass' :
            c.status === 'incurred' ? 'verified' : 'pending', c.status);
          tr.appendChild(tdS);
          var td = document.createElement('td');
          td.className = 'right';
          if (c.status === 'proposed') {
            var b = document.createElement('button');
            b.type = 'button';
            b.className = 'btn small';
            b.textContent = 'Approve';
            b.addEventListener('click', function () {
              sb.from('external_costs')
                .update({ status: 'approved', approved_by: profile.id,
                          approved_at: new Date().toISOString() })
                .eq('id', c.id)
                .then(function (r) {
                  if (r.error) {
                    showActionStatus(els.costStatus, false, friendlyDbError(r.error));
                    return;
                  }
                  loadCosts();
                });
            });
            td.appendChild(b);
          }
          tr.appendChild(td);
          els.costRows.appendChild(tr);
        });
      });
  }

  els.costForm.addEventListener('submit', function (e) {
    e.preventDefault();
    els.costStatus.hidden = true;
    var description = document.getElementById('ec-description').value.trim();
    var amount = parseFloat(document.getElementById('ec-amount').value);
    if (!description || !amount || amount < 0) {
      showActionStatus(els.costStatus, false,
        'Enter what the cost is for and the amount.');
      return;
    }
    sb.from('external_costs').insert({
      description: description,
      category: document.getElementById('ec-category').value,
      amount: amount
    }).then(function (res) {
      if (res.error) {
        showActionStatus(els.costStatus, false, friendlyDbError(res.error));
        return;
      }
      els.costStatus.hidden = true;
      document.getElementById('ec-description').value = '';
      document.getElementById('ec-amount').value = '';
      loadCosts();
    });
  });

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
        var roles = profile.roles || [];
        // Admin accounts must pass two-factor before the dashboard unlocks.
        var needsMfa = roles.some(function (r) {
          return MFA_ROLES.indexOf(r) !== -1;
        });
        if (needsMfa && !mfaPassed) {
          els.profileLine.textContent = '';
          mfaGate(user);
          return;
        }
        var canInvite = roles.some(function (r) {
          return r === 'owner' || r === 'operations';
        });
        els.invitations.hidden = !canInvite;
        if (canInvite) loadInvitations();
        canWriteWorkers = roles.indexOf('owner') !== -1 ||
          roles.indexOf('operations') !== -1;
        canRecordEvidence = canWriteWorkers ||
          roles.indexOf('compliance') !== -1;
        canRunReadiness = roles.indexOf('owner') !== -1 ||
          roles.indexOf('compliance') !== -1;
        canManageRequests = roles.indexOf('owner') !== -1 ||
          roles.indexOf('operations') !== -1;
        canSeeWorkerDocs = roles.indexOf('owner') !== -1 ||
          roles.indexOf('compliance') !== -1;
        canGiveFeedback = roles.indexOf('contractor') !== -1;
        var canSeeWorkers = canRecordEvidence || roles.indexOf('auditor') !== -1;
        els.workersPanel.hidden = !canSeeWorkers;
        els.addWorkerForm.hidden = !canWriteWorkers;
        els.wdActions.hidden = !canWriteWorkers;
        els.rtwForm.hidden = !canRecordEvidence;
        els.qualForm.hidden = !canRecordEvidence;
        els.wdReadinessActions.hidden = !canRunReadiness;
        var canSeeCrewsLocal = canSeeWorkers;
        canSeeCrews = canSeeCrewsLocal;
        canWriteCrews = canWriteWorkers;
        els.crewsPanel.hidden = !canSeeCrews;
        els.crewsToolbar.hidden = !canSeeCrews;
        els.addCrewBtn.hidden = !canWriteCrews;
        var canSeeRequests = canManageRequests || roles.indexOf('compliance') !== -1 ||
          roles.indexOf('auditor') !== -1 || canGiveFeedback;
        els.requestsPanel.hidden = !canSeeRequests;
        els.requestForm.hidden = !canManageRequests;
        els.contractorDetails.hidden = !canManageRequests;
        els.assignmentsPanel.hidden = !canSeeRequests;
        els.outcomeForm.hidden = true;
        // Attendance and incidents are team surfaces; the contractor
        // sees their own copy through the contractor view below, and
        // the worker through the passport.
        var canSeeAttendance = canManageRequests ||
          roles.indexOf('compliance') !== -1 ||
          roles.indexOf('auditor') !== -1;
        els.attendancePanel.hidden = !canSeeAttendance;
        els.attendanceForm.hidden = !canManageRequests;
        els.incidentsPanel.hidden = !canSeeAttendance;
        els.incidentForm.hidden = !canManageRequests;
        if (roles.indexOf('contractor') !== -1) {
          els.contractorPanel.hidden = false;
          loadContractorOverview();
        } else {
          els.contractorPanel.hidden = true;
        }
        var canManageSchedule = roles.indexOf('owner') !== -1 ||
          roles.indexOf('compliance') !== -1;
        var canSeeCentre = canManageSchedule || roles.indexOf('operations') !== -1 ||
          roles.indexOf('auditor') !== -1;
        els.actionCentre.hidden = !canSeeCentre;
        els.recomputeBtn.hidden = !canManageSchedule;
        els.remindersBtn.hidden = !canManageSchedule;
        if (canSeeCentre) {
          loadActionCentre();
          loadAcReminders();
        }
        var canSeeOverrides = canSeeWorkers;
        els.overridesCard.hidden = !canSeeOverrides;
        els.overrideForm.hidden = roles.indexOf('owner') === -1;
        els.documentsCard.hidden = !canSeeWorkerDocs;
        els.statementGenerate.hidden = !canManageRequests;
        var isOwner = roles.indexOf('owner') !== -1;
        els.pricesPanel.hidden = !isOwner;
        if (isOwner) {
          loadPrices();
          loadSubscriptions();
          loadCosts();
        }
        if (canSeeRequests) {
          loadRequests();
          if (canManageRequests) loadContractors();
          loadAssignments();
        } else {
          els.matchesView.hidden = true;
        }
        if (canSeeWorkers) {
          loadWorkers();
        } else {
          els.workerDetail.hidden = true;
        }
        if (canSeeCrews) {
          loadCrews();
        } else {
          els.crewFormCard.hidden = true;
        }
        if (profile.worker_id) {
          loadPassport(profile.worker_id);
        } else if (roles.indexOf('worker') !== -1) {
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
            td.appendChild(document.createTextNode(' '));
            var emailBtn = document.createElement('button');
            emailBtn.type = 'button';
            emailBtn.className = 'btn small ghost';
            emailBtn.textContent = 'Email invitee';
            emailBtn.addEventListener('click', function () {
              emailInvitation(inv, emailBtn);
            });
            td.appendChild(emailBtn);
            td.appendChild(document.createTextNode(' '));
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

  /* Send the invitation email through the platform's sender. The
     serverless function verifies the invitation server-side before
     anything is sent. If email sending is not active yet (SMTP not
     configured), the operator keeps the copy-link route. */
  function emailInvitation(inv, btn) {
    btn.disabled = true;
    var old = btn.textContent;
    btn.textContent = 'Sending…';
    sb.auth.getSession().then(function (sres) {
      var jwt = sres.data && sres.data.session &&
        sres.data.session.access_token;
      if (!jwt) throw new Error('no session');
      return fetch('/api/email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json',
                   'Authorization': 'Bearer ' + jwt },
        body: JSON.stringify({ kind: 'invitation', token: inv.token })
      });
    }).then(function (r) { return r.json(); })
      .then(function (d) {
        btn.disabled = false;
        btn.textContent = old;
        if (d.ok) {
          showActionStatus(els.inviteStatus, true,
            'Invitation email sent to ' + inv.email + ' from ' +
            (d.from || 'the platform sender') + '.');
        } else if (d.error === 'smtp_not_configured') {
          showActionStatus(els.inviteStatus, false,
            'Email sending is not active yet — copy the link and send it ' +
            'yourself for now. (Activate the platform sender by adding the ' +
            'SMTP app password to the hosting secrets.)');
        } else {
          showActionStatus(els.inviteStatus, false,
            d.reason || 'The email could not be sent. Copy the link instead.');
        }
      })
      .catch(function () {
        btn.disabled = false;
        btn.textContent = old;
        showActionStatus(els.inviteStatus, false,
          'The email could not be sent. Copy the link instead.');
      });
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

  els.inviteRole.addEventListener('change', function () {
    els.inviteContractorField.hidden = els.inviteRole.value !== 'contractor';
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
    var contractorId = role === 'contractor' ? els.inviteContractor.value : null;
    if (role === 'contractor' && !contractorId) {
      els.inviteStatus.hidden = false;
      els.inviteStatus.textContent =
        'Choose the contractor this person belongs to (add one first if needed).';
      return;
    }
    sb.from('invitations')
      .insert({ email: email, role: role, invited_by: profile.id,
                 contractor_id: contractorId })
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
