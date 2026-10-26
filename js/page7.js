/* Bentley Palm Beach — direction 7: the page scrolls as any page.
   Direction 6's scroll layer (Lenis) is gone (the client's note of
   2026-10-04: a normal, static page for an older clientele). What stays is
   the one measurement the stylesheets need. */

/* the layout width without the scrollbar, for edges aligned to the fixed header */
(function () {
  var root = document.documentElement;
  function set() { root.style.setProperty("--vw", root.clientWidth + "px"); }
  set();
  window.addEventListener("resize", set);
  document.addEventListener("DOMContentLoaded", set);
})();

/* The Torcal slide (Alex, 2026-10-05): the photograph's roof set just under
   the window's top edge, whatever the window's proportion, so the car is
   whole and the grass beneath it carries the words. Measured here rather
   than in CSS — container units inside object-position are not drawn in
   every browser, and the fallback cut the car's roof. The roof stands at
   42% of the photograph's height. */
(function () {
  var ROOF = 0.42;
  function place() {
    var imgs = document.querySelectorAll(".slide--torcal .hero__img");
    Array.prototype.forEach.call(imgs, function (img) {
      if (window.innerWidth < 768) { img.style.objectPosition = ""; return; }
      var box = img.getBoundingClientRect();
      var nw = img.naturalWidth || 2400, nh = img.naturalHeight || 1617;
      if (!box.width || !box.height) return;
      var H = Math.max(box.width * nh / nw, box.height);      /* drawn height, as object-fit: cover */
      /* more sky over the roof (Alex, 2026-10-05: "lower"), as far as the
         words beneath allow: the car's foot (67% of the frame) stays above
         the title with a little air */
      var air = Math.min(360, Math.max(96, box.height * 0.36));   /* Alex: lower, and as much again */
      var y = air - ROOF * H;
      var slide = img.closest(".slide"), title = slide && slide.querySelector(".hero__title");
      if (title) {
        var tTop = title.getBoundingClientRect().top - box.top;
        y = Math.min(y, tTop - 12 - 0.67 * H);
      }
      y = Math.max(box.height - H, y);                           /* never past the photograph's foot */
      img.style.objectPosition = "50% " + Math.min(0, y).toFixed(1) + "px";
    });
  }
  function soon() { window.requestAnimationFrame(place); }
  window.addEventListener("resize", soon);
  document.addEventListener("DOMContentLoaded", function () {
    place();
    Array.prototype.forEach.call(document.querySelectorAll(".slide--torcal .hero__img"), function (img) {
      if (!img.complete) img.addEventListener("load", place, { once: true });
    });
    /* the slide is hidden until it is turned to; measure again when it is */
    document.addEventListener("click", function (e) { if (e.target.closest && e.target.closest(".hero__arrow")) setTimeout(place, 50); });
    if ("ResizeObserver" in window) {
      var f = document.querySelector(".slide--torcal .slide__field");
      if (f) new ResizeObserver(soon).observe(f);
    }
  });
})();

/* The menu's groups (the demo site's navigation): a press opens one and closes
   the rest; Escape or a press elsewhere closes it. On a wide screen hover and
   focus open a panel too (css/static7.css); this is for touch and keys. */
(function () {
  function close(except) {
    document.querySelectorAll(".mh__item[data-open]").forEach(function (li) {
      if (li === except) return;
      li.removeAttribute("data-open");
      li.querySelector(".mh__open").setAttribute("aria-expanded", "false");
    });
  }
  document.addEventListener("click", function (e) {
    var b = e.target.closest && e.target.closest(".mh__open");
    if (b) {
      var li = b.parentElement, open = !li.hasAttribute("data-open");
      close(li);
      if (open) li.setAttribute("data-open", ""); else li.removeAttribute("data-open");
      b.setAttribute("aria-expanded", open ? "true" : "false");
      return;
    }
    if (!(e.target.closest && e.target.closest(".mh__panel"))) close();
  });
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    var li = document.querySelector(".mh__item[data-open]");
    if (li) { close(); li.querySelector(".mh__open").focus(); }
  });
})();

