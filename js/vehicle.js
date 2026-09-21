/* Bentley Palm Beach — the vehicle page.
   The header and the menu as on the home page; the film of photographs
   (drag, arrows, the line beneath, full screen); Save and Share; the small
   screen's bar. With the file absent the page stands complete: the rail
   scrolls as any rail, every photograph is on the page, the offer is there. */

(function () {
  "use strict";

  var root = document.documentElement;
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
  var motion = root.classList.contains("motion") && !reduced.matches;
  if (!motion) root.classList.remove("motion");

  /* --- Header ---------------------------------------------------------------- */
  var header = document.getElementById("mh");
  var scrolled = false, painting = false;
  var bar = document.querySelector(".vdp__bar");
  var figure = document.querySelector(".vdp__figure");
  function paint() {
    painting = false;
    var past = window.scrollY > 24;
    if (window.scrollY > window.innerHeight * 0.9) root.setAttribute("data-past", "");
    else root.removeAttribute("data-past");
    /* the small screen's bar: once the figure has scrolled off, until the enquiry */
    if (bar && figure) {
      var small = window.matchMedia("(max-width: 1023px)").matches;
      var enquire = document.getElementById("enquire");
      var gone = figure.getBoundingClientRect().bottom < 0;
      var reached = enquire && enquire.getBoundingClientRect().top < window.innerHeight * 0.7;
      if (small && gone && !reached) { bar.hidden = false; bar.setAttribute("data-on", ""); }
      else bar.removeAttribute("data-on");
    }
    if (past === scrolled) return;
    scrolled = past;
    if (past) header.setAttribute("data-scrolled", "");
    else header.removeAttribute("data-scrolled");
  }
  function requestPaint() { if (!painting) { painting = true; window.requestAnimationFrame(paint); } }
  window.addEventListener("scroll", requestPaint, { passive: true });
  window.addEventListener("resize", requestPaint);
  paint();

  /* --- Menu (under 1024) ---------------------------------------------------- */
  var toggle = header.querySelector(".mh__toggle");
  function setMenu(open) {
    if (open) header.setAttribute("data-open", "");
    else header.removeAttribute("data-open");
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    document.body.style.overflow = open ? "hidden" : "";
  }
  toggle.addEventListener("click", function () { setMenu(!header.hasAttribute("data-open")); });
  header.querySelector(".mh__nav").addEventListener("click", function (e) { if (e.target.closest("a")) setMenu(false); });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && header.hasAttribute("data-open")) { setMenu(false); toggle.focus(); }
  });

  /* --- Reveals: the name on paint, the film once its pictures are placed,
         the plate and the offer as they come into view ------------------- */
  var reveals = Array.prototype.slice.call(document.querySelectorAll("[data-reveal]"));
  function markIn(el) { el.classList.add("is-in"); }
  if (!motion || !("IntersectionObserver" in window)) {
    reveals.forEach(markIn);
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        io.unobserve(entry.target);
        markIn(entry.target);
      });
    }, { rootMargin: "0px 0px -15% 0px" });
    reveals.forEach(function (el) {
      if (el.classList.contains("vdp__head") || el.classList.contains("film")) return;
      if (el.getBoundingClientRect().top < window.innerHeight * 0.85) markIn(el);
      else io.observe(el);
    });
    window.requestAnimationFrame(function () {
      window.requestAnimationFrame(function () {
        reveals.forEach(function (el) {
          if (el.classList.contains("vdp__head") || el.classList.contains("film")) markIn(el);
        });
      });
    });
    window.setTimeout(function () {
      reveals.forEach(function (el) { if (el.getBoundingClientRect().top < window.innerHeight) markIn(el); });
    }, 3000);
  }
  reduced.addEventListener("change", function (e) {
    if (!e.matches) return;
    motion = false; root.classList.remove("motion"); reveals.forEach(markIn);
  });

  /* --- The film -------------------------------------------------------------- */
  var film = document.querySelector(".film");
  if (film) {
    var rail = film.querySelector(".film__row");
    var frames = Array.prototype.slice.call(rail.querySelectorAll(".film__frame"));
    var sources = JSON.parse(film.getAttribute("data-photos") || "[]");
    var arrows = Array.prototype.slice.call(film.querySelectorAll(".film__nav .stock__arrow"));
    var thumb = film.querySelector(".film__thumb");
    var indexEls = Array.prototype.slice.call(document.querySelectorAll(".film__count [data-index]"));
    function pad(n) { return (n < 10 ? "0" : "") + n; }
    var current = 0;

    function settle() {
      var max = rail.scrollWidth - rail.clientWidth - 1;
      arrows.forEach(function (a) {
        var dir = +a.dataset.dir;
        a.disabled = dir < 0 ? rail.scrollLeft <= 0 : rail.scrollLeft >= max;
      });
      /* the line beneath: the visible share of the rail, where it is */
      var share = Math.min(1, rail.clientWidth / rail.scrollWidth);
      var pos = max > 0 ? rail.scrollLeft / max : 0;
      thumb.style.width = (share * 100) + "%";
      thumb.style.left = (pos * (1 - share) * 100) + "%";
      /* the frame at the rail's left edge is the one counted */
      var left = rail.getBoundingClientRect().left + parseFloat(getComputedStyle(rail).paddingLeft);
      var n = 0;
      frames.forEach(function (f, i) { if (f.getBoundingClientRect().left <= left + 8) n = i; });
      current = n;
      indexEls.forEach(function (el) { el.textContent = pad(n + 1); });
    }
    function scrollToFrame(i, smooth) {
      var f = frames[Math.max(0, Math.min(frames.length - 1, i))];
      if (!f) return;
      var padL = parseFloat(getComputedStyle(rail).paddingLeft) || 0;
      rail.scrollTo({ left: f.offsetLeft - padL, behavior: smooth && !reduced.matches ? "smooth" : "auto" });
    }
    arrows.forEach(function (a) {
      a.addEventListener("click", function () { scrollToFrame(current + (+a.dataset.dir), true); });
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
    function up() {
      if (!down) return;
      down = null;
      if (moved) window.setTimeout(function () { rail.classList.remove("is-dragging"); }, 0);
    }
    rail.addEventListener("pointerup", up);
    rail.addEventListener("pointercancel", up);
    rail.addEventListener("click", function (e) { if (moved) { e.preventDefault(); e.stopPropagation(); moved = false; } }, true);
    rail.addEventListener("scroll", settle, { passive: true });
    window.addEventListener("resize", settle);
    window.addEventListener("load", settle);
    settle();

    /* --- Full screen ------------------------------------------------------- */
    var box = document.querySelector(".lightbox");
    if (box && typeof box.showModal === "function") {
      var img = box.querySelector(".lightbox__image");
      var boxIndex = box.querySelector("[data-index]");
      var shown = 0;
      function show(i) {
        shown = (i + sources.length) % sources.length;
        img.src = sources[shown];
        img.alt = frames[shown] ? frames[shown].querySelector("img").alt : "";
        boxIndex.textContent = pad(shown + 1);
      }
      frames.forEach(function (f, i) {
        f.querySelector(".film__open").addEventListener("click", function () {
          show(i);
          box.showModal();
          document.body.style.overflow = "hidden";
        });
      });
      function close() { box.close(); }
      box.addEventListener("close", function () {
        document.body.style.overflow = "";
        scrollToFrame(shown, false);
        var b = frames[shown] && frames[shown].querySelector(".film__open");
        if (b) b.focus({ preventScroll: true });
      });
      box.querySelector(".lightbox__close").addEventListener("click", close);
      Array.prototype.forEach.call(box.querySelectorAll(".lightbox__arrow"), function (a) {
        a.addEventListener("click", function () { show(shown + (+a.dataset.dir)); });
      });
      box.addEventListener("click", function (e) { if (e.target === box) close(); });
      box.addEventListener("keydown", function (e) {
        if (e.key === "ArrowRight") show(shown + 1);
        if (e.key === "ArrowLeft") show(shown - 1);
      });
      /* a swipe on a touch screen turns the page */
      var tx = null;
      box.addEventListener("touchstart", function (e) { tx = e.touches[0].clientX; }, { passive: true });
      box.addEventListener("touchend", function (e) {
        if (tx === null) return;
        var dx = e.changedTouches[0].clientX - tx; tx = null;
        if (Math.abs(dx) > 40) show(shown + (dx < 0 ? 1 : -1));
      });
    }
  }

  /* --- Save · Share ---------------------------------------------------------- */
  var tools = document.querySelector(".tools");
  if (tools) {
    var stock = tools.getAttribute("data-stock");
    var name = tools.getAttribute("data-name");
    var save = tools.querySelector('[data-tool="save"]');
    var share = tools.querySelector('[data-tool="share"]');
    var KEY = "bentley-palm-beach-saved";
    function saved() { try { return JSON.parse(window.localStorage.getItem(KEY) || "[]"); } catch (e) { return []; } }
    function paintSave() {
      var on = saved().indexOf(stock) !== -1;
      save.setAttribute("aria-pressed", on ? "true" : "false");
      save.querySelector("span").textContent = on ? "Saved" : "Save";
    }
    if (save) {
      paintSave();
      save.addEventListener("click", function () {
        var list = saved();
        var i = list.indexOf(stock);
        if (i === -1) list.push(stock); else list.splice(i, 1);
        try { window.localStorage.setItem(KEY, JSON.stringify(list)); } catch (e) {}
        paintSave();
      });
    }
    if (share) {
      var word = share.querySelector("[data-word]");
      share.addEventListener("click", function () {
        var data = { title: name + " at Bentley Palm Beach", text: name + ", stock " + stock, url: window.location.href };
        if (navigator.share) { navigator.share(data).catch(function () {}); return; }
        if (navigator.clipboard) {
          navigator.clipboard.writeText(window.location.href).then(function () {
            word.textContent = "Link copied";
            window.setTimeout(function () { word.textContent = "Share"; }, 2200);
          });
        }
      });
    }
  }

  /* the enquiry form has no service behind it in this build: it says so */
  var form = document.querySelector(".enquire__form");
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!form.checkValidity()) { form.reportValidity(); return; }
      if (!form.querySelector(".enquire__done")) {
        var p = document.createElement("p");
        p.className = "body enquire__done";
        p.textContent = "Thank you. A specialist will be in touch within one working day, or call 561 926 9111.";
        form.appendChild(p);
      }
    });
  }
})();
