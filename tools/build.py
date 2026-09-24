"""Build everything that comes from data/inventory.json:
   - the cards in inventory.html (and its model / year option lists, the count,
     the footnote),
   - the cars on the home page's inventory rail (index4.html),
   - one vehicle page per car in vehicles/, from the SRP's own chrome.
Run from anywhere: python3 tools/build.py"""
import json, re, html, os, datetime
from collections import Counter

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..') + '/'
d = json.load(open(ROOT + 'data/inventory.json'))
V = d['vehicles']
e = html.escape

# GitHub Pages caches the stylesheets; every build stamps the css and js
# links with the build time, so a new build is a new file to the browser.
STAMP = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
def stamp(s):
    return re.sub(r'((?:href|src)="(?:\.\./)?(?:css|js)/[^"?]+)(?:\?v=[^"]*)?"', lambda m: m.group(1) + '?v=' + STAMP + '"', s)

def money(n): return '${:,}'.format(n)

# --- Featured order: rows of three — a row of pre-owned, then two rows of
#     new, and again, each group in the retailer's own order. The certified
#     cars lead, and the two stocks stay mixed all the way down.
new_cars = [v for v in V if v['condition'] == 'new']
used_cars = [v for v in V if v['condition'] != 'new']
featured = []
while new_cars or used_cars:
    featured += used_cars[:3]; del used_cars[:3]
    featured += new_cars[:6]; del new_cars[:6]

CHEV = '<svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M5.5 2.5 11 8l-5.5 5.5" stroke="currentColor" stroke-width="1.25"/></svg>'
CHEV_L = '<svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M10.5 2.5 5 8l5.5 5.5" stroke="currentColor" stroke-width="1.25"/></svg>'

# the four cars the retailer has no photograph of stand on Bentley's own
# picture of the line, said so on the page
STOCK_IMAGE = {
    'Continental GT':  ('assets/bm/2026/gt-mountains.webp', 2400, 1600),
    'Continental GTC': ('assets/bm/2026/gtc-mountains.webp', 2400, 1600),
    'Flying Spur':     ('assets/bm/2026/spur-norcal.webp', 2400, 1600),
    'Bentayga':        ('assets/bm/2026/bentayga-sunset.webp', 2400, 1600),
    'Bentayga EWB':    ('assets/bm/2026/bentayga-sunset.webp', 2400, 1600),
}

def name_of(v):
    return f"{v['year']} Bentley {v['model']}" + (f" {v['trim']}" if v['trim'] else '')
def short_name(v):
    return f"{'New' if v['condition']=='new' else 'Pre-owned'} {v['year']} {v['model']}" + (f" {v['trim']}" if v['trim'] else '')

def image_of(v, p=''):
    """(src, w, h, alt-note) — the card image, or the line's picture."""
    if v['stock_image'] or not v['image']:
        src, w, h = STOCK_IMAGE.get(v['model'], STOCK_IMAGE['Continental GT'])
        return p + src, w, h, ' (Bentley image of the line; the retailer has no photograph of this car yet)'
    return p + v['image'], 840, 630, ''

def lease_text(v):
    return f"Lease {money(v['lease_month'])}/mo" if v['lease_month'] else ''

def stack_rows(v, sale_label=None):
    """The price build as the retailer's card shows it. On a pre-owned car
       with a shown MSRP: MSRP and the saving first. Then the two charges and
       the sale price; then the lease."""
    rows = []
    if v['condition'] == 'used' and v['msrp']:
        rows += [('MSRP', money(v['msrp']), ''), ('You save', '− ' + money(v['you_save'] or (v['msrp'] - v['price'])), 'card__save')]
    rows += [('Dealer service charge', '$1,189', ''), ('Electronic filing charge', '$514', '')]
    if v['sale_price_with_fees']:
        rows.append((sale_label or v.get('sale_label') or 'Sale price', money(v['sale_price_with_fees']), 'card__sale'))
    if v['lease_month']:
        rows.append(('Lease', f"{money(v['lease_month'])} / month", ''))
    return rows

def rows_html(rows, indent=14):
    pad = ' ' * indent
    return '\n'.join(f'{pad}<div{(" class=" + chr(34) + c + chr(34)) if c else ""}><dt>{e(k)}</dt><dd>{val}</dd></div>' for k, val, c in rows)

