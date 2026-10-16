#!/usr/bin/env bash
# Reproduce all results. Run from the repository root after placing data/mnist.npz.
set -euo pipefail
cd "$(dirname "$0")/src"
python3 area_law_pilot.py results.json && python3 plot_baseline.py
python3 mixture_pilot.py mixture_results.json && python3 plot_mixture.py
python3 digits_fit.py && python3 digits_mi.py && python3 plot_digits.py
python3 mnist_model.py
python3 mnist_mi.py && python3 plot_mnist.py
for s in 0 1 2; do OMP_NUM_THREADS=1 python3 mnist_fine.py $s & done; wait
python3 plot_fine.py
for p in 0 1; do OMP_NUM_THREADS=1 python3 immse_validation.py $p 2 & done; wait
python3 immse_compare.py
echo "All results written to src/."
