/* =========================================================
   PRJGENUI Workforce - script.js
   Mobile nav, active nav link, scroll reveal, sticky CTA,
   WhatsApp float. No frameworks, no dependencies.
   ========================================================= */
(function () {
  'use strict';

  /* ---- Mobile nav toggle ---- */
  var navToggle = document.querySelector('.nav-toggle');
  var mobileNav = document.querySelector('.mobile-nav');
  if (navToggle && mobileNav) {
    navToggle.addEventListener('click', function () {
      var open = mobileNav.classList.toggle('open');
      navToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    // Close when a link is tapped
    mobileNav.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () {
        mobileNav.classList.remove('open');
        navToggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  /* ---- Active nav link (current page) ---- */
  var currentPath = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav a, .mobile-nav a:not(.dash)').forEach(function (link) {
    var file = (link.getAttribute('href') || '').split('#')[0];
    if (file === currentPath) {
      link.classList.add('active');
    }
  });

  /* ---- Scroll reveal ---- */
  var reveals = document.querySelectorAll('.reveal');
  if (reveals.length) {
    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) {
            e.target.classList.add('in');
            io.unobserve(e.target);
          }
        });
      }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
      reveals.forEach(function (el) { io.observe(el); });
    } else {
      reveals.forEach(function (el) { el.classList.add('in'); });
    }
  }

  /* ---- Sticky mobile CTA ---- */
  var sticky = document.querySelector('.sticky-cta');
  var heroEl = document.querySelector('.hero');
  if (sticky && heroEl) {
    var heroBottom = heroEl.getBoundingClientRect().bottom + window.scrollY;
    function checkSticky() {
      if (window.scrollY > heroBottom - 200) {
        sticky.classList.add('show');
        document.body.classList.add('has-sticky');
      } else {
        sticky.classList.remove('show');
        document.body.classList.remove('has-sticky');
      }
    }
    window.addEventListener('scroll', checkSticky, { passive: true });
    checkSticky();
  }

  /* ---- Phone number (hidden by default; set number to show) ---- */
  var phoneNumber = ''; // TODO: set phone number e.g. '01252 900 100'
  var phoneEls = document.querySelectorAll('[data-phone]');
  if (phoneNumber) {
    phoneEls.forEach(function (el) {
      el.href = 'tel:' + phoneNumber.replace(/\s/g, '');
      el.textContent = phoneNumber;
      el.style.display = '';
    });
  }

  /* ---- WhatsApp float (hidden by default; set number to show) ---- */
  var waNumber = ''; // TODO: set WhatsApp number e.g. '447123456789'
  var wa = document.querySelector('.wa');
  if (wa && waNumber) {
    wa.href = 'https://wa.me/' + waNumber;
    wa.classList.add('show');
  } else if (wa) {
    wa.remove();
  }

  /* ---- Count-up stats (integrated in hero) ---- */
  var statNums = document.querySelectorAll('.hero-stats .hs strong[data-count]');
  if (statNums.length && 'IntersectionObserver' in window) {
    var statIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          var el = e.target;
          var target = parseInt(el.dataset.count, 10);
          var suffix = el.dataset.suffix || '';
          var duration = 1200;
          var startTime = null;
          function step(ts) {
            if (!startTime) startTime = ts;
            var progress = Math.min((ts - startTime) / duration, 1);
            var eased = 1 - Math.pow(1 - progress, 3);
            el.textContent = Math.floor(eased * target).toLocaleString('en-GB') + suffix;
            if (progress < 1) requestAnimationFrame(step);
            else el.textContent = target.toLocaleString('en-GB') + suffix;
          }
          requestAnimationFrame(step);
          statIO.unobserve(el);
        }
      });
    }, { threshold: 0.5 });
    statNums.forEach(function (el) { statIO.observe(el); });
  }

  /* ---- Form: redirect to thanks.html on submit (for static hosting) ---- */
  var form = document.getElementById('contactForm');
  if (form) {
    form.addEventListener('submit', function (e) {
      // Web3Forms handles the POST; we just redirect after a short delay
      // so the user sees a confirmation page instead of the JSON response.
      setTimeout(function () {
        if (form.dataset.redirect) {
          window.location.href = form.dataset.redirect;
        }
      }, 800);
    });
  }
})();
