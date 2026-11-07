"""Figures for "A Finite State of Mind".

Same style as "The Teacher Who Writes the Weights": Inter type, white cards with a faint
shadow and a coloured accent, colours taken from the site's palette.

Figure 1 computes the KV cache of one sequence for a Llama 3 8B-shaped model (32 layers,
32 query heads, head dimension 128, FP16), for three attention layouts and five context
lengths. The arithmetic is below; the model shape is from the Llama 3 paper.
Figure 2 plots Table 2 of Belcak et al. (2026), "You don't need long context".
Figure 3 plots the acceleration numbers stated in Hermle et al. (2026), "AI for scientific
discovery: How researchers use Claude".
Figure 4 is a schematic of my own: the paper's compaction recap next to a lab notebook.
"""
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




# ---------- Figure 1: KV cache per sequence ----------
LAYERS, QHEADS, HEAD_DIM, BYTES = 32, 32, 128, 2          # Llama 3 8B shape, FP16 cache
LAYOUTS = [("MHA", 32), ("GQA", 8), ("MQA", 1)]          # number of K/V heads
CONTEXTS = [("256K", 262144), ("128K", 131072), ("32K", 32768), ("16K", 16384), ("8K", 8192)]
FREE_GIB = 64                                            # cache budget left on an 80 GB GPU (assumption)


def kv_bytes_per_token(kv_heads):
    return 2 * LAYERS * kv_heads * HEAD_DIM * BYTES      # K and V, every layer, every K/V head


def fig_kv():
    # rows: tokens kept; columns: attention layout (narrow enough for a phone)
    gib = np.array([[kv_bytes_per_token(h) * n / 2**30 for _, h in LAYOUTS] for _, n in CONTEXTS])
    fig, ax = plt.subplots(figsize=(5.6, 5.6))
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("c", [GREEN_T, AMBER_T, "#f3c9a8", "#e3a08f"])
    ax.imshow(np.log2(gib), cmap=cmap, aspect="auto", vmin=np.log2(0.1), vmax=np.log2(128))
    for i in range(gib.shape[0]):
        for j in range(gib.shape[1]):
            v = gib[i, j]
            txt = f"{v:.0f} GiB" if v >= 1 else f"{v * 1024:.0f} MiB"
            n = int(FREE_GIB // v)
            sub = "does not fit" if n == 0 else f"{n:,} at once"
            ax.text(j, i - 0.13, txt, ha="center", va="center", fontsize=11, weight="semibold", color=INK)
            ax.text(j, i + 0.22, sub, ha="center", va="center", fontsize=8.6, color=MUTED)
    ax.xaxis.tick_top()
    ax.set_xticks(range(len(LAYOUTS)),
                  [f"{n}\n{h} K/V head{'s' if h > 1 else ''}\n{kv_bytes_per_token(h) // 1024} KiB/token"
                   for n, h in LAYOUTS], fontsize=8.8)
    ax.set_yticks(range(len(CONTEXTS)), [c for c, _ in CONTEXTS], fontsize=9.5)
    ax.set_ylabel("Tokens kept in context", fontsize=8.8, color=MUTED)
    ax.tick_params(length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_title("KV cache of one sequence (Llama 3 8B shape, FP16)\nand how many fit in 64 GiB at once",
                 loc="left", fontsize=10.5, weight="semibold", pad=12)
    fig.tight_layout()
    fig.savefig(OUT + "fig01.png", dpi=400); fig.savefig(OUT + "fig01.svg"); plt.close(fig)


# ---------- Figure 2: Table 2 of Belcak et al. (2026) ----------
T2 = [  # (label, accuracy FHA, best EoCC, SAC), (peak median, max) for FHA, EoCC, SAC
    ("Opus 4.5\nSWE-V", (70.0, 74.8, 70.2), ((32, 200), (19, 22), (8, 16))),
    ("Opus 4.5\nTB 2.1", (47.2, 52.8, 51.8), ((27, 130), (24, 31), (9, 19))),
    ("GPT 5.6\nSWE-V", (84.4, 88.8, 82.4), ((18, 173), (22, 35), (7, 15))),
    ("GPT 5.6\nTB 2.1", (87.6, 88.8, 84.3), ((17, 133), (23, 40), (8, 37))),
]
REGIMES = [("Full history", MUTED), ("Best compaction", NAVY), ("One action per context", WARM)]


def fig_nvidia():
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(5.8, 7.4))
    xs = np.arange(len(T2)); w = 0.26
    for k, (name, col) in enumerate(REGIMES):
        acc = [r[1][k] for r in T2]
        a1.bar(xs + (k - 1) * w, acc, width=w, color=col, edgecolor=BG, linewidth=1.5, label=name)
        for x, v in zip(xs + (k - 1) * w, acc):
            a1.text(x, v + 1.2, f"{v:.0f}", ha="center", va="bottom", fontsize=6.8, color=INK)
        med = [r[2][k][0] for r in T2]; mx = [r[2][k][1] for r in T2]
        xx = xs + (k - 1) * w
        a2.vlines(xx, med, mx, color=col, lw=2.2, alpha=0.45)
        a2.scatter(xx, med, color=col, s=26, zorder=3)
        a2.scatter(xx, mx, color=col, s=26, marker="_", zorder=3)
    a1.set_ylim(0, 100); a1.set_ylabel("% solved", fontsize=8.4)
    a1.set_title("Accuracy", loc="left", fontsize=9.6, weight="semibold")
    a2.set_yscale("log"); a2.set_yticks([5, 10, 20, 50, 100, 200], ["5K", "10K", "20K", "50K", "100K", "200K"])
    a2.set_title("Largest single context per task\n(dot: median, bar: up to the maximum)", loc="left",
                 fontsize=9.6, weight="semibold")
    for a in (a1, a2):
        a.set_xticks(xs, [r[0] for r in T2], fontsize=8.4)
        a.grid(axis="y", color=RULE, lw=0.6); a.set_axisbelow(True)
        a.tick_params(length=0, labelsize=7.6); a.spines["left"].set_visible(False)
    a1.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2, fontsize=8.6)
    fig.tight_layout(h_pad=2.0)
    fig.savefig(OUT + "fig02.png", dpi=400); fig.savefig(OUT + "fig02.svg"); plt.close(fig)


