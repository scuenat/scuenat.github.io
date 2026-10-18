"""Figures for "The Junior Colleague". Style matches the earlier essays.

Numbers in figures 3, 4 and 5 are taken from Zhu et al. (2026), arXiv:2610.21412,
Figure 4b, Tables 1-3. Figures 1, 2 and 6 are schematics or illustrative values of my own.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

NAVY, GREY, RED, LIGHT, PALE, AMBER = "#1f4e79", "#7f8c8d", "#c0392b", "#d5dde5", "#eef1f4", "#d68910"
GREEN = "#2e7d4f"
INK = "#2c3e50"
plt.rcParams.update({
    "font.family": "DejaVu Serif", "font.size": 10, "axes.spines.top": False,
    "axes.spines.right": False, "axes.linewidth": 1.0, "savefig.dpi": 200,
    "savefig.bbox": "tight", "legend.frameon": False, "legend.fontsize": 8.5,
})
OUT = "figures/"


def box(ax, x, y, w, h, title, sub=None, fc=LIGHT, fs=9.5, subfs=8, ec="none", ls="-"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.18",
                                fc=fc, ec=ec, ls=ls, lw=1.2))
    col = "white" if fc in (NAVY, RED, AMBER, GREEN) else INK
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


def fig_two_loops():
    """An agent loop where the LLM makes every choice, and one where a decision model takes the sure ones."""
    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    ax.set_xlim(0, 15); ax.set_ylim(-0.3, 7.2); ax.axis("off")
    choices = ["tool?", "args?", "stop?", "tool?", "args?", "stop?"]
    ax.text(0.1, 7.05, "Today: the large model makes every choice", weight="bold", fontsize=10,
            color=INK, va="top")
    for i, c in enumerate(choices):
        x = 0.4 + i * 2.0
        box(ax, x, 4.6, 1.6, 1.2, "LLM", c, fc=NAVY, fs=9)
        if i < len(choices) - 1:
            arrow(ax, (x + 1.65, 5.2), (x + 1.95, 5.2))
    ax.text(12.6, 5.2, "6 calls\nseconds each", fontsize=8.5, color=RED, style="italic", va="center")
    ax.text(0.1, 3.5, "With a decision model: it answers when sure, the LLM when not",
            weight="bold", fontsize=10, color=INK, va="top")
    sure = [True, True, True, False, True, True]
    for i, (c, s) in enumerate(zip(choices, sure)):
        x = 0.4 + i * 2.0
        if s:
            box(ax, x, 1.1, 1.6, 1.2, "DM", c, fc=GREEN, fs=9)
        else:
            box(ax, x, 1.1, 1.6, 1.2, "DM", "unsure", fc=PALE, fs=9, ec=AMBER)
            box(ax, x, -0.05, 1.6, 0.9, "LLM", None, fc=NAVY, fs=8.5)
            arrow(ax, (x + 0.8, 1.08), (x + 0.8, 0.88), color=AMBER)
        if i < len(choices) - 1:
            arrow(ax, (x + 1.65, 1.7), (x + 1.95, 1.7))
    ax.text(12.6, 1.7, "1 LLM call\nthe rest in ms", fontsize=8.5, color=GREEN, style="italic",
            va="center")
    fig.savefig(OUT + "fig01.png"); plt.close(fig)


def fig_threshold():
    """The threshold rule of Zhu et al.: delegate when c >= q_L - dC/V. Illustrative values."""
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    ratio = np.linspace(0, 0.3, 200)   # dC / V: price of the saved call over the cost of a wrong choice
    for qL, col, ls in [(0.99, NAVY, "-"), (0.95, GREY, "--"), (0.90, AMBER, ":")]:
        ax.plot(ratio, np.clip(qL - ratio, 0, 1), color=col, ls=ls, lw=2,
                label=f"LLM right {qL:.0%} of the time")
    ax.axvline(0.01, color=RED, lw=1, alpha=0.6)
    ax.text(0.013, 0.73, "a $0.01 call\nagainst a $1 task", fontsize=8, color=RED, va="bottom")
    ax.set_xlabel(r"price of the saved LLM call / cost of a wrong choice  ($\Delta C / V$)")
    ax.set_ylabel(r"lowest confidence worth trusting ($\tau$)")
    ax.set_ylim(0.6, 1.005); ax.set_xlim(0, 0.3)
    ax.legend(loc="lower left")
    fig.savefig(OUT + "fig02.png"); plt.close(fig)


def fig_isolated_vs_agent():
    """Isolated accuracy (L1) against task success inside a running agent (L3). Zhu et al., Fig. 4b."""
    data = [  # name, L1 isolated %, L3 task success % on shifted DecisionGym tasks
        ("AgentDecision-4B", 89.3, 91.5, GREEN), ("AgentDecision-0.8B", 87.1, 82.0, GREEN),
        ("Jev", 89.9, 82.0, NAVY), ("OpenAI Decisions", 90.6, 66.0, GREY),
        ("OpenJev-27B", 90.2, 69.5, GREY), ("StartLux-27B", 90.8, 79.9, GREY),
        ("StartLux-9B", 92.2, 69.5, GREY), ("StartLux-4B", 91.3, 49.0, GREY),
        ("Intern-Decision-4B", 88.2, 34.0, GREY),
    ]
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    offs = {"AgentDecision-4B": (-0.15, 2.5, "right"), "AgentDecision-0.8B": (0.0, -5.5, "left"),
            "Jev": (0.15, -4.5, "left"), "OpenAI Decisions": (0.0, -5.0, "center"),
            "OpenJev-27B": (-0.15, 2.0, "right"), "StartLux-27B": (0.15, 1.5, "left"),
            "StartLux-9B": (0.0, 2.5, "center"), "StartLux-4B": (0.15, -1.5, "left"),
            "Intern-Decision-4B": (0.15, -1.5, "left")}
    for n, x, y, c in data:
        ax.scatter(x, y, s=55, color=c, zorder=3)
        dx, dy, ha = offs[n]
        ax.text(x + dx, y + dy, n, fontsize=8, color=c if c != GREY else INK, ha=ha)
    ax.set_xlabel("accuracy on isolated questions (%)")
    ax.set_ylabel("tasks solved inside the agent (%)")
    ax.set_xlim(86.5, 93.2); ax.set_ylim(28, 98)
    ax.text(90.3, 38, "a 5-point spread in isolation becomes\na 57-point spread inside the agent",
            fontsize=8, color=RED, style="italic")
    fig.savefig(OUT + "fig03.png"); plt.close(fig)


def fig_training():
    """Task success on shifted tasks, before and after training on the agent's own states. Zhu et al., Table 3."""
    rows = [("Qwen3-4B, untrained", 13.5, GREY), ("+ SFT on the agent's states", 96.0, GREEN),
            ("+ GRPO in the loop", 96.0, GREEN), ("+ public tool-use data\n= AgentDecision-4B", 91.5, GREEN),
            ("Jev (the teacher)", 82.0, NAVY), ("StartLux-4B, off the shelf", 49.0, GREY),
            ("StartLux-4B + this recipe", 98.0, GREEN), ("Intern-Decision-4B", 34.0, GREY)]
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    y = np.arange(len(rows))[::-1]
    ax.barh(y, [r[1] for r in rows], color=[r[2] for r in rows], height=0.62)
    for yi, (n, v, c) in zip(y, rows):
        ax.text(v + 1, yi, f"{v:.1f}%", va="center", fontsize=8.5, color=INK)
    ax.set_yticks(y); ax.set_yticklabels([r[0] for r in rows], fontsize=8.5)
    ax.set_xlim(0, 108); ax.set_xlabel("tasks solved on shifted DecisionGym tasks (%)")
    ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0)
    fig.savefig(OUT + "fig04.png"); plt.close(fig)


