#!/usr/bin/env bash
# For each pattern: the three largest known sizes (SAT at max, UNSAT at max+1), a SAT rung at the open size from
# the best known configuration, and the open instance one above it.
set -e; cd "$(dirname "$0")"; mkdir -p cnf
gen() { python gen_points.py "$1" "$2" "$3" -o "cnf/$1_n$2_m$3.cnf"; }
pair() { gen "$1" "$2" "$3"; gen "$1" "$2" $(($3+1)); }
pair sq-axis 11 73;  pair sq-axis 12 85;  pair sq-axis 13 98           # A227133
gen sq-axis 14 112;  gen sq-axis 14 113                                # 112: Karpov 2016; 113 OPEN
pair sq-any 8 34;    pair sq-any 9 42;    pair sq-any 10 50            # A240443
gen sq-any 11 58;    gen sq-any 11 59                                  # 58: Israel 2016; 59 OPEN
pair tri-up 11 31;   pair tri-up 12 35;   pair tri-up 13 40            # A157795 (side = index + 1)
gen tri-up 14 46;    gen tri-up 14 47                                  # 46: certificates/; 47 OPEN
pair tri-axis 13 39; pair tri-axis 14 44; pair tri-axis 15 49          # A227308
gen tri-axis 16 54;  gen tri-axis 16 55                                # 54: certificates/; 55 OPEN
pair tri-any 13 28;  pair tri-any 14 31;  pair tri-any 15 34           # A240114
gen tri-any 16 36;   gen tri-any 16 37                                 # 36: certificates/; 37 OPEN
