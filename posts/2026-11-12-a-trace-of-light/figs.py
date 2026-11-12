"""Figure for "A Trace of Light". Same palette as the other essays.
Run: python figs.py
Written twice: a vector SVG (used in the page) and a 400 dpi PNG (card image). A schematic, my own."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
import numpy as np

# ---------- palette (from light.scss) ----------
BG = "#ffffff"
INK = "#1f2328"
MUTED = "#5f6b76"
NIGHT = "#0b1733"
STAR = "#c9d3e6"
AMBER = "#e0952b"
GLOW = "#ffd27a"

plt.rcParams.update({
    "font.family": "Inter", "font.size": 10, "text.color": INK,
    "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
    "savefig.dpi": 400, "savefig.bbox": "tight", "savefig.pad_inches": 0.35,
})
plt.rcParams["svg.fonttype"] = "path"


def fig01():
    """The solar system's story, from dust to dust, and the trace we are in it."""
    fig, ax = plt.subplots(figsize=(10, 4.6))
    ax.set_xlim(-5.4, 8.4); ax.set_ylim(-2.3, 3.2); ax.axis("off")

    # the night: a dark band, the whole story of the solar system
    ax.add_patch(FancyBboxPatch((-5.2, -0.6), 13.4, 3.6, boxstyle="round,pad=0,rounding_size=0.3",
                                fc=NIGHT, ec="none", zorder=1))
    rng = np.random.default_rng(7)
    xs = rng.uniform(-5.0, 8.0, 160); ys = rng.uniform(-0.45, 2.85, 160)
    ax.scatter(xs, ys, s=rng.uniform(0.3, 3.0, 160), color=STAR, alpha=0.55, lw=0, zorder=2)

    # dust clouds at both ends
    for cx in (-4.3, 7.0):
        px = np.clip(rng.normal(cx, 0.38, 500), -5.0, 8.0); py = np.clip(rng.normal(1.2, 0.55, 500), -0.45, 2.85)
        ax.scatter(px, py, s=1.2, color=STAR, alpha=0.35, lw=0, zorder=2)
    ax.text(-4.3, 2.55, "Dust", color="white", ha="center", fontsize=12, weight="bold", zorder=4)
    ax.text(-4.3, -0.25, "a cloud of gas\nand dust", color=STAR, ha="center", fontsize=8.4, zorder=4, linespacing=1.2)
    ax.text(7.0, 2.55, "Dust again", color="white", ha="center", fontsize=12, weight="bold", zorder=4)
    ax.text(7.0, -0.25, "the Sun's outer layers\nblown back to space", color=STAR, ha="center", fontsize=8.4, zorder=4, linespacing=1.2)

    # the Sun and planets in between, very faint
    ax.plot([-3.4, 6.4], [1.2, 1.2], color=STAR, lw=0.8, alpha=0.5, zorder=3)

    # the trace: us, drawn far wider than its true size
    for w, a in ((0.34, 0.10), (0.20, 0.18), (0.10, 0.35)):
        ax.add_patch(Rectangle((-w / 2, -0.6), w, 3.6, fc=GLOW, ec="none", alpha=a, zorder=4))
    ax.plot([0, 0], [-0.6, 3.0], color="white", lw=1.6, zorder=5)
    ax.text(0.28, 2.55, "Us", color=GLOW, fontsize=12, weight="bold", zorder=6)
    ax.text(0.28, 2.15, "a trace of light", color=GLOW, fontsize=9.2, style="italic", zorder=6)

    # the time axis, under the night
    ax.annotate("", xy=(8.2, -1.05), xytext=(-5.2, -1.05),
                arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.0, mutation_scale=11))
    ticks = [(-4.6, "4.6 billion\nyears ago"), (0, "now"), (5.0, "in about 5 billion years:\nthe Sun starts to swell")]
    for x, lab in ticks:
        ax.plot([x, x], [-0.98, -1.12], color=MUTED, lw=1.0)
        ax.text(x, -1.3, lab, ha="center", va="top", fontsize=8.4, color=INK if x == 0 else MUTED,
                weight="bold" if x == 0 else "normal", linespacing=1.2)

    ax.text(1.5, -2.25, "At true scale, all of human history (about 300,000 years) would be far thinner than a hair on this page.",
            ha="center", va="center", fontsize=8.6, color=MUTED, style="italic")
    for ext in ("svg", "png"):
        fig.savefig(f"figures/fig01.{ext}")
    plt.close(fig)


if __name__ == "__main__":
    fig01()
