"""Figures for "A Rollout That Cannot Shrink", a deep dive into LeHami (Yalovetzky, Balestriero and LeCun, 2026).

Figures 1 to 4 are my own toys on a true pendulum, not the paper's learned model. Figure 5 redraws numbers
reported in the paper's Tables 2 and 7. Run from this folder: python figs.py
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

NAVY, GREY, RED, LIGHT, PALE, AMBER = "#1f4e79", "#7f8c8d", "#c0392b", "#d5dde5", "#eef1f4", "#d68910"
INK = "#2c3e50"
plt.rcParams.update({
    "font.family": "DejaVu Serif", "font.size": 10, "axes.spines.top": False,
    "axes.spines.right": False, "axes.linewidth": 1.0, "savefig.dpi": 200,
    "savefig.bbox": "tight", "legend.frameon": False, "legend.fontsize": 8.5,
})
OUT = "figures/"
H = 0.1  # the paper's frame interval, 0.1 s (Appendix D.3)


def grad_V(q):
    """Pendulum with g/L = 1: H = p^2/2 - cos q."""
    return np.sin(q)


def leapfrog(q, p, h=H, n=1):
    """Kick-drift-kick, the step of the paper's Eq. 4 with K = p^2/2 and S = I."""
    for _ in range(n):
        p = p - 0.5 * h * grad_V(q)
        q = q + h * p
        p = p - 0.5 * h * grad_V(q)
    return q, p


def contracting(q, p, h=H, rate=0.97):
    """A stand-in for an unconstrained predictor: a good step, then a small pull toward the batch mean."""
    q, p = leapfrog(q, p, h)
    return q.mean() + rate * (q - q.mean()), p.mean() + rate * (p - p.mean())


def shoelace(x, y):
    return 0.5 * abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))


def energy_contours(ax, lim=(-3.3, 3.3, -2.6, 2.6)):
    qq, pp = np.meshgrid(np.linspace(lim[0], lim[1], 300), np.linspace(lim[2], lim[3], 300))
    ax.contour(qq, pp, 0.5 * pp**2 - np.cos(qq), levels=np.linspace(-0.9, 2.4, 12), colors=LIGHT, linewidths=0.8)
    ax.set_xlim(lim[0], lim[1]); ax.set_ylim(lim[2], lim[3])
    ax.set_xlabel("position-like $q$"); ax.set_ylabel("momentum-like $p$")


# --------------------------------------------------------------------------------------------
def fig_cloud():
    """A blob of latent states rolled out by a contracting map and by a leapfrog step."""
    t = np.linspace(0, 2 * np.pi, 400, endpoint=False)
    q0, p0 = -1.3 + 0.35 * np.cos(t), 0.7 + 0.35 * np.sin(t)
    a0 = shoelace(q0, p0)
    steps = [0, 20, 40, 60]

    fig, axes = plt.subplots(1, 3, figsize=(12, 3.9), gridspec_kw={"width_ratios": [1, 1, 0.9], "wspace": 0.32})
    for ax, (name, step, col) in zip(axes[:2], [("unconstrained predictor\n(3% pull per step)", contracting, RED),
                                                 ("symplectic leapfrog step", leapfrog, NAVY)]):
        energy_contours(ax)
        q, p = q0.copy(), p0.copy()
        for k in range(steps[-1] + 1):
            if k in steps:
                alpha = 0.25 + 0.75 * k / steps[-1]
                ax.add_patch(Polygon(np.c_[q, p], closed=True, fc=col, ec=col, alpha=0.22 * alpha + 0.08, lw=1.0))
                ax.text(q.mean(), p.mean(), f"{k}", fontsize=8, ha="center", va="center", color=INK)
            q, p = step(q, p)
        ax.set_title(name, fontsize=10, color=INK)

    # log area along the rollout
    ax = axes[2]
    for name, step, col in [("unconstrained", contracting, RED), ("leapfrog", leapfrog, NAVY)]:
        q, p, la = q0.copy(), p0.copy(), []
        for k in range(76):
            la.append(np.log(shoelace(q, p) / a0))
            q, p = step(q, p)
        ax.plot(range(76), la, color=col, lw=2)
        ax.text(76, la[-1], f"  {name}", color=INK, va="center", fontsize=9)
    ax.axhline(0, color=GREY, lw=0.8, ls=":")
    ax.set_xlabel("rollout step $K$"); ax.set_ylabel("log of the blob's area")
    ax.set_title("volume along the rollout", fontsize=10, color=INK)
    ax.set_xlim(0, 100)
    fig.savefig(OUT + "fig01.png"); plt.close(fig)


