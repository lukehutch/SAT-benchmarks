# Synthetic NIST FIPS 197 AES-256 Key-Recovery & Hash-Preimage Circuits (`aes256-key-recovery`)

![NIST FIPS 197 AES-256 SPN round, Boyar-Peralta S-box, Davies-Meyer equivalence, and graduated (R, k) difficulty ladder](diagram.svg)

*Figure: Clean-room NIST FIPS 197 AES-256 SPN round datapath, Boyar–Peralta (SEA 2010) 32-AND / 81-XOR-XNOR S-box decomposition, algebraic equivalence to fixed-IV Davies–Meyer AES-256 hash preimage, transparent deterministic SHA-256 key/plaintext provenance, and the 10-instance graduated $(R, k)$ difficulty ladder. Regenerated via [`src/gen_diagram.py`](src/gen_diagram.py).*

## Provenance & Credit

- **Author:** Luke Hutchison ([`lukehutch`](https://github.com/lukehutch))
- **License:** MIT License ([`../LICENSE`](../LICENSE))
- **Upstream Standards & Circuit Reference:** [NIST FIPS PUB 197](https://csrc.nist.gov/publications/detail/fips/197/final) (Advanced Encryption Standard, AES-256) and Boyar & Peralta (SEA 2010, Table 1) combinational AES S-box minimization.

## Problem Description

A 100% original, transparent, reproducible suite of synthetic **NIST FIPS 197 AES-256** key-recovery and **Davies–Meyer AES-256 hash-preimage** circuits spanning five calibrated difficulty tiers from trivial 1-round S-box inversion through full-diffusion reduced-round instances and full 14-round AES-256 partial-key recovery to a full 256-bit dual-plaintext cryptographic challenge.

- **Exact NIST FIPS 197 AES-256 & Davies–Meyer Equivalence:** For $R \in \lbrace 1, \dots, 14\rbrace$ rounds, rounds $1 \dots R-1$ apply `SubBytes`, `ShiftRows`, `MixColumns` over $\mathrm{GF}(2^8) = \mathbb{F}_2[x]/(x^8+x^4+x^3+x+1)$, and `AddRoundKey`, while final round $R$ omits `MixColumns` per standard FIPS 197 convention so $R = 14$ matches FIPS 197 byte-for-byte. Under fixed-IV **Davies–Meyer** compression $H = \mathrm{AES\text{-}256}(K, P) \oplus P$, finding a preimage key/message block $K$ for target digest $H$ and fixed chaining value $P$ is bit-for-bit identical to known-plaintext key recovery $\mathrm{AES\text{-}256}(K, P) = C$ with $C = H \oplus P$. Both the byte-level reference and the gate-level Boolean circuit are self-verified against `AES-256(0, 0) = dc95c078a2408989ad48a21492842087` and **FIPS 197 Appendix C.3** (`K = 000102...1f`, `P = 001122...ff` $\to$ `C = 8ea2b7ca516745bfeafc49904b496089`) on 128/128 bits, and against each other across all $R \in \lbrace 1, \dots, 14\rbrace$.
- **Clean-Room Boyar–Peralta S-Box & Factored $\mathbb{F}_2$-Linear Layers:** Each AES S-box uses the published **Boyar–Peralta (SEA 2010, Table 1)** combinational decomposition (**32 AND gates + 81 XOR/XNOR gates = 113 gates**, verified 256/256 against the FIPS 197 S-box). `MixColumns` is factored via $d_j = a_j \oplus a_{(j+1)\bmod 4}$ and $b_j = \mathrm{xtime}(d_j) \oplus a_{(j+1)\bmod 4} \oplus d_{(j+2)\bmod 4}$ so every XOR parity gate across the entire circuit has arity 2 or 3 (maximum native XCNF/CNF width 4, requiring zero auxiliary CNF variables during XOR expansion).
- **Transparent Deterministic Synthetic Provenance:** Every instance derives its 32-byte synthetic key $K$ and 16-byte plaintext(s) $P_1$ (and $P_2$ for the dual-block miter) deterministically from $\mathrm{SHA\text{-}256}(\texttt{"frobenius-aes256-benchmark-v1:}\langle\text{name}\rangle\texttt{:}\langle\text{role}\rangle\texttt{"})$ (`role` $\in \lbrace \text{"key"}, \text{"plaintext1"}, \text{"plaintext2"}\rbrace$). Variables `1..256` represent the 256 key bits in LSB-first byte order (`var = 1 + 8*byte + bit`); bits `0..k-1` are left free while bits `k..255` are fixed to their synthetic values via unit clauses.
- **Mathematically Verified Ground Truth (`8 SAT / 2 UNSAT`):** Every SAT instance's synthetic witness is verified directly against 100% of clauses/equations/gates in all four re-parsed compressed formats (and uniquely verified over $2^k$ for $k \le 12$). Both UNSAT instances (`aes256_r04_k12_unsat`, `aes256_r14_k12_unsat`) flip bit 0 of ciphertext byte 0 (`C[0] ^= 0x01`) and are **exhaustively proven UNSAT** across all $2^{12} = 4{,}096$ keys in Python.

## Corpus & Data Sizes

### Directory Layout & Regeneration

- `xcnf-orig/` — Native **[CryptoMiniSat](https://github.com/msoos/cryptominisat) `.xcnf.xz`** circuits (`853.7 KB`, native `x l1 ... lk 0` parity clauses + 3-clause Tseitin AND gates).
- `cnf-converted/` — Exact Tseitin **DIMACS `.cnf.xz`** conversions (`2.12 MB`, zero auxiliary variables; max clause width 4).
- `aig-converted/` — Combinational **Binary AIGER 1.9 `.aig.xz`** miters (`103.0 KB`, `L = 0, O = 1`, `I = k` free key bits with fixed key bits constant-folded, `PO_0 = 1` iff SAT; independently parsed and witness-simulated across all 10 files plus Frobenius native `.aig.xz` parser checks).
- `anf-converted/` — Lossless linear-size **DIMACS-ANF `.anf.xz`** conversions (`884.7 KB`, degree $\le 3$, generated and verified via [`../src/to_anf.py`](../src/to_anf.py)).
- **[`expected.tsv`](expected.tsv)** — Ground-truth verdict manifest for all 10 instances (**8 SAT / 2 UNSAT**).
- `src/` — Standalone zero-dependency clean-room generator [`src/gen_aes256.py`](src/gen_aes256.py) (`python3 src/gen_aes256.py`) and vector diagram script [`src/gen_diagram.py`](src/gen_diagram.py).

### Problem Parameters & Data Sizes

| Instance | Rounds $R$ | Free Bits $k$ | Pairs | Ans | Vars | CNF Clauses | Native XORs | AIG ANDs | `.xcnf.xz` | `.cnf.xz` | `.aig.xz` | `.anf.xz` |
|---|---:|---:|---:|:---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `aes256_r01_k128_sat` | 1 | 128 | 1 | SAT | 2,192 | 7,488 | 1,424 | 4,495 | 9.7 KB | 20.4 KB | 2.0 KB | 10.4 KB |
| `aes256_r02_k16_sat` | 2 | 16 | 1 | SAT | 5,012 | 18,752 | 3,604 | 2,949 | 20.7 KB | 47.5 KB | 1.9 KB | 22.2 KB |
| `aes256_r02_k32_sat` | 2 | 32 | 1 | SAT | 5,012 | 18,736 | 3,604 | 6,064 | 20.5 KB | 47.7 KB | 3.5 KB | 22.2 KB |
| `aes256_r03_k16_sat` | 3 | 16 | 1 | SAT | 7,832 | 29,904 | 5,784 | 8,751 | 31.0 KB | 74.7 KB | 4.5 KB | 33.0 KB |
| `aes256_r04_k12_sat` | 4 | 12 | 1 | SAT *(unique)* | 10,652 | 41,060 | 7,964 | 15,148 | 41.6 KB | 100.1 KB | 7.3 KB | 45.3 KB |
| `aes256_r04_k12_unsat` | 4 | 12 | 1 | UNSAT *(proved)* | 10,652 | 41,060 | 7,964 | 15,140 | 41.8 KB | 102.7 KB | 7.5 KB | 45.1 KB |
| `aes256_r14_k10_sat` | 14 | 10 | 1 | SAT *(unique)* | 38,852 | 152,582 | 29,764 | 87,439 | 144.6 KB | 370.4 KB | 19.5 KB | 148.8 KB |
| `aes256_r14_k12_sat` | 14 | 12 | 1 | SAT *(unique)* | 38,852 | 152,580 | 29,764 | 87,635 | 140.1 KB | 372.4 KB | 19.7 KB | 147.8 KB |
| `aes256_r14_k12_unsat` | 14 | 12 | 1 | UNSAT *(proved)* | 38,852 | 152,580 | 29,764 | 87,651 | 153.2 KB | 365.8 KB | 19.3 KB | 147.6 KB |
| `aes256_r14_k256_dual_sat` | 14 | 256 | 2 | SAT | 69,908 | 276,176 | 53,652 | 186,077 | 250.6 KB | 669.4 KB | 17.8 KB | 262.2 KB |

### Deterministic Synthetic Vectors

Every key $K$ and plaintext $P$ below is generated solely by $\mathrm{SHA\text{-}256}(\texttt{"frobenius-aes256-benchmark-v1:}\langle\text{instance}\rangle\texttt{:}\langle\text{role}\rangle\texttt{"})$ (truncating to 16 bytes for plaintexts) with zero external or secret data:

| Instance | Plaintext $P_1$ (hex) | Target Ciphertext $C_1$ (hex) | Davies–Meyer Target $H_1 = C_1 \oplus P_1$ (hex) |
|---|---|---|---|
| `aes256_r01_k128_sat` | `40b0c8b82745f45b12e01c7ca5c3548c` | `fef2a145e85f53cbb7ee31afd60071ff` | `be4269fdcf1aa790a50e2dd373c32573` |
| `aes256_r02_k16_sat` | `4745caffec7cfb8ae9215233e513664f` | `79cdd60025c3b29a8a9cd1e31aa07afc` | `3e881cffc9bf491063bd83d0ffb31cb3` |
| `aes256_r02_k32_sat` | `464de296da7ac07dff3cd2a7f9d6467c` | `af7258e417fc6c5d72934bb9fc69ce14` | `e93fba72cd86ac208daf991e05bf8868` |
| `aes256_r03_k16_sat` | `b8fc7df30471ef78230f4133c8045d59` | `c640c77956a883979b5b5f7b09e11030` | `7ebcba8a52d96cefb8541e48c1e54d69` |
| `aes256_r04_k12_sat` | `7e41b425620ec62a117bd6150e628d80` | `07a2ed35ebb77855779f930c578a306b` | `79e3591089b9be7f66e4451959e8bdeb` |
| `aes256_r04_k12_unsat` | `6b7d640988303de8a5ca07dfb1024a29` | `95e44b7ce06e713ca88df09bd3144a2f` *(bit 0 flipped)* | `fe992f75685e4cd40d47f74462160006` |
| `aes256_r14_k10_sat` | `6e5afa773f9603e9334ac56dfe8c1358` | `6900bc31f7135ac41f79569a23036e38` | `075a4646c885592d2c3393f7dd8f7d60` |
| `aes256_r14_k12_sat` | `2c59620c18955595bf622215bcb14dff` | `49927945fe924fe337988fb5ae48fb9b` | `65cb1b49e6071a7688faada012f9b664` |
| `aes256_r14_k12_unsat` | `bea241460daa55ab160d75fc6e76d057` | `6c6c4d224f032d43dbb701cc72a24faf` *(bit 0 flipped)* | `d2ce0c6442a978e8cdba74301cd49ff8` |
| `aes256_r14_k256_dual_sat` | `7e4baee5d39a09cdeef674f31747ea8a` *(P2: `647c75927a5f1485ba2e380338e8ac78`)* | `790284c2d41a1c40e5dbdaecda1af724` *(C2: `02517ef512c4aee57a3752eb826eaebd`)* | `07492a270780158d0b2dae1fcd5d1dae` |

## Benchmark Results

- **Hardware & Protocol:** Same machine — **AMD Ryzen 9 5950X** (16C/32T Linux x86_64), 1 core pinned per run (`taskset -c 8`), uncompressed identical inputs, default single-thread flags (`--max-cores 1` for Frobenius, `-t 1` for CryptoMiniSat 5.18.0), exact median of 3 runs for solves `< 5 s`, $T_{\max} = 60\text{ s}$ (PAR-2 penalty $120\text{ s}$) across the 9 solvable partial-key / reduced-round instances, plus a $T_{\max} = 30\text{ s}$ search-throughput stress test on `aes256_r14_k256_dual_sat`.
- **Independent Verification:** **100% raw-CNF SAT witness verification (`55 / 55` PASS)** across all solver configurations and **0 verdict disagreements** against [`expected.tsv`](expected.tsv). Both UNSAT instances are exhaustively refuted over all $2^{12} = 4{,}096$ keys in Python, and `aes256_r04_k12_unsat` was externally triple-certified (`512.0 MiB` LRAT proof verified by [`lrat-check`](https://github.com/marijnheule/drat-trim) in `5.95 s`, formally verified [`cake_lpr`](https://github.com/tanyongkiam/cake_lpr) `s VERIFIED UNSAT`, and Frobenius `--check-proof` in `2.01 s`).

### 1. Solvable Partial-Key & Reduced-Round Ladder (9 Instances, $T_{\max} = 60\text{ s}$)

| Instance | Ans | Frobenius 1C (.cnf) | Frobenius 1C (.xcnf) | Frobenius 1C (.aig) | [CaDiCaL](https://github.com/arminbiere/cadical) 3.1.0 (.cnf) | [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18.0 (.cnf) | [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18.0 (.xcnf) | [dense-solver](https://github.com/libdense/dense-solver) 0.0.4 (.cnf) | [Kissat](https://github.com/arminbiere/kissat) 4.0.4 (.cnf) |
|---|:---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `aes256_r01_k128_sat` | SAT | 19.46 ms | 15.05 ms | **8.30 ms** | 9.90 ms | 133.76 ms | 36.28 ms | 10.61 ms | 36.21 ms |
| `aes256_r02_k16_sat` | SAT | 2.32 ms | 3.62 ms | **1.17 ms** | 5.24 ms | 10.84 ms | 8.62 ms | 12.38 ms | 5.75 ms |
| `aes256_r02_k32_sat` | SAT | 44.93 ms | 41.80 ms | 18.37 ms | **11.75 ms** | 200.08 ms | 59.25 ms | 18.77 ms | 51.22 ms |
| `aes256_r03_k16_sat` | SAT | 237.74 ms | 232.64 ms | **2.59 ms** | 67.85 ms | 299.20 ms | 64.96 ms | 55.21 ms | 136.24 ms |
| `aes256_r04_k12_sat` | SAT | 69.33 ms | 61.76 ms | **2.75 ms** | 1,195.96 ms | 844.85 ms | 1,524.89 ms | 348.70 ms | 1,159.26 ms |
| `aes256_r04_k12_unsat` | UNSAT | 2,202.92 ms | 2,195.37 ms | **2.57 ms** | 2,494.03 ms | 2,954.34 ms | 2,313.22 ms | 3,529.67 ms | 6,504.89 ms |
| `aes256_r14_k10_sat` | SAT | 494.96 ms | 1,160.24 ms | **11.18 ms** | 2,607.10 ms | 12,719.98 ms | 33,262.83 ms | 1,552.64 ms | 1,740.19 ms |
| `aes256_r14_k12_sat` | SAT | 1,008.79 ms | 248.67 ms | **11.89 ms** | 1,542.82 ms | 13,600.43 ms | >60 s *(T/O)* | 7,629.73 ms | 1,518.84 ms |
| `aes256_r14_k12_unsat` | UNSAT | 9,627.57 ms | 8,498.91 ms | **11.08 ms** | 13,590.49 ms | 45,678.79 ms | >60 s *(T/O)* | 20,395.81 ms | 10,205.96 ms |
| **Solved ($T_{\max} = 60\text{ s}$)** | — | **9 / 9** *(highest)* | **9 / 9** *(highest)* | **9 / 9** *(highest)* | **9 / 9** *(highest)* | **9 / 9** *(highest)* | 7 / 9 *(-2 worse)* | **9 / 9** *(highest)* | **9 / 9** *(highest)* |
| **Total PAR-2** | — | 13,708.02 ms *(196.11x slower)* | 12,458.06 ms *(178.23x slower)* | **69.90 ms** *(fastest)* | 21,525.14 ms *(307.94x slower)* | 76,442.27 ms *(1,093.59x slower)* | 277,270.05 ms *(3,966.67x slower)* | 33,553.52 ms *(480.02x slower)* | 21,358.56 ms *(305.56x slower)* |

- **Format-matched comparisons:** On identical flat `.cnf` inputs, Frobenius 1C (`13,708.02 ms`) is **`1.56x` faster** than Kissat 4.0.4 (`21,358.56 ms`), **`1.57x` faster** than CaDiCaL 3.1.0 (`21,525.14 ms`), **`2.45x` faster** than dense-solver 0.0.4 (`33,553.52 ms`), and **`5.58x` faster** than CryptoMiniSat 5.18.0 (`76,442.27 ms`). On native `.xcnf` inputs, Frobenius 1C (`12,458.06 ms`) is **`1.71x` faster** than Kissat 4.0.4 (`.cnf`), **`1.73x` faster** than CaDiCaL 3.1.0 (`.cnf`), and **`22.26x` faster** than CryptoMiniSat 5.18.0 (`.xcnf`). On native Binary AIGER `.aig` miters, Frobenius 1C solves all `9 / 9` instances in **`69.90 ms`** (**`305.56x` faster** than Kissat 4.0.4 `.cnf`).

### 2. Full 14-Round 256-Bit Dual-Plaintext Stress Test (`aes256_r14_k256_dual_sat`, $T_{\max} = 30\text{ s}$)

| Metric (30 s, 1C) | Frobenius 1C (.cnf) | Frobenius 1C (.xcnf) | Frobenius 1C (.aig) | [CaDiCaL](https://github.com/arminbiere/cadical) 3.1.0 (.cnf) | [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18.0 (.cnf) | [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18.0 (.xcnf)\* | [dense-solver](https://github.com/libdense/dense-solver) 0.0.4 (.cnf)† | [Kissat](https://github.com/arminbiere/kissat) 4.0.4 (.cnf) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **Verdict** | T/O | T/O | T/O | T/O | T/O | T/O | UNKNOWN | T/O |
| **Conflicts** | 5,824 | 762,368 | 14,336 | 59,991 | 10,495 | — | 5,000 | 1,206,991 |
| **Conflicts/s** | 193.75 / s | 25,340.77 / s | 473.20 / s | 1,998.33 / s | 342.90 / s | — | 162.57 / s | 40,220.76 / s |
| **Propagations** | 184,046,964 | 210,337,031 | 354,807,985 | 162,259,815 | ~44,000,000 | — | 174,803,126 | 114,421,785 |
| **Propagations/s** | 6.12M / s | 6.99M / s | 11.71M / s | 5.40M / s | 1.44M / s | — | 5.68M / s | 3.81M / s |

*\*CryptoMiniSat 5.18.0 (.xcnf) hit the 35 s external watchdog (`35.06 s` wall) during Gaussian-elimination initialization before emitting search statistics.*
*†dense-solver 0.0.4 has no `--time` flag or SIGINT statistics handler; throughput was measured via `--explain --conflicts 5000` (`30.76 s` wall).*

<!-- BEGIN_STRUCTURAL_ANALYSIS -->
## Phase-Transition & Structural Analysis

*Auto-generated by [`../src/analyze_benchmarks.py`](../src/analyze_benchmarks.py). Position relative to the critical phase transition is measured by $\rho_{\mathrm{crit}} = \frac{1}{n}\sum_k m_k / \alpha_c(k)$ (exact $\alpha/\alpha_c(k)$ for pure $k$-SAT; effective critical threshold $\alpha_c^{\mathrm{eff}} = \alpha/\rho_{\mathrm{crit}}$; `Under` $<0.90\times$, `Near-crit` $0.90\text{--}1.10\times$, `Over` $>1.10\times$), alongside Gent–Walsh annealed constrainedness $\kappa = -\frac{1}{n}\sum_i \log_2(1-2^{-k_i})$ (AAAI 1996), clause-length profile ($\bar{k}$, `%Bin`, `%Horn`), variable-degree CV ($\sigma_d/\bar{d}$, uniformity vs. hub skew), and extracted native XOR parity clauses.*

| Instance | Active $n$ | Clauses $m$ | $\alpha=m/n$ | $\alpha_c^{\mathrm{eff}}$ | $\rho_{\mathrm{crit}}$ (Regime) | $\kappa$ | $\bar{k}$ ($k_{\max}$) | Bin% | Horn% | Pos% | Deg CV | XORs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `aes256_r01_k128_sat` | 2,192 | 7,488 | 3.42 | 2.74 | **1.25x** (Over) | 0.86 | 2.79 (3) | 14% | 48% | 49% | 0.41 | 1,424 |
| `aes256_r02_k16_sat` | 5,012 | 18,752 | 3.74 | 2.97 | **1.26x** (Over) | 0.86 | 2.89 (4) | 12% | 45% | 49% | 0.42 | 3,604 |
| `aes256_r02_k32_sat` | 5,012 | 18,736 | 3.74 | 2.98 | **1.25x** (Over) | 0.86 | 2.89 (4) | 12% | 44% | 49% | 0.42 | 3,604 |
| `aes256_r03_k16_sat` | 7,832 | 29,904 | 3.82 | 3.06 | **1.25x** (Over) | 0.85 | 2.92 (4) | 12% | 43% | 49% | 0.41 | 5,784 |
| `aes256_r04_k12_sat` | 10,652 | 41,060 | 3.85 | 3.11 | **1.24x** (Over) | 0.84 | 2.94 (4) | 12% | 43% | 49% | 0.41 | 7,964 |
| `aes256_r04_k12_unsat` | 10,652 | 41,060 | 3.85 | 3.11 | **1.24x** (Over) | 0.84 | 2.94 (4) | 12% | 43% | 49% | 0.41 | 7,964 |
| `aes256_r14_k10_sat` | 38,852 | 152,582 | 3.93 | 3.19 | **1.23x** (Over) | 0.83 | 2.97 (4) | 12% | 42% | 49% | 0.42 | 29,764 |
| `aes256_r14_k12_sat` | 38,852 | 152,580 | 3.93 | 3.19 | **1.23x** (Over) | 0.83 | 2.97 (4) | 12% | 42% | 49% | 0.42 | 29,764 |
| `aes256_r14_k12_unsat` | 38,852 | 152,580 | 3.93 | 3.19 | **1.23x** (Over) | 0.83 | 2.97 (4) | 12% | 42% | 49% | 0.42 | 29,764 |
| `aes256_r14_k256_dual_sat` | 69,908 | 276,176 | 3.95 | 3.22 | **1.23x** (Over) | 0.83 | 2.98 (4) | 12% | 42% | 49% | 0.43 | 53,652 |

**Collection Phase-Transition Summary (10 instances, 4 formats: 10 CNF / 10 AIG / 10 XCNF / 10 ANF):** median $\rho_{\mathrm{crit}} = 1.24\times$ (range `1.23x–1.26x`), median $\kappa = 0.84$, regime split **0 Under / 0 Near-critical / 10 Over**, total extracted native XOR parity clauses = **173,288**, total ANF equations = **332,654**.
<!-- END_STRUCTURAL_ANALYSIS -->

## References

- NIST, *Advanced Encryption Standard (AES)*, FIPS PUB 197, November 2001 (updated May 2023).
- J. Boyar and R. Peralta, *A New Combinational Logic Minimization Technique with Applications to Cryptology*, SEA 2010, LNCS 6049, pp. 178–189.
- N. Courtois and G. V. Bard, *Algebraic Cryptanalysis of the Data Encryption Standard*, Cryptography and Coding (IMA 2007), LNCS 4887, pp. 152–169.
- M. Soos, K. Nohl, and C. Castelluccia, *Extending SAT Solvers to Cryptographic Problems*, SAT 2009, LNCS 5584, pp. 244–257.
- A. Menezes, P. van Oorschot, and S. Vanstone, *Handbook of Applied Cryptography*, Section 9.4.1 (Davies–Meyer hash construction), CRC Press, 1996.
