# Curated SAT Competition 2023 & 2024 Flat-CNF Suite (`sat-competition-2023-2024-selected`)

## Overview & Origin

A curated 14-instance cross-domain suite **sourced from the International SAT Competition [2023](https://satcompetition.github.io/2023/) and [2024](https://satcompetition.github.io/2024/) Main Tracks** via the **[Global Benchmark Database (GBD)](https://benchmark-database.de/)** ([`Udopia/gbd`](https://github.com/Udopia/gbd)), spanning 11 distinct industrial, cryptographic, hardware-verification, algebraic, and combinatorial domains (upstream benchmark license: **CC-BY-4.0**, see [`LICENSE`](LICENSE)):
- **Parity / Tseitin / Urquhart:** `tseitingrid6x200`, `tseitin_d3_n10000`, `urq45`, `two_trees_511v`, `two_trees_1023v`
- **Cardinality / Combinatorial / Clique / Register Allocation:** `intervals122`, `clique_n2_k10`, `gzipfile_close_11`
- **Hardware Verification Miters (HWMCC & Random Networks):** `rand_net70_40_10`, `hwmcc20_iso_rast_p06`, `hwmcc17_iso_bobsmfpu`
- **Cryptography, Subgraph Isomorphism & Polynomial Multiplication:** `vmpc_24`, `si2_b03m_m800_03`, `mp1_nb7t42`

Twelve of these instances form the SAT Competition slice of the unified 50-benchmark flat-CNF gauntlet; `two_trees_511v` and `mp1_nb7t42` are companion SC 2023/2024 instances from the same selection.

## Directory Layout & Reproducibility

- `*.cnf` — Original native **DIMACS CNF** formulas (decompressed from official GBD `.cnf.xz` archives).
- `aig-version/` — Exact logically equivalent **Binary AIGER 1.9 `.aig`** conversions (all 14/14 verified with Berkeley ABC, including 1.09M-AND-gate `si2_b03m_m800_03.aig` at `4.24 MB`).
- `src/sc23_24_manifest.json` & `src/fetch_and_convert.py` — Exact GBD MD5 hashes and script to re-fetch from `benchmark-database.de` and regenerate `aig-version/*.aig`.

## Problem Parameters & Data Sizes

| Instance | Year | Family | GBD Hash | Ans | CNF Vars | CNF Clauses | CNF Size | AIG ANDs | AIG Size |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|
| `tseitingrid6x200` | 2024 | SC24-Tseitin | `35789168b67a...` | UNSAT | 2,400 | 9,600 | 207.7 KB | 28,799 | 102.5 KB |
| `tseitin_d3_n10000` | 2023 | SC23-Tseitin | `1153a473e1d5...` | UNSAT | 15,000 | 40,000 | 753.1 KB | 119,999 | 493.3 KB |
| `urq45` | 2023 | SC23-Urquhart | `aa39c6d885d2...` | UNSAT | 74 | 694 | 15.5 KB | 1,943 | 5.0 KB |
| `two_trees_511v` | 2023 | SC23-Parity | `16c5482d8e65...` | SAT | 511 | 2,039 | 29.3 KB | 6,039 | 19.1 KB |
| `two_trees_1023v` | 2023 | SC23-Parity | `7db30d12cb06...` | SAT | 1,023 | 4,088 | 60.2 KB | 12,098 | 38.9 KB |
| `intervals122` | 2023 | SC23-Card. | `18416a9ac090...` | UNSAT | 2,568 | 57,706 | 698.9 KB | 117,770 | 497.7 KB |
| `clique_n2_k10` | 2024 | SC24-Clique | `cb2e8b7fada4...` | UNSAT | 180 | 3,160 | 33.9 KB | 6,479 | 19.7 KB |
| `gzipfile_close_11` | 2023 | SC23-RegAlloc | `72b5ad031bf8...` | UNSAT | 187 | 1,348 | 14.7 KB | 2,848 | 8.9 KB |
| `rand_net70_40_10` | 2023 | SC23-Miter | `00f2eb377986...` | UNSAT | 5,600 | 16,661 | 235.1 KB | 39,111 | 154.6 KB |
| `hwmcc20_iso_rast_p06` | 2024 | SC24-Miter | `1545660e7215...` | UNSAT | 85,230 | 276,273 | 4.89 MB | 696,006 | 2.79 MB |
| `hwmcc17_iso_bobsmfpu` | 2024 | SC24-Miter | `0a02751cacf5...` | UNSAT | 62,500 | 204,019 | 3.46 MB | 504,001 | 2.06 MB |
| `vmpc_24` | 2023 | SC23-Crypto | `220bb8aa093e...` | SAT | 576 | 67,872 | 927.9 KB | 162,816 | 670.9 KB |
| `si2_b03m_m800_03` | 2024 | SC24-SubIso | `af750c18578d...` | SAT | 10,862 | 472,588 | 29.14 MB | 1,093,425 | 4.24 MB |
| `mp1_nb7t42` | 2024 | SC24-PolyMul | `c0293283432a...` | SAT | 52,731 | 208,936 | 3.89 MB | 550,367 | 2.45 MB |

*(Full 32-character GBD hashes are listed in [`src/sc23_24_manifest.json`](src/sc23_24_manifest.json).)*

## Benchmark Results (1-Core, Flat DIMACS `.cnf`, $T_{\max} = 600\;\text{s}$)

Evaluated sequentially on an AMD Ryzen 9 5950X (exact median of 3 runs; all solvers read the identical flat `.cnf` file):

| Instance | Frobenius 1C | Kissat 4.0.4 | CaDiCaL 3.1.0 | CryptoMiniSat 5.18 (CNF) | CryptoMiniSat 5.18 (XCNF) |
|---|---:|---:|---:|---:|---:|
| `tseitingrid6x200` | **3.07 ms** | >600 s (T/O) | >600 s (T/O) | >600 s (T/O) | 1,093.37 ms |
| `tseitin_d3_n10000` | **7.66 ms** | >600 s (T/O) | >600 s (T/O) | >600 s (T/O) | 731.97 ms |
| `urq45` | **1.10 ms** | 222,854.68 ms | >600 s (T/O) | >600 s (T/O) | 50.83 ms |
| `two_trees_1023v` | **5.15 ms** | >600 s (T/O) | >600 s (T/O) | >600 s (T/O) | 18,574.19 ms |
| `intervals122` | **46.97 ms** | >600 s (T/O) | >600 s (T/O) | >600 s (T/O) | >600 s (T/O) |
| `clique_n2_k10` | **3.33 ms** | 8,185.14 ms | >600 s (T/O) | >600 s (T/O) | >600 s (T/O) |
| `gzipfile_close_11` | **1.83 ms** | 294.83 ms | >600 s (T/O) | >600 s (T/O) | >600 s (T/O) |
| `rand_net70_40_10` | **5.39 ms** | 12.31 ms | 417.88 ms | 9,516.11 ms | 8,579.44 ms |
| `hwmcc20_iso_rast_p06` | **75.85 ms** | 347.68 ms | 1,764.89 ms | >600 s (T/O) | >600 s (T/O) |
| `hwmcc17_iso_bobsmfpu` | **53.54 ms** | 321.55 ms | 2,755.84 ms | >600 s (T/O) | >600 s (T/O) |
| `vmpc_24` | **1,596.46 ms** | 12,462.32 ms | 6,171.80 ms | 1,653.58 ms | 44,855.40 ms |
| `si2_b03m_m800_03` | **1,944.36 ms** | 6,670.87 ms | 5,892.54 ms | 48,671.18 ms | 44,618.32 ms |

## References

- M. Iser and C. Sinz, *Global Benchmark Database (GBD)*, https://benchmark-database.de/, SAT 2019 / 2024.
- T. Balyo, M. J. H. Heule, M. Iser, M. Järvisalo, and M. Suda (eds.), *Proceedings of SAT Competition 2023 & 2024: Solver, Benchmark and Proof Checker Descriptions*, University of Helsinki, 2023–2024.
- N. Froleyks et al., *SAT Competition 2020*, Artificial Intelligence 301:103572, 2021.
