// IOS Hannover – Menü, Smooth Scroll, Seitwärts-Abschnitte, Scroll-Effekte.
// Ohne JavaScript bleibt alles lesbar: Seitwärts-Abschnitte sind dann normal waagerecht scrollbar.
(function () {
  "use strict";

  var root = document.documentElement;
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var isHome = !!document.getElementById("start");
  if (isHome) document.body.classList.add("is-home");
  var header = document.querySelector(".site-header");
  var headerH = function () { return header ? header.offsetHeight : 0; };

  // ---------- Smooth Scroll (Lenis) ----------
  var lenis = null;
  if (!reduce && window.Lenis) {
    lenis = new window.Lenis({ lerp: 0.1, wheelMultiplier: 1, smoothWheel: true });
    var raf = function (t) { lenis.raf(t); requestAnimationFrame(raf); };
    requestAnimationFrame(raf);
    root.classList.add("lenis-on");
  }

  var scrollToTarget = function (el, immediate) {
    if (!el) return;
    var y = el.getBoundingClientRect().top + window.scrollY - (el.id === "start" ? 0 : headerH() - 1);
    if (lenis) lenis.scrollTo(Math.max(0, y), { immediate: !!immediate, duration: 1.2 });
    else window.scrollTo({ top: y, behavior: reduce || immediate ? "auto" : "smooth" });
  };

  // Ankerlinks (#… und /#… auf der Startseite) weich ansteuern
  document.addEventListener("click", function (e) {
    var a = e.target.closest("a[href]");
    if (!a) return;
    var href = a.getAttribute("href");
    var hash = href.charAt(0) === "#" ? href : (isHome && href.indexOf("/#") === 0 ? href.slice(1) : null);
    if (!hash || hash === "#") return;
    var target = document.getElementById(hash.slice(1));
    if (!target) return;
    e.preventDefault();
    closeMenu(false);
    scrollToTarget(target);
    history.replaceState(null, "", hash);
  });

  // ---------- Burger-Menü ----------
  var burger = document.querySelector(".burger");
  var menu = document.getElementById("menu");
  var outside = Array.prototype.slice.call(document.querySelectorAll("main, footer, .skip"));
  var open = false;

  function setOpen(next, restoreFocus) {
    if (!menu || next === open) return;
    open = next;
    root.classList.toggle("menu-open", open);
    burger.setAttribute("aria-expanded", String(open));
    burger.querySelector(".burger-label").textContent = open ? "Schließen" : "Menü";
    outside.forEach(function (el) { el.inert = open; });
    if (lenis) { open ? lenis.stop() : lenis.start(); }
    if (open) {
      var first = menu.querySelector("a");
      setTimeout(function () { first && first.focus({ preventScroll: true }); }, 60);
    } else if (restoreFocus) {
      burger.focus({ preventScroll: true });
    }
  }
  function closeMenu(restoreFocus) { setOpen(false, restoreFocus); }

  if (burger && menu) {
    burger.addEventListener("click", function () { setOpen(!open, true); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && open) closeMenu(true);
    });
    // Aktive Station im Menü markieren
    if (isHome && "IntersectionObserver" in window) {
      var links = {};
      menu.querySelectorAll("[data-station]").forEach(function (a) { links[a.dataset.station] = a; });
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (!en.isIntersecting || !links[en.target.id]) return;
          Object.keys(links).forEach(function (k) { links[k].removeAttribute("aria-current"); });
          links[en.target.id].setAttribute("aria-current", "location");
        });
      }, { rootMargin: "-45% 0px -50% 0px" });
      Object.keys(links).forEach(function (id) {
        var sec = document.getElementById(id);
        if (sec) io.observe(sec);
      });
    }
  }

  // ---------- Seitwärts-Abschnitte (vertikal scrollen → waagerecht fahren) ----------
  var hs = Array.prototype.slice.call(document.querySelectorAll(".hscroll"));
  var pinned = !reduce && hs.length > 0;
  var layout = function () {
    hs.forEach(function (sec) {
      var track = sec.querySelector(".hscroll-track");
      var sticky = sec.querySelector(".hscroll-sticky");
      var dist = Math.max(0, track.scrollWidth - sticky.clientWidth);
      sec._dist = dist;
      sec._rest = window.innerHeight * 0.2; // kurze Ruhezone am Anfang und Ende
      sec.style.height = dist + window.innerHeight + 2 * sec._rest + "px";
    });
  };
  if (pinned) {
    root.classList.add("hscroll-on");
    layout();
  }

  // ---------- Bogendraht-Verbinder, Fortschritt, Parallaxe ----------
  var connectors = Array.prototype.slice.call(document.querySelectorAll(".connector path"));
  var bar = document.querySelector(".scroll-progress span");
  var para = document.querySelector("[data-parallax]");
  var clamp = function (v) { return v < 0 ? 0 : v > 1 ? 1 : v; };

  var update = function () {
    var vh = window.innerHeight;
    var sy = window.scrollY;

    if (pinned) {
      hs.forEach(function (sec) {
        var top = sec.getBoundingClientRect().top;
        var p = clamp((-top - sec._rest) / (sec._dist || 1));
        var x = sec.classList.contains("hscroll--left") ? -(1 - p) * sec._dist : -p * sec._dist;
        sec.querySelector(".hscroll-track").style.transform = "translate3d(" + x + "px,0,0)";
        var b = sec.querySelector(".hscroll-bar span");
        if (b) b.style.transform = "scaleX(" + p + ")";
      });
    }

    connectors.forEach(function (path) {
      var r = path.ownerSVGElement.getBoundingClientRect();
      var p = clamp((vh * 0.9 - r.top) / (r.height + vh * 0.4));
      path.style.strokeDashoffset = String(1 - p);
    });

    if (bar) {
      var max = document.documentElement.scrollHeight - vh;
      bar.style.transform = "scaleX(" + (max > 0 ? sy / max : 0) + ")";
    }

    if (para && !reduce && sy < vh * 1.2) {
      para.style.transform = "translate3d(0," + sy * parseFloat(para.dataset.parallax) + "px,0)";
    }
    if (header) header.classList.toggle("is-scrolled", sy > 8);
  };

  var ticking = false;
  var onScroll = function () {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () { ticking = false; update(); });
  };
  if (lenis) lenis.on("scroll", onScroll);
  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", function () {
    if (pinned) layout();
    if (lenis) lenis.resize();
    update();
  });
  update();

  // Direkt aufgerufene Anker (z. B. /#referenten) nach dem Layout korrekt ansteuern
  if (isHome && location.hash.length > 1) {
    var t = document.getElementById(location.hash.slice(1));
    if (t) requestAnimationFrame(function () { scrollToTarget(t, true); });
  }

  // ---------- Einblenden beim Scrollen ----------
  var reveals = document.querySelectorAll(".reveal");
  if (!reduce && "IntersectionObserver" in window && reveals.length) {
    root.classList.add("reveal-on");
    var rio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("is-in"); rio.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -12% 0px" });
    reveals.forEach(function (el) { rio.observe(el); });
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
      if (lenis) lenis.resize();
    };
    input.addEventListener("input", apply);
    apply();
  }
})();
