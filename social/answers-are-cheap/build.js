// LinkedIn carousel: "Answers are cheap. Questions are ours." Eight pages that zoom in
// from the universe to the person, one scale per page, drawing on the physics essays,
// the AI experiments, the essays on teams, and The Joy of the Question.
// Run from this folder: node build.js [en] [fr] (both by default). Shared style and renderer: ../lib.js.
const { C, render } = require("../lib");

const N = 8;

const T = {
  en: {
    url: "scuenat.github.io", swipe: "Swipe", essay: "Essay", essays: "Essays",
    scales: ["Universe", "Machines", "Teams", "Classroom", "You"],
    art: {
      before: "Before: all possible", after: "After: one chosen", question: "a question",
      modelA: "Model A", modelB: "Model B", its: "its answer", agree: "they agree…", world: "…then check the world",
      making: "cost of making", carrying: "cost of carrying", time: "time with AI → (schematic)",
      chatbot: "Plain chatbot", tutor: "Tutor giving hints", minus: "−17%", zeroLine: "0 = students who never had AI",
      note: "Exam scores once the AI was taken away (~1,000 high-school students; Bastani et al., <i>PNAS</i>, 2025)",
      climb: "the climb is the point",
    },
    cover: { kicker: "Six essays, one question", h1: "Answers are cheap.<br><span>Questions are ours.</span>",
      sub: "What stays human when AI can answer almost anything, seen at five scales." },
    scenes: [
      ["An answer needs someone asking.",
       "In recent calculations, a closed universe seen from outside holds nothing to know. Information begins with someone inside, asking. A language model works a bit like that: every answer waits until a question arrives.",
       "Nothing From Outside, Everything From Inside"],
      ["Agreement is not truth.",
       "When ten of my models all agreed, they were right <b>99.8%</b> of the time, unless they had all learned the same mistake. Then their agreement was worth no more than chance.",
       "What Survives Comparison · Coherence Is Measurable"],
      ["Everything you make, you carry.",
       "AI lowers the cost of making, not of carrying. So make less, approve only what you cannot undo, watch the rest, and keep processes light.",
       "Work Has Mass · Stop Reviewing Pull Requests"],
      ["The skill is in the effort.",
       "A tool that does the climbing for you takes the learning with it. A tool that keeps the effort does no harm.",
       "The Joy of the Question"],
      ["A machine has no reason of its own to want an answer. We&nbsp;do.",
       "“One must imagine Sisyphus happy,” wrote Camus. Being first at the top is not the same as being glad to be there. Choosing the question, and caring about it, stays ours.",
       "The Joy of the Question"],
    ],
    rules: [
      ["Ask your own question.", "An answer means something only to someone."],
      ["Compare, then check against the world.", "Agreement is not truth."],
      ["Carry only what matters.", "Making is free; keeping is not."],
      ["Keep the effort, and the joy.", "That is where the skill comes from."],
    ],
    end: { line: "What question would you never hand to a machine?", read: "Essays, experiments and code, in English and French",
      ask: "Tell me in the comments. Good questions often become the next essay." },
  },
  fr: {
    url: "scuenat.github.io/fr", swipe: "Faites défiler", essay: "Essai", essays: "Essais",
    scales: ["Univers", "Machines", "Équipes", "Classe", "Vous"],
    art: {
      before: "Avant : tout est possible", after: "Après : une seule, choisie", question: "une question",
      modelA: "Modèle A", modelB: "Modèle B", its: "sa réponse", agree: "ils s’accordent…", world: "…puis le monde tranche",
      making: "coût de fabriquer", carrying: "coût de porter", time: "le temps, avec l’IA → (schéma)",
      chatbot: "Simple chatbot", tutor: "Tuteur qui guide", minus: "−17 %", zeroLine: "0 = élèves qui n’ont jamais eu d’IA",
      note: "Notes à l’examen une fois l’IA retirée (près de 1 000 lycéens ; Bastani et al., <i>PNAS</i>, 2025)",
      climb: "l’ascension est le but",
    },
    cover: { kicker: "Six essais, une question", h1: "Les réponses ne coûtent plus rien.<br><span>Les questions sont&nbsp;à&nbsp;nous.</span>",
      sub: "Ce qui reste humain quand l’IA peut répondre à presque tout, vu à cinq échelles." },
    scenes: [
      ["Une réponse a besoin de quelqu’un qui demande.",
       "Selon des calculs récents, un univers fermé vu de l’extérieur ne contient rien à savoir. L’information commence avec quelqu’un à l’intérieur, qui demande. Un modèle de langage fonctionne un peu ainsi : chaque réponse attend qu’une question arrive.",
       "Rien du dehors, tout du dedans"],
      ["S’accorder n’est pas avoir raison.",
       "Quand mes dix modèles étaient tous d’accord, ils avaient raison dans <b>99,8 %</b> des cas, sauf s’ils avaient tous appris la même erreur. Leur accord ne valait alors pas mieux que le hasard.",
       "Ce qui survit à la comparaison · La cohérence se mesure"],
      ["Tout ce que vous fabriquez, vous le portez.",
       "L’IA baisse le coût de fabriquer, pas celui de porter. Alors fabriquez moins, n’approuvez que ce que vous ne pouvez pas défaire, surveillez le reste, et gardez des processus légers.",
       "Le travail a une masse · Arrêtez de relire les pull requests"],
      ["La compétence est dans l’effort.",
       "Un outil qui grimpe à votre place emporte l’apprentissage avec lui. Un outil qui garde l’effort ne fait pas de mal.",
       "La joie de la question"],
      ["Une machine n’a aucune raison à elle de vouloir une réponse. Nous,&nbsp;si.",
       "« Il faut imaginer Sisyphe heureux », écrivait Camus. Arriver le premier au sommet n’est pas la même chose qu’être heureux d’y être. Choisir la question, et y tenir, reste à nous.",
       "La joie de la question"],
    ],
    rules: [
      ["Posez votre propre question.", "Une réponse n’a de sens que pour quelqu’un."],
      ["Comparez, puis vérifiez face au monde.", "S’accorder n’est pas avoir raison."],
      ["Ne portez que ce qui compte.", "Fabriquer ne coûte rien ; garder, si."],
      ["Gardez l’effort, et la joie.", "C’est de là que vient la compétence."],
    ],
    end: { line: "Quelle question ne confieriez‑vous jamais à une machine ?", read: "Essais, expériences et code, en français et en anglais",
      ask: "Dites-le-moi en commentaire. Les bonnes questions deviennent souvent l’essai suivant." },
  },
};

