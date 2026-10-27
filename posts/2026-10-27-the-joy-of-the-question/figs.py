"""Figures for "The Joy of the Question". Same style as "Coherence Is Measurable".
Run: python figs.py
Each figure is written twice: a vector SVG (used in the page) and a 400 dpi PNG.
Numbers in figures 3 and 5 come from the cited studies; figures 1, 2, 4 and 6 are schematics."""
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



# ---------- Figure 1: how, which, why ----------
def fig01():
    fig, ax = canvas(10, 4.6, 20, 9.2)
    cx, cy = 4.6, 4.6
    for r, fc, ec in ((4.3, GREEN_T, GREEN), (3.0, AMBER_T, WARM), (1.6, NAVY, NAVY)):
        ax.add_patch(Circle((cx, cy), r, fc=fc, ec=ec, lw=1.1, zorder=2))
    ax.text(cx, cy + 0.25, "HOW", ha="center", va="center", fontsize=13, weight="bold", color="white", zorder=3)
    ax.text(cx, cy - 0.4, "solve", ha="center", va="center", fontsize=9.5, color="#dfe8f1", zorder=3)
    ax.text(cx, cy + 2.3, "WHICH", ha="center", va="center", fontsize=11.5, weight="bold", color=WARM, zorder=3)
    ax.text(cx, cy + 3.65, "WHY", ha="center", va="center", fontsize=11.5, weight="bold", color=GREEN, zorder=3)
    rows = [(cy + 3.6, GREEN, "Why does it matter to us?",
             "Care, motivation, meaning. The reason to start,\nand the joy of the climb. No machine needs it."),
            (cy + 0.75, WARM, "Which problem, and what counts as good?",
             "Noticing, framing, choosing, checking.\nCreativity, imagination and judgement."),
            (cy - 2.4, NAVY, "How do we solve it?",
             "Search, compute, prove, write.\nMachines do more of it, faster every year.")]
    anchors = [(cx + 3.65 * np.cos(np.deg2rad(32)), cy + 3.65 * np.sin(np.deg2rad(32))),
               (cx + 2.3 * np.cos(np.deg2rad(12)), cy + 2.3 * np.sin(np.deg2rad(12))),
               (cx + 1.0 * np.cos(np.deg2rad(-35)), cy + 1.0 * np.sin(np.deg2rad(-35)))]
    for (y, col, t, s), (ax0, ay0) in zip(rows, anchors):
        lc = "white" if col == NAVY else col
        ax.plot([ax0, 10.4], [ay0, y], color=col, lw=0.9, zorder=5)
        ax.add_patch(Circle((ax0, ay0), 0.1, fc=lc, ec=col, lw=1, zorder=6))
        ax.text(10.6, y + 0.2, t, va="bottom", fontsize=10.5, weight="bold", color=col)
        ax.text(10.6, y + 0.05, s, va="top", fontsize=8.8, color=INK, linespacing=1.35)
    save(fig, "fig01")


