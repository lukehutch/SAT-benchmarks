# $\mathbb{F}_2$-Frobenius Circulants (`f2-frobenius-circulants`)

## Overview & Origin

Uniquely satisfiable, strictly balanced $\mathbb{F}_2$-linear circulant parity circuits $\Psi_{k, b}$ on $n = 2^k$ Boolean inputs with stride $s = 2^{\lfloor k/2 \rfloor}$:

$$x_i \oplus x_{(i+1) \bmod n} \oplus x_{(i+s) \bmod n} = b_i \quad (0 \le i < n),$$

constructed with a deterministic planted unique solution $x^{\star} \in \mathbb{F}_2^n$ (the circulant polynomial $1 + t + t^s \in \mathbb{F}_2[t]/(t^{2^k} - 1)$ is invertible over $\mathbb{F}_2$ because $(1 + t + t^s)^{2^k} = 1 + t^{2^k} + t^{s\cdot 2^k} = 1$).

- **Origin:** Developed as Stage 1 algebraic inversion counterexamples in the Frobenius project (`counterexamples.rs`).
- **Why they are hard:** Every merge-tree DNF/ANF circuit solver incurs $\ge 2^{\sqrt{n}/(3\sqrt{2})}$ blowup, and pure CDCL without $\mathbb{F}_2$ Gaussian elimination scales super-polynomially ($364\;\text{s}$ for Kissat and $211\;\text{s}$ for CaDiCaL at $n = 4{,}096$), whereas M4RI / Gaussian elimination over $\mathbb{F}_2$ solves them in milliseconds.

## Directory Layout & Regeneration

- `*.aig` — Original native **Binary AIGER 1.9** circuits (`L = 0`, `O = 1` miter where `PO_0 = 1` iff all $n$ parity assertions hold; verified with Berkeley ABC).
- `cnf-version/` — Tseitin **DIMACS `.cnf`** and native-XOR **CryptoMiniSat `.xcnf`** conversions.
- `src/` — Standalone zero-dependency Rust generator crate. To regenerate all `.aig`, `.cnf`, and `.xcnf` files:
  ```bash
  cd src && cargo run --release
  ```

## Problem Parameters & Data Sizes

| Instance | $k$ | $n = 2^k$ | Stride $s$ | Seed | Ans | AIG Inputs | AIG ANDs | AIG Size | CNF Vars | CNF Clauses | CNF Size |
|---|---:|---:|---:|---:|:---:|---:|---:|---:|---:|---:|---:|
| `f2_frobenius_n64` | 6 | 64 | 8 | `12351` | SAT | 64 | 447 | 1.2 KB | 128 | 576 | 8.4 KB |
| `f2_frobenius_n256` | 8 | 256 | 16 | `12353` | SAT | 256 | 1,791 | 4.8 KB | 512 | 2,304 | 39.1 KB |
| `f2_frobenius_n1024` | 10 | 1,024 | 32 | `12355` | SAT | 1,024 | 7,167 | 19.1 KB | 2,048 | 9,216 | 173.5 KB |
| `f2_frobenius_n4096` | 12 | 4,096 | 64 | `12357` | SAT | 4,096 | 28,671 | 88.9 KB | 8,192 | 36,864 | 772.1 KB |

## Benchmark Results (1-Core, Flat DIMACS `.cnf` Input)

Evaluated sequentially on an AMD Ryzen 9 5950X (exact median of 3 runs; $T_{\max} = 5{,}000\;\text{s}$; all solvers read the identical flat `.cnf` file, except CMS-X which receives `cnf-version/*.xcnf`):

| Instance | Frobenius 1C PGO | Kissat 4.0.4 | CaDiCaL 3.1.0 | CryptoMiniSat 5.18 (CNF) | CryptoMiniSat 5.18 (XCNF) |
|---|---:|---:|---:|---:|---:|
| `f2_frobenius_n64` | **1.22 ms** | 2.68 ms | 2.91 ms | 23.08 ms | 22.23 ms |
| `f2_frobenius_n256` | **1.52 ms** | 156.50 ms | 388.02 ms | 34.73 ms | 27.54 ms |
| `f2_frobenius_n1024` | **3.54 ms** | 2,923.48 ms | 13,775.17 ms | 83.44 ms | 53.56 ms |
| `f2_frobenius_n4096` | **16.10 ms** | 364,047.66 ms | 210,776.92 ms | 516.92 ms | 999.39 ms |

## References

- M. Albrecht, G. Bard, and W. Hart, *Algorithm 898: Efficient Multiplication of Dense Matrices over GF(2) (M4RI)*, ACM TOMS 37(1), 2010.
- A. Biere, T. Faller, K. Fazekas, M. Fleury, N. Froleyks, and F. Pollitt, *CaDiCaL 2.0 / Kissat 4.0*, CAV 2024.
- M. Soos, K. Nohl, and C. Castelluccia, *Extending SAT Solvers to Cryptographic Problems (CryptoMiniSat)*, SAT 2009.
- A. Biere, *The AIGER And-Inverter Graph (AIG) Format Version 20071012*, FMV Technical Report 07/1, JKU Linz, 2007.