# --- One card. `p` is the path prefix to the site root ('' or '../').
#     One plate: the photograph, then the kind, the name, the facts, the
#     headline figure on a hairline, the retailer's build as three quiet rows,
#     two lines kept for the MSRP saving and the lease, the way in. Every line
#     is reserved whether the car needs it or not, so a row of cards is one
#     height and its figures sit on one line.
def card(v, p='', eager=False, cls='card', style=''):
    src, w, h, note = image_of(v, p)
    flag = '<span class="card__flag">Internet special</span>' if v['special'] else ''
    label = v['price_label']
    used = v['condition'] == 'used'
    if not used: kind = 'New · In stock'
    elif v['certified'] and v['one_owner']: kind = 'Pre-owned · <b>Certified by Bentley, one owner</b>'
    elif v['certified']: kind = 'Pre-owned · <b>Certified by Bentley</b>'
    elif v['one_owner']: kind = 'Pre-owned · One owner'
    else: kind = 'Pre-owned'
    # every fact on its own row, the colours too (Alex, 2026-09-21: no "X over Y")
    facts = (f"<span><b>Exterior</b>{e(v['exterior'])}</span>"
             f"<span><b>Interior</b>{e(v['interior'])}</span>"
             f"<span><b>Mileage</b>{'{:,}'.format(v['mileage'])} miles</span>"
             f"<span><b>Stock #</b>{e(v['stock'])}</span>")
    alt = f"{v['exterior']} {name_of(v)}{note}"
    build = [('Dealer service charge', '$1,189', ''), ('Electronic filing charge', '$514', '')]
    if v['sale_price_with_fees']:
        build.append((v.get('sale_label') or 'Sale price', money(v['sale_price_with_fees']), 'card__sale'))
    extra = []
    if used and v['msrp']:
        extra.append(f"MSRP {money(v['msrp'])} · You save {money(v['you_save'] or (v['msrp'] - v['price']))}")
    if v['lease_month']:
        extra.append(f"Lease {money(v['lease_month'])} a month")
    extra_html = ''.join(f'<span>{e(x)}</span>' for x in extra)
    return f'''        <li class="{cls}"{f' style="{style}"' if style else ''} data-condition="{v['condition']}" data-certified="{1 if v['certified'] else 0}" data-year="{v['year']}" data-price="{v['price']}" data-mileage="{v['mileage']}" data-model="{e(v['model'])}" data-trim="{e(v['trim'])}" data-stock="{e(v['stock'])}" data-vin="{e(v['vin'])}">
          <a class="card__link" href="{p}{v['page']}" aria-label="{e(v['title'])}, {e(label)} {money(v['price'])}">
            <span class="card__media">{flag}<img src="{src}" width="{w}" height="{h}" loading="{'eager' if eager else 'lazy'}" decoding="async" alt="{e(alt)}"></span>
            <span class="card__body">
              <span class="card__kind">{kind}</span>
              <h2 class="card__title">{e(name_of(v))}</h2>
              <span class="card__facts">{facts}</span>
              <span class="card__price"><span class="card__price-label">{e(label)}<sup aria-hidden="true">*</sup></span><span class="card__price-value">{money(v['price'])}</span></span>
              <dl class="card__build">
{rows_html(build, 16)}
              </dl>
              <span class="card__extra">{extra_html}</span>
              <span class="link">View details<i aria-hidden="true"></i></span>
            </span>
          </a>
        </li>'''

# =========================================================================
# 1. The SRP: the grid, the option lists, the count, the footnote
# =========================================================================
cards = [card(v, '', eager=i < 3) for i, v in enumerate(featured)]
grid = '<ul class="grid" id="grid">\n' + '\n'.join(cards) + '\n      </ul>'
years = sorted(Counter(v['year'] for v in V), reverse=True)
order = ['Continental GT', 'Continental GTC', 'Flying Spur', 'Bentayga', 'Bentayga EWB']
models = [m for m in order if any(v['model'] == m for v in V)] + sorted({v['model'] for v in V} - set(order))
def options(first, values):
    return '\n'.join([f'              <option value="">{first}</option>'] + [f'              <option value="{v}">{v}</option>' for v in values])

