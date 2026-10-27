"""Figures for "The Question Is the Work". Same style as "Coherence Is Measurable".
Run: python figs.py
Each figure is written twice: a vector SVG (used in the page) and a 400 dpi PNG.
Numbers in figures 2, 3 and 5 come from the cited studies; figures 1, 4 and 6 are schematics."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

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
NAVY_T, AMBER_T, GREEN_T, SAND_T, RED_T = "#e5eef5", "#fdf1dc", "#e2f0e8", "#f2efe9", "#f6e3e0"

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
        ax.text(cx, cy + 0.2 + 0.25 * n, title, ha="center", va="center", fontsize=fs, weight="bold", color=tcol, zorder=z + 3)
        ax.text(cx, cy - 0.28 + 0.03 * n, sub, ha="center", va="center", fontsize=subfs, color=scol, zorder=z + 3,
                linespacing=1.25)
    else:
        ax.text(cx, cy, title, ha="center", va="center", fontsize=fs, weight="bold", color=tcol, zorder=z + 3)


def arrow(ax, p, q, col=MUTED, lw=1.3, rad=0.0, ls="-", z=1):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=11, lw=lw, color=col,
                                 connectionstyle=f"arc3,rad={rad}", linestyle=ls, zorder=z,
                                 shrinkA=2, shrinkB=2))


def save(fig, name):
    fig.savefig(OUT + name + ".svg")
    fig.savefig(OUT + name + ".png")
    plt.close(fig)


def bar_axes(ax):
    ax.spines["left"].set_visible(False)
    ax.tick_params(left=False, labelleft=False)
    ax.axhline(0, color=MUTED, lw=0.8)


# ---------- Figure 1: the life of a problem ----------
def fig01():
    fig, ax = canvas(10, 3.3, 20, 6.6)
    stages = [("Notice", "something is\nwrong or missing"), ("Frame", "say what the\nproblem really is"),
              ("Choose", "decide it is\nworth solving"), ("Solve", "search, compute,\nprove, write"),
              ("Check", "is the answer\nright, and enough?"), ("Decide", "what it means,\nwhat to do next")]
    w, h, gap, y = 2.95, 2.0, 0.27, 2.6
    for i, (t, s) in enumerate(stages):
        x = 0.25 + i * (w + gap)
        machine = t == "Solve"
        box(ax, x, y, w, h, t, s, fill=NAVY if machine else "white", edge=NAVY if machine else RULE,
            accent=None if machine else AMBER, tcol="white" if machine else INK,
            scol="#dfe8f1" if machine else MUTED)
        if i < len(stages) - 1:
            arrow(ax, (x + w + 0.02, y + h / 2), (x + w + gap - 0.02, y + h / 2))
    # loop back
    arrow(ax, (0.25 + 5 * (w + gap) + w / 2, y - 0.05), (0.25 + w / 2, y - 0.05), col=WARM, rad=-0.12, lw=1.2, ls=(0, (4, 3)))
    ax.text(10, 0.75, "a good answer usually changes the question", ha="center", fontsize=8.6,
            color=WARM, style="italic")
    # brackets
    def bracket(x0, x1, label, col):
        yb = 5.05
        ax.plot([x0, x0, x1, x1], [yb, yb + 0.25, yb + 0.25, yb], color=col, lw=1.1)
        ax.text((x0 + x1) / 2, yb + 0.55, label, ha="center", fontsize=9, color=col, weight="bold")
    x_s = 0.25 + 3 * (w + gap)
    bracket(0.25, 0.25 + 3 * w + 2 * gap, "problem setting: people stay in charge", WARM)
    bracket(x_s, x_s + w, "machines, more and more", NAVY)
    bracket(x_s + w + gap, 0.25 + 6 * w + 5 * gap, "judgement", WARM)
    save(fig, "fig01")


# ---------- Figure 2: same tool, different people ----------
def fig02():
    fig, (a, b) = plt.subplots(1, 2, figsize=(10, 3.7), gridspec_kw={"wspace": 0.35})
    # (a) Dell'Acqua et al.: inside vs outside the frontier, change vs control
    vals = [12.2, 25.1, -19]
    labels = ["Tasks\ncompleted", "Speed", "Correct\nanswers"]
    # first two: % change; third: change in percentage points
    cols = [NAVY, NAVY, RED]
    xs = [0, 1, 2.4]
    a.bar(xs, vals, width=0.62, color=cols, edgecolor=BG, linewidth=2)
    for x, v in zip(xs, vals):
        a.text(x, v + (1.4 if v > 0 else -1.4), f"{v:+.1f}%" if v != -19 else "−19 points", ha="center",
               va="bottom" if v > 0 else "top", fontsize=9.5, weight="bold", color=INK)
    a.set_xticks(xs, labels, fontsize=8.6)
    a.set_ylim(-30, 34)
    bar_axes(a)
    a.text(0.5, 31, "inside the frontier", ha="center", fontsize=8.6, color=NAVY, weight="bold")
    a.text(2.4, 31, "outside", ha="center", fontsize=8.6, color=RED, weight="bold")
    a.axvline(1.7, color=RULE, lw=1)
    a.set_title("Consultants with AI vs without (n = 758)", fontsize=9.6, loc="left", color=INK, pad=12)
    # (b) Otis et al.: entrepreneurs, by baseline performance
    vals = [15, -10]
    b.bar([0, 1], vals, width=0.55, color=[GREEN, RED], edgecolor=BG, linewidth=2)
    b.text(0, 16.2, "over +15%", ha="center", va="bottom", fontsize=9.5, weight="bold")
    b.text(1, -11.2, "about −10%", ha="center", va="top", fontsize=9.5, weight="bold")
    b.set_xticks([0, 1], ["High performers\nbefore the study", "Low performers\nbefore the study"], fontsize=8.6)
    b.set_ylim(-20, 24); b.set_xlim(-0.7, 1.7)
    bar_axes(b)
    b.set_title("Entrepreneurs with an AI mentor (n = 640)", fontsize=9.6, loc="left", color=INK, pad=12)
    b.text(0.5, 21.5, "average effect: none detectable", ha="center", fontsize=8.4, color=MUTED, style="italic")
    save(fig, "fig02")


# ---------- Figure 5: practice vs exam ----------
def fig03():
    fig, ax = plt.subplots(figsize=(7.4, 3.8))
    groups = ["During practice\n(with AI)", "Exam\n(AI removed)"]
    base, tutor = [48, -17], [127, 0]
    xs = [0, 1.25]
    ax.bar([x - 0.2 for x in xs], base, width=0.36, color=AMBER, edgecolor=BG, linewidth=2, label="Plain chat assistant")
    ax.bar([x + 0.2 for x in xs], tutor, width=0.36, color=NAVY, edgecolor=BG, linewidth=2, label="Tutor that gives hints, not answers")
    for x, v in zip(xs, base):
        ax.text(x - 0.2, v + (3 if v >= 0 else -3), f"{v:+d}%".replace("-", "−"), ha="center", va="bottom" if v >= 0 else "top",
                fontsize=9.5, weight="bold")
    ax.text(xs[0] + 0.2, 130, "+127%", ha="center", va="bottom", fontsize=9.5, weight="bold")
    ax.text(xs[1] + 0.2, 3, "≈ 0", ha="center", va="bottom", fontsize=9.5, weight="bold")
    ax.set_xticks(xs, groups, fontsize=9)
    ax.set_ylim(-35, 150)
    bar_axes(ax)
    ax.legend(loc="upper right", fontsize=8.6)
    ax.set_title("Change in grades vs students without AI (about 1,000 high-school students)",
                 fontsize=9.6, loc="left", pad=10)
    save(fig, "fig05")


# ---------- Figure 3: delegation is rising ----------
def fig04():
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    xs, ys = [0, 1], [27, 39]
    ax.plot(xs, ys, color=NAVY, lw=2, marker="o", ms=9, mec=BG, mew=2)
    for x, y, lab in zip(xs, ys, ["late 2024", "August 2025"]):
        ax.text(x, y + 2.2, f"{y}%", ha="center", fontsize=11, weight="bold")
    ax.set_xticks(xs, ["late 2024", "August 2025"], fontsize=9)
    ax.set_xlim(-0.4, 1.4); ax.set_ylim(0, 50)
    ax.set_ylabel("share of conversations", fontsize=9, color=MUTED)
    ax.set_yticks([0, 10, 20, 30, 40, 50], [f"{t}%" for t in range(0, 60, 10)], fontsize=8.5)
    ax.grid(axis="y", color=RULE, lw=0.7); ax.set_axisbelow(True)
    ax.set_title("Conversations where the whole task is handed over", fontsize=9.6, loc="left", pad=10)
    save(fig, "fig03")


# ---------- Figure 4: supercharged vs surrendered ----------
def fig05():
    fig, ax = canvas(10, 4.6, 20, 9.2)
    def loop(x0, title, col, steps, note, ncol):
        ax.text(x0 + 4.4, 8.6, title, ha="center", fontsize=11.5, weight="bold", color=col)
        pos = [(x0 + 0.3, 5.6), (x0 + 4.8, 5.6), (x0 + 4.8, 2.4), (x0 + 0.3, 2.4)]
        for (x, y), (t, s, who) in zip(pos, steps):
            human = who == "you"
            box(ax, x, y, 3.9, 2.0, t, s, fill="white", accent=AMBER if human else NAVY, fs=9.6, subfs=8.2)
        arrow(ax, (x0 + 4.25, 6.6), (x0 + 4.75, 6.6), col=col)
        arrow(ax, (x0 + 6.75, 5.55), (x0 + 6.75, 4.45), col=col)
        arrow(ax, (x0 + 4.75, 3.4), (x0 + 4.25, 3.4), col=col)
        arrow(ax, (x0 + 2.25, 4.45), (x0 + 2.25, 5.55), col=col)
        ax.text(x0 + 4.4, 1.35, note, ha="center", fontsize=8.8, color=ncol, style="italic")
    loop(0.4, "Supercharged", GREEN,
         [("You set the question", "what matters, and why", "you"),
          ("AI explores", "options, drafts, proofs", "ai"),
          ("You judge", "test, compare, doubt", "you"),
          ("You reframe", "a sharper question", "you")],
         "each turn of the loop makes you better", GREEN)
    loop(10.4, "Surrendered", RED,
         [("A vague request", "\"do this for me\"", "you"),
          ("AI answers", "fluent and confident", "ai"),
          ("Accepted as is", "no test, no doubt", "you"),
          ("Next request", "same question, less skill", "you")],
         "each turn of the loop makes you weaker", RED)
    ax.add_patch(FancyBboxPatch((0.6, 0.1), 0.3, 0.3, boxstyle="round,pad=0,rounding_size=0.06", fc=AMBER, ec="none"))
    ax.text(1.05, 0.25, "a step done by a person", va="center", fontsize=8, color=MUTED)
    ax.add_patch(FancyBboxPatch((5.4, 0.1), 0.3, 0.3, boxstyle="round,pad=0,rounding_size=0.06", fc=NAVY, ec="none"))
    ax.text(5.85, 0.25, "a step done by AI", va="center", fontsize=8, color=MUTED)
    ax.plot([10, 10], [1.0, 8.4], color=RULE, lw=1)
    save(fig, "fig04")


# ---------- Figure 6: from information to knowledge ----------
def fig06():
    fig, ax = canvas(10, 4.5, 20, 9)
    rungs = [("Information", "a statement you have read or been given", SAND_T, MUTED),
             ("Sourced", "you know where it comes from, and how that source can fail", NAVY_T, NAVY),
             ("Tested", "you know what would show it is wrong, and you looked", NAVY_T, NAVY),
             ("Connected", "it fits, or clashes, with what else you know", GREEN_T, GREEN),
             ("Knowledge", "you can explain it, use it, and defend it without the tool", GREEN_T, GREEN)]
    for i, (t, s, fill, col) in enumerate(rungs):
        x, y = 0.4 + i * 0.8, 0.4 + i * 1.65
        w = 19.2 - 2 * i * 0.8
        box(ax, x, y, w, 1.35, "", None, fill=fill, edge=RULE, r=0.2)
        ax.text(x + 0.45, y + 0.68, t, va="center", fontsize=10.5, weight="bold", color=col)
        ax.text(x + 3.1, y + 0.68, s, va="center", fontsize=9, color=INK)
    save(fig, "fig06")


if __name__ == "__main__":
    for f in (fig01, fig02, fig03, fig04, fig05, fig06):
        f()
