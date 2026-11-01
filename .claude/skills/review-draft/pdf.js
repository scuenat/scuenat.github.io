// Print a post as ONE PDF document that looks exactly like the site on screen.
// Usage: node .claude/skills/review-draft/pdf.js <site-root> <url-path> <out.pdf> [width]
// KATEX_DIR=<dir with katex.min.js, katex.min.css, fonts/> serves KaTeX locally when the CDN is blocked.
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const [root, urlPath, outFile, widthArg] = process.argv.slice(2);
const width = Number(widthArg || 430);            // phone width: text stays large when the PDF fits a phone screen
const pageH = Math.round(width * 1.9);            // one phone screen per PDF page
const types = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.svg': 'image/svg+xml',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.json': 'application/json', '.woff2': 'font/woff2', '.woff': 'font/woff',
  '.ttf': 'font/ttf' };
const server = http.createServer((req, res) => {
  let p = path.join(root, decodeURIComponent(req.url.split('?')[0]));
  if (fs.existsSync(p) && fs.statSync(p).isDirectory()) p = path.join(p, 'index.html');
  if (!fs.existsSync(p)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': types[path.extname(p)] || 'application/octet-stream' });
  fs.createReadStream(p).pipe(res);
}).listen(0, async () => {
  const port = server.address().port;
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width, height: pageH } });
  const katex = process.env.KATEX_DIR;
  if (katex) await page.route(/cdn\.jsdelivr\.net\/npm\/katex@[^/]+\/dist\/(.*)$/, (route) => {
    const rel = route.request().url().match(/\/dist\/(.*)$/)[1].split('?')[0];
    const f = path.join(katex, rel);
    if (!fs.existsSync(f)) return route.fulfill({ status: 404 });
    route.fulfill({ status: 200, body: fs.readFileSync(f), contentType: types[path.extname(f)] || 'font/ttf' });
  });
  await page.goto(`http://localhost:${port}/${urlPath}`, { waitUntil: 'networkidle' });
  await page.emulateMedia({ media: 'screen' });    // the on-screen look, not the print stylesheet
  await page.addStyleTag({ content: `
    html, body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    #quarto-header, .headroom { position: static !important; transform: none !important; }
    body { padding-top: 0 !important; }
    figure, .quarto-figure, table, .callout, .katex-display, .read-next, pre, blockquote { break-inside: avoid; }
    h1, h2, h3, h4 { break-after: avoid; }
    p { orphans: 3; widows: 3; }
    /* A PDF cannot scroll sideways: let wide tables wrap to the page instead of being cut off. */
    .table-responsive, .quarto-figure, figure, .cell-output-display, div:has(> table) { overflow: visible !important; }
    table, caption { width: 100% !important; max-width: 100% !important; min-width: 0 !important; }
    th, td { white-space: normal !important; padding-left: .35em !important; padding-right: .35em !important; }
    @page { margin: 0; }` });
  await page.waitForTimeout(1500);                 // let KaTeX and fonts settle
  fs.mkdirSync(path.dirname(outFile), { recursive: true });
  await page.pdf({ path: outFile, width: `${width}px`, height: `${pageH}px`, printBackground: true,
                   margin: { top: '0px', bottom: '0px', left: '0px', right: '0px' } });
  console.log(outFile);
  await browser.close(); server.close();
});
