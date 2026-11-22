"""Figures for "The Disposable Screen". Same palette as the other essays.
Run: python figs.py   (needs matplotlib)
Written twice: a vector SVG (used in the page) and a 400 dpi PNG (card image).
All three figures are schematics, my own: they show a shape, not data."""
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


def _arrow(ax, a, b, color=MUTED, lw=1.8, ls="-"):
    ax.annotate("", xy=b, xytext=a,
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, linestyle=ls, shrinkA=0, shrinkB=0))


def fig01():
    """Who reaches the backend: a person through a screen, or an agent."""
    fig, ax = plt.subplots(figsize=(10.5, 6.6))
    ax.set_xlim(0, 10.5); ax.set_ylim(0, 6.7); ax.axis("off")
    ax.text(0.05, 6.4, "The screen was the way in to the backend", fontsize=15, weight="bold")

    # ----- left: today -----
    ax.text(0.1, 5.85, "Today: a person drives the backend", fontsize=12.5, weight="bold", color=BLUE)
    ax.text(0.1, 5.5, "through screens defined in advance", fontsize=11, color=MUTED)
    _box(ax, 1.2, 4.55, 2.6, 0.65, BG, ec=MUTED)
    ax.text(2.5, 4.87, "a person", ha="center", va="center", fontsize=11.5)
    _arrow(ax, (2.5, 4.5), (2.5, 4.05))
    _box(ax, 0.3, 2.3, 4.4, 1.7, BLUE_GLOW, ec=BLUE, lw=1.8)
    ax.text(2.5, 3.6, "The screen", ha="center", fontsize=13, weight="bold", color=BLUE)
    ax.text(2.5, 2.75, "menus, pages, forty-field forms,\nthe same for everyone", ha="center",
            fontsize=10.5, color=MUTED, linespacing=1.3)
    _arrow(ax, (2.5, 2.25), (2.5, 1.8))
    _box(ax, 0.3, 0.75, 4.4, 1.0, SOFT, ec=INK)
    ax.text(2.5, 1.38, "The backend", ha="center", fontsize=12.5, weight="bold")
    ax.text(2.5, 1.0, "functions and data", ha="center", fontsize=10.5, color=MUTED)

    # ----- right: tomorrow -----
    ax.text(5.6, 5.85, "Tomorrow: an agent drives the backend", fontsize=12.5, weight="bold", color=AMBER)
    ax.text(5.6, 5.5, "and draws a screen only when a person is needed", fontsize=11, color=MUTED)
    _box(ax, 6.0, 4.55, 2.6, 0.65, BG, ec=MUTED)
    ax.text(7.3, 4.87, "a person", ha="center", va="center", fontsize=11.5)
    _arrow(ax, (7.0, 4.5), (7.0, 4.05))
    ax.text(6.9, 4.25, "says what\nthey want", ha="right", va="center", fontsize=9.8, color=MUTED, linespacing=1.15)
    _box(ax, 6.0, 3.25, 2.6, 0.75, GLOW, ec=AMBER, lw=1.8)
    ax.text(7.3, 3.62, "an agent", ha="center", va="center", fontsize=12.5, weight="bold", color=AMBER)
    _arrow(ax, (7.3, 3.2), (7.3, 1.8), color=INK, lw=2.2)
    ax.text(7.42, 2.5, "calls the\nfunctions\ndirectly", ha="left", va="center", fontsize=9.8, color=INK, linespacing=1.15)
    _box(ax, 5.6, 0.75, 4.8, 1.0, SOFT, ec=INK)
    ax.text(8.0, 1.38, "The backend", ha="center", fontsize=12.5, weight="bold")
    ax.text(8.0, 1.0, "functions and data, described for the agent", ha="center", fontsize=10.5, color=MUTED)
    # the occasional screen
    _box(ax, 9.0, 3.3, 1.35, 1.0, BG, ec=AMBER, r=0.08, lw=1.6)
    ax.plot([9.15, 10.2], [4.05, 4.05], color=LINE, lw=1.2)
    ax.plot([9.15, 9.9], [3.82, 3.82], color=LINE, lw=1.2)
    _box(ax, 9.35, 3.42, 0.65, 0.24, AMBER, ec=AMBER, r=0.05)
    _arrow(ax, (8.65, 3.62), (8.95, 3.75), color=AMBER, lw=1.6, ls="--")
    _arrow(ax, (9.67, 4.35), (8.65, 4.85), color=AMBER, lw=1.6, ls="--")
    ax.text(9.67, 2.95, "a screen for\nthis moment,\nif needed", ha="center", va="top", fontsize=9.8,
            color=AMBER, linespacing=1.15)

    ax.text(5.25, 0.25, "The backend stays. What changes is who reaches it, and how often a screen is needed.",
            ha="center", fontsize=10.5, color=MUTED)
    _save(fig, 1)


