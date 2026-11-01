---
name: review-draft
description: Show the user the complete draft of a post for review before anything is published, without being asked. Covers the full text, every figure, equations, tables and references, as an interactive Claude doc they can read, edit inline and comment on in the Claude app. Use automatically whenever a post or its French translation is drafted or revised (new-post, write-essay, write-analysis, write-note, write-position-paper, translate-fr), and whenever the user asks to see, read, review or preview a draft.
---

# Review a draft

The user reviews every post in full, with its pictures, before it goes live. Never make them ask for it. As soon as a draft or a revision is ready, put it in an **interactive doc** (Claude Docs), open it for them, then stop and wait.

Do not send HTML files for review: they do not load in the user's app. The HTML preview below is only for your own checks.

## 1. Check the draft renders (for you, not the user)

```bash
.claude/skills/review-draft/preview.sh posts/<YYYY-MM-DD-slug> [path/to/quarto]
```

This writes a self-contained `_preview/<slug>.html` (git-ignored). Fix every warning it prints. If Quarto is missing, download it as in **new-post** (step 6) into the scratchpad and pass the binary as the second argument. Screenshot the page with Playwright at 900 px wide and look at it. Check that no figure label overlaps a line, and that equations, tables and citations render.

## 2. Build the review doc

Follow the Claude Docs connector's own instructions (`guide` topic.index, topic.uploads, topic.editing). Load the docs tools with ToolSearch if they are deferred. The steps, in this order:

1. **Skeleton first.** Make one `batch` call that creates the doc. Name it `<Title> (draft for review)`. Give it the byline chips and one `pending` block per section: a review-copy block first, then one per `##` section of the post, then References.
2. **Open it** right away with the Artifact tool's `open` action and the link from the ack.
3. **Figures.** Upload every `figures/figNN.png` to the doc's artifact. Use one Artifact `publish` call with `url` set to the doc link, `asset: true` and `file_paths`. Then `create` one `blob` per returned id, in a single `batch`. Embed each figure as `![<alt>](blob/<minted id>)` where the post has it, followed by its caption as a paragraph starting with **Figure N.**
4. **Fill one section per `update` call**, in reading order, by replacing that section's pending block. Convert the Quarto source as follows:

   | In the .qmd | In the doc |
   |---|---|
   | Front matter | Review-copy section: one sentence saying this is the full draft and nothing is published until approval, then a table of kind, subtitle, description, topic tile(s) and word count |
   | Callout (`::: {.callout-…}`) | Blockquote; a Claims or Key takeaways callout becomes `### Claims` plus its list |
   | `[@key]`, `@key` | (Author year) / Author (year), matching the .bib |
   | Inline math `$…$` | Plain Unicode in the sentence (π, δ, ≈, ·) |
   | Display math `$$…$$ {#eq-x}` | A ```latex block of bare TeX; refer to it as "Equation N" in the text |
   | `@eq-x`, `@fig-x` | "Equation N", "Figure N" |
   | Links to other posts (`../<slug>/index.qmd`) | Full links `https://scuenat.github.io/posts/<slug>/` |
   | Tables and their `: **Table N.** …` caption | Pipe table, then the caption as a bold-led paragraph |
   | `::: {.read-next}`, disclaimer | **Read next** line with a link, then the italic disclaimer |
   | `## References` | A bullet list built from references.bib, with DOI or URL links |

   Copy the text word for word. The doc is the review copy of the exact draft, not a summary.
5. **Hand off.** End with one short line in your own words, for example: "<Title> is ready: read it, edit inline, or comment." Do not recap the doc. In the same reply, give only the points that need the author's judgement, such as unverified sources, strong wording, or a place where a personal example would help.

## 3. Revise, then publish only on approval

- **Comments and inline edits** in the doc are the user's review. When they come back, read what changed since your last revision (`read` with `{"kind":"view","sinceRev":<rev>}`) and the comment threads (`query` utterances). Carry every accepted change into the `.qmd`, word for word where they edited inline. Answer each comment thread in the doc, as the connector's comment rules say.
- **Changes asked in chat**: edit the `.qmd`, then apply the same change to the same doc with `update`. Keep the same doc and never create a second one for the same post. Re-upload a figure only if it changed.
- Keep the draft safe on a branch `draft/<slug>`: commit the sources, push that branch, and put the doc link in the commit message. Never commit `_preview/` or `_site/`. Pushing to `main` publishes, so never push the draft there before the user approves.
- After approval, continue with **new-post** step 5 (French) and step 7 (publish). Review the French version the same way, in a second doc, unless the user said the English approval covers it.
