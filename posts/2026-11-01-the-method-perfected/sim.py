"""Toy simulation for "The Method, Perfected".

A field holds two pools of ideas.

  ordinary   N_ORD ideas. Consensus prior pi ~ Beta(2, 6). The consensus is calibrated:
             each idea is true with probability pi. Value 1 if true; it takes T_ORD
             periods of work to reach a decisive test.
  frontier   N_FRO ideas far from the consensus. Prior pi ~ U(0.01, 0.06). Value V_FRO if
             true; T_FRO periods to a decisive test (the "dark period": no useful evidence
             before it). A share UNDERRATED of them are ones the consensus is wrong about:
             they are true with probability P_UNDER. The rest ("cranks") are true with
             probability pi, as the consensus says.

Every idea carries a taste signal a = delta * truth + N(0, 1): a weak, private sense that
the idea is right (Poincare's "harmony"), independent of the consensus prior. delta = 0 is
faith without taste.

Strategies share one budget B, in person-periods:
  method     ranks every idea by pi * V / T (expected value per period under the consensus)
             and works down the list. With AI, a period costs C_AI_ORD on ordinary ideas and
             C_AI_FRO on frontier ideas.
  conviction ranks frontier ideas by taste a and carries each one through its dark period.
  mixed      AI method on (1 - s) of the budget, conviction (AI-assisted) on s.

A last experiment divides the AI cost per period by a factor k, for the base field and for a field
ten times larger, to find where testing becomes cheap enough to try every idea.

All parameters are invented to show a mechanism, not measured. Writes results.json.
Run: python sim.py   (about two minutes)
"""
import json
import numpy as np

N_ORD, N_FRO = 5000, 400
T_ORD, T_FRO, V_FRO = 2, 8, 20
UNDERRATED, P_UNDER = 0.25, 0.30
B = 1000.0
C_AI_ORD, C_AI_FRO = 0.25, 0.5
SEEDS = 300
DELTAS = (0.0, 0.5, 1.0)
SHARES = (0.0, 0.05, 0.1, 0.2, 0.3, 0.5)
SENS_P_UNDER = (0.10, 0.15, 0.30)
# Cheap-testing limit: divide the AI cost per period by k, for the base pool and a pool ten times larger.
COST_FACTORS = (1, 2, 5, 10, 20, 50)
POOL_MULTS = (1, 10)
LIMIT_SEEDS = 100


def field(rng, delta, p_under=None):
    p_under = P_UNDER if p_under is None else p_under
    pi = np.concatenate([rng.beta(2, 6, N_ORD), rng.uniform(0.01, 0.06, N_FRO)])
    fro = np.r_[np.zeros(N_ORD, bool), np.ones(N_FRO, bool)]
    under = np.zeros_like(fro)
    under[N_ORD:] = rng.random(N_FRO) < UNDERRATED
    p_true = np.where(under, p_under, pi)
    truth = rng.random(pi.size) < p_true
    taste = delta * truth + rng.normal(0, 1, pi.size)
    V = np.where(fro, V_FRO, 1.0)
    T = np.where(fro, T_FRO, T_ORD)
    return dict(pi=pi, fro=fro, under=under, truth=truth, taste=taste, V=V, T=T)


def run(f, order, budget, c_ord, c_fro, used):
    """Work down `order` until the budget runs out. Returns (ordinary found, breakthroughs)."""
    ordn = brk = 0
    for i in order:
        if used[i]:
            continue
        cost = f["T"][i] * (c_fro if f["fro"][i] else c_ord)
        if cost > budget:
            break
        budget -= cost
        used[i] = True
        if f["truth"][i]:
            if f["fro"][i]:
                brk += 1
            else:
                ordn += 1
    return ordn, brk


def strategy(f, name, s=0.0):
    used = np.zeros(f["pi"].size, bool)
    by_ev = np.argsort(-(f["pi"] * f["V"] / f["T"]))
    fro_idx = np.where(f["fro"])[0]
    by_taste = fro_idx[np.argsort(-f["taste"][fro_idx])]
    if name == "method":
        return run(f, by_ev, B, 1.0, 1.0, used)
    if name == "method_ai":
        return run(f, by_ev, B, C_AI_ORD, C_AI_FRO, used)
    if name == "conviction":
        return run(f, by_taste, B, 1.0, 1.0, used)
    if name == "mixed":
        o2, b2 = run(f, by_taste, s * B, C_AI_ORD, C_AI_FRO, used)
        o1, b1 = run(f, by_ev, (1 - s) * B, C_AI_ORD, C_AI_FRO, used)
        return o1 + o2, b1 + b2
    raise ValueError(name)


