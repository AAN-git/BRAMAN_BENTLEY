"""Direction 5 (coastal) mirrors direction 4's inventory:
   - inventory5.html from inventory.html,
   - vehicles5/<stock>.html from vehicles/<stock>.html,
   - the rail on index5.html from the rail on index4.html,
each with its links re-pointed to the direction-5 set (index5, inventory5,
vehicles5, and the -5 stylesheets). Direction 5's look lives only in its
stylesheets, so the markup can be mirrored again after every build.
build.py runs this last; it can also be run on its own: python3 tools/mirror5.py"""
import os, re, hashlib

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..') + '/'

# Every rewrite leaves a string the next run cannot match again
# ('vehicles5/' does not contain 'vehicles/'), so mirroring is idempotent.
SWAP = [
    ('index4.html',        'index5.html'),
    ('css/index4.css',     'css/index5.css'),
    ('css/inventory.css',  'css/inventory5.css'),
    ('css/vehicle.css',    'css/vehicle5.css'),
    ('inventory.html',     'inventory5.html'),
    ('vehicles/',          'vehicles5/'),
]
def five(s):
    for a, b in SWAP:
        s = s.replace(a, b)
    return s

def read(p):  return open(ROOT + p, encoding='utf-8').read()
def write(p, s): open(ROOT + p, 'w', encoding='utf-8', newline='\n').write(s)

# Direction 5's header also carries the retailer's blog, after About
ABOUT = '<li><a href="https://www.bramanbentleypalmbeach.com/about-us/">About</a></li>'
BLOG = '<li><a href="https://blog.bramanbentleypalmbeach.com/">Blog</a></li>'
def blog(s):
    return s if BLOG in s else s.replace(ABOUT, ABOUT + '\n        ' + BLOG, 1)

# Direction 5's vehicle page: the car's facts leave the offer plate and
# stand under the key figures in the main column, as one column
FACTS = re.compile(r'\n\s*<dl class="offer__rows offer__facts">.*?</dl>', re.S)
KEYS = re.compile(r'(<dl class="keys step"[^>]*>.*?</dl>)', re.S)
def facts(s):
    m = FACTS.search(s)
    if not m:
        return s
    dl = m.group(0).strip().replace('class="offer__rows offer__facts"', 'class="specs step" data-reveal style="--i:1"', 1)
    s = s[:m.start()] + s[m.end():]
    return KEYS.sub(lambda k: k.group(1) + '\n        ' + dl, s, count=1)

# Direction 5's lease specials: where the retailer offers a lease on a car,
# the monthly payment is the mark on its photograph, in the place and the
# style of the retailer's own "Internet special" flag (the same twelve cars
# carry both) — on the card, and on the first frame of the car's page. The
# card's quiet "Lease ... a month" line goes: the flag says it.
LEASE_LINE = re.compile(r'<span>Lease (\$[\d,]+) a month</span>')
CARD = re.compile(r'<li class="card[^"]*"[^>]*>.*?</li>', re.S)
def lease_flag(amount):
    return f'<span class="card__flag card__flag--lease">Lease {amount} + tax / mo</span>'
def lease_cards(s):
    def one(m):
        card = m.group(0)
        line = LEASE_LINE.search(card)
        if not line:
            return card
        flag = lease_flag(line.group(1))
        card = LEASE_LINE.sub('', card, count=1)
        if '<span class="card__flag">' in card:
            return re.sub(r'<span class="card__flag">[^<]*</span>', flag, card, count=1)
        return card.replace('<span class="card__media">', '<span class="card__media">' + flag, 1)
    return CARD.sub(one, s)
SPECIAL = re.compile(r'<p class="special__figure">(\$[\d,]+) <span>a month</span>')
def lease_page(s):
    m = SPECIAL.search(s)
    if not m:
        return s
    s = s.replace('<p class="offer__flag label">Internet special</p>', '<p class="offer__flag label">Lease special</p>', 1)
    first = re.search(r'<button class="film__open"[^>]*>', s)
    return s[:first.end()] + lease_flag(m.group(1)) + s[first.end():] if first else s

