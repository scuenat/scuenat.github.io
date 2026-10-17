"""Figures for "An Ecosystem, Not an Oracle". Style matches the earlier essays."""
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


def box(ax, x, y, w, h, title, sub=None, fc=LIGHT, fs=9.5, subfs=8, ec="none", ls="-"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.18",
                                fc=fc, ec=ec, ls=ls, lw=1.2))
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


def fig_oracle_ecosystem():
    """One general model for every task, or a router and small specialists."""
    fig, ax = plt.subplots(figsize=(7.0, 3.4))
    ax.set_xlim(0, 14.2); ax.set_ylim(0, 6.6); ax.axis("off")
    tasks = ["read a drawing", "write code", "answer an email", "check a contract"]
    ax.text(0.1, 6.45, "An oracle", weight="bold", fontsize=10, color=INK, va="top")
    ax.text(7.5, 6.45, "An ecosystem", weight="bold", fontsize=10, color=INK, va="top")
    # oracle
    for i, t in enumerate(tasks):
        y = 4.9 - i * 1.25
        box(ax, 0.1, y, 2.5, 0.85, t, None, fc=PALE, fs=8)
        arrow(ax, (2.65, y + 0.42), (3.85, 2.9), rad=0.0)
    box(ax, 3.9, 1.7, 2.8, 2.4, "One large\nmodel", None, fc=NAVY, fs=10)
    ax.text(5.3, 1.25, "every request pays\nfor everything it knows", ha="center", va="top",
            fontsize=8, color=RED, style="italic")
    # workshop
    box(ax, 7.6, 2.35, 1.7, 1.1, "Router", None, fc=NAVY, fs=9)
    specs = ["drawings", "code", "email", "contracts"]
    for i, (t, s) in enumerate(zip(tasks, specs)):
        y = 4.9 - i * 1.25
        arrow(ax, (9.35, 2.9), (10.35, y + 0.42), color=NAVY)
        box(ax, 10.4, y, 1.75, 0.85, s, None, fc=LIGHT, fs=8.5)
        arrow(ax, (12.2, y + 0.42), (12.75, y + 0.42), color=GREY, lw=1.0)
    box(ax, 12.8, 1.15, 1.3, 4.6, "", None, fc=PALE)
    ax.text(13.45, 3.45, "shared\nmemory", ha="center", va="center", rotation=90, fontsize=8.5,
            color=INK, weight="bold")
    ax.text(9.6, 0.15, "small, narrow, replaceable,\neach one testable on its own job",
            ha="left", va="bottom", fontsize=8, color=NAVY, style="italic")
    fig.savefig(OUT + "fig01.png"); plt.close(fig)


