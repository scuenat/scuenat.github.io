"""Figures for "Let the Code Be Chaotic".

Same style as "It Must Be Simpler Than This": Inter type, white cards with a faint shadow and a
coloured accent, colours taken from the site's palette. Figures 1 to 3 are drawn from the
simulations in sim.py (run here; numbers also written to results.json). Figure 4 is a schematic
of my own.
"""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import sim
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


def style(ax):
    ax.grid(axis="y", color=RULE, lw=0.6); ax.set_axisbelow(True)
    ax.spines["left"].set_visible(False); ax.tick_params(length=0, labelsize=8)


# ---------- Figure 1: Lorenz, unpredictable path, predictable place ----------
def fig_lorenz():
    t, out, sep, lz = sim.lorenz()
    fig = plt.figure(figsize=(5.8, 8.4))
    gs = fig.add_gridspec(2, 1, height_ratios=[1, 1.35], hspace=0.42)
    a = fig.add_subplot(gs[0])
    m = t <= 40
    a.plot(t[m], out[m, 0, 0], color=NAVY, lw=1.1, label="Run 1")
    a.plot(t[m], out[m, 1, 0], color=AMBER, lw=1.1, label="Run 2, started $10^{-8}$ away")
    ts = lz["t_separated"]
    a.axvline(ts, color=MUTED, lw=0.8, ls="--")
    a.text(ts + 0.6, 21, f"paths part\n(t ≈ {ts:.0f})", fontsize=7.8, color=MUTED, va="top")
    a.set_xlabel("Time", fontsize=8.6); a.set_ylabel("x", fontsize=8.6)
    style(a)
    a.set_title("The path: two runs that start one hundred-millionth apart",
                loc="left", fontsize=10.5, weight="semibold")
    a.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2, fontsize=8)
    b = fig.add_subplot(gs[1])
    k = int(20 / 0.005)
    b.plot(out[k:, 0, 0], out[k:, 0, 2], color=NAVY, lw=0.35, alpha=0.75)
    b.plot(out[k:, 1, 0], out[k:, 1, 2], color=AMBER, lw=0.35, alpha=0.75)
    b.set_xlabel("x", fontsize=8.6); b.set_ylabel("z", fontsize=8.6)
    b.tick_params(length=0, labelsize=8)
    for sp in ("left", "bottom"):
        b.spines[sp].set_color(RULE)
    z1, z2 = lz["run1"]["mean_z"], lz["run2"]["mean_z"]
    b.set_title("The place: after they part, both runs trace the same shape",
                loc="left", fontsize=10.5, weight="semibold")
    b.text(0.02, 0.02, f"average height z: {z1:.1f} and {z2:.1f}", transform=b.transAxes,
           fontsize=7.8, color=MUTED)
    fig.savefig(OUT + "fig01.png", dpi=400); fig.savefig(OUT + "fig01.svg"); plt.close(fig)
    return lz


# ---------- Figure 2: the code diverges, the tested behaviour does not ----------
def fig_twins():
    t, code, tested, _, s30 = sim.twins(sim.M)
    _, code20, _, untested20, s20 = sim.twins(20)
    fig, ax = plt.subplots(figsize=(5.8, 4.6))
    fl = 1e-12
    ax.semilogy(t, np.maximum(code, fl), color=NAVY, lw=1.8, label="Code (all 300 directions)")
    ax.semilogy(t, np.maximum(untested20, fl), color=AMBER, lw=1.5,
                label="Behaviour no test checks (run with 20 of 30 tested)")
    ax.semilogy(t, np.maximum(tested, fl), color=GREEN, lw=1.8,
                label="Behaviour the tests check")
    ax.set_ylim(1e-10, 1e2)
    ax.set_xlabel("Generation steps (time)", fontsize=8.6)
    ax.set_ylabel("Distance between the two runs (log)", fontsize=8.6)
    style(ax)
    ax.set_title("Same generator, same spec, starts $10^{-8}$ apart:\nthe code parts completely; the tested behaviour\nstays within a band set by the loop",
                 loc="left", fontsize=10.5, weight="semibold")
    ax.text(60, 3e-4, f"grows like $e^{{{s30['lyapunov_fit']:.2f}\\,t}}$", color=NAVY,
            fontsize=8, ha="right")
    ax.text(t[-1], 25, "as far apart as two\nunrelated programs", color=NAVY, fontsize=7.6,
            ha="right", va="bottom", linespacing=1.2)
    ax.text(t[-1], 0.03, "held within a narrow band", color=GREEN, fontsize=7.6, ha="right",
            va="top")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.18), fontsize=8, ncol=1)
    fig.savefig(OUT + "fig02.png", dpi=400); fig.savefig(OUT + "fig02.svg"); plt.close(fig)
    return {"30": s30, "20": s20}


