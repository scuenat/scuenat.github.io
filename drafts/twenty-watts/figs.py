"""Figure for "Twenty Watts". Same palette as the other essays.
Run: python figs.py   (needs matplotlib, numpy)
Written twice: a vector SVG (used in the page) and a 400 dpi PNG (card image).
Figure 1 is a schematic, my own: two ways to pay for a mind, in time (evolution,
then a childhood) or in stored time and power (a large model, trained on centuries
of human writing). It shows a shape, not data."""
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
        (0.05, AMBER, GLOW, "A human mind", [0.95, 0.07, 0.06],
         ["hundreds of millions of\nyears, then a childhood", "what one child\nsees and hears", "twenty watts"],
         "Nature paid in time."),
        (5.4, BLUE, BLUE_GLOW, "A large model", [0.07, 0.95, 0.95],
         ["a few years\nof training", "centuries of\nwriting, stored", "a power station"],
         "We pay in stored time and power."),
    ]
    rows = ["Time", "Data", "Power"]
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


if __name__ == "__main__":
    fig01()
