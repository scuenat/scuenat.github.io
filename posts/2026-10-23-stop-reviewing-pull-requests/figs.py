"""Figures for "Stop Reviewing Pull Requests". Same style as "Intent Is the Source".

Figures 1 and 2 are schematics of my own. Figure 3 plots the break-even condition of the
cost model in section 3; its three positions are illustrative, not measured. Figures 4 and 5 are a
small Monte Carlo simulation with the parameters in P (Table 2 of the paper); running this
file prints the numbers used in Table 3.
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




# ---------- figure 1: from a gate on every change to a loop over the system ----------
def fig_gate_to_loop():
    """Today a person approves each change. Proposed: rules travel with every session,
    changes merge on green, and a daily audit of the whole codebase steers the team."""
    fig, ax = canvas(11.2, 6.9, 33.0, 20.4)
    # top band: today
    ax.add_patch(FancyBboxPatch((0.3, 13.9), 32.4, 6.2, boxstyle="round,pad=0,rounding_size=0.45",
                                fc="#eef1f4", ec="none", zorder=0.5))
    heading(ax, 0.95, 19.45, "TODAY  ·  control on every change", "A person approves each pull request",
            color=NAVY)
    y = 14.6
    card(ax, 0.95, y, 6.2, 3.3, "Session", "a developer and\nan agent write", accent=NAVY,
         eyebrow="write", fs=10, subfs=7.9)
    card(ax, 8.4, y, 5.6, 3.3, "Checks", "tests, CI,\nAI review", accent=NAVY, eyebrow="machine",
         fs=10, subfs=7.9)
    for k in range(4):
        mini_pr(ax, 15.15 + k * 0.32, y + 0.5 + k * 0.32, w=2.6, h=1.6, z=3 + k, label=f"PR #{731 + k}")
    card(ax, 19.9, y, 6.4, 3.3, "Human gate", "a person reads\nand approves", accent=AMBER,
         fill=AMBER_T, eyebrow="every change", fs=10, subfs=7.9)
    person(ax, 25.5, y + 2.55, s=0.8, color=AMBER)
    card(ax, 27.6, y, 4.4, 3.3, "Merge", None, accent=GREEN, fs=10)
    arrow(ax, (7.25, y + 1.65), (8.3, y + 1.65), lw=1.5)
    arrow(ax, (14.1, y + 1.65), (15.0, y + 1.65), lw=1.5)
    arrow(ax, (18.95, y + 1.65), (19.8, y + 1.65), lw=1.5)
    arrow(ax, (26.4, y + 1.65), (27.5, y + 1.65), color=GREEN, lw=1.5)
    ax.annotate("queue", (17.2, y - 0.45), ha="center", fontsize=7.6, color=WARM, weight="medium")

    # bottom band: proposed
    ax.add_patch(FancyBboxPatch((0.3, 0.3), 32.4, 12.9, boxstyle="round,pad=0,rounding_size=0.45",
                                fc=SAND_T, ec="none", zorder=0.5))
    heading(ax, 0.95, 12.55, "PROPOSED  ·  control on the system",
            "Rules travel with every session; a daily audit steers the team", color=WARM)
    y = 6.75
    card(ax, 0.95, y, 9.4, 3.9, None, None, accent=NAVY, fs=10)
    ax.text(5.77, y + 3.3, "WRITE", fontsize=6.6, weight="semibold", color=NAVY, ha="center", va="center", zorder=6)
    ax.text(5.77, y + 2.65, "Session with a contract", fontsize=10, weight="semibold", color=INK,
            ha="center", va="center", zorder=6)
    rules = ["adds tests", "diff coverage ≥ 80%", "no test weakened", "conventions file"]
    for i, r_ in enumerate(rules):
        chip(ax, 3.55 + (i % 2) * 4.45, y + 1.55 - (i // 2) * 0.85, r_, fs=6.6)
    card(ax, 11.6, y, 5.6, 3.9, "Checks", "the same, and\nnow blocking", accent=NAVY,
         eyebrow="machine", fs=10, subfs=7.9)
    card(ax, 18.5, y, 4.6, 3.9, "Merge", "on green", accent=GREEN, fs=10, subfs=7.9)
    card(ax, 24.4, y, 7.6, 3.9, "Main", "flags and fast\nrollback", fill=NAVY, eyebrow="production",
         fs=10, subfs=7.9)
    arrow(ax, (10.45, y + 1.95), (11.5, y + 1.95), lw=1.5)
    arrow(ax, (17.3, y + 1.95), (18.4, y + 1.95), color=GREEN, lw=1.5)
    arrow(ax, (23.2, y + 1.95), (24.3, y + 1.95), color=GREEN, lw=1.5)
    pill(ax, 17.85, y - 0.6, "no person waits here", color=GREEN, fs=7.2)

    # the loop: daily audit -> report -> team -> session rules
    yb = 1.0
    card(ax, 24.4, yb, 7.6, 3.9, "Daily audit", "reads the whole\ncodebase, not a diff", accent=AMBER,
         eyebrow="scheduled job", fs=10, subfs=7.9)
    card(ax, 12.4, yb, 9.6, 3.9, "Report", "coverage and mutation trend,\nweakened tests, drift, hotspots",
         accent=AMBER, fill=AMBER_T, eyebrow="what to improve", fs=10, subfs=7.7)
    card(ax, 0.95, yb, 9.0, 3.9, "Team", "decides what to fix\nand tightens the rules", accent=AMBER,
         eyebrow="people", fs=10, subfs=7.9)
    for k in range(3):
        person(ax, 8.35 - k * 0.8, yb + 3.05, s=0.62, color=AMBER)
    arrow(ax, (28.2, y - 0.1), (28.2, yb + 4.0), color=WARM, lw=1.5)
    arrow(ax, (24.3, yb + 1.95), (22.1, yb + 1.95), color=WARM, lw=1.5)
    arrow(ax, (12.3, yb + 1.95), (10.05, yb + 1.95), color=WARM, lw=1.5)
    arrow(ax, (5.45, yb + 4.0), (5.45, y - 0.1), color=WARM, lw=1.5)
    pill(ax, 5.45, (yb + 4.0 + y) / 2, "rules", color=WARM, fs=7.2)
    pill(ax, 28.2, (yb + 4.0 + y) / 2, "every night", color=WARM, fs=7.2)
    fig.savefig(OUT + "fig01.png"); plt.close(fig)


# ---------- figure 2: the cost of a late fix ----------
def fig_cost_curve():
    """Schematic. The relative cost of fixing a defect against when it is found."""
    fig, ax = plt.subplots(figsize=(9.6, 4.9))
    stages = ["while\nwriting", "at\nreview", "next day\n(audit)", "after\na week", "in production,\nmonths later"]
    x = np.arange(len(stages))
    curves = [
        ("Steep curve, as usually cited (Boehm, 1981)", [1, 3, 10, 30, 100], MUTED, (0, (4, 3))),
        ("Flattened by practice (Beck, 1999)", [1, 1.6, 2.4, 3.5, 6], NAVY, "-"),
        ("Agentic session, fast rollback (assumed)", [1, 1.15, 1.3, 1.6, 2.4], GREEN, "-"),
    ]
    for name, ys, col, ls in curves:
        ax.plot(x, ys, color=col, lw=2.2, ls=ls, marker="o", ms=5, mfc="white", mew=1.6, zorder=3)
        ax.text(x[-1] + 0.12, ys[-1], name, color=col, va="center", fontsize=8.4, weight="semibold")
    # irreversible harm does not flatten
    ax.plot(x[2:], [40, 55, 75], color=RED, lw=2.2, marker="s", ms=5, mfc="white", mew=1.6, zorder=3)
    ax.text(1.9, 52, "Irreversible harm: data loss, breach", color=RED,
            va="center", ha="right", fontsize=8.4, weight="semibold")
    ax.annotate("", xy=(1, 1.15), xytext=(1, 3), arrowprops=dict(arrowstyle="-|>", color=WARM, lw=1.3))
    ax.text(1.1, 0.97, "what a gate used to save", color=WARM, fontsize=7.8, va="center")
    ax.set_yscale("log")
    ax.set_ylim(0.8, 200)
    ax.set_yticks([1, 3, 10, 30, 100]); ax.set_yticklabels(["1×", "3×", "10×", "30×", "100×"])
    ax.set_xticks(x); ax.set_xticklabels(stages)
    ax.set_xlim(-0.3, len(stages) + 1.9)
    ax.set_ylabel("Relative cost to fix")
    ax.set_xlabel("When the defect is found")
    tidy(ax)
    fig.savefig(OUT + "fig02.png"); plt.close(fig)


# ---------- figure 3: the break-even map ----------
def fig_break_even():
    """Review pays when p * d * dC > r. Positions are illustrative, not measured."""
    fig, ax = plt.subplots(figsize=(9.0, 6.2))
    xs = np.logspace(-1, 3, 400)
    d = 0.5
    edge = 1 / (d * xs)
    ax.fill_between(xs, edge, 1.0, color=AMBER_T, zorder=0)
    ax.fill_between(xs, 1e-3, np.minimum(edge, 1.0), color=GREEN_T, zorder=0)
    ax.plot(xs, edge, color=INK, lw=1.8, zorder=2)
    for dd, lab in ((0.25, "d = 0.25"), (0.75, "d = 0.75")):
        ax.plot(xs, 1 / (dd * xs), color=MUTED, lw=1.0, ls=(0, (4, 3)), zorder=2)
        xl = 8 if dd < 0.5 else 600
        ax.text(xl, 1 / (dd * xl) * (1.3 if dd < 0.5 else 0.75), lab, color=MUTED, fontsize=7.6,
                rotation=-42, ha="center", va="center")
    ax.text(560, 1 / (d * 560) * 1.5, "break-even, d = 0.5", color=INK, fontsize=8, rotation=-42,
            ha="center", va="center", weight="semibold")
    ax.text(150, 0.6, "The gate pays\nfor itself", color=WARM, fontsize=11, weight="semibold",
            ha="center", va="center")
    ax.text(0.45, 0.0035, "The gate costs more\nthan it prevents", color=GREEN, fontsize=11,
            weight="semibold", ha="left", va="center")
    pts = [
        ("A", 40, 0.2, "Hand-written code,\nreview as the main check", NAVY, (18, 6)),
        ("B", 3, 0.03, "Agentic session with a contract,\ndaily audit, fast rollback", GREEN, (8, -26)),
        ("C", 300, 0.03, "Irreversible:\nmigration, auth, money", RED, (-34, 30)),
    ]
    for tag, px, py, lab, col, off in pts:
        ax.scatter([px], [py], s=150, color="white", edgecolor=col, lw=2.2, zorder=5)
        ax.text(px, py, tag, color=col, fontsize=8, weight="bold", ha="center", va="center", zorder=6)
        ax.annotate(lab, (px, py), xytext=off, textcoords="offset points", fontsize=8, color=col,
                    weight="medium", va="center", linespacing=1.3)
    ax.annotate("", xy=(3.6, 0.036), xytext=(34, 0.17),
                arrowprops=dict(arrowstyle="-|>,head_length=0.6,head_width=0.3", color=INK, lw=1.4,
                                connectionstyle="arc3,rad=0.25", shrinkA=10, shrinkB=10))
    ax.text(0.14, 0.105, "checks move into the session (p falls)\nfixes get cheap, queues grow (ΔC/r falls)",
            fontsize=7.8, color=INK, ha="left", va="bottom", linespacing=1.35)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(0.1, 1000); ax.set_ylim(1e-3, 1.0)
    ax.set_xlabel("Late-fix cost avoided by catching the defect at review, ΔC / r\n(in units of the full cost of the gate for one change)")
    ax.set_ylabel("Residual defect probability per change, p\n(after the automated checks)")
    ax.set_xticks([0.1, 1, 10, 100, 1000]); ax.set_xticklabels(["0.1", "1", "10", "100", "1000"])
    ax.set_yticks([0.001, 0.01, 0.1, 1]); ax.set_yticklabels(["0.001", "0.01", "0.1", "1"])
    tidy(ax, grid_axis="both")
    ax.spines["left"].set_color(MUTED)
    fig.savefig(OUT + "fig03.png"); plt.close(fig)


# ---------- figure 4: simulation ----------
# Parameters (Table 2 in the paper). Time in working hours; one working day = 8 h.
P = dict(
    day=8.0,
    auto_mean=0.4,      # automated checks (CI + AI review), hours, lognormal cv 0.5
    rev_mean=1 / 3,     # first review round, hours, lognormal cv 1
    rev2_mean=1 / 6,    # second round, hours
    p_round2=0.4,       # share of changes needing a second round
    author_back=2.0,    # author turnaround before round two, hours, exponential
    servers=3,          # reviewer capacity, full-time equivalents
    p_defect=0.05,      # residual defect probability per change after automated checks
    d=0.5,              # share of residual defects a reviewer catches (generous)
    h_users=0.10,       # daily chance an escaped defect is found by users or monitoring
    h_audit=0.50,       # extra daily chance the nightly audit finds it
    lam=40,             # changes per day for panel (b)
    days=60,
    audit_hours=1.0,    # team hours per day spent on the audit report
)


def lognormal(rng, mean, cv, size=None):
    s2 = np.log(1 + cv ** 2)
    return rng.lognormal(np.log(mean) - s2 / 2, np.sqrt(s2), size)


def sim_lead_times(lam_day, gate, rng, days=60, warm=10):
    """Lead time (working hours) from 'ready' to 'merged' for one run of a FIFO M/G/c review queue.
    Optimistic for the gate: reviewers pick up work the moment they are free and never batch."""
    import heapq
    T = days * P["day"]
    n = rng.poisson(lam_day * days)
    arr = np.sort(rng.uniform(0, T, n))
    ready = arr + lognormal(rng, P["auto_mean"], 0.5, n)
    if not gate:
        lt = ready - arr
        return lt[arr > warm * P["day"]]
    free = [0.0] * P["servers"]  # min-heap of server free times
    heapq.heapify(free)
    events = [(t, i, 1) for i, t in enumerate(ready)]  # (time ready for review, change, round)
    heapq.heapify(events)
    done = np.zeros(n)
    while events:
        t, i, rnd = heapq.heappop(events)
        s = heapq.heappop(free)
        start = max(t, s)
        dur = lognormal(rng, P["rev_mean"] if rnd == 1 else P["rev2_mean"], 1.0)
        end = start + dur
        heapq.heappush(free, end)
        if rnd == 1 and rng.random() < P["p_round2"]:
            heapq.heappush(events, (end + rng.exponential(P["author_back"]), i, 2))
        else:
            done[i] = end
    lt = done - arr
    return lt[arr > warm * P["day"]]


def sim_defects(gate, audit, rng, runs=300, h_audit=None, d=None):
    """Latent defects in main, day by day: those live in main during the day, before that day's
    detections. Returns (runs x days) counts and the ages at fix."""
    h = P["h_users"] + ((P["h_audit"] if h_audit is None else h_audit) if audit else 0.0)
    d = P["d"] if d is None else d
    out = np.zeros((runs, P["days"]))
    ages = []
    for r in range(runs):
        live = []  # day each latent defect entered main
        for t in range(P["days"]):
            k = rng.binomial(rng.poisson(P["lam"]), P["p_defect"])
            if gate:
                k = rng.binomial(k, 1 - d)
            live += [t] * k
            out[r, t] = len(live)
            keep = []
            for t0 in live:
                if rng.random() < h:
                    ages.append(t - t0 + 1)
                else:
                    keep.append(t0)
            live = keep
    return out, np.array(ages)


def fig_simulation():
    rng = np.random.default_rng(2026)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.2, 4.6), gridspec_kw=dict(wspace=0.32))

    # (a) lead time against arrival rate
    lams = np.arange(5, 57, 3)
    res = {True: [], False: []}
    for gate in (True, False):
        for lam in lams:
            lt = np.concatenate([sim_lead_times(lam, gate, rng) for _ in range(6)])
            res[gate].append(np.percentile(lt, [10, 50, 90]))
        res[gate] = np.array(res[gate])
    for gate, col, lab in ((True, AMBER, "Human gate on every change"),
                           (False, GREEN, "Merge on green")):
        q = res[gate]
        a1.fill_between(lams, q[:, 0], q[:, 2], color=col, alpha=0.18, lw=0)
        a1.plot(lams, q[:, 1], color=col if gate else GREEN, lw=2.2)
        a1.text(lams[-1] + 1, q[-1, 1], lab, color=WARM if gate else GREEN, fontsize=8,
                weight="semibold", va="center")
    a1.axvline(P["lam"], color=MUTED, lw=0.9, ls=(0, (3, 3)))
    a1.text(P["lam"] + 0.6, 0.13, "λ used in (b)", color=MUTED, fontsize=7.4, rotation=90, va="bottom")
    a1.set_yscale("log"); a1.set_ylim(0.1, 30)
    a1.set_yticks([0.1, 0.5, 1, 4, 8, 24]); a1.set_yticklabels(["6 min", "30 min", "1 h", "4 h", "1 day", "3 days"])
    a1.set_xlim(4, 74)
    a1.set_xlabel("Changes per day"); a1.set_ylabel("Time from ready to merged (working time)")
    a1.set_title("(a) The gate adds waiting, more at high volume", loc="left", fontsize=10, weight="semibold")
    tidy(a1)

    # (b) latent defects in main
    pol = [(True, False, "Gate, no audit (today)", NAVY, "-"),
           (False, True, "No gate, daily audit (proposed)", GREEN, "-"),
           (True, True, "Gate and daily audit", AMBER, "-"),
           (False, False, "No gate, no audit (chaos)", RED, (0, (4, 3)))]
    days = np.arange(1, P["days"] + 1)
    summary = []
    for gate, audit, lab, col, ls in pol:
        out, ages = sim_defects(gate, audit, rng)
        m = out.mean(0)
        lo, hi = np.percentile(out, [10, 90], axis=0)
        a2.fill_between(days, lo, hi, color=col, alpha=0.12, lw=0)
        a2.plot(days, m, color=col, lw=2.0, ls=ls)
        nudge = {"No gate, daily audit (proposed)": 1.6, "Gate and daily audit": 0.2}.get(lab, 0)
        a2.text(days[-1] + 1, m[-10:].mean() + nudge, lab, color=WARM if col == AMBER else col, fontsize=8, weight="semibold", va="center")
        summary.append((lab, out[:, 20:].mean(), np.median(ages), ages.mean()))
    a2.set_xlim(0, 95); a2.set_ylim(0, 28)
    a2.set_xlabel("Working day"); a2.set_ylabel("Latent defects in main")
    a2.set_title(f"(b) Defects waiting to be found, λ = {P['lam']} per day", loc="left", fontsize=10,
                 weight="semibold")
    tidy(a2)
    fig.savefig(OUT + "fig04.png"); plt.close(fig)

    # numbers for Table 3
    lt_g = np.concatenate([sim_lead_times(P["lam"], True, rng) for _ in range(20)])
    lt_n = np.concatenate([sim_lead_times(P["lam"], False, rng) for _ in range(20)])
    rev_h = P["lam"] * (P["rev_mean"] + P["p_round2"] * P["rev2_mean"])
    print(f"lead time at lam={P['lam']}: gate median {np.median(lt_g):.2f} h, p90 {np.percentile(lt_g, 90):.2f} h;"
          f" no gate median {np.median(lt_n):.2f} h, p90 {np.percentile(lt_n, 90):.2f} h")
    print(f"reviewer hours per day with gate: {rev_h:.1f}; utilisation {rev_h / (P['servers'] * P['day']):.2f}")
    for lab, mean_latent, med_age, mean_age in summary:
        print(f"{lab:36s} latent {mean_latent:5.1f}  age at fix median {med_age:4.1f} d, mean {mean_age:4.1f} d")


# ---------- figure 5: how good must the audit be? ----------
def fig_sensitivity():
    """Latent defects without a gate but with an audit, relative to a gate without an audit.
    By Little's law the ratio is h_users / ((1 - d) * (h_users + h_audit)), so the proposal
    leaves fewer latent defects as soon as h_audit > h_users * d / (1 - d)."""
    rng = np.random.default_rng(7)
    hu = P["h_users"]
    fig, ax = plt.subplots(figsize=(9.0, 5.0))
    ha = np.linspace(0, 0.6, 300)
    ax.fill_between([0, 0.6], 0.08, 1, color=GREEN_T, zorder=0, lw=0)
    ax.plot([0, 0.6], [1, 1], color=INK, lw=1.2, zorder=2)
    ax.text(0.612, 1, "today: gate, no audit", ha="left", va="center", fontsize=8, color=INK,
            weight="semibold")
    ax.text(0.598, 0.1, "the proposal leaves fewer latent defects than today", ha="right",
            va="bottom", fontsize=8.4, color=GREEN, weight="semibold")
    for dd, col in ((0.25, NAVY), (0.5, GREEN), (0.75, WARM)):
        ax.plot(ha, hu / ((1 - dd) * (hu + ha)), color=col, lw=2.2, zorder=3)
        be = hu * dd / (1 - dd)
        ax.scatter([be], [1], s=46, color="white", edgecolor=col, lw=1.8, zorder=5)
        ax.annotate(f"{be:.2f}", (be, 1), xytext=(0, -15), textcoords="offset points", ha="center",
                    fontsize=7.6, color=col, weight="semibold")
        ax.text(0.612, hu / ((1 - dd) * (hu + 0.6)), f"reviewer catches d = {dd:.2f}", color=col,
                fontsize=8, weight="semibold", ha="left", va="center")
    # simulated check for d = 0.5
    base, _ = sim_defects(True, False, rng, runs=150)
    base = base[:, 20:].mean()
    sx = np.array([0.0, 0.05, 0.1, 0.2, 0.3, 0.5])
    sy = [sim_defects(False, True, rng, runs=150, h_audit=h)[0][:, 20:].mean() / base for h in sx]
    ax.scatter(sx, sy, marker="D", s=22, color=GREEN, zorder=6)
    ax.text(0.33, 0.66, "◆ simulation, d = 0.5", color=GREEN, fontsize=7.8)
    ax.plot([P["h_audit"]] * 2, [0.08, 5], color=MUTED, lw=0.9, ls=(0, (3, 3)))
    ax.text(P["h_audit"] - 0.008, 3.2, "value used in Figure 4", color=MUTED, fontsize=7.4, rotation=90,
            ha="right", va="center")
    ax.set_yscale("log"); ax.set_ylim(0.08, 5)
    ax.set_yticks([0.1, 0.25, 0.5, 1, 2, 4]); ax.set_yticklabels(["0.1×", "0.25×", "0.5×", "1×", "2×", "4×"])
    ax.set_xlim(0, 0.8); ax.set_xticks(np.arange(0, 0.61, 0.1))
    ax.spines["bottom"].set_bounds(0, 0.6)
    ax.set_xlabel("Daily chance that the audit finds a given latent defect, h_audit\n"
                  f"(users and monitoring find it with chance {hu:.2f} per day)")
    ax.set_ylabel("Latent defects, no gate with audit,\nrelative to gate without audit")
    tidy(ax, grid_axis="y")
    ax.grid(False)
    ax.hlines([0.1, 0.25, 0.5, 2, 4], 0, 0.6, color=RULE, lw=0.8, zorder=0.5)
    ax.spines["left"].set_color(MUTED)
    fig.savefig(OUT + "fig05.png"); plt.close(fig)


if __name__ == "__main__":
    import os
    os.makedirs(OUT, exist_ok=True)
    fig_gate_to_loop(); fig_cost_curve(); fig_break_even(); fig_simulation(); fig_sensitivity()
