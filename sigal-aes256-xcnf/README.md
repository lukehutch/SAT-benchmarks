# Full 14-Round AES-256 Known-Plaintext Key-Recovery XCNFs (`sigal-aes256-xcnf`)

## Provenance & Credit

- **Author & Contributor:** Victor Sigal ([`@uniexpertise`](https://twitter.com/uniexpertise))
- **Origin Archive:** `Sigal.zip` (`LH_sat/w5.solved.xcnf` and `LH_sat/w126.unsolved.xcnf`), shared directly for evaluation and community benchmarking.
- **Author's Context:** *"Solved file have only one SAT model. I expecting that w126 should have only one SAT. I trying to solve w126 for 2 years now."*
- **Upstream References:**
  - National Institute of Standards and Technology, *Advanced Encryption Standard (AES)*, Federal Information Processing Standards Publication 197 (**FIPS 197**, 2001), [`doi:10.6028/NIST.FIPS.197`](https://doi.org/10.6028/NIST.FIPS.197).
  - Joan Boyar and René Peralta, *"A New Combinational Logic Minimization Technique with Applications to Cryptology"*, SEA 2010, LNCS 6049, pp. 178–189, [`doi:10.1007/978-3-642-13193-6_16`](https://doi.org/10.1007/978-3-642-13193-6_16).

## Structural & Cryptographic Analysis

Circuit-level analysis confirms that both instances encode **exact full 14-round NIST FIPS 197 AES-256 key recovery from two known 128-bit plaintext–ciphertext pairs**:
$$\mathrm{AES\text{-}256}(K, P_1) = C_1 \quad \land \quad \mathrm{AES\text{-}256}(K, P_2) = C_2.$$

- **Exact NIST FIPS 197 Verification:** Assigning `K = 0` (`vars 1..256 = FALSE`) and `P_1 = 0` (`vars 7293..7420 = FALSE`) and evaluating the 59,324-variable gate network forward yields ciphertext output bits (`vars 7421..7548`, LSB-first per byte) matching NIST's official test vector `AES-256(0, 0) = dc95c078a2408989ad48a21492842087` on **128 / 128 bits**.
- **Exact Circuit Decomposition (`59,324 / 59,324` variables resolved, max depth = `215`, multiplicative AND-depth = `84`):**
  - **256 unconstrained primary inputs** (`vars 1..256`): the 256-bit secret key (**0 key bits fixed**).
  - **512 unit clauses**: two known 128-bit plaintexts (`vars 7293..7420`, `7549..7676`) and two known 128-bit ciphertexts (`vars 7421..7548`, `7677..7804`).
  - **500 Boyar–Peralta AES S-boxes** (`52` key-schedule + $2 \times 224$ encryption S-boxes) = **16,000 nonlinear AND gates**, each encoded compactly as 2 binary clauses `(-z | b), (-b | -d)` paired with 1 3-XOR `d = a ^ z`.
  - **90,500 Gröbner-basis implied binary clauses** (`181` per S-box: `9,412` on the key schedule + `81,088` on encryption rounds).
  - **42,812 native [CryptoMiniSat](https://github.com/msoos/cryptominisat) `x...` XOR parity clauses** (lengths `3..15`, mean `6.02`) forming a single 59,324-variable connected component.
- **Why `w5` vs. `w126` Differ in Difficulty:** Out of `165,824` total clauses (`123,012` CNF + `42,812` XOR), **`165,312` lines are byte-for-byte identical** across both files — only the 512 plaintext/ciphertext unit clauses differ. The filenames reflect the presumed Hamming weight of the secret key:
  - **`w5.solved.xcnf.xz`**: Hamming-weight-5 key ($\binom{256}{5} \approx 8.8 \times 10^9 \approx 2^{33}$ candidates — reachable via specialized low-weight search if the weight bound is known, though **no weight constraint is encoded in the XCNF**).
  - **`w126.unsolved.xcnf.xz`**: Balanced weight-126 key ($\binom{256}{126} \approx 2^{252}$ candidates — **full-strength 14-round AES-256** key recovery, matching the best known $\approx 2^{254.4}$ classical cryptanalytic barrier).

## Corpus & Data Sizes (Three Formats)

Native unmodified `.xcnf.xz` files (xz-compressed) live at the suite root; exact Tseitin DIMACS `.cnf.xz` conversions (`cnf-version/`) and [Berkeley ABC](https://github.com/berkeley-abc/abc)-verified Binary AIGER 1.9 `.aig.xz` miters (`aig-version/`, `0` errors via `read_aiger`) are generated reproducibly by [`src/xcnf2cnf_aig.py`](src/xcnf2cnf_aig.py):

| Instance | Status | XCNF Vars / CNF + XOR Clauses | `.xcnf.xz` Size | Tseitin CNF Vars / Clauses | `.cnf.xz` Size | AIG PIs / AND Gates | `.aig.xz` Size |
|---|:---:|---:|---:|---:|---:|---:|---:|
| `w5.solved` | SAT *(known unique)* | 59,324 / 123,012 + 42,812 | 489.2 KB | 119,644 / 811,268 | 1.93 MB | 256 / 460,695 | 457.1 KB |
| `w126.unsolved` | Open *(expected unique SAT)* | 59,324 / 123,012 + 42,812 | 489.2 KB | 119,644 / 811,268 | 1.89 MB | 256 / 460,647 | 457.5 KB |

## Comparative 1-Core Benchmark Results ($T_{\max} = 30\;\text{s}$)

- **Hardware & Protocol:** Same machine (**AMD Ryzen 9 5950X**, Linux, 1 core pinned per run via `taskset -c 0`, sequential execution, $T_{\max} = 30\;\text{s}$).
- **Result:** All five solvers time out (`T/O`) on both instances — as expected for full 14-round AES-256 without key-weight side information. Because every solver remains inside the exponential search tree at 30 s, we report exact single-core search throughput (`conflicts/sec` and `propagations/sec`):

| Solver & Format (1C, $T_{\max} = 30\;\text{s}$) | `w5.solved` Verdict | `w5.solved` Conflicts (Rate) | `w5.solved` Propagations (Rate) | `w126.unsolved` Verdict | `w126.unsolved` Conflicts (Rate) | `w126.unsolved` Propagations (Rate) |
|---|:---:|---:|---:|:---:|---:|---:|
| **Frobenius 1C (`.aig`)** | T/O | **1,606,528 (53,369/s)** | 144.1M (4.79M/s) | T/O | **1,498,176 (49,508/s)** | 197.4M (6.52M/s) |
| **Frobenius 1C (`.xcnf`)** | T/O | **1,221,568 (40,531/s)** | **245.9M (8.16M/s)** | T/O | **1,172,096 (38,917/s)** | **208.7M (6.93M/s)** |
| [Kissat](https://github.com/arminbiere/kissat) 4.0.4 (`.cnf`) | T/O | 376,058 (12,525/s) | 115.7M (3.85M/s) | T/O | 379,192 (12,606/s) | 117.0M (3.89M/s) |
| [CaDiCaL](https://github.com/arminbiere/cadical) 3.1.0 (`.cnf`) | T/O | 193,256 (6,385/s) | 39.6M (1.31M/s) | T/O | 189,394 (6,300/s) | 82.8M (2.75M/s) |
| [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18.0 (`.cnf`) | T/O | 48,128 (1,609/s) | — | T/O | 55,809 (1,867/s) | — |
| Frobenius 1C (`.cnf`) | T/O | 7,552 (250/s) | 106.5M (3.52M/s) | T/O | 7,744 (252/s) | 111.9M (3.64M/s) |
| [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18.0 (`.xcnf`) | T/O | 2,561 (74.8/s)\* | — | T/O | —\* | — |
| [`dense-solver 0.0.4`](https://github.com/libdense/dense-solver) (`.cnf`) | T/O | — | — | T/O | — | — |

*\*On native `.xcnf`, CryptoMiniSat 5.18.0 spends $>16\text{--}50\;\text{s}$ initializing dense $\mathbb{F}_2$ Gaussian elimination over the $42{,}524 \times 58{,}524$ connected XOR system (`w126.unsolved.xcnf` did not exit Gauss initialization before the 50 s hard watchdog).*

<!-- BEGIN_STRUCTURAL_ANALYSIS -->
## Phase-Transition & Structural Analysis

*Auto-generated by [`../src/analyze_benchmarks.py`](../src/analyze_benchmarks.py). Position relative to the critical phase transition is measured by $\rho_{\mathrm{crit}} = \frac{1}{n}\sum_k m_k / \alpha_c(k)$ (exact $\alpha/\alpha_c(k)$ for pure $k$-SAT; effective critical threshold $\alpha_c^{\mathrm{eff}} = \alpha/\rho_{\mathrm{crit}}$; `Under` $<0.90\times$, `Near-crit` $0.90\text{--}1.10\times$, `Over` $>1.10\times$), alongside Gent–Walsh annealed constrainedness $\kappa = -\frac{1}{n}\sum_i \log_2(1-2^{-k_i})$ (AAAI 1996), clause-length profile ($\bar{k}$, `%Bin`, `%Horn`), variable-degree CV ($\sigma_d/\bar{d}$, uniformity vs. hub skew), and extracted native XOR parity clauses.*

| Instance | Active $n$ | Clauses $m$ | $\alpha=m/n$ | $\alpha_c^{\mathrm{eff}}$ | $\rho_{\mathrm{crit}}$ (Regime) | $\kappa$ | $\bar{k}$ ($k_{\max}$) | Bin% | Horn% | Pos% | Deg CV | XORs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `w126.unsolved` | 119,644 | 811,268 | 6.78 | 3.85 | **1.76x** (Over) | 1.08 | 3.53 (4) | 15% | 54% | 48% | 1.14 | 42,812 |
| `w5.solved` | 119,644 | 811,268 | 6.78 | 3.85 | **1.76x** (Over) | 1.08 | 3.53 (4) | 15% | 54% | 48% | 1.14 | 42,812 |

**Suite Phase-Transition Summary (2 instances):** median $\rho_{\mathrm{crit}} = 1.76\times$ (range `1.76x–1.76x`), median $\kappa = 1.08$, regime split **0 Under / 0 Near-critical / 2 Over**, total extracted native XOR parity clauses = **85,624**.
<!-- END_STRUCTURAL_ANALYSIS -->
