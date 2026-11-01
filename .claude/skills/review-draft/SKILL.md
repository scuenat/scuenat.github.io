---
name: review-draft
description: Show the user the complete draft of a post for review before anything is published, without being asked. Covers the full text, every figure, equations, tables and citations, as one self-contained page they can read in the Claude app. Use automatically whenever a post or its French translation is drafted or revised (new-post, write-essay, write-analysis, write-note, write-position-paper, translate-fr), and whenever the user asks to see, read, review or preview a draft.
---

# Review a draft

The user reviews every post in full, with its pictures, before it goes live. Never make them ask for it: as soon as a draft or a revision is ready, show it this way, then stop and wait.

## 1. Build the preview

```bash
.claude/skills/review-draft/preview.sh posts/<YYYY-MM-DD-slug> [path/to/quarto]
# French: .claude/skills/review-draft/preview.sh fr/posts/<YYYY-MM-DD-slug> [path/to/quarto]
```

The script copies the post outside the site project and renders it alone. The result is one self-contained HTML file with figures embedded, MathML equations, resolved citations and a table of contents. It writes `_preview/<slug>.html`, which is git-ignored and never published. If Quarto is missing, download it as in **new-post** (step 6) into the scratchpad and pass the binary as the second argument.

The script prints any render warning. Fix it in the post and run it again until there is none.

## 2. Check it before sending

Open the file with Playwright (pre-installed, `require('playwright')`), take screenshots at 900 px wide, and look at them. Check that:
- every figure appears and no label overlaps a line or another label;
- equations are typeset, with no raw `\pi` or `$…$` showing;
- tables are readable and citations show as names and years, not `?@key`.

Fix what you find, in the post or in `figs.py`, then rebuild.

## 3. Send it

1. Call **SendUserFile** with the preview HTML, `display: "render"`, `status: "normal"`. That one page carries the full text and all pictures. Also send the lead figure PNG (`figures/fig01.png`) so it shows in the conversation.
2. In the reply, give only:
   - kind, title, subtitle, description, topic tile(s) and the word count of the body;
   - the thesis or main point in two or three sentences;
   - the few things that need the author's judgement (unverified sources, strong wording, places where a personal example would help);
   - the question: what to change, or approve to publish.

Do not paste the whole text into the chat as well: the page is the review copy.

## 4. Revise, then publish only on approval

- Apply every change the user asks for, rebuild the preview and send it again (steps 1 to 3). Each revision goes through the same loop.
- While waiting, keep the draft safe on a branch `draft/<slug>` (commit the sources, push that branch, never `_preview/` or `_site/`). Pushing to `main` publishes, so never push the draft to `main` before the user approves.
- After approval, continue with **new-post** step 5 (French) and step 7 (publish). Preview the French version the same way, unless the user said the English approval covers it.
