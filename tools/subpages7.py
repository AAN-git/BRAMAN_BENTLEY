"""Direction 7's inner pages. Each page is its own <main> in pages7/<name>.main.html;
this wraps it in index7.html's head, header and footer, so the bar and the
footer on every inner page are exactly the home page's, and loads the inner-
page sheet (css/subpages7.css) plus inventory7.css (the listing's head and
sections) and vehicle7.css (the form fields).
Writes <name>7.html at the root. Run: python3 tools/subpages7.py"""
import os, re, hashlib

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..') + '/'
def read(p): return open(ROOT + p, encoding='utf-8').read()
def stamp(p): return hashlib.md5(open(ROOT + p, 'rb').read()).hexdigest()[:10]

PAGES = {
    'contact': ('Contact Us | Bentley Palm Beach',
                'Contact Bentley Palm Beach, 2801 Okeechobee Blvd, West Palm Beach: sales 561-926-9111, service 561-926-9110, parts 561-926-9112, opening hours and directions.'),
    'about': ('About Us | Bentley Palm Beach',
              'About Bentley Palm Beach, the official Bentley retailer at 2801 Okeechobee Blvd, West Palm Beach: our sales, service and parts staff, opening hours and location.'),
    'parts': ('Parts Department | Bentley Palm Beach',
              'Bentley Palm Beach parts department, West Palm Beach: order genuine Bentley parts, parts specials, service appointments and tires; parts 561-926-9112.'),
    'sell': ('Sell Your Vehicle | Bentley Palm Beach',
             'Sell your vehicle to Bentley Palm Beach, West Palm Beach: tell us about it and our team will contact you shortly. Sales 561-926-9111.'),
    'calculator': ('Payment Calculator | Bentley Palm Beach',
                   'Estimate a monthly payment on a Bentley at Bentley Palm Beach, West Palm Beach: price, down payment, trade-in, rate and term.'),
    'bentayga-speed': ('All-New 2027 Bentayga Speed | Bentley Palm Beach',
                       'The all-new 2027 Bentley Bentayga Speed at Bentley Palm Beach, West Palm Beach: its twin-turbocharged V8, exterior and interior, Bentaygas in stock and an enquiry.'),
    'flying-spur': ('New Flying Spur | Bentley Palm Beach',
                    'The new Bentley Flying Spur at Bentley Palm Beach, West Palm Beach: the five models, the High Performance Hybrid, the cabin, Flying Spurs in stock and an enquiry.'),
    'torcal': ('All-New Torcal | Bentley Palm Beach',
               'The all-new Bentley Torcal at Bentley Palm Beach, West Palm Beach: the Torcal and Torcal S, the design, the cabin, the electric performance, and registering your interest.'),
    'continental-gt': ('New Continental GT | Bentley Palm Beach',
                       'The new Bentley Continental GT at Bentley Palm Beach, West Palm Beach: the five models, the design, the cabin, the High Performance Hybrid, Continental GTs in stock and an enquiry.'),
    'continental-gtc': ('New Continental GT Convertible | Bentley Palm Beach',
                        'The new Bentley Continental GT Convertible at Bentley Palm Beach, West Palm Beach: the five models, the four-layer roof, the cabin, the High Performance Hybrid, Convertibles in stock and an enquiry.'),
    'ask-a-tech': ('Ask a Tech | Bentley Palm Beach',
                   'Ask a Bentley technician at Bentley Palm Beach, West Palm Beach: describe the problem and a technician will contact you. Service 561-926-9110.'),
    'home-delivery': ('Bentley Home Delivery Program | Bentley Palm Beach',
                      'Bentley Palm Beach home delivery program, West Palm Beach: start your vehicle purchase online and schedule a test drive at your home or office.'),
    'informational-videos': ('Dealership Informational Videos | Bentley Palm Beach',
                             'Bentley Palm Beach dealership videos, West Palm Beach: the Bentley Palm Beach Boutique Shop, our sales, service and parts hours, and a message to our staff.'),
    'test-drive-new': ('Schedule a New Vehicle Test Drive | Bentley Palm Beach',
                      'Schedule a new Bentley test drive at Bentley Palm Beach, West Palm Beach: choose a date and time to come in. Sales 561-926-9111.'),
    'test-drive-used': ('Schedule a Used Vehicle Test Drive | Bentley Palm Beach',
                       'Schedule a pre-owned vehicle test drive at Bentley Palm Beach, West Palm Beach: choose a date and time to come in. Sales 561-926-9111.'),
    'quote-new': ('Get a New Vehicle Quote | Bentley Palm Beach',
                 'Get a sales quote on a new Bentley from Bentley Palm Beach, West Palm Beach. Sales 561-926-9111.'),
    'quote-used': ('Get a Used Vehicle Quote | Bentley Palm Beach',
                  'Get a sales quote on a pre-owned vehicle from Bentley Palm Beach, West Palm Beach. Sales 561-926-9111.'),
    'value-trade': ('Vehicle Trade-In Value | Bentley Palm Beach',
                   'Find out what your vehicle may be worth at Bentley Palm Beach, West Palm Beach: tell us about it and our team will contact you. Sales 561-926-9111.'),
    'find-my-car': ('Find My Car - Vehicle Locator | Bentley Palm Beach',
                   'Bentley Palm Beach can find nearly any vehicle you are looking for: tell us what you want and we will begin a search. Sales 561-926-9111.'),
    'recall': ('Bentley Vehicle Recall Information Request | Bentley Palm Beach',
              'Check your vehicle for safety notices and recalls at Bentley Palm Beach, West Palm Beach: a service representative will run a report. Service 561-926-9110.'),
    'order-parts': ('Order Bentley Parts | Bentley Palm Beach',
                   'Order genuine Bentley parts from Bentley Palm Beach, West Palm Beach. Parts 561-926-9112.'),
    'service': ('Bentley Service Department | Bentley Palm Beach',
                'Bentley Palm Beach service department, West Palm Beach: schedule service, service specials, ask a tech, safety recalls and our service staff. Service 561-926-9110.'),
    'continental-gt-speed-edition-12': ('The Continental GT Speed Edition 12 | Bentley Palm Beach',
                'The Bentley Continental GT Speed Edition 12 at Bentley Palm Beach, West Palm Beach: the W12 engine, the Edition 12 details, the cabin, Continental GTs in stock and an enquiry.'),
    'flying-spur-speed-edition-12': ('The Flying Spur Speed Edition 12 | Bentley Palm Beach',
                'The Bentley Flying Spur Speed Edition 12 at Bentley Palm Beach, West Palm Beach: one of 120, the W12 engine and its performance, Flying Spurs in stock and an enquiry.'),
    'bentayga-ewb': ('New Bentayga Extended Wheelbase | Bentley Palm Beach',
                'The new Bentley Bentayga Extended Wheelbase at Bentley Palm Beach, West Palm Beach: its design, cabin, performance and technology, Bentayga EWBs in stock and an enquiry.'),
    'finance': ('Finance Department | Bentley Palm Beach',
                'Bentley Palm Beach finance department, West Palm Beach: apply for financing, value your trade, estimate a payment, or speak with the finance team.'),
}

