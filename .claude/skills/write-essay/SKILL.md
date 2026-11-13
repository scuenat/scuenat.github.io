---
name: write-essay
description: Shape and write an essay for this site (kind essay, amber ESSAY badge) — a first-person argument or reflection that carries one idea through. Interviews the user first (the claim, the opening moment and what stays private, the objection to meet, where AI fits) with options built from their own words. Use when the user asks for an essay, or after new-post chose "Essay". Starts by confirming the kind (essay, analysis, note, position paper or overview) and defers to new-post for files, front matter, translation, the drafts area and publishing.
---

# Write an essay

**First, confirm the kind.** If this skill was not reached through **new-post** after the user chose "Essay", ask with AskUserQuestion: "Which kind of post should this be: an essay, an analysis, a note, a position paper or an overview?" (options Essay (Recommended) / Analysis / Note / Position paper). If the answer is not Essay, switch to **write-analysis**, **write-note**, **write-position-paper** or **write-overview**. Then follow **new-post** for files, front matter (`kind: essay`, first category `essay`), translation, verification, the drafts area (`drafts/<name>/`, reviewed at /drafts/) and publishing.

## What makes it an essay

One idea, argued in the first person, for a reader who has ten minutes. It may be personal, speculative or philosophical. It does not need data, but it must be honest about what is opinion. Examples: `posts/2026-10-30-the-tool-and-the-hand`, `posts/2026-10-27-the-joy-of-the-question`, `posts/2026-10-24-work-has-mass`.

## Ask the right questions first

An essay lives or dies on its one idea and on the moment it starts from. Both belong to the user; never guess them. Before writing, run a short interview with AskUserQuestion. Rules:

- **Read the request first, then ask only what it leaves open.** Never ask for something the user already said; quote it back instead ("You said: *it matters at least a bit*").
- **Offer real candidates, not blanks.** Build every option from the user's own words and the site's past essays, mark the one you would pick "(Recommended)" and put it first. The user can always type "Other".
- **At most two rounds** of up to four questions each. Round 1 is the essay itself; round 2 (only if still open) is the site placement. Then write.
- **Do not ask about wording, length or structure**: this skill, **write-plainly** and **write-for-listening** settle those.

### Round 1 — the essay

1. **The claim** (header "Claim"). "What is the one thing this essay argues?" Offer two to four sharp, different one-sentence claims the request could carry (for example: a consoling answer, a defiant one, a modest one, a question left open). This is the most important question; if the user picks "Other", use their sentence as the anchor line.
2. **The moment** (header "Moment"). "What should the opening scene keep, and what stays private?" For a personal story, ask what may be told: names (default: none, "my daughter", "a colleague"), ages, exact words said, what the user felt. Offer: *Tell it as you told me* / *Keep it brief and anonymous* / *Add details you will give me*. Never invent dialogue, feelings or facts in the scene; use only what the user said, and mark anything uncertain as such in the text ("I don't know for sure why").
3. **The strongest objection** (header "Objection"). "Which view should the essay take on?" Offer the two or three opposing positions a thoughtful reader would raise (for a philosophical essay: the named school, e.g. "nothing matters, so just enjoy it", nihilism, the religious answer, the scientific shrug). The essay meets the one chosen at full strength.
4. **The thread to the site** (header "AI's place"). The site is about AI; an essay off that path must say how, or whether, it comes back. Offer: *A closing section on what AI changes or cannot change* / *AI as one lens throughout* / *Leave AI out; say so in the callout* / *AI as the main subject*. If the user said "if at all", keep *if at all* honest: the essay may conclude that AI does not help.

Optional, instead of one of the above when the request is clear on it: **the thinkers** (header "Sources") — "Which thinkers or sources should it lean on?" with two to four candidates that fit the claim (e.g. Camus, Nagel, Sagan's *Pale Blue Dot*, Spinoza; for AI: Poincaré, McGilchrist, as in past essays), or *None, keep it personal*. Every quotation used must then be real and cited.

### Round 2 — placement (skip what **new-post** has already asked)

- **Theme tile** (`topics:`): the best fit first (`human` for "what stays ours", `physics` for the curiosity series, or none).
- **French version** in the same commit (recommended: yes).
- **Series**: whether it belongs to a series (e.g. *Evenings with Physics*) or continues an earlier essay (a "read next" link). Ask before starting a new series.

**Read the answers as text, not as choices.** A user often answers one question with something that belongs to another (an image for the whole essay typed under "Objection", two options merged under "Claim"). Take what they wrote as the strongest signal: it may replace the claim, become the carried metaphor or the title. Keep their words where you can.

After the answers, restate in two lines, in the chat, the claim and the opening scene you will write from, then write. If an answer changes the claim later, the user's latest word wins.

## Shape

1. Opening callout: `**Essay, <Month YYYY>.** A short, personal essay …` plus where figures come from.
2. `**In short.**` — the whole argument in one paragraph.
3. Three to six numbered sections (`## 1. …`), each moving the idea one step:
   - start concrete (a scene, a history, a familiar promise);
   - state the claim plainly;
   - meet the strongest objection;
   - end with what follows for the reader (a question to ask, a thing to do).
   - for a personal or philosophical essay, the sections can follow the movement of the thought instead (the moment → the fact that caused it → the easy answer and why it is not enough → the answer the essay defends → what it changes); keep the objection as a section of its own.
4. A last short paragraph that lands the image or the line the reader will remember.
5. Optional `::: {.read-next}`, then the disclaimer: *The views in this essay are my own …*

## Style

- 1 000–4 000 words. Short paragraphs, plain words, one metaphor carried through rather than many.
- One or two schematic figures at most, labelled "Schematic, my own"; they show a shape, not data.
- No numbers without a source. If a claim is a hunch, say so.
- Categories: `essay` first, then 2–4 topical ones (add `thought-essay`, `experiment`, `curiosity` or `personal` where they fit).
- An essay that leaves the site's usual subject says so in its opening callout ("This blog is usually about AI … this essay is a curiosity"), as `posts/2026-10-15-a-universe-without-a-bottom` does.
- Facts from science (ages of the Sun, the Earth, the universe; timescales of the future) get a source, and the essay says plainly when the far future is a prediction, not a fact.
- Family and private people: no names unless the user gives them for publication; tell their part briefly and with care.
