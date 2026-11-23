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

| Instance | Verdict | Frobenius 1C | [CaDiCaL](https://github.com/arminbiere/cadical) 3.1.0 | [CMS](https://github.com/msoos/cryptominisat) 5.18 (CNF) | [CMS](https://github.com/msoos/cryptominisat) 5.18 (XCNF) | [Kissat](https://github.com/arminbiere/kissat) 4.0.4 |
|---|---:|---:|---:|---:|---:|---:|
| `BB_30_4_6_w5_unsat.cnf` | UNSAT | 585.09 ms | **12.67 ms** | 38.69 ms | 34.51 ms | 14.89 ms |
| `BB_30_4_6_w6_sat.cnf` | SAT | 6.97 ms | **2.03 ms** | 30.53 ms | 25.60 ms | 6.34 ms |
| `BB_72_12_6_w5_unsat.cnf` | UNSAT | 87.66 ms | **50.94 ms** | 104.06 ms | 90.29 ms | 56.43 ms |
| `BB_72_12_6_w6_sat.cnf` | SAT | 1.83 ms | 2.35 ms | 67.94 ms | 35.26 ms | **1.22 ms** |
| `BB_144_12_12_w11_unsat.cnf` | UNSAT | T/O | T/O | T/O | T/O | T/O |
| `BB_144_12_12_w12_sat.cnf` | SAT | 3.38 ms | 3.93 ms | 253.40 ms | 100.13 ms | **1.97 ms** |
| **Solved (6 files)** |  | **5 / 6** | **5 / 6** | **5 / 6** | **5 / 6** | **5 / 6** |

<!-- BEGIN_STRUCTURAL_ANALYSIS -->
## Phase-Transition & Structural Analysis

*Auto-generated by [`../src/analyze_benchmarks.py`](../src/analyze_benchmarks.py). Position relative to the critical phase transition is measured by $\rho_{\mathrm{crit}} = \frac{1}{n}\sum_k m_k / \alpha_c(k)$ (exact $\alpha/\alpha_c(k)$ for pure $k$-SAT; effective critical threshold $\alpha_c^{\mathrm{eff}} = \alpha/\rho_{\mathrm{crit}}$; `Under` $<0.90\times$, `Near-crit` $0.90\text{--}1.10\times$, `Over` $>1.10\times$), alongside Gent–Walsh annealed constrainedness $\kappa = -\frac{1}{n}\sum_i \log_2(1-2^{-k_i})$ (AAAI 1996), clause-length profile ($\bar{k}$, `%Bin`, `%Horn`), variable-degree CV ($\sigma_d/\bar{d}$, uniformity vs. hub skew), and extracted native XOR parity clauses.*

| Instance | Active $n$ | Clauses $m$ | $\alpha=m/n$ | $\alpha_c^{\mathrm{eff}}$ | $\rho_{\mathrm{crit}}$ (Regime) | $\kappa$ | $\bar{k}$ ($k_{\max}$) | Bin% | Horn% | Pos% | Deg CV | XORs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `BB_144_12_12_w11_unsat` | 2,077 | 5,007 | 2.41 | 1.93 | **1.25x** (Over) | 0.67 | 2.63 (12) | 37% | 74% | 44% | 1.01 | 84 |
| `BB_144_12_12_w12_sat` | 2,220 | 5,292 | 2.38 | 1.91 | **1.25x** (Over) | 0.66 | 2.62 (12) | 38% | 75% | 43% | 1.03 | 84 |
| `BB_30_4_6_w5_unsat` | 254 | 691 | 2.72 | 2.18 | **1.25x** (Over) | 0.71 | 2.70 (4) | 29% | 59% | 45% | 0.84 | 19 |
| `BB_30_4_6_w6_sat` | 283 | 748 | 2.64 | 2.12 | **1.24x** (Over) | 0.70 | 2.69 (4) | 30% | 62% | 45% | 0.88 | 19 |
| `BB_360_12_24_w23_unsat` | 9,731 | 22,027 | 2.26 | 1.83 | **1.24x** (Over) | 0.64 | 2.59 (12) | 41% | 82% | 42% | 1.27 | 192 |
| `BB_360_12_24_w24_sat` | 10,090 | 22,744 | 2.25 | 1.82 | **1.24x** (Over) | 0.64 | 2.59 (12) | 41% | 83% | 42% | 1.29 | 192 |
| `BB_72_12_6_w5_unsat` | 623 | 1,705 | 2.74 | 2.19 | **1.25x** (Over) | 0.71 | 2.71 (12) | 29% | 59% | 46% | 0.88 | 48 |
| `BB_72_12_6_w6_sat` | 694 | 1,846 | 2.66 | 2.13 | **1.25x** (Over) | 0.70 | 2.70 (12) | 30% | 62% | 45% | 0.92 | 48 |
| `BB_756_16_34_w33_unsat` | 29,581 | 67,705 | 2.29 | 1.88 | **1.22x** (Over) | 0.64 | 2.61 (16) | 39% | 81% | 43% | 1.56 | 394 |
| `BB_756_16_34_w34_sat` | 30,336 | 69,214 | 2.28 | 1.87 | **1.22x** (Over) | 0.64 | 2.61 (16) | 39% | 81% | 43% | 1.57 | 394 |

**Suite Phase-Transition Summary (10 instances):** median $\rho_{\mathrm{crit}} = 1.24\times$ (range `1.22x–1.25x`), median $\kappa = 0.66$, regime split **0 Under / 0 Near-critical / 10 Over**, total extracted native XOR parity clauses = **1,474**.
<!-- END_STRUCTURAL_ANALYSIS -->