def fig_ecosystem():
    """The local ecosystem: router, specialists, memory, consolidation, and the big model outside."""
    fig, ax = plt.subplots(figsize=(7.6, 4.4))
    ax.set_xlim(0, 15.4); ax.set_ylim(0, 9.0); ax.axis("off")
    # machine boundary
    ax.add_patch(FancyBboxPatch((0.1, 0.1), 11.6, 8.7, boxstyle="round,pad=0.02,rounding_size=0.3",
                                fc="none", ec=GREY, lw=1.2, ls="--"))
    ax.text(0.4, 8.5, "your machine", fontsize=8.5, color=GREY, style="italic", va="top")
    box(ax, 0.5, 6.4, 2.2, 1.2, "You", "a task", fc=PALE)
    box(ax, 3.4, 6.4, 2.6, 1.2, "Router", "who does what?", fc=NAVY)
    arrow(ax, (2.75, 7.0), (3.35, 7.0))
    names = ["Vision", "Language", "Planner", "Domain"]
    for i, n in enumerate(names):
        x = 0.5 + i * 2.5
        box(ax, x, 4.0, 2.1, 1.1, n, "specialist", fc=LIGHT)
        arrow(ax, (4.7, 6.35), (x + 1.05, 5.15), color=NAVY, lw=1.1)
    box(ax, 0.5, 1.9, 9.6, 1.3, "", None, fc=PALE)
    ax.text(5.3, 2.85, "Shared memory", ha="center", va="center", weight="bold", fontsize=9.5, color=INK)
    ax.text(5.3, 2.3, "knowledge: facts, rules  ·  episodes: what happened, what was corrected",
            ha="center", va="center", style="italic", fontsize=7.5, color=INK)
    for i in range(4):
        x = 0.5 + i * 2.5 + 1.05
        arrow(ax, (x - 0.25, 3.95), (x - 0.25, 3.25), color=GREY, lw=1.0)
        arrow(ax, (x + 0.25, 3.25), (x + 0.25, 3.95), color=GREY, lw=1.0)
    box(ax, 0.5, 0.4, 9.6, 1.0, "Nightly consolidation", "learn from episodes · test · keep or roll back",
        fc=AMBER, subfs=7.5)
    ax.annotate("", xy=(9.7, 3.95), xytext=(10.35, 0.9),
                arrowprops=dict(arrowstyle="-|>", color=AMBER, lw=1.6,
                                connectionstyle="arc3,rad=0.35"))
    ax.text(10.8, 1.5, "updated\nspecialists", fontsize=7.5, color=AMBER, va="center")
    # big model outside
    box(ax, 12.4, 5.6, 2.9, 2.2, "Frontier\nmodel", None, fc=GREY, fs=9.5)
    ax.text(13.85, 5.3, "teacher, once\nconsultant, rarely", ha="center", va="top", fontsize=8,
            color=GREY, style="italic")
    arrow(ax, (6.05, 7.1), (12.35, 7.1), color=GREY, ls="--", lw=1.1)
    ax.text(9.2, 7.3, "only for the new,\nwith permission", ha="center", fontsize=7.5, color=GREY,
            style="italic")
    arrow(ax, (12.35, 6.0), (9.0, 5.15), color=GREY, ls="--", lw=1.1, rad=0.15)
    ax.text(11.1, 6.2, "distils", fontsize=7.5, color=GREY, style="italic", ha="center")
    fig.savefig(OUT + "fig02.png"); plt.close(fig)


def fig_memory():
    """What lives in the weights versus in a shared memory."""
    rows = ["readable by a person", "correctable in one place", "deletable, for real",
            "shared by every specialist", "stays on your machine"]
    weights = [False, False, False, False, None]
    memory = [True, True, True, True, True]
    fig, ax = plt.subplots(figsize=(5.6, 2.8))
    ax.set_xlim(0, 10); ax.set_ylim(-0.4, len(rows) + 0.9); ax.axis("off")
    ax.text(6.3, len(rows) + 0.35, "in the weights", ha="center", weight="bold", fontsize=9, color=INK)
    ax.text(8.6, len(rows) + 0.35, "in a shared\nmemory", ha="center", weight="bold", fontsize=9,
            color=NAVY, va="center")
    for i, r in enumerate(rows):
        y = len(rows) - 1 - i + 0.2
        if i % 2 == 0:
            ax.add_patch(plt.Rectangle((0, y - 0.42), 10, 0.84, fc=PALE, ec="none"))
        ax.text(0.2, y, r, va="center", fontsize=9, color=INK)
        for x, v in [(6.3, weights[i]), (8.6, memory[i])]:
            if v is True:
                ax.text(x, y, "yes", ha="center", va="center", color=NAVY, weight="bold", fontsize=9)
            elif v is False:
                ax.text(x, y, "hardly", ha="center", va="center", color=RED, fontsize=9)
            else:
                ax.text(x, y, "if local", ha="center", va="center", color=GREY, fontsize=9)
    fig.savefig(OUT + "fig12.png"); plt.close(fig)


