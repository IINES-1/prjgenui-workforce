/* =========================================================
   PRJGENUI Workforce - script.js
   Nav, scroll progress, reveal, count-up, the scroll-built
   passport sequence, timeline fill and a few small touches.
   No frameworks, no dependencies. Every effect is skipped
   under prefers-reduced-motion and the page reads fine
   without any of it.
   ========================================================= */
(function () {
  'use strict';

  var doc = document;
  var root = doc.documentElement;
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var hasIO = 'IntersectionObserver' in window;
  function $(s, c) { return (c || doc).querySelector(s); }
  function $$(s, c) { return Array.prototype.slice.call((c || doc).querySelectorAll(s)); }
  function clamp(n, a, b) { return Math.min(b, Math.max(a, n)); }

  /* ---- Header: mobile nav, stuck shadow, offset for the mobile menu ---- */
  var header = $('.site-header');
  var navToggle = $('.nav-toggle');
  var mobileNav = $('.mobile-nav');
  function placeMobileNav() {
    if (!header || !mobileNav) return;
    mobileNav.style.setProperty('--mnav-top', Math.round(header.getBoundingClientRect().bottom) + 'px');
  }
  if (navToggle && mobileNav) {
    navToggle.addEventListener('click', function () {
      placeMobileNav();
      var open = mobileNav.classList.toggle('open');
      navToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    $$('a', mobileNav).forEach(function (a) {
      a.addEventListener('click', function () {
        mobileNav.classList.remove('open');
        navToggle.setAttribute('aria-expanded', 'false');
      });
    });
    doc.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && mobileNav.classList.contains('open')) {
        mobileNav.classList.remove('open');
        navToggle.setAttribute('aria-expanded', 'false');
        navToggle.focus();
      }
    });
    window.addEventListener('resize', placeMobileNav);
  }

  /* ---- Active nav link ---- */
  var currentPath = window.location.pathname.split('/').pop() || 'index.html';
  $$('.nav a, .mobile-nav a:not(.dash)').forEach(function (link) {
    var file = (link.getAttribute('href') || '').split('#')[0];
    if (file === currentPath) link.classList.add('active');
  });

  /* ---- One shared scroll loop (rAF-throttled) ---- */
  var progressBar = $('.progress i');
  var seq = $('.seq');
  var tl = $('.tl');
  var sticky = $('.sticky-cta');
  var heroEl = $('.hero');
  var heroBottom = heroEl ? heroEl.offsetTop + heroEl.offsetHeight : 0;
  var ticking = false;

  /* Sequence: the passport verifies itself as you scroll */
  var gates = seq ? $$('.gates li', seq) : [];
  var rows = seq ? $$('.sp li', seq) : [];
  var sheet = seq ? $('.sheet', seq) : null;
  var meter = seq ? $('.meter i', seq) : null;
  var readout = seq ? $('.meter-read output', seq) : null;
  var nowTitle = seq ? $('.seq-now strong', seq) : null;
  var nowText = seq ? $('.seq-now span', seq) : null;
  var scoreEl = seq ? $('.sheet-foot .score b', seq) : null;
  var pinned = !!(seq && gates.length && root.classList.contains('js') && !reduce && !seq.classList.contains('nopin') &&
                  window.matchMedia('(min-height: 561px)').matches);
  if (seq && !pinned) {
    seq.classList.add('static');
    root.classList.remove('seq-pinned');
    seq.style.height = 'auto';
    var stg = $('.seq-stage', seq);
    if (stg) { stg.style.position = 'static'; stg.style.height = 'auto'; }
    gates.concat(rows).forEach(function (li) { li.classList.add('on'); });
    if (sheet) sheet.classList.add('done');
    if (readout) readout.textContent = '100';
    var skipLink = $('.meter-read a', seq);
    if (skipLink) skipLink.style.display = 'none';
  }
  var lastN = -1;
  function updateSeq() {
    var r = seq.getBoundingClientRect();
    var span = r.height - window.innerHeight;
    var p = span > 0 ? clamp(-r.top / span, 0, 1) : 1;
    var n = gates.length;
    var steps = clamp(Math.floor(p / 0.84 * (n + 0.4)), 0, n);
    if (meter) meter.style.setProperty('--p', p.toFixed(3));
    if (readout) readout.textContent = Math.round(p * 100);
    if (steps !== lastN) {
      lastN = steps;
      gates.forEach(function (li, i) { li.classList.toggle('on', i < steps); });
      rows.forEach(function (li, i) { li.classList.toggle('on', i < steps); });
      if (sheet) sheet.classList.toggle('done', steps >= n);
      if (nowTitle && gates.length) {
        var g = gates[clamp(steps - 1, 0, n - 1)];
        var s = $('strong', g), t = $('p', g);
        nowTitle.textContent = steps === 0 ? 'Starting checks' : s.textContent;
        nowText.textContent = steps === 0 ? 'Scroll to run each check in turn.' : (t ? t.textContent : '');
      }
      if (scoreEl) {
        var target = Math.round(97 * steps / n);
        scoreEl.textContent = target;
      }
    }
  }

  function updateTimeline() {
    var r = tl.getBoundingClientRect();
    var mid = window.innerHeight * 0.6;
    var p = clamp((mid - r.top) / r.height, 0, 1);
    tl.style.setProperty('--fill', p.toFixed(3));
    $$('li', tl).forEach(function (li) {
      var lr = li.getBoundingClientRect();
      li.classList.toggle('on', lr.top < mid);
    });
  }

  function onScroll() {
    ticking = false;
    var y = window.scrollY || window.pageYOffset;
    if (progressBar) {
      var max = root.scrollHeight - window.innerHeight;
      progressBar.style.transform = 'scaleX(' + (max > 0 ? clamp(y / max, 0, 1) : 0).toFixed(4) + ')';
    }
    if (header) header.classList.toggle('stuck', y > 8);
    if (sticky && heroEl) {
      var inSeq = false;
      if (seq) { var sr = seq.getBoundingClientRect(); inSeq = sr.top < window.innerHeight && sr.bottom > 0 && pinned; }
      var show = y > heroBottom - 200 && !inSeq;
      sticky.classList.toggle('show', show);
      doc.body.classList.toggle('has-sticky', show);
    }
    if (pinned && seq) updateSeq();
    if (tl && !reduce && root.classList.contains('js')) updateTimeline();
  }
  function req() { if (!ticking) { ticking = true; window.requestAnimationFrame(onScroll); } }
  window.addEventListener('scroll', req, { passive: true });
  window.addEventListener('resize', function () {
    if (heroEl) heroBottom = heroEl.offsetTop + heroEl.offsetHeight;
    req();
  });
  if (tl && (reduce || !root.classList.contains('js'))) $$('li', tl).forEach(function (li) { li.classList.add('on'); });
  onScroll();

  /* ---- Scroll reveal ---- */
  var reveals = $$('.reveal');
  if (reveals.length) {
    if (hasIO && !reduce) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
        });
      }, { threshold: 0.1, rootMargin: '0px 0px -6% 0px' });
      reveals.forEach(function (el) { io.observe(el); });
    } else {
      reveals.forEach(function (el) { el.classList.add('in'); });
    }
  }

  /* ---- Pause long-running animations while off screen ---- */
  if (hasIO) {
    $$('.hero, .ticker').forEach(function (el) {
      new IntersectionObserver(function (es) { el.classList.toggle('off', !es[0].isIntersecting); }).observe(el);
    });
  }

  /* ---- Count-up numbers ---- */
  function countUp(el) {
    var target = parseFloat(el.dataset.count);
    var suffix = el.dataset.suffix || '';
    if (reduce) { el.textContent = target.toLocaleString('en-GB') + suffix; return; }
    var start = null, dur = 1400;
    function step(ts) {
      if (!start) start = ts;
      var p = Math.min((ts - start) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.floor(eased * target).toLocaleString('en-GB') + suffix;
      if (p < 1) window.requestAnimationFrame(step);
      else el.textContent = target.toLocaleString('en-GB') + suffix;
    }
    window.requestAnimationFrame(step);
  }
  var counters = $$('[data-count]');
  if (counters.length && hasIO) {
    var cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { countUp(e.target); cio.unobserve(e.target); }
      });
    }, { threshold: 0.6 });
    counters.forEach(function (el) { cio.observe(el); });
  }

  /* ---- Phone and WhatsApp (hidden until numbers are set) ---- */
  var phoneNumber = ''; // TODO: set phone number e.g. '01252 900 100'
  if (phoneNumber) {
    $$('[data-phone]').forEach(function (el) {
      el.href = 'tel:' + phoneNumber.replace(/\s/g, '');
      el.textContent = phoneNumber;
      el.style.display = '';
    });
  }
  var waNumber = ''; // TODO: set WhatsApp number e.g. '447123456789'
  var wa = $('.wa');
  if (wa && waNumber) {
    wa.href = 'https://wa.me/' + waNumber;
    wa.classList.add('show');
  } else if (wa) {
    wa.remove();
  }

  /* ---- Form keys: filled at runtime from secrets.js, which is deployed but
         not committed to the repository. Without JS the form cannot submit. ---- */
  if (window.PRJGENUI && window.PRJGENUI.web3formsKey) {
    $$('form[action^="https://api.web3forms.com"] input[name="access_key"]').forEach(function (i) {
      i.value = window.PRJGENUI.web3formsKey;
    });
  }

  /* ---- Forms: send to Web3Forms in the background, then go to thanks.html.
         Without JS the form posts normally and Web3Forms shows its own page. ---- */
  $$('form[data-redirect]').forEach(function (form) {
    if (!window.fetch || !window.FormData) return;
    var status = $('.form-status', form);
    var btn = $('button[type="submit"]', form);
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!form.checkValidity()) { form.reportValidity(); return; }
      var label = btn ? btn.textContent : '';
      if (btn) { btn.disabled = true; btn.textContent = 'Sending...'; }
      if (status) { status.hidden = true; status.textContent = ''; }
      fetch(form.action, { method: 'POST', body: new FormData(form), headers: { Accept: 'application/json' } })
        .then(function (r) { return r.json().then(function (d) { return { ok: r.ok && d.success !== false, d: d }; }); })
        .then(function (res) {
          if (!res.ok) throw new Error('send failed');
          window.location.href = form.dataset.redirect;
        })
        .catch(function () {
          if (btn) { btn.disabled = false; btn.textContent = label; }
          if (status) {
            status.hidden = false;
            status.textContent = 'Sorry, that did not send. Please try again, or email hello@prjgenuiworkforce.co.uk.';
          }
        });
    });
  });
})();
