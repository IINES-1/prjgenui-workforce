// Run via: agent-browser eval --stdin < tools/font_check.js
// Reports which font faces loaded and what key elements actually render in.
(() => {
  const ff = (sel) => {
    const el = document.querySelector(sel);
    if (!el) return sel + ': MISSING';
    const cs = getComputedStyle(el);
    const fam = cs.fontFamily.split(',')[0].replace(/["']/g, '');
    return `${sel}: ${fam} ${cs.fontWeight} ${cs.fontStyle} ${cs.fontSize}`;
  };
  const faces = [...document.fonts].map(f => `${f.family} ${f.weight} ${f.style} -> ${f.status}`);
  const header = document.querySelector('.header .wrap, header .wrap, .site-header .wrap, header');
  const brand = document.querySelector('.brand');
  const cta = document.querySelector('.header-cta .btn, .header-cta a.btn');
  const navLinks = [...document.querySelectorAll('.nav a')];
  const tops = navLinks.map(a => Math.round(a.getBoundingClientRect().top));
  const sameRow = tops.length ? tops.every(t => Math.abs(t - tops[0]) < 4) : null;
  const h1 = document.querySelector('h1');
  return JSON.stringify({
    viewport: `${innerWidth}x${innerHeight}`,
    archivoReady: document.fonts.check('800 1em Archivo'),
    plexReady: document.fonts.check("400 1em 'IBM Plex Sans'"),
    faces,
    rendered: [
      ff('body'), ff('h1'), ff('h2'), ff('h3'), ff('h4'),
      ff('.brand .word'), ff('.brand .mark'), ff('em.gold'),
      ff('.hero-stats .hs strong'), ff('.readiness .score'),
      ff('.product .num'), ff('.gates .g'), ff('.timeline .time'),
      ff('.metric .n'), ff('.result .n'), ff('.faq summary'),
      ff('.contact-copy .next li span'), ff('.btn'), ff('.query'),
    ],
    headerHeight: header ? Math.round(header.getBoundingClientRect().height) : null,
    brandWidth: brand ? Math.round(brand.getBoundingClientRect().width) : null,
    ctaVisible: cta ? getComputedStyle(cta).display !== 'none' : null,
    navLinkCount: navLinks.length,
    navSingleRow: sameRow,
    h1Lines: h1 ? Math.round(h1.getBoundingClientRect().height / parseFloat(getComputedStyle(h1).lineHeight)) : null,
    h1Text: h1 ? h1.textContent.trim() : null,
    docWidthOverflow: document.documentElement.scrollWidth > innerWidth,
  }, null, 1);
})();
