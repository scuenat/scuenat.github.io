"""Simulations for "Let the Code Be Chaotic".

Two models, both small and both labelled as toys in the paper.

1. The Lorenz system (sigma=10, rho=28, beta=8/3), integrated with RK4. Two runs start 1e-8 apart:
   their paths separate exponentially, yet both stay on the same attractor, so any long-run
   statistic of the two runs agrees.

2. A chaotic generator held by a test loop. The implementation is a vector x in R^n (n = 300).
   The generator is a random recurrent network in its chaotic regime
   (Sompolinsky, Crisanti and Sommers, 1988):
        x <- x + dt * (-x + J tanh(g x)),      J_ij ~ N(0, 1/n), g = 1.6.
   Behaviour is what an observer can see: y = B x, with B an m x n matrix with orthonormal rows
   (m = 30). The spec fixes a target behaviour y*. The tests check K of the m behaviour
   directions (rows of an orthonormal basis C of R^m). After each generation step, the loop
   pulls the tested directions back toward the spec:
        x <- x - kappa * B^T C_K^T C_K (B x - y*).
   Nothing else is controlled: the n - m directions of x that no one observes, and the m - K
   observable directions that no test checks, are left to the generator.
All numbers are written to results.json.
"""
import json
import numpy as np

# ---------------------------------------------------------------- Lorenz
def lorenz_rhs(s, sigma=10.0, rho=28.0, beta=8.0 / 3.0):
    x, y, z = s[..., 0], s[..., 1], s[..., 2]
    return np.stack([sigma * (y - x), x * (rho - z) - y, x * y - beta * z], axis=-1)


def lorenz(T=60.0, dt=0.005, eps=1e-8):
    n = int(T / dt)
    s = np.array([[1.0, 1.0, 20.0], [1.0 + eps, 1.0, 20.0]])
    out = np.empty((n, 2, 3))
    for i in range(n):
        out[i] = s
        k1 = lorenz_rhs(s); k2 = lorenz_rhs(s + dt / 2 * k1)
        k3 = lorenz_rhs(s + dt / 2 * k2); k4 = lorenz_rhs(s + dt * k3)
        s = s + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    t = np.arange(n) * dt
    sep = np.linalg.norm(out[:, 0] - out[:, 1], axis=1)
    # Lyapunov exponent from the slope of log separation before saturation
    m = (sep > 1e-6) & (sep < 1e-1)
    lam = float(np.polyfit(t[m], np.log(sep[m]), 1)[0])
    t_sep = float(t[np.argmax(sep > 1.0)])
    burn = int(10 / dt)
    zs = [out[burn:, k, 2] for k in range(2)]
    stats = {f"run{k + 1}": dict(mean_z=float(zs[k].mean()), sd_z=float(zs[k].std()))
             for k in range(2)}
    return t, out, sep, dict(eps=1e-8, lyapunov_fit=round(lam, 3), t_separated=round(t_sep, 2),
                             **stats)


# ---------------------------------------------------------------- generator held by tests
N, M = 300, 30


class World:
    def __init__(self, seed=0, n=N, m=M, g=1.6):
        r = np.random.default_rng(seed)
        self.n, self.m, self.g = n, m, g
        self.J = r.normal(0, 1 / np.sqrt(n), (n, n))
        q, _ = np.linalg.qr(r.normal(size=(n, m)))
        self.B = q.T                                   # m x n, orthonormal rows
        c, _ = np.linalg.qr(r.normal(size=(m, m)))
        self.C = c.T                                   # m x m, test directions in behaviour space
        self.ystar = r.normal(0, 0.5, m)              # the spec

    def run(self, x0, K, kappa=0.5, steps=3000, dt=0.1, record=False):
        P = self.B.T @ self.C[:K].T                    # n x K: tested directions in code space
        x = x0.copy()
        ys = self.C[:K] @ self.ystar
        hist = []
        for _ in range(steps):
            x = x + dt * (-x + self.J @ np.tanh(self.g * x))
            if K:
                x = x - kappa * P @ (P.T @ x - ys)
            if record:
                hist.append(x.copy())
        return (x, np.array(hist)) if record else x

    def split(self, x, K):
        """Code, tested behaviour, untested behaviour."""
        y = self.B @ x
        z = self.C @ (y - self.ystar)
        return x, z[:K], z[K:]


