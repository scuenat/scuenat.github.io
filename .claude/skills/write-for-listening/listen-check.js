#!/usr/bin/env node
// What will the "Listen" button say? Prints the transcript of a rendered post or draft, exactly as
// listen.js builds it, and flags what a voice reads badly.
//
//   node .claude/skills/write-for-listening/listen-check.js drafts/<name> [fr/drafts/<name> ...]
//   options: --transcript <file>   also write the transcript to a file (one paragraph per line)
//
// Render first (quarto render, or quarto render <dir>/index.qmd): the check reads _site/<dir>/index.html.
// Exit code 1 when something must be fixed, 0 when only notes remain.
const fs = require("fs");
const path = require("path");
const http = require("http");
const { chromium } = require("playwright");

const ROOT = path.resolve(__dirname, "../../..");
const SITE = path.join(ROOT, "_site");
const args = process.argv.slice(2);
let out = null;
const targets = [];
for (let i = 0; i < args.length; i++) {
  if (args[i] === "--transcript") out = args[++i];
  else targets.push(args[i]);
}
if (!targets.length) {
  console.error("usage: listen-check.js <post-or-draft-dir|index.qmd> [...] [--transcript file]");
  process.exit(2);
}

// ---- Rules on the spoken text (after listen.js has shaped it) ----
// [label, regex, level, advice]
const RULES = [
  ["file or code name", /\b[\w-]+\.(py|js|qmd|md|bib|svg|png|jpe?g|pdf|csv|json|ya?ml|ipynb|html|sh|txt)\b/gi, "fix",
    "a voice says \"figs dot p y\": name what the file does, or leave the link to the figure caption"],
  ["web address", /\bhttps?:\/\/\S+|\bwww\.\S+/gi, "fix", "put the link on words, not on the bare address"],
  ["figure or table reference", /\b(fig(ure)?s?|tables?|tableaux?)\.?\s*\d+/gi, "fix",
    "figures and tables are silent: say in the sentence what they show, or \"in the drawing I made\""],
  ["seen, not heard", /\b(see below|see above|shown below|shown above|as shown|on the left|on the right|in red|in blue|in green|in grey|in amber|ci-dessous|ci-dessus|à gauche|à droite|en rouge|en bleu|en vert|en gris)\b/gi, "note",
    "a listener cannot see it: check the sentence still makes sense with eyes closed"],
  ["equation read as \"an equation\"", /\b(an equation|une équation)\b/gi, "fix",
    "inline maths is read as \"an equation\": say it in words, or move the formula after the sentence that says it"],
  ["symbol", /[→←↔⇒⇐×≈±≤≥≠∼~<>=+*#@^|\\§•·∑∫√∞∝]|(?<=\w)\/(?=\w)/g, "fix",
    "write the word: \"to\", \"times\", \"about\", \"at most\", \"or\"..."],
  ["abbreviation", /\b(cf|approx|ca|resp|incl|esp|viz|w\.r\.t|n\.b|fig|eq|sec|ch|vol|pp?|no|env|ex|av)\.(?=\s|$)|\bet al\.?/gi, "fix",
    "write it in full (\"compare\", \"about\", \"and colleagues\")"],
  ["unit abbreviation", /\d\s?(km|cm|mm|kg|ms|µs|ns|GB|MB|kB|TB|Gyr|Myr|kyr|GHz|MHz|Hz|kW|MW|W|°C|K|tok\/s)\b/g, "fix",
    "write the unit in words: \"5 gigabytes\", \"300 thousand years\""],
  ["scientific notation", /\d\s*(e[+-]?\d+|\^\s*\d+)|10\s*\d{2,}\b/gi, "fix", "say \"a billion\", not 10^9"],
  ["leftover bracket or quote mark", /[()[\]{}]/g, "note", "a bracket the reader did not turn into a pause"],
];
const CAPS = /\b[A-Z]{2,}s?\b/g;
const CAPS_OK = new Set(["AI", "IA", "US", "UK", "EU", "UE", "OK", "TV", "PDF", "DNA", "ADN", "CEO", "IT", "PC", "OS", "API"]);

function sentences(t) { return t.match(/[^.!?…]+[.!?…]+["»”’]*|[^.!?…]+$/g) || [t]; }
function words(t) { return t.split(/\s+/).filter(Boolean).length; }

function sourceChecks(qmd) {
  // Things the reader drops or reads flat, seen in the source
  const notes = [];
  const body = fs.readFileSync(qmd, "utf8").replace(/^---[\s\S]*?\n---\n/, "").replace(/```[\s\S]*?```/g, "");
  const asides = body.match(/\(([^()\n]{0,400})\)/g) || [];
  asides.forEach((a) => {
    if (/^\(\s*(figures?|https?:|\.\.?\/|[\w-]+\.(py|qmd|svg|png))/i.test(a)) return;
    if (words(a) > 14) notes.push(["long aside in brackets", a.slice(0, 90) + (a.length > 90 ? "…" : ""),
      "read as a comma pause, the listener loses the thread: make it its own sentence"]);
  });
  (body.match(/\$[^$\n]+\$/g) || []).forEach((m) => notes.push(["inline maths", m, "read as \"an equation\""]));
  (body.match(/(?<![*\w])\*(?!\*)[^*\n]{3,60}\*(?!\*)/g) || []).forEach((m) => {
    if (/\s/.test(m.trim().slice(1, -1)) && /\b(sub|ergo|qua|a priori|a posteriori|ipso|facto|sapiens|aeternitatis|zeitgeist|gestalt|bona fide|mutatis|ceteris|ad hoc|per se)\b/i.test(m))
      notes.push(["foreign phrase", m, "the page's voice will mispronounce it: say what it means just before or after"]);
  });
  (body.match(/^#{2,4} .+$/gm) || []).forEach((h) => {
    if (words(h.replace(/^#+\s*/, "")) > 10) notes.push(["long heading", h, "headings are read as a sentence: keep them short and spoken"]);
  });
  return notes;
}

function serve() {
  const types = { ".html": "text/html", ".js": "text/javascript", ".css": "text/css", ".svg": "image/svg+xml", ".png": "image/png", ".json": "application/json", ".woff2": "font/woff2" };
  return new Promise((resolve) => {
    const srv = http.createServer((req, res) => {
      let p = decodeURIComponent(req.url.split("?")[0]);
      if (p.endsWith("/")) p += "index.html";
      const f = path.join(SITE, p);
      if (!f.startsWith(SITE) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { res.writeHead(404); res.end(); return; }
      res.writeHead(200, { "content-type": types[path.extname(f)] || "application/octet-stream" });
      fs.createReadStream(f).pipe(res);
    });
    srv.listen(0, "127.0.0.1", () => resolve(srv));
  });
}

(async () => {
  const srv = await serve();
  const port = srv.address().port;
  const browser = await chromium.launch();
  let mustFix = 0;
  const transcript = [];
  for (const t of targets) {
    const dir = t.replace(/\/?index\.qmd$/, "").replace(/\/$/, "");
    const qmd = path.join(ROOT, dir, "index.qmd");
    const html = path.join(SITE, dir, "index.html");
    if (!fs.existsSync(html)) { console.error(`✗ ${dir}: no ${path.relative(ROOT, html)}; render it first`); mustFix++; continue; }
    const page = await browser.newPage();
    // A stand-in voice, so the button appears even in a browser without one
    await page.addInitScript(() => {
      if (!window.speechSynthesis) {
        window.speechSynthesis = { getVoices: () => [], speak() {}, cancel() {}, pause() {}, resume() {}, addEventListener() {} };
        window.SpeechSynthesisUtterance = function (t) { this.text = t; };
      }
    });
    await page.goto(`http://127.0.0.1:${port}/${dir}/`, { waitUntil: "load" });
    const items = await page.evaluate(() => (window.listenTranscript ? window.listenTranscript() : null));
    await page.close();
    if (!items) { console.error(`✗ ${dir}: the Listen button did not start (is listen.js loaded, is it a post or draft?)`); mustFix++; continue; }

    const all = items.join(" ");
    const n = words(all);
    const sent = items.flatMap(sentences).map((s) => s.trim()).filter((s) => words(s) > 1);
    const long = sent.filter((s) => words(s) > 30);
    console.log(`\n${dir}`);
    console.log(`  ${items.length} paragraphs read, ${n} words, about ${Math.max(1, Math.round(n / 153))} min of listening; ` +
      `${sent.length} sentences, ${(n / Math.max(1, sent.length)).toFixed(1)} words each on average`);

    const found = [];
    items.forEach((text, i) => {
      RULES.forEach(([label, re, level, advice]) => {
        (text.match(re) || []).forEach((m) => found.push({ level, label, m, i, text, advice }));
      });
    });
    const caps = {};
    (all.match(CAPS) || []).forEach((c) => { const b = c.replace(/s$/, ""); if (!CAPS_OK.has(b)) caps[b] = (caps[b] || 0) + 1; });

    found.forEach((f) => {
      if (f.level === "fix") mustFix++;
      const at = f.text.indexOf(f.m);
      const ctx = f.text.slice(Math.max(0, at - 40), at + f.m.length + 40);
      console.log(`  ${f.level === "fix" ? "✗" : "·"} ${f.label}: "${f.m}" (paragraph ${f.i + 1}) …${ctx}…\n      → ${f.advice}`);
    });
    long.forEach((s) => console.log(`  · sentence of ${words(s)} words, hard to follow by ear: "${s.slice(0, 110)}${s.length > 110 ? "…" : ""}"`));
    Object.keys(caps).forEach((c) => console.log(`  · acronym "${c}" (${caps[c]}×): spelled letter by letter or read as a word? Say it in full once.`));
    if (fs.existsSync(qmd)) sourceChecks(qmd).forEach(([label, m, advice]) => console.log(`  · ${label}: ${m}\n      → ${advice}`));
    if (!found.length && !long.length) console.log("  ✓ nothing to fix in the spoken text");

    transcript.push(`### ${dir}`, ...items, "");
  }
  await browser.close();
  srv.close();
  if (out) { fs.writeFileSync(out, transcript.join("\n")); console.log(`\nTranscript written to ${out}`); }
  console.log(mustFix ? `\n${mustFix} thing(s) to fix (✗). Notes (·) are for judgement.` : "\nNo blocking issue. Read the notes (·), then listen to the opening once.");
  process.exit(mustFix ? 1 : 0);
})();
