# Hard SPN / LowMC-Style Linear-Form + Nonlinear Circuits (`hard-spn`)

## Overview & Origin

Substitution–Permutation Network (SPN) / LowMC-style algebraic cryptanalysis benchmarks pairing a dense $\mathbb{F}_2$ linear diffusion layer ($r = n/2$ sparse 5-input parity assertions) with nonlinear $\mathrm{And}$, $\mathrm{Maj}_3$, and $\mathrm{Mux}$ S-box gates evaluated on **3-input $\mathbb{F}_2$ linear forms** $\ell_a = x_i \oplus x_j \oplus x_k$ rather than raw input wires. Both satisfiable planted instances ($n \in \{64, 96, 128\}$) and a deep unsatisfiable flipped-target instance (`spn_unsat_n48_d24`) are included.

- **Origin:** **Original** benchmark suite (MIT [`../LICENSE`](../LICENSE)), modeled on algebraic LowMC-style ciphers (Albrecht et al., [EUROCRYPT 2015](https://eprint.iacr.org/2016/687)).
- **Why they are hard:** Feeding 3-input linear forms into nonlinear gates couples the affine diffusion layer with nonlinear S-box constraints, making flat clausal propagation challenging: at $n = 128$, Kissat 4.0.4 takes `4,330 ms`, CaDiCaL 3.1.0 takes `2,137 ms`, and CryptoMiniSat CNF takes `10,805 ms`.

## Directory Layout & Regeneration

- `*.aig` — Original native **Binary AIGER 1.9** circuits (verified with Berkeley ABC).
- `cnf-version/` — Tseitin **DIMACS `.cnf`** conversions.
- `xcnf-version/` — Native-XOR **CryptoMiniSat `.xcnf`** conversions.
- `src/` — Standalone zero-dependency Rust generator crate (`cd src && cargo run --release`).

## Problem Parameters & Data Sizes

| Instance | Inputs $n$ | Linear Eqs $r$ | Nullspace $d$ | Nonlinear S-box Gates | Seed | Ans | AIG ANDs | AIG Size | CNF Vars | CNF Clauses | CNF Size |
|---|---:|---:|---:|---:|---:|:---:|---:|---:|---:|---:|---:|
| `spn_unsat_n48_d24` | 48 | 24 | 24 | 38 (last flipped) | `0x777788889999AAAA` | UNSAT | 969 | 2.5 KB | 247 | 1,363 | 20.1 KB |
| `spn_sat_n64_d32` | 64 | 32 | 32 | 55 | `0x13572468ABCD0064` | SAT | 1,395 | 3.6 KB | 350 | 1,984 | 30.1 KB |
| `spn_sat_n96_d48` | 96 | 48 | 48 | 85 | `0x13572468ABCD0096` | SAT | 2,205 | 5.6 KB | 539 | 3,060 | 47.1 KB |
| `spn_sat_n128_d64` | 128 | 64 | 64 | 150 | `0x13572468ABCD7981` | SAT | 3,643 | 9.4 KB | 856 | 5,104 | 81.2 KB |

## Benchmark Results (1-Core, Flat DIMACS `.cnf` Input)

Evaluated sequentially on an AMD Ryzen 9 5950X (exact median of 3 runs; $T_{\max} = 5{,}000\;\text{s}$):

| Instance | Frobenius 1C | Kissat 4.0.4 | CaDiCaL 3.1.0 | CryptoMiniSat 5.18 (CNF) | CryptoMiniSat 5.18 (XCNF) |
|---|---:|---:|---:|---:|---:|
| `spn_unsat_n48_d24` | **2.35 ms** | 32.47 ms | 22.35 ms | 58.31 ms | 27.06 ms |
| `spn_sat_n64_d32` | **2.18 ms** | 84.09 ms | 30.83 ms | 77.31 ms | 27.36 ms |
| `spn_sat_n96_d48` | **6.68 ms** | 326.02 ms | 176.70 ms | 247.54 ms | 105.45 ms |
| `spn_sat_n128_d64` | **38.08 ms** | 4,329.94 ms | 2,136.73 ms | 10,804.67 ms | 1,850.59 ms |

## References

- M. R. Albrecht, C. Rechberger, T. Schneider, T. Tiessen, and M. Zohner, *Ciphers for MPC and FHE (LowMC)*, EUROCRYPT 2015, LNCS 9056.
- M. Soos, K. Nohl, and C. Castelluccia, *Extending SAT Solvers to Cryptographic Problems*, SAT 2009.
