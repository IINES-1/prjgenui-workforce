import io

files = ['index.html', 'about.html', 'contact.html', 'privacy.html',
         'terms.html', 'workers.html', 'request.html']
old = '<li><a href="dashboard.html">Dashboard demo</a></li>'
new = '<li><a href="app/">Team sign-in</a></li>'

for f in files:
    with io.open(f, 'r', encoding='utf-8') as fh:
        src = fh.read()
    n = src.count(old)
    if n:
        src = src.replace(old, new)
        with io.open(f, 'w', encoding='utf-8', newline='') as fh:
            fh.write(src)
    print(f, 'replaced', n)
