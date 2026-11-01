---
name: write-position-paper
description: Shape and write a position paper for this site (kind position, plum POSITION PAPER badge) — a deliberately provocative claim in the form of a short scientific paper, stated precisely (often formally), defended with arguments, a model or a simulation, and with predictions that could prove it wrong. Use when the user asks for a position paper, a provocative paper or a thesis to defend, or after new-post chose "Position paper". Starts by confirming the kind (essay, analysis, note or position paper) and defers to new-post for files, front matter, translation and publishing to main.
---

# Write a position paper

**First, confirm the kind.** If this skill was not reached through **new-post** after the user chose "Position paper", ask with AskUserQuestion: "Which kind of post should this be: an essay, an analysis, a note or a position paper?" (options Position paper (Recommended) / Essay / Analysis / Note). If the answer is not Position paper, switch to **write-essay**, **write-analysis** or **write-note**. Then follow **new-post** for files, translation, verification and publishing to `main`.

## What makes it a position paper

A thesis the author defends on purpose, sharper than the evidence alone would force, in the form of a short scientific paper. It differs from an essay by its precision (a definition, a formal statement or a cost model) and from an analysis by its stance: it argues for a change, and it says exactly what would show it wrong. Examples: `posts/2026-10-21-intent-is-the-source`, `posts/2026-10-23-stop-reviewing-pull-requests`.

Ask the user, if not given: the thesis in one sentence, what it is provoking against (the current practice or belief), and whether there is a model, a simulation or data to support it.

## Front matter

On top of the shared fields from **new-post**:

```yaml
subtitle: "A provocative position paper: <the thesis in a few words>"
description: "A deliberately provocative position paper. …"
citation: true
google-scholar: true
bibliography: references.bib
categories: [paper, position, ai, ...]
kind: position   # card marker: essay | analysis | note | position
```

Put the sources in `references.bib` and cite them as `[@key]`. Simulation code goes in `sim.py`, its output in `results.json`, figures in `figs.py`; list them under `resources:`.

## Shape

1. `::: {.callout-warning appearance="simple"}` — **A provocative paper, on purpose.** Say what form it takes (thesis, model, simulation, predictions), what it follows from, and how to read it.
2. `**Abstract.**` — one paragraph, as in a paper: context, the model in one formula if there is one, the rule it implies, the conditions, the test.
3. `::: {.callout-tip appearance="simple" icon="false"}` with `## Claims` — four to six numbered, bold-led claims, each one line.
4. Numbered sections:
   - `## 1. Introduction` — the practice being challenged and why now;
   - `## 2. Background` — what the practice was for; prior work, credited;
   - `## 3.` a minimal definition or cost model (KaTeX: `$…$`, `$$…$$`);
   - `## 4.` the arguments, or the rule in practice;
   - `## 5.` a simulation or worked example, if any (with **Table N.** / **Figure N.**);
   - `## 6. Predictions and a test protocol` — concrete, falsifiable, with what result would refute the thesis;
   - `## 7. Objections and limitations` — the strongest counter-arguments, met honestly;
   - `## 8. Conclusion` — the thesis in one line the reader will remember.
5. `::: {.read-next}`, the disclaimer (*The views in this paper are my own and do not describe any product or plan of my employer.*), then `## References` and `::: {#refs}`.

## Style

- 2 000–5 000 words. Provocative in the thesis, careful in the argument: never overstate the evidence, and label what is modelled versus measured.
- Each claim in the Claims box must be argued in the body and tied to a prediction.
- Plain words around the formalism: every symbol is explained in a sentence the first time it appears.
