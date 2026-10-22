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
    """Today a person approves every change. Proposed: a person approves only what cannot be
    undone; everything else merges on green and a daily audit steers the team."""
    fig, ax = canvas(11.2, 6.4, 33.0, 18.9)
    # top band: today
    ax.add_patch(FancyBboxPatch((0.3, 12.6), 32.4, 6.0, boxstyle="round,pad=0,rounding_size=0.45",
                                fc="#eef1f4", ec="none", zorder=0.5))
    heading(ax, 0.95, 17.95, "TODAY", "A person approves every change", color=NAVY)
    y = 13.3
    card(ax, 0.95, y, 7.0, 2.9, "Write", None, accent=NAVY, fs=11)
    card(ax, 9.6, y, 7.0, 2.9, "Checks", None, accent=NAVY, fs=11)
    card(ax, 18.25, y, 7.0, 2.9, "A person approves", None, accent=AMBER, fill=AMBER_T, fs=11)
    card(ax, 26.9, y, 5.1, 2.9, "Merge", None, accent=GREEN, fs=11)
    arrow(ax, (8.05, y + 1.45), (9.5, y + 1.45), lw=1.6)
    arrow(ax, (16.7, y + 1.45), (18.15, y + 1.45), lw=1.6)
    arrow(ax, (25.35, y + 1.45), (26.8, y + 1.45), color=GREEN, lw=1.6)
    pill(ax, 21.75, y - 0.35, "every change waits here", color=WARM, fs=7.6)

    # bottom band: proposed
    ax.add_patch(FancyBboxPatch((0.3, 0.3), 32.4, 11.6, boxstyle="round,pad=0,rounding_size=0.45",
                                fc=SAND_T, ec="none", zorder=0.5))
    heading(ax, 0.95, 11.25, "PROPOSED", "Approve what you cannot undo. Watch everything else.", color=WARM)
    y = 6.0
    card(ax, 0.95, y, 7.0, 2.9, "Write", "with rules", accent=NAVY, fs=11, subfs=8.4)
    card(ax, 9.6, y, 7.0, 2.9, "Checks", None, accent=NAVY, fs=11)
    card(ax, 18.25, y, 7.0, 2.9, "Can it be undone?", None, accent=NAVY, fs=10.5)
    card(ax, 26.9, y + 1.6, 5.1, 2.3, "A person", "approves", accent=AMBER, fill=AMBER_T, fs=10, subfs=8)
    card(ax, 26.9, y - 1.0, 5.1, 2.3, "Merge", None, accent=GREEN, fs=11)
    arrow(ax, (8.05, y + 1.45), (9.5, y + 1.45), lw=1.6)
    arrow(ax, (16.7, y + 1.45), (18.15, y + 1.45), lw=1.6)
    arrow(ax, (25.35, y + 2.1), (26.8, y + 2.75), color=WARM, lw=1.6)
    arrow(ax, (25.35, y + 0.8), (26.8, y + 0.15), color=GREEN, lw=1.6)
    ax.text(26.05, y + 3.0, "no", color=WARM, fontsize=8.5, weight="semibold", ha="center")
    ax.text(26.05, y - 0.35, "yes", color=GREEN, fontsize=8.5, weight="semibold", ha="center")
    # the loop
    yb = 1.0
    card(ax, 18.25, yb, 13.75, 2.5, "Daily audit of the whole codebase", None, accent=AMBER, fs=10.5)
    card(ax, 0.95, yb, 15.65, 2.5, "The team fixes what matters and tightens the rules", None,
         accent=AMBER, fs=10.5)
    arrow(ax, (18.15, yb + 1.25), (16.7, yb + 1.25), color=WARM, lw=1.6)
    arrow(ax, (4.45, yb + 2.6), (4.45, y - 0.1), color=WARM, lw=1.6)
    arrow(ax, (29.45, y - 1.1), (29.45, yb + 2.6), color=WARM, lw=1.6, ls=(0, (4, 3)))
    pill(ax, 29.45, (yb + 2.6 + y - 1.1) / 2, "every night", color=WARM, fs=7.4)
    fig.savefig(OUT + "fig01.png"); plt.close(fig)


