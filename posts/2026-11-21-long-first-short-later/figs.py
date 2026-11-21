"""Figures for "Long First, Short Later". Same palette as the other essays.
Run: python figs.py   (needs matplotlib, numpy, mpmath)
Written twice: a vector SVG (used in the page) and a 400 dpi PNG (card image).
Figure 1 compares the two claims as reported on 20 November 2026 (see the essay's sources).
Figure 2 is computed: the prime staircase and the Riemann zeta function on the critical line.
Figure 3 places proof lengths, as reported, on a log scale. Figure 4 is a schematic, my own."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import sys, pathlib  # hand-drawn house style: _figstyle/handdrawn.py at the site root
sys.path.insert(0, str(next(p / "_figstyle" for p in pathlib.Path(__file__).resolve().parents if (p / "_figstyle").is_dir())))
import handdrawn; handdrawn.apply()
from matplotlib.patches import FancyBboxPatch
import numpy as np
import mpmath as mp

# ---------- palette (from light.scss) ----------
BG = "#ffffff"
INK = "#1f2328"
MUTED = "#5f6b76"
LINE = "#d0d7de"
AMBER = "#e0952b"
BLUE = "#3b6ea8"
GLOW = "#fff4e0"
BLUE_GLOW = "#eef3f9"

plt.rcParams.update({
    "font.family": "Inter", "font.size": 10, "text.color": INK,
    "axes.edgecolor": LINE, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
    "savefig.dpi": 400, "savefig.bbox": "tight", "savefig.pad_inches": 0.35,
})
plt.rcParams["svg.fonttype"] = "path"


def _box(ax, x, y, w, h, fc, ec=LINE, r=0.18, lw=1.4):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw))


def _save(fig, n):
    for ext in ("svg", "png"):
        fig.savefig(f"figures/fig{n:02d}.{ext}")
    plt.close(fig)


def fig01():
    """Two proofs, one day: each has what the other lacks."""
    fig, ax = plt.subplots(figsize=(10.5, 5.6))
    ax.set_xlim(0, 10.5); ax.set_ylim(0, 5.75); ax.axis("off")
    ax.text(0.05, 5.45, "Two proofs of the Riemann hypothesis, one day", fontsize=14.5, weight="bold")
    ax.text(0.05, 5.08, "20 November 2026, as reported. Neither is confirmed yet.", fontsize=10, color=MUTED)

    cols = [
        (0.05, BLUE, BLUE_GLOW, "With a machine", "Levent Alpöge and Claude",
         [("41 days", "of work"),
          ("175,187", "files of Lean code,\na language a computer checks"),
          ("250,000+", "pages when written out\nin prose (not posted)")],
         "Checked by a machine: it compiles.", "Not yet: understood by a person."),
        (5.35, AMBER, GLOW, "By hand", "Alessandro Masullo",
         [("12 years", "of work, no AI"),
          ("940", "pages of manuscript"),
          ("months", "of close reading by Brian Conrad")],
         "Read by people: a mind can follow it.", "Not yet: checked by a machine. Under revision."),
    ]
    w = 5.1
    for x, ec, fc, head, who, rows, yes, no in cols:
        _box(ax, x, 0.15, w, 4.65, fc, ec=ec)
        ax.text(x + 0.3, 4.38, head, fontsize=13.5, weight="bold", color=ec)
        ax.text(x + 0.3, 4.05, who, fontsize=11, color=MUTED)
        for i, (big, small) in enumerate(rows):
            y = 3.45 - i * 0.68
            ax.text(x + 0.3, y, big, fontsize=16, weight="bold", color=INK, va="center")
            ax.text(x + 1.95, y, small, fontsize=10.5, color=MUTED, va="center", linespacing=1.25)
        ax.plot([x + 0.3, x + w - 0.3], [1.38, 1.38], color=LINE, lw=1)
        ax.text(x + 0.3, 1.0, "✓  " + yes, fontsize=10.8, color=INK, va="center")
        ax.text(x + 0.3, 0.52, "…  " + no, fontsize=10.8, color=MUTED, va="center")
    _save(fig, 1)


def fig02():
    """The music of the primes: the staircase, and the zeros that tune it."""
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(8.2, 7.4), gridspec_kw=dict(hspace=0.55))
    fig.suptitle("What both proofs are about", x=0.125, ha="left", fontsize=14.5, weight="bold", y=0.98)

    # top: prime staircase vs the smooth guess
    N = 200
    xs = np.arange(2, N + 1)
    sieve = np.ones(N + 1, bool); sieve[:2] = False
    for p in range(2, int(N ** 0.5) + 1):
        if sieve[p]:
            sieve[p * p::p] = False
    pi = np.cumsum(sieve)[2:]
    a1.step(xs, pi, where="post", color=BLUE, lw=1.6, label="the number of primes up to x")
    xx = np.linspace(2, N, 400)
    li = [float(mp.li(v) - mp.li(2)) for v in xx]
    a1.plot(xx, li, color=AMBER, lw=2, label="Gauss's smooth guess")
    a1.set_title("The primes climb like a staircase, close to a smooth curve", loc="left", fontsize=11, color=INK)
    a1.set_xlabel("x"); a1.set_xlim(0, N); a1.set_ylim(0, 52)
    a1.legend(frameon=False, loc="upper left", fontsize=9)
    for s in ("top", "right"): a1.spines[s].set_visible(False)

    # bottom: |zeta(1/2 + it)|
    t = np.linspace(0, 50, 1600)
    z = [abs(complex(mp.zeta(mp.mpf(0.5) + 1j * v))) for v in t]
    a2.plot(t, z, color=BLUE, lw=1.4)
    zeros = [float(mp.zetazero(k).imag) for k in range(1, 11)]
    a2.scatter(zeros, [0] * len(zeros), s=36, color=AMBER, zorder=3, edgecolor="white", lw=0.8)
    for zz in zeros:
        a2.axvline(zz, color=AMBER, lw=0.6, alpha=0.35)
    a2.text(zeros[0], 3.6, "first zero, at 14.13", fontsize=9, color=MUTED, ha="center")
    a2.set_title("The zeros of the zeta function, the notes that tune the staircase", loc="left", fontsize=11, color=INK)
    a2.set_xlabel("height t along the critical line, real part 1/2")
    a2.set_ylabel("size of ζ(1/2 + it)")
    a2.set_xlim(0, 50); a2.set_ylim(0, 4.2)
    for s in ("top", "right"): a2.spines[s].set_visible(False)
    _save(fig, 2)


def fig03():
    """Long first, short later: proof lengths over time, as reported, on a log scale."""
    fig, ax = plt.subplots(figsize=(8.4, 5.8))
    ax.set_yscale("log")
    ax.set_xlim(1880, 2065); ax.set_ylim(1.5, 2e6)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    ax.set_ylabel("pages (log scale)")
    ax.set_title("Long first, short later", loc="left", fontsize=16, weight="bold", pad=24)
    ax.text(0, 1.02, "As published or reported. The question mark is my bet, not a fact.",
            transform=ax.transAxes, fontsize=12.2, color=MUTED)
    ax.grid(axis="y", color=LINE, lw=0.6, alpha=0.6)

    # Prime number theorem
    ax.scatter([1896], [22], s=70, color=BLUE, zorder=3)
    ax.annotate("Prime number theorem\nHadamard, 1896: 22 pages", (1896, 22), (1886, 70),
                fontsize=11.2, color=INK)
    ax.scatter([1980], [4], s=70, color=BLUE, zorder=3)
    ax.annotate("Newman, 1980:\n4 pages", (1980, 4), (1985, 2.2), fontsize=11.2, color=INK)
    ax.annotate("", xy=(1978, 4.4), xytext=(1899, 20),
                arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.6, connectionstyle="arc3,rad=0.18"))
    ax.text(1938, 2.05, "84 years", fontsize=11.7, color=BLUE, ha="center")

    # Riemann hypothesis claims, 2026
    ax.scatter([2026], [940], s=70, color=AMBER, zorder=3)
    ax.annotate("Masullo, by hand:\n940 pages", (2026, 940), (1968, 560), fontsize=11.2, color=INK)
    ax.scatter([2026], [250000], s=70, color=BLUE, zorder=3, marker="D")
    ax.annotate("Alpöge with Claude, in prose:\nmore than 250,000 pages (not posted)", (2026, 250000),
                (1930, 300000), fontsize=11.2, color=INK)
    ax.text(1968, 9000, "Riemann hypothesis,\nthe two 2026 claims", fontsize=10.7, color=MUTED, va="center")

    # the bet
    ax.scatter([2052], [12], s=260, color=GLOW, edgecolor=AMBER, lw=1.6, zorder=3)
    ax.text(2052, 12, "?", ha="center", va="center", fontsize=15.2, weight="bold", color=AMBER)
    for y0 in (940, 250000):
        ax.annotate("", xy=(2050, 15), xytext=(2028, y0 * 0.8),
                    arrowprops=dict(arrowstyle="-|>", color=AMBER, lw=1.3, ls="--",
                                    connectionstyle="arc3,rad=-0.15"))
    ax.text(2052, 2.6, "a proof one\nmind can hold", fontsize=11.2, color=AMBER, ha="center")
    _save(fig, 3)


def fig04():
    """The two routes need each other."""
    fig, ax = plt.subplots(figsize=(8.4, 5.0))
    ax.set_xlim(0, 10.5); ax.set_ylim(0, 5.2); ax.axis("off")
    ax.text(0.05, 4.9, "The two routes need each other", fontsize=16, weight="bold")

    _box(ax, 0.1, 2.55, 3.4, 1.85, BLUE_GLOW, ec=BLUE)
    ax.text(1.8, 3.85, "The machine's proof", ha="center", fontsize=13.7, weight="bold")
    ax.text(1.8, 3.15, "checked by a computer,\ntoo long to read", ha="center", fontsize=11.7, color=MUTED)

    _box(ax, 0.1, 0.2, 3.4, 1.85, GLOW, ec=AMBER)
    ax.text(1.8, 1.5, "The human proof", ha="center", fontsize=13.7, weight="bold")
    ax.text(1.8, 0.8, "readable, full of ideas,\nnot yet checked", ha="center", fontsize=11.7, color=MUTED)

    _box(ax, 7.0, 1.35, 3.4, 1.9, "#f6f8fa", ec=INK, lw=1.6)
    ax.text(8.7, 2.7, "A short proof", ha="center", fontsize=14.7, weight="bold")
    ax.text(8.7, 1.95, "checked, and one mind\ncan hold it", ha="center", fontsize=11.7, color=MUTED)

    ax.annotate("", xy=(6.95, 2.55), xytext=(3.55, 3.45),
                arrowprops=dict(arrowstyle="-|>", color=AMBER, lw=2))
    ax.text(5.25, 3.55, "people distil it:\nfind the idea inside", ha="center", fontsize=11.7, color=AMBER)
    ax.annotate("", xy=(6.95, 2.05), xytext=(3.55, 1.15),
                arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=2))
    ax.text(5.25, 0.6, "machines check it:\nevery line, in Lean", ha="center", fontsize=11.7, color=BLUE)
    _save(fig, 4)


if __name__ == "__main__":
    fig01(); fig02(); fig03(); fig04()
