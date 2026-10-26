"""Writes "HANDOFF BENTLEY/design-system.html": the design system as a page,
built on the site's own sheets, so every element on it is the real one.

Components are cut from the handoff pages themselves — with the chain of
ancestors they sit in on the site, so the site's selectors reach them as they
do there — and the home page's chapters are shown live, in frames, at desktop
and phone width. Run after tools/handoff.py:
    python3 tools/handoff.py && python3 tools/ds_page.py"""
import os, re, html as H

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..') + '/'
OUT = ROOT + 'HANDOFF BENTLEY/'
def read(p): return open(OUT + p, encoding='utf-8').read()

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}
def outer(doc, tag, cls, nth=0):
    """the outer HTML of the nth <tag> whose class list holds every class in cls"""
    want = cls.split()
    rx = re.compile(r'<' + tag + r'\b[^>]*\bclass="([^"]*)"[^>]*>')
    hits = [m for m in rx.finditer(doc) if all(c in m.group(1).split() for c in want)]
    if len(hits) <= nth: raise SystemExit(f'not found: {tag}.{cls}')
    m = hits[nth]; i = m.end(); depth = 1
    if tag in VOID: return m.group(0)
    tok = re.compile(r'<(/?)' + tag + r'\b[^>]*>')
    while depth:
        t = tok.search(doc, i)
        if not t: raise SystemExit(f'unclosed: {tag}.{cls}')
        depth += -1 if t.group(1) else 1
        i = t.end()
    return doc[m.start():i]

def up(s):   # a car page's paths, from the root
    return s.replace('="../', '="').replace(', ../', ', ')

def wrap(chain, inner):
    """re-create the ancestors (tag.class) the element sits in on the site"""
    for tag, cls in reversed(chain):
        inner = f'<{tag} class="{cls}">{inner}</{tag}>'
    return inner

index, inv, vdp = read('index.html'), read('inventory.html'), read('vehicles/v66142t.html')

# --- the parts ----------------------------------------------------------------
header   = outer(index, 'header', 'mh')
deck     = outer(index, 'nav', 'hero__deck')
homecard = outer(index, 'li', 'stock__car')
footer   = outer(index, 'footer', 'close')
link     = outer(index, 'a', 'link')
arrows   = ''.join(outer(index, 'button', 'stock__arrow', n) for n in (0, 1))
vdptop   = up(outer(vdp, 'section', 'vdp__top'))
offer    = up(outer(vdp, 'aside', 'offer'))
special  = up(outer(vdp, 'aside', 'special'))
enquire  = up(outer(vdp, 'section', 'vdp__enquire'))
pricing  = up(outer(vdp, 'section', 'pricing'))
# the inner pages: the one page title, and the staff card (the demo site's)
about    = read('about.html')
subhead  = outer(about, 'section', 'srp__head sub__head--pic')
member   = outer(about, 'li', 'sub__member')   # the first: a note and a direct line
SUB      = [('main', 'srp sub')]
TEAM     = [('main', 'srp sub'), ('section', 'sub__team'), ('div', 'page'), ('ul', 'sub__team-grid ds-team')]

# six listing cards, one of each kind the stock has
cards, seen = [], set()
for m in re.finditer(r'<li class="card"[^>]*>', inv):
    i = len(re.findall(r'<li class="card"', inv[:m.start()]))
    c = outer(inv, 'li', 'card', i)
    cond = re.search(r'data-condition="([^"]*)"', c).group(1)
    cert = re.search(r'data-certified="([^"]*)"', c).group(1)
    lease = 'lease' in c.lower()
    key = (cond, cert, lease)
    if key in seen: continue
    seen.add(key)
    name = {'new': 'New', 'used': 'Certified pre-owned' if cert == '1' else 'Pre-owned'}.get(cond, cond)
    cards.append((name + (' · with a lease offer' if lease else ''), c))
    if len(cards) == 6: break

# --- the flags under a card's photograph: one real card of each kind --------------
def first_card(doc, tag, cls, test):
    n = len(re.findall(r'<' + tag + r' class="' + cls, doc))
    for i in range(n):
        c = outer(doc, tag, cls.split()[0] if ' ' not in cls else cls, i)
        if test(c): return c
    raise SystemExit('no card for a flag')
flag_lease   = first_card(inv, 'li', 'card', lambda c: 'card__flag--lease' in c and 'card__flag-cond' not in c)
flag_rebate  = first_card(inv, 'li', 'card', lambda c: 'card__flag-cond' in c)
flag_pending = first_card(index, 'li', 'card', lambda c: 'card__flag--pending' in c)
# Sold has its style but no car carries it: a sold car is never advertised.
# Only the flag is shown, on a photograph — the "Recently sold" record it
# belongs to (no price, no calls) is not part of this build.
media = outer(flag_pending, 'span', 'card__media')
flag_sold = ('<li class="card" style="max-width:420px"><span class="card__link" style="display:block">'
             + media.replace('card__flag--pending', 'card__flag--sold').replace('>Sale Pending<', '>Sold<')
             + '</span></li>')
FLAGS = [
    ('Lease', 'card__flag--lease', 'A lease offer on the car: the payment, then its term and the money down, in Bentley\'s word.', flag_lease, 'srp'),
    ('Lease with a rebate', 'card__flag--lease + card__flag-cond', 'The lease rests on a rebate: the condition line says so, with the credit it needs.', flag_rebate, 'srp'),
    ('Sale Pending', 'card__flag--pending', 'A deal is in progress; the car stays in stock and keeps its price. Bentley Green.', flag_pending, 'home'),
    ('Sold — the flag only', 'card__flag--sold', 'For a "Recently sold" record only, kept apart from the listing, with no price and no calls. A sold car never appears in the listing, its count, its filters or the home rail — so no card carries this flag.', flag_sold, 'srp'),
]

CARD_HOME = [('main', ''), ('section', 'stock is-in'), ('div', 'stock__in'), ('div', 'stock__frame'), ('ul', 'stock__rail stock__four')]
CARD_SRP  = [('main', 'srp'), ('section', 'srp__list'), ('div', 'page'), ('ul', 'grid')]
VDP_SIDE  = [('main', 'vdp'), ('section', 'vdp__body'), ('div', 'page vdp__grid'), ('div', 'vdp__side')]
VDP_MAIN  = [('main', 'vdp'), ('section', 'vdp__body'), ('div', 'page vdp__grid'), ('div', 'vdp__main')]
VDP_ROOT  = [('main', 'vdp')]

# --- tokens, read from the token sheet -----------------------------------------
tok = read('css/tokens.css')
def val(name):
    m = re.search(r'--' + re.escape(name) + r':\s*([^;]+);', tok)
    return m.group(1).strip() if m else ''

PALETTE = [
    ('bentley-green', 'Bentley Green', 'Deep grounds; the brand colour.'),
    ('heritage-white', 'Heritage White', 'The Retailer chapter ground; hover ink on dark grounds.'),
    ('white', 'White', 'Plates on the Satin Linen ground; ink on photographs.'),
    ('black', 'Black', 'Ink on light grounds; night grounds.'),
]
TINTS = [
    ('teal-70', 'Teal 70%', 'The button. Hover #6F836F.'),
    ('satin-linen-40', 'Satin Linen 40%', 'The page ground (theme-satin, the client\'s choice).'),
    ('light-grey-10', 'Light Grey 10%', 'Rules on white.'),
    ('dark-grey-40', 'Dark Grey 40%', 'Secondary ink.'),
]
SYSTEM = [
    ('system-success', 'Success', 'Form states only.'),
    ('system-error', 'Error', 'Form states only.'),
]
TYPE = [
    ('hero', 'Hero', 'Hero slide headline.', 'Continental GT Azure'),
    ('display', 'Display', 'Chapter titles (.h2) and slide words.', 'The Model Range'),
    ('h2', 'H2', 'Prices on the car page; .h2--small.', '$433,038'),
    ('h3', 'H3', 'Card titles, model names, header routes.', '2026 Continental GT Mulliner'),
    ('lead', 'Lead', 'Range names, car page subheads.', 'Each built to order'),
    ('body', 'Body', 'Paragraphs, form inputs, pricing rows.', 'A specialist will confirm availability and arrange a private viewing.'),
    ('sm', 'Small', 'Card facts, offers, hero buttons.', 'Stock V66142T · 30 miles'),
    ('xs', 'Label', 'Labels, price labels, counts (uppercase, tracked); a form field label at the same size in its own case.', 'FINAL PRICE'),
    ('button', 'Button', 'Every button (uppercase, tracked).', 'CONFIRM AVAILABILITY'),
    ('legal', 'Legal', 'Legal text that stands apart, 12px on 16px, Regular, in its own case — as bentleymotors.com: the reCAPTCHA line, the copyright, the price disclaimer, the full lease terms. Never what stands beside a price.', 'This site is protected by reCAPTCHA and the Google Privacy Policy and Terms of Service apply.'),
]
SPACE = [f'space-{i}' for i in range(1, 12)]

