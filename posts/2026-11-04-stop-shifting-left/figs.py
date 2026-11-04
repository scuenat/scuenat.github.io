"""Figures for "Stop Shifting Left". Same style as "Stop Reviewing Pull Requests".

Figures 1 and 2 are schematics of my own. Figure 3 comes from the simulation in sim.py (parameters
in Table 1 of the paper). Figure 4 plots the condition of section 3; it is a model, not a measurement.
Run `python figs.py` to redraw them and `python sim.py` to print Table 2.
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





import sim


def save(fig, n):
    fig.savefig(OUT + f"fig0{n}.png", dpi=400); fig.savefig(OUT + f"fig0{n}.svg"); plt.close(fig)


# ---------- figure 1: from a test pyramid before release to a loop behind a flag ----------
def fig_loop():
    fig, ax = canvas(11.2, 7.0, 33.0, 20.6)
    # top band: today
    ax.add_patch(FancyBboxPatch((0.3, 13.4), 32.4, 6.9, boxstyle="round,pad=0,rounding_size=0.45",
                                fc="#eef1f4", ec="none", zorder=0.5))
    heading(ax, 0.95, 19.65, "THE FIRST WORLD: SHIFT LEFT", "Test everything before anyone uses it", color=NAVY)
    y = 14.5
    steps = [("Write", None, NAVY, 4.2), ("Unit tests", None, NAVY, 4.6),
             ("Integration\nand E2E", None, AMBER, 4.9), ("QA pass", None, AMBER, 4.2),
             ("Acceptance", "in staging", AMBER, 4.6), ("Release", None, GREEN, 4.0)]
    x = 0.95
    xs = []
    for i, (t, sub, acc, w) in enumerate(steps):
        fill = AMBER_T if acc == AMBER else "white"
        card(ax, x, y, w, 2.9, t, sub, accent=acc, fill=fill, fs=10, subfs=8)
        xs.append((x, w))
        if i:
            px, pw = xs[i - 1]
            arrow(ax, (px + pw + 0.08, y + 1.45), (x - 0.08, y + 1.45), lw=1.5,
                  color=GREEN if i == len(steps) - 1 else MUTED)
        x += w + 0.75
    arrow(ax, (xs[4][0] + 1.0, y - 0.1), (xs[2][0] + 1.6, y - 0.1), color=WARM, rad=-0.35, lw=1.4)
    pill(ax, (xs[2][0] + xs[4][0]) / 2 + 2.0, y - 1.15, "each finding goes back through every stage",
         color=WARM, fs=7.4)

    # bottom band: proposed
    ax.add_patch(FancyBboxPatch((0.3, 0.3), 32.4, 11.9, boxstyle="round,pad=0,rounding_size=0.45",
                                fc=SAND_T, ec="none", zorder=0.5))
    heading(ax, 0.95, 11.55, "THE TWO WORLDS TOGETHER",
            "Learn with experts behind a flag; lock in with regression tests when done", color=WARM)
    y = 5.6
    card(ax, 0.95, y, 5.0, 2.9, "Write", "the agent", accent=NAVY, fs=10.5, subfs=8)
    card(ax, 6.95, y, 6.0, 2.9, "Unit tests", "and automatic checks", accent=NAVY, fs=10.5, subfs=8)
    card(ax, 13.95, y, 6.4, 2.9, "Production", "flag off for customers", accent=GREEN, fs=10.5, subfs=8)
    card(ax, 21.35, y, 5.6, 2.9, "Use it", "domain experts", accent=AMBER, fill=AMBER_T,
         fs=10.5, subfs=8)
    card(ax, 27.95, y + 1.7, 4.05, 2.5, "Lock in", "regression tests", accent=NAVY, fs=10, subfs=7.6)
    card(ax, 27.95, y - 1.6, 4.05, 2.5, "Flip", "for everyone", accent=GREEN, fs=10.5, subfs=7.6)
    arrow(ax, (6.03, y + 1.45), (6.87, y + 1.45), lw=1.5)
    arrow(ax, (13.03, y + 1.45), (13.87, y + 1.45), color=GREEN, lw=1.5)
    arrow(ax, (20.43, y + 1.45), (21.27, y + 1.45), lw=1.5)
    arrow(ax, (27.03, y + 2.0), (27.87, y + 2.6), color=NAVY, lw=1.5)
    arrow(ax, (29.97, y + 1.6), (29.97, y + 0.98), color=GREEN, lw=1.5)
    ax.text(27.45, y + 3.0, "done", color=NAVY, fontsize=7, ha="center", va="bottom", weight="semibold")
    # the loop
    yb = 1.0
    card(ax, 6.95, yb, 20.0, 2.4, "Findings tonight, a new version tomorrow", None, accent=WARM, fs=10.5)
    arrow(ax, (24.15, y - 0.1), (24.15, yb + 2.5), color=WARM, lw=1.6)
    arrow(ax, (9.95, yb + 2.5), (9.95, y - 0.1), color=WARM, lw=1.6)
    pill(ax, 24.15, (y + yb + 2.4) / 2, "what they found", color=WARM, fs=7.4)
    pill(ax, 9.95, (y + yb + 2.4) / 2, "every day", color=WARM, fs=7.4)
    save(fig, 1)



# ---------- figure 2: write the regression tests when the behaviour stops moving ----------
def fig_lifecycle():
    """Schematic. Where test-writing effort goes over a feature's life, in each approach."""
    fig, axes = plt.subplots(3, 1, figsize=(8.2, 7.6), sharex=True,
                             gridspec_kw=dict(height_ratios=[1.0, 1.15, 1.15], hspace=0.42))
    days = np.arange(0, 16)
    dev_end, lock_end = 7, 8
    change = np.where(days < dev_end, 0.85 * np.exp(-days / 4.0) + 0.1, 0.02)
    for ax in axes:
        ax.axvspan(-0.6, dev_end - 0.5, color=AMBER_T, zorder=0, lw=0)
        ax.axvspan(dev_end - 0.5, lock_end - 0.5, color=NAVY_T, zorder=0, lw=0)
        tidy(ax); ax.set_yticks([])
        ax.spines["left"].set_visible(False)
    a = axes[0]
    a.bar(days, change, color=WARM, width=0.62)
    a.set_title("How much of the feature's behaviour still changes each day", loc="left",
                fontsize=10, weight="semibold", color=INK)
    a.set_ylim(0, 1.15)
    a.text(1.0, 1.0, "DEVELOP, BEHIND THE FLAG", fontsize=7.2, weight="semibold", color=WARM)
    a.text(dev_end - 0.42, 1.0, "LOCK IN", fontsize=7.2, weight="semibold", color=NAVY)
    a.text(lock_end + 0.4, 1.0, "IN THE MARKET", fontsize=7.2, weight="semibold", color=GREEN)
    b = axes[1]
    sl = np.where(days < 11, 0.55, 0.12); sl[days < 2] = 0.9
    b.bar(days, sl, color=MUTED, width=0.62)
    b.set_title("Shift left: integration and E2E tests written and rewritten every cycle", loc="left",
                fontsize=10, weight="semibold", color=INK)
    b.set_ylim(0, 1.3)
    b.text(3.0, 0.72, "most of this effort tests behaviour that will change", fontsize=8.5, color=MUTED)
    c = axes[2]
    pr = np.where(days < dev_end, 0.12, 0.04); pr[dev_end] = 1.0
    cols = [WARM if d < dev_end else (NAVY if d == dev_end else GREEN) for d in days]
    c.bar(days, pr, color=cols, width=0.62)
    c.set_title("Proposed: unit tests while developing, the regression suite once", loc="left",
                fontsize=10, weight="semibold", color=INK)
    c.set_ylim(0, 1.3)
    c.annotate("generated from the accepted\nbehaviour, then automated", (dev_end, 1.0), xytext=(14, -4),
               textcoords="offset points", fontsize=8.5, color=NAVY, va="top")
    c.text(lock_end + 2.4, 0.2, "runs on every build, guards against regressions", fontsize=8.5, color=GREEN)
    c.text(0.0, 0.2, "unit tests with each change", fontsize=8.5, color=WARM)
    c.set_xticks([0, 7, 15]); c.set_xticklabels(["first version", "accepted", "later"])
    c.set_xlim(-0.6, 15.6)
    fig.text(0.075, 0.5, "test-writing effort  →", rotation=90, va="center", ha="center", fontsize=9, color=MUTED)
    save(fig, 2)

