import json, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

r = json.load(open("results.json"))
t = [p for p in r["trajectory"] if p["beta"] is not None]
x = [p["abar"] for p in t]; y = [p["beta"] for p in t]

S, INK, INK2, MUTED, BLUE = "#fcfcfb", "#0b0b0b", "#52514e", "#a3a29e", "#2a78d6"
fig, ax = plt.subplots(figsize=(6.4, 4.2), dpi=200, facecolor=S)
ax.set_facecolor(S)
for lvl, lab in [(1, "area law (β = 1)"), (2, "volume law (β = 2)")]:
    ax.axhline(lvl, color=MUTED, lw=1, ls="--", zorder=1)
    above = lvl == 2
    ax.text(0.995, lvl + (0.03 if above else -0.03), lab, ha="right", va="bottom" if above else "top",
            color=INK2, fontsize=8.5,
            transform=ax.get_yaxis_transform())
ax.plot(x, y, color=BLUE, lw=2, marker="o", ms=5, mec=S, mew=1.5, zorder=3)
ax.annotate(f"data: β = {y[-1]:.2f}", (x[-1], y[-1]), xytext=(-8, 14), textcoords="offset points",
            ha="right", color=INK, fontsize=9)
ax.annotate(f"near-pure noise: β = {y[0]:.2f}", (x[0], y[0]), xytext=(10, 4), textcoords="offset points",
            color=INK, fontsize=9)
ax.set_xlim(-0.02, 1.02); ax.set_ylim(0.8, 2.15)
ax.set_xlabel("Signal fraction ᾱ  (0 = pure noise → 1 = finished image)", color=INK2, fontsize=9)
ax.set_ylabel("Scaling exponent β  (I ∝ L^β)", color=INK2, fontsize=9)
ax.set_title("Gaussian baseline: area law emerges smoothly, no sharp transition",
             loc="left", color=INK, fontsize=10.5, pad=10)
for s in ["top", "right"]: ax.spines[s].set_visible(False)
for s in ["left", "bottom"]: ax.spines[s].set_color(MUTED)
ax.tick_params(colors=INK2, labelsize=8.5)
ax.grid(axis="y", color="#e6e5e1", lw=0.6, zorder=0)
fig.tight_layout()
fig.savefig("beta_trajectory.png", facecolor=S)
