---
name: write-analysis
description: Shape and write an analysis for this site (kind analysis, blue ANALYSIS badge) — a close reading of a paper, post or system, or a working/position paper with a model, data or simulation and predictions that could prove it wrong. Use when the user asks for an analysis, a paper or a position paper, or after new-post chose "Analysis". Starts by confirming the kind (essay, analysis or note) and defers to new-post for files, front matter, translation and publishing to main.
---

# Write an analysis

**First, confirm the kind.** If this skill was not reached through **new-post** after the user chose "Analysis", ask with AskUserQuestion: "Which kind of post should this be: an essay, an analysis or a note?" (options Analysis (Recommended) / Essay / Note). If the answer is not Analysis, switch to **write-essay** or **write-note**. Then follow **new-post** for files, front matter (`kind: analysis`), translation, verification and publishing to `main`.

## Two flavours

Ask which one, if it is not obvious:

- **Reading of a source** — a paper, a blog post, a system. First category `analysis`. Examples: `posts/2026-10-18-the-junior-colleague`, `posts/2026-10-22-review-the-intent-not-the-diff`.
- **Working or position paper** — the author's own claim, stated precisely and put to a test. First categories `paper` (and `position` if deliberately provocative); still `kind: analysis`. Add a `references.bib`, `bibliography: references.bib`, `google-scholar: true`, and a PDF next to `index.qmd` if one exists. Examples: `posts/2026-10-21-intent-is-the-source`, `posts/2026-10-23-stop-reviewing-pull-requests`, `posts/2026-09-29-show-what-changed`.

Ask the user for the source (link or file) or the claim, and any data, code or numbers to use. Read the source in full before writing; never summarise from memory.

## Shape

1. Opening callout: `**Analysis, <Month YYYY>.**` (or `**Position paper, …**`) — what is analysed, with a link; where the numbers come from ("Unless stated otherwise, numbers come from …"); that figures are drawn with `figs.py`.
2. `**In short.**` — the finding and the author's own position, in one paragraph.
3. Sections, in this order:
   - the problem or context (why it matters now);
   - what the source does or what the claim is, stated precisely (a small formal statement or cost model is welcome);
   - what the numbers or the simulation show — tables as `**Table N.**`, figures from data, with code in `figs.py` / `sim.py` and results in `results.json` when computed;
   - the author's own reading: what to keep, what to let go of;
   - **Where it breaks** / **What I am not claiming** — limits, threats to validity;
   - **What would prove me wrong** — concrete, checkable predictions.
4. `::: {.read-next}`, the disclaimer (*The views in this analysis are my own …*; "this paper" for papers), and `## References` / `::: {#refs}` when there is a bibliography.

## Style

- 2 000–6 000 words. Every number is sourced or computed in the repo; quote exact figures and say which are estimates.
- Keep the source's terms when describing it; be fair to it before disagreeing.
- Prefer one clear table over prose full of numbers.
