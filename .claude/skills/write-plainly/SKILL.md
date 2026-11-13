---
name: write-plainly
description: Write and revise posts on this site in Stéphane's own plain voice, so any reader can follow them, not only specialists. Short sentences, everyday words, a story or a moment first, jargon explained by what it does, formulas after the sentence that says the same thing. Use for every new post and every new draft version (with new-post, write-essay, write-analysis, write-note, write-position-paper, write-overview, translate-fr), and whenever the user asks to simplify, make clearer, make easier to read, plain English, "write like me", or to rework the wording of a post or draft.
---

# Write plainly, in Stéphane's voice

The site is for all readers, not only researchers. The ideas can be deep; the words must not
be. This skill sets the voice and gives a check to run on every draft version.

The reference is Stéphane's own handwriting: read `voice-sample.md` in this folder before
writing or revising. It shows how he thinks on paper when nobody edits him. Keep that rhythm
and order of thought. Correct the grammar (English is his second language), never the voice.

## 1. The voice

- **Start from a moment or a thing, not from the thesis.** "One evening I opened a paper I could
  not follow" comes before "complexity is description length".
- **First person, humble, honest.** Say what you are not ("I am not a physicist"), what you
  believe ("I believe"), and what you checked. Doubt is allowed and said once, plainly.
- **The idea fits in a sentence anyone could say aloud.** "It must be simpler." "Look at what
  changed, not at the data." Find that sentence, use it as the anchor, repeat it, then sharpen it.
- **Define words your own way, with an example**, before using the field's term:
  "simpler, seen from a different angle" first, "a change of frame" after, if at all.
- **Go from the far field to what you know**: physics or maths → software engineering → teams
  and work. Say when you move.
- **Concrete objects**: a dashboard, a team processing items, a diff, a notebook, a junior colleague.
- **Signposts**: "Now, …", "So …", "Here is the test." Short bridges, not "Furthermore" or "Moreover".

## 2. The rules for wording

1. **One idea per sentence.** Aim for 12 to 18 words on average. Split any sentence over 25 words.
2. **Everyday words first.** use (not utilise), show (not demonstrate), about (not approximately),
   because (not due to the fact that), help (not facilitate), so (not consequently).
3. **Verbs, not stacks of nouns.** "We describe it at the wrong level" beats
   "description-level misalignment". No more than two abstract nouns in a row.
4. **One technical term at a time, explained by what it does**, the first time it appears:
   "the KV cache, the model's short-term memory of the text so far".
   If a term is used only once, drop it.
5. **Sentence first, formula second.** Every equation is preceded by the plain sentence that says
   the same thing, so a reader can skip the equation and lose nothing.
6. **No hedging chains, no hype.** Not "it could arguably be suggested that"; say "I think".
   Not "revolutionary"; say what changed.
7. **Paragraphs of 2 to 5 sentences.** A list or a small table when there are three or more
   parallel items.
8. **Headings say the point**: "Look at the diffs" rather than "Methodological considerations".
9. **The "In short" paragraph must pass the phone test**: a friend who does not work in AI
   could read it aloud and explain it back.
10. **Keep precision.** Simpler words, same claims. Never drop a number, a caveat or a citation
    to make a sentence shorter. Long technical detail goes to a later section, a footnote or
    the PDF, not away.

## 3. Before and after

**Before** (abstract of *It Must Be Simpler Than This*):

> We call a system complex when describing it takes a long time. I argue that this length is
> mostly a property of the description, not of the system. Formally, the *apparent* complexity
> $A(x)$ of a thing is the length of the description we actually use; its *intrinsic* complexity
> is the length of the shortest description that would regenerate it…

**After:**

> One evening I read a physics paper I could not follow, and a voice said: *it must be simpler
> than this.* I am not a physicist, and I know the work is hard. But I think the voice was
> partly right. Often, a thing looks complex because of how we describe it, not because of what
> it is. Seen from another angle, the same thing can have a short description. This paper turns
> that feeling into a claim you can test. (The formal version, $A(x)$ against $K(x)$, comes in
> section 2.)

What changed: the moment comes first, the doubt is said, the idea is one spoken sentence, the
formula is moved after the plain claim. Nothing was removed from the argument.

## 4. Check every version

Run the check on the post and fix what it flags before sending the review PDF:

```bash
python3 .claude/skills/write-plainly/readability.py drafts/<name>/index.qmd
```

It ignores front matter, code, math, tables and callout markers, then reports the average
sentence length, the share of long sentences, a reading-ease score, and lists the sentences
over 25 words and the words from the "plain swap" list. Targets: average ≤ 18 words, under
10 % of sentences over 25 words, reading ease ≥ 50. Formal sections of a position paper may
run a little higher; the opening callout, "In short", takeaways and conclusion may not.

Then reread the opening and "In short" against `voice-sample.md`: does it start from a moment
or a thing, and is the idea one sentence anyone could say?

Then make sure it also works aloud: follow **write-for-listening** and run its check
(`node .claude/skills/write-for-listening/listen-check.js drafts/<name> fr/drafts/<name>`).

When the wording changes in a new draft version, say so in the commit message
("Draft v<N>: <Title> (plainer wording: …)").

## 5. French

The same rules apply in French (**translate-fr**): phrases courtes, mots de tous les jours,
« je », l'idée en une phrase qu'on peut dire à voix haute. Stéphane's French is his first
language: keep it natural and spoken, not academic. The check script works on French text
too (the reading-ease score is calibrated for English; use the sentence lengths).
