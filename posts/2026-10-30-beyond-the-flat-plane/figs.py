"""Figures for "Tools as Neurons".

Same style as "The Interface Is Data": Inter type, white cards with a faint shadow
and a coloured accent, colours taken from the site's palette.

Figures 5 to 9 and the heat map in Figure 12 are drawn from results.json, written by
sim.py. Figure 2 is plain counting with an illustrative token cost per tool. Figures 1,
3, 4, 10, 11 and 12 (left) are schematics with hand-placed or seeded positions.
"""
import json
import re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle

# ---------- palette (from light.scss) ----------
BG = "#fbfaf7"
INK = "#1f2328"
MUTED = "#5f6b76"
RULE = "#e6e2da"
NAVY = "#1d4f73"
DEEP = "#0b1733"
AMBER = "#f5b041"
WARM = "#b36b00"
GREEN = "#2e7d5b"
RED = "#a93226"
NAVY_T, AMBER_T, GREEN_T, SAND_T = "#e5eef5", "#fdf1dc", "#e2f0e8", "#f2efe9"

SANS, MONO = "Inter", "JetBrains Mono"
plt.rcParams.update({
    "font.family": SANS, "font.size": 10, "text.color": INK,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.8,
    "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
    "savefig.dpi": 220, "savefig.bbox": "tight", "savefig.pad_inches": 0.18,
    "legend.frameon": False,
})
OUT = "figures/"


# ---------- drawing helpers ----------
def canvas(w, h, xmax, ymax):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, xmax); ax.set_ylim(0, ymax); ax.set_aspect("equal"); ax.axis("off")
    return fig, ax


def shadow(ax, x, y, w, h, r=0.28, z=1):
    for i, a in enumerate((0.035, 0.03, 0.025)):
        d = 0.05 + 0.05 * i
        ax.add_patch(FancyBboxPatch((x + d * 0.4, y - d), w, h,
                                    boxstyle=f"round,pad=0,rounding_size={r + d * 0.5}",
                                    fc=DEEP, ec="none", alpha=a, zorder=z))


def card(ax, x, y, w, h, title, sub=None, accent=NAVY, fill="white", eyebrow=None,
         fs=10.5, subfs=8.4, z=2, r=0.28, bar=True, align="center", mono_sub=False):
    """A white card with a faint shadow and a coloured accent bar on the left.
    fill set to a colour gives a solid card with white text."""
    solid = fill not in ("white", BG, NAVY_T, AMBER_T, GREEN_T, SAND_T)
    shadow(ax, x, y, w, h, r, z)
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                fc=fill, ec="none" if solid else RULE, lw=0.9, zorder=z + 1))
    if bar and not solid:
        ax.add_patch(FancyBboxPatch((x + 0.16, y + 0.2), 0.09, h - 0.4,
                                    boxstyle="round,pad=0,rounding_size=0.045",
                                    fc=accent, ec="none", zorder=z + 2))
    tcol = "white" if solid else INK
    scol = "#dfe8f1" if solid else MUTED
    shift = 0.12 if bar and not solid else 0
    cx = x + w / 2 + shift if align == "center" else x + 0.55
    ha = "center" if align == "center" else "left"
    # stack eyebrow, title and subtitle around the card's centre, measured in points
    nsub = sub.count("\n") + 1 if sub else 0
    parts = []
    if eyebrow:
        parts.append((eyebrow.upper(), dict(fontsize=6.6, weight="semibold",
                                            color=accent if not solid else AMBER), 6.6 * 1.25 + 3))
    if title:
        parts.append((title, dict(fontsize=fs, weight="semibold", color=tcol), fs * 1.25 + 3))
    if sub:
        parts.append((sub, dict(fontsize=subfs, color=scol, linespacing=1.3,
                                fontfamily=MONO if mono_sub else SANS), subfs * 1.3 * nsub))
    total = sum(p[2] for p in parts)
    off = total / 2
    for text, kw, hgt in parts:
        ax.annotate(text, (cx, y + h / 2), xytext=(0, off), textcoords="offset points",
                    ha=ha, va="top", zorder=z + 3, **kw)
        off -= hgt


def arrow(ax, p, q, color=MUTED, rad=0.0, lw=1.5, ls="-", z=1.5, head=10, alpha=1.0):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>,head_length=0.55,head_width=0.3",
                                 mutation_scale=head, color=color, lw=lw, ls=ls, alpha=alpha,
                                 connectionstyle=f"arc3,rad={rad}", shrinkA=0, shrinkB=0,
                                 capstyle="round", joinstyle="round", zorder=z))


def edge_point(x, y, w, h, tx, ty, gap=0.12):
    """Where the ray from the centre of box (x, y, w, h) toward (tx, ty) leaves the box."""
    cx, cy = x + w / 2, y + h / 2
    dx, dy = tx - cx, ty - cy
    t = min((w / 2 + gap) / abs(dx) if dx else 1e9, (h / 2 + gap) / abs(dy) if dy else 1e9)
    return cx + dx * t, cy + dy * t


