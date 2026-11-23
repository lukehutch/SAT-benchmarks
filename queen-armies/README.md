# Peaceable Queen Armies (`queen-armies`)

## Overview & Origin

The **Peaceable Queen Armies** problem asks whether $A \ge 2$ opposing armies of at least $k$ chess queens each can be placed simultaneously on an $R \times C$ chessboard so that **no queen attacks any queen of a different army** along a row, column, or diagonal (queens belonging to the *same* army are allowed to attack one another).

- **Origin:** **Original** parameterized CNF generator (MIT [`../LICENSE`](../LICENSE)), directly inspired by **Christopher Wolfram's** [*Chess Queen Armies With SAT Solvers*](https://christopherwolfram.com/projects/queen-armies/) (September 2022) and the Rosetta Code [*Peaceful Chess Queen Armies*](https://rosettacode.org/wiki/Peaceful_chess_queen_armies) challenge.
- **OEIS Sequences (square $n \times n$ maximal equal-army sizes $a_A(n)$):**
  - $A = 2$ armies ([OEIS A250000](https://oeis.org/A250000)): $0, 0, 1, 2, 4, 5, 7, 9, 12, 14, 17, 21, 24, 28, 32, \dots$ for $n = 1\text{--}15$.
  - $A = 3$ armies ([OEIS A277433](https://oeis.org/A277433)): $0, 0, 0, 1, 1, 2, 3, 4, 5, 7, 8, 10, 11, 14, 15, 17, \dots$ for $n = 1\text{--}16$.
  - $A = 4$ armies ([OEIS A277434](https://oeis.org/A277434)): $0, 0, 0, 0, 1, 1, 2, 3, 4, 5, 6, 7, 8, \dots$ for $n = 1\text{--}13$.

### Encoding

Each instance is encoded in standard flat DIMACS CNF:
1. **Queen placement variables:** $q_{r,c,a}$ ($0 \le r < R$, $0 \le c < C$, $0 \le a < A$), true iff a queen of army $a$ stands on square $(r, c)$.
2. **Line-occupancy non-attacking constraints:** For every line $\ell$ (each row, column, main diagonal, and anti-diagonal of length $\ge 2$):
   - For $A = 2$: a single polarity variable $L_\ell$ with clauses $(\neg q_{r,c,0} \lor L_\ell)$ and $(\neg q_{r,c,1} \lor \neg L_\ell)$, ensuring no line contains both armies (and simultaneously enforcing per-square mutual exclusion).
   - For $A \ge 3$: per-army occupancy variables $L_{\ell, a}$ with clauses $(\neg q_{r,c,a} \lor L_{\ell,a})$ and pairwise mutual exclusion $(\neg L_{\ell,a} \lor \neg L_{\ell,b})$ for all $a < b$.
3. **Army-size cardinality constraints:** $\sum_{r,c} q_{r,c,a} \ge k$ for each army $a \in \{0, \dots, A-1\}$, encoded via **Sinz (2005)** monotone sequential counters.

### Calibration & Selection

Instances were swept across board dimensions $R \times C$ and army counts $A \in \{2, 3, 4\}$ with Frobenius 1C up to a **15 s** timeout. For smaller boards (e.g., $7 \times 7$ to $13 \times 13$ SAT or $7 \times 7$ UNSAT), solving completes in `< 2 s`; past the 15 s frontier (e.g., $A=2$ UNSAT at $8 \times 8, k=10$ or $A=3$ SAT at $17 \times 17, k=19$), solvers time out. The final **8-instance suite (4 SAT / 4 UNSAT)** selects instances positioned cleanly in the **~5–15 second** difficulty band without timing out across repeated runs.

## Directory Layout & Regeneration

- `*.cnf` — Original native **DIMACS CNF** encodings (8 instances: 4 SAT / 4 UNSAT).
- `aig-version/` — Exact logically equivalent **Binary AIGER 1.9 `.aig`** conversions (8/8 verified with [Berkeley ABC](https://github.com/berkeley-abc/abc)).
- `xcnf-version/` — Exact **[CryptoMiniSat](https://github.com/msoos/cryptominisat) `.xcnf`** conversions.
- `src/gen_queen_armies.py` — Standalone zero-dependency Python 3 generator and witness verifier (`python3 src/gen_queen_armies.py --generate-suite .`), plus `cnf2aig.py` and `cnf2xcnf.py`.

## Problem Parameters & Data Sizes

| Instance | Armies $A$ | Board $R \times C$ | Army Size $k$ | Status | CNF Vars | CNF Clauses | CNF Size | AIG ANDs | AIG Size |
|---|---:|:---:|---:|:---:|---:|---:|---:|---:|---:|
| `queen_armies_a3_13x16_k14_sat` | 3 | $13 \times 16$ | 14 | SAT | 9,330 | 19,032 | 268 KB | 46,481 | 185 KB |
| `queen_armies_a4_14x16_k9_sat` | 4 | $14 \times 16$ | 9 | SAT | 9,152 | 19,020 | 267 KB | 45,919 | 183 KB |
| `queen_armies_a2_15x16_k33_sat` | 2 | $15 \times 16$ | 33 | SAT | 15,351 | 31,002 | 465 KB | 76,719 | 315 KB |
| `queen_armies_a3_15x16_k16_sat` | 3 | $15 \times 16$ | 16 | SAT | 12,141 | 24,732 | 358 KB | 60,572 | 246 KB |
| `queen_armies_a3_7x8_k5_unsat` | 3 | $7 \times 8$ | 5 | UNSAT | 1,095 | 2,232 | 27 KB | 5,255 | 17 KB |
| `queen_armies_a3_6x10_k5_unsat` | 3 | $6 \times 10$ | 5 | UNSAT | 1,176 | 2,397 | 30 KB | 5,645 | 19 KB |
| `queen_armies_a3_6x11_k6_unsat` | 3 | $6 \times 11$ | 6 | UNSAT | 1,476 | 3,006 | 38 KB | 7,133 | 23 KB |
| `queen_armies_a2_7x10_k12_unsat` | 2 | $7 \times 10$ | 12 | UNSAT | 1,733 | 3,510 | 46 KB | 8,541 | 27 KB |

## Benchmark Results (1-Core, Flat DIMACS `.cnf`, $T_{\max} = 15\;\text{s}$)

- **Timeout:** $T_{\max} = 15\;\text{s}$ per instance (PAR-2 penalty $30{,}000\;\text{ms}$).
- **Same machine?** **Yes** — all five solvers were run on the exact same **AMD Ryzen 9 5950X** Linux workstation (1 core per run; Frobenius 1C reports the exact median of 3 runs; 0 verdict disagreements; all 4/4 SAT placements independently verified for non-attacking armies of size $\ge k$).

| Instance | Status | Frobenius 1C | [Kissat](https://github.com/arminbiere/kissat) 4.0.4 | [CaDiCaL](https://github.com/arminbiere/cadical) 3.1.0 | [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18.0 | [`dense-solver 0.0.4`](https://github.com/libdense/dense-solver) |
|---|:---:|---:|---:|---:|---:|---:|
| `queen_armies_a3_13x16_k14_sat` | SAT | **4,881.3 ms** | >15 s (T/O) | >15 s (T/O) | >15 s (T/O) | >15 s (T/O) |
| `queen_armies_a4_14x16_k9_sat` | SAT | **5,042.9 ms** | >15 s (T/O) | >15 s (T/O) | >15 s (T/O) | >15 s (T/O) |
| `queen_armies_a2_15x16_k33_sat` | SAT | 6,070.6 ms | 5,757.6 ms | 4,106.2 ms | **1,830.4 ms** | >15 s (T/O) |
| `queen_armies_a3_15x16_k16_sat` | SAT | **6,070.9 ms** | >15 s (T/O) | >15 s (T/O) | >15 s (T/O) | >15 s (T/O) |
| `queen_armies_a3_7x8_k5_unsat` | UNSAT | **6,221.1 ms** | 11,902.2 ms | >15 s (T/O) | >15 s (T/O) | 13,448.9 ms |
| `queen_armies_a3_6x10_k5_unsat` | UNSAT | **8,321.4 ms** | 13,366.5 ms | >15 s (T/O) | >15 s (T/O) | 11,398.4 ms |
| `queen_armies_a3_6x11_k6_unsat` | UNSAT | **10,444.0 ms** | >15 s (T/O) | >15 s (T/O) | >15 s (T/O) | >15 s (T/O) |
| `queen_armies_a2_7x10_k12_unsat` | UNSAT | 9,620.1 ms | **9,577.9 ms** | >15 s (T/O) | >15 s (T/O) | >15 s (T/O) |
| **TOTAL (8 instances, PAR-2)** | **4 / 4** | **8/8 — 56,672.4 ms** *(fastest)* | 4/8 — 160,604.2 ms *(2.83x slower)* | 1/8 — 214,106.2 ms *(3.78x slower)* | 1/8 — 211,830.4 ms *(3.74x slower)* | 2/8 — 204,847.3 ms *(3.61x slower)* |

## References

- C. Wolfram, [*Chess Queen Armies With SAT Solvers*](https://christopherwolfram.com/projects/queen-armies/), September 2022.
- Rosetta Code, [*Peaceful Chess Queen Armies*](https://rosettacode.org/wiki/Peaceful_chess_queen_armies).
- OEIS Foundation Inc., [*A250000*](https://oeis.org/A250000), [*A277433*](https://oeis.org/A277433), and [*A277434*](https://oeis.org/A277434): Maximal peaceable armies of 2, 3, and 4 queens on an $n \times n$ board.
- S. Ainley, *Mathematical Puzzles*, G. Bell & Sons, 1977.
- R. A. Bosch, *Peaceably Coexisting Armies of Queens*, Optima 62:6–9, 1999.
- B. M. Smith, K. E. Petrie, and I. P. Gent, *Models and Symmetry Breaking for "Peaceably Coexisting Armies of Queens"*, CPAIOR 2004, LNCS 3011, pp. 271–286.
- C. Sinz, *Towards an Optimal CNF Encoding of Boolean Cardinality Constraints*, CP 2005, LNCS 3709, pp. 827–831.