# ---------- figure 3: the frontier ----------
def frontier(policy, s, runs=3000, seed=11):
    rng = np.random.default_rng(seed)
    pts = []
    for cd in (1, 2, 3, 4, 5):
        rs = [sim.run(policy, rng, dict(sim.P, s=s, clean_days=cd)) for _ in range(runs)]
        pts.append((float(np.mean([r["days"] for r in rs])), float(np.mean([r["escaped"] for r in rs]))))
    return pts


def fig_frontier():
    fig, axes = plt.subplots(2, 1, figsize=(7.4, 8.6), sharex=True)
    lines = [("shift_left", "Shift left", MUTED, (0, (4, 3))),
             ("suite_and_flag", "Full suite + flag", NAVY, "-"),
             ("proposed", "Unit tests + flag", WARM, (0, (2, 2))),
             ("lock_in", "Two worlds: flag, then lock-in", WARM, "-")]
    data = {}
    for ax, s, title in zip(axes, (1.0, 0.25), ("Suite costs a day per cycle", "Suite costs two hours per cycle")):
        for pol, lab, col, ls in lines:
            pts = frontier(pol, s)
            data[f"{pol}_s{s}"] = pts
            xs, ys = zip(*pts)
            ax.plot(xs, ys, color=col, lw=2.4, ls=ls, marker="o", ms=5.5, mfc="white", mew=1.6,
                    label=lab, zorder=3)
        ax.set_title(title, fontsize=10.5, weight="semibold", loc="left", color=INK)
        ax.set_ylabel("Defects left for customers")
        ax.set_yscale("log"); ax.set_ylim(0.03, 2.5); ax.set_xlim(3, 24)
        ax.set_yticks([0.05, 0.1, 0.2, 0.5, 1, 2]); ax.set_yticklabels(["0.05", "0.1", "0.2", "0.5", "1", "2"])
        tidy(ax, "both")
    axes[1].set_xlabel("Days until the flag is flipped for everyone")
    axes[0].legend(loc="upper right", fontsize=9)
    axes[1].text(23.5, 1.9, "lower left is better", ha="right", fontsize=9, color=MUTED)
    fig.tight_layout(h_pad=2.2)
    save(fig, 3)
    return data


