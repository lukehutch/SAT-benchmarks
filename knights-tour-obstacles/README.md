# Obstacle Knight's Tour — Hamiltonian Cycle on Punched Chessboards (`knights-tour-obstacles`)

## Overview & Origin

Given an $N \times N$ chessboard with a **random number of obstacle pieces** already occupying a subset $B \subset \{0,\dots,N-1\}^2$ of squares (each square occupied independently with probability $d$ via Python's deterministic `random.Random(seed)`), the **Obstacle Knight's Tour** problem asks whether there exists a **closed knight's tour** — a Hamiltonian cycle in the knight's graph over all unoccupied squares $V = \{0,\dots,N-1\}^2 \setminus B$ that visits every unoccupied square exactly once and returns to its starting square.

- **Origin:** **Original** parameterized benchmark suite and generator (MIT [`../LICENSE`](../LICENSE)).
- **Mathematical structure:** Because every knight move alternates square color (white $\leftrightarrow$ black), the knight's graph is bipartite. Random obstacle placements with unequal remaining white/black squares, degree-$<2$ vertices, cut vertices, or Hall matching deficiencies are trivially non-Hamiltonian (`< 20 ms`). Every instance in this curated benchmark is **color-balanced** ($|W| = |B|$), **2-vertex-connected**, and **admits a spanning 2-factor (cycle cover)**, so every UNSAT instance fails strictly via global subtour entanglement rather than local parity or degree obstructions.

### Encoding (Hamiltonian Cycle CNF)

Each punched knight graph $G = (V, E)$ is encoded into flat DIMACS CNF using compact $O(|E|\log |V|)$ **directed 1-factor + strict binary-order Miller–Tucker–Zemlin (MTZ) subtour elimination**:
1. **Arc variables:** $a_{u \to v}$ for every directed knight jump $(u, v)$ between unoccupied squares.
2. **Exact-One in-degree and out-degree** at every vertex $v \in V$ (pairwise AMO for $\deg(v) \le 6$, Sinz sequential counter for $\deg(v) \in \{7, 8\}$).
3. **No 2-cycles:** $(\neg a_{u \to v} \lor \neg a_{v \to u})$ for every undirected knight edge $\{u, v\}$.
4. **Reversal symmetry breaking** at vertex $0$: $\mathrm{succ}(0) < \mathrm{pred}(0)$.
5. **Strict binary-order MTZ rank constraints:** $b = \lceil \log_2 |V| \rceil$ rank bits $r_v$ per vertex $v \ne 0$ enforcing $a_{u \to v} \implies r_u < r_v$ for all $u, v \ne 0$.

### Calibration Sweep Across Board Sizes & Obstacle Densities

Using Frobenius 1C with a **15 s** timeout across $N \in \{8, 10, 11, 12, 13, 14, 15, 16, 18, 20, 22, 24\}$ and obstacle densities $d \in [0.10, 0.35]$:
- **$N \le 11$:** Non-trivial color-balanced boards solve almost exclusively in `0.15–0.65 s`.
- **$N = 12\text{--}16$, $d \in [0.15, 0.26]$:** Hard phase-transition frontier where both SAT and globally entangled UNSAT boards fall cleanly in the **~5–15 second** window on Frobenius.
- **$N \ge 18$:** Nearly all non-trivial color-balanced boards time out past `15 s` on Frobenius.

The final **10-instance benchmark (5 SAT / 5 UNSAT)** selects hard instances spanning $N \in \{12, 14, 15, 16\}$ and $d \in [0.15, 0.26]$ with balanced satisfiability.

## Directory Layout & Regeneration

- `*.cnf` — Original native **DIMACS CNF** encodings (10 instances: 5 SAT / 5 UNSAT; each file includes an ASCII diagram of the obstacle layout in its header comments).
- `aig-version/` — Exact logically equivalent **Binary AIGER 1.9 `.aig`** conversions (10/10 verified with [Berkeley ABC](https://github.com/berkeley-abc/abc)).
- `xcnf-version/` — Exact **[CryptoMiniSat](https://github.com/msoos/cryptominisat) `.xcnf`** conversions.
- `src/gen_knights_tour.py` — Standalone zero-dependency Python 3 generator and closed-tour verifier (`python3 src/gen_knights_tour.py --generate-suite .`), plus `cnf2aig.py` and `cnf2xcnf.py`.

## Problem Parameters & Data Sizes

| Instance | Board | Density $d$ | Obstacles | Free Squares $|V|$ | Seed | Status | CNF Vars | CNF Clauses | CNF Size | AIG ANDs | AIG Size |
|---|:---:|---:|---:|---:|---:|:---:|---:|---:|---:|---:|---:|
| `knights_12x12_d15_obs16_s12150144_sat` | $12 \times 12$ | 0.15 | 16 | 128 | `12150144` | SAT | 6,185 | 17,111 | 326 KB | 47,997 | 176 KB |
| `knights_14x14_d26_obs52_s34280941_sat` | $14 \times 14$ | 0.26 | 52 | 144 | `34280941` | SAT | 6,782 | 18,886 | 365 KB | 53,431 | 197 KB |
| `knights_14x14_d20_obs34_s14203078_sat` | $14 \times 14$ | 0.20 | 34 | 162 | `14203078` | SAT | 8,402 | 23,259 | 451 KB | 65,749 | 247 KB |
| `knights_15x15_d24_obs55_s35244162_sat` | $15 \times 15$ | 0.24 | 55 | 170 | `35244162` | SAT | 8,634 | 23,901 | 464 KB | 67,577 | 254 KB |
| `knights_16x16_d25_obs66_s365029087_sat` | $16 \times 16$ | 0.25 | 66 | 190 | `365029087` | SAT | 9,502 | 26,430 | 514 KB | 74,715 | 282 KB |
| `knights_15x15_d22_obs41_s956712163_unsat` | $15 \times 15$ | 0.22 | 41 | 184 | `956712163` | UNSAT | 9,828 | 27,156 | 527 KB | 76,723 | 290 KB |
| `knights_15x15_d22_obs51_s756748105_unsat` | $15 \times 15$ | 0.22 | 51 | 174 | `756748105` | UNSAT | 8,838 | 24,739 | 480 KB | 69,909 | 263 KB |
| `knights_15x15_d21_obs55_s956405106_unsat` | $15 \times 15$ | 0.21 | 55 | 170 | `956405106` | UNSAT | 8,248 | 22,841 | 444 KB | 64,593 | 242 KB |
| `knights_15x15_d22_obs53_s756776522_unsat` | $15 \times 15$ | 0.22 | 53 | 172 | `756776522` | UNSAT | 8,780 | 24,214 | 470 KB | 68,435 | 258 KB |
| `knights_15x15_d21_obs51_s556324743_unsat` | $15 \times 15$ | 0.21 | 51 | 174 | `556324743` | UNSAT | 8,890 | 24,674 | 479 KB | 69,731 | 263 KB |

## Benchmark Results (1-Core, Flat DIMACS `.cnf`, $T_{\max} = 15\;\text{s}$)

- **Timeout:** $T_{\max} = 15\;\text{s}$ per instance (PAR-2 penalty $30{,}000\;\text{ms}$).
- **Same machine?** **Yes** — all five solvers were run on the exact same **AMD Ryzen 9 5950X** Linux workstation (1 core per run; Frobenius 1C reports the exact median of 3 runs; 0 verdict disagreements; all 5/5 SAT Hamiltonian knight's tours decoded and independently verified).

| Instance | Status | Frobenius 1C | [Kissat](https://github.com/arminbiere/kissat) 4.0.4 | [CaDiCaL](https://github.com/arminbiere/cadical) 3.1.0 | [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18.0 | [`dense-solver 0.0.4`](https://github.com/libdense/dense-solver) |
|---|:---:|---:|---:|---:|---:|---:|
| `knights_12x12_d15_obs16_s12150144_sat` | SAT | 5,441.1 ms | 1,327.4 ms | 1,127.5 ms | **776.6 ms** | >15 s (T/O) |
| `knights_14x14_d26_obs52_s34280941_sat` | SAT | 5,382.9 ms | 973.9 ms | 2,751.0 ms | **806.3 ms** | >15 s (T/O) |
| `knights_14x14_d20_obs34_s14203078_sat` | SAT | 4,732.6 ms | **951.8 ms** | 1,810.1 ms | 1,178.5 ms | >15 s (T/O) |
| `knights_15x15_d24_obs55_s35244162_sat` | SAT | 3,180.2 ms | 2,028.9 ms | **1,516.1 ms** | 3,212.6 ms | >15 s (T/O) |
| `knights_16x16_d25_obs66_s365029087_sat` | SAT | 6,057.3 ms | 2,535.1 ms | 3,307.6 ms | **931.4 ms** | >15 s (T/O) |
| `knights_15x15_d22_obs41_s956712163_unsat` | UNSAT | 5,109.2 ms | 41.4 ms | **14.3 ms** | 271.7 ms | >15 s (T/O) |
| `knights_15x15_d22_obs51_s756748105_unsat` | UNSAT | 5,209.6 ms | 39.9 ms | **13.2 ms** | 271.1 ms | >15 s (T/O) |
| `knights_15x15_d21_obs55_s956405106_unsat` | UNSAT | 5,933.8 ms | 700.1 ms | 733.4 ms | **476.1 ms** | 3,359.8 ms |
| `knights_15x15_d22_obs53_s756776522_unsat` | UNSAT | 5,821.2 ms | 40.6 ms | **13.5 ms** | 853.5 ms | >15 s (T/O) |
| `knights_15x15_d21_obs51_s556324743_unsat` | UNSAT | 7,177.1 ms | 39.3 ms | **14.8 ms** | 343.1 ms | 6,914.1 ms |
| **TOTAL (10 instances, PAR-2)** | **5 / 5** | 10/10 — 54,045.0 ms *(6.23x slower)* | **10/10 — 8,678.3 ms** *(fastest)* | 10/10 — 11,301.6 ms *(1.30x slower)* | 10/10 — 9,121.0 ms *(1.05x slower)* | 2/10 — 250,274.0 ms *(28.84x slower)* |

## References

- A. J. Schwenk, *Which Rectangular Chessboards Have a Knight's Tour?*, Mathematics Magazine 64(5):325–332, 1991.
- C. E. Miller, A. W. Tucker, and R. A. Zemlin, *Integer Programming Formulation of Traveling Salesman Problems*, Journal of the ACM 7(4):326–329, 1960.
- C. Sinz, *Towards an Optimal CNF Encoding of Boolean Cardinality Constraints*, CP 2005, LNCS 3709, pp. 827–831.
- Q. Van Vi, T. Van Kieu, and K. Van To, *StructHCP: Structure-Aware SAT–CEGAR for the Hamiltonian Cycle Problem*, arXiv:2610.14780, 2026.
