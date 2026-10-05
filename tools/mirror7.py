"""Direction 7 (a working copy of direction 6) mirrors direction 6's inventory:
   - inventory7.html from inventory6.html,
   - vehicles7/<stock>.html from vehicles6/<stock>.html,
   - the rail on index7.html from the rail on index6.html, four cars,
each re-pointed to the direction-7 set (index7, inventory7, vehicles7 and the
-7 sheets). On the client's note of 2026-10-04: a normal, static page for an
older clientele — no scroll layer, no motion on arrival — and the routes to
the inventory, the specials, financing and contact always on screen.
build.py runs this after mirror6.py; on its own: python3 tools/mirror7.py"""
import os, re, hashlib

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..') + '/'

def read(p):  return open(ROOT + p, encoding='utf-8').read()
def write(p, s): open(ROOT + p, 'w', encoding='utf-8', newline='\n').write(s)

# Every rewrite leaves a string the next run cannot match again, so
# mirroring is idempotent.
SWAP = [
    ('index6.html',        'index7.html'),
    ('css/index6.css',     'css/index7.css'),
    ('css/inventory6.css', 'css/inventory7.css'),
    ('css/vehicle6.css',   'css/vehicle7.css'),
    ('css/day6.css',       'css/day7.css'),
    ('js/index6.js',       'js/index7.js'),
    ('inventory6.html',    'inventory7.html'),
    ('vehicles6/',         'vehicles7/'),
]
def seven(s):
    for a, b in SWAP:
        s = s.replace(a, b)
    return s

# No scroll layer and no motion on arrival: Lenis goes, and the page opens
# without the `motion` class, so every script and sheet takes its finished,
# static composition. css/static7.css loads last; js/page7.js keeps the one
# measurement the sheets need.
LENIS = re.compile(r'<link rel="stylesheet" href="https://cdn\.jsdelivr\.net/npm/lenis[^"]*">\n'
                   r'|<script src="https://cdn\.jsdelivr\.net/npm/lenis[^"]*" defer></script>\n'
                   r'|<script src="(?:\.\./)?js/lenis6\.js[^"]*" defer></script>\n')
DAY = re.compile(r'<link rel="stylesheet" href="((?:\.\./)?)css/day7\.css[^"]*">\n')
def calm(s):
    s = LENIS.sub('', s)
    s = s.replace('<html lang="en" class="motion">', '<html lang="en">', 1)
    s = s.replace('/* Direction 6: the look is the link', '/* Direction 7 keeps direction 6\'s look: the look is the link', 1)
    if 'css/static7.css' not in s:
        m = DAY.search(s)
        pre = m.group(1)
        s = s[:m.end()] + (f'<link rel="stylesheet" href="{pre}css/static7.css">\n'
                           f'<script src="{pre}js/page7.js" defer></script>\n') + s[m.end():]
    return s

# The routes the client wants on screen at all times (2026-10-04): the
# inventory first and filled, then the specials, financing and contact (the
# retailer's own form). On a wide screen they are the header's second line;
# below 1024 the same list is the bar at the foot of the screen.
SPECIALS = 'https://www.bramanbentleypalmbeach.com/search/special-west-palm-beach-fl/?cy=33409&amp;tp=special'
FINANCE = 'https://www.bramanbentleypalmbeach.com/finance-department/'
CONTACT = 'https://www.bramanbentleypalmbeach.com/contact-us/'
def deck(s, pre, here=''):
    if 'mh__deck' in s:
        return s
    cur = ' aria-current="page"' if here == 'inventory' else ''
    nav = (f'\n  <nav class="mh__deck" aria-label="Shop">\n'
           f'    <a class="mh__deck-main" href="{pre}inventory7.html"{cur}>Bentley Inventory</a>\n'
           f'    <a href="{SPECIALS}">Special Offers</a>\n'
           f'    <a href="{FINANCE}">Financing</a>\n'
           f'    <a href="{CONTACT}">Contact Us</a>\n'
           f'  </nav>\n')
    s = s.replace('\n</header>', nav + '</header>', 1)
    # the menu (a phone, a tablet) keeps every route; on a wide screen the
    # four the deck carries leave the first line, so nothing is said twice
    s = re.sub(r'<li>(<a href="[^"]*inventory7\.html"[^>]*>Inventory</a>)</li>',
               lambda m: f'<li class="mh__nav-deck">{m.group(1)}</li>\n        '
                         f'<li class="mh__nav-deck"><a href="{SPECIALS}">Special Offers</a></li>', s, count=1)
    s = s.replace(f'<li><a href="{FINANCE}">Finance</a></li>', f'<li class="mh__nav-deck"><a href="{FINANCE}">Finance</a></li>', 1)
    s = s.replace('<li><a href="https://blog.bramanbentleypalmbeach.com/">Blog</a></li>',
                  '<li><a href="https://blog.bramanbentleypalmbeach.com/">Blog</a></li>\n        '
                  f'<li class="mh__nav-deck"><a href="{CONTACT}">Contact Us</a></li>', 1)
    return s

# Direction 7's own sheets and scripts are stamped with their content, so a
# browser (and GitHub Pages' cache) fetches them again whenever they change
OWN = ['css/index7.css', 'css/inventory7.css', 'css/vehicle7.css', 'css/day7.css', 'css/static7.css',
       'js/index7.js', 'js/page7.js']
STAMPS = {f: hashlib.md5(open(ROOT + f, 'rb').read()).hexdigest()[:10] for f in OWN}
def stamp7(s):
    for f, h in STAMPS.items():
        s = re.sub(r'(' + re.escape(f) + r')(\?v=[^"]*)?"', lambda m: m.group(1) + '?v=' + h + '"', s)
    return s

def page(s, pre, here=''):
    return stamp7(deck(calm(seven(s)), pre, here))

# 1. The SRP
write('inventory7.html', page(read('inventory6.html'), '', 'inventory'))

# 2. The vehicle pages — cars no longer in direction 6 are removed here too
os.makedirs(ROOT + 'vehicles7', exist_ok=True)
pages = sorted(f for f in os.listdir(ROOT + 'vehicles6') if f.endswith('.html'))
for f in os.listdir(ROOT + 'vehicles7'):
    if f.endswith('.html') and f not in pages:
        os.remove(ROOT + 'vehicles7/' + f)
for f in pages:
    write('vehicles7/' + f, page(read('vehicles6/' + f), '../'))

# 3. The home page: index6's rail, re-pointed, four cars and no more (the
# client's note of 2026-10-04: four; three in view, centred, the arrows at
# the sides bring the fourth — Alex, 2026-10-05)
idx6, idx7 = read('index6.html'), read('index7.html')
rail = re.search(r'<ul class="stock__rail"[^>]*>.*?</ul>', idx6, re.S)
if rail:
    cars = re.findall(r'\n\s*<li class="card[^"]*"[^>]*>.*?</li>', rail.group(0), re.S)[:4]
    four = ('<ul class="stock__rail stock__four" tabindex="0" aria-label="New Bentley in stock; use the arrows or scroll sideways">'
            + ''.join(cars) + '\n      </ul>')
    idx7 = re.sub(r'<ul class="stock__rail[^"]*"[^>]*>.*?</ul>', lambda m: seven(four), idx7, count=1, flags=re.S)
write('index7.html', page(idx7, ''))

print("inventory7.html,", len(pages), "vehicle pages in vehicles7/, index7 rail")
