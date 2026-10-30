"""Simulation for "Tools as Neurons".

A toy world of tools, tasks and traces. It tests three claims:

1. When a catalogue grows, choosing tools by their resemblance to the request fails,
   and a layer on top that ranks by resemblance fails with it (Experiment 1).
2. Edges between tools, declared by authors or learned from co-use (a Hebbian rule),
   restore it; a small graph neural network that reads those edges does at least as well
   (Experiments 1 and 2).
3. For workflows never seen before, couplings between clusters of tools, read by the same
   network, find the helpers that resemblance alone confuses (Experiment 3).

Plain NumPy and SciPy. Every number in the paper's Figures 5 to 9 and 12 comes from this file;
results go to results.json. The world is synthetic and deliberately simple: it tests the
shape of an argument, not any product.
"""
import json
import time
import numpy as np
import scipy.sparse as sp

D = 64            # dimensions of the space of meaning
C = 20            # domains (think: servers, or families of servers)
K = 12            # tools a caller may put in front of the model
STEPS = 4         # tools per workflow: one main tool and three helpers
PARTNERS = 2      # each domain leans on two partner domains
P_LOCAL = 0.5     # share of helpers taken from the main tool's own domain
SPREAD = 0.55     # weight of what is specific to each tool
VERBS = 12        # actions shared across domains: search, create, send, convert...
VERB_W = 0.8      # weight of the action in a tool's description
MENTION = 0.3     # how much a request says about the helpers
Q_NOISE = 0.45    # noise in a request
SUB_NOISE = 1.4   # noise in a per-step request for one helper
SAYS_DOMAIN = 0.3 # how much a per-step request says about where the helper lives
SEEDS = (1, 2, 3, 4, 5)


def unit(x):
    return x / np.linalg.norm(x, axis=-1, keepdims=True)


# ---------- the world ----------
def world(n, rng):
    """Tools as points, grouped in domains, with a hidden structure of use."""
    centres = unit(rng.normal(size=(C, D)))
    verbs = unit(rng.normal(size=(VERBS, D)))
    dom = rng.integers(0, C, size=n)
    verb = rng.integers(0, VERBS, size=n)
    own = unit(rng.normal(size=(n, D)))
    emb = unit(centres[dom] + VERB_W * verbs[verb] + SPREAD * own)
    partners = np.array([rng.choice([j for j in range(C) if j != i], PARTNERS, replace=False)
                         for i in range(C)])
    members = [np.flatnonzero(dom == j) for j in range(C)]
    M = sp.csr_matrix((np.ones(n), (np.arange(n), dom)), shape=(n, C))
    return dict(n=n, emb=emb, dom=dom, verb=verb, own=own, centres=centres, verbs=verbs,
                partners=partners, members=members, M=M)


def template(w, rng):
    """A workflow: a main tool, then helpers from its domain or a partner domain.
    Helpers are drawn at random inside a domain, not because they resemble the main tool."""
    a = rng.integers(w["n"])
    tools, d = [a], w["dom"][a]
    while len(tools) < STEPS:
        j = d if rng.random() < P_LOCAL else rng.choice(w["partners"][d])
        t = rng.choice(w["members"][j])
        if t not in tools:
            tools.append(t)
    return np.array(tools)


def query(w, tools, rng):
    """A request names its main goal and barely mentions the helpers."""
    e = w["emb"]
    return unit(e[tools[0]] + MENTION * e[tools[1:]].sum(0) + Q_NOISE * unit(rng.normal(size=D)))


def sub_query(w, h, rng):
    """A per-step request: what the helper must do, little about where it lives."""
    return unit(SAYS_DOMAIN * w["centres"][w["dom"][h]] + VERB_W * w["verbs"][w["verb"][h]]
                + SPREAD * w["own"][h] + SUB_NOISE * unit(rng.normal(size=D)))


# ---------- edges ----------
def hebbian(n, traces):
    """Learned edges: tools that are used in the same task wire together."""
    r, c = [], []
    for t in traces:
        for a in t:
            for b in t:
                if a != b:
                    r.append(a); c.append(b)
    return sp.csr_matrix((np.ones(len(r)), (r, c)), shape=(n, n))


def coupling(w, traces):
    """Learned coupling between domains: how often a task led by domain a used domain b."""
    m = np.zeros((C, C))
    for t in traces:
        ds = w["dom"][t]
        for b in ds[1:]:
            m[ds[0], b] += 1
    np.fill_diagonal(m, 0)
    return m / np.maximum(m.sum(1, keepdims=True), 1)


def sym_norm(A):
    A = A.copy().astype(float)
    A.data = np.log1p(A.data)
    d = np.asarray(A.sum(1)).ravel()
    s = sp.diags(1 / np.sqrt(np.maximum(d, 1e-9)))
    return (s @ A @ s).tocsr()


