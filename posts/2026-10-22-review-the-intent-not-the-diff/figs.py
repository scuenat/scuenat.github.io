"""Figures for "Review the Intent, Not the Diff". Same style as "Intent Is the Source".

All three figures are schematics of my own. Figure 2 summarises the review setup described
by the Claude Code team at Anthropic; it is my drawing, not theirs.
"""
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
    "savefig.dpi": 220, "savefig.bbox": "tight", "savefig.pad_inches": 0.18,
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
        parts.append((eyebrow if any(c.isdigit() for c in eyebrow) else eyebrow.upper(), dict(fontsize=6.6, weight="semibold",
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


def tidy(ax, grid_axis="y"):
    ax.grid(axis=grid_axis, color=RULE, lw=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(length=0, labelsize=8.5)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(RULE if s == "left" else MUTED)




def person(ax, x, y, s=1.0, color=AMBER, z=7):
    """A small person glyph: a head over rounded shoulders, centred at (x, y)."""
    ax.add_patch(Circle((x, y + 0.32 * s), 0.2 * s, fc=color, ec="none", zorder=z))
    ax.add_patch(FancyBboxPatch((x - 0.32 * s, y - 0.42 * s), 0.64 * s, 0.5 * s,
                                boxstyle=f"round,pad=0,rounding_size={0.22 * s}",
                                fc=color, ec="none", zorder=z))


def mini_pr(ax, x, y, w=1.75, h=0.95, z=4, label="PR"):
    """A small pull-request card: a title chip and two grey lines."""
    shadow(ax, x, y, w, h, r=0.14, z=z)
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.14",
                                fc="white", ec=RULE, lw=0.8, zorder=z + 1))
    ax.text(x + 0.18, y + h - 0.26, label, fontsize=5.6, fontfamily=MONO, color=NAVY,
            va="center", weight="semibold", zorder=z + 2)
    for k, frac in enumerate((0.78, 0.55)):
        ax.add_patch(FancyBboxPatch((x + 0.18, y + 0.2 + k * 0.2), (w - 0.36) * frac, 0.07,
                                    boxstyle="round,pad=0,rounding_size=0.03",
                                    fc="#d5dbe1", ec="none", zorder=z + 2))


def fig_bottleneck():
    """Writing used to be the slow step. With agents, the queue forms in front of review."""
    fig, ax = canvas(11.2, 5.3, 31.0, 14.6)
    rows = [  # y, eyebrow, title, write width, write label, bottleneck on write?
        (8.6, "BEFORE", "People write every line", 13.6, "days of typing", True),
        (1.4, "WITH AGENTS", "Code arrives faster than anyone reads it", 3.4, "minutes", False),
    ]
    for y, eb, title, ww, wsub, slow_write in rows:
        heading(ax, 0.3, y + 4.75, eb, title, color=WARM if not slow_write else NAVY)
        card(ax, 0.3, y, ww, 2.9, "Write", wsub, accent=AMBER if slow_write else NAVY,
             fill=AMBER_T if slow_write else "white",
             eyebrow="bottleneck" if slow_write else "agent", fs=10.5, subfs=8.2)
        card(ax, 18.4, y, 6.6, 2.9, "Review", "a person reads\nthe diff",
             accent=NAVY if slow_write else AMBER, fill="white" if slow_write else AMBER_T,
             eyebrow="a person" if slow_write else "bottleneck", fs=10.5, subfs=8.2)
        card(ax, 26.7, y, 4.0, 2.9, "Merge", None, accent=GREEN, fs=10.5)
        arrow(ax, (25.1, y + 1.45), (26.6, y + 1.45), color=GREEN, lw=1.5)
        if slow_write:
            arrow(ax, (0.3 + ww + 0.1, y + 1.45), (18.3, y + 1.45), color=MUTED, lw=1.5)
            pill(ax, 16.0, y + 1.45, "one PR at a time", fs=7.4)
        else:
            arrow(ax, (3.8, y + 1.45), (4.7, y + 1.45), color=MUTED, lw=1.5)
            # the pile of PRs waiting for a reader
            rng = np.random.default_rng(7)
            n = 0
            for c in range(6):
                for r in range(3 if c < 4 else 2 if c < 5 else 1):
                    jx, jy = rng.uniform(-0.12, 0.12, 2)
                    mini_pr(ax, 5.0 + c * 2.1 + jx, y + 0.05 + r * 1.15 + jy, z=3 + r,
                            label=f"PR #{412 + n}")
                    n += 1
            arrow(ax, (17.4, y + 1.45), (18.3, y + 1.45), color=MUTED, lw=1.5)
            ax.annotate("waiting for a reader", (11.0, y - 0.75), ha="center", fontsize=7.8,
                        color=WARM, weight="medium")
    fig.savefig(OUT + "fig01.png"); plt.close(fig)


def fig_layers():
    """Six layers of checks over fast rollback, with human approval set by a risk classifier."""
    fig, ax = canvas(11.2, 6.6, 33.0, 19.4)
    layers = [
        ("Verification", "the agent proves its work: tests, build, screenshot", "machine", NAVY),
        ("Required CI", "the same checks on every change, no exceptions", "machine", NAVY),
        ("AI review", "a reviewer agent with fresh context, rounds capped", "machine", NAVY),
        ("Security review", "a dedicated pass; open findings block the merge", "blocking", NAVY),
        ("Human approval", "zero, one or two people, set by risk", "people", AMBER),
        ("Merge queue + flags", "merge in order, switch off without a revert", "release", GREEN),
    ]
    x0, w, h, gap, top = 2.0, 16.3, 2.3, 0.3, 15.9
    ax.text(0.3, 18.9, "SIX LAYERS OF CHECKS", fontsize=7.4, weight="semibold", color=NAVY)
    for i, (name, sub, kind, col) in enumerate(layers):
        y = top - i * (h + gap)
        hot = kind == "people"
        card(ax, x0, y, w, h, name, sub, accent=col, eyebrow=f"Layer {i + 1}  ·  {kind}",
             fill=AMBER_T if hot else "white", align="left", fs=9.8, subfs=7.8)
    yr = top - 6 * (h + gap) + 0.15
    card(ax, x0, yr, w, 1.75, "Fast rollback", "underneath everything: any change can be undone quickly",
         fill=NAVY, align="left", fs=9.8, subfs=7.8)
    # a change falls through the stack
    arrow(ax, (1.1, top + h), (1.1, yr + 0.3), color=MUTED, lw=1.4, ls=(0, (4, 3)))
    ax.text(0.45, (top + h + yr) / 2, "a change falls through every layer", rotation=90, fontsize=7.4,
            color=MUTED, va="center", ha="center", style="italic")

    # right: who must approve
    rx, rw = 21.1, 11.6
    ax.text(rx, 18.9, "WHO MUST APPROVE", fontsize=7.4, weight="semibold", color=WARM)
    card(ax, rx, 14.6, rw, 3.2, "Risk classifier", "reads the change, not the author",
         fill=NAVY, eyebrow="per change", fs=10, subfs=8)
    tiers = [("Low risk", "merges if automated review passes", 0, GREEN),
             ("Medium risk", "one person approves", 1, AMBER),
             ("High risk", "two people approve", 2, RED)]
    for i, (name, sub, n, col) in enumerate(tiers):
        y = 10.9 - i * 3.0
        card(ax, rx, y, rw, 2.45, name, sub, accent=col, align="left", fs=9.6, subfs=7.8)
        for k in range(n):
            person(ax, rx + rw - 0.9 - k * 0.95, y + 1.2, s=1.05, color=col)
        if n == 0:
            ax.text(rx + rw - 0.9, y + 1.22, "no human", fontsize=6.8, color=GREEN,
                    ha="right", va="center", weight="semibold", zorder=7)
        arrow(ax, (rx + 0.85, 14.5), (rx + 0.85, y + 2.55) if i == 0 else (rx + 0.85, y + 1.22),
              color="#b9c3cc", lw=1.1, z=1)
    # the tiers set layer 5
    y5 = top - 4 * (h + gap) + h / 2
    arrow(ax, (rx - 0.15, 9.1), (x0 + w + 0.15, y5), color=WARM, lw=1.4, ls=(0, (4, 3)), rad=-0.15)
    ax.text(rx, 3.3, "Whoever prompted the change owns it\nand is a required reviewer.",
            fontsize=9, color=INK, weight="semibold", va="top", linespacing=1.35)
    ax.text(rx, 1.3, "An agent's approval never replaces a human one.", fontsize=8.4, color=MUTED, va="top")
    fig.savefig(OUT + "fig02.png"); plt.close(fig)


def fig_intent():
    """Humans own the intent, agents own the implementation, review checks one against the other."""
    fig, ax = canvas(11.2, 6.2, 33.0, 18.2)
    # bands
    for y, hgt, fill in ((10.4, 7.4, SAND_T), (0.3, 6.1, "#eef1f4")):
        ax.add_patch(FancyBboxPatch((0.3, y), 30.4, hgt, boxstyle="round,pad=0,rounding_size=0.45",
                                    fc=fill, ec="none", zorder=0.5))
    heading(ax, 0.95, 17.05, "INTENT  ·  owned by people",
            "Short enough to hold in your head, explicit enough to enforce", color=WARM)
    items = [("Decisions", "why it is built this way", "short decision records"),
             ("Contracts", "what each part promises", "typed interfaces, tests"),
             ("Invariants", "what must always hold", "properties, assertions"),
             ("Conventions", "how we do things here", "agent instructions, linters")]
    cw, cg = 6.85, 0.45
    for i, (t, s_, home) in enumerate(items):
        x = 0.95 + i * (cw + cg)
        card(ax, x, 11.0, cw, 3.9, t, s_ + "\n\nlives in", accent=AMBER, fs=10.3, subfs=7.8)
        chip(ax, x + cw / 2 + 0.12, 11.75, home, color=WARM, fill=AMBER_T, fs=6.9)

    heading(ax, 0.95, 5.75, "IMPLEMENTATION  ·  owned by agents",
            "Large, fast-changing, read on demand", color=NAVY)
    rng = np.random.default_rng(3)
    fw, fg = 4.6, 0.36
    for i in range(6):
        x = 0.95 + i * (fw + fg)
        shadow(ax, x, 0.75, fw, 3.35, r=0.2, z=1)
        ax.add_patch(FancyBboxPatch((x, 0.75), fw, 3.35, boxstyle="round,pad=0,rounding_size=0.2",
                                    fc="white", ec=RULE, lw=0.8, zorder=2))
        ax.text(x + 0.25, 3.78, ["router.py", "approve.py", "rules.ts", "store.go", "api.ts", "jobs.py"][i],
                fontsize=6.2, fontfamily=MONO, color=MUTED, va="center", zorder=3)
        for k in range(8):
            ind = rng.choice([0, 0, 0.35, 0.7])
            ln = rng.uniform(0.35, 0.95) * (fw - 0.6 - ind)
            ax.add_patch(FancyBboxPatch((x + 0.25 + ind, 3.25 - k * 0.3), ln, 0.09,
                                        boxstyle="round,pad=0,rounding_size=0.04",
                                        fc=NAVY if rng.random() < 0.18 else "#d5dbe1",
                                        ec="none", alpha=0.55, zorder=3))
    # between the bands: agents follow, review enforces
    arrow(ax, (8.0, 10.25), (8.0, 6.55), color=NAVY, lw=1.6)
    pill(ax, 8.0, 8.4, "agents follow it", color=NAVY, fs=7.6)
    arrow(ax, (22.6, 6.55), (22.6, 10.25), color=AMBER, lw=1.6)
    pill(ax, 22.6, 8.4, "review checks the diff against it", color=WARM, fs=7.6)
    ax.text(15.3, 8.4, "a change to the intent\nalways goes to a person", ha="center", va="center",
            fontsize=8.2, color=INK, weight="semibold", linespacing=1.35)
    # abstractions leak: in an incident someone goes deep
    arrow(ax, (31.9, 16.6), (31.9, 1.2), color=RED, lw=1.4, ls=(0, (4, 3)))
    ax.text(32.45, 8.9, "incident: someone goes deep", rotation=-90, fontsize=9, color=RED,
            va="center", ha="center", weight="medium")
    fig.savefig(OUT + "fig03.png"); plt.close(fig)


if __name__ == "__main__":
    import os
    os.makedirs(OUT, exist_ok=True)
    fig_bottleneck(); fig_layers(); fig_intent()
