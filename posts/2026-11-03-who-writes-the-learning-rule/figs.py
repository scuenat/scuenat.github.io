"""Figures for "Who Writes the Learning Rule?".

Same style as "The Teacher Who Writes the Weights": Inter type, white cards with a faint
shadow and a coloured accent, colours taken from the site's palette.

Figure 1 is a schematic map of work from 2020 to 2026 on learning with local rules, sorted by
what the designer still fixes. The placement is my own reading; the works are cited in the text.
It shows no data.
"""
import json
import re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle

# ---------- palette (from light.scss) ----------
BG = "#fbfaf7"
INK = "#1f2328"
MUTED = "#5f6b76"
RULE = "#e6e2da"
NAVY = "#1d4f73"
DEEP = "#0b1733"
AMBER = "#f5b041"
WARM = "#b36b00"
GREEN = "#2e7d5b"
RED = "#a93226"
NAVY_T, AMBER_T, GREEN_T, SAND_T = "#e5eef5", "#fdf1dc", "#e2f0e8", "#f2efe9"

SANS, MONO = "Inter", "JetBrains Mono"
plt.rcParams.update({
    "font.family": SANS, "font.size": 10, "text.color": INK,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.8,
    "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
    "savefig.dpi": 220, "savefig.bbox": "tight", "savefig.pad_inches": 0.35,
    "legend.frameon": False,
})
OUT = "figures/"


# ---------- drawing helpers ----------
def canvas(w, h, xmax, ymax):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, xmax); ax.set_ylim(0, ymax); ax.set_aspect("equal"); ax.axis("off")
    return fig, ax


def shadow(ax, x, y, w, h, r=0.28, z=1):
    for i, a in enumerate((0.035, 0.03, 0.025)):
        d = 0.05 + 0.05 * i
        ax.add_patch(FancyBboxPatch((x + d * 0.4, y - d), w, h,
                                    boxstyle=f"round,pad=0,rounding_size={r + d * 0.5}",
                                    fc=DEEP, ec="none", alpha=a, zorder=z))


def card(ax, x, y, w, h, title, sub=None, accent=NAVY, fill="white", eyebrow=None,
         fs=10.5, subfs=8.4, z=2, r=0.28, bar=True, align="center", mono_sub=False):
    """A white card with a faint shadow and a coloured accent bar on the left.
    fill set to a colour gives a solid card with white text."""
    solid = fill not in ("white", BG, NAVY_T, AMBER_T, GREEN_T, SAND_T)
    shadow(ax, x, y, w, h, r, z)
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                fc=fill, ec="none" if solid else RULE, lw=0.9, zorder=z + 1))
    if bar and not solid:
        ax.add_patch(FancyBboxPatch((x + 0.16, y + 0.2), 0.09, h - 0.4,
                                    boxstyle="round,pad=0,rounding_size=0.045",
                                    fc=accent, ec="none", zorder=z + 2))
    tcol = "white" if solid else INK
    scol = "#dfe8f1" if solid else MUTED
    shift = 0.12 if bar and not solid else 0
    cx = x + w / 2 + shift if align == "center" else x + 0.55
    ha = "center" if align == "center" else "left"
    # stack eyebrow, title and subtitle around the card's centre, measured in points
    nsub = sub.count("\n") + 1 if sub else 0
    parts = []
    if eyebrow:
        parts.append((eyebrow.upper(), dict(fontsize=6.6, weight="semibold",
                                            color=accent if not solid else AMBER), 6.6 * 1.25 + 3))
    if title:
        parts.append((title, dict(fontsize=fs, weight="semibold", color=tcol), fs * 1.25 + 3))
    if sub:
        parts.append((sub, dict(fontsize=subfs, color=scol, linespacing=1.3,
                                fontfamily=MONO if mono_sub else SANS), subfs * 1.3 * nsub))
    total = sum(p[2] for p in parts)
    off = total / 2
    for text, kw, hgt in parts:
        ax.annotate(text, (cx, y + h / 2), xytext=(0, off), textcoords="offset points",
                    ha=ha, va="top", zorder=z + 3, **kw)
        off -= hgt


def arrow(ax, p, q, color=MUTED, rad=0.0, lw=1.5, ls="-", z=1.5, head=10, alpha=1.0):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>,head_length=0.55,head_width=0.3",
                                 mutation_scale=head, color=color, lw=lw, ls=ls, alpha=alpha,
                                 connectionstyle=f"arc3,rad={rad}", shrinkA=0, shrinkB=0,
                                 capstyle="round", joinstyle="round", zorder=z))


def edge_point(x, y, w, h, tx, ty, gap=0.12):
    """Where the ray from the centre of box (x, y, w, h) toward (tx, ty) leaves the box."""
    cx, cy = x + w / 2, y + h / 2
    dx, dy = tx - cx, ty - cy
    t = min((w / 2 + gap) / abs(dx) if dx else 1e9, (h / 2 + gap) / abs(dy) if dy else 1e9)
    return cx + dx * t, cy + dy * t


def pill(ax, x, y, text, color=MUTED, fill=BG, fs=7.6, z=6, weight="medium", mono=False):
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, color=color, weight=weight,
            fontfamily=MONO if mono else SANS, zorder=z,
            bbox=dict(boxstyle="round,pad=0.32,rounding_size=0.6", fc=fill, ec=RULE, lw=0.7))


