// Screenshots of the rendered site for a design check (site-design skill).
// Usage: (cd _site && python3 -m http.server 8765 &) ; node .claude/skills/site-design/shots.js <out-dir> [path ...]
// Default paths: home and archive, in English and French. Each is shot at desktop (1400 px) and
// phone (390 px) width, in light and dark mode. Prints page errors (external font failures are ignored).
const { chromium } = require('playwright');
const [,, out = '.', ...given] = process.argv;
const paths = given.length ? given : ['/', '/archive.html', '/fr/', '/fr/archive.html'];
(async () => {
  const b = await chromium.launch();
  for (const path of paths) for (const [w, tag] of [[1400, 'desktop'], [390, 'phone']]) for (const scheme of ['light', 'dark']) {
    const p = await b.newPage({ viewport: { width: w, height: 900 }, colorScheme: scheme });
    const errs = [];
    p.on('pageerror', e => errs.push(e.message));
    p.on('console', m => m.type() === 'error' && !/ERR_TUNNEL|ERR_NAME|fonts/.test(m.text()) && errs.push(m.text()));
    await p.goto('http://localhost:8765' + path, { waitUntil: 'networkidle' });
    if (scheme === 'dark') await p.evaluate(() => { if (document.body.classList.contains('quarto-light') && window.quartoToggleColorScheme) window.quartoToggleColorScheme(); });
    await p.waitForTimeout(300);
    const name = `${out}/${(path.replace(/\W+/g, '_').replace(/^_|_$/g, '') || 'home')}-${tag}-${scheme}.png`;
    await p.screenshot({ path: name, fullPage: true });
    console.log(name, errs.length ? 'ERRORS ' + JSON.stringify(errs) : 'ok');
    await p.close();
  }
  await b.close();
})();
