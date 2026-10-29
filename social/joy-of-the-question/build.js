// LinkedIn carousel for "The Joy of the Question", in English and French.
// Run from this folder: node build.js
// Writes carousel-en.pdf and carousel-fr.pdf (10 portrait pages, 1080 x 1350), plus
// preview PNGs in preview/. Shared style and renderer: ../lib.js. Numbers come from
// the studies cited in the essay.
const { C, render } = require("../lib");

const T = {
  en: {
    url: "scuenat.github.io",
    swipe: "Swipe",
    cover: {
      kicker: "Essay · October 2026",
      title: "The Joy of the Question",
      sub: "AI will solve more and more of our problems. What stays ours is choosing them, and caring about them.",
    },
    fear: {
      title: "The oldest fear",
      quote: "“The appearance of wisdom, not true wisdom.”",
      who: "King Thamus, on the invention of writing. Plato, <i>Phaedrus</i>",
      body: "Twenty-four centuries later, we ask the same question about AI. It reached gold-medal level at the Maths Olympiad in 2025 and settled problems open for decades in 2026.<br><br><b>What will this do to us?</b>",
    },
    rings: {
      title: "Speed is the machine’s game",
      how: ["HOW", "solve"], which: ["WHICH", "which problem, what counts as a good answer"],
      why: ["WHY", "why it matters at all"],
      notes: [["Machines", "take more of it every year"], ["Imagination and judgement", "a person frames and checks"], ["Ours to bring", "a reason to care"]],
      foot: "“Whoever has a <i>why</i> to live can bear almost any <i>how</i>.” Nietzsche",
    },
    go: {
      title: "Losing work, gaining height",
      big: "5.8 million",
      bigSub: "moves by professional Go players, 1950–2021",
      body: "After superhuman AI arrived in 2016, human moves became <b>better</b>, and <b>more novel</b>. The machines did not end the game. The game turned out to be bigger than people thought.",
      src: "Shin et al., <i>PNAS</i>, 2023. An association, not proof of cause.",
    },
    jagged: {
      title: "Same tool, different results",
      lead: "758 consultants with AI, compared with colleagues without it",
      g1: "On tasks AI does well", g2: "On a task just beyond what AI can do",
      r: [["more tasks completed", "+12.2%"], ["faster", "+25.1%"], ["correct answers", "−19 pts"]],
      body: "The tool did not say where its competence ended. <b>Knowing that was the person’s job.</b>",
      src: "Dell’Acqua et al., <i>Organization Science</i>, 2026",
    },
    effort: {
      title: "Effort builds the skill",
      lead: "~1,000 high-school students practised maths with AI. Grades compared with students who never had AI.",
      groups: ["During practice, with AI", "Exam, AI taken away"],
      legend: ["Plain chat assistant", "Tutor that gives hints, not answers"],
      body: "With the plain assistant, students learned less than with no AI at all. <b>Designed to keep the effort, the tutor did no harm.</b>",
      src: "Bastani et al., <i>PNAS</i>, 2025",
    },
    head: {
      title: "A well-made head",
      quote: "“Better a well-made head than a well-filled one.”",
      who: "Montaigne, <i>Essais</i>, 1580",
      steps: [["Information", "you read it or were given it"], ["Sourced", "you know where it comes from"], ["Tested", "you know what would prove it wrong"], ["Connected", "it fits with what you know"], ["Knowledge", "you can explain and defend it without the tool"]],
      body: "AI can fill any head. <b>The making is still ours.</b>",
    },
    why: {
      title: "What a machine has no reason to want",
      quote: "“One must imagine Sisyphus happy.”",
      who: "Albert Camus, 1942",
      body: "A machine may one day reach the top of every hill faster than we can. But being there first is not the same as being glad to be there.<br><br>The motivation to begin, the meaning found on the way, the joy of understanding something yourself: <b>that is the reason any of it is worth doing.</b>",
    },
    todo: {
      title: "What to do",
      us: "For ourselves",
      usItems: ["Write the question before opening the tool", "Decide what a good answer looks like", "Keep doing some things by hand, for the pleasure and the skill"],
      kids: "For our children",
      kidsItems: ["Let them try first", "Teach them to ask “how do you know?”", "Reward good questions as much as right answers", "Leave room for boredom and play"],
    },
    end: {
      line: "The machine will find answers. Whether they matter, and the joy of looking for them, is up to us.",
      read: "Full essay, sources and figure code",
      link: "scuenat.github.io",
      ask: "Questions or objections? Comment below.",
    },
  },
  fr: {
    url: "scuenat.github.io/fr",
    swipe: "Faites défiler",
    cover: {
      kicker: "Essai · octobre 2026",
      title: "La joie de la question",
      sub: "L’IA résoudra de plus en plus de nos problèmes. Ce qui reste à nous, c’est de les choisir, et d’y tenir.",
    },
    fear: {
      title: "La plus ancienne des craintes",
      quote: "« L’apparence de la sagesse, non la sagesse véritable. »",
      who: "Le roi Thamous, à propos de l’invention de l’écriture. Platon, <i>Phèdre</i>",
      body: "Vingt-quatre siècles plus tard, nous posons la même question à propos de l’IA. Elle a atteint le niveau de la médaille d’or aux Olympiades de mathématiques en 2025, et tranché en 2026 des problèmes ouverts depuis des décennies.<br><br><b>Qu’est-ce que cela va nous faire ?</b>",
    },
    rings: {
      title: "La vitesse est le jeu de la machine",
      how: ["COMMENT", "résoudre"], which: ["LEQUEL", "quel problème, ce qui compte comme une bonne réponse"],
      why: ["POURQUOI", "pourquoi cela compte"],
      notes: [["Les machines", "en prennent davantage chaque année"], ["Imagination et jugement", "une personne cadre et vérifie"], ["À nous de l’apporter", "une raison d’y tenir"]],
      foot: "« Celui qui a un <i>pourquoi</i> de vivre peut supporter presque n’importe quel <i>comment</i>. » Nietzsche",
    },
    go: {
      title: "Perdre du travail, gagner de la hauteur",
      big: "5,8 millions",
      bigSub: "de coups joués par des joueurs de go professionnels, 1950–2021",
      body: "Après l’arrivée d’une IA surhumaine en 2016, les coups humains sont devenus <b>meilleurs</b>, et <b>plus nouveaux</b>. Les machines n’ont pas mis fin au jeu. Le jeu s’est révélé plus grand qu’on ne le pensait.",
      src: "Shin et al., <i>PNAS</i>, 2023. Une association, pas une preuve de causalité.",
    },
    jagged: {
      title: "Le même outil, des résultats différents",
      lead: "758 consultants avec IA, comparés à des collègues sans IA",
      g1: "Sur des tâches que l’IA fait bien", g2: "Sur une tâche juste au-delà de ce que l’IA sait faire",
      r: [["de tâches accomplies", "+12,2 %"], ["plus rapides", "+25,1 %"], ["de bonnes réponses", "−19 pts"]],
      body: "L’outil ne disait pas où s’arrêtait sa compétence. <b>Le savoir, c’était le travail de la personne.</b>",
      src: "Dell’Acqua et al., <i>Organization Science</i>, 2026",
    },
    effort: {
      title: "L’effort construit la compétence",
      lead: "Près de 1 000 lycéens se sont exercés aux maths avec l’IA. Notes comparées à celles d’élèves qui n’ont jamais eu d’IA.",
      groups: ["Pendant l’exercice, avec l’IA", "À l’examen, sans l’IA"],
      legend: ["Simple assistant conversationnel", "Tuteur qui donne des indices, pas des réponses"],
      body: "Avec le simple assistant, les élèves ont moins appris que sans IA du tout. <b>Conçu pour garder l’effort, le tuteur n’a pas nui.</b>",
      src: "Bastani et al., <i>PNAS</i>, 2025",
    },
    head: {
      title: "Une tête bien faite",
      quote: "« Plutôt la tête bien faite que bien pleine. »",
      who: "Montaigne, <i>Essais</i>, 1580",
      steps: [["Information", "vous l’avez lue ou reçue"], ["Sourcée", "vous savez d’où elle vient"], ["Testée", "vous savez ce qui la réfuterait"], ["Reliée", "elle s’accorde avec ce que vous savez"], ["Connaissance", "vous pouvez l’expliquer et la défendre sans l’outil"]],
      body: "L’IA peut remplir n’importe quelle tête. <b>La faire reste notre affaire.</b>",
    },
    why: {
      title: "Ce qu’une machine n’a aucune raison de vouloir",
      quote: "« Il faut imaginer Sisyphe heureux. »",
      who: "Albert Camus, 1942",
      body: "Une machine atteindra peut-être un jour le sommet de chaque colline plus vite que nous. Mais y être le premier n’est pas la même chose qu’être heureux d’y être.<br><br>La motivation de commencer, le sens trouvé en chemin, la joie de comprendre par soi-même : <b>c’est la raison pour laquelle tout cela vaut la peine.</b>",
    },
    todo: {
      title: "Que faire",
      us: "Pour nous-mêmes",
      usItems: ["Écrire la question avant d’ouvrir l’outil", "Décider à quoi ressemble une bonne réponse", "Continuer à faire certaines choses à la main, pour le plaisir et la compétence"],
      kids: "Pour nos enfants",
      kidsItems: ["Les laisser essayer d’abord", "Leur apprendre à demander « comment le sais-tu ? »", "Récompenser les bonnes questions autant que les bonnes réponses", "Laisser de la place à l’ennui et au jeu"],
    },
    end: {
      line: "La machine trouvera des réponses. Qu’elles comptent, et la joie de les chercher, cela dépend de nous.",
      read: "L’essai complet, les sources et le code des figures",
      link: "scuenat.github.io/fr",
      ask: "Des questions ou des objections ? Commentez ci‑dessous.",
    },
  },
};

