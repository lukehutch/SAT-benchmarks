# Quantum Error-Correcting LDPC Code Distance SAT Benchmarks (`QDistSAT` / Bivariate-Bicycle Codes)

## Provenance & Credit

- **Recommended by:** [`@TravisRudd`](https://twitter.com/TravisRudd) (Twitter/X)
- **Upstream Benchmark Suite & Matrices:** [`guluchen/QDistSAT`](https://github.com/guluchen/QDistSAT) & [`guluchen/DistQLDPC`](https://github.com/guluchen/DistQLDPC) (Yu-Fang Chen and contributors)
- **License & Attribution:** **GNU General Public License v3.0 or later (`GPL-3.0-or-later`)** — see [`LICENSE`](LICENSE), [`NOTICE`](NOTICE), and [`DATA-TIERS.md`](DATA-TIERS.md) (copied verbatim from `guluchen/QDistSAT`, retaining all upstream matrix notices).
- **Quantum LDPC Code Literature Cited ([`@TravisRudd`](https://twitter.com/TravisRudd) notes & `NOTICE`):**
  - S. Bravyi, A. W. Cross, J. M. Gambetta, D. Maslov, P. Rall, and T. J. Yoder, *"High-threshold and low-overhead fault-tolerant quantum memory"*, Nature 627, pp. 778–782 (2024), [`arXiv:2308.07915`](https://arxiv.org/abs/2308.07915) — source of the `[[144, 12, 12]]` "gross" bivariate-bicycle code (`BB_144_12_12`) and the `[[756, 16, 34]]` code (`BB_756_16_34`).
  - M. Wang and F. Mueller, *"Coprime Bivariate Bicycle Codes and their Properties"*, [`arXiv:2408.10001`](https://arxiv.org/abs/2408.10001) — related bivariate-bicycle family (including `[[784, 24, 24]]` codes).
  - Z. Liang, K. Liu, H. Song, and Y.-A. Chen, *"Generalized toric codes on twisted tori for quantum error correction"*, PRX Quantum 6, 020357 (2025), [`arXiv:2503.03827`](https://arxiv.org/abs/2503.03827) — source of `BB_30_4_6`.
  - *"Large-Language-Model Discovery of Quantum LDPC Codes through Structured Concept Evolution (SCE)"*, [`arXiv:2606.24808`](https://arxiv.org/abs/2606.24808) — related `[[1496, ...]]` lifted-product codes.
  - Full tiering of all 80 QDistSAT/DistQLDPC codes (`tier0`–`tier5`) is documented in [`DATA-TIERS.md`](DATA-TIERS.md).

## Problem Description

Given a CSS quantum LDPC code defined by binary parity-check matrices $H_X, H_Z$ over $\mathbb{F}_2$ ($H_X H_Z^T = 0$) and logical operator bases $G_X \subseteq \ker(H_X)$, $G_Z \subseteq \ker(H_Z)$, certifying minimum $Z$-distance $d_Z$ asks for a binary vector $z \in \mathbb{F}_2^n$ such that:
1. $H_X z = 0 \pmod 2$ (commutes with all $X$-stabilizers),
2. $G_Z z \neq 0 \pmod 2$ (non-trivial logical operator: $z \notin \mathrm{row}(H_Z)$, since $\ker(H_Z) = \mathrm{row}(H_X) \oplus \mathrm{row}(G_Z)$), and
3. $\mathrm{wt}(z) = \sum_{j=1}^n z_j \le w$ (encoded via a Sinz 2005 sequential counter).

The formula is **SAT** iff $d_Z \le w$ and **UNSAT** iff $d_Z > w$. These coupled sparse $\mathbb{F}_2$-linear + low-Hamming-weight cardinality instances are notorious stress tests for both CDCL and XOR-aware SAT solvers.

## Corpus & Data Sizes

Includes the exact upstream CSS parity-check and logical-basis matrices (`matrices/`, 20 files covering 5 canonical Bivariate-Bicycle codes), **10 paired boundary decision CNFs** ($w = d-1$ UNSAT and $w = d$ SAT), **10 native-XOR `.xcnf` files** in `xcnf-version/`, **10 exact Binary AIGER 1.9 conversions** in `aig-version/` (all 10/10 verified via [Berkeley ABC](https://github.com/berkeley-abc/abc) `read_aiger`), and the standalone exporter `src/export_qdist_cnf.py`:

| Code Stem | Parameters $[[n,k,d]]$ | Weight $w$ | Status | Vars | Clauses | AIG AND Gates |
|---|---|---:|:---:|---:|---:|---:|
| `BB_30_4_6` | `[[30, 4, 6]]` | 5 / 6 | UNSAT / SAT | 254 / 283 | 691 / 748 | 1,855 / 1,996 |
| `BB_72_12_6` | `[[72, 12, 6]]` | 5 / 6 | UNSAT / SAT | 623 / 694 | 1,705 / 1,846 | 4,623 / 4,974 |
| `BB_144_12_12` ("gross") | `[[144, 12, 12]]` | 11 / 12 | UNSAT / SAT | 2,077 / 2,220 | 5,007 / 5,292 | 13,161 / 13,872 |
| `BB_360_12_24` | `[[360, 12, 24]]` | 23 / 24 | UNSAT / SAT | 9,731 / 10,090 | 22,027 / 22,744 | 57,093 / 58,884 |
| `BB_756_16_34` | `[[756, 16, 34]]` | 33 / 34 | UNSAT / SAT | 29,581 / 30,336 | 67,705 / 69,214 | 176,671 / 180,442 |

## Comparative 1-Core Benchmark Results (`BB_30`, `BB_72`, `BB_144`, $T_{\max} = 10\;\text{s}$)

- **Hardware & Protocol:** Same machine (AMD Ryzen 9 5950X, Linux, 1 core per run, $T_{\max} = 10\;\text{s}$, identical flat `.cnf` input for CNF solvers plus `xcnf-version/*.xcnf` for [CryptoMiniSat](https://github.com/msoos/cryptominisat) XCNF, 0 disagreements).

| Instance | Verdict | Frobenius 1C | [Kissat](https://github.com/arminbiere/kissat) 4.0.4 | [CaDiCaL](https://github.com/arminbiere/cadical) 3.1.0 | [CMS](https://github.com/msoos/cryptominisat) 5.18 (CNF) | [CMS](https://github.com/msoos/cryptominisat) 5.18 (XCNF) |
|---|---:|---:|---:|---:|---:|---:|
| `BB_30_4_6_w5_unsat.cnf` | UNSAT | 585.09 ms | 14.89 ms | **12.67 ms** | 38.69 ms | 34.51 ms |
| `BB_30_4_6_w6_sat.cnf` | SAT | 6.97 ms | 6.34 ms | **2.03 ms** | 30.53 ms | 25.60 ms |
| `BB_72_12_6_w5_unsat.cnf` | UNSAT | 87.66 ms | 56.43 ms | **50.94 ms** | 104.06 ms | 90.29 ms |
| `BB_72_12_6_w6_sat.cnf` | SAT | 1.83 ms | **1.22 ms** | 2.35 ms | 67.94 ms | 35.26 ms |
| `BB_144_12_12_w11_unsat.cnf` | UNSAT | T/O | T/O | T/O | T/O | T/O |
| `BB_144_12_12_w12_sat.cnf` | SAT | 3.38 ms | **1.97 ms** | 3.93 ms | 253.40 ms | 100.13 ms |
| **Solved (6 files)** | | **5 / 6** | **5 / 6** | **5 / 6** | **5 / 6** | **5 / 6** |
