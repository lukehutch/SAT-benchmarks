# SAT Competition 2024, 2025, and 2026 Main Track Corpus (`sat-competition-2024-2026-main-track`)

## Overview & Origin

Complete official benchmark URI manifests and reproducible evaluation/conversion harness for the **1,166 unique Main Track `.cnf.xz` instances** from the **2024, 2025, and 2026 International SAT Competitions** (400 instances per year; 34 cross-year overlaps; ~11 GiB compressed upstream corpus on the Global Benchmark Database).

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

Frobenius (1C, LLVM PGO, unrestricted available memory, `T = 60 s`, 0 errors, 0 unsoundness, 0 verdict disagreements against official SC 2024 & SC 2026 ground truth) compared against official published competition logs/slides (StarExec for SC 2024; LMU/competition sequential clusters for SC 2025–2026; different CPU hardware affects absolute runtimes, though rankings and PAR-2 magnitudes are comparable within an order of magnitude):

| Year | Solver (Track / Official Rank) | $T = 15\;\text{s}$ Solved | $T = 15\;\text{s}$ PAR-2 | $T = 60\;\text{s}$ Solved | $T = 60\;\text{s}$ PAR-2 | Official $T = 5{,}000\;\text{s}$ Solved | Official PAR-2 |
|---|---|---:|---:|---:|---:|---:|---:|
| **SC 2024** | **Frobenius 1C PGO (ours)** | **72 / 400** | **25.04 s** | **111 / 400** | **91.02 s** | *n/r* | *n/r* |
| *(400 CNFs)* | `kissat-sc2024` (Main #1 Gold) | 43 / 400 | 27.15 s | 81 / 400 | 99.47 s | 306 / 400 | 2,788.13 s |
| | `CaDiCaL` (Main #7) | 26 / 400 | 28.24 s | 54 / 400 | 106.69 s | 284 / 400 | 3,494.11 s |
| | `BreakID-Kissat` (Main #6) | 23 / 400 | 28.55 s | 50 / 400 | 107.75 s | 284 / 400 | 3,461.77 s |
| | `Kissat_MAB-DC` (Main #2 Silver) | 20 / 400 | 28.81 s | 50 / 400 | 108.11 s | 290 / 400 | 3,435.23 s |
| **SC 2025** | **Frobenius 1C PGO (ours)** | **95 / 400** | **23.51 s** | **141 / 400** | **81.92 s** | *n/r* | *n/r* |
| *(400 CNFs)* | `AE-Kissat-MAB` (Main #1 Gold) | —† | —† | —† | —† | 327 / 400 | 2,264.73 s |
| | `Kissat-public` (Main #2 Silver) | —† | —† | —† | —† | 321 / 400 | 2,423.38 s |
| | `Kissat-VSA` (Main #3 Bronze) | —† | —† | —† | —† | 317 / 400 | 2,478.45 s |
| **SC 2026** | **Frobenius 1C PGO (ours)** | **122 / 400** | **21.37 s** | **139 / 400** | **80.24 s** | *n/r* | *n/r* |
| *(400 CNFs)* | `satsuma-iter-kissat` (Main #1 Gold) | 70 / 400 | 25.13 s | 112 / 400 | 90.46 s | 276 / 400 | 3,647.02 s |
| | `Lymphosat` (AI-Track #1 Gold) | 81 / 400 | 24.58 s | 109 / 400 | 90.07 s | 251 / 400 | 4,176.90 s |
| | `satsuma-iter-ae-kissat-mab` (Main #2) | 66 / 400 | 25.37 s | 108 / 400 | 91.58 s | 269 / 400 | 3,696.84 s |
| | `kissat-mab-hypre` (Main #3) | 63 / 400 | 25.73 s | 102 / 400 | 92.81 s | 255 / 400 | 3,996.29 s |
| | `kissat-biere` (Main #15) | 41 / 400 | 27.38 s | 74 / 400 | 100.38 s | 238 / 400 | 4,611.54 s |

† SC 2025 published aggregate 5,000 s slide standings without a per-instance runtime CSV.
*Notable unique wins:* Frobenius solved **12** SC 2024 instances within 60 s where `kissat-sc2024` timed out past 5,000 s (**26** vs. `CaDiCaL`), and **18** SC 2026 instances within 60 s where `satsuma-iter-kissat` timed out past 5,000 s (**41** vs. `Lymphosat`, **53** vs. `kissat-biere`).

## References

- International SAT Competition Archives (2024, 2025, 2026): https://satcompetition.github.io/
- Global Benchmark Database (GBD): https://benchmark-database.de/
- N. Froleyks, M. Heule, M. Iser, M. Järvisalo, and M. Suda, *SAT Competition 2020*, Artificial Intelligence 301:103572, 2021.
