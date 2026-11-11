---
name: write-overview
description: Shape and write an overview for this site (kind overview, teal OVERVIEW badge, PANORAMA in French) — a map of a research area built from many openly accessible sources, showing the main lines of work, how they relate, what is established and what is still open. Use when the user asks for an overview, a survey, a state of the art, a panorama or "what is known about X", or after new-post chose "Overview". Starts by confirming the kind (essay, analysis, note, position paper or overview) and defers to new-post for files, front matter, translation, the drafts area and publishing.
---

# Write an overview

**First, confirm the kind.** If this skill was not reached through **new-post** after the user chose "Overview", ask with AskUserQuestion: "Which kind of post should this be: an essay, an analysis, a note, a position paper or an overview?" (options Overview (Recommended) / Analysis / Essay / Position paper). If the answer is not Overview, switch to **write-analysis**, **write-essay**, **write-note** or **write-position-paper**. Then follow **new-post** for files, front matter (`kind: overview`, first category `overview`), translation, verification, the drafts area (`drafts/<name>/`, reviewed at /drafts/) and publishing.

## What makes it an overview

An analysis reads one source closely; an overview maps a field. It gathers many sources (typically 10–25), groups them into a few lines of work, shows how they answer the same question differently, and separates what is established from what is claimed and what is open. The author's view is welcome, but it comes last and is labelled as such. It is a way in for a curious reader, not a verdict.

## Sources

- Ask the user for the topic, the period (for example 2020–2026) and any papers they want included.
- Prefer openly accessible sources (open-access journals, arXiv, bioRxiv, PMC, proceedings, lab or institute pages) so a reader can follow every link.
- Verify each source's authors, title, venue, year and DOI or URL before citing it; put every one in `references.bib` and cite with `[@key]`. Add `bibliography: references.bib` and `google-scholar: true`.
- Report claims as the sources state them ("the authors report …"), with exact numbers only when a source gives them. Never invent a number, a quotation or a result.
- Say in the opening callout how the sources were read: in full, or from abstracts and the publishers' or institutes' summaries. If only abstracts were available, say so plainly and keep claims to what the abstracts state.

## Shape

1. Opening callout: `**Overview, <Month YYYY>.**` — what area is mapped, the period covered, how sources were chosen and read, and that figures are schematic and drawn with `figs.py`.
2. `**In short.**` — the map in one paragraph: the question, the main lines, and where things stand.
3. Sections, in this order (plain or numbered headings):
   - **The question** — why it matters and how it is usually framed;
   - **A map** — one figure or table that places the lines of work side by side (a `**Table N.**` with columns such as approach / what is local / what is learned / best reported result / source);
   - one section per line of work (3–6), each with what it proposes, the key results with sources, and its known limits;
   - **What is established, what is open** — short lists;
   - **My reading** — the author's own view, clearly marked as opinion;
   - **Where to start** — 3–5 sources to read first, each with one line on why.
4. `::: {.read-next}` when there is a natural next post, then in `::: {.small}` a non-exhaustiveness note before the usual disclaimer (*This overview is not exhaustive. It maps representative, openly accessible work from <period> as I could read it … Missing work and corrections are welcome.*; in French *Ce panorama n'est pas exhaustif. …*), then *The views in this overview are my own …*, then `## References` / `::: {#refs}`.

## Style

- 2 500–6 000 words. Plain sentences, no hype; be fair to every line of work.
- One clear map beats many small figures; keep schematic figures honest (label them "Schematic, my own").
- Date-stamp the field: say what period is covered and that it will age.
