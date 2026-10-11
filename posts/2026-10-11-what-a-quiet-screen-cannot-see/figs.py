"""Figures for "What a Quiet Screen Cannot See". Style matches the first essay."""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import sim

NAVY, GREY, RED, LIGHT = "#1f4e79", "#7f8c8d", "#c0392b", "#d5dde5"
plt.rcParams.update({
    "font.family": "DejaVu Serif", "font.size": 10, "axes.spines.top": False,
    "axes.spines.right": False, "axes.linewidth": 1.0, "savefig.dpi": 200,
    "savefig.bbox": "tight", "legend.frameon": False, "legend.fontsize": 8.5,
})
OUT = "figures/"
WEEKS = np.arange(1, 13)
PROBLEM_WEEK_X = 7 + (sim.PROBLEM_DAY - 49) / 7 + 0.5   # day 51 sits inside week 8


def fit(w, with_device=False):
    days = sorted(w.day.unique())
    cells = [(a, l) for a in sim.AGENTS for l in sim.LANGS]
    devs = ["desktop", "iOS"]
    k = len(days) - 1 + len(cells) + 1 + (2 if with_device else 0)
    X = np.zeros((len(w), k))
    di = {d: i for i, d in enumerate(days)}
    ci = {c: i for i, c in enumerate(cells)}
    for r, (d, a, l, L, dv) in enumerate(zip(w.day, w.agent, w.lang, w.length, w.device)):
        if di[d] > 0:
            X[r, di[d] - 1] = 1
        X[r, len(days) - 1 + ci[(a, l)]] = 1
        X[r, len(days) - 1 + len(cells)] = np.log(L / 100)
        if with_device and dv in devs:
            X[r, len(days) + len(cells) + devs.index(dv)] = 1
    sw = np.sqrt(w.n.values)
    b, *_ = np.linalg.lstsq(X * sw[:, None], w.mean_log.values * sw, rcond=None)
    resid = w.mean_log.values - X @ b
    speeds = b[len(days) - 1:len(days) - 1 + len(cells)]
    share = w.groupby(["agent", "lang"]).n.sum().reindex(cells).values
    speeds = speeds - np.average(speeds, weights=share)
    day_fx = np.r_[0.0, b[:len(days) - 1]]
    return speeds, resid, resid * sw / sim.SIGMA, day_fx


def compute():
    df = sim.simulate()
    df["week"] = df.day // 7 + 1
    cards, z_no, z_dev, parts = [], [], [], []
    for wk in WEEKS:
        w = df[df.week == wk].copy()
        s, r, z, _ = fit(w)
        cards.append(s)
        z_no.append(np.mean(z ** 2))
        z_dev.append(np.mean(fit(w, True)[2] ** 2))
        w["z"] = z
        parts.append(w)
    res = pd.concat(parts)
    cards = np.array(cards)
    d_last = np.r_[0, np.abs(np.expm1(np.diff(cards, axis=0))).max(axis=1) * 100]
    d_ref = np.abs(np.expm1(cards - cards[:6].mean(axis=0))).max(axis=1) * 100
    ref = np.mean(z_no[:6])
    size_no, size_dev = np.array(z_no) / ref, np.array(z_dev) / ref

    def explained(g, f):
        m = g.groupby(f).z.transform("mean")
        return (m ** 2).sum() / (g.z ** 2).sum()
    expl = {f: res.groupby("week").apply(lambda g: explained(g, f)).values
            for f in ["device", "region", "plan"]}
    # Shared daily level, as the shape sees it: everything common to all agents that day
    daily = df.groupby("day").apply(lambda g: np.average(
        g.mean_log - g.agent.map(sim.agent_base) - g.lang.map(sim.lang_base)
        - 0.5 * np.log(g.length / 100), weights=g.n)).values
    return dict(d_last=d_last, d_ref=d_ref, size_no=size_no, size_dev=size_dev,
                expl=expl, daily=daily, n=df.n.sum())


