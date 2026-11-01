// Screenshot a post exactly as the site renders it, in readable slices.
// Usage: node .claude/skills/review-draft/shots.js <site-root> <url-path> <out-dir> [width]
// e.g.   node shots.js _site posts/2026-11-01-slug/ _preview/slug 430
// KATEX_DIR=<dir with katex.min.js, katex.min.css, fonts/> serves KaTeX locally when the CDN is blocked.
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const [root, urlPath, outDir, widthArg] = process.argv.slice(2);
const width = Number(widthArg || 430);          // phone width by default
const sliceH = Math.round(width * 2.1);         // one screen-and-a-bit per image
const types = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.svg': 'image/svg+xml',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.json': 'application/json', '.woff2': 'font/woff2', '.woff': 'font/woff' };
const server = http.createServer((req, res) => {
  let p = path.join(root, decodeURIComponent(req.url.split('?')[0]));
  if (fs.existsSync(p) && fs.statSync(p).isDirectory()) p = path.join(p, 'index.html');
  if (!fs.existsSync(p)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': types[path.extname(p)] || 'application/octet-stream' });
  fs.createReadStream(p).pipe(res);
}).listen(0, async () => {
  const port = server.address().port;
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width, height: sliceH }, deviceScaleFactor: 2 });
  const katex = process.env.KATEX_DIR;
  if (katex) await page.route(/cdn\.jsdelivr\.net\/npm\/katex@[^/]+\/dist\/(.*)$/, (route) => {
    const rel = route.request().url().match(/\/dist\/(.*)$/)[1].split('?')[0];
    const f = path.join(katex, rel);
    if (!fs.existsSync(f)) return route.fulfill({ status: 404 });
    route.fulfill({ status: 200, body: fs.readFileSync(f), contentType: types[path.extname(f)] || 'font/ttf' });
  });
  await page.goto(`http://localhost:${port}/${urlPath}`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1500);               // let KaTeX and fonts settle
  const total = await page.evaluate(() => document.documentElement.scrollHeight);
  fs.mkdirSync(outDir, { recursive: true });
  for (const f of fs.readdirSync(outDir)) if (/^page-\d+\.png$/.test(f)) fs.unlinkSync(path.join(outDir, f));
  // Cut between blocks (paragraphs, figures, tables, callouts) so no figure is split in two.
  const edges = await page.evaluate(() => {
    const ys = new Set([0, document.documentElement.scrollHeight]);
    const blocks = document.querySelectorAll(
      'header, #title-block-header > *, main > *, main section > *, .callout, figure, .quarto-figure, table, .katex-display, footer');
    for (const el of blocks) {
      const r = el.getBoundingClientRect();
      if (r.height > 0) { ys.add(Math.round(r.top + scrollY)); ys.add(Math.round(r.bottom + scrollY)); }
    }
    return [...ys].sort((a, b) => a - b);
  });
  const inside = await page.evaluate(() => [...document.querySelectorAll('figure, .quarto-figure, table, .callout, .katex-display')]
    .map(e => { const r = e.getBoundingClientRect(); return [Math.round(r.top + scrollY), Math.round(r.bottom + scrollY)]; }));
  const headEnds = await page.evaluate(() => [...document.querySelectorAll('main h2, main h3, main h4')]
    .map(e => Math.round(e.getBoundingClientRect().bottom + scrollY)));
  // Never cut through a figure, a table or a callout, nor right below a heading.
  const splits = (y) => inside.some(([a, b]) => a < y && y < b) || headEnds.some(h => Math.abs(h - y) < 60);
  let n = 0, y = 0;
  while (y < total) {
    let end = Math.min(y + sliceH, total);
    if (end < total) {
      const ok = edges.filter(e => e > y + sliceH * 0.4 && e <= y + sliceH && !splits(e));
      if (ok.length) end = ok[ok.length - 1];
    }
    const file = path.join(outDir, `page-${String(++n).padStart(2, '0')}.png`);
    await page.screenshot({ path: file, fullPage: true, clip: { x: 0, y, width, height: end - y } });
    console.log(file);
    y = end;
  }
  await browser.close(); server.close();
});
