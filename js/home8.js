/* index8.html: the search in the deck sends only what was chosen, so the
   listing opens on a clean address (inventory7.html?model=Bentayga). */
(function () {
  var form = document.querySelector(".hero__find");
  if (!form) return;
  form.addEventListener("submit", function () {
    var sels = form.querySelectorAll("select");
    Array.prototype.forEach.call(sels, function (sel) { sel.disabled = !sel.value; });
    /* back from the listing, the choices are usable again */
    window.setTimeout(function () {
      Array.prototype.forEach.call(sels, function (sel) { sel.disabled = false; });
    }, 0);
  });
})();
