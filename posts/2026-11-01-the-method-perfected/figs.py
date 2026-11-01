"""Figures for "The Method, Perfected". Same palette as the other posts.

Figure 1 is a schematic of my own. Figure 2 draws one field from the toy model in sim.py
(seed 0). Figure 3 plots the sweep in results.json (run sim.py first).
Each figure is written as SVG for the page and as a 400 dpi PNG for the share image.
"""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sim import field

BG, INK, MUTED, RULE = "#fbfaf7", "#1f2328", "#5f6b76", "#e6e2da"
NAVY, AMBER, WARM, GREEN, RED, PLUM = "#1d4f73", "#f5b041", "#b36b00", "#2e7d5b", "#a93226", "#7a3b69"
NAVY_T, AMBER_T = "#e5eef5", "#fdf1dc"
plt.rcParams.update({
    "font.family": "Inter", "font.size": 10, "text.color": INK,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.8,
    "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
    "savefig.bbox": "tight", "savefig.pad_inches": 0.35, "legend.frameon": False,
    "svg.fonttype": "none",
})


def save(fig, name):
    fig.savefig(f"figures/{name}.svg")
    fig.savefig(f"figures/{name}.png", dpi=400)
    plt.close(fig)


def fig01():
    """The dark period: evidence over time for an ordinary idea and a frame-breaking one."""
    t = np.linspace(0, 10, 400)
    dark_end = 7.0
    ordinary = 0.95 * (1 - np.exp(-t / 1.2))
    walk = np.cumsum(np.random.default_rng(3).normal(0, 0.02, t.size))
    walk = walk - walk[0] - 0.08 - 0.2 * np.sin(np.pi * t / dark_end)
    i_end = np.searchsorted(t, dark_end)
    after = walk[i_end] + 1.05 * (1 - np.exp(-(t - dark_end) / 0.6))
    frontier = np.where(t < dark_end, walk, after)
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.axvspan(0, dark_end, color=AMBER_T, zorder=0)
    ax.text(dark_end / 2, 1.2, "dark period: no decisive evidence yet", ha="center", color=WARM, fontsize=9.5)
    ax.axhline(0, color=RULE, lw=1, zorder=1)
    ax.axhline(-0.3, color=RED, lw=1.1, ls=(0, (4, 3)), zorder=2)
    ax.text(9.9, -0.36, "below this line,\nthe method moves on", ha="right", va="top", color=RED, fontsize=9)
    ax.plot(t, ordinary, color=NAVY, lw=2.2, zorder=3)
    ax.text(1.6, 1.0, "an idea the consensus expects", color=NAVY, fontsize=9.5)
    ax.plot(t, frontier, color=PLUM, lw=2.2, zorder=3)
    ax.text(7.15, -0.05, "an idea it does not:\nconviction carries it\nto the decisive test", color=PLUM, fontsize=9.5)
    ax.set_xlim(0, 10); ax.set_ylim(-0.6, 1.32)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_xlabel("time spent on the idea"); ax.set_ylabel("evidence for it")
    save(fig, "fig01")


def fig02():
    """One field from the model: consensus prior against the chance an idea is true."""
    f = field(np.random.default_rng(0), 0.5)
    rng = np.random.default_rng(1)
    keep = np.r_[rng.choice(np.where(~f["fro"])[0], 600, replace=False), np.where(f["fro"])[0]]
    pi, fro, under = f["pi"][keep], f["fro"][keep], f["under"][keep]
    p_true = np.where(under, 0.30, pi)
    jit = rng.normal(0, 0.008, keep.size)
    fig, ax = plt.subplots(figsize=(8, 4.6))
    ax.plot([0, 0.9], [0, 0.9], color=RULE, lw=1.2, zorder=0)
    ax.text(0.82, 0.77, "consensus is right", color=MUTED, fontsize=8.5, rotation=0, ha="right")
    ax.scatter(pi[~fro], p_true[~fro] + jit[~fro], s=8, color=NAVY, alpha=0.45, lw=0, label="ordinary ideas (value 1)")
    m = fro & ~under
    ax.scatter(pi[m], p_true[m] + jit[m], s=12, color=MUTED, alpha=0.5, lw=0, label="far ideas the consensus rightly doubts")
    ax.scatter(pi[under], p_true[under] + jit[under], s=16, color=PLUM, alpha=0.85, lw=0,
               label="far ideas the consensus underrates (value 20)")
    ax.axvspan(0, 0.07, color=AMBER_T, zorder=-1)
    ax.text(0.075, 0.5, "the method ranks\nthese last and\ncannot tell them\napart; taste can", color=WARM, fontsize=9, va="center")
    ax.set_xlim(0, 0.9); ax.set_ylim(-0.03, 0.9)
    ax.set_xlabel("consensus prior: how plausible the field finds the idea")
    ax.set_ylabel("true rate p: share of such ideas that turn out true")
    ax.legend(loc="upper left", fontsize=8.5, handletextpad=0.3, markerscale=1.6)
    save(fig, "fig02")


