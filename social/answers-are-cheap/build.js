// LinkedIn carousel: "Answers are cheap. Questions are ours." Eight pages that zoom in
// from the universe to the person, one scale per page, drawing on the physics essays,
// the AI experiments, the essays on teams, and The Joy of the Question.
// Run from this folder: node build.js. Shared style and renderer: ../lib.js.
const { C, render } = require("../lib");

const URL = "scuenat.github.io";
const SCALES = ["Universe", "Machines", "Teams", "Classroom", "You"];
const N = 8;

const page = (n, inner, cls = "") => `
<section class="slide ${cls}">
  <header><span class="brand"><span class="dot"></span>AI, Honestly</span><span class="num">${n} / ${N}</span></header>
  <div class="content">${inner}</div>
  <footer><span>${URL}</span>${n < N ? '<span class="next">Swipe →</span>' : ""}</footer>
</section>`;

// Zoom bar: five scales, the current one marked
const zoom = (k) => `<ol class="zoom">${SCALES.map((s, i) =>
  `<li class="${i === k ? "now" : i < k ? "done" : ""}"><i style="width:${46 - i * 7}px;height:${46 - i * 7}px"></i><span>${s}</span></li>`).join("")}</ol>`;

const scene = (k, title, art, body, essays) => page(k + 2, `${zoom(k)}
  <h2 class="t">${title}</h2>
  <div class="art">${art}</div>
  <p class="body">${body}</p>
  <p class="essays"><span>${essays.includes("·") ? "Essays" : "Essay"} · </span>${essays}</p>`, "scene");

// Seeded random, so the dots are the same on every build
let seed = 7;
const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);

function cloud(cx, cy, r, n, bright) {
  let s = "";
  for (let i = 0; i < n; i++) {
    const a = rnd() * Math.PI * 2, d = Math.sqrt(rnd()) * r;
    const col = rnd() < 0.5 ? C.navy : C.amber;
    s += `<circle cx="${(cx + d * Math.cos(a)).toFixed(1)}" cy="${(cy + d * Math.sin(a)).toFixed(1)}" r="${(4 + rnd() * 4).toFixed(1)}" fill="${col}" opacity="${bright ? 0.75 : 0.14}"/>`;
  }
  return s;
}

const artQuestion = `<svg viewBox="0 0 900 330" width="900" height="330">
  <circle cx="190" cy="160" r="150" fill="${C.navyT}"/>${cloud(190, 160, 140, 140, true)}
  <text x="190" y="325" text-anchor="middle" class="cap">Before: every answer possible</text>
  <path d="M370 160 H520" stroke="${C.amber}" stroke-width="6" marker-end="url(#ah)"/>
  <text x="445" y="140" text-anchor="middle" class="capb" fill="${C.warm}">a question</text>
  <defs><marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0L10 5L0 10z" fill="${C.amber}"/></marker></defs>
  <circle cx="710" cy="160" r="150" fill="${C.navyT}"/>${cloud(710, 160, 140, 140, false)}
  <circle cx="742" cy="128" r="30" fill="${C.amber}" opacity=".25"/><circle cx="742" cy="128" r="15" fill="${C.amber}"/>
  <text x="710" y="325" text-anchor="middle" class="cap">After: one answer, chosen</text>
</svg>`;

const artCompare = `<svg viewBox="0 0 900 300" width="900" height="300">
  <rect x="20" y="40" width="250" height="150" rx="16" fill="#fff" stroke="${C.rule}" stroke-width="3"/>
  <text x="145" y="100" text-anchor="middle" class="capb">Record A</text><text x="145" y="140" text-anchor="middle" class="cap">one view</text>
  <rect x="630" y="40" width="250" height="150" rx="16" fill="#fff" stroke="${C.rule}" stroke-width="3"/>
  <text x="755" y="100" text-anchor="middle" class="capb">Record B</text><text x="755" y="140" text-anchor="middle" class="cap">another view</text>
  <path d="M275 115 C360 115 380 210 440 210" fill="none" stroke="${C.navy}" stroke-width="5"/>
  <path d="M625 115 C540 115 520 210 460 210" fill="none" stroke="${C.navy}" stroke-width="5"/>
  <circle cx="450" cy="215" r="44" fill="${C.green}"/><path d="M430 215 l14 14 l24 -28" stroke="#fff" stroke-width="8" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <text x="450" y="292" text-anchor="middle" class="capb" fill="${C.green}">they meet, and agree</text>
</svg>`;

