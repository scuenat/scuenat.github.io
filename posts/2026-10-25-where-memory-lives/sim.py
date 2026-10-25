"""Experiments for "Where Memory Lives". Pure NumPy, runs on a laptop CPU.

    python sim.py            # all experiments, writes results.json (about 2 hours on 4 cores)
    python sim.py capacity   # one experiment: capacity, capacity_long, editing, editing_sweep,
                             # lookup, lookup_noise, working

1. capacity  How many bits of random facts fit in the weights of a small network.
2. editing   What happens to the other facts when a few are changed in the weights.
3. lookup    The same facts in an external memory: recall, latency, bytes touched.
4. working   Time per generated token for one Llama-3.2-1B-shaped layer: weights vs KV cache.
"""
import json
import sys
import time
import numpy as np

OUT = "results.json"
V = 256          # each fact's value is one of 256 classes: 8 bits
D = 32           # key dimension (the "question" a fact answers)


# ---------------------------------------------------------------- 1. parametric memory
def init(h, d=D, v=V, seed=0):
    r = np.random.default_rng(seed)
    return [(r.standard_normal((d, h)) / np.sqrt(d)).astype(np.float32), np.zeros(h, np.float32),
            (r.standard_normal((h, v)) / np.sqrt(h)).astype(np.float32), np.zeros(v, np.float32)]


def n_params(h, d=D, v=V):
    return d * h + h + h * v + v


def logits(P, X):
    return np.maximum(X @ P[0] + P[1], 0) @ P[2] + P[3]


def fit(P, X, y, steps, lr, state=None, log=None, every=10):
    """Full-batch Adam on cross-entropy, cosine decay. Returns the Adam state."""
    W1, b1, W2, b2 = P
    m, v, t0 = state if state else ([np.zeros_like(p) for p in P], [np.zeros_like(p) for p in P], 0)
    n = len(y)
    for s in range(1, steps + 1):
        H = X @ W1 + b1
        A = np.maximum(H, 0)
        Z = A @ W2 + b2
        Z -= Z.max(1, keepdims=True)
        G = np.exp(Z)
        G /= G.sum(1, keepdims=True)
        G[np.arange(n), y] -= 1
        G /= n
        GA = (G @ W2.T) * (H > 0)
        grads = [X.T @ GA, GA.sum(0), A.T @ G, G.sum(0)]
        t = t0 + s
        a = lr * 0.5 * (1 + np.cos(np.pi * s / steps))
        for p, g, mm, vv in zip(P, grads, m, v):
            mm *= 0.9; mm += 0.1 * g
            vv *= 0.999; vv += 0.001 * g * g
            p -= a * (mm / (1 - 0.9 ** t)) / (np.sqrt(vv / (1 - 0.999 ** t)) + 1e-8)
        if log is not None and (s % every == 0 or s == 1):
            log(s)
    return m, v, t0 + steps


def stored_bits(P, X, y):
    """Bits of the facts the network holds: per fact, log2 V minus its cross-entropy in bits,
    floored at zero (a lower bound in the spirit of Allen-Zhu & Li, 2024)."""
    Z = logits(P, X)
    Z -= Z.max(1, keepdims=True)
    lp = Z[np.arange(len(y)), y] - np.log(np.exp(Z).sum(1))
    return float(np.clip(np.log2(V) + lp / np.log(2), 0, None).sum())


def accuracy(P, X, y):
    return float((logits(P, X).argmax(1) == y).mean()) if len(y) else float("nan")


def capacity_run(h, load, seed, steps=3000):
    p = n_params(h)
    n = int(round(load * p / np.log2(V)))
    r = np.random.default_rng(1000 * seed + h)
    X = r.standard_normal((n, D)).astype(np.float32)
    y = r.integers(0, V, n)
    P = init(h, seed=seed)
    t = time.time()
    fit(P, X, y, steps=steps, lr=1e-2)
    b = stored_bits(P, X, y)
    row = dict(hidden=h, params=p, facts=n, seed=seed, steps=steps, offered_bits=n * np.log2(V),
               stored_bits=b, bits_per_param=b / p, accuracy=accuracy(P, X, y), seconds=time.time() - t)
    print(f"capacity h={h:3d} P={p:6d} N={n:6d} seed={seed} steps={steps} "
          f"bits/param={b / p:.2f} acc={row['accuracy']:.3f}", flush=True)
    return row