def fig_geometry():
    fig, ax = plt.subplots(figsize=(5.2, 3.0))
    ax.set_xlim(-0.3, 5.2); ax.set_ylim(-0.6, 3.4); ax.axis("off")
    ax.annotate("", xy=(5.0, 0), xytext=(-0.2, 0),
                arrowprops=dict(arrowstyle="-|>", color=GREY, lw=1.2))
    ax.text(5.0, -0.32, "what the shape describes", ha="right", color=GREY, fontsize=9)
    ax.annotate("", xy=(0, 3.2), xytext=(0, -0.2),
                arrowprops=dict(arrowstyle="-|>", color=GREY, lw=1.2))
    ax.text(0.12, 3.15, "what it does not describe", ha="left", va="top", color=GREY, fontsize=9)
    ax.axvspan(0, 1.2, ymin=0.13, ymax=0.165, color=RED, alpha=0.25, lw=0)
    ax.text(1.3, -0.33, "too small to report", ha="left", color=RED, fontsize=8)
    ax.annotate("", xy=(0.9, 2.7), xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=2.2))
    ax.text(1.0, 2.75, "the real change", color=NAVY, fontsize=9.5, va="center")
    ax.plot([0.9, 0.9], [0, 2.7], ls=":", color=GREY, lw=1)
    ax.plot([0, 0.9], [0, 0], color=NAVY, lw=4, solid_capstyle="butt")
    ax.text(0.45, -0.38, "seen", ha="center", color=NAVY, fontsize=9, weight="bold")
    ax.text(1.02, 1.35, "unseen", color=GREY, fontsize=9, weight="bold", va="center")
    ax.annotate("", xy=(3.9, 0.9), xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1.2, alpha=0.45))
    ax.text(3.95, 0.95, "a change the shape\nwas built for", color=NAVY, alpha=0.7, fontsize=8.5)
    fig.savefig(OUT + "fig01.png"); plt.close(fig)


def fig_silent(r):
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(5.4, 4.4), gridspec_kw=dict(hspace=0.75))
    d = np.arange(84)
    lvl = np.expm1(r["daily"] - r["daily"][:49].mean()) * 100
    a1.plot(d, lvl, color=GREY, lw=1, marker="o", ms=2.2)
    roll = pd.Series(lvl).rolling(7, center=True).mean()
    a1.plot(d, roll, color=NAVY, lw=2, label="7-day average")
    a1.axvline(sim.PROBLEM_DAY - 0.5, color=GREY, ls="--", lw=0.8)
    a1.text(sim.PROBLEM_DAY + 0.8, -11.5, "iOS problem starts", color=GREY, fontsize=8)
    a1.set_xlabel("day"); a1.set_ylabel("shared level (%)")
    a1.set_title("What the shape calls server swings", fontsize=9.5, loc="left")
    a1.legend(loc="lower left")
    w = 0.38
    a2.bar(WEEKS - w / 2, r["d_last"], w, color=GREY, label="vs last week")
    a2.bar(WEEKS + w / 2, r["d_ref"], w, color=NAVY, label="vs reference (weeks 1–6)")
    a2.axhline(5, color=RED, ls=":", lw=1.3)
    a2.text(0.6, 5.3, "material (5%)", color=RED, fontsize=8)
    a2.axvline(PROBLEM_WEEK_X, color=GREY, ls="--", lw=0.8)
    a2.set_ylim(0, 8.5); a2.set_xticks(WEEKS); a2.set_xlabel("week")
    a2.set_ylabel("largest change (%)")
    a2.set_title("The dashboard: largest change in the shape card", fontsize=9.5, loc="left")
    a2.legend(loc="upper left", ncol=2, bbox_to_anchor=(0, 1.04), frameon=True, facecolor="white", edgecolor="none", framealpha=1)
    fig.savefig(OUT + "fig02.png"); plt.close(fig)