# ---------- Figure 2: losing work, gaining height ----------
def fig02():
    fig, ax = plt.subplots(figsize=(10, 4.6))
    years = np.array([1950, 1975, 1997, 2016, 2023, 2030])
    machine = np.array([0.6, 1.6, 2.6, 3.6, 4.6, 4.6])
    human = machine + 1.6
    ax.fill_between([1945, 1975], 0, 0.6, step=None, color=NAVY_T)
    ax.step(np.r_[1945, years], np.r_[0.6, machine], where="post", color=NAVY, lw=2)
    ax.fill_between(np.r_[1945, years], 0, np.r_[0.6, machine], step="post", color=NAVY_T, zorder=0)
    ax.step(np.r_[1945, years], np.r_[2.2, human], where="post", color=WARM, lw=2, ls=(0, (5, 3)))
    labels = [(1950, "arithmetic"), (1975, "calculation"), (1997, "chess moves"),
              (2016, "Go moves"), (2023, "code, essays,\nproofs")]
    for (x, t), m in zip(labels, machine):
        ax.text(x + 1, m - 0.18, t, va="top", fontsize=8.6, color=NAVY)
    ax.text(1947, 7.1, "what people choose to learn and attempt", fontsize=9.5, color=WARM, weight="bold")
    ax.text(1947, 6.6, "rises when we keep climbing", fontsize=8.8, color=WARM, style="italic")
    ax.text(2008, 0.35, "work handed to machines", fontsize=9.5, color=NAVY, weight="bold", ha="center")
    notes = [(1997, 4.6, "After strong chess engines, the quality\nof human play rose (Strittmatter 2020)"),
             (2016, 6.1, "After AlphaGo, professionals played\nbetter and more novel moves (Shin 2023)")]
    for x, y, t in notes:
        ax.annotate(t, xy=(x + 0.5, y - 0.95), xytext=(x - 17 if x == 1997 else x - 15, y + 0.9),
                    fontsize=8.4, color=INK, linespacing=1.3,
                    arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    ax.set_xlim(1945, 2030); ax.set_ylim(0, 8.2)
    ax.set_xticks([1950, 1975, 1997, 2016, 2023], ["1950", "1975", "1997", "2016", "2023"], fontsize=8.6)
    ax.spines["left"].set_visible(False); ax.tick_params(left=False, labelleft=False)
    save(fig, "fig02")


# ---------- Figure 3: same tool, different people ----------
def fig03():
    rows = [("Consultants, tasks AI does well", "more tasks completed", 12.2, "+12.2%", NAVY),
            ("", "faster", 25.1, "+25.1%", NAVY),
            ("Consultants, a task just beyond AI", "correct answers", -19, "−19 points", RED),
            ("Entrepreneurs, strong before the study", "business performance", 15, "over +15%", GREEN),
            ("Entrepreneurs, weak before the study", "business performance", -10, "about −10%", RED)]
    fig, ax = plt.subplots(figsize=(10, 4.2))
    ys = [5.9, 5.2, 3.8, 2.3, 0.9]
    for (grp, what, v, lab, col), y in zip(rows, ys):
        ax.barh(y, v, height=0.5, color=col, edgecolor=BG, linewidth=2)
        ax.text(v + (0.8 if v > 0 else -0.8), y, lab, va="center", ha="left" if v > 0 else "right",
                fontsize=9.5, weight="bold")
        ax.text(-62, y, what, va="center", ha="left", fontsize=8.8, color=MUTED)
        if grp:
            ax.text(-62, y + 0.42, grp, va="bottom", ha="left", fontsize=9.4, color=INK, weight="bold")
    ax.axvline(0, color=MUTED, lw=0.8)
    ax.axhline(3.15, color=RULE, lw=1)
    ax.text(-62, 7.05, "With AI, compared with similar people without it", fontsize=9.8, color=INK)
    ax.set_xlim(-62, 34); ax.set_ylim(0.4, 7.4)
    ax.axis("off")
    save(fig, "fig03")


# ---------- Figure 4: supercharged vs surrendered ----------
def fig04():
    fig, ax = canvas(10, 5.4, 20, 10.8)
    def loop(cx, title, col, steps, note):
        cy, R = 5.0, 2.9
        ax.add_patch(Circle((cx, cy), R, fc="none", ec=col, lw=1.4, ls=(0, (2, 3)), zorder=1, alpha=0.7))
        for ang in (45, -45, -135, 135):
            a = np.deg2rad(ang)
            p = (cx + R * np.cos(a), cy + R * np.sin(a))
            t = np.deg2rad(ang - 90)
            ax.add_patch(FancyArrowPatch((p[0] - 0.05 * np.cos(t), p[1] - 0.05 * np.sin(t)),
                                         (p[0] + 0.05 * np.cos(t), p[1] + 0.05 * np.sin(t)),
                                         arrowstyle="-|>", mutation_scale=13, color=col, lw=0, zorder=2))
        pos = [(cx, cy + R), (cx + R, cy), (cx, cy - R), (cx - R, cy)]
        for (x, y), (t, s, who) in zip(pos, steps):
            box(ax, x - 1.8, y - 0.7, 3.6, 1.4, t, s, fill="white",
                accent=AMBER if who == "you" else NAVY, fs=9.4, subfs=7.9)
        ax.text(cx, cy + R + 1.25, title, ha="center", va="center", fontsize=12.5, weight="bold", color=col)
        ax.text(cx, cy - R - 1.15, note, ha="center", va="center", fontsize=9, color=col, style="italic")
    loop(5.0, "Supercharged", GREEN,
         [("You ask", "what matters, and why", "you"),
          ("AI explores", "options, drafts, proofs", "ai"),
          ("You judge", "test, compare, doubt", "you"),
          ("You reframe", "a sharper question", "you")],
         "each turn, you grow")
    loop(15.0, "Surrendered", RED,
         [("A vague request", "\"do this for me\"", "you"),
          ("AI answers", "fluent and confident", "ai"),
          ("Accepted as is", "no test, no doubt", "you"),
          ("Next request", "no sharper than the last", "you")],
         "each turn, you shrink")
    for x, col, t in ((6.3, AMBER, "a step done by a person"), (10.6, NAVY, "a step done by AI")):
        ax.add_patch(FancyBboxPatch((x, -0.05), 0.3, 0.3, boxstyle="round,pad=0,rounding_size=0.06", fc=col, ec="none"))
        ax.text(x + 0.45, 0.1, t, va="center", fontsize=8, color=MUTED)
    save(fig, "fig04")

# ---------- Figure 5: practice vs exam ----------
def fig05():
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



# ---------- Figure 6: from information to knowledge ----------
def fig06():
    fig, ax = canvas(10, 4.4, 20, 8.8)
    rungs = [("Information", "a statement you have\nread or been given", MUTED, SAND_T),
             ("Sourced", "you know where it comes\nfrom, and how it can fail", NAVY, NAVY_T),
             ("Tested", "you know what would show\nit is wrong, and you looked", NAVY, NAVY_T),
             ("Connected", "it fits, or clashes, with\nwhat else you know", GREEN, GREEN_T),
             ("Knowledge", "you can explain, use and\ndefend it without the tool", GREEN, GREEN_T)]
    w, h = 3.75, 1.9
    for i, (t, s, col, fill) in enumerate(rungs):
        x, y = 0.35 + i * 3.9, 0.35 + i * 1.3
        ax.add_patch(FancyBboxPatch((x, 0.35), w, y - 0.35 + h, boxstyle="round,pad=0,rounding_size=0.2",
                                    fc=fill, ec=RULE, lw=0.9, zorder=2))
        ax.add_patch(FancyBboxPatch((x, y + h - 0.12), w, 0.12, boxstyle="round,pad=0,rounding_size=0.05",
                                    fc=col, ec="none", zorder=3))
        ax.text(x + 0.3, y + h - 0.45, t, fontsize=10.5, weight="bold", color=col, va="center", zorder=4)
        ax.text(x + 0.3, y + h - 0.85, s, fontsize=7.9, color=INK, va="top", linespacing=1.3, zorder=4)
    arrow(ax, (0.6, 7.3), (6.0, 7.3), col=WARM, lw=1.2)
    ax.text(0.6, 7.65, "the work only a person can finish", fontsize=9, color=WARM, style="italic")
    save(fig, "fig06")


if __name__ == "__main__":
    for f in (fig01, fig02, fig03, fig04, fig05, fig06):
        f()
