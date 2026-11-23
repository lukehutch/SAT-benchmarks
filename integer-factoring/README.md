# Pure-Logic Integer Factorization & Masked Multiplier Circuits (`integer-factoring`)

## Overview & Origin

Bit-level combinational multiplier inversion benchmarks asserting $p \cdot q = N$ (with odd-factor LSBs fixed to $1$ and $p \ge q$ / equal-half-bit symmetry breaking) across **Wallace-tree** and **Karatsuba** multiplier topologies, including a 28-bit prime UNSAT instance, 32–40-bit balanced semiprimes, and a 32-bit Wallace multiplier augmented with 16 sparse 4-bit $\mathbb{F}_2$ parity leakage constraints (`masked_mult_32b_xor16`, modeling side-channel / masked hardware cryptanalysis).

- **Origin:** **Original** generator authored in the Frobenius project (`factoring.rs`; MIT [`../LICENSE`](../LICENSE)), motivated by classic bit-blasted factoring SAT benchmarks (Purdom & Sabry 2004; Srebrny 2004) and computer-algebra multiplier verification (Kaufmann, Biere, & Kauers, [AMulet](https://github.com/d-kaufmann/amulet), FMCAD 2019).
- **Why they are hard:** Bit-level carry chains create high-treewidth nonlinear arithmetic constraints; Karatsuba multiplication further couples partial products via extra adders/subtractors.

## Directory Layout & Regeneration

- `*.aig` — Original native **Binary AIGER 1.9** circuits (verified with Berkeley ABC).
- `cnf-version/` — Tseitin **DIMACS `.cnf`** and native-XOR **CryptoMiniSat `.xcnf`** conversions.
- `src/` — Standalone zero-dependency Rust generator crate (`cd src && cargo run --release`).

## Problem Parameters & Data Sizes

| Instance | Target $N$ | Factors $(p, q)$ | Topology | Ans | AIG Inputs | AIG ANDs | AIG Size | CNF Vars | CNF Clauses | CNF Size |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|
| `factor_prime_28b_unsat` | `268,435,399` | prime ($2^{28}-57$) | Wallace | UNSAT | 26 | 2,076 | 4.9 KB | 635 | 3,264 | 51.0 KB |
| `factor_wallace_32b` | `4,292,870,399` | `65519 × 65521` | Wallace | SAT | 30 | 2,732 | 6.4 KB | 825 | 4,286 | 67.6 KB |
| `factor_wallace_36b` | `68,715,282,487` | `262133 × 262139` | Wallace | SAT | 34 | 3,480 | 8.2 KB | 1,041 | 5,451 | 87.0 KB |
| `factor_karatsuba_36b` | `68,715,282,487` | `262133 × 262139` | Karatsuba | SAT | 34 | 3,289 | 7.9 KB | 999 | 5,231 | 83.4 KB |
| `factor_wallace_40b` | `1,006,647,906,441` | `960017 × 1048573` | Wallace | SAT | 38 | 4,296 | 10.1 KB | 1,271 | 6,717 | 111.7 KB |
| `masked_mult_32b_xor16` | `4,292,870,399` | `65519 × 65521` + 16 XOR4 leaks | Wallace + $\mathbb{F}_2$ | SAT | 30 | 2,886 | 6.8 KB | 856 | 4,486 | 70.5 KB |

## Benchmark Results (1-Core, Flat DIMACS `.cnf` Input)

Evaluated sequentially on an AMD Ryzen 9 5950X (exact median of 3 runs; $T_{\max} = 5{,}000\;\text{s}$; all solvers operate strictly on flat `.cnf` with **zero number-theoretic shortcuts**):

| Instance | Frobenius 1C | Kissat 4.0.4 | CaDiCaL 3.1.0 | CryptoMiniSat 5.18 (CNF) | CryptoMiniSat 5.18 (XCNF) |
|---|---:|---:|---:|---:|---:|
| `factor_prime_28b_unsat` | **2.05 ms** | 25.29 ms | 5.99 ms | 75.60 ms | 38.82 ms |
| `factor_wallace_32b` | **2.79 ms** | 25.43 ms | 5.60 ms | 121.22 ms | 82.24 ms |
| `factor_wallace_36b` | **3.11 ms** | 27.58 ms | 8.05 ms | 151.32 ms | 51.40 ms |
| `factor_karatsuba_36b` | **9.56 ms** | 39.72 ms | 39.46 ms | 146.49 ms | 81.61 ms |
| `factor_wallace_40b` | **3.16 ms** | 383.26 ms | 695.57 ms | 774.73 ms | 61.26 ms |
| `masked_mult_32b_xor16` | **2.91 ms** | 17.79 ms | 5.89 ms | 50.11 ms | 72.80 ms |

## References

- D. Kaufmann, A. Biere, and M. Kauers, *Verifying Large Multipliers by Combining SAT and Computer Algebra (AMulet)*, FMCAD 2019.
- C. S. Wallace, *A Suggestion for a Fast Multiplier*, IEEE Trans. Electronic Computers 13(1):14–17, 1964.
- A. Karatsuba and Y. Ofman, *Multiplication of Many-Digital Numbers by Automatic Computers*, Doklady Akad. Nauk SSSR 145:293–294, 1962.
