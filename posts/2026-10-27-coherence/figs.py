"""Figures for "Coherence Is Measurable". Same style as "Where Memory Lives".
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



def save(fig, name):
    fig.savefig(OUT + name + ".svg")
    fig.savefig(OUT + name + ".png")
    plt.close(fig)


def title(ax, eyebrow, text, y=1.1):
    ax.text(0, y, eyebrow, transform=ax.transAxes, fontsize=7, weight="semibold", color=NAVY)
    ax.text(0, y - 0.06, text, transform=ax.transAxes, fontsize=11.5, weight="semibold", color=INK)




# ---------- Figure 1: four kinds of coherence ----------
def fig_four():
    fig, ax = canvas(10.4, 3.5, 20.8, 7.0)
    cards = [
        ("Across samples", "Ask the same question\nseveral times. Do the\nanswers agree?", NAVY, "1 · Output", "self-consistency\nsemantic entropy"),
        ("Across logic", "If A is B, is B A?\nDo paraphrases and\nnegations line up?", WARM, "2 · Reasoning", "reversal curse\nconsistency checks"),
        ("Thought and word", "Does the stated reason\nmatch what drove\nthe answer?", GREEN, "3 · Faithfulness", "CoT faithfulness\nlatent knowledge"),
        ("Across views and time", "Do two views of one\nscene, or two moments,\nmap to one state?", DEEP, "4 · Representation", "JEPA world models\nshared geometry"),
    ]
    w, h, gap = 4.6, 4.6, 0.55
    for i, (t, s, c, eb, tag) in enumerate(cards):
        x = 0.3 + i * (w + gap)
        card(ax, x, 1.7, w, h, t, s, accent=c, eyebrow=eb, fs=10.4, subfs=8.6)
        chip(ax, x + w / 2 + 0.1, 0.95, tag, color=c if c != DEEP else NAVY,
             fill=SAND_T, fs=6.8)
    arrow(ax, (0.6, 0.15), (20.4, 0.15), color=RULE, lw=1.2)
    ax.text(0.6, -0.25, "cheap to check, from outside the model", fontsize=7.5, color=MUTED, va="top")
    ax.text(20.4, -0.25, "needs access to its insides, or a new architecture", fontsize=7.5,
            color=MUTED, va="top", ha="right")
    save(fig, "fig01")


# ---------- Figure 2: measured, ensembles of small networks (sim.py) ----------
R = json.load(open("results.json"))


def fig_agreement():
    n = R["n_test"]
    fig, (a, b) = plt.subplots(1, 2, figsize=(10.2, 3.8), gridspec_kw=dict(wspace=0.3))
    for cond, col, lab in (("clean", NAVY, "clean digits"), ("noisy", WARM, "noisy digits (unseen)")):
        r = R["control"][cond]
        curve = np.array(r["selective_curve"])
        cov = (np.arange(len(curve)) * 9 + 1) / n * 100
        a.plot(cov, curve * 100, color=col, lw=2, label=f"{lab}  ·  AUROC {r['auroc_agreement_detects_error']:.2f}")
        a.plot(100, r["majority_acc"] * 100, "o", color=col, ms=4)
        a.annotate(f"{r['majority_acc']*100:.1f}% if it\nanswers everything", (100, r["majority_acc"] * 100),
                   xytext=(-6, -6), textcoords="offset points", ha="right", va="top", fontsize=7.3, color=col)
    a.set_xlabel("share of digits answered, most agreed first (%)")
    a.set_ylabel("of those, majority vote correct (%)")
    a.set_xlim(0, 102); a.set_ylim(84, 100.8)
    a.legend(loc="lower left", fontsize=7.8)
    tidy(a); title(a, "A · AGREEMENT AS A SIGNAL", "Disagreement points at the errors")

    sw = R["sweep"]
    ps = sorted({r["hint_p"] for r in sw})
    x = np.arange(len(ps))
    for key, col, lab in (("auroc", GREEN, "agreement detects errors (AUROC)"),
                          ("followed_hint_share", RED, "majority follows the wrong hint")):
        v = np.array([[r[key] for r in sw if r["hint_p"] == p] for p in ps])
        b.fill_between(x, v.min(1), v.max(1), color=col, alpha=0.15, lw=0)
        b.plot(x, v.mean(1), "-o", color=col, lw=2, ms=4.5, label=lab)
        for xi, m in zip(x, v.mean(1)):
            dy = 7 if key == "auroc" else (8 if xi < len(ps) - 1 else -13)
            b.annotate(f"{m:.2f}", (xi, m), xytext=(0, dy),
                       textcoords="offset points", ha="center", fontsize=7.3, color=col)
    b.axhline(0.5, color=MUTED, ls=":", lw=1)
    b.text(-0.1, 0.515, "chance", fontsize=7.3, color=MUTED, ha="left")
    b.set_xticks(x, [f"{p*100:.0f}%" for p in ps])
    b.set_xlabel("how often the hint was right during training")
    b.set_ylim(0, 1.02)
    b.legend(loc="center left", bbox_to_anchor=(0, 0.62), fontsize=7.8)
    b.set_ylabel("share or score")
    tidy(b); title(b, "B · A SHARED SHORTCUT", "When all models learn it, agreement goes blind")
    save(fig, "fig02")


# ---------- Figure 3: predict the pixels vs predict the representation ----------
def fig_jepa():
    fig, ax = canvas(10.4, 4.4, 20.8, 8.8)
    heading(ax, 0.3, 8.6, "Generative", "Predict every detail", color=WARM)
    heading(ax, 10.9, 8.6, "Joint embedding (JEPA)", "Predict what stays coherent", color=GREEN)
    # left: context -> decoder -> pixels, loss in pixel space
    card(ax, 0.3, 4.6, 3.0, 2.2, "Context", "frame t", accent=WARM)
    card(ax, 4.2, 4.6, 2.6, 2.2, "Model", None, accent=WARM)
    card(ax, 7.6, 4.6, 2.7, 2.2, "Pixels", "frame t+1\nevery leaf", accent=WARM)
    arrow(ax, (3.42, 5.7), (4.08, 5.7)); arrow(ax, (6.92, 5.7), (7.48, 5.7))
    card(ax, 7.6, 1.2, 2.7, 2.0, "True pixels", "frame t+1", accent=MUTED)
    ax.annotate("", (8.95, 4.45), (8.95, 3.35), arrowprops=dict(arrowstyle="<->", color=RED, lw=1.3))
    ax.text(8.75, 3.9, "loss on\nevery pixel", ha="right", va="center", fontsize=7.6, color=RED)
    ax.text(0.3, 2.6, "Spends capacity on noise\nthat cannot be predicted:\nleaves, glare, texture.",
            fontsize=8.4, color=MUTED, va="center", linespacing=1.4)
    # right: two encoders -> predictor in latent space
    card(ax, 10.9, 4.6, 2.8, 2.2, "Context", "frame t", accent=GREEN)
    card(ax, 14.4, 4.6, 2.6, 2.2, "Predictor", None, accent=GREEN)
    card(ax, 17.8, 4.6, 2.7, 2.2, "Prediction", "state t+1", accent=GREEN)
    arrow(ax, (13.82, 5.7), (14.28, 5.7)); arrow(ax, (17.12, 5.7), (17.68, 5.7))
    card(ax, 14.4, 1.2, 2.6, 2.0, "Encoder", "frame t+1", accent=MUTED)
    card(ax, 17.8, 1.2, 2.7, 2.0, "Target", "state t+1", accent=MUTED)
    arrow(ax, (17.12, 2.2), (17.68, 2.2))
    ax.annotate("", (19.15, 4.45), (19.15, 3.35), arrowprops=dict(arrowstyle="<->", color=GREEN, lw=1.3))
    ax.text(18.95, 3.9, "loss on\nthe state", ha="right", va="center", fontsize=7.6, color=GREEN)
    ax.text(10.9, 2.2, "Keeps what views\nshare: objects,\npositions, motion.",
            fontsize=8.4, color=MUTED, va="center", linespacing=1.4)
    ax.plot([10.45, 10.45], [0.6, 8.6], color=RULE, lw=1)
    save(fig, "fig03")


# ---------- Figure 4: coherent is not true ----------
def fig_grid():
    fig, ax = canvas(8.6, 5.0, 17.2, 10.0)
    ax.text(5.75, 9.6, "COHERENT", ha="center", fontsize=8, weight="semibold", color=NAVY)
    ax.text(12.95, 9.6, "INCOHERENT", ha="center", fontsize=8, weight="semibold", color=NAVY)
    ax.text(1.2, 6.95, "TRUE", ha="center", rotation=90, fontsize=8, weight="semibold", color=NAVY)
    ax.text(1.2, 2.55, "FALSE", ha="center", rotation=90, fontsize=8, weight="semibold", color=NAVY)
    cells = [
        (2.1, 5.0, "Knowledge", "Stable across samples,\nparaphrases and reasons.\nAnswer.", GREEN, GREEN_T),
        (9.3, 5.0, "Lucky guess", "Right this time, wrong\nnext time. Treat as\nunknown.", WARM, AMBER_T),
        (2.1, 0.6, "Coherent fiction", "A shared bias, a stale\nfact, a confident myth.\nOnly the world can catch it.", RED, "#f6e3e0"),
        (9.3, 0.6, "Visible error", "Samples disagree. Easy\nto detect: look up\nor abstain.", NAVY, NAVY_T),
    ]
    for x, y, t, s, c, f in cells:
        card(ax, x, y, 7.2, 4.0, t, s, accent=c, fill="white", fs=12, subfs=9)
    save(fig, "fig04")


# ---------- Figure 5: the design loop ----------
def fig_loop():
    fig, ax = canvas(10.4, 3.9, 20.8, 7.8)
    card(ax, 0.3, 3.0, 3.6, 2.4, "Question", None, accent=MUTED)
    card(ax, 5.0, 3.0, 4.0, 2.4, "Probe", "k samples\nparaphrases\nreverse query", accent=NAVY, subfs=8)
    card(ax, 10.1, 3.0, 3.8, 2.4, "Measure", "agreement\nfaithfulness", accent=NAVY, subfs=8)
    card(ax, 15.6, 5.2, 4.9, 2.2, "Coherent", "answer, then check\nagainst the world", accent=GREEN, subfs=8)
    card(ax, 15.6, 1.8, 4.9, 2.2, "Incoherent", "look it up, ask a tool,\nor say \"I don't know\"", accent=WARM, subfs=8)
    arrow(ax, (4.0, 4.2), (4.88, 4.2)); arrow(ax, (9.1, 4.2), (9.98, 4.2))
    arrow(ax, (14.0, 4.5), (15.48, 6.2)); arrow(ax, (14.0, 3.9), (15.48, 2.9))
    # training feedback
    ax.plot([18.05, 18.05, 7.0], [1.6, 0.7, 0.7], color=GREEN, lw=1.3, ls="--", zorder=1.5)
    arrow(ax, (7.0, 0.7), (7.0, 2.88), color=GREEN, lw=1.3, ls="--")
    pill(ax, 12.5, 0.7, "train on consistency: same input meaning → same behaviour", color=GREEN, fs=7.6)
    save(fig, "fig05")


if __name__ == "__main__":
    fig_four(); fig_agreement(); fig_jepa(); fig_grid(); fig_loop()