function build(t) {
  const page = (n, inner, cls = "") => `
<section class="slide ${cls}">
  <header><span class="brand"><span class="dot"></span>AI, Honestly</span><span class="num">${n} / ${N}</span></header>
  <div class="content">${inner}</div>
  <footer><span>${t.url}</span>${n < N ? `<span class="next">${t.swipe} →</span>` : ""}</footer>
</section>`;

  // Zoom bar: five scales, the current one marked
  const zoom = (k) => `<ol class="zoom">${t.scales.map((s, i) =>
    `<li class="${i === k ? "now" : i < k ? "done" : ""}"><i style="width:${46 - i * 7}px;height:${46 - i * 7}px"></i><span>${s}</span></li>`).join("")}</ol>`;

  const scene = (k, art) => {
    const [title, body, essays] = t.scenes[k];
    return page(k + 2, `${zoom(k)}
  <h2 class="t">${title}</h2>
  <div class="art">${art}</div>
  <p class="body">${body}</p>
  <p class="essays"><span>${essays.includes("·") ? t.essays : t.essay} · </span>${essays}</p>`, "scene");
  };

const a = t.art;
  seed = 7;   // same dots in every language

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
    <text x="190" y="325" text-anchor="middle" class="cap">${a.before}</text>
    <path d="M370 160 H520" stroke="${C.amber}" stroke-width="6" marker-end="url(#ah)"/>
    <text x="445" y="140" text-anchor="middle" class="capb" fill="${C.warm}">${a.question}</text>
    <defs><marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0L10 5L0 10z" fill="${C.amber}"/></marker></defs>
    <circle cx="710" cy="160" r="150" fill="${C.navyT}"/>${cloud(710, 160, 140, 140, false)}
    <circle cx="742" cy="128" r="30" fill="${C.amber}" opacity=".25"/><circle cx="742" cy="128" r="15" fill="${C.amber}"/>
    <text x="710" y="325" text-anchor="middle" class="cap">${a.after}</text>
  </svg>`;
  
  const artCompare = `<svg viewBox="0 0 900 300" width="900" height="300">
    <rect x="20" y="10" width="250" height="110" rx="16" fill="#fff" stroke="${C.rule}" stroke-width="3"/>
    <text x="145" y="58" text-anchor="middle" class="capb">${a.modelA}</text><text x="145" y="94" text-anchor="middle" class="cap">${a.its}</text>
    <rect x="630" y="10" width="250" height="110" rx="16" fill="#fff" stroke="${C.rule}" stroke-width="3"/>
    <text x="755" y="58" text-anchor="middle" class="capb">${a.modelB}</text><text x="755" y="94" text-anchor="middle" class="cap">${a.its}</text>
    <path d="M275 65 C370 65 390 145 438 145" fill="none" stroke="${C.navy}" stroke-width="5"/>
    <path d="M625 65 C530 65 510 145 462 145" fill="none" stroke="${C.navy}" stroke-width="5"/>
    <circle cx="450" cy="147" r="16" fill="${C.navy}"/>
    <text x="425" y="192" text-anchor="end" class="capb" fill="${C.navy}">${a.agree}</text>
    <path d="M450 168 V202" stroke="${C.muted}" stroke-width="4" marker-end="url(#dn)"/>
    <defs><marker id="dn" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0L10 5L0 10z" fill="${C.muted}"/></marker></defs>
    <rect x="200" y="212" width="500" height="80" rx="18" fill="${C.greenT}" stroke="${C.green}" stroke-width="3"/>
    <circle cx="250" cy="252" r="24" fill="${C.green}"/><path d="M239 252 l8 8 l14 -16" stroke="#fff" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
    <text x="290" y="262" class="capb" fill="${C.green}">${a.world}</text>
  </svg>`;
  
  const artMass = `<svg viewBox="0 0 900 300" width="900" height="300">
    <line x1="60" y1="250" x2="860" y2="250" stroke="${C.muted}" stroke-width="2"/>
    <line x1="60" y1="20" x2="60" y2="250" stroke="${C.muted}" stroke-width="2"/>
    <path d="M60 60 C240 70 300 220 860 232" fill="none" stroke="${C.amber}" stroke-width="7"/>
    <path d="M60 225 C320 210 600 120 860 40" fill="none" stroke="${C.navy}" stroke-width="7"/>
    <text x="80" y="40" class="capb" fill="${C.warm}">${a.making}</text>
    <text x="860" y="30" text-anchor="end" class="capb" fill="${C.navy}">${a.carrying}</text>
    <text x="860" y="285" text-anchor="end" class="cap">${a.time}</text>
  </svg>`;
  
  const artEffort = `<div class="effort"><svg viewBox="0 0 900 330" width="900" height="330">
    <text x="270" y="34" text-anchor="middle" class="capb">${a.chatbot}</text>
    <text x="640" y="34" text-anchor="middle" class="capb">${a.tutor}</text>
    <rect x="190" y="110" width="160" height="140" rx="6" fill="${C.amber}"/>
    <text x="270" y="318" text-anchor="middle" class="bignum" fill="${C.warm}">${a.minus}</text>
    <rect x="560" y="104" width="160" height="12" rx="4" fill="${C.navy}"/>
    <text x="640" y="200" text-anchor="middle" class="bignum" fill="${C.navy}">≈ 0</text>
    <line x1="40" y1="110" x2="860" y2="110" stroke="${C.ink}" stroke-width="3"/>
    <text x="40" y="96" class="cap">${a.zeroLine}</text>
  </svg>
    <p class="note">${a.note}</p></div>`;
  
  const artHill = `<svg viewBox="0 0 900 300" width="900" height="300">
    <path d="M0 290 C200 290 380 60 560 50 C700 45 800 160 900 290 Z" fill="${C.greenT}"/>
    <path d="M0 290 C200 290 380 60 560 50 C700 45 800 160 900 290" fill="none" stroke="${C.green}" stroke-width="5"/>
    <circle cx="455" cy="78" r="34" fill="${C.amber}"/>
    <path d="M250 230 C300 190 350 140 400 112" fill="none" stroke="${C.navy}" stroke-width="5" stroke-dasharray="4 12" stroke-linecap="round" marker-end="url(#up)"/>
    <defs><marker id="up" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0L10 5L0 10z" fill="${C.navy}"/></marker></defs>
    <text x="700" y="250" text-anchor="middle" class="cap">${a.climb}</text>
  </svg>`;
  
  return [
    page(1, `<p class="kicker">${t.cover.kicker}</p><h1>${t.cover.h1}</h1><p class="sub">${t.cover.sub}</p>${zoom(-1)}`, "cover"),
    scene(0, artQuestion), scene(1, artCompare), scene(2, artMass), scene(3, artEffort), scene(4, artHill),
    page(7, `<h1 class="msg">${t.cover.h1}</h1>
    <ul class="rules">${t.rules.map(([b, x]) => `<li><b>${b}</b> ${x}</li>`).join("")}</ul>`, "message"),
    page(8, `<p class="endline">${t.end.line}</p>
    <div class="cta"><p>${t.end.read}</p><p class="link">${t.url}</p></div>
    <p class="ask">${t.end.ask}</p>`, "dark"),
  ].join("\n");
}

// Seeded random, so the dots are the same on every build and in every language
let seed;
const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);

const css = `
.bignum { font: 600 72px "Source Serif 4", serif; }
.effort { display: flex; flex-direction: column; align-items: center; gap: 6px; }
.effort .note { font-size: 25px; color: ${C.muted}; text-align: center; line-height: 1.35; }
.cover h1 { font-size: 104px; line-height: 1.04; }
.cover h1 span { color: ${C.amber}; }
.msg span { color: ${C.warm}; }
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
.cap { font: 400 28px Inter; fill: ${C.muted}; }
.capb { font: 700 31px Inter; fill: ${C.ink}; }
.scene .body { font-size: 39px; line-height: 1.42; }
.scene .body b { color: ${C.navy}; }
.essays { margin-top: auto; font-size: 28px; color: ${C.navy}; font-weight: 600; }
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

const langs = process.argv.slice(2).length ? process.argv.slice(2) : ["en", "fr"];
render(__dirname, Object.fromEntries(langs.map((l) => [l, build(T[l])])), css);
