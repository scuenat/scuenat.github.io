"""Figures for "Who Writes the Learning Rule?".

Same style as "The Teacher Who Writes the Weights": Inter type, white cards with a faint
shadow and a coloured accent, colours taken from the site's palette.

All five figures are schematics of ideas described in the cited work; none shows data.
Figure 1: the weight transport problem, and two ways around it.
Figure 2: a map of work from 2020 to 2026, sorted by what the designer still fixes (my own reading).
Figure 3: three local ways to carry an error signal (equilibrium propagation, predictive coding,
bursts).
Figure 4: two loops, a fast lifetime loop and a slow loop that tunes the rule.
Figure 5: the idea of self-assembling learning, simplified; not the paper's exact circuit.
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
    ("Learned rules", "an outer loop finds\nthe plasticity rule", ("D", "E", "D"),
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
    fig.savefig(OUT + "fig02.png", dpi=400); fig.savefig(OUT + "fig02.svg"); plt.close(fig)



TEAL = "#1f6f78"
TEAL_T = "#e1f0f1"


def layer(ax, cx, cy, n=3, w=1.9, label=None, fill="white", dot=NAVY):
    """A layer of neurons: a rounded box with n dots."""
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - 0.32), w, 0.64,
                                boxstyle="round,pad=0,rounding_size=0.3", fc=fill, ec=RULE,
                                lw=0.9, zorder=3))
    xs = np.linspace(cx - w / 2 + 0.38, cx + w / 2 - 0.38, n)
    for x in xs:
        ax.add_patch(Circle((x, cy), 0.13, fc=dot, ec="none", zorder=4))
    if label:
        ax.text(cx - w / 2 - 0.15, cy, label, ha="right", va="center", fontsize=8, color=MUTED)
    return xs


def save(fig, n):
    fig.savefig(OUT + f"fig0{n}.png", dpi=400); fig.savefig(OUT + f"fig0{n}.svg"); plt.close(fig)


# ---------- Figure 1: weight transport ----------
def fig_transport():
    W, H = 10.6, 7.4
    fig, ax = canvas(6.6, 4.6, W, H)
    ax.set_ylim(-0.6, H)
    heading(ax, 0.2, 7.15, "Credit assignment", "Who tells a connection how to change?")
    panels = [
        ("Backpropagation", "feedback = W$^{\\mathsf{T}}$", NAVY, "-",
         "Feedback must copy\nthe forward weights:\na synapse must know\nanother's strength."),
        ("Feedback alignment", "feedback = B, random", MUTED, (0, (3, 2)),
         "Fixed random\nfeedback; forward\nweights adapt to it.\nWeak on hard tasks."),
        ("Learned feedback", "B learns to track W", WARM, "-",
         "Feedback weights\nlearn from local\nactivity (Kolen-Pollack,\nweight mirrors)."),
    ]
    for i, (title, flab, col, ls, note) in enumerate(panels):
        cx = 1.75 + i * 3.55
        ax.text(cx, 5.95, title, ha="center", fontsize=9.6, weight="semibold", color=INK)
        layer(ax, cx, 5.2, label="output" if i == 0 else None)
        layer(ax, cx, 2.9, label="input" if i == 0 else None)
        arrow(ax, (cx - 0.45, 3.3), (cx - 0.45, 4.8), color=NAVY, lw=1.8)
        ax.text(cx - 0.62, 4.05, "W", ha="right", va="center", fontsize=9, color=NAVY,
                weight="semibold")
        arrow(ax, (cx + 0.45, 4.8), (cx + 0.45, 3.3), color=col, lw=1.8, ls=ls)
        ax.text(cx + 0.62, 4.05, "error", ha="left", va="center", fontsize=8, color=col)
        chip(ax, cx, 2.2, flab, color=col if col != MUTED else INK,
             fill={NAVY: NAVY_T, MUTED: SAND_T, WARM: AMBER_T}[col], fs=8.2)
        ax.text(cx, 1.65, note, ha="center", va="top", fontsize=9, color=MUTED, linespacing=1.35)
    save(fig, 1)


# ---------- Figure 3: three local error signals ----------
def fig_local():
    W, H = 10.6, 11.6
    fig, ax = canvas(6.6, 7.22, W, H)
    heading(ax, 0.2, 11.35, "Approximating the gradient locally",
            "Three ways to carry an error with local signals")
    rows = [
        ("Equilibrium propagation", NAVY,
         [("1. free phase", "network settles\non the input"),
          ("2. nudged phase", "output pulled to the\ntarget, settles again"),
          ("3. update", "each synapse\ncompares two states")],
         "Δw ~ (pre × post, nudged) − (pre × post, free)"),
        ("Predictive coding", GREEN,
         [("prediction", "each layer predicts\nthe one below"),
          ("error unit", "ε = activity\n− prediction"),
          ("update", "error times the\nlocal input")],
         "Δw ~ ε × pre: both are at the synapse"),
        ("Burst-dependent plasticity", WARM,
         [("presynaptic trace", "the input was\nrecently active"),
          ("burst", "postsynaptic burst:\nstrengthen"),
          ("single spike", "postsynaptic spike:\nweaken")],
         "feedback changes the burst rate: a teaching signal"),
    ]
    rh = 3.35
    for i, (name, col, steps, rule) in enumerate(rows):
        y = 10.2 - i * rh
        ax.add_patch(FancyBboxPatch((0.2, y - 0.08), 0.09, 0.42, boxstyle="round,pad=0,rounding_size=0.04",
                                    fc=col, ec="none"))
        ax.text(0.45, y + 0.13, name, fontsize=9.8, weight="semibold", color=INK, va="center")
        for k, (t, sub) in enumerate(steps):
            x = 0.2 + k * 3.5
            card(ax, x, y - 2.05, 3.05, 1.6, t, sub, accent=col, fs=9.8, subfs=8.6)
            if k == 2 and i == 2:
                ax.text(x - 0.22, y - 1.25, "or", ha="center", va="center", fontsize=8,
                        color=MUTED, style="italic")
            if k < 2 and not (i == 2 and k == 1):
                arrow(ax, (x + 3.1, y - 1.25), (x + 3.45, y - 1.25), color=MUTED, lw=1.2, head=8)
        ax.text(0.45, y - 2.45, rule, fontsize=9, color=col, va="center", style="italic")
    save(fig, 3)


# ---------- Figure 4: two loops ----------
def fig_loops():
    W, H = 10.6, 7.6
    fig, ax = canvas(6.6, 4.73, W, H)
    heading(ax, 0.2, 7.35, "Learning the learning rule", "Two loops, two speeds")
    # outer loop frame
    ax.add_patch(FancyBboxPatch((0.2, 0.3), 10.2, 5.9, boxstyle="round,pad=0,rounding_size=0.4",
                                fc=AMBER_T, ec="none", zorder=0.5))
    ax.text(0.5, 5.85, "SLOW LOOP · evolution or meta-learning",
            fontsize=8, weight="semibold", color=WARM, va="center")
    # inner loop frame
    ax.add_patch(FancyBboxPatch((0.55, 0.65), 6.0, 4.75, boxstyle="round,pad=0,rounding_size=0.35",
                                fc=NAVY_T, ec="none", zorder=0.6))
    ax.text(0.85, 5.05, "FAST LOOP · one lifetime", fontsize=8, weight="semibold",
            color=NAVY, va="center")
    card(ax, 0.9, 2.7, 2.6, 1.7, "Network", "weights w\nstart random", accent=NAVY, fs=10.2, subfs=8.8)
    card(ax, 3.75, 2.7, 2.5, 1.7, "Local rule", "Δw = $f_\\theta$(pre, post,\nsignal)", accent=NAVY,
         fs=10.2, subfs=8.6, mono_sub=False)
    arrow(ax, (3.5, 3.85), (3.75, 3.85), color=NAVY, lw=1.3, head=8)
    arrow(ax, (3.75, 3.2), (3.5, 3.2), color=NAVY, lw=1.3, head=8)
    ax.text(0.9, 1.55, "the network lives its task;\nthe rule changes w at every step",
            ha="left", va="center", fontsize=8.6, color=MUTED, linespacing=1.35)
    card(ax, 7.1, 3.3, 3.0, 1.55, "Score", "how well did it learn\nby the end of life?",
         accent=WARM, fs=10.2, subfs=8.6)
    card(ax, 7.1, 0.85, 3.0, 1.55, "Update θ", "change the rule's\nfew parameters",
         accent=WARM, fs=10.2, subfs=8.6)
    arrow(ax, (6.3, 4.0), (7.05, 4.05), color=WARM, lw=1.4)
    arrow(ax, (8.6, 3.25), (8.6, 2.45), color=WARM, lw=1.4)
    arrow(ax, (7.05, 1.6), (5.9, 2.65), color=WARM, lw=1.4, rad=-0.25)
    save(fig, 4)


# ---------- Figure 5: self-assembling learning, simplified ----------
def fig_assembly():
    W, H = 10.6, 12.2
    fig, ax = canvas(6.6, 7.6, W, H)
    heading(ax, 0.2, 11.95, "Self-assembling learning, simplified",
            "From random wiring to gradient-like learning", color=TEAL)
    rng = np.random.default_rng(3)
    boxes = [(0.2, 6.0), (5.45, 6.0), (0.2, 0.75), (5.45, 0.75)]
    titles = ["1. Random connectivity", "2. A local, heterosynaptic rule",
              "3. A motif assembles", "4. Motifs stack into layers"]
    subs = ["no structure is designed", "a synapse changes with its\nneighbours' activity",
            "a forward and a feedback stream\nwhose connections now fit together",
            "the whole network now learns\nlike (generalised) SGD"]
    for (x, y), t, sb in zip(boxes, titles, subs):
        ax.add_patch(FancyBboxPatch((x, y), 4.95, 4.85, boxstyle="round,pad=0,rounding_size=0.3",
                                    fc="white", ec=RULE, lw=0.9, zorder=1))
        ax.text(x + 0.3, y + 4.5, t, fontsize=9.2, weight="semibold", color=INK, va="center")
        ax.text(x + 0.3, y + 0.55, sb, fontsize=8.4, color=MUTED, va="center", linespacing=1.3)
    # panel 1: random graph
    x0, y0 = 0.2, 6.0
    pts = np.column_stack([rng.uniform(x0 + 0.6, x0 + 4.4, 14), rng.uniform(y0 + 1.3, y0 + 4.0, 14)])
    for i in range(14):
        for j in rng.choice(14, 2, replace=False):
            if i != j:
                ax.plot(*zip(pts[i], pts[j]), color=MUTED, lw=0.6, alpha=0.45, zorder=2)
    for p in pts:
        ax.add_patch(Circle(p, 0.12, fc=NAVY, ec="none", zorder=3))
    # panel 2: neuron with three synapses
    x0, y0 = 5.45, 6.0
    nc = (x0 + 3.5, y0 + 2.85)
    ax.add_patch(Circle(nc, 0.45, fc=NAVY_T, ec=NAVY, lw=1.2, zorder=3))
    ax.text(*nc, "neuron", ha="center", va="center", fontsize=6.8, color=NAVY, zorder=4)
    for k, (dy, col, lab) in enumerate([(0.8, MUTED, "neighbour"), (0.0, TEAL, "this synapse"),
                                        (-0.8, MUTED, "neighbour")]):
        start = (x0 + 0.5, nc[1] + dy)
        arrow(ax, start, (nc[0] - 0.5, nc[1] + dy * 0.35), color=col, lw=2.2 if col == TEAL else 1.2)
        if dy < 0:
            ax.text(start[0], start[1] - 0.18, lab, fontsize=8.2, color=col, va="top")
        else:
            ax.text(start[0], start[1] + 0.16, lab, fontsize=8.2, color=col, va="bottom")
    # panel 3: motif, two streams
    x0, y0 = 0.2, 0.75
    for k, (cx, lab, col) in enumerate([(x0 + 1.5, "forward", NAVY), (x0 + 3.45, "feedback", WARM)]):
        ax.text(cx, y0 + 4.0, lab, ha="center", fontsize=7.6, color=col, weight="semibold")
        for r in range(2):
            ax.add_patch(Circle((cx, y0 + 3.3 - r * 1.6), 0.24, fc=col, ec="none", alpha=0.9, zorder=3))
        if col == NAVY:
            arrow(ax, (cx, y0 + 1.95), (cx, y0 + 3.0), color=col, lw=1.6)
        else:
            arrow(ax, (cx, y0 + 3.0), (cx, y0 + 1.95), color=col, lw=1.6)
    for r in range(2):
        yy = y0 + 3.3 - r * 1.6
        ax.plot([x0 + 1.8, x0 + 3.15], [yy, yy], color=TEAL, lw=1.6, ls=(0, (3, 2)), zorder=2)
    ax.text(x0 + 2.47, y0 + 2.5, "cross-\nlinks", ha="center", va="center", fontsize=7, color=TEAL)
    # panel 4: stacked motifs
    x0, y0 = 5.45, 0.75
    for r in range(3):
        yy = y0 + 1.25 + r * 1.0
        ax.add_patch(FancyBboxPatch((x0 + 0.8, yy), 2.0, 0.7, boxstyle="round,pad=0,rounding_size=0.2",
                                    fc=TEAL_T, ec=TEAL, lw=0.9, zorder=3))
        ax.text(x0 + 1.8, yy + 0.35, "motif", ha="center", va="center", fontsize=7.6, color=TEAL, zorder=4)
    arrow(ax, (x0 + 0.55, y0 + 1.3), (x0 + 0.55, y0 + 3.85), color=NAVY, lw=1.4)
    arrow(ax, (x0 + 3.05, y0 + 3.85), (x0 + 3.05, y0 + 1.3), color=WARM, lw=1.4)
    ax.text(x0 + 3.3, y0 + 3.1, "errors\nflow back", fontsize=7, color=WARM, va="center")
    arrow(ax, (5.17, 8.4), (5.43, 8.4), color=MUTED, lw=1.3, head=8)
    arrow(ax, (7.9, 5.98), (2.7, 5.62), color=MUTED, lw=1.1, head=8, rad=0.0, alpha=0.6)
    arrow(ax, (5.17, 3.2), (5.43, 3.2), color=MUTED, lw=1.3, head=8)
    ax.text(W - 0.2, 0.25, "Schematic of the idea, not the paper's exact circuit", fontsize=7.2,
            ha="right", va="center", color=MUTED, style="italic")
    save(fig, 5)


if __name__ == "__main__":
    fig_transport()
    fig_map()
    fig_local()
    fig_loops()
    fig_assembly()