def capacity(seeds=(0, 1, 2)):
    return [capacity_run(h, load, seed) for seed in seeds for h in (8, 16, 32, 64)
            for load in (0.5, 1, 1.5, 2, 3, 4)]        # load: bits offered per parameter


def capacity_long():
    """Does the network store less past capacity because facts interfere, or because 3,000
    steps are too few? Same runs with three times more steps."""
    return [capacity_run(32, load, 0, steps=s) for load in (2, 3, 4) for s in (3000, 9000)]


# ---------------------------------------------------------------- 2. editing the weights
def editing(h=64, n=1500, n_change=75, n_new=75):
    r = np.random.default_rng(7)
    X = r.standard_normal((n + n_new, D)).astype(np.float32)
    y = r.integers(0, V, n + n_new)
    P = init(h, seed=7)
    fit(P, X[:n], y[:n], steps=3000, lr=1e-2)
    before = accuracy(P, X[:n], y[:n])

    y2 = y.copy()
    changed = r.choice(n, n_change, replace=False)
    y2[changed] = (y[changed] + r.integers(1, V, n_change)) % V      # a different value
    kept = np.setdiff1d(np.arange(n), changed)
    edits = np.concatenate([changed, np.arange(n, n + n_new)])
    out = {"params": n_params(h), "facts": n, "changed": n_change, "new": n_new,
           "accuracy_before": before}

    for name, train_idx, lr, steps in (("edits only", edits, 1e-3, 400),
                                       ("edits only, small steps", edits, 2e-4, 400),
                                       ("rehearse everything", np.arange(n + n_new), 1e-3, 400)):
        Q = [p.copy() for p in P]
        curve = []

        def log(s, Q=Q):
            curve.append(dict(step=s, kept=accuracy(Q, X[kept], y2[kept]),
                              edits=accuracy(Q, X[edits], y2[edits])))
        log(0)
        t = time.time()
        fit(Q, X[train_idx], y2[train_idx], steps=steps, lr=lr, log=log)
        out[name] = dict(curve=curve, examples_seen=int(steps * len(train_idx)),
                         seconds=time.time() - t)
        print(f"editing {name:26s} kept={curve[-1]['kept']:.3f} edits={curve[-1]['edits']:.3f}",
              flush=True)

    # the same edits in an external table: overwrite and append, then read back
    table = {i: int(y[i]) for i in range(n)}
    t = time.perf_counter()
    for i in edits:
        table[int(i)] = int(y2[i])
    dt = time.perf_counter() - t
    out["external"] = dict(kept=float(np.mean([table[int(i)] == y2[i] for i in kept])),
                           edits=float(np.mean([table[int(i)] == y2[i] for i in edits])),
                           seconds=dt)
    return out


def editing_sweep(h=64, n=1500, n_change=75, n_new=75):
    """The same change as editing(), over a grid of learning rates and step counts, so that
    no single choice of settings decides the comparison. Each point is one fine-tuning run."""
    r = np.random.default_rng(7)
    X = r.standard_normal((n + n_new, D)).astype(np.float32)
    y = r.integers(0, V, n + n_new)
    P = init(h, seed=7)
    fit(P, X[:n], y[:n], steps=3000, lr=1e-2)
    y2 = y.copy()
    changed = r.choice(n, n_change, replace=False)
    y2[changed] = (y[changed] + r.integers(1, V, n_change)) % V
    kept = np.setdiff1d(np.arange(n), changed)
    edits = np.concatenate([changed, np.arange(n, n + n_new)])
    rows = []
    for method, idx in (("edits only", edits), ("rehearse everything", np.arange(n + n_new))):
        for lr in (1e-4, 3e-4, 1e-3, 3e-3):
            for steps in (100, 400, 1600):
                Q = [p.copy() for p in P]
                fit(Q, X[idx], y2[idx], steps=steps, lr=lr)
                rows.append(dict(method=method, lr=lr, steps=steps, examples_seen=int(steps * len(idx)),
                                 kept=accuracy(Q, X[kept], y2[kept]), edits=accuracy(Q, X[edits], y2[edits])))
                print(f"sweep {method:20s} lr={lr:.0e} steps={steps:5d} kept={rows[-1]['kept']:.3f} "
                      f"edits={rows[-1]['edits']:.3f}", flush=True)
    return rows


