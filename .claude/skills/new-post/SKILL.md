---
name: new-post
description: Create and publish a new post on this Quarto site (AI, Honestly). Always asks first whether the post is an essay, an analysis, a note, a position paper or an overview, then follows the matching skill (write-essay, write-analysis, write-note, write-position-paper, write-overview) and the shared steps here, and publishes directly to main. Use whenever the user asks to write, draft, create or publish a new post, article, essay, analysis, paper or note for the site.
---

# Create a new post

Every post on the site is one of five kinds. The kind sets the post's shape and the coloured badge on its card (home strip, theme tiles, archive):

| Kind | Badge | What it is | Typical length |
|---|---|---|---|
| `essay` | amber **ESSAY** / ESSAI | An argument or a reflection in the first person: one idea, carried through. Personal or speculative is fine. | 1 000–4 000 words |
| `analysis` | blue **ANALYSIS** / ANALYSE | A close reading of a source (paper, post, system), or a working paper that tests an idea with a model, a simulation or data. | 2 000–6 000 words |
| `note` | green **NOTE** / NOTE | Short and practical: assembles existing ideas into something you could ship, with a recipe and a way to test it. | 1 000–3 000 words |
| `position` | plum **POSITION PAPER** / ARTICLE DE POSITION | A deliberately provocative claim, stated precisely (often formally), defended with arguments and a model, with predictions that could prove it wrong. | 2 000–5 000 words |
| `overview` | teal **OVERVIEW** / PANORAMA | A map of a research area from many openly accessible sources: the main lines of work, how they relate, what is established and what is open. | 2 500–6 000 words |

## 1. Ask the kind — always

Before writing anything, ask with the AskUserQuestion tool, even if the request seems to imply a kind (then mark that kind as "(Recommended)" and put it first):

- Question: "Which kind of post should this be: an essay, an analysis, a note, a position paper or an overview?"
- Header: "Post kind"
- Options:
  - **Essay** — an argument or reflection in the first person, one idea carried through.
  - **Analysis** — a close reading of a source, or a working paper that tests an idea with a model or data.
  - **Note** — short and practical: a recipe you could ship, and a way to test it.
  - **Position paper** — a provocative claim, stated precisely and defended, with predictions that could prove it wrong.
  - **Overview** — a map of a research area from many accessible sources: main lines, what is settled, what is open.

AskUserQuestion takes at most four options: offer the four most plausible kinds for the request (recommended first) and drop the least likely one; the user can still type it under "Other", and the question text names all five.

In the same call, if they are not already clear, also ask for the topic tile(s) (`agentic-coding`, `fast-ai`, `human`, `dashboards`, `physics`, or none) and whether to publish a French translation in the same commit (recommended: yes).

Then load and follow the matching skill: **write-essay**, **write-analysis**, **write-note**, **write-position-paper** or **write-overview**. It gives the structure; the steps below are shared.

## 2. Files

