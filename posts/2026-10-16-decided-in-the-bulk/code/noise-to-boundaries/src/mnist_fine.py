"""Fine noise grid around the steepest change, with independent seeds (model refit + Monte Carlo)."""
import numpy as np, json, sys, time
from mnist_model import load, fit, diffuse, logpdf, sample, total_cov

seed = int(sys.argv[1])
rng = np.random.default_rng(100 + seed)
Xtr, ytr, _, _ = load()
M = fit(Xtr, ytr, 4, seed=seed); Ctot = total_cov(M)
n, D, N = 28, 784, 2000
Ls = [2, 3, 4, 6, 8, 10, 12]
abars = [0.3, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.9]

def region(L):
    m = np.zeros((n, n), bool); o = (n-L)//2; m[o:o+L, o:o+L] = True
    return np.where(m.ravel())[0], np.where(~m.ravel())[0]

def gauss_mi(C, a, b):
    ld = lambda Mx: np.linalg.slogdet(Mx)[1]
    return 0.5*(ld(C[np.ix_(a, a)]) + ld(C[np.ix_(b, b)]) - ld(C))

out = {"seed": seed, "Ls": Ls, "points": []}
for ab in abars:
    t0 = time.time(); Mt = diffuse(M, ab); Ct = ab*Ctot + (1-ab)*np.eye(D)
    X, _ = sample(Mt, N, rng); lp = logpdf(X, Mt)
    Im, Ie, Ic = [], [], []
    for L in Ls:
        a, b = region(L)
        pmi = lp - logpdf(X, Mt, a) - logpdf(X, Mt, b)
        Im.append(float(pmi.mean())); Ie.append(float(pmi.std()/np.sqrt(N)))
        Ic.append(float(gauss_mi(Ct, a, b)))
    out["points"].append({"abar": ab, "I_mix": Im, "err": Ie, "I_ctl": Ic})
    print(f"seed={seed} abar={ab:.2f} ({time.time()-t0:.0f}s)", flush=True)
    json.dump(out, open(f"mnist_fine_s{seed}.json", "w"), indent=1)
print(f"seed={seed} done", flush=True)