# ---------- Figure 3: what is held is what is stable ----------
def fig_sweeps(res):
    cov = res["coverage"]
    ph = res["phase"]
    fig = plt.figure(figsize=(5.8, 8.6))
    gs = fig.add_gridspec(2, 1, hspace=0.62)
    a = fig.add_subplot(gs[0])
    x = [c["K"] / sim.M for c in cov]
    a.plot(x, [c["code_div"] for c in cov], color=MUTED, lw=1.6, marker="o", ms=3.5,
           label="How different the code is between runs")
    a.plot(x, [c["err_all_rel"] for c in cov], color=NAVY, lw=2.2, marker="o", ms=4,
           label="How far behaviour is from the spec")
    a.set_ylim(0, 1.08); a.set_xlim(-0.02, 1.02)
    a.set_xticks([0, 0.25, 0.5, 0.75, 1], ["0%", "25%", "50%", "75%", "100%"])
    a.set_xlabel("Share of the observable behaviour that tests check", fontsize=8.6)
    a.set_ylabel("Relative to no tests (1 = unrelated)", fontsize=8.6)
    style(a)
    a.set_title("(a) Behaviour converges as tests cover it;\nthe code stays far apart",
                loc="left", fontsize=10.5, weight="semibold")
    a.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), fontsize=8)
    b = fig.add_subplot(gs[1])
    E = np.array(ph["err_rel"])
    cols = plt.get_cmap("cividis")(np.linspace(0.1, 0.9, len(ph["gains"])))
    for i, g in enumerate(ph["gains"]):
        b.plot(ph["kappas"], E[i], color=cols[i], lw=1.3, marker="o", ms=3,
               label=f"g = {g:g}")
    b.set_xlabel("Strength of the loop κ (share of a test failure fixed per step)", fontsize=8.6)
    b.set_ylabel("Behaviour error, relative to no tests", fontsize=8.6)
    b.set_ylim(0, 0.75)
    style(b)
    b.set_title("(b) The loop sets the error; how chaotic\nthe generator is barely matters",
                loc="left", fontsize=10.5, weight="semibold")
    b.legend(title="chaos gain of the generator", title_fontsize=7.6, fontsize=7.4, ncol=4,
             loc="upper center", bbox_to_anchor=(0.5, -0.2))
    fig.savefig(OUT + "fig03.png", dpi=400); fig.savefig(OUT + "fig03.svg"); plt.close(fig)


# ---------- Figure 4: three kinds of freedom ----------
ZONES = [
    ("Held", "The behaviour the checks hold", GREEN,
     "Pulled back by machines on every\nchange. This is the attractor.", "Automate:\nstrong and fast"),
    ("Free, and harmless", "What no one can observe", NAVY,
     "Names, structure, order of lines,\nthe exact code of this run.", "Let it go\nto the machine"),
    ("Free, and not harmless", "Observable, but not checked", WARM,
     "Security, latency, edge cases,\nwhat users came to rely on.", "Automate it\nas a check"),
]


