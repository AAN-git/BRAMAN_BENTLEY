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
OWN = ['css/system.css', 'css/index7.css', 'css/inventory7.css', 'css/vehicle7.css', 'css/day7.css', 'css/static7.css',
       'js/index7.js', 'js/page7.js']
STAMPS = {f: hashlib.md5(open(ROOT + f, 'rb').read()).hexdigest()[:10] for f in OWN}
def stamp7(s):
    for f, h in STAMPS.items():
        s = re.sub(r'(' + re.escape(f) + r')(\?v=[^"]*)?"', lambda m: m.group(1) + '?v=' + h + '"', s)
    return s

# The client, 2026-10-05: "Range" reads "Model Range" (as the chapter it
# leads to says), and the site terms are in the first screen on a phone too.
TERMS = 'https://www.bramanbentleypalmbeach.com/terms-and-conditions/'
def model_range(s):
    return re.sub(r'(<li><a href="[^"]*#range">)Range(</a></li>)', r'\1Model Range\2', s)
# the way into a model page is the home page's Model Range (Alex, 2026-10-26):
# a model's tile opens its page where one is built, its cars in stock otherwise
MODEL_PAGES = {'Bentayga': 'bentayga-speed7.html', 'Flying Spur': 'flying-spur7.html', 'Torcal': 'torcal7.html',
               'Continental GT': 'continental-gt7.html', 'Continental GT Convertible': 'continental-gtc7.html'}
def range_tiles(s, pre):
    def one(m):
        name = re.search(r'<span class="range__name">([^<]+)</span>', m.group(0)).group(1)
        return re.sub(r'<a href="[^"]*">', f'<a href="{pre}{MODEL_PAGES[name]}">', m.group(0), count=1) if name in MODEL_PAGES else m.group(0)
    return re.sub(r'<li class="range__item[^"]*"[^>]*>.*?</li>', one, s, flags=re.S)
def terms_line(s):
    if 'mh__terms-line' in s:
        return s
    line = f'\n  <div class="mh__terms-line"><a href="{TERMS}">Site Terms &amp; Conditions</a></div>'
    return s.replace('\n  <nav class="mh__deck"', line + '\n  <nav class="mh__deck"', 1)

# Direction 7's own inner pages (tools/subpages7.py, 2026-10-23): every
# route to the retailer's contact and finance pages lands on ours instead
INNER = {CONTACT: 'contact7.html', FINANCE: 'finance7.html',
         'https://www.bramanbentleypalmbeach.com/about-us/': 'about7.html',
         'https://www.bramanbentleypalmbeach.com/meet-our-staff/': 'about7.html#team',
         'https://www.bramanbentleypalmbeach.com/parts-department/': 'parts7.html',
         'https://www.bramanbentleypalmbeach.com/sell-your-vehicle/': 'sell7.html',
         'https://www.bramanbentleypalmbeach.com/payment-calculator/': 'calculator7.html'}
def inner(s, pre):
    for url, f in INNER.items():
        s = s.replace(f'href="{url}"', f'href="{pre}{f}"')
    return s

