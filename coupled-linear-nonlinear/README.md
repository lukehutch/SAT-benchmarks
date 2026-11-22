# Coupled Linear + Nonlinear Circuits (`coupled-linear-nonlinear`)

## Overview & Origin

Satisfiable hybrid algebraic–Boolean benchmark circuits coupling an under-determined system of sparse 5-variable $\mathbb{F}_2$ linear parity constraints ($\mathrm{rank} = r$, nullspace dimension $d = n - r$) with a layer of nonlinear Boolean gates ($\mathrm{Maj}_3$, $\mathrm{And}$, $\mathrm{Mux}$) directly over primary inputs, consistent with a planted secret assignment $x^{\star} \in \mathbb{F}_2^n$.

- **Origin:** Developed in the Frobenius project (`main.rs::build_coupled_or_spn_aig`, `spn_forms = false`) to benchmark simultaneous $\mathbb{F}_2$-nullspace contraction and nonlinear Boolean constraint satisfaction.
- **Why they are interesting:** Pure linear algebra cannot handle the nonlinear $\mathrm{Maj}_3/\mathrm{And}/\mathrm{Mux}$ layer, while pure CDCL does not contract the $r$-equation affine subspace upfront. Fused nullspace-conditioned search solves all three circuits in $1.8\text{--}2.7\;\text{ms}$ on flat CNFs.

## Directory Layout & Regeneration

- `*.aig` — Original native **Binary AIGER 1.9** circuits (verified with Berkeley ABC).
- `cnf-version/` — Tseitin **DIMACS `.cnf`** and native-XOR **CryptoMiniSat `.xcnf`** conversions.
- `src/` — Standalone zero-dependency Rust generator crate (`cd src && cargo run --release`).

## Problem Parameters & Data Sizes

| Instance | Inputs $n$ | Linear Eqs $r$ | Nullspace $d$ | Nonlinear Gates | Seed | Ans | AIG ANDs | AIG Size | CNF Vars | CNF Clauses | CNF Size |
|---|---:|---:|---:|---:|---:|:---:|---:|---:|---:|---:|---:|
| `coupled_n128_d64` | 128 | 64 | 64 | 96 | `0xFEEDFACE115122A2` | SAT | 1,161 | 3.1 KB | 411 | 1,640 | 22.9 KB |
| `coupled_n256_d128` | 256 | 128 | 128 | 180 | `0xFEEDFACE11912322` | SAT | 2,292 | 6.3 KB | 809 | 3,222 | 47.6 KB |
| `coupled_n512_d128` | 512 | 384 | 128 | 420 | `0xFEEDFACE10912022` | SAT | 6,489 | 18.1 KB | 2,074 | 9,001 | 146.1 KB |

## Benchmark Results (1-Core, Flat DIMACS `.cnf` Input)

Evaluated sequentially on an AMD Ryzen 9 5950X (exact median of 3 runs; $T_{\max} = 5{,}000\;\text{s}$):

| Instance | Frobenius 1C PGO | Kissat 4.0.4 | CaDiCaL 3.1.0 | CryptoMiniSat 5.18 (CNF) | CryptoMiniSat 5.18 (XCNF) |
|---|---:|---:|---:|---:|---:|
| `coupled_n128_d64` | **1.82 ms** | 1.99 ms | 2.83 ms | 22.02 ms | 21.39 ms |
| `coupled_n256_d128` | **2.27 ms** | 3.98 ms | 3.74 ms | 56.09 ms | 23.62 ms |
| `coupled_n512_d128` | **2.65 ms** | 3.63 ms | 5.51 ms | 7.24 ms | 5.65 ms |

## References

- A. Biere et al., *CaDiCaL 2.0 / Kissat 4.0*, CAV 2024.
- M. Soos, K. Nohl, and C. Castelluccia, *Extending SAT Solvers to Cryptographic Problems*, SAT 2009.
