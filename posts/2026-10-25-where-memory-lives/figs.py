"""Figures for "Where Memory Lives". Same style as "Work Has Mass".
Run sim.py first (it writes results.json), then: python figs.py
Each figure is written twice: a vector SVG (used in the page) and a 400 dpi PNG."""
import json
import numpy as np
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
    "savefig.dpi": 400, "savefig.bbox": "tight", "savefig.pad_inches": 0.18,
    "legend.frameon": False,
})
OUT = "figures/"
plt.rcParams["svg.fonttype"] = "path"     # text as outlines: the SVG looks the same everywhere


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


R = json.load(open("results.json"))


def save(fig, name):
    fig.savefig(OUT + name + ".svg")
    fig.savefig(OUT + name + ".png")
    plt.close(fig)


def title(ax, eyebrow, text, y=1.1):
    ax.text(0, y, eyebrow, transform=ax.transAxes, fontsize=7, weight="semibold", color=NAVY)
    ax.text(0, y - 0.06, text, transform=ax.transAxes, fontsize=11.5, weight="semibold", color=INK)


# ---------- Figure 1: four memories, and when you pay for each ----------
def fig_four():
    fig, ax = canvas(11.6, 4.9, 23.2, 9.8)
    cols = [
        ("WEIGHTS", "Parametric memory", "What the model knows:\nlanguage, skills,\nfacts",
         "read in full for\nevery token", NAVY, "every token"),
        ("KV CACHE", "Working memory", "What it is reading now:\nthe prompt,\nthe conversation",
         "grows with the context,\nread for every token", WARM, "every token × context"),
        ("LOOKUP", "External memory", "What it can look up:\ndocuments, records,\npast cases",
         "a few rows, only\nwhen it is asked", GREEN, "per question"),
        ("HABITS", "Compiled memory", "What it has decided before:\nverified answers,\nsmall models",
         "built once,\nreused in milliseconds", "#6b5ca5", "once"),
    ]
    w, gap, x0 = 5.1, 0.6, 0.4
    for i, (eb, t, sub, cost, col, when) in enumerate(cols):
        x = x0 + i * (w + gap)
        card(ax, x, 3.5, w, 4.4, t, sub, accent=col, eyebrow=eb, fs=12, subfs=8.8)
        ax.text(x + w / 2 + 0.12, 2.75, "YOU PAY", ha="center", fontsize=6.6, weight="semibold", color=MUTED)
        ax.text(x + w / 2 + 0.12, 2.35, cost, ha="center", va="top", fontsize=8.6, color=INK, linespacing=1.3)
    # the cost axis
    ax.add_patch(FancyArrowPatch((x0 + 0.2, 0.75), (x0 + 4 * w + 3 * gap - 0.2, 0.75),
                                 arrowstyle="-|>,head_length=0.6,head_width=0.32", mutation_scale=12,
                                 color=MUTED, lw=1.2))
    ax.text(x0 + 0.2, 0.25, "paid on every token", fontsize=8.2, color=MUTED, va="center")
    ax.text(x0 + 4 * w + 3 * gap - 0.2, 0.25, "paid rarely", fontsize=8.2, color=MUTED, va="center", ha="right")
    ax.text(x0, 9.45, "THE FOUR MEMORIES OF A LANGUAGE MODEL", fontsize=7, weight="semibold", color=NAVY)
    ax.text(x0, 9.0, "Fast AI moves what it can to the right", fontsize=12.5, weight="semibold", color=INK, va="top")
    save(fig, "fig01")