def fig_exceptions(r):
    fig, ax = plt.subplots(figsize=(5.2, 2.7))
    ax.plot(WEEKS, r["size_no"], color=NAVY, lw=2.2, marker="o", ms=4, label="the shape as it is")
    ax.plot(WEEKS[7:], r["size_dev"][7:], color=GREY, lw=1.6, ls="--", marker="o", ms=3,
            label="after it learns device type")
    ax.axhline(1.10, color=RED, ls=":", lw=1.3)
    ax.text(0.6, 1.115, "material (+10%)", color=RED, fontsize=8)
    ax.axvline(PROBLEM_WEEK_X, color=GREY, ls="--", lw=0.8)
    ax.set_xticks(WEEKS); ax.set_xlabel("week"); ax.set_ylim(0.9, 1.45)
    ax.set_ylabel("size of exceptions\n(1 = usual)")
    ax.legend(loc="upper left")
    fig.savefig(OUT + "fig03.png"); plt.close(fig)


def fig_where(r):
    fig, ax = plt.subplots(figsize=(5.2, 2.7))
    styles = {"device": (NAVY, "-", 2.2), "region": (GREY, "-", 1.4), "plan": (GREY, ":", 1.6)}
    for f, v in r["expl"].items():
        c, ls, lw = styles[f]
        ax.plot(WEEKS, v * 100, color=c, ls=ls, lw=lw, marker="o", ms=3.5, label=f)
    ax.axvline(PROBLEM_WEEK_X, color=GREY, ls="--", lw=0.8)
    ax.set_xticks(WEEKS); ax.set_xlabel("week"); ax.set_ylim(0, 25)
    ax.set_ylabel("share of exceptions\nexplained (%)")
    ax.legend(loc="upper left", title="recorded field, not in the shape", title_fontsize=8)
    fig.savefig(OUT + "fig04.png"); plt.close(fig)


def fig_silences():
    fig, ax = plt.subplots(figsize=(5.6, 3.3))
    ax.set_xlim(0, 10); ax.set_ylim(0, 6.2); ax.axis("off")
    boxes = [((0.1, 0.1), 9.8, 6.0, "#eef1f4", "The world", "changes here leave no record",
              "seen by: people"),
             ((0.7, 0.45), 8.6, 4.3, LIGHT, "The data", "changes here leave traces in the exceptions",
              "seen by: exception monitor"),
             ((1.3, 0.8), 7.4, 2.0, NAVY, "The shape", "changes here move the shape card",
              "seen by: dashboard")]
    for (xy, w, h, fc, title, sub, who) in boxes:
        ax.add_patch(FancyBboxPatch(xy, w, h, boxstyle="round,pad=0.02,rounding_size=0.25",
                                    fc=fc, ec="none"))
        col = "white" if fc == NAVY else "#2c3e50"
        ax.text(xy[0] + 0.3, xy[1] + h - 0.3, title, color=col, weight="bold", fontsize=10, va="top")
        ax.text(xy[0] + w - 0.3, xy[1] + h - 0.32, who, color=col, fontsize=8.5, va="top",
                ha="right", style="italic")
        ax.text(xy[0] + 0.3, xy[1] + h - 0.78, sub, color=col, fontsize=8.5, va="top")
    fig.savefig(OUT + "fig05.png"); plt.close(fig)


if __name__ == "__main__":
    import os
    os.makedirs(OUT, exist_ok=True)
    r = compute()
    np.set_printoptions(precision=3, suppress=True)
    print("requests", r["n"]); print("d_last", r["d_last"]); print("d_ref", r["d_ref"])
    print("size_no", r["size_no"]); print("size_dev", r["size_dev"])
    print({k: np.round(v, 3) for k, v in r["expl"].items()})
    lvl = np.expm1(r["daily"] - r["daily"][:49].mean()) * 100
    print("shared level mean before/after day 51:", lvl[:51].mean().round(2), lvl[51:].mean().round(2),
          "daily sd:", lvl[:51].std().round(2))
    fig_geometry(); fig_silent(r); fig_exceptions(r); fig_where(r); fig_silences()
