# Bentley Palm Beach — project notes

See README.md for the directions, the data and the build.

## Feedback log

- **Client baseline:** the last version the client saw is Direction 6 as live
  on GitHub Pages at commit f3a738a. Never edit a direction the client has
  seen; changes go into a new numbered copy (6 → 7), mirrored by
  `tools/mirrorN.py`.
- **Audience (client, 2026-10-04):** an older clientele, on desktop and phone.
  Rejected: scroll-driven UI (Lenis, chapters that stick and cover, reveals on
  scroll), autoplaying sliders and any video (dead cell-service pockets make a
  film look broken). Approved direction: a normal static page, photographs
  only, slides turned by the visitor.
- **Routes always on screen (client, 2026-10-04):** Bentley Inventory
  (prominent), Special Offers, Financing, Contact Us — the header's second line
  on desktop, a bar at the foot of the screen on a phone.
- **Under the hero (client's sketch, 2026-10-04):** NEW INVENTORY and
  PRE-OWNED INVENTORY side by side, SPECIAL OFFERS centred beneath; static, the
  same for every slide; no empty space between the slide and these buttons.
  "Both sites" in the client's note means Bentley **and the Braman
  Rolls-Royce site**: the whole note applies there too (Alex, 2026-10-05).
- **Don't touch what already works (Alex, 2026-10-05, said sharply):** change
  only what was asked. Car cards keep direction 6's width and type exactly.
- **Home "New in stock":** four cars; one row, three in view, centred; arrows
  at the sides; title centred. Never stack the cards in rows (rejected 2026-10-05).
- **Torcal slide:** full screen like every slide (a split layout was rejected
  2026-10-05); words on the road and grass below the car, never on it.
- **Sell your car:** photograph across the section, the words on a plate at
  the right, high, clear of the car.
- **Retailer section (Okeechobee Boulevard):** its own ground, Heritage White.
- Look 2 (Satin Linen) is the client's chosen look.
- **Demo vs git (Alex, 2026-10-26):** "демо" is the developers' built site
  (bramanbentleypalmbeach.aandemo.com), "гит" is ours. We rebuild on git the
  pages the demo got wrong (Alex in column E of the testing sheet), then hand
  them over with the design system; where the demo already does a part well
  (the staff card), ours takes the demo's design.
- **Inner-page title (Alex, 2026-10-26, corrected the same day):** the eyebrow
  is always exactly "Braman Bentley Palm Beach" on every inner page; the title
  is the page's name in Title Case. Both in their own case, not capitals, as
  bentleymotors.com sets titles — capitals are for model names only (MULLINER,
  TORCAL). All caps on the title was tried and withdrawn. Written down in the design
  system ("Inner pages"), with the writing rules: section headings in Title
  Case, phone numbers with dashes (561-926-9111), a direct line as "Call …"
  with any note (a language) under it.
- **Forms (Alex, 2026-10-26):** one form wherever a form is (inner pages and
  every car page): first/last name, email/phone in two columns, best time to
  contact under the phone across, message, consent; one column on a phone.
- **Legal lines (Alex, 2026-10-26):** 16px was "far too much". Legal text that
  stands apart (reCAPTCHA, copyright, the price disclaimer, full lease terms)
  is 12px on 16px, as bentleymotors.com — token --text-legal, the one exception
  to the 14px floor. What stands beside a price keeps its size (FTC).
- **Form labels (Alex, 2026-10-26, approved: "a good move"):** as on
  bentleymotors.com — the label on the field's line in Body Light grey, rising
  above it at 14px on focus or value (js/page7.js marks fields; static7.css).
  Line in the ink, 2px on focus, no box; firm chevron; 24px square check box,
  20px circle choice, Teal 70% edge. Every form, every new one. In the DS.
- **Dropdowns (Alex, 2026-10-26, corrected the same day):** the closed field is
  the native <select> on its ruled line; the OPEN list is our own panel as on
  the demo (white plate, hairline, 40px rows, model names in capitals, car
  counts on the listing's picks), dropped from the line, left-aligned, at least
  the field's width, height = its choices (not the demo's empty foot). The
  Windows system list was "hujevo" — never leave the open list to the OS on
  desktop; phones keep the native picker. js/page7.js + .dd; in the DS.
- **Card marks (Alex, 2026-10-26):** lease, Sale Pending, New Arrival, Sold sit
  as a band under the photograph, never on it. An unmarked card keeps NO empty
  band room, not even beside a marked one (the reserved room was rejected
  twice: first everywhere, then "the wild gap on New · In stock").
  Certified Pre-Owned is a band mark too (certified cars without a
  lease; with a lease, "Certified by Bentley" stays in the kind line). In the DS.
  The car page's photographs carry no flag either; the lease is the offer's.
- **Cards in a row: one height (Alex, 2026-10-26, a rule for every real page,
  not only the DS):** View details on one foot line; among marked cards (and
  among unmarked ones) the lines meet across the row, a line that runs long
  grows in the whole row. An unmarked card's words start under its photo and
  its slack sits above View details — its lines may sit higher than a marked
  neighbour's. static7.css: card spans 9 grid rows, body a subgrid of 7; an
  unmarked body spans rows 2–9 as a column. Never fixed heights or cut text. The DS shows cards in look 2
  (white plates on Satin Linen) exactly as the pages do.
- **Model pages (Alex, 2026-10-26):** first Kirsten's version — the AAN master
  model page's order (aanmaster2027.aandemo.com/models/vantage/: hero, key
  figures, lead, film, statement, alternating stories, then stock and enquiry)
  in our parts; then our own alternative. The way in is the home page's Model
  Range tile (Bentayga → bentayga-speed7.html). No invented specs: the master's
  engine/specs blocks wait for Bentley's figures. In the DS.
