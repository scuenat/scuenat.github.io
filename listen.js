// "Listen" button on posts: the reader's own browser reads the post aloud (Web Speech API).
// Free: the voice runs on the reader's device, no service, no key, no audio files.
// Shown on posts and drafts (English and French) in browsers that can speak; elsewhere nothing appears.
// The text is read one paragraph at a time; the paragraph being read is highlighted.
// Skipped: code, equations, figures, tables, footnotes, the series note, and everything from the
// "Questions or objections?" note (discuss.lua) onward (sources, references).
(function () {
  var synth = window.speechSynthesis;
  if (!synth || !window.SpeechSynthesisUtterance) return;
  if (!/^\/(fr\/)?(posts|drafts)\/[^/]+\//.test(location.pathname)) return;
  var main = document.querySelector("main.content");
  var meta = document.querySelector("#title-block-header .quarto-title-meta");
  if (!main || !meta) return;

  var fr = (document.documentElement.lang || "").slice(0, 2) === "fr";
  var T = fr
    ? { listen: "Écouter", pause: "Pause", resume: "Reprendre", stop: "Arrêter", speed: "Vitesse de lecture", min: "min",
        label: "Écouter ce texte, lu par la voix de votre appareil", equation: "équation" }
    : { listen: "Listen", pause: "Pause", resume: "Resume", stop: "Stop", speed: "Reading speed", min: "min",
        label: "Listen to this post, read by your device's voice", equation: "equation" };

  // ---------- What to read ----------
  var SKIP = "pre, .sourceCode, .katex-display, figure, .quarto-figure, .cell-output-display, table, " +
    ".footnotes, .series-note, .post-updates, .listen, .callout-tip, #refs, .references, script, style, nav, .quarto-appendix";
  var READ = "p, h2, h3, h4, li, blockquote > p, dt, dd";
  var END = ".discuss, #refs, .references, .footnotes, .quarto-appendix-contents, .read-next";

  function clean(el) {
    var c = el.cloneNode(true);
    c.querySelectorAll(".katex").forEach(function (k) { k.replaceWith(" " + T.equation + " "); });
    c.querySelectorAll("sup, .footnote-ref, .anchorjs-link, .visually-hidden, .sr-only").forEach(function (n) { n.remove(); });
    return c.textContent.replace(/\s+/g, " ").trim();
  }

  function collect() {
    var items = [];
    var title = document.querySelector("#title-block-header h1.title");
    var sub = document.querySelector("#title-block-header .subtitle");
    if (title) items.push({ el: title, text: clean(title) });
    if (sub) items.push({ el: sub, text: clean(sub) });
    var end = main.querySelector(END);
    var nodes = main.querySelectorAll(READ);
    for (var i = 0; i < nodes.length; i++) {
      var n = nodes[i];
      if (end && (end === n || end.contains(n) || (end.compareDocumentPosition(n) & Node.DOCUMENT_POSITION_FOLLOWING))) break;
      if (n.closest(SKIP) || n.closest("#title-block-header")) continue;
      // A list item that holds paragraphs is read through those paragraphs
      if (n.tagName === "LI" && n.querySelector("p")) continue;
      var text = clean(n);
      if (text.length > 1) items.push({ el: n, text: text });
    }
    return items;
  }

  // Long paragraphs are split into sentence groups: some browsers stop a single long utterance after ~15 s.
  function chunks(text) {
    if (text.length <= 220) return [text];
    var parts = text.match(/[^.!?…]+[.!?…]+["»”’)]*\s*|[^.!?…]+$/g) || [text];
    var out = [], cur = "";
    parts.forEach(function (p) {
      if (cur && (cur + p).length > 220) { out.push(cur.trim()); cur = ""; }
      cur += p;
    });
    if (cur.trim()) out.push(cur.trim());
    return out;
  }

  // ---------- Voice ----------
  var voice = null;
  function pickVoice() {
    var want = fr ? "fr" : "en";
    var all = synth.getVoices().filter(function (v) { return (v.lang || "").toLowerCase().indexOf(want) === 0; });
    if (!all.length) return null;
    function score(v) {
      var n = v.name.toLowerCase(), s = 0;
      if (/natural|neural|premium|enhanced|siri/.test(n)) s += 4;
      if (/google/.test(n)) s += 2;
      if (fr ? /fr-fr|fr_fr/i.test(v.lang) : /en-(gb|us)|en_(gb|us)/i.test(v.lang)) s += 1;
      if (v.localService) s += 1;
      if (/compact|espeak/.test(n)) s -= 3;
      return s;
    }
    all.sort(function (a, b) { return score(b) - score(a); });
    return all[0];
  }
  voice = pickVoice();
  if (synth.addEventListener) synth.addEventListener("voiceschanged", function () { voice = pickVoice(); });

  // ---------- Controls ----------
  var RATES = [1, 1.25, 1.5, 0.85];
  var rateIdx = 0;
  try { rateIdx = Math.max(0, RATES.indexOf(parseFloat(localStorage.getItem("listen-rate")))); } catch (e) {}

  var items = collect();
  if (!items.length) return;
  var words = items.reduce(function (n, it) { return n + it.text.split(" ").length; }, 0);
  var minutes = Math.max(1, Math.round(words / 165));

  var ICON_PLAY = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M4.5 2.8v10.4L13 8z" fill="currentColor"/></svg>';
  var ICON_PAUSE = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M4 2.8h3v10.4H4zM9 2.8h3v10.4H9z" fill="currentColor"/></svg>';
  var ICON_STOP = '<svg viewBox="0 0 16 16" aria-hidden="true"><rect x="3.5" y="3.5" width="9" height="9" rx="1" fill="currentColor"/></svg>';

  var bar = document.createElement("div");
  bar.className = "listen";
  bar.setAttribute("role", "group");
  bar.setAttribute("aria-label", T.label);
  bar.innerHTML =
    '<button type="button" class="listen-play" aria-label="' + T.label + '"></button>' +
    '<button type="button" class="listen-speed" title="' + T.speed + '" aria-label="' + T.speed + '"></button>' +
    '<button type="button" class="listen-stop" title="' + T.stop + '" aria-label="' + T.stop + '">' + ICON_STOP + '</button>';
  meta.insertAdjacentElement("afterend", bar);
  var playBtn = bar.querySelector(".listen-play");
  var speedBtn = bar.querySelector(".listen-speed");
  var stopBtn = bar.querySelector(".listen-stop");

  // state: idle | playing | paused
  var state = "idle", idx = 0, queue = [], qi = 0, run = 0;

  function render() {
    bar.dataset.state = state;
    if (state === "playing") playBtn.innerHTML = ICON_PAUSE + "<span>" + T.pause + "</span>";
    else if (state === "paused") playBtn.innerHTML = ICON_PLAY + "<span>" + T.resume + "</span>";
    else playBtn.innerHTML = ICON_PLAY + "<span>" + T.listen + '</span><span class="listen-time">' + minutes + " " + T.min + "</span>";
    playBtn.setAttribute("aria-pressed", state === "playing" ? "true" : "false");
    speedBtn.textContent = String(RATES[rateIdx]).replace(".", fr ? "," : ".") + "×";
  }

  function mark(i) {
    document.querySelectorAll(".listen-current").forEach(function (e) { e.classList.remove("listen-current"); });
    if (i == null || !items[i]) return;
    var el = items[i].el;
    el.classList.add("listen-current");
    var r = el.getBoundingClientRect();
    if (r.top < 70 || r.bottom > window.innerHeight - 40) el.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  function speakNext(token) {
    if (token !== run || state !== "playing") return;
    if (qi >= queue.length) {
      idx++;
      if (idx >= items.length) { stop(); return; }
      queue = chunks(items[idx].text); qi = 0;
    }
    if (qi === 0) mark(idx);
    var u = new SpeechSynthesisUtterance(queue[qi]);
    u.lang = fr ? "fr-FR" : "en-US";
    if (voice) { u.voice = voice; u.lang = voice.lang; }
    u.rate = RATES[rateIdx];
    u.onend = function () { if (token !== run) return; qi++; speakNext(token); };
    u.onerror = function (e) {
      if (token !== run) return;
      if (e.error === "interrupted" || e.error === "canceled") return;
      qi++; speakNext(token);
    };
    synth.speak(u);
  }

  // Pause and resume restart the current paragraph: synth.pause() is unreliable on Android.
  function play() {
    run++;
    synth.cancel();
    state = "playing";
    queue = chunks(items[idx].text); qi = 0;
    render();
    var token = run;
    setTimeout(function () { speakNext(token); }, 60);
  }
  function pause() { run++; synth.cancel(); state = "paused"; render(); }
  function stop() { run++; synth.cancel(); state = "idle"; idx = 0; mark(null); render(); }

  playBtn.addEventListener("click", function () {
    if (state === "playing") pause(); else play();
  });
  stopBtn.addEventListener("click", stop);
  speedBtn.addEventListener("click", function () {
    rateIdx = (rateIdx + 1) % RATES.length;
    try { localStorage.setItem("listen-rate", String(RATES[rateIdx])); } catch (e) {}
    render();
    if (state === "playing") play();   // apply the new speed from the current paragraph
  });
  // Tap a paragraph while listening to jump there
  main.addEventListener("click", function (e) {
    if (state === "idle" || e.target.closest("a, button, .listen")) return;
    for (var i = 0; i < items.length; i++) {
      if (items[i].el.contains(e.target)) { idx = i; play(); return; }
    }
  });
  window.addEventListener("pagehide", function () { run++; synth.cancel(); });

  render();
})();