# The menu (Alex, 2026-10-26): the demo site's own navigation, so every page of
# the site can be reached from ours, and each route says where it lands — on
# our page where we have one, on the demo's where we do not yet (marked
# data-demo, so what is left to rebuild can be counted). As on the demo, less
# "Browse by Make" (other brands may not be advertised — the client's note) and
# "One-Owner Vehicles" (on the demo it opens the whole pre-owned list).
DEMO = 'https://bramanbentleypalmbeach.aandemo.com'
def _r(label, href): return (label, href)
MENU = [
    ('Home', 'index7.html'),
    ('New', [
        ('New Bentley Inventory', [
            _r('Search All New Bentley', 'inventory7.html?condition=new'),
            _r('Search Bentayga', 'inventory7.html?condition=new&amp;model=Bentayga'),
            _r('Search Continental Convertible', 'inventory7.html?condition=new&amp;model=Continental+GTC'),
            _r('Search Continental Coupe', 'inventory7.html?condition=new&amp;model=Continental+GT'),
            _r('Search Flying Spur', 'inventory7.html?condition=new&amp;model=Flying+Spur'),
            _r('Search Bentayga EWB', 'inventory7.html?condition=new&amp;model=Bentayga+EWB')]),
        ('Shopping Tools', [
            _r('Schedule Test Drive', '/schedule-new-vehicle-test-drive/'),
            _r('Sell Us Your Vehicle', 'sell7.html'),
            _r('Home Delivery Program', '/bentley-home-delivery-program/'),
            _r('Online Buying Program', '/bentley-home-delivery-program/'),
            _r('Get a Quote', '/new-vehicle-quick-quote/'),
            _r('Value Your Trade', '/value-trade-in/'),
            _r('Build Your Own', 'https://www.bentleymotors.com/en/misc/car-configurator.html')]),
        ('Research', [
            _r('Reasons to Choose Braman', '/bentley-palm-beach-difference/'),
            _r('Bentley Test Drive Videos', '/bentley-palm-beach-test-drive-videos/'),
            _r('Current Incentives', '/incentives/'),
            _r('Bentayga Speed', 'bentayga-speed7.html'),
            _r('Continental GT Speed Edition 12', '/continental-gt-speed-edition-12/'),
            _r('Flying Spur Speed Edition 12', '/flying-spur-speed-edition-12/'),
            _r('The New Bentayga Extended Wheelbase', '/bentayga-extended-wheelbase/')]),
    ]),
    ('Pre-Owned', [
        ('Pre-Owned Inventory', [
            _r('All Pre-Owned Vehicles', 'inventory7.html?condition=used'),
            _r('Certified Pre-Owned', 'inventory7.html?condition=certified'),
            _r('What is a Braman Certified Pre-Owned?', '/braman-bentley-cpo/')]),
        ('Shopping Tools', [
            _r('Sell Us Your Vehicle', 'sell7.html'),
            _r('Find My Car', '/find-my-car/'),
            _r('Schedule Test Drive', '/schedule-used-vehicle-test-drive/'),
            _r('Home Delivery Program', '/bentley-home-delivery-program/'),
            _r('Online Buying Program', '/bentley-home-delivery-program/'),
            _r('Value Your Trade', '/value-trade-in/'),
            _r('Get a Quote', '/used-vehicle-quick-quote/')]),
    ]),
    ('Offers', [('', [
        _r('New Vehicle Specials', '/new-inventory-specials/'),
        _r('Pre-Owned Vehicle Specials', '/used-inventory-specials/')])]),
    ('Service', [('', [
        _r('Service Department', '/service-department/'),
        _r('Ask a Tech', 'ask-a-tech7.html'),
        _r('Vehicle Recall Request', '/vehicle-recall-request/')])]),
    ('Parts', [('', [
        _r('Parts Department', 'parts7.html'),
        _r('Order Parts', '/order-parts/')])]),
    ('Finance', [('', [
        _r('Finance Department', 'finance7.html'),
        _r('Personal Finance Application', '/finance-application/'),
        _r('Business Finance Application', '/business-finance-app/'),
        _r('Payment Calculator', 'calculator7.html')])]),
    ('About', [('', [
        _r('About Us', 'about7.html'),
        _r('Hours', '/hours/'),
        _r('Meet the Staff', 'about7.html#team'),
        _r('Contact Us', 'contact7.html'),
        _r('Testimonials', '/DR-reviews/'),
        _r('Dealership Informational Videos', '/informational-videos/'),
        _r('Bentley Test Drive Videos', '/bentley-palm-beach-test-drive-videos/'),
        _r('Home Delivery Program', '/bentley-home-delivery-program/'),
        _r('Bentley Blog', 'https://blog.bramanbentleypalmbeach.com/'),
        _r('Magazine', 'http://www.clubbraman.com/magazine/'),
        _r('Join Our Team', 'https://www.bramanmotorcars.com/current-job-opportunities/'),
        _r('Privacy Policy', '/privacy-policy/')])]),
]
def _href(h, pre):
    if h.startswith('/'): return f'{DEMO}{h}" data-demo="'   # a demo page: not rebuilt on ours yet
    if h.startswith('http'): return h
    return pre + h
def menu(s, pre):
    # written afresh on every run (the whole <nav>), so an edit to MENU reaches
    # every page, the hand-made home page too
    items = []
    for i, (top, body) in enumerate(MENU):
        if isinstance(body, str):
            items.append(f'        <li class="mh__item"><a href="{_href(body, pre)}">{top}</a></li>')
            continue
        pid = 'm-' + top.lower().replace('-', '')
        groups = ''
        for head, links in body:
            h = f'<p class="mh__group-h">{head}</p>' if head else ''
            lis = ''.join(f'<li><a href="{_href(u, pre)}">{t}</a></li>' for t, u in links)
            groups += f'<div class="mh__group">{h}<ul>{lis}</ul></div>'
        wide = ' mh__panel--wide' if len(body) > 1 else (' mh__panel--cols' if len(body[0][1]) > 6 else '')
        items.append(f'        <li class="mh__item mh__item--sub"><button class="mh__open" type="button" aria-expanded="false" aria-controls="{pid}">{top}</button>'
                     f'<div class="mh__panel{wide}" id="{pid}"><div class="mh__panel-in">{groups}</div></div></li>')
    terms = f'        <li class="mh__nav-terms"><a href="{TERMS}">Site Terms &amp; Conditions</a></li>'
    ul = '<ul class="mh__menu">\n' + '\n'.join(items) + '\n' + terms + '\n      </ul>'
    return re.sub(r'(<nav class="mh__nav" id="nav" aria-label="Primary">).*?(</nav>)', lambda m: m.group(1) + '\n      ' + ul + '\n    ' + m.group(2), s, count=1, flags=re.S)

