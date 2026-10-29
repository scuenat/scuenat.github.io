// Shared look and renderer for the LinkedIn carousels in this folder.
// render(dir, slidesByLang) writes carousel-<lang>.pdf and preview/<lang>-NN.png for each language.
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const C = {
  bg: "#fbfaf7", ink: "#1f2328", muted: "#5f6b76", rule: "#e6e2da",
  navy: "#1d4f73", deep: "#0b1733", amber: "#e0952b", warm: "#b36b00",
  green: "#2e7d5b", red: "#a93226", amberT: "#fdf1dc", navyT: "#e5eef5", greenT: "#e2f0e8",
};

const baseCss = `
@page { size: 1080px 1350px; margin: 0; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: ${C.bg}; color: ${C.ink}; font-family: Inter, sans-serif; -webkit-font-smoothing: antialiased; }
.slide { width: 1080px; height: 1350px; padding: 72px 88px 64px; display: flex; flex-direction: column; background: ${C.bg}; page-break-after: always; overflow: hidden; }
header, footer { display: flex; justify-content: space-between; align-items: center; font-size: 26px; color: ${C.muted}; }
.brand { font-family: "Source Serif 4", serif; font-weight: 600; font-size: 30px; color: ${C.navy}; display: flex; align-items: center; gap: 14px; }
.dot { width: 18px; height: 18px; border-radius: 50%; background: ${C.amber}; }
.next { color: ${C.warm}; font-weight: 600; }
footer { border-top: 2px solid ${C.rule}; padding-top: 26px; }
.content { flex: 1; display: flex; flex-direction: column; justify-content: center; gap: 30px; }
h1 { font-family: "Source Serif 4", serif; font-weight: 600; font-size: 118px; line-height: 1.02; letter-spacing: -.02em; }
h2 { font-family: "Source Serif 4", serif; font-weight: 600; font-size: 68px; line-height: 1.08; letter-spacing: -.015em; color: ${C.navy}; }
h2::after { content: ""; display: block; width: 96px; height: 6px; background: ${C.amber}; border-radius: 3px; margin-top: 28px; }
.body { font-size: 37px; line-height: 1.42; }
.body b { color: ${C.navy}; }
blockquote { font-family: "Source Serif 4", serif; font-style: italic; font-size: 54px; line-height: 1.22; color: ${C.ink}; border-left: 8px solid ${C.amber}; padding-left: 36px; }
.who { font-size: 27px; color: ${C.muted}; margin-top: -10px; padding-left: 44px; }
.src { font-size: 24px; color: ${C.muted}; }
.lead { font-size: 30px; color: ${C.muted}; line-height: 1.35; }
/* cover */
.cover { background: ${C.deep}; color: #fff; }
.cover header .brand { color: #fff; } .cover header, .cover footer { color: #aab6c3; } .cover footer { border-color: rgba(255,255,255,.15); }
.cover .next { color: ${C.amber}; }
.kicker { font-size: 30px; letter-spacing: .16em; text-transform: uppercase; color: ${C.amber}; font-weight: 600; }
.cover h1 { color: #fff; }
.sub { font-family: "Source Serif 4", serif; font-size: 46px; line-height: 1.3; color: #dfe6ee; max-width: 860px; }
.author { font-size: 30px; color: #aab6c3; margin-top: 30px; }
/* dark end */
.dark { background: ${C.navy}; color: #fff; }
.dark header .brand { color: #fff; } .dark header, .dark footer { color: #c9d6e2; } .dark footer { border-color: rgba(255,255,255,.2); }
.endline { font-family: "Source Serif 4", serif; font-size: 66px; line-height: 1.2; font-weight: 600; }
.cta { background: rgba(255,255,255,.08); border-left: 8px solid ${C.amber}; padding: 34px 40px; border-radius: 0 16px 16px 0; font-size: 32px; color: #dfe6ee; }
.cta .link { font-size: 50px; font-weight: 700; color: ${C.amber}; margin-top: 10px; }
.ask { font-size: 36px; font-weight: 600; }
/* rings */
.rings { display: flex; align-items: center; gap: 36px; }
.rl { font-family: Inter; font-weight: 700; font-size: 30px; letter-spacing: .08em; }
.rnotes { list-style: none; display: flex; flex-direction: column; gap: 30px; flex: 1; }
.rnotes li { border-left: 8px solid var(--c); padding-left: 22px; font-size: 28px; line-height: 1.3; }
.rnotes li span { color: ${C.muted}; font-size: 25px; }
.foot { font-family: "Source Serif 4", serif; font-style: italic; font-size: 34px; color: ${C.muted}; line-height: 1.3; }
/* big number */
.big { font-family: "Source Serif 4", serif; font-weight: 600; font-size: 150px; color: ${C.amber}; line-height: 1; margin-top: 10px; }
.bigsub { font-size: 32px; color: ${C.muted}; margin-top: -16px; }
/* horizontal bars */
.hgroup { display: flex; flex-direction: column; gap: 16px; }
.hg { font-size: 30px; font-weight: 700; }
.hrow { display: grid; grid-template-columns: 300px 1fr; align-items: center; gap: 20px; }
.hlab { font-size: 27px; color: ${C.muted}; }
.htrack { position: relative; height: 66px; display: flex; align-items: center; padding-left: 45%; }
.htrack::before { content: ""; position: absolute; left: 45%; top: -8px; bottom: -8px; width: 2px; background: ${C.muted}; }
.hbar { height: 54px; border-radius: 0 8px 8px 0; }
.hbar.neg { position: absolute; right: 55%; border-radius: 8px 0 0 8px; }
.hval { font-size: 38px; font-weight: 800; margin-left: 16px; }
.hbar.neg + .hval { margin-left: 18px; }
/* vertical bars */
.vchart { display: flex; gap: 70px; padding: 10px 20px 0; border-bottom: 0; }
.vgroup { display: grid; grid-template-columns: 1fr 1fr; column-gap: 26px; flex: 1; }
.vb { display: flex; flex-direction: column; }
.vpos { display: flex; flex-direction: column; justify-content: flex-end; border-bottom: 3px solid ${C.muted}; }
.vpos div, .vneg div { width: 100%; border-radius: 8px 8px 0 0; }
.vneg div { border-radius: 0 0 8px 8px; }
.vv { font-size: 36px; font-weight: 800; text-align: center; padding: 6px 0; }
.vneg .vv { display: block; } .vv.zero { padding-top: 10px; }
.vg { grid-column: 1 / 3; text-align: center; font-size: 27px; font-weight: 600; margin-top: 4px; }
.legend { display: flex; flex-direction: column; gap: 10px; font-size: 26px; color: ${C.muted}; }
.legend i { display: inline-block; width: 26px; height: 26px; border-radius: 5px; margin-right: 14px; vertical-align: -4px; }
/* steps */
.steps { list-style: none; display: flex; flex-direction: column; gap: 14px; }
.steps li { background: #fff; border: 2px solid ${C.rule}; border-left: 8px solid ${C.navy}; border-radius: 0 12px 12px 0; padding: 14px 24px; display: flex; flex-direction: column; max-width: 760px; }
.steps li:last-child { border-left-color: ${C.green}; background: ${C.greenT}; }
.steps b { font-size: 30px; } .steps span { font-size: 24px; color: ${C.muted}; }
/* to do */
.todo { border-left: 8px solid var(--c); padding-left: 30px; }
.todo h3 { font-size: 34px; margin-bottom: 14px; }
.todo ul { list-style: none; display: flex; flex-direction: column; gap: 12px; }
.todo li { font-size: 33px; line-height: 1.3; padding-left: 36px; position: relative; }
.todo li::before { content: "→"; position: absolute; left: 0; color: var(--c); font-weight: 700; }
`;

