---
name: review-draft
description: Show the user the complete draft of a post exactly as it will render on the site, while it is still a draft in the review area (/drafts/) and before it is promoted to the home page, without being asked. Renders the page with the site's own theme and sends it here as ONE PDF document at phone width, with the full text, every figure, equations, tables and references. Use automatically whenever a post or its French translation is drafted or revised (new-post, write-essay, write-analysis, write-note, write-position-paper, translate-fr), and whenever the user asks to see, read, review or preview a draft.
---

# Review a draft

The user reviews every post in full, as it will look on the site, before it goes live. Never make them ask for it. As soon as a draft or a revision is ready, send it here as **one PDF document** of the real rendered page, then stop and wait.

What not to send:
- an HTML file, which does not load in the user's app;
- a series of screenshots, because the user wants one document;
- a separate doc, which does not look like the site (use one only if the user asks for a doc to comment on).

## 1. Render and print

```bash
.claude/skills/review-draft/preview.sh drafts/<name> [path/to/quarto] [width]
# French: .claude/skills/review-draft/preview.sh fr/drafts/<name> [path/to/quarto]
# A published post under revision: posts/<YYYY-MM-DD-slug> or fr/posts/<YYYY-MM-DD-slug>
```

- The script renders only this page inside the site project, so it gets the real theme, navbar, badges, callouts, citations and footer.
- It then serves `_site` locally and prints the page with `pdf.js` to `_preview/<slug>.pdf`, which is git-ignored. The PDF uses the on-screen look, not the print stylesheet.
- Pages are 430 px wide by default, one phone screen each, so the text stays large on a phone.
- Page breaks never fall inside a figure, a table, a callout or an equation, nor right after a heading. Wide tables wrap to the page instead of being cut off.
- The site loads KaTeX from a CDN that the sandbox may block. The script then fetches KaTeX once with `npm pack` and serves it locally, so equations render as they will online.
- If Quarto is missing, download it as in **new-post** (step 6) into the scratchpad and pass the binary as the second argument.
- Fix every warning it prints and run it again.

## 2. Check before sending

Read the PDF yourself with the Read tool (`pages`, at most 20 per call) and look at every page. Check that:
- every figure appears whole and no label overlaps a line or runs off the edge (on phones the site shows figures edge to edge, so keep `savefig.pad_inches` at 0.35 or more in `figs.py`);
- equations are typeset, with no raw `\pi` or `$…$` showing;
- tables show every column, and citations show as names and years, not `?@key`.

Fix what you find in the post, in `figs.py` or in `pdf.js`, then rerun step 1.

## 3. Send it here

1. Make one **SendUserFile** call with the PDF, `display: "render"` and `status: "normal"`. The caption names the post and says it is the full draft as it will render on a phone.
2. In the reply, give only:
   - kind, title, topic tile(s) and word count of the body;
   - the thesis or main point in two or three sentences;
   - the few points that need the author's judgement, such as unverified sources, strong wording, or a place where a personal example would help;
   - the draft's address, https://scuenat.github.io/drafts/<name>/ (French: /fr/drafts/<name>/), and the list of all drafts, https://scuenat.github.io/drafts/, once it has been pushed (new-post step 7a);
   - the question: what to change, or approve to publish it on the home page.

Do not paste the text into the chat as well: the PDF is the review copy.

## 4. Revise in the drafts area, promote only on approval

- New posts are drafts under `drafts/<name>/` and `fr/drafts/<name>/` (see **new-post**, step 2). They are pushed to `main` from the first version on (new-post step 7a): pushing a draft publishes it only at https://scuenat.github.io/drafts/<name>/, listed on https://scuenat.github.io/drafts/, with a "Draft" banner and `noindex`, and nowhere else on the site.
- Apply every change the user asks for in the draft, push it to `main` again, then run steps 1 to 3 and send the new PDF. Each revision goes through the same loop. Never commit `_preview/` or `_site/`.
- Only when the user approves, promote the draft with `promote-draft.py` (new-post step 7b): that is the step that puts it on the home page, the archive and the feed. Send the French version for review the same way, unless the user said the English approval covers it.
