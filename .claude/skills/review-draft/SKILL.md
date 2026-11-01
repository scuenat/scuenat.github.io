---
name: review-draft
description: Show the user the complete draft of a post exactly as it will render on the site, before anything is published, without being asked. Renders the page with the site's own theme and sends it here in the conversation as phone-width screenshots, covering the full text, every figure, equations, tables and references. Use automatically whenever a post or its French translation is drafted or revised (new-post, write-essay, write-analysis, write-note, write-position-paper, translate-fr), and whenever the user asks to see, read, review or preview a draft.
---

# Review a draft

The user reviews every post in full, as it will look on the site, before it goes live. Never make them ask for it. As soon as a draft or a revision is ready, send it here as screenshots of the real rendered page, then stop and wait.

Do not send HTML files: they do not load in the user's app. Do not use a separate doc, because it does not look like the site. Use a doc only if the user asks for one to comment on.

## 1. Render and screenshot

```bash
.claude/skills/review-draft/preview.sh posts/<YYYY-MM-DD-slug> [path/to/quarto] [width]
# French: .claude/skills/review-draft/preview.sh fr/posts/<YYYY-MM-DD-slug> [path/to/quarto]
```

- The script renders only this page inside the site project, so it gets the real theme, navbar, badges, callouts, citations and footer. It writes `_site/<post>/index.html`.
- It then serves `_site` locally and screenshots the page at phone width (430 px by default, at 2x), as `_preview/<slug>/page-NN.png`. `_preview/` is git-ignored.
- Each screenshot ends between blocks: never through a figure, a table, a callout or an equation, and never right below a heading.
- The site loads KaTeX from a CDN that the sandbox may block. The script then fetches KaTeX with `npm pack` once and serves it locally, so equations render in the screenshots as they will online.
- If Quarto is missing, download it as in **new-post** (step 6) into the scratchpad and pass the binary as the second argument.
- Fix every warning it prints and run it again.

## 2. Check before sending

Look at the screenshots yourself. A contact sheet of all pages, made with matplotlib, is the quickest way. Check that:
- every figure appears whole and no label overlaps a line or runs off the edge (on phones the site shows figures edge to edge, so keep `savefig.pad_inches` at 0.35 or more in `figs.py`);
- equations are typeset, with no raw `\pi` or `$…$` showing;
- tables are readable and citations show as names and years, not `?@key`.

Fix what you find in the post or in `figs.py`, then rerun step 1.

## 3. Send it here

1. One **SendUserFile** call with every `page-NN.png` in order, `display: "render"` and `status: "normal"`. Leave out a last page that holds only the site footer. The caption names the post and says it is the full draft as it will render on a phone.
2. In the reply, give only:
   - kind, title, topic tile(s) and word count of the body;
   - the thesis or main point in two or three sentences;
   - the few points that need the author's judgement, such as unverified sources, strong wording, or a place where a personal example would help;
   - the question: what to change, or approve to publish.

Do not paste the text into the chat as well: the screenshots are the review copy.

## 4. Revise, then publish only on approval

- Apply every change the user asks for, then run steps 1 to 3 again and send the new screenshots. Each revision goes through the same loop.
- Keep the draft safe on a branch `draft/<slug>`: commit the sources, push that branch, and never commit `_preview/` or `_site/`. Pushing to `main` publishes, so never push the draft there before the user approves.
- After approval, continue with **new-post** step 5 (French) and step 7 (publish). Send the French version the same way, unless the user said the English approval covers it.