const artMass = `<svg viewBox="0 0 900 300" width="900" height="300">
  <line x1="60" y1="250" x2="860" y2="250" stroke="${C.muted}" stroke-width="2"/>
  <line x1="60" y1="20" x2="60" y2="250" stroke="${C.muted}" stroke-width="2"/>
  <path d="M60 60 C240 70 300 220 860 232" fill="none" stroke="${C.amber}" stroke-width="7"/>
  <path d="M60 225 C320 210 600 120 860 40" fill="none" stroke="${C.navy}" stroke-width="7"/>
  <text x="80" y="40" class="capb" fill="${C.warm}">cost of making</text>
  <text x="860" y="20" text-anchor="end" class="capb" fill="${C.navy}">cost of carrying</text>
  <text x="860" y="285" text-anchor="end" class="cap">time with AI → (schematic)</text>
</svg>`;

const artEffort = `<div class="bars">
  <div class="b"><div class="v" style="color:${C.amber}">−17%</div><div class="bar neg" style="height:120px;background:${C.amber}"></div>
    <p>Practised with a plain chatbot</p></div>
  <div class="b"><div class="v" style="color:${C.navy}">≈ 0</div><div class="bar" style="height:6px;background:${C.navy}"></div>
    <p>Practised with a tutor that gives hints, not answers</p></div>
  <p class="note">Exam scores once the AI was taken away, compared with students who never had it (~1,000 students; Bastani et al., <i>PNAS</i>, 2025)</p>
</div>`;

const artHill = `<svg viewBox="0 0 900 300" width="900" height="300">
  <path d="M0 290 C200 290 380 60 560 50 C700 45 800 160 900 290 Z" fill="${C.greenT}"/>
  <path d="M0 290 C200 290 380 60 560 50 C700 45 800 160 900 290" fill="none" stroke="${C.green}" stroke-width="5"/>
  <circle cx="455" cy="78" r="34" fill="${C.amber}"/>
  <path d="M250 230 C300 190 350 140 400 112" fill="none" stroke="${C.navy}" stroke-width="5" stroke-dasharray="4 12" stroke-linecap="round" marker-end="url(#up)"/>
  <defs><marker id="up" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0L10 5L0 10z" fill="${C.navy}"/></marker></defs>
  <text x="700" y="250" text-anchor="middle" class="cap">the climb is the point</text>
</svg>`;

const slides = [
  page(1, `<p class="kicker">Six essays, one question</p>
    <h1>Answers are cheap.<br><span>Questions are ours.</span></h1>
    <p class="sub">What stays human when AI can answer almost anything, seen at five scales.</p>
    ${zoom(-1)}`, "cover"),
  scene(0, "An answer needs someone asking.", artQuestion,
    "In recent calculations, a closed universe seen from outside holds nothing to know. Information begins with someone inside, asking. A language model works a bit like that: every answer waits until a question arrives.",
    "Nothing From Outside, Everything From Inside"),
  scene(1, "Agreement is not truth.", artCompare,
    "Ten of my models that agreed were right <b>99.8%</b> of the time, unless they had all learned the same mistake. Then their agreement was worth no more than chance. Compare, then check against the world.",
    "What Survives Comparison · Coherence Is Measurable"),
  scene(2, "Everything you make, you carry.", artMass,
    "AI lowers the cost of making, not of carrying. So make less, approve only what you cannot undo, watch the rest, and keep processes light.",
    "Work Has Mass · Stop Reviewing Pull Requests"),
  scene(3, "The skill is in the effort.", artEffort,
    "A tool that does the climbing for you takes the learning with it. A tool that keeps the effort does no harm.",
    "The Joy of the Question"),
  scene(4, "A machine has no reason to want an answer. We&nbsp;do.", artHill,
    "“One must imagine Sisyphus happy,” wrote Camus. Being first at the top is not the same as being glad to be there. Choosing the question, and caring about it, stays ours.",
    "The Joy of the Question"),
  page(7, `<h1 class="msg">Answers are cheap.<br><span>Questions are ours.</span></h1>
    <ul class="rules">
      <li><b>Ask your own question.</b> An answer means something only to someone.</li>
      <li><b>Compare, then check against the world.</b> Agreement is not truth.</li>
      <li><b>Carry only what matters.</b> Making is free; keeping is not.</li>
      <li><b>Keep the effort, and the joy.</b> That is where the skill comes from.</li>
    </ul>`, "message"),
  page(8, `<p class="endline">What question would you never hand to a machine?</p>
    <div class="cta"><p>Essays, experiments and code, in English and French</p><p class="link">${URL}</p></div>
    <p class="ask">Tell me in the comments. Good questions often become the next essay.</p>`, "dark"),
];

