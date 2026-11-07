"""Figures for "It Must Be Simpler Than This".

Same style as "A Finite State of Mind": Inter type, white cards with a faint shadow and a
coloured accent, colours taken from the site's palette.

Figure 1 runs three elementary cellular automata-like patterns (Rule 90, Rule 30, and seeded
coin flips) on a 255 x 128 grid and measures each three ways: raw bits, bits after a
general-purpose compressor (zlib, level 9), and the length of the Python program that
regenerates it. All numbers are computed here and written to results.json.
Figure 2 fits polynomials of degree 0 to 14 to 40 noisy points drawn from a quadratic and
counts the two-part description length (crude MDL: model bits + residual bits).
Figures 3 and 4 are schematics of my own.
"""
import json
import zlib
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


# ---------- Figure 1: three patterns, three ways to describe them ----------
W, T = 255, 128

# Each generator is a complete program that prints the pattern; its length is the "short description".
GEN_CA = ("r={rule};w=255;c=[0]*w;c[127]=1\n"
          "for _ in range(128):\n"
          " print(''.join(map(str,c)))\n"
          " c=[r>>(4*c[i-1]+2*c[i]+c[(i+1)%w])&1 for i in range(w)]\n")
GEN_NOISE = ("import numpy as n\n"
             "for row in n.random.default_rng(7).integers(0,2,(128,255)):print(''.join(map(str,row)))\n")