/* Recently Viewed (the demo site's widget, Alex 2026-10-26): every car page
   remembers its car in this browser (localStorage, the last eight, newest
   first); every page that has one shows a tab at the lower right — the count,
   then on a press the cars, each with its photograph, name, Final price and
   stock. The price is the Final price, as the price rules ask, not the MSRP
   the demo shows. Text goes in as text, never as markup. */
(function () {
  var KEY = "bpb-recently-viewed", MAX = 8;
  function read() { try { return JSON.parse(localStorage.getItem(KEY)) || []; } catch (e) { return []; } }
  function write(a) { try { localStorage.setItem(KEY, JSON.stringify(a)); } catch (e) {} }

  function remember() {
    var h1 = document.querySelector("main.vdp h1"), price = document.querySelector(".vdp__price-value");
    if (!h1 || !price) return;
    var file = location.pathname.split("/").pop().replace(/\.html$/, "");
    var label = document.querySelector(".vdp__price-label");
    var item = {
      url: location.href.split("#")[0].split("?")[0],
      name: h1.textContent.trim().replace(/\s+/g, " "),
      price: (label ? label.textContent.replace("*", "").trim() + " " : "") + price.textContent.trim(),
      stock: file.toUpperCase(),
      img: (function () { var i = document.querySelector("main.vdp img"); return i ? i.src : ""; })()   /* the car's first photograph on its page */
    };
    var list = read().filter(function (x) { return x && x.url !== item.url; });
    list.unshift(item);
    write(list.slice(0, MAX));
  }

  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text) e.textContent = text; return e; }
  var CAR = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.21.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.5 16c-.83 0-1.5-.67-1.5-1.5S5.67 13 6.5 13s1.5.67 1.5 1.5S7.33 16 6.5 16zm11 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM5 11l1.5-4.5h11L19 11H5z"/></svg>';

  function render() {
    var list = read();
    if (!list.length) return;
    var box = el("div", "rv"); box.id = "rv";
    var panel = el("div", "rv__panel"); panel.id = "rv-panel"; panel.hidden = true;
    panel.setAttribute("role", "dialog"); panel.setAttribute("aria-label", "Recently viewed");
    var head = el("div", "rv__head");
    head.appendChild(el("p", "rv__title", "Recently Viewed"));
    var close = el("button", "rv__close", "×"); close.type = "button"; close.setAttribute("aria-label", "Close");
    head.appendChild(close); panel.appendChild(head);
    var ul = el("ul", "rv__list");
    list.forEach(function (x) {
      var li = el("li"), a = el("a", "rv__item"); a.href = x.url;
      var img = el("img"); img.src = x.img; img.alt = ""; img.width = 96; img.height = 72; img.loading = "lazy";
      var body = el("span", "rv__body");
      body.appendChild(el("span", "rv__name", x.name));
      body.appendChild(el("span", "rv__meta", String(x.price).replace("*", "") + " · Stock " + x.stock));
      a.appendChild(img); a.appendChild(body); li.appendChild(a); ul.appendChild(li);
    });
    panel.appendChild(ul);
    var tab = el("button", "rv__tab"); tab.type = "button";
    tab.setAttribute("aria-expanded", "false"); tab.setAttribute("aria-controls", "rv-panel");
    tab.innerHTML = CAR;
    tab.appendChild(el("span", "rv__label", "Recently Viewed"));
    tab.appendChild(el("span", "rv__count", String(list.length)));
    box.appendChild(panel); box.appendChild(tab);
    document.body.appendChild(box);
    document.documentElement.classList.add("has-rv");

    function set(open) { panel.hidden = !open; tab.setAttribute("aria-expanded", open ? "true" : "false"); }
    tab.addEventListener("click", function () { set(panel.hidden); });
    close.addEventListener("click", function () { set(false); tab.focus(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !panel.hidden) { set(false); tab.focus(); } });
    document.addEventListener("click", function (e) { if (!panel.hidden && !box.contains(e.target)) set(false); });
  }

  document.addEventListener("DOMContentLoaded", function () { remember(); render(); });
})();