def fig_where_it_pays():
    """Cost saved and change in success by setting. Zhu et al., Tables 1 and 2."""
    rows = [  # setting, cost saved %, change in success (points)
        ("Customer service\n(4B, own GPU)", 86.3, "+0.5 pt, 2.5x faster"),
        ("ALFWorld text games\n(4B trained there)", 89.0, "+4.3 pt, ~2x faster"),
        ("Hard tasks, new rule\n(Jev, refitted)", 30.5, "+2.0 pt, slower"),
        ("Coding agents\n(strong or fast LLM)", 10.5, "-6.0 to +7.9 pt"),
    ]
    fig, ax = plt.subplots(figsize=(6.4, 3.2))
    y = np.arange(len(rows))[::-1]
    cols = [GREEN, GREEN, AMBER, GREY]
    ax.barh(y, [r[1] for r in rows], color=cols, height=0.6)
    for yi, (n, v, d) in zip(y, rows):
        lab = f"{v:.1f}%" if "Coding" not in n else "7.0-10.5%"
        ax.text(v + 1.5, yi, f"{lab}   {d}", va="center", fontsize=8.5, color=INK)
    ax.set_yticks(y); ax.set_yticklabels([r[0] for r in rows], fontsize=8.5)
    ax.set_xlim(0, 135); ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("LLM cost saved (%)")
    ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0)
    fig.savefig(OUT + "fig05.png"); plt.close(fig)


