// LinkedIn carousel across the essays of AI, Honestly, in English and French.
// One message: AI made making cheap; what it did not make cheap is now the work.
// Each essay is one step of that thread, shown as a bar at the top of the page.
// Run from this folder: node build.js [en] [fr] (English only by default; the French text
// is ready but not reviewed yet). Shared style and renderer: ../lib.js.
const { C, render } = require("../lib");

const STEPS = [
  { essay: "Fast AI", fr: "Fast AI", col: C.navy },
  { essay: "Where Memory Lives", fr: "Là où vit la mémoire", col: C.navy },
  { essay: "Coherence Is Measurable", fr: "La cohérence se mesure", col: C.navy },
  { essay: "Intent Is the Source", fr: "L’intention est la source", col: C.amber },
  { essay: "Stop Reviewing Pull Requests", fr: "Arrêtez de relire les pull requests", col: C.amber },
  { essay: "Work Has Mass", fr: "Le travail a une masse", col: C.amber },
  { essay: "Show What Changed, Not the Data", fr: "Montrer ce qui a changé, pas les données", col: C.green },
  { essay: "The Joy of the Question", fr: "La joie de la question", col: C.green },
];

const T = {
  en: {
    url: "scuenat.github.io", swipe: "Swipe", from: "Essay",
    verbs: ["Remember", "Store", "Trust", "Specify", "Check", "Carry", "Notice", "Care"],
    cover: {
      kicker: "AI, Honestly · eight essays, one thread",
      title: "AI made making cheap.",
      sub: "What it didn’t make cheap is now the work.",
    },
    shift: {
      title: "The shift",
      cheap: "Cheap now", cheapItems: ["Writing code", "Drafting text", "Generating answers", "Producing features"],
      dear: "Still expensive", dearItems: ["Remembering what we learned", "Trusting an answer", "Checking what matters", "Carrying what we made", "Knowing why it matters"],
      body: "Eight essays, written over one month. Each one looks at a different piece of what stays expensive.",
    },
    steps: [
      { claim: "Learn slowly, once. Act fast, every time.",
        body: "Most agents reason from scratch on every run, so they repeat their mistakes and forget what they learned. Use the large model once, to build a memory people can inspect. Let small, explainable models run the routine. Keep the agent for the exceptions." },
      { claim: "Keep in the weights what you use on every word. Look up the rest.",
        stat: "19,000", statSub: "tokens: the point where a small model’s working memory outweighs the model itself (1B parameters, 4-bit weights)",
        body: "Weights are dense but hard to change. A table changes one row at a time." },
      { claim: "Agreement is a cheap alarm. But coherent is not true.",
        stat: "99.8%", statSub: "right when ten networks all agreed. When they all learned the same shortcut, agreement did no better than chance.",
        body: "Disagreement tells you when to look it up. Only the world tells you when everyone is wrong together." },
      { claim: "Intent is the new source code.",
        body: "What we write moves up a level: intent plus the checks that prove it. Code becomes an output, still readable, rarely written. The new language is exactly as precise as its tests." },
      { claim: "Approve what you cannot undo. Watch everything else.",
        body: "Reviewing every change made sense when fixes were slow and code was typed by hand. Now: rules for every session, merge on green, a daily audit of the whole codebase, and a person at the point of no return." },
      { claim: "Everything you make, you carry.",
        body: "AI lowers the cost of making, not of carrying. Every feature, test and document needs attention for as long as it lives. A process is mass too: in a heavier world, frameworks like Scrum and SAFe must get lighter, not heavier." },
      { claim: "Show what changed in our understanding, not the data.",
        body: "Most weeks, a good dashboard is empty. But a quiet screen must earn its silence: say what it checked, what it could not explain, and when it last proved it can still see." },
      { claim: "What stays ours is choosing the question, and caring about it.",
        body: "A machine has no reason of its own to want an answer. We do. Students who practised with a plain chatbot scored 17% lower once it was taken away: keep the effort that builds the skill, and the joy." },
    ],
    message: {
      title: "The thread",
      line: "When making is cheap, the value moves to everything around it.",
      recap: ["Remember what you learned", "Store it where it’s cheap to use", "Trust, but check against the world", "Specify the intent, not the code", "Check only what you can’t undo", "Carry less", "Notice what changed", "Care why it matters"],
    },
    end: {
      line: "Which step is the hardest where you work?",
      read: "All essays, with code and data, in English and French",
      link: "scuenat.github.io",
      ask: "Tell me in the comments. Good questions often become the next essay.",
    },
  },
  fr: {
    url: "scuenat.github.io/fr", swipe: "Faites défiler", from: "Essai",
    verbs: ["Retenir", "Ranger", "Se fier", "Spécifier", "Vérifier", "Porter", "Remarquer", "Tenir à"],
    cover: {
      kicker: "AI, Honestly · huit essais, un fil",
      title: "L’IA a rendu la fabrication bon marché.",
      sub: "Ce qu’elle n’a pas rendu bon marché, c’est désormais le travail.",
    },
    shift: {
      title: "Le basculement",
      cheap: "Bon marché", cheapItems: ["Écrire du code", "Rédiger un texte", "Produire des réponses", "Livrer des fonctionnalités"],
      dear: "Toujours cher", dearItems: ["Retenir ce que l’on a appris", "Se fier à une réponse", "Vérifier ce qui compte", "Porter ce que l’on a fait", "Savoir pourquoi cela compte"],
      body: "Huit essais, écrits en un mois. Chacun regarde une partie différente de ce qui reste cher.",
    },
    steps: [
      { claim: "Apprendre lentement, une fois. Agir vite, à chaque fois.",
        body: "La plupart des agents raisonnent de zéro à chaque exécution : ils répètent leurs erreurs et oublient ce qu’ils ont appris. Utilisez le grand modèle une fois, pour construire une mémoire que l’on peut inspecter. Laissez de petits modèles explicables faire la routine. Gardez l’agent pour les exceptions." },
      { claim: "Gardez dans les poids ce qui sert à chaque mot. Cherchez le reste.",
        stat: "19 000", statSub: "tokens : le point où la mémoire de travail d’un petit modèle pèse plus que le modèle lui-même (1 milliard de paramètres, poids en 4 bits)",
        body: "Les poids sont denses mais difficiles à modifier. Une table se modifie ligne par ligne." },
      { claim: "L’accord est une alarme bon marché. Mais cohérent ne veut pas dire vrai.",
        stat: "99,8 %", statSub: "de bonnes réponses quand dix réseaux étaient tous d’accord. Quand ils avaient tous appris le même raccourci, l’accord ne faisait pas mieux que le hasard.",
        body: "Le désaccord dit quand aller vérifier. Seul le monde dit quand tout le monde se trompe ensemble." },
      { claim: "L’intention est le nouveau code source.",
        body: "Ce que nous écrivons monte d’un niveau : l’intention, plus les vérifications qui la prouvent. Le code devient un produit, toujours lisible, rarement écrit. Le nouveau langage est exactement aussi précis que ses tests." },
      { claim: "Approuvez ce que vous ne pouvez pas défaire. Surveillez le reste.",
        body: "Relire chaque changement avait du sens quand les corrections étaient lentes et le code tapé à la main. Désormais : des règles pour chaque session, la fusion quand tout est vert, un audit quotidien de tout le code, et une personne au point de non-retour." },
      { claim: "Tout ce que vous fabriquez, vous le portez.",
        body: "L’IA baisse le coût de fabriquer, pas celui de porter. Chaque fonctionnalité, chaque test, chaque document demande de l’attention aussi longtemps qu’il existe. Un processus aussi a une masse : dans un monde plus lourd, Scrum et SAFe doivent s’alléger, pas s’alourdir." },
      { claim: "Montrer ce qui a changé dans notre compréhension, pas les données.",
        body: "La plupart des semaines, un bon tableau de bord est vide. Mais un écran silencieux doit mériter son silence : dire ce qu’il a vérifié, ce qu’il n’a pas su expliquer, et quand il a prouvé pour la dernière fois qu’il voit encore." },
      { claim: "Ce qui reste à nous, c’est de choisir la question, et d’y tenir.",
        body: "Une machine n’a aucune raison à elle de vouloir une réponse. Nous, si. Des lycéens qui s’étaient exercés avec un simple chatbot ont obtenu 17 % de moins une fois l’outil retiré : gardez l’effort qui construit la compétence, et la joie." },
    ],
    message: {
      title: "Le fil",
      line: "Quand fabriquer ne coûte plus rien, la valeur se déplace vers tout ce qui l’entoure.",
      recap: ["Retenir ce que l’on a appris", "Le ranger là où il coûte peu", "Se fier, mais vérifier face au monde", "Spécifier l’intention, pas le code", "Vérifier seulement l’irréversible", "Porter moins", "Remarquer ce qui a changé", "Tenir à ce qui compte"],
    },
    end: {
      line: "Quelle étape est la plus difficile là où vous travaillez ?",
      read: "Tous les essais, avec code et données, en anglais et en français",
      link: "scuenat.github.io/fr",
      ask: "Dites-le-moi en commentaire. Les bonnes questions deviennent souvent l’essai suivant.",
    },
  },
};

