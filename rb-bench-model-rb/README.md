# Model RB Forced-Satisfiable SAT Benchmarks (`RB-bench` / BHOSLIB)

## Provenance & Credit

- **Recommended by:** [`@merlin_numa`](https://twitter.com/merlin_numa) (Twitter/X)
- **Author:** Prof. Ke Xu (Beihang University) and collaborators
- **Upstream Homepage:** [RB-bench — Prof. Ke Xu's Homepage](https://rb-bench.github.io/) ([Forced Satisfiable CSP and SAT Benchmarks of Model RB](https://rb-bench.github.io/forced-sat-csp/))
- **License:** Public academic benchmark collection distributed on `rb-bench.github.io` and used in SAT Competitions since 2004; no separate upstream `LICENSE` file is bundled in the archives.
- **Primary Papers:**
  - K. Xu and W. Li, *"Exact Phase Transitions in Random Constraint Satisfaction Problems"*, Journal of Artificial Intelligence Research (JAIR), 12:93–103 (2000).
  - K. Xu, F. Boussemart, F. Hemery, and C. Lecoutre, *"Random Constraint Satisfaction: Easy Generation of Hard (Satisfiable) Instances"*, Artificial Intelligence (AIJ), 171(8–9):514–534 (2007); earlier version in IJCAI 2005, pp. 337–342.
  - K. Xu and G. Zhou, *"SAT Requires Exhaustive Search"*, Frontiers of Computer Science, 19, 1912405 (2025).

## Problem Description

Model RB generates random binary Constraint Satisfaction Problems (CSPs) whose domain size grows polynomially with the number of variables ($d = n^\alpha$), avoiding the trivial asymptotic unsatisfiability of classical fixed-domain random CSP models and exhibiting an exact, provable phase transition.

The **40 forced-satisfiable SAT benchmarks** (`frb30-15` through `frb59-26`) are direct CNF encodings of Model RB CSPs with $k = 2$, $\alpha = 0.8$, and $r = 0.8 / (\ln 4 - \ln 3)$, located precisely at the critical phase-transition threshold with a hidden planted solution. Every instance is **guaranteed SAT**, yet because the constraint structure hides the planted assignment among exponentially many near-solutions, larger sizes (`frb45`–`frb59`) remain very difficult for complete CDCL solvers.

## Corpus & Data Sizes (Four Formats)

- **`cnf-orig/`:** All 40 forced-SAT `.cnf.xz` files (`4.98 MB` xz-compressed) across all 8 size classes.
- **`aig-converted/`:** 40 exact Binary AIGER 1.9 `.aig.xz` conversions (`5.80 MB` xz-compressed, all 40/40 verified via [Berkeley ABC](https://github.com/berkeley-abc/abc) `read_aiger`).
- **`xcnf-converted/`:** 40 lossless [CryptoMiniSat](https://github.com/msoos/cryptominisat) `.xcnf.xz` conversions (`4.80 MB`).
- **`anf-converted/`:** 40 lossless linear-size DIMACS-ANF `.anf.xz` conversions (`6.54 MB`, degree $\le 3$, generated via [`../src/to_anf.py`](../src/to_anf.py)).
- **`src/`:** Standalone converters (`cnf2aig.py`, `cnf2xcnf.py`).

| Family | Instances | Status | Vars ($n \cdot d$) | Clauses | `.cnf.xz` Size (5 files) | 4-Format Files |
|---|---:|:---:|---:|---:|---:|---:|
| `frb30-15-1..5` | 5 | SAT | 450 | 19,084 | 160.5 KB | 20 |
| `frb35-17-1..5` | 5 | SAT | 595 | 29,707 | 244.5 KB | 20 |
| `frb40-19-1..5` | 5 | SAT | 760 | 43,780 | 365.8 KB | 20 |
| `frb45-21-1..5` | 5 | SAT | 945 | 61,855 | 509.8 KB | 20 |
| `frb50-23-1..5` | 5 | SAT | 1,150 | 84,508 | 739.7 KB | 20 |
| `frb53-24-1..5` | 5 | SAT | 1,272 | 98,921 | 874.8 KB | 20 |
| `frb56-25-1..5` | 5 | SAT | 1,400 | 114,668 | 1013.3 KB | 20 |
| `frb59-26-1..5` | 5 | SAT | 1,534 | 132,295 | 1.16 MB | 20 |
| **Total** | **40** | **40 SAT** | **450–1,534** | **19,084–132,295** | **4.98 MB** | **160** |

## Comparative 1-Core Benchmark Results (All 40 Instances, Flat `.cnf`, $T_{\max} = 5\;\text{s}$)

- **Hardware & Protocol:** Same machine (**AMD Ryzen 9 5950X**, 16C/32T Linux, **1 thread per run** pinned across 8 dedicated physical cores, $T_{\max} = 5\;\text{s}$, PAR-2 penalty $10,000\;\text{ms}$). All solvers received identical uncompressed flat `.cnf` inputs; **100% of all 40 instances** were run (no subsampling), every Frobenius SAT model was independently verified against 100% of input clauses, and **0 verdict disagreements** occurred across all solvers.

| Instance | Verdict | Frobenius 1C | [CaDiCaL](https://github.com/arminbiere/cadical) 3.1.0 | [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18.0 | [dense-solver](https://github.com/libdense/dense-solver) 0.0.4 | [Kissat](https://github.com/arminbiere/kissat) 4.0.4 |
|---|:---:|---:|---:|---:|---:|---:|
| `frb30-15-1` | SAT | 603.47 ms | 360.71 ms | 499.53 ms | 387.16 ms | **117.22 ms** |
| `frb30-15-2` | SAT | 74.31 ms | 55.16 ms | 753.11 ms | **53.33 ms** | 347.67 ms |
| `frb30-15-3` | SAT | **47.73 ms** | 516.99 ms | 592.00 ms | 208.16 ms | 51.01 ms |
| `frb30-15-4` | SAT | 528.56 ms | 577.01 ms | 640.88 ms | **45.47 ms** | 384.63 ms |
| `frb30-15-5` | SAT | 76.69 ms | 24.31 ms | 554.68 ms | **11.22 ms** | 103.28 ms |
| `frb35-17-1` | SAT | 2,528.89 ms | 1,929.43 ms | 2,622.37 ms | 988.37 ms | **554.92 ms** |
| `frb35-17-2` | SAT | >5 s | **1,872.10 ms** | >5 s | >5 s | 2,390.83 ms |
| `frb35-17-3` | SAT | 4,171.17 ms | **485.21 ms** | 666.91 ms | 791.30 ms | 1,703.06 ms |
| `frb35-17-4` | SAT | 881.11 ms | 1,043.66 ms | 1,122.46 ms | 1,764.75 ms | **714.48 ms** |
| `frb35-17-5` | SAT | >5 s | **505.99 ms** | 607.48 ms | 933.50 ms | >5 s |
| `frb40-19-1` | SAT | 1,431.96 ms | 3,669.19 ms | **637.06 ms** | 2,344.61 ms | 4,985.73 ms |
| `frb40-19-2` | TIMEOUT | >5 s | >5 s | >5 s | >5 s | >5 s |
| `frb40-19-3` | SAT | >5 s | **2,688.17 ms** | >5 s | >5 s | 4,955.80 ms |
| `frb40-19-4` | TIMEOUT | >5 s | >5 s | >5 s | >5 s | >5 s |
| `frb40-19-5` | TIMEOUT | >5 s | >5 s | >5 s | >5 s | >5 s |
| `frb45-21-1` | TIMEOUT | >5 s | >5 s | >5 s | >5 s | >5 s |
| `frb45-21-2` | TIMEOUT | >5 s | >5 s | >5 s | >5 s | >5 s |
| `frb45-21-3` | TIMEOUT | >5 s | >5 s | >5 s | >5 s | >5 s |
| `frb45-21-4` | TIMEOUT | >5 s | >5 s | >5 s | >5 s | >5 s |
| `frb45-21-5` | TIMEOUT | >5 s | >5 s | >5 s | >5 s | >5 s |
| `frb50-23-1` | TIMEOUT | >5 s | >5 s | >5 s | >5 s | >5 s |
| `frb50-23-2` | TIMEOUT | >5 s | >5 s | >5 s | >5 s | >5 s |
| `frb50-23-3` | TIMEOUT | >5 s | >5 s | >5 s | >5 s | >5 s |
| `frb50-23-4` | TIMEOUT | >5 s | >5 s | >5 s | >5 s | >5 s |
| `frb50-23-5` | TIMEOUT | >5 s | >5 s | >5 s | >5 s | >5 s |
| `frb53-24-1` | TIMEOUT | >5 s | >5 s | >5 s | >5 s | >5 s |
| `frb53-24-2` | TIMEOUT | >5 s | >5 s | >5 s | >5 s | >5 s |
| `frb53-24-3` | TIMEOUT | >5 s | >5 s | >5 s | >5 s | >5 s |
| `frb53-24-4` | TIMEOUT | >5 s | >5 s | >5 s | >5 s | >5 s |
| `frb53-24-5` | TIMEOUT | >5 s | >5 s | >5 s | >5 s | >5 s |
| `frb56-25-1` | TIMEOUT | >5 s | >5 s | >5 s | >5 s | >5 s |
| `frb56-25-2` | TIMEOUT | >5 s | >5 s | >5 s | >5 s | >5 s |
| `frb56-25-3` | TIMEOUT | >5 s | >5 s | >5 s | >5 s | >5 s |
| `frb56-25-4` | TIMEOUT | >5 s | >5 s | >5 s | >5 s | >5 s |
| `frb56-25-5` | TIMEOUT | >5 s | >5 s | >5 s | >5 s | >5 s |
| `frb59-26-1` | TIMEOUT | >5 s | >5 s | >5 s | >5 s | >5 s |
| `frb59-26-2` | TIMEOUT | >5 s | >5 s | >5 s | >5 s | >5 s |
| `frb59-26-3` | TIMEOUT | >5 s | >5 s | >5 s | >5 s | >5 s |
| `frb59-26-4` | TIMEOUT | >5 s | >5 s | >5 s | >5 s | >5 s |
| `frb59-26-5` | TIMEOUT | >5 s | >5 s | >5 s | >5 s | >5 s |
| **Total (40 files, PAR-2)** | **12/40** | 9/40 — 320,343.9 ms *(1.09x)* | **12/40 — 293,727.9 ms** *(fastest)* | 10/40 — 308,696.5 ms *(1.05x)* | 10/40 — 307,527.9 ms *(1.05x)* | 11/40 — 306,308.6 ms *(1.04x)* |

<!-- BEGIN_STRUCTURAL_ANALYSIS -->
## Phase-Transition & Structural Analysis

*Auto-generated by [`../src/analyze_benchmarks.py`](../src/analyze_benchmarks.py). Position relative to the critical phase transition is measured by $\rho_{\mathrm{crit}} = \frac{1}{n}\sum_k m_k / \alpha_c(k)$ (exact $\alpha/\alpha_c(k)$ for pure $k$-SAT; effective critical threshold $\alpha_c^{\mathrm{eff}} = \alpha/\rho_{\mathrm{crit}}$; `Under` $<0.90\times$, `Near-crit` $0.90\text{--}1.10\times$, `Over` $>1.10\times$), alongside Gent–Walsh annealed constrainedness $\kappa = -\frac{1}{n}\sum_i \log_2(1-2^{-k_i})$ (AAAI 1996), clause-length profile ($\bar{k}$, `%Bin`, `%Horn`), variable-degree CV ($\sigma_d/\bar{d}$, uniformity vs. hub skew), and extracted native XOR parity clauses.*

| Group / Family | Files | Med $n$ | Med $m$ | $\alpha=m/n$ (Med) | $\alpha_c^{\mathrm{eff}}$ (Med) | $\rho_{\mathrm{crit}}$ Med [Min–Max] (Regime) | Med $\kappa$ | Med $\bar{k}$ | Bin% | Horn% | Deg CV | Total XORs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `frb30-15` | 5 | 450 | 19,084 | 42.41 | 1.00 | **42.3x** [42.3x–42.3x] (Over) | 17.57 | 2.02 | 100% | 100% | 0.18 | 0 |
| `frb35-17` | 5 | 595 | 29,707 | 49.93 | 1.00 | **49.9x** [49.9x–49.9x] (Over) | 20.70 | 2.02 | 100% | 100% | 0.21 | 0 |
| `frb40-19` | 5 | 760 | 43,780 | 57.61 | 1.00 | **57.6x** [57.6x–57.6x] (Over) | 23.89 | 2.02 | 100% | 100% | 0.18 | 0 |
| `frb45-21` | 5 | 945 | 61,855 | 65.46 | 1.00 | **65.4x** [65.4x–65.4x] (Over) | 27.15 | 2.01 | 100% | 100% | 0.19 | 0 |
| `frb50-23` | 5 | 1,150 | 84,508 | 73.49 | 1.00 | **73.4x** [73.4x–73.4x] (Over) | 30.48 | 2.01 | 100% | 100% | 0.19 | 0 |
| `frb53-24` | 5 | 1,272 | 98,921 | 77.77 | 1.00 | **77.7x** [77.7x–77.7x] (Over) | 32.26 | 2.01 | 100% | 100% | 0.18 | 0 |
| `frb56-25` | 5 | 1,400 | 114,668 | 81.91 | 1.00 | **81.9x** [81.9x–81.9x] (Over) | 33.98 | 2.01 | 100% | 100% | 0.19 | 0 |
| `frb59-26` | 5 | 1,534 | 132,295 | 86.24 | 1.00 | **86.2x** [86.2x–86.2x] (Over) | 35.78 | 2.01 | 100% | 100% | 0.19 | 0 |

**Collection Phase-Transition Summary (40 instances, 4 formats: 40 CNF / 40 AIG / 40 XCNF / 40 ANF):** median $\rho_{\mathrm{crit}} = 69.4\times$ (range `42.3x–86.2x`), median $\kappa = 28.81$, regime split **0 Under / 0 Near-critical / 40 Over**, total extracted native XOR parity clauses = **0**, total ANF equations = **2,959,100**.
<!-- END_STRUCTURAL_ANALYSIS -->
