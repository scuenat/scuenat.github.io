"""
beta along the diffusion path for a learned model of real digits (8x8).
Diffusing the learned mixture gives exact marginals:
   x_t ~ sum_k w_k N(sqrt(abar) mu_k, abar Sigma_k + (1-abar) I)
I(A;B) = E[log p(x) - log p(x_A) - log p(x_B)] by Monte Carlo with exact densities.
Control: one Gaussian with the model's total covariance (exact log-determinants).
"""
import numpy as np, pickle, json
from scipy.special import logsumexp
from scipy.linalg import cholesky, solve_triangular

rng = np.random.default_rng(1)
d = pickle.load(open("digits_gmm.pkl", "rb")); gm = d["gm"]
w, MU, SIG = gm.weights_, gm.means_, gm.covariances_
K, D, n = len(w), 64, 8
mbar = w @ MU
Stot = sum(w[k]*(SIG[k] + np.outer(MU[k]-mbar, MU[k]-mbar)) for k in range(K))
Ls = [1, 2, 3, 4, 5]
N = 20000

def region(L):
    m = np.zeros((n, n), bool); o = (n-L)//2; m[o:o+L, o:o+L] = True
    return m.ravel()

def gmm_logpdf(X, mus, covs, w):
    out = np.empty((X.shape[0], len(w)))
    for k in range(len(w)):
        Lc = cholesky(covs[k], lower=True)
        z = solve_triangular(Lc, (X - mus[k]).T, lower=True)
        out[:, k] = (np.log(w[k]) - 0.5*(z**2).sum(0) - np.log(np.diag(Lc)).sum()
                     - 0.5*X.shape[1]*np.log(2*np.pi))
    return logsumexp(out, axis=1)

def gauss_mi(C, a):
    ld = lambda M: np.linalg.slogdet(M)[1]
    return 0.5*(ld(C[np.ix_(a, a)]) + ld(C[np.ix_(~a, ~a)]) - ld(C))

abars = [0.01, 0.02, 0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 0.85, 0.95, 0.99]
res = {"Ls": Ls, "K": K, "points": []}
for ab in abars:
    mus = np.sqrt(ab)*MU; covs = ab*SIG + (1-ab)*np.eye(D)
    ks = rng.choice(K, N, p=w)
    X = np.empty((N, D))
    for k in range(K):
        idx = np.where(ks == k)[0]
        X[idx] = rng.multivariate_normal(mus[k], covs[k], len(idx))
    lp = gmm_logpdf(X, mus, covs, w)
    Im, Ie, Ic = [], [], []
    Cc = ab*Stot + (1-ab)*np.eye(D)
    for L in Ls:
        a = region(L)
        la = gmm_logpdf(X[:, a], mus[:, a], covs[:, a][:, :, a], w)
        lb = gmm_logpdf(X[:, ~a], mus[:, ~a], covs[:, ~a][:, :, ~a], w)
        pmi = lp - la - lb
        Im.append(float(pmi.mean())); Ie.append(float(pmi.std()/np.sqrt(N)))
        Ic.append(float(gauss_mi(Cc, a)))
    fit = lambda I: float(np.polyfit(np.log(Ls), np.log(np.maximum(I, 1e-9)), 1)[0])
    pt = {"abar": ab, "I_mix": Im, "err": Ie, "I_ctl": Ic, "beta_mix": fit(Im), "beta_ctl": fit(Ic)}
    res["points"].append(pt)
    print(f"abar={ab:5.2f} beta model={pt['beta_mix']:.2f} ctl={pt['beta_ctl']:.2f} "
          f"I(L=1..5) model={np.round(Im,3)} err~{max(Ie):.3f} ctl={np.round(Ic,3)}", flush=True)

# a strip of forward snapshots of one generated digit, for the figure
k0 = 0; x0 = rng.multivariate_normal(MU[k0], SIG[k0]); eps = rng.standard_normal(D)
strip = [(ab, (np.sqrt(ab)*x0 + np.sqrt(1-ab)*eps).tolist()) for ab in [0.02, 0.1, 0.3, 0.7, 1.0]]
res["strip"] = strip
samples = gm.sample(12)[0]; res["samples"] = samples.tolist()
json.dump(res, open("digits_results.json", "w"), indent=1)
