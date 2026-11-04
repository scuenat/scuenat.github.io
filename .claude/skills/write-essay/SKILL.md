---
name: write-essay
description: Shape and write an essay for this site (kind essay, amber ESSAY badge) — a first-person argument or reflection that carries one idea through. Use when the user asks for an essay, or after new-post chose "Essay". Starts by confirming the kind (essay, analysis, note, position paper or overview) and defers to new-post for files, front matter, translation and publishing to main.
---

# Write an essay

**First, confirm the kind.** If this skill was not reached through **new-post** after the user chose "Essay", ask with AskUserQuestion: "Which kind of post should this be: an essay, an analysis, a note, a position paper or an overview?" (options Essay (Recommended) / Analysis / Note / Position paper). If the answer is not Essay, switch to **write-analysis**, **write-note**, **write-position-paper** or **write-overview**. Then follow **new-post** for files, front matter (`kind: essay`, first category `essay`), translation, verification and publishing to `main`.

## What makes it an essay

One idea, argued in the first person, for a reader who has ten minutes. It may be personal, speculative or philosophical. It does not need data, but it must be honest about what is opinion. Examples: `posts/2026-10-30-the-tool-and-the-hand`, `posts/2026-10-27-the-joy-of-the-question`, `posts/2026-10-24-work-has-mass`.

Ask the user, if not given: the one claim the essay makes, who it is for, and any source, story or experience it should start from.

## Shape

1. Opening callout: `**Essay, <Month YYYY>.** A short, personal essay …` plus where figures come from.
2. `**In short.**` — the whole argument in one paragraph.
3. Three to six numbered sections (`## 1. …`), each moving the idea one step:
   - start concrete (a scene, a history, a familiar promise);
   - state the claim plainly;
   - meet the strongest objection;
   - end with what follows for the reader (a question to ask, a thing to do).
4. A last short paragraph that lands the image or the line the reader will remember.
5. Optional `::: {.read-next}`, then the disclaimer: *The views in this essay are my own …*

## Style

- 1 000–4 000 words. Short paragraphs, plain words, one metaphor carried through rather than many.
- One or two schematic figures at most, labelled "Schematic, my own"; they show a shape, not data.
- No numbers without a source. If a claim is a hunch, say so.
- Categories: `essay` first, then 2–4 topical ones (add `thought-essay`, `experiment` or `personal` where they fit).
