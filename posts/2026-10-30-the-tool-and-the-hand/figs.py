"""Figures for "The Tool and the Hand". Same style as "The Joy of the Question".
Run: python figs.py
Each figure is written twice: a vector SVG (used in the page) and a 400 dpi PNG.
Both figures are schematics: they show a shape, not measured data."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle

# ---------- palette (from light.scss) ----------
BG = "#fbfaf7"
INK = "#1f2328"
MUTED = "#5f6b76"
RULE = "#e6e2da"
NAVY = "#1d4f73"
DEEP = "#0b1733"
AMBER = "#e0952b"
WARM = "#b36b00"
GREEN = "#2e7d5b"
RED = "#a93226"
NAVY_T, AMBER_T, GREEN_T, SAND_T = "#e5eef5", "#fdf1dc", "#e2f0e8", "#f2efe9"

SANS = "Inter"
plt.rcParams.update({
    "font.family": SANS, "font.size": 10, "text.color": INK,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.8,
    "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
    "savefig.dpi": 400, "savefig.bbox": "tight", "savefig.pad_inches": 0.18,
    "legend.frameon": False,
})
plt.rcParams["svg.fonttype"] = "path"     # text as outlines: the SVG looks the same everywhere
OUT = "figures/"


# ---------- drawing helpers ----------
def canvas(w, h, xmax, ymax):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, xmax); ax.set_ylim(0, ymax); ax.set_aspect("equal"); ax.axis("off")
    return fig, ax


def box(ax, x, y, w, h, title, sub=None, fill="white", edge=RULE, accent=None,
        fs=10.5, subfs=8.4, tcol=INK, scol=MUTED, z=2, r=0.25):
    ax.add_patch(FancyBboxPatch((x + 0.04, y - 0.07), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                fc=DEEP, ec="none", alpha=0.05, zorder=z))
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                fc=fill, ec=edge, lw=0.9, zorder=z + 1))
    if accent:
        ax.add_patch(FancyBboxPatch((x + 0.14, y + 0.18), 0.08, h - 0.36,
                                    boxstyle="round,pad=0,rounding_size=0.04", fc=accent, ec="none", zorder=z + 2))
    cx, cy = x + w / 2 + (0.08 if accent else 0), y + h / 2
    if sub:
        n = sub.count("\n")
        ax.text(cx, cy + 0.2 + 0.15 * n, title, ha="center", va="center", fontsize=fs, weight="bold", color=tcol, zorder=z + 3)
        ax.text(cx, cy - 0.28 + 0.03 * n, sub, ha="center", va="center", fontsize=subfs, color=scol, zorder=z + 3,
                linespacing=1.25)
    else:
        ax.text(cx, cy, title, ha="center", va="center", fontsize=fs, weight="bold", color=tcol, zorder=z + 3)


def save(fig, name):
    fig.savefig(OUT + name + ".svg")
    fig.savefig(OUT + name + ".png")
    plt.close(fig)


# ---------- Figure 1: the tool amplifies what is there ----------
def fig01():
    fig, ax = plt.subplots(figsize=(10, 4.6))
    xs = [0, 1]
    people = [("Already driven", "asks, tries, fails, tries again", 3.0, 7.4, GREEN),
              ("Does what is asked", "no more, no less", 2.0, 3.1, NAVY),
              ("Waits to be told", "postpones, avoids the hard part", 1.0, 1.25, RED)]
    for name, sub, a, b, col in people:
        ax.plot(xs, [a, b], color=col, lw=2.4, solid_capstyle="round", zorder=3)
        ax.scatter(xs, [a, b], s=46, color=col, zorder=4, edgecolor=BG, linewidth=1.5)
        ax.text(1.04, b + 0.12, name, va="bottom", fontsize=10, weight="bold", color=col)
        ax.text(1.04, b + 0.05, sub, va="top", fontsize=8.6, color=MUTED)
    # the gap, before and after
    for x, lo, hi, lab in ((-0.05, 1.0, 3.0, "gap before"), (0.95, 1.25, 7.4, "gap after")):
        ax.annotate("", xy=(x, lo), xytext=(x, hi),
                    arrowprops=dict(arrowstyle="<->", color=WARM, lw=1.0, shrinkA=4, shrinkB=4))
        ax.text(x - 0.02, (lo + hi) / 2, lab, ha="right", va="center", fontsize=8.6, color=WARM, style="italic")
    ax.set_xticks(xs, ["Before AI", "With AI"], fontsize=10)
    ax.set_xlim(-0.32, 1.55); ax.set_ylim(0, 8.4)
    ax.spines["left"].set_visible(False); ax.tick_params(left=False, labelleft=False)
    ax.set_ylabel("")
    ax.text(-0.32, 8.3, "What gets done, with the same tool", fontsize=9.8, color=INK, va="top")
    save(fig, "fig01")


# ---------- Figure 2: how a mindset is shaped ----------
def fig02():
    fig, ax = canvas(10, 5.6, 20, 11.2)
    cx, cy, R = 7.0, 5.6, 4.4
    ax.add_patch(Circle((cx, cy), R, fc="none", ec=GREEN, lw=1.4, ls=(0, (2, 3)), zorder=1, alpha=0.7))
    for ang in (45, -45, -135, 135):
        a = np.deg2rad(ang)
        p = (cx + R * np.cos(a), cy + R * np.sin(a))
        t = np.deg2rad(ang - 90)
        ax.add_patch(FancyArrowPatch((p[0] - 0.05 * np.cos(t), p[1] - 0.05 * np.sin(t)),
                                     (p[0] + 0.05 * np.cos(t), p[1] + 0.05 * np.sin(t)),
                                     arrowstyle="-|>", mutation_scale=13, color=GREEN, lw=0, zorder=2))
    steps = [("See it done", "someone who explains\nthe why, and finishes"),
             ("Own something", "a task of your own,\ntrusted while unfinished"),
             ("Finish it", "a small win, shown\nbefore it is perfect"),
             ("Be noticed", "feedback that names\nthe step forward")]
    pos = [(cx, cy + R), (cx + R, cy), (cx, cy - R), (cx - R, cy)]
    for (x, y), (t, s) in zip(pos, steps):
        box(ax, x - 1.95, y - 0.8, 3.9, 1.6, t, s, accent=GREEN, fs=9.8, subfs=7.9)
    ax.text(cx, cy + 0.3, "shaped by people", ha="center", va="center", fontsize=11, weight="bold", color=GREEN)
    ax.text(cx, cy - 0.3, "each turn, initiative\nfeels more natural", ha="center", va="center",
            fontsize=8.6, color=MUTED, style="italic", linespacing=1.25)
    # the tool, outside the loop
    box(ax, 14.0, 4.3, 5.6, 2.6, "", fill=AMBER_T, edge=AMBER)
    ax.text(16.8, 6.3, "AI", ha="center", va="center", fontsize=11.5, weight="bold", color=WARM, zorder=6)
    ax.text(16.8, 5.25, "can speed up each step\nonce the loop is turning.\nIt cannot start it.",
            ha="center", va="center", fontsize=8.6, color=INK, linespacing=1.3, zorder=6)
    ax.add_patch(FancyArrowPatch((13.9, 5.6), (cx + R + 1.9, 5.6), arrowstyle="-|>", mutation_scale=11,
                                 lw=1.2, color=WARM, linestyle=(0, (4, 3)), zorder=1))
    save(fig, "fig02")


if __name__ == "__main__":
    for f in (fig01, fig02):
        f()
