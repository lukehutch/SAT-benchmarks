# Matrix Multiplication SAT Challenges (Heule–Kauers–Seidl, SAT 2019)

## Provenance & Credit

- **Recommended by:** `@SMT_Solvers` (Twitter/X)
- **Authors:** Marijn J. H. Heule, Manuel Kauers, and Martina Seidl
- **Upstream Repository:** [`marijnheule/matrix-challenges`](https://github.com/marijnheule/matrix-challenges)
- **Primary Paper:** M. J. H. Heule, M. Kauers, and M. Seidl, *"Local Search for Fast Matrix Multiplication"*, Theory and Applications of Satisfiability Testing (SAT 2019), LNCS 11628, pp. 155–163, DOI: [`10.1007/978-3-030-24258-9_10`](https://doi.org/10.1007/978-3-030-24258-9_10), [`arXiv:1903.11391`](https://arxiv.org/abs/1903.11391).
- **License:** Upstream repository does not include a dedicated `LICENSE` file; all `.cnf.xz` instances and C encoding/decoding utilities are preserved verbatim from [`marijnheule/matrix-challenges`](https://github.com/marijnheule/matrix-challenges) for scientific benchmarking and reproducibility.

## Problem Description

Multiplying two $3 \times 3$ matrices over $\mathbb{F}_2$ requires finding a tensor decomposition of the $3\times 3$ matrix-multiplication tensor into $R$ rank-1 products (Laderman's 1976 scheme achieved $R = 23$, and whether $R \le 22$ exists over $\mathbb{F}_2$ or $\mathbb{Q}$ remains a famous open problem in algebraic complexity). Encoding the Brent equations over $\mathbb{F}_2$ yields structured, highly symmetric, non-linear XOR+AND polynomial systems whose clausal forms challenge both CDCL and local-search SAT solvers:

- **`challenge1/` (10 instances, SAT):** $R = 23$ schemes with hardcoded pairings of type-3 terms and **no** streamlining constraints. Satisfiable, yet very hard for complete CDCL solvers (five were solved by `yalsat` in minutes in the SAT 2019 paper).
- **`challenge2/` (10 instances, expected UNSAT):** $R = 23$ subproblems with hardcoded pairings of type-3 terms intended as unsatisfiability targets for complete solvers.
- **`challenge3/` (1 instance, open/hard):** Tests whether an $R = 23$ scheme exists in which the last summand contains no type-3 term (no streamlining constraints).
- **`challenge4/` (1 instance, open frontier):** Plain Brent-equation encoding for an $R = 22$ matrix multiplication scheme over $\mathbb{F}_2$.
- **`6pooled3and/` (12 instances):** Alternative compact pooled-AND encodings of `challenge1`, `challenge3`, and `challenge4` (reducing variable count from $26{,}541 \to 21{,}033$ while increasing clause count from $\sim 117\text{k} \to \sim 187\text{k}$).
- **`fraction/` (3 instances, `f-d-3`, `f-d-4`, `f-d-6`):** Fractional / restricted-coefficient variants ($152{,}785$ vars, $150{,}314$ clauses).
- **`xor6cut/` (6 instances, `xor6cut-22..27`):** Compact XOR-cut encodings spanning $R = 22 \dots 27$ ($19{,}548\text{--}24{,}786$ vars, $180{,}858\text{--}221{,}697$ clauses).

## Corpus & Data Sizes

All **43 `.cnf.xz`** benchmark files from upstream are mirrored verbatim (`11.4 MB` compressed), together with exact **Binary AIGER 1.9** conversions in `aig-version/` for all **43 / 43** instances (all verified via Berkeley ABC `read_aiger`), lossless **CryptoMiniSat XCNF** conversions in `xcnf-version/` (`253,692` extracted native `x`-clauses across 40/43 files, `.xcnf.xz`), and the upstream C encoders/decoders plus `cnf2aig.py` / `cnf2xcnf.py` in `src/`:

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

- **Heule, Kauers, and Seidl (SAT 2019, `arXiv:1903.11391`):** Discovered over $17{,}000$ inequivalent $R = 23$ schemes over $\mathbb{F}_2$ using `yalsat` local search with random type-3 pairings and streamlining constraints; noted that complete CDCL solvers struggled even on the satisfiable `challenge1` instances without streamlining, and left `challenge2`–`challenge4` as open solver benchmarks.
