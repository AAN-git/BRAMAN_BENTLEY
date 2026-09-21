# Bentley Palm Beach — homepage directions

Static mock-ups, no build step: open any `index*.html`, or serve the folder
(`python3 -m http.server`).

| File | Direction |
|---|---|
| `index.html` | Light, inset hero — the guideline's first worked example |
| `index2.html` | Cinematic dark hero, light page below |
| `index3.html` | Offer-led, stepped display captions |
| `index4.html` | **Dark** — one chapter per screen, full-screen slides, stacked chapters with their own openings |
| `dashboard.html` | **The presentation** — the four directions as a deck for the retailer: cover, one chapter per direction with real renders, side by side, next steps |
| `inventory.html` | **The inventory (SRP)** in direction 4's language — every car on the floor, the retailer's own price build, four picks (condition, model, year, sort) |
| `vehicles/<stock>.html` | **The vehicle pages (VDP)** — generated, one per car: photographs, the plate, the offer as the retailer builds it, lease terms, enquiry |

`css/system.css` carries the tokens (palette, type and spacing from the 2026
Retailer Website Guidelines); each direction has its own stylesheet and script.
Imagery in `assets/bm/` is Bentley library photography with provenance in
`assets/bm/MANIFEST.json`; inventory and pre-owned records on `index4` are the
retailer's own listings as published on 18 September 2026.

## Inventory

`data/inventory.json` is the source: 60 cars (42 new, 18 pre-owned) as the
retailer listed them on 21 September 2026, with the price build exactly as the
retailer's cards show it — MSRP or Braman Price, the $1,189 dealer service
charge, the $514 electronic filing charge, the sale (or final) price, the lease
where one is offered and its Details popup parsed into `lease_terms`. The
`note` field says what every key means. Each car carries its first eight
retailer photographs (`assets/img/vdp/<stock>/`, 1400 wide) and a card image
(`assets/img/inventory/<stock>.webp`, 840×630). The four cars the retailer has
no photograph of stand on Bentley's picture of the line, labelled.

`python3 tools/build.py` writes the cards into `inventory.html` (and its option
lists), the first twelve new cars onto `index4.html`'s rail, and one page per
car into `vehicles/`, from the SRP's own head, header and footer. Edit the
data, then build; the css/js links are stamped so GitHub Pages serves the new
files. `tools/ingest.py` is the capture step (from a browser session's saved
listing and vehicle pages, not in the repository) that made the data.

Links: `inventory.html?condition=new|used|certified&model=Bentayga&year=2026&sort=price-asc`
pre-select the picks.

The 360 on each vehicle page is the retailer's own turntable (DealerMade
Next HD viewer, ~54 positions × three cameras). The widget cannot be
embedded off the retailer's domain, so `tools/spin.py` asks the viewer's API
for each car's picture set (as the widget does) and keeps 24 frames of the
middle camera, evenly around the turn, 1000 wide (`assets/img/spin/<stock>/`;
`spin_source` records the picks). On the page the second frame of the rail is
the way in and the "360° view" switch is the other; the car turns once by
itself, then under the hand, a throw keeps it turning, the arrows and the
keyboard step it. It needs one saved `LoadVehicle` request body from a
browser session (`.playwright-mcp/drop/dm-post.json`, not in the repository).

The Bentley typeface and the imagery are Bentley brand assets, here for the
client's review only.
