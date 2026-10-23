"""Figures for "Nothing From Outside, Everything From Inside". Style matches the earlier essays.

All figures are schematic toys, not physics simulations. Run from this folder: python figs.py
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Circle, Wedge, FancyArrowPatch, ConnectionPatch

NAVY, GREY, RED, LIGHT, PALE, AMBER = "#1f4e79", "#7f8c8d", "#c0392b", "#d5dde5", "#eef1f4", "#d68910"
INK = "#2c3e50"
plt.rcParams.update({
    "font.family": "DejaVu Serif", "font.size": 10, "axes.spines.top": False,
    "axes.spines.right": False, "axes.linewidth": 1.0, "savefig.dpi": 200,
    "savefig.bbox": "tight", "legend.frameon": False, "legend.fontsize": 8.5,
})
OUT = "figures/"
# Night sky for the "seen from inside" images: deep navy to amber to white
SKY = LinearSegmentedColormap.from_list("sky", ["#0b1a2e", NAVY, "#5b7fa6", AMBER, "#fbeed7"])


def shaded_sphere(ax, cx, cy, r, base, n=400, alpha=1.0):
    """A lit sphere drawn as an image, so it reads as a ball rather than a disc."""
    x = np.linspace(-1, 1, n)
    X, Y = np.meshgrid(x, x)
    inside = X**2 + Y**2 <= 1
    Z = np.sqrt(np.clip(1 - X**2 - Y**2, 0, 1))
    light = np.array([-0.45, 0.55, 0.70]); light /= np.linalg.norm(light)
    shade = np.clip(X * light[0] + Y * light[1] + Z * light[2], 0, 1)
    rgb = np.array(matplotlib.colors.to_rgb(base))
    img = rgb[None, None, :] * (0.45 + 0.55 * shade[..., None]) + 0.35 * shade[..., None] ** 12
    rgba = np.dstack([np.clip(img, 0, 1), inside * alpha])
    ax.imshow(rgba, extent=[cx - r, cx + r, cy - r, cy + r], origin="lower", zorder=2, interpolation="bilinear")


def clock(ax, x, y, s, color=INK, z=6):
    """A small clock: the simplest observer, a system that keeps a record."""
    ax.add_patch(Circle((x, y), s, fc="white", ec=color, lw=1.4, zorder=z))
    ax.plot([x, x], [y, y + 0.7 * s], color=color, lw=1.4, zorder=z + 1, solid_capstyle="round")
    ax.plot([x, x + 0.5 * s], [y, y + 0.15 * s], color=color, lw=1.4, zorder=z + 1, solid_capstyle="round")


# --------------------------------------------------------------------------------------------
def fig_two_nothings():
    """Two kinds of nothing: one state without an observer, a full horizon with one."""
    fig = plt.figure(figsize=(9.6, 6.6))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.55, 1], hspace=0.28, wspace=0.18)
    a, b = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])
    c, d = fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1])
    rng = np.random.default_rng(3)

    # (a) A closed universe seen from nowhere: a ball with galaxies in it, and a single state
    a.set_aspect("equal"); a.axis("off"); a.set_xlim(-1.35, 1.35); a.set_ylim(-1.45, 1.3)
    shaded_sphere(a, 0, 0, 1, "#9fb3c8")
    pts = rng.normal(size=(140, 3)); pts /= np.linalg.norm(pts, axis=1)[:, None]
    pts *= rng.uniform(0.15, 0.95, (140, 1)) ** (1 / 3)
    a.scatter(pts[:, 0], pts[:, 1], s=rng.uniform(1, 9, 140), color="white", alpha=0.85, lw=0, zorder=3)
    a.text(0, 1.18, "No observer", ha="center", fontsize=11.5, weight="bold", color=INK)
    a.text(0, -1.17, "seen from nowhere: stars and galaxies included,\n"
           "the whole universe is one state", ha="center", va="top", fontsize=9, style="italic", color=NAVY)

    # (b) One observer at the centre: a horizon covered with tiles, every pattern equally likely
    b.set_aspect("equal"); b.axis("off"); b.set_xlim(-1.35, 1.35); b.set_ylim(-1.45, 1.3)
    b.add_patch(Circle((0, 0), 0.86, fc=PALE, ec="none", zorder=1))
    for k in range(18):                                  # lines of sight from the observer
        t = 2 * np.pi * k / 18
        b.plot([0.1 * np.cos(t), 0.84 * np.cos(t)], [0.1 * np.sin(t), 0.84 * np.sin(t)],
               color=NAVY, lw=0.5, alpha=0.35, zorder=2)
    for ring, (r0, r1, n) in enumerate([(0.86, 0.98, 72), (0.98, 1.10, 80)]):
        bits = rng.integers(0, 2, n)
        for i in range(n):
            b.add_patch(Wedge((0, 0), r1, 360 * i / n, 360 * (i + 1) / n, width=r1 - r0,
                              fc=AMBER if bits[i] else NAVY, ec="white", lw=0.5,
                              alpha=0.95 if bits[i] else 0.75, zorder=3))
    clock(b, 0, 0, 0.09)
    b.text(0, -0.2, "the observer:\nany system that\nkeeps a record", ha="center", va="top", fontsize=8.5,
           color=INK, zorder=7, bbox=dict(fc=PALE, ec="none", pad=1.5))
    b.text(0, 1.18, "One observer at the centre", ha="center", fontsize=11.5, weight="bold", color=INK)
    b.text(0, -1.17, "a horizon full of tiles: every pattern possible,\n"
           "none of them distinguishable", ha="center", va="top", fontsize=9, style="italic", color=NAVY)

    arrow = FancyArrowPatch((0.475, 0.74), (0.535, 0.74), transform=fig.transFigure,
                            arrowstyle="-|>,head_width=4,head_length=7", color=AMBER, lw=2.2)
    fig.patches.append(arrow)
    fig.text(0.505, 0.775, "add a\nreference\npoint", ha="center", fontsize=8.5, color=AMBER, weight="bold")

    # (c), (d) The same two universes as probability over their possible states
    n = 48
    for ax in (c, d):
        ax.spines["left"].set_visible(False); ax.set_yticks([])
        ax.set_xlim(-1, n); ax.set_ylim(0, 1.18); ax.set_xticks([])
        ax.set_xlabel("possible states of the universe", fontsize=9, color=GREY)
    c.vlines(n // 2, 0, 1, color=NAVY, lw=3)
    c.plot(n // 2, 1, "o", color=NAVY, ms=6)
    c.text(n // 2 + 1.5, 0.95, "probability 1", fontsize=9, color=NAVY, va="top")
    c.text(0, 1.1, "one state  ·  entropy 0  ·  nothing to know", fontsize=9.5, color=INK, weight="bold")
    p = np.full(n, 1 / n) * 20
    d.bar(np.arange(n), p, width=0.72, color=[AMBER if i % 2 else NAVY for i in range(n)], alpha=0.85)
    d.text(0, 1.1, "all states  ·  entropy maximal  ·  nothing to tell apart", fontsize=9.5, color=INK, weight="bold")
    d.annotate("every bar the same height", xy=(n * 0.62, p[0] + 0.02), xytext=(n * 0.52, 0.8),
               fontsize=8.5, color=GREY, arrowprops=dict(arrowstyle="-", color=GREY, lw=0.8))
    fig.text(0.5, 0.035, "Both are featureless. One has no possibilities; the other has all of them.",
             ha="center", fontsize=9.5, style="italic", color=INK)
    fig.savefig(OUT + "fig02.png"); plt.close(fig)


# --------------------------------------------------------------------------------------------
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


def fig_observer_size():
    """A bigger observer sees a richer, more accurate universe; a tiny one sees a blurry one."""
    field = cosmic_field()
    total_bits = 8 * field.size
    shown = [(2**7, "a tiny observer"), (2**11, "a larger one"), (2**15, "a large one")]
    fig = plt.figure(figsize=(10, 6.2))
    gs = fig.add_gridspec(2, 4, height_ratios=[1, 0.72], hspace=0.22, wspace=0.08)
    axes = [fig.add_subplot(gs[0, i]) for i in range(4)]
    vmin, vmax = 0, np.percentile(field, 99.5)
    for ax, (bits, name) in zip(axes, shown):
        ax.imshow(describe(field, bits), cmap=SKY, vmin=vmin, vmax=vmax, interpolation="bilinear")
        ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values(): s.set_visible(False)
        ax.set_title(f"{name}\n$2^{{{int(np.log2(bits))}}}$ bits of record", fontsize=9.5, color=INK)
    axes[3].imshow(field, cmap=SKY, vmin=vmin, vmax=vmax, interpolation="bilinear")
    axes[3].set_xticks([]); axes[3].set_yticks([])
    for s in axes[3].spines.values(): s.set_visible(False)
    axes[3].set_title("the whole toy universe\n(no one sees this)", fontsize=9.5, color=GREY, style="italic")
    for s in axes[3].spines.values(): s.set_visible(True); s.set_color(GREY); s.set_linestyle((0, (3, 2)))

    # Accuracy of the description against how much the observer can hold
    ax = fig.add_subplot(gs[1, :])
    bits = 2.0 ** np.linspace(5, np.log2(total_bits), 60)
    acc = [np.corrcoef(describe(field, b).ravel(), field.ravel())[0, 1] for b in bits]
    ax.semilogx(bits, acc, color=NAVY, lw=2.2, base=2)
    ax.fill_between(bits, 0, acc, color=NAVY, alpha=0.08)
    for b, name in shown:
        y = np.corrcoef(describe(field, b).ravel(), field.ravel())[0, 1]
        ax.plot(b, y, "o", color=AMBER, ms=7, mec="white", mew=1.2, zorder=5)
        ax.annotate(name, xy=(b, y), xytext=(b * 1.25, y - 0.13), fontsize=8.5, color="#9a5f06")
    ax.axhline(1, color=GREY, lw=1, ls=(0, (3, 2)))
    ax.text(bits[-1], 1.02, "a perfect description", color=GREY, fontsize=8.5, ha="right", va="bottom")
    ax.set_xlabel("how much the observer can hold (bits of record, log scale)", fontsize=9.5)
    ax.set_ylabel("how faithful its\ndescription is", fontsize=9.5)
    ax.set_ylim(0, 1.12); ax.set_xlim(bits[0], bits[-1])
    fig.savefig(OUT + "fig01.png"); plt.close(fig)


# --------------------------------------------------------------------------------------------
def bag_profile(z, rs=0.35, R=1.55, gap=0.06, neck=1.0):
    """Radius of a 'bag of gold' slice at height z: Flamm-like funnel above, big closed bulb below."""
    r = np.empty_like(z)
    up = z >= 0
    r[up] = rs * neck + z[up] ** 2 / (4 * rs)
    zc = -(R + gap)
    sph = np.sqrt(np.clip(R**2 - (z[~up] - zc) ** 2, 0, None))
    win = rs * neck * np.exp(-(z[~up] / 0.35) ** 2)
    r[~up] = (win**4 + sph**4) ** 0.25
    return r


def fig_bag_of_gold():
    """A small black hole from outside, a whole cosmos from inside, and the pinch-off."""
    fig = plt.figure(figsize=(10.2, 5.4))
    ax = fig.add_axes([-0.04, -0.04, 0.62, 1.08], projection="3d")
    zc, R, gap = -(1.55 + 0.06), 1.55, 0.06
    z = np.r_[np.linspace(zc - R + 1e-3, -1e-3, 260), np.linspace(0, 1.55, 120)]
    r = bag_profile(z)
    th = np.linspace(0, 2 * np.pi, 140)
    Z, TH = np.meshgrid(z, th)
    Rr = np.tile(r, (len(th), 1))
    X, Y = Rr * np.cos(TH), Rr * np.sin(TH)
    # Light the surface from its normals; bake a tile grid into the funnel (no z-order trouble)
    drdz = np.gradient(r, z)
    nz = -drdz / np.sqrt(1 + drdz**2); nr = 1 / np.sqrt(1 + drdz**2)
    N = np.stack([nr * np.cos(TH), nr * np.sin(TH), np.tile(nz, (len(th), 1))], -1)
    L = np.array([-0.55, -0.75, 0.45]); L /= np.linalg.norm(L)
    V = np.array([np.cos(np.radians(-62)) * 0.97, np.sin(np.radians(-62)) * 0.97, 0.24])
    diff = np.clip(np.abs(N @ L), 0, 1)
    H = (L + V) / np.linalg.norm(L + V); spec = np.clip(np.abs(N @ H), 0, 1) ** 40
    up = Z >= 0
    base = np.where(up[..., None], np.array(matplotlib.colors.to_rgb("#7f9cbc")), np.array(matplotlib.colors.to_rgb(AMBER)))
    grid = up & ((np.abs(((TH * 180 / np.pi) % 15) - 7.5) > 6.9) | (np.abs((Z % 0.18) - 0.09) > 0.08))
    base = np.where(grid[..., None], base * 0.55, base)
    rgb = np.clip(base * (0.35 + 0.65 * diff[..., None]) + 0.35 * spec[..., None], 0, 1)
    ax.plot_surface(X, Y, Z, facecolors=rgb, rstride=1, cstride=1, lw=0, antialiased=True, shade=False)
    neck = bag_profile(np.array([0.0]))[0]
    ax.plot(neck * np.cos(th), neck * np.sin(th), 0, color=RED, lw=2.2)
    ax.set_box_aspect((4.4, 4.4, 1.6 - (zc - R))); ax.view_init(elev=14, azim=-62)
    ax.set_xlim(-2.2, 2.2); ax.set_ylim(-2.2, 2.2); ax.set_zlim(zc - R, 1.6); ax.axis("off")
    ax.text2D(0.75, 0.86, "outside: our universe.\nA small black hole,\nsome tiles on its surface",
              transform=ax.transAxes, fontsize=9, color=NAVY)
    ax.text2D(0.62, 0.575, "the neck: the\nhorizon", transform=ax.transAxes, fontsize=9, color=RED)
    ax.text2D(0.70, 0.22, "inside: a whole\ncosmos, expanding", transform=ax.transAxes, fontsize=9,
              color="#9a5f06", weight="bold")
    ax.text2D(0.08, 0.93, "A 'bag of gold'", transform=ax.transAxes, fontsize=11.5, weight="bold", color=INK)

    # Pinch-off sequence, as slices through the middle
    titles = ["connected", "the neck closes", "pinched off"]
    notes = ["counts as its\nhorizon tiles", "fewer and\nfewer tiles", "from outside:\none state"]
    for i, (nk, t, nt) in enumerate(zip([1.0, 0.35, 0.0], titles, notes)):
        sub = fig.add_axes([0.60 + i * 0.135, 0.12, 0.12, 0.66])
        sub.set_aspect("equal"); sub.axis("off")
        zz = np.r_[zc - R, np.linspace(zc - R + 1e-3, -1e-3, 300), np.linspace(0, 1.55, 100)]
        rr = bag_profile(zz, neck=nk) if nk > 0 else bag_profile(zz, neck=1e-3)
        rr[0] = 0
        if nk == 0:
            top = zz >= 0
            sub.plot(rr[top], zz[top] + 0.25, color=NAVY, lw=1.6); sub.plot(-rr[top], zz[top] + 0.25, color=NAVY, lw=1.6)
            sub.plot([-0.02, 0.02], [0.25, 0.25], color=NAVY, lw=1.6)
            sub.fill_betweenx(zz[~top], -rr[~top], rr[~top], color=AMBER, alpha=0.35, lw=0)
            sub.plot(rr[~top], zz[~top], color="#9a5f06", lw=1.6); sub.plot(-rr[~top], zz[~top], color="#9a5f06", lw=1.6)
            sub.plot(0, 0.25, "o", color=RED, ms=3)
        else:
            sub.fill_betweenx(zz[zz < 0], -rr[zz < 0], rr[zz < 0], color=AMBER, alpha=0.35, lw=0)
            sub.plot(rr, zz, color=NAVY, lw=1.6); sub.plot(-rr, zz, color=NAVY, lw=1.6)
            sub.plot([-rr[zz >= 0][0], rr[zz >= 0][0]], [0, 0], color=RED, lw=2)
        sub.set_xlim(-1.8, 1.8); sub.set_ylim(zc - R - 0.1, 1.9)
        sub.text(0, 2.05, t, ha="center", fontsize=9, color=INK, weight="bold")
        sub.text(0, zc - R - 0.25, nt, ha="center", va="top", fontsize=8.5, color=RED if nk == 0 else GREY,
                 style="italic")
        if i < 2:
            fig.patches.append(FancyArrowPatch((0.60 + i * 0.135 + 0.115, 0.45), (0.60 + (i + 1) * 0.135 + 0.005, 0.45),
                                               transform=fig.transFigure, arrowstyle="-|>,head_width=2.5,head_length=5",
                                               color=GREY, lw=1))
    fig.text(0.802, 0.86, "The bubble pinches off. From inside, it stays everything.", ha="center", fontsize=9.5, style="italic", color="#9a5f06")
    fig.savefig(OUT + "fig03.png"); plt.close(fig)


# --------------------------------------------------------------------------------------------
def grow(rng, depth, maxdepth):
    """A grain: some smaller grains placed inside it without overlap, recursively. Unit radius."""
    kids = []
    if depth >= maxdepth:
        return {"kids": kids, "stars": rng.uniform(-0.7, 0.7, (25, 2))}
    for _ in range(400):
        if len(kids) >= 7:
            break
        r = rng.uniform(0.13, 0.27) if kids else 0.30
        ang, rad = rng.uniform(0, 2 * np.pi), rng.uniform(0, 0.93 - r)
        x, y = rad * np.cos(ang), rad * np.sin(ang)
        if all(np.hypot(x - k["x"], y - k["y"]) > r + k["r"] + 0.035 for k in kids):
            kids.append({"x": x, "y": y, "r": r})
    for k in kids:
        k.update(grow(rng, depth + 1, maxdepth))
    stars = rng.uniform(-0.9, 0.9, (90, 2))
    stars = stars[np.hypot(*stars.T) < 0.92]
    stars = stars[[all(np.hypot(sx - k["x"], sy - k["y"]) > k["r"] + 0.02 for k in kids) for sx, sy in stars]]
    return {"kids": kids, "stars": stars}


LEVEL = ["#0b1a2e", NAVY, "#5b7fa6", AMBER, "#e8b45c", "#f6dcae"]


def draw_grain(ax, g, cx, cy, r, depth, start, shown=3):
    """Draw a grain; deeper than `shown` levels below the view, a grain is just a dot: one state."""
    rel = depth - start
    col = LEVEL[min(depth, len(LEVEL) - 1)]
    if rel > shown:
        ax.add_patch(Circle((cx, cy), r, fc=col, ec="none", alpha=0.9, zorder=10 + depth))
        return
    ax.add_patch(Circle((cx, cy), r, fc=col, ec="white", lw=max(0.3, 1.6 - 0.45 * rel), zorder=10 + depth))
    st = g.get("stars", np.empty((0, 2)))
    if len(st):
        ax.scatter(cx + r * st[:, 0], cy + r * st[:, 1], s=max(0.3, 3.5 - 1.1 * rel), color="white",
                   alpha=0.7, lw=0, zorder=10 + depth)
    for k in g["kids"]:
        draw_grain(ax, k, cx + r * k["x"], cy + r * k["y"], r * k["r"], depth + 1, start, shown)


def fig_grains():
    """Grains inside grains, each one a single state to the grain around it and a cosmos to its own."""
    rng = np.random.default_rng(11)
    root = grow(rng, 0, 6)
    fig, axes = plt.subplots(1, 3, figsize=(10.4, 4.3), gridspec_kw={"wspace": 0.42})
    path = [root, root["kids"][0], root["kids"][0]["kids"][0]]
    labels = ["our universe", "a grain inside it", "a grain inside the grain"]
    for i, (ax, g, lab) in enumerate(zip(axes, path, labels)):
        ax.set_aspect("equal"); ax.axis("off"); ax.set_xlim(-1.08, 1.08); ax.set_ylim(-1.3, 1.15)
        draw_grain(ax, g, 0, 0, 1, i, i)
        ax.text(0, -1.13, lab, ha="center", va="top", fontsize=10, color=INK, weight="bold")
        ax.text(0, 1.08, "to its inhabitants: everything", ha="center", fontsize=8.5, color="#9a5f06", style="italic")
        if i < 2:
            k = g["kids"][0]
            ax.add_patch(Circle((k["x"], k["y"]), k["r"] * 1.12, fc="none", ec=RED, lw=1.4, zorder=40))
            for sgn in (1, -1):
                con = ConnectionPatch(xyA=(k["x"], k["y"] + sgn * k["r"] * 1.12), coordsA=ax.transData,
                                      xyB=(-0.0, sgn * 1.0), coordsB=axes[i + 1].transData,
                                      color=RED, lw=0.8, alpha=0.7, ls=(0, (3, 2)))
                fig.add_artist(con)
            p0 = axes[i].get_position(); p1 = axes[i + 1].get_position()
            fig.text((p0.x1 + p1.x0) / 2, 0.1, "seen from\nthe grain around it:\none state", ha="center",
                     va="bottom", fontsize=8.5, color=RED, style="italic")
    fig.text(0.94, 0.5, "…", fontsize=26, color=GREY, ha="center", va="center")
    fig.savefig(OUT + "fig04.png"); plt.close(fig)


# --------------------------------------------------------------------------------------------
def fig_question():
    """An analogy, not physics: a space of possible answers, and what a question does to it."""
    rng = np.random.default_rng(2)
    n = 300
    xs = np.linspace(-3, 3, n); X, Y = np.meshgrid(xs, xs)
    centres = rng.normal(0, 1.2, (260, 2)); w = rng.gamma(2.0, 1.0, 260); s = rng.uniform(0.12, 0.35, 260)
    prior = sum(wi * np.exp(-((X - c[0]) ** 2 + (Y - c[1]) ** 2) / (2 * si**2)) for c, wi, si in zip(centres, w, s))
    q = np.array([1.1, 0.7])                                   # where the question comes from
    like = np.exp(-((X - q[0]) ** 2 + (Y - q[1]) ** 2) / (2 * 0.24**2))
    post = prior * like

    def bits(p):
        p = p / p.sum(); p = p[p > 0]
        return -(p * np.log2(p)).sum()

    fig, (a, b) = plt.subplots(1, 2, figsize=(9.6, 4.6), gridspec_kw={"wspace": 0.25})
    for ax, img, title, h in [(a, prior, "before anyone asks", bits(prior)), (b, post, "after a question", bits(post))]:
        ax.imshow(img / img.max(), extent=[-3, 3, -3, 3], origin="lower", cmap=SKY, interpolation="bilinear",
                  vmin=0, vmax=1 if ax is b else 0.8)
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values(): sp.set_visible(False)
        ax.set_title(title, fontsize=11, color=INK, weight="bold", pad=20)
        ax.text(-2.85, -2.85, f"spread ≈ {h:.1f} bits", color="white", fontsize=9, va="bottom")
    a.text(0, 3.1, "every answer weighted, none chosen", ha="center", fontsize=8.5, color=GREY, style="italic")
    b.text(0, 3.1, "the possibilities narrow into one", ha="center", fontsize=8.5, color=GREY, style="italic")
    clock(b, q[0] + 0.85, q[1] + 0.9, 0.13, color=AMBER)
    b.annotate("", xy=(q[0] + 0.15, q[1] + 0.15), xytext=(q[0] + 0.75, q[1] + 0.8),
               arrowprops=dict(arrowstyle="-|>", color=AMBER, lw=1.8))
    b.text(q[0] + 0.62, q[1] + 1.2, "a question from\na particular place", color="#fbeed7", fontsize=8.5, ha="right")
    fig.patches.append(FancyArrowPatch((0.49, 0.5), (0.535, 0.5), transform=fig.transFigure,
                                       arrowstyle="-|>,head_width=4,head_length=7", color=AMBER, lw=2.2))
    fig.text(0.5, 0.02, "the space of possible answers, drawn flat  ·  an analogy, not physics",
             ha="center", fontsize=8.5, color=GREY, style="italic")
    fig.savefig(OUT + "fig05.png"); plt.close(fig)


if __name__ == "__main__":
    fig_two_nothings()
    fig_observer_size()
    fig_bag_of_gold()
    fig_grains()
    fig_question()
