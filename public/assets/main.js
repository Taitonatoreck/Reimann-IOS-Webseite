// IOS Hannover – Menü und Referenten-Suche. Gescrollt wird nativ.
(function () {
  "use strict";

  var root = document.documentElement;
  if (document.getElementById("start")) document.body.classList.add("is-home");

  // ---------- Menü ----------
  var burger = document.querySelector(".burger");
  var menu = document.getElementById("menu");
  var open = false;

  function setOpen(next, restoreFocus) {
    if (!burger || !menu || next === open) return;
    open = next;
    root.classList.toggle("menu-open", open);
    burger.setAttribute("aria-expanded", String(open));
    burger.querySelector(".burger-label").textContent = open ? "Schließen" : "Menü";
    if (!open && restoreFocus) burger.focus({ preventScroll: true });
  }

  if (burger && menu) {
    burger.addEventListener("click", function (e) {
      e.stopPropagation();
      setOpen(!open, false);
    });
    document.addEventListener("click", function (e) {
      if (open && !menu.contains(e.target)) setOpen(false, false);
    });
    menu.addEventListener("click", function (e) {
      if (e.target.closest("a")) setOpen(false, false);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && open) setOpen(false, true);
    });
  }

  // ---------- Scroll-Effekte (natives Scrollen, nichts wird festgehalten) ----------
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var header = document.querySelector(".site-header");
  var heroImg = document.querySelector(".hero-media img");

  // Seitwärts-Abschnitt: ab Tablet-Breite fährt die Zeitleiste beim Runterscrollen seitwärts.
  // Höhe wird nur bei echter Breitenänderung neu gemessen (nicht beim Ein-/Ausfahren der Adressleiste).
  var hs = Array.prototype.slice.call(document.querySelectorAll(".hscroll"));
  var wide = window.matchMedia("(min-width: 48rem)");
  var pinned = false;
  var lastWidth = 0;
  var measure = function () {
    hs.forEach(function (sec) {
      var track = sec.querySelector(".hscroll-track");
      var sticky = sec.querySelector(".hscroll-sticky");
      track.style.transform = "";
      sec._dist = Math.max(0, track.scrollWidth - sticky.clientWidth);
      sec._rest = Math.round(sticky.offsetHeight * 0.15); // kurze Ruhezone am Anfang und Ende
      sec.style.height = sec._dist + sticky.offsetHeight + 2 * sec._rest + "px";
    });
  };
  var setPinned = function () {
    var next = !reduce && wide.matches && hs.length > 0;
    if (next !== pinned) {
      pinned = next;
      root.classList.toggle("hscroll-on", pinned);
      if (!pinned) hs.forEach(function (sec) {
        sec.style.height = "";
        sec.querySelector(".hscroll-track").style.transform = "";
      });
    }
    if (pinned) measure();
    lastWidth = window.innerWidth;
  };
  var moveTracks = function () {
    if (!pinned) return;
    hs.forEach(function (sec) {
      var top = sec.getBoundingClientRect().top;
      var p = sec._dist ? Math.min(1, Math.max(0, (-top - sec._rest) / sec._dist)) : 0;
      sec.querySelector(".hscroll-track").style.transform = "translate3d(" + (-p * sec._dist).toFixed(1) + "px,0,0)";
      var bar = sec.querySelector(".hscroll-bar span");
      if (bar) bar.style.transform = "scaleX(" + p.toFixed(3) + ")";
    });
  };
  setPinned();
  var resizeTimer;
  window.addEventListener("resize", function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () {
      if (window.innerWidth !== lastWidth) setPinned();
      moveTracks();
    }, 120);
  });
  var remeasure = function () { if (pinned) { measure(); moveTracks(); } };
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(remeasure);
  window.addEventListener("load", remeasure);

  // Geschichte als Bogen: zeichnet sich beim Scrollen von 2000 bis 2026
  var arcs = Array.prototype.slice.call(document.querySelectorAll(".arc-story")).map(function (sec) {
    var line = sec.querySelector(".arc-line");
    return {
      sec: sec, line: line, dot: sec.querySelector(".arc-dot"),
      year: sec.querySelector(".arc-year"), count: sec.querySelector(".arc-count b"),
      len: line ? line.getTotalLength() : 0
    };
  });
  var moveArcs = function () {
    if (reduce) { arcs.forEach(function (a) { a.sec.classList.add("is-done"); }); return; }
    arcs.forEach(function (a) {
      var r = a.sec.getBoundingClientRect();
      var span = a.sec.offsetHeight - window.innerHeight;
      // erst ab 10 % starten, bei 85 % fertig – kurze Ruhezonen am Anfang und Ende
      var raw = span > 0 ? -r.top / span : 0;
      var p = Math.min(1, Math.max(0, (raw - 0.1) / 0.75));
      a.line.style.strokeDashoffset = String(1 - p);
      if (a.dot && a.len) {
        var pt = a.line.getPointAtLength(p * a.len);
        a.dot.setAttribute("cx", pt.x.toFixed(1));
        a.dot.setAttribute("cy", pt.y.toFixed(1));
      }
      if (a.year) a.year.textContent = String(Math.round(2000 + 26 * p));
      if (a.count) a.count.textContent = String(Math.round(1 + 29 * p));
      a.sec.classList.toggle("is-done", p >= 0.999);
    });
  };

  var ticking = false;
  var onScroll = function () {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () {
      ticking = false;
      moveTracks();
      moveArcs();
      var y = window.scrollY;
      if (header) header.classList.toggle("is-scrolled", y > 24);
      if (heroImg && !reduce && y < window.innerHeight * 1.2) {
        heroImg.style.transform = "translate3d(0," + (y * 0.2).toFixed(1) + "px,0) scale(1.08)";
      }
    });
  };
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  if (!reduce && "IntersectionObserver" in window) {
    // Inhalte gleiten beim Erreichen sanft herein (einmalig)
    var reveals = document.querySelectorAll(".reveal");
    if (reveals.length) {
      root.classList.add("reveal-on");
      var rio = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) { en.target.classList.add("is-in"); rio.unobserve(en.target); }
        });
      }, { rootMargin: "0px 0px -8% 0px" });
      Array.prototype.forEach.call(reveals, function (el) { rio.observe(el); });
    }

    // Zahlen zählen einmal hoch, wenn sie sichtbar werden
    var counters = document.querySelectorAll("[data-count]");
    var countUp = function (el) {
      var end = parseInt(el.getAttribute("data-count"), 10);
      var suffix = el.getAttribute("data-suffix") || "";
      var start = end >= 1000 ? end - 30 : 0;
      var t0 = null;
      var step = function (t) {
        if (t0 === null) t0 = t;
        var p = Math.min(1, (t - t0) / 1400);
        var eased = 1 - Math.pow(1 - p, 4);
        el.textContent = Math.round(start + (end - start) * eased) + (p === 1 ? suffix : "");
        if (p < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    };
    if (counters.length) {
      var cio = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) { countUp(en.target); cio.unobserve(en.target); }
        });
      }, { threshold: 0.6 });
      Array.prototype.forEach.call(counters, function (el) { cio.observe(el); });
    }
  }

  // ---------- Referenten-Suche (sofort, ohne Animation) ----------
  var input = document.getElementById("speaker-filter");
  if (input) {
    var items = Array.prototype.slice.call(document.querySelectorAll("[data-person]"));
    var groups = Array.prototype.slice.call(document.querySelectorAll(".letter-group"));
    var count = document.getElementById("speaker-count");
    var norm = function (s) {
      return s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
    };
    items.forEach(function (li) { li._text = norm(li.textContent); });
    var apply = function () {
      var q = norm(input.value.trim());
      var shown = 0;
      items.forEach(function (li) {
        var hit = !q || li._text.indexOf(q) !== -1;
        li.hidden = !hit;
        if (hit) shown++;
      });
      groups.forEach(function (g) {
        g.hidden = !g.querySelector("[data-person]:not([hidden])");
      });
      if (count) count.textContent = shown + (shown === 1 ? " Referent" : " Referenten");
    };
    input.addEventListener("input", apply);
    apply();
  }
})();
