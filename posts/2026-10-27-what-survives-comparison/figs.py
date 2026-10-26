"""Figures for "What Survives Comparison". Style matches "Nothing From Outside, Everything From Inside".

All figures are schematic toys, not physics simulations. Run from this folder: python figs.py
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Circle, Polygon, FancyArrowPatch

NAVY, GREY, RED, LIGHT, PALE, AMBER = "#1f4e79", "#7f8c8d", "#c0392b", "#d5dde5", "#eef1f4", "#d68910"
INK = "#2c3e50"
plt.rcParams.update({
    "font.family": "DejaVu Serif", "font.size": 10, "axes.spines.top": False,
    "axes.spines.right": False, "axes.linewidth": 1.0, "savefig.dpi": 200,
    "savefig.bbox": "tight", "legend.frameon": False, "legend.fontsize": 8.5,
})
OUT = "figures/"
SKY = LinearSegmentedColormap.from_list("sky", ["#0b1a2e", NAVY, "#5b7fa6", AMBER, "#fbeed7"])


def clock(ax, x, y, s, color=INK, z=6):
    """A small clock: the simplest observer, a system that keeps a record."""
    ax.add_patch(Circle((x, y), s, fc="white", ec=color, lw=1.4, zorder=z))
    ax.plot([x, x], [y, y + 0.7 * s], color=color, lw=1.4, zorder=z + 1, solid_capstyle="round")
    ax.plot([x, x + 0.5 * s], [y, y + 0.15 * s], color=color, lw=1.4, zorder=z + 1, solid_capstyle="round")


def bare(ax):
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_visible(False)


# --------------------------------------------------------------------------------------------
# The same toy universe as in the previous essay
def cosmic_field(n=256, seed=7):
    """A web-like toy 'universe': filaments where a smooth random field crosses zero."""
    rng = np.random.default_rng(seed)
    k = np.fft.fftfreq(n)[:, None] ** 2 + np.fft.fftfreq(n)[None, :] ** 2
    k = np.sqrt(k); k[0, 0] = 1
    spec = k ** -1.6 * np.exp(-(k / 0.09) ** 2)
    g1 = np.real(np.fft.ifft2(np.fft.fft2(rng.normal(size=(n, n))) * spec))
    g2 = np.real(np.fft.ifft2(np.fft.fft2(rng.normal(size=(n, n))) * spec))
    g1, g2 = g1 / g1.std(), g2 / g2.std()
    web = np.exp(-(g1 / 0.22) ** 2) + np.exp(-(g2 / 0.22) ** 2) + 2.2 * np.exp(-(g1**2 + g2**2) / 0.12)
    return web / web.max()


def describe(field, bits):
    """What an observer holding `bits` can describe: the largest-scale modes it can afford, 8 bits each."""
    n = field.shape[0]
    F = np.fft.fft2(field)
    k = np.sqrt(np.fft.fftfreq(n)[:, None] ** 2 + np.fft.fftfreq(n)[None, :] ** 2)
    keep = max(1, int(bits // 8))
    thresh = np.sort(k.ravel())[min(keep, k.size) - 1]
    return np.real(np.fft.ifft2(F * (k <= thresh)))


def fig_two_records():
    """Two observers of different size: their records differ, until compared at the coarser scale."""
    field = cosmic_field()
    small, large = 2**10, 2**15
    rec_s, rec_l = describe(field, small), describe(field, large)
    rec_l_coarse = describe(rec_l, small)                 # the large record, read at the small one's scale
    vmax = np.percentile(field, 99.5)

    fig = plt.figure(figsize=(10, 6.4))
    gs = fig.add_gridspec(2, 4, height_ratios=[1, 0.72], hspace=0.18, wspace=0.08)
    axes = [fig.add_subplot(gs[0, i]) for i in range(4)]
    panels = [(rec_s, "small observer's record\n$2^{10}$ bits", INK),
              (rec_l, "large observer's record\n$2^{15}$ bits", INK),
              (rec_l_coarse, "large record, read at\nthe small one's scale", NAVY)]
    for ax, (img, title, col) in zip(axes, panels):
        ax.imshow(img, cmap=SKY, vmin=0, vmax=vmax, interpolation="bilinear"); bare(ax)
        ax.set_title(title, fontsize=9.5, color=col)
    diff_naive = np.abs(rec_l - rec_s).mean() / field.mean()
    diff_fair = np.abs(rec_l_coarse - rec_s).mean() / field.mean()
    axes[3].imshow(np.abs(rec_l - rec_s), cmap="Greys", vmin=0, vmax=0.5 * vmax, interpolation="bilinear")
    bare(axes[3])
    axes[3].set_title("where the first two differ", fontsize=9.5, color=RED)
    for s in axes[3].spines.values(): s.set_visible(True); s.set_color(RED); s.set_linestyle((0, (3, 2)))

    # Disagreement, pixel by pixel, against the small observer's size: naive vs fair comparison
    ax = fig.add_subplot(gs[1, :])
    sizes = 2.0 ** np.arange(6, 15.01, 0.25)
    naive = [np.abs(rec_l - describe(field, b)).mean() / field.mean() for b in sizes]
    fair = [np.abs(describe(rec_l, b) - describe(field, b)).mean() / field.mean() for b in sizes]
    ax.semilogx(sizes, naive, color=RED, lw=2.2, base=2, label="compared pixel by pixel")
    ax.semilogx(sizes, fair, color=NAVY, lw=2.2, base=2, label="compared at the coarser scale")
    ax.scatter([small], [diff_naive], color=AMBER, zorder=5, s=36)
    ax.set_xlabel("size of the smaller observer (bits of record); the larger one holds $2^{15}$")
    ax.set_ylabel("disagreement\n(mean difference, relative)")
    ax.set_ylim(-0.03, max(naive) * 1.15)
    ax.legend(loc="upper right")
    ax.text(2**6.2, max(naive) * 0.08, "zero: on what both can see, they agree", color=NAVY, fontsize=8.5,
            style="italic", va="bottom")
    fig.savefig(OUT + "fig01.png"); plt.close(fig)
    return diff_naive, diff_fair


# --------------------------------------------------------------------------------------------
def h2(s):
    """Entropy (bits) of an equal mixture of two pure states with overlap s."""
    lam = np.clip(np.array([(1 + s) / 2, (1 - s) / 2]), 1e-300, 1)
    return -(lam * np.log2(lam)).sum(axis=0)


def darwinism_info(m, N, c):
    """Mutual information between a qubit and m of N environment qubits that each copied it imperfectly.

    State: (|0>|e0>^N + |1>|e1>^N)/sqrt2 with <e0|e1> = c. Every reduced state is an equal mixture of two
    pure states, so I(S:F) = h(c^N) + h(c^m) - h(c^(N-m)), with h the entropy above.
    """
    return h2(c ** N) + h2(c ** m) - h2(c ** (N - m))


def fig_darwinism():
    """Quantum Darwinism, toy version: a small fraction of the environment already holds the whole answer."""
    N = 60
    fig = plt.figure(figsize=(10, 4.6))
    gs = fig.add_gridspec(1, 2, width_ratios=[1, 1.55], wspace=0.22)
    a, b = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])

    # (a) A system, the photons that scattered off it, two observers each catching a few
    a.set_aspect("equal"); a.axis("off"); a.set_xlim(-1.5, 1.5); a.set_ylim(-1.45, 1.35)
    a.add_patch(Circle((0, 0), 0.2, fc=NAVY, ec="white", lw=1.5, zorder=4))
    a.text(0, 0, "S", color="white", ha="center", va="center", fontsize=11, weight="bold", zorder=5)
    rng = np.random.default_rng(4)
    ang = np.linspace(0, 2 * np.pi, 46, endpoint=False) + rng.normal(0, 0.03, 46)
    rad = rng.uniform(0.45, 1.05, 46)
    obsA, obsB = np.array([-1.18, 0.62]), np.array([1.02, -0.72])
    for t, r in zip(ang, rad):
        p = np.array([r * np.cos(t), r * np.sin(t)])
        near = min(np.linalg.norm(p - obsA), np.linalg.norm(p - obsB)) < 0.7
        a.annotate("", xy=p, xytext=0.22 * p / np.linalg.norm(p),
                   arrowprops=dict(arrowstyle="-|>,head_width=0.15,head_length=0.3",
                                   color=AMBER if near else LIGHT, lw=1.0 if near else 0.7))
    for o, lab in [(obsA, "A"), (obsB, "B")]:
        clock(a, *o, 0.12)
        a.text(o[0], o[1] - 0.22, lab, ha="center", va="top", fontsize=10, weight="bold", color=INK)
    a.text(0, 1.22, "Copies everywhere", ha="center", fontsize=11.5, weight="bold", color=INK)
    a.text(0, -1.2, "A and B read different photons,\nnever touching S or each other",
           ha="center", va="top", fontsize=9, style="italic", color=NAVY)

    # (b) The plateau: how much a fraction of the environment knows about S
    f = np.arange(N + 1) / N
    for c, col, lab in [(0.97, LIGHT, "weak copies"), (0.85, "#5b7fa6", "medium copies"),
                        (0.5, NAVY, "good copies")]:
        I = np.array([darwinism_info(m, N, c) for m in range(N + 1)])
        b.plot(f, I, color=col, lw=2.2, label=lab)
    b.axhline(1, color=GREY, lw=0.8, ls=(0, (3, 2)))
    b.text(0.22, 1.04, "everything there is to know about S (1 bit)", ha="left", fontsize=8.5, color=GREY)
    b.axvspan(0, 0.1, color=AMBER, alpha=0.12, lw=0)
    b.axvspan(0.9, 1.0, color=LIGHT, alpha=0.35, lw=0)
    b.text(0.05, 1.45, "A's\nshare\n(10%)", ha="center", fontsize=8.5, color="#9a5f06")
    b.text(0.95, 0.42, "beyond\n1 bit:\nonly with\nalmost\nall of it", ha="center", fontsize=8.5, color=GREY)
    b.set_xlim(0, 1); b.set_ylim(0, 2.1)
    b.set_xlabel("fraction of the environment an observer reads")
    b.set_ylabel("what it learns about S (bits)")
    b.legend(loc="upper left", bbox_to_anchor=(0.12, 0.98))
    b.set_title("The plateau: a small fraction already knows", fontsize=11, color=INK, weight="bold")
    fig.savefig(OUT + "fig02.png"); plt.close(fig)
    return darwinism_info(int(0.1 * N), N, 0.5)


# --------------------------------------------------------------------------------------------
def fig_horizons():
    """A de Sitter universe as a Penrose square: who can ever compare records with whom."""
    fig, ax = plt.subplots(figsize=(8.6, 6.4))
    ax.set_aspect("equal"); ax.axis("off"); ax.set_xlim(-1.75, 1.75); ax.set_ylim(-1.3, 1.25)

    # Shading: everything A can ever see (its causal past) and everything C can ever see; they overlap below
    ax.add_patch(Polygon([(-1, -1), (-1, 1), (1, -1)], fc=NAVY, alpha=0.13, lw=0))
    ax.add_patch(Polygon([(-1, -1), (1, -1), (1, 1)], fc=AMBER, alpha=0.18, lw=0))
    ax.plot([-1, 1, 1, -1, -1], [-1, -1, 1, 1, -1], color=INK, lw=1.4)
    ax.plot([-1, 1], [-1, 1], color=RED, lw=1.2, ls=(0, (4, 2)))
    ax.plot([-1, 1], [1, -1], color=RED, lw=1.2, ls=(0, (4, 2)))
    ax.text(0, 1.06, "far future", ha="center", fontsize=9, color=GREY, style="italic")
    ax.text(0, -1.1, "far past", ha="center", va="top", fontsize=9, color=GREY, style="italic")

    # Worldlines: A on the left edge, B close to A, C on the right edge
    t = np.linspace(-1, 1, 200)
    ax.plot(-np.ones_like(t), t, color=NAVY, lw=3)
    bx = -1 + 0.18 * np.cos(np.pi * t / 2) ** 1.5
    ax.plot(bx, t, color="#5b7fa6", lw=2.2)
    ax.plot(np.ones_like(t), t, color=AMBER, lw=3)
    ax.text(-1.07, -0.55, "A", ha="right", fontsize=12, weight="bold", color=NAVY)
    ax.text(-0.9, -0.82, "B", ha="left", fontsize=12, weight="bold", color="#5b7fa6")
    ax.text(1.07, -0.55, "C", ha="left", fontsize=12, weight="bold", color="#9a5f06")

    # A and B exchange records: a light ray from B to A and back
    y0 = -0.15
    xb = -1 + 0.18 * np.cos(np.pi * y0 / 2) ** 1.5
    ax.annotate("", xy=(-1, y0 + (xb + 1)), xytext=(xb, y0),
                arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1.4))
    ax.annotate("", xy=(xb, y0 + 2 * (xb + 1)), xytext=(-1, y0 + (xb + 1)),
                arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1.4))
    ax.text(-1.55, 0.62, "A and B meet\nand compare:\nconsistent", ha="center", va="center", fontsize=8.5,
            color=NAVY, style="italic")
    ax.annotate("", xy=(-0.97, 0.12), xytext=(-1.4, 0.45), arrowprops=dict(arrowstyle="-", color=NAVY, lw=0.7))

    # A and C each send a message early; a third observer D, between them, catches both
    D = (0, 0.6)
    ax.annotate("", xy=D, xytext=(-1, -0.4), arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1.3))
    ax.annotate("", xy=D, xytext=(1, -0.4), arrowprops=dict(arrowstyle="-|>", color="#9a5f06", lw=1.3))
    ax.annotate("", xy=(0.4, 1), xytext=D, arrowprops=dict(arrowstyle="-|>", color=GREY, lw=1.2, ls=(0, (3, 2))))
    clock(ax, D[0], D[1] + 0.07, 0.06)
    ax.text(0.1, 0.68, "D", fontsize=12, weight="bold", color=INK)
    ax.text(-0.08, 0.86, "A's message goes on,\nnever reaches C", fontsize=8.5, color=GREY, style="italic",
            ha="right", va="center")
    ax.text(1.55, 0.72, "D can compare\nboth messages,\nbut can never\ntell A or C", ha="center", va="center",
            fontsize=8.5, color=INK, style="italic")
    ax.annotate("", xy=(0.17, 0.66), xytext=(1.3, 0.72), arrowprops=dict(arrowstyle="-", color=INK, lw=0.7))

    ax.text(0, 0.1, "horizons", ha="center", fontsize=8.5, color=RED, style="italic")
    ax.text(0, -0.68, "common past:\nboth A and C can see it", ha="center", va="center", fontsize=8.5, color=INK)
    ax.text(-1.55, -0.3, "what A\ncan ever\nsee", ha="center", fontsize=8.5, color=NAVY, va="center")
    ax.text(1.55, -0.1, "what C\ncan ever\nsee", ha="center", fontsize=8.5, color="#9a5f06", va="center")
    ax.annotate("", xy=(-0.55, -0.3), xytext=(-1.38, -0.3), arrowprops=dict(arrowstyle="-", color=NAVY, lw=0.7))
    ax.annotate("", xy=(0.55, -0.1), xytext=(1.38, -0.1), arrowprops=dict(arrowstyle="-", color="#9a5f06", lw=0.7))
    ax.text(0, -1.27, "A and C can never compare with each other: for them, \"do we agree?\" has no answer",
            ha="center", fontsize=9, color=INK, style="italic")
    fig.savefig(OUT + "fig03.png"); plt.close(fig)


if __name__ == "__main__":
    print("fig01 disagreement naive / fair:", fig_two_records())
    print("fig02 bits known from 10%, good copies:", fig_darwinism())
    fig_horizons()