path = ROOT + 'inventory.html'
srp = open(path).read()
srp = re.sub(r'<ul class="grid" id="grid">.*?</ul>', lambda m: grid, srp, count=1, flags=re.S)
srp = re.sub(r'(<select class="pick__select" name="year" data-pick="year">\n).*?(\n            </select>)', lambda m: m.group(1) + options('All years', years) + m.group(2), srp, count=1, flags=re.S)
srp = re.sub(r'(<select class="pick__select" name="model" data-pick="model">\n).*?(\n            </select>)', lambda m: m.group(1) + options('All models', models) + m.group(2), srp, count=1, flags=re.S)
n_new = sum(v['condition'] == 'new' for v in V)
srp = re.sub(r'<span data-count>\d+</span>', f'<span data-count>{len(V)}</span>', srp)
srp = re.sub(r'<span data-split>[^<]*</span>', f'<span data-split>{n_new} new and {len(V) - n_new} pre-owned</span>', srp)
legal = d.get('price_disclaimer') or ''
srp = re.sub(r'<p class="srp__legal" id="legal">.*?</p>', lambda m: f'<p class="srp__legal" id="legal">{e(legal)}</p>', srp, count=1, flags=re.S)
srp = stamp(srp)
open(path, 'w').write(srp)
print(len(cards), 'cards in inventory.html;', len(years), 'years,', len(models), 'models')

# =========================================================================
# 2. The home page: the rail — new cars first, in the retailer's order,
#    the real car's own photograph
# =========================================================================
def rail_car(v, i):
    """The same plate as the inventory's, on the rail, arriving with the chapter."""
    return card(v, '', eager=False, cls='card stock__car step', style=f'--i:{i}')
rail_cars = [v for v in V if v['condition'] == 'new'][:12]
rail = '<ul class="stock__rail" tabindex="0" aria-label="New Bentley in stock; drag or scroll sideways">\n' + '\n'.join(rail_car(v, i + 2) for i, v in enumerate(rail_cars)) + '\n      </ul>'
path = ROOT + 'index4.html'
idx = open(path).read()
if '<ul class="stock__rail"' in idx:
    idx = re.sub(r'<ul class="stock__rail"[^>]*>.*?</ul>', lambda m: rail, idx, count=1, flags=re.S)
    idx = stamp(idx)
    open(path, 'w').write(idx)
    print(len(rail_cars), 'cars on the index4 rail')

# =========================================================================
# 3. The vehicle pages — the SRP's head, header and footer, paths lifted a
#    level, and the car between them.
# =========================================================================
head = re.search(r'<head>.*?</head>', srp, re.S).group(0)
header = re.search(r'<a class="skip".*?</header>', srp, re.S).group(0)
footer = re.search(r'<!-- LAST MASS.*?</footer>', srp, re.S).group(0)
def lift(s):
    s = re.sub(r'(href|src)="(assets/|css/|js/|index4\.html|inventory\.html)', r'\1="../\2', s)
    return s
head = re.sub(r'<link rel="stylesheet" href="\.\./css/inventory\.css[^"]*">', lambda m: m.group(0) + f'\n<link rel="stylesheet" href="../css/vehicle.css?v={STAMP}">', lift(head))   # the cards' sheet, then the vehicle page's own
header = lift(header).replace(' aria-current="page"', '')
footer = lift(footer)

DRIVE = {'AWD': 'all-wheel drive', 'RWD': 'rear-wheel drive'}
def engine_short(v):
    en = v['engine'] or ''
    if 'W12' in en: return 'W12'
    if 'Hybrid' in (v['trim'] or ''): return 'V6 hybrid'
    if 'V8' in en or '8-Cyl' in en: return 'V8'
    return en
def engine_long(v):
    en = v['engine'] or ''
    if 'Hybrid' in (v['trim'] or ''): return '2.9-litre V6 plug-in hybrid'
    if 'W12' in en: return '6.0-litre W12, twin-turbocharged'
    if 'V8' in en or '8-Cyl' in en: return '4.0-litre V8, twin-turbocharged'
    return en