def fig_fast_ai_loop():
    """Fast AI with a decision model: shadow, fit, delegate, log, retrain, refit."""
    fig, ax = plt.subplots(figsize=(7.4, 4.0))
    ax.set_xlim(0, 15); ax.set_ylim(0, 8.2); ax.axis("off")
    box(ax, 0.2, 5.6, 2.6, 1.4, "Choice", "options listed", fc=PALE)
    box(ax, 4.0, 5.6, 3.2, 1.4, "Decision model", "small, on one GPU", fc=GREEN)
    arrow(ax, (2.85, 6.3), (3.95, 6.3))
    box(ax, 8.8, 6.4, 3.0, 1.1, "Fast path", "confident enough", fc=LIGHT, fs=9)
    box(ax, 8.8, 4.6, 3.0, 1.1, "Slow path", "LLM, agent, person", fc=NAVY, fs=9)
    arrow(ax, (7.25, 6.5), (8.75, 6.95), color=GREEN)
    arrow(ax, (7.25, 6.1), (8.75, 5.15), color=AMBER)
    box(ax, 12.6, 5.5, 2.2, 1.2, "Action", None, fc=PALE)
    arrow(ax, (11.85, 6.95), (12.55, 6.3)); arrow(ax, (11.85, 5.15), (12.55, 5.9))
    # learning loop
    box(ax, 9.0, 1.8, 2.6, 1.3, "Logs", "states, deferrals,\nmistakes", fc=PALE, subfs=7.5)
    box(ax, 3.7, 1.8, 3.8, 1.3, "Retrain + refit", "on the agent's own states", fc=AMBER)
    box(ax, 0.0, 1.8, 3.0, 1.3, "Shadow mode", "test before trusting", fc=LIGHT, fs=9, subfs=7.5)
    arrow(ax, (10.3, 4.55), (10.3, 3.15), color=GREY, ls="--")
    arrow(ax, (8.95, 2.45), (7.55, 2.45), color=GREY, ls="--")
    arrow(ax, (3.65, 2.45), (3.05, 2.45), color=GREY, ls="--")
    arrow(ax, (1.5, 3.15), (4.6, 5.55), color=GREY, ls="--", rad=-0.2)
    ax.text(7.5, 0.6, "the slow path's answers become the fast path's next habits",
            ha="center", fontsize=8.5, color=INK, style="italic")
    fig.savefig(OUT + "fig06.png"); plt.close(fig)


if __name__ == "__main__":
    import os
    os.makedirs(OUT, exist_ok=True)
    fig_two_loops(); fig_threshold(); fig_isolated_vs_agent()
    fig_training(); fig_where_it_pays(); fig_fast_ai_loop()
