# Critical & Off-Threshold Phase-Transition Random 3-SAT (`random-3sat-phase-transition`)

## Overview & Origin

Uniform random 3-SAT formulas ($n = 200$ variables; clauses of 3 distinct uniformly random variables with independent uniform polarities) sampled across the classic **easy–hard–easy satisfiability phase transition** around the critical clause-to-variable ratio $\alpha_c = m / n \approx 4.26$:

- **Under-constrained (SAT side, below threshold):** $\alpha \in \{3.80, 4.00, 4.10\}$ ($m \in \{760, 800, 820\}$, 3 SAT instances)
- **Critical phase transition:** $\alpha = 4.26$ ($m = 852$, 1 SAT + 1 UNSAT instance — also included in the Unified 50-Benchmark Gauntlet)
- **Over-constrained (UNSAT side, above threshold):** $\alpha \in \{4.45, 4.65, 5.00\}$ ($m \in \{890, 930, 1{,}000\}$, 3 UNSAT instances)

These 8 instances (**4 SAT / 4 UNSAT**) provide a pure unstructured baseline with zero gate, parity, cardinality, or symmetry structure on both flanks and at the peak of the phase transition.

- **Recommended by:** [`@tingan87`](https://twitter.com/tingan87) (Twitter/X)
- **Origin:** **Original** generator (MIT [`../LICENSE`](../LICENSE)), sampling the canonical uniform random 3-SAT phase-transition ensemble (Mitchell, Selman, & Levesque, AAAI 1992; Crawford & Auton, [AIJ 1996](https://doi.org/10.1016/0004-3702(95)00046-1)).
- **Why they are important:** They trace raw solver search and local-search behavior across the under-constrained SAT shoulder, the critical threshold peak, and the over-constrained UNSAT slope where structural preprocessing yields no simplification.

## Directory Layout & Regeneration

- `*.cnf` — Original native **DIMACS CNF** formulas (8 instances: 4 SAT / 4 UNSAT).
- `aig-version/` — Exact logically equivalent **Binary AIGER 1.9 `.aig`** conversions (all 8/8 verified with [Berkeley ABC](https://github.com/berkeley-abc/abc)).
- `xcnf-version/` — Exact **[CryptoMiniSat](https://github.com/msoos/cryptominisat) `.xcnf`** conversions.
- `src/gen_rand3sat.py` — Standalone zero-dependency Python 3 generator (`python3 src/gen_rand3sat.py`), alongside `src/cnf2aig.py` and `src/cnf2xcnf.py`.

## Problem Parameters & Data Sizes

| Instance | Regime | Vars $n$ | Clauses $m$ | Ratio $m/n$ | Python `random.Random` Seed | Ans | CNF Size | AIG Inputs | AIG ANDs | AIG Size |
|---|---|---:|---:|---:|---:|:---:|---:|---:|---:|---:|
| `rand3sat_n200_r380_sat` | Under-constrained | 200 | 760 | 3.80 | `203800` | SAT | 10.4 KB | 200 | 2,274 | 6.9 KB |
| `rand3sat_n200_r400_sat` | Under-constrained | 200 | 800 | 4.00 | `204000` | SAT | 11.0 KB | 200 | 2,393 | 7.3 KB |
| `rand3sat_n200_r410_sat` | Near-threshold SAT | 200 | 820 | 4.10 | `204100` | SAT | 11.2 KB | 200 | 2,452 | 7.5 KB |
| `rand3sat_n200_sat` | Critical threshold | 200 | 852 | 4.26 | `200000` | SAT | 11.6 KB | 200 | 2,549 | 7.8 KB |
| `rand3sat_n200_unsat` | Critical threshold | 200 | 852 | 4.26 | `200005` | UNSAT | 11.6 KB | 200 | 2,549 | 7.8 KB |
| `rand3sat_n200_r445_unsat` | Near-threshold UNSAT | 200 | 890 | 4.45 | `204450` | UNSAT | 12.2 KB | 200 | 2,661 | 8.1 KB |
| `rand3sat_n200_r465_unsat` | Over-constrained | 200 | 930 | 4.65 | `204650` | UNSAT | 12.7 KB | 200 | 2,785 | 8.5 KB |
| `rand3sat_n200_r500_unsat` | Over-constrained | 200 | 1,000 | 5.00 | `205000` | UNSAT | 13.6 KB | 200 | 2,990 | 9.1 KB |

## Benchmark Results (1-Core, Flat DIMACS `.cnf` Input)

- **Timeout:** $T_{\max} = 60\;\text{s}$ per instance.
- **Same machine?** **Yes** — all six solver configurations were run sequentially on the exact same **AMD Ryzen 9 5950X** Linux workstation (1 core per run, exact median of 3 runs; 0 verdict disagreements; all 4/4 SAT assignments independently verified clause-by-clause).

| Instance ($m/n$) | Ans | Frobenius 1C | [`dense-solver 0.0.4`](https://github.com/libdense/dense-solver) | [Kissat](https://github.com/arminbiere/kissat) 4.0.4 | [CaDiCaL](https://github.com/arminbiere/cadical) 3.1.0 | [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18 (CNF) | [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18 (XCNF) |
|---|:---:|---:|---:|---:|---:|---:|---:|
| `rand3sat_n200_r380_sat` (3.80) | SAT | **3.18 ms** | 10.66 ms | 22.15 ms | 4.01 ms | 30.82 ms | 28.57 ms |
| `rand3sat_n200_r400_sat` (4.00) | SAT | **3.11 ms** | 4.67 ms | 25.32 ms | 21.35 ms | 30.81 ms | 32.51 ms |
| `rand3sat_n200_r410_sat` (4.10) | SAT | **3.74 ms** | 7.47 ms | 137.37 ms | 245.96 ms | 114.58 ms | 111.14 ms |
| `rand3sat_n200_sat` (4.26) | SAT | **2.97 ms** | 28.04 ms | 37.57 ms | 55.98 ms | 36.20 ms | 37.56 ms |
| `rand3sat_n200_unsat` (4.26) | UNSAT | 348.51 ms | **200.24 ms** | 341.01 ms | 334.04 ms | 508.83 ms | 515.00 ms |
| `rand3sat_n200_r445_unsat` (4.45) | UNSAT | 298.54 ms | **114.02 ms** | 278.28 ms | 241.13 ms | 228.32 ms | 241.28 ms |
| `rand3sat_n200_r465_unsat` (4.65) | UNSAT | 232.62 ms | **99.04 ms** | 203.30 ms | 218.58 ms | 227.29 ms | 222.57 ms |
| `rand3sat_n200_r500_unsat` (5.00) | UNSAT | 173.65 ms | **18.71 ms** | 67.91 ms | 45.88 ms | 81.35 ms | 81.24 ms |
| **TOTAL (8 instances, 8/8 solved)** | **4 / 4** | 1,066.32 ms *(2.21x slower)* | **482.86 ms** *(fastest)* | 1,112.90 ms *(2.30x slower)* | 1,166.94 ms *(2.42x slower)* | 1,258.22 ms *(2.61x slower)* | 1,269.88 ms *(2.63x slower)* |

*(Across a broader 10-seed $n = 200, m = 852$ cohort [7 SAT / 3 UNSAT], Frobenius achieved median `115.68 ms` / mean `274.43 ms` vs. [Kissat](https://github.com/arminbiere/kissat) `98.41 / 305.15 ms`, [CaDiCaL](https://github.com/arminbiere/cadical) `318.43 / 402.75 ms`, and [CMS](https://github.com/msoos/cryptominisat) `303.07 / 534.09 ms`; across 10 seeds at $n = 250, m = 1{,}065$ [3 SAT / 7 UNSAT], Frobenius achieved `8.01 s` median / `7.80 s` mean vs. [Kissat](https://github.com/arminbiere/kissat) `4.50 / 4.46 s`, [CaDiCaL](https://github.com/arminbiere/cadical) `6.69 / 6.50 s`, [CMS](https://github.com/msoos/cryptominisat) `7.88 / 10.58 s`.)*

## References

- D. Mitchell, B. Selman, and H. Levesque, *Hard and Easy Distributions of SAT Problems*, AAAI 1992.
- J. M. Crawford and L. D. Auton, *Experimental Results on the Crossover Point in Random 3-SAT*, Artificial Intelligence 81(1–2):31–57, 1996.