def run_ca(rule):
    g = np.zeros((T, W), dtype=np.uint8)
    c = np.zeros(W, dtype=np.uint8); c[W // 2] = 1
    for t in range(T):
        g[t] = c
        idx = 4 * np.roll(c, 1) + 2 * c + np.roll(c, -1)
        c = (rule >> idx) & 1
    return g


def noise():
    return np.random.default_rng(7).integers(0, 2, (T, W)).astype(np.uint8)


def sizes(g, gen):
    raw = g.size                                          # one bit per cell
    z = len(zlib.compress(np.packbits(g).tobytes(), 9)) * 8
    return raw, z, len(gen) * 8


def fig_patterns():
    pats = [("Rule 90", run_ca(90), GEN_CA.format(rule=90), NAVY, "nested: a short rule,\nand it looks it"),
            ("Rule 30", run_ca(30), GEN_CA.format(rule=30), WARM, "looks random: a short rule\nthe compressor barely sees"),
            ("Coin flips", noise(), GEN_NOISE, MUTED, "drawn from a seeded generator:\nshort too, but you cannot tell")]
    res = {}
    fig = plt.figure(figsize=(5.8, 9.6))
    gs = fig.add_gridspec(3, 2, width_ratios=[1.35, 1], wspace=0.42, hspace=0.55)
    for i, (name, g, gen, col, note) in enumerate(pats):
        raw, z, p = sizes(g, gen)
        res[name] = dict(raw_bits=raw, zlib_bits=z, program_bits=p)
        a = fig.add_subplot(gs[i, 0])
        cmap = matplotlib.colors.ListedColormap([BG, col])
        a.imshow(g[:, 64:192], cmap=cmap, interpolation="nearest", aspect="auto")
        a.set_xticks([]); a.set_yticks([])
        for sp in a.spines.values():
            sp.set_visible(False)
        a.set_title(name, loc="left", fontsize=10.5, weight="semibold", color=INK, pad=6)
        a.text(0, 1.0 + 0.0, "", transform=a.transAxes)
        a.set_xlabel(note, fontsize=7.8, color=MUTED, linespacing=1.3, labelpad=6)
        b = fig.add_subplot(gs[i, 1])
        vals = [raw, z, p]
        labels = ["Raw", "Compressor", "Program"]
        ys = np.arange(3)[::-1]
        b.barh(ys, vals, color=[RULE, "#c9d5df", col], height=0.6)
        for y, v in zip(ys, vals):
            b.text(v * 1.15, y, f"{v / 8 / 1024:.1f} KB" if v >= 8192 else f"{v // 8} B",
                   va="center", fontsize=7.8, color=INK)
        b.set_xscale("log"); b.set_xlim(500, 2e5)
        b.set_yticks(ys, labels, fontsize=7.8)
        b.tick_params(length=0, labelsize=7.4); b.set_xticks([]); b.minorticks_off(); b.tick_params(axis="x", which="both", bottom=False, labelbottom=False)
        for sp in ("left", "bottom"):
            b.spines[sp].set_visible(False)
    fig.text(0.02, 0.985, "Same size, very different descriptions", fontsize=11.5, weight="semibold",
             color=INK, va="top")
    fig.text(0.02, 0.962, f"{T} rows × {W} cells; bars: bytes to store each pattern three ways (log scale)",
             fontsize=8, color=MUTED, va="top")
    fig.savefig(OUT + "fig01.png", dpi=400); fig.savefig(OUT + "fig01.svg"); plt.close(fig)
    return res


# ---------- Figure 2: the two-part description length ----------
def fig_mdl():
    rng = np.random.default_rng(3)
    n, sigma = 40, 0.35
    x = np.sort(rng.uniform(-1, 1, n))
    y = 1.0 - 2.0 * x + 1.5 * x**2 + rng.normal(0, sigma, n)
    degs = np.arange(0, 15)
    lm, ld = [], []
    for k in degs:
        coef = np.polynomial.polynomial.polyfit(x, y, k)
        rss = np.sum((y - np.polynomial.polynomial.polyval(x, coef))**2)
        lm.append((k + 1) / 2 * np.log2(n))               # bits to state k+1 parameters (BIC-style)
        ld.append(n / 2 * np.log2(rss / n))               # bits for the residual, up to a constant
    lm, ld = np.array(lm), np.array(ld)
    ld = ld - ld.min() + 20                               # shift: only differences matter
    tot = lm + ld
    best = int(degs[np.argmin(tot)])
    fig, ax = plt.subplots(figsize=(5.8, 4.2))
    ax.plot(degs, ld, color=MUTED, lw=1.6, marker="o", ms=3.5, label="Residual: what the model leaves out")
    ax.plot(degs, lm, color=AMBER, lw=1.6, marker="o", ms=3.5, label="Model: bits to state the rule")
    ax.plot(degs, tot, color=NAVY, lw=2.4, marker="o", ms=4, label="Total description")
    ax.scatter([best], [tot[best]], s=110, facecolor="none", edgecolor=NAVY, lw=1.6, zorder=4)
    ax.annotate(f"shortest total:\ndegree {best}, the true law", (best, tot[best]),
                xytext=(best + 2.2, tot[best] + 38), fontsize=8.2, color=NAVY,
                arrowprops=dict(arrowstyle="-", color=NAVY, lw=0.8))
    ax.set_xlabel("Degree of the polynomial (a more complex model →)", fontsize=8.6)
    ax.set_ylabel("Bits (relative)", fontsize=8.6)
    ax.grid(axis="y", color=RULE, lw=0.6); ax.set_axisbelow(True)
    ax.spines["left"].set_visible(False); ax.tick_params(length=0, labelsize=8)
    ax.set_title("Forty noisy points from a quadratic: the simplest\ncomplete description is the true one",
                 loc="left", fontsize=10.5, weight="semibold")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), fontsize=8.2, ncol=1)
    fig.savefig(OUT + "fig02.png", dpi=400); fig.savefig(OUT + "fig02.svg"); plt.close(fig)
    return dict(best_degree=best, n=n, sigma=sigma)


# ---------- Figure 3: three sources of excess complexity ----------
SOURCES = [
    ("Wrong level", "Looking at the parts when the law\nlives in the whole", NAVY,
     "Molecules → temperature\nTokens → scaling laws\nSynapses → a learning circuit", "Change level"),
    ("Wrong frame", "Describing in a variable where\nthe pattern does not show", GREEN,
     "State → what changed\nVolume → boundary\nCode → intent and checks", "Change variable"),
    ("Mass", "Layers kept after the reason\nfor them has gone", WARM,
     "A gate on every change\nGlue code for every pair\nRe-reasoning on every run", "Remove"),
]


