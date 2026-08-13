// Paste into the console on the live page (or a local serve) to re-check the two
// hover bugs the flyer had in Aug 2026. Both came from the same thing: the tilt used to
// live on .flyer, which is the element deciding :hover, so the hit region changed shape
// with the state. Both scans must print 0. See "The tilt does not live on the hover
// target" in the README.
//
// Run it whenever you touch .flyer's transform, its anchoring, --fw-open, the pad inset,
// or the closing timings.
(() => {
  const f = document.getElementById('weekFlyer');
  if (!f) return console.warn('No flyer on this page (it retires itself after the week).');
  if (f.hidden) f.hidden = false;
  const hits = (x, y) => { const e = document.elementFromPoint(x, y); return !!(e && (e === f || f.contains(e))); };
  const settle = () => f.getAnimations({ subtree: true }).forEach(a => { try { a.finish(); } catch (e) {} });
  const styled = (css, fn) => {
    const s = Object.assign(document.createElement('style'), { textContent: css });
    document.head.appendChild(s);
    try { return fn(); } finally { s.remove(); }
  };

  // ---- 1. Does any point hover while closed but miss while open? ----
  // One fixed grid for both states: deriving it per state gives the two scans different
  // parities, and they then can't overlap at all, which reads as a pass or a fail at
  // random. The grid has to cover the open flyer plus a margin.
  const b = f.getBoundingClientRect();
  const X0 = Math.round(b.right) - 420, X1 = Math.round(b.right) + 30;
  const Y0 = Math.round(b.top) - 30, Y1 = Math.round(b.top) + 520;
  const scan = () => {
    const s = new Set();
    for (let x = X0; x <= X1; x++) for (let y = Y0; y <= Y1; y++) if (hits(x, y)) s.add(x + ',' + y);
    return s;
  };
  // :hover can't be turned off from script, so pin the closed state over the top of it.
  const NOHOVER = '.flyer:hover{--fw:var(--fw-roll) !important;}' +
    '.flyer:hover .flyer-btn{transform:rotate(-2.2deg) !important;}' +
    '.flyer:hover .flyer-window,.flyer:hover .flyer-burst{height:var(--roll-h) !important;}';
  f.className = 'flyer'; settle();
  const closed = styled(NOHOVER, scan);
  f.classList.add('is-open'); settle();
  const open = scan();
  f.classList.remove('is-open'); settle();
  const flicker = [...closed].filter(p => !open.has(p));

  // ---- 2. Does the closing tilt sweep back over the cursor you just left with? ----
  // The geometry snaps at 100ms but the tilt runs 260ms, so a full-size box is rotating
  // for the first stretch. Anything it newly covers is a spurious mouseenter, which
  // cancels the pop.
  f.className = 'flyer is-open'; settle();
  const sweepScan = deg => styled('.flyer.is-open .flyer-btn{transform:rotate(' + deg + 'deg) !important;}', () => {
    const s = new Set(), bb = f.getBoundingClientRect();
    for (let x = Math.round(bb.left); x <= Math.round(bb.right); x += 4)
      for (let y = Math.round(bb.bottom) - 10; y <= Math.round(bb.bottom) + 40; y++)
        if (hits(x, y)) s.add(x + ',' + y);
    return s;
  });
  const atOpen = sweepScan(0), midClose = sweepScan(-1.6);
  const swept = [...midClose].filter(p => !atOpen.has(p));
  f.className = 'flyer'; settle();

  console.log('flicker points (hover closed, miss open):', flicker.length, flicker.slice(0, 5));
  console.log('points the closing tilt sweeps back over:', swept.length, swept.slice(0, 5));
  console.log(flicker.length || swept.length ? '❌ the hit region changes shape with the state' : '✅ stable');
})();
