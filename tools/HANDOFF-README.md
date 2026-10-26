# Bentley Palm Beach — handoff (Direction 7)

The approved mockup, as designed: plain HTML, CSS and a little vanilla JS. No build step, no framework, no server-side code.

**Start with `design-system.html`** — its first chapter, *Handoff*, lists what to change on the demo, page by page, with links to the approved pages; the chapters after it show every element on the site's own stylesheets, with the rules for using them.

## Pages

| File | What |
|---|---|
| `index.html` | Home |
| `inventory.html` | The listing (SRP) — filters work from the URL: `?condition=new`, `?condition=used`, `?condition=certified`, `?model=Continental+GT` |
| `vehicles/<stock>.html` | One page per car (VDP) — 60 cars, captured from the retailer's listings |
| `about.html`, `contact.html`, `finance.html`, `parts.html`, `sell.html`, `calculator.html` | The inner pages: About Us (with the staff), Contact Us, Finance Department, Parts Department, Sell Your Vehicle, Payment Calculator (working: standard amortised payment, `js/sub.js`). `bentayga-speed.html` is the **model page in the AAN master's layout**; `flying-spur.html`, `torcal.html`, `continental-gt.html` and `continental-gtc.html` are **our version of the model page** — Bentley's words inside its photographs (see the design system, "Inner pages"); their cars in stock are the listing's cards for that model. The page title and the writing rules for every inner page are in the design system, "Inner pages" |
| `design-system.html` | The design system |

Open any file in a browser. The fonts load best from a local server (`python3 -m http.server` in this folder, then `http://localhost:8000/`).

## Stylesheets — in this order on every page

| File | What |
|---|---|
| `css/tokens.css` | The design tokens: colour, type, space, format. The single source of values. |
| `css/site.css` | Header, hero, chapters, rails, footer — the site |
| `css/cards.css` | The vehicle card |
| `css/inventory.css` | The listing (listing and car pages) |
| `css/vehicle.css` | The car page (car pages only) |
| `css/theme.css` | The theme: Satin Linen 40%, the client's choice — carried by `<html class="theme-satin">` |
| `css/static.css` | The static page: last, wins over the above |
| `css/subpages.css` | The inner pages only: the page title, the picture band, the staff card, hours, location. After `static.css` |

The home page loads `tokens, site, cards, theme, static`; the listing adds `inventory`; a car page adds `inventory` and `vehicle`; an inner page adds `inventory`, `vehicle` and, last, `subpages`.

In `theme.css` some selectors repeat the class (`html.theme-satin.theme-satin`). That keeps the exact weight the approved look had in the cascade. Do not shorten them.

## Scripts

| File | What |
|---|---|
| `js/page.js` | Every page: the layout width the header-aligned edges use; the Torcal photograph's framing |
| `js/home.js` | The home page: the header and the phone menu, the hero and pre-owned slides, the inventory rail |
| `js/inventory.js` | The listing: the header and the phone menu, filters and sort |
| `js/vehicle.js` | The car page: the header and the phone menu, gallery, 360, lightbox |
| `js/sub.js` | The inner pages: the reviews row on Finance, turned by its arrows |

Slides turn only when the visitor turns them. The page is static by the client's brief: no scroll effects, no autoplay, no video.

## Rules that must survive the build

- **Price (FTC 2026, Florida § 501.976):** the figure that stands out is the **Final price** — the sale price with the dealer's charges in it ($1,189 dealer service + $514 electronic filing). MSRP and the two charges sit beneath. Every lease payment shows its term and the money **down** beside it. A lease that rests on a rebate says so. Sold cars are not advertised. A pending deal reads **Sale Pending**.
- **Photographs:** the whole car in the frame, always. Words never on the car.
- **Routes always on screen:** Bentley Inventory, Special Offers, Financing, Contact Us — the header's second line on a desktop, a bar at the foot of the screen on a phone.
- **Colours:** only those in `tokens.css`, from the Bentley Retailer Website Guidelines.

## Assets

`assets/` holds only what the pages use: the Bentley fonts (licensed — for this retailer's site only), the photographs, the car galleries and the icons.

The vehicle data on the listing and car pages is a capture of 21 September 2026. On the live site it comes from the inventory feed. Prices, fees and lease terms must come from the feed, never be typed into templates.
