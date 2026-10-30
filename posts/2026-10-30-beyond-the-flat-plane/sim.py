"""Simulation for "Beyond the Flat Plane".

A toy world of tools, tasks and traces, to test one claim: when a catalogue grows,
finding the tools a task needs by their resemblance to the request stops working,
and edges between tools (declared or learned from use) keep working.

Plain NumPy. Every number in the essay's Figures 4 to 7 comes from this file;
results go to results.json. The world is synthetic and deliberately simple: it
tests the shape of an argument, not any product.
"""
import json
import numpy as np

D = 64            # dimensions of the space of meaning
C = 20            # domains (think: servers, or families of servers)
K = 12            # tools a caller may put in front of the model
STEPS = 4         # tools per workflow: one main tool and three helpers
PARTNERS = 2      # each domain leans on two partner domains
P_LOCAL = 0.5     # share of helpers taken from the main tool's own domain
SPREAD = 0.55     # how far tools sit from their domain's centre
VERBS = 12        # actions shared across domains: search, create, send, convert...
VERB_W = 0.8      # weight of the action in a tool's description
SEEDS = (1, 2, 3, 4, 5)


def unit(x):
    return x / np.linalg.norm(x, axis=-1, keepdims=True)


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
    return dict(emb=emb, dom=dom, partners=partners, members=members, centres=centres,
                verbs=verbs, verb=verb, own=own)


def template(w, rng):
    """A workflow: a main tool, then helpers from its domain or a partner domain.
    Helpers are drawn at random inside a domain, not because they resemble the main tool."""
    a = rng.integers(len(w["dom"]))
    tools, d = [a], w["dom"][a]
    while len(tools) < STEPS:
        j = d if rng.random() < P_LOCAL else rng.choice(w["partners"][d])
        t = rng.choice(w["members"][j])
        if t not in tools:
            tools.append(t)
    return np.array(tools)


def query(w, tools, rng, mention=0.3, noise=0.45):
    """A request names its main goal and barely mentions the helpers."""
    e = w["emb"]
    q = e[tools[0]] + mention * e[tools[1:]].sum(0) + noise * unit(rng.normal(size=D))
    return unit(q)


def traces_to_graph(n, traces):
    """Learned edges: how often two tools were used in the same task."""
    rows, cols = [], []
    for t in traces:
        for a in t:
            for b in t:
                if a != b:
                    rows.append(a); cols.append(b)
    g = {}
    for a, b in zip(rows, cols):
        g.setdefault(a, {}).setdefault(b, 0)
        g[a][b] += 1
    return g


def domain_coupling(w, traces):
    """Learned couplings between domains: how often a task led by a tool of domain a
    also used a tool of domain b. Normalised by row."""
    m = np.zeros((C, C))
    for t in traces:
        ds = w["dom"][t]
        for b in ds[1:]:
            m[ds[0], b] += 1
    np.fill_diagonal(m, 0)
    return m / np.maximum(m.sum(1, keepdims=True), 1)


# ---------- four ways to choose K tools ----------
def flat(w, q):
    return np.argsort(-(w["emb"] @ q))[:K]


def hierarchy(w, q, top=2):
    """A layer on top: pick the closest domains, then the closest tools inside them."""
    cent = unit(np.array([w["emb"][m].mean(0) for m in w["members"]]))
    ds = np.argsort(-(cent @ q))[:top]
    cand = np.concatenate([w["members"][d] for d in ds])
    return cand[np.argsort(-(w["emb"][cand] @ q))[:K]]


def local_graph(w, q, g, seeds=3):
    """Edges in the protocol: start from the closest tools, then follow their edges."""
    s = w["emb"] @ q
    order = np.argsort(-s)
    chosen = list(order[:seeds])
    score = {}
    for a in chosen:
        for b, c in g.get(a, {}).items():
            score[b] = score.get(b, 0) + c * max(s[a], 0)
    for b, _ in sorted(score.items(), key=lambda kv: (-kv[1], -s[kv[0]])):
        if len(chosen) >= K:
            break
        if b not in chosen:
            chosen.append(b)
    for b in order:
        if len(chosen) >= K:
            break
        if b not in chosen:
            chosen.append(b)
    return np.array(chosen)


def sub_queries(w, q, tools, coup, rng, noise=1.4, top=3, coupled=2, says_domain=0.3):
    """A workflow nobody has run before. The agent finds the main tool, then asks
    again for each helper with a short request of its own. Searched over the whole
    catalogue, or only over the main tool's domain and the domains most coupled to it.
    A helper's request says what it must do, and says little about where it lives."""
    d0 = w["dom"][np.argmax(w["emb"] @ q)]
    near = np.concatenate([w["members"][d] for d in [d0, *np.argsort(-coup[d0])[:coupled]]])
    ok_flat = ok_coup = True
    for h in tools[1:]:
        sq = unit(says_domain * w["centres"][w["dom"][h]] + VERB_W * w["verbs"][w["verb"][h]]
                  + SPREAD * w["own"][h] + noise * unit(rng.normal(size=D)))
        ok_flat &= h in np.argsort(-(w["emb"] @ sq))[:top]
        ok_coup &= h in near[np.argsort(-(w["emb"][near] @ sq))[:top]]
    return float(ok_flat), float(ok_coup), len(near)