const css = `
.cover h1 { font-size: 104px; line-height: 1.04; }
h1 span, .msg span { color: ${C.amber}; }
.cover .sub { font-size: 44px; }
.cover .zoom { margin-top: 50px; }
.cover .zoom span { color: #aab6c3; }
.cover .zoom i { background: rgba(255,255,255,.18); border-color: rgba(255,255,255,.3); }
.zoom { list-style: none; display: flex; justify-content: space-between; align-items: flex-end; }
.zoom li { display: flex; flex-direction: column; align-items: center; gap: 10px; flex: 1; }
.zoom i { border-radius: 50%; background: ${C.rule}; border: 2px solid ${C.rule}; }
.zoom span { font-size: 22px; color: ${C.muted}; letter-spacing: .04em; }
.zoom li.done i { background: ${C.navyT}; border-color: ${C.navy}; }
.zoom li.now i { background: ${C.amber}; border-color: ${C.amber}; box-shadow: 0 0 0 8px rgba(224,149,43,.18); }
.zoom li.now span { color: ${C.warm}; font-weight: 800; }
.scene .content { justify-content: flex-start; padding-top: 40px; gap: 26px; }
.scene .zoom { margin-bottom: 20px; padding-bottom: 26px; border-bottom: 2px solid ${C.rule}; }
h2.t { font-family: "Source Serif 4", serif; font-weight: 600; font-size: 82px; line-height: 1.08; letter-spacing: -.015em; color: ${C.ink}; margin-top: -8px; }
h2.t::after { display: none; }
.art { display: flex; justify-content: center; }
.cap { font: 400 24px Inter; fill: ${C.muted}; }
.capb { font: 700 28px Inter; fill: ${C.ink}; }
.scene .body { font-size: 39px; line-height: 1.42; }
.scene .body b { color: ${C.navy}; }
.essays { margin-top: auto; font-size: 24px; color: ${C.navy}; font-weight: 600; }
.essays span { color: ${C.muted}; font-weight: 400; }
.bars { display: grid; grid-template-columns: 1fr 1fr; column-gap: 60px; width: 100%; padding: 0 40px; }
.b { display: flex; flex-direction: column; align-items: center; }
.b .v { font-family: "Source Serif 4", serif; font-weight: 600; font-size: 84px; line-height: 1; }
.b .bar { width: 160px; border-radius: 0 0 10px 10px; margin-top: 18px; border-top: 3px solid ${C.muted}; }
.b p { font-size: 26px; color: ${C.muted}; text-align: center; margin-top: 16px; line-height: 1.3; }
.bars .note { grid-column: 1 / 3; font-size: 21px; color: ${C.muted}; text-align: center; margin-top: 18px; line-height: 1.35; }
.message .content { gap: 50px; }
.msg { font-size: 96px; line-height: 1.05; }
.rules { list-style: none; display: flex; flex-direction: column; gap: 26px; }
.rules li { font-size: 34px; line-height: 1.35; color: ${C.muted}; border-left: 8px solid ${C.amber}; padding-left: 26px; }
.rules b { color: ${C.ink}; display: block; font-size: 38px; }
`;

render(__dirname, { en: slides.join("\n") }, css);
