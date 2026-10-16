"""Full-covariance Gaussian mixture on 28x28 MNIST: a learned pixel-space density with exact marginals."""
import numpy as np
from scipy.special import logsumexp
from sklearn.cluster import KMeans

S_FLOOR = 1e-2

def load(path=None):
    import os
    path = path or os.environ.get("MNIST_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "mnist.npz"))
    d = np.load(path, allow_pickle=False)
    f = lambda x: x.reshape(len(x), -1).astype(np.float64) / 255.0 * 2 - 1
    return f(d["x_train"]), d["y_train"], f(d["x_test"]), d["y_test"]

def fit(X, y, m, seed=0):
    """m sub-clusters per digit (k-means), one full-covariance Gaussian per cluster."""
    w, mu, C = [], [], []
    for c in range(10):
        Xc = X[y == c]
        lab = (KMeans(m, n_init=3, random_state=seed).fit_predict(Xc) if m > 1
               else np.zeros(len(Xc), int))
        for j in range(m):
            Z = Xc[lab == j]
            w.append(len(Z)/len(X)); mu.append(Z.mean(0))
            C.append(np.cov(Z, rowvar=False) + S_FLOOR*np.eye(X.shape[1]))
    return dict(w=np.array(w), mu=np.array(mu), C=np.array(C))

def diffuse(M, ab):
    """Exact forward marginal at signal fraction ab: still a Gaussian mixture."""
    D = M["mu"].shape[1]
    return dict(w=M["w"], mu=np.sqrt(ab)*M["mu"], C=ab*M["C"] + (1-ab)*np.eye(D))

def logpdf(X, M, idx=None):
    """Log density of the mixture marginal on pixel subset idx."""
    if idx is None: idx = np.arange(X.shape[1])
    Xs = X[:, idx]; d = len(idx); out = []
    for wk, mk, Ck in zip(M["w"], M["mu"], M["C"]):
        L = np.linalg.cholesky(Ck[np.ix_(idx, idx)])
        z = np.linalg.solve(L, (Xs - mk[idx]).T)
        out.append(np.log(wk) - 0.5*((z**2).sum(0) + 2*np.log(np.diag(L)).sum() + d*np.log(2*np.pi)))
    return logsumexp(np.array(out), axis=0)

def sample(M, N, rng):
    k = rng.choice(len(M["w"]), N, p=M["w"]); X = np.empty((N, M["mu"].shape[1]))
    for j in np.unique(k):
        i = np.where(k == j)[0]; L = np.linalg.cholesky(M["C"][j])
        X[i] = M["mu"][j] + rng.standard_normal((len(i), L.shape[0])) @ L.T
    return X, k

def total_cov(M):
    mbar = M["w"] @ M["mu"]; C = np.zeros_like(M["C"][0])
    for wk, mk, Ck in zip(M["w"], M["mu"], M["C"]):
        dm = mk - mbar; C += wk*(Ck + np.outer(dm, dm))
    return C

if __name__ == "__main__":
    Xtr, ytr, Xte, yte = load()
    for m in [1, 2, 4]:
        M = fit(Xtr, ytr, m)
        print(f"{10*m:2d} components  held-out log-lik/img = {logpdf(Xte, M).mean():9.1f}", flush=True)
    C = np.cov(Xtr, rowvar=False) + S_FLOOR*np.eye(784)
    L = np.linalg.cholesky(C); R = (Xte - Xtr.mean(0)) @ np.linalg.inv(L).T
    print("single Gaussian held-out log-lik/img =",
          round(float((-0.5*((R**2).sum(1) + 2*np.log(np.diag(L)).sum() + 784*np.log(2*np.pi))).mean()), 1))
