"""Direction 6 (a working copy of direction 5) mirrors direction 4's inventory:
   - inventory6.html from inventory.html,
   - vehicles6/<stock>.html from vehicles/<stock>.html,
   - the rail on index6.html from the rail on index4.html,
each with its links re-pointed to the direction-6 set (index6, inventory6,
vehicles6, and the -6 stylesheets). Direction 6's look lives only in its
stylesheets, so the markup can be mirrored again after every build.
build.py runs this last; it can also be run on its own: python3 tools/mirror6.py"""
import os, re, hashlib

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..') + '/'

# Every rewrite leaves a string the next run cannot match again
# ('vehicles6/' does not contain 'vehicles/'), so mirroring is idempotent.
SWAP = [
    ('index4.html',        'index6.html'),
    ('css/index4.css',     'css/index6.css'),
    ('css/inventory.css',  'css/inventory6.css'),
    ('css/vehicle.css',    'css/vehicle6.css'),
    ('inventory.html',     'inventory6.html'),
    ('vehicles/',          'vehicles6/'),
]
def six(s):
    for a, b in SWAP:
        s = s.replace(a, b)
    return s

def read(p):  return open(ROOT + p, encoding='utf-8').read()
def write(p, s): open(ROOT + p, 'w', encoding='utf-8', newline='\n').write(s)

# Direction 6's header also carries the retailer's blog, after About
ABOUT = '<li><a href="https://www.bramanbentleypalmbeach.com/about-us/">About</a></li>'
BLOG = '<li><a href="https://blog.bramanbentleypalmbeach.com/">Blog</a></li>'
def blog(s):
    return s if BLOG in s else s.replace(ABOUT, ABOUT + '\n        ' + BLOG, 1)

# Direction 6's vehicle page: the car's facts leave the offer plate and
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

# Direction 6's lease specials: where the retailer offers a lease on a car,
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

# Direction 6's vehicle page: the CARFAX mark on every pre-owned car, beside
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

# Direction 6's own sheets and script are stamped with their content, so a
# browser (and GitHub Pages' cache) fetches them again whenever they change
OWN = ['css/index6.css', 'css/inventory6.css', 'css/vehicle6.css', 'css/day6.css', 'js/index6.js', 'js/lenis6.js']
STAMPS = {f: hashlib.md5(open(ROOT + f, 'rb').read()).hexdigest()[:10] for f in OWN}
def stamp6(s):
    for f, h in STAMPS.items():
        s = re.sub(r'(' + re.escape(f) + r')(\?v=[^"]*)?"', lambda m: m.group(1) + '?v=' + h + '"', s)
    return s


# Direction 6's day: css/day6.css loads last on every page, over direction
# 5's sheets, and a script in the head sets the look before first paint.
# Each look has its own link, ?look=1..4; the session keeps it from page to
# page, so the inventory and the car pages open in the look they came from.
LOOK = """<script>
  /* Direction 6: the look is the link's, ?look=1..4; the client chose 2 (css/day6.css) */
  (function () {
    var m = /[?&]look=([1-4])/.exec(location.search), l = m && m[1];
    try { l = l || sessionStorage.getItem("bpb-look"); if (l) sessionStorage.setItem("bpb-look", l); } catch (e) {}
    document.documentElement.setAttribute("data-look", l || "2");
  })();
</script>
"""
SHEETS = re.compile(r'(<link rel="stylesheet" href="(\.\./)?css/[^"]+">\n)(?!<link rel="stylesheet")')
OLD_LOOK = re.compile(r'<script>\n  /\* Direction 6: .*?</script>\n', re.S)
def day6(s):
    if 'css/day6.css' in s:
        return OLD_LOOK.sub(lambda m: LOOK, s, count=1)
    m = list(SHEETS.finditer(s))[-1]
    pre = m.group(2) or ''
    add = f'<link rel="stylesheet" href="{pre}css/day6.css">\n' + LOOK
    return s[:m.end()] + add + s[m.end():]

# Direction 6's scroll layer: Lenis on every page (Alex's standing
# instruction). Its stylesheet and the library from jsDelivr, pinned, then
# js/lenis6.js, all deferred in the head, so they run before the page's own
# script at the foot, which finds the instance on window.lenis.
LENIS_V = '1.3.26'
def lenis6(s):
    if 'js/lenis6.js' in s:
        return s
    m = re.search(r'<link rel="stylesheet" href="(\.\./)?css/day6\.css[^"]*">\n', s)
    pre = m.group(1) or ''
    add = (f'<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/lenis@{LENIS_V}/dist/lenis.css">\n'
           f'<script src="https://cdn.jsdelivr.net/npm/lenis@{LENIS_V}/dist/lenis.min.js" defer></script>\n'
           f'<script src="{pre}js/lenis6.js" defer></script>\n')
    return s[:m.end()] + add + s[m.end():]

