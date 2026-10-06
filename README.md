# Stéphane Cuenat — blog

Quarto website: essays and papers (*AI, Honestly*). Live at https://scuenat.github.io, deployed on every push to `main`.

## One-time setup

1. Install Quarto: https://quarto.org/docs/get-started/
2. In `about.qmd`: set your email and add `profile.jpg`.
3. Create a **public** GitHub repo named `scuenat.github.io` (empty, no README), then:
   ```bash
   git init && git add . && git commit -m "Initial blog"
   git branch -M main
   git remote add origin https://github.com/scuenat/scuenat.github.io.git
   git push -u origin main
   ```
4. Run once locally to create the `gh-pages` branch: `quarto publish gh-pages`
5. Repo → Settings → Pages: source = branch `gh-pages`, folder `/ (root)`.

### Later: your own domain
Add a file `CNAME` containing the domain, add `- CNAME` under `project: resources:` in `_quarto.yml`, update `site-url`, and at your registrar point `www` → CNAME → `scuenat.github.io` (root domain: A records `185.199.108.153`, `.109.153`, `.110.153`, `.111.153`). Then set the domain in Settings → Pages and tick **Enforce HTTPS**.

After that, every `git push` publishes automatically (`.github/workflows/publish.yml`).

## Writing

- Preview: `quarto preview`
- New essay: create `posts/YYYY-MM-DD-slug/index.qmd` (copy an existing one)
- Paper: publish it as a post (category `paper`) and put the PDF next to `index.qmd` with a download link (see `posts/2026-09-29-show-what-changed`)
- Math: `$inline$` and `$$display$$` (KaTeX)

## Optional

- **Comments:** set up https://giscus.app, then uncomment the block in `posts/_metadata.yml`
- **Email list:** Buttondown can send new posts from the RSS feed (`/index.xml`)