async function render(dir, slidesByLang, extraCss = "") {
  const browser = await chromium.launch();
  for (const [lang, body] of Object.entries(slidesByLang)) {
    const html = `<!doctype html><html lang="${lang}"><head><meta charset="utf-8"><style>${baseCss}${extraCss}</style></head><body>${body}</body></html>`;
    const htmlPath = path.join(dir, `carousel-${lang}.html`);
    fs.writeFileSync(htmlPath, html);
    const page = await browser.newPage({ viewport: { width: 1080, height: 1350 } });
    await page.goto("file://" + htmlPath);
    await page.evaluate(() => document.fonts.ready);
    await page.pdf({ path: path.join(dir, `carousel-${lang}.pdf`), width: "1080px", height: "1350px", printBackground: true });
    fs.mkdirSync(path.join(dir, "preview"), { recursive: true });
    const els = await page.$$(".slide");
    for (let i = 0; i < els.length; i++) await els[i].screenshot({ path: path.join(dir, "preview", `${lang}-${String(i + 1).padStart(2, "0")}.png`) });
    // Flag any slide whose content does not fit its box
    const over = await page.$$eval(".slide .content", (cs) => cs.map((c, i) => {
      const box = c.getBoundingClientRect(), kids = [...c.children].map((k) => k.getBoundingClientRect());
      return Math.min(...kids.map((k) => k.top)) < box.top - 1 || Math.max(...kids.map((k) => k.bottom)) > box.bottom + 1 ? i + 1 : 0;
    }).filter(Boolean));
    console.log(lang, els.length, "slides", over.length ? "OVERFLOW on " + over.join(", ") : "ok");
    await page.close();
  }
  await browser.close();
}

module.exports = { C, render };