- **Model page photos/figures (Alex, 2026-10-26):** photographs from Bentley's own
  model page (authorised), no placeholder tags; the key figures are Bentley's US
  four (mph, lb-ft, 0–60, bhp). A story's photograph starts on its title's
  capitals — not lower, not higher.
- **Model pages, two versions (Alex, 2026-10-26):** Bentayga Speed stays the AAN
  master layout (Kirsten); every other model gets OUR version, "maximally
  striking": Bentley's words inside its photographs (road, studio wall, dark road
  at sunset), the kinds of mass changing between them. Flying Spur first, then
  Torcal, then the rest. Model photos/figures from bentleymotors.com (US).
  Text on photos is measured on the render; a failing region moves the words.
- **Strictly BENTLEY STYLE (Alex, 2026-10-26):** every element comes from
  Bentley's guidelines, bentleymotors.com's own patterns or our approved
  pages — nothing of my own invention. A short rule drawn before the chapter
  labels on the model page was rejected ("where did this line come from?!").
  No decorative rules, marks or ornaments without a Bentley precedent.
- **Hero video on our model pages — approved (Alex, 2026-10-26):** Bentley's own
  stage loop from the /en/ model page, muted, in the hero (from 1024px, motion
  allowed, pause button, photo on phones); the official Bentley Motors YouTube
  film plays from the hero's third call. Carry it to every model page.
- **Model pages — bright car (Alex, 2026-10-26):** "the Torcal needed a bright
  car — this is very dull": use the model's most vivid Bentley frames (Torcal =
  lime Torcal S), not the silver studio set. Our-version pages now: Flying Spur,
  Torcal, Continental GT, Continental GT Convertible (Bentayga = master).
- **Ready components only (Alex, 2026-10-26):** a demo page rebuilt on git is
  assembled from the DS's components and the templates (offer plate and its
  variations, enquiry block, hours chapter, page head…), the demo's words and
  CTAs verbatim. A part with no component goes into the DS first.
- **Inner pages keep their template (Alex, 2026-10-26):** "we have templates for
  these pages — why did we leave the Bentley styling we set?" Contact, Finance,
  About, Parts, Sell, Calculator stay on the inner-page template (head band,
  Finance tiles, department chapter, form). The model-page language (.mx__*) is
  for model pages only. Fixing a weak inner page = better pictures/words inside
  the template, not a new layout.
