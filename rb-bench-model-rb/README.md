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

## Corpus & Data Sizes

All **40 forced-SAT CNFs** (`39.0 MB` total) across all 8 size classes, plus **40 exact Binary AIGER 1.9 conversions** in `aig-version/` (`24.7 MB`, all 40/40 verified via [Berkeley ABC](https://github.com/berkeley-abc/abc) `read_aiger`) and `src/cnf2aig.py`:

| Family | Instances | Status | Vars ($n \cdot d$) | Clauses | CNF Size (5 files) | AIG Files |
|---|---:|:---:|---:|---:|---:|---:|
| `frb30-15-1..5.cnf` | 5 | SAT | 450 | 19,084 | 1.15 MB | 5 |
| `frb35-17-1..5.cnf` | 5 | SAT | 595 | 29,707 | 1.80 MB | 5 |
| `frb40-19-1..5.cnf` | 5 | SAT | 760 | 43,780 | 2.66 MB | 5 |
| `frb45-21-1..5.cnf` | 5 | SAT | 945 | 61,855 | 3.79 MB | 5 |
| `frb50-23-1..5.cnf` | 5 | SAT | 1,150 | 84,508 | 5.28 MB | 5 |
| `frb53-24-1..5.cnf` | 5 | SAT | 1,272 | 98,921 | 6.26 MB | 5 |
| `frb56-25-1..5.cnf` | 5 | SAT | 1,400 | 114,668 | 7.36 MB | 5 |
| `frb59-26-1..5.cnf` | 5 | SAT | 1,534 | 132,295 | 8.66 MB | 5 |
| **Total** | **40** | **40 SAT** | **450–1,534** | **19,084–132,295** | **39.0 MB** | **40** |

## Comparative 1-Core Spot Check (`frb30-15-1..5`, $T_{\max} = 5\;\text{s}$)

- **Hardware & Protocol:** Same machine (AMD Ryzen 9 5950X, Linux, 1 core per run, $T_{\max} = 5\;\text{s}$, identical flat `.cnf` input, 100% SAT consensus).

| Instance | Verdict | [Kissat](https://github.com/arminbiere/kissat) 4.0.4 | [CaDiCaL](https://github.com/arminbiere/cadical) 3.1.0 | Frobenius 1C |
|---|---:|---:|---:|---:|
| `frb30-15-1.cnf` | SAT | **110.50 ms** | 335.36 ms | 762.64 ms |
| `frb30-15-2.cnf` | SAT | 320.92 ms | **49.27 ms** | 371.34 ms |
| `frb30-15-3.cnf` | SAT | **48.75 ms** | 447.59 ms | 692.54 ms |
| `frb30-15-4.cnf` | SAT | **347.33 ms** | 523.84 ms | 877.06 ms |
| `frb30-15-5.cnf` | SAT | 96.01 ms | **20.54 ms** | 461.58 ms |
| **Total (5 files)** | **5 / 5** | **923.51 ms** *(fastest)* | **1,376.60 ms** *(1.49x slower)* | **3,165.16 ms** *(3.43x slower)* |
