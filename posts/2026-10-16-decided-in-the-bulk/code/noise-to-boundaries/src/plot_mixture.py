import json, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

r = json.load(open("mixture_results.json"))
P = r["points"]
ab = [p["abar"] for p in P]
import numpy as np
# refit mixture beta using only regions whose MI is clearly above Monte Carlo error (>=4 regions)
ok = []
for p in P:
    keep = [(L, i) for L, i, e in zip(r["Ls"], p["I_mix"], p["mc_err"]) if i > 5*e]
    if len(keep) >= 4 and p["abar"] >= 0.02:
        x, y = np.log([k[0] for k in keep]), np.log([k[1] for k in keep])
        p["beta_mix"] = float(np.polyfit(x, y, 1)[0]); ok.append(p)
for p in ok: print(f"abar={p['abar']:.3f} beta_mix={p['beta_mix']:.2f} beta_ctl={p['beta_ctl']:.2f}")
S, INK, INK2, MUTED, BLUE, ORANGE = "#fcfcfb", "#0b0b0b", "#52514e", "#a3a29e", "#2a78d6", "#eb6834"

fig, ax = plt.subplots(figsize=(6.6, 4.4), dpi=200, facecolor=S); ax.set_facecolor(S)
# window where the class (global structure) gets decided: 10% -> 99% known
lo = next(p["abar"] for p in P if p["J_full_frac"] >= 0.1)
hi = next(p["abar"] for p in P if p["J_full_frac"] >= 0.99)
ax.axvspan(lo, hi, color="#eceae4", zorder=0)
ax.text((lo*hi)**0.5, 2.32, "global structure\nbeing decided", ha="center", va="top",
        color=INK2, fontsize=8)
for lvl, lab in [(1, "area law"), (2, "volume law")]:
    ax.axhline(lvl, color=MUTED, lw=1, ls="--", zorder=1)
    ax.text(0.97, lvl - 0.03, lab, ha="right", va="top", color=INK2, fontsize=8,
            transform=ax.get_yaxis_transform())
ax.plot(ab, [p["beta_ctl"] for p in P], color=ORANGE, lw=2, ls=(0, (4, 2)), marker="s", ms=4.5,
        mec=S, mew=1.2, zorder=3, label="Gaussian control (same covariance)")
ax.plot([p["abar"] for p in ok], [p["beta_mix"] for p in ok], color=BLUE, lw=2, marker="o", ms=5,
        mec=S, mew=1.2, zorder=4, label="16-class dataset (non-Gaussian)")
p03 = next(p for p in ok if p["abar"] == 0.3)
ax.annotate("falls away once\nthe class is fixed", (0.3, p03["beta_mix"]), xytext=(-125, -45),
            textcoords="offset points", color=INK, fontsize=8.5,
            arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
ax.annotate("information saturates:\nsize-independent", (0.95, P[-2]["beta_mix"]),
            xytext=(-4, -38), textcoords="offset points", ha="right", color=INK, fontsize=8.5)
ax.set_xscale("log"); ax.set_ylim(0, 2.4)
ax.set_xlabel("Signal fraction ᾱ (log scale; noise → finished image)", color=INK2, fontsize=9)
ax.set_ylabel("Scaling exponent β  (I ∝ L^β)", color=INK2, fontsize=9)
ax.set_title("Non-Gaussian data leaves the Gaussian path once its global structure is set", loc="left",
             color=INK, fontsize=10.5, pad=10)
ax.legend(loc="lower left", frameon=False, fontsize=8, labelcolor=INK2)
for s in ["top", "right"]: ax.spines[s].set_visible(False)
for s in ["left", "bottom"]: ax.spines[s].set_color(MUTED)
ax.tick_params(colors=INK2, labelsize=8.5)
ax.grid(axis="y", color="#e6e5e1", lw=0.6, zorder=0)
fig.tight_layout(); fig.savefig("beta_mixture_vs_control.png", facecolor=S)
print("window", lo, hi, "reliable from", ok[0]["abar"])
