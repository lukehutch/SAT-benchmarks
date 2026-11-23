# Aloul Symmetry, FPGA Switch-Box, and Multiplier Factoring Benchmarks

## Provenance & Credit

- **Recommended by:** `@merlin_numa` (Twitter/X)
- **Authors:** Fadi A. Aloul, Arathi Ramani, Igor L. Markov, and Karem A. Sakallah (University of Michigan / American University of Sharjah)
- **Upstream Homepage:** [Fadi Aloul — SAT Benchmarks](https://www.aloul.net/benchmarks.html)
- **License:** Classic public academic benchmarks contributed to the SAT 2002 Competition and published on `aloul.net`; no separate upstream `LICENSE` file is bundled in the archives.
- **Primary Papers:**
  - F. A. Aloul, A. Ramani, I. L. Markov, and K. A. Sakallah, *"Solving Difficult SAT Instances in the Presence of Symmetry"*, Proc. 39th Design Automation Conference (DAC 2002), pp. 731–736.
  - F. A. Aloul, A. Ramani, I. L. Markov, and K. A. Sakallah, *"Solving Difficult Instances of Boolean Satisfiability in the Presence of Symmetry"*, IEEE Trans. Computer-Aided Design (TCAD), 22(9), pp. 1117–1137, Sept. 2003.

## Problem Description

This classic EDA / symmetry-breaking collection contains **82 DIMACS CNF instances** across five families (variables and clauses randomly reordered in the FPGA and factoring families):

1. **`DAC02Bench/` (32 instances):** Mixed suite from the DAC 2002 paper spanning FPGA switch-boxes, global routing (SAT), pigeonhole (`hole`, `chnl`), and randomized Urquhart parity instances (`Urq3_5`, `Urq4_5`, `Urq5_5`).
2. **`FPGA_SB_UNS/` (10 instances, SAT 2002 *"Homer"*):** Unsatisfiable FPGA switch-box routing formulas (`fpga10_*`, `fpga11_*`) with rich permutation symmetry and cardinality bottlenecks.
3. **`FPGA_SB_SAT/` (11 instances, SAT 2002 *"Bart"*):** Satisfiable FPGA switch-box routing formulas (`fpga10_*`, `fpga12_*`, `fpga13_*`).
4. **`difp_a/` (14 instances, SAT):** Difficult Integer Factorization Problems encoded via **Array multipliers** multiplying two $n$-bit primes ($n \in \{19, 20, 21\}$).
5. **`difp_w/` (15 instances, SAT):** Difficult Integer Factorization Problems encoded via **Wallace Tree multipliers** ($n \in \{19, 20, 21\}$).

## Corpus & Data Sizes

All **82 CNFs** (`6.21 MB` total) plus **82 exact Binary AIGER 1.9 conversions** in `aig-version/` (all 82/82 verified via Berkeley ABC `read_aiger`) and `src/cnf2aig.py`:

| Subdirectory | Instances | Status | Vars Range | Clauses Range | CNF Size | AIG Files |
|---|---:|:---:|---:|---:|---:|---:|
| `DAC02Bench/` | 32 | Mixed | 46–1,056 | 204–10,862 | 1.06 MB | 32 |
| `FPGA_SB_SAT/` | 11 | SAT | 120–234 | 448–1,242 | 118 KB | 11 |
| `FPGA_SB_UNS/` | 10 | UNSAT | 220–440 | 1,122–4,220 | 251 KB | 10 |
| `difp_a/` | 14 | SAT | 1,201–1,453 | 6,563–7,967 | 1.69 MB | 14 |
| `difp_w/` | 15 | SAT | 1,755–2,125 | 10,446–12,677 | 3.09 MB | 15 |
| **Total** | **82** | | **46–2,125** | **204–12,677** | **6.21 MB** | **82** |

## Comparative 1-Core Benchmark Results (`FPGA_SB_UNS` + `FPGA_SB_SAT`, 21 Instances, $T_{\max} = 5\;\text{s}$)

- **Hardware & Protocol:** Same machine (AMD Ryzen 9 5950X, Linux, 1 core per run, $T_{\max} = 5\;\text{s}$, PAR-2 penalty $10{,}000\;\text{ms}$, identical flat `.cnf` input, 0 disagreements).

| Solver (1C) | Solved | SAT / UNSAT | Total PAR-2 (21 files) | Relative PAR-2 |
|---|---:|:---:|---:|---|
| **`dense-solver 0.0.4`** | **21 / 21** | **11 / 10** | **27.45 ms** | *(fastest)* |
| **Frobenius 1C** | **21 / 21** | **11 / 10** | **219.53 ms** | *(8.00x slower)* |
| Kissat 4.0.4 | 12 / 21 | 11 / 1 | 92,980.13 ms | *(3,387x slower)* |
| CaDiCaL 3.1.0 | 11 / 21 | 11 / 0 | 100,091.48 ms | *(3,646x slower)* |
