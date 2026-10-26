"""Experiment for "Coherence Is Measurable": does agreement between models predict
whether they are right, and when does it fail?

An ensemble of ten small neural networks (scikit-learn MLPs, different seeds and
bootstrap samples) is trained on the handwritten digits that ship with scikit-learn
(1,797 8x8 images, split in half for training and testing).

Each image can carry a ten-slot "hint", a one-hot tag naming a digit, like a hint
planted in a prompt. A carried hint names the right digit with probability p, and a
random digit otherwise. Two training regimes:
  always     every training image carries a hint
  withheld   20% of training images carry no hint (the rest do)

Test conditions on the same held-out images:
  clean    no hint, original pixels (unfamiliar input for the "always" regime)
  noisy    no hint, Gaussian pixel noise (sd 4 on a 0-16 scale): harder, unseen
  random   a random digit as hint: uninformative but familiar to every hint regime,
           so it measures the cost of a learned shortcut without an unseen input
  wrong    a hint that always names a wrong digit

The control ensemble never sees hints. Each hint regime sweeps p from 50% to 99%.
Everything is repeated on ten random train/test splits.

Writes results.json. Runs in about twelve minutes on 4 CPU cores: python sim.py
"""
import json
import numpy as np
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import roc_auc_score

K, SPLITS, NOISE_SD = 10, 10, 4.0
REGIMES = {"always": 1.0, "withheld": 0.8}   # share of training images that carry a hint
PS = (0.5, 0.8, 0.9, 0.95, 0.99)
CONDS = ("clean", "noisy", "random", "wrong")
X, y = load_digits(return_X_y=True)


def onehot(labels):
    return np.eye(10)[labels] * 16.0          # same scale as the pixels


def ensemble(rng, Xtr, ytr, p=None, present=1.0):
    """p=None: the control, which never sees a hint."""
    models = []
    for k in range(K):
        idx = rng.integers(0, len(ytr), len(ytr))                       # bootstrap
        H = np.zeros((len(idx), 10))
        if p is not None:
            tag = np.where(rng.random(len(idx)) < p, ytr[idx], rng.integers(0, 10, len(idx)))
            H = onehot(tag) * (rng.random(len(idx)) < present)[:, None]
        m = MLPClassifier(hidden_layer_sizes=(64,), max_iter=600, random_state=k)
        models.append(m.fit(np.hstack([Xtr[idx], H]), ytr[idx]))
    return models


def evaluate(models, Xp, H, yte, wrong=None):
    votes = np.stack([m.predict(np.hstack([Xp, H])) for m in models], 1)    # (n, K)
    counts = np.stack([(votes == c).sum(1) for c in range(10)], 1)
    maj, agree = counts.argmax(1), counts.max(1) / K
    right = maj == yte
    order = np.argsort(-agree, kind="stable")
    sel = np.cumsum(right[order]) / np.arange(1, len(order) + 1)
    unanimous = agree == 1
    return {
        "single_model_acc": float((votes == yte[:, None]).mean()),
        "majority_acc": float(right.mean()),
        "auroc": float(roc_auc_score(~right, -agree)),
        "share_unanimous": float(unanimous.mean()),
        "acc_when_unanimous": float(right[unanimous].mean()) if unanimous.any() else None,
        "errors_with_low_agreement": float(((agree < 0.8) & ~right).sum() / max((~right).sum(), 1)),
        "followed_wrong_hint": float((maj == wrong).mean()) if wrong is not None else None,
        "selective_curve": sel.tolist(),
    }


runs = []
for split in range(SPLITS):
    rng = np.random.default_rng(split)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.5, stratify=y, random_state=split)
    n = len(yte)
    none = np.zeros((n, 10))
    wrong = (yte + rng.integers(1, 10, n)) % 10
    noisy = np.clip(Xte + rng.normal(0, NOISE_SD, Xte.shape), 0, 16)
    conds = {"clean": (Xte, none, None), "noisy": (noisy, none, None),
             "random": (Xte, onehot(rng.integers(0, 10, n)), None),
             "wrong": (Xte, onehot(wrong), wrong)}
    for regime, p in [("control", None)] + [(g, p) for g in REGIMES for p in PS]:
        models = ensemble(rng, Xtr, ytr, p, REGIMES.get(regime, 1.0))
        for c, (Xp, H, w) in conds.items():
            runs.append({"split": split, "regime": regime, "hint_p": p, "condition": c,
                         **evaluate(models, Xp, H, yte, w)})
    print(f"split {split} done", flush=True)


def summary(g, p, c, key):
    v = np.array([r[key] for r in runs if r["regime"] == g and r["hint_p"] == p and r["condition"] == c
                  and r[key] is not None])
    if not len(v):
        return None
    return {"mean": float(v.mean()), "sd": float(v.std(ddof=1)), "min": float(v.min()), "max": float(v.max())}


KEYS = ("single_model_acc", "majority_acc", "auroc", "share_unanimous", "acc_when_unanimous",
        "errors_with_low_agreement", "followed_wrong_hint")
SETTINGS = [("control", None)] + [(g, p) for g in REGIMES for p in PS]
out = {"K": K, "splits": SPLITS, "n_test": n, "regimes": REGIMES, "noise_sd": NOISE_SD, "hint_ps": PS,
       "summary": {f"{g}:{p}": {c: {k: summary(g, p, c, k) for k in KEYS} for c in CONDS} for g, p in SETTINGS},
       "mean_selective_curve": {c: np.mean([r["selective_curve"] for r in runs
                                            if r["regime"] == "control" and r["condition"] == c], 0).round(4).tolist()
                                for c in ("clean", "noisy")}}
json.dump(out, open("results.json", "w"), indent=1)

for g, p in SETTINGS:
    for c in CONDS:
        s = out["summary"][f"{g}:{p}"][c]
        f = lambda k: f"{s[k]['mean']:.3f}±{s[k]['sd']:.3f}" if s[k] else "-"
        print(f"{g:8s} p={str(p):5s} {c:6s} single {f('single_model_acc')} majority {f('majority_acc')} "
              f"AUROC {f('auroc')} unanimous {f('share_unanimous')} acc|unan {f('acc_when_unanimous')} "
              f"low-agree errors {f('errors_with_low_agreement')} followed {f('followed_wrong_hint')}")
