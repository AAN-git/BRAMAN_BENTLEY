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
  var mode = "photos", turn = null;
  if (film) {
    film.setAttribute("data-js", "");
    var rail = film.querySelector(".film__row");
    var frames = Array.prototype.slice.call(rail.querySelectorAll(".film__frame"));
    var photoFrames = frames.filter(function (f) { return !f.classList.contains("film__frame--spin"); });
    var sources = JSON.parse(film.getAttribute("data-photos") || "[]");
    var arrows = Array.prototype.slice.call(film.querySelectorAll(".film__arrow"));
    var thumb = film.querySelector(".film__thumb");
    var counter = film.querySelector(".film__count");
    var indexEls = Array.prototype.slice.call(document.querySelectorAll(".film__count [data-index]"));
    function pad(n) { return (n < 10 ? "0" : "") + n; }
    var current = 0;

    function settle() {
      if (mode === "spin") return;
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
      /* the frame at the rail's left edge is the one counted; the 360 tile counts as itself */
      var left = rail.getBoundingClientRect().left + parseFloat(getComputedStyle(rail).paddingLeft);
      var n = 0;
      frames.forEach(function (f, i) { if (f.getBoundingClientRect().left <= left + 8) n = i; });
      current = n;
      var f = frames[n];
      var onTile = f && f.classList.contains("film__frame--spin");
      indexEls.forEach(function (el) { el.textContent = onTile ? "360°" : pad(photoFrames.indexOf(f) + 1); });
      var total = counter && counter.querySelector(".film__total");
      if (total) total.hidden = onTile;
    }
    function scrollToFrame(i, smooth) {
      var f = frames[Math.max(0, Math.min(frames.length - 1, i))];
      if (!f) return;
      var padL = parseFloat(getComputedStyle(rail).paddingLeft) || 0;
      rail.scrollTo({ left: f.offsetLeft - padL, behavior: smooth && !reduced.matches ? "smooth" : "auto" });
    }
    arrows.forEach(function (a) {
      a.addEventListener("click", function () {
        if (mode === "spin") { if (turn) turn(+a.dataset.dir); return; }
        scrollToFrame(current + (+a.dataset.dir), true);
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
    function up() {
      if (!down) return;
      down = null;
      if (moved) window.setTimeout(function () { rail.classList.remove("is-dragging"); }, 0);
    }
    rail.addEventListener("pointerup", up);
    rail.addEventListener("pointercancel", up);
    rail.addEventListener("click", function (e) { if (moved) { e.preventDefault(); e.stopPropagation(); moved = false; } }, true);
    /* the arrows show while the rail is moving sideways — a drag, a wheel,
       a throw, a click — and fade once it has stood still */
    var movingUntil = 0;
    var moving = function () {
      film.setAttribute("data-scrolling", "");
      window.clearTimeout(movingUntil);
      movingUntil = window.setTimeout(function () { film.removeAttribute("data-scrolling"); }, 900);
    };
    rail.addEventListener("scroll", function () { moving(); settle(); }, { passive: true });
    window.addEventListener("resize", settle);
    window.addEventListener("load", settle);
    settle();

    /* keyboard on the film */
    film.addEventListener("keydown", function (e) {
      if (box && box.open) return;
      if (e.key === "ArrowRight") { if (mode === "spin" && turn) turn(1); else scrollToFrame(current + 1, true); e.preventDefault(); }
      else if (e.key === "ArrowLeft") { if (mode === "spin" && turn) turn(-1); else scrollToFrame(current - 1, true); e.preventDefault(); }
    });

    /* --- Full screen ------------------------------------------------------- */
    var box = document.querySelector(".lightbox");
    if (box && typeof box.showModal === "function") {
      var img = box.querySelector(".lightbox__image");
      var boxIndex = box.querySelector("[data-index]");
      var shown = 0;
      var show = function (i) {
        shown = (i + sources.length) % sources.length;
        img.src = sources[shown];
        img.alt = photoFrames[shown] ? photoFrames[shown].querySelector("img").alt : "";
        boxIndex.textContent = pad(shown + 1);
      };
      photoFrames.forEach(function (f, i) {
        f.querySelector(".film__open").addEventListener("click", function () {
          show(i);
          box.showModal();
          document.body.style.overflow = "hidden";
        });
      });
      var close = function () { box.close(); };
      box.addEventListener("close", function () {
        document.body.style.overflow = "";
        scrollToFrame(frames.indexOf(photoFrames[shown]), false);
        var b = photoFrames[shown] && photoFrames[shown].querySelector(".film__open");
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

    /* --- 360°: the turntable ---------------------------------------------
           Twenty-four frames of the retailer's turntable, fetched when the
           view is first opened. It turns once by itself; then a drag turns
           it (one stage width is one full turn), a throw keeps it turning
           and slows, the arrows and the keyboard step it a frame, a sideways
           wheel turns it too. Under reduced motion it stands, and turns only
           under the hand. ------------------------------------------------- */
    var spinFrames = [];
    try { spinFrames = JSON.parse(film.getAttribute("data-spin") || "[]"); } catch (e) { spinFrames = []; }
    var spin = film.querySelector(".spin");
    var modes = Array.prototype.slice.call(film.querySelectorAll(".film__mode-button"));
    var note = film.querySelector(".film__note");
    var track = film.querySelector(".film__track");

    if (spin && spinFrames.length > 1) {
      var stage = spin.querySelector(".spin__stage");
      var picture = spin.querySelector(".spin__image");
      var loading = spin.querySelector(".spin__loading");
      var loadBar = loading ? loading.querySelector("span") : null;
      var n = spinFrames.length;
      var angle = 0;                      /* in frames, fractional */
      var loaded = 0, ready = false, cache = [];
      var velocity = 0, raf = 0, auto = false;

      var paintFrame = function () {
        var i = ((Math.round(angle) % n) + n) % n;
        var src = spinFrames[i];
        if (picture.getAttribute("src") !== src) picture.src = src;
      };
      var fetchAll = function (done) {
        if (ready) { done(); return; }
        if (loading) loading.hidden = false;
        spinFrames.forEach(function (src, i) {
          var im = new Image();
          im.onload = im.onerror = function () {
            loaded += 1;
            if (loadBar) loadBar.style.width = (loaded / n * 100) + "%";
            if (loaded === n) { ready = true; if (loading) loading.hidden = true; done(); }
          };
          im.src = src; cache[i] = im;
        });
      };
      var tick = function () {
        raf = 0;
        if (auto) { angle += 0.05; paintFrame(); raf = window.requestAnimationFrame(tick); return; }
        if (Math.abs(velocity) > 0.002) {
          angle += velocity; velocity *= 0.94; paintFrame(); moving();
          raf = window.requestAnimationFrame(tick);
        } else velocity = 0;
      };
      var stopAuto = function () { auto = false; stage.setAttribute("data-touched", ""); };
      var start = function () {
        fetchAll(function () {
          if (!reduced.matches && !stage.hasAttribute("data-touched")) {
            auto = true;
            if (!raf) raf = window.requestAnimationFrame(tick);
            window.setTimeout(function () { auto = false; }, 8000);
          }
        });
      };

      var hold = null;
      stage.addEventListener("pointerdown", function (e) {
        if (e.button !== 0) return;
        stopAuto(); velocity = 0;
        hold = { x: e.clientX, a: angle, t: performance.now(), v: 0, id: e.pointerId };
        stage.setAttribute("data-dragging", "");
        stage.setPointerCapture(e.pointerId);
      });
      stage.addEventListener("pointermove", function (e) {
        if (!hold) return;
        var per = stage.clientWidth / n;                 /* one stage width is one turn */
        var next = hold.a - (e.clientX - hold.x) / per;
        var now = performance.now();
        hold.v = (next - angle) / Math.max(1, now - hold.t) * 16;   /* frames per tick */
        hold.t = now; angle = next; paintFrame(); moving();
      });
      var letGo = function () {
        if (!hold) return;
        velocity = Math.max(-1.2, Math.min(1.2, hold.v));
        hold = null;
        stage.removeAttribute("data-dragging");
        if (!raf && !reduced.matches) raf = window.requestAnimationFrame(tick);
      };
      stage.addEventListener("pointerup", letGo);
      stage.addEventListener("pointercancel", letGo);
      stage.addEventListener("wheel", function (e) {
        if (Math.abs(e.deltaX) <= Math.abs(e.deltaY)) return;   /* sideways only */
        stopAuto(); angle += e.deltaX / 40; paintFrame(); moving(); e.preventDefault();
      }, { passive: false });

      var setMode = function (next) {
        mode = next;
        var spinning = mode === "spin";
        rail.hidden = spinning; spin.hidden = !spinning;
        film.removeAttribute("data-scrolling");
        modes.forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.mode === mode ? "true" : "false"); });
        if (track) track.style.visibility = spinning ? "hidden" : "";
        if (counter) counter.style.visibility = spinning ? "hidden" : "";
        if (note) note.style.visibility = spinning ? "hidden" : "";
        arrows.forEach(function (a) {
          a.disabled = false;
          a.setAttribute("aria-label", spinning ? (+a.dataset.dir < 0 ? "Turn the car left" : "Turn the car right") : (+a.dataset.dir < 0 ? "Previous photograph" : "Next photograph"));
        });
        if (spinning) { start(); stage.focus({ preventScroll: true }); }
        else { auto = false; velocity = 0; settle(); }
      };
      modes.forEach(function (b) { b.addEventListener("click", function () { setMode(b.dataset.mode); }); });
      var launch = film.querySelector(".film__launch");
      if (launch) launch.addEventListener("click", function () { setMode("spin"); });
      turn = function (dir) { stopAuto(); velocity = 0; angle = Math.round(angle) + dir; paintFrame(); moving(); };
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
