---
name: new-post
description: Create and publish a new post on this Quarto site (AI, Honestly). Always asks first whether the post is an essay, an analysis, a note, a position paper or an overview, then follows the matching skill (write-essay, write-analysis, write-note, write-position-paper, write-overview) and the shared steps here. Every new post is first published to main as a draft in the review area (/drafts/), revised there, and promoted to the home page only on the user's approval. Use whenever the user asks to write, draft, create or publish a new post, article, essay, analysis, paper or note for the site.
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

## 2. Files: start in the drafts area

Every new post starts as a **draft**, published on `main` but only in the review area, and becomes a post when the user approves it (step 7).

| | Draft (review) | Post (published) |
|---|---|---|
| English | `drafts/<name>/` | `posts/YYYY-MM-DD-<name>/` |
| French | `fr/drafts/<name>/` | `fr/posts/YYYY-MM-DD-<name>/` |
| Listed on | https://scuenat.github.io/drafts/ (and `/fr/drafts/`) only | home page, archive, RSS feed, search, sitemap |

- `<name>` is a short slug from the title (lowercase, hyphens), with **no date**: the date is added on promotion, so the draft's URL stays the same while it is revised.
- `drafts/_metadata.yml` (and `fr/drafts/_metadata.yml`) give drafts the posts' author and license, plus `search: false` and `draft-preview: true`. `draft-banner.lua` then adds a "Draft, not yet published" banner and a `noindex` tag; `sitemap-lastmod.py` drops drafts from the sitemap; the home, archive and feed listings only read `posts/`. Do not add `draft: true` (the site's `draft-mode: gone` would remove the page altogether).
- **Links from a draft** to published posts go through the root: `../../posts/<slug>/index.qmd` (French draft: `../../posts/<slug>/` for French posts, `../../../posts/<slug>/` for English ones). The French draft points at the English draft's files with `../../../drafts/<name>/<file>`. The promotion script rewrites all of these.
- Do **not** add the draft to series pages (`agentic-coding.qmd`), `about.qmd` or other posts' read-next boxes yet: those links go in at promotion.
- `index.qmd`, plus `figs.py` and `figures/` when there are figures (copy the palette and helpers from the newest post's `figs.py`; write each figure as SVG for the page and 400 dpi PNG for the share image).
- Read the newest post of the same kind first and match its tone and structure:
  `grep -l '^kind: <kind>' posts/*/index.qmd | tail -1`

## 3. Front matter

```yaml
---
title: "Title in Title Case"
subtitle: "One line that says what the post claims"
description: "Under ~155 characters where possible: the Google snippet and the listing summary."
date: YYYY-MM-DD   # the drafting date; promote-draft.py sets the publication date
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

## 6. Verify and review

```bash
quarto render 2>&1 | grep -iE "warn|error"   # must print nothing
grep -c '<name>' _site/index.html _site/archive.html _site/index.xml _site/search.json _site/sitemap.xml   # all 0 while it is a draft
grep -o 'href="[^"]*<name>[^"]*"' _site/drafts/index.html   # listed on the drafts page
```

If Quarto is missing, download `https://github.com/quarto-dev/quarto-cli/releases/download/v1.6.42/quarto-1.6.42-linux-amd64.tar.gz` into the scratchpad and run `quarto-1.6.42/bin/quarto`. Also check the page for unresolved citations (`grep -c '?@' _site/drafts/<name>/index.html` → 0) and that every figure file exists.

Then follow the **review-draft** skill without being asked: send the full draft here as one PDF of the page exactly as the site will render it, with every figure, and give the draft's URL, `https://scuenat.github.io/drafts/<name>/`. Repeat after every revision. Skip the review only if the user asked to publish without it.

## 7. Publish: the draft first, then the post

Commit only sources (never `_site/` or `_preview/`), and push straight to `main`; no pull request. If the session started on a detached HEAD or another branch, carry the commit onto `main` (`git checkout -B main origin/main && git cherry-pick <sha>`). Retry a push that fails on a network error up to 4 times (2 s, 4 s, 8 s, 16 s). Pushing to `main` publishes through `.github/workflows/publish.yml`; after it succeeds, check the follow-up "pages build and deployment" run, and re-run it once if it fails on an upload error such as ECONNRESET.

**7a. Publish the draft** as soon as the first version renders cleanly, so the user can read it at https://scuenat.github.io/drafts/<name>/ and on the list at https://scuenat.github.io/drafts/:

```bash
git checkout main 2>/dev/null || git checkout -B main origin/main
git pull --rebase origin main
git add drafts/<name> fr/drafts/<name>
git commit -m "Draft: <Title> (<kind>, English and French)"
git push -u origin main
```

Each revision goes the same way (`git commit -m "Draft: <Title>, revised (<what changed>)"`), followed by a new review PDF. Drafts are not announced: no newsletter, no series page, no `updates:` entries.

**7b. Promote it**, only when the user says the draft is approved (for example "publish it", "promote it", "approved"):

```bash
python3 .claude/skills/new-post/promote-draft.py <name> [YYYY-MM-DD]   # default date: today
```

The script moves `drafts/<name>/` to `posts/<date>-<name>/` and `fr/drafts/<name>/` to `fr/posts/<date>-<name>/` with `git mv`, sets `date:` to the publication date, rewrites the links listed in step 2, and points any page that linked the draft at the new folder. Then:

- add the post where it belongs: series page (`agentic-coding.qmd` and `fr/agentic-coding.qmd`), the `::: {.series-note}`, read-next boxes of earlier posts if the series calls for it;
- render and check that the post now appears first on the home strip, in the archive and in the feed (`grep -o 'kind-badge kind-[a-z]*' _site/index.html | head -3`), that `_site/drafts/` no longer lists it, and that `grep -rn 'drafts/<name>' --include=*.qmd .` prints nothing;
- commit and push:

```bash
git add -A drafts fr/drafts posts/<date>-<name> fr/posts/<date>-<name> <series or other pages you touched>
git commit -m "New <kind>: <Title> (English and French)"
git push -u origin main
```

The old draft URL stops working after promotion; that is expected, since drafts are never linked from outside the review area.

A post that is already published is revised in place under `posts/` (see "Revising a published post"), not moved back to the drafts.
