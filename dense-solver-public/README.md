# [dense-solver](https://github.com/libdense/dense-solver) Public SAT Benchmarks (`dense-solver-public`)

## Provenance & Credit

- **Author & Recommended by:** Merlin Numa ([`@merlin_numa`](https://twitter.com/merlin_numa) on Twitter/X)
- **Upstream Repository:** [`libdense/dense-solver`](https://github.com/libdense/dense-solver)
- **Zenodo Archive (v0.0.4):** [`zenodo.org/records/24443907`](https://zenodo.org/records/24443907)
- **License & Attribution:**
  - [dense-solver](https://github.com/libdense/dense-solver) scripts are licensed under the **MIT License** — see [`LICENSE`](LICENSE).
  - Third-party public formulas retain their full upstream provenance, SHA-256 digests, and credits in [`SOURCES.md`](SOURCES.md), [`CITATION.cff`](CITATION.cff), and [`src/public-inputs.csv`](src/public-inputs.csv) (22 SATLIB formulas + 8 SAT Competition 2025 Main Track GBD formulas).
- **Companion Collection:** [`dense-solver-synthetic/`](../dense-solver-synthetic/README.md) (20 multi-encoding PHP & mutilated chessboard CNFs).

## Problem Description

This collection holds the **30 third-party public CNFs** (`public-instances/`) shipped with [dense-solver](https://github.com/libdense/dense-solver) 0.0.4 (16 SAT / 14 UNSAT):

- **22 SATLIB classics:** `hole6..10` (John Hooker), `uf50-01..04` & `uuf50-01..04` (uniform random 3-SAT), `flat30-1..3` (Joseph Culberson graph coloring), `anomaly`, `medium`, `bw_large.a` (SATPLAN Blocks World), and `par8-1-c..par8-3-c` (James Crawford parity learning).
- **8 compact SAT Competition 2025 Main Track representatives** (sourced via GBD / RocSAT selection): `sc25-subset-cardinality`, `sc25-fpga-routing`, `sc25-scheduling`, `sc25-hgen`, `sc25-tseitin-formulas`, `sc25-mutilated-chessboard`, `sc25-hamiltonian`, and `sc25-pigeon-hole`.

## Corpus & Data Sizes (Four Formats)

- **`cnf-orig/`** — 30 original native **DIMACS `.cnf.xz`** files (70.4 KB).
- **`aig-converted/`** — 30 exact **Binary AIGER 1.9 `.aig.xz`** conversions (88.1 KB, verified via [Berkeley ABC](https://github.com/berkeley-abc/abc) `read_aiger`).
- **`xcnf-converted/`** — 30 lossless **[CryptoMiniSat](https://github.com/msoos/cryptominisat) `.xcnf.xz`** conversions (69.1 KB, `323` extracted native XOR parity clauses).
- **`anf-converted/`** — 30 lossless linear-size **DIMACS-ANF `.anf.xz`** conversions (113.4 KB, generated via [`../src/to_anf.py`](../src/to_anf.py)).
- **`src/`** — Upstream fetcher and manifest (`fetch_public.py`, `public-inputs.csv`) plus `cnf2aig.py` and `cnf2xcnf.py`.

| Format | Directory | Files | Key Dimensions (Range) | Compressed Size |
|---|---|---:|---|---:|
| **DIMACS CNF (origin)** | `cnf-orig/` | 30 | Vars: 42–760; Clauses: 133–4,675 | 70.4 KB |
| **Binary AIGER 1.9** | `aig-converted/` | 30 | Inputs: 42–760; ANDs: 293–10,808 | 88.1 KB |
| **[CryptoMiniSat](https://github.com/msoos/cryptominisat) XCNF** | `xcnf-converted/` | 30 | Native XOR clauses total: 323 | 69.1 KB |
| **DIMACS-ANF** | `anf-converted/` | 30 | Vars: 50–1,084; Eqs: 86–4,762 (deg ≤ 3) | 113.4 KB |
| **Total (4 Formats, Status: 16 SAT / 14 UNSAT)** | | **120** | | **340.9 KB** |

## Comparative 1-Core Benchmark Results (All 30 Instances, Flat `.cnf`, $T_{\max} = 5\;\text{s}$)

- **Hardware & Protocol:** Same machine (**AMD Ryzen 9 5950X**, 16C/32T Linux, **1 thread per run** pinned across 8 dedicated physical cores, $T_{\max} = 5\;\text{s}$, PAR-2 penalty $10,000\;\text{ms}$). All solvers received identical uncompressed flat `.cnf` inputs; **100% of all 30 instances** were run (no subsampling), every Frobenius SAT model was independently verified against 100% of input clauses, and **0 verdict disagreements** occurred across all solvers.

| Instance | Verdict | Frobenius 1C | [CaDiCaL](https://github.com/arminbiere/cadical) 3.1.0 | [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18.0 | [dense-solver](https://github.com/libdense/dense-solver) 0.0.4 | [Kissat](https://github.com/arminbiere/kissat) 4.0.4 |
|---|:---:|---:|---:|---:|---:|---:|
| `anomaly` | SAT | 2.58 ms | 2.76 ms | 5.56 ms | 1.87 ms | **1.51 ms** |
| `bw_large.a` | SAT | 15.55 ms | **4.22 ms** | 121.62 ms | 4.63 ms | 23.90 ms |
| `flat30-1` | SAT | 1.79 ms | 2.16 ms | 9.81 ms | **1.28 ms** | 1.43 ms |
| `flat30-2` | SAT | 1.72 ms | 1.91 ms | 7.92 ms | 1.32 ms | **1.20 ms** |
| `flat30-3` | SAT | 2.03 ms | 1.92 ms | 7.38 ms | **1.40 ms** | 1.41 ms |
| `hole10` | UNSAT | 2.00 ms | >5 s | >5 s | **1.48 ms** | 1,268.85 ms |
| `hole6` | UNSAT | 2.27 ms | 5.03 ms | 23.34 ms | **1.55 ms** | 4.28 ms |
| `hole7` | UNSAT | 1.78 ms | 28.95 ms | 53.23 ms | **1.50 ms** | 10.26 ms |
| `hole8` | UNSAT | 2.25 ms | 267.08 ms | 330.46 ms | **1.55 ms** | 46.59 ms |
| `hole9` | UNSAT | 1.78 ms | 3,131.20 ms | >5 s | **1.20 ms** | 124.17 ms |
| `medium` | SAT | 2.62 ms | 3.21 ms | 11.79 ms | 3.41 ms | **1.37 ms** |
| `par8-1-c` | SAT | 1.94 ms | 2.20 ms | >5 s | **1.27 ms** | 2.31 ms |
| `par8-2-c` | SAT | 2.47 ms | 2.16 ms | >5 s | **1.31 ms** | 2.47 ms |
| `par8-3-c` | SAT | 2.26 ms | 1.91 ms | >5 s | **1.59 ms** | 2.84 ms |
| `sc25-fpga-routing` | UNSAT | 2.69 ms | >5 s | >5 s | **1.96 ms** | >5 s |
| `sc25-hamiltonian` | SAT | **119.19 ms** | 218.70 ms | 174.33 ms | 412.11 ms | 348.18 ms |
| `sc25-hgen` | SAT | **50.95 ms** | 339.34 ms | >5 s | >5 s | 1,265.29 ms |
| `sc25-mutilated-chessboard` | UNSAT | 2.91 ms | >5 s | >5 s | **2.22 ms** | >5 s |
| `sc25-pigeon-hole` | UNSAT | **2.91 ms** | >5 s | >5 s | 2.92 ms | >5 s |
| `sc25-scheduling` | SAT | 7.11 ms | 2.37 ms | 51.50 ms | **2.15 ms** | 9.71 ms |
| `sc25-subset-cardinality` | TIMEOUT | >5 s | >5 s | >5 s | >5 s | >5 s |
| `sc25-tseitin-formulas` | UNSAT | 2.16 ms | >5 s | 33.98 ms | **1.49 ms** | >5 s |
| `uf50-01` | SAT | 2.21 ms | 2.49 ms | 6.17 ms | **1.39 ms** | 3.01 ms |
| `uf50-02` | SAT | 1.93 ms | 2.65 ms | 17.84 ms | **1.50 ms** | 3.28 ms |
| `uf50-03` | SAT | 1.81 ms | 2.94 ms | 7.97 ms | **1.72 ms** | 2.44 ms |
| `uf50-04` | SAT | 1.84 ms | 2.34 ms | 6.28 ms | **1.30 ms** | 3.02 ms |
| `uuf50-01` | UNSAT | 3.01 ms | 2.40 ms | 13.44 ms | **1.39 ms** | 2.18 ms |
| `uuf50-02` | UNSAT | 3.01 ms | 2.40 ms | 16.36 ms | **1.32 ms** | 2.50 ms |
| `uuf50-03` | UNSAT | 2.92 ms | 2.13 ms | 14.21 ms | **1.35 ms** | 2.76 ms |
| `uuf50-04` | UNSAT | 3.01 ms | 2.29 ms | 14.95 ms | **1.30 ms** | 2.35 ms |
| **Total (30 files, PAR-2)** | **29/30** | **29/30 — 10,250.7 ms** *(fastest)* | 24/30 — 64,034.8 ms *(6.25x)* | 20/30 — 100,928.1 ms *(9.85x)* | 28/30 — 20,459.5 ms *(2.00x)* | 25/30 — 53,137.3 ms *(5.18x)* |

<!-- BEGIN_STRUCTURAL_ANALYSIS -->
## Phase-Transition & Structural Analysis

*Auto-generated by [`../src/analyze_benchmarks.py`](../src/analyze_benchmarks.py). Position relative to the critical phase transition is measured by $\rho_{\mathrm{crit}} = \frac{1}{n}\sum_k m_k / \alpha_c(k)$ (exact $\alpha/\alpha_c(k)$ for pure $k$-SAT; effective critical threshold $\alpha_c^{\mathrm{eff}} = \alpha/\rho_{\mathrm{crit}}$; `Under` $<0.90\times$, `Near-crit` $0.90\text{--}1.10\times$, `Over` $>1.10\times$), alongside Gent–Walsh annealed constrainedness $\kappa = -\frac{1}{n}\sum_i \log_2(1-2^{-k_i})$ (AAAI 1996), clause-length profile ($\bar{k}$, `%Bin`, `%Horn`), variable-degree CV ($\sigma_d/\bar{d}$, uniformity vs. hub skew), and extracted native XOR parity clauses.*

| Group / Family | Files | Med $n$ | Med $m$ | $\alpha=m/n$ (Med) | $\alpha_c^{\mathrm{eff}}$ (Med) | $\rho_{\mathrm{crit}}$ Med [Min–Max] (Regime) | Med $\kappa$ | Med $\bar{k}$ | Bin% | Horn% | Deg CV | Total XORs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `dense-solver-public` | 8 | 81 | 356 | 4.86 | 1.05 | **4.50x** [3.00x–7.89x] (Over) | 1.92 | 2.20 | 95% | 95% | 0.00 | 0 |
| `flat30-1` | 1 | 90 | 300 | 3.33 | 1.08 | **3.08x** [3.08x] (Over) | 1.31 | 2.10 | 90% | 90% | 0.18 | 0 |
| `flat30-2` | 1 | 90 | 300 | 3.33 | 1.08 | **3.08x** [3.08x] (Over) | 1.31 | 2.10 | 90% | 90% | 0.19 | 0 |
| `flat30-3` | 1 | 90 | 300 | 3.33 | 1.08 | **3.08x** [3.08x] (Over) | 1.31 | 2.10 | 90% | 90% | 0.16 | 0 |
| `par8-1` | 1 | 64 | 254 | 3.97 | 3.08 | **1.29x** [1.29x] (Over) | 0.87 | 2.88 | 12% | 43% | 0.61 | 56 |
| `par8-2` | 1 | 68 | 270 | 3.97 | 3.13 | **1.27x** [1.27x] (Over) | 0.86 | 2.89 | 11% | 41% | 0.67 | 60 |
| `par8-3` | 1 | 75 | 298 | 3.97 | 3.21 | **1.24x** [1.24x] (Over) | 0.85 | 2.90 | 10% | 39% | 0.72 | 67 |
| `sc25-fpga` | 1 | 220 | 1,122 | 5.10 | 1.02 | **5.00x** [5.00x] (Over) | 2.08 | 2.16 | 98% | 69% | 0.00 | 0 |
| `sc25-hamiltonian` | 1 | 300 | 2,696 | 8.99 | 1.09 | **8.23x** [8.23x] (Over) | 3.44 | 2.27 | 91% | 91% | 0.08 | 0 |
| `sc25-hgen` | 1 | 322 | 1,127 | 3.50 | 4.27 | **0.82x** [0.82x] (Under) | 0.67 | 3.00 | 0% | 50% | 0.06 | 0 |
| `sc25-mutilated` | 1 | 760 | 2,556 | 3.36 | 1.16 | **2.91x** [2.91x] (Over) | 1.24 | 2.28 | 85% | 84% | 0.11 | 0 |
| `sc25-pigeon` | 1 | 240 | 3,496 | 14.57 | 1.00 | **14.5x** [14.5x] (Over) | 6.02 | 2.06 | 100% | 76% | 0.00 | 0 |
| `sc25-scheduling` | 1 | 226 | 1,106 | 4.89 | 1.15 | **4.24x** [4.24x] (Over) | 1.81 | 2.33 | 84% | 93% | 0.65 | 0 |
| `sc25-subset` | 1 | 149 | 606 | 4.07 | 4.31 | **0.94x** [0.94x] (Near-crit) | 0.78 | 3.02 | 0% | 49% | 0.09 | 0 |
| `sc25-tseitin` | 1 | 264 | 968 | 3.67 | 7.68 | **0.48x** [0.48x] (Under) | 0.41 | 3.82 | 1% | 33% | 0.23 | 140 |
| `uf50-01` | 1 | 50 | 218 | 4.36 | 4.27 | **1.02x** [1.02x] (Near-crit) | 0.84 | 3.00 | 0% | 47% | 0.27 | 0 |
| `uf50-02` | 1 | 50 | 218 | 4.36 | 4.27 | **1.02x** [1.02x] (Near-crit) | 0.84 | 3.00 | 0% | 47% | 0.26 | 0 |
| `uf50-03` | 1 | 50 | 218 | 4.36 | 4.27 | **1.02x** [1.02x] (Near-crit) | 0.84 | 3.00 | 0% | 47% | 0.30 | 0 |
| `uf50-04` | 1 | 50 | 218 | 4.36 | 4.27 | **1.02x** [1.02x] (Near-crit) | 0.84 | 3.00 | 0% | 50% | 0.23 | 0 |
| `uuf50-01` | 1 | 50 | 218 | 4.36 | 4.27 | **1.02x** [1.02x] (Near-crit) | 0.84 | 3.00 | 0% | 50% | 0.25 | 0 |
| `uuf50-02` | 1 | 50 | 218 | 4.36 | 4.27 | **1.02x** [1.02x] (Near-crit) | 0.84 | 3.00 | 0% | 51% | 0.27 | 0 |
| `uuf50-03` | 1 | 50 | 218 | 4.36 | 4.27 | **1.02x** [1.02x] (Near-crit) | 0.84 | 3.00 | 0% | 50% | 0.30 | 0 |
| `uuf50-04` | 1 | 50 | 218 | 4.36 | 4.27 | **1.02x** [1.02x] (Near-crit) | 0.84 | 3.00 | 0% | 48% | 0.24 | 0 |

**Collection Phase-Transition Summary (30 instances, 4 formats: 30 CNF / 30 AIG / 30 XCNF / 30 ANF):** median $\rho_{\mathrm{crit}} = 2.96\times$ (range `0.48x–14.5x`), median $\kappa = 1.25$, regime split **2 Under / 9 Near-critical / 19 Over**, total extracted native XOR parity clauses = **323**, total ANF equations = **24,963**.
<!-- END_STRUCTURAL_ANALYSIS -->

## References

- M. Numa, *[dense-solver](https://github.com/libdense/dense-solver) v0.0.4*, [GitHub](https://github.com/libdense/dense-solver) and [Zenodo `24443907`](https://zenodo.org/records/24443907) (2026).
- H. H. Hoos and T. Stützle, *"SATLIB: An Online Resource for Research on SAT"*, SAT 2000, pp. 283–292.
- International SAT Competition 2025 & Global Benchmark Database (GBD): [`benchmark-database.de`](https://benchmark-database.de/).
