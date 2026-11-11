#!/usr/bin/env python3
"""Promote a reviewed draft to a published post.

Usage: python3 .claude/skills/new-post/promote-draft.py <name> [YYYY-MM-DD]

Moves drafts/<name>/ to posts/<date>-<name>/ (and fr/drafts/<name>/ to fr/posts/<date>-<name>/
when the French draft exists) with git mv, sets `date:` in both front matters to the
publication date (default: today), removes `draft-version:` and `draft-revised:`, and rewrites the links that change with the move:

- links to published posts, `../../posts/<slug>/` from a draft, become `../<slug>/`;
- the French draft's links to the English draft's files, `../../../drafts/<name>/`,
  become `../../../posts/<date>-<name>/`;
- any other page in the repository that links `drafts/<name>/` is pointed at the new folder.

It changes files only; review the diff, render, then commit and push (see new-post, step 7).
"""
import datetime
import pathlib
import re
import subprocess
import sys

if len(sys.argv) < 2:
    sys.exit(__doc__)
name = sys.argv[1].strip("/").split("/")[-1]
date = sys.argv[2] if len(sys.argv) > 2 else datetime.date.today().isoformat()
if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
    sys.exit("date must be YYYY-MM-DD")
root = pathlib.Path(subprocess.run(["git", "rev-parse", "--show-toplevel"],
                                   capture_output=True, text=True, check=True).stdout.strip())
new = f"{date}-{name}"
moves = [(root / "drafts" / name, root / "posts" / new),
         (root / "fr" / "drafts" / name, root / "fr" / "posts" / new)]
if not moves[0][0].is_dir():
    sys.exit(f"no draft at drafts/{name}/")
for src, dst in moves:
    if dst.exists():
        sys.exit(f"{dst.relative_to(root)} already exists")

for src, dst in moves:
    if not src.is_dir():
        continue
    subprocess.run(["git", "mv", str(src), str(dst)], check=True, cwd=root)
    qmd = dst / "index.qmd"
    text = qmd.read_text(encoding="utf-8")
    text = re.sub(r"(?m)^date:.*$", f"date: {date}", text, count=1)
    text = re.sub(r"(?m)^draft-(version|revised):.*\n", "", text)    # drafts only
    text = re.sub(r"(?<!\.\./)\.\./\.\./posts/", "../", text)          # draft -> sibling post
    text = text.replace(f"../../../drafts/{name}/", f"../../../posts/{new}/")  # fr -> en files
    qmd.write_text(text, encoding="utf-8")
    print(f"moved {src.relative_to(root)}/ -> {dst.relative_to(root)}/")

# Other pages that link the draft (another draft, a series page, About ...).
pattern = re.compile(rf"drafts/{re.escape(name)}/")
for path in root.rglob("*.qmd"):
    rel = path.relative_to(root)
    if rel.parts[0] in ("_site", ".quarto", "_preview"):
        continue
    text = path.read_text(encoding="utf-8")
    if pattern.search(text):
        path.write_text(pattern.sub(f"posts/{new}/", text), encoding="utf-8")
        print(f"relinked {rel}")

left = subprocess.run(["git", "grep", "-n", f"drafts/{name}"], capture_output=True, text=True,
                      cwd=root).stdout.strip()
if left:
    print("still pointing at the draft, fix by hand:\n" + left)
print(f"\nPublished path: posts/{new}/. Next: series pages, read-next links, render, commit, push.")
