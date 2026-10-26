"""Experiment for "Coherence Is Measurable": does agreement between models predict
whether they are right, and when does it fail?

Ten small neural networks (scikit-learn MLPs, different seeds and bootstrap samples)
are trained on the handwritten digits that ship with scikit-learn (1,797 8x8 images).
Each training image also carries a ten-slot "hint": a one-hot tag that names the right
digit 90% of the time and a random digit otherwise, like a hint planted in a prompt.

Three test conditions on the same held-out images:
  clean    no hint, original pixels
  noisy    no hint, Gaussian pixel noise (sd 4 on a 0-16 scale): harder, unseen
  hinted   original pixels, but the hint names a wrong digit
A control ensemble trained without hints is tested on the same three conditions.
A sweep then varies how often the training hint is right (50% to 99%), three seeds each,
and tests on wrong hints only.

Writes results.json. Runs in about two minutes on 4 CPU cores: python sim.py
"""
import json
import numpy as np
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import roc_auc_score

K, SEED, HINT_P, NOISE_SD = 10, 0, 0.9, 4.0
rng = np.random.default_rng(SEED)
X, y = load_digits(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.5, stratify=y, random_state=SEED)


def onehot(labels):
    return np.eye(10)[labels] * 16.0          # same scale as the pixels


def train_hint(labels, p=HINT_P):
    tag = np.where(rng.random(len(labels)) < p, labels, rng.integers(0, 10, len(labels)))
    return onehot(tag)


wrong = (yte + rng.integers(1, 10, len(yte))) % 10       # a wrong digit for every test image
noisy = np.clip(Xte + rng.normal(0, NOISE_SD, Xte.shape), 0, 16)
conds = {
    "clean": (Xte, np.zeros((len(yte), 10))),
    "noisy": (noisy, np.zeros((len(yte), 10))),
    "hinted": (Xte, onehot(wrong)),
}


def ensemble(with_hint, p=HINT_P):
    models = []
    for k in range(K):
        idx = rng.integers(0, len(ytr), len(ytr))                   # bootstrap
        feats = np.hstack([Xtr[idx], train_hint(ytr[idx], p) if with_hint else np.zeros((len(idx), 10))])
        m = MLPClassifier(hidden_layer_sizes=(64,), max_iter=600, random_state=k).fit(feats, ytr[idx])
        models.append(m)
    return models


def evaluate(models, Xp, H):
    votes = np.stack([m.predict(np.hstack([Xp, H])) for m in models], 1)   # (n, K)
    counts = np.stack([(votes == c).sum(1) for c in range(10)], 1)
    maj, agree = counts.argmax(1), counts.max(1) / K
    right = maj == yte
    single = (votes == yte[:, None]).mean()
    order = np.argsort(-agree, kind="stable")
    sel = np.cumsum(right[order]) / np.arange(1, len(order) + 1)
    errs = ~right
    return {
        "single_model_acc": float(single),
        "majority_acc": float(right.mean()),
        "mean_agreement": float(agree.mean()),
        "auroc_agreement_detects_error": float(roc_auc_score(errs, -agree)) if errs.any() and right.any() else None,
        "share_unanimous": float((agree == 1).mean()),
        "acc_when_unanimous": float(right[agree == 1].mean()) if (agree == 1).any() else None,
        "confident_wrong_share_of_all": float(((agree >= 0.8) & errs).mean()),
        "confident_wrong_share_of_errors": float(((agree >= 0.8) & errs).sum() / max(errs.sum(), 1)),
        "selective_curve": [round(float(v), 4) for v in sel[::9]],
        "_maj": maj,
    }


out = {"n_train": int(len(ytr)), "n_test": int(len(yte)), "K": K, "hint_p": HINT_P, "noise_sd": NOISE_SD}
for name, with_hint in (("hint_trained", True), ("control", False)):
    models = ensemble(with_hint)
    out[name] = {}
    for c, (Xp, H) in conds.items():
        r = evaluate(models, Xp, H)
        maj = r.pop("_maj")
        r["followed_hint_share"] = float((maj == wrong).mean()) if c == "hinted" else None
        out[name][c] = r
        print(f"{name:13s} {c:7s} single {r['single_model_acc']:.3f}  majority {r['majority_acc']:.3f}  "
              f"agree {r['mean_agreement']:.2f}  AUROC {r['auroc_agreement_detects_error']}  "
              f"conf-wrong {r['confident_wrong_share_of_all']:.3f} ({r['confident_wrong_share_of_errors']:.2f} of errors)  "
              f"followed hint {r['followed_hint_share']}")
out["sweep"] = []
for p in (0.5, 0.8, 0.9, 0.95, 0.99):
    for seed in range(3):
        rng = np.random.default_rng(100 + seed)
        r = evaluate(ensemble(True, p), Xte, onehot(wrong))
        maj = r.pop("_maj")
        row = {"hint_p": p, "seed": seed, "majority_acc": r["majority_acc"],
               "followed_hint_share": float((maj == wrong).mean()),
               "mean_agreement": r["mean_agreement"],
               "auroc": r["auroc_agreement_detects_error"],
               "confident_wrong_share_of_all": r["confident_wrong_share_of_all"],
               "confident_wrong_share_of_errors": r["confident_wrong_share_of_errors"]}
        out["sweep"].append(row)
        print("sweep", {k: round(v, 3) if isinstance(v, float) else v for k, v in row.items()})
json.dump(out, open("results.json", "w"), indent=1)
