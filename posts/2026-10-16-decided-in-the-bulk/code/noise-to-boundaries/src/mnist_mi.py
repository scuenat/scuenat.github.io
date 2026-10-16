"""Information scaling along the diffusion path for a learned 28x28 MNIST model vs a Gaussian control."""
import numpy as np, json, time
from mnist_model import load, fit, diffuse, logpdf, sample, total_cov

rng = np.random.default_rng(2)
Xtr, ytr, _, _ = load()
M = fit(Xtr, ytr, 4)
Ctot = total_cov(M)
n, D, N = 28, 784, 2000
Ls = [2, 3, 4, 6, 8, 10, 12, 14, 17, 20]
abars = [0.05, 0.1, 0.2, 0.35, 0.5, 0.7, 0.85, 0.95, 0.99]

def region(L):
    m = np.zeros((n, n), bool); o = (n-L)//2; m[o:o+L, o:o+L] = True
    return np.where(m.ravel())[0], np.where(~m.ravel())[0]

def gauss_mi(C, a, b):
    ld = lambda Mx: np.linalg.slogdet(Mx)[1]
    return 0.5*(ld(C[np.ix_(a, a)]) + ld(C[np.ix_(b, b)]) - ld(C))

out = {"Ls": Ls, "points": []}
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
    print(f"abar={ab:4.2f} ({time.time()-t0:4.0f}s)  model={np.round(Im,2)}  err<={max(Ie):.2f}"
          f"  ctl={np.round(Ic,2)}", flush=True)
    json.dump(out, open("mnist_results.json", "w"), indent=1)

out["samples"] = sample(M, 12, rng)[0].tolist()
json.dump(out, open("mnist_results.json", "w"), indent=1)
print("done")