# ---------- Figure 2: how many facts fit in the weights ----------
def fig_capacity():
    rows = R["capacity"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.6, 4.4), gridspec_kw=dict(width_ratios=[1.25, 1]))
    widths = sorted({r["hidden"] for r in rows})
    shades = ["#9cb7cc", "#5f8fb3", "#2f6b95", DEEP]
    for h, c in zip(widths, shades):
        rr = [r for r in rows if r["hidden"] == h]
        p = rr[0]["params"]
        x = [r["offered_bits"] / 1e3 for r in rr]
        y = [r["stored_bits"] / 1e3 for r in rr]
        a1.plot(x, y, color=c, lw=2, marker="o", ms=5, mfc="white", mew=1.6)
        a1.annotate(f"{p:,} parameters".replace(",", "\u2009"), (x[-1], y[-1]), xytext=(8, 0),
                    textcoords="offset points", fontsize=8, color=c, va="center", weight="semibold")
    lim = max(r["offered_bits"] for r in rows) / 1e3
    a1.plot([0, lim], [0, lim], color=MUTED, lw=0.9, ls=(0, (3, 3)))
    a1.text(lim * 0.47, lim * 0.5, "every bit offered is kept  ", fontsize=8, color=MUTED, ha="right")
    a1.set_xlim(0, lim * 1.32); a1.set_ylim(0, lim * 0.55)
    a1.set_xlabel("Bits of facts offered (thousands)")
    a1.set_ylabel("Bits of facts stored (thousands)")
    tidy(a1)
    title(a1, "EXPERIMENT 1", "Each network fills up, then stops")

    # right: bits per parameter at the plateau, and accuracy as load grows
    for h, c in zip(widths, shades):
        rr = [r for r in rows if r["hidden"] == h]
        load = [r["offered_bits"] / r["params"] for r in rr]
        a2.plot(load, [r["bits_per_param"] for r in rr], color=c, lw=2, marker="o", ms=5, mfc="white", mew=1.6)
    best = max(r["bits_per_param"] for r in rows)
    a2.axhline(2, color=WARM, lw=1, ls=(0, (2, 2)))
    a2.text(0.45, 2.04, "2 bits per parameter, measured in language models\n(Allen-Zhu & Li, 2024)",
            fontsize=7.8, color=WARM, va="bottom")
    a2.set_xlabel("Bits offered per parameter")
    a2.set_ylabel("Bits stored per parameter")
    a2.set_ylim(0, 2.6); a2.set_xlim(0.3, 4.2)
    tidy(a2)
    title(a2, "THE PLATEAU", f"Up to {best:.1f} bits per parameter")
    fig.subplots_adjust(wspace=0.3)
    save(fig, "fig02")


# ---------- Figure 3: editing a fact in the weights ----------
def fig_editing():
    E = R["editing"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.6, 4.3), sharey=True)
    runs = [("edits only", NAVY, "-"), ("edits only, small steps", "#7fa6c4", (0, (4, 2))),
            ("rehearse everything", WARM, "-")]
    for name, c, ls in runs:
        cv = E[name]["curve"]
        s = [p["step"] for p in cv]
        a1.plot(s, [100 * p["edits"] for p in cv], color=c, lw=2.2, ls=ls)
        a2.plot(s, [100 * p["kept"] for p in cv], color=c, lw=2.2, ls=ls)
        dy = {"rehearse everything": 4, "edits only, small steps": -4}.get(name, 0)
        a2.text(s[-1] + 8, 100 * cv[-1]["kept"] + dy, name, fontsize=8.2, color=c, va="center", weight="semibold")
        a1.text(s[-1] + 8, 100 * cv[-1]["edits"] + (3 if name == "edits only" else -3 if name == "rehearse everything" else 2),
                name, fontsize=8.2, color=c, va="center", weight="semibold")
    for ax in (a1, a2):
        ax.scatter([0], [100 * E["external"]["edits" if ax is a1 else "kept"]], s=90, marker="D",
                   color=GREEN, zorder=6, clip_on=False)
        ax.set_xlabel("Training steps after the change")
        ax.set_xlim(-12, 400); ax.set_ylim(0, 106)
        tidy(ax)
    a1.annotate("external memory: overwrite the row,\nright at once", (0, 100 * E["external"]["edits"]),
                xytext=(30, -40), textcoords="offset points", fontsize=8, color=GREEN, weight="semibold",
                arrowprops=dict(arrowstyle="-", color=GREEN, lw=0.9))
    a1.set_ylabel("Facts right (%)")
    n = E["changed"] + E["new"]
    title(a1, "THE 150 EDITS", f"{E['changed']} facts changed, {E['new']} added")
    title(a2, "EVERYTHING ELSE", f"The other {E['facts'] - E['changed']:,} facts".replace(",", " "))
    fig.subplots_adjust(wspace=0.38, right=0.86)
    save(fig, "fig03")