# ---------- baselines ----------
def topk(scores, k=K):
    idx = np.argpartition(-scores, k)[:k]
    return idx[np.argsort(-scores[idx])]


def flat(w, q):
    return topk(w["emb"] @ q)


def hierarchy(w, q, top=2):
    cent = unit(np.array([w["emb"][m].mean(0) for m in w["members"]]))
    ds = np.argsort(-(cent @ q))[:top]
    cand = np.concatenate([w["members"][d] for d in ds])
    return cand[np.argsort(-(w["emb"][cand] @ q))[:K]]


def graph_walk(w, q, A, seeds=3):
    """Start from the closest tools, then follow their edges, weighted by how close each seed is."""
    s = w["emb"] @ q
    order = np.argsort(-s)
    chosen = list(order[:seeds])
    score = np.zeros(w["n"])
    for a in chosen:
        row = A.getrow(a)
        score[row.indices] += row.data * max(s[a], 0)
    score[chosen] = -1
    nb = [b for b in np.argsort(-score - 1e-6 * s) if score[b] > 0][:K - seeds]
    chosen += nb
    for b in order:
        if len(chosen) >= K:
            break
        if b not in chosen:
            chosen.append(b)
    return np.array(chosen[:K])


# ---------- the graph neural network ----------
SEEDS_ACTIVE = 3   # tools that fire first: a k-winners-take-all activation


def activate(S, k=SEEDS_ACTIVE):
    """First activation for a batch of requests: only the k closest tools fire,
    each in proportion to its resemblance to the request."""
    X = np.zeros_like(S)
    idx = np.argpartition(-S, k, axis=1)[:, :k]
    rows = np.arange(len(S))[:, None]
    X[rows, idx] = np.maximum(S[rows, idx], 0)
    return X / np.maximum(X.sum(1, keepdims=True), 1e-9)


def features(w, S, X0, A_hat, Cp):
    """Messages passed over two graphs, for a batch (B requests x N tools).

    S   resemblance of each tool to the request (cosine)
    X0  starting activation (the k closest tools, or the tools already chosen)
    A_hat  normalised tool-to-tool edges;  Cp  coupling between domains
    Returns an array (B, N, 9) of node features for a shared readout."""
    M = w["M"]
    def hop(X):
        Y = (A_hat @ X.T).T
        return Y / np.maximum(Y.max(1, keepdims=True), 1e-9)
    AX = hop(X0)                               # one hop over tool edges
    AAX = hop(AX)                              # two hops
    own = (M @ (M.T @ X0.T)).T                 # activation of the tool's own domain
    cpl = (M @ (Cp.T @ (M.T @ X0.T))).T        # activation arriving from coupled domains
    own = own / np.maximum(own.max(1, keepdims=True), 1e-9)
    cpl = cpl / np.maximum(cpl.max(1, keepdims=True), 1e-9)
    Sp = np.maximum(S, 0)
    # products: a neighbour counts only if it also matches the request, which makes the
    # effective edges depend on the task (a simple form of attention)
    return np.stack([S, AX, AAX, own, cpl, Sp * AX, Sp * AAX, Sp * own, Sp * cpl], -1)


class Readout:
    """The learned part of the network: one linear readout, shared by every node, fitted by
    weighted logistic regression (Newton's method), as in SGC and SIGN, where messages are
    passed first and only the readout is learned. Linear on purpose: it extrapolates
    sensibly, and its weights can be read."""

    def __init__(self, f):
        self.w = np.zeros(f)
        self.b = 0.0

    def __call__(self, F):
        return F @ self.w + self.b

    def fit(self, F, y, pos_w=8.0, l2=1e-2, iters=25):
        X = np.c_[F, np.ones(len(F))]
        sw = np.where(y > 0, pos_w, 1.0)
        th = np.zeros(X.shape[1])
        R = l2 * np.eye(X.shape[1]); R[-1, -1] = 0
        for _ in range(iters):
            p = 1 / (1 + np.exp(-np.clip(X @ th, -30, 30)))
            g = X.T @ (sw * (p - y)) + R @ th
            H = (X * (sw * p * (1 - p))[:, None]).T @ X + R
            th -= np.linalg.solve(H, g)
        self.w, self.b = th[:-1], th[-1]
        return self


