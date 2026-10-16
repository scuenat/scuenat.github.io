"""Integrate the region-wise denoising-error excess (I-MMSE) and compare with exact mutual information."""
import json, glob, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

pts = sorted([p for f in sorted(glob.glob("immse_part*.json")) for p in json.load(open(f))["points"]],
             key=lambda p: p["abar"])
Ls = [2, 4, 8, 12]
ab = np.array([p["abar"] for p in pts]); snr = ab/(1-ab)
F = np.array([[r[0] for r in p["excess_mmse"]] for p in pts])      # n_ab x n_L
E = np.array([[r[1] for r in p["excess_mmse"]] for p in pts])

# I(snr) = 1/2 * int_0^snr F ; f(0)=0, so the first interval is a triangle
I = np.zeros_like(F); V = np.zeros_like(F)
I[0] = 0.5*0.5*snr[0]*F[0]; V[0] = (0.25*snr[0]*E[0])**2
for i in range(1, len(snr)):
    h = snr[i]-snr[i-1]
    I[i] = I[i-1] + 0.5*0.5*h*(F[i]+F[i-1])
    V[i] = V[i-1] + (0.25*h*E[i])**2 + (0.25*h*E[i-1])**2
Ierr = np.sqrt(V)

exact = json.load(open("mnist_results.json"))
eL = exact["Ls"]; idx = [eL.index(L) for L in Ls]
rows = []
for p in exact["points"]:
    if p["abar"] in list(ab):
        i = list(ab).index(p["abar"])
        for j, L in enumerate(Ls):
            rows.append({"abar": p["abar"], "L": L, "exact": p["I_mix"][idx[j]],
                         "exact_err": p["err"][idx[j]], "immse": float(I[i, j]), "immse_err": float(Ierr[i, j])})
for r in rows:
    print(f"abar={r['abar']:.2f} L={r['L']:2d}  exact={r['exact']:7.3f}±{r['exact_err']:.3f}  "
          f"I-MMSE={r['immse']:7.3f}±{r['immse_err']:.3f}  ratio={r['immse']/r['exact']:.3f}")
ex = np.array([r["exact"] for r in rows]); im = np.array([r["immse"] for r in rows])
rel = np.abs(im-ex)/ex
print(f"median |rel. diff| = {np.median(rel):.3f}, max = {rel.max():.3f}, corr(log) = "
      f"{np.corrcoef(np.log(ex), np.log(im))[0,1]:.4f}")
json.dump({"rows": rows, "median_rel": float(np.median(rel)), "max_rel": float(rel.max())},
          open("immse_comparison.json", "w"), indent=1)

S, INK, INK2, MUTED, BLUE = "#fcfcfb", "#0b0b0b", "#52514e", "#a3a29e", "#2a78d6"
fig, ax = plt.subplots(figsize=(5.2, 4.6), dpi=200, facecolor=S); ax.set_facecolor(S)
lo, hi = ex.min()*0.6, ex.max()*1.6
ax.plot([lo, hi], [lo, hi], color=MUTED, lw=1, ls="--", zorder=1)
ax.text(hi*0.6, hi*0.12, "dashed line:\nperfect agreement", ha="right", va="top", color=INK2, fontsize=8)
ax.errorbar(ex, im, xerr=2*np.array([r["exact_err"] for r in rows]),
            yerr=2*np.array([r["immse_err"] for r in rows]), fmt="o", color=BLUE, ms=5,
            mec=S, mew=1, elinewidth=1, zorder=3)
ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
ax.set_xlabel("Exact mutual information (nats)", color=INK2, fontsize=9)
ax.set_ylabel("From denoising errors, I-MMSE (nats)", color=INK2, fontsize=9)
ax.set_title(f"Denoising errors recover the information\n(median deviation {100*np.median(rel):.1f}%)",
             loc="left", color=INK, fontsize=10)
for s in ["top", "right"]: ax.spines[s].set_visible(False)
for s in ["left", "bottom"]: ax.spines[s].set_color(MUTED)
ax.tick_params(colors=INK2, labelsize=8, which="both")
fig.text(0.99, 0.01, f"{len(rows)} points: regions L = 2, 4, 8, 12 px × 8 noise levels; bars ± 2 s.e.",
         ha="right", color=INK2, fontsize=7)
fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig("immse_validation.png", facecolor=S)
