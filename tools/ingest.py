"""Turn the dealer captures into data/inventory.json and the photographs.
   Inputs (not in the repository — .playwright-mcp/ is ignored):
     .playwright-mcp/new-all.json, used-all.json   the two SRPs, every card's text + JSON-LD
     .playwright-mcp/drop/vdp-<stock>.json         one record per vehicle page: gallery, description,
                                                   details, price block, lease popup, JSON-LD
   Outputs:
     data/inventory.json
     assets/img/inventory/<slug>.webp              the card image, 840×630
     assets/img/vdp/<slug>/N.webp + N-thumb.webp   the first PHOTOS photographs, 1400 and 420 wide
   Run from anywhere: python3 tools/ingest.py [--no-photos]"""
import json, re, os, sys, io, urllib.request, datetime
from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..') + '/'
CAP = ROOT + '.playwright-mcp/'
PHOTOS = 8
TODAY = datetime.date.today().isoformat()
no_photos = '--no-photos' in sys.argv

def load(p):
    d = json.load(open(p))
    return json.loads(d) if isinstance(d, str) else d

def num(s):
    if s is None: return None
    s = re.sub(r'[^\d.]', '', str(s))
    return int(float(s)) if s else None

def slug(stock): return stock.lower()

# --- the two listings, in the dealer's order
cards, order = {}, []
for f, cond in [('new-all', 'new'), ('used-all', 'used')]:
    d = load(CAP + f + '.json')
    ld_by_vin = {x['vehicleIdentificationNumber']: x for x in d['ld']}
    for it in d['items']:
        it['condition'] = cond
        it['ld_srp'] = ld_by_vin.get(it['vin'])
        cards[it['stock']] = it; order.append(it['stock'])

MODELS = ['Bentayga EWB', 'Bentayga', 'Continental GTC', 'Continental GT', 'Flying Spur']
def split_name(title):
    m = re.match(r'(New|Used) (\d{4}) Bentley (.*)$', title.strip())
    year, rest = int(m.group(2)), m.group(3).strip()
    for mo in MODELS:
        if rest.startswith(mo): return year, mo
    return year, rest

def parse_lease(pop):
    """The dealer's lease 'Details' popup, parsed. Nothing not in the text."""
    t = pop.replace('\n', ' ')
    g = lambda re_, f=num: (lambda m: f(m.group(1)) if m else None)(re.search(re_, t, re.I))
    return {
        'down': g(r'\$([\d,\.]+) down'),
        'payment': g(r'\$([\d,\.]+) a month'),
        'term_months': g(r'(\d+) MONTHS? lease'),
        'miles_per_year': g(r'([\d,]+) MILES PER YEAR'),
        'overage_per_mile': g(r'overage at \$([\d.]+) per mile', lambda s: float(s)),
        'disposition_fee': g(r'\$([\d,]+) lease disposition fee'),
        'rebates': g(r'Includes \$([\d,\.]+) rebates'),
        'credit': 'Tier 1' if re.search(r'Tier 1', t) else None,
        'lender': 'Bentley Financial Services' if 'Bentley Financial Services' in t else None,
        'deal_number': g(r'DEAL #(\d+)', str),
        'offer_ends': g(r'valid through ([A-Za-z]+ \d{1,2}, \d{4})', lambda x: x.title()),
        'security_deposit': 0 if re.search(r'No security deposit', t, re.I) else None,
    }

def parse_description(text, cond):
    """The dealer's paragraph: the spec line, the feature list, the prose and the
       CARFAX / Certified notes are run together; take them apart."""
    t = text.strip()
    features, notes, prose, certified = [], [], '', None
    # the feature list: "ABS brakes, Alloy wheels, …, Traction control."
    m = re.search(r'((?:[A-Z][^,.]*?, ){3,}[^,.]*?\.)', t)
    if m:
        features = [x.strip() for x in m.group(1).rstrip('.').split(',') if x.strip()]
        # on a new car the spec line runs straight into the list: "… 8 Speed Dual Clutch V8 ABS brakes"
        if ' Bentley ' in features[0]:
            features[0] = re.sub(r'^.*\b(V8|W12|V6|DOHC|Clutch|Automatic|AWD|Hybrid|Turbocharged)\b\s*', '', features[0]).strip()
        features = [x for x in features if x]
        t = t.replace(m.group(1), ' ')
    # the dealer's prose
    m = re.search(r'(We are honored[^!]*!)', t)
    if m: prose = m.group(1).strip()
    if 'Recent Arrival' in text: notes.append('Recent arrival')
    if 'CARFAX One-Owner' in text: notes.append('CARFAX one-owner')
    if 'Clean CARFAX' in text: notes.append('Clean CARFAX')
    m = re.search(r'Odometer is ([\d,]+) miles below market average', text)
    if m: notes.append(f'Odometer {m.group(1)} miles below market average')
    if 'Certified By Bentley' in text:
        certified = [x.strip() for x in re.split(r'\s+\*\s+', text.split('Certified By Bentley Details:', 1)[1]) if x.strip()]
    return prose, features, notes, certified

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(req, timeout=60).read()

