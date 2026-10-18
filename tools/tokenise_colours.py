"""Turn hard-coded accent/forest rgba() values in styles.css into color-mix() on the
palette variables, so a palette swap changes every shadow and stripe too."""
import os
import re

path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'styles.css')
css = open(path, encoding='utf-8').read()

MAP = {'232,163,61': '--amber', '12,24,18': '--forest-ink', '20,39,30': '--forest-deep'}


def sub(m):
    rgb, a = m.group(1).replace(' ', ''), float(m.group(2))
    var = MAP.get(rgb)
    if not var:
        return m.group(0)
    pct = round(a * 100)
    return 'color-mix(in srgb,var(%s) %d%%,transparent)' % (var, pct)


new, n = re.subn(r'rgba\(\s*(\d+\s*,\s*\d+\s*,\s*\d+)\s*,\s*(\.?\d*\.?\d+)\s*\)', sub, css)
open(path, 'w', encoding='utf-8', newline='\n').write(new)
print('rgba values visited:', n, '| remaining mapped rgba:', len(re.findall(r'rgba\((232,163,61|12,24,18|20,39,30)', new)))