# Direction 6's prices, to the FTC's letters (the client's note of 2026-09-25,
# as on Rolls-Royce): the price that stands out is the sale price with the
# dealer's two charges in it; the listed price and the charges are the
# working beneath it; a saving is measured against the sale price; every
# advertised lease payment carries its term and the money down, in the
# dealer's own word ("down"). Direction 5 is left as the client saw it.
import json as _json
_D = {v['stock']: v for v in _json.load(open(ROOT + 'data/inventory.json', encoding='utf-8'))['vehicles']}
def _m(n): return '${:,}'.format(n)
FEES = [('+ Dealer service charge', '$1,189'), ('+ Electronic filing charge', '$514')]
# the dealer's disclosure puts both charges in every sale price; where the
# listing captured no sale price (one car, VC-P35787) it is the dealer's
# price plus the two charges, never the price without them
FEE_SUM = 1189 + 514
def _sale(v): return v.get('sale_price_with_fees') or (v['price'] + FEE_SUM)
def _base(v): return v.get('price_label') or ('MSRP' if v['condition'] == 'new' else 'Braman Price')
def _terms(v):
    lt = v.get('lease_terms') or {}
    parts = []
    if lt.get('term_months'): parts.append(f"{lt['term_months']} months")
    if lt.get('down'): parts.append(f"{_m(lt['down'])} down")
    return ' · '.join(parts)
def _flag(v, html):
    """the lease flag on a photograph: the payment, and its term and money down beneath"""
    terms = _terms(v)
    if not terms: return html
    # a payment that rests on a rebate carries it, and the credit it needs,
    # on the flag itself (the FTC's letters: key terms beside the price)
    lt = v.get('lease_terms') or {}
    cond = ''
    if lt.get('rebates'):
        cond = f"Includes {_m(lt['rebates'])} rebates" + (f" · {lt['credit']} credit" if lt.get('credit') else '')
        cond = f'<span class="card__flag-terms card__flag-cond">{cond}</span>'
    return re.sub(r'<span class="card__flag card__flag--lease">(Lease [^<]*)</span>',
                  lambda m: f'<span class="card__flag card__flag--lease"><span>{m.group(1)}</span><span class="card__flag-terms">{terms}</span>{cond}</span>', html)

def _card(m):
    c = m.group(0)
    st = re.search(r'data-stock="([^"]+)"', c)
    v = _D.get(st.group(1)) if st else None
    if not v or 'card__flag-terms' in c and 'Sale price</span>' in c: return c
    sale, base = _sale(v), _base(v)
    c = re.sub(r'aria-label="([^"]*), (?:Braman Price|MSRP|Price|Sale price) \$[\d,]+"', lambda a: f'aria-label="{a.group(1)}, Sale price {_m(sale)}"', c, count=1)
    c = re.sub(r'<span class="card__price-label">[^<]*(<sup[^>]*>\*</sup>)?</span><span class="card__price-value">\$[\d,]+</span>',
               lambda a: f'<span class="card__price-label">Sale price{a.group(1) or ""}</span><span class="card__price-value">{_m(sale)}</span>', c, count=1)
    rows = [(base, _m(v['price']))] + FEES
    c = re.sub(r'<dl class="card__build">.*?</dl>', lambda a: '<dl class="card__build">\n' + '\n'.join(f'                  <div><dt>{k}</dt><dd>{d}</dd></div>' for k, d in rows) + '\n                </dl>', c, count=1, flags=re.S)
    if v.get('msrp') and v['msrp'] > sale:
        c = re.sub(r'You save \$[\d,]+', f'You save {_m(v["msrp"] - sale)}', c)
    c = re.sub(r'<span class="card__flag card__flag--pending">[^<]*</span>', '<span class="card__flag card__flag--pending">Sale Pending</span>', c)
    return _flag(v, c)

