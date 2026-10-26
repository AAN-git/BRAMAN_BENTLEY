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
flag_sold = ('<li class="card ds-flagonly"><span class="card__link">'
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

# every card in the listing grid's own wrapper, so its subgrid keeps the
# specimens in a row level and equally tall, as the listing does
flags = '\n'.join(f'<div class="ds-item"><div class="ds-item__head"><p class="ds-cap">{H.escape(n)} · <code>.{k}</code></p><p class="ds-note" style="font-size:var(--text-sm)">{H.escape(u)}</p></div>{wrap(CARD_SRP, cc)}</div>' for n, k, u, cc, w in FLAGS)
cardgrid = '\n'.join(f'<div class="ds-item"><div class="ds-item__head"><p class="ds-cap">{H.escape(n)}</p></div>{wrap(CARD_SRP, c)}</div>' for n, c in cards)

sections = '\n'.join(f'''<article class="ds-section" id="ds-{a}">
  <h3 class="ds-h3">{n}</h3><p class="ds-note">{u}</p>
  <div class="ds-frames">{frame(a, 1440, 900, 0.5)}{frame(a, 390, 844, 0.55)}</div>
  <p class="ds-cap"><a href="index.html#{a}">Open in the page →</a></p>
</article>''' for a, n, u in SECTIONS)

# --- the page blocks: a real example cut from the page at 1440px (assets/ds/,
# taken by hand from the live pages) and what it is built of, measured there --
def block(name, img, size, rows, note='', ref='', phone=False):
    w, h = size
    trs = ''.join(f'<tr><th scope="row">{k}</th><td>{v}</td></tr>' for k, v in rows)
    return (f'<article class="ds-block"><h3 class="ds-h3">{name}</h3>'
            + (f'<p class="ds-note">{note}</p>' if note else '')
            + f'<figure class="ds-ex{" ds-ex--phone" if phone else ""}"><img src="assets/ds/{img}.webp" alt="{H.escape(name)}, as built" width="{w}" height="{h}" loading="lazy">'
            + (f'<figcaption>{ref}{"" if phone else " at 1440px"}</figcaption>' if ref else '') + '</figure>'
            + f'<table class="ds-table ds-spec"><tbody>{trs}</tbody></table></article>')

MENU = block('Header and menu', 'ex-menu', (1400, 437), [
    ('Bar', '80px (<code>--bar-h</code>), 72px on a phone; the four routes\' line under it 56px. Satin Linen; a hairline under each line; frosted (<code>--bar-ground</code>, 95%) once the page scrolls.'),
    ('Left', 'The demo\'s eight routes — Home, New, Pre-Owned, Offers, Service, Parts, Finance, About. 14px Regular, uppercase, tracking 0.1em, Dark Grey 40%; the ink on hover. Inline from 1536px; behind <b>Menu</b> below.'),
    ('Centre', 'The Bentley marque.'),
    ('Right', '561-926-9111 (14px, tracked), <b>Site Terms &amp; Conditions</b> under it (14px, own case, underlined), <b>Request Test Drive</b> (<code>.btn--line</code>).'),
    ('Second line', '<b>Bentley Inventory</b> (the filled button) · Special Offers · Financing · Contact Us, in the button register. On a phone: a 64px bar fixed at the foot of the screen.'),
    ('Panel', '<b>Its top on the bar\'s lower line (80px) — no gap, no overlap</b>; its left edge 24px left of its route. Satin Linen, a 1px hairline (<code>--rule</code>), no shadow. Padding 24 / 24 / 16px. Groups side by side, 48px apart: the group\'s name as a label (14px, uppercase, Dark Grey), its pages under it at 16px Regular in the ink, 6px above and below each. Opens on hover, focus or a press; fades in 0.25s.'),
    ('Phone', 'Menu opens the groups in place, one under another; pages at 18px.'),
], ref='Parts Department, the Pre-Owned panel open')

SUB_HEAD = block('Page head — the photograph', 'ex-sub-head', (1200, 433), [
    ('Photograph', 'The full width of the screen, straight under the header. <b>Height <code>clamp(320px, 42vh, 460px)</code></b> — 378px at 1440×900, 454px at 1920×1080: a band, under half the screen, not a hero. <code>object-fit: cover</code>; <code>object-position</code> set for each photograph (Parts 50% 42%).'),
    ('Words', 'At the lower left, on the page column\'s left edge; <code>clamp(32px, 4vw, 56px)</code> above the photograph\'s bottom.'),
    ('Eyebrow', '<i>Braman Bentley Palm Beach</i> — always exactly this. 14px Regular, own case, tracking 0.01em, white 88%.'),
    ('Title', 'The page\'s name in Title Case. 50px on a desktop, 32px on a phone; Light 300; leading 1.08; white.'),
    ('Shade', 'Only under the words: <code>linear-gradient(90deg, rgba(4,4,4,.62) 0, rgba(4,4,4,.32) 38%, transparent 62%)</code> + <code>linear-gradient(0deg, rgba(4,4,4,.38) 0, transparent 55%)</code>.'),
    ('Phone', 'Below 768px the photograph is a 16:9 band (211px at 375px) and the words stand <b>under</b> it, in black on Satin Linen, the eyebrow in Dark Grey 40% (example under the tiles).'),
], ref='Parts Department')

SUB_TILES = block('Tiles — the page\'s calls', 'ex-sub-tiles', (1200, 512), [
    ('Grid', '<code>2fr 1fr 1fr 1fr</code>, gap 24px — 499 / 250 / 250 / 250px at 1440. 96px above.'),
    ('Picture', '378px tall, <code>object-fit: cover</code>. <b>Each picture shows what its route is for</b> — Bentley\'s own photographs.'),
    ('Name', '24px Regular (Lead), the ink, under the picture on a hairline.'),
    ('Call', 'The first, twice the width, carries the one filled button; the others are the whole tile as a link.'),
    ('Phone', 'One column, 32px apart; the first picture 16:9, the others 4:3; the button the column\'s width.'),
], ref='Parts Department')

SUB_DEPT = block('Department chapter', 'ex-sub-dept', (1200, 494), [
    ('Grid', '<code>2fr 1fr</code> — 820 / 413px, gap 86px. 96px above.'),
    ('Heading', '30px Light (H3), Title Case: <i>Our Parts Department</i>.'),
    ('Copy', 'The dealer\'s words, then Bentley\'s where it has them (<i>Genuine parts</i>, a 30px Light subheading). 18px Regular, Dark Grey 40%, leading 1.5.'),
    ('Right', 'The department manager\'s staff card, 413px wide (the card is shown live below).'),
], ref='Parts Department')

SUB_ENQ = block('Enquiry — address, form, hours', 'ex-sub-enquire', (1200, 766), [
    ('Grid', '<code>5fr 7fr</code> — 514 / 720px, gap 86px. 96px above and below.'),
    ('Left column', 'Heading 30px Light. A hairline, then <b>Our Location</b> 24px Regular; the address 18px Dark Grey; the department\'s phone as a record row (label 14px uppercase, number 18px); <b>Get directions</b> and <b>Send to phone</b> side by side (<code>.btn--line</code>). At the foot the department\'s hours (24px heading, rows 14px label / 18px value on hairlines). <b>This block is the same on every page.</b>'),
    ('Fit', 'From 1024px the column is as tall as the form: the heading\'s capitals on the plate\'s top edge, the last hours line on its bottom edge (<code>.enquire--fit</code>).'),
    ('Plate', 'White, a 1px hairline, padding 46px. <i>Fields marked with (*) are required.</i> first, 16px Dark Grey, across both columns. Fields in two columns, gap 24px; each 46px tall.'),
    ('Fields', 'The label on the line, 18px Light Dark Grey, rising to 14px on focus or a value; 1px ink line, 2px on focus. Radio 20px circle, check box 24px square, Teal 70% edge. <b>Send message</b> (<code>.btn</code>); the reCAPTCHA line 12px.'),
    ('Phone', 'One column: the location and hours first, then the plate (padding 24px).'),
], ref='Parts Department')

SUB_MAP = ('<article class="ds-block"><h3 class="ds-h3">Map</h3><table class="ds-table ds-spec"><tbody>'
    '<tr><th scope="row">Place</th><td>Straight under the enquiry; the page column\'s full width (1318 × 564px at 1440); 96px under it.</td></tr>'
    '<tr><th scope="row">Tone</th><td>Google\'s map, toned to the page: <code>filter: grayscale(1) brightness(1.02) contrast(1.05)</code>, Heritage White ground. No frame, no shadow.</td></tr>'
    '</tbody></table></article>')

SUB_REV = block('Reviews — below the map', 'ex-sub-reviews', (1200, 626), [
    ('Head', '<i>Reviews</i> 30px Light, with <i>4.4 on Google</i> 16px Dark Grey at the right.'),
    ('Plates', 'White, 424 × 344px, padding 37px, side by side in a row turned by the rail arrows. The review 18px; the reviewer as a label (14px uppercase).'),
    ('Words', 'Google reviews of the dealer, verbatim; a long one cut at a sentence and marked …'),
    ('Foot', '<b>Read all reviews on Google</b> (<code>.btn--line</code>). 96px above, 128px below.'),
], ref='Parts Department')

SUB_PHONE = ('<div class="ds-phones">'
    + block('Inner page on a phone', 'ex-sub-phone', (750, 1784), [
        ('Head', 'The photograph a 16:9 band under the 72px bar; the eyebrow (Dark Grey 40%) and the title (32px, the ink) under it, 24px from the edge.'),
        ('Tiles', 'One column, 32px apart; the button the column\'s width.'),
    ], ref='Parts Department, 390px', phone=True)
    + block('Enquiry on a phone', 'ex-sub-enquire-phone', (750, 3646), [
        ('Order', 'The heading, the location and the hours first; then the form plate, padding 24px, one column of fields.'),
    ], ref='Parts Department, 390px', phone=True)
    + '</div>')

SUB_FORMPAGE = block('Form page — words, form, then the details', 'ex-sub-form', (1200, 924), [
    ('Order', 'For a page that is mainly a form (Ask a Tech, Sell Your Vehicle): the dealer\'s words first (18px, Dark Grey), then the form plate across the column, then the location and hours under it.'),
    ('Plate', 'As the enquiry\'s: white, hairline, padding 46px, two columns of fields; longer forms in headed groups (Lead, a hairline above each).'),
], ref='Ask a Tech')

SUB_THREE = block('Under the form — three columns', 'ex-sub-three', (1200, 320), [
    ('Grid', '<code>1fr 1fr 1.25fr</code>, gap 58px from 1280px; two columns from 768px; one on a phone.'),
    ('Columns', 'The location block (the same as everywhere) · Service Hours · Parts Hours. Headings 24px Regular; rows 14px label / 18px value on hairlines; the two buttons stay on one line from 1024px.'),
], ref='Ask a Tech')

SUB_PROMO = block('Offer plate', 'ex-sub-promo', (1200, 446), [
    ('Use', 'A dealer offer the demo carries (Ask a Tech: Sunbit payment plans), kept and redrawn in the site\'s parts — no other brand\'s colours or artwork.'),
    ('Grid', '<code>7fr 5fr</code> — the photograph 769 × 432px (<code>object-position 50% 60%</code>), the words 549px.'),
    ('Words', 'On Bentley Green, padding 46px. Heading 30px Light white; the offer\'s own line 18px, white 84%; its one call as a light button.'),
], ref='Ask a Tech')

MX_BLOCKS = ''.join([
    block('Hero', 'ex-mx-hero', (1200, 817), [
        ('Photograph', 'Bentley\'s road photograph, the full width under the header. Height <code>clamp(560px, 100svh − header, 62vw)</code> — 764px at 1440×900. The car in the right two thirds (<code>object-position 50% 62%</code>).'),
        ('Loop', 'From 1024px, unless the visitor asks for less motion: Bentley\'s own stage film, muted, in the photograph\'s place; a 42px round pause button 24px from the top right. A phone never loads it.'),
        ('Words', 'Lower left, on the bar\'s own left edge; <code>clamp(40px, 6vh, 72px)</code> from the bottom. Eyebrow 14px; <i>New</i> 24px; the model\'s name in <b>capitals</b>, Light, <code>clamp(44px, 4vw + 8px, 96px)</code>, two lines (FLYING / SPUR); Bentley\'s line 24px, at most 20rem.'),
        ('Calls', '<b>View [model] in stock</b> (<code>.btn</code>) · <b>Enquire</b> (<code>.btn--line</code>) · the film: a 42px round play button with <i>Film</i> (label) and its name. The film plays in the hero; × or Escape returns.'),
        ('Shade', 'Over the photograph: <code>radial-gradient(ellipse 55% 80% at 0 100%, rgba(4,4,4,.76) 0, rgba(4,4,4,.44) 48%, transparent)</code>. Over the loop: <code>linear-gradient(90deg, .8 → .55 at 40% → 0 at 65%)</code> + <code>linear-gradient(0deg, .6 → 0 at 60%)</code>.'),
        ('Chapter bar', 'Under the hero, 70px: The Range · Exterior · Interior · Performance · Personalisation · In Stock — 14px uppercase, tracked, Dark Grey, centred, gap <code>clamp(24px, 3.5vw, 56px)</code>; a hairline under it; hover the ink and a 1px line. Below 1024px a row to swipe.'),
        ('Phone', 'Below 1024px the photograph is 3:2 and the words stand under it; below 768px 1:1, the name <code>clamp(40px, 11vw, 52px)</code>, the buttons the column\'s width.'),
    ], ref='Flying Spur'),
    block('Chapter opening — label, heading, words', 'ex-mx-statement', (1200, 614), [
        ('Grid', '<code>5fr 7fr</code> — 526 / 736px, gap 58px. 128px above and below.'),
        ('Left', 'The chapter\'s name as the site\'s label (14px, uppercase, tracked, Dark Grey) — nothing drawn before it — and Bentley\'s heading, 50px Light, Title Case.'),
        ('Right', 'Bentley\'s words: the first paragraph 24px (Lead) in the ink, the rest 18px Dark Grey.'),
    ], ref='Flying Spur, The Range'),
    block('The range — the models', 'ex-mx-range', (1200, 435), [
        ('Grid', 'Five across, gap 16px; 128px below.'),
        ('Portrait', 'Bentley\'s portrait of each model at 4:5 (251 × 314px), <code>object-position 50% 54%</code>.'),
        ('Words', 'The model\'s name 24px, Bentley\'s line under it 18px Dark Grey. On a phone a row to swipe, a model and a half wide.'),
    ], ref='Flying Spur'),
    block('Scene — words inside the photograph', 'ex-mx-wall', (1200, 667), [
        ('Photograph', 'The screen\'s full width, 792px (a studio wall) to 900px (a road). The words where the car is not: on the lit wall in the ink, on a dark road or sky in white.'),
        ('Words', 'Label + 50px Light heading + Bentley\'s line; on a dark region the label white 86%, the copy white 92%.'),
    ], ref='Flying Spur, Exterior'),
    block('Details — points and mosaic', 'ex-mx-details', (1200, 724), [
        ('Grid', 'Three columns, 413px, gap 40 / 24px. 96px above, 128px below.'),
        ('Points', 'Bentley\'s points: the name 18px Regular in the ink, its sentence 18px Dark Grey.'),
        ('Mosaic', 'One tall photograph (413 × 527) and two short (413 × 233) of the details the points name, each captioned with its own point.'),
    ], ref='Flying Spur, Exterior'),
    block('Interior — mirrored rows', 'ex-mx-cabin', (1200, 1108), [
        ('Ground', 'White, 128px above and below.'),
        ('Rows', 'Two rows, mirrored: <code>767px | 548px</code>, gap 58px. The photograph (767 × 479) runs to the screen\'s edge; the words beside it.'),
        ('Photo to title', '<b>A photograph beside words starts on the title\'s capitals</b> — its top edge on the cap height of the heading, not lower, not higher.'),
    ], ref='Flying Spur, Interior'),
    block('Performance — the green band', 'ex-mx-power', (1200, 814), [
        ('Ground', 'Bentley Green, the page\'s one dark band. 128px above, 64px below.'),
        ('Words', '<code>5fr 7fr</code>, as a chapter opening, in white (label 84%).'),
        ('Figures', 'Bentley\'s US figures, five across on hairlines: the figure in Light at H2 size, its unit small beside it, its name as a label. Bentley\'s own conditions under them at the legal size.'),
    ], ref='Flying Spur, Performance'),
    block('Personalisation — the closing scene', 'ex-mx-sky', (1200, 758), [
        ('Photograph', 'A second road photograph, the full screen (900px), <code>object-position 50% 94%</code>.'),
        ('Words', 'In its darkest region, lower left: label, heading, Bentley\'s line, <b>Build your own</b> (<code>.btn</code>).'),
    ], ref='Flying Spur, Personalisation'),
    block('In stock', 'ex-mx-stock', (1200, 910), [
        ('Head', '<i>[Model] in Stock</i> 30px Light; <i>View all</i> as a text route at the right.'),
        ('Cards', 'The listing\'s own cards, three across, gap 32px — filled from the inventory, never typed. 96px above. Then the enquiry, as on the inner pages.'),
    ], ref='Flying Spur'),
])

TOC = [('principles', 'Principles'), ('colour', 'Colour'), ('type', 'Type'), ('space', 'Space & layout'),
       ('buttons', 'Buttons'), ('forms', 'Forms'), ('cards', 'Vehicle cards'), ('header', 'Header & menu'),
       ('photo', 'Text on photographs'), ('sections', 'Home'), ('inner', 'Inner pages'), ('model', 'Model pages'),
       ('vdp', 'Listing & car page'), ('writing', 'Writing'), ('price', 'Price')]
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
  /* cards in a row stand level and equally tall, as in the listing: caption,
     photograph, mark and words are each one row shared across the row (subgrid) */
  @supports (grid-template-rows: subgrid) {{
    .ds-cards:not(.ds-stage) {{ align-items: stretch; }}
    .ds-cards:not(.ds-stage) > .ds-item {{ display: grid; grid-row: span 10; grid-template-rows: subgrid; row-gap: 0; }}
    .ds-cards:not(.ds-stage) > .ds-item main, .ds-cards:not(.ds-stage) > .ds-item section,
    .ds-cards:not(.ds-stage) > .ds-item .page, .ds-cards:not(.ds-stage) > .ds-item .grid {{ display: contents; }}
    /* the Sold flag is shown alone, photograph and band, with no words to line up */
    .ds-cards .grid > li.card.ds-flagonly {{ display: block; align-self: start; }}
    .ds-cards .grid > li.card.ds-flagonly > .card__link {{ display: block; }}
    .ds-cards .grid > li.card.ds-flagonly .card__media {{ display: flex; }}
  }}
  .ds-cards .card {{ width: 100%; max-width: 420px; flex: none; margin: 0; transform: none; }}
  .ds-cards main, .ds-cards section, .ds-cards .page, .ds-cards .stock__in, .ds-cards .stock__frame,
  .ds-stage main, .ds-stage section, .ds-stage .page {{ min-height: 0; height: auto; padding: 0; margin: 0; width: auto; max-width: none; position: static; }}
  .ds-stage .mh {{ position: relative !important; top: auto; transform: none; }}
  .ds-stage--header {{ padding: 0; }}
  /* the phone's bottom bar shown in the sample, not fixed over this page */
  .ds-stage--header .mh__deck {{ position: static; }}
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
  .ds-rules--two {{ margin-top: var(--space-6); grid-template-columns: repeat(auto-fit, minmax(min(100%, 420px), 1fr)); }}
  .ds-rules ul {{ margin: 0; padding-left: 1.1em; }}
  .ds-principles {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 380px), 1fr)); gap: var(--space-5) var(--space-7); margin: 0; padding-left: 1.4em; }}
  .ds-principles li, .ds-list li, .ds-steps li {{ font-size: var(--text-body); line-height: var(--leading-body); }}
  .ds-list {{ max-width: 52rem; margin: 0 0 var(--space-5); padding-left: 1.1em; }}
  .ds-list li {{ margin: 0 0 var(--space-2); }}
  /* a block: its example, then what it is built of */
  .ds-block {{ margin-top: var(--space-8); }}
  .ds-block .ds-h3 {{ margin-top: 0; }}
  .ds-ex {{ margin: 0 0 var(--space-4); }}
  .ds-ex img {{ display: block; width: 100%; height: auto; border: 1px solid var(--rule); }}
  .ds-ex--phone {{ max-width: 375px; }}
  .ds-phones {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 375px), 1fr)); gap: var(--space-7); align-items: start; }}
  .ds-ex figcaption, .ds-map figcaption {{ margin-top: var(--space-2); font-size: var(--text-xs); color: var(--ink-secondary); }}
  .ds-spec th {{ width: 9.5rem; font-size: var(--text-sm); letter-spacing: 0; text-transform: none; color: var(--ink-secondary); }}
  .ds-tpl {{ display: grid; grid-template-columns: minmax(0, 260px) minmax(0, 1fr); gap: var(--space-7); align-items: start; margin-top: var(--space-6); }}
  .ds-tpl > div > .ds-block:first-child {{ margin-top: 0; }}
  .ds-map {{ margin: 0; }}
  .ds-map img {{ display: block; width: 100%; height: auto; border: 1px solid var(--rule); }}
  .ds-stage .close {{ min-height: 0; }}
  @media (max-width: 1023px) {{
    .ds-tpl {{ grid-template-columns: 1fr; }}
    .ds-tpl .ds-map {{ max-width: 260px; }}
  }}
  /* states shown at rest */
  .ds-hover.btn {{ background: var(--teal-hover); border-color: var(--teal-hover); }}
  .ds-hover.btn--line {{ background: rgba(4, 4, 4, 0.05); border-color: var(--ink); }}
  .ds-stage--dark .ds-hover.btn--line, .ds-stage--photo .ds-hover.btn--line {{ background: rgba(255,255,255,0.06); border-color: var(--white); }}
  .ds-focus {{ outline: 2px solid var(--ink); outline-offset: 3px; }}
  @media (max-width: 767px) {{
    .ds-toc {{ flex-wrap: nowrap; overflow-x: auto; white-space: nowrap; }}
    .ds-type {{ grid-template-columns: 1fr; gap: var(--space-2); }}
    .ds-space {{ grid-template-columns: 1fr auto; }}
    .ds-space__bar {{ grid-column: 1 / -1; grid-row: 2; }}
    /* wide tables and the desktop previews scroll in their own box, not the page */
    .ds-table {{ display: block; overflow-x: auto; }}
    .ds-frames {{ flex-wrap: nowrap; overflow-x: auto; }}
    .ds-frame {{ flex: none; }}
  }}