# The client's testing notes (and the demo): no "Bentley Palm Beach" before the
# number in the bar, and the number written with dashes
PHONE = re.compile(r'(>[^<]*?)\b(561) (\d{3}) (\d{4})\b')
def retailer(s):
    s = s.replace('<span>Bentley Palm Beach</span><span class="mh__tel">561 926 9111</span>',
                  '<span class="mh__tel">561-926-9111</span>')
    # every number on the page, as the client asked (home: Expert care, the
    # location) and the design system writes it — the text only, not tel:
    while PHONE.search(s): s = PHONE.sub(r'\1\2-\3-\4', s)
    return s

# The client's form on the car page too (Alex, 2026-10-26: one form wherever a
# form is): the inner pages' fields, two columns; the car's message kept
FORM_HEAD = '''<label class="field"><span class="field__label">First name*</span><input class="field__input" type="text" name="fname" autocomplete="given-name" required></label>
          <label class="field"><span class="field__label">Last name*</span><input class="field__input" type="text" name="lname" autocomplete="family-name" required></label>
          <label class="field"><span class="field__label">Email*</span><input class="field__input" type="email" name="email" autocomplete="email" required></label>
          <label class="field"><span class="field__label">Phone*</span><input class="field__input" type="tel" name="phone" autocomplete="tel" required></label>
          <fieldset class="field sub__choice">
            <legend class="field__label">Best time to contact*</legend>
            <label><input type="radio" name="contact_mode" value="Morning"> Morning</label>
            <label><input type="radio" name="contact_mode" value="Afternoon"> Afternoon</label>
            <label><input type="radio" name="contact_mode" value="Evening"> Evening</label>
          </fieldset>
          '''
FORM_TAIL = ('<label class="field field--wide sub__consent"><input type="checkbox" name="i_agree"> Please note that by completing this form, you agree to being contacted via text, phone and email.</label>\n'
             '          <div class="enquire__send"><button class="btn" type="submit">Send message</button><span class="enquire__fine">This site is protected by reCAPTCHA and the Google Privacy Policy and Terms of Service apply.</span></div>')
OLD_FIELDS = re.compile(r'<label class="field"><span class="field__label">Name</span>.*?<label class="field"><span class="field__label">Telephone</span>[^\n]*\n\s*', re.S)
OLD_SEND = re.compile(r'<div class="enquire__send"><button class="btn" type="submit">Send enquiry</button>.*?</div>')
def form(s):
    if 'sub__choice' in s or 'enquire__form' not in s:
        return s
    s = OLD_FIELDS.sub(lambda m: FORM_HEAD, s, count=1)
    return OLD_SEND.sub(lambda m: FORM_TAIL, s, count=1)

# Certified Pre-Owned as a card's mark (Alex, 2026-10-26): a certified car with
# no other mark carries it in the band under its photograph, and the line over
# its name no longer repeats it; a certified car with a lease keeps the lease
# in the band and "Certified by Bentley" in the line, so nothing is lost
CARD_LI = re.compile(r'<li class="card[^"]*"[^>]*data-certified="1"[^>]*>.*?</li>', re.S)
def cpo(s):
    def one(m):
        c = m.group(0)
        if 'card__flag' in c:
            return c
        c = c.replace('<span class="card__media">', '<span class="card__media"><span class="card__flag card__flag--cpo">Certified Pre-Owned</span>', 1)
        c = c.replace('Pre-owned · <b>Certified by Bentley, one owner</b>', 'Pre-owned · One owner', 1)
        c = c.replace('Pre-owned · <b>Certified by Bentley</b>', 'Pre-owned', 1)
        return c
    return CARD_LI.sub(one, s)

# the car page's first photograph carries no flag: nothing may cover the car
# (the client's Bentley note), and the lease is already the offer's own, under
# its flag "Lease special" beside the photographs
FILM_FLAG = re.compile(r'(<button class="film__open"[^>]*>)<span class="card__flag[^"]*">(?:<span[^>]*>[^<]*</span>)+</span>')
def film_flag(s):
    return FILM_FLAG.sub(r'\1', s)

def page(s, pre, here=''):
    return stamp7(film_flag(cpo(form(retailer(menu(range_tiles(inner(terms_line(model_range(deck(calm(seven(s)), pre, here))), pre), pre), pre))))))

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
