/* Bentley Palm Beach — direction 6: Lenis, the scroll layer of every page.
   Loaded after lenis.min.js (deferred, from jsDelivr) and before the page's
   own script, which finds the instance on `window.lenis`.

   - Not constructed under prefers-reduced-motion: the page scrolls natively.
   - The visitor keeps the transport: anchors, the keyboard and focus
     scrolling; nested scrollers (the rails, the light box) scroll natively.
   - No GSAP on these pages, so Lenis runs its own frame loop (autoRaf).
   - On the home page at desktop width the wheel steps one chapter a gesture
     (js/index6.js): that wheel is the stepping's, not Lenis's, and the glide
     between chapters is a Lenis scrollTo. */
(function () {
  "use strict";
  if (typeof window.Lenis !== "function") return;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  var stepping = window.matchMedia("(min-width: 1024px) and (pointer: fine)");
  var sectioned = document.body && document.body.hasAttribute("data-scroll");

  window.lenis = new window.Lenis({
    autoRaf: true,
    anchors: true,
    allowNestedScroll: true,
    stopInertiaOnNavigate: true,
    /* the home page's stepped wheel is left to the stepping */
    virtualScroll: function (data) {
      return !(sectioned && stepping.matches && data.event && data.event.type === "wheel");
    },
    /* the light box and the open menu scroll on their own */
    prevent: function (node) {
      return node.classList && (node.classList.contains("lightbox") || node.classList.contains("mh__nav"));
    }
  });
})();
