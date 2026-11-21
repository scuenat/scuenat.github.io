---
name: site-design
description: The visual design of this Quarto site (AI, Honestly) — colours, fonts, the post card, home page and archive layouts, the filter bar, dark mode — and how to change it without breaking it. Use whenever the user asks to restyle, redesign or improve the look of the site, the home page, the archive, the cards, a listing, the navbar or the hero, to borrow ideas from another blog's design, or when adding a new listing, template (.ejs) or page component; also when choosing a post's `image:` for its card.
---

# Site design

The site should read like a good engineering blog (Netflix TechBlog, Meta Engineering,
Spotify R&D were the references in November 2026) while keeping its own identity: navy and
amber, a serif for reading, the network hero. Pictures lead, text is short, every card has the
same shape.

## 1. Identity: black and white, amber as the signature

Since November 2026 the frame is black and white and the colour comes from the figures.
Amber is the author's mark and is used **sparingly, on purpose**: "Honestly" and the stars in
the hero, the hero buttons, the "Follow" pill, the active menu line, the rule under post titles,
the reading-progress line, the left edge of the follow and read-next boxes, and hover states
(card borders, link underlines, card titles). Nowhere else: no amber section labels, tints or
top bars. Ask the user before adding amber to a new place.

| Token | Light | Dark | Use |
|---|---|---|---|
| `$paper` / `$body-bg` | #fcfcfa | #141416 | the page |
| `$ink` | #111111 | #f0f0ee | titles, links, section labels, active chip |
| `$body-color` | #1f1f1f | #d6d6d3 | running text |
| `$muted` / `$rule` | #595959 / #e3e2de | #a5a5a2 / #303033 | secondary text, lines, list markers |
| `$surface` / `$surface-alt` | #fff / #f2f1ed | #1b1b1e / #222226 | cards, boxes, code, chips |
| `$navy` (historical name) | #0d0d0e | #000 | black of the hero and footer |
| `$amber` | #f5b041 | same | the mark (above) |
| `$mark` | #a35f00 | amber | amber **text** on white (contrast) |
| `$nav-*` | white bar, grey links | near-black bar | navbar |
| `$kind-*` | essay amber, analysis blue, note green, position plum, overview teal | lighter tints | type of post, as a dot on cards or a left edge on badges, never as fills |

- Reading (November 2026): body text 18px (`$font-size-base: 1.125rem`), line-height 1.72,
  paragraphs 1.2em apart; keep `$muted` at 7:1 or better on the page.
- Hero: black gradient, `hero-network.svg` in grey lines with amber nodes.
- Fonts: **Inter** (sans) for interface, labels and card titles; **Source Serif 4** for headings in
  posts, summaries and body text. Loaded in `_quarto.yml`, never with `@import`.
- Colours live in `light.scss` and `dark.scss` (same variable names); components in `styles.scss`.
  Never hard-code a colour in a component except white behind figures (they are drawn on white)
  and the fixed black and white inside the hero and footer.

## 2. Ideas taken from the references

| From | Idea | Where on the site |
|---|---|---|
| Netflix TechBlog | Newest post as a large feature: figure left, big title right | Home, "Latest writing" (`latest-strip.ejs`) |
| Netflix TechBlog | A row of three image cards, bold sans titles, plain meta line | Home, under the feature |
| Meta Engineering | Small coloured type label on the left, date on the right, above the title | Every `.post-card` |
| Spotify R&D | Grid of cards with an "All categories" menu | Archive (`archive-list.ejs`) |
| Meta / Spotify | Filter by kind with chips | Archive filter bar |

When the user shows another blog, name the one or two ideas worth taking, map them onto the
components below, and keep the identity in section 1.

## 3. Components

**Post card** (`.post-card`, used by `latest-strip.ejs` and `archive-list.ejs`):

```html
<article class="post-card [is-feature]" data-kind="essay" data-cats="ai memory">
  <div class="post-card-media"><img src="…" alt="" onload="…is-tall…" loading="lazy"></div>
  <div class="post-card-body">
    <p class="post-card-meta"><span class="post-card-kind kind-essay">Essay</span><span class="post-card-date">Nov 7, 2026</span></p>
    <h3 class="no-anchor post-card-title"><a href="…">Title</a></h3>
    <p class="post-card-summary">subtitle, else description (2 lines)</p>
    <p class="post-card-foot">15 min</p>
  </div>
</article>
```

