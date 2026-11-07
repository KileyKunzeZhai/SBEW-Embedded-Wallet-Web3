"""Draw Figure 1 and print the Table 4 rows from results/*.json."""
import json, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
S = json.load(open("results/sweep.json")); R = json.load(open("results/results.json"))
def wilson(p, n, z=1.96):
    c = p*n; d = 1+z*z/n; m = (p + z*z/(2*n))/d; h = z*np.sqrt(p*(1-p)/n + z*z/(4*n*n))/d
    return m-h, m+h
fig, ax = plt.subplots(figsize=(5.2, 3.3))
for f, col, mk in ((4, "#4C72B0", "o"), (10, "#DD8452", "s")):
    pts = sorted([r for r in S if r["layout"]=="fixed" and r["f_hz"]==f], key=lambda r: r["sigma_h"])
    x = [r["sigma_h"] for r in pts]; y = [100*r["p_hit@10"] for r in pts]
    lo = [100*wilson(r["p_hit@10"], r["trials"])[0] for r in pts]; hi = [100*wilson(r["p_hit@10"], r["trials"])[1] for r in pts]
    ax.plot(x, y, marker=mk, color=col, label=f"fixed keypad, {f} Hz gauge")
    ax.fill_between(x, lo, hi, color=col, alpha=0.15)
pts = sorted([r for r in S if r["layout"]=="rand_all"], key=lambda r: r["sigma_h"])
ax.errorbar([r["sigma_h"] for r in pts], [100*r["p_hit@10"] for r in pts],
            yerr=np.array([[100*(r["p_hit@10"]-wilson(r["p_hit@10"], r["trials"])[0]), 100*(wilson(r["p_hit@10"], r["trials"])[1]-r["p_hit@10"])] for r in pts]).T,
            fmt="^", color="#55A868", capsize=3, label="randomised keypad, 10 Hz")
ax.axhline(0.1, color="grey", ls="--", lw=1, label="blind guessing (10/10$^4$)")
ax.set_xlabel(r"human timing variability $\sigma_h$ (lognormal)"); ax.set_ylabel("PIN recovered within 10 guesses (%)")
ax.set_yscale("log"); ax.legend(fontsize=7.5, frameon=False); ax.grid(alpha=0.3, which="both", lw=0.4)
fig.tight_layout(); fig.savefig("figures/fig_pin.pdf"); fig.savefig("figures/fig_pin.png", dpi=300)
# table rows
rows = [r for r in R]+[r for r in S if r["layout"]=="rand_all"]
for r in R:
    lo, hi = wilson(r["p_hit@10"], r["trials"])
    print(r["layout"], r["f_hz"], r["trials"], f'{100*r["p_hit@1"]:.2f} {100*r["p_hit@10"]:.2f} [{100*lo:.2f},{100*hi:.2f}] med={r["median_rank"]:.0f} eff={r["mean_eff_set"]:.0f} bits={r["bits_leaked"]:.2f}')