- Folder: `posts/YYYY-MM-DD-slug/` with today's date and a short slug from the title (lowercase, hyphens).
- `index.qmd`, plus `figs.py` and `figures/` when there are figures (copy the palette and helpers from the newest post's `figs.py`; write each figure as SVG for the page and 400 dpi PNG for the share image).
- Read the newest post of the same kind first and match its tone and structure:
  `grep -l '^kind: <kind>' posts/*/index.qmd | tail -1`

## 3. Front matter

```yaml
---
title: "Title in Title Case"
subtitle: "One line that says what the post claims"
description: "Under ~155 characters where possible: the Google snippet and the listing summary."
date: YYYY-MM-DD
citation: true
toc-depth: 2
categories: [<kind>, ai, ...]   # first category = the kind (essay | analysis | note | overview); working papers: paper; position papers: paper, position
kind: <kind>   # card marker: essay | analysis | note | position | overview
topics: [<tile-id>]   # home-page theme tiles (index.qmd); [] lands in "Also on the site"
image: figures/fig01.png   # or ../../social-card.jpg when there is no figure
resources:
  - figs.py
  - figures/*.png
---
```

- `kind:` is required: without it the card shows no badge. Only `essay`, `analysis`, `note`, `position` and `overview` are valid.
- Categories are lowercase; reuse existing ones (`grep -h '^categories' posts/*/index.qmd | sort -u`).
- Author, license and the "Questions or objections?" footer come from `posts/_metadata.yml` and `discuss.lua`; do not add them.

## 4. House style (all kinds)

- Plain, short sentences, first person, no hype. Say what is claimed and what is not.
- Open with a `::: {.callout-note appearance="simple"}` that starts with the kind and month in bold (**Essay, November 2026.** / **Analysis, …** / **Note …** / **Position paper, …** / **Overview, …**), says what the post is and where figures come from.
- Then `**In short.**` — one paragraph a busy reader can stop after.
- Numbered `##` sections (`## 1. …`) for essays and notes; plain headings are fine for analyses.
- Figures: `![**Figure N.** Caption. Schematic, my own.](figures/figNN.svg){fig-alt="…"}` — always a full `fig-alt`.
- Series: link both ways ("A follow-up to …" / "Continued in …"); for the Agentic Coding series, add the `::: {.series-note}` line and update `agentic-coding.qmd` (and `fr/agentic-coding.qmd`).
- End with `::: {.read-next}` when there is a natural next post, then the disclaimer in `::: {.small}`:
  `*The views in this <essay|analysis|note|paper|overview> are my own and do not describe any product or plan of my employer.*`
- Never invent quotations, numbers or sources. Every external claim gets a link or a `[@key]` citation with a `references.bib`.

### Revising a published post

When a change matters to readers (a new section, a corrected result, a changed conclusion), add an entry to the post's front matter, newest first:

```yaml
updates:
  - date: YYYY-MM-DD
    note: "Added section 4 on what the model cannot see."
```

`updates.lua` shows it as an "Updated on …" note after the opening callout and sets the title block's modified date; the archive's "Recent changes" lists it. Typo fixes and small edits get no entry. When unsure, ask the user whether the change deserves one. Add the same entry, translated, to the French version (see **translate-fr**).

## 5. French version

If the user agreed, follow the **translate-fr** skill for the new post (it carries `kind:` over unchanged; the French badge labels come from `fr/index.qmd` and `fr/archive.qmd`).

## 6. Verify

```bash
quarto render 2>&1 | grep -iE "warn|error"   # must print nothing
grep -o 'kind-badge kind-[a-z]*' _site/index.html | head -3   # the new post's badge is first
```

If Quarto is missing, download `https://github.com/quarto-dev/quarto-cli/releases/download/v1.6.42/quarto-1.6.42-linux-amd64.tar.gz` into the scratchpad and run `quarto-1.6.42/bin/quarto`. Also check the post page for unresolved citations (`grep -c '?@' _site/posts/<slug>/index.html` → 0) and that every figure file exists.

Before publishing, follow the **review-draft** skill without being asked: send the full draft here as one PDF of the page exactly as the site will render it, with every figure, and wait for their approval. Repeat after every revision. Skip it only if the user asked to publish without review. Until approval, keep the draft on a `draft/<slug>` branch, never on `main`.

## 7. Publish directly to main

Commit only sources (never `_site/`), then push straight to `main`; no branch, no pull request:

```bash
git checkout main 2>/dev/null || git checkout -B main origin/main
git pull --rebase origin main
git add posts/<slug> fr/posts/<slug> <any page you touched>
git commit -m "New <kind>: <Title> (English and French)"
git push -u origin main
```

If the session started on a detached HEAD or another branch, carry the commit onto `main` (`git checkout -B main origin/main && git cherry-pick <sha>`). Retry a push that fails on a network error up to 4 times (2 s, 4 s, 8 s, 16 s). Pushing to `main` publishes through `.github/workflows/publish.yml`; after it succeeds, check the follow-up "pages build and deployment" run, and re-run it once if it fails on an upload error such as ECONNRESET.