def fig_sources():
    fig, ax = canvas(6.4, 9.0, 12.8, 18.0)
    heading(ax, 0.3, 17.75, "Where apparent complexity comes from",
            "Three sources of excess, and what removes each")
    h, gap = 4.6, 0.55
    for i, (t, s, col, ex, fix) in enumerate(SOURCES):
        y = 11.6 - i * (h + gap)
        card(ax, 0.4, y, 7.6, h, None, accent=col)
        ax.text(1.0, y + h - 0.55, f"SOURCE {i + 1}", fontsize=6.8, weight="semibold", color=col,
                va="top", zorder=8)
        ax.text(1.0, y + h - 1.0, t, fontsize=11, weight="semibold", color=INK, va="top", zorder=8)
        ax.text(1.0, y + h - 1.75, s, fontsize=8.2, color=MUTED, va="top", linespacing=1.3, zorder=8)
        ax.text(1.0, y + 0.35, ex, fontsize=7.6, color=INK, fontfamily=MONO, va="bottom",
                linespacing=1.5, zorder=8)
        arrow(ax, (8.2, y + h / 2), (9.2, y + h / 2), color=col, lw=1.6, head=9)
        card(ax, 9.35, y + h / 2 - 0.9, 3.1, 1.8, fix, accent=col, fill=col, fs=9.8, bar=False)
    pill(ax, 6.4, 0.75, "What remains after all three is the essential part: keep it, and watch what it misses.",
         fs=7.8, color=INK)
    fig.savefig(OUT + "fig03.png", dpi=400); fig.savefig(OUT + "fig03.svg"); plt.close(fig)


# ---------- Figure 4: find the generator, watch the residual ----------
def fig_loop():
    fig, ax = canvas(6.4, 5.6, 12.8, 11.2)
    heading(ax, 0.3, 11.0, "The rule in practice",
            "Find the generator once, act with it fast,\nand let the residual say when it is wrong")
    boxes = {
        "obs": (0.5, 7.0, 5.2, 2.0, "Observations", "data, traces, incidents", MUTED),
        "gen": (7.1, 7.0, 5.2, 2.0, "Find the generator", "slow, once: the short rule", NAVY),
        "act": (7.1, 3.0, 5.2, 2.0, "Act with it", "fast, every time, explainable", GREEN),
        "res": (0.5, 3.0, 5.2, 2.0, "Watch the residual", "what the rule leaves out", WARM),
    }
    for k, (x, y, w, h, t, s, c) in boxes.items():
        card(ax, x, y, w, h, t, sub=s, accent=c, fs=10.2, subfs=8)
    arrow(ax, (5.85, 8.0), (6.95, 8.0), color=NAVY, lw=1.6)
    arrow(ax, (9.7, 6.85), (9.7, 5.15), color=GREEN, lw=1.6)
    arrow(ax, (6.95, 4.0), (5.85, 4.0), color=MUTED, lw=1.6)
    arrow(ax, (3.1, 5.15), (3.1, 6.85), color=WARM, lw=1.6, ls="--")
    pill(ax, 6.4, 1.9, "the leftover grows → the rule is wrong → go back to the slow path", fs=7.8, color=WARM)
    ax.text(3.0, 6.0, "residual\ngrows", fontsize=7.4, color=WARM, ha="right", va="center", linespacing=1.2)
    ax.text(9.85, 6.0, "rule\nholds", fontsize=7.4, color=GREEN, ha="left", va="center", linespacing=1.2)
    ax.text(6.4, 0.7, "Fast AI is this loop for automation; the quiet-screen dashboard is this loop\n"
            "for monitoring; a scientific theory is this loop for nature.",
            fontsize=7.8, color=MUTED, ha="center", va="center", linespacing=1.4)
    fig.savefig(OUT + "fig04.png", dpi=400); fig.savefig(OUT + "fig04.svg"); plt.close(fig)


if __name__ == "__main__":
    out = {"fig01": fig_patterns(), "fig02": fig_mdl()}
    fig_sources()
    fig_loop()
    json.dump(out, open("results.json", "w"), indent=2)
    print(json.dumps(out, indent=2))
