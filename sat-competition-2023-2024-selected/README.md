# Curated SAT Competition 2023 & 2024 Flat-CNF Suite (`sat-competition-2023-2024-selected`)

## Overview & Origin

A curated 14-instance cross-domain suite **sourced from the International SAT Competition [2023](https://satcompetition.github.io/2023/) and [2024](https://satcompetition.github.io/2024/) Main Tracks** via the **[Global Benchmark Database (GBD)](https://benchmark-database.de/)** ([`Udopia/gbd`](https://github.com/Udopia/gbd)), spanning 11 distinct industrial, cryptographic, hardware-verification, algebraic, and combinatorial domains (upstream benchmark license: **CC-BY-4.0**, see [`LICENSE`](LICENSE)):
- **Parity / Tseitin / Urquhart:** `tseitingrid6x200`, `tseitin_d3_n10000`, `urq45`, `two_trees_511v`, `two_trees_1023v`
- **Cardinality / Combinatorial / Clique / Register Allocation:** `intervals122`, `clique_n2_k10`, `gzipfile_close_11`
- **Hardware Verification Miters (HWMCC & Random Networks):** `rand_net70_40_10`, `hwmcc20_iso_rast_p06`, `hwmcc17_iso_bobsmfpu`
- **Cryptography, Subgraph Isomorphism & Polynomial Multiplication:** `vmpc_24`, `si2_b03m_m800_03`, `mp1_nb7t42`

Twelve of these instances form the SAT Competition slice of the unified 50-benchmark flat-CNF gauntlet; `two_trees_511v` and `mp1_nb7t42` are companion SC 2023/2024 instances from the same selection.

## Directory Layout & Reproducibility

- `cnf-orig/` — Original native **DIMACS CNF** formulas (14 `.cnf.xz` files, `3.11 MB`, xz-compressed directly from official GBD `.cnf.xz` archives).
- `aig-converted/` — Exact logically equivalent **Binary AIGER 1.9 `.aig.xz`** conversions (`3.79 MB`, all 14/14 verified with [Berkeley ABC](https://github.com/berkeley-abc/abc), including 1.09M-AND-gate `si2_b03m_m800_03.aig.xz` at `1.06 MB`).
- `xcnf-converted/` — Lossless **[CryptoMiniSat](https://github.com/msoos/cryptominisat) `.xcnf.xz`** conversions (`2.60 MB`, `71,848` extracted native XOR clauses).
- `anf-converted/` — Lossless linear-size **DIMACS-ANF `.anf.xz`** conversions (`27.89 MB`, degree $\le 3$, generated via [`../src/to_anf.py`](../src/to_anf.py)).
- `src/sc23_24_manifest.json` & `src/fetch_and_convert.py` — Exact GBD MD5 hashes and script to re-fetch from `benchmark-database.de` and regenerate `aig-converted/*.aig.xz`, plus `src/cnf2xcnf.py`.

## Problem Parameters & Data Sizes

| Instance | Year | Family | GBD Hash | Ans | CNF Vars | CNF Clauses | `.cnf.xz` | `.aig.xz` | `.anf.xz` |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|
| `tseitingrid6x200` | 2024 | SC24-Tseitin | `35789168b67a...` | UNSAT | 2,400 | 9,600 | 54.0 KB | 62.7 KB | 10.8 KB |
| `tseitin_d3_n10000` | 2023 | SC23-Tseitin | `1153a473e1d5...` | UNSAT | 15,000 | 40,000 | 112.8 KB | 138.6 KB | 65.8 KB |
| `urq45` | 2023 | SC23-Urquhart | `aa39c6d885d2...` | UNSAT | 74 | 694 | 1.7 KB | 3.6 KB | 10.9 KB |
| `two_trees_511v` | 2023 | SC23-Parity | `16c5482d8e65...` | SAT | 511 | 2,039 | 6.2 KB | 10.0 KB | 4.6 KB |
| `two_trees_1023v` | 2023 | SC23-Parity | `7db30d12cb06...` | SAT | 1,023 | 4,088 | 12.3 KB | 17.6 KB | 9.4 KB |
| `intervals122` | 2023 | SC23-Card. | `18416a9ac090...` | UNSAT | 2,568 | 57,706 | 107.0 KB | 163.9 KB | 160.9 KB |
| `clique_n2_k10` | 2024 | SC24-Clique | `cb2e8b7fada4...` | UNSAT | 180 | 3,160 | 4.1 KB | 4.6 KB | 6.5 KB |
| `gzipfile_close_11` | 2023 | SC23-RegAlloc | `72b5ad031bf8...` | UNSAT | 187 | 1,348 | 2.5 KB | 1.7 KB | 4.4 KB |
| `rand_net70_40_10` | 2023 | SC23-Miter | `00f2eb377986...` | UNSAT | 5,600 | 16,661 | 88.7 KB | 86.8 KB | 132.0 KB |
| `hwmcc20_iso_rast_p06` | 2024 | SC24-Miter | `1545660e7215...` | UNSAT | 85,230 | 276,273 | 657.7 KB | 936.9 KB | 965.0 KB |
| `hwmcc17_iso_bobsmfpu` | 2024 | SC24-Miter | `0a02751cacf5...` | UNSAT | 62,500 | 204,019 | 536.0 KB | 728.6 KB | 904.5 KB |
| `vmpc_24` | 2023 | SC23-Crypto | `220bb8aa093e...` | SAT | 576 | 67,872 | 84.5 KB | 257.9 KB | 203.9 KB |
| `si2_b03m_m800_03` | 2024 | SC24-SubIso | `af750c18578d...` | SAT | 10,862 | 472,588 | 1.17 MB | 1.06 MB | 25.01 MB |
| `mp1_nb7t42` | 2024 | SC24-PolyMul | `c0293283432a...` | SAT | 52,731 | 208,936 | 317.0 KB | 376.3 KB | 466.2 KB |

*(Full 32-character GBD hashes are listed in [`src/sc23_24_manifest.json`](src/sc23_24_manifest.json).)*

## Benchmark Results (1-Core, Flat DIMACS `.cnf`, $T_{\max} = 600\;\text{s}$)

Evaluated sequentially on an AMD Ryzen 9 5950X (exact median of 3 runs; all solvers read the identical flat `.cnf` file):

| Instance | Frobenius 1C | [CaDiCaL](https://github.com/arminbiere/cadical) 3.1.0 | [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18 (CNF) | [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18 (XCNF) | [dense-solver](https://github.com/libdense/dense-solver) 0.0.4 *($T=30\;\text{s}$)* | [Kissat](https://github.com/arminbiere/kissat) 4.0.4 |
|---|---:|---:|---:|---:|---:|---:|
| `tseitingrid6x200` | **3.07 ms** | >600 s (T/O) | >600 s (T/O) | 1,093.37 ms | 4.89 ms | >600 s (T/O) |
| `tseitin_d3_n10000` | **7.66 ms** | >600 s (T/O) | >600 s (T/O) | 731.97 ms | 84.03 ms | >600 s (T/O) |
| `urq45` | **1.10 ms** | >600 s (T/O) | >600 s (T/O) | 50.83 ms | 1.41 ms | 222,854.68 ms |
| `two_trees_1023v` | **5.15 ms** | >600 s (T/O) | >600 s (T/O) | 18,574.19 ms | >30 s | >600 s (T/O) |
| `intervals122` | **46.97 ms** | >600 s (T/O) | >600 s (T/O) | >600 s (T/O) | 19.26 ms | >600 s (T/O) |
| `clique_n2_k10` | **3.33 ms** | >600 s (T/O) | >600 s (T/O) | >600 s (T/O) | >30 s | 8,185.14 ms |
| `gzipfile_close_11` | **1.83 ms** | >600 s (T/O) | >600 s (T/O) | >600 s (T/O) | 1.51 ms | 294.83 ms |
| `rand_net70_40_10` | **5.39 ms** | 417.88 ms | 9,516.11 ms | 8,579.44 ms | 17.43 s | 12.31 ms |
| `hwmcc20_iso_rast_p06` | **75.85 ms** | 1,764.89 ms | >600 s (T/O) | >600 s (T/O) | >30 s | 347.68 ms |
| `hwmcc17_iso_bobsmfpu` | **53.54 ms** | 2,755.84 ms | >600 s (T/O) | >600 s (T/O) | >30 s | 321.55 ms |
| `vmpc_24` | **1,596.46 ms** | 6,171.80 ms | 1,653.58 ms | 44,855.40 ms | 1,795.47 ms | 12,462.32 ms |
| `si2_b03m_m800_03` | **1,944.36 ms** | 5,892.54 ms | 48,671.18 ms | 44,618.32 ms | 651.13 ms | 6,670.87 ms |

<!-- BEGIN_STRUCTURAL_ANALYSIS -->
## Phase-Transition & Structural Analysis

*Auto-generated by [`../src/analyze_benchmarks.py`](../src/analyze_benchmarks.py). Position relative to the critical phase transition is measured by $\rho_{\mathrm{crit}} = \frac{1}{n}\sum_k m_k / \alpha_c(k)$ (exact $\alpha/\alpha_c(k)$ for pure $k$-SAT; effective critical threshold $\alpha_c^{\mathrm{eff}} = \alpha/\rho_{\mathrm{crit}}$; `Under` $<0.90\times$, `Near-crit` $0.90\text{--}1.10\times$, `Over` $>1.10\times$), alongside Gent–Walsh annealed constrainedness $\kappa = -\frac{1}{n}\sum_i \log_2(1-2^{-k_i})$ (AAAI 1996), clause-length profile ($\bar{k}$, `%Bin`, `%Horn`), variable-degree CV ($\sigma_d/\bar{d}$, uniformity vs. hub skew), and extracted native XOR parity clauses.*

| Instance | Active $n$ | Clauses $m$ | $\alpha=m/n$ | $\alpha_c^{\mathrm{eff}}$ | $\rho_{\mathrm{crit}}$ (Regime) | $\kappa$ | $\bar{k}$ ($k_{\max}$) | Bin% | Horn% | Pos% | Deg CV | XORs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `clique_n2_k10` | 180 | 3,160 | 17.56 | 1.00 | **17.5x** (Over) | 7.26 | 2.05 (18) | 100% | 100% | 3% | 0.00 | 0 |
| `gzipfile_close_11` | 187 | 1,348 | 7.21 | 1.01 | **7.12x** (Over) | 2.95 | 2.11 (11) | 99% | 99% | 7% | 0.20 | 0 |
| `hwmcc17_iso_bobsmfpu` | 62,500 | 204,019 | 3.26 | 1.79 | **1.82x** (Over) | 0.94 | 2.58 (3) | 42% | 63% | 46% | 3.49 | 9,137 |
| `hwmcc20_iso_rast_p06` | 85,230 | 276,273 | 3.24 | 1.87 | **1.73x** (Over) | 0.91 | 2.61 (3) | 39% | 66% | 46% | 7.27 | 24,647 |
| `intervals122` | 2,568 | 57,706 | 22.47 | 1.00 | **22.4x** (Over) | 9.31 | 2.04 (88) | 100% | 76% | 48% | 0.51 | 0 |
| `mp1_nb7t42` | 52,731 | 208,936 | 3.96 | 1.96 | **2.03x** (Over) | 1.05 | 2.74 (4) | 38% | 63% | 45% | 1.87 | 25,480 |
| `rand_net70_40_10` | 5,600 | 16,661 | 2.98 | 1.36 | **2.19x** (Over) | 1.01 | 2.35 (70) | 66% | 66% | 50% | 0.33 | 70 |
| `si2_b03m_m800_03` | 10,862 | 472,588 | 43.51 | 2.92 | **14.9x** (Over) | 6.22 | 13.29 (20) | 34% | 35% | 55% | 4.80 | 0 |
| `tseitin_d3_n10000` | 15,000 | 40,000 | 2.67 | 4.27 | **0.62x** (Under) | 0.51 | 3.00 (3) | 0% | 50% | 50% | 0.00 | 10,000 |
| `tseitingrid6x200` | 2,400 | 9,600 | 4.00 | 9.93 | **0.40x** (Under) | 0.37 | 4.00 (4) | 0% | 31% | 50% | 0.00 | 1,200 |
| `two_trees_1023v` | 1,023 | 4,088 | 4.00 | 3.77 | **1.06x** (Near-crit) | 0.81 | 2.96 (3) | 4% | 51% | 50% | 0.23 | 857 |
| `two_trees_511v` | 511 | 2,039 | 3.99 | 3.80 | **1.05x** (Near-crit) | 0.80 | 2.96 (3) | 4% | 52% | 50% | 0.24 | 433 |
| `urq45` | 74 | 694 | 9.38 | 25.55 | **0.37x** (Under) | 0.32 | 6.16 (7) | 0% | 12% | 50% | 0.68 | 24 |
| `vmpc_24` | 576 | 67,872 | 117.8 | 1.87 | **62.9x** (Over) | 32.94 | 2.62 (24) | 39% | 100% | 24% | 0.01 | 0 |

**Collection Phase-Transition Summary (14 instances, 4 formats: 14 CNF / 14 AIG / 14 XCNF / 14 ANF):** median $\rho_{\mathrm{crit}} = 1.92\times$ (range `0.37x–62.9x`), median $\kappa = 0.97$, regime split **3 Under / 2 Near-critical / 9 Over**, total extracted native XOR parity clauses = **71,848**, total ANF equations = **6,201,418**.
<!-- END_STRUCTURAL_ANALYSIS -->

## References

- M. Iser and C. Sinz, *Global Benchmark Database (GBD)*, https://benchmark-database.de/, SAT 2019 / 2024.
- T. Balyo, M. J. H. Heule, M. Iser, M. Järvisalo, and M. Suda (eds.), *Proceedings of SAT Competition 2023 & 2024: Solver, Benchmark and Proof Checker Descriptions*, University of Helsinki, 2023–2024.
- N. Froleyks et al., *SAT Competition 2020*, Artificial Intelligence 301:103572, 2021.