# --------------------------------------------------------------------------------------------
def fig_shears():
    """The leapfrog step is three shears; each one keeps area exactly."""
    g = np.linspace(-1, 1, 9)
    sq = np.array([[-1, -1], [1, -1], [1, 1], [-1, 1]], float)
    h = 0.9
    kick = lambda z: np.c_[z[:, 0], z[:, 1] - 0.5 * h * 1.2 * np.sin(z[:, 0])]
    drift = lambda z: np.c_[z[:, 0] + h * z[:, 1], z[:, 1]]

    def dense(poly, n=60):
        return np.vstack([np.linspace(poly[i], poly[(i + 1) % len(poly)], n, endpoint=False) for i in range(len(poly))])

    shapes = [dense(sq)]
    for f in (kick, drift, kick):
        shapes.append(f(shapes[-1]))
    titles = ["a cell of states", "half kick\n$p \\leftarrow p - \\frac{h}{2}\\nabla V(q,u)$",
              "drift\n$q \\leftarrow q + h\\,\\nabla K(p)$", "half kick\n$p \\leftarrow p - \\frac{h}{2}\\nabla V(q,u)$"]
    fig, axes = plt.subplots(1, 4, figsize=(12, 3.4), sharex=True, sharey=True)
    a0 = shoelace(*shapes[0].T)
    for i, (ax, z, ttl) in enumerate(zip(axes, shapes, titles)):
        for v in g:
            ax.axvline(v * 2.4, color=PALE, lw=0.6, zorder=0); ax.axhline(v * 2.4, color=PALE, lw=0.6, zorder=0)
        ax.add_patch(Polygon(z, closed=True, fc=NAVY if i else GREY, alpha=0.25, ec=NAVY if i else GREY, lw=1.4))
        ax.set_title(ttl, fontsize=9.5, color=INK)
        ax.text(0, -2.75, f"area = {shoelace(*z.T) / a0:.4f}", ha="center", fontsize=9, color=INK)
        ax.set_xlim(-3, 3); ax.set_ylim(-3, 3); ax.set_aspect("equal")
        ax.set_xticks([]); ax.set_yticks([])
        if i == 0:
            ax.set_ylabel("$p$"); 
        ax.set_xlabel("$q$")
    fig.savefig(OUT + "fig02.png"); plt.close(fig)


# --------------------------------------------------------------------------------------------
def fig_sign():
    """A tied symmetric window cannot see the direction of motion; the antisymmetric stencil can."""
    th, w, dt = 0.6, 2.0, H
    sg = np.array([-2, -1, 0, 1, 2]) / 10          # centred Savitzky-Golay derivative (Appendix C.4)
    offs = np.arange(-2, 3)
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.6), gridspec_kw={"wspace": 0.3})

    ax = axes[0]
    for sign, col, lab in [(+1, NAVY, "swinging forward, $+\\omega$"), (-1, AMBER, "same angle, swinging back, $-\\omega$")]:
        x = th + sign * w * offs * dt
        ax.plot(offs, x, "o-", color=col, lw=2, ms=8)
        ax.text(2.15, x[-1], lab, color=INK, va="center", fontsize=9)
    ax.set_xlim(-2.4, 6.2); ax.set_xticks(offs, ["$t-2$", "$t-1$", "$t$", "$t+1$", "$t+2$"])
    ax.set_ylabel("angle $\\theta$ [rad]"); ax.set_title("two moments that share a middle frame", fontsize=10, color=INK)

    ax = axes[1]
    ws = np.linspace(-4, 4, 161)
    a, b = 1.0, 1.0
    tied = (b + 2 * a * np.cos(ws * dt)) / (b + 2 * a)    # Eq. 16, the factor on (sin, cos)
    stencil = np.array([np.dot(sg, th + v * offs * dt) / dt for v in ws])
    ax.plot(ws, tied, color=RED, lw=2); ax.text(-3.8, 0.84, "tied window $(a,b,a)$: same output for $\\pm\\omega$", color=INK, fontsize=9)
    ax.plot(ws, stencil / 4, color=NAVY, lw=2); ax.text(0.5, -0.55, "Savitzky–Golay stencil ($\\div 4$):\nsign follows $\\omega$", color=INK, fontsize=9)
    ax.axhline(0, color=GREY, lw=0.8, ls=":"); ax.axvline(0, color=GREY, lw=0.8, ls=":")
    ax.set_xlim(-4, 4); ax.set_xlabel("true angular velocity $\\omega$ [rad/s]"); ax.set_ylabel("what the encoder outputs")
    ax.set_title("even in $\\omega$ versus odd in $\\omega$", fontsize=10, color=INK)
    fig.savefig(OUT + "fig03.png"); plt.close(fig)


