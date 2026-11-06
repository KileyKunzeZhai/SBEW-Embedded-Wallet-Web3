# Embedded Wallets for Shielded Bitcoin

Paper and simulation code for **"Embedded Wallets for Shielded Bitcoin: Threshold Seed Custody, Proving Placement, and Side-Channel-Hardened PIN Authorization for Replay-Based Shielded Transfers"** by Roi Mateo, Kiley Kunze Zhai, and Suzuki Motoyasu (2026).

- Paper (PDF): [`paper/Embedded_Wallets_for_Shielded_Bitcoin.pdf`](paper/Embedded_Wallets_for_Shielded_Bitcoin.pdf)
- IACR ePrint: `https://eprint.iacr.org/2026/XXXX` *(link added after publication)*

## Abstract

Shielded Bitcoin enables private Bitcoin transfers on L1 through encrypted notes, nullifiers, and zero-knowledge proofs, but its specification assumes a self-contained wallet. We ask how to build an embedded wallet, unlocked by a PIN and backed up by a provider, without making the provider a custodian or a surveillance point. We present SBEW, which splits the wallet seed 2-of-3 across device, provider, and recovery shares, with the provider share released by an attempt-limited oblivious-PRF PIN check. It also defines on-device, enclave, and MPC proving, replaces single-indexer trust with k-of-n root agreement, and wraps the device share on Cortex-M chips with the tweakable block cipher Rotom. We prove non-custody, PIN-leak tolerance, theft resistance, sync integrity, recovery, and the wrap's security. Against fuel-gauge PIN leakage, randomized keypads provably cap 10-guess success on 4-digit PINs at 1.5%, versus up to 6.7% for fixed keypads in simulation. We also show that a provider that both scans and relays can reconstruct its users' payment graph. SBEW requires no protocol changes.

## Repository layout

```
paper/
  Embedded_Wallets_for_Shielded_Bitcoin.pdf    the paper
  Embedded_Wallets_for_Shielded_Bitcoin.docx   editable Word version
  main.tex, fig_pin.pdf                        LaTeX source and figure
simulation/
  sim.py             fuel-gauge PIN attack model (Table 4)
  sweep.py           timing-variability sweep (Figure 1 data)
  fig.py             draws Figure 1, prints Table 4 rows
  check_repeats.py   randomized-keypad leakage comes only from repeated digits (Section 7)
  verify_bounds.py   exact checks of Corollary 1 and the Shamir identity in Theorem 6
  run_all.sh         runs everything above
  results/           JSON outputs used in the paper
  figures/           Figure 1 (PDF and PNG)
```

## Reproducing the results

Requires Python 3.10 or later.

```bash
cd simulation
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
./run_all.sh
```

The full run takes about 3 minutes on a laptop. The random seed is fixed (`20261105`), so `results/results.json` and `results/sweep.json` match the files in this repository byte for byte when run with the pinned package versions.

| Script | Reproduces |
| --- | --- |
| `sim.py` | Table 4 (PIN recovery by keypad and sampling rate) |
| `sweep.py` + `fig.py` | Figure 1 (10-guess success vs. timing variability) |
| `check_repeats.py` | Section 7, finding 3: no PIN with four distinct digits is recovered under a randomized keypad |
| `verify_bounds.py` | Corollary 1 caps (1.5%, 0.198%, 0.203%) and Shamir 2-of-3 reconstruction over GF(2^8) |

The model parameters (keypad geometry, Fitts' law constants, sampling with random phase, attacker likelihood) are listed in Appendix A of the paper.

## Citation

```bibtex
@misc{MateoZhaiMotoyasu2026,
  author       = {Roi Mateo and Kiley Kunze Zhai and Suzuki Motoyasu},
  title        = {Embedded Wallets for Shielded Bitcoin: Threshold Seed Custody, Proving Placement, and Side-Channel-Hardened PIN Authorization for Replay-Based Shielded Transfers},
  howpublished = {Cryptology {ePrint} Archive, Paper 2026/XXXX},
  year         = {2026},
  url          = {https://eprint.iacr.org/2026/XXXX}
}
```

## License

- Code in `simulation/`: MIT License, see [`LICENSE`](LICENSE).
- Paper in `paper/`: Creative Commons Attribution 4.0 (CC BY 4.0), see [`paper/LICENSE`](paper/LICENSE).

## Contact

Roi Mateo (roimateo.nsofts@gmail.com), Kiley Kunze Zhai (zhai16263@gmail.com), Suzuki Motoyasu (suzukimotoyasu9429@outlook.com)
"# SBEW-Embedded-Wallet-Web3" 
