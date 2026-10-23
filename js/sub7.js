/* Direction 7 inner pages: a row of plates turned by the arrows beside it,
   one plate a press; the spent arrow quieter, never gone (as the home rail). */
(function () {
  document.querySelectorAll(".sub__reviews-frame").forEach(function (frame) {
    var row = frame.querySelector(".sub__review-list");
    var prev = frame.querySelector('[data-dir="-1"]'), next = frame.querySelector('[data-dir="1"]');
    if (!row || !prev || !next) return;
    function step() { var item = row.querySelector("li"); return item ? item.getBoundingClientRect().width + parseFloat(getComputedStyle(row).columnGap || 0) : row.clientWidth; }
    function paint() {
      prev.disabled = row.scrollLeft <= 2;
      next.disabled = row.scrollLeft + row.clientWidth >= row.scrollWidth - 2;
    }
    prev.addEventListener("click", function () { row.scrollBy({ left: -step(), behavior: "smooth" }); });
    next.addEventListener("click", function () { row.scrollBy({ left: step(), behavior: "smooth" }); });
    row.addEventListener("scroll", paint, { passive: true });
    window.addEventListener("resize", paint);
    paint();
  });
})();