def chip(ax, x, y, text, color=NAVY, fill=NAVY_T, fs=7.2, z=6):
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, color=color, fontfamily=MONO,
            zorder=z, bbox=dict(boxstyle="round,pad=0.28,rounding_size=0.35", fc=fill, ec="none"))


def heading(ax, x, y, eyebrow, title, color=NAVY):
    ax.text(x, y, eyebrow.upper(), fontsize=7, weight="semibold", color=color, va="bottom")
    ax.text(x, y - 0.18, title, fontsize=11.5, weight="semibold", color=INK, va="top")



# ---------- Figure 1: what the designer still fixes ----------
# Each rung: title, subtitle, (wiring, plasticity rule, credit-assignment circuit), works.
# States: "D" designed by hand, "E" learned or emergent, "-" not needed.
RUNGS = [
    ("Backpropagation", "the reference point", ("D", "D", "D"),
     ["Standard deep learning"]),
    ("Local approximations", "local rules, feedback\nthat learns or settles", ("D", "D", "E"),
     ["Kolen-Pollack, mirrors 2019", "e-prop 2020", "Predictive coding 2020",
      "Burst plasticity 2021", "Equilibrium prop. 2021", "Prospective config. 2024"]),
    ("No backward pass", "each layer learns\non its own", ("D", "D", "-"),
     ["Forward-Forward 2022", "SoftHebb 2023"]),
    ("Learned rules", "an outer loop finds\nthe plasticity rule", ("D", "E", "E"),
     ["Confavreux et al. 2020", "Najarro & Risi 2020", "Lindsey & Litwin-Kumar 2020",
      "Jordan et al. 2021", "Kirsch & Schmidhuber 2021", "Shervani-Tabar & R. 2023"]),
    ("Self-assembly", "wiring or learning\ncircuit emerges", ("E", "D", "E"),
     ["Neural cellular automata 2020", "Developmental programs 2023",
      "Heterosynaptic circuits 2025", "Self-assembling learning 2026"]),
]
ROWS = ["Wiring", "Plasticity rule", "Learning circuit"]
COLORS = [MUTED, NAVY, GREEN, WARM, "#1f6f78"]


def state_dot(ax, x, y, s, color):
    if s == "D":
        ax.add_patch(Circle((x, y), 0.13, fc=NAVY, ec=NAVY, lw=1, zorder=6))
    elif s == "E":
        ax.add_patch(Circle((x, y), 0.13, fc=AMBER, ec=WARM, lw=1, zorder=6))
    else:
        ax.add_patch(Circle((x, y), 0.13, fc="white", ec=MUTED, lw=1, ls=(0, (2, 1.5)), zorder=6))


def fig_map():
    """Vertical layout, so it stays readable on a phone: one row per line of work."""
    W, H = 10.6, 15.2
    fig, ax = canvas(6.6, 9.46, W, H)
    heading(ax, 0.2, 14.95, "Learning with local rules, 2020 to 2026",
            "What does the designer still fix?", color=NAVY)
    rh, gap, top = 2.38, 0.3, 13.95
    for i, (title, sub, states, works) in enumerate(RUNGS):
        y = top - (i + 1) * rh - i * gap
        indent = 0.2
        card(ax, indent, y + 0.35, 3.75, rh - 0.7, title, sub, accent=COLORS[i], fs=10.2,
             subfs=8.2, align="left")
        for r, (lab, st) in enumerate(zip(ROWS, states)):
            yy = y + rh - 0.62 - r * 0.5
            state_dot(ax, 4.35, yy, st, COLORS[i])
            ax.text(4.6, yy, lab, fontsize=8.4, color=INK if st != "-" else MUTED, va="center")
        ncol = 1 if len(works) <= 3 else 2
        per = (len(works) + ncol - 1) // ncol
        for k, wk in enumerate(works):
            c, rr = divmod(k, per)
            ax.text(6.75 + c * 0.0, y + rh - 0.42 - k * 0.33, wk, fontsize=7.9, color=MUTED,
                    va="center")
        if i < len(RUNGS) - 1:
            ax.plot([0.2, W - 0.2], [y - gap / 2, y - gap / 2], color=RULE, lw=0.8)
    ly = 0.35
    state_dot(ax, 0.4, ly, "D", NAVY)
    ax.text(0.65, ly, "designed by hand", fontsize=8.4, va="center", color=INK)
    state_dot(ax, 3.4, ly, "E", WARM)
    ax.text(3.65, ly, "learned or emergent", fontsize=8.4, va="center", color=INK)
    state_dot(ax, 6.8, ly, "-", MUTED)
    ax.text(7.05, ly, "not needed", fontsize=8.4, va="center", color=INK)
    ax.text(W - 0.2, 14.95, "Schematic, my own reading", fontsize=7.6, va="bottom", ha="right",
            color=MUTED, style="italic")
    fig.savefig(OUT + "fig01.png", dpi=400); fig.savefig(OUT + "fig01.svg"); plt.close(fig)


if __name__ == "__main__":
    fig_map()