def pill(ax, x, y, text, color=MUTED, fill=BG, fs=7.6, z=6, weight="medium", mono=False):
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, color=color, weight=weight,
            fontfamily=MONO if mono else SANS, zorder=z,
            bbox=dict(boxstyle="round,pad=0.32,rounding_size=0.6", fc=fill, ec=RULE, lw=0.7))


def chip(ax, x, y, text, color=NAVY, fill=NAVY_T, fs=7.2, z=6):
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, color=color, fontfamily=MONO,
            zorder=z, bbox=dict(boxstyle="round,pad=0.28,rounding_size=0.35", fc=fill, ec="none"))


def heading(ax, x, y, eyebrow, title, color=NAVY):
    ax.text(x, y, eyebrow.upper(), fontsize=7, weight="semibold", color=color, va="bottom")
    ax.text(x, y - 0.18, title, fontsize=11.5, weight="semibold", color=INK, va="top")


def tidy(ax, grid_axis="y"):
    ax.grid(axis=grid_axis, color=RULE, lw=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(length=0, labelsize=8.5)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(RULE if s == "left" else MUTED)




def _json_line(ax, x, y, line, fs):
    """Draw one line of JSON with simple syntax colours, token by token."""
    KEY, STR, LIT, PUN = "#8fc1e8", "#f5c77e", "#9fd8b8", "#aab4c0"
    tokens = re.findall(r'"[^"]*"\s*:|"[^"]*"?|\b(?:true|false|null)\b|-?\d+\.?\d*|\s+|.', line)
    from matplotlib.textpath import TextPath
    from matplotlib.font_manager import FontProperties
    fp = FontProperties(family=MONO, size=fs)
    cw = TextPath((0, 0), "M" * 10, prop=fp).get_extents().width / 10   # points per char
    cursor = 0
    for tok in tokens:
        if tok.endswith(":") and tok.startswith('"'):
            col = KEY
        elif tok.startswith('"'):
            col = STR
        elif re.fullmatch(r"true|false|null|-?\d+\.?\d*", tok):
            col = LIT
        else:
            col = PUN
        if tok.strip():
            ax.annotate(tok, (x, y), xytext=(cursor * cw, 0), textcoords="offset points",
                        fontfamily=MONO, fontsize=fs, color=col, va="center", ha="left", zorder=8)
        cursor += len(tok)



R = json.load(open("results.json"))
TEAL, PLUM = "#2a7f86", "#7a4e8c"
DOMCOL = [NAVY, GREEN, WARM, PLUM, TEAL, RED]


def blob(ax, cx, cy, rx, ry, color, alpha=0.08, z=0.5):
    from matplotlib.patches import Ellipse
    ax.add_patch(Ellipse((cx, cy), 2 * rx, 2 * ry, fc=color, ec=color, alpha=alpha, lw=0, zorder=z))
    ax.add_patch(Ellipse((cx, cy), 2 * rx, 2 * ry, fc="none", ec=color, alpha=0.35, lw=0.8,
                         ls=(0, (3, 3)), zorder=z))


def cluster_points(rng, centres, n=11, sx=0.85, sy=0.7):
    pts = []
    for (cx, cy) in centres:
        p = np.c_[rng.normal(cx, sx, n), rng.normal(cy, sy, n)]
        pts.append(p)
    return pts


# ---------- Figure 1: points on a plane, and the same points with structure ----------
def fig_plane():
    rng = np.random.default_rng(11)
    centres = [(3.0, 6.6), (8.4, 6.9), (13.8, 6.5), (3.4, 2.0), (8.8, 2.3), (14.2, 1.9)]
    names = ["invoices", "currency", "mail", "documents", "identity", "calendar"]
    pts = cluster_points(rng, centres)
    fig, axes = plt.subplots(1, 2, figsize=(11.6, 4.9))
    for ax in axes:
        ax.set_xlim(0, 17.2); ax.set_ylim(-1.0, 10.6); ax.set_aspect("equal"); ax.axis("off")
    # left: flat
    ax = axes[0]
    ax.text(0.3, 10.35, "TODAY · A FLAT CATALOGUE", fontsize=7.2, weight="semibold", color=NAVY, va="top")
    ax.text(0.3, 9.85, "Points, and a path drawn at run time", fontsize=11.5, weight="semibold", va="top")
    for p in pts:
        ax.scatter(p[:, 0], p[:, 1], s=26, color="white", edgecolor=MUTED, lw=0.9, zorder=3)
    path = [pts[0][2], pts[1][4], pts[3][1], pts[2][6]]
    for a, b in zip(path, path[1:]):
        arrow(ax, a, b, color=AMBER, ls=(0, (3, 2.5)), lw=1.6, rad=0.18, z=4)
    for i, q in enumerate(path):
        ax.scatter(*q, s=60, color=AMBER, edgecolor=WARM, lw=1, zorder=5)
        ax.text(q[0] + 0.25, q[1] + 0.3, str(i + 1), fontsize=8, color=WARM, weight="bold", zorder=6)
    pill(ax, 8.6, -0.6, "the graph lives for one task, then it is forgotten", color=WARM, fs=8)
    # right: structured
    ax = axes[1]
    ax.text(0.3, 10.35, "PROPOSED · A LOCAL GRAPH", fontsize=7.2, weight="semibold", color=GREEN, va="top")
    ax.text(0.3, 9.85, "The same points, with edges that persist", fontsize=11.5, weight="semibold", va="top")
    for i, (p, (cx, cy)) in enumerate(zip(pts, centres)):
        col = DOMCOL[i]
        blob(ax, cx, cy, 2.15, 1.75, col)
        ax.text(cx, cy - 1.45, names[i], ha="center", va="top", fontsize=7.6, color=col,
                weight="semibold", zorder=6,
                bbox=dict(boxstyle="round,pad=0.2", fc=BG, ec="none", alpha=0.85))
        d = np.linalg.norm(p[:, None] - p[None], axis=-1)
        for a in range(len(p)):
            for b in np.argsort(d[a])[1:3]:
                ax.plot(*zip(p[a], p[b]), color=col, lw=0.7, alpha=0.45, zorder=2)
        ax.scatter(p[:, 0], p[:, 1], s=26, color="white", edgecolor=col, lw=1.0, zorder=3)
    bridges = [(0, 2, 1, 4), (0, 5, 2, 6), (0, 7, 3, 1), (2, 3, 5, 8), (4, 0, 3, 5), (1, 9, 4, 2)]
    for a, ia, b, ib in bridges:
        ax.plot(*zip(pts[a][ia], pts[b][ib]), color=AMBER, lw=1.6, alpha=0.9, zorder=2.5,
                solid_capstyle="round")
    pill(ax, 8.6, -0.6, "edges inside clusters, and a few strong bridges between them", color=GREEN, fs=8)
    fig.subplots_adjust(wspace=0.04)
    fig.savefig(OUT + "fig01.png"); plt.close(fig)


# ---------- Figure 2: what grows when the catalogue grows ----------
def fig_growth():
    n = np.logspace(1, 4, 200)
    tok = R["tokens_per_tool"]
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 3.9))
    ax = axes[0]
    ax.plot(n, n * tok, color=NAVY, lw=2.2)
    for lim, lab in ((200e3, "a 200k-token context window"), (1e6, "a 1M-token context window")):
        ax.axhline(lim, color=WARM, lw=1, ls=(0, (4, 3)))
        ax.text(11, lim * 1.15, lab, fontsize=8, color=WARM)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("tools in the catalogue"); ax.set_ylabel("tokens to list every definition")
    ax.set_title("Listing everything", loc="left", fontsize=11, weight="semibold")
    tidy(ax, "both")
    ax = axes[1]
    ax.plot(n, n ** 4, color=RED, lw=2.2, label="possible 4-step chains, $N^4$")
    ax.plot(n, n * 3, color=GREEN, lw=2.2, label="edges in a sparse graph, ~$3N$")
    ax.plot(n, n / 2, color=GREEN, lw=1.4, ls=(0, (4, 2)), label="workflows actually run, ~$N/2$")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("tools in the catalogue"); ax.set_ylabel("count")
    ax.set_title("Possible compositions against useful ones", loc="left", fontsize=11, weight="semibold")
    ax.legend(fontsize=8, loc="upper left")
    tidy(ax, "both")
    fig.tight_layout(w_pad=3)
    fig.savefig(OUT + "fig02.png"); plt.close(fig)


