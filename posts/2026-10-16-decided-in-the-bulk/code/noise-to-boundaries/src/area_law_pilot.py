"""
Area law or volume law? Analytic pilot on Gaussian random fields.

For a Gaussian field x0 ~ N(0, S0) on an n x n periodic grid, the DDPM forward
marginal at noise level abar is x_t = sqrt(abar) x0 + sqrt(1-abar) eps, so
S_t = abar*S0 + (1-abar)*I. A perfectly trained reverse process has the same
marginals, so mutual information along the generation path is exact:

    I(A; B) = 0.5 * (logdet S_A + logdet S_B - logdet S)

A small pixel-noise floor sigma2 keeps I finite for smooth fields.
We fit I(L) ~ L^beta for centered L x L squares: beta~1 area law, beta~2 volume law.
"""
import numpy as np, json, sys

n = 40                      # grid side (1600 pixels)
sigma2 = 1e-2               # measurement-noise floor
Ls = [2, 3, 4, 6, 8, 10, 12, 14, 16]

def spectrum_cov(alpha, corr_len=None):
    """Stationary covariance with power spectrum ~ 1/(k^2+k0^2)^(alpha/2), unit variance."""
    k = np.fft.fftfreq(n) * 2 * np.pi
    kx, ky = np.meshgrid(k, k, indexing="ij")
    k2 = kx**2 + ky**2
    if alpha == 0:
        P = np.ones_like(k2)
    else:
        k0 = 2*np.pi/corr_len if corr_len else 2*np.pi/n
        P = 1.0 / (k2 + k0**2) ** (alpha/2)
    c = np.real(np.fft.ifft2(P)); c /= c[0, 0]
    idx = np.arange(n*n); ix, iy = idx // n, idx % n
    dx = (ix[:, None] - ix[None, :]) % n
    dy = (iy[:, None] - iy[None, :]) % n
    return c[dx, dy]

def logdet(M):
    s, v = np.linalg.slogdet(M); return v

def mi_square(S, L):
    m = np.zeros((n, n), bool); o = (n - L)//2
    m[o:o+L, o:o+L] = True; a = m.ravel()
    return 0.5*(logdet(S[np.ix_(a, a)]) + logdet(S[np.ix_(~a, ~a)]) - logdet(S))

def mi_strip(S, w):
    """Strip of width w spanning the torus: boundary is constant (2n), area grows with w."""
    m = np.zeros((n, n), bool); m[:w, :] = True; a = m.ravel()
    return 0.5*(logdet(S[np.ix_(a, a)]) + logdet(S[np.ix_(~a, ~a)]) - logdet(S))

def fit_beta(Ls, I):
    x, y = np.log(Ls), np.log(np.maximum(I, 1e-12))
    A = np.vstack([x, np.ones_like(x)]).T
    b, c = np.linalg.lstsq(A, y, rcond=None)[0]
    return float(b)

results = {}
fields = {
    "white_noise": spectrum_cov(0),
    "short_range (corr 2px)": spectrum_cov(2, corr_len=2),
    "natural_like (1/k^2)": spectrum_cov(2),
}
eye = np.eye(n*n)

# 1) Estimator validation on fields with known behaviour
for name, S0 in fields.items():
    S = S0 + sigma2*eye
    I = [mi_square(S, L) for L in Ls]
    Istrip = [mi_strip(S, w) for w in [2, 4, 8, 12, 16]]
    results[name] = {"I_square": I, "beta": fit_beta(Ls, I) if max(I) > 1e-6 else None,
                     "I_strip": Istrip}
    print(f"{name:26s} beta={results[name]['beta']}  strip I={np.round(Istrip,2)}", flush=True)

# 2) Generation trajectory for natural-like data: noise (abar=0) -> data (abar=1)
abars = [0.0, 0.01, 0.03, 0.1, 0.2, 0.4, 0.6, 0.8, 0.9, 0.97, 1.0]
S0 = fields["natural_like (1/k^2)"]
traj = []
for ab in abars:
    S = ab*S0 + (1-ab)*eye + sigma2*eye
    I = [mi_square(S, L) for L in Ls]
    traj.append({"abar": ab, "I": I, "beta": fit_beta(Ls, I) if max(I) > 1e-6 else None})
    print(f"abar={ab:5.2f} beta={traj[-1]['beta']}  I(L=16)={I[-1]:.3f}", flush=True)
results["trajectory"] = traj
results["Ls"] = Ls
json.dump(results, open(sys.argv[1] if len(sys.argv) > 1 else "results.json", "w"), indent=1)
