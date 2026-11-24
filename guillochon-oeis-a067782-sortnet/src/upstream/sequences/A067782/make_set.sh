#!/usr/bin/env bash
# Target + calibration instances (known answers from A067782).
set -e
cd "$(dirname "$0")"
gen() { python gen_depth_cnf.py "$1" "$2" -o "cnf/sortnet_n$1_d$2.cnf"; }
gen 11 7    # UNSAT  (a(11)=8, Bundala et al. 2014)
gen 12 7    # UNSAT  (a(12)=8)
gen 12 8    # SAT
gen 14 8    # UNSAT  (a(14)=9)
gen 16 8    # UNSAT  (a(16)=9, Bundala et al. 2014)
gen 16 9    # SAT
gen 17 9    # UNSAT  (a(17)=10)
gen 17 10   # SAT    (Ehlers & Mueller 2014 network)
gen 18 10   # OPEN   target: SAT => a(18)=10, UNSAT => a(18)=11
gen 18 11   # SAT    (known depth-11 networks exist)
