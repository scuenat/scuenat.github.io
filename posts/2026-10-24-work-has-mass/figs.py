"""Figures for "Work Has Mass". Same style as "Intent Is the Source"."""
import re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle

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
    "savefig.dpi": 220, "savefig.bbox": "tight", "savefig.pad_inches": 0.18,
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




# ---------- the toy model, shared by figures 2 and 3 ----------
H = 100.0        # hours of human attention per sprint, for the whole team
K = 0.1          # hours per sprint to carry one item that stays in the system
A = 3.0          # hours to absorb one new item: review, decide, integrate
P_HAND, P_AI = 6.0, 1.5   # hours of human time to produce one item, by hand and with AI
M0 = 250.0       # items already in the system at sprint 0
SPRINTS = 26     # one year of two-week sprints


def simulate(p, budget=None, delete_cost=0.5):
    """Mass M(t) and new items delivered per sprint.
    Each sprint the team spends K*M carrying what exists; the rest goes to new items,
    each costing p (produce) + A (absorb). With a mass budget, the team also removes
    items so that carrying never takes more than `budget` of its attention."""
    M, mass, out = M0, [M0], []
    for _ in range(SPRINTS):
        free = H - K * M
        removed, del_hours = 0.0, 0.0
        if budget is not None:
            n_try = free / (p + A)
            excess = max(0.0, M + n_try - budget * H / K)
            removed, del_hours = excess, excess * delete_cost
        n = max(0.0, (free - del_hours) / (p + A))
        M = M + n - removed
        mass.append(M); out.append(n)
    return np.array(mass), np.array(out)


def fig_spacetime():
    """Items as masses that curve the grid in which work moves."""
    fig, axes = plt.subplots(1, 2, figsize=(11.6, 5.0))
    rng = np.random.default_rng(7)
    few = [(0.0, 0.0, 1.0), (-1.7, 1.2, 0.35), (1.6, -1.1, 0.4), (1.5, 1.5, 0.25)]
    many = few + [(x, y, m) for x, y, m in zip(rng.uniform(-2.4, 2.4, 34), rng.uniform(-2.4, 2.4, 34),
                                                rng.uniform(0.08, 0.3, 34))]
    many[0] = (0.0, 0.0, 1.6)
    titles = [("CALIBRATED FOR", "A few items, a gentle curve"),
              ("WITH AI", "Many more items, a deep well")]
    for ax, masses, (eb, tt), pull in zip(axes, (few, many), titles, (0.32, 0.22)):
        ax.set_xlim(-3, 3); ax.set_ylim(-3, 3); ax.set_aspect("equal"); ax.axis("off")
        t = np.linspace(-3, 3, 400)

        def warp(X, Y):
            dX, dY = np.zeros_like(X), np.zeros_like(Y)
            for mx, my, m in masses:
                rx, ry = X - mx, Y - my
                r2 = rx ** 2 + ry ** 2 + 0.25
                dX -= pull * m * rx / r2; dY -= pull * m * ry / r2
            # never pull a point past the centre of its well, so the grid folds in but does not cross
            return X + np.clip(dX, -0.9, 0.9), Y + np.clip(dY, -0.9, 0.9)
        for g in np.linspace(-3, 3, 19):
            for X, Y in ((t, np.full_like(t, g)), (np.full_like(t, g), t)):
                wx, wy = warp(X, Y)
                ax.plot(wx, wy, color="#b9c3cc", lw=0.7, zorder=1)
        for mx, my, m in masses:
            heavy = m > 0.9
            ax.add_patch(Circle((mx, my), 0.07 + 0.15 * np.sqrt(m), fc=NAVY if heavy else "white",
                                ec=NAVY, lw=1.1, zorder=3))
        # a new request crossing the system: dots one sprint apart
        if masses is few:
            path = np.array([(-2.8 + 5.4 * s, -2.2 + 0.9 * s + 0.35 * np.sin(np.pi * s)) for s in np.linspace(0, 1, 9)])
        else:
            s = np.linspace(0, 1, 9) ** 1.9 * 0.62
            path = np.array([(-2.8 + 5.4 * u, -2.2 + 0.9 * u + 1.6 * np.sin(np.pi * u)) for u in s])
        ax.plot(path[:, 0], path[:, 1], color=WARM, lw=1.6, ls=(0, (4, 3)), zorder=4)
        ax.scatter(path[:, 0], path[:, 1], s=26, color=AMBER, edgecolor=WARM, lw=1, zorder=5)
        ax.text(-2.9, 3.25, eb, fontsize=7, weight="semibold", color=NAVY if masses is few else WARM)
        ax.text(-2.9, 3.05, tt, fontsize=11.5, weight="semibold", color=INK, va="top")
    axes[0].text(2.85, -2.75, "a new request:\none dot per sprint", fontsize=8, color=WARM, ha="right")
    axes[1].text(0.6, -2.85, "same nine sprints, a shorter and bent path", fontsize=8, color=WARM, ha="center")
    fig.savefig(OUT + "fig01.png"); plt.close(fig)


