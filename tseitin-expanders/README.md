# $\mathrm{MOD}_2$-Tseitin Expanders & Prisms (`tseitin-expanders`)

## Overview & Origin

Unsatisfiable Tseitin parity formulas over deterministic 3-regular expander graphs ($n \in \{60, 120, 300\}$ vertices; Hamiltonian cycle plus pseudorandom perfect matching) and the 3-regular prism graph $C_{200} \times K_2$ ($n = 400$ vertices), assigning total odd vertex charge ($c_0 = 1$, $c_v = 0$ for $v > 0$).

- **Origin:** **Original** circuit-native AIG generator (MIT [`../LICENSE`](../LICENSE)), instantiating the classic Resolution proof-complexity lower-bound family introduced by Tseitin (1968) and Urquhart ([JACM 1987](https://doi.org/10.1145/7531.8928)).
- **Why they are hard:** Every pure Resolution / CDCL refutation of a Tseitin formula on a 3-regular expander requires $2^{\Omega(n)}$ steps (Urquhart, JACM 1987). Both Kissat 4.0.4 and CaDiCaL 3.1.0 time out past $5{,}000\;\text{s}$ starting at $n = 120$.

## Directory Layout & Regeneration

- `*.aig` — Original native **Binary AIGER 1.9** circuits (verified with Berkeley ABC).
- `cnf-version/` — Tseitin **DIMACS `.cnf`** and native-XOR **CryptoMiniSat `.xcnf`** conversions.
- `src/` — Standalone zero-dependency Rust generator crate (`cd src && cargo run --release`).

## Problem Parameters & Data Sizes

| Instance | Graph Family | Vertices $n$ | Edges $m$ | Seed | Ans | AIG Inputs | AIG ANDs | AIG Size | CNF Vars | CNF Clauses | CNF Size |
|---|---|---:|---:|---:|:---:|---:|---:|---:|---:|---:|---:|
| `tseitin_exp_n60` | 3-reg expander | 60 | 90 | `777` | UNSAT | 90 | 419 | 1.2 KB | 150 | 540 | 8.2 KB |
| `tseitin_exp_n120` | 3-reg expander | 120 | 180 | `778` | UNSAT | 180 | 839 | 2.3 KB | 300 | 1,080 | 17.9 KB |
| `tseitin_exp_n300` | 3-reg expander | 300 | 450 | `779` | UNSAT | 450 | 2,099 | 5.6 KB | 750 | 2,700 | 47.3 KB |
| `tseitin_prism_n400` | Prism $C_{200} \times K_2$ | 400 | 600 | — | UNSAT | 600 | 2,799 | 7.4 KB | 1,000 | 3,600 | 63.6 KB |

## Benchmark Results (1-Core, Flat DIMACS `.cnf` Input)

Evaluated sequentially on an AMD Ryzen 9 5950X (exact median of 3 runs; $T_{\max} = 5{,}000\;\text{s}$; all solvers read the identical flat `.cnf` file, except CMS-X which receives `cnf-version/*.xcnf`):

| Instance | Frobenius 1C | Kissat 4.0.4 | CaDiCaL 3.1.0 | CryptoMiniSat 5.18 (CNF) | CryptoMiniSat 5.18 (XCNF) |
|---|---:|---:|---:|---:|---:|
| `tseitin_exp_n60` | **1.19 ms** | 58.59 ms | 546.39 ms | 22.59 ms | 22.91 ms |
| `tseitin_exp_n120` | **1.25 ms** | >5,000 s (T/O) | >5,000 s (T/O) | 27.62 ms | 23.45 ms |
| `tseitin_exp_n300` | **1.36 ms** | >5,000 s (T/O) | >5,000 s (T/O) | 29.10 ms | 23.68 ms |
| `tseitin_prism_n400` | **1.66 ms** | 13.60 ms | 9.56 ms | 27.82 ms | 23.21 ms |

*(All three expander proofs emitted by Frobenius in LRAT format additionally pass formal verification in HOL4/CakeML `cake_lpr` and `lrat-check`.)*

## References

- G. S. Tseitin, *On the Complexity of Derivation in Propositional Calculus*, Studies in Constructive Mathematics and Mathematical Logic, 1968.
- A. Urquhart, *Hard Examples for Resolution*, Journal of the ACM 34(1):209–219, 1987.
- T. Philipp and A. Rebola-Pardo, *DRAT Proofs for XOR Reasoning*, JELIA 2016, LNCS 10021.
- Y. K. Tan, M. J. H. Heule, and M. O. Myreen, *cake\_lpr: Verified Propagation Redundancy Checking in CakeML*, TACAS 2021.