const N = 2 + STEPS.length + 2;

const page = (n, inner, cls = "") => `
<section class="slide ${cls}">
  <header><span class="brand"><span class="dot"></span>AI, Honestly</span><span class="num">${n} / ${N}</span></header>
  <div class="content">${inner}</div>
  <footer><span>{{url}}</span>${n < N ? '<span class="next">{{swipe}} →</span>' : ""}</footer>
</section>`;

// The thread: eight verbs, the current one highlighted, the ones before it done
const thread = (t, k) => `<ol class="thread">${t.verbs.map((v, i) =>
  `<li class="${i < k ? "done" : i === k ? "now" : ""}" style="--c:${STEPS[i].col}"><i></i><span>${v}</span></li>`).join("")}</ol>`;

function slides(t, lang) {
  const s = [];
  s.push(page(1, `<p class="kicker">${t.cover.kicker}</p><h1>${t.cover.title}</h1><p class="sub">${t.cover.sub}</p>${thread(t, -1)}`, "cover"));
  s.push(page(2, `<h2>${t.shift.title}</h2>
    <div class="shift">
      <div class="col cheap"><h3>${t.shift.cheap}</h3><ul>${t.shift.cheapItems.map((x) => `<li>${x}</li>`).join("")}</ul></div>
      <div class="arrow">→</div>
      <div class="col dear"><h3>${t.shift.dear}</h3><ul>${t.shift.dearItems.map((x) => `<li>${x}</li>`).join("")}</ul></div>
    </div><p class="body">${t.shift.body}</p>`));
  t.steps.forEach((st, k) => {
    const stat = st.stat ? `<div class="stat"><p class="sn" style="color:${STEPS[k].col}">${st.stat}</p><p class="ss">${st.statSub}</p></div>` : "";
    s.push(page(3 + k, `${thread(t, k)}
      <p class="step" style="color:${STEPS[k].col}">${String(k + 1).padStart(2, "0")} · ${t.verbs[k]}</p>
      <h2 class="claim">${st.claim}</h2>${stat}<p class="body">${st.body}</p>
      <p class="essay">${t.from} · <b>${lang === "fr" ? STEPS[k].fr : STEPS[k].essay}</b></p>`, "pinned"));
  });
  s.push(page(N - 1, `${thread(t, 8)}<h2>${t.message.title}</h2><p class="mline">${t.message.line}</p>
    <ol class="recap">${t.message.recap.map((x, i) => `<li style="--c:${STEPS[i].col}"><b>${String(i + 1).padStart(2, "0")}</b>${x}</li>`).join("")}</ol>`, "pinned"));
  s.push(page(N, `<p class="endline">${t.end.line}</p><div class="cta"><p>${t.end.read}</p><p class="link">${t.end.link}</p></div><p class="ask">${t.end.ask}</p>`, "dark"));
  return s.join("\n").replaceAll("{{url}}", t.url).replaceAll("{{swipe}}", t.swipe);
}

