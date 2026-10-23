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
    'finance': ('Finance Center | Bentley Palm Beach',
                'Bentley Palm Beach Finance Center, West Palm Beach: apply for financing, value your trade, estimate a payment, or speak with the finance team.'),
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

for name, (title, desc) in PAGES.items():
    h = re.sub(r'<title>.*?</title>', f'<title>{title}</title>', head, count=1, flags=re.S)
    h = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{desc}">', h, count=1)
    out = h + read(f'pages7/{name}.main.html').rstrip() + '\n' + foot
    open(ROOT + f'{name}7.html', 'w', encoding='utf-8', newline='\n').write(out)
    print(f'{name}7.html')
