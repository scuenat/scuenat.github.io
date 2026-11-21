"""Figure for "A Universe Without a Bottom". Style matches the earlier essays."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import sys, pathlib  # hand-drawn house style: _figstyle/handdrawn.py at the site root
sys.path.insert(0, str(next(p / "_figstyle" for p in pathlib.Path(__file__).resolve().parents if (p / "_figstyle").is_dir())))
import handdrawn; handdrawn.apply()

NAVY, GREY, RED, LIGHT, PALE, AMBER = "#1f4e79", "#7f8c8d", "#c0392b", "#d5dde5", "#eef1f4", "#d68910"
INK = "#2c3e50"
plt.rcParams.update({
    "font.family": "DejaVu Serif", "font.size": 10, "axes.spines.top": False,
    "axes.spines.right": False, "axes.linewidth": 1.0, "savefig.dpi": 200,
    "savefig.bbox": "tight", "legend.frameon": False, "legend.fontsize": 8.5,
})
OUT = "figures/"


def fig_area_law():
    """Left: a horizon covered with tiles. Right: doubling the size, volume x8, information x4."""
    fig, (a, b) = plt.subplots(1, 2, figsize=(9, 3.9), gridspec_kw={"width_ratios": [1, 1.15]})

    # Globe seen from the side: latitude lines, longitude lines, a patch of tiles shaded
    a.set_aspect("equal"); a.axis("off")
    a.add_patch(plt.Circle((0, 0), 1, fc=PALE, ec=NAVY, lw=1.6))
    lats = np.radians(np.arange(-75, 76, 15))
    lons = np.radians(np.arange(-75, 76, 15))
    for la in lats:
        a.plot([-np.cos(la), np.cos(la)], [np.sin(la)] * 2, color=NAVY, lw=0.5, alpha=0.5)
    t = np.linspace(-np.pi / 2, np.pi / 2, 100)
    for lo in lons:
        a.plot(np.sin(lo) * np.cos(t), np.sin(t), color=NAVY, lw=0.5, alpha=0.5)
    for i, lo0 in enumerate(lons[4:7]):
        for j, la0 in enumerate(lats[5:7]):
            la = np.linspace(la0, la0 + np.radians(15), 12)
            lo1 = lo0 + np.radians(15)
            x = np.r_[np.sin(lo0) * np.cos(la), np.sin(lo1) * np.cos(la[::-1])]
            y = np.r_[np.sin(la), np.sin(la[::-1])]
            a.fill(x, y, color=AMBER, alpha=0.9 if (i + j) % 2 else 0.6, lw=0)
    a.annotate("each tile: the smallest\narea physics knows", xy=(0.3, 0.12),
               xytext=(1.15, 0.85), fontsize=9, color=INK, ha="left",
               arrowprops=dict(arrowstyle="-", color=GREY, lw=0.9))
    a.text(0, -1.25, "count the tiles on the surface,\nand you have counted everything inside",
           ha="center", va="top", fontsize=9, style="italic", color=NAVY)
    a.set_xlim(-1.2, 2.3); a.set_ylim(-1.75, 1.15)

    # Doubling the size: volume x8 against area (information) x4
    x = np.arange(2); w = 0.36
    vol, area = [1, 8], [1, 4]
    b.bar(x - w / 2, vol, w, color=LIGHT, label="room inside (volume)")
    b.bar(x + w / 2, area, w, color=NAVY, label="information it can hold (area)")
    for xi, v, s in zip(x, vol, area):
        b.text(xi - w / 2, v + 0.15, f"×{v}", ha="center", fontsize=10, color=GREY)
        b.text(xi + w / 2, s + 0.15, f"×{s}", ha="center", fontsize=10, color=NAVY, weight="bold")
    b.set_xticks(x, ["black hole", "twice as wide"])
    b.set_yticks([]); b.spines["left"].set_visible(False)
    b.set_ylim(0, 11)
    b.legend(loc="upper left", bbox_to_anchor=(0, 1.02))
    fig.savefig(OUT + "fig01.png"); plt.close(fig)



def fig_cover():
    """Card image: a horizon tiled with information (left) and circles inside circles,
    a universe without a bottom (right)."""
    from matplotlib.patches import Circle, Wedge
    fig, ax = plt.subplots(figsize=(6.46, 3.53))
    ax.set_xlim(0, 13); ax.set_ylim(0, 7.1); ax.set_aspect("equal"); ax.axis("off")
    cx, cy, r = 3.7, 3.55, 2.45
    n = 40
    for i in range(n):
        a0 = 360 * i / n
        ax.add_patch(Wedge((cx, cy), r + 0.27, a0 + 1.2, a0 + 360 / n - 1.2, width=0.27,
                           fc=AMBER if i % 2 else "#f0b75a", ec="none"))
    ax.add_patch(Circle((cx, cy), r, fc=NAVY, ec=NAVY, lw=1.4))
    ax.text(cx, cy, r"$S = \dfrac{A}{4\,\ell_P^{\,2}}$", ha="center", va="center", fontsize=26, color="white")

    def nest(x, y, rr, depth):
        ax.add_patch(Circle((x, y), rr, fc="none", ec=NAVY, lw=max(2.4 * rr / 2.45, 0.5)))
        if depth == 0:
            return
        k = 0.45
        for ang in (90, 210, 330):
            t = np.radians(ang)
            nest(x + rr * 0.53 * np.cos(t), y + rr * 0.53 * np.sin(t), rr * k, depth - 1)

    nest(9.4, 3.55, 2.45, 4)
    ax.add_patch(Circle((9.4, 3.55), 0.08, fc=AMBER, ec=AMBER))
    fig.savefig(OUT + "cover.png", dpi=255, bbox_inches="tight", pad_inches=0.05); plt.close(fig)


if __name__ == "__main__":
    fig_area_law()
    fig_cover()