def complete(chosen, tools):
    return float(np.isin(tools, chosen).all())


def run(n, n_traces, rng, n_test=400):
    w = world(n, rng)
    n_tpl = max(n // 2, 50)
    tpls = [template(w, rng) for _ in range(n_tpl)]
    pop = 1 / np.arange(1, n_tpl + 1)          # some workflows are far more common
    pop /= pop.sum()
    hist = [tpls[i] for i in rng.choice(n_tpl, n_traces, p=pop)]
    declared = traces_to_graph(n, tpls)         # authors declare every edge they know
    learned = traces_to_graph(n, hist)
    coup = domain_coupling(w, hist)
    out = {k: [] for k in ("flat", "hierarchy", "declared", "learned", "learned_novel",
                           "subq_flat_novel", "subq_coupled_novel", "searched")}
    for _ in range(n_test):
        t = tpls[rng.choice(n_tpl, p=pop)]
        q = query(w, t, rng)
        out["flat"].append(complete(flat(w, q), t))
        out["hierarchy"].append(complete(hierarchy(w, q), t))
        out["declared"].append(complete(local_graph(w, q, declared), t))
        out["learned"].append(complete(local_graph(w, q, learned), t))
        nt = template(w, rng)                   # a workflow nobody has run before
        nq = query(w, nt, rng)
        out["learned_novel"].append(complete(local_graph(w, nq, learned), nt))
        a, b, m = sub_queries(w, nq, nt, coup, rng)
        out["subq_flat_novel"].append(a)
        out["subq_coupled_novel"].append(b)
        out["searched"].append(m / n)
    return {k: float(np.mean(v)) for k, v in out.items()}, w, hist, coup


def pairs(w, hist, rng, m=6000):
    """Resemblance against co-use for pairs of tools that were used together, and for random pairs."""
    g = traces_to_graph(len(w["dom"]), hist)
    used = [(a, b, c) for a, nb in g.items() for b, c in nb.items() if a < b]
    used = [used[i] for i in rng.choice(len(used), min(m, len(used)), replace=False)]
    e = w["emb"]
    sim_used = [float(e[a] @ e[b]) for a, b, _ in used]
    cnt_used = [int(c) for _, _, c in used]
    same = [bool(w["dom"][a] == w["dom"][b]) for a, b, _ in used]
    ra, rb = rng.integers(len(e), size=m), rng.integers(len(e), size=m)
    sim_rand = [float(x) for x in (e[ra] * e[rb]).sum(1)]
    # rank of each helper among all tools, by resemblance to the main tool
    return dict(sim_used=sim_used, cnt_used=cnt_used, same_domain=same, sim_rand=sim_rand)


if __name__ == "__main__":
    res = {"params": dict(D=D, C=C, K=K, STEPS=STEPS, PARTNERS=PARTNERS, P_LOCAL=P_LOCAL,
                          SPREAD=SPREAD, seeds=list(SEEDS))}
    sizes = [100, 300, 1000, 3000, 10000]
    scale = {}
    for n in sizes:
        runs = [run(n, 5 * max(n // 2, 50), np.random.default_rng(s))[0] for s in SEEDS]
        scale[n] = {k: [float(np.mean([r[k] for r in runs])), float(np.std([r[k] for r in runs]))]
                    for k in runs[0]}
        print(n, {k: round(v[0], 3) for k, v in scale[n].items()})
    res["scale"] = scale
    n = 1000
    learn = {}
    for tr in [0, 100, 300, 1000, 3000, 10000, 30000]:
        runs = [run(n, tr, np.random.default_rng(s))[0] for s in SEEDS]
        learn[tr] = {k: float(np.mean([r[k] for r in runs])) for k in ("flat", "learned", "declared")}
        print("traces", tr, learn[tr])
    res["learning"] = learn
    rng = np.random.default_rng(7)
    _, w, hist, coup = run(1000, 2500, rng, n_test=1)
    res["pairs"] = pairs(w, hist, rng)
    # order domains so that partners sit close, for the coupling map
    res["coupling"] = coup.tolist()
    res["partners"] = w["partners"].tolist()
    # context cost of listing every tool, at an assumed 350 tokens per full definition
    res["tokens_per_tool"] = 350
    with open("results.json", "w") as f:
        json.dump(res, f)