def fig_zones():
    fig, ax = canvas(6.4, 9.0, 12.8, 18.0)
    heading(ax, 0.3, 17.75, "Hold the attractor, let go of the path",
            "Three kinds of freedom in generated code")
    h, gap = 4.6, 0.55
    for i, (t, s, col, ex, fix) in enumerate(ZONES):
        y = 11.6 - i * (h + gap)
        card(ax, 0.4, y, 7.6, h, None, accent=col)
        ax.text(1.0, y + h - 0.55, f"ZONE {i + 1}", fontsize=6.8, weight="semibold", color=col,
                va="top", zorder=8)
        ax.text(1.0, y + h - 1.0, t, fontsize=11, weight="semibold", color=INK, va="top", zorder=8)
        ax.text(1.0, y + h - 1.75, s, fontsize=8.4, color=MUTED, va="top", linespacing=1.3, zorder=8)
        ax.text(1.0, y + 0.45, ex, fontsize=7.8, color=INK, va="bottom", linespacing=1.45, zorder=8)
        arrow(ax, (8.2, y + h / 2), (9.2, y + h / 2), color=col, lw=1.6, head=9)
        card(ax, 9.35, y + h / 2 - 1.0, 3.1, 2.0, fix, accent=col, fill=col, fs=9.4, bar=False)
    pill(ax, 6.4, 0.75, "Machines move zone 3 into zone 1. People gate only the irreversible.",
         fs=7.8, color=INK)
    fig.savefig(OUT + "fig04.png", dpi=400); fig.savefig(OUT + "fig04.svg"); plt.close(fig)


# ---------- Figure 5: where the people go ----------
def fig_levels():
    fig, ax = canvas(6.4, 8.1, 12.8, 16.2)
    heading(ax, 0.3, 15.95, "Out of the loop, not out of the system",
            "Where people work when the code is generated")
    # above the loop
    card(ax, 0.6, 10.9, 11.6, 3.6, "Guide and structure", accent=NAVY,
         eyebrow="Above the loop · people, continuously",
         sub="the promise · which checks must exist · budgets and metrics\n"
             "architecture and boundaries · what to build next · what to remove",
         fs=11.5, subfs=8.4)
    arrow(ax, (4.4, 10.75), (4.4, 8.75), color=NAVY, lw=1.6)
    ax.text(4.25, 9.75, "sets the attractor", fontsize=7.6, color=NAVY, ha="right", va="center")
    arrow(ax, (8.4, 8.75), (8.4, 10.75), color=MUTED, lw=1.4, ls="--")
    ax.text(8.55, 9.75, "metrics, drills,\nincidents", fontsize=7.6, color=MUTED, ha="left",
            va="center", linespacing=1.2)
    # the loop
    card(ax, 0.6, 5.0, 11.6, 3.6, "Generate, check, fix", accent=GREEN,
         eyebrow="The loop · machines, on every change",
         sub="agents write code and tests · checks run in the session\n"
             "scanners and budgets · regeneration drills · daily audit",
         fs=11.5, subfs=8.4)
    ax.add_patch(FancyArrowPatch((11.3, 7.9), (11.3, 5.7), connectionstyle="arc3,rad=-0.9",
                                 arrowstyle="-|>,head_length=0.5,head_width=0.28", mutation_scale=9,
                                 color=GREEN, lw=1.3, zorder=8))
    arrow(ax, (6.4, 4.85), (6.4, 3.65), color=WARM, lw=1.6)
    ax.text(6.6, 4.25, "only what cannot be undone", fontsize=7.6, color=WARM, ha="left", va="center")
    # the gate
    card(ax, 1.4, 1.6, 10.0, 1.95, "Decide the irreversible", accent=WARM,
         eyebrow="The gate · people, rarely",
         sub="deleting data · payments · releases · new dependencies", fs=10.5, subfs=8)
    pill(ax, 6.4, 0.6, "People leave the loop, not the system: they move up a level.", fs=7.8, color=INK)
    fig.savefig(OUT + "fig05.png", dpi=400); fig.savefig(OUT + "fig05.svg"); plt.close(fig)


if __name__ == "__main__":
    res = json.load(open("results.json"))
    fig_lorenz()
    res["twins"] = fig_twins()
    fig_sweeps(res)
    fig_zones()
    fig_levels()
    json.dump(res, open("results.json", "w"), indent=2)
    print(json.dumps(res["twins"], indent=1))
