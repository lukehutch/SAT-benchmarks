#!/usr/bin/env bash
# Calibration (known w(2;3,t), A171081) + open instance.  SAT at N = w-1, UNSAT at N = w.
set -e; cd "$(dirname "$0")"; mkdir -p cnf
gen() { python gen_vdw.py "$1" "$2" -o "cnf/vdw_3_$1_N$2.cnf"; }
declare -A W=([10]=97 [11]=114 [12]=135 [13]=160 [14]=186 [15]=218 [16]=238 [17]=279 [18]=312 [19]=349)
for t in 10 11 12 13 14 15 16 17 18 19; do gen $t $((W[$t]-1)); gen $t ${W[$t]}; done
gen 20 388   # SAT: Ahmed, Kullmann, Snevily (2014) give a coloring, w(2;3,20) >= 389
gen 20 389   # OPEN: UNSAT => w(2;3,20) = 389 (their conjecture); SAT => w(2;3,20) >= 390
