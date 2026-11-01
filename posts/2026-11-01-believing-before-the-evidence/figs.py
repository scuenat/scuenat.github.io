"""Figure for "Believing Before the Evidence". Same palette as the other posts.

Figure 1 is a schematic of my own: it shows a shape, not data.
It is written as SVG for the page and as a 400 dpi PNG for the share image.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BG, INK, MUTED, RULE = "#fbfaf7", "#1f2328", "#5f6b76", "#e6e2da"
NAVY, AMBER, WARM, GREEN, RED, PLUM = "#1d4f73", "#f5b041", "#b36b00", "#2e7d5b", "#a93226", "#7a3b69"
NAVY_T, AMBER_T = "#e5eef5", "#fdf1dc"
plt.rcParams.update({
    "font.family": "Inter", "font.size": 10, "text.color": INK,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.8,
    "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
    "savefig.bbox": "tight", "savefig.pad_inches": 0.35, "legend.frameon": False,
    "svg.fonttype": "none",
})


def save(fig, name):
    fig.savefig(f"figures/{name}.svg")
    fig.savefig(f"figures/{name}.png", dpi=400)
    plt.close(fig)


def fig01():
    """The dark period: evidence over time for an ordinary idea and a frame-breaking one."""
    t = np.linspace(0, 10, 400)
    dark_end = 7.0
    ordinary = 0.95 * (1 - np.exp(-t / 1.2))
    walk = np.cumsum(np.random.default_rng(3).normal(0, 0.02, t.size))
    walk = walk - walk[0] - 0.08 - 0.2 * np.sin(np.pi * t / dark_end)
    i_end = np.searchsorted(t, dark_end)
    after = walk[i_end] + 1.05 * (1 - np.exp(-(t - dark_end) / 0.6))
    frontier = np.where(t < dark_end, walk, after)
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.axvspan(0, dark_end, color=AMBER_T, zorder=0)
    ax.text(dark_end / 2, 1.2, "dark period: no decisive evidence yet", ha="center", color=WARM, fontsize=9.5)
    ax.axhline(0, color=RULE, lw=1, zorder=1)
    ax.axhline(-0.3, color=RED, lw=1.1, ls=(0, (4, 3)), zorder=2)
    ax.text(9.9, -0.36, "below this line,\nthe method moves on", ha="right", va="top", color=RED, fontsize=9)
    ax.plot(t, ordinary, color=NAVY, lw=2.2, zorder=3)
    ax.text(1.6, 1.0, "an idea the consensus expects", color=NAVY, fontsize=9.5)
    ax.plot(t, frontier, color=PLUM, lw=2.2, zorder=3)
    ax.text(7.15, -0.05, "an idea it does not:\nconviction carries it\nto the decisive test", color=PLUM, fontsize=9.5)
    ax.set_xlim(0, 10); ax.set_ylim(-0.6, 1.32)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_xlabel("time spent on the idea"); ax.set_ylabel("evidence for it")
    save(fig, "fig01")


if __name__ == "__main__":
    fig01()