def fig_day_night():
    """Schematic: a specialist improves in small nightly steps; a bad update is tested and rolled back."""
    rng = np.random.default_rng(3)
    days = np.arange(0, 31)
    skill = [60.0]
    rejected = 17
    for d in days[1:]:
        gain = max(0.0, 1.6 * np.exp(-d / 14) + rng.normal(0.15, 0.25))
        skill.append(skill[-1] + (0.0 if d == rejected + 1 else gain))
    skill = np.array(skill)
    fig, ax = plt.subplots(figsize=(5.6, 2.9))
    for d in days[1:]:
        ax.axvspan(d - 0.3, d, color=PALE, lw=0)
    ax.step(days, skill, where="post", color=NAVY, lw=2.2, label="specialist in use")
    ax.plot([rejected, rejected + 0.6], [skill[rejected], skill[rejected] - 4.5], color=RED, lw=1.6)
    ax.plot([rejected + 0.6], [skill[rejected] - 4.5], "x", color=RED, ms=7, mew=2)
    ax.annotate("night 17: the update forgot\nan old skill; the test caught it,\nrolled back",
                xy=(rejected + 0.6, skill[rejected] - 4.5), xytext=(19.5, skill[rejected] - 9.5),
                fontsize=8, color=RED, arrowprops=dict(arrowstyle="-", color=RED, lw=0.9))
    ax.axhline(skill[0], color=GREY, ls=":", lw=1.2)
    ax.text(30, skill[0] + 0.6, "frozen model", ha="right", fontsize=8, color=GREY)
    ax.text(0.5, skill[-1] + 1.0, "small, tested steps, every night", fontsize=8, color=NAVY)
    ax.set_xlim(0, 30); ax.set_ylim(skill[0] - 14, skill[-1] + 4)
    ax.set_yticks([])
    ax.set_xlabel("days in use (shaded: nights)")
    ax.set_ylabel("quality on its job")
    fig.savefig(OUT + "fig13.png"); plt.close(fig)


def fig_three_architectures():
    """Dense, mixture of experts, ecosystem: what must be loaded, and what works on each request."""
    fig, ax = plt.subplots(figsize=(7.2, 3.3))
    ax.set_xlim(0, 15); ax.set_ylim(0, 6.6); ax.axis("off")
    titles = [("Dense model", "everything loaded,\neverything works"),
              ("Mixture of experts", "everything loaded,\na few experts work"),
              ("Ecosystem", "separate models, loaded when needed,\none specialist works")]
    rng = np.random.default_rng(7)
    for k, (t, sub) in enumerate(titles):
        x0 = 0.3 + k * 5.0
        ax.text(x0 + 2.1, 6.35, t, ha="center", va="top", weight="bold", fontsize=9.5, color=INK)
        ax.text(x0 + 2.1, 0.55, sub, ha="center", va="center", fontsize=8, color=GREY, style="italic")
        if k < 2:
            ax.add_patch(FancyBboxPatch((x0, 1.3), 4.2, 4.4, boxstyle="round,pad=0.02,rounding_size=0.2",
                                        fc="none", ec=GREY, lw=1.0, ls="--"))
            ax.text(x0 + 4.1, 1.45, "one model", ha="right", fontsize=7, color=GREY, style="italic")
        active = set(range(48)) if k == 0 else set(rng.choice(48, 6, replace=False))
        if k < 2:
            for i in range(48):
                r, c = divmod(i, 8)
                fc = NAVY if i in active else LIGHT
                ax.add_patch(FancyBboxPatch((x0 + 0.25 + c * 0.47, 1.85 + r * 0.6), 0.36, 0.45,
                                            boxstyle="round,pad=0.01,rounding_size=0.06", fc=fc, ec="none"))
        else:
            labels = ["drawings", "code", "email", "contracts", "speech", "vision"]
            for i, lab in enumerate(labels):
                r, c = divmod(i, 2)
                fc = NAVY if lab == "drawings" else (LIGHT if i < 4 else PALE)
                box(ax, x0 + 0.1 + c * 2.15, 4.35 - r * 1.35, 1.95, 0.95, lab, None, fc=fc, fs=8)
    fig.savefig(OUT + "fig03.png"); plt.close(fig)


