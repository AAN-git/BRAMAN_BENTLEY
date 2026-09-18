/* Bentley Palm Beach — the presentation of the four directions.
   The same transport as index4: chapters stack, one gesture is one chapter,
   copy arrives as the staircase. No dependencies; with this file absent the
   page is simply the finished composition, read by ordinary scrolling. */

(function () {
  "use strict";

  var root = document.documentElement;
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
  var motion = root.classList.contains("motion") && !reduced.matches;
  if (!motion) root.classList.remove("motion");
  else root.classList.add("ready");

  /* --- The stack ------------------------------------------------------------ */
  var chapters = Array.prototype.slice.call(document.querySelectorAll("main > section"));
  var follower = chapters.map(function (el, i) { return chapters[i + 1] || document.querySelector("footer"); });
  var stacked = motion && window.matchMedia("(min-width: 1024px)").matches;

  function measureStack() {
    stacked = motion && window.matchMedia("(min-width: 1024px)").matches;
    var vh = window.innerHeight;
    chapters.forEach(function (el, i) {
      el.style.setProperty("--stick", stacked ? Math.min(0, vh - el.offsetHeight) + "px" : "0px");
      if (i === 0) el.style.setProperty("--arrive", "1");
    });
  }

  function paintCover() {
    if (!stacked) return;
    var vh = window.innerHeight;
    for (var i = 0; i < chapters.length; i++) {
      var next = follower[i];
      if (!next) continue;
      var top = next.getBoundingClientRect().top;
      var cover = top >= vh ? 0 : top <= 0 ? 1 : 1 - top / vh;
      chapters[i].style.setProperty("--cover", cover.toFixed(3));
      if (next.tagName === "SECTION") next.style.setProperty("--arrive", cover.toFixed(3));
    }
  }

  var painting = false;
  function paint() {
    painting = false;
    paintCover();
    if (window.scrollY > window.innerHeight * 0.9) root.setAttribute("data-past", "");
    else root.removeAttribute("data-past");
    var bar = document.querySelector(".deck__bar");
    if (bar) bar.setAttribute("data-scrolled", window.scrollY > 24 ? "" : null);
    if (bar && window.scrollY <= 24) bar.removeAttribute("data-scrolled");
    /* the running folio: which chapter is on screen */
    var folio = document.querySelector(".deck__now");
    if (folio) {
      var n = 0;
      for (var j = 0; j < chapters.length; j++) if (chapters[j].getBoundingClientRect().top <= window.innerHeight * 0.5) n = j;
      folio.textContent = (n < 9 ? "0" : "") + (n + 1);
    }
  }
  function requestPaint() { if (!painting) { painting = true; window.requestAnimationFrame(paint); } }
  window.addEventListener("scroll", requestPaint, { passive: true });
  window.addEventListener("resize", function () { measureStack(); requestPaint(); });
  window.addEventListener("load", function () { measureStack(); requestPaint(); });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { measureStack(); requestPaint(); });
  measureStack();
  paint();

  /* --- Reveals ---------------------------------------------------------------- */
  var reveals = Array.prototype.slice.call(document.querySelectorAll("[data-reveal]"));
  function markIn(el) { el.classList.add("is-in"); }

  if (!motion || !("IntersectionObserver" in window)) {
    reveals.forEach(markIn);
  } else {
    var first = chapters[0];
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        io.unobserve(entry.target);
        markIn(entry.target);
      });
    }, { rootMargin: window.matchMedia("(min-width: 1024px) and (pointer: fine)").matches ? "0px 0px -62% 0px" : "0px 0px -45% 0px" });
    reveals.forEach(function (el) {
      if (el === first) return;
      if (el.getBoundingClientRect().top < window.innerHeight * 0.55) markIn(el);
      else io.observe(el);
    });
    if (first) window.requestAnimationFrame(function () { window.requestAnimationFrame(function () { markIn(first); }); });
    window.setTimeout(function () {
      reveals.forEach(function (el) { if (el.getBoundingClientRect().top < window.innerHeight) markIn(el); });
    }, 3000);
  }

  reduced.addEventListener("change", function (e) {
    if (!e.matches) return;
    motion = false;
    root.classList.remove("motion");
    root.classList.remove("ready");
    reveals.forEach(markIn);
    measureStack();
  });

  /* --- One gesture, one chapter ----------------------------------------------- */
  var stepping = window.matchMedia("(min-width: 1024px) and (pointer: fine)");
  var sectioned = document.body.hasAttribute("data-scroll") && motion;
  var stops = [];
  var animating = false;
  var lockedUntil = 0;

  function readStops() {
    var vh = window.innerHeight;
    var list = [];
    Array.prototype.forEach.call(document.querySelectorAll("main > section, footer"), function (el) {
      var box = el.getBoundingClientRect();
      var top = Math.round(box.top + window.scrollY);
      list.push(top);
      if (box.height > vh * 1.15) list.push(Math.round(top + box.height - vh));
    });
    var max = root.scrollHeight - vh;
    stops = list.map(function (y) { return Math.max(0, Math.min(max, y)); })
      .sort(function (a, b) { return a - b; })
      .filter(function (y, i, arr) { return i === 0 || y - arr[i - 1] > 24; });
  }

  function glideTo(y) {
    var from = window.scrollY, span = y - from;
    if (!span) return;
    var t0 = performance.now();
    var ms = Math.min(1100, Math.max(620, Math.abs(span) * 0.7));
    animating = true;
    (function frame(now) {
      var p = Math.min(1, (now - t0) / ms);
      var e = 1 - Math.pow(1 - p, 3);
      window.scrollTo({ top: Math.round(from + span * e), behavior: "instant" });
      if (p < 1) window.requestAnimationFrame(frame);
      else { animating = false; lockedUntil = performance.now() + 220; }
    })(t0);
  }

  function step(direction) {
    if (animating || performance.now() < lockedUntil) return true;
    if (!stops.length) readStops();
    var y = window.scrollY, next = null;
    for (var i = 0; i < stops.length; i++) {
      if (direction > 0 && stops[i] > y + 8) { next = stops[i]; break; }
      if (direction < 0 && stops[i] < y - 8) next = stops[i];
    }
    if (next === null) return false;
    glideTo(next);
    return true;
  }

  var gestureGap = 180, lastWheel = 0, gestureUsed = false;
  function onWheel(e) {
    if (!sectioned || !stepping.matches) return;
    if (Math.abs(e.deltaX) > Math.abs(e.deltaY)) return;
    var now = performance.now();
    var sameGesture = now - lastWheel < gestureGap;
    lastWheel = now;
    e.preventDefault();
    if (sameGesture && gestureUsed) return;
    if (!sameGesture) gestureUsed = false;
    if (Math.abs(e.deltaY) < 4) return;
    if (animating || now < lockedUntil) { gestureUsed = true; return; }
    gestureUsed = true;
    step(e.deltaY > 0 ? 1 : -1);
  }
  window.addEventListener("wheel", onWheel, { passive: false });
  window.addEventListener("resize", function () { stops = []; });
  window.addEventListener("load", readStops);
  readStops();

  document.addEventListener("keydown", function (e) {
    var tag = (e.target.tagName || "").toLowerCase();
    if (tag === "input" || tag === "textarea" || e.metaKey || e.ctrlKey || e.altKey) return;
    if (!sectioned) return;
    if (e.key === "PageDown" || e.key === "ArrowRight" || e.key === " ") { if (step(1)) e.preventDefault(); }
    else if (e.key === "PageUp" || e.key === "ArrowLeft") { if (step(-1)) e.preventDefault(); }
  });

  /* --- The devices ------------------------------------------------------------
         Each direction's screen and phone hold the page itself in a frame.
         The frames load when the chapter is one screen away, and the deck
         scrolls them slowly while the chapter is on screen — down at a
         reading pace, a pause, back up, a pause — so the page's own motion
         plays inside the device. The pointer turns the devices a few
         degrees. Pointer devices at desktop width only; elsewhere the still
         of the first screen stands. ------------------------------------------- */
  var live = motion && window.matchMedia("(min-width: 1024px) and (pointer: fine)").matches;
  var dirs = Array.prototype.slice.call(document.querySelectorAll(".dir"));

  function frameOf(device) { return device.querySelector("iframe"); }

  /* the page inside a device is laid out at its real size — 1440 on the
     screen, 390 on the phone — and scaled to the pane; the factor comes from
     the pane's measured width, on load and on every resize */
  function zoomDevices() {
    Array.prototype.forEach.call(document.querySelectorAll(".device"), function (d) {
      var f = frameOf(d);
      if (!f) return;
      var natural = d.classList.contains("phone") ? 390 : 1440;
      var w = d.clientWidth;
      if (w > 0) d.style.setProperty("--zoom", (w / natural).toFixed(4));
    });
  }
  zoomDevices();
  window.addEventListener("resize", zoomDevices);
  window.addEventListener("load", zoomDevices);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(zoomDevices);

  function loadFrames(sec) {
    Array.prototype.forEach.call(sec.querySelectorAll(".device iframe[data-src]"), function (f) {
      f.src = f.getAttribute("data-src");
      f.removeAttribute("data-src");
      f.addEventListener("load", function () {
        f.closest(".device").classList.add("is-live");
      }, { once: true });
    });
  }

  function scroller(device) {
    var f = frameOf(device);
    var running = false, raf = 0, y = 0, dir = 1, holdUntil = 0, last = 0;
    var downSpeed = device.classList.contains("phone") ? 120 : 190;   /* px per second — a brisk read */
    var upSpeed = 1400;
    function tick(now) {
      if (!running) return;
      raf = window.requestAnimationFrame(tick);
      var win = f.contentWindow, doc = f.contentDocument;
      if (!win || !doc || !doc.documentElement) return;
      var max = doc.documentElement.scrollHeight - win.innerHeight;
      if (max <= 0) return;
      var dt = last ? Math.min(0.05, (now - last) / 1000) : 0;
      last = now;
      if (now < holdUntil) return;
      y += (dir > 0 ? downSpeed : -upSpeed) * dt;
      if (y >= max) { y = max; dir = -1; holdUntil = now + 1400; }
      else if (y <= 0) { y = 0; dir = 1; holdUntil = now + 1800; }
      win.scrollTo({ top: y, behavior: "instant" });
    }
    return {
      start: function () { if (running) return; running = true; last = 0; holdUntil = performance.now() + 1200; raf = window.requestAnimationFrame(tick); },
      stop: function () { running = false; window.cancelAnimationFrame(raf); }
    };
  }

  if (live && "IntersectionObserver" in window) {
    var scrollers = new Map();
    dirs.forEach(function (sec) {
      Array.prototype.forEach.call(sec.querySelectorAll(".device"), function (d) { scrollers.set(d, scroller(d)); });
    });
    /* load one screen ahead */
    var loader = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { loadFrames(e.target); loader.unobserve(e.target); } });
    }, { rootMargin: "100% 0px 100% 0px" });
    dirs.forEach(function (sec) { loader.observe(sec); });
    /* run while the chapter is the one on screen */
    var runner = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        Array.prototype.forEach.call(e.target.querySelectorAll(".device"), function (d) {
          var s = scrollers.get(d);
          if (e.intersectionRatio > 0.5) s.start(); else s.stop();
        });
        if (e.intersectionRatio > 0.5) window.setTimeout(function () { e.target.classList.add("is-settled"); }, 2200);
      });
    }, { threshold: [0, 0.5, 1] });
    dirs.forEach(function (sec) { runner.observe(sec); });

    /* the pointer turns the devices — a few degrees, eased by the stylesheet */
    dirs.forEach(function (sec) {
      var stage = sec.querySelector(".stage");
      if (!stage) return;
      sec.addEventListener("pointermove", function (e) {
        if (!sec.classList.contains("is-settled")) return;
        var r = stage.getBoundingClientRect();
        var px = (e.clientX - r.left) / r.width - 0.5, py = (e.clientY - r.top) / r.height - 0.5;
        stage.style.setProperty("--ry", (px * 3).toFixed(2) + "deg");
        stage.style.setProperty("--rx", (-py * 2).toFixed(2) + "deg");
      });
      sec.addEventListener("pointerleave", function () { stage.style.setProperty("--ry", "0deg"); stage.style.setProperty("--rx", "0deg"); });
    });
  }

  /* the arrows in the running bar, and the way back to the top */
  Array.prototype.forEach.call(document.querySelectorAll("[data-step]"), function (b) {
    b.addEventListener("click", function () { if (!stops.length) readStops(); step(+b.dataset.step); });
  });
  var totop = document.querySelector(".totop");
  if (totop) totop.addEventListener("click", function (e) {
    e.preventDefault();
    if (reduced.matches || !motion) { window.scrollTo({ top: 0, behavior: "instant" }); return; }
    glideTo(0);
  });

})();
