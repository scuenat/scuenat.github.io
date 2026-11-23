"""Figure for "Twenty Watts". Same palette as the other essays.
Run: python figs.py   (needs matplotlib, numpy)
Written twice: a vector SVG (used in the page) and a 400 dpi PNG (card image).
Figure 1 is a schematic, my own: two ways to reach an answer, by trying almost
every path, or by seeing the few that matter. It shows a shape, not data."""
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


def _branch(ax, x0, y0, x1, y1, color, lw, alpha, bend):
    """A gently curved path from (x0, y0) to (x1, y1)."""
    t = np.linspace(0, 1, 30)
    xs = x0 + (x1 - x0) * t
    ys = y0 + (y1 - y0) * t + bend * np.sin(np.pi * t)
    ax.plot(xs, ys, color=color, lw=lw, alpha=alpha, solid_capstyle="round")


def fig01():
    """Two ways to find the answer: try almost every path, or see the few that matter."""
    fig, ax = plt.subplots(figsize=(10.5, 5.9))
    ax.set_xlim(0, 10.5); ax.set_ylim(0, 6.05); ax.axis("off")
    ax.text(0.05, 5.75, "Two ways to find the answer", fontsize=15.5, weight="bold")
    ax.text(0.05, 5.37, "A drawing of an idea, not a measurement.", fontsize=10.5, color=MUTED)

    w, h, yb = 5.05, 4.55, 0.2
    panels = [(0.05, BLUE, BLUE_GLOW), (5.4, AMBER, GLOW)]
    for x, ec, fc in panels:
        _box(ax, x, yb, w, h, fc, ec=ec)

    # --- left: search almost everything ---
    x = 0.05
    ax.text(x + 0.3, 4.38, "Try almost every path", fontsize=13.5, weight="bold", color=BLUE)
    sx, sy = x + 0.55, 2.55   # start
    gx, gy = x + 4.45, 2.55   # answer
    rng = np.random.default_rng(7)
    for i in range(46):
        ex = sx + rng.uniform(1.6, 3.6)
        ey = sy + rng.uniform(-1.45, 1.45)
        _branch(ax, sx, sy, ex, ey, BLUE, 0.9, 0.35, rng.uniform(-0.25, 0.25))
    _branch(ax, sx, sy, gx, gy, BLUE, 2.2, 1.0, 0.55)
    ax.plot([sx], [sy], "o", color=INK, ms=7)
    ax.plot([gx], [gy], "*", color=BLUE, ms=17)
    ax.text(sx, sy - 0.38, "question", ha="center", fontsize=10, color=MUTED)
    ax.text(gx, gy - 0.48, "answer", ha="center", fontsize=10, color=MUTED)
    ax.text(x + 0.3, 0.88, "Very fast, very many paths.", fontsize=11.3, color=INK)
    ax.text(x + 0.3, 0.48, "It needs a power station.", fontsize=11.3, color=MUTED)

    # --- right: see the few paths that matter ---
    x = 5.4
    ax.text(x + 0.3, 4.38, "See the few that matter", fontsize=13.5, weight="bold", color=AMBER)
    sx, sy = x + 0.55, 2.55
    gx, gy = x + 4.45, 2.55
    for ey, bend in [(3.55, 0.1), (1.7, -0.1)]:
        _branch(ax, sx, sy, sx + 1.9, ey, AMBER, 1.1, 0.45, bend)
    _branch(ax, sx, sy, gx, gy, AMBER, 2.4, 1.0, 0.35)
    ax.plot([sx], [sy], "o", color=INK, ms=7)
    ax.plot([gx], [gy], "*", color=AMBER, ms=17)
    ax.text(sx, sy - 0.38, "question", ha="center", fontsize=10, color=MUTED)
    ax.text(gx, gy - 0.48, "answer", ha="center", fontsize=10, color=MUTED)
    ax.text(x + 0.3, 0.88, "Slower, a handful of paths.", fontsize=11.3, color=INK)
    ax.text(x + 0.3, 0.48, "It runs on twenty watts.", fontsize=11.3, color=MUTED)
    _save(fig, 1)


if __name__ == "__main__":
    fig01()