def _vdp(s):
    st = re.search(r'<dt>Stock #</dt><dd>([^<]+)</dd>', s)
    v = _D.get(st.group(1)) if st else None
    if not v: return s
    sale, base = _sale(v), _base(v)
    # the head
    s = re.sub(r'(<span class="vdp__price-label">)[^<]*(<a class="asterisk"[^>]*>\*</a></span><span class="vdp__price-value">)\$[\d,]+',
               lambda a: f'{a.group(1)}Sale price{a.group(2)}{_m(sale)}', s, count=1)
    # the offer
    s = re.sub(r'(<p class="offer__label">)[^<]*(<a class="asterisk")', lambda a: f'{a.group(1)}Sale price{a.group(2)}', s, count=1)
    s = re.sub(r'<p class="offer__price">\$[\d,]+</p>', f'<p class="offer__price">{_m(sale)}</p>', s, count=1)
    rows = []
    if v['condition'] != 'new' and v.get('msrp'): rows.append(('MSRP', _m(v['msrp']), ''))
    rows.append((base, _m(v['price']), ''))
    rows += [(k, d, '') for k, d in FEES]
    if v.get('msrp') and v['msrp'] > sale and v['condition'] != 'new':
        rows.append(('You save', f"− {_m(v['msrp'] - sale)}", ' class="card__save"'))
    if v.get('lease_month'):
        tax = ' + tax' if v.get('lease_plus_tax') else ''
        terms = _terms(v)
        rows.append(('Lease', f"{_m(v['lease_month'])}{tax} / month" + (f'<small>{terms}</small>' if terms else ''), ' class="offer__lease-row"'))
    s = re.sub(r'<dl class="offer__rows">\n.*?</dl>', lambda a: '<dl class="offer__rows">\n' + '\n'.join(f'            <div{cls}><dt>{k}</dt><dd>{d}</dd></div>' for k, d, cls in rows) + '\n          </dl>', s, count=1, flags=re.S)
    # the phone's bar and the page's description
    s = re.sub(r'(<p class="vdp__bar-price"><span>)[^<]*(</span> )\$[\d,]+', lambda a: f'{a.group(1)}Sale price{a.group(2)}{_m(sale)}', s, count=1)
    s = re.sub(r'(<meta name="description" content="[^"]*?), (?:Braman Price|MSRP|Price|Sale price) \$[\d,]+ at', lambda a: f'{a.group(1)}, Sale price {_m(sale)} at', s, count=1)
    # a lease that rests on a rebate says so beside its payment, with the
    # credit it needs (the FTC's letters: a price that factors in a rebate
    # not everyone will get)
    lt = v.get('lease_terms') or {}
    if v.get('lease_month') and lt.get('rebates') and 'in rebates' not in s:
        cond = f"Includes {_m(lt['rebates'])} in rebates" + (f"; {lt['credit']} credit approval with {lt.get('lender') or 'the lender'} required" if lt.get('credit') else '')
        s = re.sub(r'(<p class="special__fine">)', lambda a: a.group(1) + cond + '. ', s, count=1)
    # the lease flag on the first photograph
    return _flag(v, s)

PO_PRICE = re.compile(r'(<p class="po-facts[^"]*"[^>]*>[^<]*<br>Stock ([^<]+)</p>\s*)<p class="po-price step" style="--i:3">.*?</p>(?:\s*<p class="po-fees[^"]*"[^>]*>.*?</p>)?', re.S)
def _plates(s):
    """the certified pre-owned slider on the home page: the figure from the
    data, named, with the charges it holds said beside it"""
    def one(m):
        v = _D.get(m.group(2).strip())
        if not v: return m.group(0)
        return (m.group(1) + f'<p class="po-price step" style="--i:3"><span class="po-price__label">Sale price</span> {_m(_sale(v))}</p>'
                f'\n        <p class="po-fees step" style="--i:3">Includes the $1,189 dealer service charge and $514 electronic filing charge; excludes tax, tag and title.</p>')
    return PO_PRICE.sub(one, s)

def price6(s):
    s = CARD.sub(_card, s)
    if '<dl class="offer__rows">' in s: s = _vdp(s)
    if 'po-plate' in s: s = _plates(s)
    return s

# 1. The SRP
write('inventory6.html', stamp6(lenis6(day6(price6(lease_cards(blog(six(read('inventory.html')))))))))

# 2. The vehicle pages — cars no longer in direction 4 are removed here too
os.makedirs(ROOT + 'vehicles6', exist_ok=True)
pages = sorted(f for f in os.listdir(ROOT + 'vehicles') if f.endswith('.html'))
for f in os.listdir(ROOT + 'vehicles6'):
    if f.endswith('.html') and f not in pages:
        os.remove(ROOT + 'vehicles6/' + f)
for f in pages:
    write('vehicles6/' + f, stamp6(lenis6(day6(price6(carfax(lease_page(lease_cards(facts(blog(six(read('vehicles/' + f))))))))))))

# MOCK-UP ONLY: the retailer's data marks no car sold or pending, so the home
# rail shows the two other flags on two cars to present them (Alex,
# 2026-09-24). Remove these entries once the data carries a real status.
DEMO_FLAGS = {
    'V69245': ('pending', 'Sale Pending'),
    # 'V68412' was shown as sold; a sold car is not advertised (the FTC's
    # letters, 2026-09-25), so the mockup shows only the pending state
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

# 3. The home page: index4's rail, re-pointed, and index6's own links
idx4, idx6 = read('index4.html'), read('index6.html')
rail = re.search(r'<ul class="stock__rail"[^>]*>.*?</ul>', idx4, re.S)
if rail:
    idx6 = re.sub(r'<ul class="stock__rail"[^>]*aria-label="New Bentley in stock[^>]*>.*?</ul>', lambda m: demo_flags(lease_cards(six(rail.group(0)))), idx6, count=1, flags=re.S)
idx6 = idx6.replace('href="inventory.html', 'href="inventory6.html').replace('href="vehicles/', 'href="vehicles6/')
write('index6.html', stamp6(lenis6(day6(price6(idx6)))))

print("inventory6.html,", len(pages), "vehicle pages in vehicles6/, index6 rail")