const N = 10;
const frame = (n, inner, { dark = false } = {}) => `
<section class="slide${dark ? " dark" : ""}">
  <header><span class="brand"><span class="dot"></span>AI, Honestly</span><span class="num">${n} / ${N}</span></header>
  <div class="content">${inner}</div>
  <footer><span>{{url}}</span>${n < N ? '<span class="next">{{swipe}} →</span>' : ""}</footer>
</section>`;

function rings(t) {
  // Three concentric circles, labels on the right
  return `<div class="rings">
  <svg viewBox="0 0 520 520" width="460" height="460">
    <circle cx="260" cy="260" r="250" fill="${C.greenT}" stroke="${C.green}" stroke-width="3"/>
    <circle cx="260" cy="260" r="170" fill="${C.amberT}" stroke="${C.amber}" stroke-width="3"/>
    <circle cx="260" cy="260" r="88" fill="${C.navy}"/>
    <text x="260" y="268" text-anchor="middle" class="rl" fill="#fff">${t.how[0]}</text>
    <text x="260" y="140" text-anchor="middle" class="rl" fill="${C.warm}">${t.which[0]}</text>
    <text x="260" y="56" text-anchor="middle" class="rl" fill="${C.green}">${t.why[0]}</text>
  </svg>
  <ul class="rnotes">
    <li style="--c:${C.navy}"><b>${t.how[0]}</b> · ${t.how[1]}<br><span>${t.notes[0][0]}: ${t.notes[0][1]}</span></li>
    <li style="--c:${C.amber}"><b>${t.which[0]}</b> · ${t.which[1]}<br><span>${t.notes[1][0]}: ${t.notes[1][1]}</span></li>
    <li style="--c:${C.green}"><b>${t.why[0]}</b> · ${t.why[1]}<br><span>${t.notes[2][0]}: ${t.notes[2][1]}</span></li>
  </ul></div>`;
}

