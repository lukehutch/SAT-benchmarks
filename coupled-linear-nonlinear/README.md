# Coupled Linear + Nonlinear Circuits (`coupled-linear-nonlinear`)

## Overview & Origin

Hybrid algebraic–Boolean benchmark circuits (3 SAT + 1 UNSAT) coupling an under-determined system of sparse 5-variable $\mathbb{F}_2$ linear parity constraints ($\mathrm{rank} = r$, nullspace dimension $d = n - r$) with a layer of nonlinear Boolean gates ($\mathrm{Maj}_3$, $\mathrm{And}$, $\mathrm{Mux}$) directly over primary inputs. The three SAT instances are consistent with a planted secret assignment $x^{\star} \in \mathbb{F}_2^n$; the UNSAT instance (`coupled_n128_d32_unsat`) flips the final nonlinear gate polarity so both the linear layer ($d = 32$) and nonlinear gates are individually consistent while their coupled intersection is unsatisfiable.

- **Origin:** **Original** benchmark suite (MIT [`../LICENSE`](../LICENSE)) coupling $\mathbb{F}_2$-linear parity constraints with nonlinear Boolean gates ($\mathrm{Maj}_3$, $\mathrm{And}$, $\mathrm{Mux}$).
- **Why they are interesting:** Pure linear algebra cannot handle the nonlinear $\mathrm{Maj}_3/\mathrm{And}/\mathrm{Mux}$ layer, while standard CDCL solvers must jointly satisfy both the $r$-equation parity layer and the nonlinear gate constraints.

## Directory Layout & Regeneration

- `*.aig` — Original native **Binary AIGER 1.9** circuits (verified with [Berkeley ABC](https://github.com/berkeley-abc/abc)).
- `cnf-version/` — Tseitin **DIMACS `.cnf`** conversions.
- `xcnf-version/` — Native-XOR **[CryptoMiniSat](https://github.com/msoos/cryptominisat) `.xcnf`** conversions.
- `src/` — Standalone zero-dependency Rust generator crate (`cd src && cargo run --release`).

## Problem Parameters & Data Sizes

| Instance | Inputs $n$ | Linear Eqs $r$ | Nullspace $d$ | Nonlinear Gates | Seed | Ans | AIG ANDs | AIG Size | CNF Vars | CNF Clauses | CNF Size |
|---|---:|---:|---:|---:|---:|:---:|---:|---:|---:|---:|---:|
| `coupled_n128_d64` | 128 | 64 | 64 | 96 | `0xFEEDFACE115122A2` | SAT | 1,161 | 3.1 KB | 411 | 1,640 | 22.9 KB |
| `coupled_n128_d32_unsat` | 128 | 96 | 32 | 84 (last flipped) | `0xCAFEBABE0003` | UNSAT | 1,514 | 4.0 KB | 488 | 2,036 | 30.0 KB |
| `coupled_n256_d128` | 256 | 128 | 128 | 180 | `0xFEEDFACE11912322` | SAT | 2,292 | 6.3 KB | 809 | 3,222 | 47.6 KB |
| `coupled_n512_d128` | 512 | 384 | 128 | 420 | `0xFEEDFACE10912022` | SAT | 6,489 | 18.1 KB | 2,074 | 9,001 | 146.1 KB |

## Benchmark Results (1-Core, Flat DIMACS `.cnf` Input)

Evaluated sequentially on the same AMD Ryzen 9 5950X machine (exact median of 3 runs; $T_{\max} = 5{,}000\;\text{s}$ on SAT instances, $T_{\max} = 30\;\text{s}$ on `coupled_n128_d32_unsat`):

| Instance | Frobenius 1C | [Kissat](https://github.com/arminbiere/kissat) 4.0.4 | [CaDiCaL](https://github.com/arminbiere/cadical) 3.1.0 | [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18 (CNF) | [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18 (XCNF) |
|---|---:|---:|---:|---:|---:|
| `coupled_n128_d64` | **1.82 ms** *(fastest)* | 1.99 ms *(1.1x)* | 2.83 ms *(1.6x)* | 22.02 ms *(12.1x)* | 21.39 ms *(11.8x)* |
| `coupled_n128_d32_unsat` | **2.02 ms** *(fastest)* | 14.75 ms *(7.3x)* | 2.63 ms *(1.3x)* | 71.15 ms *(35.2x)* | 24.73 ms *(12.2x)* |
| `coupled_n256_d128` | **2.27 ms** *(fastest)* | 3.98 ms *(1.8x)* | 3.74 ms *(1.6x)* | 56.09 ms *(24.7x)* | 23.62 ms *(10.4x)* |
| `coupled_n512_d128` | **2.65 ms** *(fastest)* | 3.63 ms *(1.4x)* | 5.51 ms *(2.1x)* | 7.24 ms *(2.7x)* | 5.65 ms *(2.1x)* |

## References

- A. Biere et al., *[CaDiCaL](https://github.com/arminbiere/cadical) 2.0 / [Kissat](https://github.com/arminbiere/kissat) 4.0*, CAV 2024.
- M. Soos, K. Nohl, and C. Castelluccia, *Extending SAT Solvers to Cryptographic Problems*, SAT 2009.