- The title link stretches over the whole card (`::after`), so the card is one link.
- **Figures**: the frame is 16:10 on white. Wide figures are shown whole (`contain`);
  tall ones (height > 0.8 × width, flagged `is-tall` by the `onload`) fill the frame and show
  their top. So **the top of a post's `image:` must make sense alone**: a title and the main
  shape, not a legend. Prefer the figure that best explains the post in one look, not always
  `fig01`. A post without a figure uses `../../social-card.jpg`.
- `.is-feature`: two columns (figure 1.35, text 1), title up to 2.15rem, four lines of summary;
  one column under 768 px.

**Grids**: `.post-grid.post-grid-3` → 3 columns, 2 under 992 px, 1 under 576 px.

**Archive filter bar** (`.post-filter`): kind chips (only kinds that exist), a category
`<select>` with counts, and a live count. The script in `archive-list.ejs` filters cards by
`data-kind` / `data-cats`, and opens filtered on `archive.html#category=<name>`
(URL-encoded or base64). Quarto's own category sidebar is off (`categories: false`).

**Kind badge vs kind label**: the `.kind-badge` (neutral box, coloured left edge) is for text
lists (the drafts list); the dot-and-text `.post-card-kind` is for anything with an image
(cards, Start here, theme rows). Do not mix them in one component.

**Start here** (raw HTML in `index.qmd` / `fr/index.qmd`): `a.start-card` with a
`.start-media` image (the post's `image:`, or the series page's), a `.post-card-kind` label,
`.start-title` and `.start-why`. Five in one row on wide screens; below 992 px a compact list
(small picture left, text right), two columns then one. No sideways scrolling anywhere: the
user found it awkward. When you change a pick, change its image too, in both languages.

**Themes** (`topic-tiles.ejs`): one `.theme-row` per theme. Left: title (linked to its series
when the theme has one: `link` / `linkText` in template-params), thesis, and "N posts" linking
to the theme page. Right: the first three posts in reading order as small image cards, and a
"+N more" tile to the theme page when there are more. On phones the cards become a compact
list. A post sits in one theme only (`topics:` names one id).

**Theme pages** (`themes/<id>.qmd`, `fr/themes/<id>.qmd`): every post in the theme, oldest
first, as archive cards without the filter bar (`archive-list.ejs` with `theme:` and
`filters: false`). They are generated from the theme list in `index.qmd` / `fr/index.qmd`:
after adding, renaming or re-describing a theme, run
`python3 .claude/skills/site-design/make-theme-pages.py` and render. Never edit them by hand.

**Light/dark switch** (`.quarto-color-scheme-toggle`, in `styles.scss` under `.navbar`): a grey
pill with an icon and the mode a click switches to (moon + "Dark" / sun + "Light"; "Sombre" /
"Clair" on French pages via `:lang(fr)`), amber border on hover, icon alone under 380 px.

**Figure lightbox** (`lightbox: auto`, GLightbox; styles under "Figure lightbox" in `styles.scss`):
the caption is small sans text, never a heading. On phones it sits under the figure on a dark
background (portrait) or in a column beside it (landscape) and scrolls when long; it must never
cover the figure. Selectors start with `body .glightbox-container.glightbox-clean` to beat
GLightbox's own mobile rules. Check with an emulated iPhone, portrait and landscape.

**Other parts**: hero (`.hero`, keep it compact: about 3.5rem padding), follow box, section
labels (`h2.latest-heading`: small uppercase with a rule).

**Series** (`series.qmd`, `series-cards.ejs`; a series page such as `agentic-coding.qmd`):
the Series page lists one large card per series (`contents:` in order, root path `/x.qmd` in
English; each series page sets `series-parts:`). A series page starts with
`[← All series](series.qmd){.series-back}` (which also lights "Series" in the menu), the intro,
then the `ol.series-strip` (numbered steps linking to `#step-N`), then one
`::: {.series-step data-step="N"}` per part: a raw-HTML `a.series-step-media` with the post's
`image:`, the `## N. … {#step-N}` heading, the post link, summary and takeaway. Follow-ups use
`.series-step .is-followup` (smaller figure).