# ---------- Figure 5: resemblance is not complementarity ----------
def fig_similarity():
    p = R["pairs"]
    sr, ss, sc = np.array(p["rand"]), np.array(p["same"]), np.array(p["cross"])
    fig, ax = plt.subplots(figsize=(8.4, 3.8))
    bins = np.linspace(-0.45, 1.0, 59)
    for data, col, lab in ((sr, MUTED, "two tools picked at random"),
                           (ss, NAVY, "used together, same domain"),
                           (sc, AMBER, "used together, different domains")):
        h, e = np.histogram(data, bins=bins, density=True)
        c = (e[1:] + e[:-1]) / 2
        ax.fill_between(c, h, color=col, alpha=0.18, lw=0)
        ax.plot(c, h, color=col if col != AMBER else WARM, lw=1.8, label=lab)
    ax.set_xlabel("resemblance of the two descriptions (cosine similarity)")
    ax.set_ylabel("share of pairs")
    ax.set_yticks([])
    ax.legend(fontsize=8.5, loc="upper right")
    xs = sc
    ax.text(-0.43, ax.get_ylim()[1] * 0.62,
            f"{np.mean(xs < 0.3):.0%} of the partners used\nacross domains resemble\neach other no more than\ntwo tools picked at random",
            fontsize=8.2, color=WARM, va="top", linespacing=1.4)
    tidy(ax, "x")
    fig.savefig(OUT + "fig05.png"); plt.close(fig)


