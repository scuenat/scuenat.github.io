"""Figures for "Show What Changed, Not the Data", in the site's house figure style.
Run: python figs.py   (needs matplotlib, numpy)
All data is simulated, as in the paper. Figures 1-9 redraw the paper's figures from the same
recipes. Figures 10 and 11 come from a small re-run of the copilot simulation (section 11): the same
model (weekly cycle, growth, export replacing draft, shared server swings, a slow drift in
translate from day 45, code agent 25% slower for German from day 60), with a fixed seed; the
tiles' normal range is set so they raise the paper's 106 flags. Figure 12 plots the paper's
own values for the translate agent.
Written as a 400 dpi PNG (page and card) and an SVG."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import sys, pathlib  # house figure style: _figstyle/house.py at the site root
sys.path.insert(0, str(next(p / "_figstyle" for p in pathlib.Path(__file__).resolve().parents if (p / "_figstyle").is_dir())))
import house; house.apply()
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Ellipse

NAVY, RED, GREY, INK, MUTED, LINE = "#1f4e79", "#c0392b", "#7f8c8d", "#1f2328", "#6b7680", "#d0d7de"
PALE_RED = "#f6d5d0"
plt.rcParams.update({
    "font.size": 11, "text.color": INK, "axes.edgecolor": INK, "axes.labelcolor": INK,
    "xtick.color": INK, "ytick.color": INK, "axes.spines.top": False, "axes.spines.right": False,
    "legend.frameon": False, "figure.facecolor": "white", "axes.facecolor": "white",
    "savefig.dpi": 400, "savefig.bbox": "tight", "savefig.pad_inches": 0.35,
})
OUT = "figures/"


def save(fig, name):
    fig.savefig(OUT + name + ".png")
    plt.close(fig)


def box(ax, x, y, w, h, fc, title, sub=None, tc="white", fs=13, sfs=10.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.12", fc=fc, ec=fc, lw=1.4))
    if sub:
        ax.text(x + w / 2, y + h * 0.64, title, ha="center", va="center", color=tc, fontsize=fs, weight="bold")
        ax.text(x + w / 2, y + h * 0.3, sub, ha="center", va="center", color=tc, fontsize=sfs)
    else:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center", color=tc, fontsize=fs, weight="bold")


def arrow(ax, p, q, color=GREY, rad=0.0, lw=1.6):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=14, color=color, lw=lw,
                                 connectionstyle=f"arc3,rad={rad}", shrinkA=0, shrinkB=0))


truth = lambda x: np.sin(1.6 * x) * 0.85


# ---------- 1. the curve that fits too well ----------
def fig01():
    rng = np.random.default_rng(3)
    x = np.linspace(-1, 1, 16)
    y = truth(x) + rng.normal(0, 0.18, x.size)
    xs = np.linspace(-1, 1, 800)
    p15 = np.polynomial.Polynomial.fit(x, y, 15)
    p3 = np.polynomial.Polynomial.fit(x, y, 3)
    fig, ax = plt.subplots(figsize=(6.6, 4.4))
    ax.plot(xs, truth(xs), color=GREY, lw=1.6, ls="--", label="underlying reality")
    ax.plot(xs, p15(xs), color=RED, lw=1.6, label="degree 15: fits every point")
    ax.plot(xs, p3(xs), color=NAVY, lw=2.6, label="degree 3: fits the shape")
    ax.scatter(x, y, s=34, color=INK, zorder=5, label="observations")
    ax.set_ylim(-1.3, 1.3); ax.set_xlabel("x"); ax.set_ylabel("y")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=2, fontsize=10.5)
    save(fig, "fig01")


# ---------- 2. explaining the past vs predicting ----------
def fig02():
    rng = np.random.default_rng(3)
    x = np.linspace(-1, 1, 16); y = truth(x) + rng.normal(0, 0.18, x.size)
    xt = np.linspace(-1.05, 1.05, 400); yt = truth(xt)
    deg = np.arange(16); fit, pred = [], []
    for d in deg:
        p = np.polynomial.Polynomial.fit(x, y, d)
        fit.append(np.mean((p(x) - y) ** 2) + 1e-4)
        pred.append(np.mean((p(xt) - yt) ** 2) + 0.02)
    fig, ax = plt.subplots(figsize=(6.6, 3.9))
    ax.set_yscale("log")
    ax.plot(deg, fit, color=GREY, lw=2, marker="o", ms=5, label="fit to what was measured")
    ax.plot(deg, pred, color=NAVY, lw=2.6, marker="o", ms=5, label="accuracy where it matters")
    best = int(np.argmin(pred))
    ax.axvline(best, color=RED, lw=1.2, ls=":")
    ax.annotate("sweet spot", (best, pred[best]), (best + 2.5, pred[best] * 12), color=RED, fontsize=11.5,
                arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.2))
    ax.set_xlabel("complexity (degree, or metrics shown)"); ax.set_ylabel("error (log)")
    ax.legend(loc="upper center", fontsize=10.5)
    save(fig, "fig02")


# ---------- 3. lots of data, few numbers ----------
def fig03():
    rng = np.random.default_rng(7)
    f = lambda x, y: 0.9 - 0.35 * x ** 2 - 0.3 * y ** 2 + 0.15 * x * y + 0.1 * x - 0.05 * y
    X = rng.uniform(-1.5, 1.5, 120); Y = rng.uniform(-1.5, 1.5, 120); Z = f(X, Y) + rng.normal(0, 0.12, 120)
    gx, gy = np.meshgrid(np.linspace(-1.5, 1.5, 30), np.linspace(-1.5, 1.5, 30))
    fig = plt.figure(figsize=(5.6, 5.0))
    ax = fig.add_subplot(projection="3d")
    ax.plot_surface(gx, gy, f(gx, gy), cmap="Blues_r", alpha=0.75, linewidth=0, antialiased=True, vmin=-1.6, vmax=1.4)
    ax.scatter(X, Y, Z, color=RED, s=16, depthshade=False)
    ax.set_xlabel("x"); ax.set_ylabel("y"); ax.view_init(24, -58)
    for a in (ax.xaxis, ax.yaxis, ax.zaxis):
        a.pane.set_facecolor("white"); a.pane.set_edgecolor(LINE)
    save(fig, "fig03")


# ---------- 4. the information funnel ----------
def fig04():
    fig, ax = plt.subplots(figsize=(7.2, 3.9))
    ax.set_xlim(0, 10); ax.set_ylim(0, 5.4); ax.axis("off")
    rows = [(10.0, GREY, "Raw observations", "millions of events"),
            (7.0, NAVY, "Model / compression", "a few meaningful terms"),
            (4.2, NAVY, "Signal", "3 things moved, 1 matters"),
            (2.0, RED, "Decision", "act, or don't")]
    for i, (w, c, t, s) in enumerate(rows):
        y = 4.35 - i * 1.35
        box(ax, 5 - w / 2 + 0.05, y, w - 0.1, 0.95, c, t, s)
        if i < 3:
            arrow(ax, (5, y - 0.04), (5, y - 0.36), color=GREY)
    save(fig, "fig04")


# ---------- 5. summarising is discovering ----------
def fig05():
    fig, ax = plt.subplots(figsize=(7.4, 6.2))
    ax.set_xlim(0, 10); ax.set_ylim(1.2, 9.6); ax.axis("off")
    ax.text(0.05, 9.35, "History", fontsize=14, weight="bold", color=NAVY)
    for i, (c, t, s, lab) in enumerate([(GREY, "Tycho", "decades of positions", "data"),
                                         (NAVY, "Kepler", "3 laws", "compression"),
                                         (RED, "Newton", "1 rule", "rule")]):
        x = 0.1 + i * 3.4
        box(ax, x, 7.75, 3.0, 1.3, c, t, s)
        ax.text(x + 1.5, 7.4, lab, ha="center", color=c, fontsize=11.5, style="italic")
        if i < 2:
            arrow(ax, (x + 3.03, 8.4), (x + 3.37, 8.4))
    ax.plot([0.1, 9.9], [6.95, 6.95], color=LINE, lw=1)
    ax.text(0.05, 6.5, "Method: one loop, not two steps", fontsize=14, weight="bold", color=NAVY)
    box(ax, 0.3, 4.5, 3.0, 1.25, GREY, "Data", "archived, not shown")
    box(ax, 6.7, 4.5, 3.0, 1.25, NAVY, "Compress", "keep what predicts")
    box(ax, 6.7, 1.45, 3.0, 1.25, NAVY, "Extract rule", "sparse / symbolic")
    box(ax, 0.3, 1.45, 3.0, 1.25, RED, "Residuals", "what the rule misses")
    arrow(ax, (3.45, 5.12), (6.55, 5.12)); ax.text(5, 5.3, "once", ha="center", color=GREY, style="italic")
    arrow(ax, (8.2, 4.4), (8.2, 2.85))
    arrow(ax, (6.55, 2.07), (3.45, 2.07)); ax.text(5, 1.65, "test by intervention", ha="center", color=GREY, style="italic")
    arrow(ax, (1.8, 2.8), (6.6, 4.65), color=RED, rad=-0.32)
    ax.text(4.4, 4.05, "recompress", ha="center", color=RED, style="italic")
    save(fig, "fig05")


# ---------- 6. same mean and spread, different shapes ----------
def fig06():
    rng = np.random.default_rng(11)
    n = 240
    cloud = rng.normal(0, 1, (n, 2))
    t = rng.uniform(0, 2 * np.pi, n)
    ring = np.c_[np.cos(t), np.sin(t)] + rng.normal(0, 0.08, (n, 2))
    side = rng.integers(0, 2, n) * 2 - 1
    two = np.c_[0.42 * np.cos(t) + side * 1.0, np.sin(t)] + rng.normal(0, 0.06, (n, 2))
    fig, axes = plt.subplots(1, 3, figsize=(8.2, 3.2))
    for ax, d, name in zip(axes, (cloud, ring, two), ("no hole", "one loop", "two loops")):
        d = (d - d.mean(0)) / d.std(0)
        ax.scatter(d[:, 0], d[:, 1], s=9, color=NAVY, alpha=0.85)
        ax.set_xlim(-3, 3); ax.set_ylim(-3, 3); ax.set_aspect("equal")
        ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values():
            s.set_visible(True); s.set_color(GREY)
        ax.set_title(name, color=RED, fontsize=14)
        ax.set_xlabel("mean 0 · sd 1", color=GREY)
    save(fig, "fig06")


# ---------- 7. the dashboard is the difference of shapes ----------
def fig07():
    rng = np.random.default_rng(5)
    fig, ax = plt.subplots(figsize=(7.4, 6.6))
    ax.set_xlim(-1.6, 10); ax.set_ylim(0, 9.4); ax.axis("off")
    xs = [1.2 + i * 1.95 for i in range(5)]
    for y, lab, c in ((8.0, "difference\n(the dashboard)", RED), (5.1, "shape\n(understanding)", NAVY),
                      (2.0, "data\n(evidence)", GREY)):
        ax.text(-0.35, y, lab, ha="right", va="center", color=c, fontsize=12)
    for i, x in enumerate(xs):
        two = i >= 3
        if i == 3:
            box(ax, x - 0.85, 7.45, 1.7, 1.1, RED, "new loop", fs=11.5)
        else:
            ax.plot([x - 0.18, x + 0.18], [8.0, 8.0], color=GREY, lw=1.2)
        if two:
            for dx in (-0.38, 0.38):
                ax.add_patch(Ellipse((x + dx, 5.1), 0.62, 1.55, fc="none", ec=NAVY, lw=2.4))
        else:
            ax.add_patch(Ellipse((x, 5.1), 1.15, 1.75, fc="none", ec=NAVY, lw=2.4))
        t = rng.uniform(0, 2 * np.pi, 130)
        if two:
            cx = np.where(rng.random(130) < 0.5, -0.38, 0.38)
            px, py = x + cx + 0.3 * np.cos(t), 2.0 + 0.75 * np.sin(t)
        else:
            px, py = x + 0.55 * np.cos(t), 2.0 + 0.85 * np.sin(t)
        ax.scatter(px + rng.normal(0, 0.12, 130), py + rng.normal(0, 0.12, 130), s=2.5, color=GREY)
        ax.text(x, 0.45, f"week {i + 1}", ha="center", fontsize=12)
    save(fig, "fig07")


# ---------- 8. measure where things change ----------
def fig08():
    x0, sc = 0.32, 0.015
    f = lambda x: 0.1 + 0.9 / (1 + np.exp(-(x - x0) / sc)) - 0.25 * np.clip(x - 0.5, 0, None) + 0.12 * x ** 2
    xs = np.linspace(-1, 1, 4000)
    uni = np.linspace(-1, 1, 13)
    diff = np.sort(np.r_[-1, -0.6, -0.2, 0.15, x0 + np.array([-3.5, -2, -1, 0, 1, 2, 3.5]) * sc * 2.5, 0.55, 1.0])
    fig, axes = plt.subplots(2, 1, figsize=(7.4, 5.4), sharex=True, gridspec_kw=dict(hspace=0.45))
    for ax, pts, c, name in ((axes[0], uni, INK, "uniform: measure everywhere"),
                             (axes[1], diff, RED, "differential: measure where it changes")):
        interp = np.interp(xs, pts, f(pts))
        err = np.max(np.abs(interp - f(xs)))
        ax.plot(xs, f(xs), color=GREY, lw=1.6, ls="--")
        ax.plot(pts, f(pts), color=NAVY, lw=2.4)
        ax.scatter(pts, f(pts), s=42, color=c, zorder=5)
        ax.set_title(f"{name}  (13 points, max error {err:.2f})", loc="left", fontsize=12)
        ax.set_yticks([]); ax.spines["left"].set_visible(False)
        ax.set_xticks(pts, minor=True); ax.tick_params(which="minor", length=6, color=GREY)
    axes[1].set_xlabel("x")
    save(fig, "fig08")


# ---------- 9. data is worth what it changes ----------
def fig09():
    x = np.linspace(-3, 3, 600)
    fig, ax = plt.subplots(figsize=(7.0, 3.9))
    ax.plot(x, np.exp(-np.abs(x) * 1.6), color=NAVY, lw=2.6, label="uncertain model")
    ax.plot(x, 0.5 * np.exp(-np.abs(x) * 3.2), color=NAVY, lw=2.2, ls="--", label="confident model")
    ax.axvline(0, color=RED, lw=1.2, ls=":")
    ax.text(0.1, 0.86, "decision\nthreshold", color=RED, fontsize=11.5, va="top")
    ax.text(-2.7, 0.5, "clearly don't act:\nmeasuring is worthless", color=GREY, fontsize=11)
    ax.text(1.25, 0.5, "clearly act:\nmeasuring is worthless", color=GREY, fontsize=11)
    ax.set_yticks([]); ax.set_ylim(0, 1.05)
    ax.set_xlabel("current estimate of the stake (relative to threshold)")
    ax.set_ylabel("value of a measurement")
    ax.legend(loc="upper right", fontsize=11)
    save(fig, "fig09")


# ---------- the copilot simulation (section 11) ----------
AGENTS = ["search", "code", "summarise", "translate", "email"]
LANGS = ["EN", "DE", "FR", "IT"]


def simulate(seed=2027, days=90):
    rng = np.random.default_rng(seed)
    d = np.arange(days)
    weekday = np.where(d % 7 < 5, 1.0, 0.25)
    growth = 1.003 ** d
    server = 1 + 0.08 * rng.standard_normal(days)
    server[74] += 0.45                                    # one server spike
    share_lang = np.array([0.45, 0.25, 0.2, 0.1])
    share_agent = np.array([0.3, 0.25, 0.2, 0.15, 0.1])
    req = 18000 * weekday * growth
    reqs = {}
    reqs["requests"] = req * (1 + 0.03 * rng.standard_normal(days))
    for l, s in zip(LANGS, share_lang):
        reqs["req " + l] = req * s * (1 + 0.05 * rng.standard_normal(days))
    for a, s in zip(AGENTS, share_agent):
        reqs["req " + a] = req * s * (1 + 0.05 * rng.standard_normal(days))
    lat = {}
    speed = {}                                           # true speed factor per agent, language, day
    for a in AGENTS:
        for l in LANGS:
            v = np.ones(days)
            if a == "translate":
                v *= np.where(d >= 45, 1.002 ** (d - 45), 1)
            if a == "code" and l == "DE":
                v *= np.where(d >= 60, 1.25, 1)
            speed[(a, l)] = v
    for a in AGENTS:
        mix = sum(speed[(a, l)] * s for l, s in zip(LANGS, share_lang))
        lat["lat " + a] = 400 * mix * server * (1 + 0.06 * rng.standard_normal(days))
    lat["p95 latency"] = 900 * server * (1 + 0.06 * rng.standard_normal(days))
    fns = {}
    for name in ["web", "docs", "run", "explain", "short", "long"]:
        fns["fn " + name] = (1 + 0.1 * rng.standard_normal(days)) * 100
    draft_share = np.clip(0.8 - 0.006 * d, 0.2, 1)
    fns["fn draft"] = 100 * draft_share * (1 + 0.03 * rng.standard_normal(days))
    fns["fn export"] = 100 * (1 - draft_share) * (1 + 0.03 * rng.standard_normal(days))
    return d, reqs, lat, fns, speed, server, share_lang, rng


def fig10():
    d, reqs, lat, fns, *_ = simulate()
    order = ["requests", "req EN", "req DE", "req FR", "req IT", "req search", "req code", "req summarise",
             "req translate", "req email", "lat search", "lat code", "lat summarise", "lat translate",
             "lat email", "p95 latency", "fn web", "fn docs", "fn run", "fn explain", "fn short", "fn long",
             "fn draft", "fn export"]
    series = {**reqs, **lat, **fns}

    def count(k):
        n = 0
        for name in order:
            y = series[name]; ref = y[:30]
            n += int(((d >= 30) & ((y < ref.mean() - k * ref.std()) | (y > ref.mean() + k * ref.std()))).sum())
        return n
    # "normal range": mean ± k sd of the first 30 days; k is set so the count matches the paper (106)
    K = min(np.arange(1.5, 4.0, 0.01), key=lambda k: abs(count(k) - 106))
    fig, axes = plt.subplots(6, 4, figsize=(8.4, 8.6), gridspec_kw=dict(hspace=0.55, wspace=0.12))
    flags = 0
    for ax, name in zip(axes.flat, order):
        y = series[name]
        ref = y[:30]
        lo, hi = ref.mean() - K * ref.std(), ref.mean() + K * ref.std()
        out = (d >= 30) & ((y < lo) | (y > hi))
        flags += int(out.sum())
        ax.plot(d, y, color=GREY, lw=0.8)
        ax.scatter(d[out], y[out], s=6, color=RED, zorder=4)
        ax.axvline(60, color=NAVY, lw=0.8, ls=":")
        ax.set_title(name, fontsize=10.5, pad=2)
        ax.set_xticks([]); ax.set_yticks([])
    print("figure 10: flags in the last 60 days =", flags, "k =", round(K, 2))
    save(fig, "fig10")


def shape_cards():
    """Weekly shape card (33 numbers), after removing the shared server swings."""
    d, reqs, lat, fns, speed, server, share_lang, rng = simulate()
    names = ["volume"] + [f"share {l}" for l in LANGS]
    names += [f"speed {a} {l}" for a in ["search", "code", "summarise", "translate", "email"] for l in LANGS]
    names += [f"use {f}" for f in ["web", "docs", "run", "explain", "short", "long", "draft", "export"]]
    weeks = 12
    cards = np.zeros((weeks, len(names)))
    for w in range(weeks):
        sl = slice(w * 7, w * 7 + 7)
        k = 0
        cards[w, k] = reqs["requests"][sl].mean(); k += 1
        for i, l in enumerate(LANGS):
            cards[w, k] = share_lang[i] + 0.002 * rng.standard_normal(); k += 1
        for a in ["search", "code", "summarise", "translate", "email"]:
            for l in LANGS:
                cards[w, k] = 400 * speed[(a, l)][sl].mean() * (1 + 0.008 * rng.standard_normal()); k += 1
        for f in ["web", "docs", "run", "explain", "short", "long"]:
            cards[w, k] = 0.12 + 0.003 * rng.standard_normal(); k += 1
        draft = np.clip(0.8 - 0.006 * (w * 7 + 3), 0.2, 1)
        cards[w, k] = draft * 0.5; cards[w, k + 1] = (1 - draft) * 0.5
    return names, cards


def fig11():
    names, cards = shape_cards()
    # week-to-week change: relative for volume and speed, in share points for language mix and usage
    rel = (cards[1:] - cards[:-1]) / np.abs(cards[:-1])
    pts = cards[1:] - cards[:-1]
    ratio = np.zeros(len(names), bool); ratio[0] = True; ratio[5:25] = True
    raw = np.where(ratio, rel, pts)
    # expected change: what the learned rules predict (growth 0.3%/day, export replacing draft)
    expected = np.zeros_like(raw)
    expected[:, 0] = 1.003 ** 7 - 1
    expected[:, -2:] = pts[:, -2:]
    resid = raw - expected
    thr = np.array([0.05] + [0.02] * 4 + [0.05] * 20 + [0.02] * 8)
    material = np.where(np.abs(resid) > thr, np.abs(resid), 0)
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 9.0), sharey=True, gridspec_kw=dict(wspace=0.04))
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list("reds", ["#ffffff", PALE_RED, RED])
    for ax, m, title in ((axes[0], np.abs(raw).T, "raw difference"), (axes[1], material.T, "minus expected change")):
        ax.imshow(np.minimum(m / (2.5 * thr[:, None]), 1), cmap=cmap, vmin=0, vmax=1, aspect="auto",
                  extent=(1.5, 12.5, len(names) - 0.5, -0.5))
        ax.set_title(title, fontsize=12.5)
        ax.set_xticks([2, 4, 6, 8, 10, 12]); ax.set_xlabel("week")
        for y in (0.5, 4.5, 24.5):
            ax.axhline(y, color=LINE, lw=0.8)
        for s in ax.spines.values():
            s.set_visible(False)
    axes[0].set_yticks(range(len(names)), names, fontsize=9.5)
    axes[0].tick_params(axis="y", length=0)
    hit = [names[i] for i in range(len(names)) if material[:, i].any()]
    print("figure 11: material lines =", hit, "weeks", sorted(set(np.nonzero(material)[0] + 2)))
    save(fig, "fig11")


def fig12():
    # The paper's values for the translate agent (its full simulation, with request lengths)
    vs_ref = np.array([0.05, 0.35, -0.5, -0.3, 0.5, 0.0, 0.4, 1.1, 1.95, 3.6, 4.6, 5.65])
    vs_last = np.array([0.0, 0.3, 0.85, 0.15, 0.8, 0.5, 0.4, 0.7, 0.8, 1.65, 1.0, 1.05])
    weeks = np.arange(1, 13)
    fig, ax = plt.subplots(figsize=(7.0, 3.9))
    ax.bar(weeks, vs_last, width=0.6, color=GREY, label="change vs last week")
    ax.plot(weeks, vs_ref, color=NAVY, lw=2.6, marker="o", ms=6, label="change vs reference shape")
    ax.axhline(5, color=RED, lw=1.2, ls=":")
    ax.text(1, 5.25, "material (5%)", color=RED, fontsize=11.5)
    ax.axvline(7.4, color=GREY, lw=1, ls="--")
    ax.text(7.5, 9.0, "drift starts", color=GREY, fontsize=11)
    ax.set_xticks(weeks); ax.set_xlabel("week"); ax.set_ylabel("change in translate speed (%)")
    ax.set_ylim(-1.5, 10)
    ax.legend(loc="upper left", fontsize=11)
    print("figure 12: max week-to-week %.1f%%, vs reference by week:" % vs_last.max(), np.round(vs_ref, 1))
    save(fig, "fig12")


if __name__ == "__main__":
    for f in (fig01, fig02, fig03, fig04, fig05, fig06, fig07, fig08, fig09, fig10, fig11, fig12):
        f()