# ---------- figure 2: the cost of a late fix ----------
def fig_cost_curve():
    """Schematic. Late fixes used to be expensive; with agents they are cheap, except
    when the harm cannot be undone."""
    fig, ax = plt.subplots(figsize=(9.0, 4.6))
    stages = ["while\nwriting", "at\nreview", "next\nday", "months\nlater"]
    x = np.arange(len(stages))
    lines = [("Before agents", [1, 3, 10, 100], MUTED, (0, (4, 3))),
             ("With agents (assumed)", [1, 1.2, 1.4, 2.4], GREEN, "-"),
             ("Cannot be undone", [None, None, 40, 60], RED, "-")]
    for name, ys, col, ls in lines:
        xs = [xi for xi, yi in zip(x, ys) if yi is not None]
        ys = [yi for yi in ys if yi is not None]
        ax.plot(xs, ys, color=col, lw=2.6, ls=ls, marker="o", ms=6, mfc="white", mew=1.8, zorder=3)
        if col == RED:
            ax.text(xs[0] - 0.12, ys[0], name, color=col, va="center", ha="right", fontsize=10, weight="semibold")
        else:
            ax.text(xs[-1] + 0.12, ys[-1], name, color=col, va="center", fontsize=10, weight="semibold")
    ax.set_yscale("log"); ax.set_ylim(0.8, 160)
    ax.set_yticks([1, 10, 100]); ax.set_yticklabels(["1×", "10×", "100×"])
    ax.set_xticks(x); ax.set_xticklabels(stages)
    ax.set_xlim(-0.3, len(stages) + 0.9)
    ax.set_ylabel("Cost to fix")
    ax.set_xlabel("When the defect is found")
    tidy(ax)
    fig.savefig(OUT + "fig02.png"); plt.close(fig)


# ---------- figure 3: the break-even map ----------
def fig_break_even():
    """Review pays when p * d * dC > r (d = 0.5). Positions are illustrative, not measured."""
    fig, ax = plt.subplots(figsize=(8.4, 5.6))
    xs = np.logspace(-1, 3, 400)
    edge = 1 / (0.5 * xs)
    ax.fill_between(xs, edge, 1.0, color=AMBER_T, zorder=0)
    ax.fill_between(xs, 1e-3, np.minimum(edge, 1.0), color=GREEN_T, zorder=0)
    ax.plot(xs, edge, color=INK, lw=1.8, zorder=2)
    ax.text(200, 0.4, "Review pays", color=WARM, fontsize=13, weight="semibold", ha="center", va="center")
    ax.text(0.6, 0.004, "Review costs more\nthan it saves", color=GREEN, fontsize=13, weight="semibold",
            ha="center", va="center")
    pts = [(40, 0.2, "Before agents", NAVY, (12, 0), "left"),
           (3, 0.03, "With agents", GREEN, (-12, 0), "right"),
           (300, 0.03, "Cannot be undone", RED, (0, -18), "center")]
    for px, py, lab, col, off, ha in pts:
        ax.scatter([px], [py], s=110, color=col, edgecolor="white", lw=1.5, zorder=5)
        ax.annotate(lab, (px, py), xytext=off, textcoords="offset points", fontsize=10, color=col,
                    weight="semibold", va="center", ha=ha)
    ax.annotate("", xy=(3.6, 0.036), xytext=(34, 0.17),
                arrowprops=dict(arrowstyle="-|>,head_length=0.6,head_width=0.3", color=INK, lw=1.4,
                                connectionstyle="arc3,rad=0.25", shrinkA=9, shrinkB=9))
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(0.1, 1000); ax.set_ylim(1e-3, 1.0)
    ax.set_xlabel("Cost of a late fix, relative to the cost of a review  →")
    ax.set_ylabel("Chance a change still has a defect  →")
    ax.set_xticks([]); ax.set_yticks([]); ax.minorticks_off()
    for s_ in ("left", "bottom"):
        ax.spines[s_].set_color(MUTED)
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


def sim_defects(gate, audit, rng, runs=300, h_audit=None, d=None, c=1.0):
    """Latent defects in main, day by day: those live in main during the day, before that day's
    detections. A share c of defects is visible to the audit; the rest are found only by users.
    Returns (runs x days) counts and the ages at fix."""
    hu = P["h_users"]
    ha = (P["h_audit"] if h_audit is None else h_audit) if audit else 0.0
    d = P["d"] if d is None else d
    out = np.zeros((runs, P["days"]))
    ages = []
    for r in range(runs):
        live = []  # day each latent defect entered main
        for t in range(P["days"]):
            k = rng.binomial(rng.poisson(P["lam"]), P["p_defect"])
            if gate:
                k = rng.binomial(k, 1 - d)
            live += [(t, hu + ha if rng.random() < c else hu) for _ in range(k)]
            out[r, t] = len(live)
            keep = []
            for t0, h in live:
                if rng.random() < h:
                    ages.append(t - t0 + 1)
                else:
                    keep.append((t0, h))
            live = keep
    return out, np.array(ages)


