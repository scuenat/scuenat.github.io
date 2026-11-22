"""Figures for "The Disposable Screen". Same palette as the other essays.
Run: python figs.py   (needs matplotlib)
Written twice: a vector SVG (used in the page) and a 400 dpi PNG (card image).
Both figures are schematics, my own: they show a shape, not data."""
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
SOFT = "#f6f8fa"

plt.rcParams.update({
    "font.family": "Inter", "font.size": 10, "text.color": INK,
    "axes.edgecolor": LINE, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
    "savefig.dpi": 400, "savefig.bbox": "tight", "savefig.pad_inches": 0.35,
})
plt.rcParams["svg.fonttype"] = "path"


def _box(ax, x, y, w, h, fc, ec=LINE, r=0.12, lw=1.4):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw))


def _save(fig, n):
    for ext in ("svg", "png"):
        fig.savefig(f"figures/fig{n:02d}.{ext}")
    plt.close(fig)


def fig01():
    """One screen for everyone, or one screen per task."""
    fig, ax = plt.subplots(figsize=(10.5, 6.0))
    ax.set_xlim(0, 10.5); ax.set_ylim(0, 6.1); ax.axis("off")
    ax.text(0.05, 5.8, "One screen for everyone, or one screen per task", fontsize=15, weight="bold")

    # ----- left: today -----
    ax.text(0.1, 5.3, "Today: drawn once, for everyone", fontsize=12.5, weight="bold", color=BLUE)
    _box(ax, 0.1, 0.55, 4.8, 4.45, SOFT, ec=MUTED)
    # menu bar
    for i, m in enumerate(["File", "Edit", "View", "Tools", "Help"]):
        ax.text(0.3 + i * 0.85, 4.7, m, fontsize=9.5, color=MUTED)
    ax.plot([0.1, 4.9], [4.5, 4.5], color=LINE, lw=1)
    # side menu
    for j in range(7):
        _box(ax, 0.3, 3.95 - j * 0.48, 0.9, 0.3, BG, ec=LINE, r=0.05, lw=1)
    # grid of fields
    cells = []
    for r in range(6):
        for c in range(4):
            x, y = 1.45 + c * 0.85, 3.95 - r * 0.55
            cells.append((x, y))
            _box(ax, x, y, 0.7, 0.32, BG, ec=LINE, r=0.05, lw=1)
    # the few cells one person actually uses
    for k in (1, 6, 14):
        x, y = cells[k]
        _box(ax, x, y, 0.7, 0.32, GLOW, ec=AMBER, r=0.05, lw=1.8)
    ax.text(2.5, 0.2, "one task uses a few of these", ha="center", fontsize=10.5, color=AMBER)

    # ----- right: tomorrow -----
    ax.text(5.6, 5.3, "Tomorrow: drawn per task, then thrown away", fontsize=12.5, weight="bold", color=AMBER)
    _box(ax, 5.6, 4.15, 4.8, 0.75, BG, ec=MUTED)
    ax.text(5.8, 4.52, "“Pay this invoice, like last month.”", fontsize=11, color=INK, va="center")
    ax.annotate("", xy=(8.0, 3.55), xytext=(8.0, 4.1),
                arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.6))
    ax.text(8.15, 3.78, "the agent draws", fontsize=10, color=MUTED, va="center")
    _box(ax, 6.6, 1.55, 2.8, 1.95, GLOW, ec=AMBER, lw=1.8)
    ax.text(6.8, 3.1, "Amount   1,240.00", fontsize=10.5, color=INK)
    ax.text(6.8, 2.68, "To   the usual supplier", fontsize=10.5, color=INK)
    _box(ax, 7.35, 1.78, 1.3, 0.45, AMBER, ec=AMBER, r=0.1)
    ax.text(8.0, 2.0, "Confirm", ha="center", va="center", fontsize=11, color=BG, weight="bold")
    ax.text(9.55, 2.5, "used once,\nthen gone", fontsize=10, color=MUTED, va="center")

    # what stays
    _box(ax, 5.6, 0.25, 4.8, 0.9, BLUE_GLOW, ec=BLUE)
    ax.text(8.0, 0.84, "What stays: the parts and the rules", ha="center", fontsize=11, weight="bold", color=BLUE)
    ax.text(8.0, 0.45, "buttons, fields, charts; what must always be shown", ha="center", fontsize=9.8, color=MUTED)
    _save(fig, 1)


def fig02():
    """Where a fixed screen survives."""
    fig, ax = plt.subplots(figsize=(9.0, 6.4))
    ax.set_xlim(0, 10); ax.set_ylim(0, 7.2); ax.axis("off")
    ax.text(0.0, 6.9, "Where a fixed screen survives", fontsize=15.5, weight="bold")

    x0, y0, w, h = 1.0, 0.9, 4.3, 2.6
    quads = [
        # (col, row, fill, edge, title, lines)
        (0, 0, GLOW, AMBER, "Disposable", "drawn, used, thrown away:\na refund, a form you\nfill in once a year."),
        (1, 0, BLUE_GLOW, BLUE, "Drawn once, then kept", "a habit forms, so the\nscreen stops changing:\nthe daily timesheet."),
        (0, 1, SOFT, INK, "Drawn from fixed rules", "the same facts, shown the\nsame way, before anything\nthat matters: a payment,\na signature."),
        (1, 1, SOFT, MUTED, "Instruments", "a map, a canvas,\nan editor: kept, and\nshaped by hand\nover years."),
    ]
    for col, row, fc, ec, title, body in quads:
        x, y = x0 + col * (w + 0.15), y0 + row * (h + 0.15)
        _box(ax, x, y, w, h, fc, ec=ec, lw=1.6)
        ax.text(x + 0.25, y + h - 0.45, title, fontsize=13.5, weight="bold", color=ec if ec != MUTED else INK)
        ax.text(x + 0.25, y + h - 0.85, body, fontsize=11.5, color=MUTED, va="top", linespacing=1.35)

    # axes
    ax.annotate("", xy=(x0 + 2 * w + 0.2, 0.55), xytext=(x0, 0.55),
                arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.5))
    ax.text(x0, 0.2, "rare", fontsize=11, color=MUTED)
    ax.text(x0 + 2 * w + 0.15, 0.2, "every day", fontsize=11, color=MUTED, ha="right")
    ax.text(x0 + w + 0.1, 0.2, "how often I do it", fontsize=11, color=INK, ha="center")
    ax.annotate("", xy=(0.72, y0 + 2 * h + 0.2), xytext=(0.72, y0),
                arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.5))
    ax.text(-0.05, y0 + h + 0.07, "what I need the screen for", fontsize=11, color=INK, rotation=90, ha="center", va="center")
    ax.text(0.35, y0 + 0.1, "to get it done", fontsize=10, color=MUTED, rotation=90, ha="center", va="bottom")
    ax.text(0.35, y0 + 2 * h + 0.1, "to see, decide", fontsize=10, color=MUTED, rotation=90, ha="center", va="top")
    _save(fig, 2)


if __name__ == "__main__":
    fig01(); fig02()
