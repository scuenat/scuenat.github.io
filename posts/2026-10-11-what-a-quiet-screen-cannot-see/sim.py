"""Simulated copilot telemetry with a problem the shape card does not track.

Same setting as "Show What Changed": five agents, four languages, request length,
shared server swings, weekly shape cards. New here: every request also records
its device (web, desktop, iOS app), region and plan. The shape card ignores them.

Hidden problem: from day 51 (week 8), requests from the iOS app are 15% slower,
for every agent and language.
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(7)

DAYS = 84
AGENTS = ["search", "code", "summarise", "translate", "email"]
LANGS = ["English", "German", "French", "Italian"]
DEVICES = {"web": 0.50, "desktop": 0.35, "iOS": 0.15}
REGIONS = {"Europe": 0.6, "Americas": 0.3, "Other": 0.1}
PLANS = {"free": 0.55, "pro": 0.45}
LEN_BINS = np.array([40, 120, 400, 1200])           # typical request length (tokens)
LEN_SHARE = np.array([0.35, 0.35, 0.2, 0.1])
AGENT_SHARE = np.array([0.3, 0.25, 0.2, 0.15, 0.1])
LANG_SHARE = np.array([0.45, 0.3, 0.15, 0.1])

PROBLEM_DAY = 51
PROBLEM_FACTOR = 1.15
SIGMA = 0.5                                        # per-request spread of log latency

agent_base = dict(zip(AGENTS, np.log([0.9, 2.2, 1.6, 1.2, 1.0])))
lang_base = dict(zip(LANGS, [0.0, 0.03, 0.02, 0.04]))
device_base = {"web": 0.0, "desktop": -0.02, "iOS": 0.03}

server = rng.normal(0, 0.06, DAYS)                 # shared server swings, unknown to the model


def simulate():
    rows = []
    for d in range(DAYS):
        weekday = d % 7 < 5
        total = 30000 * (1.003 ** d) * (1.0 if weekday else 0.25)
        for ai, a in enumerate(AGENTS):
            for li, l in enumerate(LANGS):
                for dev, sd in DEVICES.items():
                    for reg, sr in REGIONS.items():
                        for pl, sp in PLANS.items():
                            for bi, L in enumerate(LEN_BINS):
                                mu = total * AGENT_SHARE[ai] * LANG_SHARE[li] * sd * sr * sp * LEN_SHARE[bi]
                                n = rng.poisson(mu)
                                if n == 0:
                                    continue
                                m = (agent_base[a] + lang_base[l] + device_base[dev]
                                     + 0.5 * np.log(L / 100) + server[d])
                                if dev == "iOS" and d >= PROBLEM_DAY:
                                    m += np.log(PROBLEM_FACTOR)
                                # small misfit the shape never explains (keeps it honest)
                                m += rng.normal(0, 0.01)
                                mean_log = m + rng.normal(0, SIGMA / np.sqrt(n))
                                rows.append((d, a, l, dev, reg, pl, L, n, mean_log))
    return pd.DataFrame(rows, columns=["day", "agent", "lang", "device", "region",
                                       "plan", "length", "n", "mean_log"])


def fit_week(w):
    """Weighted least squares: day effects + agent x language speed + length rule.
    Device, region and plan are deliberately not in the shape."""
    days = sorted(w.day.unique())
    cells = [(a, l) for a in AGENTS for l in LANGS]
    X = np.zeros((len(w), len(days) - 1 + len(cells) + 1))
    di = {d: i for i, d in enumerate(days)}
    ci = {c: i for i, c in enumerate(cells)}
    for r, (d, a, l, L) in enumerate(zip(w.day, w.agent, w.lang, w.length)):
        if di[d] > 0:
            X[r, di[d] - 1] = 1
        X[r, len(days) - 1 + ci[(a, l)]] = 1
        X[r, -1] = np.log(L / 100)
    y = w.mean_log.values
    wt = w.n.values
    sw = np.sqrt(wt)
    beta, *_ = np.linalg.lstsq(X * sw[:, None], y * sw, rcond=None)
    resid = y - X @ beta
    speeds = beta[len(days) - 1:-1]
    # Shared server swings are removed: speeds are relative to the traffic-weighted
    # average, as in the first essay. A slowdown that hits everyone equally looks
    # exactly like a server swing.
    share = w.groupby(["agent", "lang"]).n.sum().reindex(cells).values
    speeds = speeds - np.average(speeds, weights=share)
    day_fx = np.r_[0.0, beta[:len(days) - 1]]
    return speeds, beta[-1], resid, day_fx


def main():
    df = simulate()
    df["week"] = df.day // 7 + 1
    print("requests:", df.n.sum(), "cells:", len(df))

    cards, rules, out = [], [], []
    for wk in range(1, 13):
        w = df[df.week == wk].copy()
        speeds, b, resid, day_fx = fit_week(w)
        cards.append(speeds)
        rules.append(b)
        w["resid"] = resid
        w["z"] = resid * np.sqrt(w.n) / SIGMA       # standardised: ~1 if the shape holds
        out.append(w)
    cards = np.array(cards)
    res = pd.concat(out)

    # Shape-difference dashboard (as in the first essay)
    d_last = np.r_[0, np.abs(np.expm1(np.diff(cards, axis=0))).max(axis=1) * 100]
    ref = cards[:6].mean(axis=0)
    d_ref = np.abs(np.expm1(cards - ref)).max(axis=1) * 100

    # Exception monitor 1: size of the exceptions
    size = res.groupby("week").apply(lambda g: np.average(g.z ** 2, weights=None)).values
    size_ratio = size / size[:6].mean()

    # Exception monitor 2: which recorded field explains the exceptions?
    def explained(g, field):
        tot = (g.z ** 2).sum()
        means = g.groupby(field).z.transform("mean")
        return (means ** 2).sum() / tot
    fields = ["device", "region", "plan"]
    expl = {f: res.groupby("week").apply(lambda g: explained(g, f)).values for f in fields}

    # Exception monitor 3: which value of that field?
    by_dev = res[res.week >= 8].groupby("device").apply(
        lambda g: np.average(g.resid, weights=g.n))
    by_dev_ref = res[res.week <= 6].groupby("device").apply(
        lambda g: np.average(g.resid, weights=g.n))

    # Daily server effect as the model sees it (all weeks, one fit per week, re-anchored)
    daily = df.groupby("day").apply(lambda g: np.average(
        g.mean_log - g.agent.map(agent_base) - g.lang.map(lang_base)
        - 0.5 * np.log(g.length / 100), weights=g.n)).values

    np.savez("results.npz", d_last=d_last, d_ref=d_ref, size_ratio=size_ratio,
             daily=daily, server=server, rules=np.array(rules),
             **{f"expl_{f}": v for f, v in expl.items()})
    print("rule (length exponent) per week:", np.round(rules, 3))
    print("max change vs last week (%):", np.round(d_last, 2))
    print("max change vs reference (%):", np.round(d_ref, 2))
    print("exception size / reference:", np.round(size_ratio, 2))
    for f in fields:
        print(f"share of exceptions explained by {f}:", np.round(expl[f], 3))
    print("mean exception by device, weeks 1-6 (%):", np.round(np.expm1(by_dev_ref) * 100, 1).to_dict())
    print("mean exception by device, weeks 8-12 (%):", np.round(np.expm1(by_dev) * 100, 1).to_dict())
    # Daily comparison noise, for the text
    print("server swing sd (%):", round(np.std(server) * 100, 1))
    print("iOS share of requests:", round(df[df.device == 'iOS'].n.sum() / df.n.sum(), 3))
    print("overall slowdown after day 51 (%):", round((PROBLEM_FACTOR - 1) * 0.15 * 100, 2))


if __name__ == "__main__":
    main()