**About** (`about.qmd`; Research was merged into it in November 2026, `research.qmd` only
redirects to `about.html#research`): `title-block-style: none`, a `.profile` header (name,
role, link pills, the TEDx photo), `ul.profile-facts` (four tiles, two by two), the bio, "This
site" with `nav.ways-in`, `#kinds`, `#research` with the publications listing
(`research/publications.ejs`: selected papers as `.pub-card`s, the full list in
`details.pub-all`), and `#reuse` (linked from the footer). Keep these anchors.

## 4. Layout

- Home (`index.qmd`, `fr/index.qmd`): `page-layout: article`; each section is wrapped in
  `:::: {.column-page .home-section}` so cards get the wide column while running text stays
  at 46rem. Order: hero, Latest writing (feature + 3 cards), Start here, Themes.
- Archive: `page-layout: full` (Quarto renders `main.column-page`), recent changes, then the
  filter bar and grid.
- Series and About pages: article width; their blocks (steps, profile, cards) stay inside the text column so left edges line up.
- Posts keep the article layout with the TOC on the right: reading comes first.
- Breakpoints: 576, 768, 992, 1200 px (Bootstrap). Phone side gutter at least 1rem, no
  horizontal scroll.

## 5. Both languages

The English and French pages share the templates. Every visible word in a template comes from
`template-params` with an English default: `kinds` (type labels) and, for the archive, `ui`
(`all`, `allCategories`, `posts`, `filter`). When adding text to a template, add the French
value in `fr/index.qmd` or `fr/archive.qmd`.

## 6. Check every design change

```bash
quarto render 2>&1 | grep -iE "warn|error"          # must print nothing
(cd _site && python3 -m http.server 8765 >/dev/null 2>&1 &)
node .claude/skills/site-design/shots.js <scratchpad-dir>   # home + archive, EN + FR, desktop + phone, light + dark
```

Look at every screenshot (crop long pages into parts): alignment of the wide sections, no
orphan card on a row, figures readable, labels on one line, dark mode contrast, phone width
without horizontal scroll. In this container the web fonts do not load, so Inter falls back
to a lighter local copy: check `font-weight` with `getComputedStyle` rather than by eye.
Send the user the desktop and phone screenshots of what changed before publishing a large
redesign, and publish (push to `main`, see **new-post** §7) once they agree.

## 7. Figures: the hand-drawn house style

Since November 2026 every figure is drawn in one hand-made style, so the pictures look like
the author's own sketches rather than default charts. It lives in `_figstyle/handdrawn.py`
(with the Kalam font, SIL OFL, in `_figstyle/fonts/`) and is added when a figure is saved, so a
`figs.py` only needs these lines right after `import matplotlib.pyplot as plt`:

```python
import sys, pathlib  # hand-drawn house style: _figstyle/handdrawn.py at the site root
sys.path.insert(0, str(next(p / "_figstyle" for p in pathlib.Path(__file__).resolve().parents if (p / "_figstyle").is_dir())))
import handdrawn; handdrawn.apply()
```

- **Handwriting**: all text except code is set in Kalam (DejaVu Sans fills in symbols Kalam
  lacks; Greek letters in `$...$` come from STIX). Monospace text (code, tool names) stays mono.
- **Pen strokes**: boxes, arrows, frames and axes wobble a little and get a lighter second
  pass, like a pen going over the line. Coloured areas are laid slightly off their outline,
  like a felt-tip.
- **Data stays exact**: curves with many points, scatter dots, error bars and markers get only
  a faint tremor and no second pass, so no value moves.
- Same look in the SVG (page) and the 400 dpi PNG (card): the wobble is scaled to the resolution
  and is the same on every run.
- Kalam is taller than Inter: after changing a figure, look for labels that touch each other or
  a frame and move them in that `figs.py`. Tune the whole look (wobble, offset, line spacing)
  only in `handdrawn.py`, then rerun every `figs.py`.
- *Decided in the Bulk*: its research bundle under `code/` is left as published; the post's own
  `figs.py` reruns three of its plotting scripts with the house style.
- Every figure on the site comes from a `figs.py`, including *Show What Changed* (redrawn
  from the paper's recipes; its PDF keeps the original figures) and the two cover images
  (*A Universe Without a Bottom*, French *Les murs sont en marche*). Not figures, so left as
  they are: the TEDx photo, `social-card.jpg`, the favicon and the hero network.