# ---------- Figure 4: the same facts, looked up ----------
def fig_lookup():
    rows = R["lookup"]
    meth = [("exact", MUTED, "o", "exact: read every key"), ("IVF, 16 clusters", NAVY, "s", "index: 16 nearest clusters"),
            ("IVF, 4 clusters", GREEN, "D", "index: 4 nearest clusters")]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.6, 4.4))
    for m, c, mk, lab in meth:
        rr = [r for r in rows if r["method"] == m]
        n = [r["n"] for r in rr]
        a1.plot(n, [r["ms"] for r in rr], color=c, lw=2, marker=mk, ms=5.5, mfc="white", mew=1.6)
        a2.plot(n, [r["bytes_read"] / 1e6 for r in rr], color=c, lw=2, marker=mk, ms=5.5, mfc="white", mew=1.6)
        a1.text(n[-1] * 1.3, rr[-1]["ms"], lab, fontsize=8, color=c, va="center", weight="semibold")
        for r in rr:
            if r["recall"] < 0.995:
                a1.annotate(f"{r['recall']:.0%}", (r["n"], r["ms"]), xytext=(0, 8), textcoords="offset points",
                            fontsize=7.4, color=c, ha="center")
    for ax in (a1, a2):
        ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_xlabel("Facts in memory")
        tidy(ax, "both")
    a1.set_xlim(6e3, 6e7)
    a1.set_ylabel("Time per question, 4-core CPU (ms)")
    a2.set_ylabel("Megabytes read per question")
    # what the weights of small models read per token, for scale
    for p, lab in ((1.24e9 * 0.5, "Llama 3.2 1B, 4-bit:\nweights read per token"),):
        a2.axhline(p / 1e6, color=WARM, lw=1, ls=(0, (2, 2)))
        a2.text(1.1e4, p / 1e6 * 0.62, lab, fontsize=7.8, color=WARM, va="top")
    a2.set_xlim(6e3, 6e6)
    title(a1, "EXPERIMENT 3", "Looking up stays fast as memory grows")
    title(a2, "WHAT IT COSTS", "An index reads megabytes, not the whole memory")
    fig.subplots_adjust(wspace=0.32)
    save(fig, "fig04")


# ---------- Figure 5: working memory ----------
LLAMA = [  # parameters, layers, key-value heads, head size: from the published model configs
    ("Llama 3.2 1B", 1.24e9, 16, 8, 64),
    ("Llama 3.2 3B", 3.21e9, 28, 8, 128),
    ("Llama 3.1 8B", 8.03e9, 32, 8, 128),
    ("Llama 3.1 70B", 70.6e9, 80, 8, 128),
]


def kv_bytes(L, kv, hd, b=2.0):
    return 2 * L * kv * hd * b


