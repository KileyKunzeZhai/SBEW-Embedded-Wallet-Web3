"""Check which PINs are still recovered under a randomized keypad (Section 7, finding 3).

Runs 600 randomized-keypad entries (sigma_h = 0.05, 10 Hz) and counts ten-guess
successes separately for PINs with four distinct digits and PINs with a repeat.
"""
import collections
import numpy as np
import sim

sim.SIGMA_H = 0.05
logT, maxk = sim.build_lik_table(10)
hits, tot = collections.Counter(), collections.Counter()
for _ in range(600):
    ti = sim.rng.integers(10 ** 4)
    pin = sim.PINS[ti]
    lay, ok = sim.rand_layout(True)
    pts = [lay[d] for d in pin]
    ds = [sim.dist(pts[0], pts[1]), sim.dist(pts[1], pts[2]), sim.dist(pts[2], pts[3]), sim.dist(pts[3], ok)]
    obs = np.clip(sim.observe(sim.sample_intervals(ds), 10), 0, maxk)
    ll = sim.pattern_loglik(obs, logT, maxk, True, 150)[sim.PAT_ARR]
    post = np.exp(ll - ll.max()) + sim.rng.uniform(0, 1e-9, 10 ** 4)
    rank = int(np.where(np.argsort(-post) == ti)[0][0]) + 1
    k = "distinct" if len(set(pin)) == 4 else "repeat"
    tot[k] += 1
    hits[k] += rank <= 10
print("entries:", dict(tot))
print("hits within 10 guesses:", dict(hits))
