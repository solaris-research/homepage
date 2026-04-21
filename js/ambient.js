/*
 * Ambient cursor glow: a very soft teal/accent radial that follows the cursor
 * inside the hero band. Enhances the "quiet motion" feel. Does nothing on
 * touch devices or when the user prefers reduced motion.
 *
 * The CSS keyframe animation on .hero-band::before handles the baseline
 * breathing; this script layers cursor-reactive warmth on top.
 */
(function () {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  if (window.matchMedia('(hover: none)').matches) return; // skip on touch

  var band = document.querySelector('.hero-band');
  if (!band) return;

  // We add a second layer via an inline element so the CSS ::before stays intact.
  var glow = document.createElement('div');
  glow.className = 'hero-band__cursor-glow';
  glow.setAttribute('aria-hidden', 'true');
  Object.assign(glow.style, {
    position: 'absolute',
    inset: '0',
    pointerEvents: 'none',
    opacity: '0',
    transition: 'opacity 0.6s ease',
    background: 'radial-gradient(180px 180px at 0% 0%, rgba(15, 92, 107, 0.12), transparent 70%)',
    zIndex: '0'
  });
  band.appendChild(glow);

  var rafPending = false;
  var targetX = 0, targetY = 0;
  var currentX = 0, currentY = 0;

  function onMove(ev) {
    var rect = band.getBoundingClientRect();
    targetX = ev.clientX - rect.left;
    targetY = ev.clientY - rect.top;
    if (!rafPending) {
      rafPending = true;
      requestAnimationFrame(tick);
    }
  }

  function tick() {
    // soft easing toward cursor position
    currentX += (targetX - currentX) * 0.18;
    currentY += (targetY - currentY) * 0.18;
    glow.style.background =
      'radial-gradient(200px 200px at ' + currentX + 'px ' + currentY + 'px, rgba(15, 92, 107, 0.14), transparent 70%)';
    if (Math.abs(targetX - currentX) > 0.5 || Math.abs(targetY - currentY) > 0.5) {
      requestAnimationFrame(tick);
    } else {
      rafPending = false;
    }
  }

  band.addEventListener('mouseenter', function () { glow.style.opacity = '1'; });
  band.addEventListener('mouseleave', function () { glow.style.opacity = '0'; });
  band.addEventListener('mousemove', onMove);
})();
