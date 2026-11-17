"""Figures for "Two Cores and an Idea". Same palette as the other essays.
Run: python figs.py
Written twice: a vector SVG (used in the page) and a 400 dpi PNG (card image).
Figure 1 is a schematic, my own. Figure 2 plots the numbers of my preliminary experiment
(2 seeds, 2 CPU cores; results/prelim_ablation_summary.md in the experiment's repository)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ---------- palette (from light.scss) ----------
BG = "#ffffff"
INK = "#1f2328"
MUTED = "#5f6b76"
LINE = "#d0d7de"
AMBER = "#e0952b"
BLUE = "#3b6ea8"
GLOW = "#fff4e0"

plt.rcParams.update({
    "font.family": "Inter", "font.size": 10, "text.color": INK,
    "axes.edgecolor": LINE, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
    "savefig.dpi": 400, "savefig.bbox": "tight", "savefig.pad_inches": 0.3,
})
plt.rcParams["svg.fonttype"] = "path"


def fig01():
    """The picture behind the experiment: facts dig wells, the question is a ball, it rolls hop by hop."""
    fig, ax = plt.subplots(figsize=(10, 4.4))
    x = np.linspace(-0.6, 9.6, 1200)
    wells = [(1.0, 1.0), (3.6, 1.0), (6.2, 1.0), (8.6, 1.0)]  # (position, depth)
    y = 1.6 + 0.05 * (x - 4.5) ** 2 * 0.25
    for c, d in wells:
        y -= d * np.exp(-((x - c) ** 2) / (2 * 0.42 ** 2))
    ax.fill_between(x, y, -0.15, color=GLOW, zorder=1)
    ax.plot(x, y, color=INK, lw=2.0, zorder=2)

    labels = ["A", "B", "C", "D"]
    for (c, d), lab in zip(wells, labels):
        yb = np.interp(c, x, y)
        ax.text(c, yb - 0.32, lab, ha="center", fontsize=13, weight="bold", color=MUTED, zorder=3)

    # the ball, starting in A
    ya = np.interp(1.0, x, y)
    ax.scatter([1.0], [ya + 0.17], s=260, color=AMBER, ec=INK, lw=1.0, zorder=5)
    ax.text(1.0, ya + 0.55, "the question\nstarts here", ha="center", fontsize=9, color=INK, linespacing=1.2)

    # hops
    for a, b in ((1.0, 3.6), (3.6, 6.2), (6.2, 8.6)):
        ax.annotate("", xy=(b - 0.15, np.interp(b, x, y) + 0.32), xytext=(a + 0.15, np.interp(a, x, y) + 0.32),
                    arrowprops=dict(arrowstyle="-|>", color=AMBER, lw=1.6, mutation_scale=13,
                                    connectionstyle="arc3,rad=-0.45", linestyle=(0, (4, 3))), zorder=4)
    for i, (a, b) in enumerate(((1.0, 3.6), (3.6, 6.2), (6.2, 8.6))):
        ax.text((a + b) / 2, 1.85, f"hop {i + 1}", ha="center", fontsize=9, color=AMBER, weight="bold")
    yd = np.interp(8.6, x, y)
    ax.text(8.6, yd + 0.55, "it settles:\nthe answer", ha="center", fontsize=9, color=INK, linespacing=1.2)

    ax.text(-0.5, 2.55, "Each fact in the text digs a well. The question is a ball. Let it roll until it rests.",
            fontsize=10.5, color=INK, weight="bold")
    ax.text(-0.5, -0.4, "Schematic, my own: the landscape is rebuilt for every new text, so the same network follows chains it has never seen.",
            fontsize=8.4, color=MUTED, style="italic")
    ax.set_xlim(-0.7, 9.7); ax.set_ylim(-0.5, 2.75); ax.axis("off")
    for ext in ("svg", "png"):
        fig.savefig(f"figures/fig01.{ext}")
    plt.close(fig)


def fig02():
    """Accuracy by number of hops: independent wells against competing wells (preliminary)."""
    hops = [1, 2, 3, 4, 5]
    sig = [99.9, 98.8, 94.0, 80.8, 57.8]
    soft = [99.3, 99.0, 93.4, 31.9, 2.9]
    fig, ax = plt.subplots(figsize=(8, 4.4))
    ax.axvspan(0.5, 3.5, color="#f3f5f7", zorder=0)
    ax.text(2.0, 8, "trained on\n1 to 3 hops", ha="center", fontsize=9, color=MUTED, linespacing=1.2)
    ax.text(4.5, 97, "never seen\nin training", ha="center", fontsize=9, color=MUTED, linespacing=1.2)
    ax.plot(hops, sig, "-o", color=AMBER, lw=2.4, ms=7, zorder=3)
    ax.plot(hops, soft, "-o", color=BLUE, lw=2.4, ms=7, zorder=3)
    for h, v in zip(hops[3:], sig[3:]):
        ax.text(h + 0.08, v + 3, f"{v:.0f}%", color=AMBER, fontsize=9, weight="bold")
    for h, v in zip(hops[3:], soft[3:]):
        ax.text(h + 0.08, v + 3, f"{v:.0f}%", color=BLUE, fontsize=9, weight="bold")
    ax.text(5.35, 66, "independent wells", color=AMBER, va="center", fontsize=10, weight="bold")
    ax.text(5.35, 11, "competing wells", color=BLUE, va="center", fontsize=10, weight="bold")
    ax.set_xlim(0.5, 6.6); ax.set_ylim(-2, 106)
    ax.set_xticks(hops); ax.set_xlabel("number of hops in the chain")
    ax.set_ylabel("correct answers (%)")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.set_title("Same network, one change: do the wells compete?", loc="left", fontsize=11, weight="bold")
    for ext in ("svg", "png"):
        fig.savefig(f"figures/fig02.{ext}")
    plt.close(fig)


if __name__ == "__main__":
    fig01()
    fig02()
