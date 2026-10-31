// LinkedIn image for "A Grammar for Tools": one 1080 x 1350 picture, English only.
// Build: node build.js  ->  post-en.png
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");
const { C } = require("../lib.js");

const chip = (x, y, w, label, fill = "#fff", stroke = C.rule, color = C.ink) => `
  <rect x="${x}" y="${y}" width="${w}" height="64" rx="12" fill="${fill}" stroke="${stroke}" stroke-width="2"/>
  <text x="${x + w / 2}" y="${y + 41}" text-anchor="middle" font-family="JetBrains Mono, monospace" font-size="25" fill="${color}">${label}</text>`;
const edge = (x1, y1, x2, y2, label, color, lx, ly, dash = "") => `
  <line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${color}" stroke-width="4" ${dash ? `stroke-dasharray="${dash}"` : ""} marker-end="url(#a-${color.slice(1)})"/>
  <rect x="${lx - label.length * 8.6 - 14}" y="${ly - 22}" width="${label.length * 17.2 + 28}" height="40" rx="20" fill="${C.bg}" stroke="${color}" stroke-width="2"/>
  <text x="${lx}" y="${ly + 7}" text-anchor="middle" font-family="JetBrains Mono, monospace" font-size="22" fill="${color}">${label}</text>`;
const marker = (c) => `<marker id="a-${c.slice(1)}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="${c}"/></marker>`;

// Left: the dictionary. Right: the grammar.
const left = ["approve_invoice", "pay_invoice", "convert", "post_ledger", "send_message"]
  .map((t, i) => chip(0, i * 86, 270, t)).join("");
const right = `
  ${chip(0, 0, 240, "approve_invoice")}
  ${chip(275, 0, 215, "convert")}
  ${chip(120, 178, 250, "pay_invoice", C.green, C.green, "#fff")}
  ${chip(0, 356, 240, "send_message")}
  ${chip(275, 356, 215, "post_ledger")}
  ${edge(120, 66, 196, 170, "requires", C.navy, 90, 122)}
  ${edge(382, 66, 300, 170, "used with", C.warm, 410, 122)}
  ${edge(196, 244, 120, 348, "notifies", C.warm, 90, 300)}
  ${edge(300, 244, 382, 348, "feeds", C.green, 410, 300)}`;

const html = `<!doctype html><html><head><meta charset="utf-8"><style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { width: 1080px; height: 1350px; background: ${C.deep}; font-family: Inter, sans-serif; color: #fff; -webkit-font-smoothing: antialiased; }
.wrap { width: 1080px; height: 1350px; padding: 70px 80px 60px; display: flex; flex-direction: column; }
header { display: flex; justify-content: space-between; align-items: center; font-size: 26px; color: #aab6c3; }
.brand { font-family: "Source Serif 4", serif; font-weight: 600; font-size: 30px; color: #fff; display: flex; align-items: center; gap: 14px; }
.dot { width: 18px; height: 18px; border-radius: 50%; background: ${C.amber}; }
.new { color: ${C.amber}; font-weight: 600; letter-spacing: .14em; text-transform: uppercase; font-size: 24px; }
.kicker { margin-top: 64px; font-size: 26px; letter-spacing: .16em; text-transform: uppercase; color: ${C.amber}; font-weight: 600; }
h1 { margin-top: 22px; font-family: "Source Serif 4", serif; font-weight: 600; font-size: 74px; line-height: 1.08; letter-spacing: -.015em; }
h1 span { color: ${C.amber}; }
.panel { margin-top: 54px; background: ${C.bg}; border-radius: 22px; padding: 34px 40px 30px; display: grid; grid-template-columns: 270px 1fr; column-gap: 60px; color: ${C.ink}; }
.lab { white-space: nowrap; font-size: 21px; letter-spacing: .14em; text-transform: uppercase; font-weight: 700; margin-bottom: 22px; }
.l1 { color: ${C.navy}; } .l2 { color: ${C.green}; }
.note { grid-column: 1 / 3; margin-top: 26px; padding-top: 22px; border-top: 2px solid ${C.rule}; font-family: "Source Serif 4", serif; font-style: italic; font-size: 30px; color: ${C.muted}; }
footer { margin-top: auto; display: flex; justify-content: space-between; align-items: flex-end; border-top: 2px solid rgba(255,255,255,.15); padding-top: 24px; }
.title { font-family: "Source Serif 4", serif; font-size: 36px; font-weight: 600; }
.by { font-size: 24px; color: #aab6c3; margin-top: 6px; }
.url { font-size: 28px; color: ${C.amber}; font-weight: 700; }
</style></head><body><div class="wrap">
<header><div class="brand"><span class="dot"></span>AI, Honestly</div><div class="new">New essay</div></header>
<div class="kicker">Model Context Protocol</div>
<h1>MCP gave AI agents a dictionary.<br><span>It still lacks a grammar.</span></h1>
<div class="panel">
  <div><div class="lab l1">Today · a dictionary</div>
    <svg width="270" height="420" viewBox="0 0 270 420">${left}</svg></div>
  <div><div class="lab l2">Missing · a grammar</div>
    <svg width="490" height="420" viewBox="0 0 490 420" overflow="visible"><defs>${[C.navy, C.green, C.warm].map(marker).join("")}</defs>${right}</svg></div>
  <div class="note">Every agent redraws these lines on every run, then forgets them.</div>
</div>
<footer><div><div class="title">A Grammar for Tools</div><div class="by">Stéphane Cuenat · essay</div></div><div class="url">scuenat.github.io</div></footer>
</div></body></html>`;

(async () => {
  const out = path.join(__dirname, "post-en.html");
  fs.writeFileSync(out, html);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1350 } });
  await page.goto("file://" + out);
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: path.join(__dirname, "post-en.png") });
  await browser.close();
  fs.unlinkSync(out);
  console.log("post-en.png written");
})();