SECTIONS = [
    ('top', 'Hero', 'Full-screen photographs, one motor car each, turned by the visitor — never autoplay, never video. The slide count is locked at the photograph\'s lower right on every slide. Words stand on the road or the ground below the car, never on it. Under the hero: NEW INVENTORY and PRE-OWNED INVENTORY side by side, SPECIAL OFFERS centred beneath — the same on every slide, no gap between slide and buttons.'),
    ('range', 'The Model Range', '"The Model Range, / five, each built to order." Five tiles, one per model line (Torcal included); the model kind sits above the hairline, over the name. Five across from 768px.'),
    ('mulliner', 'Bespoke — Mulliner', 'One picture, one line, one route.'),
    ('commission', 'Split', 'Copy on the ground, the picture on its own; the mirror variant swaps sides (Care).'),
    ('pre-owned', 'Certified pre-owned', 'One car per slide, turned by the visitor; its figures on a light frosted plate.'),
    ('continental', 'Scene', 'A full-bleed photograph with the words in its own shaded corner.'),
    ('stock', 'New in stock', 'Four cars in one row, three in view, centred; arrows at the sides; title centred. Never stacked in rows.'),
    ('sell', 'Sell your Bentley', 'The photograph across the section; the words on a plate at the right, high, clear of the car.'),
    ('care', 'Split — mirror', 'Service and parts; the split with the picture on the left.'),
    ('retailer', 'Retailer', 'Okeechobee Boulevard — on its own ground, Heritage White.'),
    ('contact', 'Footer', 'Index of routes, addresses, hours, social, legal.'),
]

def swatch(token, name, use, dark=False):
    hexv = val(token)
    return f'''<figure class="ds-swatch" data-token="--{token}">
  <div class="ds-swatch__chip" style="background:var(--{token})"><span class="ds-cr"></span></div>
  <figcaption><b>{name}</b><code>--{token}</code><code>{hexv}</code><span>{use}</span></figcaption>
</figure>'''

def frame(anchor, w, h, scale):
    return (f'<div class="ds-frame" style="width:{w*scale:.0f}px;height:{h*scale:.0f}px">'
            f'<iframe src="index.html#{anchor}" width="{w}" height="{h}" loading="lazy" scrolling="no" '
            f'style="transform:scale({scale})" title="{anchor} at {w}px"></iframe>'
            f'<span class="ds-frame__w">{w}px</span></div>')

pal = '\n'.join(swatch(*p) for p in PALETTE)
tin = '\n'.join(swatch(*p) for p in TINTS)
sysw = '\n'.join(swatch(*p) for p in SYSTEM)

types = '\n'.join(f'''<div class="ds-type" data-token="--text-{t}">
  <div class="ds-type__meta"><b>{n}</b><code>--text-{t}</code><code class="ds-type__val">{H.escape(val('text-' + t))}</code><span class="ds-px"></span><span>{u}</span></div>
  <div class="ds-type__sample" style="font-size:var(--text-{t});{'text-transform:uppercase;letter-spacing:var(--track-label);' if t in ('xs','button') else ''}{'line-height:var(--leading-display);letter-spacing:var(--track-display);font-weight:300;' if t in ('hero','display','h2') else ''}{'line-height:1rem;letter-spacing:0.01em;font-weight:400;color:var(--ink-2);' if t == 'legal' else ''}">{s}</div>
</div>''' for t, n, u, s in TYPE)

spaces = '\n'.join(f'<div class="ds-space"><code>--{s}</code><span class="ds-space__bar" style="width:var(--{s})"></span><span class="ds-px-w" data-var="--{s}"></span></div>' for s in SPACE)

flags = '\n'.join(f'<div class="ds-item"><p class="ds-cap">{H.escape(n)} · <code>.{k}</code></p><p class="ds-note" style="font-size:var(--text-sm)">{H.escape(u)}</p>{wrap(CARD_SRP if w == "srp" else CARD_HOME, cc)}</div>' for n, k, u, cc, w in FLAGS)
cardgrid = '\n'.join(f'<div class="ds-item"><p class="ds-cap">{H.escape(n)}</p>{wrap(CARD_SRP, c)}</div>' for n, c in cards)

sections = '\n'.join(f'''<article class="ds-section" id="ds-{a}">
  <h3 class="ds-h3">{n}</h3><p class="ds-note">{u}</p>
  <div class="ds-frames">{frame(a, 1440, 900, 0.5)}{frame(a, 390, 844, 0.55)}</div>
  <p class="ds-cap"><a href="index.html#{a}">Open in the page →</a></p>
</article>''' for a, n, u in SECTIONS)

TOC = [('handoff', 'Handoff'), ('colour', 'Colour'), ('type', 'Type'), ('space', 'Space & layout'), ('buttons', 'Buttons'),
       ('links', 'Links & labels'), ('forms', 'Forms'), ('cards', 'Vehicle cards'), ('vdp', 'Car page'),
       ('header', 'Header'), ('sections', 'Home chapters'), ('inner', 'Inner pages'), ('rules', 'Rules')]
toc = ''.join(f'<a href="#{a}">{n}</a>' for a, n in TOC)

