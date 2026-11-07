"""Monte Carlo model of a fuel-gauge timing attack on wallet PIN entry.

Keypad: 3x4 grid, rows 1-2-3 / 4-5-6 / 7-8-9 / DEL-0-OK.
Inter-press time (Fitts' law):  t = a + b*log2(1 + D/W), multiplied by lognormal human noise.
Observation: each press time is quantised to a fuel-gauge sampling grid of f Hz with random phase.
Attacker observes the 4 intervals d1->d2, d2->d3, d3->d4, d4->OK and ranks all 10^4 PINs by likelihood.
Layouts: 'fixed', 'rand_digits' (digits permuted per entry, OK fixed),
         'rand_all' (digits and OK permuted over the 12 slots minus DEL... see code).
"""
import itertools, json, sys
import numpy as np

rng = np.random.default_rng(20261105)
A, B, W = 0.25, 0.15, 1.0          # seconds, seconds/bit, key width
SIGMA_H = 0.15                      # lognormal sigma of human timing noise
SLOTS = [(r, c) for r in range(4) for c in range(3)]   # 12 slots
FIXED = {d: (( (d - 1) // 3, (d - 1) % 3) if d else (3, 1)) for d in range(10)}
FIXED["OK"] = (3, 2)
DIGIT_SLOTS = [FIXED[d] for d in range(10)]           # slots the 10 digits occupy
OK_SLOT_CHOICES = [(3, 0), (3, 2)]                    # rand_all: OK swaps among bottom corners

def dist(p, q):
    return float(np.hypot(p[0] - q[0], p[1] - q[1]))

ALL_D = sorted({round(dist(p, q), 6) for p in SLOTS for q in SLOTS})
D_INDEX = {d: i for i, d in enumerate(ALL_D)}

def fitts(d):
    return A + B * np.log2(1 + d / W)

def observe(true_intervals, f):
    """Quantise press times to an f-Hz grid with random phase; return observed intervals (in samples)."""
    t = np.concatenate([[0.0], np.cumsum(true_intervals)])
    phase = rng.uniform(0, 1.0 / f)
    k = np.floor((t + phase) * f)
    return np.diff(k).astype(int)

def sample_intervals(dists):
    base = np.array([fitts(d) for d in dists])
    return base * rng.lognormal(0.0, SIGMA_H, size=len(base))

def build_lik_table(f, n=200_000):
    """p(observed samples | distance) per distance class, by Monte Carlo (single interval, random phase)."""
    maxk = int(np.ceil(fitts(max(ALL_D)) * np.exp(5 * SIGMA_H) * f)) + 3
    table = np.full((len(ALL_D), maxk + 1), 1e-12)
    for i, d in enumerate(ALL_D):
        t = fitts(d) * rng.lognormal(0.0, SIGMA_H, size=n)
        phase = rng.uniform(0, 1.0 / f, size=n)
        k = (np.floor((t + phase) * f) - np.floor(phase * f)).astype(int)
        k = np.clip(k, 0, maxk)
        table[i] += np.bincount(k, minlength=maxk + 1)
        table[i] /= table[i].sum()
    return np.log(table), maxk

PINS = np.array(list(itertools.product(range(10), repeat=4)))

def pin_dist_idx(layout_pos, ok_pos):
    """Distance-class index of the 4 observed intervals for every PIN under a given layout."""
    pos = np.array([layout_pos[d] for d in range(10)], dtype=float)
    P = pos[PINS]                                   # (10^4, 4, 2)
    seg = np.linalg.norm(P[:, 1:] - P[:, :-1], axis=2)
    last = np.linalg.norm(P[:, 3] - np.array(ok_pos, float), axis=1)
    D = np.concatenate([seg, last[:, None]], axis=1).round(6)
    lut = np.vectorize(D_INDEX.get)
    return lut(D)

FIXED_IDX = pin_dist_idx(FIXED, FIXED["OK"])

# equality pattern of each PIN (canonical relabelling), for the randomised-layout attacker
def pattern(p):
    m, out = {}, []
    for x in p:
        m.setdefault(x, len(m)); out.append(m[x])
    return tuple(out)
PAT = [pattern(p) for p in PINS]
PAT_IDS = {q: i for i, q in enumerate(sorted(set(PAT)))}
PAT_ARR = np.array([PAT_IDS[q] for q in PAT])

def rand_layout(rand_ok):
    perm = rng.permutation(10)
    lay = {d: DIGIT_SLOTS[perm[d]] for d in range(10)}
    ok = FIXED["OK"]
    if rand_ok:
        # OK and DEL swap among the two bottom corners
        ok = OK_SLOT_CHOICES[rng.integers(2)]
    return lay, ok

def pattern_loglik(obs, logT, maxk, rand_ok, n_perm=400):
    """Bayes-optimal log-likelihood per equality pattern, averaging over random layouts."""
    obs = np.clip(obs, 0, maxk)
    reps = {}
    for i, p in enumerate(PINS):
        reps.setdefault(PAT_ARR[i], p)
    out = np.zeros(len(PAT_IDS))
    for pid, rep in reps.items():
        ls = []
        for _ in range(n_perm):
            lay, ok = rand_layout(rand_ok)
            pts = [lay[d] for d in rep]
            ds = [dist(pts[0], pts[1]), dist(pts[1], pts[2]), dist(pts[2], pts[3]), dist(pts[3], ok)]
            idx = [D_INDEX[round(d, 6)] for d in ds]
            ls.append(sum(logT[j, o] for j, o in zip(idx, obs)))
        ls = np.array(ls)
        out[pid] = ls.max() + np.log(np.mean(np.exp(ls - ls.max())))
    return out

def metrics(post, true_i, qs=(1, 5, 10)):
    order = np.argsort(-post, kind="stable")
    rank = int(np.where(order == true_i)[0][0]) + 1
    p = post / post.sum()
    H = -np.sum(p[p > 0] * np.log2(p[p > 0]))
    return rank, {q: rank <= q for q in qs}, 2 ** H

def run(layout, f, trials, logT, maxk):
    ranks, hits, effs = [], {1: 0, 5: 0, 10: 0}, []
    for _ in range(trials):
        ti = rng.integers(10 ** 4)
        pin = PINS[ti]
        if layout == "fixed":
            lay, ok = FIXED, FIXED["OK"]
        else:
            lay, ok = rand_layout(layout == "rand_all")
        pts = [lay[d] for d in pin]
        ds = [dist(pts[0], pts[1]), dist(pts[1], pts[2]), dist(pts[2], pts[3]), dist(pts[3], ok)]
        obs = np.clip(observe(sample_intervals(ds), f), 0, maxk)
        if layout == "fixed":
            ll = sum(logT[FIXED_IDX[:, k], obs[k]] for k in range(4))
        else:
            pl = pattern_loglik(obs, logT, maxk, layout == "rand_all", n_perm=150)
            ll = pl[PAT_ARR]
        post = np.exp(ll - ll.max())
        post = post + rng.uniform(0, 1e-9, size=post.shape)   # random tie-breaking
        r, h, e = metrics(post, ti)
        ranks.append(r); effs.append(e)
        for q in h: hits[q] += h[q]
    ranks = np.array(ranks)
    return {
        "layout": layout, "f_hz": f, "trials": trials,
        "p_hit@1": hits[1] / trials, "p_hit@5": hits[5] / trials, "p_hit@10": hits[10] / trials,
        "median_rank": float(np.median(ranks)), "mean_rank": float(ranks.mean()),
        "mean_eff_set": float(np.mean(effs)),
        "bits_leaked": float(np.log2(1e4) - np.mean(np.log2(effs))),
    }

if __name__ == "__main__":
    res = []
    for f in (4, 10, 50):
        logT, maxk = build_lik_table(f)
        res.append(run("fixed", f, 4000, logT, maxk))
        if f != 50:
            res.append(run("rand_digits", f, 300, logT, maxk))
            res.append(run("rand_all", f, 300, logT, maxk))
        print(json.dumps(res[-1]), flush=True)
    for r in res:
        print(json.dumps(r))
    json.dump(res, open(sys.argv[1] if len(sys.argv) > 1 else "results/results.json", "w"), indent=1)
