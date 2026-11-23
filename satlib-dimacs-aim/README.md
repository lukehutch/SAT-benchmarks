# SATLIB — Artificial Random 3-SAT — Iwama et al. (full) (`satlib-dimacs-aim`)

## Provenance & Credit

- **Recommended by:** [`@jasonslenderman`](https://twitter.com/jasonslenderman) (Twitter/X)
- **Upstream Archive:** [SATLIB — Benchmark Problems (UBC)](https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html)
- **SATLIB Curators:** Holger H. Hoos and Thomas Stützle (University of British Columbia / TU Darmstadt)
- **Family Contributors:** Kazuo Iwama, Eiji Miyano, and Yuichi Asahiro
- **License:** Classic public scientific benchmark collection redistributed by UBC SATLIB for academic SAT research; no separate upstream `LICENSE` file is bundled in the archives.
- **Format Hygiene:** Legacy SATLIB trailing `%` / `0` EOF sentinels were stripped and wrapped multi-line clauses normalized to canonical 1-clause-per-line DIMACS CNF so every modern SAT solver parses all files cleanly.
- **Full SATLIB Archive Manifest:** [`../satlib-archive-uris/`](../satlib-archive-uris/README.md) (all 97 official UBC SATLIB `.tar.gz` archive URLs; Pretolani's `PRET` formulas live in [`../pretolani-pret/`](../pretolani-pret/README.md)).

## Problem Description

All 72 artificially generated random 3-SAT instances (`aim-50`, `aim-100`, `aim-200`) from the Second DIMACS Implementation Challenge, featuring unique-solution SAT and hard UNSAT formulas.

## Corpus & Data Sizes (Four Formats)

- **`cnf-orig/`** — 72 original native **DIMACS `.cnf.xz`** files (121.6 KB).
- **`aig-converted/`** — 72 exact **Binary AIGER 1.9 `.aig.xz`** conversions (142.7 KB, verified via [Berkeley ABC](https://github.com/berkeley-abc/abc) `read_aiger`).
- **`xcnf-converted/`** — 72 lossless **[CryptoMiniSat](https://github.com/msoos/cryptominisat) `.xcnf.xz`** conversions (125.2 KB, `0` extracted native XOR parity clauses).
- **`anf-converted/`** — 72 lossless linear-size **DIMACS-ANF `.anf.xz`** conversions (197.8 KB, generated via [`../src/to_anf.py`](../src/to_anf.py)).
- **`src/`** — Standalone converters (`cnf2aig.py`, `cnf2xcnf.py`).

| Format | Directory | Files | Key Dimensions (Range) | Compressed Size |
|---|---|---:|---|---:|
| **DIMACS CNF (origin)** | `cnf-orig/` | 72 | Vars: 50–200; Clauses: 80–1,200 | 121.6 KB |
| **Binary AIGER 1.9** | `aig-converted/` | 72 | Inputs: 50–200; ANDs: 224–3,535 | 142.7 KB |
| **[CryptoMiniSat](https://github.com/msoos/cryptominisat) XCNF** | `xcnf-converted/` | 72 | Native XOR clauses total: 0 | 125.2 KB |
| **DIMACS-ANF** | `anf-converted/` | 72 | Vars: 50–200; Eqs: 76–1,197 (deg ≤ 3) | 197.8 KB |
| **Total (4 Formats, Status: Mixed)** | | **288** | | **587.2 KB** |

## Comparative 1-Core Benchmark Results (All 72 Instances, Flat `.cnf`, $T_{\max} = 5\;\text{s}$)

- **Hardware & Protocol:** Same machine (**AMD Ryzen 9 5950X**, 16C/32T Linux, **1 thread per run** pinned across 8 dedicated physical cores, $T_{\max} = 5\;\text{s}$, PAR-2 penalty $10,000\;\text{ms}$). All solvers received identical uncompressed flat `.cnf` inputs; **100% of all 72 instances** were run (no subsampling), every Frobenius SAT model was independently verified against 100% of input clauses, and **0 verdict disagreements** occurred across all solvers.

| Instance | Verdict | Frobenius 1C | [CaDiCaL](https://github.com/arminbiere/cadical) 3.1.0 | [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18.0 | [`dense-solver 0.0.4`](https://github.com/libdense/dense-solver) | [Kissat](https://github.com/arminbiere/kissat) 4.0.4 |
|---|:---:|---:|---:|---:|---:|---:|
| `aim-100-1_6-no-1` | UNSAT | 3.69 ms | 2.82 ms | 27.49 ms | **1.87 ms** | 3.03 ms |
| `aim-100-1_6-no-2` | UNSAT | 4.63 ms | 3.05 ms | 29.58 ms | **1.87 ms** | 3.02 ms |
| `aim-100-1_6-no-3` | UNSAT | 3.82 ms | 3.32 ms | 26.84 ms | **1.71 ms** | 2.77 ms |
| `aim-100-1_6-no-4` | UNSAT | 3.39 ms | 4.26 ms | 40.76 ms | **1.92 ms** | 3.61 ms |
| `aim-100-1_6-yes1-1` | SAT | 3.31 ms | 3.30 ms | 28.83 ms | **1.86 ms** | 2.72 ms |
| `aim-100-1_6-yes1-2` | SAT | 3.46 ms | 3.13 ms | 21.83 ms | 1.60 ms | **1.56 ms** |
| `aim-100-1_6-yes1-3` | SAT | 4.29 ms | 3.49 ms | 22.22 ms | **1.79 ms** | 2.92 ms |
| `aim-100-1_6-yes1-4` | SAT | 2.76 ms | 3.23 ms | 22.35 ms | **1.70 ms** | 2.33 ms |
| `aim-100-2_0-no-1` | UNSAT | 3.58 ms | 3.06 ms | 21.84 ms | **1.86 ms** | 1.87 ms |
| `aim-100-2_0-no-2` | UNSAT | 4.49 ms | 2.52 ms | 21.56 ms | **1.41 ms** | 4.46 ms |
| `aim-100-2_0-no-3` | UNSAT | 3.28 ms | 2.71 ms | 21.04 ms | **1.57 ms** | 1.92 ms |
| `aim-100-2_0-no-4` | UNSAT | 3.74 ms | 3.03 ms | 21.94 ms | 2.29 ms | **2.10 ms** |
| `aim-100-2_0-yes1-1` | SAT | 3.25 ms | 2.70 ms | 20.92 ms | **1.55 ms** | 1.84 ms |
| `aim-100-2_0-yes1-2` | SAT | 4.04 ms | 3.03 ms | 20.73 ms | **1.88 ms** | 2.07 ms |
| `aim-100-2_0-yes1-3` | SAT | 3.32 ms | 2.41 ms | 20.03 ms | **1.54 ms** | 1.69 ms |
| `aim-100-2_0-yes1-4` | SAT | 3.87 ms | 3.13 ms | 21.79 ms | **1.71 ms** | 1.99 ms |
| `aim-100-3_4-yes1-1` | SAT | 2.61 ms | 2.41 ms | 19.41 ms | **1.52 ms** | 2.35 ms |
| `aim-100-3_4-yes1-2` | SAT | **2.29 ms** | 3.63 ms | 27.08 ms | 2.37 ms | 3.00 ms |
| `aim-100-3_4-yes1-3` | SAT | 2.74 ms | 2.73 ms | 26.27 ms | **1.99 ms** | 5.92 ms |
| `aim-100-3_4-yes1-4` | SAT | 2.96 ms | 2.56 ms | 27.23 ms | **2.23 ms** | 3.90 ms |
| `aim-100-6_0-yes1-1` | SAT | 2.81 ms | 2.36 ms | 5.29 ms | **1.55 ms** | 2.61 ms |
| `aim-100-6_0-yes1-2` | SAT | 1.77 ms | 2.29 ms | 5.60 ms | **1.49 ms** | 3.02 ms |
| `aim-100-6_0-yes1-3` | SAT | 2.01 ms | 2.47 ms | 5.08 ms | **1.56 ms** | 2.14 ms |
| `aim-100-6_0-yes1-4` | SAT | 2.64 ms | 3.25 ms | 5.57 ms | **1.58 ms** | 2.52 ms |
| `aim-200-1_6-no-1` | UNSAT | 3.75 ms | 2.39 ms | 30.58 ms | **1.89 ms** | 4.66 ms |
| `aim-200-1_6-no-2` | UNSAT | 3.27 ms | 2.27 ms | 23.89 ms | **1.56 ms** | 4.31 ms |
| `aim-200-1_6-no-3` | UNSAT | 3.50 ms | **2.46 ms** | 40.91 ms | 3.18 ms | 4.99 ms |
| `aim-200-1_6-no-4` | UNSAT | 3.39 ms | 2.29 ms | 24.83 ms | **1.47 ms** | 2.57 ms |
| `aim-200-1_6-yes1-1` | SAT | 3.09 ms | 2.40 ms | 24.50 ms | **1.93 ms** | 2.38 ms |
| `aim-200-1_6-yes1-2` | SAT | 4.13 ms | 3.32 ms | 22.48 ms | **1.97 ms** | 2.48 ms |
| `aim-200-1_6-yes1-3` | SAT | 3.75 ms | 3.13 ms | 23.77 ms | **1.77 ms** | 3.39 ms |
| `aim-200-1_6-yes1-4` | SAT | 4.19 ms | 3.18 ms | 23.24 ms | **2.06 ms** | 3.05 ms |
| `aim-200-2_0-no-1` | UNSAT | 3.70 ms | 3.30 ms | 27.34 ms | **1.54 ms** | 6.21 ms |
| `aim-200-2_0-no-2` | UNSAT | 5.03 ms | 3.32 ms | 26.70 ms | **1.56 ms** | 6.65 ms |
| `aim-200-2_0-no-3` | UNSAT | 3.90 ms | 2.44 ms | 26.24 ms | **1.61 ms** | 6.58 ms |
| `aim-200-2_0-no-4` | UNSAT | 3.45 ms | 2.65 ms | 20.87 ms | **1.67 ms** | 1.85 ms |
| `aim-200-2_0-yes1-1` | SAT | 4.29 ms | 2.93 ms | 25.41 ms | **2.47 ms** | 2.49 ms |
| `aim-200-2_0-yes1-2` | SAT | 4.18 ms | 3.15 ms | 26.31 ms | **2.10 ms** | 2.62 ms |
| `aim-200-2_0-yes1-3` | SAT | 4.25 ms | 2.68 ms | 23.64 ms | **2.56 ms** | 2.68 ms |
| `aim-200-2_0-yes1-4` | SAT | 4.25 ms | 2.98 ms | 26.46 ms | **1.99 ms** | 2.56 ms |
| `aim-200-3_4-yes1-1` | SAT | 2.27 ms | 4.33 ms | 39.59 ms | **1.94 ms** | 4.61 ms |
| `aim-200-3_4-yes1-2` | SAT | 3.86 ms | 3.91 ms | 29.48 ms | **2.45 ms** | 15.08 ms |
| `aim-200-3_4-yes1-3` | SAT | 4.00 ms | 4.73 ms | 28.36 ms | **2.10 ms** | 14.30 ms |
| `aim-200-3_4-yes1-4` | SAT | 4.42 ms | 3.41 ms | 27.40 ms | **1.86 ms** | 16.03 ms |
| `aim-200-6_0-yes1-1` | SAT | 2.35 ms | 4.12 ms | 11.80 ms | **2.25 ms** | 4.64 ms |
| `aim-200-6_0-yes1-2` | SAT | **2.69 ms** | 3.67 ms | 16.78 ms | 3.30 ms | 5.62 ms |
| `aim-200-6_0-yes1-3` | SAT | 4.49 ms | 3.57 ms | 9.45 ms | **2.16 ms** | 4.63 ms |
| `aim-200-6_0-yes1-4` | SAT | 4.34 ms | 4.11 ms | 17.04 ms | **2.57 ms** | 5.79 ms |
| `aim-50-1_6-no-1` | UNSAT | 2.60 ms | 2.18 ms | 23.35 ms | **1.51 ms** | 2.08 ms |
| `aim-50-1_6-no-2` | UNSAT | 3.10 ms | 2.33 ms | 21.69 ms | **1.58 ms** | 2.12 ms |
| `aim-50-1_6-no-3` | UNSAT | 2.60 ms | 2.65 ms | 29.04 ms | **1.56 ms** | 1.90 ms |
| `aim-50-1_6-no-4` | UNSAT | 3.05 ms | 2.51 ms | 21.42 ms | **1.49 ms** | 1.64 ms |
| `aim-50-1_6-yes1-1` | SAT | 2.61 ms | 3.20 ms | 20.62 ms | 1.85 ms | **1.64 ms** |
| `aim-50-1_6-yes1-2` | SAT | 2.85 ms | 2.32 ms | 20.66 ms | 1.62 ms | **1.51 ms** |
| `aim-50-1_6-yes1-3` | SAT | 2.11 ms | 3.25 ms | 27.68 ms | 1.53 ms | **1.40 ms** |
| `aim-50-1_6-yes1-4` | SAT | 3.01 ms | 2.62 ms | 21.07 ms | **1.82 ms** | 1.91 ms |
| `aim-50-2_0-no-1` | UNSAT | 2.85 ms | 2.03 ms | 24.83 ms | **1.48 ms** | 1.78 ms |
| `aim-50-2_0-no-2` | UNSAT | 2.83 ms | 4.04 ms | 20.75 ms | **1.41 ms** | 1.73 ms |
| `aim-50-2_0-no-3` | UNSAT | 3.17 ms | 2.76 ms | 21.27 ms | **1.68 ms** | 2.07 ms |
| `aim-50-2_0-no-4` | UNSAT | 3.01 ms | 2.99 ms | 22.57 ms | **1.68 ms** | 1.98 ms |
| `aim-50-2_0-yes1-1` | SAT | 3.09 ms | 2.48 ms | 21.60 ms | **1.62 ms** | 1.65 ms |
| `aim-50-2_0-yes1-2` | SAT | 3.00 ms | 3.27 ms | 10.35 ms | **1.39 ms** | 1.51 ms |
| `aim-50-2_0-yes1-3` | SAT | 3.78 ms | 2.74 ms | 20.60 ms | **1.64 ms** | 1.74 ms |
| `aim-50-2_0-yes1-4` | SAT | 2.96 ms | 2.19 ms | 29.87 ms | **1.74 ms** | 1.78 ms |
| `aim-50-3_4-yes1-1` | SAT | 3.49 ms | 2.43 ms | 25.76 ms | **1.80 ms** | 2.16 ms |
| `aim-50-3_4-yes1-2` | SAT | 1.99 ms | 2.49 ms | 11.05 ms | **1.74 ms** | 1.93 ms |
| `aim-50-3_4-yes1-3` | SAT | 2.19 ms | 2.64 ms | 7.94 ms | **1.49 ms** | 1.70 ms |
| `aim-50-3_4-yes1-4` | SAT | 2.11 ms | 2.41 ms | 4.88 ms | **1.34 ms** | 2.12 ms |
| `aim-50-6_0-yes1-1` | SAT | 2.59 ms | 3.12 ms | 7.30 ms | **1.63 ms** | 1.93 ms |
| `aim-50-6_0-yes1-2` | SAT | 2.69 ms | 3.04 ms | 6.20 ms | **1.97 ms** | 2.14 ms |
| `aim-50-6_0-yes1-3` | SAT | 1.96 ms | 2.21 ms | 4.83 ms | **1.62 ms** | 2.01 ms |
| `aim-50-6_0-yes1-4` | SAT | 2.09 ms | 2.37 ms | 4.89 ms | **1.51 ms** | 1.97 ms |
| **Total (72 files, PAR-2)** | **72/72** | 72/72 — 235.0 ms *(1.79x)* | 72/72 — 211.9 ms *(1.62x)* | 72/72 — 1,538.6 ms *(11.74x)* | **72/72 — 131.1 ms** *(fastest)* | 72/72 — 239.9 ms *(1.83x)* |

<!-- BEGIN_STRUCTURAL_ANALYSIS -->
## Phase-Transition & Structural Analysis

*Auto-generated by [`../src/analyze_benchmarks.py`](../src/analyze_benchmarks.py). Position relative to the critical phase transition is measured by $\rho_{\mathrm{crit}} = \frac{1}{n}\sum_k m_k / \alpha_c(k)$ (exact $\alpha/\alpha_c(k)$ for pure $k$-SAT; effective critical threshold $\alpha_c^{\mathrm{eff}} = \alpha/\rho_{\mathrm{crit}}$; `Under` $<0.90\times$, `Near-crit` $0.90\text{--}1.10\times$, `Over` $>1.10\times$), alongside Gent–Walsh annealed constrainedness $\kappa = -\frac{1}{n}\sum_i \log_2(1-2^{-k_i})$ (AAAI 1996), clause-length profile ($\bar{k}$, `%Bin`, `%Horn`), variable-degree CV ($\sigma_d/\bar{d}$, uniformity vs. hub skew), and extracted native XOR parity clauses.*

| Group / Family | Files | Med $n$ | Med $m$ | $\alpha=m/n$ (Med) | $\alpha_c^{\mathrm{eff}}$ (Med) | $\rho_{\mathrm{crit}}$ Med [Min–Max] (Regime) | Med $\kappa$ | Med $\bar{k}$ | Bin% | Horn% | Deg CV | Total XORs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `aim-100` | 24 | 100 | 200 | 2.00 | 4.21 | **0.47x** [0.37x–1.44x] (Under) | 0.39 | 3.00 | 0% | 50% | 0.03 | 0 |
| `aim-200` | 24 | 200 | 400 | 2.00 | 4.22 | **0.47x** [0.37x–1.44x] (Under) | 0.39 | 3.00 | 0% | 50% | 0.03 | 0 |
| `aim-50` | 24 | 50 | 100 | 2.00 | 4.24 | **0.47x** [0.37x–1.45x] (Under) | 0.39 | 3.00 | 0% | 49% | 0.04 | 0 |

**Collection Phase-Transition Summary (72 instances, 4 formats: 72 CNF / 72 AIG / 72 XCNF / 72 ANF):** median $\rho_{\mathrm{crit}} = 0.47\times$ (range `0.37x–1.45x`), median $\kappa = 0.39$, regime split **60 Under / 0 Near-critical / 12 Over**, total extracted native XOR parity clauses = **0**, total ANF equations = **23,162**.
<!-- END_STRUCTURAL_ANALYSIS -->

## References

- H. H. Hoos and T. Stützle, *"SATLIB: An Online Resource for Research on SAT"*, SAT 2000, IOS Press, pp. 283–292 ([`cs.ubc.ca/~hoos/SATLIB/`](https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html)).
- D. S. Johnson and M. A. Trick (eds.), *Cliques, Coloring, and Satisfiability: Second DIMACS Implementation Challenge*, DIMACS Series vol. 26, AMS, 1996.
