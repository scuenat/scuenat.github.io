"""Figure for "Not Because It Is Useful". Same style as "The Joy of the Question".
Run: python figs.py
Written twice: a vector SVG (used in the page) and a 400 dpi PNG (card image). A schematic, my own."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

# ---------- palette (from light.scss) ----------
BG = "#ffffff"
INK = "#1f2328"
MUTED = "#5f6b76"
RULE = "#e6e2da"
NAVY = "#1d4f73"
DEEP = "#0b1733"
AMBER = "#e0952b"
WARM = "#b36b00"
NAVY_T, AMBER_T = "#e5eef5", "#fdf1dc"

plt.rcParams.update({
    "font.family": "Inter", "font.size": 10, "text.color": INK,
    "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
    "savefig.dpi": 400, "savefig.bbox": "tight", "savefig.pad_inches": 0.18,
})
plt.rcParams["svg.fonttype"] = "path"     # text as outlines: the SVG looks the same everywhere
SERIF = "Inter"   # Source Serif is not always installed; Inter keeps the titles inside the cards


def card(ax, x, y, w, h, fill, edge):
    ax.add_patch(FancyBboxPatch((x + 0.05, y - 0.08), w, h, boxstyle="round,pad=0,rounding_size=0.28",
                                fc=DEEP, ec="none", alpha=0.05, zorder=1))
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.28",
                                fc=fill, ec=edge, lw=1.0, zorder=2))


def fig01():
    """Three parts of science, and how far the machine reaches into each."""
    fig, ax = plt.subplots(figsize=(10, 5.6))
    ax.set_xlim(0, 15); ax.set_ylim(0, 8.4); ax.set_aspect("equal"); ax.axis("off")

    cols = [
        # x, kicker, title, lines, who, reach (0..1), reach text
        (0.3, "WHY WE LOOK", "Wonder", "beauty, the wish to grasp\nwhy it must be so", "Poincaré · Plato",
         0.0, "Cannot be delegated:\nthe grasp happens in you"),
        (5.3, "HOW WE FIND", "Seeing the whole", "a new pattern that makes\nthe parts fit", "McGilchrist · Kuhn",
         0.5, "Proposes ideas,\nby plausibility"),
        (10.3, "HOW WE CHECK", "The method", "hypotheses, tests, rules\nthat keep us honest", "Reichenbach",
         1.0, "Follows it,\noften better than we do"),
    ]
    w = 4.4
    for x, kick, title, lines, who, reach, rtext in cols:
        human = reach == 0.0
        card(ax, x, 3.2, w, 4.6, AMBER_T if human else "white", AMBER if human else RULE)
        ax.text(x + 0.35, 7.25, kick, fontsize=8.2, weight="bold", color=WARM if human else MUTED, va="center")
        ax.text(x + 0.35, 6.45, title, fontsize=14, weight="bold", color=INK, va="center", family=SERIF)
        ax.text(x + 0.35, 5.35, lines, fontsize=9.6, color=INK, va="center", linespacing=1.35)
        ax.text(x + 0.35, 4.05, who, fontsize=8.6, color=MUTED, va="center", style="italic")

        # what AI covers: a bar, full / half / empty
        ax.text(x, 2.55, "WHAT AI DOES HERE", fontsize=7.6, weight="bold", color=MUTED, va="center")
        ax.add_patch(FancyBboxPatch((x, 1.75), w, 0.42, boxstyle="round,pad=0,rounding_size=0.21",
                                    fc="#f1f1f0", ec=RULE, lw=0.8, zorder=2))
        if reach > 0:
            ax.add_patch(FancyBboxPatch((x, 1.75), w * reach, 0.42, boxstyle="round,pad=0,rounding_size=0.21",
                                        fc=NAVY, ec="none", zorder=3))
        ax.text(x, 1.0, rtext, fontsize=9.2, color=NAVY if reach else WARM, va="center", linespacing=1.3,
                weight="bold" if not reach else "normal")

    # the arrow of a discovery, from why to check
    for x0 in (4.75, 9.75):
        ax.annotate("", xy=(x0 + 0.5, 5.5), xytext=(x0 + 0.02, 5.5),
                    arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.1, mutation_scale=12))

    ax.text(7.5, 0.15, "The method is the part of science that can be written down, so it is the part a machine can carry.",
            ha="center", va="center", fontsize=9.4, color=INK, family=SERIF, style="italic")
    for ext in ("svg", "png"):
        fig.savefig(f"figures/fig01.{ext}")
    plt.close(fig)


if __name__ == "__main__":
    import os
    os.makedirs("figures", exist_ok=True)
    fig01()