def fig_mass():
    """The toy model over one year: mass, and what is left for new work."""
    runs = [("By hand", simulate(P_HAND), MUTED, "-"),
            ("With AI", simulate(P_AI), NAVY, "-"),
            ("With AI and a mass budget", simulate(P_AI, budget=0.35), WARM, (0, (5, 2)))]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.6, 4.3))
    x = np.arange(SPRINTS + 1)
    horizon = H / K
    for lab, (m, n), col, ls in runs:
        a1.plot(x, m, color=col, lw=2.2, ls=ls)
        a2.plot(x[1:], n, color=col, lw=2.2, ls=ls)
        print(f"{lab:28s} mass {m[-1]:5.0f}  delivered s1 {n[0]:4.1f}  s26 {n[-1]:4.1f}  "
              f"total {n.sum():5.0f}  carrying share {K * m[-1] / H:.0%}")
    a1.axhline(horizon, color=RED, lw=1, ls=(0, (2, 2)))
    a1.text(0.3, horizon - 20, "horizon: all attention goes to carrying", fontsize=8, color=RED, va="top")
    a1.set_ylim(0, 1080); a1.set_xlim(0, SPRINTS + 7)
    a1.set_ylabel("Items in the system (mass)"); a1.set_xlabel("Sprint")
    a2.set_ylim(0, 20); a2.set_xlim(1, SPRINTS + 9)
    a2.set_ylabel("New items delivered per sprint"); a2.set_xlabel("Sprint")
    for lab, (m, n), col, ls in runs:
        a1.text(SPRINTS + 0.4, m[-1], lab.replace(" and a", "\nand a"), fontsize=8.4, color=col, weight="semibold", va="center")
        a2.text(SPRINTS + 0.4, n[-1], lab.replace(" and a", "\nand a"), fontsize=8.4, color=col,
                weight="semibold", va="center")
    for ax, (eb, tt) in zip((a1, a2), (("MASS", "What the team must carry"), ("FLOW", "What is left for new work"))):
        tidy(ax)
        ax.text(0, 1.1, eb, transform=ax.transAxes, fontsize=7, weight="semibold", color=NAVY)
        ax.text(0, 1.04, tt, transform=ax.transAxes, fontsize=11.5, weight="semibold", color=INK)
    fig.subplots_adjust(wspace=0.32)
    fig.savefig(OUT + "fig02.png"); plt.close(fig)