# Direction 5's vehicle page: the CARFAX mark on every pre-owned car, beside
# the dealer's notes in the description, as on the Rolls-Royce pages. The
# dealer's listing has no report link, so the mark stands without one.
NOTES = re.compile(r'<ul class="vdp__notes">.*?</ul>', re.S)
CARFAX_MARK = ('<span class="carfax"><img src="../assets/icons/carfax/carfax.svg" '
               'width="169" height="40" alt="CARFAX vehicle history reports"></span>')
def carfax(s):
    m = NOTES.search(s)
    if not m or 'CARFAX' not in m.group(0) or 'class="carfax"' in s:
        return s
    return s[:m.start()] + '<div class="vdp__marks">' + CARFAX_MARK + m.group(0) + '</div>' + s[m.end():]

# Direction 5's own sheets and script are stamped with their content, so a
# browser (and GitHub Pages' cache) fetches them again whenever they change
OWN = ['css/index5.css', 'css/inventory5.css', 'css/vehicle5.css', 'js/index5.js']
STAMPS = {f: hashlib.md5(open(ROOT + f, 'rb').read()).hexdigest()[:10] for f in OWN}
def stamp5(s):
    for f, h in STAMPS.items():
        s = re.sub(r'(' + re.escape(f) + r')(\?v=[^"]*)?"', lambda m: m.group(1) + '?v=' + h + '"', s)
    return s

# 1. The SRP
write('inventory5.html', stamp5(lease_cards(blog(five(read('inventory.html'))))))

# 2. The vehicle pages — cars no longer in direction 4 are removed here too
os.makedirs(ROOT + 'vehicles5', exist_ok=True)
pages = sorted(f for f in os.listdir(ROOT + 'vehicles') if f.endswith('.html'))
for f in os.listdir(ROOT + 'vehicles5'):
    if f.endswith('.html') and f not in pages:
        os.remove(ROOT + 'vehicles5/' + f)
for f in pages:
    write('vehicles5/' + f, stamp5(carfax(lease_page(lease_cards(facts(blog(five(read('vehicles/' + f)))))))))

# MOCK-UP ONLY: the retailer's data marks no car sold or pending, so the home
# rail shows the two other flags on two cars to present them (Alex,
# 2026-09-24). Remove these entries once the data carries a real status.
DEMO_FLAGS = {
    'V69245': ('pending', 'Sale pending'),
    'V68412': ('sold', 'Sold'),
}
def demo_flags(s):
    def one(m):
        card = m.group(0)
        stock = re.search(r'data-stock="([^"]+)"', card)
        if not stock or stock.group(1) not in DEMO_FLAGS or 'card__flag' in card:
            return card
        kind, text = DEMO_FLAGS[stock.group(1)]
        flag = f'<span class="card__flag card__flag--{kind}">{text}</span>'
        return card.replace('<span class="card__media">', '<span class="card__media">' + flag, 1)
    return CARD.sub(one, s)

# 3. The home page: index4's rail, re-pointed, and index5's own links
idx4, idx5 = read('index4.html'), read('index5.html')
rail = re.search(r'<ul class="stock__rail"[^>]*>.*?</ul>', idx4, re.S)
if rail:
    idx5 = re.sub(r'<ul class="stock__rail"[^>]*aria-label="New Bentley in stock[^>]*>.*?</ul>', lambda m: demo_flags(lease_cards(five(rail.group(0)))), idx5, count=1, flags=re.S)
idx5 = idx5.replace('href="inventory.html', 'href="inventory5.html').replace('href="vehicles/', 'href="vehicles5/')
write('index5.html', stamp5(idx5))

print('inventory5.html,', len(pages), 'vehicle pages in vehicles5/, index5 rail')
