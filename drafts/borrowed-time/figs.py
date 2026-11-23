"""Figures for "Borrowed Time". Same palette as the other essays.
Run: python figs.py   (needs matplotlib, numpy)
Written twice: a vector SVG (used in the page) and a 400 dpi PNG (card image).
Figure 1 is a schematic, my own: two ways to pay for a mind, in time (evolution,
then a childhood) or in borrowed time and power (a large model, trained on what
people wrote). The word counts in its labels are from the essay's sources.
Figure 2 is a schematic of a textbook result (Curzon and Ahlborn, 1975): for a
heat engine, efficiency falls as it runs faster, and power output rises, peaks,
then falls. Here efficiency = 1 - s and power = s (1 - s), for a speed s from 0 to 1:
the shape, not the numbers, of an endoreversible engine."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import sys, pathlib  # hand-drawn house style: _figstyle/handdrawn.py at the site root
sys.path.insert(0, str(next(p / "_figstyle" for p in pathlib.Path(__file__).resolve().parents if (p / "_figstyle").is_dir())))
import handdrawn; handdrawn.apply()
from matplotlib.patches import FancyBboxPatch
import numpy as np

# ---------- palette (from light.scss) ----------
BG = "#ffffff"
INK = "#1f2328"
MUTED = "#5f6b76"
LINE = "#d0d7de"
AMBER = "#e0952b"
BLUE = "#3b6ea8"
GLOW = "#fff4e0"
BLUE_GLOW = "#eef3f9"

plt.rcParams.update({
    "font.family": "Inter", "font.size": 10, "text.color": INK,
    "axes.edgecolor": LINE, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
    "savefig.dpi": 400, "savefig.bbox": "tight", "savefig.pad_inches": 0.35,
})
plt.rcParams["svg.fonttype"] = "path"


def _box(ax, x, y, w, h, fc, ec=LINE, r=0.18, lw=1.4):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw))


def _save(fig, n):
    for ext in ("svg", "png"):
        fig.savefig(f"figures/fig{n:02d}.{ext}")
    plt.close(fig)


def fig01():
    """Two ways to pay for a mind: nature paid in time, we pay in data and power."""
    fig, ax = plt.subplots(figsize=(10.5, 5.9))
    ax.set_xlim(0, 10.5); ax.set_ylim(0, 6.05); ax.axis("off")
    ax.text(0.05, 5.75, "Two ways to pay for a mind", fontsize=15.5, weight="bold")
    ax.text(0.05, 5.37, "A drawing of an idea, not a measurement.", fontsize=10.5, color=MUTED)

    w, yb, h = 5.05, 0.2, 4.55
    panels = [
        (0.05, AMBER, GLOW, "A human mind", [0.95, 0.06, 0.06],
         ["hundreds of millions of\nyears, then a childhood", "under 100 million\nby age 13", "twenty watts,\nlearning for life"],
         "Nature paid in time."),
        (5.4, BLUE, BLUE_GLOW, "A large model", [0.07, 0.95, 0.95],
         ["months of\ntraining", "trillions, written\nover centuries", "a data centre"],
         "We pay in borrowed time and power."),
    ]
    rows = ["Time", "Words", "Power"]
    for x, ec, fc, head, vals, notes, verdict in panels:
        _box(ax, x, yb, w, h, fc, ec=ec)
        ax.text(x + 0.3, 4.38, head, fontsize=13.5, weight="bold", color=ec)
        bx, bw = x + 1.2, 1.75
        for i, (r, v, n) in enumerate(zip(rows, vals, notes)):
            y = 3.45 - i * 0.92
            ax.text(x + 0.3, y, r, fontsize=12, color=INK, va="center")
            ax.add_patch(FancyBboxPatch((bx, y - 0.17), bw, 0.34, boxstyle="round,pad=0,rounding_size=0.08",
                                        fc="none", ec=LINE, lw=1.1))
            ax.add_patch(FancyBboxPatch((bx, y - 0.17), max(bw * v, 0.1), 0.34,
                                        boxstyle="round,pad=0,rounding_size=0.08", fc=ec, ec=ec, lw=1.1))
            ax.text(bx + bw + 0.15, y, n, fontsize=9.8, color=MUTED, va="center", linespacing=1.15)
        ax.plot([x + 0.3, x + w - 0.3], [0.95, 0.95], color=LINE, lw=1)
        ax.text(x + 0.3, 0.55, verdict, fontsize=12.5, weight="bold", color=ec, va="center")
    _save(fig, 1)


def fig02():
    """Every speed has a price: efficiency falls with speed; output peaks, then falls."""
    fig, ax = plt.subplots(figsize=(9.6, 5.6))
    s = np.linspace(0, 1, 300)
    eff = 1 - s
    power = 4 * s * (1 - s)          # scaled so the peak is 1
    ax.plot(s, eff, color=BLUE, lw=2.4)
    ax.plot(s, power, color=AMBER, lw=2.8)
    ax.set_xlim(0, 1.02); ax.set_ylim(0, 1.24)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_xlabel("how fast we run it  \u2192", fontsize=12, color=INK, labelpad=8)
    ax.text(0.02, 1.02, "what we get from\neach unit of energy", color=BLUE, fontsize=11.5, va="bottom")
    ax.text(0.64, 1.04, "what we get per hour", color=AMBER, fontsize=11.5, va="center")
    ax.plot([0.5, 0.5], [0, 1], color=MUTED, lw=1, ls=(0, (3, 3)))
    ax.plot([0.5], [1], "o", color=AMBER, ms=8)
    ax.text(0.5, 1.09, "the right speed", ha="center", va="bottom", fontsize=11.5, color=INK, weight="bold")
    ax.text(0.075, 0.03, "too slow:\nlittle happens", fontsize=10.5, color=MUTED, ha="left", va="bottom")
    ax.text(0.995, 0.56, "too fast:\nwe get less,\nand waste more", fontsize=10.5, color=MUTED, ha="right", va="bottom")
    fig.suptitle("Every speed has a price", x=0.125, ha="left", fontsize=15.5, weight="bold", y=1.0)
    fig.text(0.125, 0.925, "A heat engine, after Curzon and Ahlborn (1975). Schematic: the shape, not the numbers.",
             fontsize=10.5, color=MUTED, ha="left")
    _save(fig, 2)


if __name__ == "__main__":
    fig01(); fig02()
