"""Sweep human timing variability (sigma_h) for Figure 1. Writes results/sweep.json."""
import json
import sim

out = []
for s in (0.05, 0.08, 0.15, 0.25):
    sim.SIGMA_H = s
    for f in (4, 10):
        logT, maxk = sim.build_lik_table(f)
        r = sim.run("fixed", f, 3000, logT, maxk); r["sigma_h"] = s; out.append(r); print(json.dumps(r), flush=True)
        if s in (0.05, 0.15) and f == 10:
            r = sim.run("rand_all", f, 800, logT, maxk); r["sigma_h"] = s; out.append(r); print(json.dumps(r), flush=True)
json.dump(out, open("results/sweep.json", "w"), indent=1)