/* Form labels as bentleymotors.com sets them: the label stands on the field's
   line, in the body size, until the field is chosen or filled; then it rises
   above the line, small. The script only marks which fields hold a value
   (field--float, is-filled); the sheet does the rest. Without it, the labels
   simply stay above their fields. */
(function () {
  function mark(input) {
    var field = input.closest(".field");
    if (field) field.classList.toggle("is-filled", input.value.trim() !== "");
  }
  function init() {
    document.querySelectorAll(".field > .field__input").forEach(function (input) {
      var field = input.parentElement;
      if (!field.querySelector(".field__label")) return;
      field.classList.add("field--float");
      mark(input);
      input.addEventListener("input", function () { mark(input); });
      input.addEventListener("change", function () { mark(input); });
    });
    document.documentElement.classList.add("has-float");
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();

/* The open list of a dropdown as the demo site draws it (Alex, 2026-10-26):
   the closed field stays the browser's own <select> on its ruled line; a press
   opens the site's own list under that line instead of the system's — a white
   plate with a hairline, a choice to a 40px row, the model names in capitals,
   and on the listing's picks how many cars each choice leaves. Its height is
   its choices. Keys: arrows, Home/End, Enter or Space to choose, Escape or
   Tab to close. On a touch screen the phone's own picker stays. */
(function () {
  if (window.matchMedia && window.matchMedia("(pointer: coarse)").matches) return;
  var open = null, uid = 0;

  /* how many cars a choice leaves, the other picks as they stand (the
     listing's own rule: "certified" is the pre-owned cars in Bentley's programme) */
  function counter(sel) {
    var grid = document.getElementById("grid");
    if (!grid || !sel.dataset.pick) return null;
    var cards = Array.prototype.slice.call(grid.querySelectorAll(".card"));
    var others = Array.prototype.slice.call(document.querySelectorAll("[data-pick]")).filter(function (p) { return p !== sel; });
    function ok(card, pick, want) {
      if (!want) return true;
      if (pick === "condition" && want === "certified") return card.dataset.certified === "1";
      var have = card.dataset[pick];
      return have === undefined || have === want;
    }
    return function (value) {
      return cards.filter(function (c) {
        return ok(c, sel.dataset.pick, value) && others.every(function (p) { return ok(c, p.dataset.pick, p.value); });
      }).length;
    };
  }

  function close(refocus) {
    if (!open) return;
    var o = open; open = null;
    o.list.remove();
    o.sel.setAttribute("aria-expanded", "false");
    o.sel.removeAttribute("aria-activedescendant");
    o.box.classList.remove("is-open");
    if (refocus) o.sel.focus();
  }

  function activate(i, step) {
    var items = open.items;
    i = Math.max(0, Math.min(items.length - 1, i));
    while (items[i].hidden && i + (step || 1) >= 0 && i + (step || 1) < items.length) i += step || 1;
    while (items[i].hidden && i + 1 < items.length) i += 1;   /* the prompt at the top: the first real choice */
    items.forEach(function (li, k) { li.classList.toggle("is-active", k === i); });
    open.active = i;
    open.sel.setAttribute("aria-activedescendant", items[i].id);
    var li = items[i], l = open.list;
    if (li.offsetTop < l.scrollTop) l.scrollTop = li.offsetTop;
    else if (li.offsetTop + li.offsetHeight > l.scrollTop + l.clientHeight) l.scrollTop = li.offsetTop + li.offsetHeight - l.clientHeight;
  }

  function choose(i) {
    var sel = open.sel, v = sel.options[i].value;
    close(true);
    if (sel.value === v) return;
    sel.value = v;
    sel.dispatchEvent(new Event("input", { bubbles: true }));
    sel.dispatchEvent(new Event("change", { bubbles: true }));
  }

  function show(sel) {
    close(false);
    var box = sel.parentElement;
    var list = document.createElement("ul");
    list.className = "dd" + (sel.name === "model" ? " dd--caps" : "");
    list.id = "dd-" + (++uid);
    list.setAttribute("role", "listbox");
    var count = counter(sel);
    var items = Array.prototype.map.call(sel.options, function (opt, i) {
      var li = document.createElement("li");
      li.className = "dd__opt"; li.id = list.id + "-" + i;
      /* a form's empty first choice is only a prompt — its label already says it */
      if (!opt.value && sel.classList.contains("field__select")) li.hidden = true;
      li.setAttribute("role", "option");
      li.setAttribute("aria-selected", opt.selected ? "true" : "false");
      if (opt.disabled) li.setAttribute("aria-disabled", "true");
      var name = document.createElement("span"); name.className = "dd__name"; name.textContent = opt.textContent;
      li.appendChild(name);
      if (count && opt.value) {
        var n = count(opt.value), c = document.createElement("span");
        c.className = "dd__count"; c.textContent = "/" + n;
        if (!n) li.classList.add("is-none");
        li.appendChild(c);
      }
      li.addEventListener("mousedown", function (e) { e.preventDefault(); });
      li.addEventListener("click", function () { if (!opt.disabled) choose(i); });
      li.addEventListener("mousemove", function () { if (open && open.active !== i) activate(i); });
      return li;
    });
    items.forEach(function (li) { list.appendChild(li); });
    box.appendChild(list);
    box.classList.add("is-open");
    sel.setAttribute("aria-controls", list.id);
    sel.setAttribute("aria-expanded", "true");
    /* a list wider than its field keeps inside the window */
    var r = list.getBoundingClientRect();
    if (r.right > document.documentElement.clientWidth - 8) list.classList.add("dd--end");
    open = { sel: sel, box: box, list: list, items: items, active: 0 };
    activate(Math.max(0, sel.selectedIndex));
  }

  function init() {
    document.querySelectorAll("select.pick__select, select.field__select").forEach(function (sel) {
      sel.setAttribute("aria-haspopup", "listbox");
      sel.setAttribute("aria-expanded", "false");
      sel.addEventListener("mousedown", function (e) {
        if (e.button !== 0) return;
        e.preventDefault();
        if (open && open.sel === sel) close(true); else { sel.focus({ focusVisible: false }); show(sel); }
      });
      sel.addEventListener("keydown", function (e) {
        var isOpen = open && open.sel === sel;
        var k = e.key;
        if (!isOpen) {
          if (k === "ArrowDown" || k === "ArrowUp" || k === "Enter" || k === " " || k === "F4") { e.preventDefault(); show(sel); }
          return;
        }
        if (k === "ArrowDown") { e.preventDefault(); activate(open.active + 1); }
        else if (k === "ArrowUp") { e.preventDefault(); activate(open.active - 1, -1); }
        else if (k === "Home") { e.preventDefault(); activate(0); }
        else if (k === "End") { e.preventDefault(); activate(open.items.length - 1, -1); }
        else if (k === "Enter" || k === " ") { e.preventDefault(); choose(open.active); }
        else if (k === "Escape") { e.preventDefault(); close(true); }
        else if (k === "Tab") close(false);
      });
      sel.addEventListener("blur", function () { setTimeout(function () { if (open && open.sel === sel && document.activeElement !== sel) close(false); }, 0); });
    });
    document.addEventListener("mousedown", function (e) { if (open && !open.box.contains(e.target)) close(false); });
    window.addEventListener("resize", function () { close(false); });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