def fig_bandwidth():
    """Upper bound on generation speed when memory bandwidth is the limit, at 4-bit weights."""
    bw = 500.0          # GB/s, a high-end laptop with unified memory
    ram = 128.0         # GB
    n = np.logspace(np.log10(1), np.log10(800), 300)    # billions of parameters read per token
    tps = bw / (0.5 * n)
    fig, ax = plt.subplots(figsize=(5.8, 3.2))
    ax.plot(n, tps, color=GREY, lw=1.6)
    pts = [("3B specialist", 3, 3, NAVY), ("8B specialist", 8, 8, NAVY),
           ("70B dense", 70, 70, INK), ("MoE: 37B active,\n671B total", 37, 671, RED)]
    for lab, active, total, c in pts:
        y = bw / (0.5 * active)
        fits = total * 0.5 <= ram
        ax.plot([active], [y], "o", color=c, ms=7, mfc=c if fits else "white", mew=1.8, zorder=5)
        dx, ha = (1.25, "left")
        ax.text(active * dx, y * 1.12, lab, fontsize=8, color=c, ha=ha, va="bottom")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(1, 800); ax.set_ylim(1, 600)
    ax.set_xlabel("billions of parameters read per token (4-bit)")
    ax.set_ylabel("tokens per second\n(upper bound)")
    ax.text(780, 1.3, "open circle: does not fit in 128 GB\nbandwidth 500 GB/s; ignores compute and cache",
            ha="right", va="bottom", fontsize=7.2, color=GREY, style="italic")
    fig.savefig(OUT + "fig05.png"); plt.close(fig)


def fig_brain():
    """How the brain seems to be organised, and the part of the ecosystem each idea maps to."""
    rows = [("Many specialised areas", "faces, language, motion, movement", "Specialists"),
            ("A domain-general network", "engaged by many demanding tasks", "Shared core + router"),
            ("Hippocampus: learns fast", "records new episodes quickly", "Shared memory"),
            ("Cortex: learns slowly", "replays and consolidates during sleep", "Nightly consolidation"),
            ("Plasticity", "connections change with use, areas are reused", "Specialists that adapt"),
            ("About 20 watts", "only a small part strongly active at once", "Small, sparse, local")]
    fig, ax = plt.subplots(figsize=(7.0, 3.6))
    ax.set_xlim(0, 14); ax.set_ylim(-0.3, len(rows) * 1.0 + 0.8); ax.axis("off")
    ax.text(0.2, len(rows) + 0.45, "In the brain", weight="bold", fontsize=9.5, color=INK)
    ax.text(10.1, len(rows) + 0.45, "In the ecosystem", weight="bold", fontsize=9.5, color=NAVY)
    for i, (a, b, c) in enumerate(rows):
        y = len(rows) - 1 - i
        box(ax, 0.1, y + 0.08, 8.0, 0.84, "", None, fc=PALE)
        ax.text(0.35, y + 0.62, a, fontsize=8.6, weight="bold", color=INK, va="center")
        ax.text(0.35, y + 0.3, b, fontsize=7.6, style="italic", color=INK, va="center")
        arrow(ax, (8.25, y + 0.5), (9.85, y + 0.5), color=GREY, lw=1.1)
        box(ax, 10.0, y + 0.13, 3.9, 0.74, c, None, fc=AMBER if "Nightly" in c else NAVY,
            fs=8.3)
    fig.savefig(OUT + "fig11.png"); plt.close(fig)



def fig_active_fraction():
    """Share of parameters (or neurons) that work on each word, from published figures."""
    items = [("Dense model", 100.0, INK, ""),
             ("Mixtral 8x7B\n12.9B of 46.7B", 12.9 / 46.7 * 100, NAVY, ""),
             ("DeepSeek-V3\n37B of 671B", 37 / 671 * 100, NAVY, ""),
             ("Cortex, estimate\n(Lennie 2003)", 1.0, AMBER, "//")]
    fig, ax = plt.subplots(figsize=(5.6, 2.7))
    for i, (lab, v, c, h) in enumerate(items):
        y = len(items) - 1 - i
        ax.barh(y, v, color=c if not h else "white", edgecolor=c, hatch=h, height=0.6, lw=1.2)
        ax.text(v + 1.5, y, f"~{v:.0f}%" if h else f"{v:.1f}%".replace(".0%", "%"), va="center",
                fontsize=8.5, color=c)
    ax.set_yticks(range(len(items))); ax.set_yticklabels([it[0] for it in items][::-1], fontsize=8.3)
    ax.set_xlim(0, 112); ax.set_xlabel("share active for each word or moment (%)")
    fig.savefig(OUT + "fig04.png"); plt.close(fig)