# ---------- Figure 3: acceleration numbers stated by Hermle et al. (2026) ----------
SC1 = [("Arts", 1.35), ("Anthropology", 1.36), ("Chemistry", 1.41), ("Computer science", 1.96), ("Statistics", 2.02)]
SC3 = [("Biology, chemistry, materials,\nagricultural, biomedical", 3, 4),
       ("Statistics, CS, economics, maths,\npsychology, most social sciences", 15, 16)]


def fig_science():
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(5.8, 6.4), gridspec_kw={"height_ratios": [1.5, 1]})
    ys = np.arange(len(SC1))
    a1.barh(ys, [v for _, v in SC1], color=[MUTED, MUTED, WARM, NAVY, NAVY], height=0.6)
    for y, (_, v) in zip(ys, SC1):
        a1.text(v + 0.03, y, f"{v:.2f}×", va="center", fontsize=8, color=INK)
    a1.set_yticks(ys, [n for n, _ in SC1], fontsize=8)
    a1.set_xlim(1, 2.3); a1.axvline(1, color=MUTED, lw=0.8)
    a1.set_title("Today's abilities, widely adopted", loc="left", fontsize=9.6, weight="semibold")
    ys2 = np.arange(len(SC3))
    for y, (n, lo, hi) in zip(ys2, SC3):
        col = WARM if lo < 5 else NAVY
        a2.barh(y, hi - 1, left=1, color=col, height=0.5, alpha=0.25)
        a2.barh(y, lo - 1, left=1, color=col, height=0.5)
        a2.text(hi + 0.3, y, f"{lo}–{hi}×", va="center", fontsize=8, color=INK)
    a2.set_yticks(ys2, [n for n, *_ in SC3], fontsize=7.8)
    a2.set_xlim(1, 19); a2.set_ylim(-0.7, 1.7)
    a2.set_title("All non-physical steps automated", loc="left", fontsize=9.6, weight="semibold")
    for a in (a1, a2):
        a.tick_params(length=0, labelsize=7.6); a.spines["left"].set_visible(False)
        a.grid(axis="x", color=RULE, lw=0.6); a.set_axisbelow(True)
        a.set_xlabel("research output for a fixed budget, × no AI", fontsize=7.8, color=MUTED)
    fig.tight_layout(h_pad=2.2)
    fig.savefig(OUT + "fig03.png", dpi=400); fig.savefig(OUT + "fig03.svg"); plt.close(fig)


# ---------- Figure 4: a compaction recap is a lab notebook ----------
PAIRS = [
    ("Objective", "one line: the required result", "Aim", "the question the study answers"),
    ("Established facts", "observations, kept apart\nfrom unverified ideas", "Results", "what was measured,\napart from the discussion"),
    ("Applied changes", "what was changed, and\nwhether it was verified", "Methods", "what was done, so that\nsomeone else can redo it"),
    ("Verification", "exact checks run\nand their outcomes", "Controls", "how we know it is\nnot an artefact"),
    ("Dead ends", "approaches not to repeat", "Negative results", "what did not work"),
    ("Remaining plan", "next step and the\ncondition for completion", "Next experiment", "what would settle it"),
]


def fig_notebook():
    fig, ax = canvas(6.6, 9.2, 13.2, 18.4)
    heading(ax, 0.3, 18.15, "Where the three readings meet",
            "The best compaction found by the NVIDIA team\nhas the shape of a lab notebook")
    ax.text(3.35, 15.75, "COMPACTION RECAP\n(Belcak et al., App. G.1)", ha="center", fontsize=7.6,
            weight="semibold", color=NAVY, linespacing=1.3)
    ax.text(9.85, 15.75, "LAB NOTEBOOK,\nOR A PAPER", ha="center", fontsize=7.6, weight="semibold",
            color=WARM, linespacing=1.3)
    h, gap, w = 1.85, 0.35, 5.7
    for i, (t1, s1, t2, s2) in enumerate(PAIRS):
        y = 13.1 - i * (h + gap)
        card(ax, 0.5, y, w, h, t1, sub=s1, accent=NAVY, fs=9.6, subfs=7.8, align="left")
        card(ax, 7.0, y, w, h, t2, sub=s2, accent=WARM, fs=9.6, subfs=7.8, align="left")
        arrow(ax, (6.3, y + h / 2), (6.9, y + h / 2), color=MUTED, lw=1.1, head=6)
        arrow(ax, (6.9, y + h / 2), (6.3, y + h / 2), color=MUTED, lw=1.1, head=6)
    pill(ax, 6.6, 0.55, "What neither can hold: the sample, the instrument,\nthe living cell. That state stays in the world.",
         fs=8.2, color=WARM)
    fig.savefig(OUT + "fig04.png", dpi=400); fig.savefig(OUT + "fig04.svg"); plt.close(fig)


if __name__ == "__main__":
    for b in (32, 8, 1):
        print(b, "K/V heads:", kv_bytes_per_token(b) // 1024, "KiB per token")
    fig_kv()
    fig_nvidia()
    fig_science()
    fig_notebook()
