"""Figures for "Partly Wrong, Mostly Right". Same palette as the other essays.
Run: python figs.py
Written twice: a vector SVG (used in the page) and a 400 dpi PNG (card image).
Figure 1 is a schematic, my own. Figure 2 places reported results on a timeline; the dates and
descriptions come from the sources cited in the essay (several are company announcements)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import sys, pathlib  # hand-drawn house style: _figstyle/handdrawn.py at the site root
sys.path.insert(0, str(next(p / "_figstyle" for p in pathlib.Path(__file__).resolve().parents if (p / "_figstyle").is_dir())))
import handdrawn; handdrawn.apply()
from matplotlib.patches import FancyBboxPatch

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
    "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
    "savefig.dpi": 400, "savefig.bbox": "tight", "savefig.pad_inches": 0.35,
})
plt.rcParams["svg.fonttype"] = "path"


def _box(ax, x, y, w, h, fc, ec=LINE, r=0.18, lw=1.4):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw))


def _arrow(ax, x0, x1, y, color=MUTED):
    ax.annotate("", xy=(x1, y), xytext=(x0, y),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.6, mutation_scale=15))


def fig01():
    """The four steps of a discovery: the middle two moved to machines, the ends are still ours."""
    fig, ax = plt.subplots(figsize=(10.5, 4.2))
    ax.set_xlim(0, 10.5); ax.set_ylim(0, 4.3); ax.axis("off")
    ax.text(0.05, 4.05, "Where the frontier moved", fontsize=13.5, weight="bold", color=INK)

    steps = [
        ("1. Choose\nthe question", "Erdős, the Clay Institute,\na science writer's challenge", AMBER, GLOW),
        ("2. Find\na candidate", "a formula, a counterexample,\na nine-loop result", BLUE, BLUE_GLOW),
        ("3. Check it", "proof checkers and tests\nthat people built", BLUE, BLUE_GLOW),
        ("4. Say what\nit means", "is it the right physics?\ndoes it matter?\ndo we understand it?", AMBER, GLOW),
    ]
    w, gap, x0 = 2.3, 0.33, 0.05
    for i, (title, note, ec, fc) in enumerate(steps):
        x = x0 + i * (w + gap)
        _box(ax, x, 0.25, w, 2.75, fc, ec=ec)
        ax.text(x + w / 2, 2.25, title, ha="center", va="center", fontsize=12, weight="bold",
                color=INK, linespacing=1.15)
        ax.text(x + w / 2, 1.05, note, ha="center", va="center", fontsize=8.8, color=MUTED, linespacing=1.3)
        if i < 3:
            _arrow(ax, x + w + 0.04, x + w + gap - 0.04, 1.62)

    # brackets / labels above
    def bracket(xa, xb, text, color):
        y = 3.2
        ax.plot([xa, xa, xb, xb], [y - 0.08, y, y, y - 0.08], color=color, lw=1.6)
        ax.text((xa + xb) / 2, y + 0.12, text, ha="center", va="bottom", fontsize=9.5, weight="bold", color=color)

    xb1 = x0 + 1 * (w + gap)
    xb2 = x0 + 2 * (w + gap) + w
    bracket(xb1 + 0.1, xb2 - 0.1, "machines: much stronger since April", BLUE)
    bracket(x0 + 0.1, x0 + w - 0.1, "still ours", AMBER)
    xa4 = x0 + 3 * (w + gap)
    bracket(xa4 + 0.1, xa4 + w - 0.1, "still ours", AMBER)
    for ext in ("svg", "png"):
        fig.savefig(f"figures/fig01.{ext}")
    plt.close(fig)


def fig02():
    """Seven months on a timeline: physics above the line, mathematics below, the talk in grey."""
    fig, ax = plt.subplots(figsize=(10.5, 4.6))
    months = ["Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov"]
    xs = list(range(len(months)))
    ax.set_xlim(-1.7, 9.9); ax.set_ylim(-1.9, 2.75); ax.axis("off")
    ax.plot([-0.5, 9.5], [0, 0], color=LINE, lw=2.2, zorder=1)
    for x, m in zip(xs, months):
        ax.plot([x, x], [-0.07, 0.07], color=LINE, lw=1.4)
        ax.text(x, -0.27, m, ha="center", va="top", fontsize=9, color=MUTED)
    ax.text(-1.65, 2.62, "Seven months, as reported (2026)", fontsize=13, weight="bold", color=INK)
    ax.text(-1.65, 0.3, "physics", fontsize=9.5, weight="bold", color=BLUE)
    ax.text(-1.65, -0.42, "mathematics", fontsize=9.5, weight="bold", color=AMBER)

    events = [
        (0, 1.75, BLUE, "a gluon formula\nonce presumed zero,\nfirst proposed by a model"),
        (1.2, 0.45, BLUE, "exact formulas for\ngravitational waves\nfrom cosmic strings"),
        (2.2, 1.2, MUTED, "my TEDx talk,\nDelémont"),
        (3, -1.0, AMBER, "an Erdős conjecture\nfrom 1946 disproved"),
        (7, 1.25, BLUE, "a nine-loop amplitude\n(the human record\nwas eight loops)"),
        (8, -1.0, AMBER, "700+ papers released,\nincluding the\nquasi-Riemann hypothesis"),
        (9.05, 0.55, BLUE, "Yang–Mills exists:\nchecked in Lean,\nmass gap untouched"),
    ]
    for x, y, c, text in events:
        ax.plot([x, x], [0, y * 0.82], color=c, lw=1.2, zorder=2)
        ax.scatter([x], [0], s=70, color=c, ec=BG, lw=1.5, zorder=3)
        va = "bottom" if y > 0 else "top"
        ax.text(x, y * 0.85, text, ha="center", va=va, fontsize=8.5, color=INK if c != MUTED else MUTED,
                linespacing=1.25, weight="bold" if c == MUTED else "normal")
    for ext in ("svg", "png"):
        fig.savefig(f"figures/fig02.{ext}")
    plt.close(fig)


if __name__ == "__main__":
    fig01()
    fig02()