function hbars(t) {
  // Bars scaled to 25.1 = full width; the negative one grows left from the axis
  const w = (v) => Math.abs(v) / 26 * 40;   // % of the track; axis at 45%
  const row = (r, v, col) => `<div class="hrow"><div class="hlab">${r[0]}</div>
    <div class="htrack"><div class="hbar ${v < 0 ? "neg" : ""}" style="width:${w(v)}%;background:${col}"></div>
    <span class="hval" style="color:${col}">${r[1]}</span></div></div>`;
  return `<p class="lead">${t.lead}</p>
  <div class="hgroup"><div class="hg">${t.g1}</div>${row(t.r[0], 12.2, C.navy)}${row(t.r[1], 25.1, C.navy)}</div>
  <div class="hgroup"><div class="hg">${t.g2}</div>${row(t.r[2], -19, C.red)}</div>`;
}

function vbars(t, lang) {
  // Grouped bars on one scale: +127 at the top, -17 below the axis
  const H = 300, top = 127, unit = H / (top + 20);
  const fmt = (v) => (v === 0 ? "≈ 0" : (v > 0 ? "+" : "−") + Math.abs(v) + (lang === "fr" ? " %" : "%"));
  const bar = (v, col) => `<div class="vb">
     <div class="vpos" style="height:${top * unit}px">${v > 0 ? `<span class="vv" style="color:${col}">${fmt(v)}</span><div style="height:${v * unit}px;background:${col}"></div>` : ""}</div>
     <div class="vneg" style="height:${17 * unit + 60}px">${v < 0 ? `<div style="height:${-v * unit}px;background:${col}"></div><span class="vv" style="color:${col}">${fmt(v)}</span>` : v === 0 ? `<span class="vv zero" style="color:${col}">${fmt(v)}</span>` : ""}</div></div>`;
  return `<p class="lead">${t.lead}</p>
  <div class="vchart">
    <div class="vgroup">${bar(48, C.amber)}${bar(127, C.navy)}<div class="vg">${t.groups[0]}</div></div>
    <div class="vgroup">${bar(-17, C.amber)}${bar(0, C.navy)}<div class="vg">${t.groups[1]}</div></div>
  </div>
  <div class="legend"><span><i style="background:${C.amber}"></i>${t.legend[0]}</span><span><i style="background:${C.navy}"></i>${t.legend[1]}</span></div>`;
}

