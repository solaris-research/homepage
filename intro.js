(function () {
  var intro = document.getElementById("intro");
  var body = document.body;
  if (!intro) return;

  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    intro.classList.add("intro--skip");
    intro.setAttribute("aria-hidden", "true");
    return;
  }

  body.classList.add("intro-active");

  // Logo fades in at 0.2s, tagline at 0.7s — both done by ~1.5s
  var doneMs = 1500;
  var holdMs = 600;
  var exitMs = 1000;

  window.setTimeout(function () {
    intro.classList.add("intro--exit");
    body.classList.remove("intro-active");
    window.setTimeout(function () {
      intro.setAttribute("aria-hidden", "true");
    }, exitMs);
  }, doneMs + holdMs);
})();
