"""Figures for "The Teacher Who Writes the Weights".

Same style as "The Mathematics Still to Come": Inter type, white cards with a faint shadow
and a coloured accent, colours taken from the site's palette.

Figure 1 is a schematic map of work from 2023 to 2026 that reads or writes neural network
weights; the placement is my own reading, the works are cited in the text.
Figure 2 plots the numbers of Experiment 8 of Takehi et al. (2026), copied from their table.
Figure 3 is a schematic of the incubator I propose; it shows no data.
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



# ---------- Figure 1: who reads and writes weights, 2023-2026 ----------
# (column, row, label, year)  columns: 0 tools built for the job, 1 models trained for it,
# 2 a general model used as it is.  rows: 1 read, 0 write.
WORKS = [
    (0, 1, "Circuits, induction heads", "2021-23"), (0, 1, "Sparse autoencoders", "2023"),
    (0, 1, "Circuit tracing", "2025"),
    (1, 1, "Weight-space networks", "2023-24"), (1, 1, "Neuron explanations", "2023"),
    (1, 1, "Weight-diff interpreters", "2025"), (1, 1, "Activation, weight oracles", "2025-26"),
    (0, 0, "Task arithmetic, merging", "2023-24"), (0, 0, "Compiled programs (Tracr)", "2023"),
    (0, 0, "Direction ablation", "2024"), (0, 0, "Gradient-free (ES, MeZO)", "2023-25"),
    (1, 0, "Checkpoint diffusion", "2022-24"), (1, 0, "HyperTuning", "2023"),
    (1, 0, "Text-to-LoRA, DnD", "2025"), (1, 0, "Self-edits (SEAL)", "2025"),
]


def fig_map():
    fig, ax = canvas(9.0, 6.4, 18.0, 12.8)
    heading(ax, 0.3, 12.55, "Reading and writing weights, 2023-2026",
            "Until this year, the reader or the writer was built or trained for the job")
    cx = [3.0, 9.0, 15.0]; cw = 5.6
    heads = ["TOOLS BUILT\nFOR THE JOB", "MODELS TRAINED\nFOR THE JOB", "A GENERAL MODEL,\nUSED AS IT IS"]
    for x, h in zip(cx, heads):
        ax.text(x, 10.9, h, ha="center", va="center", fontsize=7.4, weight="semibold",
                color=MUTED, linespacing=1.25)
    rows = {1: (5.6, "READ"), 0: (0.6, "WRITE")}
    for r, (y0, lab) in rows.items():
        ax.text(0.05, y0 + 2.2, lab, rotation=90, ha="left", va="center", fontsize=7.4,
                weight="semibold", color=MUTED)
        for c in range(3):
            fill = AMBER_T if c == 2 else "white"
            ax.add_patch(FancyBboxPatch((cx[c] - cw / 2, y0), cw, 4.5,
                                        boxstyle="round,pad=0,rounding_size=0.3",
                                        fc=fill, ec=RULE, lw=0.9, zorder=1))
    for c, r in [(0, 1), (1, 1), (0, 0), (1, 0)]:
        items = [w for w in WORKS if w[0] == c and w[1] == r]
        y0 = rows[r][0]
        for i, (_, _, lab, yr) in enumerate(items):
            y = y0 + 3.75 - i * 1.0
            ax.text(cx[c] - cw / 2 + 0.35, y, lab, fontsize=8.4, color=INK, va="center", zorder=3)
            ax.text(cx[c] + cw / 2 - 0.3, y, yr, fontsize=7.2, color=MUTED, va="center",
                    ha="right", fontfamily=MONO, zorder=3)
    for r, txt in [(1, "Which game, which shape,\nwhich language, which heads"),
                   (0, "Fix a policy, write Go\nand MinAtar players, edit\n0.016% of a 0.8B model")]:
        y0 = rows[r][0]
        ax.text(cx[2], y0 + 3.55, "Weight-space programming", ha="center", fontsize=9.2,
                weight="semibold", color=WARM, zorder=3)
        ax.text(cx[2], y0 + 2.75, "Takehi et al., Nov 2026", ha="center", fontsize=7.4,
                color=MUTED, fontfamily=MONO, zorder=3)
        ax.text(cx[2], y0 + 1.35, txt, ha="center", va="center", fontsize=8.2, color=INK,
                linespacing=1.3, zorder=3)
    fig.savefig(OUT + "fig01.png", dpi=400); fig.savefig(OUT + "fig01.svg"); plt.close(fig)


# ---------- Figure 2: Experiment 8, from the source's table ----------
BUDGETS = ["Base", "10", "25", "50"]
EXP8 = {  # Takehi et al. (2026), Experiment 8 table, Qwen3.5-0.8B
    "MATH-500": [7.9, 12.3, 14.1, 48.1],
    "GSM8K": [13.8, 25.7, 25.1, 67.1],
    "IFEval": [21.0, 49.0, 39.9, 62.3],
    "Answers that hit the token limit": [93.0, 87.2, 86.4, 33.1],
}


def fig_exp8():
    fig, axes = plt.subplots(1, 4, figsize=(9.6, 3.3), sharey=True)
    for k, (ax, (name, vals)) in enumerate(zip(axes, EXP8.items())):
        col = WARM if k == 3 else NAVY
        xs = np.arange(4)
        ax.bar(xs, vals, width=0.62, color=[MUTED] + [col] * 3, edgecolor=BG, linewidth=2)
        for x, v in zip(xs, vals):
            ax.text(x, v + 2.0, f"{v:.1f}", ha="center", va="bottom", fontsize=7.6, color=INK)
        ax.set_xticks(xs, BUDGETS, fontsize=7.8)
        ax.set_title(name, fontsize=9.0, weight="semibold", loc="left", color=INK, wrap=True)
        ax.set_ylim(0, 105)
        ax.grid(axis="y", color=RULE, lw=0.6); ax.set_axisbelow(True)
        ax.tick_params(axis="y", labelsize=7.6, length=0)
        ax.tick_params(axis="x", length=0)
        ax.spines["left"].set_visible(False)
    axes[0].set_ylabel("%", fontsize=8.4)
    fig.supxlabel("Forward passes Astra was allowed (Base: the unedited model)", fontsize=8.2,
                  color=MUTED, y=-0.02)
    fig.suptitle("Qwen3.5-0.8B after one weight edit, by forward-pass budget", x=0.06, ha="left",
                 fontsize=11.0, weight="semibold", y=1.04)
    axes[3].set_title("Hit the token limit\n(MATH-500, lower is better)", fontsize=9.0,
                      weight="semibold", loc="left", color=INK)
    fig.tight_layout(w_pad=1.6)
    fig.savefig(OUT + "fig02.png", dpi=400); fig.savefig(OUT + "fig02.svg"); plt.close(fig)


# ---------- Figure 3: the incubator ----------
STAGES = [  # (title, sub, accent)
    ("1  Conceive", "the mentor writes\na first network\nfrom a spec", AMBER),
    ("2  Grow", "ordinary training\nfrom that start,\non real data", NAVY),
    ("3  Examine", "the mentor reads\nweights and probes:\nloops, shortcuts", GREEN),
    ("4  Operate", "a small, stated\nedit, kept only if\nheld-out tests agree", RED),
    ("5  Release", "an audit note and\nthe weight diff,\nreviewed like code", MUTED),
]


def fig_incubator():
    fig, ax = canvas(10.2, 4.2, 20.4, 8.4)
    heading(ax, 0.3, 8.15, "An incubator for small networks",
            "A large model that reads and writes weights, around an ordinary training loop on premise")
    w, h, gap = 3.6, 3.0, 0.4
    xs = [0.3 + i * (w + gap) for i in range(5)]
    y = 3.2
    for x, (t, s, a) in zip(xs, STAGES):
        card(ax, x, y, w, h, t, sub=s, accent=a, fs=10.0, subfs=7.8)
    where = [("spec only", AMBER_T, WARM), ("on premise", GREEN_T, GREEN),
             ("local or remote", SAND_T, MUTED), ("local or remote", SAND_T, MUTED),
             ("on premise", GREEN_T, GREEN)]
    for x, (lab, fill, col) in zip(xs, where):
        chip(ax, x + w / 2, y + h + 0.45, lab, color=col, fill=fill, fs=7.4)
    for i in range(4):
        arrow(ax, (xs[i] + w + 0.06, y + h / 2), (xs[i + 1] - 0.08, y + h / 2), lw=1.3, head=8)
    # loop back from Operate to Grow
    arrow(ax, (xs[3] + w / 2, y - 0.12), (xs[1] + w / 2, y - 0.12), rad=-0.32, color=NAVY,
          lw=1.3, ls=(0, (3, 2)), head=8)
    ax.text((xs[1] + xs[3]) / 2 + w / 2, 1.05, "repeat while each edit pays for itself",
            ha="center", fontsize=8.0, color=NAVY, style="italic")
    pill(ax, 10.1, 0.35, "budget: forward passes and mentor tokens, counted against plain training; at most the spec leaves",
         fs=7.6)
    fig.savefig(OUT + "fig03.png", dpi=400); fig.savefig(OUT + "fig03.svg"); plt.close(fig)


if __name__ == "__main__":
    fig_map()
    fig_exp8()
    fig_incubator()