# ---------- Figure 4: the experiment ----------
def fig_scale():
    s = R["scale"]
    ns = sorted(int(k) for k in s)
    fig, ax = plt.subplots(figsize=(8.4, 4.2))
    series = [("flat", "flat: nearest descriptions", MUTED, "o"),
              ("hierarchy", "layer on top: nearest domains, then tools", RED, "s"),
              ("declared", "local graph: edges declared by authors", NAVY, "D"),
              ("learned", "local graph: edges learned from traces", GREEN, "^"),
              ("gnn", "graph neural network over learned edges", AMBER, "v")]
    for key, lab, col, m in series:
        y = np.array([s[str(n)][key][0] for n in ns]) * 100
        e = np.array([s[str(n)][key][1] for n in ns]) * 100
        ax.errorbar(ns, y, yerr=e, color=col if col != AMBER else WARM, lw=2, marker=m, ms=6,
                    capsize=3, label=lab, mec="white", mew=0.8)
    ax.set_xscale("log")
    ax.set_xticks(ns); ax.set_xticklabels([f"{n:,}" for n in ns])
    ax.set_ylim(-3, 103)
    ax.set_xlabel("tools in the catalogue")
    ax.set_ylabel("tasks with every needed tool\namong the 12 offered (%)")
    ax.legend(fontsize=8.3, loc="center right", bbox_to_anchor=(1.0, 0.45))
    tidy(ax)
    fig.savefig(OUT + "fig06.png"); plt.close(fig)


# ---------- Figure 5: learning the edges ----------
def fig_learning():
    L = R["learning"]
    ts = sorted(int(k) for k in L)
    x = [max(t, 30) for t in ts]
    fig, ax = plt.subplots(figsize=(8.4, 3.7))
    for key, lab, col in (("declared", "edges declared by authors", NAVY),
                          ("learned", "graph walk over learned edges", GREEN),
                          ("gnn", "graph neural network over learned edges", WARM),
                          ("flat", "flat: nearest descriptions", MUTED)):
        pts = [(xx, L[str(t)][key] * 100) for xx, t in zip(x, ts) if key in L[str(t)]]
        ax.plot(*zip(*pts), color=col, lw=2, marker="o", ms=5, mec="white", label=lab)
    ax.set_xscale("log")
    ax.set_xticks(x); ax.set_xticklabels(["none"] + [f"{t:,}" for t in ts[1:]])
    ax.set_ylim(-3, 100)
    ax.set_xlabel("past tasks observed (1,000 tools, 500 kinds of workflow)")
    ax.legend(fontsize=8.3, loc="center right")
    ax.set_ylabel("tasks fully covered (%)")
    tidy(ax)
    fig.savefig(OUT + "fig07.png"); plt.close(fig)


