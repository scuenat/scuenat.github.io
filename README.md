# Stéphane Cuenat — blog

Quarto website: essays and papers (*AI, Honestly*). Live at https://scuenat.github.io, deployed on every push to `main`.

## One-time setup

1. Install Quarto: https://quarto.org/docs/get-started/
2. Create a **public** GitHub repo named `scuenat.github.io` (empty, no README), then:
   ```bash
   git init && git add . && git commit -m "Initial blog"
   git branch -M main
   git remote add origin https://github.com/scuenat/scuenat.github.io.git
   git push -u origin main
   ```
3. Run once locally to create the `gh-pages` branch: `quarto publish gh-pages`
4. Repo → Settings → Pages: source = branch `gh-pages`, folder `/ (root)`.

### Later: your own domain
Add a file `CNAME` containing the domain, add `- CNAME` under `project: resources:` in `_quarto.yml`, update `site-url`, and at your registrar point `www` → CNAME → `scuenat.github.io` (root domain: A records `185.199.108.153`, `.109.153`, `.110.153`, `.111.153`). Then set the domain in Settings → Pages and tick **Enforce HTTPS**.

After that, every `git push` publishes automatically (`.github/workflows/publish.yml`).

## Writing

- Preview: `quarto preview`
- New post: ask Claude Code to use the `new-post` skill (`.claude/skills/new-post/SKILL.md`). It asks whether the post is an essay, an analysis, a note, a position paper or an overview, follows `write-essay`, `write-analysis`, `write-note`, `write-position-paper` or `write-overview` for the shape, and publishes it to `main` as a draft first: drafts live in `drafts/<name>/` (French: `fr/drafts/<name>/`), are listed only at https://scuenat.github.io/drafts/ with a "Draft" banner and `noindex`, and stay out of the home page, archive, feed, search and sitemap. When a draft is approved, `.claude/skills/new-post/promote-draft.py <name>` moves it to `posts/<date>-<name>/`. By hand: create `posts/YYYY-MM-DD-slug/index.qmd` (copy an existing one)
- Every post needs `kind:` (`essay`, `analysis`, `note`, `position` or `overview`): it sets the coloured badge on its card in the home strip, the theme tiles and the archive (`latest-strip.ejs`, `topic-tiles.ejs`, `archive-list.ejs`; French labels in `fr/index.qmd` and `fr/archive.qmd`). Working papers use `kind: analysis`; position papers `kind: position`
- Paper: publish it as a post (category `paper`, `citation: true`) and put the PDF next to `index.qmd` with a download link (see `posts/2026-09-29-show-what-changed`)
- Every post needs an `image:` (listing thumbnail and LinkedIn preview); the site default is `social-card.jpg`
- Every post needs `topics:` (the home-page tiles it appears in: `agentic-coding`, `fast-ai`, `human`, `dashboards`, `physics`; a post may have several). The tiles are defined in `index.qmd` and `fr/index.qmd`; a post with no known topic lands in a fallback "Also on the site" tile. The full list by date, with category filters, is `archive.qmd`
- Every page needs a `description:`: it is the snippet in Google results (the first ~155 characters show) and the summary in the listing
- A translation lives at the same path under `fr/`; the two are linked automatically (hreflang, language switch, `translationOfWork`). To translate a post (or every missing one), ask Claude Code to use the `translate-fr` skill (`.claude/skills/translate-fr/SKILL.md`)

## Search engines

Handled by the build, nothing to do per post:

- `seo.lua`: a canonical URL on every page and schema.org JSON-LD (`BlogPosting`, or `ScholarlyArticle` for posts in the `paper`/`article` category; `WebSite` on the home pages; `ProfilePage` on About)
- `lang-links.lua`: hreflang links between English and French
- `sitemap-lastmod.py` (post-render): sitemap dates from the last commit touching each page, URLs in directory form (`/posts/x/`), like the canonical links; drafts are left out
- `draft-banner.lua`: "Draft" banner and `noindex` on pages under `drafts/` and `fr/drafts/` (front matter `draft-preview: true`, set in their `_metadata.yml`)
- Google Scholar tags (`google-scholar: true`) on English papers only, so each paper is indexed once

Once, by hand: verify the site in [Google Search Console](https://search.google.com/search-console) (URL-prefix property `https://scuenat.github.io/`) and submit `sitemap.xml`; optionally the same in Bing Webmaster Tools.
- Categories are lowercase (`ai`, `data`, `physics`, ...)
- Series: link both ways ("A follow-up to…" / "Continued in…")
- Analytics: GoatCounter (https://scuenat.goatcounter.com)
- Math: `$inline$` and `$$display$$` (KaTeX)

## License

- Essays, papers and figures: [CC BY 4.0](LICENSE-content.md)
- Code: [MIT](LICENSE)

## Optional

- **Comments:** every post ends with a "Questions or objections?" note pointing to LinkedIn (`discuss.lua`; opt out per post with `discuss: false`). For comments on the site instead, set up https://giscus.app, then uncomment the block in `posts/_metadata.yml`
- **Email list:** Buttondown can send new posts from the RSS feed (`/index.xml`)
