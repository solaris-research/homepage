/*
 * Scroll-reveal: fades in elements with class "reveal" as they enter the viewport.
 * Per-element delay can be set via inline style --d (e.g. style="--d:120ms").
 * Respects prefers-reduced-motion via CSS; this script only adds the class.
 */
(function () {
  var blocks = document.querySelectorAll('.reveal');
  if (!blocks.length) return;

  // Fallback for very old browsers: just show everything.
  if (typeof IntersectionObserver === 'undefined') {
    blocks.forEach(function (b) { b.classList.add('reveal--in'); });
    return;
  }

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) {
        e.target.classList.add('reveal--in');
        io.unobserve(e.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

  blocks.forEach(function (b) { io.observe(b); });
})();
