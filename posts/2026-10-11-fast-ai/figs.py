"""Figures for "Fast AI". Style matches the earlier essays."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

NAVY, GREY, RED, LIGHT, PALE, AMBER = "#1f4e79", "#7f8c8d", "#c0392b", "#d5dde5", "#eef1f4", "#d68910"
INK = "#2c3e50"
plt.rcParams.update({
    "font.family": "DejaVu Serif", "font.size": 10, "axes.spines.top": False,
    "axes.spines.right": False, "axes.linewidth": 1.0, "savefig.dpi": 200,
    "savefig.bbox": "tight", "legend.frameon": False, "legend.fontsize": 8.5,
})
OUT = "figures/"


def box(ax, x, y, w, h, title, sub=None, fc=LIGHT, fs=9.5, subfs=8):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.18",
                                fc=fc, ec="none"))
    col = "white" if fc in (NAVY, RED, AMBER) else INK
    if sub:
        ax.text(x + w / 2, y + h * 0.63, title, ha="center", va="center", color=col,
                weight="bold", fontsize=fs)
        ax.text(x + w / 2, y + h * 0.3, sub, ha="center", va="center", color=col, fontsize=subfs,
                style="italic")
    else:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center", color=col,
                weight="bold", fontsize=fs)


def arrow(ax, p, q, color=GREY, rad=0.0, lw=1.4, ls="-"):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=11, color=color, lw=lw,
                                 ls=ls, connectionstyle=f"arc3,rad={rad}", shrinkA=2, shrinkB=2))


def fig_expertise():
    """Schematic: time per invoice falls as learning turns into habit; new cases bring slow-downs."""
    t = np.linspace(0, 10, 600)
    base = 0.6 + 9.4 * np.exp(-t / 1.4)
    bumps = [(3.2, 3.0), (5.6, 2.4), (7.6, 2.0)]
    y = base.copy()
    for c, a in bumps:
        y += a * np.exp(-((t - c) / 0.18) ** 2) * (t >= c - 0.6)
    fig, ax = plt.subplots(figsize=(5.4, 2.8))
    ax.plot(t, y, color=NAVY, lw=2.2)
    ax.fill_between(t, 0, y, color=LIGHT, alpha=0.5, lw=0)
    for c, a in bumps:
        ax.annotate("", xy=(c, base[np.argmin(abs(t - c))] + a + 0.3),
                    xytext=(c, base[np.argmin(abs(t - c))] + a + 1.9),
                    arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.1))
    ax.text(5.5, 6.4, "something new: slow down, think,\nkeep the lesson as a habit",
            color=RED, fontsize=8, ha="center")
    ax.text(0.35, 9.6, "first week:\nevery invoice is\nan investigation", fontsize=8, color=INK,
            va="top", ha="left")
    ax.text(9.9, 1.2, "ten years later:\na glance", fontsize=8, color=INK, ha="right")
    ax.set_xlim(0, 10); ax.set_ylim(0, 11)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_xlabel("experience (years)"); ax.set_ylabel("effort per invoice")
    fig.savefig(OUT + "fig01.png"); plt.close(fig)


def fig_compound():
    n = np.arange(1, 41)
    fig, ax = plt.subplots(figsize=(5.4, 2.9))
    for p, c, ls, lw in [(0.99, GREY, ":", 1.6), (0.95, NAVY, "-", 2.3), (0.90, GREY, "--", 1.6)]:
        ax.plot(n, 100 * p ** n, color=c, ls=ls, lw=lw, label=f"each step right {p:.0%}")
    ax.plot([20], [100 * 0.95 ** 20], "o", color=RED, ms=6, zorder=5)
    ax.annotate(f"20 steps at 95%:\n{0.95 ** 20:.0%} fully right", xy=(20, 100 * 0.95 ** 20),
                xytext=(23.5, 52), color=RED, fontsize=8.5,
                arrowprops=dict(arrowstyle="-", color=RED, lw=0.9))
    ax.set_xlim(1, 40); ax.set_ylim(0, 102)
    ax.set_xlabel("number of steps in the loop")
    ax.set_ylabel("chance every step\nis right (%)")
    ax.legend(loc="lower left")
    fig.savefig(OUT + "fig02.png"); plt.close(fig)


def fig_compile():
    fig, ax = plt.subplots(figsize=(6.2, 3.6))
    ax.set_xlim(0, 12); ax.set_ylim(-0.1, 7.2); ax.axis("off")
    ax.text(0.1, 6.95, "Interpret: an agentic loop", weight="bold", fontsize=10, color=INK, va="top")
    ax.text(0.1, 3.1, "Compile: Fast AI", weight="bold", fontsize=10, color=INK, va="top")
    # interpreter: every run goes through the large model loop
    for i in range(4):
        x = 0.4 + i * 2.9
        box(ax, x, 4.0, 2.4, 1.9, f"run {i + 1}", "read · reason · call\nread · reason · …", fc=PALE)
    ax.text(6, 3.65, "the large model thinks on every run, and may take a different path each time",
            ha="center", fontsize=8, color=RED, style="italic")
    # compiler: think once, then fast identical runs
    box(ax, 0.4, 0.2, 3.0, 2.15, "Large model", "reads, extracts,\nstructures: once", fc=NAVY)
    arrow(ax, (3.5, 1.27), (4.5, 1.27), color=NAVY, lw=1.8)
    box(ax, 4.6, 0.2, 2.2, 2.15, "Memory +\nfast models", None, fc=LIGHT)
    for i in range(5):
        x = 7.4 + i * 0.92
        box(ax, x, 0.75, 0.75, 1.05, f"{i + 1}", None, fc=PALE, fs=8.5)
    arrow(ax, (6.9, 1.27), (7.35, 1.27), color=NAVY, lw=1.8)
    ax.text(9.65, 0.3, "runs: fast, identical, explainable", ha="center", fontsize=8, color=NAVY,
            style="italic")
    fig.savefig(OUT + "fig03.png"); plt.close(fig)


def fig_graph():
    nodes = {
        "Supplier\nAcme AG": (2.2, 3.6, NAVY),
        "Contract\n2025-114": (5.0, 4.6, LIGHT),
        "Cost centre\nMaintenance": (8.6, 3.6, LIGHT),
        "Approver\nHead of Ops": (8.6, 1.0, LIGHT),
        "Rule\n> CHF 10,000:\nsecond approval": (5.0, 0.75, LIGHT),
        "Line item\n'spare parts'": (2.2, 1.0, LIGHT),
        "3 disputes\nlast year": (-0.5, 3.4, PALE),
    }
    edges = [
        ("Supplier\nAcme AG", "Contract\n2025-114", "has"),
        ("Contract\n2025-114", "Cost centre\nMaintenance", "charged to"),
        ("Cost centre\nMaintenance", "Approver\nHead of Ops", "approved by"),
        ("Rule\n> CHF 10,000:\nsecond approval", "Approver\nHead of Ops", "applies to"),
        ("Supplier\nAcme AG", "Line item\n'spare parts'", "bills"),
        ("Line item\n'spare parts'", "3 disputes\nlast year", "disputed"),
        ("Contract\n2025-114", "Rule\n> CHF 10,000:\nsecond approval", "limit"),
    ]
    fig, ax = plt.subplots(figsize=(5.8, 3.6))
    ax.set_xlim(-1.7, 9.8); ax.set_ylim(0.0, 5.2); ax.axis("off")
    for a, b, lab in edges:
        (x1, y1, _), (x2, y2, _) = nodes[a], nodes[b]
        ax.plot([x1, x2], [y1, y2], color=GREY, lw=1.2, zorder=1)
        if lab:
            ax.text((x1 + x2) / 2, (y1 + y2) / 2, lab, fontsize=7.2, color=GREY,
                    ha="center", style="italic", zorder=3,
                    bbox=dict(fc="white", ec="none", pad=0.6))
    for name, (x, y, fc) in nodes.items():
        w = 2.1 if "Rule" not in name else 2.3
        h = 0.95 if "Rule" not in name else 1.2
        ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                    boxstyle="round,pad=0.02,rounding_size=0.18", fc=fc, ec="none", zorder=2))
        ax.text(x, y, name, ha="center", va="center", fontsize=8,
                color="white" if fc == NAVY else INK, zorder=3)
    fig.savefig(OUT + "fig04.png"); plt.close(fig)


def fig_hybrid():
    fig, ax = plt.subplots(figsize=(7.0, 2.9))
    ax.set_xlim(0, 14.4); ax.set_ylim(0.4, 5.4); ax.axis("off")
    box(ax, 0.0, 1.9, 2.6, 1.4, "Raw input", "scan, photo, text", fc=PALE)
    box(ax, 3.4, 1.9, 2.9, 1.4, "Deep network", "perceives", fc=LIGHT)
    box(ax, 7.4, 1.9, 2.6, 1.4, "Trees", "decide", fc=NAVY)
    box(ax, 10.8, 1.9, 3.5, 1.4, "Decision", "in milliseconds,\nwith its reasons", fc=PALE)
    box(ax, 3.4, 4.0, 2.9, 1.3, "Knowledge graph", "remembers", fc=LIGHT)
    arrow(ax, (2.65, 2.6), (3.35, 2.6))
    arrow(ax, (6.35, 2.6), (7.35, 2.6))
    ax.text(6.85, 2.8, "features", fontsize=7.5, color=GREY, ha="center", style="italic")
    arrow(ax, (10.05, 2.6), (10.75, 2.6))
    arrow(ax, (6.35, 4.65), (8.2, 3.35), rad=-0.25)
    ax.text(7.75, 4.4, "facts, history, rules", fontsize=7.5, color=GREY, style="italic")
    ax.text(7.2, 0.95, "each part does what it is best at; none of them thinks from scratch",
            ha="center", fontsize=8, color=INK, style="italic")
    fig.savefig(OUT + "fig05.png"); plt.close(fig)


def fig_paths():
    fig, ax = plt.subplots(figsize=(6.8, 3.9))
    ax.set_xlim(-0.2, 14.0); ax.set_ylim(-0.2, 7.0); ax.axis("off")
    box(ax, 0.0, 3.0, 2.2, 1.3, "New case", None, fc=PALE)
    box(ax, 3.2, 3.0, 3.0, 1.3, "Fast models", "is this familiar?", fc=NAVY)
    box(ax, 8.4, 4.6, 5.5, 1.3, "Fast path", "the common cases, in milliseconds", fc=LIGHT)
    box(ax, 8.4, 1.4, 5.5, 1.3, "Slow path", "language model, agent or person", fc=AMBER)
    box(ax, 3.2, 0.0, 3.0, 1.15, "Knowledge graph", None, fc=LIGHT, fs=9)
    arrow(ax, (2.25, 3.65), (3.15, 3.65))
    arrow(ax, (6.25, 3.95), (8.35, 5.2), color=NAVY)
    ax.text(6.7, 4.85, "confident", fontsize=7.5, color=NAVY, style="italic", rotation=28)
    arrow(ax, (6.25, 3.35), (8.35, 2.1), color=AMBER)
    ax.text(7.45, 3.0, "unsure, or unlike\nanything seen", fontsize=7.5, color=AMBER, style="italic")
    arrow(ax, (11.1, 1.35), (6.3, 0.6), color=AMBER, rad=-0.2)
    ax.text(9.4, 0.05, "the new answer is kept", fontsize=7.5, color=AMBER, style="italic")
    arrow(ax, (4.7, 1.2), (4.7, 2.95), color=GREY, ls="--")
    ax.text(4.5, 2.05, "if it repeats,\nretrain", fontsize=7.5, color=GREY, style="italic", ha="right")
    ax.text(7.0, 6.6, "Deliberation becomes habit", ha="center", fontsize=10, weight="bold", color=INK)
    fig.savefig(OUT + "fig06.png"); plt.close(fig)


def fig_invoice():
    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    ax.set_xlim(0, 14.0); ax.set_ylim(-0.1, 7.4); ax.axis("off")
    ax.text(0, 7.25, "The agentic way: every invoice", weight="bold", fontsize=9.5, color=INK, va="top")
    steps = ["read", "reason:\nsupplier", "search\ncontracts", "reason:\namount", "look up\nrules",
             "propose", "check,\nadjust"]
    for i, s in enumerate(steps):
        x = i * 2.0
        box(ax, x, 5.0, 1.7, 1.15, s, None, fc=PALE, fs=7.8)
        if i:
            arrow(ax, (x - 0.3, 5.57), (x - 0.02, 5.57))
    ax.text(0, 4.45, "about half a minute · noticeable cost · may differ next time · "
            "explained by pages of reasoning", fontsize=7.8, color=RED, style="italic")
    ax.text(0, 3.75, "The Fast AI way", weight="bold", fontsize=9.5, color=INK, va="top")
    ax.text(0, 3.15, "once, months earlier:", fontsize=7.8, color=GREY, style="italic")
    box(ax, 0.0, 1.5, 3.1, 1.35, "Language model", "reads contracts,\npolicies, cases", fc=NAVY,
        fs=8.5, subfs=7.3)
    box(ax, 3.6, 1.5, 2.5, 1.35, "Graph", "reviewed by the\nfinance team", fc=LIGHT, fs=8.5, subfs=7.3)
    arrow(ax, (3.15, 2.17), (3.55, 2.17), color=NAVY)
    ax.text(6.9, 3.15, "every invoice:", fontsize=7.8, color=GREY, style="italic")
    box(ax, 6.9, 1.5, 2.1, 1.35, "Network", "reads it", fc=LIGHT, fs=8.5, subfs=7.3)
    box(ax, 9.5, 1.5, 2.1, 1.35, "Trees", "pick a route", fc=NAVY, fs=8.5, subfs=7.3)
    box(ax, 12.1, 1.5, 1.9, 1.35, "Route", "+ its reasons", fc=PALE, fs=8.5, subfs=7.3)
    arrow(ax, (9.05, 2.17), (9.45, 2.17)); arrow(ax, (11.65, 2.17), (12.05, 2.17))
    arrow(ax, (6.15, 1.75), (9.7, 1.45), color=GREY, rad=0.35)
    ax.text(0, 0.6, "milliseconds · same answer every time · explains: supplier, amount vs contract, "
            "cost centre, past disputes", fontsize=7.8, color=NAVY, style="italic")
    ax.text(0, 0.1, "unfamiliar invoice → person or agent → the answer goes back into the graph",
            fontsize=7.8, color=AMBER, style="italic")
    fig.savefig(OUT + "fig07.png"); plt.close(fig)


if __name__ == "__main__":
    import os
    os.makedirs(OUT, exist_ok=True)
    fig_expertise(); fig_compound(); fig_compile(); fig_graph(); fig_hybrid(); fig_paths(); fig_invoice()
