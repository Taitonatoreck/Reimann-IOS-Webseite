// IOS Hannover – Menü und Referenten-Suche. Gescrollt wird nativ.
(function () {
  "use strict";

  var root = document.documentElement;

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
