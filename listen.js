// "Listen" button on posts: the reader's own browser reads the post aloud (Web Speech API).
// Free: the voice runs on the reader's device, no service, no key, no audio files.
// Shown on posts and drafts (English and French) in browsers that can speak; elsewhere nothing appears.
//
// Storyteller mode: browsers ignore acting markup (SSML), so the "story" feel comes from
//   - the voice: the most natural one on the device (Natural, Premium, Enhanced, Siri, Google),
//     never the novelty voices; readers can pick another one, remembered per language;
//   - the pace: a little slower than the device default (STORY.rate);
//   - pauses: a breath between paragraphs, a longer one before a new section, a short one in lists;
//   - the text: dashes and brackets become pauses, "e.g." becomes "for example", headings end with a stop.
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
        voice: "Voix", label: "Écouter ce texte, lu par la voix de votre appareil", equation: "une équation" }
    : { listen: "Listen", pause: "Pause", resume: "Resume", stop: "Stop", speed: "Reading speed", min: "min",
        voice: "Voice", label: "Listen to this post, read by your device's voice", equation: "an equation" };

  // ---------- Storyteller settings ----------
  var STORY = {
    rate: 0.93,          // 1 is the device default; a story is told a little slower
    pitch: 1,            // changing the pitch makes most voices sound artificial
    pause: { paragraph: 550, item: 300, beforeHeading: 1000, afterHeading: 700, afterTitle: 1100, end: 0 }
  };

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

  // Shape written text for the ear
  var WORDS = fr
    ? [[/\bp\. ?ex\./gi, "par exemple"], [/\bc\.-à-d\./gi, "c'est-à-dire"], [/\betc\./gi, "et cetera"], [/\bvs\.?(?=\s)/gi, "contre"], [/\s&\s/g, " et "]]
    : [[/\be\.g\.,?/gi, "for example,"], [/\bi\.e\.,?/gi, "that is,"], [/\betc\./gi, "et cetera"], [/\bvs\.?(?=\s)/gi, "versus"], [/\s&\s/g, " and "]];
  function narrate(text, heading) {
    var t = text;
    WORDS.forEach(function (w) { t = t.replace(w[0], w[1]); });
    t = t.replace(/\s*[—–]\s*/g, ", ")          // dashes: a short pause
         .replace(/\s*\(\s*/g, ", ")            // brackets: said as an aside
         .replace(/\s*\)\s*(?=[.,;:!?])/g, "")
         .replace(/\s*\)\s*/g, ", ")
         .replace(/…/g, "...")
         .replace(/\s*,\s*([,.;:!?])/g, "$1")
         .replace(/^,\s*/, "")
         .replace(/\s+/g, " ")
         .trim();
    // A heading or title without a final stop is read with a rising, unfinished tone
    if (heading && !/[.!?…:]$/.test(t)) t += ".";
    return t;
  }

  function collect() {
    var items = [];
    var title = document.querySelector("#title-block-header h1.title");
    var sub = document.querySelector("#title-block-header .subtitle");
    if (title) items.push({ el: title, text: narrate(clean(title), true), pause: sub ? 500 : STORY.pause.afterTitle });
    if (sub) items.push({ el: sub, text: narrate(clean(sub), true), pause: STORY.pause.afterTitle });
    var end = main.querySelector(END);
    var nodes = main.querySelectorAll(READ);
    for (var i = 0; i < nodes.length; i++) {
      var n = nodes[i];
      if (end && (end === n || end.contains(n) || (end.compareDocumentPosition(n) & Node.DOCUMENT_POSITION_FOLLOWING))) break;
      if (n.closest(SKIP) || n.closest("#title-block-header")) continue;
      // A list item that holds paragraphs is read through those paragraphs
      if (n.tagName === "LI" && n.querySelector("p")) continue;
      var heading = /^H[2-4]$/.test(n.tagName);
      var text = narrate(clean(n), heading);
      if (text.length < 2) continue;
      if (heading && items.length) items[items.length - 1].pause = Math.max(items[items.length - 1].pause, STORY.pause.beforeHeading);
      var inList = n.tagName === "LI" || !!n.closest("li");
      items.push({ el: n, text: text, pause: heading ? STORY.pause.afterHeading : inList ? STORY.pause.item : STORY.pause.paragraph });
    }
    if (items.length) items[items.length - 1].pause = STORY.pause.end;
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
  var VOICE_KEY = "listen-voice-" + (fr ? "fr" : "en");
  // Apple's novelty and robotic voices: never chosen by default
  var NOVELTY = /\b(albert|bad news|bahh|bells|boing|bubbles|cellos|good news|jester|organ|superstar|trinoids|whisper|wobble|zarvox|fred|junior|ralph|kathy|grandma|grandpa|rocko|eddy|flo|reed|sandy|shelley|espeak)\b/i;
  var voices = [], voice = null;
  function score(v) {
    var n = v.name.toLowerCase(), s = 0;
    if (/natural|neural|premium|enhanced|siri/.test(n)) s += 6;
    if (/google/.test(n)) s += 3;
    if (fr ? /^fr[-_](fr|ch|be)/i.test(v.lang) : /^en[-_](gb|us)/i.test(v.lang)) s += fr ? 4 : 1;   // a French accent from Europe
    if (/compact/.test(n)) s -= 3;
    if (NOVELTY.test(n)) s -= 10;
    return s;
  }
  function loadVoices() {
    var want = fr ? "fr" : "en";
    voices = synth.getVoices()
      .filter(function (v) { return (v.lang || "").toLowerCase().indexOf(want) === 0 && !NOVELTY.test(v.name); })
      .sort(function (a, b) { return score(b) - score(a) || a.name.localeCompare(b.name); });
    var saved = null;
    try { saved = localStorage.getItem(VOICE_KEY); } catch (e) {}
    voice = voices.filter(function (v) { return v.voiceURI === saved; })[0] || voices[0] || null;
    if (typeof fillVoices === "function") fillVoices();
  }
  // "Microsoft Aria Online (Natural) - English (United States)" -> "Aria (Natural), US"
  function voiceLabel(v) {
    var name = v.name.split(" - ")[0].replace(/^(Microsoft|Apple)\s+/i, "").replace(/\s+Online\b/i, "");
    var region = (v.lang.split(/[-_]/)[1] || "").toUpperCase();
    return name + (region ? ", " + region : "");
  }

  // ---------- Controls ----------
  var RATES = [1, 1.25, 1.5, 0.85];   // multiples of STORY.rate
  var rateIdx = 0;
  try { rateIdx = Math.max(0, RATES.indexOf(parseFloat(localStorage.getItem("listen-rate")))); } catch (e) {}

  var items = collect();
  if (!items.length) return;
  var words = items.reduce(function (n, it) { return n + it.text.split(" ").length; }, 0);
  var minutes = Math.max(1, Math.round(words / (165 * STORY.rate)));

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
    '<button type="button" class="listen-stop" title="' + T.stop + '" aria-label="' + T.stop + '">' + ICON_STOP + '</button>' +
    '<select class="listen-voice" title="' + T.voice + '" aria-label="' + T.voice + '"></select>';
  meta.insertAdjacentElement("afterend", bar);
  var playBtn = bar.querySelector(".listen-play");
  var speedBtn = bar.querySelector(".listen-speed");
  var stopBtn = bar.querySelector(".listen-stop");
  var voiceSel = bar.querySelector(".listen-voice");

  function fillVoices() {
    voiceSel.innerHTML = "";
    voices.forEach(function (v, i) {
      var o = document.createElement("option");
      o.value = String(i);
      o.textContent = voiceLabel(v);
      if (v === voice) o.selected = true;
      voiceSel.appendChild(o);
    });
    bar.classList.toggle("has-voices", voices.length > 1);
  }
  loadVoices();
  if (synth.addEventListener) synth.addEventListener("voiceschanged", loadVoices);
  else synth.onvoiceschanged = loadVoices;

  // state: idle | playing | paused
  var state = "idle", idx = 0, queue = [], qi = 0, run = 0, wait = null;

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
      // End of a paragraph: take a breath (shorter when reading faster), then go on
      var pause = items[idx].pause / RATES[rateIdx];
      idx++;
      if (idx >= items.length) { stop(); return; }
      queue = chunks(items[idx].text); qi = 0;
      wait = setTimeout(function () { speakNext(token); }, pause);
      return;
    }
    if (qi === 0) mark(idx);
    var u = new SpeechSynthesisUtterance(queue[qi]);
    u.lang = fr ? "fr-FR" : "en-US";
    if (voice) { u.voice = voice; u.lang = voice.lang; }
    u.rate = STORY.rate * RATES[rateIdx];
    u.pitch = STORY.pitch;
    u.onend = function () { if (token !== run) return; qi++; speakNext(token); };
    u.onerror = function (e) {
      if (token !== run) return;
      if (e.error === "interrupted" || e.error === "canceled") return;
      qi++; speakNext(token);
    };
    synth.speak(u);
  }

  function halt() { run++; clearTimeout(wait); synth.cancel(); }
  // Pause and resume restart the current paragraph: synth.pause() is unreliable on Android.
  function play() {
    halt();
    state = "playing";
    queue = chunks(items[idx].text); qi = 0;
    render();
    var token = run;
    wait = setTimeout(function () { speakNext(token); }, 60);
  }
  function pause() { halt(); state = "paused"; render(); }
  function stop() { halt(); state = "idle"; idx = 0; mark(null); render(); }

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
  voiceSel.addEventListener("change", function () {
    voice = voices[+voiceSel.value] || voice;
    try { localStorage.setItem(VOICE_KEY, voice.voiceURI); } catch (e) {}
    if (state === "playing") play();   // hear the new voice straight away
  });
  // Tap a paragraph while listening to jump there
  main.addEventListener("click", function (e) {
    if (state === "idle" || e.target.closest("a, button, select, .listen")) return;
    for (var i = 0; i < items.length; i++) {
      if (items[i].el.contains(e.target)) { idx = i; play(); return; }
    }
  });
  window.addEventListener("pagehide", halt);

  render();
})();
