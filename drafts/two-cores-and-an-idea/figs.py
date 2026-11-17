"""Figures for "Two Cores and an Idea". Same palette as the other essays.
Run: python figs.py
Written twice: a vector SVG (used in the page) and a 400 dpi PNG (card image).
Figures 1, 3 and 4 are schematics, my own. Figure 2 draws the Gödel notebook numbers as reported
in the press (rounded; see the essay's references). Figures 5 and 6 plot the numbers of my own
experiment: figure 5 from results/v2/results_stability.json (3 seeds, mean), figure 6 from
results/prelim_ablation_summary.md (2 seeds, preliminary), in the experiment's repository."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, Rectangle

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
    "savefig.dpi": 400, "savefig.bbox": "tight", "savefig.pad_inches": 0.35,
})
plt.rcParams["svg.fonttype"] = "path"


def fig03():
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
        fig.savefig(f"figures/fig03.{ext}")
    plt.close(fig)


def fig06():
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
        fig.savefig(f"figures/fig06.{ext}")
    plt.close(fig)


def _box(ax, x, y, w, h, fc, ec=LINE, r=0.18, lw=1.2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw))


def _arrow(ax, x0, x1, y, color=MUTED):
    ax.annotate("", xy=(x1, y), xytext=(x0, y),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.6, mutation_scale=15))


def fig01():
    """The order the essay defends: an idea, a small test, then (only if it survives) a big machine."""
    fig, ax = plt.subplots(figsize=(10, 4.3))
    ax.set_xlim(0, 10); ax.set_ylim(-0.3, 4.3); ax.axis("off")
    ax.text(0.1, 4.05, "The order I believe in", fontsize=13, weight="bold", color=INK)

    # 1. a notebook and a pencil
    _box(ax, 0.1, 0.2, 2.9, 3.4, GLOW, ec=AMBER)
    _box(ax, 0.75, 1.75, 1.5, 1.45, BG, ec=INK, r=0.05)
    for yy in np.linspace(1.95, 2.95, 6):
        ax.plot([0.9, 2.1], [yy, yy], color=LINE, lw=0.9)
    ax.plot([0.9, 1.6], [2.55, 2.35], color=INK, lw=1.0)
    ax.plot([1.6, 2.0], [2.35, 2.75], color=INK, lw=1.0)
    ax.plot([2.35, 2.75], [1.85, 3.15], color=AMBER, lw=5, solid_capstyle="butt")
    ax.plot([2.33, 2.35], [1.78, 1.85], color=INK, lw=2)
    ax.text(1.55, 1.3, "1. The idea", ha="center", fontsize=11.5, weight="bold", color=INK)
    ax.text(1.55, 0.55, "a mind, a pencil,\nalmost nothing", ha="center", fontsize=9, color=MUTED, linespacing=1.25)

    _arrow(ax, 3.1, 3.5, 2.25)

    # 2. two cores
    _box(ax, 3.55, 0.2, 2.9, 3.4, "#eef3f9", ec=BLUE)
    _box(ax, 4.25, 1.75, 1.5, 1.45, BG, ec=INK, r=0.06)
    for cx in (4.7, 5.3):
        _box(ax, cx - 0.22, 2.25, 0.44, 0.44, BLUE, ec=BLUE, r=0.04)
        for k in np.linspace(-0.15, 0.15, 3):
            ax.plot([cx + k, cx + k], [2.69, 2.8], color=BLUE, lw=1)
            ax.plot([cx + k, cx + k], [2.14, 2.25], color=BLUE, lw=1)
    ax.text(5.0, 1.92, "two cores", ha="center", fontsize=8.4, color=MUTED)
    ax.text(5.0, 1.3, "2. A small test", ha="center", fontsize=11.5, weight="bold", color=INK)
    ax.text(5.0, 0.55, "one that could prove me wrong,\nin minutes", ha="center", fontsize=9, color=MUTED, linespacing=1.25)

    _arrow(ax, 6.55, 6.95, 2.25)

    # 3. a data centre
    _box(ax, 7.0, 0.2, 2.9, 3.4, "#f3f5f7", ec=MUTED)
    for rx in (7.55, 8.2, 8.85):
        _box(ax, rx, 1.75, 0.5, 1.45, "#d5dbe1", ec=MUTED, r=0.03)
        for yy in np.linspace(1.9, 3.0, 7):
            ax.plot([rx + 0.07, rx + 0.43], [yy, yy], color=MUTED, lw=0.8)
            ax.scatter([rx + 0.38], [yy + 0.03], s=2, color=AMBER, zorder=3)
    ax.text(8.45, 1.3, "3. A big machine", ha="center", fontsize=11.5, weight="bold", color=INK)
    ax.text(8.45, 0.55, "only if it survives:\nto check it and scale it", ha="center", fontsize=9, color=MUTED, linespacing=1.25)
    ax.text(0.1, -0.2, "Schematic, my own.", fontsize=8.2, color=MUTED, style="italic")
    for ext in ("svg", "png"):
        fig.savefig(f"figures/fig01.{ext}")
    plt.close(fig)


def fig02():
    """Gödel's notebooks: who did what, with the numbers as reported (rounded)."""
    fig, ax = plt.subplots(figsize=(10, 4.6))
    ax.set_xlim(0, 10); ax.set_ylim(0, 4.6); ax.axis("off")
    ax.text(0.1, 4.35, "Gödel's notebooks: who did what", fontsize=13, weight="bold", color=INK)
    steps = [
        ("Gödel", "early 1940s", "16 notebooks,\nabout 1,009 pages,\nin old shorthand", AMBER, GLOW, "a mind and\na pencil"),
        ("Jan von Plato", "since 2017", "learns the shorthand,\ntranscribes the pages,\nwrites six books", AMBER, GLOW, "a mind,\nby hand, for years"),
        ("The AI", "September 2026", "reads it all, explains it,\nlists 663 results", BLUE, "#eef3f9", "a machine,\nfor the volume"),
    ]
    for i, (who, when, what, ec, fc, tag) in enumerate(steps):
        x = 0.1 + i * 3.35
        _box(ax, x, 1.55, 2.9, 2.35, fc, ec=ec)
        ax.text(x + 0.2, 3.5, who, fontsize=11.5, weight="bold", color=INK)
        ax.text(x + 0.2, 3.15, when, fontsize=8.6, color=MUTED)
        ax.text(x + 0.2, 2.25, what, fontsize=9.2, color=INK, linespacing=1.3, va="center")
        ax.text(x + 1.45, 1.15, tag, ha="center", fontsize=8.6, color=ec, weight="bold", linespacing=1.15, va="center")
        if i < 2:
            _arrow(ax, x + 2.95, x + 3.3, 2.7)

    # what the checking found, as a stacked bar (rounded numbers as reported)
    y0, h = 0.1, 0.42
    parts = [(400, "about 400 held", "#7fae7a"), (200, "about 200 repaired", "#e8b765"), (50, "", "#c96f5d")]
    total = 650.0
    x = 3.0
    ax.text(2.85, y0 + h / 2, "checked by a\nproof program:", ha="right", va="center", fontsize=8.6, color=MUTED, linespacing=1.15)
    for n, lab, c in parts:
        w = 5.6 * n / total
        ax.add_patch(Rectangle((x, y0), w, h, fc=c, ec=BG, lw=1.5))
        ax.text(x + w / 2, y0 + h / 2, lab, ha="center", va="center", fontsize=8.2 if n > 100 else 7.0,
                color=INK if n > 100 else BG, weight="bold")
        x += w
    ax.text(x + 0.1, y0 + h / 2, "about 50 wrong", va="center", fontsize=8.2, color="#c96f5d", weight="bold")
    for ext in ("svg", "png"):
        fig.savefig(f"figures/fig02.{ext}")
    plt.close(fig)


