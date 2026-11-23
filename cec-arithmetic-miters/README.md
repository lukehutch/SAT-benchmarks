# EDA Arithmetic Combinational Equivalence Checking (CEC) Miters (`cec-arithmetic-miters`)

## Overview & Origin

Unsatisfiable hardware verification **Combinational Equivalence Checking (CEC)** miter circuits asserting $\bigvee_k (A_k(x, y) \oplus B_k(x, y)) = 1$ across pairs of functionally identical but structurally distinct arithmetic architectures:
- **32-bit Ripple-Carry vs. Kogge–Stone** logarithmic parallel-prefix adder (`cec_adder_32b_rc_vs_ks`)
- **Array vs. Wallace-tree** multipliers ($6\times 6$, $8\times 8$, $10\times 10$)
- **Wallace-tree vs. Karatsuba** recursive multiplier ($12\times 12$)

- **Origin:** **Original** circuit generator (MIT [`../LICENSE`](../LICENSE)), modeled on industrial EDA multiplier equivalence benchmarks ([HWMCC](https://hwmcc.github.io/); Kaufmann, Biere, & Kauers, [AMulet](https://github.com/d-kaufmann/amulet), FMCAD 2019).
- **Why they are hard:** Multiplier miters between structurally divergent topologies (Array vs. Wallace vs. Karatsuba) have few internal equivalent wires, causing pure CDCL solvers to scale exponentially ($3.6\text{--}8.1\;\text{s}$ at $8\times 8$, exploding rapidly at $10\times 10$ and $12\times 12$).

## Directory Layout & Regeneration

- `*.aig` — Original native **Binary AIGER 1.9** circuits (verified with [Berkeley ABC](https://github.com/berkeley-abc/abc)).
- `cnf-version/` — Tseitin **DIMACS `.cnf`** conversions.
- `xcnf-version/` — Native-XOR **[CryptoMiniSat](https://github.com/msoos/cryptominisat) `.xcnf`** conversions.
- `src/` — Standalone zero-dependency Rust generator crate (`cd src && cargo run --release`).

## Problem Parameters & Data Sizes

| Instance | Circuit A vs. Circuit B | Width | Ans | AIG Inputs | AIG ANDs | AIG Size | CNF Vars | CNF Clauses | CNF Size |
|---|---|---:|:---:|---:|---:|---:|---:|---:|---:|
| `cec_adder_32b_rc_vs_ks` | Ripple-Carry vs. Kogge–Stone Adder | 32b | UNSAT | 64 | 871 | 2.4 KB | 606 | 2,059 | 27.3 KB |
| `cec_mult_6x6_arr_vs_wal` | Array vs. Wallace Multiplier | 6×6 | UNSAT | 12 | 591 | 1.4 KB | 183 | 918 | 13.2 KB |
| `cec_mult_8x8_arr_vs_wal` | Array vs. Wallace Multiplier | 8×8 | UNSAT | 16 | 1,148 | 2.7 KB | 340 | 1,769 | 27.0 KB |
| `cec_array_vs_wallace_10x10` | Array vs. Wallace Multiplier | 10×10 | UNSAT | 20 | 1,868 | 4.3 KB | 530 | 2,850 | 45.0 KB |
| `cec_wallace_vs_karat_12x12` | Wallace vs. Karatsuba Multiplier | 12×12 | UNSAT | 24 | 2,673 | 6.3 KB | 814 | 4,247 | 67.7 KB |

## Benchmark Results (1-Core, Flat DIMACS `.cnf` Input)

Evaluated sequentially on an AMD Ryzen 9 5950X (exact median of 3 runs; $T_{\max} = 5{,}000\;\text{s}$):

| Instance | Frobenius 1C | [Kissat](https://github.com/arminbiere/kissat) 4.0.4 | [CaDiCaL](https://github.com/arminbiere/cadical) 3.1.0 | [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18 (CNF) | [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18 (XCNF) |
|---|---:|---:|---:|---:|---:|
| `cec_adder_32b_rc_vs_ks` | **8.56 ms** | 46.70 ms | 36.21 ms | 146.85 ms | 78.33 ms |
| `cec_mult_6x6_arr_vs_wal` | **1.47 ms** | 213.67 ms | 146.33 ms | 494.59 ms | 285.64 ms |
| `cec_mult_8x8_arr_vs_wal` | **1.66 ms** | 3,598.79 ms | 5,831.30 ms | 8,148.17 ms | 3,300.73 ms |

## References

- P. M. Kogge and H. S. Stone, *A Parallel Algorithm for the Efficient Solution of a General Class of Recurrence Equations*, IEEE Trans. Computers C-22(8):786–793, 1973.
- D. Kaufmann, A. Biere, and M. Kauers, *Verifying Large Multipliers by Combining SAT and Computer Algebra ([AMulet](https://github.com/d-kaufmann/amulet))*, FMCAD 2019.
- A. Mishchenko, S. Chatterjee, R. Jiang, and R. K. Brayton, *FRAIGs: A Unifying Representation for Logic Synthesis and Verification*, ERL Technical Report, UC Berkeley, 2005.
