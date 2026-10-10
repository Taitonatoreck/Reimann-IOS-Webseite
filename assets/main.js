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

  var ticking = false;
  var onScroll = function () {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () {
      ticking = false;
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
