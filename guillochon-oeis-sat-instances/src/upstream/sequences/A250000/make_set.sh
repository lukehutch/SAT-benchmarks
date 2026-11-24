#!/usr/bin/env bash
# Calibration (known A250000(n), n <= 20) + open instance n = 21.  SAT at m = a(n), UNSAT at m = a(n)+1.
set -e; cd "$(dirname "$0")"; mkdir -p cnf
gen() { python gen_queens.py "$1" "$2" -o "cnf/queens_n$1_m$2.cnf"; }
A=(0 0 0 1 2 4 5 7 9 12 14 17 21 24 28 32 37 42 47 52 58)   # A[n] = a(n), n = 1..20
for n in 12 13 14 15 16 17 18 19 20; do gen $n ${A[$n]}; gen $n $((A[$n]+1)); done
gen 21 64    # SAT: Ainley's 1977 construction, floor(7*21^2/48) = 64
gen 21 65    # OPEN: UNSAT => a(21) = 64; SAT => a(21) >= 65 (beats Ainley)
