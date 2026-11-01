---
name: write-note
description: Shape and write a note for this site (kind note, green NOTE badge) — short and practical, it assembles existing ideas into something you could ship, gives a recipe and says how to test it. Use when the user asks for a note, a recipe, a how-to or a practical write-up, or after new-post chose "Note". Starts by confirming the kind (essay, analysis or note) and defers to new-post for files, front matter, translation and publishing to main.
---

# Write a note

**First, confirm the kind.** If this skill was not reached through **new-post** after the user chose "Note", ask with AskUserQuestion: "Which kind of post should this be: an essay, an analysis or a note?" (options Note (Recommended) / Essay / Analysis). If the answer is not Note, switch to **write-essay** or **write-analysis**. Then follow **new-post** for files, front matter (`kind: note`, first category `note`), translation, verification and publishing to `main`.

## What makes it a note

Shorter than an essay and more practical. A note takes ideas that already exist, puts them together into something a reader could build this week, and says how to check that it works. It credits where each idea comes from and is honest that the test may not have been run. Example: `posts/2026-11-01-the-context-is-the-wire`.

Ask the user, if not given: the problem, the ideas or sources being combined, and whether the recipe has been tested (if not, the claims are written as hypotheses).

## Shape

1. Opening callout: `**Note, <Month YYYY>.**` — what the note proposes, whether it has been tested, where figures come from. Add a `::: {.callout-important appearance="simple"}` box when a key term needs defining for newcomers.
2. `**In short.**` — the problem, the idea, and what the reader gets (e.g. "about twenty lines of hook code").
3. Numbered sections, roughly:
   - `## 1.` why the obvious approach misses it;
   - `## 2.` the idea that fixes it;
   - `## 3. What already exists` — prior work, credited with links;
   - `## 4. The recipe` — steps and a code listing (`**Listing 1.**`), short enough to copy;
   - `## 5. The test` — how to measure that it works (say "(not yet run)" if so), starting with something cheap such as shadow mode or a week of logging;
   - `## 6. Objections` — bold one-line objections, each answered in two or three sentences;
   - `## 7. What would prove me wrong`;
   - `## 8. Where this comes from` — the post or question it grew out of.
4. A one-paragraph "short version" of the recipe to end, then the disclaimer: *The views in this note are my own …*

## Style

- 1 000–3 000 words. Concrete over abstract: commands, file names, thresholds.
- Code must run or be clearly marked as a sketch; keep listings under ~40 lines.
- No claims of effectiveness without a measurement; say what would be measured.
