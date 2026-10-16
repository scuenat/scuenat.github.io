import json, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = [json.load(open(f"mnist_fine_s{s}.json")) for s in range(3)]
L = np.array(R[0]["Ls"]); ab = np.array([p["abar"] for p in R[0]["points"]])
fit = lambda I: np.polyfit(np.log(L), np.log(I), 1)[0]
BM = np.array([[fit(np.array(p["I_mix"])) for p in r["points"]] for r in R])
BC = np.array([[fit(np.array(p["I_ctl"])) for p in r["points"]] for r in R])
BE = np.array([[fit(np.array(p["I_mix"]) - np.array(p["I_ctl"])) for p in r["points"]] for r in R])

S, INK, INK2, MUTED, BLUE, ORANGE, AQUA = "#fcfcfb", "#0b0b0b", "#52514e", "#a3a29e", "#2a78d6", "#eb6834", "#1baf7a"
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.6, 3.6), dpi=200, facecolor=S)
for ax in (a1, a2):
    ax.set_facecolor(S); ax.axhline(1, color=MUTED, lw=1, ls="--", zorder=1)
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    for s in ["left", "bottom"]: ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=INK2, labelsize=8); ax.grid(axis="y", color="#e6e5e1", lw=0.6, zorder=0)
    ax.set_xlabel("Signal fraction ᾱ", color=INK2, fontsize=9)

a1.errorbar(ab, BC.mean(0), yerr=2*BC.std(0), color=ORANGE, lw=2, ls=(0, (4, 2)), marker="s", ms=4,
            mec=S, mew=1, label="Gaussian control")
a1.errorbar(ab, BM.mean(0), yerr=2*BM.std(0), color=BLUE, lw=2, marker="o", ms=4.5, mec=S, mew=1,
            capsize=0, label="Learned MNIST model")
a1.set_ylim(0.95, 1.5); a1.set_ylabel("Scaling exponent β", color=INK2, fontsize=9)
a1.set_title("a  Total information: smooth convergence", loc="left", color=INK, fontsize=9.5)
a1.legend(loc="upper right", frameon=False, fontsize=7.5, labelcolor=INK2)
a1.text(0.31, 1.005, "area law", color=INK2, fontsize=7.5, va="bottom")

a2.errorbar(ab, BE.mean(0), yerr=2*BE.std(0), color=AQUA, lw=2, marker="D", ms=4, mec=S, mew=1, capsize=0)
a2.axhline(2, color=MUTED, lw=1, ls="--", zorder=1)
a2.text(0.31, 1.97, "volume law", color=INK2, fontsize=7.5, va="top")
a2.text(0.31, 1.005, "area law", color=INK2, fontsize=7.5, va="bottom")
a2.set_ylim(0.95, 2.1); a2.set_ylabel("Exponent of excess over control", color=INK2, fontsize=9)
a2.set_title("b  Non-Gaussian excess: bulk → boundary", loc="left", color=INK, fontsize=9.5)
fig.text(0.99, 0.01, "mean ± 2 s.d. over 3 seeds (model refit + Monte Carlo); regions L = 2–12 px",
         ha="right", color=INK2, fontsize=7)
fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig("mnist_fine.png", facecolor=S)
