"""Figures for "The Time We Cannot Compress".

On purpose, these figures do not use the site's usual style (Inter type, white cards,
the navy and amber palette). The essay is partly about everything starting to look the
same, so the figures are drawn like an old engraved plate instead: sepia ink on paper,
serif italic type, hatching instead of fills, slightly unsteady lines.

Both figures are schematics, my own; neither shows data.
Figure 1: proper time along four paths between the same two events (special relativity).
          At rest: 10 ticks; 0.6 c: 8; 0.9 c: about 4.4; light: 0.
Figure 2: wandering paths that end in different places, and fast, straight paths that
          all arrive at the same plausible point.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PAPER = "#f3ead7"
INK = "#3b2a1a"
FADED = "#8a7356"
RUST = "#9c3d1f"
SERIF = "FreeSerif"
plt.rcParams.update({
    "font.family": SERIF, "font.style": "italic", "font.size": 12, "text.color": INK,
    "figure.facecolor": PAPER, "axes.facecolor": PAPER, "savefig.facecolor": PAPER,
    "savefig.bbox": "tight", "savefig.pad_inches": 0.4,
})
OUT = "figures/"
rng = np.random.default_rng(7)


def wobble(x, y, amp=0.012, n=None):
    """Resample a polyline and add a small hand tremor."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    d = np.r_[0, np.cumsum(np.hypot(np.diff(x), np.diff(y)))]
    n = n or max(30, int(d[-1] * 60))
    t = np.linspace(0, d[-1], n)
    xs, ys = np.interp(t, d, x), np.interp(t, d, y)
    noise = np.convolve(rng.normal(0, amp, n), np.ones(5) / 5, mode="same")
    return xs + noise, ys + np.roll(noise, 3)


def ink(ax, x, y, lw=1.3, c=INK, amp=0.012, **kw):
    xs, ys = wobble(x, y, amp)
    ax.plot(xs, ys, color=c, lw=lw, solid_capstyle="round", **kw)


def frame(ax):
    """A double ruled border, like a printed plate."""
    ax.axis("off")
    x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim()
    for m, lw in ((0, 1.4), (0.08 * (x1 - x0) / 10, 0.5)):
        ax.plot([x0 + m, x1 - m, x1 - m, x0 + m, x0 + m],
                [y0 + m, y0 + m, y1 - m, y1 - m, y0 + m], color=INK, lw=lw)


def save(fig, name):
    fig.savefig(OUT + name + ".svg")
    fig.savefig(OUT + name + ".png", dpi=400)
    plt.close(fig)


# ---------- Figure 1: the slow path holds the most time ----------
def fig01():
    T = 10.0
    fig, ax = plt.subplots(figsize=(6.4, 8.3))
    ax.set_xlim(-7.0, 7.0); ax.set_ylim(-5.6, 12.6); ax.set_aspect("equal")

    # light cone of A and past cone of B, hatched
    for k in np.linspace(0.3, 9.7, 30):
        h = min(k, T - k)
        ink(ax, [-h, h], [k, k], lw=0.35, c=FADED, amp=0.01)
    ink(ax, [0, -5, 0], [0, 5, T], lw=0.9, c=FADED)
    ink(ax, [0, 5, 0], [0, 5, T], lw=0.9, c=FADED)

    paths = [  # (speed, colour, letter, letter position, lw)
        (0.0, INK, "a", (0.55, 6.6), 1.8),
        (-0.6, INK, "b", (-3.0 + 0.85, 5.0), 1.3),
        (0.9, INK, "c", (4.5 - 1.1, 5.0), 1.3),
        (-1.0, RUST, "d", (-5.0 - 0.75, 5.0), 1.5),
    ]
    for v, c, let, (lx, ly), lw in paths:
        xm = v * T / 2
        ink(ax, [0, xm, 0], [0, T / 2, T], lw=lw, c=c, amp=0.008)
        tau = T * np.sqrt(max(0.0, 1 - v * v))
        n = int(np.ceil(tau)) if abs(v) < 1 else 0
        for i in range(1, n + 1):
            frac = i / tau
            if frac >= 0.999: break
            px = xm * (2 * frac if frac <= 0.5 else 2 - 2 * frac)
            ax.plot([px - 0.25, px + 0.25], [T * frac, T * frac], color=c, lw=1.4)
        ax.text(lx, ly, let, ha="center", va="center", fontsize=19, color=c)
    key = [("a", "at rest", "10", INK), ("b", "at 0.6 c", "8", INK),
           ("c", "at 0.9 c", "4.4", INK), ("d", "light", "0", RUST)]
    for i, (let, what, lived, c) in enumerate(key):
        x0, y0 = -3.6, -2.0 - i * 1.0
        ax.text(x0, y0, f"{let}.  {what}, time lived: {lived}", fontsize=15.5, color=c,
                va="center")
    for y, name in ((0, "A, a question"), (T, "B, an answer")):
        ax.add_patch(plt.Circle((0, y), 0.16, color=INK, zorder=5))
        ax.text(0.45, y, name, va="center", fontsize=16)
    ax.annotate("", xy=(-6.3, 11.4), xytext=(-6.3, -0.9),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.9))
    ax.text(-6.1, 11.2, "time", fontsize=15)
    ax.annotate("", xy=(6.3, -0.9), xytext=(-6.3, -0.9),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.9))
    ax.text(6.2, -0.5, "space", ha="right", fontsize=15)
    ax.text(0, 11.95, "Plate I. The slow path holds the most time", ha="center",
            fontsize=17)
    frame(ax)
    save(fig, "fig01")


