#!/usr/bin/env python3
"""Plain-words check for a post (.qmd): sentence length, reading ease, long sentences, heavy words.

Usage: python3 .claude/skills/write-plainly/readability.py path/to/index.qmd [--all]
--all lists every long sentence instead of the first 15.
"""
import re
import sys

SWAPS = {
    "utilize": "use", "utilise": "use", "leverage": "use", "facilitate": "help",
    "demonstrate": "show", "approximately": "about", "consequently": "so",
    "furthermore": "also", "moreover": "also", "nevertheless": "still",
    "subsequently": "then", "commence": "start", "endeavour": "try", "endeavor": "try",
    "numerous": "many", "sufficient": "enough", "additional": "more", "regarding": "about",
    "in order to": "to", "due to the fact that": "because", "with respect to": "about",
    "a number of": "some", "prior to": "before", "in terms of": "(rephrase)",
    "paradigm": "(say what you mean)", "notwithstanding": "despite", "thereby": "so",
    "wherein": "where", "henceforth": "from now on", "aforementioned": "this",
}


def prose(text):
    text = re.sub(r"\A---.*?\n---\n", "", text, flags=re.S)          # front matter
    text = re.sub(r"```.*?```", "", text, flags=re.S)                # code
    text = re.sub(r"\$\$.*?\$\$", " ", text, flags=re.S)            # display math
    text = re.sub(r"\$[^$\n]+\$", "X", text)                         # inline math -> one word
    lines = []
    for ln in text.splitlines():
        s = ln.strip()
        if s.startswith((":::", "|", "<", "#", "![")) or not s:
            lines.append("")
            continue
        if re.match(r"(?:[-+*]|\d+\.)\s", s):                       # list item: its own paragraph
            lines.append("")
        lines.append(s)
    text = "\n".join(lines)
    text = re.sub(r"\[@[^\]]*\]", "", text)                          # citations
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)             # links -> text
    text = re.sub(r"\{[^}]*\}", "", text)                            # attributes
    text = re.sub(r"[*_`>]", "", text)
    return text


def sentences(text):
    out = []
    for para in re.split(r"\n\s*\n", text):
        para = " ".join(para.split())
        para = re.sub(r"^(?:[-+]|\d+\.)\s+", "", para)
        for s in re.split(r"(?<=[.!?…])\s+(?=[\"“«(A-ZÀ-Ý0-9])", para):
            if len(s.split()) >= 3:
                out.append(s)
    return out


def syllables(word):
    w = re.sub(r"[^a-zà-ÿ]", "", word.lower())
    if not w:
        return 0
    n = len(re.findall(r"[aeiouyàâäéèêëîïôöùûü]+", w))
    if w.endswith("e") and n > 1 and not w.endswith(("le", "ee")):
        n -= 1
    return max(n, 1)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    text = prose(open(sys.argv[1], encoding="utf-8").read())
    sents = sentences(text)
    if not sents:
        sys.exit("No prose found.")
    lens = [len(s.split()) for s in sents]
    words = [w for s in sents for w in s.split()]
    syl = sum(syllables(w) for w in words)
    avg = sum(lens) / len(lens)
    long_ = [(n, s) for n, s in zip(lens, sents) if n > 25]
    ease = 206.835 - 1.015 * avg - 84.6 * syl / max(len(words), 1)

    ok = lambda c: "ok " if c else "FIX"
    print(f"{len(sents)} sentences, {len(words)} words")
    print(f"[{ok(avg <= 18)}] average sentence length: {avg:.1f} words (target <= 18)")
    print(f"[{ok(len(long_) / len(sents) < 0.10)}] sentences over 25 words: {len(long_)} "
          f"({100 * len(long_) / len(sents):.0f} %, target < 10 %)")
    print(f"[{ok(ease >= 50)}] reading ease (Flesch, English): {ease:.0f} (target >= 50)")

    if long_:
        print("\nLongest sentences (split them):")
        shown = sorted(long_, reverse=True)
        for n, s in shown if "--all" in sys.argv else shown[:15]:
            print(f"  ({n}) {s}")

    low = text.lower()
    hits = [(k, v, len(re.findall(r"\b" + re.escape(k) + r"\b", low))) for k, v in SWAPS.items()]
    hits = [h for h in hits if h[2]]
    if hits:
        print("\nPlain swaps:")
        for k, v, c in sorted(hits, key=lambda h: -h[2]):
            print(f"  {k!r} x{c} -> {v}")


if __name__ == "__main__":
    main()