# ---------- figure 4: when does the engineering-side suite pay? ----------
def fig_threshold():
    """Largest extra cost per cycle for which the suite still speeds learning, in working hours
    (one cycle = one working day = 8 h): s* = ln(1 - e*phi) / ln(1 - q), with e = 0.6."""
    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    phi = np.linspace(0.0, 0.95, 300)
    hi = sim.threshold(phi, q=0.4) * 8
    lo = sim.threshold(phi, q=0.6) * 8
    top = 8
    ax.fill_between(phi, 0, lo, color=NAVY_T, zorder=0)
    ax.fill_between(phi, np.minimum(hi, top), top, color=AMBER_T, zorder=0)
    ax.plot(phi, hi, color=NAVY, lw=2.2, ls=(0, (4, 3)))
    ax.plot(phi, lo, color=NAVY, lw=2.2)
    ax.text(0.685, 7.75, "if experts find 40%\nof what remains each day", ha="left", va="top",
            fontsize=8.5, color=NAVY, linespacing=1.2)
    ax.text(0.80, 4.9, "if they find 60%", ha="left", va="top", fontsize=8.5, color=NAVY)
    ax.text(0.62, 0.6, "the suite pays", color=NAVY, fontsize=12, weight="semibold")
    ax.text(0.04, 6.6, "the suite costs more\nthan it saves", color=WARM, fontsize=12, weight="semibold",
            va="center")
    for sh, lab in ((8, "Figure 3: one day"), (2, "two hours")):
        ax.scatter([0.5], [sh], s=90, color=WARM, edgecolor="white", lw=1.5, zorder=5, clip_on=False)
        ax.annotate(lab, (0.5, sh), xytext=(9 if sh < 8 else -10, -2 if sh < 8 else -12), textcoords="offset points",
                    fontsize=8.5, color=WARM, weight="semibold", va="center", ha="left" if sh < 8 else "right")
    ax.set_xlim(0, 1); ax.set_ylim(0, top)
    ax.set_yticks([0, 2, 4, 6, 8]); ax.set_yticklabels(["0", "2 h", "4 h", "6 h", "8 h"])
    ax.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0]); ax.set_xticklabels(["0%", "20%", "40%", "60%", "80%", "100%"])
    ax.set_xlabel("Share of defects that are implementation defects, φ")
    ax.set_ylabel("Extra cost of the suite per cycle")
    tidy(ax)
    save(fig, 4)


if __name__ == "__main__":
    fig_loop()
    fig_lifecycle()
    fig_frontier()
    fig_threshold()
