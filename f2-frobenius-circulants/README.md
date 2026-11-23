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
- **Why they are hard:** Every merge-tree DNF/ANF circuit solver incurs $\ge 2^{\sqrt{n}/(3\sqrt{2})}$ blowup, and pure CDCL solvers without $\mathbb{F}_2$ parity reasoning scale super-polynomially ($364\;\text{s}$ for Kissat and $211\;\text{s}$ for CaDiCaL at $n = 4{,}096$ SAT; CaDiCaL times out past $30\;\text{s}$ on `n1024_unsat`).

## Directory Layout & Regeneration

- `*.aig` — Original native **Binary AIGER 1.9** circuits (`L = 0`, `O = 1` miter where `PO_0 = 1` iff all $n$ parity assertions hold; verified with Berkeley ABC).
- `cnf-version/` — Tseitin **DIMACS `.cnf`** and native-XOR **CryptoMiniSat `.xcnf`** conversions.
- `src/` — Standalone zero-dependency Rust generator crate (`cd src && cargo run --release`).

## Problem Parameters & Data Sizes

| Instance | $k$ | $n = 2^k$ | Stride $s$ | Arity | Seed | Ans | AIG Inputs | AIG ANDs | AIG Size | CNF Vars | CNF Clauses | CNF Size |
|---|---:|---:|---:|---:|---:|:---:|---:|---:|---:|---:|---:|---:|
| `f2_frobenius_n64` | 6 | 64 | 8 | 3-XOR | `12351` | SAT | 64 | 447 | 1.2 KB | 128 | 576 | 8.4 KB |
| `f2_frobenius_n256` | 8 | 256 | 16 | 3-XOR | `12353` | SAT | 256 | 1,791 | 4.8 KB | 512 | 2,304 | 39.1 KB |
| `f2_frobenius_n1024` | 10 | 1,024 | 32 | 3-XOR | `12355` | SAT | 1,024 | 7,167 | 19.1 KB | 2,048 | 9,216 | 173.5 KB |
| `f2_frobenius_n4096` | 12 | 4,096 | 64 | 3-XOR | `12357` | SAT | 4,096 | 28,671 | 88.9 KB | 8,192 | 36,864 | 772.1 KB |
| `f2_frobenius_n256_unsat` | 8 | 256 | 16 | 4-XOR | `22353` | UNSAT | 256 | 2,559 | 6.8 KB | 768 | 3,328 | 54.4 KB |
| `f2_frobenius_n1024_unsat` | 10 | 1,024 | 32 | 4-XOR | `22355` | UNSAT | 1,024 | 10,239 | 28.4 KB | 3,072 | 13,312 | 243.4 KB |

## Benchmark Results (1-Core, Flat DIMACS `.cnf` Input)

Evaluated sequentially on the same AMD Ryzen 9 5950X machine (exact median of 3 runs; $T_{\max} = 5{,}000\;\text{s}$ on SAT instances, $T_{\max} = 30\;\text{s}$ on UNSAT instances; all solvers read the identical flat `.cnf` file, except CMS-X which receives `cnf-version/*.xcnf`):

| Instance | Frobenius 1C | Kissat 4.0.4 | CaDiCaL 3.1.0 | CryptoMiniSat 5.18 (CNF) | CryptoMiniSat 5.18 (XCNF) |
|---|---:|---:|---:|---:|---:|
| `f2_frobenius_n64` | **1.22 ms** *(fastest)* | 2.68 ms *(2.2x)* | 2.91 ms *(2.4x)* | 23.08 ms *(18.9x)* | 22.23 ms *(18.2x)* |
| `f2_frobenius_n256` | **1.52 ms** *(fastest)* | 156.50 ms *(103x)* | 388.02 ms *(255x)* | 34.73 ms *(22.8x)* | 27.54 ms *(18.1x)* |
| `f2_frobenius_n1024` | **3.54 ms** *(fastest)* | 2,923.48 ms *(826x)* | 13,775.17 ms *(3,891x)* | 83.44 ms *(23.6x)* | 53.56 ms *(15.1x)* |
| `f2_frobenius_n4096` | **16.10 ms** *(fastest)* | 364,047.66 ms *(22,612x)* | 210,776.92 ms *(13,092x)* | 516.92 ms *(32.1x)* | 999.39 ms *(62.1x)* |
| `f2_frobenius_n256_unsat` | **1.76 ms** *(fastest)* | 62.87 ms *(35.7x)* | 75.75 ms *(43.0x)* | 36.07 ms *(20.5x)* | 23.03 ms *(13.1x)* |
| `f2_frobenius_n1024_unsat` | **3.49 ms** *(fastest)* | 928.70 ms *(266x)* | >30 s *(T/O)* | 104.27 ms *(29.9x)* | 30.75 ms *(8.8x)* |

## References

- A. Biere, T. Faller, K. Fazekas, M. Fleury, N. Froleyks, and F. Pollitt, *CaDiCaL 2.0 / Kissat 4.0*, CAV 2024.
- M. Soos, K. Nohl, and C. Castelluccia, *Extending SAT Solvers to Cryptographic Problems (CryptoMiniSat)*, SAT 2009.
- A. Biere, *The AIGER And-Inverter Graph (AIG) Format Version 20071012*, FMV Technical Report 07/1, JKU Linz, 2007.
