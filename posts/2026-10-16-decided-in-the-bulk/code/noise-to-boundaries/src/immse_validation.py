"""
Validate the I-MMSE route to region-complement information against the exact values.

Channel: Y = sqrt(snr) X + N  (equivalent to x_t = sqrt(abar) x0 + sqrt(1-abar) eps, snr = abar/(1-abar)).
I-MMSE (Guo, Shamai, Verdu 2005): d/dsnr I(X_S; Y_S) = 1/2 mmse_S(snr).
Noise entropies cancel in H(Y_A)+H(Y_B)-H(Y), so

   I(Y_A; Y_B)(snr) = 1/2 * integral_0^snr [ mmse_A + mmse_B - mmse_full ](g) dg

mmse_A  : error denoising region A from noisy A only
mmse_full: error denoising all pixels from the whole noisy image
-> information = how much seeing the rest of the image helps denoise each part, integrated over noise.
This needs only denoisers (with and without context), so it applies to trained diffusion models.

Here the denoisers are exact (posterior of the learned MNIST mixture), using the
Rao-Blackwellized error E[tr Cov(X_S | Y_S)] with common random numbers across denoisers.
"""
import numpy as np, json, sys, time
from scipy.special import logsumexp
from mnist_model import load, fit

part, nparts = int(sys.argv[1]), int(sys.argv[2])
rng = np.random.default_rng(7 + part)
Xtr, ytr, _, _ = load()
M = fit(Xtr, ytr, 4, seed=0)                       # same model as the exact-MI run
w, MU, SIG = M["w"], M["mu"], M["C"]; K, D, n = len(w), 784, 28
N = 1000
Ls = [2, 4, 8, 12]
abars = [0.003, 0.006, 0.012, 0.02, 0.035, 0.05, 0.075, 0.1, 0.15, 0.2, 0.27,
         0.35, 0.42, 0.5, 0.6, 0.7, 0.78, 0.85, 0.9, 0.95]
mine = abars[part::nparts]

def region(L):
    m = np.zeros((n, n), bool); o = (n-L)//2; m[o:o+L, o:o+L] = True
    return np.where(m.ravel())[0], np.where(~m.ravel())[0]

def posterior_error(Y, ab, idx):
    """Per-sample E[ ||X_S - E[X_S|Y_S]||^2 | Y_S ] for the mixture, using only pixels idx."""
    Ys = Y[:, idx]; d = len(idx)
    logr, means, trc = [], [], []
    for k in range(K):
        S = SIG[k][np.ix_(idx, idx)]; m = MU[k][idx]
        C = ab*S + (1-ab)*np.eye(d)
        L = np.linalg.cholesky(C)
        R = Ys - np.sqrt(ab)*m
        z = np.linalg.solve(L, R.T)                                   # d x N
        logr.append(np.log(w[k]) - 0.5*(z**2).sum(0) - np.log(np.diag(L)).sum())
        G = np.linalg.solve(L.T, z)                                   # C^-1 R^T
        means.append(m[None, :] + np.sqrt(ab)*(S @ G).T)              # N x d
        LS = np.linalg.solve(L, S)                                    # L^-1 S
        trc.append(np.trace(S) - ab*(LS**2).sum())                   # tr(S - ab S C^-1 S)
    logr = np.array(logr); r = np.exp(logr - logsumexp(logr, axis=0))  # K x N
    mbar = np.einsum("kn,knd->nd", r, np.array(means))
    spread = np.einsum("kn,kn->n", r, np.array([((mk - mbar)**2).sum(1) for mk in means]))
    return r.T @ np.array(trc) + spread

out = {"part": part, "Ls": Ls, "points": []}
for ab in mine:
    t0 = time.time()
    k = rng.choice(K, N, p=w); X = np.empty((N, D))
    for j in np.unique(k):
        i = np.where(k == j)[0]
        X[i] = MU[j] + rng.standard_normal((len(i), D)) @ np.linalg.cholesky(SIG[j]).T
    Y = np.sqrt(ab)*X + np.sqrt(1-ab)*rng.standard_normal((N, D))
    full = posterior_error(Y, ab, np.arange(D))
    rows = []
    for L in Ls:
        a, b = region(L)
        diff = posterior_error(Y, ab, a) + posterior_error(Y, ab, b) - full
        rows.append([float(diff.mean()), float(diff.std()/np.sqrt(N))])
    out["points"].append({"abar": ab, "excess_mmse": rows})
    print(f"part{part} abar={ab:.3f} ({time.time()-t0:.0f}s) excess={np.round([r[0] for r in rows],3)}", flush=True)
    json.dump(out, open(f"immse_part{part}.json", "w"), indent=1)
print(f"part{part} done", flush=True)