const css = `
.pinned .content { justify-content: flex-start; padding-top: 44px; gap: 34px; }
.pinned .thread { margin-bottom: 18px; }
.pinned .body { font-size: 40px; }
.cover h1 { font-size: 104px; }
.cover .sub { font-size: 52px; color: ${C.amber}; font-weight: 600; }
.cover .thread { margin-top: 40px; }
.cover .thread span { color: #aab6c3; }
.thread { list-style: none; display: grid; grid-template-columns: repeat(8, 1fr); gap: 8px; }
.thread li { display: flex; flex-direction: column; gap: 10px; }
.thread i { height: 12px; border-radius: 6px; background: ${C.rule}; }
.thread span { font-size: 21px; color: ${C.muted}; text-align: center; white-space: nowrap; }
.thread li.done i { background: var(--c); opacity: .45; }
.thread li.now i { background: var(--c); height: 18px; margin-top: -3px; }
.thread li.now span { color: var(--c); font-weight: 800; }
.cover .thread i { background: rgba(255,255,255,.25); }
.step { font-size: 30px; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; margin-top: 20px; }
h2.claim { font-size: 80px; color: ${C.ink}; margin-top: -10px; }
.stat { display: flex; flex-direction: column; gap: 4px; }
.sn { font-family: "Source Serif 4", serif; font-weight: 600; font-size: 104px; line-height: 1; }
.ss { font-size: 27px; color: ${C.muted}; line-height: 1.35; }
.essay { font-size: 26px; color: ${C.muted}; border-top: 2px solid ${C.rule}; padding-top: 18px; }
.essay b { color: ${C.navy}; }
.shift { display: grid; grid-template-columns: 1fr 70px 1.25fr; align-items: center; }
.shift .arrow { font-size: 64px; color: ${C.amber}; text-align: center; }
.shift h3 { font-size: 32px; margin-bottom: 18px; }
.shift ul { list-style: none; display: flex; flex-direction: column; gap: 14px; }
.shift li { font-size: 31px; padding: 14px 20px; border-radius: 10px; }
.cheap li { background: #efece6; color: ${C.muted}; text-decoration: line-through; text-decoration-color: rgba(95,107,118,.5); }
.dear li { background: #fff; border: 2px solid ${C.rule}; border-left: 8px solid ${C.amber}; font-weight: 600; }
.mline { font-family: "Source Serif 4", serif; font-size: 52px; line-height: 1.22; }
.recap { list-style: none; display: grid; grid-template-columns: 1fr 1fr; gap: 14px 24px; }
.recap li { font-size: 28px; line-height: 1.25; border-left: 7px solid var(--c); padding: 6px 0 6px 18px; }
.recap b { display: block; font-size: 22px; color: var(--c); letter-spacing: .08em; }
`;

const langs = process.argv.slice(2).length ? process.argv.slice(2) : ["en"];
render(__dirname, Object.fromEntries(langs.map((l) => [l, slides(T[l], l)])), css);
