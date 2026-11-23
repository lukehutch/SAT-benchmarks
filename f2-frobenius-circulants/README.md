# $\mathbb{F}_2$-Frobenius Circulants (`f2-frobenius-circulants`)

## Overview & Origin

Strictly balanced $\mathbb{F}_2$-linear circulant parity circuits on $n = 2^k$ Boolean inputs with stride $s = 2^{\lfloor k/2 \rfloor}$ (4 SAT + 2 UNSAT):

- **Uniquely satisfiable 3-XOR circulants** $\Psi_{k, b}$ ($n \in \{64, 256, 1{,}024, 4{,}096\}$):
  $$x_i \oplus x_{(i+1) \bmod n} \oplus x_{(i+s) \bmod n} = b_i \quad (0 \le i < n),$$
  constructed with a deterministic planted unique solution $x^{\star} \in \mathbb{F}_2^n$ (the circulant polynomial $1 + t + t^s \in \mathbb{F}_2[t]/(t^{2^k} - 1)$ is invertible over $\mathbb{F}_2$ because $(1 + t + t^s)^{2^k} = 1$).
- **Minimally unsatisfiable 4-XOR circulants** (`f2_frobenius_n256_unsat`, `f2_frobenius_n1024_unsat`):
  $$x_i \oplus x_{(i+1) \bmod n} \oplus x_{(i+s) \bmod n} \oplus x_{(i+s+1) \bmod n} = b_i \quad (0 \le i < n),$$
  where $b_i$ matches a planted assignment for $i > 0$ and is flipped at $i = 0$. Every variable appears in exactly 4 equations, so the $\mathbb{F}_2$ sum of all $n$ LHS rows is identically $0$ while $\sum_i b_i = 1 \pmod 2$, yielding a strictly balanced global parity contradiction.