G, KAPPA, DT = 3.0, 0.8, 0.1


def twins(K, seed=1, kappa=KAPPA, eps=1e-8, steps=2500):
    """Two runs of the same generator from starts 1e-8 apart: the Lyapunov picture.
    Returns time, and the separation of the two runs in code, tested behaviour and
    untested behaviour, plus the fitted Lyapunov exponent of the code separation."""
    w = World(seed, g=G)
    r = np.random.default_rng(100 + seed)
    x0 = r.normal(0, 1, w.n)
    _, h1 = w.run(x0, K, kappa, steps, DT, record=True)
    _, h2 = w.run(x0 + eps * r.normal(0, 1, w.n) / np.sqrt(w.n), K, kappa, steps, DT, record=True)
    d = h1 - h2
    code = np.linalg.norm(d, axis=1)
    beh = (w.C @ (w.B @ d.T)).T
    tested = np.linalg.norm(beh[:, :K], axis=1)
    untested = np.linalg.norm(beh[:, K:], axis=1)
    t = np.arange(steps) * DT
    msk = (code > 1e-6) & (code < 1e-1)
    lam = float(np.polyfit(t[msk], np.log(code[msk]), 1)[0])
    # distance of each run's tested behaviour to the spec, averaged after the transient
    Y1 = (w.C[:K] @ (w.B @ h1[300:].T)).T - w.C[:K] @ w.ystar
    err = float(np.sqrt((Y1 ** 2).sum(1).mean()))
    return t, code, tested, untested, dict(K=K, lyapunov_fit=round(lam, 3),
                                           final_code_sep=float(code[-1]),
                                           max_tested_sep=float(tested.max()),
                                           final_untested_sep=float(untested[-1]),
                                           tested_error_to_spec=err)


def ensemble(K, kappa=KAPPA, g=G, runs=10, seed=7, steps=1000, burn=300):
    """Independent runs (different starting points) of one generator under one spec.
    Time-averaged after a transient. Returns
      code_div: mean distance between two runs' code / the distance expected for unrelated
                vectors of the same size (1 = as different as two random programs);
      err_all / err_tested / err_untested: rms distance of behaviour to the spec."""
    w = World(seed, g=g)
    r = np.random.default_rng(seed + 1000)
    X, Ys = [], []
    for _ in range(runs):
        _, h = w.run(r.normal(0, 1, w.n), K, kappa, steps, DT, record=True)
        h = h[burn::10]
        X.append(h)
        Ys.append((w.C @ (w.B @ h.T)).T - w.C @ w.ystar)
    X, Y = np.array(X), np.array(Ys)                  # runs x time x dims
    pair = np.mean([np.linalg.norm(X[i] - X[j], axis=1).mean()
                    for i in range(runs) for j in range(i + 1, runs)])
    rms = np.sqrt((X ** 2).sum(2).mean())
    rms_err = lambda A: float(np.sqrt((A ** 2).sum(2).mean())) if A.shape[2] else 0.0
    return dict(K=K, kappa=kappa, g=g, code_div=float(pair / (np.sqrt(2) * rms)),
                err_all=rms_err(Y), err_tested=rms_err(Y[:, :, :K]),
                err_untested=rms_err(Y[:, :, K:]))


def main():
    res = {"model": dict(n=N, m=M, g=G, kappa=KAPPA, dt=DT)}
    _, _, _, lz = lorenz()
    res["lorenz"] = lz
    res["twins"] = {str(K): twins(K)[4] for K in (M, 20)}
    res["coverage"] = [ensemble(K) for K in range(0, M + 1, 3)]
    free = res["coverage"][0]["err_all"]
    for row in res["coverage"]:
        row["err_all_rel"] = row["err_all"] / free
    kappas = [0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0]
    gains = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0]
    grid = []
    for g in gains:
        f = ensemble(0, g=g, runs=4)["err_all"]
        grid.append([ensemble(M, kappa=k, g=g, runs=4)["err_all"] / f for k in kappas])
    res["phase"] = dict(kappas=kappas, gains=gains, err_rel=grid)
    return res


if __name__ == "__main__":
    out = main()
    json.dump(out, open("results.json", "w"), indent=2)
    print(json.dumps({k: v for k, v in out.items() if k != "phase"}, indent=1))
    print(np.round(np.array(out["phase"]["err_rel"]), 3))