# --------------------------------------------------------------------------------------------
def fig_clock():
    """One vector field, many step sizes, and both directions of time."""
    from scipy.integrate import solve_ivp
    q0, p0, T = 2.4, 0.0, 4.0
    ts = np.linspace(0, T, 401)
    ref = solve_ivp(lambda t, z: [z[1], -np.sin(z[0])], (0, T), [q0, p0], t_eval=ts, rtol=1e-11, atol=1e-11).y[0]
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.6), gridspec_kw={"wspace": 0.3})
    ax = axes[0]
    for h, col, lab in [(4 * H, RED, "$h = 4\\Delta t$"), (H, NAVY, "$h = \\Delta t$ (the frame rate)"),
                        (H / 4, AMBER, "$h = \\Delta t/4$")]:
        n = int(round(T / h)); q, p, qs = q0, p0, [q0]
        for _ in range(n):
            q, p = leapfrog(q, p, h); qs.append(q)
        tt = np.arange(n + 1) * h
        e = np.abs(np.array(qs) - np.interp(tt, ts, ref))
        ax.semilogy(tt[1:], e[1:], color=col, lw=1.8)
        ax.text(T, e[-1], f"  {lab}", color=INK, va="center", fontsize=9)
    ax.set_xlim(0, 6.2); ax.set_xlabel("time integrated [s]"); ax.set_ylabel("angle error vs exact [rad]")
    ax.set_title("one flow, three step sizes", fontsize=10, color=INK)

    ax = axes[1]
    Ks = np.arange(1, 61)
    err = []
    for K in Ks:
        q, p = leapfrog(q0, 0.3, H, K)
        q, p = leapfrog(q, p, -H, K)
        err.append(abs(q - q0) + abs(p - 0.3))
    ax.semilogy(Ks, np.maximum(err, 1e-17), "o", color=NAVY, ms=4)
    ax.set_xlabel("steps out, then the same number back"); ax.set_ylabel("round-trip error")
    ax.set_title("run forward, flip $h \\to -h$, run back", fontsize=10, color=INK)
    ax.set_ylim(1e-18, 1e-12)
    ax.text(30, 1e-13, "only floating-point rounding remains", ha="center", fontsize=9, color=INK)
    fig.savefig(OUT + "fig04.png"); plt.close(fig)


# --------------------------------------------------------------------------------------------
def fig_numbers():
    """Numbers reported in the paper, redrawn: Table 7 (velocity error) and Table 2 (planning success)."""
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 3.9), gridspec_kw={"wspace": 0.35, "width_ratios": [1, 1.3]})
    ax = axes[0]
    bands = ["1–10", "11–20", "21–70"]
    leh, lew = [0.364, 0.669, 1.534], [1.020, 1.169, 2.331]
    x = np.arange(3)
    ax.bar(x - 0.19, lew, 0.36, color=GREY, label="LeWM (baseline)")
    ax.bar(x + 0.19, leh, 0.36, color=NAVY, label="LeHami")
    for i in range(3):
        ax.text(x[i] + 0.19, leh[i] + 0.04, f"{lew[i] / leh[i]:.2f}×", ha="center", fontsize=8.5, color=INK)
    ax.set_xticks(x, [f"steps {b}" for b in bands]); ax.set_ylabel("velocity error, MAE $\\omega$ [rad/s]")
    ax.set_title("conservative pendulum, rollout (Table 7)", fontsize=10, color=INK); ax.legend(loc="upper left")

    ax = axes[1]
    clauses = ["position", "velocity", "position\n+ velocity"]
    models = [("LeWM $W$=1", [0.800, 0.184, 0.142], LIGHT), ("LeWM $W$=3 tied", [0.633, 0.473, 0.400], GREY),
              ("LeWM $W$=3 untied", [0.696, 0.800, 0.636], INK), ("LeHami", [0.480, 0.527, 0.304], NAVY)]
    w = 0.2
    for j, (name, vals, col) in enumerate(models):
        ax.bar(np.arange(3) + (j - 1.5) * w, vals, w * 0.92, color=col, label=name)
    ax.set_xticks(np.arange(3), clauses); ax.set_ylim(0, 1); ax.set_ylabel("goal-reaching success")
    ax.set_title("actuated pendulum, planning at ≤ 15 TFLOP (Table 2)", fontsize=10, color=INK)
    ax.legend(loc="upper right", ncol=2, fontsize=8)
    fig.savefig(OUT + "fig05.png"); plt.close(fig)


if __name__ == "__main__":
    fig_cloud(); fig_shears(); fig_sign(); fig_clock(); fig_numbers()