- **Origin:** **Original** suite of algebraic circulant parity benchmark circuits (MIT [`../LICENSE`](../LICENSE)).
- **Why they are hard:** Every merge-tree DNF/ANF circuit solver incurs $\ge 2^{\sqrt{n}/(3\sqrt{2})}$ blowup, and pure CDCL solvers without $\mathbb{F}_2$ parity reasoning scale super-polynomially ($364\;\text{s}$ for [Kissat](https://github.com/arminbiere/kissat) and $211\;\text{s}$ for [CaDiCaL](https://github.com/arminbiere/cadical) at $n = 4{,}096$ SAT; [CaDiCaL](https://github.com/arminbiere/cadical) times out past $30\;\text{s}$ on `n1024_unsat`).

## Directory Layout & Regeneration

- `aig-orig/` — Original native **Binary AIGER 1.9** circuits (`33.7 KB`, `L = 0`, `O = 1` miter where `PO_0 = 1` iff all $n$ parity assertions hold; verified with [Berkeley ABC](https://github.com/berkeley-abc/abc)).
- `cnf-converted/` — Tseitin **DIMACS `.cnf.xz`** conversions (`114.3 KB`).
- `xcnf-converted/` — Native-XOR **[CryptoMiniSat](https://github.com/msoos/cryptominisat) `.xcnf.xz`** conversions (`23.7 KB`).
- `anf-converted/` — Lossless degree-1 linear **DIMACS-ANF `.anf.xz`** conversions (`29.6 KB`, generated via [`../src/to_anf.py`](../src/to_anf.py)).
- `src/` — Standalone zero-dependency Rust generator crate (`cd src && cargo run --release`).

## Problem Parameters & Data Sizes

| Instance | $k$ | $n = 2^k$ | Stride $s$ | Arity | Seed | Ans | AIG ANDs | `.aig.xz` | CNF Vars | CNF Clauses | `.cnf.xz` | `.xcnf.xz` | `.anf.xz` |
|---|---:|---:|---:|---:|---:|:---:|---:|---:|---:|---:|---:|---:|---:|
| `f2_frobenius_n64` | 6 | 64 | 8 | 3-XOR | `12351` | SAT | 447 | 0.6 KB | 128 | 576 | 1.6 KB | 0.5 KB | 0.5 KB |
| `f2_frobenius_n256` | 8 | 256 | 16 | 3-XOR | `12353` | SAT | 1,791 | 1.7 KB | 512 | 2,304 | 4.7 KB | 1.2 KB | 1.4 KB |
| `f2_frobenius_n1024` | 10 | 1,024 | 32 | 3-XOR | `12355` | SAT | 7,167 | 5.3 KB | 2,048 | 9,216 | 15.3 KB | 3.1 KB | 4.3 KB |
| `f2_frobenius_n4096` | 12 | 4,096 | 64 | 3-XOR | `12357` | SAT | 28,671 | 17.6 KB | 8,192 | 36,864 | 58.4 KB | 10.7 KB | 17.4 KB |
| `f2_frobenius_n256_unsat` | 8 | 256 | 16 | 4-XOR | `22353` | UNSAT | 2,559 | 2.0 KB | 768 | 3,328 | 7.7 KB | 1.9 KB | 1.4 KB |
| `f2_frobenius_n1024_unsat` | 10 | 1,024 | 32 | 4-XOR | `22355` | UNSAT | 10,239 | 6.6 KB | 3,072 | 13,312 | 26.6 KB | 6.3 KB | 4.5 KB |

## Benchmark Results (1-Core, Flat DIMACS `.cnf` Input)

Evaluated sequentially on the same AMD Ryzen 9 5950X machine (exact median of 3 runs; $T_{\max} = 5{,}000\;\text{s}$ on SAT instances, $T_{\max} = 30\;\text{s}$ on UNSAT instances; all solvers read the identical flat `.cnf` file, except [CMS-X](https://github.com/msoos/cryptominisat) which receives `xcnf-converted/*.xcnf`):

| Instance | Frobenius 1C | [CaDiCaL](https://github.com/arminbiere/cadical) 3.1.0 | [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18 (CNF) | [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18 (XCNF) | [dense-solver](https://github.com/libdense/dense-solver) 0.0.4 *($T=30\;\text{s}$)* | [Kissat](https://github.com/arminbiere/kissat) 4.0.4 |
|---|---:|---:|---:|---:|---:|---:|
| `f2_frobenius_n64` | **1.22 ms** *(fastest)* | 2.91 ms *(2.4x)* | 23.08 ms *(18.9x)* | 22.23 ms *(18.2x)* | 1.59 ms | 2.68 ms *(2.2x)* |
| `f2_frobenius_n256` | **1.52 ms** *(fastest)* | 388.02 ms *(255x)* | 34.73 ms *(22.8x)* | 27.54 ms *(18.1x)* | 1.96 ms | 156.50 ms *(103x)* |
| `f2_frobenius_n1024` | **3.54 ms** *(fastest)* | 13,775.17 ms *(3,891x)* | 83.44 ms *(23.6x)* | 53.56 ms *(15.1x)* | 5.06 ms | 2,923.48 ms *(826x)* |
| `f2_frobenius_n4096` | **16.10 ms** *(fastest)* | 210,776.92 ms *(13,092x)* | 516.92 ms *(32.1x)* | 999.39 ms *(62.1x)* | 63.48 ms | 364,047.66 ms *(22,612x)* |
| `f2_frobenius_n256_unsat` | **1.76 ms** *(fastest)* | 75.75 ms *(43.0x)* | 36.07 ms *(20.5x)* | 23.03 ms *(13.1x)* | 2.21 ms | 62.87 ms *(35.7x)* |
| `f2_frobenius_n1024_unsat` | **3.49 ms** *(fastest)* | >30 s *(T/O)* | 104.27 ms *(29.9x)* | 30.75 ms *(8.8x)* | 7.51 ms | 928.70 ms *(266x)* |

<!-- BEGIN_STRUCTURAL_ANALYSIS -->
## Phase-Transition & Structural Analysis

*Auto-generated by [`../src/analyze_benchmarks.py`](../src/analyze_benchmarks.py). Position relative to the critical phase transition is measured by $\rho_{\mathrm{crit}} = \frac{1}{n}\sum_k m_k / \alpha_c(k)$ (exact $\alpha/\alpha_c(k)$ for pure $k$-SAT; effective critical threshold $\alpha_c^{\mathrm{eff}} = \alpha/\rho_{\mathrm{crit}}$; `Under` $<0.90\times$, `Near-crit` $0.90\text{--}1.10\times$, `Over` $>1.10\times$), alongside Gent–Walsh annealed constrainedness $\kappa = -\frac{1}{n}\sum_i \log_2(1-2^{-k_i})$ (AAAI 1996), clause-length profile ($\bar{k}$, `%Bin`, `%Horn`), variable-degree CV ($\sigma_d/\bar{d}$, uniformity vs. hub skew), and extracted native XOR parity clauses.*

| Instance | Active $n$ | Clauses $m$ | $\alpha=m/n$ | $\alpha_c^{\mathrm{eff}}$ | $\rho_{\mathrm{crit}}$ (Regime) | $\kappa$ | $\bar{k}$ ($k_{\max}$) | Bin% | Horn% | Pos% | Deg CV | XORs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `f2_frobenius_n1024` | 2,048 | 9,216 | 4.50 | 4.98 | **0.90x** (Near-crit) | 0.87 | 3.67 (4) | 0% | 56% | 50% | 0.45 | 1,024 |
| `f2_frobenius_n1024_unsat` | 3,072 | 13,312 | 4.33 | 4.74 | **0.91x** (Near-crit) | 0.84 | 3.46 (4) | 0% | 46% | 50% | 0.64 | 2,048 |
| `f2_frobenius_n256` | 512 | 2,304 | 4.50 | 4.98 | **0.90x** (Near-crit) | 0.87 | 3.67 (4) | 0% | 56% | 50% | 0.45 | 256 |
| `f2_frobenius_n256_unsat` | 768 | 3,328 | 4.33 | 4.74 | **0.91x** (Near-crit) | 0.84 | 3.46 (4) | 0% | 46% | 50% | 0.64 | 512 |
| `f2_frobenius_n4096` | 8,192 | 36,864 | 4.50 | 4.98 | **0.90x** (Near-crit) | 0.87 | 3.67 (4) | 0% | 56% | 50% | 0.45 | 4,096 |
| `f2_frobenius_n64` | 128 | 576 | 4.50 | 4.98 | **0.90x** (Near-crit) | 0.87 | 3.67 (4) | 0% | 56% | 50% | 0.45 | 64 |

**Collection Phase-Transition Summary (6 instances, 4 formats: 6 CNF / 6 AIG / 6 XCNF / 6 ANF):** median $\rho_{\mathrm{crit}} = 0.90\times$ (range `0.90x–0.91x`), median $\kappa = 0.87$, regime split **0 Under / 6 Near-critical / 0 Over**, total extracted native XOR parity clauses = **8,000**, total ANF equations = **6,720**.
<!-- END_STRUCTURAL_ANALYSIS -->

## References

- A. Biere, T. Faller, K. Fazekas, M. Fleury, N. Froleyks, and F. Pollitt, *[CaDiCaL](https://github.com/arminbiere/cadical) 2.0 / [Kissat](https://github.com/arminbiere/kissat) 4.0*, CAV 2024.
- M. Soos, K. Nohl, and C. Castelluccia, *Extending SAT Solvers to Cryptographic Problems ([CryptoMiniSat](https://github.com/msoos/cryptominisat))*, SAT 2009.
- A. Biere, *The AIGER And-Inverter Graph (AIG) Format Version 20071012*, FMV Technical Report 07/1, JKU Linz, 2007.
