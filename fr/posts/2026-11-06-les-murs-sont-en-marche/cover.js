// Image de couverture (1920 × 1080) pour « Les murs, eux, sont en marche ».
// Version française de l'image de l'édition LinkedIn.
// Usage : node cover.js [dossier-des-polices]
//   Sans argument, les polices (Lora, Poppins) viennent de Google Fonts.
//   Avec un dossier, il doit contenir Lora.ttf, Poppins-Regular.ttf et Poppins-Medium.ttf.
// Écrit figures/cover.png. Requiert Playwright.
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const W = 1920, H = 1080;
const BG = "#111a31", GRID = "#18223d", INK = "#f2f1ee", ORANGE = "#ec9a3c";
const MUTED = "#8f99b5", DIM = "#5b6685";

// générateur pseudo-aléatoire déterministe (mulberry32)
let seed = 1964;
const rnd = () => {
  seed |= 0; seed = (seed + 0x6d2b79f5) | 0;
  let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};
const between = (a, b) => a + (b - a) * rnd();

function graphic() {
  const s = [];
  const top = 300, bottom = 840, oldX = 1250, wallX = 1640;
  // grille de fond
  for (let x = 0; x <= W; x += 48) s.push(`<line x1="${x}" y1="0" x2="${x}" y2="${H}" stroke="${GRID}" stroke-width="1"/>`);
  for (let y = 0; y <= H; y += 48) s.push(`<line x1="0" y1="${y}" x2="${W}" y2="${y}" stroke="${GRID}" stroke-width="1"/>`);
  // flèche pointillée : le mur se déplace
  for (let x = 1268; x < 1605; x += 14) s.push(`<circle cx="${x}" cy="260" r="2" fill="${MUTED}"/>`);
  s.push(`<path d="M1610 251 L1628 260 L1610 269 Z" fill="${MUTED}"/>`);
  // ancien mur : colonne de cases vides
  for (let y = top + 6; y <= bottom; y += 22)
    s.push(`<rect x="${oldX - 8}" y="${y - 6}" width="16" height="11" rx="3" fill="none" stroke="${DIM}" stroke-width="1.6"/>`);
  // le travail qui passait l'ancien mur, avec sa traînée
  const trail = (x, y, len, col, r, op) => {
    s.push(`<line x1="${x - len}" y1="${y}" x2="${x}" y2="${y}" stroke="${col}" stroke-width="1.2" opacity="${op * 0.55}"/>`);
    s.push(`<circle cx="${x}" cy="${y}" r="${r}" fill="${col}" opacity="${op}"/>`);
  };
  for (let i = 0; i < 150; i++) trail(between(1010, oldX + 30), between(top + 10, bottom - 40), between(18, 40), MUTED, 2, 0.75);
  for (let i = 0; i < 110; i++) trail(between(oldX + 40, 1570), between(top + 10, bottom - 15), between(8, 22), "#c9cede", 2.6, 0.9);
  // le travail qui s'entasse contre le nouveau mur
  for (let i = 0; i < 330; i++) {
    const d = Math.abs(between(0, 1) * between(0, 1)) * 60;
    s.push(`<circle cx="${wallX - 6 - d}" cy="${between(top + 8, bottom - 8)}" r="${between(2.2, 4.4)}" fill="${ORANGE}" opacity="${between(0.55, 1)}"/>`);
  }
  for (let i = 0; i < 18; i++) s.push(`<circle cx="${between(1575, 1625)}" cy="${between(top + 10, bottom - 10)}" r="3.4" fill="#f4f2ee"/>`);
  // nouveau mur
  s.push(`<rect x="${wallX}" y="${top - 6}" width="23" height="${bottom - top + 12}" rx="6" fill="${ORANGE}"/>`);
  return s.join("\n");
}

function html(fontDir) {
  const faces = fontDir
    ? ["Lora.ttf|Lora|400 700", "Poppins-Regular.ttf|Poppins|400", "Poppins-Medium.ttf|Poppins|500"]
        .map((l) => { const [f, n, w] = l.split("|");
          return `@font-face{font-family:"${n}";src:url(data:font/ttf;base64,${fs.readFileSync(path.resolve(fontDir, f)).toString("base64")});font-weight:${w};}`; })
        .join("\n")
    : `@import url("https://fonts.googleapis.com/css2?family=Lora:wght@700&family=Poppins:wght@400;500&display=block");`;
  return `<!doctype html><html><head><meta charset="utf-8"><style>
${faces}
html,body{margin:0;width:${W}px;height:${H}px;background:${BG};overflow:hidden}
svg{position:absolute;inset:0}
.txt{position:absolute;left:150px;top:0;width:900px}
.brand{position:absolute;top:300px;font:500 22px Poppins;letter-spacing:.24em;color:${ORANGE}}
.rule{position:absolute;top:342px;width:50px;height:3px;background:${ORANGE}}
h1{position:absolute;top:378px;margin:0;font:700 102px/1.25 Lora;white-space:nowrap;letter-spacing:-.005em;color:${INK}}
h1 span{color:${ORANGE}}
.sub{position:absolute;top:770px;font:400 30px/1.5 Poppins;color:#c9cede}
.lab{position:absolute;top:866px;font:500 18px Poppins;letter-spacing:.2em;transform:translateX(-50%);white-space:nowrap}
</style></head><body>
<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">${graphic()}</svg>
<div class="txt">
  <div class="brand">AI, HONESTLY</div><div class="rule"></div>
  <h1>Les murs, eux,<br><span>sont en marche.</span></h1>
  <div class="sub">L’IA ne supprime pas la partie lente.<br>Elle la déplace.</div>
</div>
<div class="lab" style="left:1265px;color:${MUTED}">LÀ OÙ IL ÉTAIT</div>
<div class="lab" style="left:1652px;color:${ORANGE}">LÀ OÙ IL EST AUJOURD’HUI</div>
</body></html>`;
}

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: W, height: H } });
  await page.setContent(html(process.argv[2]), { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: path.join(__dirname, "figures", "cover.png") });
  await browser.close();
})();
