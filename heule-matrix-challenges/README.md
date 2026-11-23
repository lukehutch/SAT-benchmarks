# Matrix Multiplication SAT Challenges (Heule–Kauers–Seidl, SAT 2019)

## Provenance & Credit

- **Recommended by:** [`@SMT_Solvers`](https://twitter.com/SMT_Solvers) (Twitter/X)
- **Authors:** Marijn J. H. Heule, Manuel Kauers, and Martina Seidl
- **Upstream Repository:** [`marijnheule/matrix-challenges`](https://github.com/marijnheule/matrix-challenges)
- **Primary Paper:** M. J. H. Heule, M. Kauers, and M. Seidl, *"Local Search for Fast Matrix Multiplication"*, Theory and Applications of Satisfiability Testing (SAT 2019), LNCS 11628, pp. 155–163, DOI: [`10.1007/978-3-030-24258-9_10`](https://doi.org/10.1007/978-3-030-24258-9_10), [`arXiv:1903.11391`](https://arxiv.org/abs/1903.11391).
- **License:** Upstream repository does not include a dedicated `LICENSE` file; all `.cnf.xz` instances and C encoding/decoding utilities are preserved verbatim from [`marijnheule/matrix-challenges`](https://github.com/marijnheule/matrix-challenges) for scientific benchmarking and reproducibility.

## Problem Description

Multiplying two $3 \times 3$ matrices over $\mathbb{F}_2$ requires finding a tensor decomposition of the $3\times 3$ matrix-multiplication tensor into $R$ rank-1 products (Laderman's 1976 scheme achieved $R = 23$, and whether $R \le 22$ exists over $\mathbb{F}_2$ or $\mathbb{Q}$ remains a famous open problem in algebraic complexity). Encoding the Brent equations over $\mathbb{F}_2$ yields structured, highly symmetric, non-linear XOR+AND polynomial systems whose clausal forms challenge both CDCL and local-search SAT solvers:

- **`challenge1/` (10 instances, SAT):** $R = 23$ schemes with hardcoded pairings of type-3 terms and **no** streamlining constraints. Satisfiable, yet very hard for complete CDCL solvers (five were solved by [`yalsat`](https://github.com/arminbiere/yalsat) in minutes in the SAT 2019 paper).
- **`challenge2/` (10 instances, expected UNSAT):** $R = 23$ subproblems with hardcoded pairings of type-3 terms intended as unsatisfiability targets for complete solvers.
- **`challenge3/` (1 instance, open/hard):** Tests whether an $R = 23$ scheme exists in which the last summand contains no type-3 term (no streamlining constraints).
- **`challenge4/` (1 instance, open frontier):** Plain Brent-equation encoding for an $R = 22$ matrix multiplication scheme over $\mathbb{F}_2$.
- **`6pooled3and/` (12 instances):** Alternative compact pooled-AND encodings of `challenge1`, `challenge3`, and `challenge4` (reducing variable count from $26{,}541 \to 21{,}033$ while increasing clause count from $\sim 117\text{k} \to \sim 187\text{k}$).
- **`fraction/` (3 instances, `f-d-3`, `f-d-4`, `f-d-6`):** Fractional / restricted-coefficient variants ($152{,}785$ vars, $150{,}314$ clauses).
- **`xor6cut/` (6 instances, `xor6cut-22..27`):** Compact XOR-cut encodings spanning $R = 22 \dots 27$ ($19{,}548\text{--}24{,}786$ vars, $180{,}858\text{--}221{,}697$ clauses).

## Corpus & Data Sizes

All **43 `.cnf.xz`** benchmark files from upstream are mirrored verbatim (`11.4 MB` compressed), together with exact **Binary AIGER 1.9** conversions in `aig-version/` for all **43 / 43** instances (all verified via [Berkeley ABC](https://github.com/berkeley-abc/abc) `read_aiger`), lossless **[CryptoMiniSat](https://github.com/msoos/cryptominisat) XCNF** conversions in `xcnf-version/` (`253,692` extracted native `x`-clauses across 40/43 files, `.xcnf.xz`), and the upstream C encoders/decoders plus `cnf2aig.py` / `cnf2xcnf.py` in `src/`:

| Directory | Instances | Vars | Clauses | CNF (`.cnf.xz`) Size | AIG / XCNF Files | Status |
|---|---:|---:|---:|---:|---:|---|
| `challenge1/` | 10 | 26,541 | 117,206–117,219 | 1.86 MB | 10 / 10 | SAT (hard for CDCL) |
| `challenge2/` | 10 | 26,541 | 117,203–117,207 | 1.94 MB | 10 / 10 | Expected UNSAT |
| `challenge3/` | 1 | 26,541 | 117,153 | 165 KB | 1 / 1 | Open / Hard |
| `challenge4/` | 1 | 24,975 | 111,780 | 193 KB | 1 / 1 | Open ($R = 22$) |
| `6pooled3and/` | 12 | 19,548–21,033 | 180,792–186,717 | 3.97 MB | 12 / 12 | Mixed / Open |
| `fraction/` | 3 | 152,785 | 150,314 | 948 KB | 3 / 3 | Hard |
| `xor6cut/` | 6 | 19,548–24,786 | 180,858–221,697 | 2.08 MB | 6 / 6 | Mixed ($R=22\text{--}27$) |
| **Total** | **43** | **19,548–152,785** | **111,780–221,697** | **11.4 MB** | **43 / 43** | |

## Source Code (`src/`)

- Upstream C utilities preserved from `marijnheule/matrix-challenges`: `encode.c`, `decode.c`, `exp2cnf.c`, `pair.c`, `palin.c`, `stats.c`, `type3.c`.
- `cnf2aig.py`: Standalone DIMACS `.cnf`/`.cnf.xz` to Binary AIGER 1.9 converter.

## Published Results & References

- **Heule, Kauers, and Seidl (SAT 2019, `arXiv:1903.11391`):** Discovered over $17{,}000$ inequivalent $R = 23$ schemes over $\mathbb{F}_2$ using [`yalsat`](https://github.com/arminbiere/yalsat) local search with random type-3 pairings and streamlining constraints; noted that complete CDCL solvers struggled even on the satisfiable `challenge1` instances without streamlining, and left `challenge2`–`challenge4` as open solver benchmarks.

<!-- BEGIN_STRUCTURAL_ANALYSIS -->
## Phase-Transition & Structural Analysis

*Auto-generated by [`../src/analyze_benchmarks.py`](../src/analyze_benchmarks.py). Position relative to the critical phase transition is measured by $\rho_{\mathrm{crit}} = \frac{1}{n}\sum_k m_k / \alpha_c(k)$ (exact $\alpha/\alpha_c(k)$ for pure $k$-SAT; effective critical threshold $\alpha_c^{\mathrm{eff}} = \alpha/\rho_{\mathrm{crit}}$; `Under` $<0.90\times$, `Near-crit` $0.90\text{--}1.10\times$, `Over` $>1.10\times$), alongside Gent–Walsh annealed constrainedness $\kappa = -\frac{1}{n}\sum_i \log_2(1-2^{-k_i})$ (AAAI 1996), clause-length profile ($\bar{k}$, `%Bin`, `%Horn`), variable-degree CV ($\sigma_d/\bar{d}$, uniformity vs. hub skew), and extracted native XOR parity clauses.*

| Group / Family | Files | Med $n$ | Med $m$ | $\alpha=m/n$ (Med) | $\alpha_c^{\mathrm{eff}}$ (Med) | $\rho_{\mathrm{crit}}$ Med [Min–Max] (Regime) | Med $\kappa$ | Med $\bar{k}$ | Bin% | Horn% | Deg CV | Total XORs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `6pooled3and/challenge1` | 10 | 21,033 | 186,706 | 8.88 | 3.37 | **2.64x** [2.64x–2.64x] (Over) | 1.22 | 4.69 | 27% | 48% | 0.53 | 43,740 |
| `6pooled3and/challenge3` | 1 | 21,033 | 186,651 | 8.87 | 3.37 | **2.63x** [2.63x] (Over) | 1.22 | 4.70 | 27% | 48% | 0.53 | 4,374 |
| `6pooled3and/challenge4` | 1 | 19,548 | 180,792 | 9.25 | 3.45 | **2.68x** [2.68x] (Over) | 1.23 | 4.76 | 27% | 48% | 0.53 | 3,645 |
| `challenge1` | 10 | 26,541 | 117,208 | 4.42 | 2.43 | **1.82x** [1.82x–1.82x] (Over) | 0.95 | 3.18 | 32% | 73% | 0.96 | 80,190 |
| `challenge2` | 10 | 26,541 | 117,207 | 4.42 | 2.43 | **1.82x** [1.82x–1.82x] (Over) | 0.95 | 3.18 | 32% | 73% | 0.96 | 80,190 |
| `challenge3` | 1 | 26,541 | 117,153 | 4.41 | 2.43 | **1.82x** [1.82x] (Over) | 0.94 | 3.18 | 32% | 73% | 0.96 | 8,019 |
| `challenge4` | 1 | 24,975 | 111,780 | 4.48 | 2.45 | **1.83x** [1.83x] (Over) | 0.95 | 3.20 | 32% | 74% | 0.95 | 7,290 |
| `fraction` | 3 | 33,291 | 150,314 | 4.52 | 1.73 | **2.60x** [2.60x–2.60x] (Over) | 1.26 | 4.68 | 48% | 89% | 0.76 | 0 |
| `xor6cut` | 6 | 22,167 | 196,903 | 8.94 | 3.39 | **2.65x** [2.62x–2.68x] (Over) | 1.22 | 4.71 | 27% | 48% | 0.53 | 26,244 |

**Suite Phase-Transition Summary (43 instances):** median $\rho_{\mathrm{crit}} = 1.83\times$ (range `1.82x–2.68x`), median $\kappa = 0.95$, regime split **0 Under / 0 Near-critical / 43 Over**, total extracted native XOR parity clauses = **253,692**.
<!-- END_STRUCTURAL_ANALYSIS -->