def fig_capacity():
    """Simple capacity model: parameters a general model needs to match a specialist on one domain."""
    n_shared, n_dom = 2.0, 1.0           # billions, illustrative
    f = np.logspace(-3, 0, 300)
    gen = n_shared + n_dom / f
    fig, ax = plt.subplots(figsize=(5.6, 3.0))
    ax.plot(f * 100, gen, color=NAVY, lw=2.2, label="general model: $N_{shared} + N_{domain}/f$")
    ax.axhline(n_shared + n_dom, color=AMBER, lw=2.0, label="specialist: $N_{shared} + N_{domain}$")
    ax.plot([1], [n_shared + n_dom / 0.01], "o", color=RED, ms=6, zorder=5)
    ax.annotate("domain is 1% of its training mix:\n~102B vs 3B", xy=(1, 102), xytext=(0.13, 12),
                fontsize=8, color=RED, arrowprops=dict(arrowstyle="-", color=RED, lw=0.9))
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(0.1, 100); ax.set_ylim(1, 2000)
    ax.set_xlabel("share $f$ of the general model's training devoted to the domain (%)")
    ax.set_ylabel("parameters needed\n(billions)")
    ax.legend(loc="upper right", bbox_to_anchor=(1.0, 0.72))
    ax.text(0.11, 1.15, "illustrative: $N_{shared}$ = 2B, $N_{domain}$ = 1B, no transfer beyond the shared core",
            fontsize=7, color=GREY, style="italic")
    fig.savefig(OUT + "fig06.png"); plt.close(fig)


def fig_adapters():
    """Storage for k specialists: separate small models versus one shared base plus adapters."""
    k = np.arange(1, 101)
    base = 3e9 * 0.5 / 1e9                 # 3B parameters at 4 bits, GB
    adapter = 30e6 * 2 / 1e9               # ~1% of 3B at 16 bits, GB
    fig, ax = plt.subplots(figsize=(5.6, 2.9))
    ax.plot(k, k * base, color=GREY, lw=2.0, ls="--", label="separate 3B models (4-bit)")
    ax.plot(k, base + k * adapter, color=NAVY, lw=2.4, label="one 3B base + rank-16 adapters")
    ax.axhline(128, color=RED, lw=1.0, ls=":")
    ax.text(99, 131, "128 GB", ha="right", fontsize=8, color=RED)
    ax.annotate(f"100 specialists: {base + 100 * adapter:.1f} GB", xy=(100, base + 100 * adapter),
                xytext=(48, 40), fontsize=8, color=NAVY,
                arrowprops=dict(arrowstyle="-", color=NAVY, lw=0.9))
    ax.set_xlim(1, 100); ax.set_ylim(0, 160)
    ax.set_xlabel("number of specialists $k$")
    ax.set_ylabel("memory (GB)")
    ax.legend(loc="upper left")
    fig.savefig(OUT + "fig07.png"); plt.close(fig)


def fig_router():
    """Expected quality of an ecosystem as a function of router accuracy (illustrative values)."""
    a = np.linspace(0.5, 1.0, 200)
    qs, qw, qg, ql = 0.90, 0.30, 0.80, 0.95
    plain = a * qs + (1 - a) * qw
    esc = a * qs + (1 - a) * (0.5 * ql + 0.5 * qw)
    fig, ax = plt.subplots(figsize=(5.6, 3.0))
    ax.plot(a * 100, plain, color=GREY, lw=2.0, ls="--", label="router alone")
    ax.plot(a * 100, esc, color=NAVY, lw=2.4, label="router that escalates half its mistakes")
    ax.axhline(qg, color=AMBER, lw=1.8, label="one general model, similar speed")
    for q, c in [(plain, GREY), (esc, NAVY)]:
        i = np.argmin(abs(q - qg))
        ax.plot([a[i] * 100], [qg], "o", color=c, ms=6, zorder=5)
        ax.text(a[i] * 100, qg - 0.035, f"{a[i] * 100:.0f}%", ha="center", va="top", fontsize=8, color=c)
    ax.set_xlim(50, 100); ax.set_ylim(0.55, 0.95)
    ax.set_xlabel("router accuracy $a$ (%)")
    ax.set_ylabel("expected quality")
    ax.legend(loc="lower right")
    ax.text(51, 0.92, "illustrative: $q_s$ = 0.90, $q_w$ = 0.30, $q_g$ = 0.80, $q_L$ = 0.95",
            fontsize=7, color=GREY, style="italic")
    fig.savefig(OUT + "fig08.png"); plt.close(fig)


