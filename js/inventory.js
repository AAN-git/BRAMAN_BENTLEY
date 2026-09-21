/* Bentley Palm Beach — the inventory.
   The header and the menu as on the home page; then four picks over the
   cards already in the page: condition, model, year, sort. The cards carry
   their facts as data attributes (generated from data/inventory.json, as are
   the option lists), so a feed can replace the markup later and this file
   will not need to know. With the file absent the page is the full list. */

(function () {
  "use strict";

  var root = document.documentElement;
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
  var motion = root.classList.contains("motion") && !reduced.matches;
  if (!motion) root.classList.remove("motion");

  /* --- Header: condenses once the page has moved; the way back appears
         once the first screen has gone ------------------------------------ */
  var header = document.getElementById("mh");
  var scrolled = false, painting = false;
  function paint() {
    painting = false;
    var past = window.scrollY > 24;
    if (window.scrollY > window.innerHeight * 0.9) root.setAttribute("data-past", "");
    else root.removeAttribute("data-past");
    if (past === scrolled) return;
    scrolled = past;
    if (past) header.setAttribute("data-scrolled", "");
    else header.removeAttribute("data-scrolled");
  }
  function requestPaint() { if (!painting) { painting = true; window.requestAnimationFrame(paint); } }
  window.addEventListener("scroll", requestPaint, { passive: true });
  window.addEventListener("resize", requestPaint);
  paint();

  /* --- Menu (under 1024) ---------------------------------------------------- */
  var toggle = header.querySelector(".mh__toggle");
  function setMenu(open) {
    if (open) header.setAttribute("data-open", "");
    else header.removeAttribute("data-open");
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    document.body.style.overflow = open ? "hidden" : "";
  }
  toggle.addEventListener("click", function () { setMenu(!header.hasAttribute("data-open")); });
  header.querySelector(".mh__nav").addEventListener("click", function (e) { if (e.target.closest("a")) setMenu(false); });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && header.hasAttribute("data-open")) { setMenu(false); toggle.focus(); }
  });

  /* --- The picks ----------------------------------------------------------- */
  var grid = document.getElementById("grid");
  if (!grid) return;

  var cards = Array.prototype.slice.call(grid.querySelectorAll(".card"));
  var picks = Array.prototype.slice.call(document.querySelectorAll("[data-pick]"));
  var select = document.querySelector(".sort__select");
  var count = document.querySelector("[data-count]");
  var split = document.querySelector("[data-split]");
  var empty = document.querySelector(".srp__empty");
  var query = empty.querySelector("[data-query]");
  var clear = empty.querySelector(".srp__clear");
  var columns = 3;
  function measureColumns() {
    columns = window.getComputedStyle(grid).gridTemplateColumns.split(" ").length || 1;
  }

  /* Every card remembers where the page put it, so "Featured" is that order. */
  cards.forEach(function (card, i) { card.dataset.featured = i; });

  var sorters = {
    "featured":    function (a, b) { return +a.dataset.featured - +b.dataset.featured; },
    "price-asc":   function (a, b) { return +a.dataset.price - +b.dataset.price; },
    "price-desc":  function (a, b) { return +b.dataset.price - +a.dataset.price; },
    "year-desc":   function (a, b) { return +b.dataset.year - +a.dataset.year || +a.dataset.featured - +b.dataset.featured; },
    "mileage-asc": function (a, b) { return +a.dataset.mileage - +b.dataset.mileage; },
    "model":       function (a, b) { return a.dataset.model.localeCompare(b.dataset.model) || +a.dataset.featured - +b.dataset.featured; }
  };

  /* A pick left on its first option asks for nothing. "Certified" is a
     condition of its own: the pre-owned cars carrying Bentley's programme. */
  function matches(card) {
    return picks.every(function (p) {
      var want = p.value;
      if (!want) return true;
      if (p.dataset.pick === "condition" && want === "certified") return card.dataset.certified === "1";
      var have = card.dataset[p.dataset.pick];
      return have === undefined || have === want;
    });
  }

  var pending = 0;

  function render(first) {
    var sorter = sorters[select.value] || sorters.featured;
    var shown = cards.filter(matches).sort(sorter);

    /* Off, reorder, then on — so the arrival plays from the new order. */
    if (motion) cards.forEach(function (c) { c.classList.add("is-off"); });

    window.clearTimeout(pending);
    pending = window.setTimeout(function () {
      measureColumns();
      cards.forEach(function (c) { c.hidden = shown.indexOf(c) === -1; });
      shown.forEach(function (c, i) {
        grid.appendChild(c);
        c.style.setProperty("--col", i % columns);
      });
      count.textContent = shown.length;
      var n = shown.filter(function (c) { return c.dataset.condition === "new"; }).length;
      split.textContent = n + " new and " + (shown.length - n) + " pre-owned";
      empty.hidden = shown.length > 0;
      query.textContent = picks.filter(function (p) { return p.value; })
        .map(function (p) { return p.options[p.selectedIndex].textContent; })
        .join(" · ") || "your choice";
      if (motion) {
        /* two frames: the off state has to paint before it transitions */
        window.requestAnimationFrame(function () {
          window.requestAnimationFrame(function () {
            shown.forEach(function (c) { c.classList.remove("is-off"); });
          });
        });
      }
      if (!first) {
        var top = grid.getBoundingClientRect().top + window.scrollY - 120;
        if (window.scrollY > top) window.scrollTo({ top: top, behavior: reduced.matches ? "auto" : "smooth" });
      }
    }, motion ? 40 : 0);
  }

  picks.forEach(function (p) { p.addEventListener("change", function () { render(false); }); });
  select.addEventListener("change", function () { render(false); });
  clear.addEventListener("click", function () {
    picks.forEach(function (p) { p.value = ""; });
    render(false);
    picks[0].focus();
  });

  /* A link can arrive with a pick set: inventory.html?condition=used&model=Bentayga */
  var params = new URLSearchParams(window.location.search);
  var preset = false;
  picks.forEach(function (p) {
    var v = params.get(p.dataset.pick);
    if (!v) return;
    for (var i = 0; i < p.options.length; i++) {
      if (p.options[i].value.toLowerCase() === v.toLowerCase()) { p.value = p.options[i].value; preset = true; }
    }
  });
  if (params.get("sort") && sorters[params.get("sort")]) { select.value = params.get("sort"); preset = true; }

  /* First paint: the cards arrive, a column at a time. */
  measureColumns();
  if (motion) cards.forEach(function (c, i) { c.classList.add("is-off"); c.style.setProperty("--col", i % columns); });
  if (preset) render(true);
  else if (motion) {
    window.requestAnimationFrame(function () {
      window.requestAnimationFrame(function () {
        cards.forEach(function (c) { c.classList.remove("is-off"); });
      });
    });
  }
  window.addEventListener("resize", function () {
    var was = columns; measureColumns();
    if (was !== columns) cards.forEach(function (c, i) { c.style.setProperty("--col", i % columns); });
  });
})();
