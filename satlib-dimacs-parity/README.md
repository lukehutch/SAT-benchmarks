# SATLIB — Parity Learning `par8`/`par16`/`par32` (full) (`satlib-dimacs-parity`)

## Provenance & Credit

- **Recommended by:** [`@jasonslenderman`](https://twitter.com/jasonslenderman) (Twitter/X)
- **Upstream Archive:** [SATLIB — Benchmark Problems (UBC)](https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html)
- **SATLIB Curators:** Holger H. Hoos and Thomas Stützle (University of British Columbia / TU Darmstadt)
- **Family Contributors:** James M. Crawford, Michael Kearns, and Robert Schapire
- **License:** Classic public scientific benchmark collection redistributed by UBC SATLIB for academic SAT research; no separate upstream `LICENSE` file is bundled in the archives.
- **Format Hygiene:** Legacy SATLIB trailing `%` / `0` EOF sentinels were stripped and wrapped multi-line clauses normalized to canonical 1-clause-per-line DIMACS CNF so every modern SAT solver parses all files cleanly.
- **Full SATLIB Archive Manifest:** [`../satlib-archive-uris/`](../satlib-archive-uris/README.md) (all 97 official UBC SATLIB `.tar.gz` archive URLs; Pretolani's `PRET` formulas live in [`../pretolani-pret/`](../pretolani-pret/README.md)).

## Problem Description

All 30 parity-learning SAT benchmarks (`par8`, `par16`, `par32`, original & compressed) encoding learning parity functions with noise.

## Corpus & Data Sizes (Four Formats)

- **`cnf-orig/`** — 30 original native **DIMACS `.cnf.xz`** files (252.4 KB).
- **`aig-converted/`** — 30 exact **Binary AIGER 1.9 `.aig.xz`** conversions (345.3 KB, verified via [Berkeley ABC](https://github.com/berkeley-abc/abc) `read_aiger`).
- **`xcnf-converted/`** — 30 lossless **[CryptoMiniSat](https://github.com/msoos/cryptominisat) `.xcnf.xz`** conversions (125.0 KB, `18,548` extracted native XOR parity clauses).
- **`anf-converted/`** — 30 lossless linear-size **DIMACS-ANF `.anf.xz`** conversions (189.7 KB, generated via [`../src/to_anf.py`](../src/to_anf.py)).
- **`src/`** — Standalone converters (`cnf2aig.py`, `cnf2xcnf.py`).

| Format | Directory | Files | Key Dimensions (Range) | Compressed Size |
|---|---|---:|---|---:|
| **DIMACS CNF (origin)** | `cnf-orig/` | 30 | Vars: 64–3,176; Clauses: 254–10,325 | 252.4 KB |
| **Binary AIGER 1.9** | `aig-converted/` | 30 | Inputs: 64–3,176; ANDs: 700–27,244 | 345.3 KB |
| **[CryptoMiniSat](https://github.com/msoos/cryptominisat) XCNF** | `xcnf-converted/` | 30 | Native XOR clauses total: 18,548 | 125.0 KB |
| **DIMACS-ANF** | `anf-converted/` | 30 | Vars: 64–3,176; Eqs: 86–5,645 (deg ≤ 3) | 189.7 KB |
| **Total (4 Formats, Status: SAT)** | | **120** | | **912.5 KB** |

## Comparative 1-Core Benchmark Results (All 30 Instances, Flat `.cnf`, $T_{\max} = 5\;\text{s}$)

- **Hardware & Protocol:** Same machine (**AMD Ryzen 9 5950X**, 16C/32T Linux, **1 thread per run** pinned across 8 dedicated physical cores, $T_{\max} = 5\;\text{s}$, PAR-2 penalty $10,000\;\text{ms}$). All solvers received identical uncompressed flat `.cnf` inputs; **100% of all 30 instances** were run (no subsampling), every Frobenius SAT model was independently verified against 100% of input clauses, and **0 verdict disagreements** occurred across all solvers.

| Instance | Verdict | Frobenius 1C | [CaDiCaL](https://github.com/arminbiere/cadical) 3.1.0 | [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18.0 | [`dense-solver 0.0.4`](https://github.com/libdense/dense-solver) | [Kissat](https://github.com/arminbiere/kissat) 4.0.4 |
|---|:---:|---:|---:|---:|---:|---:|
| `par16-1` | SAT | **7.24 ms** | 44.80 ms | 54.69 ms | 30.65 ms | 42.56 ms |
| `par16-1-c` | SAT | **2.40 ms** | 53.62 ms | 47.60 ms | 11.13 ms | 20.36 ms |
| `par16-2` | SAT | 5.51 ms | 20.10 ms | 62.20 ms | **5.40 ms** | 70.47 ms |
| `par16-2-c` | SAT | **2.68 ms** | 79.20 ms | 57.34 ms | 53.90 ms | 43.00 ms |
| `par16-3` | SAT | **17.73 ms** | 58.73 ms | 56.41 ms | 21.50 ms | 24.98 ms |
| `par16-3-c` | SAT | **3.20 ms** | 23.98 ms | 50.99 ms | 25.51 ms | 18.74 ms |
| `par16-4` | SAT | 24.60 ms | **8.91 ms** | 52.45 ms | 60.16 ms | 38.70 ms |
| `par16-4-c` | SAT | **2.82 ms** | 40.37 ms | 49.08 ms | 7.01 ms | 11.09 ms |
| `par16-5` | SAT | **10.94 ms** | 71.23 ms | 56.37 ms | 43.08 ms | 14.60 ms |
| `par16-5-c` | SAT | **2.95 ms** | 77.75 ms | 53.22 ms | 33.45 ms | 52.94 ms |
| `par32-1` | SAT | >5 s | >5 s | **1,083.24 ms** | >5 s | >5 s |
| `par32-1-c` | SAT | >5 s | >5 s | **1,300.94 ms** | >5 s | >5 s |
| `par32-2` | SAT | >5 s | >5 s | **533.68 ms** | >5 s | >5 s |
| `par32-2-c` | SAT | >5 s | >5 s | **1,267.72 ms** | >5 s | >5 s |
| `par32-3` | SAT | >5 s | >5 s | **685.67 ms** | >5 s | >5 s |
| `par32-3-c` | SAT | >5 s | >5 s | **1,599.42 ms** | >5 s | >5 s |
| `par32-4` | SAT | >5 s | >5 s | **403.59 ms** | >5 s | >5 s |
| `par32-4-c` | SAT | >5 s | >5 s | **1,085.10 ms** | >5 s | >5 s |
| `par32-5` | SAT | >5 s | >5 s | **418.33 ms** | >5 s | >5 s |
| `par32-5-c` | SAT | >5 s | >5 s | **1,981.89 ms** | >5 s | >5 s |
| `par8-1` | SAT | 2.37 ms | 2.66 ms | 25.87 ms | 2.61 ms | **1.62 ms** |
| `par8-1-c` | SAT | 2.51 ms | 2.46 ms | 23.13 ms | **1.68 ms** | 2.44 ms |
| `par8-2` | SAT | 2.68 ms | 2.61 ms | 27.67 ms | **2.47 ms** | 2.72 ms |
| `par8-2-c` | SAT | 2.45 ms | 2.43 ms | 23.09 ms | **1.69 ms** | 2.46 ms |
| `par8-3` | SAT | 3.03 ms | 2.66 ms | 28.05 ms | **2.57 ms** | 3.17 ms |
| `par8-3-c` | SAT | 2.57 ms | 2.40 ms | 25.14 ms | **1.72 ms** | 2.92 ms |
| `par8-4` | SAT | 2.98 ms | 2.85 ms | 29.08 ms | **2.62 ms** | 3.08 ms |
| `par8-4-c` | SAT | 2.52 ms | 2.58 ms | 20.46 ms | **1.67 ms** | 2.83 ms |
| `par8-5` | SAT | 3.57 ms | **2.78 ms** | 26.20 ms | 2.97 ms | 2.94 ms |
| `par8-5-c` | SAT | 2.33 ms | 2.49 ms | 21.82 ms | **1.58 ms** | 2.74 ms |
| **Total (30 files, PAR-2)** | **30/30** | 20/30 — 100,107.1 ms *(8.98x)* | 20/30 — 100,504.6 ms *(9.01x)* | **30/30 — 11,150.4 ms** *(fastest)* | 20/30 — 100,313.4 ms *(9.00x)* | 20/30 — 100,364.4 ms *(9.00x)* |

<!-- BEGIN_STRUCTURAL_ANALYSIS -->
## Phase-Transition & Structural Analysis

*Auto-generated by [`../src/analyze_benchmarks.py`](../src/analyze_benchmarks.py). Position relative to the critical phase transition is measured by $\rho_{\mathrm{crit}} = \frac{1}{n}\sum_k m_k / \alpha_c(k)$ (exact $\alpha/\alpha_c(k)$ for pure $k$-SAT; effective critical threshold $\alpha_c^{\mathrm{eff}} = \alpha/\rho_{\mathrm{crit}}$; `Under` $<0.90\times$, `Near-crit` $0.90\text{--}1.10\times$, `Over` $>1.10\times$), alongside Gent–Walsh annealed constrainedness $\kappa = -\frac{1}{n}\sum_i \log_2(1-2^{-k_i})$ (AAAI 1996), clause-length profile ($\bar{k}$, `%Bin`, `%Horn`), variable-degree CV ($\sigma_d/\bar{d}$, uniformity vs. hub skew), and extracted native XOR parity clauses.*

| Group / Family | Files | Med $n$ | Med $m$ | $\alpha=m/n$ (Med) | $\alpha_c^{\mathrm{eff}}$ (Med) | $\rho_{\mathrm{crit}}$ Med [Min–Max] (Regime) | Med $\kappa$ | Med $\bar{k}$ | Bin% | Horn% | Deg CV | Total XORs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `par16-1` | 2 | 666 | 2,287 | 3.62 | 2.66 | **1.40x** [1.23x–1.57x] (Over) | 0.88 | 2.78 | 20% | 44% | 0.91 | 735 |
| `par16-2` | 2 | 682 | 2,383 | 3.66 | 2.74 | **1.37x** [1.20x–1.53x] (Over) | 0.87 | 2.80 | 18% | 43% | 1.00 | 799 |
| `par16-3` | 2 | 674 | 2,338 | 3.64 | 2.70 | **1.38x** [1.21x–1.55x] (Over) | 0.88 | 2.79 | 19% | 43% | 0.96 | 769 |
| `par16-4` | 2 | 669 | 2,308 | 3.63 | 2.68 | **1.39x** [1.22x–1.56x] (Over) | 0.88 | 2.78 | 19% | 44% | 0.94 | 749 |
| `par16-5` | 2 | 678 | 2,359 | 3.65 | 2.72 | **1.38x** [1.21x–1.54x] (Over) | 0.88 | 2.79 | 19% | 43% | 0.98 | 783 |
| `par32-1` | 2 | 2,245 | 7,765 | 3.62 | 2.79 | **1.34x** [1.15x–1.53x] (Over) | 0.85 | 2.80 | 18% | 42% | 1.53 | 2,706 |
| `par32-2` | 2 | 2,239 | 7,729 | 3.61 | 2.78 | **1.34x** [1.15x–1.53x] (Over) | 0.85 | 2.80 | 19% | 42% | 1.52 | 2,682 |
| `par32-3` | 2 | 2,250 | 7,795 | 3.62 | 2.80 | **1.34x** [1.15x–1.52x] (Over) | 0.85 | 2.80 | 18% | 41% | 1.54 | 2,726 |
| `par32-4` | 2 | 2,254 | 7,819 | 3.62 | 2.80 | **1.34x** [1.15x–1.52x] (Over) | 0.85 | 2.81 | 18% | 42% | 1.55 | 2,742 |
| `par32-5` | 2 | 2,257 | 7,837 | 3.62 | 2.81 | **1.33x** [1.15x–1.52x] (Over) | 0.85 | 2.81 | 18% | 41% | 1.55 | 2,754 |
| `par8-1` | 2 | 207 | 701 | 3.63 | 2.57 | **1.44x** [1.29x–1.59x] (Over) | 0.91 | 2.76 | 20% | 48% | 0.55 | 209 |
| `par8-2` | 2 | 209 | 713 | 3.64 | 2.61 | **1.43x** [1.27x–1.58x] (Over) | 0.90 | 2.77 | 20% | 47% | 0.59 | 217 |
| `par8-3` | 2 | 212 | 734 | 3.66 | 2.68 | **1.40x** [1.24x–1.56x] (Over) | 0.90 | 2.78 | 18% | 45% | 0.63 | 231 |
| `par8-4` | 2 | 208 | 710 | 3.64 | 2.60 | **1.43x** [1.27x–1.58x] (Over) | 0.90 | 2.76 | 20% | 45% | 0.58 | 215 |
| `par8-5` | 2 | 212 | 734 | 3.66 | 2.68 | **1.40x** [1.24x–1.56x] (Over) | 0.90 | 2.78 | 18% | 45% | 0.65 | 231 |

**Collection Phase-Transition Summary (30 instances, 4 formats: 30 CNF / 30 AIG / 30 XCNF / 30 ANF):** median $\rho_{\mathrm{crit}} = 1.40\times$ (range `1.15x–1.59x`), median $\kappa = 0.87$, regime split **0 Under / 0 Near-critical / 30 Over**, total extracted native XOR parity clauses = **18,548**, total ANF equations = **52,790**.
<!-- END_STRUCTURAL_ANALYSIS -->

## References

- H. H. Hoos and T. Stützle, *"SATLIB: An Online Resource for Research on SAT"*, SAT 2000, IOS Press, pp. 283–292 ([`cs.ubc.ca/~hoos/SATLIB/`](https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html)).
- D. S. Johnson and M. A. Trick (eds.), *Cliques, Coloring, and Satisfiability: Second DIMACS Implementation Challenge*, DIMACS Series vol. 26, AMS, 1996.
