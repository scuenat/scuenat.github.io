"""Post-render step: show the site's version in the footer of every page.

The footer (`page-footer` in _quarto.yml) holds a placeholder, `<span class="site-version">`.
This fills it with the date and short hash of the commit the site was built from,
e.g. "v2026.11.21 · 95890bf", linked to that commit on GitHub. Without git (a copy
of the files only), the placeholder is removed.
"""
import glob
import html
import os
import re
import subprocess

REPO = "https://github.com/scuenat/scuenat.github.io"
PLACEHOLDER = re.compile(r'<span class="site-version">.*?</span>', re.S)


def version():
    out = subprocess.run(["git", "log", "-1", "--format=%H %cs"],
                         capture_output=True, text=True).stdout.split()
    if len(out) != 2:
        return None
    sha, day = out
    return sha, "v" + day.replace("-", ".") + " · " + sha[:7]


def main():
    v = version()
    if v:
        sha, label = v
        stamp = (f'<span class="site-version"><a href="{REPO}/commit/{sha}" '
                 f'title="Version of this site: the commit it was built from">'
                 f'{html.escape(label)}</a></span>')
    else:
        stamp = ""
    listed = os.environ.get("QUARTO_PROJECT_OUTPUT_FILES", "").split("\n")
    files = [f for f in listed if f.endswith(".html")] or glob.glob("_site/**/*.html", recursive=True)
    for path in files:
        if not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        new = PLACEHOLDER.sub(lambda _: stamp, text)
        if new != text:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(new)


if __name__ == "__main__":
    main()
