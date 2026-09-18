/* Bentley retailer — home.
   No dependencies. Everything degrades: without JS the page is complete, the
   nav is a list, the band is solid and nothing is hidden. */

(function () {
  "use strict";

  var root = document.documentElement;
  root.classList.add("js");

  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
  var band = document.getElementById("band");

  /* --- The sticky mass, published so anchors can clear it ---------------- */
  function measureBand() {
    // The document's real width, so full-bleed media meets the edge exactly
    // instead of running 8px under the scrollbar.
    root.style.setProperty("--vw", root.clientWidth + "px");
    if (!band) return;
    root.style.setProperty("--header-h", Math.round(band.getBoundingClientRect().height) + "px");
  }
  measureBand();
  window.addEventListener("resize", measureBand);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(measureBand);

  /* --- Ground: transparent over the cinematic field, solid after -------- */
  var hero = document.querySelector(".hero");
  if (band && hero && "IntersectionObserver" in window) {
    var watch;
    var arm = function () {
      if (watch) watch.disconnect();
      var h = band.getBoundingClientRect().height;
      watch = new IntersectionObserver(function (e) {
        if (e[0].isIntersecting) band.removeAttribute("data-solid");
        else band.setAttribute("data-solid", "");
      }, { rootMargin: "-" + Math.round(h) + "px 0px 0px 0px" });
      watch.observe(hero);
    };
    arm();
    window.addEventListener("resize", arm);
  } else if (band) {
    band.setAttribute("data-solid", "");
  }

  /* --- Section arrival. One movement, once, downward. -------------------- */
  var risers = document.querySelectorAll(".rise, .reveal");
  var reveal = function (el) { el.setAttribute("data-in", ""); };

  if (reduced.matches || !("IntersectionObserver" in window)) {
    risers.forEach(reveal);
  } else {
    var seen = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        reveal(e.target);
        seen.unobserve(e.target);
      });
    }, { rootMargin: "0px 0px -10% 0px", threshold: 0.05 });

    risers.forEach(function (el) {
      // Anything already at or above the fold is shown at once, so a deep link,
      // a restored scroll position or a fast scroll never leaves a gap.
      if (el.getBoundingClientRect().top < window.innerHeight) reveal(el);
      else seen.observe(el);
    });

    // Safety net: content is never left hidden by a missed callback.
    window.setTimeout(function () {
      risers.forEach(function (el) {
        if (el.getBoundingClientRect().top < window.innerHeight * 1.2) reveal(el);
      });
    }, 2500);
  }

  /* --- Menu -------------------------------------------------------------- */
  var toggle = document.querySelector(".band__toggle");
  if (toggle && band) {
    toggle.addEventListener("click", function () {
      var open = band.hasAttribute("data-open");
      if (open) band.removeAttribute("data-open");
      else band.setAttribute("data-open", "");
      toggle.setAttribute("aria-expanded", String(!open));
      measureBand();
    });
    document.querySelectorAll(".nav a").forEach(function (a) {
      a.addEventListener("click", function () {
        band.removeAttribute("data-open");
        toggle.setAttribute("aria-expanded", "false");
        measureBand();
      });
    });
  }

  /* --- The hero: manual only, nothing advances while anyone is reading -- */
  var frames = document.getElementById("heroFrames");
  if (frames) {
    var slides = Array.prototype.slice.call(frames.children);
    var slots = Array.prototype.slice.call(document.querySelectorAll(".hero__slot"));
    var ticks = Array.prototype.slice.call(document.querySelectorAll(".hero__track i"));
    var bleed = document.getElementById("heroBleed");
    var idx = document.getElementById("heroIndex");
    var at = 0;

    function show(n) {
      at = (n + slides.length) % slides.length;
      slides.forEach(function (el, i) { el.toggleAttribute("data-current", i === at); });
      slots.forEach(function (el, i) { el.toggleAttribute("data-current", i === at); });
      ticks.forEach(function (el, i) { el.toggleAttribute("data-on", i === at); });
      if (idx) idx.textContent = String(at + 1);
      // the bleed is swapped behind a short fade, so it does not cut
      // underneath the dissolve happening in front of it
      if (bleed) {
        var next = slides[at].querySelector("img").getAttribute("src");
        if (bleed.getAttribute("src") !== next) {
          var host = bleed.parentNode;
          host.setAttribute("data-changing", "");
          window.setTimeout(function () {
            bleed.setAttribute("src", next);
            host.removeAttribute("data-changing");
          }, 450);
        }
      }
    }

    document.querySelectorAll("[data-hero]").forEach(function (b) {
      b.addEventListener("click", function () {
        show(at + (b.getAttribute("data-hero") === "next" ? 1 : -1));
      });
    });
    /* The Bentayga opens the hero. The markup already ships in that state —
       current frame, current slot, tick and counter — so this only hands the
       same index to the script; nothing repaints and slide 1 never flashes. */
    show(1);
  }

  /* --- The rail --------------------------------------------------------
     Wheel, drag, buttons, keyboard and snapping. Nothing auto-advances, and
     vertical page scrolling is never trapped. */
  var rail = document.getElementById("rail");
  if (rail) {
    var items = Array.prototype.slice.call(rail.children);
    var idxOut = document.getElementById("railIndex");
    var nameOut = document.getElementById("railName");
    var prev = document.querySelector('[data-rail="prev"]');
    var next = document.querySelector('[data-rail="next"]');
    var ease = function () { return reduced.matches ? "auto" : "smooth"; };

    var step = function () {
      var a = items[0].getBoundingClientRect().width;
      var b = items[1] ? items[1].getBoundingClientRect().left - items[0].getBoundingClientRect().left : a;
      return Math.round(b || a);
    };

    var pad = function (n) { return (n < 10 ? "0" : "") + n; };

    function sync() {
      var left = rail.scrollLeft;
      var max = rail.scrollWidth - rail.clientWidth;
      var railRect = rail.getBoundingClientRect();
      var padL = parseFloat(getComputedStyle(rail).paddingInlineStart) || 0;
      var anchor = railRect.left + padL;
      var at = 0, best = Infinity;
      items.forEach(function (el, i) {
        var d = Math.abs(el.getBoundingClientRect().left - anchor);
        if (d < best) { best = d; at = i; }
      });
      // At the far end the last model is the one being offered, not the one
      // that happens to sit against the leading edge.
      if (left >= max - 2) at = items.length - 1;
      if (idxOut) idxOut.textContent = pad(at + 1);
      if (nameOut) {
        var n = items[at].querySelector(".model__name");
        if (n) nameOut.textContent = n.textContent;
      }
      if (prev) prev.disabled = left <= 1;
      if (next) next.disabled = left >= max - 1;
    }

    rail.addEventListener("scroll", function () {
      window.clearTimeout(rail._t);
      rail._t = window.setTimeout(sync, 90);
    });

    if (prev) prev.addEventListener("click", function () { rail.scrollBy({ left: -step(), behavior: ease() }); });
    if (next) next.addEventListener("click", function () { rail.scrollBy({ left: step(), behavior: ease() }); });

    // Trackpad and wheel translate horizontally over the strip, but a plain
    // vertical wheel at either end still scrolls the page.
    rail.addEventListener("wheel", function (e) {
      var horizontal = Math.abs(e.deltaX) > Math.abs(e.deltaY);
      var delta = horizontal ? e.deltaX : e.deltaY;
      var max = rail.scrollWidth - rail.clientWidth;
      var atEnd = (delta > 0 && rail.scrollLeft >= max - 1) || (delta < 0 && rail.scrollLeft <= 1);
      if (atEnd) return;                       // hand the gesture back to the page
      e.preventDefault();
      rail.scrollLeft += delta;
    }, { passive: false });

    // Click and drag.
    var down = false, startX = 0, startLeft = 0, moved = 0;
    rail.addEventListener("pointerdown", function (e) {
      if (e.pointerType === "touch") return;   // native swipe handles touch
      down = true; moved = 0;
      startX = e.clientX; startLeft = rail.scrollLeft;
      rail.setAttribute("data-dragging", "");
      rail.setPointerCapture(e.pointerId);
    });
    rail.addEventListener("pointermove", function (e) {
      if (!down) return;
      var dx = e.clientX - startX;
      moved = Math.max(moved, Math.abs(dx));
      rail.scrollLeft = startLeft - dx;
    });
    var release = function (e) {
      if (!down) return;
      down = false;
      rail.removeAttribute("data-dragging");
      if (moved > 6) {                          // a drag must not follow the link
        var block = function (ev) { ev.preventDefault(); ev.stopPropagation(); };
        rail.addEventListener("click", block, { capture: true, once: true });
      }
      sync();
    };
    rail.addEventListener("pointerup", release);
    rail.addEventListener("pointercancel", release);

    rail.setAttribute("tabindex", "0");
    rail.addEventListener("keydown", function (e) {
      if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
      e.preventDefault();
      rail.scrollBy({ left: e.key === "ArrowRight" ? step() : -step(), behavior: ease() });
    });

    sync();
    window.addEventListener("resize", sync);
  }
})();