# ---------------------------------------------------------------- 3. external memory
def kmeans(K, c, iters=8, sample=60_000, seed=0):
    r = np.random.default_rng(seed)
    S = K[r.choice(len(K), min(sample, len(K)), replace=False)]
    C = S[r.choice(len(S), c, replace=False)].copy()
    for _ in range(iters):
        a = (S @ C.T).argmax(1)
        for j in range(c):
            m = S[a == j]
            if len(m):
                C[j] = m.mean(0)
        C /= np.linalg.norm(C, axis=1, keepdims=True)
    return C


def lookup(d=256, topics=2000, noise=0.35, queries=300):
    """Keys are unit vectors drawn around topic centres, as sentence embeddings cluster by
    subject. A query is a key plus noise (a paraphrase). Exact search reads every key; an
    inverted-file index (IVF) reads the keys of the few clusters nearest to the query."""
    rows = []
    r = np.random.default_rng(3)
    centres = r.standard_normal((topics, d)).astype(np.float32)
    centres /= np.linalg.norm(centres, axis=1, keepdims=True)
    for n in (10_000, 100_000, 1_000_000, 4_000_000):
        K = np.empty((n, d), np.float32)
        for i in range(0, n, 250_000):          # in chunks, to keep peak memory low
            m = min(250_000, n - i)
            k = (centres[r.integers(0, topics, m)] + 0.6 * r.standard_normal((m, d)) / np.sqrt(d)).astype(np.float32)
            K[i:i + m] = k / np.linalg.norm(k, axis=1, keepdims=True)
        qi = r.integers(0, n, queries)
        Q = (K[qi] + noise * r.standard_normal((queries, d)) / np.sqrt(d)).astype(np.float32)
        Q /= np.linalg.norm(Q, axis=1, keepdims=True)

        t, hit = [], 0
        for q, i in zip(Q, qi):
            s = time.perf_counter()
            j = int((K @ q).argmax())
            t.append(time.perf_counter() - s)
            hit += j == i
        rows.append(dict(method="exact", n=n, recall=hit / queries, ms=1e3 * float(np.median(t)),
                         bytes_read=n * d * 4, bytes_stored=n * d * 4))

        c = int(4 * np.sqrt(n))
        C = kmeans(K, c)
        assign = np.concatenate([(K[i:i + 200_000] @ C.T).argmax(1) for i in range(0, n, 200_000)])
        order = np.argsort(assign, kind="stable")
        starts = np.searchsorted(assign[order], np.arange(c + 1))
        K = K[order]                             # keys of one cluster are now contiguous
        for probe in (4, 16):
            t, hit, read = [], 0, 0
            for q, i in zip(Q, qi):
                s = time.perf_counter()
                cl = np.argpartition(-(C @ q), probe)[:probe]
                idx = np.concatenate([np.arange(starts[k], starts[k + 1]) for k in cl])
                j = order[idx[int((K[idx] @ q).argmax())]]
                t.append(time.perf_counter() - s)
                hit += j == i
                read += (len(idx) + c) * d * 4
            rows.append(dict(method=f"IVF, {probe} clusters", n=n, recall=hit / queries,
                             ms=1e3 * float(np.median(t)), bytes_read=read / queries,
                             bytes_stored=n * d * 4 + c * d * 4))
        for row in rows[-3:]:
            print(f"lookup N={n:8d} {row['method']:18s} recall={row['recall']:.3f} "
                  f"ms={row['ms']:.3f} MB read={row['bytes_read'] / 1e6:.2f}", flush=True)
        del K
    return rows