def sample_rows(F, pos, rng, hard, n_neg=60, task=None, drop=0.5):
    """Positives, plus hard negatives (high resemblance) and random negatives.
    With probability `drop`, the edges between the task's own tools are hidden (DropEdge),
    so the readout also learns what to do when a workflow has never been seen."""
    n = F.shape[0]
    if task is not None and rng.random() < drop:
        F = F.copy()
        F[task, 1:3] = 0
        F[task, 5:7] = 0
    # hard negatives: the closest tools by resemblance, and the closest by edges
    by_edge = np.argsort(-(F[:, 1] + F[:, 2]))[:20]
    neg_h = [i for i in list(hard[:25]) + list(by_edge) if i not in set(pos)]
    neg_r = rng.integers(0, n, n_neg // 2)
    idx = np.concatenate([pos, neg_h, neg_r]).astype(int)
    y = np.isin(idx, pos).astype(float)
    return F[idx], y


def train_gnn(w, tasks, A_hat, Cp, rng, mode, epochs=2, batch=64):
    """mode 'one': one request, choose K tools.  mode 'step': choose the next helper,
    given the tools already chosen and a short request for that step."""
    e = w["emb"]
    allF, ally = [], []
    for _ in range(epochs):
        order = rng.permutation(len(tasks))
        for b0 in range(0, len(order), batch):
            Fs, ys = [], []
            ids = order[b0:b0 + batch]
            if mode == "one":
                Q = np.array([query(w, tasks[i], rng) for i in ids])
                S = Q @ e.T
                F = features(w, S, activate(S), A_hat, Cp)
                for r, i in enumerate(ids):
                    f, y = sample_rows(F[r], tasks[i], rng, np.argsort(-S[r])[:40])
                    Fs.append(f); ys.append(y)
            else:
                rows = []
                for i in ids:
                    t = tasks[i]
                    j = rng.integers(1, STEPS)
                    rows.append((t, j, sub_query(w, t[j], rng)))
                S = np.array([r[2] for r in rows]) @ e.T
                X0 = np.zeros_like(S)
                for r, (t, j, _) in enumerate(rows):
                    X0[r, t[:j]] = 1.0 / j
                F = features(w, S, X0, A_hat, Cp)
                for r, (t, j, _) in enumerate(rows):
                    f, y = sample_rows(F[r], np.array([t[j]]), rng, np.argsort(-S[r])[:40], task=t[j:])
                    Fs.append(f); ys.append(y)
            allF += Fs; ally += ys
    return Readout(allF[0].shape[1]).fit(np.concatenate(allF), np.concatenate(ally))


# ---------- one experiment ----------
def run(n, n_traces, seed, n_test=300, gnn=True):
    rng = np.random.default_rng(seed)
    w = world(n, rng)
    n_tpl = max(n // 2, 50)
    tpls = [template(w, rng) for _ in range(n_tpl)]
    pop = 1 / np.arange(1, n_tpl + 1)
    pop /= pop.sum()
    hist = [tpls[i] for i in rng.choice(n_tpl, n_traces, p=pop)] if n_traces else []
    A_dec = hebbian(n, tpls)                    # authors declare every edge they know
    A_learn = hebbian(n, hist)                  # edges grown from use
    A_hat = sym_norm(A_learn) if n_traces else sp.csr_matrix((n, n))
    Cp = coupling(w, hist) if n_traces else np.zeros((C, C))
    out = {}
    test = [tpls[i] for i in rng.choice(n_tpl, n_test, p=pop)]
    novel = [template(w, rng) for _ in range(n_test)]
    Q = np.array([query(w, t, rng) for t in test])
    for name, f in (("flat", lambda q: flat(w, q)), ("hierarchy", lambda q: hierarchy(w, q)),
                    ("declared", lambda q: graph_walk(w, q, A_dec)),
                    ("learned", lambda q: graph_walk(w, q, A_learn))):
        out[name] = float(np.mean([np.isin(t, f(q)).all() for t, q in zip(test, Q)]))
    if gnn and n_traces:
        train = hist[:3000]
        train = train * max(1, 600 // len(train))   # small histories: several passes
        net = train_gnn(w, train, A_hat, Cp, rng, "one")
        S = Q @ w["emb"].T
        Z = net(features(w, S, activate(S), A_hat, Cp))
        picks = [topk(z) for z in Z]
        out["gnn"] = float(np.mean([np.isin(t, p).all() for t, p in zip(test, picks)]))
        # activation patterns, for the figure: which tools fire for which task
        if n == 1000 and seed == SEEDS[0]:
            out["_patterns"] = dict(picks=[p.tolist() for p in picks[:40]],
                                    tasks=[t.tolist() for t in test[:40]],
                                    dom=w["dom"].tolist())
            sets = [set(p) for p in picks]
            jac = [len(sets[i] & sets[j]) / len(sets[i] | sets[j])
                   for i in range(len(sets)) for j in range(i + 1, min(i + 30, len(sets)))]
            out["_overlap"] = float(np.mean(jac))
        # step by step: for workflows already seen, and for workflows never seen
        step_net = train_gnn(w, train, A_hat, Cp, rng, "step")
        e = w["emb"]

        def one_step(t, j, s, d0):
            """Scores of four routers for step j of workflow t, given request s."""
            near = np.concatenate([w["members"][d] for d in [d0, *np.argsort(-Cp[d0])[:2]]])
            hard = np.full(n, -np.inf); hard[near] = s[near]
            X0 = np.zeros((1, n)); X0[0, t[:j]] = 1.0 / j
            F = features(w, s[None], X0, A_hat, Cp)[0]
            # novelty gate: how well the best graph neighbour of the chosen tools matches
            match = float((np.maximum(s, 0) * (F[:, 1] > 0.05)).max())
            return s, hard, step_net(F), match

        def evaluate(tasks, theta):
            ok = {k: [] for k in ("flat", "hard", "gnn", "gated")}
            for t in tasks:
                q = query(w, t, rng)
                d0 = w["dom"][np.argmax(e @ q)]
                r = dict.fromkeys(ok, True)
                for j in range(1, STEPS):
                    h = t[j]
                    s, hard, z, match = one_step(t, j, e @ sub_query(w, h, rng), d0)
                    r["flat"] &= h in topk(s, 3)
                    r["hard"] &= h in topk(hard, 3)
                    r["gnn"] &= h in topk(z, 3)
                    r["gated"] &= h in topk(z if match >= theta else hard, 3)
                for k in ok:
                    ok[k].append(r[k])
            return {k: float(np.mean(v)) for k, v in ok.items()}

        # the gate's threshold is set on a small validation set: half seen, half new
        val = [hist[i] for i in rng.integers(len(hist), size=60)] + [template(w, rng) for _ in range(60)]
        thetas = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
        theta = max(thetas, key=lambda th: evaluate(val, th)["gated"])
        out["theta"] = theta
        for label, tasks in (("seen", test), ("novel", novel)):
            for k, v in evaluate(tasks, theta).items():
                out[f"{label}_step_{k}"] = v
        out["_w_step"] = step_net.w.tolist()
        out["_w_one"] = net.w.tolist()
    return out


def mean_sd(runs, key):
    v = [r[key] for r in runs if key in r]
    return [float(np.mean(v)), float(np.std(v))]


if __name__ == "__main__":
    t0 = time.time()
    res = {"params": dict(D=D, C=C, K=K, STEPS=STEPS, PARTNERS=PARTNERS, P_LOCAL=P_LOCAL,
                          SPREAD=SPREAD, VERBS=VERBS, VERB_W=VERB_W, MENTION=MENTION,
                          Q_NOISE=Q_NOISE, SUB_NOISE=SUB_NOISE, SAYS_DOMAIN=SAYS_DOMAIN,
                          SEEDS_ACTIVE=SEEDS_ACTIVE, seeds=list(SEEDS))}
    sizes = [100, 300, 1000, 3000, 10000]
    scale = {}
    for n in sizes:
        runs = [run(n, 5 * max(n // 2, 50), s) for s in SEEDS]
        keys = [k for k in runs[0] if not k.startswith("_")]
        scale[n] = {k: mean_sd(runs, k) for k in keys}
        if n == 1000:
            res["weights"] = dict(one=runs[0]["_w_one"], step=runs[0]["_w_step"])
        for r in runs:
            if "_patterns" in r:
                res["patterns"] = r["_patterns"]
                res["overlap"] = r["_overlap"]
        print(n, {k: round(v[0], 3) for k, v in scale[n].items()}, f"{time.time() - t0:.0f}s", flush=True)
    res["scale"] = scale
    learn = {}
    for tr in [0, 100, 300, 1000, 3000, 10000]:
        runs = [run(1000, tr, s, gnn=tr > 0, n_test=300) for s in SEEDS]
        learn[tr] = {k: mean_sd(runs, k)[0] for k in ("flat", "learned", "declared", "gnn") if k in runs[0]}
        print("traces", tr, learn[tr], flush=True)
    res["learning"] = learn
    # pairs of tools used together: resemblance against random pairs (Figure 3)
    rng = np.random.default_rng(7)
    w = world(1000, rng)
    tpls = [template(w, rng) for _ in range(500)]
    pairs_same, pairs_cross = [], []
    for t in tpls:
        for b in t[1:]:
            (pairs_same if w["dom"][b] == w["dom"][t[0]] else pairs_cross).append(
                float(w["emb"][t[0]] @ w["emb"][b]))
    ra, rb = rng.integers(1000, size=6000), rng.integers(1000, size=6000)
    res["pairs"] = dict(same=pairs_same, cross=pairs_cross,
                        rand=[float(x) for x in (w["emb"][ra] * w["emb"][rb]).sum(1)])
    hist = [tpls[i] for i in rng.integers(500, size=2500)]
    res["coupling"] = coupling(w, hist).tolist()
    res["tokens_per_tool"] = 350
    with open("results.json", "w") as f:
        json.dump(res, f)
    print(f"done in {time.time() - t0:.0f}s")
