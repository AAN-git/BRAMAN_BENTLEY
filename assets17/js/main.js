/* Bentley of the Potomac — index17.
   Four behaviours: the narrow menu, scroll reveals, scroll-linked parallax on
   the photography, and an enquiry form that validates honestly. No library —
   the page makes no external request, and a CDN would be the wrong trade for
   clip-path masks and a transform on one rAF.

   The hidden state lives behind html.js-motion, which this file adds. Without
   JavaScript, or under prefers-reduced-motion, the page is simply finished. */
(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var reduce = window.matchMedia('(prefers-reduced-motion:reduce)');

  /* ---- narrow menu ------------------------------------------------------ */
  var mh = $('#mh'), burger = $('.burger');
  if (mh && burger) {
    var setOpen = function (open) {
      if (open) mh.setAttribute('data-open', ''); else mh.removeAttribute('data-open');
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    };
    burger.addEventListener('click', function () { setOpen(!mh.hasAttribute('data-open')); });
    $$('#nav a').forEach(function (a) { a.addEventListener('click', function () { setOpen(false); }); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && mh.hasAttribute('data-open')) { setOpen(false); burger.focus(); }
    });
    var mq = window.matchMedia('(min-width:1261px)');   /* follows the stylesheet */
    var onW = function (e) { if (e.matches) setOpen(false); };
    if (mq.addEventListener) mq.addEventListener('change', onW); else mq.addListener(onW);
  }

  if (!reduce.matches) {
    document.documentElement.classList.add('js-motion');

    $$('[data-reveal]').forEach(function (el) {
      var v = el.getAttribute('data-i');
      if (v !== null) el.style.setProperty('--i', v);
    });

    /* ---- the opening ---------------------------------------------------
       Fired on the frame after the fonts settle, so a masked headline never
       reveals one face and settles into another. */
    var openHero = function () {
      requestAnimationFrame(function () {
        requestAnimationFrame(function () {
          var hero = $('.hero');
          if (hero) { hero.classList.add('is-load'); hero.classList.add('is-in'); }
        });
      });
    };
    if (document.fonts && document.fonts.ready) {
      var done = false, go = function () { if (!done) { done = true; openHero(); } };
      document.fonts.ready.then(go);
      window.setTimeout(go, 700);
    } else { openHero(); }

    /* ---- scroll reveals -------------------------------------------------
       One observer for the page. A group commits on a share of ITSELF being
       visible rather than on its top edge crossing the fold: a tall group
       whose content sits far below its own top would otherwise finish off
       screen before anyone had looked at it. */
    var groups = $$('[data-seq]');
    if ('IntersectionObserver' in window) {
      var seen = new WeakSet();
      var commit = function (el) { if (!seen.has(el)) { seen.add(el); el.classList.add('is-in'); } };
      var io = new IntersectionObserver(function (entries, obs) {
        entries.forEach(function (en) {
          if (!en.isIntersecting || seen.has(en.target)) return;
          var r = en.boundingClientRect;
          var tall = r.height > window.innerHeight * 0.8;
          if (en.intersectionRatio < 0.25 && !(tall && r.top < window.innerHeight * 0.5)) return;
          commit(en.target); obs.unobserve(en.target);
        });
      }, { rootMargin: '0px 0px -6% 0px', threshold: [0, 0.25] });
      groups.forEach(function (g) { io.observe(g); });

      /* A refresh partway down, or a deep link, means whole groups were never
         crossed and would never be reported. Anything already ABOVE the fold
         is resolved with the transition switched off — the reader did not see
         it move, so it must not move. */
      window.setTimeout(function () {
        groups.forEach(function (g) {
          if (seen.has(g)) return;
          var r = g.getBoundingClientRect();
          if (r.top < window.innerHeight && r.bottom > 0) { commit(g); io.unobserve(g); }
          else if (r.bottom <= 0) {
            var kids = $$('[data-reveal]', g);
            g.style.transition = 'none';
            kids.forEach(function (e) { e.style.transition = 'none'; });
            commit(g); io.unobserve(g);
            window.setTimeout(function () {
              g.style.transition = '';
              kids.forEach(function (e) { e.style.transition = ''; });
            }, 60);
          }
        });
      }, 350);

      var settle = function (e) {
        if (!e.matches) return;
        io.disconnect();
        groups.forEach(function (g) { g.classList.add('is-in'); });
      };
      if (reduce.addEventListener) reduce.addEventListener('change', settle);
      else reduce.addListener(settle);
    } else {
      groups.forEach(function (g) { g.classList.add('is-in'); });
    }

    /* ---- parallax and the slide-in --------------------------------------
       Scroll-linked, but restrained: the container never moves, only the
       photograph inside its own frame. Travel is expressed as a share of the
       over-scale the CSS already applies, so the image can never expose an
       edge — the arithmetic guarantees it rather than a hopeful magic number.

       One rAF for every layer on the page, positions read in a single pass
       before anything is written, so there is no layout thrash. Elements are
       only tracked while they are on screen. */
    var layers = $$('[data-par]').map(function (el) {
      return { el: el, amt: parseFloat(el.getAttribute('data-par')) || 0.06, on: false };
    });

    if (layers.length) {
      var vh = window.innerHeight, queued = false;

      var draw = function () {
        queued = false;
        /* read every rect first, write afterwards */
        var reads = layers.map(function (L) {
          return L.on ? L.el.parentNode.getBoundingClientRect() : null;
        });
        layers.forEach(function (L, i) {
          var r = reads[i]; if (!r) return;
          /* -1 when the frame is entering at the bottom, +1 when it leaves at
             the top; 0 when it is centred */
          var p = ((r.top + r.height / 2) - vh / 2) / (vh / 2 + r.height / 2);
          p = Math.max(-1, Math.min(1, p));
          L.el.style.transform = 'translate3d(0,' + (p * L.amt * r.height).toFixed(2) + 'px,0) ' +
            'scale(' + (1 + L.amt * 2) + ')';
        });
      };
      var tick = function () { if (!queued) { queued = true; requestAnimationFrame(draw); } };

      if ('IntersectionObserver' in window) {
        var pio = new IntersectionObserver(function (entries) {
          entries.forEach(function (en) {
            var L = layers.filter(function (x) { return x.el === en.target; })[0];
            if (L) L.on = en.isIntersecting;
          });
          tick();
        }, { rootMargin: '20% 0px 20% 0px' });
        layers.forEach(function (L) { pio.observe(L.el); });
      } else {
        layers.forEach(function (L) { L.on = true; });
      }

      window.addEventListener('scroll', tick, { passive: true });
      window.addEventListener('resize', function () { vh = window.innerHeight; tick(); }, { passive: true });
      tick();
    }
  }

  /* ---- the hero carousel ------------------------------------------------
     Three slides, advanced by the arrows and by the arrow keys. It does not
     advance itself: an automatic carousel takes the first screen away from a
     reader who is still reading it, and the counter exists so the reader can
     see there is more rather than be shown it. */
  var frame = $('.hero__frame');
  if (frame) {
    var slides = $$('.hero__slide', frame);
    var bars = $$('.hero__bar span', frame);
    var nEl = $('#hero-n'), tEl = $('#hero-t'), dEl = $('#hero-d'), aEl = $('#hero-a');
    var COPY = [
      ['4.99% APR financing',
       'On 2026 Bentayga models, for up to 72 months. Tier 1 or Tier 2 credit approval required through Bentley Financial Services.',
       'Learn more', '#finance'],
      ['Continental GTC on the floor',
       'New Azure and S specifications at 2801 Okeechobee Boulevard, each one with its build record.',
       'View inventory', '#stock'],
      ['Bentayga, commissioned not selected',
       'Hide, veneer, thread and finish chosen at the desk here and written down before the car is built.',
       'Open a commission', '#contact']
    ];
    var at = 0;
    var show = function (i) {
      at = (i + slides.length) % slides.length;
      slides.forEach(function (s, k) {
        if (k === at) s.setAttribute('data-on', ''); else s.removeAttribute('data-on');
      });
      if (bars[0]) bars[0].style.transform = 'translateX(' + (at * 100) + '%)';
      if (nEl) nEl.textContent = String(at + 1);
      /* the band behind the masthead is the same frame, so it follows */
      var bleed = document.getElementById('hero-bleed');
      var src = slides[at] && slides[at].querySelector('img');
      if (bleed && src) {
        var nextSrc = src.getAttribute('src');
        if (bleed.getAttribute('src') !== nextSrc) {
          var host = bleed.parentNode;
          host.setAttribute('data-changing', '');
          window.setTimeout(function () {
            bleed.setAttribute('src', nextSrc);
            host.removeAttribute('data-changing');
          }, 450);
        }
      }
      var c = COPY[at] || COPY[0];
      if (tEl) tEl.textContent = c[0];
      if (dEl) dEl.textContent = c[1];
      var alEl = document.getElementById('hero-al');
      if (alEl) alEl.textContent = c[2];
      if (aEl) aEl.setAttribute('href', c[3]);
    };
    $$('[data-hero]', frame).forEach(function (btn) {
      btn.addEventListener('click', function () {
        show(at + (btn.getAttribute('data-hero') === 'next' ? 1 : -1));
      });
    });
    frame.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') show(at + 1);
      if (e.key === 'ArrowLeft') show(at - 1);
    });
    show(0);
  }

  /* ---- enquiry ----------------------------------------------------------
     Validation is immediate and never waits on an animation. */
  var form = $('#enq');
  if (form) {
    var status = $('#f-status');
    var say = function (id, msg) {
      var el = $('.form__err[data-for="' + id + '"]');
      if (el) el.textContent = msg || '';
      var f = document.getElementById(id);
      if (f) { if (msg) f.setAttribute('aria-invalid', 'true'); else f.removeAttribute('aria-invalid'); }
    };
    var checks = [
      ['f-name', function (v) { return v.trim().length >= 2 ? '' : 'Please give a name.'; }],
      ['f-tel', function (v) { return v.replace(/\D/g, '').length >= 7 ? '' : 'Please give a telephone number.'; }],
      ['f-mail', function (v) { return (!v || /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v)) ? '' : 'That email does not look complete.'; }]
    ];
    checks.forEach(function (c) {
      var el = document.getElementById(c[0]);
      if (el) el.addEventListener('blur', function () { say(c[0], c[1](el.value)); });
    });
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var bad = null;
      checks.forEach(function (c) {
        var el = document.getElementById(c[0]); if (!el) return;
        var m = c[1](el.value); say(c[0], m);
        if (m && !bad) bad = el;
      });
      if (bad) {
        bad.focus();
        status.className = 'full form__err';
        status.textContent = 'Please correct the fields marked above.';
        return;
      }
      status.className = 'full form__err form__ok';
      status.textContent = 'This is a design study — the form is not connected to a mailbox. ' +
        'Everything you entered is valid and would have been sent.';
    });
  }
})();