home = read('index7.html')
head, rest = home.split('<main id="main">', 1)
foot = rest.split('</main>', 1)[1]
# the home page's own first-screen preload has no place on an inner page
head = re.sub(r'<link rel="preload" href="assets/bm/[^>]*>\n', '', head)
# the car page's order: cards, inventory, vehicle, then the theme and the static
# page over them; the inner-page sheet last
mid = (f'<link rel="stylesheet" href="css/inventory7.css?v={stamp("css/inventory7.css")}">\n'
       f'<link rel="stylesheet" href="css/vehicle7.css?v={stamp("css/vehicle7.css")}">\n')
head = re.sub(r'(<link rel="stylesheet" href="css/cards\.css[^"]*">\n)', lambda m: m.group(1) + mid, head, count=1)
last = f'<link rel="stylesheet" href="css/subpages7.css?v={stamp("css/subpages7.css")}">\n'
head = re.sub(r'(<link rel="stylesheet" href="css/static7\.css[^"]*">\n)', lambda m: m.group(1) + last, head, count=1)
# the dev site draws everything at 90% (html zoom 0.9, the client's "everything is
# too large"): the inner pages are shown at the same scale so they can be compared
PREVIEW = '<style data-preview>html { zoom: 0.9; } /* the dev site\'s scale — theirs, not part of the design */</style>\n'

# a model page's cars in stock: <!-- STOCK model="…" condition="…" n="…" -->
# is filled at every build with the listing's own cards, so it is never stale
CARDS = re.findall(r'\n(\s*<li class="card"[^>]*>.*?\n\s*</li>)', read('inventory7.html'), re.S)
def stock(m):
    model, cond, n = m.group(1), m.group(2), int(m.group(3))
    pick = [c for c in CARDS if f'data-model="{model}"' in c and f'data-condition="{cond}"' in c][:n]
    return '<ul class="grid sub__stock-grid">\n' + '\n'.join(pick) + '\n      </ul>'
STOCK = re.compile(r'<!-- STOCK model="([^"]+)" condition="([^"]+)" n="(\d+)" -->')

for name, (title, desc) in PAGES.items():
    h = re.sub(r'<title>.*?</title>', f'<title>{title}</title>', head, count=1, flags=re.S)
    h = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{desc}">', h, count=1)
    body = STOCK.sub(stock, read(f'pages7/{name}.main.html'))
    out = h + body.rstrip() + '\n' + foot
    out = out.replace('</body>', f'<script src="js/sub7.js?v={stamp("js/sub7.js")}" defer></script>\n</body>', 1)
    # the page's own routes in the bar and the menu say where the visitor is
    out = re.sub(rf'(<a href="{name}7\.html")(>)', r'\1 aria-current="page"\2', out)
    open(ROOT + f'{name}7.html', 'w', encoding='utf-8', newline='\n').write(out)
    print(f'{name}7.html')
