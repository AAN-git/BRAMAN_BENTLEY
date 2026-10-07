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

# --- the flags on a card's photograph: one real card of each kind --------------
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
    ('sm', 'Small', 'Card facts, offers, legal lines, hero buttons.', 'Stock V66142T · 30 miles'),
    ('xs', 'Label', 'Labels, field labels, price labels, counts (uppercase, tracked).', 'FINAL PRICE'),
    ('button', 'Button', 'Every button (uppercase, tracked).', 'CONFIRM AVAILABILITY'),
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
  <div class="ds-type__sample" style="font-size:var(--text-{t});{'text-transform:uppercase;letter-spacing:var(--track-label);' if t in ('xs','button') else ''}{'line-height:var(--leading-display);letter-spacing:var(--track-display);font-weight:300;' if t in ('hero','display','h2') else ''}">{s}</div>
</div>''' for t, n, u, s in TYPE)

spaces = '\n'.join(f'<div class="ds-space"><code>--{s}</code><span class="ds-space__bar" style="width:var(--{s})"></span><span class="ds-px-w" data-var="--{s}"></span></div>' for s in SPACE)

flags = '\n'.join(f'<div class="ds-item"><p class="ds-cap">{H.escape(n)} · <code>.{k}</code></p><p class="ds-note" style="font-size:var(--text-sm)">{H.escape(u)}</p>{wrap(CARD_SRP if w == "srp" else CARD_HOME, cc)}</div>' for n, k, u, cc, w in FLAGS)
cardgrid = '\n'.join(f'<div class="ds-item"><p class="ds-cap">{H.escape(n)}</p>{wrap(CARD_SRP, c)}</div>' for n, c in cards)

sections = '\n'.join(f'''<article class="ds-section" id="ds-{a}">
  <h3 class="ds-h3">{n}</h3><p class="ds-note">{u}</p>
  <div class="ds-frames">{frame(a, 1440, 900, 0.5)}{frame(a, 390, 844, 0.55)}</div>
  <p class="ds-cap"><a href="index.html#{a}">Open in the page →</a></p>
</article>''' for a, n, u in SECTIONS)

TOC = [('colour', 'Colour'), ('type', 'Type'), ('space', 'Space & layout'), ('buttons', 'Buttons'),
       ('links', 'Links & labels'), ('forms', 'Forms'), ('cards', 'Vehicle cards'), ('vdp', 'Car page'),
       ('header', 'Header'), ('sections', 'Home chapters'), ('rules', 'Rules')]
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
    <p>The page is static by the client's brief (2026-10-04, an older clientele): no scroll effects, no autoplay, no video. Photographs are the design.</p>
  </header>
  <nav class="ds-toc" aria-label="Design system">{toc}</nav>

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
    {types}
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
    <p class="ds-note">The enquiry on a car page: labels above, hairline fields, one call. Error and success colours are for form states only.</p>
    <div class="ds-stage ds-stage--white">{wrap(VDP_ROOT, enquire)}</div>
  </section>

  <section class="ds-part" id="cards">
    <h2 class="ds-h2">Vehicle cards</h2>
    <p class="ds-note">One card everywhere: photograph, name, facts, and the price plate — <b>Final price</b> leads; MSRP and the two dealer charges sit beneath as the working. A lease offer carries its term and the money down (Bentley's word: "down").</p>
    <h3 class="ds-h3">Flags on the photograph</h3>
    <p class="ds-note">One flag at a time, at the photograph's top left. Lease flags are Heritage White with black type; Sale Pending is Bentley Green, Sold Dark Grey, both with white type. On the car page the offer carries its own flag, <b>Lease special</b> (see Car page).</p>
    <div class="ds-cards">{flags}</div>
    <h3 class="ds-h3">On the home page rail</h3>
    <div class="ds-stage ds-cards">{wrap(CARD_HOME, homecard)}</div>
    <h3 class="ds-h3">In the listing — every kind in stock</h3>
    <div class="ds-cards">{cardgrid}</div>
  </section>

  <section class="ds-part" id="vdp">
    <h2 class="ds-h2">Car page</h2>
    <p class="ds-note">The head: name at the left with Save · Share · Email under it; the price plate at the right, level with the header's right edge — MSRP, the two charges, a rule, <b>Final price</b>, then Confirm availability.</p>
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
    <p class="ds-note">Two lines on a desktop: the marque centred with the retailer's routes either side, then the four routes the client wants always on screen — <b>Bentley Inventory</b> (prominent), Special Offers, Financing, Contact Us. On a phone the four become a bar at the foot of the screen, and the site's terms sit in the first screen.</p>
    <div class="ds-stage ds-stage--header">{header}</div>
    <div class="ds-frames" style="margin-top:var(--space-5)">{frame('top', 390, 844, 0.55)}</div>
    <h3 class="ds-h3">Footer</h3>
    <div class="ds-stage ds-stage--header">{footer}</div>
  </section>

  <section class="ds-part" id="sections">
    <h2 class="ds-h2">Home chapters</h2>
    <p class="ds-note">One chapter, one screen. Each is shown live, at 1440px and at 390px.</p>
    {sections}
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
      <section><h3>Motion &amp; access</h3><ul>
        <li>Static: no scroll-driven effects, no sticking chapters, no reveals, no autoplay. Slides turn when the visitor turns them.</li>
        <li>Transitions only on controls: colour on hover ({val('dur-2')}), the slide change ({val('dur-4')}).</li>
        <li>Contrast verified on every ground (WCAG AA); focus always visible; a skip link first.</li>
        <li>Body type never below 14px.</li>
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