def fig04():
    """How small is small: the number of values a network learns, on a log scale."""
    fig, ax = plt.subplots(figsize=(10, 3.4))
    ax.set_xscale("log"); ax.set_xlim(1e3, 3e12); ax.set_ylim(0, 3)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.set_yticks([])
    ax.set_xticks([1e3, 1e6, 1e9, 1e12])
    ax.set_xticklabels(["a thousand", "a million", "a billion", "a thousand billion"])
    ax.set_xlabel("numbers the network has to learn (each tick is a thousand times more)", color=MUTED)
    ax.axvspan(5e4, 9e4, ymin=0.55, ymax=0.85, color=AMBER, alpha=0.9)
    ax.text(5e4, 2.7, "my networks: 50,000 to 90,000", fontsize=10, weight="bold", color=AMBER, ha="left")
    ax.axvspan(1e11, 1e12, ymin=0.1, ymax=0.4, color=BLUE, alpha=0.85)
    ax.text(9e10, 0.75, "large language models:\nhundreds of billions", fontsize=10, weight="bold", color=BLUE, ha="right", va="center", linespacing=1.2)
    ax.text(3e7, 2.0, "a million times more, and more", fontsize=9.2, color=MUTED, style="italic", ha="center")
    ax.set_title("How small is small", loc="left", fontsize=12, weight="bold")
    for ext in ("svg", "png"):
        fig.savefig(f"figures/fig04.{ext}")
    plt.close(fig)


def fig05():
    """The answer passes by: accuracy as the ball keeps rolling, with and without the question kept inside."""
    mult = [1, 2, 4, 16]
    start_only = [100.0, 65.7, 25.4, 20.2]      # 'gated', 3 seeds, mean (results_stability.json)
    kept_inside = [99.9, 99.9, 99.98, 99.9]     # 'gatedQ-persist', 3 seeds, mean
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.set_xscale("log", base=2)
    ax.plot(mult, kept_inside, "-o", color=AMBER, lw=2.4, ms=7)
    ax.plot(mult, start_only, "-o", color=BLUE, lw=2.4, ms=7)
    ax.text(16, 92, "question kept inside:\nthe ball stays", color=AMBER, fontsize=10, weight="bold", ha="right", va="top", linespacing=1.15)
    ax.text(16, 28, "question only at the start:\nit rolls past the answer", color=BLUE, fontsize=10, weight="bold", ha="right", va="bottom", linespacing=1.15)
    ax.set_xticks(mult); ax.set_xticklabels(["as trained", "2 times\nlonger", "4 times\nlonger", "16 times\nlonger"])
    ax.minorticks_off()
    ax.set_ylim(0, 106); ax.set_xlim(0.85, 19)
    ax.set_ylabel("correct answers (%)")
    ax.set_xlabel("how long the ball keeps rolling", color=MUTED)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.set_title("Let the ball keep rolling: does the answer stay?", loc="left", fontsize=11, weight="bold")
    for ext in ("svg", "png"):
        fig.savefig(f"figures/fig05.{ext}")
    plt.close(fig)


if __name__ == "__main__":
    for f in (fig01, fig02, fig03, fig04, fig05, fig06):
        f()
