# SATLIB — Variable-Length Random SAT — Hooker (full) (`satlib-dimacs-jnh`)

## Provenance & Credit

- **Recommended by:** [`@jasonslenderman`](https://twitter.com/jasonslenderman) (Twitter/X)
- **Upstream Archive:** [SATLIB — Benchmark Problems (UBC)](https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html)
- **SATLIB Curators:** Holger H. Hoos and Thomas Stützle (University of British Columbia / TU Darmstadt)
- **Family Contributors:** John N. Hooker
- **License:** Classic public scientific benchmark collection redistributed by UBC SATLIB for academic SAT research; no separate upstream `LICENSE` file is bundled in the archives.
- **Format Hygiene:** Legacy SATLIB trailing `%` / `0` EOF sentinels were stripped and wrapped multi-line clauses normalized to canonical 1-clause-per-line DIMACS CNF so every modern SAT solver parses all files cleanly.
- **Full SATLIB Archive Manifest:** [`../satlib-archive-uris/`](../satlib-archive-uris/README.md) (all 97 official UBC SATLIB `.tar.gz` archive URLs; Pretolani's `PRET` formulas live in [`../pretolani-pret/`](../pretolani-pret/README.md)).

## Problem Description

All 50 variable-clause-length random SAT benchmarks (`jnh1`–`jnh310`, $n = 100$) contributed by John Hooker to the Second DIMACS Challenge.

## Corpus & Data Sizes (Four Formats)

- **`cnf-orig/`** — 50 original native **DIMACS `.cnf.xz`** files (285.7 KB).
- **`aig-converted/`** — 50 exact **Binary AIGER 1.9 `.aig.xz`** conversions (373.9 KB, verified via [Berkeley ABC](https://github.com/berkeley-abc/abc) `read_aiger`).
- **`xcnf-converted/`** — 50 lossless **[CryptoMiniSat](https://github.com/msoos/cryptominisat) `.xcnf.xz`** conversions (288.0 KB, `0` extracted native XOR parity clauses).
- **`anf-converted/`** — 50 lossless linear-size **DIMACS-ANF `.anf.xz`** conversions (970.1 KB, generated via [`../src/to_anf.py`](../src/to_anf.py)).
- **`src/`** — Standalone converters (`cnf2aig.py`, `cnf2xcnf.py`).

| Format | Directory | Files | Key Dimensions (Range) | Compressed Size |
|---|---|---:|---|---:|
| **DIMACS CNF (origin)** | `cnf-orig/` | 50 | Vars: 100; Clauses: 800–900 | 285.7 KB |
| **Binary AIGER 1.9** | `aig-converted/` | 50 | Inputs: 100; ANDs: 3,742–4,452 | 373.9 KB |
| **[CryptoMiniSat](https://github.com/msoos/cryptominisat) XCNF** | `xcnf-converted/` | 50 | Native XOR clauses total: 0 | 288.0 KB |
| **DIMACS-ANF** | `anf-converted/` | 50 | Vars: 1,662–2,119; Eqs: 2,362–2,919 (deg ≤ 3) | 970.1 KB |
| **Total (4 Formats, Status: Mixed)** | | **200** | | **1.87 MB** |

## Comparative 1-Core Benchmark Results (All 50 Instances, Flat `.cnf`, $T_{\max} = 5\;\text{s}$)

- **Hardware & Protocol:** Same machine (**AMD Ryzen 9 5950X**, 16C/32T Linux, **1 thread per run** pinned across 8 dedicated physical cores, $T_{\max} = 5\;\text{s}$, PAR-2 penalty $10,000\;\text{ms}$). All solvers received identical uncompressed flat `.cnf` inputs; **100% of all 50 instances** were run (no subsampling), every Frobenius SAT model was independently verified against 100% of input clauses, and **0 verdict disagreements** occurred across all solvers.

| Instance | Verdict | Frobenius 1C | [CaDiCaL](https://github.com/arminbiere/cadical) 3.1.0 | [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18.0 | [`dense-solver 0.0.4`](https://github.com/libdense/dense-solver) | [Kissat](https://github.com/arminbiere/kissat) 4.0.4 |
|---|:---:|---:|---:|---:|---:|---:|
| `jnh1` | SAT | 5.23 ms | 3.51 ms | 51.37 ms | **2.74 ms** | 26.69 ms |
| `jnh10` | UNSAT | 5.57 ms | 3.20 ms | 14.65 ms | 2.10 ms | **2.01 ms** |
| `jnh11` | UNSAT | 5.31 ms | 2.90 ms | 15.72 ms | **2.51 ms** | 3.36 ms |
| `jnh12` | SAT | 2.77 ms | 3.16 ms | 9.86 ms | **2.11 ms** | 3.19 ms |
| `jnh13` | UNSAT | 4.41 ms | 2.73 ms | 13.76 ms | 2.20 ms | **2.05 ms** |
| `jnh14` | UNSAT | 4.53 ms | 2.50 ms | 13.05 ms | **2.22 ms** | 2.38 ms |
| `jnh15` | UNSAT | 4.91 ms | 2.92 ms | 13.88 ms | **2.10 ms** | 2.48 ms |
| `jnh16` | UNSAT | 7.64 ms | 5.81 ms | 46.42 ms | **3.17 ms** | 6.66 ms |
| `jnh17` | SAT | 2.54 ms | 2.93 ms | 9.69 ms | **2.53 ms** | 4.06 ms |
| `jnh18` | UNSAT | 5.00 ms | 2.95 ms | 13.40 ms | 2.11 ms | **2.05 ms** |
| `jnh19` | UNSAT | 5.21 ms | 2.92 ms | 14.03 ms | **2.29 ms** | 2.61 ms |
| `jnh2` | UNSAT | 4.82 ms | 2.76 ms | 13.50 ms | **2.05 ms** | 2.35 ms |
| `jnh20` | UNSAT | 4.71 ms | 3.01 ms | 14.65 ms | **2.22 ms** | 2.45 ms |
| `jnh201` | SAT | 2.59 ms | 2.81 ms | 87.49 ms | **2.09 ms** | 25.10 ms |
| `jnh202` | UNSAT | 4.31 ms | 2.64 ms | 12.89 ms | 2.07 ms | **1.99 ms** |
| `jnh203` | UNSAT | 5.19 ms | 3.42 ms | 14.84 ms | **2.21 ms** | 4.96 ms |
| `jnh204` | SAT | 5.22 ms | 3.83 ms | 40.48 ms | **2.06 ms** | 15.06 ms |
| `jnh205` | SAT | 3.32 ms | 4.07 ms | 6.68 ms | **1.99 ms** | 5.01 ms |
| `jnh206` | UNSAT | 6.03 ms | 3.66 ms | 16.37 ms | **2.33 ms** | 5.24 ms |
| `jnh207` | SAT | 2.12 ms | 3.55 ms | 18.54 ms | 2.33 ms | **1.45 ms** |
| `jnh208` | UNSAT | 4.69 ms | 2.54 ms | 15.91 ms | **2.06 ms** | 4.67 ms |
| `jnh209` | SAT | 2.48 ms | 2.96 ms | 14.89 ms | 2.27 ms | **1.61 ms** |
| `jnh210` | SAT | 4.22 ms | 3.04 ms | 29.29 ms | **1.92 ms** | 7.57 ms |
| `jnh211` | UNSAT | 4.74 ms | 2.65 ms | 13.88 ms | **2.26 ms** | 2.38 ms |
| `jnh212` | SAT | 5.05 ms | 3.34 ms | 30.81 ms | **2.63 ms** | 19.24 ms |
| `jnh213` | SAT | 4.22 ms | 2.59 ms | 13.62 ms | **2.15 ms** | 4.20 ms |
| `jnh214` | UNSAT | 5.26 ms | 3.37 ms | 12.41 ms | **2.13 ms** | 2.93 ms |
| `jnh215` | UNSAT | 4.64 ms | 2.81 ms | 13.45 ms | **1.76 ms** | 2.26 ms |
| `jnh216` | UNSAT | 5.87 ms | 2.89 ms | 13.55 ms | **2.39 ms** | 2.58 ms |
| `jnh217` | SAT | **2.36 ms** | 3.47 ms | 126.74 ms | 2.49 ms | 24.39 ms |
| `jnh218` | SAT | **2.34 ms** | 3.48 ms | 27.42 ms | 2.43 ms | 7.68 ms |
| `jnh219` | UNSAT | 5.34 ms | 3.27 ms | 12.21 ms | **2.28 ms** | 2.62 ms |
| `jnh220` | SAT | 5.43 ms | 2.78 ms | 93.05 ms | **1.81 ms** | 25.17 ms |
| `jnh3` | UNSAT | 4.92 ms | 2.95 ms | 20.46 ms | **2.58 ms** | 4.97 ms |
| `jnh301` | SAT | 6.37 ms | 4.15 ms | 18.00 ms | **2.46 ms** | 3.96 ms |
| `jnh302` | UNSAT | 4.63 ms | 2.89 ms | 15.57 ms | 2.14 ms | **1.82 ms** |
| `jnh303` | UNSAT | 5.00 ms | 3.73 ms | 13.77 ms | 2.89 ms | **2.46 ms** |
| `jnh304` | UNSAT | 5.02 ms | 3.05 ms | 12.86 ms | **2.17 ms** | 2.37 ms |
| `jnh305` | UNSAT | 4.13 ms | 3.14 ms | 14.11 ms | 2.06 ms | **1.88 ms** |
| `jnh306` | UNSAT | 5.67 ms | 3.54 ms | 21.50 ms | **2.53 ms** | 5.99 ms |
| `jnh307` | UNSAT | 4.53 ms | 2.82 ms | 13.98 ms | 1.91 ms | **1.88 ms** |
| `jnh308` | UNSAT | 5.12 ms | 3.36 ms | 13.29 ms | **2.11 ms** | 2.52 ms |
| `jnh309` | UNSAT | 4.24 ms | 2.93 ms | 12.46 ms | **2.24 ms** | 2.40 ms |
| `jnh310` | UNSAT | 4.22 ms | 3.36 ms | 13.45 ms | **2.37 ms** | 2.44 ms |
| `jnh4` | UNSAT | 4.75 ms | 3.09 ms | 13.19 ms | **2.00 ms** | 2.49 ms |
| `jnh5` | UNSAT | 4.23 ms | 2.86 ms | 14.44 ms | **2.05 ms** | 4.44 ms |
| `jnh6` | UNSAT | 5.42 ms | 3.00 ms | 13.74 ms | **2.26 ms** | 2.86 ms |
| `jnh7` | SAT | 2.49 ms | 3.23 ms | 8.36 ms | **2.07 ms** | 3.55 ms |
| `jnh8` | UNSAT | 4.44 ms | 2.98 ms | 13.06 ms | **2.25 ms** | 2.27 ms |
| `jnh9` | UNSAT | 5.68 ms | 3.09 ms | 14.40 ms | **2.11 ms** | 2.30 ms |
| **Total (50 files, PAR-2)** | **50/50** | 50/50 — 228.9 ms *(2.04x)* | 50/50 — 158.6 ms *(1.41x)* | 50/50 — 1,105.1 ms *(9.85x)* | **50/50 — 112.2 ms** *(fastest)* | 50/50 — 279.1 ms *(2.49x)* |

<!-- BEGIN_STRUCTURAL_ANALYSIS -->
## Phase-Transition & Structural Analysis

*Auto-generated by [`../src/analyze_benchmarks.py`](../src/analyze_benchmarks.py). Position relative to the critical phase transition is measured by $\rho_{\mathrm{crit}} = \frac{1}{n}\sum_k m_k / \alpha_c(k)$ (exact $\alpha/\alpha_c(k)$ for pure $k$-SAT; effective critical threshold $\alpha_c^{\mathrm{eff}} = \alpha/\rho_{\mathrm{crit}}$; `Under` $<0.90\times$, `Near-crit` $0.90\text{--}1.10\times$, `Over` $>1.10\times$), alongside Gent–Walsh annealed constrainedness $\kappa = -\frac{1}{n}\sum_i \log_2(1-2^{-k_i})$ (AAAI 1996), clause-length profile ($\bar{k}$, `%Bin`, `%Horn`), variable-degree CV ($\sigma_d/\bar{d}$, uniformity vs. hub skew), and extracted native XOR parity clauses.*

| Group / Family | Files | Med $n$ | Med $m$ | $\alpha=m/n$ (Med) | $\alpha_c^{\mathrm{eff}}$ (Med) | $\rho_{\mathrm{crit}}$ Med [Min–Max] (Regime) | Med $\kappa$ | Med $\bar{k}$ | Bin% | Horn% | Deg CV | Total XORs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `satlib-dimacs-jnh` | 50 | 100 | 850 | 8.50 | 6.05 | **1.37x** [1.10x–1.59x] (Over) | 0.87 | 4.89 | 9% | 26% | 0.14 | 0 |

**Collection Phase-Transition Summary (50 instances, 4 formats: 50 CNF / 50 AIG / 50 XCNF / 50 ANF):** median $\rho_{\mathrm{crit}} = 1.37\times$ (range `1.10x–1.59x`), median $\kappa = 0.87$, regime split **0 Under / 1 Near-critical / 49 Over**, total extracted native XOR parity clauses = **0**, total ANF equations = **125,683**.
<!-- END_STRUCTURAL_ANALYSIS -->

## References

- H. H. Hoos and T. Stützle, *"SATLIB: An Online Resource for Research on SAT"*, SAT 2000, IOS Press, pp. 283–292 ([`cs.ubc.ca/~hoos/SATLIB/`](https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html)).
- D. S. Johnson and M. A. Trick (eds.), *Cliques, Coloring, and Satisfiability: Second DIMACS Implementation Challenge*, DIMACS Series vol. 26, AMS, 1996.