def fig_sampling():
    """Repeated sampling with a verifier: independent-attempt formula versus a published result."""
    p = 0.159
    k = np.logspace(0, np.log10(250), 300)
    fig, ax = plt.subplots(figsize=(5.6, 2.9))
    ax.plot(k, 100 * (1 - (1 - p) ** k), color=GREY, lw=1.8, ls="--",
            label="if attempts were independent: $1-(1-p)^k$")
    ax.plot([1, 250], [15.9, 56.0], "o", color=NAVY, ms=7, zorder=5,
            label="reported (Brown et al. 2024)")
    ax.annotate("15.9% with one attempt", xy=(1, 15.9), xytext=(1.4, 4), fontsize=8, color=NAVY)
    ax.annotate("56% with 250 attempts,\nchecked by the tests", xy=(250, 56), xytext=(22, 63),
                fontsize=8, color=NAVY, arrowprops=dict(arrowstyle="-", color=NAVY, lw=0.9))
    ax.axhline(43, color=AMBER, lw=1.2, ls=":")
    ax.text(290, 38.5, "best single attempt reported at the time: 43%", fontsize=7.5, color=AMBER, ha="right")
    ax.set_xscale("log"); ax.set_xlim(1, 300); ax.set_ylim(0, 105)
    ax.set_xlabel("attempts $k$")
    ax.set_ylabel("issues solved (%)")
    ax.legend(loc="upper left", bbox_to_anchor=(0.0, 0.93))
    fig.savefig(OUT + "fig09.png"); plt.close(fig)


def fig_harness():
    """Schematic hypothesis: the value of a harness falls as the model gets stronger, except the parts
    no model can absorb."""
    x = np.linspace(0, 10, 300)
    scaffold = 8.5 * np.exp(-x / 2.6)
    structural = np.full_like(x, 2.2)
    fig, ax = plt.subplots(figsize=(5.6, 2.9))
    ax.plot(x, scaffold, color=NAVY, lw=2.2, label="scaffolding for reasoning\n(orchestrators, sub-agents, retries)")
    ax.plot(x, structural, color=AMBER, lw=2.2,
            label="structure no model can absorb\n(memory, permissions, tests, local data)")
    ax.axvspan(8.3, 10, color=PALE, lw=0)
    ax.text(9.15, 7.6, "frontier\nmodels", ha="center", fontsize=8, color=INK)
    ax.text(9.15, 5.4, "scaffolding\nadds little", ha="center", fontsize=7.5, color=RED)
    ax.text(1.5, 7.2, "scaffolding\nstill helps", ha="center", fontsize=7.5, color=NAVY)
    ax.axvspan(0, 3.0, color=PALE, lw=0)
    ax.text(1.5, 9.4, "small local\nspecialists", ha="center", fontsize=8, color=INK, va="top")
    ax.set_xlim(0, 10); ax.set_ylim(0, 10)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_xlabel("strength of the model")
    ax.set_ylabel("what the harness adds")
    ax.legend(loc="center", bbox_to_anchor=(0.52, 0.62), fontsize=7.8)
    fig.savefig(OUT + "fig10.png"); plt.close(fig)


if __name__ == "__main__":
    fig_oracle_ecosystem()
    fig_ecosystem()
    fig_three_architectures()
    fig_active_fraction()
    fig_bandwidth()
    fig_capacity()
    fig_adapters()
    fig_router()
    fig_sampling()
    fig_harness()
    fig_brain()
    fig_memory()
    fig_day_night()
