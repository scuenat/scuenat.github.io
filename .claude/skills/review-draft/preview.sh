#!/usr/bin/env bash
# Render a post with the site's own theme and screenshot it as it will look online.
# Usage: .claude/skills/review-draft/preview.sh posts/YYYY-MM-DD-slug [quarto-binary] [width]
# Writes _preview/<slug>/page-NN.png (git-ignored) and prints the paths.
set -euo pipefail
POST="${1:?usage: preview.sh posts/<slug> [quarto] [width]}"
QUARTO="${2:-$(command -v quarto || true)}"
WIDTH="${3:-430}"
[ -n "$QUARTO" ] || { echo "quarto not found: pass its path as the second argument" >&2; exit 1; }
ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
cd "$ROOT"
POST="${POST%/}"
SLUG="$(basename "$POST")"
# Render only this page, inside the site project, so it gets the real theme, navbar and footer.
"$QUARTO" render "$POST/index.qmd" 2>&1 | grep -iE "warn|error" >&2 || true
[ -f "_site/$POST/index.html" ] || { echo "render failed: _site/$POST/index.html missing" >&2; exit 1; }
# KaTeX comes from a CDN that the sandbox may block: keep a local copy for the screenshots.
KATEX="$ROOT/_preview/.katex/package/dist"
if [ ! -f "$KATEX/katex.min.js" ] && ! curl -sfI https://cdn.jsdelivr.net/npm/katex@latest/dist/katex.min.js >/dev/null 2>&1; then
  mkdir -p "$ROOT/_preview/.katex"
  ( cd "$ROOT/_preview/.katex" && npm pack -q katex@0.16.11 >/dev/null 2>&1 && tar xzf katex-0.16.11.tgz ) || echo "warning: KaTeX unavailable, equations will show as raw TeX in the screenshots only" >&2
fi
[ -f "$KATEX/katex.min.js" ] && export KATEX_DIR="$KATEX"
node "$(dirname "$0")/shots.js" _site "$POST/" "_preview/$SLUG" "$WIDTH"
