(function(){
  const cs = el => el ? getComputedStyle(el) : null;
  const rgbToHex = rgb => {
    if(!rgb) return null;
    const m = rgb.match(/\d+(\.\d+)?/g);
    if(!m || m.length < 3) return rgb;
    if(m[3] !== undefined && parseFloat(m[3]) === 0) return 'transparent';
    return '#' + m.slice(0,3).map(n => ('0' + parseInt(n,10).toString(16)).slice(-2)).join('').toUpperCase();
  };
  const body = cs(document.body);
  const header = document.querySelector('header, [role="banner"], nav, .header, #header');
  const h1 = document.querySelector('h1');
  const h2s = Array.from(document.querySelectorAll('h2')).slice(0,12).map(h => (h.innerText || '').trim().replace(/\s+/g,' ').slice(0,90));
  const buttons = Array.from(document.querySelectorAll('a.btn, a.button, button, a[class*="btn"], a[class*="button"], a[class*="cta"]'))
    .map(b => ({text: (b.innerText || '').trim().replace(/\s+/g,' ').slice(0,50), bg: rgbToHex(cs(b).backgroundColor), color: rgbToHex(cs(b).color), radius: cs(b).borderRadius}))
    .filter(b => b.text.length > 1).slice(0,10);
  const colourCount = {};
  Array.from(document.querySelectorAll('*')).slice(0,2500).forEach(el => {
    const s = cs(el);
    [s.backgroundColor, s.color].forEach(c => { const h = rgbToHex(c); if(h && h !== 'transparent' && h !== '#000000' && h !== '#FFFFFF'){ colourCount[h] = (colourCount[h] || 0) + 1; } });
  });
  const topColours = Object.entries(colourCount).sort((a,b) => b[1]-a[1]).slice(0,14).map(([c,n]) => c + ' x' + n);
  const fonts = {};
  Array.from(document.querySelectorAll('h1,h2,h3,p,a,li,span,button')).slice(0,600).forEach(el => { const f = cs(el).fontFamily.split(',')[0].replace(/["']/g,'').trim(); fonts[f] = (fonts[f] || 0) + 1; });
  const imgs = Array.from(document.images);
  const heroCandidates = Array.from(document.querySelectorAll('section, div, header')).slice(0,400).filter(el => { const s = cs(el); return s.backgroundImage && s.backgroundImage !== 'none' && el.getBoundingClientRect().height > 250; }).slice(0,3).map(el => ({tag: el.tagName, cls: (el.className||'').toString().slice(0,60), bg: cs(el).backgroundImage.slice(0,120)}));
  const phones = (document.body.innerText.match(/(\+44\s?\d{2,4}|0\d{2,4})[\s-]?\d{3,4}[\s-]?\d{3,4}/g) || []).slice(0,3);
  const trust = (document.body.innerText.match(/\b(CSCS|CHAS|SafeContractor|Constructionline|REC|SDF|NAS|PDA|Dulux|Trustpilot|Google reviews?|ISO ?9001|ISO ?45001|Gangmasters|GLAA|Right to Work|DBS)\b/gi) || []).reduce((a,t)=>{ const k=t.toUpperCase(); a[k]=(a[k]||0)+1; return a; },{});
  const nav = header ? Array.from(header.querySelectorAll('a')).map(a => (a.innerText || '').trim().replace(/\s+/g,' ')).filter(t => t && t.length < 30).slice(0,14) : [];
  return JSON.stringify({
    url: location.href, title: document.title,
    metaDesc: (document.querySelector('meta[name="description"]') || {}).content || '',
    bodyBg: rgbToHex(body.backgroundColor), bodyColor: rgbToHex(body.color), bodyFont: body.fontFamily.slice(0,80),
    headerBg: header ? rgbToHex(cs(header).backgroundColor) : null,
    h1: h1 ? {text: (h1.innerText||'').trim().replace(/\s+/g,' ').slice(0,160), size: cs(h1).fontSize, font: cs(h1).fontFamily.split(',')[0], color: rgbToHex(cs(h1).color)} : null,
    h2s, nav, buttons, topColours, fonts: Object.entries(fonts).sort((a,b)=>b[1]-a[1]).slice(0,4),
    imageCount: imgs.length, largeImages: imgs.filter(i => i.naturalWidth > 600).length, heroBgImages: heroCandidates,
    phones, trustSignals: trust,
    wordCount: (document.body.innerText || '').split(/\s+/).length,
    hasForm: !!document.querySelector('form'), hasChat: !!document.querySelector('[class*="chat"], [id*="chat"], [class*="whatsapp"], a[href*="wa.me"]')
  }, null, 1);
})()