# ---------- Figure 6: three answers ----------
def fig_three_answers():
    fig, ax = canvas(11.6, 4.9, 30, 12.6)
    cols = [(0.2, "A · a layer on top", "A registry routes", RED),
            (10.2, "B · edges in the protocol", "Servers publish neighbours", NAVY),
            (20.2, "C · edges from use", "Use draws the edges", GREEN)]
    for x, eb, t, col in cols:
        heading(ax, x, 12.3, eb, t, col)
    # A
    card(ax, 2.2, 7.6, 5.6, 1.9, "Router / registry", "one index of everything", accent=RED, fill=RED)
    for i in range(4):
        xx = 0.4 + i * 2.35
        card(ax, xx, 3.0, 2.0, 1.6, f"S{i + 1}", None, accent=RED, fs=9.5)
        arrow(ax, (5.0, 7.5), (xx + 1.0, 4.75), color=RED, lw=1.1)
    ax.text(5.0, 1.6, "+ easy to add, one place to govern\n− a single point of truth and of failure\n− knows names, not how tools combine",
            ha="center", va="top", fontsize=8, color=MUTED, linespacing=1.5)
    # B
    rng = np.random.default_rng(3)
    srv = [(12.2, 7.8), (16.6, 8.2), (13.2, 3.6), (17.6, 4.2)]
    for i, (sx, sy) in enumerate(srv):
        blob(ax, sx, sy, 1.75, 1.45, NAVY, alpha=0.07)
        p = np.c_[rng.normal(sx, 0.55, 5), rng.normal(sy, 0.45, 5)]
        for a in range(5):
            ax.plot(*zip(p[a], p[(a + 1) % 5]), color=NAVY, lw=0.8, alpha=0.5)
        ax.scatter(p[:, 0], p[:, 1], s=20, color="white", edgecolor=NAVY, lw=1, zorder=3)
        srv[i] = p
    for a, ia, b, ib in ((0, 1, 1, 3), (0, 4, 2, 0), (1, 2, 3, 1), (2, 3, 3, 4)):
        ax.plot(*zip(srv[a][ia], srv[b][ib]), color=AMBER, lw=1.5, zorder=2)
    ax.text(15.0, 1.6, "+ no centre: each node knows its neighbours\n+ travels with the tool, versioned with it\n− authors see only their own side",
            ha="center", va="top", fontsize=8, color=MUTED, linespacing=1.5)
    # C
    for i, (lab, yy) in enumerate((("trace 1", 9.0), ("trace 2", 7.8), ("trace 3", 6.6))):
        ax.text(20.4, yy, lab, fontsize=7.4, color=MUTED, va="center", fontfamily=MONO)
        seq = [(22.4 + j * 1.3, yy) for j in range(4)]
        for j, q in enumerate(seq):
            ax.scatter(*q, s=24, color=["white", GREEN_T, "white", GREEN_T][(i + j) % 4],
                       edgecolor=GREEN, lw=1, zorder=3)
            if j:
                ax.plot(*zip(seq[j - 1], q), color=GREEN, lw=0.8, alpha=0.6)
    arrow(ax, (24.4, 6.0), (24.4, 5.1), color=GREEN)
    g = [(22.4, 3.6), (24.3, 4.4), (26.3, 3.6), (24.3, 2.8), (28.0, 4.3)]
    w = [(0, 1, 3.5), (1, 2, 2.2), (2, 3, 1.0), (3, 0, 2.6), (2, 4, 1.4), (0, 2, 0.6)]
    for a, b, lw in w:
        ax.plot(*zip(g[a], g[b]), color=GREEN, lw=lw, alpha=0.75, solid_capstyle="round")
    for q in g:
        ax.scatter(*q, s=34, color="white", edgecolor=GREEN, lw=1.1, zorder=3)
    ax.text(25.0, 1.6, "+ weights show what is really used\n+ finds partners nobody declared\n− needs history; private by default",
            ha="center", va="top", fontsize=8, color=MUTED, linespacing=1.5)
    for xx in (9.7, 19.7):
        ax.plot([xx, xx], [0.4, 12.0], color=RULE, lw=1)
    fig.savefig(OUT + "fig10.png"); plt.close(fig)


# ---------- Figure 7: a tool entry with edges ----------
JSON = """{
  "name": "pay_supplier_invoice",
  "description": "Pays an approved invoice.",
  "inputSchema": { ... },
  "outputSchema": { ... },
  "annotations": { "destructiveHint": true },
  "_meta": {
    "edges": [
      { "rel": "requires",   "tool": "approve_invoice" },
      { "rel": "feeds",      "tool": "post_ledger_entry" },
      { "rel": "uses",       "server": "fx-rates",
        "tool": "convert",   "weight": 0.71 },
      { "rel": "notifies",   "server": "mail",
        "tool": "send_message" },
      { "rel": "alternative","tool": "schedule_payment" }
    ],
    "cluster": "accounts-payable"
  }
}"""


def fig_entry():
    fig, ax = canvas(10.4, 5.7, 25, 13.6)
    shadow(ax, 0.2, 2.0, 13.6, 11.3, r=0.35)
    ax.add_patch(FancyBboxPatch((0.2, 2.0), 13.6, 11.3, boxstyle="round,pad=0,rounding_size=0.35",
                                fc=DEEP, ec="none", zorder=2))
    for i, c in enumerate(("#e06c5f", AMBER, "#5fb98a")):
        ax.add_patch(Circle((0.75 + i * 0.45, 12.8), 0.13, fc=c, ec="none", zorder=3))
    ax.text(13.4, 12.8, "tools/list → one entry, with its neighbourhood", ha="right", va="center",
            fontsize=7.4, color="#8592a3", fontfamily=MONO, zorder=3)
    lines = JSON.split("\n")
    top, step = 12.05, 0.54
    ys = {}
    for i, line in enumerate(lines):
        y = top - i * step
        _json_line(ax, 0.75, y, line, 7.6)
        for key in ("_meta", "requires", "uses", "alternative", "cluster"):
            if f'"{key}"' in line and key not in ys:
                ys[key] = y
    notes = [
        ("_meta", "Where it goes", "today, in the _meta field the spec\nalready allows; later, a field of its own", MUTED),
        ("requires", "Typed edges", "requires, feeds, alternative: the\nlocal shape of a workflow", NAVY),
        ("uses", "Edges across servers", "a weight learned from use, so the\nfrequent bridges stand out", WARM),
        ("cluster", "Membership", "which sub-graph the tool belongs to,\nso a caller can load it as one", GREEN),
    ]
    ny = [11.9, 9.15, 6.4, 3.65]
    for (key, t, txt, col), yy in zip(notes, ny):
        y0 = ys[key]
        ax.plot([13.85, 14.5], [y0, y0], color=col, lw=1.1, zorder=4)
        ax.plot([14.5, 14.95], [y0, yy], color=col, lw=1.1, zorder=4)
        ax.add_patch(Circle((13.85, y0), 0.09, fc=col, ec="none", zorder=5))
        card(ax, 15.0, yy - 1.15, 9.8, 2.3, "", None, accent=col, bar=True)
        ax.text(15.5, yy + 0.55, t, fontsize=10, weight="semibold", va="center", zorder=6)
        ax.text(15.5, yy - 0.3, txt, fontsize=8.1, color=MUTED, va="center", zorder=6, linespacing=1.35)
    fig.savefig(OUT + "fig11.png"); plt.close(fig)


