// IOS Hannover – Menü, weiches Ansteuern von Ankern, Seitwärts-Abschnitte, Scroll-Effekte.
// Gescrollt wird immer nativ (kein Abfangen des Mausrads). Ohne JavaScript bleibt alles lesbar.
(function () {
  "use strict";

  var root = document.documentElement;
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var isHome = !!document.getElementById("start");
  if (isHome) document.body.classList.add("is-home");
  var header = document.querySelector(".site-header");
  var headerH = function () { return header ? header.offsetHeight : 0; };

  var scrollToTarget = function (el) {
    if (!el) return;
    var y = el.getBoundingClientRect().top + window.scrollY - (el.id === "start" ? 0 : headerH() - 1);
    window.scrollTo({ top: Math.max(0, y), behavior: reduce ? "auto" : "smooth" });
  };

  // ---------- Burger-Menü ----------
  var burger = document.querySelector(".burger");
  var menu = document.getElementById("menu");
  var outside = Array.prototype.slice.call(document.querySelectorAll("main, footer, .skip, .header-actions .social"));
  var open = false;

  function setOpen(next, restoreFocus) {
    if (!menu || !burger || next === open) return;
    open = next;
    root.classList.toggle("menu-open", open);
    burger.setAttribute("aria-expanded", String(open));
    burger.querySelector(".burger-label").textContent = open ? "Schließen" : "Menü";
    outside.forEach(function (el) { el.inert = open; });
    if (open) {
      var first = menu.querySelector("a");
      setTimeout(function () { if (first) first.focus({ preventScroll: true }); }, 60);
    } else if (restoreFocus) {
      burger.focus({ preventScroll: true });
    }
  }

  if (burger && menu) {
    burger.addEventListener("click", function () { setOpen(!open, true); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && open) setOpen(false, true);
    });
  }

  // Ankerlinks (#… und auf der Startseite /#…) weich ansteuern
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a[href]");
    if (!a) return;
    var href = a.getAttribute("href");
    var hash = href.charAt(0) === "#" ? href : (isHome && href.indexOf("/#") === 0 ? href.slice(1) : null);
    if (!hash || hash.length < 2) return;
    var target = document.getElementById(hash.slice(1));
    if (!target) return;
    e.preventDefault();
    var wasOpen = open;
    setOpen(false, false);
    // Nach dem Schließen des Menüs kurz warten, damit die Seite wieder scrollbar ist
    setTimeout(function () { scrollToTarget(target); }, wasOpen ? 30 : 0);
    try { history.replaceState(null, "", hash); } catch (err) { /* z. B. in eingebetteten Ansichten */ }
  });

  // Aktive Station im Menü markieren
  if (isHome && menu && "IntersectionObserver" in window) {
    var links = {};
    Array.prototype.forEach.call(menu.querySelectorAll("[data-station]"), function (a) { links[a.getAttribute("data-station")] = a; });
    var sio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting || !links[en.target.id]) return;
        Object.keys(links).forEach(function (k) { links[k].removeAttribute("aria-current"); });
        links[en.target.id].setAttribute("aria-current", "location");
      });
    }, { rootMargin: "-45% 0px -50% 0px" });
    Object.keys(links).forEach(function (id) {
      var sec = document.getElementById(id);
      if (sec) sio.observe(sec);
    });
  }

  // ---------- Seitwärts-Abschnitte ----------
  // Ab Tablet-Breite bleibt der Abschnitt stehen und der Inhalt fährt beim Scrollen seitwärts.
  // Auf dem Handy (und bei reduzierter Bewegung) sind es normale Wisch-Streifen.
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
      sec._stickyH = sticky.offsetHeight;
      sec._rest = Math.round(sec._stickyH * 0.15); // kurze Ruhezone am Anfang und Ende
      sec.style.height = sec._dist + sec._stickyH + 2 * sec._rest + "px";
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
  setPinned();

  // ---------- Bogendraht-Verbinder, Fortschritt, Parallaxe ----------
  var connectors = Array.prototype.slice.call(document.querySelectorAll(".connector path"));
  var bar = document.querySelector(".scroll-progress span");
  var para = document.querySelector(".hero-media img");
  var clamp = function (v) { return v < 0 ? 0 : v > 1 ? 1 : v; };

  var update = function () {
    var vh = window.innerHeight;
    var sy = window.scrollY;

    if (pinned) {
      hs.forEach(function (sec) {
        var top = sec.getBoundingClientRect().top;
        var p = sec._dist ? clamp((-top - sec._rest) / sec._dist) : 0;
        var x = sec.classList.contains("hscroll--left") ? -(1 - p) * sec._dist : -p * sec._dist;
        sec.querySelector(".hscroll-track").style.transform = "translate3d(" + x.toFixed(1) + "px,0,0)";
        var b = sec.querySelector(".hscroll-bar span");
        if (b) b.style.transform = "scaleX(" + p.toFixed(3) + ")";
      });
    }

    connectors.forEach(function (path) {
      var r = path.ownerSVGElement.getBoundingClientRect();
      var p = clamp((vh * 0.9 - r.top) / (r.height + vh * 0.4));
      path.style.strokeDashoffset = String(1 - p);
    });

    if (bar) {
      var max = document.documentElement.scrollHeight - vh;
      bar.style.transform = "scaleX(" + (max > 0 ? sy / max : 0).toFixed(4) + ")";
    }

    if (para && !reduce && sy < vh * 1.2) {
      para.style.transform = "translate3d(0," + (sy * 0.18).toFixed(1) + "px,0) scale(1.06)";
    }
    if (header) header.classList.toggle("is-scrolled", sy > 8);
  };

  var ticking = false;
  window.addEventListener("scroll", function () {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () { ticking = false; update(); });
  }, { passive: true });

  // Nur bei echter Breitenänderung neu messen – nicht, wenn auf dem Handy die Adressleiste ein-/ausfährt
  var resizeTimer;
  window.addEventListener("resize", function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () {
      if (window.innerWidth !== lastWidth) setPinned();
      update();
    }, 120);
  });
  // Nach dem Laden von Schrift und Bildern einmal genau messen
  var remeasure = function () { if (pinned) measure(); update(); };
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(remeasure);
  window.addEventListener("load", remeasure);
  update();

  // Direkt aufgerufene Anker (z. B. /#referenten) nach dem Messen korrekt ansteuern
  if (isHome && location.hash.length > 1) {
    var t = document.getElementById(location.hash.slice(1));
    if (t) window.addEventListener("load", function () {
      var y = t.getBoundingClientRect().top + window.scrollY - headerH() + 1;
      window.scrollTo(0, Math.max(0, y));
    });
  }

  // ---------- Einblenden beim Scrollen ----------
  var reveals = document.querySelectorAll(".reveal");
  if (!reduce && "IntersectionObserver" in window && reveals.length) {
    root.classList.add("reveal-on");
    var rio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("is-in"); rio.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px" });
    Array.prototype.forEach.call(reveals, function (el) { rio.observe(el); });
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
