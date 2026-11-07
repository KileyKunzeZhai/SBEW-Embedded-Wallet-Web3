#!/usr/bin/env bash
# Reproduce every number and figure in Section 7 of the paper (about 3 minutes on a laptop).
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p results figures
python sim.py results/results.json   # Table 4
python sweep.py                      # Figure 1 data
python fig.py                        # Figure 1 + Table 4 rows
python check_repeats.py              # repeated-digit finding
python verify_bounds.py              # Corollary 1 and Theorem 6 checks