def fig_working():
    rows = R["working"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.6, 4.5), gridspec_kw=dict(width_ratios=[1, 1.15]))
    T = np.array([r["context"] for r in rows])
    att = np.array([r["attention_ms"] for r in rows])
    w = rows[0]["weights_ms"]
    a1.plot(T, att, color=WARM, lw=2.2, marker="o", ms=5, mfc="white", mew=1.6)
    a1.axhline(w, color=NAVY, lw=2.2)
    a1.text(T[0], w * 1.12, "weights of the layer", fontsize=8.2, color=NAVY, weight="semibold")
    a1.text(T[-2] * 1.15, att[-2] * 0.75, "KV cache", fontsize=8.2, color=WARM, weight="semibold", ha="left")
    cross = float(np.exp(np.interp(np.log(w), np.log(att), np.log(T))))
    a1.axvline(cross, color=MUTED, lw=0.9, ls=(0, (2, 2)))
    a1.text(cross * 0.9, att[-1] * 0.95, f"measured crossover\n≈ {cross / 1e3:.0f}k tokens", fontsize=7.8, color=MUTED, va="top", ha="right")
    ratio = rows[0]["weight_numbers"] / (rows[0]["cache_numbers"] / rows[0]["context"])
    a1.axvline(ratio, color=INK, lw=0.9, ls=(0, (1, 2)))
    a1.text(ratio * 0.92, w * 0.32, f"same number of bytes\n≈ {ratio / 1e3:.0f}k tokens", fontsize=7.8, color=INK,
            va="top", ha="right")
    a1.set_xscale("log", base=2); a1.set_yscale("log")
    a1.set_xticks(T); a1.set_xticklabels([f"{t // 1024}k" for t in T])
    a1.set_xlabel("Context length (tokens)")
    a1.set_ylabel("Time per generated token, one layer (ms)")
    tidy(a1, "both")
    title(a1, "EXPERIMENT 4", "One Llama 3.2 1B layer, measured")

    # right: where the crossover sits for each model, by precision
    configs = [("bf16 weights, fp16 cache", 2.0, 2.0, MUTED),
               ("4-bit weights, fp16 cache", 0.5, 2.0, WARM),
               ("4-bit weights, 2-bit cache", 0.5, 0.25, GREEN)]
    y = np.arange(len(LLAMA))
    hgt = 0.24
    for j, (lab, wb, kb, c) in enumerate(configs):
        vals = [p * wb / kv_bytes(L, kv, hd, kb) for _, p, L, kv, hd in LLAMA]
        a2.barh(y + (j - 1) * hgt, vals, height=hgt * 0.9, color=c, label=lab)
        for yy, v in zip(y, vals):
            a2.text(v * 1.08, yy + (j - 1) * hgt, f"{v / 1e3:,.0f}k", va="center", fontsize=7.4, color=c)
    a2.set_xscale("log")
    a2.set_yticks(y); a2.set_yticklabels([m[0] for m in LLAMA])
    a2.invert_yaxis()
    a2.set_xlim(5e3, 1.2e7)
    a2.set_xlabel("Context at which the cache weighs as much as the weights (tokens)")
    a2.legend(loc="upper right", fontsize=7.8, handlelength=1.2)
    tidy(a2, "x")
    title(a2, "BY THE NUMBERS", "Shrink the weights, and the cache takes over")
    fig.subplots_adjust(wspace=0.42)
    save(fig, "fig05")


