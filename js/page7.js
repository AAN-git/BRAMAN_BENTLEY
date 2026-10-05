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