def fig03():
    """Sweep: share of the budget given to conviction, for three strengths of taste."""
    r = json.load(open("results.json"))["sweep"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9, 3.8))
    cols = {"0.0": MUTED, "0.5": PLUM, "1.0": NAVY}
    labs = {"0.0": "faith without taste", "0.5": "weak taste", "1.0": "good taste"}
    for d, res in r.items():
        s = [100 * x["share"] for x in res]
        b = [x["breakthroughs"]["mean"] for x in res]
        lo = [x["breakthroughs"]["p05"] for x in res]
        hi = [x["breakthroughs"]["p95"] for x in res]
        a1.fill_between(s, lo, hi, color=cols[d], alpha=0.12, lw=0)
        a1.plot(s, b, color=cols[d], lw=2, marker="o", ms=4, label=labs[d])
    o = [x["ordinary"]["mean"] for x in r["0.5"]]
    a2.plot([100 * x["share"] for x in r["0.5"]], o, color=GREEN, lw=2, marker="o", ms=4)
    a1.set_title("Breakthroughs found", loc="left", fontsize=10.5)
    a2.set_title("Ordinary discoveries found", loc="left", fontsize=10.5)
    for a in (a1, a2):
        a.set_xlabel("share of the budget given to conviction (%)")
    a1.set_ylim(0, None); a2.set_ylim(0, 800)
    a1.legend(fontsize=8.5, loc="upper left")
    fig.tight_layout(w_pad=3)
    save(fig, "fig03")


def fig04():
    """Cheap-testing limit: breakthroughs as AI work gets cheaper, base field and a field ten times larger."""
    rows = json.load(open("results.json"))["limit"]
    fig, axs = plt.subplots(1, 2, figsize=(9, 3.9))
    for ax, pool, title in ((axs[0], 1, "Base field (5,400 ideas)"), (axs[1], 10, "Field ten times larger")):
        r = [x for x in rows if x["pool"] == pool]
        k = [x["factor"] for x in r]
        for name, col, nm in (("mixed", PLUM, "AI + 20% conviction"), ("method_ai", NAVY, "method with AI")):
            m = [x[name]["mean"] for x in r]
            ax.fill_between(k, [x[name]["p05"] for x in r], [x[name]["p95"] for x in r], color=col, alpha=0.12, lw=0)
            ax.plot(k, m, color=col, lw=2, marker="o", ms=4, label=nm)
        ax.set_xscale("log")
        ax.set_xticks([1, 2, 5, 10, 20, 50]); ax.set_xticklabels(["1x", "2x", "5x", "10x", "20x", "50x"])
        ax.minorticks_off()
        ax.set_title(title, loc="left", fontsize=10.5)
        ax.set_xlabel("AI work, times cheaper than in Table 1")
        ax.set_ylim(0, None)
    axs[0].set_ylabel("breakthroughs found")
    axs[1].legend(fontsize=8.5, loc="upper left")
    fig.tight_layout(w_pad=3)
    save(fig, "fig04")


if __name__ == "__main__":
    fig01(); fig02(); fig03(); fig04()
