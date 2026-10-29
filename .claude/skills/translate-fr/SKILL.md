---
name: translate-fr
description: Translate English posts of this Quarto site into French under fr/, following the site's conventions (shared figures and bibliographies, translated categories, link to the original, About pages kept in sync). Use when a post is published or updated, when asked to translate a post, or to find and translate every post that has no French version yet.
---

# Translate posts into French

English is the source language. Each translation lives at the same path under `fr/` (for example `posts/2026-10-27-slug/index.qmd` → `fr/posts/2026-10-27-slug/index.qmd`). `lang-links.lua` pairs the two pages automatically: hreflang tags, the FR/EN switch and `translationOfWork`. The French listings (`fr/index.qmd`, `fr/archive.qmd`) pick up new files on their own.

## 1. Find what is missing or stale

```bash
# Posts with no French version
for d in posts/*/; do s=${d#posts/}; [ -f "fr/posts/${s}index.qmd" ] || echo "missing: $s"; done
# French versions older than their English source (by last commit)
for f in fr/posts/*/index.qmd; do en=${f#fr/}; [ "$(git log -1 --format=%ct -- "$en")" -gt "$(git log -1 --format=%ct -- "$f")" ] && echo "stale: $en"; done
```

Skip drafts (`draft: true`). For a stale translation, run `git log -p` on the English file since the French one last changed, and carry over only those edits.

Before writing, read one existing translation next to its original (for example `fr/posts/2026-10-24-work-has-mass/index.qmd`) to match the tone.

## 2. Front matter

- Translate `title`, `subtitle` and `description`. Keep the description under about 155 characters where the English one is.
- Keep `date`, `citation`, `toc-depth` and `topics` unchanged. Topic ids are not translated.
- Translate `categories` with the existing names. Reuse these, and only invent a new one if no mapping exists:

  | English | French | English | French |
  |---|---|---|---|
  | essay | essai | paper | article |
  | analysis | analyse | position | position |
  | thought-essay | essai-de-réflexion | experiment | expérience |
  | curiosity | curiosité | personal | personnel |
  | ai | ia | local-ai | ia-locale |
  | data | données | dashboards | tableaux de bord |
  | physics | physique | research | recherche |
  | agents | agents | programming | programmation |
  | automation | automatisation | architecture | architecture |
  | agile | agilité | organisation | organisation |
  | machine-learning | apprentissage-automatique | deep-learning | apprentissage-profond |
  | reliability | fiabilité | memory | mémoire |
  | education | éducation | creativity | créativité |
  | philosophy | philosophie | mcp | mcp |

  To list what is in use: `grep -h '^categories' fr/posts/*/index.qmd | sort -u`.
- Point at the English post's files rather than copying them:
  - `image: ../../../posts/<slug>/figures/fig01.png`
  - `bibliography: ../../../posts/<slug>/references.bib`
- Drop `resources:` (the files are already published with the English post) and `google-scholar:` (papers are indexed once, in English).
- `fr/posts/_metadata.yml` already sets `lang: fr`, the author and the license.

## 3. Body

- **Links to the post's own files** (figures, `figs.py`, `sim.py`, `results.json`, PDFs) become `../../../posts/<slug>/<file>`.
- **Links to other posts** stay relative (`../<other-slug>/index.qmd`) when that post has a French version. Otherwise use `../../../posts/<other-slug>/index.qmd` followed by ` (en anglais)`. Site pages use `../../agentic-coding.qmd` and the like.
- **Opening callout.** Translate it, and end it with the sentence about figures if they contain text, then the link to the original:
  `Les figures sont en anglais. *Traduit de l'anglais : [version originale](../../../posts/<slug>/index.qmd).*`
  Add a callout if the English post has none.
- **Figures.** Translate captions and `fig-alt`. In alt text, quote the English label words that a reader will see in the image, and describe everything else in French.
- **Citations.** Keep `[@key]` exactly as written. Leave `## References` / `::: {#refs}` structure as is, but write the heading as `## Références`.
- **Recurring phrases:**
  - Key takeaways → `## À retenir`; In short → `**En bref.**`
  - Read next → `**À lire ensuite**`
  - Continued in … → `Suite dans …`; A follow-up to … → `La suite de …`
  - Table N → `**Tableau N.**`; Figure N → `**Figure N.**`; Schematic, my own → `Schéma, de moi`
  - What I am not claiming → `Ce que je ne prétends pas`
  - Disclaimer: `*Les opinions exprimées dans cet essai sont les miennes et ne décrivent aucun produit ni aucun projet de mon employeur.*` Use `cet article` for papers and `cette analyse` for analyses.
- **French typography.** Use a space before `; : ? !`, `« guillemets »` with spaces inside, a decimal comma (`0,92`, `97,2 %`), a space as the thousands separator (`5 000`), and a space before `%`. Inside math, write `1{,}24` and `32\,768`. Leave code, URLs, identifiers and numbers in figure descriptions consistent with the image.
- **Sources.** Keep paper titles in their original language, with French guillemets: `[« Title »](url)`. Translate `and` → `et` and `ed.` → `dir.`. Use the French title of a book when a standard translation exists (for example *Le Point de vue de nulle part*, *Monadologie*).
- **Quotations.** Use the standard French wording of well-known quotations (Camus, Montaigne, Pascal, Aristotle, Einstein and Infeld). Never invent a quotation that is presented as exact.
- **Style.** The site style is plain, short sentences and no hype. Translate the meaning, not word for word, and keep the author's first person. Do not add or remove claims.

## 4. Keep the rest of the site in sync

- `grep -rn "<slug>" fr/*.qmd fr/posts` finds French pages that link the English post with "(en anglais)". Point them at the new translation and drop the marker.
- If the English post has a "Continued in" / "Read next" link to a post that now has a French version, check the French chain both ways.
- If the English `about.qmd` or `agentic-coding.qmd` changed along with the post, apply the same change to their French versions.

## 5. Verify, then publish

Render the whole site; it must finish with no warnings:

```bash
quarto render 2>&1 | grep -iE "warn|error"
```

If Quarto is not installed, download it into the scratchpad from `https://github.com/quarto-dev/quarto-cli/releases/download/v1.6.42/quarto-1.6.42-linux-amd64.tar.gz` and run `quarto-1.6.42/bin/quarto`.

Then check each new page in `_site/fr/posts/<slug>/index.html`:

```bash
f=_site/fr/posts/<slug>/index.html
grep -c '?@' $f                                  # 0: every citation resolved
grep -o 'alt-lang-url" content="[^"]*' $f        # points to /posts/<slug>/
grep -o 'src="[^"]*\.\(png\|svg\)"' $f | sed 's/src="//;s/"$//' | while read s; do [ -f "_site/fr/posts/<slug>/$s" ] || echo "MISSING $s"; done
```

Commit only the source files (`fr/...`, plus any About or series page you touched; never `_site/`), with a message like `Translate <English title> into French`. Pushing to `main` publishes through `.github/workflows/publish.yml`. After that run succeeds, check the follow-up "pages build and deployment" run too. If it fails on an upload error such as ECONNRESET, re-run it once.
