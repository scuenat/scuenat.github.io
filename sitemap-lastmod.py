"""Post-render step: give the sitemap real modification dates and clean URLs.

Quarto stamps every sitemap entry with the file time of the build, so after a fresh
checkout every page looks changed on every deploy and search engines learn to ignore
the dates. This replaces each <lastmod> with the date of the last commit that touched
the page's source (a post's whole folder, so figures count), and writes URLs in the
directory form (/posts/x/) used by the canonical and hreflang links.
"""
import os
import re
import subprocess

SITE = "https://scuenat.github.io/"
SITEMAP = os.path.join("_site", "sitemap.xml")


def last_commit(path):
    out = subprocess.run(["git", "log", "-1", "--format=%cI", "--", path],
                         capture_output=True, text=True).stdout.strip()
    return out or None


def source_for(url):
    rel = url[len(SITE):]
    if rel == "" or rel.endswith("/"):
        rel += "index.html"
    qmd = rel[:-len(".html")] + ".qmd"
    if re.match(r"^(fr/)?posts/[^/]+/index\.qmd$", qmd):
        return os.path.dirname(qmd)
    return qmd


def fix(match):
    loc, lastmod = match.group(1), match.group(2)
    loc = re.sub(r"index\.html$", "", loc)
    src = source_for(loc)
    date = last_commit(src) if os.path.exists(src) else None
    return f"<loc>{loc}</loc>\n    <lastmod>{date or lastmod}</lastmod>"


if os.path.exists(SITEMAP):
    xml = open(SITEMAP, encoding="utf-8").read()
    xml = re.sub(r"<loc>([^<]*)</loc>\s*<lastmod>([^<]*)</lastmod>", fix, xml)
    open(SITEMAP, "w", encoding="utf-8").write(xml)
