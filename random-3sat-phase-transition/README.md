# Critical Phase-Transition Random 3-SAT (`random-3sat-phase-transition`)

## Overview & Origin

Uniform random 3-SAT formulas sampled directly at the critical satisfiability phase transition $m / n = 4.26$ ($n = 200$ variables, $m = 852$ clauses of 3 distinct uniformly random variables with independent uniform polarities), providing a pure unstructured baseline with zero gate, parity, cardinality, or symmetry structure.

- **Origin:** **Original** generator (MIT [`../LICENSE`](../LICENSE)), sampling the canonical uniform random 3-SAT phase-transition ensemble (Mitchell, Selman, & Levesque, AAAI 1992; Crawford & Auton, [AIJ 1996](https://doi.org/10.1016/0004-3702(95)00046-1)).
- **Why they are important:** They measure raw solver search throughput on unstructured uniform random formulas where structural preprocessing yields no simplification.

## Directory Layout & Regeneration

- `*.cnf` — Original native **DIMACS CNF** formulas.
- `aig-version/` — Exact logically equivalent **Binary AIGER 1.9 `.aig`** conversions (verified with [Berkeley ABC](https://github.com/berkeley-abc/abc)).
- `src/gen_rand3sat.py` — Standalone zero-dependency Python 3 generator (`python3 src/gen_rand3sat.py`).

## Problem Parameters & Data Sizes

| Instance | Vars $n$ | Clauses $m$ | Ratio $m/n$ | Python `random.Random` Seed | Ans | CNF Size | AIG Inputs | AIG ANDs | AIG Size |
|---|---:|---:|---:|---:|:---:|---:|---:|---:|---:|
| `rand3sat_n200_sat` | 200 | 852 | 4.26 | `200000` | SAT | 11.6 KB | 200 | 2,549 | 7.8 KB |
| `rand3sat_n200_unsat` | 200 | 852 | 4.26 | `200005` | UNSAT | 11.6 KB | 200 | 2,549 | 7.8 KB |

## Benchmark Results (1-Core, Flat DIMACS `.cnf` Input)

Evaluated sequentially on an AMD Ryzen 9 5950X (exact median of 3 runs; $T_{\max} = 600\;\text{s}$):

| Instance | Frobenius 1C | [Kissat](https://github.com/arminbiere/kissat) 4.0.4 | [CaDiCaL](https://github.com/arminbiere/cadical) 3.1.0 | [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18 (CNF) | [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18 (XCNF) |
|---|---:|---:|---:|---:|---:|
| `rand3sat_n200_sat` | **2.77 ms** | 56.71 ms | 83.81 ms | 58.79 ms | 59.76 ms |
| `rand3sat_n200_unsat` | **370.37 ms** | 582.15 ms | 525.20 ms | 1,099.71 ms | 890.47 ms |

*(Across a broader 10-seed $n = 200, m = 852$ cohort [7 SAT / 3 UNSAT], Frobenius achieved median `115.68 ms` / mean `274.43 ms` vs. [Kissat](https://github.com/arminbiere/kissat) `98.41 / 305.15 ms`, [CaDiCaL](https://github.com/arminbiere/cadical) `318.43 / 402.75 ms`, and [CMS](https://github.com/msoos/cryptominisat) `303.07 / 534.09 ms`; across 10 seeds at $n = 250, m = 1{,}065$ [3 SAT / 7 UNSAT], Frobenius achieved `8.01 s` median / `7.80 s` mean vs. [Kissat](https://github.com/arminbiere/kissat) `4.50 / 4.46 s`, [CaDiCaL](https://github.com/arminbiere/cadical) `6.69 / 6.50 s`, [CMS](https://github.com/msoos/cryptominisat) `7.88 / 10.58 s`.)*

## References

- D. Mitchell, B. Selman, and H. Levesque, *Hard and Easy Distributions of SAT Problems*, AAAI 1992.
- J. M. Crawford and L. D. Auton, *Experimental Results on the Crossover Point in Random 3-SAT*, Artificial Intelligence 81(1–2):31–57, 1996.