def lookup_noise(n=1_000_000, d=256, topics=2000, queries=200):
    """Recall against time as questions get harder (more noise, i.e. looser paraphrases).
    Exact search gives the best any method can do on these keys; the index trades recall for time."""
    r = np.random.default_rng(5)
    centres = r.standard_normal((topics, d)).astype(np.float32)
    centres /= np.linalg.norm(centres, axis=1, keepdims=True)
    K = np.empty((n, d), np.float32)
    for i in range(0, n, 250_000):
        m = min(250_000, n - i)
        k = (centres[r.integers(0, topics, m)] + 0.6 * r.standard_normal((m, d)) / np.sqrt(d)).astype(np.float32)
        K[i:i + m] = k / np.linalg.norm(k, axis=1, keepdims=True)
    c = int(4 * np.sqrt(n))
    C = kmeans(K, c)
    assign = np.concatenate([(K[i:i + 200_000] @ C.T).argmax(1) for i in range(0, n, 200_000)])
    order = np.argsort(assign, kind="stable")
    starts = np.searchsorted(assign[order], np.arange(c + 1))
    Ks = K[order]
    rows = []
    for noise in (0.35, 0.7, 1.0, 1.3, 1.6):
        qi = r.integers(0, n, queries)
        Q = (K[qi] + noise * r.standard_normal((queries, d)) / np.sqrt(d)).astype(np.float32)
        Q /= np.linalg.norm(Q, axis=1, keepdims=True)
        t, hit = [], 0
        for q, i in zip(Q, qi):
            s0 = time.perf_counter(); j = int((K @ q).argmax()); t.append(time.perf_counter() - s0)
            hit += j == i
        rows.append(dict(noise=noise, method="exact", probe=c, recall=hit / queries, ms=1e3 * float(np.median(t))))
        for probe in (1, 4, 16, 64):
            t, hit = [], 0
            for q, i in zip(Q, qi):
                s0 = time.perf_counter()
                cl = np.argpartition(-(C @ q), probe)[:probe]
                idx = np.concatenate([np.arange(starts[k], starts[k + 1]) for k in cl])
                j = order[idx[int((Ks[idx] @ q).argmax())]]
                t.append(time.perf_counter() - s0)
                hit += j == i
            rows.append(dict(noise=noise, method="IVF", probe=probe, recall=hit / queries,
                             ms=1e3 * float(np.median(t))))
        for row in rows[-5:]:
            print(f"noise={noise:.2f} {row['method']:5s} probe={row['probe']:5d} recall={row['recall']:.3f} "
                  f"ms={row['ms']:.3f}", flush=True)
    return rows


# ---------------------------------------------------------------- 4. working memory
def working(reps=15):
    """One decoding step of one layer with the shapes of Llama 3.2 1B (hidden 2048, 32 query
    heads, 8 key-value heads of size 64, MLP 8192). Weights are random: only time matters.
    Everything in float32, so weights and cache cost the same per number."""
    r = np.random.default_rng(0)
    hid, nq, nkv, hd, ff = 2048, 32, 8, 64, 8192
    W = {k: (r.standard_normal(s) / np.sqrt(s[0])).astype(np.float32) for k, s in
         dict(q=(hid, nq * hd), k=(hid, nkv * hd), v=(hid, nkv * hd), o=(nq * hd, hid),
              g=(hid, ff), u=(hid, ff), d=(ff, hid)).items()}
    x = r.standard_normal(hid).astype(np.float32)

    def weights_step():
        q = x @ W["q"]; k = x @ W["k"]; v = x @ W["v"]
        h = x + q @ W["o"]
        g = h @ W["g"]; u = h @ W["u"]
        return (g / (1 + np.exp(-g)) * u) @ W["d"], q

    def timeit(f):
        f()
        ts = []
        for _ in range(reps):
            s = time.perf_counter(); f(); ts.append(time.perf_counter() - s)
        return 1e3 * float(np.median(ts))

    w_ms = timeit(weights_step)
    w_numbers = sum(a.size for a in W.values())
    rows = []
    for T in (1024, 2048, 4096, 8192, 16384, 32768, 65536, 131072):
        Kt = r.standard_normal((nkv, hd, T)).astype(np.float32)     # keys, stored transposed
        Vc = r.standard_normal((nkv, T, hd)).astype(np.float32)
        q = r.standard_normal((nkv, nq // nkv, hd)).astype(np.float32)

        def attend():
            s = (q @ Kt) * np.float32(1 / np.sqrt(hd))   # stay in float32
            s -= s.max(-1, keepdims=True)
            p = np.exp(s)
            p /= p.sum(-1, keepdims=True)
            return p @ Vc
        rows.append(dict(context=T, attention_ms=timeit(attend), weights_ms=w_ms,
                         cache_numbers=2 * nkv * hd * T, weight_numbers=int(w_numbers)))
        print(f"working T={T:6d} attention={rows[-1]['attention_ms']:.2f} ms "
              f"weights={w_ms:.2f} ms", flush=True)
        del Kt, Vc
    return rows


if __name__ == "__main__":
    which = sys.argv[1:] or ["working", "lookup", "lookup_noise", "editing", "editing_sweep",
                             "capacity", "capacity_long"]
    try:
        res = json.load(open(OUT))
    except FileNotFoundError:
        res = {}
    for w in which:
        res[w] = globals()[w]()
        json.dump(res, open(OUT, "w"), indent=1, default=float)