def fig_simulation():
    """Latent defects in main under four policies, at 40 changes a day."""
    rng = np.random.default_rng(2026)
    pol = [(False, False, "No gate, no audit", RED, 0),
           (True, False, "Gate (today)", NAVY, 16),
           (False, True, "Audit, no gate (proposed)", GREEN, 1),
           (True, True, "Gate and audit", AMBER, 17)]
    vals = []
    for gate, audit, lab, col, hrs in pol:
        out, ages = sim_defects(gate, audit, rng)
        vals.append((lab, out[:, 20:].mean(), col, hrs, np.median(ages)))
    fig, ax = plt.subplots(figsize=(9.0, 3.9))
    ys = np.arange(len(vals))[::-1]
    for yv, (lab, v, col, hrs, _) in zip(ys, vals):
        ax.barh(yv, v, color=col, height=0.62, zorder=3)
        ax.text(v + 0.3, yv, f"{v:.1f}", va="center", fontsize=10.5, weight="semibold", color=INK)
        ax.text(23.2, yv, f"{hrs} h" if hrs else "0 h", va="center", ha="right", fontsize=10,
                color=WARM if hrs > 2 else MUTED, weight="semibold")
    ax.text(23.2, len(vals) - 0.35, "review time\nper day", ha="right", va="bottom", fontsize=8, color=MUTED)
    ax.set_yticks(ys); ax.set_yticklabels([v[0] for v in vals], fontsize=10)
    ax.set_xlim(0, 23.5); ax.set_ylim(-0.6, len(vals) - 0.1)
    ax.set_xticks([0, 5, 10, 15, 20])
    ax.set_xlabel("Defects waiting to be found in the main branch (average)")
    tidy(ax, grid_axis="x")
    ax.spines["left"].set_visible(False)
    fig.savefig(OUT + "fig04.png"); plt.close(fig)

    # numbers for Table 3
    lt_g = np.concatenate([sim_lead_times(P["lam"], True, rng) for _ in range(20)])
    lt_n = np.concatenate([sim_lead_times(P["lam"], False, rng) for _ in range(20)])
    rev_h = P["lam"] * (P["rev_mean"] + P["p_round2"] * P["rev2_mean"])
    print(f"lead time at lam={P['lam']}: gate median {np.median(lt_g):.2f} h, p90 {np.percentile(lt_g, 90):.2f} h;"
          f" no gate median {np.median(lt_n):.2f} h, p90 {np.percentile(lt_n, 90):.2f} h")
    print(f"reviewer hours per day with gate: {rev_h:.1f}; utilisation {rev_h / (P['servers'] * P['day']):.2f}")
    for lab, v, _, _, med_age in vals:
        print(f"{lab:28s} latent {v:5.1f}  median age at fix {med_age:4.1f} d")


# ---------- figure 5: how much must the audit see? ----------
def fig_sensitivity():
    """Latent defects without a gate but with an audit, relative to today's gate, against the
    share c of defects the audit can see. Break-even at c = d * (1 + h_users / h_audit)."""
    rng = np.random.default_rng(11)
    hu, d0 = P["h_users"], P["d"]
    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    c = np.linspace(0, 1, 300)
    ax.fill_between([0, 1], 0, 1, color=GREEN_T, zorder=0, lw=0)
    ax.axhline(1, color=INK, lw=1.3, zorder=2)
    ax.text(0.01, 1.04, "today: a person approves every change", fontsize=8.8, color=INK, va="bottom")
    ax.text(0.99, 0.08, "better than today", fontsize=10, color=GREEN, weight="semibold", ha="right")
    for ha_, col, lab in ((0.5, GREEN, "audit finds them in ~2 days"), (0.2, NAVY, "audit finds them in ~5 days")):
        ratio = (c / (hu + ha_) + (1 - c) / hu) / ((1 - d0) / hu)
        ax.plot(c, ratio, color=col, lw=2.6, zorder=3)
        be = d0 * (1 + hu / ha_)
        ax.scatter([be], [1], s=70, color="white", edgecolor=col, lw=2, zorder=5)
        ax.annotate(f"{be:.0%}", (be, 1), xytext=(0, -16), textcoords="offset points", ha="center",
                    fontsize=9.5, color=col, weight="bold")
        ax.text(1.01, ratio[-1], lab, color=col, fontsize=9, weight="semibold", va="center")
        # simulation check, printed only
        for cc in (be, 1.0):
            base = sim_defects(True, False, rng, runs=100)[0][:, 20:].mean()
            sim = sim_defects(False, True, rng, runs=100, h_audit=ha_, c=cc)[0][:, 20:].mean() / base
            print(f"check h_audit={ha_} c={cc:.2f}: sim {sim:.2f} vs analytic "
                  f"{(cc / (hu + ha_) + (1 - cc) / hu) / ((1 - d0) / hu):.2f}")
    ax.set_xlim(0, 1); ax.set_ylim(0, 2.2)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1]); ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"])
    ax.set_yticks([0, 1, 2]); ax.set_yticklabels(["0", "1×", "2×"])
    ax.set_xlabel("Share of defects the audit can see")
    ax.set_ylabel("Defects waiting to be found,\ncompared with today")
    tidy(ax)
    fig.savefig(OUT + "fig05.png"); plt.close(fig)


if __name__ == "__main__":
    import os
    os.makedirs(OUT, exist_ok=True)
    fig_gate_to_loop(); fig_cost_curve(); fig_break_even(); fig_simulation(); fig_sensitivity()
