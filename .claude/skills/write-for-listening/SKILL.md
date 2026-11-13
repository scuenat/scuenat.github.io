---
name: write-for-listening
description: Make every post on this site sound right when read aloud by the "Listen" button (listen.js, the reader's own device voice). Says what the voice reads, what it skips and what it reads badly (file names, figure references, symbols, abbreviations, units, inline maths, Latin, long asides), and gives a check that prints the exact transcript and flags problems. Use for every new post and every new draft version, English and French (with new-post, write-essay, write-analysis, write-note, write-position-paper, write-overview, write-plainly, translate-fr), when revising a published post, and whenever the user mentions the Listen button, the automatic reader, reading aloud, audio, or how a post sounds.
---

# Write for listening

Every post and draft has a **Listen** button (`listen.js`). The reader's own browser reads the
post aloud, in English or French, with a natural voice, a slightly slow pace and pauses between
paragraphs. Some readers will only ever *hear* a post, on a walk or in the car. So a post must
work with eyes closed, as well as on the page.

This skill comes after **write-plainly**: short sentences and plain words already do most of the
work. What is left is what a voice does differently from an eye.

## 1. What the voice reads and skips

**Read, in order:** the title and subtitle, the opening note (`.callout-note`), "In short", the
headings, paragraphs, list items and quotes, up to the "Questions or objections?" note.

**Skipped, silently:** figures and their captions, tables, code, display equations, footnotes,
citations like `[@sagan1980]`, the series note, `.callout-tip` boxes, and everything after the
end of the text (read-next box, sources, references).

**Changed on the way:** inline maths becomes "an equation"; dashes and brackets become short
pauses; "e.g.", "i.e.", "etc.", "vs" and "&" are said in full; "1–4" is said "1 to 4"; a heading
gets a final stop. Italics and bold are not heard. Quote marks are not heard.

## 2. The rules

1. **Never send the listener to something they cannot see.** No "In Figure 1", "see the table",
   "below", "on the left", "in red". Say in the sentence what the figure shows; if you mention
   the drawing, say it as a story ("When I drew it, I had to make the line much wider").
   A figure may add to the text, never carry it.
2. **No file names, code names or bare web addresses in the read text.** "drawn by figs.py" is
   heard as "figs dot p y". Name what it does ("the code that draws it is linked under it") and
   leave the file link in the figure caption, which is not read.
3. **Words, not symbols.** Write "to", "times", "about", "at most", "or", "per": not → × ≈ ≤ / ~.
   Keep symbols for formulas and tables.
4. **No abbreviations.** Not "cf.", "approx.", "et al.", "Fig.", "Eq.", "p." Say "compare",
   "about", "and colleagues". Units in words: "5 gigabytes", "300,000 years", not "5 GB", "300 kyr".
5. **Numbers as you would say them.** "4.6 billion years", not "4.6 × 10⁹ years". Round when the
   exact figure does not matter to the point. A range is "from 1,000 to 4,000".
6. **Acronyms said in full the first time**, then short: "large language models, LLMs". A voice
   may read an acronym as a word or letter by letter; the full form makes it clear either way.
7. **Maths: the sentence carries the meaning.** Inline maths is heard as "an equation". The
   sentence around it must make sense with that substitution, so state the idea in words first
   (as write-plainly asks) and keep inline maths rare in the opening, "In short" and conclusion.
8. **Foreign words and Latin: say what they mean, next to them.** The page's voice reads Latin
   with an English (or French) mouth. "Philosophers call that far view by a Latin name, *sub specie
   aeternitatis*: from the point of view of eternity." Then the listener knows what was just said.
9. **Short asides.** A bracket or a dash pair is heard only as a pause. An aside of more than
   about a dozen words, or a bracket inside a bracket, loses the listener: make it a sentence.
10. **Sentences under 30 words when heard.** A reader can look back; a listener cannot. Split
    long sentences at the colon or the "and" (write-plainly's 25-word rule usually covers this).
11. **Don't let meaning hang on italics or bold.** "It is what the photo is *of*" still works
    aloud; "*not* this but that" without "not" in plain words would not.
12. **Introduce quotations aloud.** Quote marks are silent, so the words "he wrote", "she said:"
    tell the listener where someone else's voice starts.
13. **Headings are spoken sentences.** Short, under ten words, saying the point.
14. **Lists are read item by item**, with a short pause: each item should be a phrase that
    makes sense alone, not a fragment that needs the eye to see its bullet.
15. **The opening note is read first.** Keep it to plain sentences about the post; the
    machine-translation notice and the link to the original are fine.

## 3. Check every version

Render the page, then run the check on the English and French versions together:

```bash
quarto render drafts/<name>/index.qmd && quarto render fr/drafts/<name>/index.qmd
node .claude/skills/write-for-listening/listen-check.js drafts/<name> fr/drafts/<name> \
     --transcript <scratchpad>/<name>-heard.txt
```

It opens the rendered page in the pre-installed Chromium, takes the transcript straight from
`listen.js` (`window.listenTranscript()`), so it checks exactly what the voice will say, and
lists:

- **✗ to fix**: file names, web addresses, figure and table references, "an equation", symbols,
  abbreviations, unit abbreviations, scientific notation;
- **· to judge**: sentences over 30 words, acronyms, seen-not-heard phrases ("below", "in red"),
  long asides, inline maths, foreign phrases, long headings, leftover brackets.

Fix every ✗. For each ·, decide: a Latin term that the text explains right next to it is fine.
Then read the opening and "In short" in the transcript file as if you heard them: is anything
missing that only the eye had?

Mention it in the commit message when wording changed for the ear
("Draft v<N>: <Title> (… ; reads well aloud: …)").

## 4. Changing the reader

The rules above assume `listen.js` as it is. If you change what it reads, skips or rewrites
(the `SKIP`, `READ`, `END` selectors, `clean()`, `narrate()`), update section 1 here and the
checker's rules in `listen-check.js` in the same commit, and keep `window.listenTranscript`.