def summarise(xs):
    xs = np.asarray(xs, float)
    return dict(mean=float(xs.mean()), p05=float(np.percentile(xs, 5)), p95=float(np.percentile(xs, 95)))


def main():
    global N_ORD, N_FRO, C_AI_ORD, C_AI_FRO
    out = dict(params=dict(N_ORD=N_ORD, N_FRO=N_FRO, T_ORD=T_ORD, T_FRO=T_FRO, V_FRO=V_FRO,
                           UNDERRATED=UNDERRATED, P_UNDER=P_UNDER, B=B, C_AI_ORD=C_AI_ORD,
                           C_AI_FRO=C_AI_FRO, SEEDS=SEEDS),
               table={}, sweep={})
    # Table: four strategies at delta = 0.5, mixed at s = 0.2
    rows = [("method", 0.0), ("method_ai", 0.0), ("conviction", 0.0), ("mixed", 0.2)]
    for name, s in rows:
        o, b = [], []
        for seed in range(SEEDS):
            f = field(np.random.default_rng(seed), 0.5)
            x, y = strategy(f, name, s)
            o.append(x); b.append(y)
        out["table"][name] = dict(ordinary=summarise(o), breakthroughs=summarise(b),
                                  p_none=float(np.mean(np.asarray(b) == 0)))
    # Sweep: share s of the budget given to conviction, for three strengths of taste
    for d in DELTAS:
        res = []
        for s in SHARES:
            o, b = [], []
            for seed in range(SEEDS):
                f = field(np.random.default_rng(1000 + seed), d)
                x, y = strategy(f, "mixed", s)
                o.append(x); b.append(y)
            res.append(dict(share=s, ordinary=summarise(o), breakthroughs=summarise(b)))
        out["sweep"][str(d)] = res
    # Sensitivity: how much rides on the true chance of the underrated ideas (P_UNDER)?
    out["sensitivity"] = {}
    for pu in SENS_P_UNDER:
        row = {}
        for name, s in rows:
            b = []
            for seed in range(SEEDS):
                f = field(np.random.default_rng(seed), 0.5, pu)
                b.append(strategy(f, name, s)[1])
            row[name] = summarise(b)
        out["sensitivity"][str(pu)] = row
    # Cheap-testing limit: when testing is cheap enough to try every idea, conviction adds nothing.
    base = (N_ORD, N_FRO, C_AI_ORD, C_AI_FRO)
    out["limit"] = []
    for m in POOL_MULTS:
        for k in COST_FACTORS:
            N_ORD, N_FRO = base[0] * m, base[1] * m
            C_AI_ORD, C_AI_FRO = base[2] / k, base[3] / k
            row = dict(pool=m, factor=k)
            for name, s in (("method_ai", 0.0), ("mixed", 0.2)):
                b = [strategy(field(np.random.default_rng(seed), 0.5), name, s)[1] for seed in range(LIMIT_SEEDS)]
                row[name] = summarise(b)
            out["limit"].append(row)
    N_ORD, N_FRO, C_AI_ORD, C_AI_FRO = base
    with open("results.json", "w") as fh:
        json.dump(out, fh, indent=1)
    for k, v in out["table"].items():
        print(f"{k:11s} ordinary {v['ordinary']['mean']:7.1f}  breakthroughs {v['breakthroughs']['mean']:5.2f}"
              f" [{v['breakthroughs']['p05']:.0f}-{v['breakthroughs']['p95']:.0f}]  P(none) {v['p_none']:.2f}")
    for d, res in out["sweep"].items():
        print("delta", d, [(r["share"], round(r["ordinary"]["mean"]), round(r["breakthroughs"]["mean"], 1)) for r in res])
    for pu, row in out["sensitivity"].items():
        print("P_UNDER", pu, {k: round(v["mean"], 1) for k, v in row.items()})
    for r in out["limit"]:
        print("pool x%d cost/%d" % (r["pool"], r["factor"]), round(r["method_ai"]["mean"], 1), round(r["mixed"]["mean"], 1))


if __name__ == "__main__":
    main()
