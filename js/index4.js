/* Bentley Palm Beach — home, direction 4.
   No dependencies. Every behaviour here has a complete static equivalent:
   with this file absent the page stands in its finished composition, the
   header keeps its ink, and the wheel scrolls the page as any page. */

(function () {
  "use strict";

  var root = document.documentElement;
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
  var header = document.getElementById("mh");
  var motion = root.classList.contains("motion") && !reduced.matches;
  if (!motion) root.classList.remove("motion");
  else root.classList.add("ready");

  /* --- The stack ------------------------------------------------------------
         Each chapter sticks and the next covers it. A chapter taller than the
         screen sticks with its foot on the fold — measured here, so the copy
         that travels up over a pinned picture is never left below the fold.
         `--cover` is how far the next chapter has risen over this one; the
         stylesheet turns it into the veil and the drift. ---------------------- */
  var chapters = Array.prototype.slice.call(document.querySelectorAll("main > section"));
  var follower = chapters.map(function (el, i) { return chapters[i + 1] || document.querySelector("footer"); });
  var stacked = motion && window.matchMedia("(min-width: 768px)").matches;

  /* the retailer pair: the detail rides onto the showroom by 60% of its own
     height, whatever the column's height came out as */
  var pairStack = document.querySelector(".retailer__stack");
  function measurePair() {
    if (!pairStack) return;
    var showroom = pairStack.querySelector(".retailer__showroom");
    var detail = pairStack.querySelector(".retailer__detail");
    if (!showroom || !detail) return;
    if (window.matchMedia("(max-width: 767px)").matches) {
      detail.style.removeProperty("--detail-top");
      showroom.style.removeProperty("--showroom-w");
      showroom.style.bottom = "";
      return;
    }
    /* the showroom keeps its 4:3 whole — the car is never cropped: as wide
       as 76% of the column's height allows, or 92% of its width */
    /* the pair as one composition: detail 58% wide over a showroom 92% wide,
       riding 60% of itself onto the showroom — sized so the pair fills the
       column's height (down to 4:3 of its width), and set on the column's
       vertical centre, level with the copy */
    var colW = pairStack.clientWidth, colH = pairStack.clientHeight;
    var detW = colW * 0.58;
    var showW = Math.min(colW * 0.92, (colH - detW * 0.4) * 4 / 3);
    var pairH = showW * 0.75 + detW * 0.4;
    var top0 = Math.max(0, (colH - pairH) / 2);
    showroom.style.setProperty("--showroom-w", Math.round(showW) + "px");
    showroom.style.bottom = Math.round(Math.max(0, colH - top0 - pairH)) + "px";
    detail.style.setProperty("--detail-top", Math.round(top0) + "px");
  }

  function measureStack() {
    stacked = motion && window.matchMedia("(min-width: 768px)").matches;
    measurePair();
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
      /* the same number is the next chapter's arrival */
      if (next.tagName === "SECTION") next.style.setProperty("--arrive", cover.toFixed(3));
    }
  }

  /* --- Header: no ground at rest; a frozen ground once the page has moved -- */
  var scrolled = false;
  var painting = false;

  function paintHeader() {
    painting = false;
    paintCover();
    var past = window.scrollY > 24;
    /* the way back appears once the first screen has gone */
    if (window.scrollY > window.innerHeight * 0.9) root.setAttribute("data-past", "");
    else root.removeAttribute("data-past");
    if (past === scrolled) return;
    scrolled = past;
    if (past) header.setAttribute("data-scrolled", "");
    else header.removeAttribute("data-scrolled");
  }
  function requestPaint() {
    if (painting) return;
    painting = true;
    window.requestAnimationFrame(paintHeader);
  }
  window.addEventListener("scroll", requestPaint, { passive: true });
  window.addEventListener("resize", function () { measureStack(); requestPaint(); });
  window.addEventListener("load", function () { measureStack(); requestPaint(); });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { measureStack(); requestPaint(); });
  measureStack();
  paintHeader();

  /* --- Menu (under 1024) ---------------------------------------------------- */
  var toggle = header.querySelector(".mh__toggle");
  function setMenu(open) {
    if (open) header.setAttribute("data-open", "");
    else header.removeAttribute("data-open");
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    document.body.style.overflow = open ? "hidden" : "";
  }
  toggle.addEventListener("click", function () {
    setMenu(!header.hasAttribute("data-open"));
  });
  header.querySelector(".mh__nav").addEventListener("click", function (e) {
    if (e.target.closest("a")) setMenu(false);
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && header.hasAttribute("data-open")) {
      setMenu(false);
      toggle.focus();
    }
  });

  /* --- Reveals: a chapter plays its staircase once its top reaches the
         middle of the screen, and stays revealed. The hero plays on paint. -- */
  var reveals = Array.prototype.slice.call(document.querySelectorAll("[data-reveal]"));

  function markIn(el) { el.classList.add("is-in"); }

  if (!motion || !("IntersectionObserver" in window)) {
    reveals.forEach(markIn);
  } else {
    var hero = document.querySelector(".hero");
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        io.unobserve(entry.target);
        markIn(entry.target);
      });
    /* on a stepping desktop a chapter always lands at the top, so its
       pictures wait until it has nearly landed; a free-scrolling screen
       reveals earlier, so nothing is left blank at a resting position */
    }, { rootMargin: window.matchMedia("(min-width: 1024px) and (pointer: fine)").matches ? "0px 0px -62% 0px" : "0px 0px -45% 0px" });

    reveals.forEach(function (el) {
      if (el === hero) return;
      /* anything already on screen — a restored position, a deep link — is
         shown at once rather than waiting for a scroll that may never come */
      if (el.getBoundingClientRect().top < window.innerHeight * 0.55) markIn(el);
      else io.observe(el);
    });

    if (hero) {
      window.requestAnimationFrame(function () {
        window.requestAnimationFrame(function () { markIn(hero); });
      });
    }

    /* safety net: nothing is ever left hidden by a missed callback */
    window.setTimeout(function () {
      reveals.forEach(function (el) {
        if (el.getBoundingClientRect().top < window.innerHeight) markIn(el);
      });
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

  /* --- Sliders ----------------------------------------------------------------
         One crossfade. The hero turns itself every eight seconds; the visitor's
         own move restarts the clock, hover and focus hold it, reduced motion
         stops it. The pre-owned frame only moves when asked. A film on a slide
         loads when that slide is shown and pauses when it is not. ------------- */
  function film(slide, on) {
    var v = slide.querySelector("video[data-src]");
    if (!v) return;
    if (on) {
      if (!v.src) v.src = v.getAttribute("data-src");
      if (!reduced.matches) { var p = v.play(); if (p && p.catch) p.catch(function () {}); }
    } else if (!v.paused) {
      v.pause();
    }
  }
  function pad(n) { return (n < 10 ? "0" : "") + n; }

  function slider(rootEl, slideSel, arrowSel, nowSel, dwell) {
    var slides = Array.prototype.slice.call(rootEl.querySelectorAll(slideSel));
    if (slides.length < 2) return;
    var current = 0, timer = null, held = false;

    var leaving = null;
    function show(n, dir) {
      n = (n + slides.length) % slides.length;
      if (n === current) return;
      /* the direction the curtain comes from, fixed before the change so the
         transition starts from the right edge */
      rootEl.setAttribute("data-dir", dir < 0 ? "-1" : "1");
      void rootEl.offsetWidth;
      var prev = slides[current];
      slides.forEach(function (el, i) {
        var on = i === n;
        el.classList.toggle("is-active", on);
        el.classList.remove("is-leaving");
        if (on) el.removeAttribute("inert"); else el.setAttribute("inert", "");
        film(el, on);
      });
      prev.classList.add("is-leaving");
      window.clearTimeout(leaving);
      leaving = window.setTimeout(function () { prev.classList.remove("is-leaving"); }, 1600);
      current = n;
      Array.prototype.forEach.call(rootEl.querySelectorAll(nowSel), function (el) { el.textContent = pad(n + 1); });
      restart();
    }
    function restart() {
      window.clearTimeout(timer);
      rootEl.removeAttribute("data-playing");
      if (!dwell || !motion || held) return;
      window.requestAnimationFrame(function () { rootEl.setAttribute("data-playing", ""); });
      timer = window.setTimeout(function () { show(current + 1, 1); }, dwell);
    }
    Array.prototype.forEach.call(rootEl.querySelectorAll(arrowSel), function (b) {
      b.addEventListener("click", function () { show(current + (+b.dataset.dir), +b.dataset.dir); });
    });
    rootEl.addEventListener("keydown", function (e) {
      if (e.key === "ArrowRight") show(current + 1, 1);
      else if (e.key === "ArrowLeft") show(current - 1, -1);
    });
    if (dwell) {
      rootEl.style.setProperty("--hero-dwell", dwell + "ms");
      rootEl.addEventListener("mouseenter", function () { held = true; restart(); });
      rootEl.addEventListener("mouseleave", function () { held = false; restart(); });
      rootEl.addEventListener("focusin", function () { held = true; restart(); });
      rootEl.addEventListener("focusout", function (e) { if (!rootEl.contains(e.relatedTarget)) { held = false; restart(); } });
      document.addEventListener("visibilitychange", function () {
        if (document.hidden) { window.clearTimeout(timer); rootEl.removeAttribute("data-playing"); }
        else restart();
      });
      restart();
    }
  }

  /* --- The standard box ------------------------------------------------------
         Every `.box` on the page is set to the tallest of them, once measured,
         so the offers and the pre-owned plates share one size exactly. On a
         phone the boxes are in flow and keep their own height. -------------- */
  var boxes = Array.prototype.slice.call(document.querySelectorAll(".box"));
  var boxed = window.matchMedia("(min-width: 768px)");
  function equaliseBoxes() {
    boxes.forEach(function (b) { b.style.height = ""; });
    if (!boxed.matches || !boxes.length) return;
    var max = 0;
    boxes.forEach(function (b) { max = Math.max(max, b.getBoundingClientRect().height); });
    boxes.forEach(function (b) { b.style.height = Math.ceil(max) + "px"; });
  }
  equaliseBoxes();
  window.addEventListener("resize", equaliseBoxes);
  window.addEventListener("load", equaliseBoxes);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(equaliseBoxes);

  var heroEl = document.querySelector(".hero");
  if (heroEl) slider(heroEl, ".slide", ".hero__arrow", ".hero__now", 8000);
  Array.prototype.forEach.call(document.querySelectorAll("[data-slider]"), function (el) {
    slider(el, ".po-slide", ".stock__arrow", ".po-now", 0);
  });

  /* --- The inventory rail ---------------------------------------------------
         Scrolls sideways by wheel or touch, drags with the pointer, and the
         arrows move it a screen at a time; each arrow goes quiet at its end. */
  /* --- The rail fits its screen: every chapter ends on the floor, so where
         the cards would run past it the cards are narrowed (a 3:2 frame gets
         shorter as it gets narrower) by exactly the overshoot. -------------- */
  function fitRail() {
    var sec = document.querySelector(".stock");
    if (!sec) return;
    sec.style.removeProperty("--stock-card-w");
    if (!window.matchMedia("(min-width: 1024px)").matches) return;
    var card = sec.querySelector(".stock__car");
    var inner = sec.querySelector(".stock__in");
    if (!card || !inner) return;
    var cs = getComputedStyle(sec);
    var room = sec.clientHeight - parseFloat(cs.paddingTop) - parseFloat(cs.paddingBottom);
    var over = inner.getBoundingClientRect().height - room;
    if (over <= 0) return;
    var w = card.getBoundingClientRect().width - over * 1.5;
    sec.style.setProperty("--stock-card-w", Math.max(208, Math.floor(w)) + "px");
  }
  window.addEventListener("resize", fitRail);
  window.addEventListener("load", fitRail);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitRail);
  fitRail();

  Array.prototype.forEach.call(document.querySelectorAll(".stock"), function (sec) {
    var rail = sec.querySelector(".stock__rail");
    var arrows = Array.prototype.slice.call(sec.querySelectorAll(".stock__arrow"));
    if (!rail) return;
    function settle() {
      var max = rail.scrollWidth - rail.clientWidth - 1;
      arrows.forEach(function (a) {
        var dir = +a.dataset.dir;
        a.disabled = dir < 0 ? rail.scrollLeft <= 0 : rail.scrollLeft >= max;
      });
    }
    arrows.forEach(function (a) {
      a.addEventListener("click", function () {
        var card = rail.querySelector(".stock__car");
        var gap = parseFloat(getComputedStyle(rail).columnGap) || 0;
        var stepW = card ? card.getBoundingClientRect().width + gap : rail.clientWidth * 0.8;
        var n = Math.max(1, Math.floor((rail.clientWidth - 2 * gap) / stepW));
        rail.scrollBy({ left: +a.dataset.dir * stepW * n, behavior: reduced.matches ? "auto" : "smooth" });
      });
    });
    /* drag with a fine pointer; a drag of more than a few pixels is not a click */
    var down = null, moved = false;
    rail.addEventListener("pointerdown", function (e) {
      if (e.pointerType !== "mouse" || e.button !== 0) return;
      down = { x: e.clientX, left: rail.scrollLeft, id: e.pointerId }; moved = false;
    });
    rail.addEventListener("pointermove", function (e) {
      if (!down) return;
      var dx = e.clientX - down.x;
      /* the pointer is captured only once this is a drag: captured on the
         press, a plain click would be delivered to the rail, not the link */
      if (!moved && Math.abs(dx) > 4) { moved = true; rail.classList.add("is-dragging"); rail.setPointerCapture(down.id); }
      if (moved) rail.scrollLeft = down.left - dx;
    });
    function up(e) {
      if (!down) return;
      down = null;
      if (moved) window.setTimeout(function () { rail.classList.remove("is-dragging"); }, 0);
    }
    rail.addEventListener("pointerup", up);
    rail.addEventListener("pointercancel", up);
    rail.addEventListener("click", function (e) { if (moved) { e.preventDefault(); moved = false; } }, true);
    rail.addEventListener("scroll", settle, { passive: true });
    window.addEventListener("resize", settle);
    settle();
  });

  /* --- One gesture, one section --------------------------------------------
         A wheel step takes the page to the next chapter, never into the middle
         of one. Pointer devices at desktop width only; touch scrolls freely.
         Stops: each chapter's top, and the foot of any chapter taller than the
         screen — where a pinned picture has its copy travelled up over it. --- */
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
      /* a chapter only a little taller than the screen has no second beat */
      if (box.height > vh * 1.15) list.push(Math.round(top + box.height - vh));
    });
    var max = root.scrollHeight - vh;
    stops = list
      .map(function (y) { return Math.max(0, Math.min(max, y)); })
      .sort(function (a, b) { return a - b; })
      .filter(function (y, i, arr) { return i === 0 || y - arr[i - 1] > 24; });
  }

  function glideTo(y) {
    var from = window.scrollY;
    var span = y - from;
    if (!span) return;
    var t0 = performance.now();
    var ms = Math.min(1100, Math.max(620, Math.abs(span) * 0.7));
    animating = true;
    (function frame(now) {
      var p = Math.min(1, (now - t0) / ms);
      var e = 1 - Math.pow(1 - p, 3);      /* cubic-out — the page's own curve */
      window.scrollTo({ top: Math.round(from + span * e), behavior: "instant" });
      if (p < 1) window.requestAnimationFrame(frame);
      else { animating = false; lockedUntil = performance.now() + 220; }
    })(t0);
  }

  function step(direction) {
    if (animating || performance.now() < lockedUntil) return true;
    if (!stops.length) readStops();
    var y = window.scrollY;
    var next = null;
    for (var i = 0; i < stops.length; i++) {
      if (direction > 0 && stops[i] > y + 8) { next = stops[i]; break; }
      if (direction < 0 && stops[i] < y - 8) next = stops[i];
    }
    if (next === null) return false;
    glideTo(next);
    return true;
  }

  /* One gesture, one step. A trackpad keeps sending inertia events for a
     second after the fingers have left; every one of them used to be read
     as a new gesture once the glide had ended, and the page ran from the
     hero to the footer on its own. A gesture is now the stream of events
     with no gap longer than `gestureGap` between them: the first event of a
     stream steps, the rest of the stream is swallowed. */
  var gestureGap = 180;
  var lastWheel = 0;
  var gestureUsed = false;

  function onWheel(e) {
    if (!sectioned || !stepping.matches || header.hasAttribute("data-open")) return;
    if (Math.abs(e.deltaX) > Math.abs(e.deltaY)) return;          /* a sideways gesture is the rail's */
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

  /* Back to the top: the page's own glide, not a jump. */
  var totop = document.querySelector(".totop");
  if (totop) totop.addEventListener("click", function (e) {
    e.preventDefault();
    if (reduced.matches || !motion) { window.scrollTo({ top: 0, behavior: "instant" }); return; }
    glideTo(0);
  });

  /* The keyboard keeps its own transport. */
  document.addEventListener("keydown", function (e) {
    if (!sectioned || header.hasAttribute("data-open")) return;
    var tag = (e.target.tagName || "").toLowerCase();
    if (tag === "input" || tag === "textarea" || e.metaKey || e.ctrlKey || e.altKey) return;
    if (e.key === "PageDown") { if (step(1)) e.preventDefault(); }
    else if (e.key === "PageUp") { if (step(-1)) e.preventDefault(); }
  });

})();
