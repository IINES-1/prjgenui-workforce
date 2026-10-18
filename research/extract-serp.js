(function(){
  const links = Array.from(document.querySelectorAll('a[href^="http"]'))
    .map(a => ({href: a.href, text: (a.innerText || '').trim().replace(/\s+/g,' ').slice(0,120)}))
    .filter(l => !/google\.|gstatic|youtube\.com\/results|accounts\./.test(l.href) && l.text.length > 3);
  const seen = new Set(); const uniq = [];
  for (const l of links){ const host = new URL(l.href).hostname; if(!seen.has(host)){ seen.add(host); uniq.push(l); } }
  const paa = Array.from(document.querySelectorAll('[data-q], [role="heading"]'))
    .map(e => (e.getAttribute('data-q') || e.innerText || '').trim())
    .filter(t => t.endsWith('?')).slice(0,20);
  const bodyText = document.body.innerText.slice(0, 7000);
  return JSON.stringify({resultHosts: uniq.slice(0,40), paa: [...new Set(paa)], bodyText}, null, 1);
})()
