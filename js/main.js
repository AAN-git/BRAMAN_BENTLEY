/* Bentley Palm Beach — home.
   No dependencies. Every behaviour here has a complete static equivalent:
   with JS off, the first frame stands, the nav is a list, the header is solid. */

(function () {
  "use strict";

  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* --- The lit field ----------------------------------------------------- */
  var frames = document.getElementById("heroFrames");
  var ticks = document.getElementById("heroTicks");
  var count = document.getElementById("heroCount");

  if (frames && ticks) {
    var items = Array.prototype.slice.call(frames.children);
    var at = 0;
    var timer = null;
    var HOLD = 8000;

    items.forEach(function (_, i) {
      var t = document.createElement("button");
      t.type = "button";
      t.setAttribute("role", "tab");
      t.setAttribute("aria-label", "Motor car " + (i + 1));
      t.setAttribute("aria-current", i === 0 ? "true" : "false");
      t.addEventListener("click", function () { go(i); hold(); });
      ticks.appendChild(t);
    });

    function pad(n) { return (n < 10 ? "0" : "") + n; }

    function go(next) {
      at = (next + items.length) % items.length;
      items.forEach(function (el, i) {
        if (i === at) el.setAttribute("data-current", "");
        else el.removeAttribute("data-current");
      });
      Array.prototype.forEach.call(ticks.children, function (t, i) {
        t.setAttribute("aria-current", i === at ? "true" : "false");
      });
      if (count) count.textContent = pad(at + 1) + " / " + pad(items.length);
    }

    function hold() {
      if (timer) clearInterval(timer);
      if (!reduced) timer = setInterval(function () { go(at + 1); }, HOLD);
    }

    document.querySelectorAll("[data-step]").forEach(function (b) {
      b.addEventListener("click", function () {
        go(at + (b.getAttribute("data-step") === "next" ? 1 : -1));
        hold();
      });
    });

    var hero = frames.closest(".hero");
    hero.addEventListener("mouseenter", function () { if (timer) clearInterval(timer); });
    hero.addEventListener("mouseleave", hold);
    hero.addEventListener("focusin", function () { if (timer) clearInterval(timer); });

    go(0);
    hold();
  }

  /* --- Menu ---------------------------------------------------------------
     The identification band has a ground of its own, so it needs no scroll
     state and no script. */
  var masthead = document.getElementById("masthead");
  var toggle = document.querySelector(".masthead__toggle");
  if (toggle && masthead) {
    toggle.addEventListener("click", function () {
      var open = masthead.hasAttribute("data-open");
      masthead.toggleAttribute("data-open", !open);
      toggle.setAttribute("aria-expanded", String(!open));
    });
  }

  /* --- Arrival ------------------------------------------------------------
     One movement, once, downward. Copy rises the last few pixels into place;
     photographs are uncovered from the bottom edge of their own frame and
     settle the last few per cent, so the picture arrives through the
     composition rather than fading on top of it.

     The marks are applied here rather than written into the markup: without
     script there is nothing to undo, and the page is complete as it stands. */
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  document.documentElement.classList.add('js');

  var RISE = [
    '.field__open > *',
    '.range__item',
    '.layer__type > *',
    '.ledger__item',
    '.about-us__body article',
    '.record > div > *',
    '.plate',
    '.close__inner > *'
  ];
  var SLIDE = [
    '.layer__front',
    '.layer__plate',
    '.about-us__frame',
    '.pair__media',
    '.range__item'
  ];

  function mark(selectors, attr) {
    selectors.forEach(function (sel) {
      var group = 0, last = null;
      document.querySelectorAll(sel).forEach(function (el) {
        if (el.parentNode !== last) { last = el.parentNode; group = 0; }
        el.setAttribute(attr, '');
        // a staircase, capped: past the sixth step a stagger reads as lag
        el.style.setProperty('--d', Math.min(group, 5) * 0.11 + 's');
        group += 1;
      });
    });
  }
  mark(RISE, 'data-rise');
  mark(SLIDE, 'data-slide');

  var arriving = document.querySelectorAll('[data-rise], [data-slide]');
  var land = function (el) { el.setAttribute('data-in', ''); };

  if (reduced.matches || !('IntersectionObserver' in window)) {
    arriving.forEach(land);
  } else {
    var watch = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        land(e.target);
        watch.unobserve(e.target);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.04 });

    arriving.forEach(function (el) {
      // anything already on the first screen is shown at once, so a deep link
      // or a restored scroll position never leaves a hole
      if (el.getBoundingClientRect().top < window.innerHeight) land(el);
      else watch.observe(el);
    });

    // and nothing is ever left hidden by a callback that did not fire
    window.setTimeout(function () {
      arriving.forEach(function (el) {
        if (el.getBoundingClientRect().top < window.innerHeight * 1.25) land(el);
      });
    }, 2500);
  }

})();