# ---------- Figure 6: the long tail ----------
def fig_tail():
    F = 1e9
    K = np.logspace(2, 9, 300)

    def H(n, s):
        n = np.asarray(n, float)
        if s == 1:
            return np.log(n) + 0.5772 + 1 / (2 * n)
        return (n ** (1 - s) - 1) / (1 - s) + 0.5772 + 0.5 * n ** (-s)
    fig, ax = plt.subplots(figsize=(10.4, 4.6))
    for s, c, lab in ((0.9, "#9cb7cc", "flatter tail (s = 0.9)"), (1.0, NAVY, "Zipf (s = 1)"),
                      (1.1, DEEP, "steeper tail (s = 1.1)")):
        cov = H(K, s) / H(F, s)
        ax.plot(K, 100 * cov, color=c, lw=2.3 if s == 1 else 1.6)
        k0, dy = {0.9: (3e6, -14), 1.0: (1.5e3, -14), 1.1: (3e6, 10)}[s]
        ax.annotate(lab, (k0, 100 * H(k0, s) / H(F, s)), xytext=(0, dy), textcoords="offset points",
                    fontsize=8, color=c, weight="semibold", va="top" if dy < 0 else "bottom")
    # each tenfold step adds the same slice
    for k in (1e5, 1e6):
        c1, c2 = H(k, 1) / H(F, 1), H(10 * k, 1) / H(F, 1)
        ax.annotate("", (10 * k, 100 * c2), (k, 100 * c1),
                    arrowprops=dict(arrowstyle="-|>", color=WARM, lw=1.4))
    ax.text(1.4e5, 100 * H(1e6, 1) / H(F, 1) + 6, "each 10× more facts\nadds the same ≈ 11 points",
            fontsize=8.2, color=WARM, weight="semibold")
    ax.set_xscale("log")
    ax.set_xlim(1e2, 1.5e9); ax.set_ylim(0, 105)
    ax.set_xlabel("Facts held, most asked first (a world of one billion facts)")
    ax.set_ylabel("Share of questions answered from memory (%)")
    tidy(ax)
    title(ax, "THE ARITHMETIC OF THE LONG TAIL", "Weights cover the head; the tail needs a lookup", y=1.12)
    save(fig, "fig06")


# ---------- Figure 7: a memory design for fast local AI ----------
def fig_design():
    fig, ax = canvas(11.6, 6.0, 23.2, 12.0)
    # centre: the small model
    card(ax, 8.4, 4.3, 6.4, 2.6, "Small model", "language, reasoning, tools\n1–4B parameters, 4-bit", accent=NAVY,
         fill=NAVY, eyebrow="REASONS")
    card(ax, 0.4, 7.3, 6.6, 2.7, "Short working memory", "sliding window, 2-bit cache,\nsummaries instead of transcripts",
         accent=WARM, eyebrow="WORKING")
    card(ax, 0.4, 0.9, 6.6, 2.7, "Indexed external memory", "documents, records, episodes\non flash, editable, deletable",
         accent=GREEN, eyebrow="LOOKUP")
    card(ax, 16.2, 7.3, 6.6, 2.7, "Compiled habits", "verified answers, small trees,\nadapters for each domain",
         accent="#6b5ca5", eyebrow="HABITS")
    card(ax, 16.2, 0.9, 6.6, 2.7, "Slow consolidation", "at night: what repeats becomes\na habit, what is wrong is deleted",
         accent=MUTED, eyebrow="LEARNING")
    arrow(ax, (7.2, 8.4), (8.6, 6.95), color=WARM, rad=-0.1)
    arrow(ax, (7.2, 2.6), (8.6, 4.25), color=GREEN, rad=0.1)
    arrow(ax, (16.0, 8.4), (14.85, 6.95), color="#6b5ca5", rad=0.1)
    arrow(ax, (14.85, 4.25), (16.0, 2.6), color=MUTED, rad=0.1)
    arrow(ax, (19.5, 3.75), (19.5, 7.15), color=MUTED, ls=(0, (3, 2)))
    arrow(ax, (16.0, 1.6), (7.2, 1.6), color=MUTED, ls=(0, (3, 2)), rad=0.0)
    pill(ax, 5.6, 6.3, "bounded per token")
    pill(ax, 5.6, 4.9, "a few rows per question")
    pill(ax, 16.9, 6.3, "checked first: milliseconds")
    pill(ax, 19.5, 4.6, "what repeats")
    pill(ax, 11.6, 1.25, "writes and corrections")
    ax.text(0.4, 11.75, "A PROPOSAL", fontsize=7, weight="semibold", color=NAVY)
    ax.text(0.4, 11.35, "Keep the model small, and give its memories their own places", fontsize=12.5,
            weight="semibold", color=INK, va="top")
    save(fig, "fig07")


if __name__ == "__main__":
    fig_four()
    fig_capacity()
    fig_editing()
    fig_lookup()
    fig_working()
    fig_tail()
    fig_design()
