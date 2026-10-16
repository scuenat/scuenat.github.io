"""
Area law or volume law along the generation path of a NON-Gaussian dataset.

Data: K classes. Each image = class template mu_k (a smooth, image-wide pattern)
      + local Gaussian texture (short-range correlations) + small pixel noise.
      This is a Gaussian mixture: x | y=k ~ N(mu_k, S_tex).

Diffusion with the exact score (a perfectly trained model) has forward marginals
      x_t | y=k ~ N(sqrt(abar) mu_k, C_t),  C_t = abar*S_tex + (1-abar+sigma2) I
so mutual information between a region A and its complement B splits exactly:

  I(A;B) = I_gauss(A;B | C_t)  +  [ J_A + J_B - J_full ],   J_S = I(X_S ; class)

I_gauss is exact (log-determinants). J_S = log K - E[posterior entropy of class
given X_S], estimated by Monte Carlo with exact posteriors (low variance, bounded).

Control: a single Gaussian with the SAME covariance as the mixture (same
second-order statistics, no non-Gaussian structure).
"""
import numpy as np, json, sys
from scipy.linalg import cholesky, solve_triangular

rng = np.random.default_rng(0)
n, K, sigma2 = 24, 16, 1e-2
D = n * n
Ls = [2, 3, 4, 6, 8, 10, 12]
N_MC = 4000

def stationary_cov(corr_len):
    k = np.fft.fftfreq(n) * 2 * np.pi
    kx, ky = np.meshgrid(k, k, indexing="ij")
    P = 1.0 / (kx**2 + ky**2 + (2*np.pi/corr_len)**2) ** 2
    c = np.real(np.fft.ifft2(P)); c /= c[0, 0]
    idx = np.arange(D); ix, iy = idx // n, idx % n
    return c[(ix[:, None]-ix[None, :]) % n, (iy[:, None]-iy[None, :]) % n]

# --- dataset -------------------------------------------------------------
S_tex = 0.3 * stationary_cov(2.0)                    # local texture
S_smooth = stationary_cov(n / 3)                     # generator of global patterns
Lsm = cholesky(S_smooth + 1e-9*np.eye(D), lower=True)
mu = (Lsm @ rng.standard_normal((D, K))).T           # K x D smooth templates
mu -= mu.mean(0); mu /= mu.std()                     # zero mixture mean, unit pixel std
S_mu = mu.T @ mu / K                                 # covariance contributed by classes
eye = np.eye(D)

def masks(L):
    m = np.zeros((n, n), bool); o = (n - L)//2
    m[o:o+L, o:o+L] = True; a = m.ravel()
    return a, ~a

def chol_logdet(M):
    Lc = cholesky(M, lower=True)
    return Lc, 2*np.log(np.diag(Lc)).sum()

def class_info(Lc, mu_S, ab):
    """J = I(X_S; class) by Monte Carlo with exact posteriors (whitened space)."""
    m = solve_triangular(Lc, mu_S.T, lower=True).T * np.sqrt(ab)   # K x |S|
    y = rng.integers(0, K, N_MC)
    w = m[y] + rng.standard_normal((N_MC, m.shape[1]))
    d2 = (w**2).sum(1)[:, None] - 2*w@m.T + (m**2).sum(1)[None, :]
    lg = -0.5*d2; lg -= lg.max(1, keepdims=True)
    p = np.exp(lg); p /= p.sum(1, keepdims=True)
    Hpost = -(p*np.log(np.maximum(p, 1e-300))).sum(1)
    return np.log(K) - Hpost.mean(), Hpost.std()/np.sqrt(N_MC)

def fit_beta(I):
    x, y = np.log(Ls), np.log(np.maximum(I, 1e-12))
    return float(np.polyfit(x, y, 1)[0])

abars = [0.002, 0.005, 0.01, 0.02, 0.04, 0.07, 0.1, 0.15, 0.2, 0.3,
         0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99]
out = {"Ls": Ls, "K": K, "points": []}
for ab in abars:
    C = ab*S_tex + (1-ab+sigma2)*eye
    Cc = C + ab*S_mu                                  # Gaussian control covariance
    Lf, ldf = chol_logdet(C); _, ldcf = chol_logdet(Cc)
    Jfull, ef = class_info(Lf, mu, ab)
    I_mix, I_ctl, I_gpart, I_cls, err = [], [], [], [], []
    for L in Ls:
        a, b = masks(L)
        La, lda = chol_logdet(C[np.ix_(a, a)]); Lb, ldb = chol_logdet(C[np.ix_(b, b)])
        _, ldca = chol_logdet(Cc[np.ix_(a, a)]); _, ldcb = chol_logdet(Cc[np.ix_(b, b)])
        Ja, ea = class_info(La, mu[:, a], ab); Jb, eb = class_info(Lb, mu[:, b], ab)
        g = 0.5*(lda + ldb - ldf); cls = Ja + Jb - Jfull
        I_gpart.append(g); I_cls.append(cls); I_mix.append(g + cls)
        I_ctl.append(0.5*(ldca + ldcb - ldcf)); err.append(float(np.sqrt(ea**2+eb**2+ef**2)))
    pt = {"abar": ab, "J_full_frac": Jfull/np.log(K), "I_mix": I_mix, "I_ctl": I_ctl,
          "I_gauss_part": I_gpart, "I_class_part": I_cls, "mc_err": err,
          "beta_mix": fit_beta(I_mix), "beta_ctl": fit_beta(I_ctl)}
    out["points"].append(pt)
    print(f"abar={ab:6.3f}  class known={pt['J_full_frac']:.2f}  beta mix={pt['beta_mix']:.2f}"
          f"  ctl={pt['beta_ctl']:.2f}  I(L=12) mix={I_mix[-1]:.2f} ctl={I_ctl[-1]:.2f}"
          f"  maxMCerr={max(err):.3f}", flush=True)

json.dump(out, open(sys.argv[1] if len(sys.argv) > 1 else "mixture_results.json", "w"), indent=1)
