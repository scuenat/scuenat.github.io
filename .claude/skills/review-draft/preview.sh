#!/usr/bin/env bash
# Build one self-contained HTML preview of a post: full text, figures, equations, citations.
# Usage: .claude/skills/review-draft/preview.sh posts/YYYY-MM-DD-slug [quarto-binary]
# Writes _preview/<slug>.html (git-ignored) and prints its path.
set -euo pipefail
POST="${1:?usage: preview.sh posts/<slug> [quarto]}"
QUARTO="${2:-$(command -v quarto || true)}"
[ -n "$QUARTO" ] || { echo "quarto not found: pass its path as the second argument" >&2; exit 1; }
ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
SLUG="$(basename "$POST")"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
# Copy the post outside the Quarto project so the site config does not apply.
cp -r "$ROOT/$POST/." "$WORK/"
rm -rf "$WORK/__pycache__"
cat > "$WORK/_quarto.yml" <<'YML'
format:
  html:
    embed-resources: true
    html-math-method: mathml
    toc: true
    toc-depth: 2
    number-sections: false
    theme: cosmo
    fontsize: 1.05em
    max-width: 46em
    title-block-banner: false
author: "Stéphane Cuenat"
YML
( cd "$WORK" && "$QUARTO" render index.qmd --to html --output "$SLUG.html" >/dev/null 2>"$WORK/render.log" ) || { cat "$WORK/render.log" >&2; exit 1; }
grep -iE "warn|error" "$WORK/render.log" >&2 || true
mkdir -p "$ROOT/_preview"
cp "$WORK/$SLUG.html" "$ROOT/_preview/$SLUG.html"
echo "$ROOT/_preview/$SLUG.html"