# ---------- Figure 8: entanglement between sub-graphs ----------
def fig_entangle():
    fig = plt.figure(figsize=(11.4, 4.6))
    ax = fig.add_axes([0.0, 0.0, 0.55, 1.0])
    ax.set_xlim(0, 15); ax.set_ylim(0, 12.2); ax.set_aspect("equal"); ax.axis("off")
    ax.text(0.2, 12.0, "SCHEMATIC", fontsize=7.2, weight="semibold", color=NAVY, va="top")
    ax.text(0.2, 11.45, "Choosing in one cluster informs the other", fontsize=11.5, weight="semibold", va="top")
    rng = np.random.default_rng(5)
    A = np.c_[rng.normal(3.6, 1.0, 10), rng.normal(5.6, 1.1, 10)]
    B = np.c_[rng.normal(11.3, 1.0, 10), rng.normal(5.6, 1.1, 10)]
    blob(ax, 3.6, 5.6, 2.9, 3.3, NAVY, alpha=0.07)
    blob(ax, 11.3, 5.6, 2.9, 3.3, GREEN, alpha=0.07)
    ax.text(3.6, 1.6, "invoices", ha="center", fontsize=8.5, color=NAVY, weight="medium")
    ax.text(11.3, 1.6, "currency", ha="center", fontsize=8.5, color=GREEN, weight="medium")
    chosen = 3
    w = np.exp(-np.linalg.norm(B - B[6], axis=1) ** 2 / 1.2)
    w = w / w.max()
    for i, p in enumerate(A):
        ax.scatter(*p, s=70 if i == chosen else 28, color=NAVY if i == chosen else "white",
                   edgecolor=NAVY, lw=1.1, zorder=4)
    for j, p in enumerate(B):
        ax.scatter(*p, s=28 + 90 * w[j], color=GREEN, alpha=0.15 + 0.85 * w[j], edgecolor=GREEN,
                   lw=1, zorder=4)
    for j in np.argsort(-w)[:3]:
        ax.plot(*zip(A[chosen], B[j]), color=AMBER, lw=0.6 + 2.2 * w[j], alpha=0.85, zorder=3,
                solid_capstyle="round")
    ax.text(3.6, 9.55, "you pick this tool…", ha="center", fontsize=8, color=NAVY)
    ax.text(11.3, 9.55, "…and these become likely", ha="center", fontsize=8, color=GREEN)
    ax.text(7.45, 0.55, "not because they look alike, but because they are used together",
            ha="center", fontsize=8, color=WARM, style="italic")
    # right: learned coupling between domains
    ax2 = fig.add_axes([0.6, 0.2, 0.36, 0.68])
    M = np.array(R["coupling"])
    order = list(range(len(M)))
    im = ax2.imshow(M[np.ix_(order, order)], cmap=matplotlib.colors.LinearSegmentedColormap.from_list(
        "c", [BG, NAVY_T, NAVY, DEEP]), vmin=0, vmax=M.max())
    ax2.set_xticks([]); ax2.set_yticks([])
    for s in ax2.spines.values():
        s.set_visible(True); s.set_color(RULE)
    ax2.set_xlabel("domain of a helper tool", fontsize=8.5, color=MUTED)
    ax2.set_ylabel("domain of the main tool", fontsize=8.5, color=MUTED)
    ax2.set_title("Learned coupling, 20 domains", loc="left", fontsize=10.5, weight="semibold")
    ax2.text(-0.5, 22.6, "from 2,500 simulated traces (sim.py). Each row has two\ndark cells: the partners that domain really leans on.",
             fontsize=7.6, color=MUTED, va="top", linespacing=1.4)
    fig.savefig(OUT + "fig12.png"); plt.close(fig)


