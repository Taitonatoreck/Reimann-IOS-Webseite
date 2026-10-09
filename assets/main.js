// IOS Hannover – kleines Skript ohne Abhängigkeiten.
// Die Seite funktioniert auch ohne JavaScript vollständig.
(function () {
  "use strict";

  // Mobiles Menü
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");
  if (toggle && nav) {
    var setOpen = function (open) {
      nav.classList.toggle("is-open", open);
      toggle.setAttribute("aria-expanded", String(open));
    };
    toggle.addEventListener("click", function (e) {
      e.stopPropagation();
      setOpen(!nav.classList.contains("is-open"));
    });
    document.addEventListener("click", function (e) {
      if (nav.classList.contains("is-open") && !nav.contains(e.target)) setOpen(false);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("is-open")) {
        setOpen(false);
        toggle.focus();
      }
    });
  }

  // Referenten-Suche (sofort, ohne Animation – wird beim Tippen ausgelöst)
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
