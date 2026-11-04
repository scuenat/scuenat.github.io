"""Simulation for "Stop Shifting Left". Running it prints Table 2 and writes results.json.

One feature, built by an agent, iterated until it is released. Defects are of two kinds:
implementation defects (the code does not do what was specified), which machines can catch,
and fit defects (the code does what was specified, but not what the domain needs), which only
people who know the domain notice when they use it. All parameters are chosen, not measured.
"""
import json
import numpy as np

P = dict(
    n0=12,          # defects in the first version
    phi=0.5,        # share of implementation defects
    a=0.25,         # days for the agent to build and run unit tests and checks
    s=1.0,          # extra days per cycle for engineering-side tests (integration, E2E, QA pass)
    u=0.5,          # share of new implementation defects caught by unit tests and checks
    e=0.6,          # share of remaining implementation defects caught by the extra tests per cycle
    e_fit=0.1,      # share of fit defects the extra tests catch (written from the spec, so a few)
    q_impl=0.6,     # daily chance a domain tester notices a given implementation defect
    q_fit=0.4,      # daily chance a domain tester notices a given fit defect
    beta=0.15,      # chance each fix introduces a new defect
    h_s=4.0,        # engineer hours per cycle of extra tests (write, maintain, rerun, triage)
    h_t=2.0,        # domain-tester hours per day of testing in place
    lock=1.0,       # days to generate the regression and extra unit tests once the feature is accepted
    post_days=60,   # working days followed after release
    reg_rate=0.05,  # daily chance that a change elsewhere breaks this feature
    e_reg=0.7,      # share of such regressions the feature's regression suite catches
    clean_days=2,   # release (flip the flag) after this many days in a row with nothing found
    runs=4000,
    horizon=120,
)

POLICIES = {
    "shift_left": "Shift left: full test suite, then acceptance at the end",
    "suite_and_flag": "Full test suite, and testing in place behind a flag",
    "proposed": "Unit tests and checks, testing in place behind a flag (proposed)",
    "lock_in": "Proposed, then lock-in: regression and unit tests generated once, before the flip",
    "nothing": "No tests at all, testing in place behind a flag",
}


def new_defects(rng, n, p):
    imp = rng.binomial(n, p["phi"])
    return imp, n - imp


def after_release(policy, rng, p):
    """Regressions introduced by later changes to shared code, and how many reach customers."""
    n = rng.binomial(p["post_days"], p["reg_rate"])
    catch = 0.0
    if policy != "nothing":
        catch = p["u"]
    if policy in ("shift_left", "suite_and_flag", "lock_in"):
        catch = 1 - (1 - p["u"]) * (1 - p["e_reg"])
    return n - rng.binomial(n, catch)


def run(policy, rng, p=P):
    unit = policy != "nothing"
    lock_in = policy == "lock_in"
    suite = policy in ("shift_left", "suite_and_flag")
    in_place_from_start = policy != "shift_left"
    imp, fit = new_defects(rng, p["n0"], p)
    if unit:
        imp -= rng.binomial(imp, p["u"])
    t, eng_h, test_h = 0.0, 0.0, 0.0
    testers_on = in_place_from_start
    clean = 0
    while t < p["horizon"]:
        found_imp = found_fit = 0
        t += p["a"]
        if suite:
            t += p["s"]; eng_h += p["h_s"]
            c_i = rng.binomial(imp, p["e"]); c_f = rng.binomial(fit, p["e_fit"])
            imp -= c_i; fit -= c_f; found_imp += c_i; found_fit += c_f
            if policy == "shift_left" and not testers_on and c_i + c_f == 0:
                testers_on = True     # the suite is clean: hand over for acceptance
        if testers_on:
            t += 1.0 - p["a"]   # the rest of the day in use; fixes start the next morning
            test_h += p["h_t"]
            c_i = rng.binomial(imp, p["q_impl"]); c_f = rng.binomial(fit, p["q_fit"])
            imp -= c_i; fit -= c_f
            clean = clean + 1 if c_i + c_f == 0 and found_imp + found_fit == 0 else 0
            if clean == p["clean_days"]:
                if lock_in:   # write the suite once, against behaviour that no longer moves
                    t += p["lock"]; eng_h += p["h_s"]
                    imp -= rng.binomial(imp, p["e"]); fit -= rng.binomial(fit, p["e_fit"])
                return dict(days=t, escaped=imp + fit, eng_h=eng_h, test_h=test_h)
            found_imp += c_i; found_fit += c_f
        # fixes, each may bring a new defect
        k = found_imp + found_fit
        ni, nf = new_defects(rng, rng.binomial(k, p["beta"]), p)
        if unit:
            ni -= rng.binomial(ni, p["u"])
        imp += ni; fit += nf
    return dict(days=t, escaped=imp + fit, eng_h=eng_h, test_h=test_h)


def summarise(p=P, seed=7):
    rng = np.random.default_rng(seed)
    rng_post = np.random.default_rng(seed + 100)   # separate stream for the months after release
    out = {}
    for pol in POLICIES:
        rs = [run(pol, rng, p) for _ in range(p["runs"])]
        for r in rs:
            r["regressions"] = after_release(pol, rng_post, p)
        d = np.array([r["days"] for r in rs]); esc = np.array([r["escaped"] for r in rs])
        out[pol] = dict(
            days_median=float(np.median(d)), days_p90=float(np.percentile(d, 90)),
            escaped_mean=float(esc.mean()), escaped_se=float(esc.std() / np.sqrt(len(esc))),
            eng_h=float(np.mean([r["eng_h"] for r in rs])),
            test_h=float(np.mean([r["test_h"] for r in rs])),
            regressions=float(np.mean([r["regressions"] for r in rs])),
        )
    return out


def threshold(phi, e=P["e"], q=0.5, cycle=1.0):
    """Largest extra test time per cycle (days) for which the suite still speeds up learning:
    s* = cycle * ln(1 - e*phi) / ln(1 - q)."""
    return cycle * np.log(1 - e * phi) / np.log(1 - q)


if __name__ == "__main__":
    res = summarise()
    for k, v in res.items():
        print(f"{POLICIES[k]:66s} days {v['days_median']:5.1f} (p90 {v['days_p90']:5.1f})  "
              f"escaped {v['escaped_mean']:.2f}±{v['escaped_se']:.2f}  eng {v['eng_h']:5.1f} h  "
              f"testers {v['test_h']:5.1f} h  regressions {v['regressions']:.2f}")
    for phi in (0.2, 0.5, 0.8):
        print("phi", phi, "s* =", round(float(threshold(phi)), 2), "days")
    json.dump(res, open("results.json", "w"), indent=2)