def fig02():
    """One task, two ways."""
    fig, ax = plt.subplots(figsize=(10.5, 5.6))
    ax.set_xlim(0, 10.5); ax.set_ylim(0, 5.6); ax.axis("off")
    ax.text(0.05, 5.3, "One task, two ways: pay a supplier's invoice", fontsize=15, weight="bold")

    ax.text(0.1, 4.6, "Today: six screens, each defined in advance, each driven by a person",
            fontsize=12, weight="bold", color=BLUE)
    steps = ["open\nthe app", "find the\nmenu", "search the\ninvoice", "check the\nsupplier",
             "fill in the\npayment", "confirm"]
    for i, t in enumerate(steps):
        x = 0.1 + i * 1.73
        _box(ax, x, 3.0, 1.45, 1.25, BLUE_GLOW, ec=BLUE, r=0.08)
        ax.plot([x + 0.12, x + 1.33], [4.02, 4.02], color=LINE, lw=1.2)
        ax.text(x + 0.72, 3.45, t, ha="center", va="center", fontsize=10.3, linespacing=1.15)
        if i < len(steps) - 1:
            _arrow(ax, (x + 1.48, 3.62), (x + 1.7, 3.62), lw=1.4)

    ax.text(0.1, 2.2, "Tomorrow: the agent does the steps through the backend; one screen, at the decision",
            fontsize=12, weight="bold", color=AMBER)
    _box(ax, 0.1, 0.35, 2.4, 1.3, BG, ec=MUTED)
    ax.text(1.3, 1.0, "\u201cPay this invoice,\nlike last month.\u201d", ha="center", va="center",
            fontsize=10.5, linespacing=1.2)
    _arrow(ax, (2.55, 1.0), (2.95, 1.0), lw=1.4)
    calls = ["find invoice", "check supplier", "prepare payment"]
    for i, t in enumerate(calls):
        x = 3.0 + i * 1.62
        ax.add_patch(plt.Circle((x + 0.15, 1.0), 0.1, color=INK))
        ax.text(x + 0.32, 1.0, t, va="center", fontsize=10.3, color=INK)
    ax.text(4.6, 0.45, "backend calls, no screen", ha="center", fontsize=10, color=MUTED)
    ax.plot([3.0, 7.85], [0.68, 0.68], color=LINE, lw=1.2)
    _arrow(ax, (7.9, 1.0), (8.3, 1.0), lw=1.4)
    _box(ax, 8.35, 0.35, 2.05, 1.3, GLOW, ec=AMBER, lw=1.8)
    ax.text(9.37, 1.33, "1,240.00 to the\nusual supplier", ha="center", va="center", fontsize=9.8, linespacing=1.15)
    _box(ax, 8.85, 0.48, 1.05, 0.34, AMBER, ec=AMBER, r=0.07)
    ax.text(9.37, 0.65, "Confirm", ha="center", va="center", fontsize=10, color=BG, weight="bold")
    _save(fig, 2)


def fig03():
    """Where a fixed screen survives."""
    fig, ax = plt.subplots(figsize=(9.0, 6.4))
    ax.set_xlim(0, 10); ax.set_ylim(0, 7.2); ax.axis("off")
    ax.text(0.0, 6.9, "Where a fixed screen survives", fontsize=15.5, weight="bold")

    x0, y0, w, h = 1.0, 0.9, 4.3, 2.6
    quads = [
        # (col, row, fill, edge, title, lines)
        (0, 0, GLOW, AMBER, "No screen, or a brief one", "the agent does it through\nthe backend; at most a screen\nto confirm: a refund, a form\nyou fill in once a year."),
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
    _save(fig, 3)


if __name__ == "__main__":
    fig01(); fig02(); fig03()
