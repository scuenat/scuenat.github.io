"""Fit a Gaussian-mixture generative model to the 8x8 sklearn digits; pick K on held-out likelihood."""
import numpy as np, pickle
from sklearn.datasets import load_digits
from sklearn.mixture import GaussianMixture
from sklearn.model_selection import train_test_split

X = load_digits().data / 16.0 * 2 - 1          # pixels in [-1, 1]
Xtr, Xte = train_test_split(X, test_size=0.25, random_state=0)
best = None
for K in [1, 5, 10, 20, 30, 40, 60]:
    gm = GaussianMixture(K, covariance_type="full", reg_covar=1e-2, n_init=2,
                         max_iter=300, random_state=0).fit(Xtr)
    tr, te = gm.score(Xtr), gm.score(Xte)
    print(f"K={K:3d}  train ll/img={tr:7.2f}  held-out ll/img={te:7.2f}", flush=True)
    if best is None or te > best[1]:
        best = (K, te, gm)
K, te, gm = best
print("chosen K =", K)
# refit on all data with the chosen K
gm = GaussianMixture(K, covariance_type="full", reg_covar=1e-2, n_init=2,
                     max_iter=300, random_state=0).fit(X)
pickle.dump({"gm": gm, "X": X}, open("digits_gmm.pkl", "wb"))