def overview(v):
    """The retailer's prose where there is some; otherwise one factual
       sentence from the record — nothing in it that is not in the data."""
    prose = (v['description'] or '').strip()
    if len(prose) > 60: return prose
    parts = [f"A {'new' if v['condition']=='new' else 'pre-owned'} {name_of(v)} in {v['exterior']} over {v['interior']}, with {'{:,}'.format(v['mileage'])} miles."]
    drive = [x for x in [engine_long(v), v['transmission'], DRIVE.get(v['drivetrain'] or '', '')] if x]
    if drive: parts.append(', '.join(drive) + '.')
    return ' '.join(parts)

def fold(title, body, open_=True):
    return f'''
          <details class="fold"{' open' if open_ else ''}>
            <summary class="fold__head"><span>{title}</span><svg class="fold__chevron" width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M2.5 5.5 8 11l5.5-5.5" stroke="currentColor" stroke-width="1.25"/></svg></summary>
            <div class="fold__body">
{body}
            </div>
          </details>'''

def vehicle_page(v):
    p = '../'
    name = name_of(v)
    used = v['condition'] == 'used'
    label = v['price_label']
    if not used: eyebrow = 'New · In stock'
    elif v['certified'] and v['one_owner']: eyebrow = 'Pre-owned · Certified by Bentley, one owner'
    elif v['certified']: eyebrow = 'Pre-owned · Certified by Bentley'
    elif v['one_owner']: eyebrow = 'Pre-owned · One owner'
    else: eyebrow = 'Pre-owned'
    if v['photos']:
        photos = v['photos']
        stock_note = ''
    else:
        src, w, h, _ = image_of(v)
        photos = [{'src': src, 'thumb': src, 'w': w, 'h': h}]
        stock_note = ' (Bentley image of the line; the retailer has no photograph of this car yet)'
    spin = v.get('spin') or []
    spin_tile = ''
    if spin:
        spin_tile = f'''
      <li class="film__frame film__frame--spin" style="--i:1"><button class="film__launch" type="button" aria-label="View the car in 360 degrees"><img src="{p}{spin[0]}" width="1000" height="667" loading="lazy" decoding="async" alt=""><span class="film__launch-mark"><span class="film__launch-ring">360°</span><span class="film__launch-label">View in 360°</span></span></button></li>'''
    frames = '\n'.join(
        f'''      <li class="film__frame" style="--i:{i + (1 if spin and i > 0 else 0)}"><button class="film__open" type="button" data-index="{i}" aria-label="Photograph {i + 1} of {len(photos)}, open full screen"><img src="{p}{ph['src']}" width="{ph['w']}" height="{ph['h']}" loading="{'eager' if i < 2 else 'lazy'}" decoding="async" alt="{e(v['exterior'])} {e(name)}{stock_note if i == 0 else ''}"></button></li>''' + (spin_tile if i == 0 else '')
        for i, ph in enumerate(photos))
    sources = json.dumps([p + ph['src'] for ph in photos])
    spin_json = json.dumps([p + f for f in spin])
    spin_block = ''
    mode_block = ''
    if spin:
        spin_block = f'''
    <div class="spin" hidden>
      <div class="spin__stage" tabindex="0" aria-label="The car in 360 degrees; drag to turn it">
        <img class="spin__image" src="{p}{spin[0]}" width="1000" height="667" alt="{e(v['exterior'])} {e(name)}, turning" draggable="false">
        <p class="spin__hint">Drag to turn</p>
        <div class="spin__loading" hidden><span></span></div>
      </div>
    </div>'''
        mode_block = '''<div class="film__mode" role="group" aria-label="View">
        <button class="film__mode-button" type="button" data-mode="photos" aria-pressed="true">Photographs</button>
        <button class="film__mode-button" type="button" data-mode="spin" aria-pressed="false">360° view</button>
      </div>'''
    lease_row = f"{money(v['lease_month'])} / month" if v['lease_month'] else ''

    # the offer box: the headline figure large, then what the retailer shows around it
    around = stack_rows(v)
    facts = [
        ('Exterior', e(v['exterior']), ''), ('Interior', e(v['interior']), ''),
        ('Stock #', e(v['stock']), ''), ('VIN', f'<span class="vdp__vin">{e(v["vin"])}</span>', ''),
        ('Engine', e(engine_long(v)), ''), ('Transmission', e(v['transmission'] or ''), ''),
        ('Drivetrain', e(DRIVE.get(v['drivetrain'] or '', v['drivetrain'] or '')).capitalize() if v['drivetrain'] else '', ''),
        ('Fuel economy', f"{v['mpg']} mpg combined" if v['mpg'] else '', ''), ('Doors', e(str(v['doors'] or '')), ''),
    ]
    facts = [f for f in facts if f[1]]

    notes = ''.join(f'<li>{e(n)}</li>' for n in v['notes'])
    features = '\n'.join(f'              <li>{e(x)}</li>' for x in v['features'])
    description = fold('Description', f'              <p class="vdp__copy">{e(overview(v))}</p>' + (f'\n              <ul class="vdp__notes">{notes}</ul>' if notes else ''))
    equipment = fold('Equipment', f'              <ul class="vdp__features">\n{features}\n              </ul>') if v['features'] else ''
    certified = ''
    if v['certified']:
        points = v['certified_terms'] or ['1 year / unlimited miles in addition to any remaining new vehicle limited warranty', 'Roadside assistance', 'Warranty deductible: $0', 'Transferable warranty', '79-point inspection']
        pts = '\n'.join(f'              <li>{e(x)}</li>' for x in points)
        certified = fold('Certified by Bentley', f'              <p class="vdp__copy">Bentley\'s own pre-owned programme: an inspection by Bentley-trained technicians, a warranty that follows the car, and roadside assistance, as the retailer lists it.</p>\n              <ul class="vdp__features">\n{pts}\n              </ul>')
    gallery_note = 'Bentley image of the line; the retailer has no photograph of this car yet' if v['stock_image'] else ''

    # the lease special above the offer: the payment, the term, the money
    # down; the full terms below
    special_box = ''
    lt = v.get('lease_terms') if v['lease_month'] else None
    if v['lease_month']:
        lines = []
        if lt and lt.get('term_months'): lines.append(f"{lt['term_months']} months")
        if lt and lt.get('down'): lines.append(f"{money(lt['down'])} down")
        if lt and lt.get('miles_per_year'): lines.append(f"{'{:,}'.format(lt['miles_per_year'])} miles a year")
        conds = ['Special closed-end lease on this one car, through Bentley Financial Services', 'excludes sales tax and registration fees']
        if lt and lt.get('offer_ends'): conds.append(f"valid through {lt['offer_ends']}")
        special_box = f'''<!-- The lease special: short, above the offer; the full terms are below -->
      <aside class="special step" data-reveal aria-labelledby="special-title" style="--i:1">
        <p class="special__label" id="special-title">Lease special<a class="asterisk" href="#pricing" aria-label="Lease terms">*</a></p>
        <p class="special__figure">{money(v['lease_month'])} <span>a month</span></p>
        {f'<p class="special__terms">{e(", ".join(lines))}</p>' if lines else ''}
        <p class="special__fine">{e('. '.join(c[0].upper() + c[1:] for c in conds))}.</p>
        <a class="link" href="#pricing">Full terms<i aria-hidden="true"></i></a>
      </aside>'''

    # the disclosure: the retailer's own text, and the lease terms as it states them
    disclaimer = d.get('price_disclaimer') or ''
    lease_rows = ''
    if lt:
        def m_(n): return money(n) if isinstance(n, int) else ''
        mileage = f"{'{:,}'.format(lt['miles_per_year'])} miles a year" + (f", ${lt['overage_per_mile']:.2f} a mile over" if lt.get('overage_per_mile') else '') if lt.get('miles_per_year') else ''
        lease_rows = rows_html([x for x in [
            ('Term', f"{lt['term_months']} months" if lt.get('term_months') else '', ''),
            ('Down', m_(lt.get('down')), ''),
            ('Monthly payment', f"{money(lt['payment'])} a month, plus tax" if lt.get('payment') else '', ''),
            ('Mileage', mileage, ''),
            ('Security deposit', 'None' if lt.get('security_deposit') == 0 else '', ''),
            ('Disposition fee', m_(lt.get('disposition_fee')), ''),
            ('Rebates included', m_(lt.get('rebates')), ''),
            ('Credit', f"{lt['credit']}, {lt.get('lender') or 'Bentley Financial Services'}" if lt.get('credit') else '', ''),
            ('Deal number', e(lt.get('deal_number') or ''), ''),
            ('Valid through', e(lt.get('offer_ends') or ''), ''),
        ] if x[1]], 10)
    raw = v.get('lease_terms_raw') or ''
    lease_fine = raw.split('Special Closed-End Lease', 1)[1] if 'Special Closed-End Lease' in raw else raw
    lease_fine = ('Special closed-end lease' + lease_fine) if lease_fine and 'Special Closed-End Lease' in raw else lease_fine
    lease_fine = re.sub(r'\s+', ' ', lease_fine).replace(' ,', ',').replace(' .', '.').strip()
    lease_block = f'''
      <div class="pricing__lease">
        <h3 class="vdp__h" id="lease-terms">Lease terms<span class="pricing__mark" aria-hidden="true">*</span></h3>
        <dl class="offer__rows pricing__rows">
{lease_rows}
        </dl>
        <p class="pricing__fine">{e(lease_fine)}</p>
      </div>''' if lt else ''
    pricing = f'''
  <!-- The disclosure: what the retailer says beside every price, and the
       lease as it states it, on the page rather than behind a click. -->
  <section class="pricing" id="pricing" aria-labelledby="pricing-title" tabindex="-1">
    <div class="page">
      <h2 class="h2 h2--small" id="pricing-title">Pricing details</h2>
      <div class="pricing__body">{lease_block}
        <div class="pricing__legal">
          <h3 class="vdp__h" id="price-terms">Disclaimer<span class="pricing__mark" aria-hidden="true">*</span></h3>
          <p class="pricing__text">{e(disclaimer.lstrip('* ').strip())}</p>
        </div>
      </div>
    </div>
  </section>'''

    others = [o for o in featured if o['stock'] != v['stock']]
    more = sorted(others, key=lambda o: (o['model'] != v['model'], o['condition'] != v['condition']))[:3]
    more_cards = '\n'.join(card(o, p) for o in more)

    title = f"{v['title']} | Bentley Palm Beach"
    desc_meta = f"{v['title']}, {v['exterior']} over {v['interior']}, {'{:,}'.format(v['mileage'])} miles, {label} {money(v['price'])} at Bentley Palm Beach, West Palm Beach, Florida."
    h = re.sub(r'<title>.*?</title>', f'<title>{e(title)}</title>', head)
    h = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{e(desc_meta)}">', h)
    h = h.replace('<link rel="preload" href="../assets/fonts/Bentley-Regular.woff2" as="font" type="font/woff2" crossorigin>',
                  f'<link rel="preload" href="../assets/fonts/Bentley-Regular.woff2" as="font" type="font/woff2" crossorigin>\n<link rel="preload" href="{json.loads(sources)[0]}" as="image">')
    h1 = e(name)
    plate_facts = [('Exterior', e(v['exterior'])), ('Interior', e(v['interior'])), ('Mileage', f"{'{:,}'.format(v['mileage'])} <span class=\"keys__unit\">miles</span>"), ('Engine', e(engine_short(v)))]

    return f'''<!DOCTYPE html>
<html lang="en" class="motion">
{h}
<body>

{header}

<main id="main" class="vdp">

  <!-- The name and the figure. -->
  <section class="vdp__top" id="top">
    <div class="page">
      <nav class="vdp__crumbs" aria-label="Breadcrumb">
        <a href="../index4.html">Home</a><span aria-hidden="true">/</span><a href="../inventory.html">Inventory</a><span aria-hidden="true">/</span><span aria-current="page">{e(name)}</span>
      </nav>
      <header class="vdp__head" data-reveal>
        <div class="vdp__name">
          <p class="label step" style="--i:1">{eyebrow}</p>
          <h1 class="h2 step" style="--i:2">{h1}</h1>
          <dl class="vdp__sub body step" style="--i:3">
            <div><dt>Mileage</dt><dd>{'{:,}'.format(v['mileage'])} miles</dd></div>
            <div><dt>Stock #</dt><dd>{e(v['stock'])}</dd></div>
          </dl>
        </div>
        <div class="vdp__figure step" style="--i:2">
          <p class="vdp__price"><span class="vdp__price-label">{e(label)}<a class="asterisk" href="#pricing" aria-label="Pricing details">*</a></span><span class="vdp__price-value">{money(v['price'])}</span></p>
          <div class="vdp__figure-act">
            <a class="btn" href="#enquire">Confirm availability</a>
            <ul class="tools" data-stock="{e(v['stock'])}" data-name="{e(name)}">
              <li><button class="tool" type="button" data-tool="save" aria-pressed="false"><svg width="16" height="16" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.2" aria-hidden="true"><path d="M10 17s-7-4.4-7-9.2A3.8 3.8 0 0 1 10 6a3.8 3.8 0 0 1 7 1.8C17 12.6 10 17 10 17z"/></svg><span>Save</span></button></li>
              <li><button class="tool" type="button" data-tool="share"><svg width="16" height="16" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.2" aria-hidden="true"><path d="M10 12V3M6.5 6.5L10 3l3.5 3.5"/><path d="M4 10v6h12v-6"/></svg><span data-word>Share</span></button></li>
              <li><a class="tool" href="mailto:?subject={e(name)}%20at%20Bentley%20Palm%20Beach&amp;body={e(name)}%2C%20stock%20{e(v['stock'])}%3A%20" data-tool="email"><svg width="16" height="16" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.2" aria-hidden="true"><rect x="2.5" y="4.5" width="15" height="11"/><path d="M2.5 5l7.5 6 7.5-6"/></svg><span>Email</span></a></li>
            </ul>
          </div>
        </div>
      </header>
    </div>
  </section>

  <!-- The photographs: one rail across the whole screen, running past its
       edge, every frame the same height. It drags, scrolls and snaps; the
       line beneath says where it is; any frame opens full screen. -->
  <section class="film" aria-label="Photographs" data-reveal data-photos='{sources}' data-spin='{spin_json}'>
    <ul class="film__row">
{frames}
    </ul>{spin_block}
    <button class="stock__arrow film__arrow film__arrow--prev" type="button" data-dir="-1" aria-label="Previous photograph" disabled>{CHEV_L}</button>
    <button class="stock__arrow film__arrow film__arrow--next" type="button" data-dir="1" aria-label="Next photograph">{CHEV}</button>
    <div class="page film__foot">
      <div class="film__track" aria-hidden="true"><span class="film__thumb"></span></div>
      {mode_block}
      <p class="film__count"><span data-index>01</span><span class="film__total"> / {len(photos):02d}</span></p>
      {f'<p class="film__note">{gallery_note}</p>' if gallery_note else ''}
    </div>
  </section>

  <section class="vdp__body" aria-label="The car">
    <div class="page vdp__grid">
      <div class="vdp__main">
        <!-- The plate: the four facts a buyer asks first, large. -->
        <dl class="keys step" data-reveal style="--i:1">
{chr(10).join(f'          <div><dt>{k}</dt><dd>{val}</dd></div>' for k, val in plate_facts)}
        </dl>
        <div class="folds">{description}{equipment}{certified}
        </div>
      </div>

      <div class="vdp__side">
        {special_box}
        <!-- The offer: the price, what the retailer shows around it, the two calls, the record. -->
        <aside class="offer step" data-reveal aria-label="The offer" style="--i:2">
          {'<p class="offer__flag label">Internet special</p>' if v['special'] else ''}
          <p class="offer__label">{e(label)}<a class="asterisk" href="#pricing" aria-label="Pricing details">*</a></p>
          <p class="offer__price">{money(v['price'])}</p>
          <dl class="offer__rows">
{rows_html(around, 12)}
          </dl>
          <div class="offer__actions">
            <a class="btn" href="#enquire">Request a quote</a>
            <a class="btn btn--line" href="tel:+15619269111">Connect with a specialist</a>
          </div>
          <p class="offer__route"><a class="link" href="https://www.bramanbentleypalmbeach.com/finance-application/">Get pre-approved<i aria-hidden="true"></i></a></p>
          <dl class="offer__rows offer__facts">
{rows_html(facts, 12)}
          </dl>
        </aside>
      </div>
    </div>
  </section>

  <!-- Enquire: one plate, the ask at the left, the form at the right -->
  <section class="vdp__enquire" id="enquire" aria-labelledby="enq-title">
    <div class="page">
      <div class="enquire">
        <div class="enquire__lede">
          <h2 class="h2 h2--small" id="enq-title">Enquire</h2>
          <p class="body">A specialist will confirm availability and arrange a private viewing at 2801 Okeechobee Boulevard, West Palm Beach, or call <a href="tel:+15619269111">561 926 9111</a>.</p>
          <p class="enquire__trade"><a class="link" href="https://www.bramanbentleypalmbeach.com/value-trade-in/">Value your trade-in<i aria-hidden="true"></i></a></p>
        </div>
        <form class="enquire__form" onsubmit="return false" aria-labelledby="enq-title">
          <label class="field"><span class="field__label">Name</span><input class="field__input" type="text" name="name" autocomplete="name" required></label>
          <label class="field"><span class="field__label">Email</span><input class="field__input" type="email" name="email" autocomplete="email" required></label>
          <label class="field"><span class="field__label">Telephone</span><input class="field__input" type="tel" name="tel" autocomplete="tel"></label>
          <label class="field field--wide"><span class="field__label">Message</span><textarea class="field__input field__area" name="message" rows="3">I am interested in the {e(name)}, stock {e(v['stock'])}.</textarea></label>
          <div class="enquire__send"><button class="btn" type="submit">Send enquiry</button><span class="enquire__fine">No obligation. A specialist replies within one working day.</span></div>
        </form>
      </div>
    </div>
  </section>
{pricing}

  <!-- More from the floor: the same model first. -->
  <section class="more" aria-labelledby="more-title">
    <div class="page">
      <div class="head">
        <div class="head__main"><h2 class="h2 h2--small" id="more-title">More on the floor</h2></div>
        <div class="head__aside"><a class="btn btn--line" href="../inventory.html">View all inventory</a></div>
      </div>
      <ul class="grid grid--more">
{more_cards}
      </ul>
    </div>
  </section>

  <!-- On a small screen the offer follows the page once it has scrolled off. -->
  <div class="vdp__bar" hidden>
    <div class="page vdp__bar-wrap">
      <p class="vdp__bar-price"><span>{e(label)}</span> {money(v['price'])}</p>
      <a class="btn" href="#enquire">Enquire</a>
    </div>
  </div>

  <!-- Full-screen photograph -->
  <dialog class="lightbox" aria-label="Photograph">
    <button class="lightbox__close" type="button" aria-label="Close"><svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.2" aria-hidden="true"><path d="M2 2l12 12M14 2L2 14"/></svg></button>
    <button class="stock__arrow lightbox__arrow lightbox__arrow--prev" type="button" data-dir="-1" aria-label="Previous photograph">{CHEV_L}</button>
    <img class="lightbox__image" src="" alt="">
    <button class="stock__arrow lightbox__arrow lightbox__arrow--next" type="button" data-dir="1" aria-label="Next photograph">{CHEV}</button>
    <p class="lightbox__count"><span data-index>01</span> / {len(photos):02d}</p>
  </dialog>
</main>

{footer}

<a class="totop" href="#top" aria-label="Back to the top">
  <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M8 13.5V2.5m0 0L3 7.5m5-5 5 5" stroke="currentColor" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round"/></svg>
</a>

<script src="../js/vehicle.js?v={STAMP}" defer></script>
</body>
</html>
'''

os.makedirs(ROOT + 'vehicles', exist_ok=True)
# pages of cars no longer in the data are removed
for f in os.listdir(ROOT + 'vehicles'):
    if f.endswith('.html') and not any(v['page'].endswith(f) for v in V):
        os.remove(ROOT + 'vehicles/' + f)
for v in V:
    open(ROOT + v['page'], 'w').write(vehicle_page(v))
print(len(V), 'vehicle pages in vehicles/')

# =========================================================================
# 4. Direction 5 mirrors the inventory, the vehicle pages and the rail.
# =========================================================================
exec(open(ROOT + 'tools/mirror5.py', encoding='utf-8').read(), {'__file__': ROOT + 'tools/mirror5.py'})

# 5. Direction 6, the working copy of direction 5, mirrors them the same way.
exec(open(ROOT + 'tools/mirror6.py', encoding='utf-8').read(), {'__file__': ROOT + 'tools/mirror6.py'})
