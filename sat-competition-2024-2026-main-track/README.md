# SAT Competition 2024, 2025, and 2026 Main Track Corpus (`sat-competition-2024-2026-main-track`)

## Overview & Origin

Complete official benchmark URI manifests and reproducible evaluation/conversion harness for the **1,166 unique Main Track `.cnf.xz` instances** **sourced from the [2024](https://satcompetition.github.io/2024/), [2025](https://satcompetition.github.io/2025/), and [2026](https://satcompetition.github.io/2026/) International SAT Competitions** (400 instances per year; 34 cross-year overlaps; ~11 GiB compressed upstream corpus hosted by the **[Global Benchmark Database (GBD)](https://benchmark-database.de/)**, [`Udopia/gbd`](https://github.com/Udopia/gbd); upstream benchmark license: **CC-BY-4.0**, see [`LICENSE`](LICENSE)).

Because the raw compressed archives total ~11 GiB (exceeding Git repository limits), this directory stores the exact immutable GBD URI manifests (`main_2024.uri`, `main_2025.uri`, `main_2026.uri`), parallel downloader, parallel evaluator, head-to-head analyzer, and exact CNF-to-AIGER converter (`src/cnf2aig.py`) so any instance—or the entire 1,166-instance corpus—can be fetched and converted on demand. *(Fourteen representative SC 2023/2024 CNFs and their pre-converted Binary AIGER 1.9 `.aig` files are stored directly in [`../sat-competition-2023-2024-selected/`](../sat-competition-2023-2024-selected/).)*

## Directory Layout & Usage

- `main_2024.uri` — All 400 SAT Competition 2024 Main Track GBD URIs (26.2 KB)
- `main_2025.uri` — All 400 SAT Competition 2025 Main Track GBD URIs (26.2 KB)
- `main_2026.uri` — All 400 SAT Competition 2026 Main Track GBD URIs (26.2 KB)
- `src/download_sc_main.py` — Parallel GBD `.cnf.xz` fetcher into `~/.cache/sc-main-cnfs`
- `src/run_sc_main.py` — Parallel 1-core-per-instance evaluator with independent Python model verification and official ground-truth cross-checking
- `src/analyze_sc_main.py` — Head-to-head PAR-2 comparator against official SC 2024 (`detailed_main.csv`) and SC 2026 (`sc2026_scores.csv`) published logs
- `src/cnf2aig.py` — Exact Binary AIGER 1.9 converter (`python3 src/cnf2aig.py <in.cnf.xz> <out.aig>`)

## Benchmark Results Across All 1,166 Unique Main Track Instances

Frobenius (1C, unrestricted available memory, `T = 60 s`, 0 errors, 0 unsoundness, 0 verdict disagreements against official SC 2024 & SC 2026 ground truth) compared against official published competition logs/slides (StarExec for SC 2024; LMU/competition sequential clusters for SC 2025–2026; different CPU hardware affects absolute runtimes, though rankings and PAR-2 magnitudes are comparable within an order of magnitude):

| Year | Solver (Track / Official Rank) | $T = 15\;\text{s}$ Solved | $T = 15\;\text{s}$ PAR-2 | $T = 60\;\text{s}$ Solved | $T = 60\;\text{s}$ PAR-2 | Official $T = 5{,}000\;\text{s}$ Solved | Official PAR-2 |
|---|---|---:|---:|---:|---:|---:|---:|
| **SC 2024** | **Frobenius 1C (ours)** | **72 / 400** | **25.04 s** | **111 / 400** | **91.02 s** | *n/r* | *n/r* |
| *(400 CNFs)* | [`kissat-sc2024`](https://github.com/arminbiere/kissat) (Main #1 Gold) | 43 / 400 | 27.15 s | 81 / 400 | 99.47 s | 306 / 400 | 2,788.13 s |
| | [`CaDiCaL`](https://github.com/arminbiere/cadical) (Main #7) | 26 / 400 | 28.24 s | 54 / 400 | 106.69 s | 284 / 400 | 3,494.11 s |
| | [`BreakID-Kissat`](https://github.com/meelgroup/breakid) (Main #6) | 23 / 400 | 28.55 s | 50 / 400 | 107.75 s | 284 / 400 | 3,461.77 s |
| | [`Kissat_MAB-DC`](https://satcompetition.github.io/2024/) (Main #2 Silver) | 20 / 400 | 28.81 s | 50 / 400 | 108.11 s | 290 / 400 | 3,435.23 s |
| **SC 2025** | **Frobenius 1C (ours)** | **95 / 400** | **23.51 s** | **141 / 400** | **81.92 s** | *n/r* | *n/r* |
| *(400 CNFs)* | [`AE-Kissat-MAB`](https://github.com/FSQH-dh/AE_kissat2025_MAB) (Main #1 Gold) | —† | —† | —† | —† | 327 / 400 | 2,264.73 s |
| | [`Kissat-public`](https://github.com/arminbiere/kissat) (Main #2 Silver) | —† | —† | —† | —† | 321 / 400 | 2,423.38 s |
| | [`Kissat-VSA`](https://satcompetition.github.io/2025/downloads.html) (Main #3 Bronze) | —† | —† | —† | —† | 317 / 400 | 2,478.45 s |
| **SC 2026** | **Frobenius 1C (ours)** | **122 / 400** | **21.37 s** | **139 / 400** | **80.24 s** | *n/r* | *n/r* |
| *(400 CNFs)* | [`satsuma-iter-kissat`](https://github.com/markusa4/satsuma) (Main #1 Gold) | 70 / 400 | 25.13 s | 112 / 400 | 90.46 s | 276 / 400 | 3,647.02 s |
| | [`Lymphosat`](https://c.mov/lymphosat/) (AI-Track #1 Gold) | 81 / 400 | 24.58 s | 109 / 400 | 90.07 s | 251 / 400 | 4,176.90 s |
| | [`satsuma-iter-ae-kissat-mab`](https://github.com/markusa4/satsuma) (Main #2) | 66 / 400 | 25.37 s | 108 / 400 | 91.58 s | 269 / 400 | 3,696.84 s |
| | [`kissat-mab-hypre`](https://satcompetition.github.io/2026/downloads.html) (Main #3) | 63 / 400 | 25.73 s | 102 / 400 | 92.81 s | 255 / 400 | 3,996.29 s |
| | [`kissat-biere`](https://github.com/arminbiere/kissat) (Main #15) | 41 / 400 | 27.38 s | 74 / 400 | 100.38 s | 238 / 400 | 4,611.54 s |

† SC 2025 published aggregate 5,000 s slide standings without a per-instance runtime CSV.
*Notable unique wins:* Frobenius solved **12** SC 2024 instances within 60 s where [`kissat-sc2024`](https://github.com/arminbiere/kissat) timed out past 5,000 s (**26** vs. [`CaDiCaL`](https://github.com/arminbiere/cadical)), and **18** SC 2026 instances within 60 s where [`satsuma-iter-kissat`](https://github.com/markusa4/satsuma) timed out past 5,000 s (**41** vs. [`Lymphosat`](https://c.mov/lymphosat/), **53** vs. [`kissat-biere`](https://github.com/arminbiere/kissat)).

<!-- BEGIN_STRUCTURAL_ANALYSIS -->
## Phase-Transition & Structural Analysis

*Auto-generated by [`../src/analyze_benchmarks.py`](../src/analyze_benchmarks.py). This directory stores **1,200 immutable GBD URI entries** across 3 manifest(s) rather than raw multi-gigabyte CNFs; run `python3 ../src/analyze_benchmarks.py --file <downloaded.cnf.xz>` on any downloaded instance, or see [`../sat-competition-2023-2024-selected/README.md`](../sat-competition-2023-2024-selected/README.md) for structural and phase-transition metrics on 14 curated SAT Competition Main Track CNFs.*
<!-- END_STRUCTURAL_ANALYSIS -->

## References

- International SAT Competition Archives (2024, 2025, 2026): https://satcompetition.github.io/
- Global Benchmark Database (GBD): https://benchmark-database.de/
- N. Froleyks, M. Heule, M. Iser, M. Järvisalo, and M. Suda, *SAT Competition 2020*, Artificial Intelligence 301:103572, 2021.