# ---------- Figure 3: tools as neurons ----------
def fig_neurons():
    rng = np.random.default_rng(4)
    fig, ax = canvas(11.6, 5.0, 30, 12.9)
    heading(ax, 0.2, 12.6, "Analogy", "A layer of neurons", NAVY)
    heading(ax, 10.6, 12.6, "Proposal", "A network of tools: two tasks, two sparse sub-networks", GREEN)
    # left: a small neural layer, sparse activation
    L = [np.c_[np.full(5, 1.5), np.linspace(2.2, 9.6, 5)], np.c_[np.full(7, 4.6), np.linspace(1.4, 10.4, 7)],
         np.c_[np.full(5, 7.7), np.linspace(2.2, 9.6, 5)]]
    act = [{1, 3}, {2, 5}, {1}]
    for a, b in ((0, 1), (1, 2)):
        for i, p in enumerate(L[a]):
            for j, q in enumerate(L[b]):
                on = i in act[a] and j in act[b]
                ax.plot(*zip(p, q), color=AMBER if on else RULE, lw=1.8 if on else 0.6, zorder=1)
    for k, layer in enumerate(L):
        for i, p in enumerate(layer):
            on = i in act[k]
            ax.add_patch(Circle(p, 0.42, fc=AMBER if on else "white", ec=WARM if on else MUTED, lw=1.1, zorder=3))
    ax.text(4.6, 0.25, "weights learned · few units fire per input", ha="center", fontsize=8, color=MUTED)
    # right: tool network, clusters, two tasks
    centres = [(13.6, 9.0), (19.0, 9.6), (24.8, 9.0), (14.6, 3.6), (20.2, 3.4), (25.8, 3.9)]
    names = ["invoices", "currency", "mail", "documents", "identity", "calendar"]
    pts = []
    for i, (cx, cy) in enumerate(centres):
        blob(ax, cx, cy, 2.25, 1.75, DOMCOL[i], alpha=0.06)
        ax.text(cx, cy - 2.0, names[i], ha="center", va="top", fontsize=7.4, color=DOMCOL[i], weight="semibold")
        p = np.c_[rng.normal(cx, 0.85, 7), rng.normal(cy, 0.6, 7)]
        pts.append(p)
        d = np.linalg.norm(p[:, None] - p[None], axis=-1)
        for a in range(7):
            for b in np.argsort(d[a])[1:3]:
                ax.plot(*zip(p[a], p[b]), color=RULE, lw=0.8, zorder=1)
    bridges = [(0, 1, 1, 2), (0, 3, 2, 4), (3, 2, 4, 1), (1, 5, 4, 3), (2, 1, 5, 2), (0, 6, 3, 0)]
    for a, ia, b, ib in bridges:
        ax.plot(*zip(pts[a][ia], pts[b][ib]), color=RULE, lw=1.2, zorder=1)
    taskA = [(0, 1), (0, 4), (1, 2), (2, 4)]           # pay an invoice in euros, confirm by mail
    taskB = [(3, 2), (4, 1), (4, 5), (5, 3)]           # sign a contract, book a meeting
    for task, col in ((taskA, AMBER), (taskB, TEAL)):
        for (a, ia), (b, ib) in zip(task, task[1:]):
            ax.plot(*zip(pts[a][ia], pts[b][ib]), color=col, lw=2.4, zorder=2, solid_capstyle="round")
    for k, p in enumerate(pts):
        for i, q in enumerate(p):
            col = AMBER if (k, i) in taskA else TEAL if (k, i) in taskB else None
            ax.add_patch(Circle(q, 0.3 if col else 0.2, fc=col or "white", ec=WARM if col == AMBER else (col or MUTED),
                                lw=1, zorder=3))
    pill(ax, 15.6, 0.25, "task A · pay an invoice in euros, confirm by mail", color=WARM, fs=7.6)
    pill(ax, 24.6, 0.25, "task B · sign a contract, book the meeting", color=TEAL, fs=7.6)
    ax.plot([9.6, 9.6], [0.6, 12.0], color=RULE, lw=1)
    fig.savefig(OUT + "fig03.png"); plt.close(fig)


# ---------- Figure 4: the router as a graph neural network ----------
def fig_architecture():
    fig, ax = canvas(11.6, 4.3, 30, 11.0)
    steps = [
        (0.2, "Request", "“pay this invoice\nin euros”", MUTED, "input"),
        (5.2, "Resemblance", "cosine to every\ntool description", NAVY, "s = E q"),
        (10.2, "k winners fire", "only the 3 closest\ntools are active", WARM, "x0 = top3(s)"),
        (15.2, "Messages", "one and two hops on\nedges; whole clusters", GREEN, "Âx · Â²x · own · coupled"),
        (20.2, "Readout", "one small function,\nshared by every tool", PLUM, "z = f(features)"),
        (25.2, "Top-K", "the 12 tools shown\nto the model", NAVY, "K = 12"),
    ]
    for x, t, sub, col, eq in steps:
        card(ax, x, 4.6, 4.4, 3.4, t, sub, accent=col, fs=10, subfs=7.8)
        ax.text(x + 2.3, 3.7, eq, ha="center", va="top", fontsize=7.8, color=col if col != AMBER else WARM,
                fontfamily=MONO)
    for x, *_ in steps[:-1]:
        arrow(ax, (x + 4.5, 6.3), (x + 5.1, 6.3), color=MUTED)
    ax.text(0.2, 10.6, "THE ROUTER", fontsize=7.2, weight="semibold", color=NAVY, va="top")
    ax.text(0.2, 10.05, "A graph neural network chooses which tools to activate", fontsize=11.5, weight="semibold", va="top")
    ax.text(15.0, 1.3, "Edges grow from use (Hebbian counts). Only the readout is trained: nine weights and a bias, fitted by logistic regression.",
            ha="center", fontsize=8.2, color=MUTED, style="italic")
    fig.savefig(OUT + "fig04.png"); plt.close(fig)