# ---------- Figure 2: slow paths differ, fast paths agree ----------
def fig02():
    fig, axes = plt.subplots(2, 1, figsize=(5.6, 11.0))
    for ax in axes:
        ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.set_aspect("equal")

    # left: wandering paths, each ending somewhere of its own
    ax = axes[0]
    ends = []
    starts = np.linspace(1.8, 8.2, 7)
    goals = [(8.6, 2.2), (6.4, 7.9), (8.8, 5.2), (5.4, 3.0), (7.6, 8.4), (6.8, 6.0), (7.9, 3.9)]
    for y0, (gx, gy) in zip(starts, goals):
        n = 12
        t = np.linspace(0, 1, n + 1)
        x = 1.2 + (gx - 1.6) * t + rng.normal(0, 0.25, n + 1) * np.sin(np.pi * t)
        y = y0 + (gy - y0) * t + np.convolve(rng.normal(0, 0.7, n + 1), np.ones(3) / 3,
                                             mode="same") * np.sin(np.pi * t)
        x[0], y[0], x[-1], y[-1] = 1.2, y0, gx - 0.4, gy
        ink(ax, x, y, lw=1.0, amp=0.03)
        ax.add_patch(plt.Circle((1.2, y0), 0.1, color=INK))
        ends.append((gx, gy))
    for j, (ex, ey) in enumerate(ends):
        kind = j % 4
        if kind == 0:
            ax.add_patch(plt.Circle((ex, ey), 0.28, fc="none", ec=INK, lw=1.1))
        elif kind == 1:
            ax.plot([ex - .3, ex, ex + .3, ex - .3], [ey - .25, ey + .3, ey - .25, ey - .25], color=INK, lw=1.1)
        elif kind == 2:
            th = np.linspace(0, 2 * np.pi, 11)
            r = np.where(np.arange(11) % 2, 0.14, 0.34)
            ax.plot(ex + r * np.cos(th), ey + r * np.sin(th), color=INK, lw=1.0)
        else:
            th = np.linspace(0, 4 * np.pi, 60)
            ax.plot(ex + 0.05 * th * np.cos(th), ey + 0.05 * th * np.sin(th), color=INK, lw=0.9)
    ax.text(5, 9.35, "made slowly", ha="center", fontsize=18)
    ax.text(5, 0.55, "every path leaves its own mark", ha="center", fontsize=15, color=FADED)
    frame(ax)

    # right: straight paths, all arriving at the same place
    ax = axes[1]
    target = (8.2, 5.0)
    for y0 in np.linspace(1.8, 8.2, 7):
        ink(ax, [1.2, target[0] - 0.4], [y0, target[1]], lw=1.0, amp=0.004)
        ax.add_patch(plt.Circle((1.2, y0), 0.1, color=INK))
    ax.add_patch(plt.Rectangle((target[0] - 0.4, target[1] - 0.4), 0.8, 0.8,
                               fc="none", ec=RUST, lw=1.6))
    for k in range(4):
        d = 0.12 * (k + 1)
        ax.add_patch(plt.Rectangle((target[0] - 0.4 + d * .25, target[1] - 0.4 - d * .25), 0.8, 0.8,
                                   fc="none", ec=RUST, lw=0.5, alpha=0.6))
    ax.text(5, 9.35, "made fast", ha="center", fontsize=18)
    ax.text(5, 0.55, "every path arrives at the plausible", ha="center", fontsize=15, color=FADED)
    frame(ax)
    fig.suptitle("Plate II. Where the differences are made", fontsize=18, y=0.915)
    save(fig, "fig02")


if __name__ == "__main__":
    fig01()
    fig02()
