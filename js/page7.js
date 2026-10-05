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
      var air = Math.min(48, Math.max(12, box.height * 0.04));
      var y = Math.max(box.height - H, air - ROOF * H);          /* never past the photograph's foot */
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
