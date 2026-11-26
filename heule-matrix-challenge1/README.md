# Heule $3\times 3$ Matrix Multiplication — Challenge 1 (`heule-matrix-challenge1`)

![Heule 3x3 matrix multiplication tensor decomposition and Challenge 1 R=23 partitions](diagram.svg)

*Figure: 3×3 matrix multiplication tensor $T_{3,3,3}$ over $\mathbb{F}_2$, 729 Brent parity equations, and live-decoded type-3 pairing partitions across all 10 satisfiable $R = 23$ Challenge-1 instances. Regenerated via [`src/gen_diagram.py`](src/gen_diagram.py).*

## Provenance & Credit

- **Authors:** Marijn J. H. Heule, Manuel Kauers, and Martina Seidl
- **Upstream Repository:** [`marijnheule/matrix-challenges`](https://github.com/marijnheule/matrix-challenges)
- **Primary Paper:** M. J. H. Heule, M. Kauers, and M. Seidl, *"Local Search for Fast Matrix Multiplication"*, Theory and Applications of Satisfiability Testing (SAT 2019), LNCS 11628, pp. 155–163, DOI: [`10.1007/978-3-030-24258-9_10`](https://doi.org/10.1007/978-3-030-24258-9_10), [`arXiv:1903.11391`](https://arxiv.org/abs/1903.11391).
- **License:** Upstream repository does not include a dedicated `LICENSE` file; all `.cnf.xz` instances and C encoding/decoding utilities are preserved verbatim from [`marijnheule/matrix-challenges`](https://github.com/marijnheule/matrix-challenges) for scientific benchmarking and reproducibility.
- **Sibling Matrix-Challenge Collections:** [`heule-matrix-6pooled3and-c1/`](../heule-matrix-6pooled3and-c1/README.md), [`heule-matrix-6pooled3and-c3/`](../heule-matrix-6pooled3and-c3/README.md), [`heule-matrix-6pooled3and-c4/`](../heule-matrix-6pooled3and-c4/README.md), [`heule-matrix-challenge2/`](../heule-matrix-challenge2/README.md), [`heule-matrix-challenge3/`](../heule-matrix-challenge3/README.md), [`heule-matrix-challenge4/`](../heule-matrix-challenge4/README.md), [`heule-matrix-fraction/`](../heule-matrix-fraction/README.md), [`heule-matrix-xor6cut/`](../heule-matrix-xor6cut/README.md)
- **Recommended by:** [`@SMT_Solvers`](https://twitter.com/SMT_Solvers) (Twitter/X)

## Problem Description

Multiplying two $3 \times 3$ matrices over $\mathbb{F}_2$ requires finding a tensor decomposition of the $3\times 3$ matrix-multiplication tensor into $R$ rank-1 products (Laderman's 1976 scheme achieved $R = 23$, and whether $R \le 22$ exists over $\mathbb{F}_2$ or $\mathbb{Q}$ remains a famous open problem in algebraic complexity). Encoding the Brent equations over $\mathbb{F}_2$ yields structured, highly symmetric, non-linear XOR+AND polynomial systems whose clausal forms challenge both CDCL and local-search SAT solvers.

Ten satisfiable $R = 23$ $\mathbb{F}_2$ matrix-multiplication Brent-equation instances with hardcoded pairings of type-3 terms and **no** streamlining constraints (five were solved by [YalSAT](https://github.com/arminbiere/yalsat) in minutes in the SAT 2019 paper, while complete CDCL solvers struggled).

## Corpus & Data Sizes

- **`cnf-orig/`** — 10 original native **DIMACS `.cnf.xz`** files (1.81 MB).
- **`aig-converted/`** — 10 exact **Binary AIGER 1.9 `.aig.xz`** conversions (2.24 MB, verified via [Berkeley ABC](https://github.com/berkeley-abc/abc) `read_aiger`).
- **`xcnf-converted/`** — 10 lossless **[CryptoMiniSat](https://github.com/msoos/cryptominisat) `.xcnf.xz`** conversions (753.9 KB, `80,190` extracted native XOR parity clauses).
- **`anf-converted/`** — 10 lossless linear-size **DIMACS-ANF `.anf.xz`** conversions (1.40 MB, generated via [`../src/to_anf.py`](../src/to_anf.py)).
- **[`expected.tsv`](expected.tsv)** — Ground-truth verdict manifest for all 10 instances (**10 SAT / 0 UNSAT**).
- **`src/`** — Upstream C utilities preserved from `marijnheule/matrix-challenges` (`encode.c`, `decode.c`, `exp2cnf.c`, `pair.c`, `palin.c`, `stats.c`, `type3.c`) plus `cnf2aig.py` and `cnf2xcnf.py`.

| Format | Directory | Files | Key Dimensions (Range) | Compressed Size |
|---|---|---:|---|---:|
| **DIMACS CNF (origin)** | `cnf-orig/` | 10 | Vars: 26,541; Clauses: 117,206–117,219 | 1.81 MB |
| **Binary AIGER 1.9** | `aig-converted/` | 10 | Inputs: 26,541; ANDs: 314,184–314,198 | 2.24 MB |
| **[CryptoMiniSat](https://github.com/msoos/cryptominisat) XCNF** | `xcnf-converted/` | 10 | Native XOR clauses total: 80,190 | 753.9 KB |
| **DIMACS-ANF** | `anf-converted/` | 10 | Vars: 26,541; Eqs: 63,989–64,002 (deg ≤ 3) | 1.40 MB |
| **Total (4 Formats, Status: SAT (hard for CDCL))** | | **40** | | **6.19 MB** |

## Benchmark Results

- **Hardware & Protocol:** Same machine (**AMD Ryzen 9 5950X**, 16C/32T Linux, **1 thread per run** pinned across 8 dedicated physical cores, $T_{\max} = 10\;\text{s}$, PAR-2 penalty $20,000\;\text{ms}$). All solvers ran with default single-thread flags (`-t 1` for CryptoMiniSat 5.18.0; `--max-cores 1` for Frobenius) on identical uncompressed flat `.cnf` inputs (with native `.xcnf` also supplied to CryptoMiniSat XCNF); **100% of all 10 instances** were run (no subsampling), every Frobenius SAT model was independently verified against 100% of input clauses, and **0 verdict disagreements** occurred across all solvers.

| Instance | Verdict | Frobenius 1C | [CaDiCaL](https://github.com/arminbiere/cadical) 3.1.0 | [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18.0 (CNF) | [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18.0 (XCNF) | [dense-solver](https://github.com/libdense/dense-solver) 0.0.4 | [Kissat](https://github.com/arminbiere/kissat) 4.0.4 |
|---|:---:|---:|---:|---:|---:|---:|---:|
| `MM-23-2-2-2-2-3` | TIMEOUT | >10 s | >10 s | >10 s | >10 s | >10 s | >10 s |
| `MM-23-2-2-2-2-A` | TIMEOUT | >10 s | >10 s | >10 s | >10 s | >10 s | >10 s |
| `MM-23-2-2-2-2-B` | TIMEOUT | >10 s | >10 s | >10 s | >10 s | >10 s | >10 s |
| `MM-23-2-2-2-2-C` | TIMEOUT | >10 s | >10 s | >10 s | >10 s | >10 s | >10 s |
| `MM-23-2-2-2-2-D` | TIMEOUT | >10 s | >10 s | >10 s | >10 s | >10 s | >10 s |
| `MM-23-2-2-2-2-M` | TIMEOUT | >10 s | >10 s | >10 s | >10 s | >10 s | >10 s |
| `MM-23-2-2-2-3-4` | TIMEOUT | >10 s | >10 s | >10 s | >10 s | >10 s | >10 s |
| `MM-23-2-2-2-4-A` | TIMEOUT | >10 s | >10 s | >10 s | >10 s | >10 s | >10 s |
| `MM-23-2-2-2-4-B` | TIMEOUT | >10 s | >10 s | >10 s | >10 s | >10 s | >10 s |
| `MM-23-4-4-4-4-1` | TIMEOUT | >10 s | >10 s | >10 s | >10 s | >10 s | >10 s |
| **Solved (10 files)** | — | 0 / 10 | 0 / 10 | 0 / 10 | 0 / 10 | 0 / 10 | 0 / 10 |
| **Total PAR-2** | — | 200,000.0 ms | 200,000.0 ms | 200,000.0 ms | 200,000.0 ms | 200,000.0 ms | 200,000.0 ms |

<!-- BEGIN_STRUCTURAL_ANALYSIS -->
## Phase-Transition & Structural Analysis

*Auto-generated by [`../src/analyze_benchmarks.py`](../src/analyze_benchmarks.py). Position relative to the critical phase transition is measured by $\rho_{\mathrm{crit}} = \frac{1}{n}\sum_k m_k / \alpha_c(k)$ (exact $\alpha/\alpha_c(k)$ for pure $k$-SAT; effective critical threshold $\alpha_c^{\mathrm{eff}} = \alpha/\rho_{\mathrm{crit}}$; `Under` $<0.90\times$, `Near-crit` $0.90\text{--}1.10\times$, `Over` $>1.10\times$), alongside Gent–Walsh annealed constrainedness $\kappa = -\frac{1}{n}\sum_i \log_2(1-2^{-k_i})$ (AAAI 1996), clause-length profile ($\bar{k}$, `%Bin`, `%Horn`), variable-degree CV ($\sigma_d/\bar{d}$, uniformity vs. hub skew), and extracted native XOR parity clauses.*

| Instance | Active $n$ | Clauses $m$ | $\alpha=m/n$ | $\alpha_c^{\mathrm{eff}}$ | $\rho_{\mathrm{crit}}$ (Regime) | $\kappa$ | $\bar{k}$ ($k_{\max}$) | Bin% | Horn% | Pos% | Deg CV | XORs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `MM-23-2-2-2-2-3` | 26,541 | 117,211 | 4.42 | 2.43 | **1.82x** (Over) | 0.95 | 3.18 (4) | 32% | 73% | 48% | 0.96 | 8,019 |
| `MM-23-2-2-2-2-A` | 26,541 | 117,207 | 4.42 | 2.43 | **1.82x** (Over) | 0.95 | 3.18 (4) | 32% | 73% | 48% | 0.96 | 8,019 |
| `MM-23-2-2-2-2-B` | 26,541 | 117,207 | 4.42 | 2.43 | **1.82x** (Over) | 0.95 | 3.18 (4) | 32% | 73% | 48% | 0.96 | 8,019 |
| `MM-23-2-2-2-2-C` | 26,541 | 117,207 | 4.42 | 2.43 | **1.82x** (Over) | 0.95 | 3.18 (4) | 32% | 73% | 48% | 0.96 | 8,019 |
| `MM-23-2-2-2-2-D` | 26,541 | 117,207 | 4.42 | 2.43 | **1.82x** (Over) | 0.95 | 3.18 (4) | 32% | 73% | 48% | 0.96 | 8,019 |
| `MM-23-2-2-2-2-M` | 26,541 | 117,206 | 4.42 | 2.43 | **1.82x** (Over) | 0.95 | 3.18 (4) | 32% | 73% | 48% | 0.96 | 8,019 |
| `MM-23-2-2-2-3-4` | 26,541 | 117,214 | 4.42 | 2.43 | **1.82x** (Over) | 0.95 | 3.18 (4) | 32% | 73% | 48% | 0.96 | 8,019 |
| `MM-23-2-2-2-4-A` | 26,541 | 117,210 | 4.42 | 2.43 | **1.82x** (Over) | 0.95 | 3.18 (4) | 32% | 73% | 48% | 0.96 | 8,019 |
| `MM-23-2-2-2-4-B` | 26,541 | 117,210 | 4.42 | 2.43 | **1.82x** (Over) | 0.95 | 3.18 (4) | 32% | 73% | 48% | 0.96 | 8,019 |
| `MM-23-4-4-4-4-1` | 26,541 | 117,219 | 4.42 | 2.43 | **1.82x** (Over) | 0.95 | 3.18 (4) | 32% | 73% | 48% | 0.96 | 8,019 |

**Collection Phase-Transition Summary (10 instances, 4 formats: 10 CNF / 10 AIG / 10 XCNF / 10 ANF):** median $\rho_{\mathrm{crit}} = 1.82\times$ (range `1.82x–1.82x`), median $\kappa = 0.95$, regime split **0 Under / 0 Near-critical / 10 Over**, total extracted native XOR parity clauses = **80,190**, total ANF equations = **639,928**.
<!-- END_STRUCTURAL_ANALYSIS -->

## References

- **Heule, Kauers, and Seidl (SAT 2019, `arXiv:1903.11391`):** Discovered over $17{,}000$ inequivalent $R = 23$ schemes over $\mathbb{F}_2$ using [YalSAT](https://github.com/arminbiere/yalsat) local search with random type-3 pairings and streamlining constraints; noted that complete CDCL solvers struggled even on satisfiable `challenge1` instances without streamlining, and left `challenge2`–`challenge4` as open solver benchmarks.
