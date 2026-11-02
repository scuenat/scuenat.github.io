"""Figures for "The Mathematics Still to Come".

Same style as "The Context Is the Wire": Inter type, white cards with a faint shadow
and a coloured accent, colours taken from the site's palette.

Figure 1 draws illustrative curves (not data) in the shape described by Belkin et al.
(2019). Figure 2 is a schematic timeline; the dates are the usual dates of first
publication, given in the text with their sources. Figure 3 is a map of the five hunches.
fig_toolbox() is kept for reference but no longer used: Table 1 in the text replaces it.
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
    "savefig.dpi": 220, "savefig.bbox": "tight", "savefig.pad_inches": 0.35,
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


# ---------- shared pieces ----------


# ---------- Figure 1: a borrowed toolbox ----------
TOOLS = [  # (year, label, row)  row > 0 above the axis, < 0 below
    (1684, "Differential\ncalculus\nLeibniz", 1),
    (1763, "Bayes' rule\nBayes", -1),
    (1805, "Least squares\nLegendre", 2),
    (1847, "Gradient descent\nCauchy", 1),
    (1858, "Matrices\nCayley", 2),
    (1868, "The Boltzmann\ndistribution\n(softmax)", -1),
    (1906, "Markov chains\nMarkov", 2),
    (1948, "Information\ntheory, entropy\nShannon", -1),
]
NEW = [(1986, "Backpropagation\nas a training method", 1), (2017, "Attention\nTransformer", -1)]


def year_x(y, y0=1660, y1=2040, x0=0.8, x1=21.2):
    return x0 + (y - y0) / (y1 - y0) * (x1 - x0)


def fig_toolbox():
    fig, ax = canvas(11, 5.6, 22, 11.2)
    heading(ax, 0.4, 10.95, "A borrowed toolbox",
            "Most of the mathematics inside a modern model was written down before 1950")
    ya = 4.6
    ax.plot([year_x(1660), year_x(2040)], [ya, ya], color=RULE, lw=3, solid_capstyle="round", zorder=1)
    ax.axvspan(year_x(1950), year_x(2040), ymin=0.08, ymax=0.82, color=AMBER_T, alpha=0.6, zorder=0)
    ax.text(year_x(1995), 8.75, "the era of\nlearning machines", ha="center", fontsize=7.6, color=WARM)
    for t in (1700, 1800, 1900, 2000):
        ax.text(year_x(t), ya - 0.42, str(t), ha="center", va="top", fontsize=7.4, color=MUTED)
        ax.plot([year_x(t)] * 2, [ya - 0.12, ya + 0.12], color=MUTED, lw=0.8, zorder=1.2)
    levels = {1: 6.3, 2: 8.1, -1: 2.9, -2: 1.1}
    for year, label, row in TOOLS + NEW:
        x, y = year_x(year), levels[row]
        col = NAVY if (year, label, row) in TOOLS else WARM
        ax.plot([x, x], [ya, y + (-0.1 if row > 0 else 0.55)], color=col, lw=0.9, alpha=0.6, zorder=1.1)
        ax.add_patch(Circle((x, ya), 0.17, fc=col, ec="white", lw=1.2, zorder=3))
        ax.text(x, y, label + f"\n{year}", ha="center", va="bottom" if row > 0 else "top", fontsize=8.4,
                color=INK, linespacing=1.25, zorder=4,
                bbox=dict(boxstyle="round,pad=0.35,rounding_size=0.4", fc="white", ec=RULE, lw=0.7))
    fig.savefig(OUT + "fig01.png", dpi=400); fig.savefig(OUT + "fig01.svg"); plt.close(fig)


# ---------- Figure 2: the engine before the theory ----------
def lane(ax, y, title, events, accent, last_open=False):
    ax.text(0.4, y + 1.0, title.upper(), fontsize=7, weight="semibold", color=accent, va="bottom")
    xs = [year_x(e[0], 1700, 2040) if e[0] else 21.0 for e in events]
    ax.plot([0.8, 21.2], [y, y], color=RULE, lw=3, solid_capstyle="round", zorder=1)
    for ev, x in zip(events, xs):
        year, label, kind = ev[:3]
        up = len(ev) > 3
        col = WARM if kind == "build" else (GREEN if kind == "theory" else MUTED)
        if year:
            ax.add_patch(Circle((x, y), 0.2, fc=col, ec="white", lw=1.2, zorder=3))
        else:
            ax.add_patch(Circle((x, y), 0.26, fc="white", ec=MUTED, lw=1.1, ls=(0, (2, 2)), zorder=3))
            ax.text(x, y, "?", ha="center", va="center", fontsize=9, color=MUTED, weight="semibold", zorder=4)
        ax.text(x, y + 0.45 if up else y - 0.45, (str(year) + "\n" if year else "") + label, ha="center",
                va="bottom" if up else "top",
                fontsize=8.6, color=INK if year else MUTED, linespacing=1.25)


def fig_engine():
    fig, ax = canvas(11, 4.9, 22, 9.8)
    heading(ax, 0.4, 9.55, "The engine before the theory",
            "Steam engines ran for a century before thermodynamics explained them")
    lane(ax, 6.0, "Engines", [
        (1712, "Newcomen's\nengine", "build"), (1769, "Watt's\ncondenser", "build"),
        (1824, "Carnot", "theory"), (1865, "Clausius:\nentropy", "theory"),
        (1877, "Boltzmann:\nentropy as counting", "theory", "up")], WARM)
    lane(ax, 2.5, "Learning machines", [
        (1958, "Perceptron", "build"), (1986, "Back-\npropagation", "build"),
        (2012, "Deep nets\nwin", "build"), (None, "our\nCarnot", "open")], NAVY)
    for (lab, col, x) in (("built and run", WARM, 13.6), ("explained", GREEN, 17.0)):
        ax.add_patch(Circle((x, 8.55), 0.16, fc=col, ec="none"))
        ax.text(x + 0.35, 8.55, lab, va="center", fontsize=7.6, color=MUTED)
    fig.savefig(OUT + "fig02.png", dpi=400); fig.savefig(OUT + "fig02.svg"); plt.close(fig)


# ---------- Figure 3: the curve the textbook predicted, and the one we see ----------
def fig_descent():
    fig, axes = plt.subplots(2, 1, figsize=(5.6, 8.4), sharex=True)
    x = np.linspace(0.05, 1.0, 400)
    thr = 0.42  # where the model can just fit the training data
    train_l = np.clip(1.15 * (1 - x / thr), 0, None) ** 1.6 * 0.9 + 0.02
    classical = 0.35 + 1.6 * (x - 0.27) ** 2
    bump = 0.95 * np.exp(-((x - thr) / 0.055) ** 2)
    modern = 0.17 + 0.45 * np.exp(-x / 0.3) + bump * 0.75
    for ax, test, title, sub in (
        (axes[0], classical, "What the textbook predicted", "too big a model overfits"),
        (axes[1], modern, "What we see", "past the peak, error falls again"),
    ):
        ax.plot(x, train_l, color=MUTED, lw=1.6, ls=(0, (4, 3)), label="training error")
        ax.plot(x, test, color=NAVY if ax is axes[0] else WARM, lw=2.6, label="test error")
        ax.axvline(thr, color=RULE, lw=1.2, zorder=0)
        ax.set_xlim(0.05, 1.0); ax.set_ylim(0, 1.15)
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_ylabel("error  →", fontsize=10, color=MUTED, loc="top")
        ax.set_title(title, fontsize=12, weight="semibold", loc="left", color=INK, pad=18)
        ax.text(0, 1.015, sub, transform=ax.transAxes, fontsize=9.5, color=MUTED, va="bottom")
    axes[1].set_xlabel("model size  →", fontsize=10, color=MUTED, loc="right")
    axes[1].text(thr + 0.07, 0.98, "just big enough\nto memorize", fontsize=8.6, color=MUTED, va="top")
    axes[0].legend(loc="upper left", bbox_to_anchor=(0.2, 1.0), fontsize=9, handlelength=2.2)
    fig.text(0.0, 1.035, "A PUZZLE FOR THE OLD MATHEMATICS", fontsize=8.5, weight="semibold", color=NAVY)
    fig.text(0.0, 1.012, "Illustrative curves, not data", fontsize=9, color=MUTED)
    fig.tight_layout(h_pad=3.0)
    fig.savefig(OUT + "fig01.png", dpi=400); fig.savefig(OUT + "fig01.svg"); plt.close(fig)


# ---------- Figure 4: five gaps, one theme ----------
GAPS = [
    ("Error falls along\nsmooth power laws", "A thermodynamics\nof learning", "effective theory 2022,\nlearning mechanics 2026", NAVY),
    ("More concepts than\ndimensions", "A geometry\nof meaning", "superposition 2022,\nlinear representations 2024", NAVY),
    ("Skills that appear\nsuddenly", "Singularities and\nsudden change", "Watanabe 2009,\nlearning coefficient 2025", NAVY),
    ("Behaviour no one\nwrote line by line", "Guarantees for what\nwe did not design", "largely open", RED),
    ("Models trained on\nmodels' outputs", "Dynamics of\nlearners in a loop", "model collapse 2024,\nits remedies 2024", NAVY),
]


def fig_gaps():
    fig, ax = canvas(8.6, 8.0, 17.2, 16.0)
    heading(ax, 0.3, 15.75, "Five gaps, one theme", "Each puzzle points to a mathematics of the many")
    cols = [(0.3, 5.0, "WHAT WE SEE"), (6.0, 5.4, "MATHEMATICS IT MAY NEED"), (12.3, 4.9, "EARLY WORK")]
    for x, w, lab in cols:
        ax.text(x + 0.2, 14.0, lab, fontsize=7.4, weight="semibold", color=MUTED, va="bottom")
    for i, (seen, need, early, acc) in enumerate(GAPS):
        y = 11.7 - i * 2.75
        card(ax, 0.3, y, 5.0, 2.05, None, sub=seen, accent=MUTED, subfs=9.6)
        card(ax, 6.0, y, 5.4, 2.05, need, accent=acc, fs=10.4)
        ax.text(12.5, y + 1.02, early, fontsize=8.8, color=MUTED if acc != RED else RED, va="center",
                linespacing=1.3, style="italic" if acc == RED else "normal")
        arrow(ax, (5.4, y + 1.02), (5.9, y + 1.02), color=MUTED, lw=1.2, head=8)
        ax.plot([11.55, 12.25], [y + 1.02] * 2, color=RULE, lw=1.2, ls=(0, (2, 2)))
    fig.savefig(OUT + "fig03.png", dpi=400); fig.savefig(OUT + "fig03.svg"); plt.close(fig)


if __name__ == "__main__":
    fig_engine()
    fig_descent()
    fig_gaps()