def save_webp(im, path, w, q=80):
    im = im.convert('RGB')
    if im.width != w:
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path, 'WEBP', quality=q, method=6)
    return im.size

vehicles = []
for stock in order:
    c = cards[stock]
    r = load(CAP + f'drop/vdp-{stock}.json')
    ld = r.get('ld') or c.get('ld_srp') or {}
    year, model = split_name(c['title'])
    trim = (c['trim'] or ld.get('vehicleConfiguration') or '').strip()
    if trim.lower() == 'base': trim = ''
    cond = c['condition']
    det = dict(zip(*[iter(r['details'].split('\n'))] * 2)) if r.get('details') and 'Stock #' in r['details'] else {}
    price_text = r.get('price') or c['text']
    g = lambda re_: (lambda m: num(m.group(1)) if m else None)(re.search(re_, price_text))
    msrp_shown = g(r'MSRP(?: Details)?\n\$([\d,]+)')
    headline = g(r'Braman Price(?: Details)?\n\$([\d,]+)') if cond == 'used' else msrp_shown
    sale = g(r'(?:Sale|Final) Price\n\$([\d,]+)')
    save = g(r'You Save\n-\s*\$([\d,]+)')
    lm = re.search(r'Lease (?:for )?\$([\d,\.]+)(?:/month| a month)', price_text)
    lease_month = num(lm.group(1)) if lm else None
    pops = [p for p in r.get('pops', []) if f'STOCK #{stock}' in p.upper().replace('  ', ' ')]
    pop = pops[0] if pops else None
    if lease_month and not pop:
        # the popup for this car does not name the stock: take the one whose payment matches
        pops = [p for p in r.get('pops', []) if re.search(r'\$' + re.escape(f'{lease_month}') + r'\.00 a month', p.replace(',', ''))]
        pop = pops[0] if pops else None
    prose, features, notes, certified = parse_description(r.get('description') or '', cond)
    vdp_title = r.get('title') or ''
    one_owner = 'One-Owner' in vdp_title
    is_cert = 'Certified' in vdp_title or bool(certified)
    engine = (ld.get('vehicleEngine') or {}).get('name') or det.get('Engine') or ''
    transmission = ld.get('vehicleTransmission') or det.get('Transmission') or ''
    transmission = transmission.replace('8 SPEED DUAL CLUTCH', '8-speed dual clutch').replace('ZF 8-Speed Automatic', 'ZF 8-speed automatic').replace('8-Speed Automatic', '8-speed automatic')
    mpg = (ld.get('fuelEfficiency') or {}).get('value')
    doors = ld.get('numberOfDoors') or det.get('Doors')
    stock_img = bool(r['photos']) and 'cloudflarestockimages' in r['photos'][0]
    photos_src = [] if stock_img else [re.sub(r'/c_limit,[^/]*/', '/c_limit,fl_lossy,w_1400/', u) for u in r['photos'][:PHOTOS]]
    s = slug(stock)
    title = f"{'New' if cond == 'new' else 'Used'} {year} Bentley {model}" + (f' {trim}' if trim else '')
    v = {
        'stock': stock, 'vin': c['vin'], 'year': year, 'model': model,
        'model_full': model + (f' {trim}' if trim else ''), 'trim': trim,
        'exterior': (c['exterior'] or '').replace(' Ii ', ' II '), 'interior': c['interior'] or '',
        'mileage': num(c['mileage']) or 0, 'condition': cond,
        'price_label': 'MSRP' if cond == 'new' else 'Braman Price',
        'price': headline, 'sale_price_with_fees': sale,
        'sale_label': 'Final price' if 'Final Price' in price_text else 'Sale price',
        'msrp': msrp_shown, 'you_save': save,
        'lease_month': lease_month, 'lease_plus_tax': True if lease_month else False,
        'special': bool(c['special']),
        'certified': is_cert, 'one_owner': one_owner, 'certified_terms': certified,
        'image': f'assets/img/inventory/{s}.webp' if not stock_img else None,
        'image_source': None if stock_img else photos_src[0],
        'stock_image': stock_img,
        'title': title, 'drivetrain': c['drivetrain'] or det.get('Drivetrain') or '',
        'engine': engine, 'transmission': transmission, 'mpg': mpg, 'doors': doors,
        'fuel': 'Hybrid' if 'Hybrid' in trim else 'Gasoline',
        'description': prose, 'description_raw': r.get('description') or '',
        'features': features, 'notes': notes,
        'dealer_url': c['url'], 'page': f'vehicles/{s}.html',
        'photos': [], 'photo_sources': photos_src, 'photo_count_at_dealer': int(c['photos'] or r.get('photoCount') or 0),
        'lease_terms': parse_lease(pop) if pop else None, 'lease_terms_raw': pop,
    }
    if not stock_img and not no_photos:
        for i, u in enumerate(photos_src, 1):
            dest = ROOT + f'assets/img/vdp/{s}/{i}.webp'
            if not os.path.exists(dest):
                im = Image.open(io.BytesIO(fetch(u)))
                w, h = save_webp(im, dest, 1400)
                save_webp(im, ROOT + f'assets/img/vdp/{s}/{i}-thumb.webp', 420, 72)
                if i == 1:
                    card = im.convert('RGB')
                    # 4:3 crop from the centre, then 840 wide
                    tw, th = card.width, round(card.width * 3 / 4)
                    if th > card.height: tw, th = round(card.height * 4 / 3), card.height
                    x, y = (card.width - tw) // 2, (card.height - th) // 2
                    card.crop((x, y, x + tw, y + th)).resize((840, 630), Image.LANCZOS).save(ROOT + v['image'], 'WEBP', quality=82, method=6)
                print(stock, i, w, h, flush=True)
            else:
                w, h = Image.open(dest).size
            v['photos'].append({'src': f'assets/img/vdp/{s}/{i}.webp', 'thumb': f'assets/img/vdp/{s}/{i}-thumb.webp', 'w': w, 'h': h})
    vehicles.append(v)