# ---------- Figure 8: activation patterns ----------
def fig_patterns():
    P = R["patterns"]
    dom = np.array(P["dom"])
    order = np.argsort(dom, kind="stable")
    pos = np.empty_like(order); pos[order] = np.arange(len(order))
    fig, ax = plt.subplots(figsize=(10.4, 3.8))
    for r, (pk, tk) in enumerate(zip(P["picks"], P["tasks"])):
        ax.scatter(pos[pk], np.full(len(pk), r), s=9, color=NAVY_T, edgecolor=NAVY, lw=0.5, zorder=2)
        hit = [t for t in tk if t in pk]
        ax.scatter(pos[hit], np.full(len(hit), r), s=16, color=AMBER, edgecolor=WARM, lw=0.6, zorder=3)
    bounds = np.r_[0, np.flatnonzero(np.diff(dom[order])) + 1, len(order)]
    for i, (a, b) in enumerate(zip(bounds[:-1], bounds[1:])):
        if i % 2 == 0:
            ax.axvspan(a, b, color=SAND_T, zorder=0, lw=0)
    ax.set_xlim(0, len(order)); ax.set_ylim(-1, len(P["picks"]))
    ax.invert_yaxis()
    ax.set_xlabel("1,000 tools, grouped by domain (bands)")
    ax.set_ylabel("40 test tasks")
    ax.set_yticks([])
    ax.set_xticks([])
    for s_ in ("left", "bottom"):
        ax.spines[s_].set_visible(False)
    share = 12 / len(order)
    ax.set_title(f"Each task activates {share:.1%} of the network; two tasks share {R['overlap']:.0%} of their active tools on average",
                 loc="left", fontsize=10.5, weight="semibold")
    from matplotlib.lines import Line2D
    ax.legend(handles=[Line2D([], [], marker="o", ls="", color=NAVY_T, mec=NAVY, label="activated (shown to the model)"),
                       Line2D([], [], marker="o", ls="", color=AMBER, mec=WARM, label="activated and needed by the task")],
              fontsize=8, loc="lower right", bbox_to_anchor=(1, 1.06), ncol=2)
    fig.savefig(OUT + "fig08.png"); plt.close(fig)


# ---------- Figure 9: step by step, seen and new workflows ----------
def fig_steps():
    s = R["scale"]
    ns = sorted(int(k) for k in s)
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.0), sharey=True)
    series = [("flat", "resemblance, whole catalogue", MUTED, "o"),
              ("hard", "resemblance, coupled clusters only", GREEN, "s"),
              ("gnn", "graph neural network", WARM, "v"),
              ("gated", "gate: network if a neighbour fits, else clusters", PLUM, "D")]
    for ax, label, title in ((axes[0], "seen", "Workflows seen before"), (axes[1], "novel", "Workflows never seen")):
        for key, lab, col, m in series:
            y = np.array([s[str(n)][f"{label}_step_{key}"][0] for n in ns]) * 100
            e = np.array([s[str(n)][f"{label}_step_{key}"][1] for n in ns]) * 100
            ax.errorbar(ns, y, yerr=e, color=col, lw=2, marker=m, ms=5.5, capsize=3, label=lab,
                        mec="white", mew=0.8)
        ax.set_xscale("log"); ax.set_xticks(ns); ax.set_xticklabels([f"{n:,}" for n in ns])
        ax.set_ylim(-3, 103)
        ax.set_title(title, loc="left", fontsize=11, weight="semibold")
        ax.set_xlabel("tools in the catalogue")
        tidy(ax)
    axes[0].set_ylabel("workflows fully found,\nstep by step (%)")
    h, l = axes[1].get_legend_handles_labels()
    fig.legend(h, l, fontsize=8.5, loc="lower center", ncol=2, bbox_to_anchor=(0.5, -0.1))
    fig.tight_layout(w_pad=2)
    fig.savefig(OUT + "fig09.png"); plt.close(fig)


if __name__ == "__main__":
    fig_plane(); fig_growth(); fig_similarity(); fig_neurons(); fig_architecture()
    fig_scale(); fig_learning(); fig_patterns(); fig_steps()
    fig_three_answers(); fig_entry(); fig_entangle()
