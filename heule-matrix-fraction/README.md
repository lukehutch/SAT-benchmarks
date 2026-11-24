# Heule $3\times 3$ Matrix Multiplication — Fractional Variants (`heule-matrix-fraction`)

## Provenance & Credit

- **Authors:** Marijn J. H. Heule, Manuel Kauers, and Martina Seidl
- **Upstream Repository:** [`marijnheule/matrix-challenges`](https://github.com/marijnheule/matrix-challenges)
- **Primary Paper:** M. J. H. Heule, M. Kauers, and M. Seidl, *"Local Search for Fast Matrix Multiplication"*, Theory and Applications of Satisfiability Testing (SAT 2019), LNCS 11628, pp. 155–163, DOI: [`10.1007/978-3-030-24258-9_10`](https://doi.org/10.1007/978-3-030-24258-9_10), [`arXiv:1903.11391`](https://arxiv.org/abs/1903.11391).
- **License:** Upstream repository does not include a dedicated `LICENSE` file; all `.cnf.xz` instances and C encoding/decoding utilities are preserved verbatim from [`marijnheule/matrix-challenges`](https://github.com/marijnheule/matrix-challenges) for scientific benchmarking and reproducibility.
- **Sibling Matrix-Challenge Collections:** [`heule-matrix-6pooled3and-c1/`](../heule-matrix-6pooled3and-c1/README.md), [`heule-matrix-6pooled3and-c3/`](../heule-matrix-6pooled3and-c3/README.md), [`heule-matrix-6pooled3and-c4/`](../heule-matrix-6pooled3and-c4/README.md), [`heule-matrix-challenge1/`](../heule-matrix-challenge1/README.md), [`heule-matrix-challenge2/`](../heule-matrix-challenge2/README.md), [`heule-matrix-challenge3/`](../heule-matrix-challenge3/README.md), [`heule-matrix-challenge4/`](../heule-matrix-challenge4/README.md), [`heule-matrix-xor6cut/`](../heule-matrix-xor6cut/README.md)
- **Recommended by:** [`@SMT_Solvers`](https://twitter.com/SMT_Solvers) (Twitter/X)

## Problem Description

Multiplying two $3 \times 3$ matrices over $\mathbb{F}_2$ requires finding a tensor decomposition of the $3\times 3$ matrix-multiplication tensor into $R$ rank-1 products (Laderman's 1976 scheme achieved $R = 23$, and whether $R \le 22$ exists over $\mathbb{F}_2$ or $\mathbb{Q}$ remains a famous open problem in algebraic complexity). Encoding the Brent equations over $\mathbb{F}_2$ yields structured, highly symmetric, non-linear XOR+AND polynomial systems whose clausal forms challenge both CDCL and local-search SAT solvers.

Three restricted-coefficient / fractional variants (`f-d-3`, `f-d-4`, `f-d-6`) of the $3\times 3$ matrix-multiplication Brent equations.

![Heule matrix multiplication fraction cardinality-restricted Brent encoding](diagram.svg)

*Figure: XOR-free cardinality-restricted $R = 23$ Brent encoding replacing mod-2 parity with `EXACTLY-1` ($\delta=1$) and `ZERO-OR-2` ($\delta=0$, `0` XORs, `89%` Horn) plus `noRank3` and live-decoded 4-pair pins for `f-d-3`, `f-d-4`, `f-d-6`. Regenerated via [`src/gen_diagram.py`](src/gen_diagram.py).*

## Corpus & Data Sizes (Four Formats)

- **`cnf-orig/`** — 3 original native **DIMACS `.cnf.xz`** files (947.7 KB).
- **`aig-converted/`** — 3 exact **Binary AIGER 1.9 `.aig.xz`** conversions (1.31 MB, verified via [Berkeley ABC](https://github.com/berkeley-abc/abc) `read_aiger`).
- **`xcnf-converted/`** — 3 lossless **[CryptoMiniSat](https://github.com/msoos/cryptominisat) `.xcnf.xz`** conversions (944.6 KB, `0` extracted native XOR parity clauses).
- **`anf-converted/`** — 3 lossless linear-size **DIMACS-ANF `.anf.xz`** conversions (4.76 MB, generated via [`../src/to_anf.py`](../src/to_anf.py)).
- **[`expected.tsv`](expected.tsv)** — Ground-truth verdict manifest for all 3 instances (**0 SAT / 0 UNSAT / 3 UNKNOWN**).
- **`src/`** — Upstream C utilities preserved from `marijnheule/matrix-challenges` (`encode.c`, `decode.c`, `exp2cnf.c`, `pair.c`, `palin.c`, `stats.c`, `type3.c`) plus `cnf2aig.py` and `cnf2xcnf.py`.

| Format | Directory | Files | Key Dimensions (Range) | Compressed Size |
|---|---|---:|---|---:|
| **DIMACS CNF (origin)** | `cnf-orig/` | 3 | Vars: 152,785; Clauses: 150,314 | 947.7 KB |
| **Binary AIGER 1.9** | `aig-converted/` | 3 | Inputs: 152,785; ANDs: 423,772 | 1.31 MB |
| **[CryptoMiniSat](https://github.com/msoos/cryptominisat) XCNF** | `xcnf-converted/` | 3 | Native XOR clauses total: 0 | 944.6 KB |
| **DIMACS-ANF** | `anf-converted/` | 3 | Vars: 477,199; Eqs: 474,728 (deg ≤ 3) | 4.76 MB |
| **Total (4 Formats, Status: Hard)** | | **12** | | **7.93 MB** |

## Published Results & References

- **Heule, Kauers, and Seidl (SAT 2019, `arXiv:1903.11391`):** Discovered over $17{,}000$ inequivalent $R = 23$ schemes over $\mathbb{F}_2$ using [YalSAT](https://github.com/arminbiere/yalsat) local search with random type-3 pairings and streamlining constraints; noted that complete CDCL solvers struggled even on satisfiable `challenge1` instances without streamlining, and left `challenge2`–`challenge4` as open solver benchmarks.

## Comparative 1-Core Benchmark Results (All 3 Instances, Flat `.cnf` + `.xcnf`, $T_{\max} = 60\;\text{s}$)

- **Hardware & Protocol:** Same machine (**AMD Ryzen 9 5950X**, 16C/32T Linux, **1 thread per run** pinned across 8 dedicated physical cores, $T_{\max} = 60\;\text{s}$, PAR-2 penalty $120,000\;\text{ms}$). All solvers ran with default single-thread flags (`-t 1` for CryptoMiniSat 5.18.0; `--max-cores 1` for Frobenius) on identical uncompressed flat `.cnf` inputs (with native `.xcnf` also supplied to CryptoMiniSat XCNF); **100% of all 3 instances** were run with **0 verdict disagreements**.

| Instance | Verdict | Frobenius 1C | [CaDiCaL](https://github.com/arminbiere/cadical) 3.1.0 | [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18.0 (CNF) | [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18.0 (XCNF) | [dense-solver](https://github.com/libdense/dense-solver) 0.0.4 | [Kissat](https://github.com/arminbiere/kissat) 4.0.4 |
|---|:---:|---:|---:|---:|---:|---:|---:|
| `f-d-3` | TIMEOUT | >60 s | >60 s | >60 s | >60 s | >60 s | >60 s |
| `f-d-4` | TIMEOUT | >60 s | >60 s | >60 s | >60 s | >60 s | >60 s |
| `f-d-6` | TIMEOUT | >60 s | >60 s | >60 s | >60 s | >60 s | >60 s |
| **Total (3 files, PAR-2)** | **0/3** | **0/3 — 360,000.0 ms** *(fastest)* | **0/3 — 360,000.0 ms** *(fastest)* | **0/3 — 360,000.0 ms** *(fastest)* | **0/3 — 360,000.0 ms** *(fastest)* | **0/3 — 360,000.0 ms** *(fastest)* | **0/3 — 360,000.0 ms** *(fastest)* |

<!-- BEGIN_STRUCTURAL_ANALYSIS -->
## Phase-Transition & Structural Analysis

*Auto-generated by [`../src/analyze_benchmarks.py`](../src/analyze_benchmarks.py). Position relative to the critical phase transition is measured by $\rho_{\mathrm{crit}} = \frac{1}{n}\sum_k m_k / \alpha_c(k)$ (exact $\alpha/\alpha_c(k)$ for pure $k$-SAT; effective critical threshold $\alpha_c^{\mathrm{eff}} = \alpha/\rho_{\mathrm{crit}}$; `Under` $<0.90\times$, `Near-crit` $0.90\text{--}1.10\times$, `Over` $>1.10\times$), alongside Gent–Walsh annealed constrainedness $\kappa = -\frac{1}{n}\sum_i \log_2(1-2^{-k_i})$ (AAAI 1996), clause-length profile ($\bar{k}$, `%Bin`, `%Horn`), variable-degree CV ($\sigma_d/\bar{d}$, uniformity vs. hub skew), and extracted native XOR parity clauses.*

| Instance | Active $n$ | Clauses $m$ | $\alpha=m/n$ | $\alpha_c^{\mathrm{eff}}$ | $\rho_{\mathrm{crit}}$ (Regime) | $\kappa$ | $\bar{k}$ ($k_{\max}$) | Bin% | Horn% | Pos% | Deg CV | XORs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `f-d-3` | 33,291 | 150,314 | 4.52 | 1.73 | **2.60x** (Over) | 1.26 | 4.68 (23) | 48% | 89% | 65% | 0.76 | 0 |
| `f-d-4` | 33,291 | 150,314 | 4.52 | 1.73 | **2.60x** (Over) | 1.26 | 4.68 (23) | 48% | 89% | 65% | 0.76 | 0 |
| `f-d-6` | 33,291 | 150,314 | 4.52 | 1.73 | **2.60x** (Over) | 1.26 | 4.68 (23) | 48% | 89% | 65% | 0.76 | 0 |

**Collection Phase-Transition Summary (3 instances, 4 formats: 3 CNF / 3 AIG / 3 XCNF / 3 ANF):** median $\rho_{\mathrm{crit}} = 2.60\times$ (range `2.60x–2.60x`), median $\kappa = 1.26$, regime split **0 Under / 0 Near-critical / 3 Over**, total extracted native XOR parity clauses = **0**, total ANF equations = **1,424,184**.
<!-- END_STRUCTURAL_ANALYSIS -->
