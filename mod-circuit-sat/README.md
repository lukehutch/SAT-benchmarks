# Exact Synthesis of Optimal $\mathrm{MOD}_n^{3,r}$ Boolean Circuits (`mod-circuit-sat`)

## Provenance & Credit

- **Author & Recommended by:** [`@vzhilin_me`](https://twitter.com/vzhilin_me) (Twitter/X, GitHub [`vzhn`](https://github.com/vzhn))
- **Upstream Repository:** [`vzhn/mod-circuit-sat`](https://github.com/vzhn/mod-circuit-sat)
- **Underlying Encoding Paper:** A. S. Kulikov, D. Pechenev, and N. Slezkin, *"SAT-based Circuit Local Improvement"*, [`arXiv:2102.12579`](https://arxiv.org/abs/2102.12579) (with symmetry and structure reductions added in `vzhn/mod-circuit-sat`).
- **License:** Upstream repository does not bundle a separate `LICENSE` file; `src/modsat.py` and `src/gen_open_cases.py` are mirrored verbatim from `vzhn/mod-circuit-sat` for reproducibility and benchmarking.

## Problem Description

Exact Boolean circuit synthesis asks for the minimum number of 2-input gates over the full binary basis $B_2$ needed to compute the symmetric modular-counting function:
$$\mathrm{MOD}_n^{m,r}(x_1, \dots, x_n) \;=\; \bigl[\, (x_1 + \dots + x_n) \bmod m = r \,\bigr].$$

For a fixed input width $n$, modulus $m = 3$, target residue $r \in \{0, 1, 2\}$, and gate budget $s$, `src/modsat.py` generates a DIMACS CNF (plus a JSON variable map in `maps/` so any satisfying assignment decodes directly into a verified $B_2$ circuit over all $2^n$ inputs). The problem exhibits sharp optimality thresholds ($s = s^* - 1$ UNSAT vs. $s = s^*$ SAT), and the $n = 6$, $s \le 12$ cases remain challenging open synthesis targets.

## Corpus & Data Sizes (Four Formats)

Generated via `src/modsat.py` and `src/gen_open_cases.py`:
- **`cnf-orig/`:** 11 native `.cnf.xz` files (`650.5 KB`; 9 decidable optimality-boundary instances for $n \in \{3, 4, 5\}$ + 2 open $n = 6$ frontier instances).
- **`aig-converted/`:** 11 exact Binary AIGER 1.9 `.aig.xz` conversions (`1.42 MB`, all 11/11 verified via [Berkeley ABC](https://github.com/berkeley-abc/abc) `read_aiger`).
- **`xcnf-converted/`:** 11 lossless [CryptoMiniSat](https://github.com/msoos/cryptominisat) `.xcnf.xz` conversions (`653.5 KB`).
- **`anf-converted/`:** 11 lossless linear-size DIMACS-ANF `.anf.xz` conversions (`4.03 MB`, degree $\le 3$, generated via [`../src/to_anf.py`](../src/to_anf.py)).
- **`maps/`:** 11 decoder variable maps.

| Instance | $(n, m, r, s)$ | Status | Vars | Clauses | `.cnf.xz` | AIG ANDs | `.anf.xz` |
|---|---|:---:|---:|---:|---:|---:|---:|
| `mod3_n3_r0_s3_sat` | $(3,3,0,3)$ | SAT | 65 | 435 | 1.2 KB | 1,053 | 2.7 KB |
| `mod3_n3_r1_s3_unsat` | $(3,3,1,3)$ | UNSAT | 65 | 426 | 1.2 KB | 1,042 | 2.6 KB |
| `mod3_n3_r1_s4_sat` | $(3,3,1,4)$ | SAT | 107 | 903 | 2.2 KB | 2,267 | 5.8 KB |
| `mod3_n4_r2_s5_unsat` | $(4,3,2,5)$ | UNSAT | 250 | 4,124 | 7.6 KB | 9,896 | 26.0 KB |
| `mod3_n4_r2_s6_sat` | $(4,3,2,6)$ | SAT | 343 | 6,762 | 11.8 KB | 16,515 | 44.9 KB |
| `mod3_n4_r0_s6_unsat` | $(4,3,0,6)$ | UNSAT | 343 | 6,884 | 11.7 KB | 16,785 | 45.9 KB |
| `mod3_n4_r0_s7_sat` | $(4,3,0,7)$ | SAT | 454 | 10,597 | 17.6 KB | 26,176 | 74.3 KB |
| `mod3_n5_r1_s8_unsat` | $(5,3,1,8)$ | UNSAT | 825 | 33,493 | 46.0 KB | 81,208 | 231.7 KB |
| `mod3_n5_r1_s9_sat` | $(5,3,1,9)$ | SAT | 1,019 | 46,402 | 59.9 KB | 113,738 | 329.3 KB |
| `mod3_n6_r1_le12_open` | $(6,3,1,\le 12)$ | Open | 2,309 | 185,679 | 242.5 KB | 474,426 | 1.64 MB |
| `mod3_n6_r2_le12_open` | $(6,3,2,\le 12)$ | Open | 2,309 | 185,760 | 248.7 KB | 474,549 | 1.64 MB |

## Comparative 1-Core Benchmark Results ($n \in \{3, 4, 5\}$, 9 Decidable Instances, $T_{\max} = 10\;\text{s}$ & $30\;\text{s}$)

- **Hardware & Protocol:** Same machine (**AMD Ryzen 9 5950X**, Linux, 1 core pinned per run via `taskset -c 0`, sequential execution, identical flat `.cnf` input, 0 verdict disagreements; all 5/5 SAT models verified via `src/modsat.py decode`).

| Instance | Verdict | Frobenius 1C | [CaDiCaL](https://github.com/arminbiere/cadical) 3.1.0 | [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18.0 | [dense-solver](https://github.com/libdense/dense-solver) 0.0.4 | [Kissat](https://github.com/arminbiere/kissat) 4.0.4 |
|---|---:|---:|---:|---:|---:|---:|
| `mod3_n3_r0_s3_sat.cnf` | SAT | 4.04 ms | 2.85 ms | 18.26 ms | **1.52 ms** | 1.94 ms |
| `mod3_n3_r1_s3_unsat.cnf` | UNSAT | 3.61 ms | 2.32 ms | 12.84 ms | 1.66 ms | **1.57 ms** |
| `mod3_n3_r1_s4_sat.cnf` | SAT | 4.31 ms | 2.53 ms | 19.06 ms | **1.99 ms** | 6.81 ms |
| `mod3_n4_r2_s5_unsat.cnf` | UNSAT | 17.04 ms | 10.26 ms | 186.51 ms | **10.15 ms** | 34.78 ms |
| `mod3_n4_r2_s6_sat.cnf` | SAT | 22.01 ms | 29.70 ms | 391.84 ms | **6.21 ms** | 67.66 ms |
| `mod3_n4_r0_s6_unsat.cnf` | UNSAT | 225.35 ms | 156.76 ms | 473.87 ms | **111.98 ms** | 305.35 ms |
| `mod3_n4_r0_s7_sat.cnf` | SAT | 31.06 ms | 16.97 ms | 786.73 ms | **14.06 ms** | 205.66 ms |
| `mod3_n5_r1_s8_unsat.cnf` | UNSAT | **16,281.07 ms** | 22,189.84 ms | T/O ($>30\;\text{s}$) | T/O ($>30\;\text{s}$) | 20,537.45 ms |
| `mod3_n5_r1_s9_sat.cnf` | SAT | **757.62 ms** | 7,290.54 ms | 5,454.97 ms | 7,621.60 ms | 4,832.84 ms |
| **Summary ($T_{\max}=10\;\text{s}$, PAR-2)** | **8 / 9** | **21,065.04 ms** *(fastest)* | 27,511.93 ms *(1.31x slower)* | 27,344.07 ms *(1.30x slower)* | 27,769.17 ms *(1.32x slower)* | 25,456.61 ms *(1.21x slower)* |
| **Summary ($T_{\max}=30\;\text{s}$, PAR-2)** | **9 / 9** | **17,346.11 ms** *(fastest)* | 29,701.77 ms *(1.71x slower)* | 8/9 — 67,344.07 ms *(3.88x slower)* | 8/9 — 67,769.17 ms *(3.91x slower)* | 25,994.07 ms *(1.50x slower)* |

<!-- BEGIN_STRUCTURAL_ANALYSIS -->
## Phase-Transition & Structural Analysis

*Auto-generated by [`../src/analyze_benchmarks.py`](../src/analyze_benchmarks.py). Position relative to the critical phase transition is measured by $\rho_{\mathrm{crit}} = \frac{1}{n}\sum_k m_k / \alpha_c(k)$ (exact $\alpha/\alpha_c(k)$ for pure $k$-SAT; effective critical threshold $\alpha_c^{\mathrm{eff}} = \alpha/\rho_{\mathrm{crit}}$; `Under` $<0.90\times$, `Near-crit` $0.90\text{--}1.10\times$, `Over` $>1.10\times$), alongside Gent–Walsh annealed constrainedness $\kappa = -\frac{1}{n}\sum_i \log_2(1-2^{-k_i})$ (AAAI 1996), clause-length profile ($\bar{k}$, `%Bin`, `%Horn`), variable-degree CV ($\sigma_d/\bar{d}$, uniformity vs. hub skew), and extracted native XOR parity clauses.*

| Instance | Active $n$ | Clauses $m$ | $\alpha=m/n$ | $\alpha_c^{\mathrm{eff}}$ | $\rho_{\mathrm{crit}}$ (Regime) | $\kappa$ | $\bar{k}$ ($k_{\max}$) | Bin% | Horn% | Pos% | Deg CV | XORs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `mod3_n3_r0_s3_sat` | 65 | 435 | 6.69 | 2.00 | **3.34x** (Over) | 1.73 | 2.91 (10) | 38% | 82% | 39% | 0.61 | 0 |
| `mod3_n3_r1_s3_unsat` | 65 | 426 | 6.55 | 2.03 | **3.24x** (Over) | 1.68 | 2.93 (10) | 38% | 86% | 35% | 0.62 | 0 |
| `mod3_n3_r1_s4_sat` | 107 | 903 | 8.44 | 2.22 | **3.79x** (Over) | 1.96 | 3.15 (15) | 35% | 81% | 34% | 0.75 | 0 |
| `mod3_n4_r0_s6_unsat` | 343 | 6,884 | 20.07 | 2.67 | **7.52x** (Over) | 4.03 | 3.39 (36) | 28% | 73% | 33% | 1.09 | 0 |
| `mod3_n4_r0_s7_sat` | 454 | 10,597 | 23.34 | 2.70 | **8.66x** (Over) | 4.57 | 3.46 (45) | 28% | 70% | 32% | 1.18 | 0 |
| `mod3_n4_r2_s5_unsat` | 250 | 4,124 | 16.50 | 2.63 | **6.27x** (Over) | 3.40 | 3.31 (28) | 27% | 79% | 32% | 1.01 | 0 |
| `mod3_n4_r2_s6_sat` | 343 | 6,762 | 19.71 | 2.71 | **7.27x** (Over) | 3.89 | 3.41 (36) | 27% | 75% | 31% | 1.10 | 0 |
| `mod3_n5_r1_s8_unsat` | 825 | 33,493 | 40.60 | 3.22 | **12.6x** (Over) | 7.05 | 3.59 (66) | 21% | 71% | 31% | 1.42 | 0 |
| `mod3_n5_r1_s9_sat` | 1,019 | 46,402 | 45.54 | 3.21 | **14.2x** (Over) | 7.81 | 3.63 (78) | 22% | 69% | 31% | 1.49 | 0 |
| `mod3_n6_r1_le12_open` | 2,309 | 185,679 | 80.42 | 7.28 | **11.0x** (Over) | 8.55 | 4.10 (136) | 3% | 58% | 34% | 2.06 | 0 |
| `mod3_n6_r2_le12_open` | 2,309 | 185,760 | 80.45 | 7.26 | **11.1x** (Over) | 8.57 | 4.09 (136) | 3% | 58% | 34% | 2.06 | 0 |

**Collection Phase-Transition Summary (11 instances, 4 formats: 11 CNF / 11 AIG / 11 XCNF / 11 ANF):** median $\rho_{\mathrm{crit}} = 7.52\times$ (range `3.24x–14.2x`), median $\kappa = 4.03$, regime split **0 Under / 0 Near-critical / 11 Over**, total extracted native XOR parity clauses = **0**, total ANF equations = **987,859**.
<!-- END_STRUCTURAL_ANALYSIS -->
