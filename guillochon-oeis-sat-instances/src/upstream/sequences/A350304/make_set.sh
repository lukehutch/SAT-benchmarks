#!/usr/bin/env bash
# Calibration (known z(n;3) = A350304(n), n = 10..16) + an n = 17 bracket.  SAT at z, UNSAT at z+1.
set -e; cd "$(dirname "$0")"; mkdir -p cnf
gen() { python gen_zaran.py "$1" "$2" -o "cnf/zaran3_n$1_m$2.cnf"; }
Z=(0 1 4 8 13 20 26 33 42 49 60 69 80 92 105 120 128)   # Z[n] = A350304(n)
for n in 10 11 12 13 14 15 16; do gen $n ${Z[$n]}; gen $n $((Z[$n]+1)); done
gen 17 135   # SAT: certificates/zaran3_n17_135 (found by annealing here)
for m in 136 140 144 148 151; do gen 17 $m; done   # OPEN bracket: 135 <= z(17;3) <= 150
