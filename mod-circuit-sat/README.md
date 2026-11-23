# Exact Synthesis of Optimal $\mathrm{MOD}_n^{3,r}$ Boolean Circuits (`mod-circuit-sat`)

## Provenance & Credit

- **Author & Recommended by:** `@vzhilin_me` (Twitter/X, GitHub [`vzhn`](https://github.com/vzhn))
- **Upstream Repository:** [`vzhn/mod-circuit-sat`](https://github.com/vzhn/mod-circuit-sat)
- **Underlying Encoding Paper:** A. S. Kulikov, D. Pechenev, and N. Slezkin, *"SAT-based Circuit Local Improvement"*, [`arXiv:2102.12579`](https://arxiv.org/abs/2102.12579) (with symmetry and structure reductions added in `vzhn/mod-circuit-sat`).
- **License:** Upstream repository does not bundle a separate `LICENSE` file; `src/modsat.py` and `src/gen_open_cases.py` are mirrored verbatim from `vzhn/mod-circuit-sat` for reproducibility and benchmarking.

## Problem Description

Exact Boolean circuit synthesis asks for the minimum number of 2-input gates over the full binary basis $B_2$ needed to compute the symmetric modular-counting function:
$$\mathrm{MOD}_n^{m,r}(x_1, \dots, x_n) \;=\; \bigl[\, (x_1 + \dots + x_n) \bmod m = r \,\bigr].$$

For a fixed input width $n$, modulus $m = 3$, target residue $r \in \{0, 1, 2\}$, and gate budget $s$, `src/modsat.py` generates a DIMACS CNF (plus a JSON variable map in `maps/` so any satisfying assignment decodes directly into a verified $B_2$ circuit over all $2^n$ inputs). The problem exhibits sharp optimality thresholds ($s = s^* - 1$ UNSAT vs. $s = s^*$ SAT), and the $n = 6$, $s \le 12$ cases remain challenging open synthesis targets.

## Corpus & Data Sizes

Generated via `src/modsat.py` and `src/gen_open_cases.py`: **11 CNFs** (9 decidable optimality-boundary instances for $n \in \{3, 4, 5\}$ + 2 open $n = 6$ frontier instances), **11 exact Binary AIGER 1.9 conversions** in `aig-version/` (all 11/11 verified via Berkeley ABC `read_aiger`), and **11 decoder variable maps** in `maps/`:

| Instance | $(n, m, r, s)$ | Status | Vars | Clauses | CNF Size | AIG AND Gates |
|---|---|:---:|---:|---:|---:|---:|
| `mod3_n3_r0_s3_sat.cnf` | $(3,3,0,3)$ | SAT | 65 | 435 | 5.4 KB | 1,053 |
| `mod3_n3_r1_s3_unsat.cnf` | $(3,3,1,3)$ | UNSAT | 65 | 426 | 5.3 KB | 1,042 |
| `mod3_n3_r1_s4_sat.cnf` | $(3,3,1,4)$ | SAT | 107 | 903 | 12.2 KB | 2,267 |
| `mod3_n4_r2_s5_unsat.cnf` | $(4,3,2,5)$ | UNSAT | 250 | 4,124 | 64.0 KB | 9,896 |
| `mod3_n4_r2_s6_sat.cnf` | $(4,3,2,6)$ | SAT | 343 | 6,762 | 114.2 KB | 16,515 |
| `mod3_n4_r0_s6_unsat.cnf` | $(4,3,0,6)$ | UNSAT | 343 | 6,884 | 115.4 KB | 16,785 |
| `mod3_n4_r0_s7_sat.cnf` | $(4,3,0,7)$ | SAT | 454 | 10,597 | 184.4 KB | 26,176 |
| `mod3_n5_r1_s8_unsat.cnf` | $(5,3,1,8)$ | UNSAT | 825 | 33,493 | 618.3 KB | 81,208 |
| `mod3_n5_r1_s9_sat.cnf` | $(5,3,1,9)$ | SAT | 1,019 | 46,402 | 871.1 KB | 113,738 |
| `mod3_n6_r1_le12_open.cnf` | $(6,3,1,\le 12)$ | Open | 2,309 | 185,679 | 4.22 MB | 474,426 |
| `mod3_n6_r2_le12_open.cnf` | $(6,3,2,\le 12)$ | Open | 2,309 | 185,760 | 4.22 MB | 474,549 |

## Comparative 1-Core Benchmark Results ($n \in \{3, 4, 5\}$, 9 Decidable Instances, $T_{\max} = 10\;\text{s}$)

- **Hardware & Protocol:** Same machine (AMD Ryzen 9 5950X, Linux, 1 core per run, $T_{\max} = 10\;\text{s}$, PAR-2 penalty $20{,}000\;\text{ms}$, identical flat `.cnf` input, 0 disagreements).

| Instance | Verdict | Kissat 4.0.4 | CaDiCaL 3.1.0 | Frobenius 1C |
|---|---:|---:|---:|---:|
| `mod3_n3_r0_s3_sat.cnf` | SAT | **0.86 ms** | 1.96 ms | 3.06 ms |
| `mod3_n3_r1_s3_unsat.cnf` | UNSAT | **1.19 ms** | 1.54 ms | 3.39 ms |
| `mod3_n3_r1_s4_sat.cnf` | SAT | 7.12 ms | **1.65 ms** | 4.79 ms |
| `mod3_n4_r2_s5_unsat.cnf` | UNSAT | 34.92 ms | **10.22 ms** | 109.28 ms |
| `mod3_n4_r2_s6_sat.cnf` | SAT | 68.87 ms | **28.18 ms** | 143.23 ms |
| `mod3_n4_r0_s6_unsat.cnf` | UNSAT | 295.11 ms | **155.00 ms** | 415.03 ms |
| `mod3_n4_r0_s7_sat.cnf` | SAT | 208.93 ms | **12.62 ms** | 399.22 ms |
| `mod3_n5_r1_s8_unsat.cnf` | UNSAT *(~25 s)* | T/O | T/O | T/O |
| `mod3_n5_r1_s9_sat.cnf` | SAT | **4,436.82 ms** | 7,151.42 ms | 8,976.47 ms |
| **Summary (Solved / PAR-2)** | **8 / 9** | **25,053.82 ms** *(fastest)* | **27,362.59 ms** *(1.09x slower)* | **30,054.47 ms** *(1.20x slower)* |