def fig_dilation():
    """Lead time of a new request as the mass takes more of the team's attention."""
    u = 0.35   # share of attention that new requests need, fixed
    s = np.linspace(0, 0.8, 600)
    w = 1 / ((1 - s) - u)              # M/M/1-like: wait grows as 1 / (spare capacity)
    w0 = 1 / ((1 - 0.25) - u)
    fig, ax = plt.subplots(figsize=(8.6, 4.4))
    ok = (1 - s) - u > 0.034
    ax.plot(s[ok], (w / w0)[ok], color=NAVY, lw=2.4)
    ax.axvline(1 - u, color=RED, lw=1, ls=(0, (2, 2)))
    ax.text(1 - u + 0.008, 5.6, "horizon:\nrequests go in,\nnothing comes out", fontsize=8, color=RED, ha="left", va="top")
    pts = [(0.25, "today: a quarter of\nattention carries the past", MUTED, (-12, 10), "right"),
           (simulate(P_HAND)[0][-1] * K / H, "by hand, after a year", MUTED, (-12, 10), "right"),
           (simulate(P_AI)[0][-1] * K / H, "with AI, after a year", NAVY, (-12, -4), "right"),
           (0.35, "with a mass budget", WARM, (10, -18), "left")]
    for sx, lab, col, off, ha in pts:
        y = (1 / ((1 - sx) - u)) / w0
        if (1 - sx) - u <= 0.03:
            ax.annotate(lab + ": past the horizon", (1 - u, 5.75), xytext=(-150, -60), textcoords="offset points",
                        fontsize=8.2, color=col, weight="semibold",
                        arrowprops=dict(arrowstyle="-|>", color=col, lw=1.2))
            print(f"dilation {lab!r}: share {sx:.2f} -> past horizon")
            continue
        ax.scatter([sx], [y], s=60, color="white", edgecolor=col, lw=2, zorder=5)
        ax.annotate(lab, (sx, y), xytext=off, textcoords="offset points", fontsize=8.2,
                    color=col, ha=ha, weight="semibold")
        print(f"dilation {lab!r}: share {sx:.2f} -> {y:.2f}x")
    ax.set_xlim(0, 0.8); ax.set_ylim(0, 6)
    ticks = [0, 0.2, 0.4, 0.6, 0.8]
    ax.set_xticks(ticks); ax.set_xticklabels([f"{v:.0%}" for v in ticks])
    ax.set_yticks([0, 1, 2, 3, 4, 5, 6]); ax.set_yticklabels(["0", "1×", "2×", "3×", "4×", "5×", "6×"])
    ax.set_xlabel("Share of the team's attention spent carrying existing mass")
    ax.set_ylabel("Lead time of a new request,\ncompared with today")
    tidy(ax)
    fig.savefig(OUT + "fig03.png"); plt.close(fig)


def fig_wsjf():
    """WSJF ranks before AI, with AI, and with AI plus the cost of carrying."""
    # name, cost of delay, job size by hand, job size with AI, carrying cost (mass it adds)
    feats = [("New partner API", 21, 13, 3, 13),
             ("Checkout redesign", 18, 8, 2, 3),
             ("Export to PDF", 9, 3, 1, 1),
             ("Fraud rules v2", 20, 20, 5, 8),
             ("Admin dashboard", 8, 5, 1, 5),
             ("Second mobile app", 16, 20, 3, 21),
             ("Faster search", 13, 8, 2, 2),
             ("Chat assistant", 15, 13, 2, 13)]
    cols = [("Classic WSJF", "by hand", lambda f: f[1] / f[2]),
            ("Classic WSJF", "with AI", lambda f: f[1] / max(f[3], 1)),
            ("WSJF with carrying cost", "with AI", lambda f: f[1] / (max(f[3], 1) + f[4]))]
    ranks, scores = [], []
    for _, _, fn in cols:
        sc = [fn(f) for f in feats]
        order = sorted(range(len(feats)), key=lambda i: -sc[i])
        r = [0] * len(feats)
        for pos, i in enumerate(order):
            r[i] = pos + 1
        ranks.append(r); scores.append(sc)
    fig, ax = plt.subplots(figsize=(11.4, 5.0))
    xs = [0, 1, 2]
    for i, f in enumerate(feats):
        y = [-ranks[c][i] for c in range(3)]
        moved = abs(ranks[2][i] - ranks[1][i]) >= 3
        col = WARM if moved else "#9aa6b1"
        ax.plot(xs, y, color=col, lw=2.2 if moved else 1.3, zorder=2)
        for c in range(3):
            ax.scatter([xs[c]], [y[c]], s=60, color="white", edgecolor=col, lw=2, zorder=3)
            ax.text(xs[c], y[c] + 0.3, f"{scores[c][i]:.1f}", fontsize=7.4, color=MUTED, ha="center",
                    zorder=4, bbox=dict(boxstyle="round,pad=0.12", fc=BG, ec="none"))
        ax.text(-0.08, y[0], f[0], ha="right", va="center", fontsize=8.8, color=INK)
        ax.text(2.08, y[2], f[0], ha="left", va="center", fontsize=8.8, color=col if moved else INK,
                weight="semibold" if moved else "normal")
    for c, (t, sub, _) in enumerate(cols):
        ax.text(xs[c], 0.35, t, ha="center", fontsize=9.6, weight="semibold", color=INK)
        ax.text(xs[c], 0.05, sub, ha="center", fontsize=8.4, color=MUTED)
        sc = scores[c]
        ax.text(xs[c], -9.0, f"spread {max(sc) / min(sc):.1f}×", ha="center", fontsize=8.2, color=MUTED)
    ax.set_xlim(-0.95, 2.95); ax.set_ylim(-9.3, 0.8); ax.axis("off")
    fig.savefig(OUT + "fig04.png"); plt.close(fig)