function slides(t, lang) {
  const s = [];
  s.push(`<section class="slide cover">
    <header><span class="brand"><span class="dot"></span>AI, Honestly</span><span class="num">1 / ${N}</span></header>
    <div class="content"><p class="kicker">${t.cover.kicker}</p><h1>${t.cover.title}</h1><p class="sub">${t.cover.sub}</p>
    <p class="author">Stéphane Cuenat</p></div>
    <footer><span>{{url}}</span><span class="next">{{swipe}} →</span></footer></section>`);
  s.push(frame(2, `<h2>${t.fear.title}</h2><blockquote>${t.fear.quote}</blockquote><p class="who">${t.fear.who}</p><p class="body">${t.fear.body}</p>`));
  s.push(frame(3, `<h2>${t.rings.title}</h2>${rings(t.rings)}<p class="foot">${t.rings.foot}</p>`));
  s.push(frame(4, `<h2>${t.go.title}</h2><p class="big">${t.go.big}</p><p class="bigsub">${t.go.bigSub}</p><p class="body">${t.go.body}</p><p class="src">${t.go.src}</p>`));
  s.push(frame(5, `<h2>${t.jagged.title}</h2>${hbars(t.jagged)}<p class="body">${t.jagged.body}</p><p class="src">${t.jagged.src}</p>`));
  s.push(frame(6, `<h2>${t.effort.title}</h2>${vbars(t.effort, lang)}<p class="body">${t.effort.body}</p><p class="src">${t.effort.src}</p>`));
  s.push(frame(7, `<h2>${t.head.title}</h2><blockquote>${t.head.quote}</blockquote><p class="who">${t.head.who}</p>
    <ol class="steps">${t.head.steps.map((x, i) => `<li style="margin-left:${i * 34}px"><b>${x[0]}</b><span>${x[1]}</span></li>`).join("")}</ol>
    <p class="body">${t.head.body}</p>`));
  s.push(frame(8, `<h2>${t.why.title}</h2><blockquote>${t.why.quote}</blockquote><p class="who">${t.why.who}</p><p class="body">${t.why.body}</p>`));
  s.push(frame(9, `<h2>${t.todo.title}</h2>
    <div class="todo" style="--c:${C.amber}"><h3>${t.todo.us}</h3><ul>${t.todo.usItems.map((x) => `<li>${x}</li>`).join("")}</ul></div>
    <div class="todo" style="--c:${C.green}"><h3>${t.todo.kids}</h3><ul>${t.todo.kidsItems.map((x) => `<li>${x}</li>`).join("")}</ul></div>`));
  s.push(frame(10, `<p class="endline">${t.end.line}</p><div class="cta"><p>${t.end.read}</p><p class="link">${t.end.link}</p></div><p class="ask">${t.end.ask}</p>`, { dark: true }));
  return s.join("\n").replaceAll("{{url}}", t.url).replaceAll("{{swipe}}", t.swipe);
}

render(__dirname, { en: slides(T.en, "en"), fr: slides(T.fr, "fr") });