page = f'''<!DOCTYPE html>
<html lang="en" class="theme-satin">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Bentley Palm Beach — Design System</title>
<link rel="stylesheet" href="css/tokens.css">
<link rel="stylesheet" href="css/site.css">
<link rel="stylesheet" href="css/cards.css">
<link rel="stylesheet" href="css/inventory.css">
<link rel="stylesheet" href="css/vehicle.css">
<link rel="stylesheet" href="css/theme.css">
<link rel="stylesheet" href="css/static.css">
<link rel="stylesheet" href="css/subpages.css">
<style>
  /* The design-system page's own frame. Everything inside .ds-stage is the
     site's real markup on the site's real sheets. */
  .ds {{ max-width: 1320px; margin: 0 auto; padding: 0 var(--gutter) var(--space-10); color: var(--ink); }}
  .ds-top {{ padding: var(--space-9) 0 var(--space-6); border-bottom: 1px solid var(--rule); }}
  .ds-top h1 {{ font-size: var(--text-display); font-weight: 300; line-height: var(--leading-display); letter-spacing: var(--track-display); margin: 0 0 var(--space-4); }}
  .ds-top p {{ max-width: 44rem; margin: 0 0 var(--space-3); font-size: var(--text-body); line-height: var(--leading-body); }}
  .ds-toc {{ position: sticky; top: 0; z-index: 50; display: flex; flex-wrap: wrap; gap: var(--space-2) var(--space-5); padding: var(--space-4) 0; background: var(--day); border-bottom: 1px solid var(--rule); font-size: var(--text-xs); letter-spacing: var(--track-label); text-transform: uppercase; }}
  .ds-toc a {{ color: var(--ink); text-decoration: none; }}
  .ds-toc a:hover {{ text-decoration: underline; text-underline-offset: 4px; }}
  .ds-part {{ padding: var(--space-9) 0 var(--space-6); border-bottom: 1px solid var(--rule); scroll-margin-top: 64px; }}
  .ds-h2 {{ font-size: var(--text-h2); font-weight: 300; line-height: var(--leading-display); margin: 0 0 var(--space-3); }}
  .ds-h3 {{ font-size: var(--text-h3); font-weight: 300; margin: var(--space-7) 0 var(--space-2); }}
  .ds-note {{ max-width: 46rem; margin: 0 0 var(--space-5); font-size: var(--text-body); line-height: var(--leading-body); color: var(--ink); }}
  .ds-cap {{ margin: var(--space-3) 0; font-size: var(--text-xs); letter-spacing: var(--track-label); text-transform: uppercase; color: var(--ink); }}
  .ds-cap a {{ color: var(--ink); }}
  .ds code {{ font: 0.875rem/1.4 ui-monospace, Menlo, monospace; color: var(--ink); }}
  .ds-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: var(--space-5); }}
  .ds-swatch {{ margin: 0; background: var(--white); border: 1px solid var(--rule); }}
  .ds-swatch__chip {{ position: relative; height: 120px; border-bottom: 1px solid var(--rule); }}
  .ds-cr {{ position: absolute; left: var(--space-3); bottom: var(--space-3); font-size: 0.875rem; }}
  .ds-swatch figcaption {{ display: grid; gap: 2px; padding: var(--space-3) var(--space-4) var(--space-4); font-size: 0.875rem; line-height: 1.45; }}
  .ds-swatch b {{ font-weight: 400; font-size: var(--text-body); }}
  .ds-type {{ display: grid; grid-template-columns: 260px 1fr; gap: var(--space-5); align-items: baseline; padding: var(--space-5) 0; border-top: 1px solid var(--rule); }}
  .ds-type__meta {{ display: grid; gap: 2px; font-size: 0.875rem; line-height: 1.45; }}
  .ds-type__meta b {{ font-weight: 400; font-size: var(--text-body); }}
  .ds-type__sample {{ min-width: 0; overflow-wrap: anywhere; }}
  .ds-space {{ display: grid; grid-template-columns: 140px 1fr 80px; gap: var(--space-4); align-items: center; padding: var(--space-2) 0; }}
  .ds-space__bar {{ display: block; height: 16px; background: var(--teal-70); }}
  .ds-table {{ width: 100%; border-collapse: collapse; font-size: var(--text-sm); }}
  .ds-table th, .ds-table td {{ text-align: left; padding: var(--space-3) var(--space-4) var(--space-3) 0; border-top: 1px solid var(--rule); vertical-align: top; }}
  .ds-table th {{ font-weight: 400; font-size: var(--text-xs); letter-spacing: var(--track-label); text-transform: uppercase; }}
  .ds-stage {{ position: relative; padding: var(--space-6); background: var(--day); border: 1px solid var(--rule); overflow: hidden; }}
  .ds-stage--band {{ padding: 0; }}
  .ds-stage--band .srp__head.sub__head--pic {{ margin: 0; padding-top: 0 !important; }}   /* on the page this clears the fixed bar */
  /* the stage reset above makes every .page static; the title's words sit on the photograph as on the page */
  @media (min-width: 768px) {{
    .ds-stage--band .sub__band-words {{ position: absolute !important; left: 0; right: 0; bottom: 0; z-index: 1; padding: 0 clamp(1.5rem, 3vw, 3rem) clamp(2rem, 4vw, 3.5rem) !important; }}
  }}
  .ds-team {{ grid-template-columns: minmax(0, 413px) !important; margin: 0 !important; }}   /* one card, at its width on the page at 1920 */
  .ds-stage--white {{ background: var(--white); }}
  .ds-stage--dark {{ background: var(--black); color: var(--white); --ink: var(--white); --rule-strong: rgba(255,255,255,0.7); }}
  .ds-stage--photo {{ background: #040404 url("assets/bm/2026/spur-norcal.webp") center / cover; --ink: var(--white); color: var(--white); }}
  .ds-row {{ display: flex; flex-wrap: wrap; gap: var(--space-5); align-items: center; }}
  .ds-item {{ min-width: 0; }}
  .ds-cards {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(330px, 1fr)); gap: var(--space-6); align-items: start; }}
  .ds-cards .grid, .ds-cards .stock__rail {{ display: block; margin: 0; padding: 0; transform: none; width: auto; }}
  .ds-cards .card {{ width: 100%; max-width: 420px; flex: none; margin: 0; transform: none; }}
  .ds-cards main, .ds-cards section, .ds-cards .page, .ds-cards .stock__in, .ds-cards .stock__frame,
  .ds-stage main, .ds-stage section, .ds-stage .page {{ min-height: 0; height: auto; padding: 0; margin: 0; width: auto; max-width: none; position: static; }}
  .ds-stage .mh {{ position: relative !important; top: auto; transform: none; }}
  .ds-stage--header {{ padding: 0; }}
  .ds-stage .vdp__grid {{ display: block; }}
  .ds-stage .vdp__side, .ds-stage .vdp__main {{ width: auto; max-width: 460px; }}
  .ds-stage .stock__in, .ds-stage .stock__frame {{ padding: 0; margin: 0; min-height: 0; height: auto; }}
  .ds-stage .stock__rail {{ display: block; transform: none !important; }}
  .ds-stage .stock__car {{ width: 419px !important; max-width: 100%; flex: none; }}   /* its width in the rail at 1440 */
  .ds-frames {{ display: flex; flex-wrap: wrap; gap: var(--space-5); align-items: flex-start; }}
  .ds-frame {{ position: relative; overflow: hidden; border: 1px solid var(--rule); background: var(--white); }}
  .ds-frame iframe {{ border: 0; transform-origin: 0 0; display: block; }}
  .ds-frame__w {{ position: absolute; right: 6px; bottom: 6px; padding: 2px 6px; background: rgba(4,4,4,0.7); color: #fff; font-size: 0.875rem; }}
  .ds-rules {{ display: grid; gap: var(--space-5); grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }}
  .ds-rules section {{ padding: var(--space-5); background: var(--white); border: 1px solid var(--rule); }}
  .ds-rules h3 {{ margin: 0 0 var(--space-3); font-size: var(--text-h3); font-weight: 300; }}
  .ds-rules li {{ margin: 0 0 var(--space-2); font-size: var(--text-body); line-height: var(--leading-body); }}
  /* states shown at rest */
  .ds-hover.btn {{ background: var(--teal-hover); border-color: var(--teal-hover); }}
  .ds-hover.btn--line {{ background: rgba(4, 4, 4, 0.05); border-color: var(--ink); }}
  .ds-stage--dark .ds-hover.btn--line, .ds-stage--photo .ds-hover.btn--line {{ background: rgba(255,255,255,0.06); border-color: var(--white); }}
  .ds-focus {{ outline: 2px solid var(--ink); outline-offset: 3px; }}
  @media (max-width: 767px) {{
    .ds-toc {{ flex-wrap: nowrap; overflow-x: auto; white-space: nowrap; }}
    .ds-type {{ grid-template-columns: 1fr; gap: var(--space-2); }}
    .ds-space {{ grid-template-columns: 110px 1fr 60px; }}
  }}
</style>
</head>
<body>
<div class="ds">
  <header class="ds-top">
    <p class="ds-cap">Bentley Palm Beach · Direction 7 · handoff</p>
    <h1>Design System</h1>
    <p>Every element of the site, on the site's own stylesheets: what you see here is the real component, not a drawing of it. Values are read from <code>css/tokens.css</code>; the theme is Satin Linen 40% (<code>&lt;html class="theme-satin"&gt;</code>).</p>
    <p>The page is static by the client's brief (2026-10-04, an older clientele): no scroll effects. Photographs are the design. The one exception is the model pages' hero: Bentley's own stage loop, muted, from 1024px, with a pause button, replaced by its photograph on phones and when the visitor asks for less motion.</p>
  </header>
  <nav class="ds-toc" aria-label="Design system">{toc}</nav>

  <section class="ds-part" id="handoff">
    <h2 class="ds-h2">Handoff — what to change on the demo</h2>
    <p class="ds-note">For the developers bringing the demo (<i>bramanbentleypalmbeach.aandemo.com</i>) in line with the approved design. Each row: the page on the demo, the approved page on git, and what changes. <b>How to work:</b> open both side by side; take spacing, sizes and colours from <code>css/tokens.css</code> and the components below in this design system — never from a screenshot; copy and figures exactly as on the approved page (they are the dealer's own or bentleymotors.com's, verbatim); keep every photograph's crop (<code>object-position</code>) as set. When something on the demo cannot follow a rule here, ask before inventing — the site is <b>strictly Bentley style</b>: no device, rule, mark or ornament that Bentley's guidelines, bentleymotors.com or these pages do not already have.</p>

    <h3 class="ds-h3">1 · Site-wide — every page</h3>
    <table class="ds-table"><thead><tr><th>Area</th><th>Change</th><th>Where in this system</th></tr></thead><tbody>
      <tr><td><b>Menu</b></td><td>The demo's own navigation, as built: eight groups; a panel per group; inline in the bar from 1536px, an accordion below. Routes to our pages where we have one. "Browse by Make" and "One-Owner Vehicles" left out (other brands may not be advertised).</td><td>Header</td></tr>
      <tr><td><b>Recently Viewed</b></td><td>The tab at the lower right (count, then the cars: photograph, name, <b>Final price · Stock</b> — never MSRP). Nothing else may sit under it.</td><td>Header</td></tr>
      <tr><td><b>Page title</b></td><td>Every inner page: eyebrow <i>Braman Bentley Palm Beach</i>, the title in its own case (Finance Department, Contact Us). Capitals only for model names (TORCAL, MULLINER).</td><td>Inner pages → The page title</td></tr>
      <tr><td><b>Type sizes</b></td><td>Only the roles in the type table. Legal lines (reCAPTCHA, disclaimers) 12/16px, as bentleymotors.com sets them.</td><td>Type</td></tr>
      <tr><td><b>Forms</b></td><td>Two columns (one on a phone). Bentley's floating labels on the line; 1px line, 2px on focus, no box; 24px square check box, 20px circle radio, Teal 70% edge. <i>Best time to contact</i> under Phone. <i>Fields marked with (*) are required.</i> is the form's first line, inside its plate.</td><td>Forms · Rules</td></tr>
      <tr><td><b>Dropdowns</b></td><td>Closed: the native select on the field's line, firm chevron. Open: the site's own list dropped from that line, left-aligned, at least the field's width, 40px rows, model names in capitals, car counts on the listing's filters, height = its choices. Phones keep the native picker.</td><td>Rules → Forms</td></tr>
      <tr><td><b>Enquiry block</b></td><td>Beside the form: heading, Our Location, the department's phone, Get directions / Send to phone, and the department's hours under them. From 1024px the column is as tall as the form — heading on the plate's top edge, last hours rule on its bottom edge.</td><td>Rules → Forms</td></tr>
      <tr><td><b>Vehicle cards</b></td><td>Every mark (lease, Sale Pending, New Arrival, Sold, Certified Pre-Owned) as a band <b>under</b> the photograph, never on it. Empty room for the band only in a row where a card has a mark. On the car page, no flag on the photographs.</td><td>Vehicle cards · Car page</td></tr>
      <tr><td><b>Model Range (home)</b></td><td>Each model's tile opens its model page (Bentayga → Bentayga Speed; Flying Spur, Torcal, Continental GT, GT Convertible → theirs).</td><td>Home chapters</td></tr>
    </tbody></table>

    <h3 class="ds-h3">2 · Pages</h3>
    <table class="ds-table"><thead><tr><th>Page</th><th>Approved (git)</th><th>What changes on the demo</th></tr></thead><tbody>
      <tr><td><b>Contact Us</b></td><td><a href="https://aan-git.github.io/BRAMAN_BENTLEY/contact7.html">contact7.html</a></td><td>New design: picture head; message + form; Opening Hours as a chapter (Sales, Service, Parts in a row); location chapter with the showroom photograph; map, toned Heritage White.</td></tr>
      <tr><td><b>Finance Department</b></td><td><a href="https://aan-git.github.io/BRAMAN_BENTLEY/finance7.html">finance7.html</a></td><td>Four tiles (Finance application — the lead, Value your trade, Payment calculator, View inventory); enquiry with Sales Hours; Google reviews rail last.</td></tr>
      <tr><td><b>About Us / Meet the Staff</b></td><td><a href="https://aan-git.github.io/BRAMAN_BENTLEY/about7.html">about7.html</a></td><td>Intro in the page column; staff cards as on the demo (4:3 portrait, job title, name, direct line, a note such as "Also speaks Russian" under the phone); Opening Hours chapter; enquiry; map.</td></tr>
      <tr><td><b>Parts Department</b></td><td><a href="https://aan-git.github.io/BRAMAN_BENTLEY/parts7.html">parts7.html</a></td><td>Inner-page template. Head: Bentley's technician photograph. Four tiles, each picture showing its route. Department chapter with Bentley's "Genuine parts" text and the Parts Manager card; enquiry with Parts Hours; map; Google reviews last, below the map. <i>Buy tires</i> link on the demo names Edmonton — confirm the URL.</td></tr>
      <tr><td><b>Sell Your Vehicle</b></td><td><a href="https://aan-git.github.io/BRAMAN_BENTLEY/sell7.html">sell7.html</a></td><td>The client's order: words, then the form (two columns), then hours and location under it. Photos field: drag-and-drop zone with thumbnails, each with its own remove.</td></tr>
      <tr><td><b>Payment Calculator</b></td><td><a href="https://aan-git.github.io/BRAMAN_BENTLEY/calculator7.html">calculator7.html</a></td><td>Working calculator (standard amortised payment, <code>js/sub.js</code>); result plate on Bentley Green; on a phone the result above the fields.</td></tr>
      <tr><td><b>Ask a Tech</b></td><td><a href="https://aan-git.github.io/BRAMAN_BENTLEY/ask-a-tech7.html">ask-a-tech7.html</a></td><td>Rebuilt on the inner-page template, in the client's order: picture head, the words, the form (two columns, the note inside it), then in a row: Take the Next Step (four routes), Service Hours, Our Location. <b>The Sunbit banner is rebuilt</b>: the demo's artwork advertises <i>Rolls-Royce</i> parts and service on the Bentley site, with its words baked into the picture. Now a plate under the head — a Bentley photograph at the left, the banner's words as text on Bentley Green ("Bentley" in place of "Rolls-Royce", to be confirmed by the client), one white <i>See your options</i> call to the Sunbit application page (confirm the live URL).</td></tr>
      <tr><td><b>2027 Bentayga Speed</b></td><td><a href="https://aan-git.github.io/BRAMAN_BENTLEY/bentayga-speed7.html">bentayga-speed7.html</a></td><td>The AAN master model-page layout: hero, key figures on Bentley Green, engine, film, exterior / interior stories, cars in stock, enquiry.</td></tr>
      <tr><td><b>Model pages</b> (new)</td><td><a href="https://aan-git.github.io/BRAMAN_BENTLEY/flying-spur7.html">flying-spur7</a> · <a href="https://aan-git.github.io/BRAMAN_BENTLEY/torcal7.html">torcal7</a> · <a href="https://aan-git.github.io/BRAMAN_BENTLEY/continental-gt7.html">continental-gt7</a> · <a href="https://aan-git.github.io/BRAMAN_BENTLEY/continental-gtc7.html">continental-gtc7</a></td><td>Our model page: chapters The Range · Exterior · Interior · Performance · Personalisation · In Stock, with a chapter bar under the hero. Bentley's stage loop in the hero where Bentley has one (from 1024px, pause button, photograph on phones and with reduced motion); the official Bentley Motors film from the hero's third call. Copy, US figures, photographs and films from bentleymotors.com / Bentley Motors only.</td></tr>
      <tr><td><b>Inventory (SRP)</b></td><td><a href="https://aan-git.github.io/BRAMAN_BENTLEY/inventory7.html">inventory7.html</a></td><td>Card marks and dropdowns as in section 1. Filters work from the URL (<code>?condition=new&amp;model=Bentayga</code>).</td></tr>
      <tr><td><b>Car page (VDP)</b></td><td><a href="https://aan-git.github.io/BRAMAN_BENTLEY/vehicles7/v66142t.html">vehicles7/…</a></td><td>No lease flag on the photographs — the lease is the offer's, under <i>Lease special</i>. The client form as in section 1.</td></tr>
    </tbody></table>

    <h3 class="ds-h3">3 · Files in this handoff</h3>
    <p class="ds-note">Plain HTML, CSS and a little vanilla JS — no build step. Stylesheets in this order: <code>tokens, site, cards, inventory, vehicle, theme, static, subpages</code> (see <code>README.md</code>). The approved pages here are named without the "7" of the git preview (<code>parts.html</code> = <code>parts7.html</code>). Photographs and films under <code>assets/bm/2026/</code> are Bentley Motors' own, used with the retailer's authorisation; keep their file names.</p>
  </section>

  <section class="ds-part" id="colour">
    <h2 class="ds-h2">Colour</h2>
    <p class="ds-note">Only the colours of the Bentley Retailer Website Guidelines. Each chip shows the contrast of black and of white type on it.</p>
    <h3 class="ds-h3">Approved palette</h3><div class="ds-grid">{pal}</div>
    <h3 class="ds-h3">Percentage tints</h3><div class="ds-grid">{tin}</div>
    <h3 class="ds-h3">System</h3><div class="ds-grid">{sysw}</div>
    <h3 class="ds-h3">Roles</h3>
    <table class="ds-table"><thead><tr><th>Token</th><th>Value</th><th>Use</th></tr></thead><tbody>
      <tr><td><code>--day</code></td><td>Satin Linen 40%</td><td>The page ground (theme-satin).</td></tr>
      <tr><td><code>--day-plate</code> / <code>--plate</code></td><td>White / White 94%</td><td>Plates on the ground: price plate, cards, Sell plate.</td></tr>
      <tr><td><code>--ink</code></td><td>Black; White on photographs</td><td>Type. Inside the hero, Mulliner and the scene from 768px the ink turns white.</td></tr>
      <tr><td><code>--ink-secondary</code></td><td>Dark Grey 40%</td><td>Secondary type.</td></tr>
      <tr><td><code>--rule</code></td><td>Black 16%</td><td>Hairlines on the Satin Linen ground.</td></tr>
      <tr><td><code>--bar-ground</code> / <code>--glass</code></td><td>Satin Linen 95% / 86%</td><td>The header once scrolled; frosted plates.</td></tr>
      <tr><td><code>--ground-deep</code></td><td>Bentley Green</td><td>Deep chapters.</td></tr>
    </tbody></table>
  </section>

  <section class="ds-part" id="type">
    <h2 class="ds-h2">Type</h2>
    <p class="ds-note">One family: the licensed Bentley face, Light (300) and Regular (400), with Arial as the required fallback (<code>--font</code>). Sizes are fluid — each shows its value at this window's width. Leading: display {val('leading-display')}, headings {val('leading-heading')}, body {val('leading-body')}. Tracking: display {val('track-display')}, labels {val('track-label')}, body {val('track-body')}. Labels, buttons and routes are uppercase.</p>
    <p class="ds-note"><b>Capitals and titles (Alex, 2026-10-26).</b> A title is never set in capitals: page titles, section headings and the small line over a title stay in their own case — Title Case for a name (<i>Finance Department</i>, <i>Opening Hours</i>), as bentleymotors.com writes them, in Bentley Light with no tracking. Capitals in a heading belong to the names of the models only — <b>MULLINER</b>, <b>TORCAL</b>. Uppercase stays where it already is: labels (job titles, field labels, days, price labels), buttons and the header's routes, all through the CSS, never typed.</p>
    {types}
    <h3 class="ds-h3">Every size — where it is used, and where it belongs</h3>
    <p class="ds-note">Measured on every page of the site at 390px and 1440px (the theme, Satin Linen, sets body 18px and small 16px). Use the role, not a number: a new element takes the role whose "belongs to" fits it. The last column names the intended exceptions; anything not listed there sits exactly on a step.</p>
    <table class="ds-table"><thead><tr><th>Role · token</th><th>Phone → desktop</th><th>Weight · case</th><th>Used now</th><th>Belongs to</th><th>To align</th></tr></thead><tbody>
      <tr><td><b>Legal</b><br><code>--text-legal</code></td><td>12 / 16px leading</td><td>Regular · own case</td><td>reCAPTCHA line under every form; footer copyright; the listing's price disclaimer; the car page's disclaimer and full lease terms</td><td>Legal text that stands apart. Nothing else.</td><td>—</td></tr>
      <tr><td><b>Label</b><br><code>--text-xs</code></td><td>14 · 14</td><td>Regular · UPPERCASE, tracking 0.1em</td><td>Header routes and the menu's group names; the number in the bar; the foot bar on a phone; text routes ("Read more ›"); job titles, price labels, filter labels; card flags; captions</td><td>Functional labels — never running text, never a heading.</td><td>—</td></tr>
      <tr><td><b>Label, own case</b><br><code>--text-xs</code></td><td>14 · 14</td><td>Regular · own case</td><td>Form field labels (First name*, Best time to contact*) as on bentleymotors.com; "Site Terms &amp; Conditions" in the bar; slide and photo counts (01 / 03); a model's kind over its name; the footer's address line</td><td>Small functional text that is read as words, not as a label.</td><td>—</td></tr>
      <tr><td><b>Small</b><br><code>--text-sm</code></td><td>16 · 16</td><td>Regular · own case</td><td>Card facts; the fees in a price; VIN; a lease's term and conditions beside the offer; a staff member's direct line and note; review rating</td><td>Secondary copy on a card or beside a price — including the price disclosures that must stay clear (FTC).</td><td>—</td></tr>
      <tr><td><b>Button</b><br><code>--text-button</code></td><td>14 → 16</td><td>Regular · UPPERCASE, tracked</td><td>Every button; Bentley Inventory in the bar</td><td>Buttons only.</td><td>—</td></tr>
      <tr><td><b>Body</b><br><code>--text-body</code></td><td>18 · 18</td><td>Regular (form inputs Light)</td><td>Paragraphs; result counts; form inputs and choices; record rows (hours, specifications)</td><td>All running text; what a visitor types; data rows.</td><td>—</td></tr>
      <tr><td><b>Lead</b><br><code>--text-lead</code></td><td>18 → 24</td><td>Regular · own case</td><td>The line under a chapter title; Bespoke's line; on inner pages the group headings (Sales, Service, Parts), department names in the hours, "Our Location"; the price in the car page's phone bar</td><td>A title's lead line; group headings (<code>h3</code>) on inner pages.</td><td>—</td></tr>
      <tr><td><b>H3</b><br><code>--text-h3</code></td><td>22 → 30</td><td>Light · own case (model names Regular)</td><td>Card titles and card prices; section headings on inner pages (<code>h2.h2--small</code>: Opening Hours, Contact Information, Reviews); model names in the range; the routes inside Menu</td><td>A card's or model's name; an inner page's section headings.</td><td>—</td></tr>
      <tr><td><b>Staff name</b><br><code>min(--text-h3, 1.65rem)</code></td><td>22 → 26.4</td><td>Light · own case</td><td>The name on a staff card</td><td>The staff card only — the demo site's size.</td><td>—</td></tr>
      <tr><td><b>Inner page title</b><br><code>.sub__title</code></td><td>32 → 50</td><td>Light · own case</td><td>Finance Department, About Us, Contact Us</td><td>The one <code>h1</code> of an inner page (Parts, Sell, the calculator, the model pages too).</td><td>—</td></tr>
      <tr><td><b>H2</b><br><code>--text-h2</code></td><td>32 → 56</td><td>Light</td><td>The price in the car page's offer (<code>.offer__price</code>); the car page's section headings (Enquire, Pricing details, More on the floor — <code>h2--small</code> there)</td><td>A section heading one step under its page's title: under the car's name (Display) on a car page. On an inner page, whose title is smaller, the same heading takes H3.</td><td>—</td></tr>
      <tr><td><b>Display</b><br><code>--text-display</code></td><td>36 → 64</td><td>Light · own case</td><td>Chapter titles on the home page (The Model Range, New Bentley in stock, At home wherever it is parked); the listing's title (Inventory); the car's name on its page</td><td>Chapter titles; the title of the listing and of a car page.</td><td>Two held forms, both intended — keep them: <b>held to the screen</b>, <code>min(var(--text-display), 6.6vh)</code>, on the home page's one-screen chapters, so a chapter stays one screen tall on a short screen (59px at 1440×900: Specified by you, Expert care, Okeechobee Boulevard); and <b>fitted to its plate</b> over a photograph, between H2 and Display (Sell us your car 40, the pre-owned slides' car names 46, Bespoke 60). The car page's head price (<code>.vdp__price-value</code>, 28 → 38) is the plate's one figure and keeps its own size. Nothing else on the site may sit between the steps.</td></tr>
      <tr><td><b>Hero</b><br><code>.hero__title</code></td><td>44 → 66 (at 1440)</td><td>Light · UPPERCASE</td><td>The slide's title on the home page's hero (The Azure range)</td><td>The hero slide's title only: a model or range name, which may be in capitals (the capitals rule).</td><td>—</td></tr>
    </tbody></table>
  </section>

  <section class="ds-part" id="space">
    <h2 class="ds-h2">Space &amp; layout</h2>
    <p class="ds-note">A 4px base. Corners are square everywhere (<code>--radius: 0</code>).</p>
    {spaces}
    <h3 class="ds-h3">Format</h3>
    <table class="ds-table"><thead><tr><th>Token</th><th>Value</th><th>Use</th></tr></thead><tbody>
      <tr><td><code>--measure-page</code></td><td>{val('measure-page')}</td><td>The page column.</td></tr>
      <tr><td><code>--gutter</code></td><td>{val('gutter')}</td><td>Column gutter and page edge.</td></tr>
      <tr><td><code>--section-y</code></td><td>{val('section-y')}</td><td>Air above and below a chapter.</td></tr>
      <tr><td><code>--bar-h</code> / <code>--bar-h-compact</code></td><td>{val('bar-h')} / {val('bar-h-compact')}</td><td>The header, at rest and once scrolled.</td></tr>
      <tr><td><code>--control-h</code></td><td>{val('control-h')}</td><td>Buttons and fields.</td></tr>
      <tr><td><code>--measure-head</code> / <code>--measure-body</code></td><td>{val('measure-head')} / {val('measure-body')}</td><td>Line lengths for headings and paragraphs.</td></tr>
    </tbody></table>
    <h3 class="ds-h3">Breakpoints</h3>
    <table class="ds-table"><thead><tr><th>Width</th><th>What changes</th></tr></thead><tbody>
      <tr><td>&lt; 768px</td><td>Phone: one column; photographs as bands above the words; the routes bar at the foot of the screen.</td></tr>
      <tr><td>768–1023px</td><td>Tablet: two columns where the desktop has more; the Model Range already five across.</td></tr>
      <tr><td>≥ 1024px</td><td>Desktop: the header's two lines; chapters at full screen.</td></tr>
      <tr><td>1280 · 1360 · 1500px</td><td>The header tightens its routes below each of these.</td></tr>
    </tbody></table>
  </section>

  <section class="ds-part" id="buttons">
    <h2 class="ds-h2">Buttons</h2>
    <p class="ds-note">Two kinds. <b>.btn</b> — Teal 70%, white type: the call to act. <b>.btn--line</b> — a hairline outline: the second call, beside or under a first. Uppercase, tracked, square, {val('control-h')} high. Hover changes colour only, over {val('dur-2')}.</p>
    <h3 class="ds-h3">On the Satin Linen ground</h3>
    <div class="ds-stage"><div class="ds-row">
      <a class="btn" href="#buttons">New inventory</a><a class="btn ds-hover" href="#buttons">Hover</a><a class="btn ds-focus" href="#buttons">Focus</a>
      <a class="btn btn--line" href="#buttons">Pre-owned inventory</a><a class="btn btn--line ds-hover" href="#buttons">Hover</a>
    </div></div>
    <h3 class="ds-h3">On a photograph or a dark ground</h3>
    <div class="ds-stage ds-stage--photo"><div class="ds-row">
      <a class="btn" href="#buttons">Request test drive</a><a class="btn btn--line" href="#buttons">Explore</a><a class="btn btn--line ds-hover" href="#buttons">Hover</a>
    </div></div>
    <h3 class="ds-h3">Under the hero — the same on every slide</h3>
    <div class="ds-stage">{deck}</div>
    <h3 class="ds-h3">Rail arrows</h3>
    <div class="ds-stage"><div class="ds-row">{arrows}</div></div>
  </section>

  <section class="ds-part" id="links">
    <h2 class="ds-h2">Links &amp; labels</h2>
    <div class="ds-stage"><div class="ds-row" style="align-items:baseline">
      <p class="label">Label · uppercase, tracked</p>
      {link}
      <span class="asterisk">*</span>
    </div></div>
  </section>

  <section class="ds-part" id="forms">
    <h2 class="ds-h2">Forms</h2>
    <p class="ds-note">One form wherever a form is — the car page's enquiry, every inner page — drawn as bentleymotors.com draws its own (Request a test drive): the label on the field's line where the value will go — Body Light, Dark Grey 40%, in its own case — rising above the line at 14px once the field is chosen or filled (<code>js/page.js</code> marks the fields; without it the labels stay above their fields); the value in Body Light on a 1px line in the ink, 2px when the field has focus, no box round it; a list shows only its label until something is chosen; two columns, one on a phone; a list ends in the thin open chevron; the check box a 24px square with a 2px edge in Teal 70%, filled with a white tick when ticked; a choice a 20px circle in the same edge, a dot when chosen; group headings (<code>.sub__form-h</code>) in Bentley Light at H3. Photographs: a dashed field to drop them on or press Upload; each chosen one appears as a thumbnail with its name and its own ×. Error and success colours are for form states only.</p>
    <div class="ds-stage ds-stage--white">{wrap(VDP_ROOT, enquire)}</div>
  </section>

  <section class="ds-part" id="cards">
    <h2 class="ds-h2">Vehicle cards</h2>
    <p class="ds-note">One card everywhere: photograph, name, facts, and the price plate — <b>Final price</b> leads; MSRP and the two dealer charges sit beneath as the working. A lease offer carries its term and the money down (Bentley's word: "down").</p>
    <h3 class="ds-h3">Flags under the photograph</h3>
    <p class="ds-note">Never on the photograph — nothing may cover the car (the client's Bentley note). One flag at a time, as a band across the card directly under its photograph. <b>The band's room is kept only in a row where a card carries a flag</b>: the other cards in that row keep the same empty room, so the photographs, names and prices stay level across the row; a row with no flag has no band and no empty room. A row of lease flags (three lines) is taller than a row of one-line marks, and only that row. Built with CSS subgrid (each card spans three rows: photograph, band, body), so the browser levels each row on its own; on the one-row home rail, <code>:has()</code> keeps the room only when the rail holds a flag. <b>Certified Pre-Owned</b> is a band mark of its own (the page's ground, <code>--day</code>, black type, a hairline above), for a certified car with no other flag; a certified car with a lease keeps "Certified by Bentley" in its kind line, one flag at a time. The first line is the mark in capitals; a lease's terms and condition follow in their own case. Lease flags are Heritage White with black type; Sale Pending is Bentley Green, Sold Dark Grey, both with white type. On the car page the offer carries its own flag, <b>Lease special</b> (see Car page).</p>
    <div class="ds-cards">{flags}</div>
    <h3 class="ds-h3">On the home page rail</h3>
    <div class="ds-stage ds-cards">{wrap(CARD_HOME, homecard)}</div>
    <h3 class="ds-h3">In the listing — every kind in stock</h3>
    <div class="ds-cards">{cardgrid}</div>
  </section>

  <section class="ds-part" id="vdp">
    <h2 class="ds-h2">Car page</h2>
    <p class="ds-note">The head: name at the left with Save · Share · Email under it; the price plate at the right, level with the header's right edge — MSRP, the two charges, a rule, <b>Final price</b>, then Confirm availability. <b>The photographs carry no flag</b> — nothing covers the car; a lease is the offer's, under its own flag <b>Lease special</b> beside the photographs (Alex, 2026-10-26).</p>
    <div class="ds-stage">{wrap(VDP_ROOT, vdptop)}</div>
    <h3 class="ds-h3">Offer and lease special</h3>
    <div class="ds-row" style="align-items:flex-start">
      <div class="ds-stage" style="flex:1 1 360px">{wrap(VDP_SIDE, offer)}</div>
      <div class="ds-stage" style="flex:1 1 360px">{wrap(VDP_SIDE, special)}</div>
    </div>
    <h3 class="ds-h3">Pricing details</h3>
    <div class="ds-stage">{wrap(VDP_ROOT, pricing)}</div>
  </section>

  <section class="ds-part" id="header">
    <h2 class="ds-h2">Header &amp; footer</h2>
    <p class="ds-note">Two lines on a desktop. The first: the marque centred; at the left the demo site's eight routes — Home, New, Pre-Owned, Offers, Service, Parts, Finance, About — each but Home opening a panel of its pages in groups (hover, focus or a press; the group's name as a label, the pages in the body face, on the Satin Linen ground with a hairline); at the right the number, 561-926-9111, the site terms and Request Test Drive. Below 1536px the eight go behind Menu, where a press opens a group in place. The second line: the four routes the client wants always on screen — <b>Bentley Inventory</b> (prominent), Special Offers, Financing, Contact Us. On a phone the four become a bar at the foot of the screen, and the site's terms sit in the first screen.</p>
    <div class="ds-stage ds-stage--header">{header}</div>
    <div class="ds-frames" style="margin-top:var(--space-5)">{frame('top', 390, 844, 0.55)}</div>
    <h3 class="ds-h3">Recently Viewed</h3>
    <p class="ds-note">The demo site's widget, on every page (<code>js/page.js</code>, styles in <code>css/static.css</code>, class <code>.rv</code>). Every car page remembers its car in the visitor's browser (localStorage, key <code>bpb-recently-viewed</code>, the last eight, newest first). Once there is one, a tab sits at the lower right: the car icon, <b>Recently Viewed</b> in the button register (Teal 70%, uppercase, tracked) and the count in a light disc; on a phone, the icon and the count only, above the foot bar. A press opens the cars above it on a white plate with a hairline — each its first photograph from its page (4:3, 96px), its name and <b>Final price · Stock</b> in 14px — never the MSRP. The car opens in the same tab. Escape, the ×, or a press elsewhere closes it. The way back to the top stands above the tab. With a live feed, read the same fields from the vehicle record instead of the page.</p>
    <h3 class="ds-h3">Footer</h3>
    <div class="ds-stage ds-stage--header">{footer}</div>
  </section>

  <section class="ds-part" id="sections">
    <h2 class="ds-h2">Home chapters</h2>
    <p class="ds-note">One chapter, one screen. Each is shown live, at 1440px and at 390px.</p>
    {sections}
  </section>

  <section class="ds-part" id="inner">
    <h2 class="ds-h2">Inner pages</h2>
    <p class="ds-note">About, Contact, Finance, Parts, Sell Your Vehicle, the Payment Calculator and the model page template (<code>about.html</code>, <code>contact.html</code>, <code>finance.html</code>, <code>parts.html</code>, <code>sell.html</code>, <code>calculator.html</code>, <code>bentayga-speed.html</code>) are built from the site's own parts: the header and footer of the home page, the listing's head, the car page's enquiry form. <code>css/subpages.css</code> holds only what those parts lack and loads last. Every inner page added later follows the same head and the same writing.</p>
    <h3 class="ds-h3">The model page (template)</h3>
    <p class="ds-note">First for the 2027 Bentayga Speed (<code>bentayga-speed.html</code>); every model page follows it. <b>The way in is the home page's Model Range</b>: a model's tile opens its page where one is built, its cars in stock otherwise (Alex, 2026-10-26). The order is the AAN master model page's (<i>aanmaster2027 /models/vantage/</i>), drawn in this site's parts: <b>1 · Hero</b> — Bentley's studio photograph of the model full width under the bar, the car whole with air round it (its height follows the width: <code>max(62vh, 38vw)</code>, never past the frame's 16:9); the words <b>under</b> the photograph, never on the car: at the left the eyebrow <i>Braman Bentley Palm Beach</i>, the year line (<i>All-New 2027</i>, Lead) and the model's name in capitals (the capitals rule); at the right one line from Bentley's words, then <b>View [model] in stock</b> and <b>Enquire</b>. <b>2 · Key figures</b> — <b>the page's one dark band, Bentley Green</b>, straight under the hero: Bentley's four as its US page gives them (Max speed, Max torque, 0–60 mph, Max power — imperial), four across (two by two on a phone), the figure at H2 Light in white, its unit small beside it, its name as a label over it; any condition Bentley attaches (the top speed's carbon ceramic brakes) under them at the legal size. <b>3 · Engine</b> — the master's lead and statement as one chapter, never two centred blocks in a row: the label and the heading at 5 columns, Bentley's words at 7 — the first paragraph at Lead size in the ink, the second as body. <b>4 · Film</b> — the full width of the screen (16:9, at most 82% of the window's height): the film's own cover frame with one round play button at its centre and its name at the lower left; YouTube loads and plays only after the press — never a bare embedded player. <b>5 · Stories</b> — words at 5 columns, picture at 7 (3:2); <b>the picture's top edge on the title's capitals</b> — not lower, not higher (the heading's line box trimmed to its cap height; Alex, 2026-10-26); the next mirrored on the plate; at least one photograph outside the studio (a detail, the cabin) so the page is not one grey; one column under 1024px, the words first. <b>6 · Cars in stock</b> — the listing's own cards (three, a route to all; filled from the inventory, never typed; when the exact model is not in stock, the closest line stands and says so). <b>7 · Enquiry</b> — the form, its message naming the model. Further technical specifications are added only as Bentley publishes them for the US — never invented. Words are Bentley's, verbatim, each paragraph under the heading it belongs to. Photographs are Bentley Motors' own media of that model, from its model page on bentleymotors.com (the retailer is authorised to use them); no placeholder stays on a published page. This is the master's layout (the version asked for); an alternative in this site's own composition follows.</p>
    <h3 class="ds-h3">The model page — our version</h3>
    <p class="ds-note">Built for the Flying Spur, Torcal, Continental GT and Continental GT Convertible (<code>flying-spur.html</code>, <code>torcal.html</code>, <code>continental-gt.html</code>, <code>continental-gtc.html</code>); the Bentayga Speed stays in the master's layout. Each model's home-page tile opens its page. <b>The photographs are the brightest Bentley has for the model</b> — its signature colour where it has one (the Torcal in Bentley's lime Torcal S, not the silver studio frames; Alex, 2026-10-26). The words take the place in the frame where the car is not: lower left (Flying Spur, Continental GT), upper left over the sky with the calls on the road (Torcal), lower right (Convertible); a wide studio frame with the car at its centre keeps only the chapter's name and heading on the wall, its lead opening the details. A model with no new car in stock shows its pre-owned ones under a heading that says so, or registers interest (Torcal). <b>One idea: Bentley's words stand inside its photographs</b> — on the road beside the car, on the studio wall, on the dark road at sunset — never in a box beside them. <b>The page is in named chapters, as Bentley's own model pages are</b> (Alex, 2026-10-26): <b>The Range · Exterior · Interior · Performance · Personalisation · In Stock</b>, each opened by its name as the site's own label (<code>.label</code>) — nothing drawn before it, and a row of the chapters under the hero that takes the visitor to each (<code>.mx__index</code>; a row to swipe below 1024px). <b>Hero</b> — Bentley's road photograph owns the first screen under the bar, the car in the right two thirds; at the lower left, on the bar's own left edge, the eyebrow, <i>New</i>, the model's name in capitals over two lines, Bentley's line and three calls: <b>View [model] in stock</b>, <b>Enquire</b>, and <b>the film</b> — a round play button with its name; the hero's photograph is the film's first frame, a press plays Bentley's own film in its place (YouTube asked only then), a close button or Escape returns. From 1024px, unless the visitor asks for less motion, <b>Bentley's own stage loop</b> for the model (bentleymotors.com's model page, muted, without its opening blur and closing logo card) runs in the photograph's place, with a round pause button at the hero's upper right; it rests while the film plays; a phone never downloads it. Over the loop the words take the inner pages' two-way shade, measured over every second of it. <b>The Range</b> — Bentley's heading at 5 columns, its words at 7; the models as Bentley's own portraits (held at 4:5 round the car), name and Bentley's line under each. <b>Exterior</b> — a studio photograph full width, the chapter's heading in black on the lit wall; then Bentley's exterior points (name + sentence) beside a mosaic of the details they name, each detail captioned with its own point. <b>Interior</b> — two mirrored rows: a cabin photograph to the screen's left edge with Bentley's interior points, then the rear passengers' controls with a second photograph to the right edge. <b>Performance</b> — the page's one dark band, Bentley Green: Bentley's words and its US figures, five across, with Bentley's own conditions under them. <b>Personalisation</b> — a second road photograph, the words in its darkest region, and <b>Build your own</b>. Then the cars in stock and the enquiry. <b>A photograph beside words starts on the words' title</b> — the title's capitals on the photograph's top edge (the heading's line box trimmed to its cap height); a chapter's name stands above that line. <b>Words over a photograph are measured on the composited render</b> (WCAG AA: 4.5 for text, 3 for headings at 24px and over); where a region fails — the evening sky did — the words move to a region that passes, never a heavier scrim. Nothing on the hero may meet the Recently Viewed tab (between 1024 and 1279px the film keeps only its round button). Below 1024px every photograph stands above its words.</p>

    <h3 class="ds-h3">The page title</h3>
    <p class="ds-note">One head on every inner page: a Bentley photograph full width under the bar, the words at its lower left. Two lines, always these two. <b>Capitals are kept for the names of the models only</b> (MULLINER, TORCAL); page titles and the line over them are written in their own case.</p>
    <div class="ds-stage ds-stage--band">{wrap(SUB, subhead)}</div>
    <table class="ds-table" style="margin-top:var(--space-5)"><thead><tr><th>Line</th><th>Markup</th><th>Rule</th></tr></thead><tbody>
      <tr><td>Eyebrow</td><td><code>&lt;p class="label sub__label"&gt;Braman Bentley Palm Beach&lt;/p&gt;</code></td><td>Always exactly <b>Braman Bentley Palm Beach</b>, identical on every inner page: never the page's name, a department or a tagline. {val('text-xs')}, <b>in its own case — not capitals</b>, tracking 0.01em (as bentleymotors.com sets the small line over a title).</td></tr>
      <tr><td>Title</td><td><code>&lt;h1 class="h2 sub__title"&gt;Finance Department&lt;/h1&gt;</code></td><td>The page's name, the one <code>h1</code> on the page, in Title Case and <b>shown as written — not capitals</b> (<code>text-transform: none</code>), as bentleymotors.com sets its titles. Bentley Light (300), 32px on a phone to 50px on a desktop, leading 1.08, no tracking.</td></tr>
      <tr><td>Colour</td><td>—</td><td>White on the photograph (the eyebrow at 88%). Below 768px the words leave the photograph and stand under it in black, the eyebrow in Dark Grey 40%.</td></tr>
      <tr><td>Photograph</td><td><code>.sub__band-pic</code></td><td>Bentley library or retail photography only. The whole car in the frame, the words on the road, ground or sky beside it — never on the car.</td></tr>
    </tbody></table>

    <h3 class="ds-h3">Writing</h3>
    <table class="ds-table"><thead><tr><th>What</th><th>How it is written</th><th>Example</th></tr></thead><tbody>
      <tr><td>Section heading</td><td><code>h2.h2.h2--small</code>, Title Case, as the demo site writes them.</td><td>Opening Hours · Contact Information · Meet Our Staff · Send Us a Message</td></tr>
      <tr><td>Group heading</td><td><code>h3</code>, one or two words, Title Case.</td><td>Sales · Service · Parts · Our Location</td></tr>
      <tr><td>Label</td><td><code>.label</code>: typed in normal case, uppercase from the CSS. Job titles, days, price labels. A form field's label (<code>.field__label</code>) is the exception: in its own case, as on bentleymotors.com.</td><td>Director of Luxury Sales · Mon – Thu · (field) First name*</td></tr>
      <tr><td>Button</td><td>A verb first, typed in sentence case; the button style sets the capitals. Use the names the demo site already uses.</td><td>Get directions · Send to phone · Send message · Contact us · Apply for financing</td></tr>
      <tr><td>Telephone</td><td>Always with dashes, as the client asked. The <code>href</code> is <code>tel:+1…</code>. A person's direct line reads "Call …".</td><td>561-926-9111 · Call 561-681-4903</td></tr>
      <tr><td>Hours</td><td>Lower-case am/pm, an en dash between times, "Closed" for a closed day.</td><td>9:00 am – 8:00 pm · Closed</td></tr>
      <tr><td>Form fields</td><td>Two columns on every page (one on a phone): a label in the label register, a ruled line, the value in Body Light. A choice from a list (<code>select.field__input.field__select</code>) ends in the listing's thin open chevron — never a filled arrow. Photographs to send: the browser's picker, its button drawn as the outlined button. A long form is split into headed groups (<code>.sub__form-h</code>, Lead), each under a hairline. On a car page and the inner pages the client's fields: first/last name, email/phone, best time to contact across, message, consent.</td><td>Sell Your Vehicle: Vehicle Info, Contact Info</td></tr>
      <tr><td>Legal line</td><td>As bentleymotors.com sets its own legal text: <b>12px on 16px</b>, <code>--text-legal</code>, Regular, tracking 0.01em, Dark Grey 40%, in its own case — never larger, never in capitals; the one exception to the 14px floor. <b>Where:</b> the form's reCAPTCHA line (<code>.enquire__fine</code>), the footer's copyright (<code>.close__legal &gt; div</code>), the listing's disclaimer (<code>.srp__legal</code>), the car page's disclaimer and full lease terms (<code>.pricing__text</code>, <code>.pricing__fine</code>). <b>Not</b> what stands beside a price — a lease's term and money down, its rebate and credit line, the fees in a price (<code>.slide__stock</code>, <code>.card__flag-terms</code>, <code>.special__fine</code>, <code>.po-fees</code>): the price rules keep those clear, at their own size.</td><td>This site is protected by reCAPTCHA and the Google Privacy Policy and Terms of Service apply.</td></tr>
      <tr><td>Body copy</td><td>The dealer's own words, kept as they wrote them. No copy of our own, no placeholder text.</td><td>—</td></tr>
    </tbody></table>

    <h3 class="ds-h3">The staff card</h3>
    <p class="ds-note">The demo site's card (Meet Our Staff), kept as it is there: a white plate drawn by a hairline (<code>--rule</code>), the portrait 4:3 across its top, then the job title as a label, the name in Bentley Light (26.4px at most), the direct line as "Call …", and under it a note if there is one (a language spoken). Three across, 40px apart, every card in a row as tall as the tallest; two on a tablet, one on a phone.</p>
    <div class="ds-stage">{wrap(TEAM, member)}</div>
  </section>

  <section class="ds-part" id="rules">
    <h2 class="ds-h2">Rules</h2>
    <div class="ds-rules">
      <section><h3>Price (FTC 2026 · Florida § 501.976)</h3><ul>
        <li>The figure that stands out is the <b>Final price</b>: the sale price with the dealer's charges in it ($1,189 dealer service + $514 electronic filing). Only tax, tag, registration and title may be left out.</li>
        <li>MSRP and "+ Dealer service charge", "+ Electronic filing charge" sit beneath as the working.</li>
        <li>"You save" is measured against the Final price, never the pre-fee price.</li>
        <li>Every lease payment carries its term and the money down beside it, in Bentley's word: <b>down</b>.</li>
        <li>A lease that rests on a rebate says so beside the payment, with the credit it needs.</li>
        <li>Sold cars are not advertised: they leave the listing, its count, filters and the home rail. A pending deal reads <b>Sale Pending</b>.</li>
      </ul></section>
      <section><h3>Photographs</h3><ul>
        <li>The whole motor car is always in the frame: move the frame, never crop the car.</li>
        <li>Words never stand on the car — on the road, the ground, the sky, or a plate.</li>
        <li>Photographs only; no video (dead cell-service pockets make a film look broken).</li>
        <li>Cars have air around them; frames in a row are equal.</li>
      </ul></section>
      <section><h3>Forms (approved)</h3><ul>
        <li>The label stands on the field's line, where the value will go — Body Light, Dark Grey 40%, in its own case — and rises above the line at 14px once the field has focus or a value, as bentleymotors.com does it. Approved by the client's side (Alex, 2026-10-26: "a good move"). Every form on the site, every new one.</li>
        <li>Two columns; one on a phone. A 1px line in the ink, 2px with focus, no box round a field.</li>
        <li>A list ends in a firm short chevron in the ink; until something is chosen it shows only its label.</li>
        <li><b>The enquiry: address, form, hours</b> (Alex, 2026-10-26). The note <i>Fields marked with (*) are required.</i> is the form's first line, inside its plate, across both columns. Beside the form, the column holds the heading, Our Location, the department's phone, Get directions / Send to phone, and under them that department's hours (Parts Hours on Parts; Sales Hours on Finance and the model pages) in tighter record rows. From 1024px the column is as tall as the form: the heading's capitals on the plate's top edge, the hours' last rule on its bottom edge (<code>.enquire--fit</code>). Contact and About keep their three-department Opening Hours chapter; Sell keeps the client's order (form, then hours and location under it).</li>
        <li><b>Dropdowns: the closed field is the browser's own <code>&lt;select&gt;</code></b> on the field's ruled line — the listing's filters (Condition, Model, Year, Sort by) and every form. <b>The open list is the site's own, as the demo site draws it</b> (Alex, 2026-10-26; <code>js/page7.js</code>, <code>.dd</code> in <code>static7.css</code>): it drops from the field's line (8px under it), its left edge on the field's, at least the field's width; a white plate with a hairline (<code>--rule</code>), no shadow; one choice to a 40px row, 16px, 16px side padding; <b>model names in capitals</b>; on the listing's picks the number of cars each choice leaves (<i>/8</i>, Dark Grey, 14px, at the right — counted with the other picks as they stand); the chosen row marked by a 2px line at its left, the row under the pointer or the keys on Satin Linen; <b>its height is its choices</b> — never the demo's empty foot; past ~10 choices it scrolls with a thin bar. A form's empty first choice (Make, Year) is only a prompt and is not listed. The chevron turns up while open. Keys: arrows, Home/End, Enter or Space, Escape, Tab. On a touch screen the phone's own picker opens instead.</li>
        <li>Check box: a 24px square, a 2px edge in Teal 70%, a white tick on Teal when ticked. A choice: a 20px circle, a dot when chosen.</li>
      </ul></section>
      <section><h3>Motion &amp; access</h3><ul>
        <li>Static: no scroll-driven effects, no sticking chapters, no reveals, no autoplay. Slides turn when the visitor turns them.</li>
        <li>Transitions only on controls: colour on hover ({val('dur-2')}), the slide change ({val('dur-4')}).</li>
        <li>Contrast verified on every ground (WCAG AA); focus always visible; a skip link first.</li>
        <li>Body type never below 14px; the one exception is a legal line, 12px (<code>--text-legal</code>), as on bentleymotors.com.</li>
      </ul></section>
    </div>
  </section>
</div>
<script>
  /* live readings: contrast on the chips, px values at this width */
  (function () {{
    function rgb(s) {{ var m = s.match(/\\d+(\\.\\d+)?/g); return m ? m.slice(0, 3).map(Number) : [0, 0, 0]; }}
    function lum(c) {{ return c.map(function (v) {{ v /= 255; return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }}).reduce(function (a, v, i) {{ return a + v * [0.2126, 0.7152, 0.0722][i]; }}, 0); }}
    function cr(a, b) {{ var x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); }}
    document.querySelectorAll('.ds-swatch__chip').forEach(function (chip) {{
      var bg = rgb(getComputedStyle(chip).backgroundColor), k = cr(bg, [4, 4, 4]), w = cr(bg, [255, 255, 255]);
      var s = chip.querySelector('.ds-cr');
      s.textContent = 'Black ' + k.toFixed(1) + ' · White ' + w.toFixed(1);
      s.style.color = k >= w ? '#040404' : '#fff';
    }});
    function px() {{
      document.querySelectorAll('.ds-type').forEach(function (row) {{
        var v = getComputedStyle(row.querySelector('.ds-type__sample')).fontSize;
        row.querySelector('.ds-px').textContent = 'now ' + Math.round(parseFloat(v)) + 'px';
      }});
      document.querySelectorAll('.ds-px-w').forEach(function (el) {{
        el.textContent = Math.round(el.previousElementSibling.getBoundingClientRect().width) + 'px';
      }});
    }}
    px(); addEventListener('resize', px);
  }})();
</script>
</body>
</html>
'''
open(OUT + 'design-system.html', 'w', encoding='utf-8', newline='\n').write(page)
print('design-system.html:', len(cards), 'listing cards,', len(SECTIONS), 'chapters')