new_n = sum(v['condition'] == 'new' for v in vehicles); used_n = len(vehicles) - new_n
disclaimer = next((p for r in [load(CAP + f'drop/vdp-{order[0]}.json')] for p in r['pops'] if p.startswith('* Prices')), '')
out = {
    'source': ['https://www.bramanbentleypalmbeach.com/search/new-bentley/?ct=all&mk=7&tp=new',
               'https://www.bramanbentleypalmbeach.com/search/used-bentley/?ct=all&mk=7&tp=used'],
    'captured': TODAY,
    'note': (f"{len(vehicles)} vehicles as listed by the dealer on {TODAY}: {new_n} new and {used_n} pre-owned. "
             "price is the headline figure on the dealer's card, labelled by price_label — MSRP on a new car, Braman Price on a used one; "
             "sale_price_with_fees is the dealer's Sale Price (Final Price on an Internet Special) = price + the $1,189 dealer service charge + the $514 electronic filing charge; "
             "msrp and you_save only where the dealer shows them on a used car; lease_month where the dealer shows a lease, its Details popup parsed into lease_terms (raw text kept); "
             "special marks the dealer's Internet Special; certified = Certified by Bentley pre-owned, with the dealer's programme points in certified_terms; one_owner from the dealer's title. "
             f"Each car carries its first {PHOTOS} dealer photographs (assets/img/vdp/<stock>/, 1400 wide, thumbs 420) with their sources, the card image is the first cut to 4:3 at 840×630; "
             "stock_image marks the four cars the dealer has no photograph of (the listing shows the make badge) — they get a manufacturer image on the site, labelled. "
             "Engine, transmission, doors and mpg from the dealer's JSON-LD; features from the dealer's own equipment sentence; notes are the dealer's CARFAX and arrival remarks. "
             "price_disclaimer is the dealer's Details text beside every price, verbatim."),
    'price_disclaimer': disclaimer,
    'vehicles': vehicles,
    'captured_history': [{'date': TODAY, 'count': len(vehicles), 'new': new_n, 'used': used_n}],
}
json.dump(out, open(ROOT + 'data/inventory.json', 'w'), indent=1, ensure_ascii=False)
print(len(vehicles), 'vehicles →', ROOT + 'data/inventory.json')