</style>
</head>
<body>
<div class="ds">
  <header class="ds-top">
    <p class="ds-cap">Braman Bentley Palm Beach · Direction 7</p>
    <h1>Design System</h1>
    <p>The rules, sizes, type, colour and blocks of the site — everything needed to redesign a page in its language. Live parts are the real components on the site's own stylesheets; examples are cut from the approved pages at 1440px, every size measured there. Values are read from <code>css/tokens.css</code>; the ground is Satin Linen 40%, the client's chosen look.</p>
  </header>
  <nav class="ds-toc" aria-label="Design system">{toc}</nav>

  <section class="ds-part" id="principles">
    <h2 class="ds-h2">Principles</h2>
    <p class="ds-note">Agreed with the client and Bentley's guidelines, in force on every page. When something cannot follow them, ask before inventing.</p>
    <ol class="ds-principles">
      <li><b>Strictly Bentley style.</b> Every element comes from Bentley's Retailer Website Guidelines, bentleymotors.com's own patterns or the approved pages here. No rule, mark, ornament or device of our own.</li>
      <li><b>A static page.</b> The clientele is older, on desktop and phone: no scroll effects, no reveals, no sticking chapters, no autoplaying slider. Slides turn when the visitor turns them. The one exception is a model page's hero loop (see Model pages).</li>
      <li><b>Photographs are the design.</b> Bentley Motors' own (the retailer is authorised) or the retailer's. The whole car in the frame, with air round it. Words never on the car — on the road, the ground, the sky or a plate.</li>
      <li><b>Words over a photograph are measured</b> on the composited render (WCAG AA: 4.5, or 3 for headings from 24px). Where a region fails, the words move — never a heavier shade.</li>
      <li><b>The dealer's words or Bentley's, verbatim.</b> No copy of our own, no invented figures or specifications, no placeholder on a published page.</li>
      <li><b>Titles in their own case.</b> Page titles and headings in Title Case, as bentleymotors.com writes them. Capitals belong to model names only (TORCAL, MULLINER). Labels, buttons and routes are uppercase through the CSS, never typed.</li>
      <li><b>Each page keeps its template.</b> Inner pages stay on the inner-page template; the model-page language is for model pages only. A weak page is fixed with better pictures and words inside its template, not a new layout.</li>
      <li><b>The client's four routes are always on screen:</b> Bentley Inventory (prominent), Special Offers, Financing, Contact Us — the header's second line on a desktop, a bar at the foot of a phone's screen.</li>
      <li><b>One form, one card, one price.</b> The same form wherever a form is; the same vehicle card everywhere; the Final price leads (FTC).</li>
      <li><b>Cards in a row are one height, every line level.</b> Wherever cards stand side by side, each card is as tall as the tallest and its lines meet the same lines in the cards beside it (see Vehicle cards).</li>
    </ol>
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
      <tr><td><code>--day-plate</code> / <code>--plate</code></td><td>White / White 94%</td><td>Plates on the ground: price plate, cards, form plate, Sell plate.</td></tr>
      <tr><td><code>--ink</code></td><td>Black; White on photographs</td><td>Type.</td></tr>
      <tr><td><code>--ink-secondary</code></td><td>Dark Grey 40%</td><td>Secondary type; form labels at rest; legal lines.</td></tr>
      <tr><td><code>--rule</code></td><td>Black 16%</td><td>Hairlines on the Satin Linen ground.</td></tr>
      <tr><td><code>--bar-ground</code> / <code>--glass</code></td><td>Satin Linen 95% / 86%</td><td>The header once scrolled; frosted plates.</td></tr>
      <tr><td><code>--ground-deep</code></td><td>Bentley Green</td><td>Deep chapters; a model page's one figures band.</td></tr>
    </tbody></table>
  </section>

  <section class="ds-part" id="type">
    <h2 class="ds-h2">Type</h2>
    <p class="ds-note">One family: the licensed Bentley face, Light (300) and Regular (400), with Arial as the required fallback (<code>--font</code>). Sizes are fluid — each shows its value at this window's width. Leading: display {val('leading-display')}, headings {val('leading-heading')}, body {val('leading-body')}. Tracking: display {val('track-display')}, labels {val('track-label')}, body {val('track-body')}.</p>
    {types}
    <h3 class="ds-h3">Every size — where it is used, and where it belongs</h3>
    <p class="ds-note">Measured on every page at 390px and 1440px. Use the role, not a number: a new element takes the role whose "belongs to" fits it. Nothing sits between the steps.</p>
    <table class="ds-table"><thead><tr><th>Role · token</th><th>Phone → desktop</th><th>Weight · case</th><th>Used now</th><th>Belongs to</th></tr></thead><tbody>
      <tr><td><b>Legal</b><br><code>--text-legal</code></td><td>12 / 16px leading</td><td>Regular · own case</td><td>reCAPTCHA line under every form; footer copyright; the listing's price disclaimer; the car page's disclaimer and full lease terms</td><td>Legal text that stands apart, as bentleymotors.com sets it. Never what stands beside a price.</td></tr>
      <tr><td><b>Label</b><br><code>--text-xs</code></td><td>14 · 14</td><td>Regular · UPPERCASE, 0.1em</td><td>Header routes, menu group names, the phone's foot bar; text routes; job titles, price labels, filter labels; card marks; a model chapter's name</td><td>Functional labels — never running text, never a heading.</td></tr>
      <tr><td><b>Label, own case</b><br><code>--text-xs</code></td><td>14 · 14</td><td>Regular · own case</td><td>Form field labels (risen); the inner-page eyebrow; "Site Terms &amp; Conditions" in the bar; slide counts (01 / 03)</td><td>Small functional text read as words.</td></tr>
      <tr><td><b>Small</b><br><code>--text-sm</code></td><td>16 · 16</td><td>Regular · own case</td><td>Card facts; the fees in a price; a lease's terms beside the offer; a staff member's direct line and note; "Fields marked with (*) are required."</td><td>Secondary copy on a card or beside a price.</td></tr>
      <tr><td><b>Button</b><br><code>--text-button</code></td><td>14 → 16</td><td>Regular · UPPERCASE, tracked</td><td>Every button; Bentley Inventory in the bar</td><td>Buttons only.</td></tr>
      <tr><td><b>Body</b><br><code>--text-body</code></td><td>18 · 18</td><td>Regular (form inputs Light)</td><td>Paragraphs; form inputs and choices; record rows (hours, specifications)</td><td>Running text; what a visitor types; data rows.</td></tr>
      <tr><td><b>Lead</b><br><code>--text-lead</code></td><td>18 → 24</td><td>Regular · own case</td><td>The line under a chapter title; "Our Location"; department names in the hours</td><td>A title's lead line; group headings on inner pages.</td></tr>
      <tr><td><b>H3</b><br><code>--text-h3</code></td><td>22 → 30</td><td>Light · own case</td><td>Card titles and prices; inner-page section headings (<code>h2.h2--small</code>: Opening Hours, Contact Information, Reviews); the routes inside Menu</td><td>A card's or model's name; an inner page's section headings.</td></tr>
      <tr><td><b>Inner page title</b><br><code>.sub__title</code></td><td>32 → 50</td><td>Light · own case</td><td>Finance Department, Parts Department, Ask a Tech</td><td>The one <code>h1</code> of an inner page.</td></tr>
      <tr><td><b>H2</b><br><code>--text-h2</code></td><td>32 → 56</td><td>Light</td><td>The price in the car page's offer; the car page's section headings; model-page chapter headings</td><td>A heading one step under its page's title.</td></tr>
      <tr><td><b>Display</b><br><code>--text-display</code></td><td>36 → 64</td><td>Light · own case</td><td>Home chapter titles; the listing's title; a car's name on its page</td><td>Chapter titles; the title of the listing and of a car page.</td></tr>
      <tr><td><b>Hero</b><br><code>.hero__title</code></td><td>44 → 66</td><td>Light · UPPERCASE</td><td>The home slide's title; a model page's name</td><td>A model or range name only (the capitals rule).</td></tr>
    </tbody></table>
    <p class="ds-note" style="margin-top:var(--space-5)">Two held forms of Display, both intended: <b>held to the screen</b> (<code>min(var(--text-display), 6.6vh)</code>) on the home page's one-screen chapters, and <b>fitted to its plate</b> over a photograph (Sell us your car, the pre-owned slides, Bespoke).</p>
  </section>

  <section class="ds-part" id="space">
    <h2 class="ds-h2">Space &amp; layout</h2>
    <p class="ds-note">A 4px base. Corners are square everywhere (<code>--radius: 0</code>). Air goes between groups, not inside every row.</p>
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
      <tr><td>&lt; 768px</td><td>Phone: one column; photographs above their words; the four routes as a bar at the foot of the screen; native pickers.</td></tr>
      <tr><td>768–1023px</td><td>Tablet: two columns where the desktop has more.</td></tr>
      <tr><td>≥ 1024px</td><td>Desktop: the header's two lines; the enquiry's column as tall as the form; the model hero's loop.</td></tr>
      <tr><td>≥ 1536px</td><td>The menu's eight routes inline in the bar (Menu below).</td></tr>
    </tbody></table>
  </section>

  <section class="ds-part" id="buttons">
    <h2 class="ds-h2">Buttons &amp; links</h2>
    <p class="ds-note">Two kinds. <b>.btn</b> — Teal 70%, white type: the call to act, one per group. <b>.btn--line</b> — a hairline outline: the second call, beside or under the first. Uppercase, tracked, square, {val('control-h')} high. Hover changes colour only, over {val('dur-2')}. A verb first, typed in sentence case.</p>
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
    <h3 class="ds-h3">Rail arrows, label, text route</h3>
    <div class="ds-stage"><div class="ds-row" style="align-items:center">{arrows}<p class="label" style="margin:0">Label · uppercase, tracked</p>{link}</div></div>
  </section>

  <section class="ds-part" id="forms">
    <h2 class="ds-h2">Forms</h2>
    <p class="ds-note">One form wherever a form is — every inner page and every car page — drawn as bentleymotors.com draws its own (Request a test drive). Approved by the client's side, 2026-10-26.</p>
    <div class="ds-stage ds-stage--white">{wrap(VDP_ROOT, enquire)}</div>
    <div class="ds-rules ds-rules--two">
      <section><h3>Fields</h3><ul>
        <li>The fields: first / last name, email / phone in two columns (one on a phone); <i>Best time to contact</i> across, under Phone; message; consent.</li>
        <li><i>Fields marked with (*) are required.</i> is the form's first line, inside its plate, across both columns.</li>
        <li>The label stands on the field's line where the value will go — Body Light, Dark Grey 40%, own case — and rises above the line at 14px on focus or with a value (<code>js/page.js</code>).</li>
        <li>A 1px line in the ink, 2px with focus, no box round a field.</li>
        <li>Check box: a 24px square, 2px Teal 70% edge, white tick on Teal. A choice: a 20px circle, a dot when chosen.</li>
        <li>Photographs to send: a dashed drop zone (<i>Drag and drop here</i> + Upload), each chosen photo a thumbnail with its own ×.</li>
        <li>The reCAPTCHA line at the legal size. Error and success colours for form states only.</li>
      </ul></section>
      <section><h3>Dropdowns</h3><ul>
        <li><b>Closed:</b> the browser's own <code>&lt;select&gt;</code> on the field's ruled line, a firm short chevron; it shows only its label until something is chosen.</li>
        <li><b>Open:</b> the site's own list, as the demo draws it (<code>js/page.js</code>, <code>.dd</code>) — never the operating system's list on a desktop.</li>
        <li>It drops from the field's line, left edge on the field's, at least the field's width: a white plate, a hairline, no shadow.</li>
        <li>40px rows, 16px type; model names in capitals; on the listing's filters the number of cars each choice leaves, at the right.</li>
        <li>Its height is its choices — no empty foot. The chosen row marked by a 2px line at its left.</li>
        <li>Keys: arrows, Home / End, Enter, Escape, Tab. On a touch screen the phone's own picker.</li>
      </ul></section>
    </div>
    <h3 class="ds-h3">The enquiry block — address, form, hours</h3>
    <p class="ds-note">Beside the form, one column: the heading, <b>Our Location</b> (address), the department's phone, <b>Get directions</b> / <b>Send to phone</b>, and under them that department's hours (Parts Hours on Parts, Sales Hours on Finance and the model pages). From 1024px the column is as tall as the form: the heading's capitals on the plate's top edge, the last hours rule on its bottom edge (<code>.enquire--fit</code>). <b>The location block is the same on every page</b> — the same heading, lines and two buttons.</p>
  </section>

  <section class="ds-part" id="cards">
    <h2 class="ds-h2">Vehicle cards</h2>
    <p class="ds-note">One card everywhere: photograph, name, facts, and the price plate — <b>Final price</b> leads; MSRP and the two dealer charges sit beneath as the working. A lease offer carries its term and the money down (Bentley's word: "down").</p>
    <h3 class="ds-h3">Cards in a row — the rule</h3>
    <ul class="ds-list">
      <li><b>One height.</b> Every card in a row is as tall as the tallest one in it. No card ends short.</li>
      <li><b>Lines level across the row:</b> photograph · mark band · kind · name · facts · price · build · extra line · View details. When one card's line runs longer (a kind line on two lines, a two-line name, a third lease line), that line grows in the whole row, so the next line still starts on the same level in every card.</li>
      <li><b>No empty band.</b> A card without a mark keeps no room for one: its words start right under its photograph, and what it is shorter by stays above View details. Its lines then sit higher than a marked neighbour's — that is accepted; an empty gap under the photograph is not.</li>
      <li><b>View details on the foot line</b> of the card, the same in every card of the row.</li>
      <li><b>One photograph shape</b> (4:3, the car whole in the frame, the same crop rule) in every card.</li>
      <li><b>Everywhere cards stand side by side:</b> the listing, the home page's New in stock, a model page's In Stock, More cars on the car page, Special Offers.</li>
      <li><b>How:</b> CSS subgrid. The list is a grid; each card spans nine of its rows (<code>grid-row: span 9; grid-template-rows: subgrid</code>), the photograph and the band take rows 1–2, the words are a subgrid of the other seven; a card without a mark runs its words from row 2 to the foot in one column, View details at its foot (<code>css/static7.css</code>). Never a fixed card height, never cut text, never an ellipsis.</li>
      <li><b>On a phone</b> the cards stand one above another, each at its own height.</li>
    </ul>
    <h3 class="ds-h3">Marks under the photograph</h3>
    <ul class="ds-list">
      <li><b>Never on the photograph</b> — nothing covers the car. One mark at a time, as a band directly under the photograph.</li>
      <li><b>Only a marked card has a band.</b> Beside it, an unmarked card keeps no empty room: its words start under its photograph (see Cards in a row).</li>
      <li>Lease: Heritage White, black type, the payment then its term and money down. Sale Pending: Bentley Green. Sold: Dark Grey (a "Recently sold" record only — a sold car never appears in the listing).</li>
      <li><b>Certified Pre-Owned</b> is a band of its own (the page ground, a hairline above) for a certified car with no other mark; with a lease, "Certified by Bentley" stays in the kind line.</li>
    </ul>
    <div class="ds-cards">{flags}</div>
    <h3 class="ds-h3">On the home page rail</h3>
    <div class="ds-stage ds-cards">{wrap(CARD_HOME, homecard)}</div>
    <h3 class="ds-h3">In the listing — every kind in stock</h3>
    <div class="ds-cards">{cardgrid}</div>
  </section>

  <section class="ds-part" id="header">
    <h2 class="ds-h2">Header &amp; menu</h2>
    {MENU}
    <h3 class="ds-h3">Live, at this window's width</h3>
    <div class="ds-stage ds-stage--header">{header}</div>
    <h3 class="ds-h3">Recently Viewed</h3>
    <ul class="ds-list">
      <li>The demo site's widget, on every page (<code>js/page.js</code>, <code>.rv</code>). Each car page remembers its car in the browser (the last eight, newest first).</li>
      <li>A tab at the lower right: the car icon, <b>Recently Viewed</b> in the button register and the count; on a phone the icon and count only, above the foot bar.</li>
      <li>Open: the cars on a white plate — first photograph (4:3), name, <b>Final price · Stock</b> — never MSRP. Escape, × or a press elsewhere closes it.</li>
      <li><b>Nothing else may sit under the tab</b> — on a model page's hero, the film's call keeps only its round button between 1024 and 1279px.</li>
    </ul>
    <h3 class="ds-h3">Footer</h3>
    <div class="ds-stage ds-stage--header">{footer}</div>
  </section>

  <section class="ds-part" id="photo">
    <h2 class="ds-h2">Text on photographs</h2>
    <ul class="ds-list">
      <li><b>Never on the car.</b> The words go where the car is not — the road, the ground, the sky, a lit wall. Choose and position the frame for the words (<code>object-position</code> set per photograph, per breakpoint).</li>
      <li><b>White on a dark region, the ink on a light one</b> (a studio wall). On white words: headings 100%, copy 92%, labels 84–88%.</li>
      <li><b>Measured on the render</b>, not guessed: the photograph as drawn, with its shade, under each line; the 95th percentile of the pixels must reach <b>4.5 : 1</b> for text, <b>3 : 1</b> for headings from 24px. A moving loop is measured over every second.</li>
      <li><b>A shade only under the words</b> — a corner or two-way gradient of Black (#040404), as the page head and model hero above give it. Never a full-frame scrim, never a box behind the words.</li>
      <li><b>Where a region fails, the words move</b> to a darker part of the frame, or the frame changes — never a heavier shade.</li>
      <li>On a phone (inner pages below 768px, model pages below 1024px) the words leave the photograph and stand under it, in the ink.</li>
    </ul>
  </section>

  <section class="ds-part" id="sections">
    <h2 class="ds-h2">Home page</h2>
    <p class="ds-note">One chapter, one screen; photographs only, slides turned by the visitor. Each chapter is shown live at 1440px and 390px.</p>
    {sections}
  </section>

  <section class="ds-part" id="inner">
    <h2 class="ds-h2">Inner pages</h2>
    <p class="ds-note">Contact, Finance, About, Parts, Sell Your Vehicle, the Payment Calculator and Ask a Tech share one template (<code>css/subpages.css</code>, loaded last). Any page still to be redesigned takes these blocks, in this order: <b>page head · tiles · department · enquiry · map · reviews</b>. A page that is mainly a form takes the form-page order. Text pages are written as Writing says.</p>
    <div class="ds-tpl">
      <figure class="ds-map"><img src="assets/ds/map-parts.webp" alt="The Parts Department page, whole, at 1440px" width="720" height="2487" loading="lazy"><figcaption>The template whole: Parts Department, 1440px · <a href="parts.html">open</a></figcaption></figure>
      <div>
        {SUB_HEAD}
        <h3 class="ds-h3">The page head, live</h3>
        <div class="ds-stage ds-stage--band">{wrap(SUB, subhead)}</div>
      </div>
    </div>
    {SUB_TILES}
    {SUB_PHONE}
    {SUB_DEPT}
    <h3 class="ds-h3">The staff card, live</h3>
    <p class="ds-note">The demo's card, kept as it is there: a white plate with a hairline, the portrait 4:3, the job title as a label, the name in Bentley Light (26.4px at most), the direct line as "Call …", a note under it if there is one (a language spoken). Three across, 40px apart, every card in a row as tall as the tallest; two on a tablet, one on a phone.</p>
    <div class="ds-stage">{wrap(TEAM, member)}</div>
    {SUB_ENQ}
    {SUB_MAP}
    {SUB_REV}
    {SUB_FORMPAGE}
    {SUB_THREE}
    {SUB_PROMO}
    <h3 class="ds-h3">Per page</h3>
    <table class="ds-table"><thead><tr><th>Page</th><th>Its blocks</th></tr></thead><tbody>
      <tr><td><a href="contact.html">Contact Us</a></td><td>Head · message + form · Opening Hours (Sales, Service, Parts in a row) · the location with the showroom photograph · map.</td></tr>
      <tr><td><a href="finance.html">Finance</a></td><td>Head · four tiles (Finance application the lead; Value your trade; Payment calculator; View inventory) · reviews · enquiry with Sales Hours.</td></tr>
      <tr><td><a href="about.html">About Us</a></td><td>Head · intro · staff cards · Opening Hours · enquiry · map.</td></tr>
      <tr><td><a href="parts.html">Parts</a></td><td>The template whole: head · four tiles · department · enquiry with Parts Hours · map · reviews.</td></tr>
      <tr><td><a href="sell.html">Sell Your Vehicle</a></td><td>Form page: words · the form (photo drop zone) · hours and location under it.</td></tr>
      <tr><td><a href="calculator.html">Payment Calculator</a></td><td>Head · the calculator, its result on a Bentley Green plate (on a phone above the fields).</td></tr>
      <tr><td><a href="ask-a-tech.html">Ask a Tech</a></td><td>Head · offer plate · form page · three columns (location, Service Hours, Parts Hours).</td></tr>
    </tbody></table>
  </section>

  <section class="ds-part" id="model">
    <h2 class="ds-h2">Model pages</h2>
    <p class="ds-note">One template for every model (Flying Spur, Torcal, Continental GT, GT Convertible built). The way in is the home page's Model Range: each model's tile opens its page. Bentley's own words, photographs and film; the US figures as Bentley's US page gives them (mph, lb-ft, 0–60, bhp) — never invented; the official Bentley Motors film (its uploader checked). <b>The brightest Bentley frames for the model</b> — its signature colour where it has one (Torcal: the lime Torcal S, not the silver studio set). Order: <b>hero · chapter bar · The Range · Exterior · Interior · Performance · Personalisation · In Stock · enquiry</b>.</p>
    <div class="ds-tpl">
      <figure class="ds-map"><img src="assets/ds/map-flying-spur.webp" alt="The Flying Spur page, whole, at 1440px" width="720" height="5031" loading="lazy"><figcaption>The template whole: Flying Spur, 1440px · <a href="flying-spur.html">open</a></figcaption></figure>
      <div>{MX_BLOCKS}</div>
    </div>
  </section>

  <section class="ds-part" id="vdp">
    <h2 class="ds-h2">Listing &amp; car page</h2>
    <ul class="ds-list">
      <li><b>Listing</b> — the cards above; filters as dropdowns with car counts; filters work from the URL (<code>?condition=new&amp;model=Bentayga</code>); the price disclaimer at the legal size.</li>
      <li><b>Car page head</b> — the name at the left with Save · Share · Email; the price plate at the right — MSRP, the two charges, a rule, <b>Final price</b>, Confirm availability.</li>
      <li><b>The photographs carry no flag.</b> A lease is the offer's, under its own flag <b>Lease special</b> beside the photographs.</li>
    </ul>
    <div class="ds-stage">{wrap(VDP_ROOT, vdptop)}</div>
    <h3 class="ds-h3">Offer and lease special</h3>
    <div class="ds-row" style="align-items:flex-start">
      <div class="ds-stage" style="flex:1 1 360px">{wrap(VDP_SIDE, offer)}</div>
      <div class="ds-stage" style="flex:1 1 360px">{wrap(VDP_SIDE, special)}</div>
    </div>
    <h3 class="ds-h3">Pricing details</h3>
    <div class="ds-stage">{wrap(VDP_ROOT, pricing)}</div>
  </section>

  <section class="ds-part" id="writing">
    <h2 class="ds-h2">Writing</h2>
    <table class="ds-table"><thead><tr><th>What</th><th>How it is written</th><th>Example</th></tr></thead><tbody>
      <tr><td>Page title</td><td>Title Case, as written; the eyebrow always <i>Braman Bentley Palm Beach</i>.</td><td>Parts Department</td></tr>
      <tr><td>Section heading</td><td><code>h2.h2--small</code>, Title Case.</td><td>Opening Hours · Contact Information · Meet Our Staff</td></tr>
      <tr><td>Group heading</td><td><code>h3</code>, one or two words, Title Case.</td><td>Sales · Service · Parts · Our Location</td></tr>
      <tr><td>Model name</td><td>Capitals in a heading; the one place capitals are typed.</td><td>FLYING SPUR · TORCAL · MULLINER</td></tr>
      <tr><td>Label</td><td><code>.label</code>: typed in normal case, uppercase from the CSS. A form field's label stays in its own case.</td><td>Director of Luxury Sales · Mon – Thu</td></tr>
      <tr><td>Button</td><td>A verb first, sentence case; the names the demo already uses.</td><td>Get directions · Send to phone · Send message</td></tr>
      <tr><td>Telephone</td><td>Always with dashes; <code>tel:+1…</code>; a direct line reads "Call …".</td><td>561-926-9111 · Call 561-681-4903</td></tr>
      <tr><td>Hours</td><td>Lower-case am/pm, an en dash, "Closed".</td><td>9:00 am – 8:00 pm · Closed</td></tr>
      <tr><td>Legal line</td><td>12px on 16px, <code>--text-legal</code>, Dark Grey 40%, own case — the one exception to the 14px floor. Not what stands beside a price.</td><td>This site is protected by reCAPTCHA…</td></tr>
      <tr><td>Body copy</td><td>The dealer's or Bentley's own words, as written.</td><td>—</td></tr>
    </tbody></table>
  </section>

  <section class="ds-part" id="price">
    <h2 class="ds-h2">Price (FTC 2026 · Florida § 501.976)</h2>
    <ul class="ds-list">
      <li>The figure that stands out is the <b>Final price</b>: the sale price with the dealer's charges in it ($1,189 dealer service + $514 electronic filing). Only tax, tag, registration and title may be left out.</li>
      <li>MSRP and "+ Dealer service charge", "+ Electronic filing charge" sit beneath as the working.</li>
      <li>"You save" is measured against the Final price.</li>
      <li>Every lease payment carries its term and the money down beside it; a lease that rests on a rebate says so, with the credit it needs.</li>
      <li>Sold cars leave the listing, its count, filters and the home rail. A pending deal reads <b>Sale Pending</b>.</li>
    </ul>
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
# the examples and page maps go with it
import shutil
shutil.copytree(ROOT + 'assets/ds', OUT + 'assets/ds', dirs_exist_ok=True)
print("design-system.html:", len(cards), "listing cards,", len(TOC), "chapters")

# the same page for the git preview, at the repo root: the repo's own
# stylesheets (the handoff's are cleaned copies of them), its assets, and its
# pages under their "7" names
GIT_CSS = {'tokens': 'system', 'site': 'index7', 'cards': 'cards', 'inventory': 'inventory7',
           'vehicle': 'vehicle7', 'theme': 'day7', 'static': 'static7', 'subpages': 'subpages7'}
git = re.sub(r'href="css/(\w+)\.css"', lambda m: 'href="css/%s.css"' % GIT_CSS[m.group(1)], page)
git = re.sub(r'href="([a-z-]+)\.html', r'href="\g<1>7.html', git)
git = git.replace('href="vehicles/', 'href="vehicles7/').replace('src="index.html', 'src="index7.html')
# the repo's sheets still carry the looks; the pages open on look 2 (the
# client's: Satin Linen ground, white plates) — the handoff has only that look
git = git.replace('<html lang="en" class="theme-satin">', '<html lang="en" class="theme-satin" data-look="2">', 1)
open(ROOT + 'design-system7.html', 'w', encoding='utf-8', newline='\n').write(git)
print('design-system7.html: git copy')