def fig_art():
    """Draw the train by mass, not by headcount. Schematic."""
    fig, ax = plt.subplots(figsize=(8.6, 4.4))
    people = np.linspace(0, 140, 200)
    cap = 100   # what one train can coordinate, in arbitrary units of mass
    for k, lab, col in ((0.8, "mass per person, by hand", MUTED), (2.6, "mass per person, with AI", NAVY)):
        ax.plot(people, k * people, color=col, lw=2.4)
        if k < 1:
            ax.text(people[-1] + 2, k * people[-1], lab, color=col, fontsize=8.6, weight="semibold", va="center")
        else:
            ax.text(128 / k - 3, 128, lab, color=col, fontsize=8.6, weight="semibold", va="center", ha="right")
    ax.axhspan(cap, 140, color=SAND_T, zorder=0)
    ax.axhline(cap, color=INK, lw=1.2)
    ax.text(52, cap + 4, "what one train can coordinate", fontsize=8.6, color=INK)
    ax.axvspan(50, 125, ymax=0.06, color=NAVY_T, zorder=1)
    ax.text(87.5, 3, "SAFe: 50 to 125 people", ha="center", fontsize=8, color=NAVY, va="bottom")
    for k, col in ((0.8, MUTED), (2.6, NAVY)):
        ax.scatter([cap / k], [cap], s=70, color="white", edgecolor=col, lw=2, zorder=5)
        ax.annotate(f"~{cap / k:.0f} people", (cap / k, cap), xytext=(8, -16), textcoords="offset points",
                    fontsize=9, color=col, weight="bold")
    ax.set_xlim(0, 175); ax.set_ylim(0, 140)
    ax.set_xlabel("People on the train"); ax.set_ylabel("Mass the train must carry")
    ax.set_yticks([])
    tidy(ax)
    fig.savefig(OUT + "fig05.png"); plt.close(fig)


def fig_ledger():
    """A mass ledger for one sprint, as a waterfall."""
    rows = [("Start of sprint", 312, "total"),
            ("Stories done", +14, "add"), ("Generated code\nand tests", +22, "add"),
            ("New docs\nand specs", +6, "add"), ("Open decisions", +9, "add"),
            ("Code deleted", -18, "rem"), ("Features retired", -11, "rem"),
            ("Backlog items\nexpired", -15, "rem"), ("End of sprint", None, "total")]
    fig, ax = plt.subplots(figsize=(11.4, 4.4))
    run = 0
    for i, (lab, v, kind) in enumerate(rows):
        if kind == "total":
            v = run if v is None else v
            ax.bar(i, v - 250, bottom=250, width=0.62, color=NAVY, zorder=3)
            ax.text(i, v + 2, f"{v:.0f}", ha="center", va="bottom", fontsize=9, weight="semibold", color=INK)
            run = v
        else:
            col = WARM if kind == "add" else GREEN
            lo = run if v > 0 else run + v
            ax.bar(i, abs(v), bottom=lo, width=0.62, color=col, zorder=3)
            ax.text(i, lo + abs(v) + 2, f"{v:+d}", ha="center", va="bottom", fontsize=9, color=INK)
            if i + 1 < len(rows):
                ax.plot([i + 0.31, i + 0.69], [run + v] * 2, color=MUTED, lw=0.8, zorder=2)
            run += v
    ax.set_xticks(range(len(rows))); ax.set_xticklabels([r[0] for r in rows], fontsize=8.2)
    ax.set_ylim(250, 380); ax.set_ylabel("Mass (hours per sprint to carry)")
    ax.text(2.5, 374, "added", color=WARM, fontsize=9, weight="semibold", ha="center")
    ax.text(6, 374, "removed", color=GREEN, fontsize=9, weight="semibold", ha="center")
    tidy(ax)
    fig.savefig(OUT + "fig06.png"); plt.close(fig)


if __name__ == "__main__":
    import os
    os.makedirs(OUT, exist_ok=True)
    fig_spacetime(); fig_mass(); fig_dilation(); fig_wsjf(); fig_art(); fig_ledger()
