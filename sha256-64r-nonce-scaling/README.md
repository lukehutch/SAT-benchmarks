# FIPS 180-4 SHA-256 64-Round Nonce-Scaling Benchmark (`sha256-64r-nonce-scaling`)

![FIPS 180-4 64-round SHA-256 single-core nonce-scaling curves across 7 solver tracks](diagram.svg)

*Figure: Single-core wall-clock runtime $T(k)$ (log scale) across $k = 1\dots 32$ unknown LSBs of nonce word $W_0 = \texttt{0x9E3779B9}$ on full 64-round FIPS 180-4 SHA-256 ($T_{\max} = 300\;\text{s}$, AMD Ryzen 9 5950X core 12, 290/290 SAT models verified), showing all 7 tracks (5 engines), shifted pure-exponential M1 fits, and Frobenius's cliff-free piecewise regimes (`Stage 0C` $\to$ `Stage 0F` 2048-lane early-exit `CompiledAig256` $\to$ shortcut-first probe + 2048-lane escalation solving **all 32 / 32** instances inside 300 s). Regenerated via [`src/gen_diagram.py`](src/gen_diagram.py).*

## Provenance & Credit

- **Author:** Luke Hutchison ([`lukehutch`](https://github.com/lukehutch))
- **License:** MIT License ([`../LICENSE`](../LICENSE))
- **Upstream Standard & Generator Lineage:** Implements [NIST FIPS PUB 180-4](https://csrc.nist.gov/publications/detail/fips/180/4/final) (full 64-round SHA-256 compression with feed-forward) using the same zero-dependency Carry-Save-Adder (CSA) AIG compiler architecture as [`../sha256-preimage/`](../sha256-preimage/README.md).

## Problem Description

A controlled, **zero-lucky-hit-bias** 32-instance scaling ladder sweeping $k = 1, 2, \dots, 32$ unknown nonce bits of full **64-round NIST FIPS 180-4 SHA-256** (with standard feed-forward addition $H_0 \boxplus \text{state}_{64}$) designed specifically to measure exact asymptotic scaling exponents $\alpha$ (in $T(k) = c_0 + a \cdot 2^{\alpha k}$) and statistically test whether modern CDCL, XOR-Gauss, or circuit-native SIMD solvers exhibit pure exponential ($2^{\alpha k}$) or sub-exponential scaling on full-round cryptographic hash inversion.

- **Exact Zero-Bias Instance Specification:** Starting from the padded 512-bit single-block message `pad_single_block(b"SAT-Benchmarks-SHA256-64R-Nonce-Scaling-v1")`, message word $W_0$ is fixed to the classic nothing-up-my-sleeve golden-ratio constant `0x9E3779B9` ($\lfloor 2^{32} / \phi \rfloor$). Its balanced `20 / 32` popcount and LSB binary prefix `10011101...` anchor its bit-reversed lexicographic sweep fraction cleanly at $\approx 0.616$ for every $k \ge 3$, eliminating trailing-zero lucky-hit bias across all sweep bit widths.
- **Exact FIPS 180-4 Digest (Independently Verified via Python `hashlib.sha256`):**
  - Target 256-bit digest: `e43badc81a63e2304f9241f32ba294e7d1e6c082b7f8e41348fe911a17b3321e`
  - For each $k \in \{1, \dots, 32\}$, instance `sha256_64r_k{k:02d}` frees the lowest $k$ bits of $W_0$ (`free = 0..k`) and fixes all other $512 - k$ block bits to their constant values. Every instance is provably **SAT** with verified preimage `W[0] = 0x9E3779B9`.
- **Symbolic Collapse at $k = 1$ vs. Full Circuit at $k \ge 2$:** With only $k = 1$ free bit $x_0$, the set of 1-variable Boolean functions $\{0, 1, x_0, \neg x_0\}$ is closed under `AND`, `XOR`, `Maj3`, and `Mux`, so hash-consed structural simplification collapses the entire 64-round circuit algebraically to `x_0 = 1` (`0` AIG AND gates, `116` unit clauses for the 116 digest bits sensitive to bit 0). From $k = 2$ onward, nonlinear cross-terms break closure immediately, yielding the full 64-round CSA circuit (`177,908`–`185,629` AIG ANDs, `42,636`–`44,127` CNF variables, `271,953`–`283,105` clauses).

## Corpus & Data Sizes

### Directory Layout & Regeneration

- `aig-orig/` — Original native **Binary AIGER 1.9** miters (`5.84 MB`, 32 `.aig.xz` files, all 32 independently forward-simulated and bit-0 flip checked).
- `cnf-converted/` — Tseitin **DIMACS `.cnf.xz`** conversions (`19.64 MB`, 32 files, max file `658.5 KB`).
- `xcnf-converted/` — Native-XOR **[CryptoMiniSat](https://github.com/msoos/cryptominisat) `.xcnf.xz`** conversions (`11.24 MB`, 32 files, `720,860` total native XOR parity clauses).
- `anf-converted/` — Lossless linear-size **DIMACS-ANF `.anf.xz`** conversions (`13.93 MB`, degree $\le 2$, `2,874,038` total ANF equations, generated and 64-vector verified via [`../src/to_anf.py`](../src/to_anf.py)).
- **[`expected.tsv`](expected.tsv)** — Ground-truth verdict manifest for all 32 instances (**32 SAT / 0 UNSAT**).
- `src/` — Standalone zero-dependency Rust generator crate (`cd src && cargo run --release`) and reproducible scaling plot generator [`src/gen_diagram.py`](src/gen_diagram.py).

### Problem Parameters & Data Sizes (32 Instances)

| Instance | Free Bits $k$ | Ans | AIG ANDs | `.aig.xz` | CNF Vars | CNF Clauses | `.cnf.xz` | Native XORs | `.xcnf.xz` | ANF Eqs | `.anf.xz` |
|---|---:|:---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `sha256_64r_k01` *(0-AND collapse)* | 1 | SAT | 0 | 0.2 KB | 1 | 116 | 0.1 KB | 0 | 0.1 KB | 1 | 0.2 KB |
| `sha256_64r_k02` | 2 | SAT | 177,908 | 190.2 KB | 42,636 | 271,953 | 629.4 KB | 22,614 | 363.0 KB | 90,318 | 451.8 KB |
| `sha256_64r_k03` | 3 | SAT | 178,564 | 191.4 KB | 42,812 | 272,928 | 635.6 KB | 22,717 | 364.6 KB | 90,631 | 451.8 KB |
| `sha256_64r_k04` | 4 | SAT | 179,405 | 191.2 KB | 42,941 | 273,777 | 635.8 KB | 22,774 | 365.2 KB | 90,928 | 448.4 KB |
| `sha256_64r_k05` | 5 | SAT | 179,636 | 191.4 KB | 43,033 | 274,536 | 635.0 KB | 22,835 | 367.6 KB | 91,171 | 455.8 KB |
| `sha256_64r_k06` | 6 | SAT | 180,265 | 193.6 KB | 43,166 | 275,483 | 640.6 KB | 22,911 | 366.9 KB | 91,466 | 453.2 KB |
| `sha256_64r_k07` | 7 | SAT | 180,405 | 191.8 KB | 43,217 | 275,961 | 638.6 KB | 22,946 | 366.8 KB | 91,634 | 455.5 KB |
| `sha256_64r_k08` | 8 | SAT | 182,052 | 193.2 KB | 43,388 | 277,592 | 645.0 KB | 23,065 | 369.6 KB | 92,104 | 454.6 KB |
| `sha256_64r_k09` | 9 | SAT | 181,985 | 192.2 KB | 43,432 | 277,999 | 647.5 KB | 23,089 | 370.8 KB | 92,273 | 456.0 KB |
| `sha256_64r_k10` | 10 | SAT | 182,386 | 193.3 KB | 43,508 | 278,386 | 648.4 KB | 23,136 | 369.6 KB | 92,389 | 459.4 KB |
| `sha256_64r_k11` | 11 | SAT | 182,361 | 192.0 KB | 43,514 | 278,408 | 645.1 KB | 23,139 | 370.7 KB | 92,394 | 455.1 KB |
| `sha256_64r_k12` | 12 | SAT | 182,836 | 193.9 KB | 43,603 | 279,070 | 650.4 KB | 23,201 | 370.7 KB | 92,580 | 458.6 KB |
| `sha256_64r_k13` | 13 | SAT | 183,558 | 192.2 KB | 43,703 | 280,099 | 654.9 KB | 23,269 | 372.4 KB | 92,859 | 467.1 KB |
| `sha256_64r_k14` | 14 | SAT | 183,683 | 192.7 KB | 43,729 | 280,213 | 647.2 KB | 23,285 | 371.8 KB | 92,897 | 459.8 KB |
| `sha256_64r_k15` | 15 | SAT | 183,825 | 193.2 KB | 43,755 | 280,319 | 644.1 KB | 23,301 | 372.8 KB | 92,930 | 459.5 KB |
| `sha256_64r_k16` | 16 | SAT | 183,893 | 193.1 KB | 43,774 | 280,412 | 652.5 KB | 23,315 | 372.2 KB | 92,954 | 460.9 KB |
| `sha256_64r_k17` | 17 | SAT | 183,722 | 192.7 KB | 43,802 | 280,542 | 651.4 KB | 23,334 | 372.0 KB | 92,991 | 459.7 KB |
| `sha256_64r_k18` | 18 | SAT | 183,821 | 192.6 KB | 43,839 | 280,769 | 652.7 KB | 23,356 | 373.2 KB | 93,052 | 460.7 KB |
| `sha256_64r_k19` | 19 | SAT | 184,504 | 194.1 KB | 43,896 | 281,222 | 652.1 KB | 23,394 | 372.9 KB | 93,176 | 461.8 KB |
| `sha256_64r_k20` | 20 | SAT | 184,622 | 193.1 KB | 43,913 | 281,342 | 651.8 KB | 23,402 | 372.3 KB | 93,212 | 457.1 KB |
| `sha256_64r_k21` | 21 | SAT | 184,774 | 193.9 KB | 43,939 | 281,511 | 651.9 KB | 23,418 | 371.7 KB | 93,255 | 470.6 KB |
| `sha256_64r_k22` | 22 | SAT | 184,607 | 194.3 KB | 43,961 | 281,704 | 652.0 KB | 23,428 | 373.3 KB | 93,312 | 462.7 KB |
| `sha256_64r_k23` | 23 | SAT | 184,873 | 192.0 KB | 43,998 | 282,040 | 651.8 KB | 23,455 | 373.2 KB | 93,393 | 467.1 KB |
| `sha256_64r_k24` | 24 | SAT | 185,066 | 192.6 KB | 44,023 | 282,204 | 656.7 KB | 23,466 | 374.3 KB | 93,441 | 463.9 KB |
| `sha256_64r_k25` | 25 | SAT | 184,861 | 192.4 KB | 44,033 | 282,271 | 653.5 KB | 23,472 | 375.4 KB | 93,457 | 462.8 KB |
| `sha256_64r_k26` | 26 | SAT | 185,364 | 193.4 KB | 44,065 | 282,559 | 654.6 KB | 23,486 | 374.4 KB | 93,537 | 467.0 KB |
| `sha256_64r_k27` | 27 | SAT | 185,045 | 192.3 KB | 44,074 | 282,618 | 655.0 KB | 23,491 | 374.2 KB | 93,552 | 464.0 KB |
| `sha256_64r_k28` | 28 | SAT | 185,161 | 193.8 KB | 44,087 | 282,799 | 655.4 KB | 23,498 | 374.4 KB | 93,582 | 463.2 KB |
| `sha256_64r_k29` | 29 | SAT | 185,388 | 192.9 KB | 44,113 | 283,061 | 657.2 KB | 23,512 | 373.6 KB | 93,631 | 464.3 KB |
| `sha256_64r_k30` | 30 | SAT | 185,400 | 192.8 KB | 44,119 | 283,083 | 658.5 KB | 23,515 | 375.5 KB | 93,636 | 464.1 KB |
| `sha256_64r_k31` | 31 | SAT | 185,406 | 192.9 KB | 44,124 | 283,097 | 652.4 KB | 23,517 | 374.1 KB | 93,640 | 464.6 KB |
| `sha256_64r_k32` | 32 | SAT | 185,629 | 193.8 KB | 44,127 | 283,105 | 655.5 KB | 23,519 | 374.3 KB | 93,642 | 466.9 KB |

## Benchmark Results

- **Hardware & Isolation Protocol:** Evaluated strictly sequentially on an **AMD Ryzen 9 5950X** (16C/32T Linux x86_64), pinned to dedicated **CCD 1 core 12** (`taskset -c 12`, isolated 32 MiB L3 cache, zero concurrent solver contention), running on uncompressed inputs in `/tmp/` (excluding `.xz` I/O). Default single-thread flags: `--max-cores 1 --profile --timeout 300` for Frobenius (evaluated at `5f04ce8`, featuring cliff-free shortcut-first cost-amortized dispatch + 2048-lane early-exit `CompiledAig256`), `-t 1` for CryptoMiniSat 5.18.0, and default single-thread CLI for CaDiCaL 3.1.0, dense-solver 0.0.4, and Kissat 4.0.4.
- **Timing, Stopping Rule & 100% Verification:** Per-instance cutoff $T_{\max} = 300\;\text{s}$ (PAR-2 penalty $600\;\text{s}$). Solves `< 2.0 s` report the **exact median of 3 runs**; solves `>= 2.0 s` use 1 clean run. Under the **3-consecutive-timeout stopping rule**, once a track hits its first timeout at $k_0$, only $k_0 + 1$ and $k_0 + 2$ are tested (resetting if either solves); remaining $k > k_0 + 2$ are recorded as `— *(skipped)*` (counted as $600\;\text{s}$ PAR-2). Every single SAT witness across all 7 tracks and all repetitions was independently verified (**290 / 290 SAT runs verified**: 100% raw CNF clauses + XCNF XOR clauses + exact FIPS 180-4 `hashlib.sha256` & Binary AIGER 1.9 evaluation; **0 BADSAT, 0 false UNSAT**).

### 1. Per-Bit Runtime Scaling ($k = 1 \dots 32$, $T_{\max} = 300\;\text{s}$)

| Instance ($k$) | Frobenius 1C (`.aig`) | Frobenius 1C (`.cnf`) | [CaDiCaL](https://github.com/arminbiere/cadical) 3.1.0 (`.cnf`) | [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18.0 (`.cnf`) | [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18.0 (`.xcnf`) | [dense-solver](https://github.com/libdense/dense-solver) 0.0.4 (`.cnf`) | [Kissat](https://github.com/arminbiere/kissat) 4.0.4 (`.cnf`) |
|---|---:|---:|---:|---:|---:|---:|---:|
| `sha256_64r_k01` | 1.32 ms | 1.48 ms | 2.08 ms | 5.34 ms | 5.15 ms | **1.14 ms** | 1.37 ms |
| `sha256_64r_k02` | **33.38 ms** | 80.11 ms | 89.58 ms | 5.93 s | 299.24 ms | 970.62 ms | 55.55 ms |
| `sha256_64r_k03` | **33.15 ms** | 104.68 ms | 104.08 ms | 9.36 s | 5.73 s | 928.94 ms | 307.45 ms |
| `sha256_64r_k04` | **33.31 ms** | 103.45 ms | 104.28 ms | 12.22 s | 7.39 s | 936.92 ms | 376.76 ms |
| `sha256_64r_k05` | **34.02 ms** | 102.90 ms | 347.26 ms | 25.67 s | 27.69 s | 967.43 ms | 381.71 ms |
| `sha256_64r_k06` | **33.72 ms** | 103.14 ms | 445.01 ms | 22.65 s | 21.63 s | 1.06 s | 559.23 ms |
| `sha256_64r_k07` | **34.65 ms** | 102.65 ms | 271.79 ms | 45.04 s | 27.90 s | 1.23 s | 639.20 ms |
| `sha256_64r_k08` | **34.02 ms** | 105.55 ms | 851.34 ms | 59.25 s | 44.65 s | 1.44 s | 785.57 ms |
| `sha256_64r_k09` | **42.00 ms** | 110.79 ms | 2.04 s | 55.51 s | 32.80 s | 2.07 s | 1.70 s |
| `sha256_64r_k10` | **41.97 ms** | 108.89 ms | 2.21 s | 112.35 s | 62.93 s | 2.44 s | 7.21 s |
| `sha256_64r_k11` | **41.34 ms** | 108.42 ms | 12.50 s | 255.40 s | 138.61 s | 4.47 s | 1.06 s |
| `sha256_64r_k12` | **41.89 ms** | 109.71 ms | 13.92 s | 230.64 s | >300 s *(T/O)* | 12.91 s | 21.92 s |
| `sha256_64r_k13` | **42.58 ms** | 110.02 ms | 6.71 s | >300 s *(T/O)* | >300 s *(T/O)* | 14.29 s | 21.36 s |
| `sha256_64r_k14` | **59.08 ms** | 125.25 ms | 40.00 s | >300 s *(T/O)* | >300 s *(T/O)* | 34.91 s | 50.92 s |
| `sha256_64r_k15` | **59.64 ms** | 128.90 ms | 159.39 s | >300 s *(T/O)* | — *(skipped)* | 178.36 s | 35.79 s |
| `sha256_64r_k16` | **62.98 ms** | 127.80 ms | 89.40 s | — *(skipped)* | — *(skipped)* | 101.83 s | >300 s *(T/O)* |
| `sha256_64r_k17` | **65.77 ms** | 130.44 ms | 6.48 s | — *(skipped)* | — *(skipped)* | 159.71 s | >300 s *(T/O)* |
| `sha256_64r_k18` | **72.80 ms** | 136.94 ms | >300 s *(T/O)* | — *(skipped)* | — *(skipped)* | >300 s *(T/O)* | >300 s *(T/O)* |
| `sha256_64r_k19` | **87.79 ms** | 146.38 ms | >300 s *(T/O)* | — *(skipped)* | — *(skipped)* | >300 s *(T/O)* | — *(skipped)* |
| `sha256_64r_k20` | **118.28 ms** | 169.33 ms | >300 s *(T/O)* | — *(skipped)* | — *(skipped)* | >300 s *(T/O)* | — *(skipped)* |
| `sha256_64r_k21` | **175.61 ms** | 215.63 ms | — *(skipped)* | — *(skipped)* | — *(skipped)* | — *(skipped)* | — *(skipped)* |
| `sha256_64r_k22` | **290.59 ms** | 307.27 ms | — *(skipped)* | — *(skipped)* | — *(skipped)* | — *(skipped)* | — *(skipped)* |
| `sha256_64r_k23` | 528.35 ms | **502.96 ms** | — *(skipped)* | — *(skipped)* | — *(skipped)* | — *(skipped)* | — *(skipped)* |
| `sha256_64r_k24` | 984.26 ms | **859.39 ms** | — *(skipped)* | — *(skipped)* | — *(skipped)* | — *(skipped)* | — *(skipped)* |
| `sha256_64r_k25` | 2.51 s | **2.27 s** | — *(skipped)* | — *(skipped)* | — *(skipped)* | — *(skipped)* | — *(skipped)* |
| `sha256_64r_k26` | 4.36 s | **3.69 s** | — *(skipped)* | — *(skipped)* | — *(skipped)* | — *(skipped)* | — *(skipped)* |
| `sha256_64r_k27` | 8.08 s | **6.82 s** | — *(skipped)* | — *(skipped)* | — *(skipped)* | — *(skipped)* | — *(skipped)* |
| `sha256_64r_k28` | 15.46 s | **12.67 s** | — *(skipped)* | — *(skipped)* | — *(skipped)* | — *(skipped)* | — *(skipped)* |
| `sha256_64r_k29` | 30.18 s | **30.15 s** | — *(skipped)* | — *(skipped)* | — *(skipped)* | — *(skipped)* | — *(skipped)* |
| `sha256_64r_k30` | 59.67 s | **54.12 s** | — *(skipped)* | — *(skipped)* | — *(skipped)* | — *(skipped)* | — *(skipped)* |
| `sha256_64r_k31` | 124.63 s | **108.42 s** | — *(skipped)* | — *(skipped)* | — *(skipped)* | — *(skipped)* | — *(skipped)* |
| `sha256_64r_k32` | 249.85 s | **197.83 s** | — *(skipped)* | — *(skipped)* | — *(skipped)* | — *(skipped)* | — *(skipped)* |
| **Solved ($T_{\max} = 300\;\text{s}$)** | **32 / 32** *(highest)* | **32 / 32** *(highest)* | 17 / 32 *(-15 worse)* | 12 / 32 *(-20 worse)* | 11 / 32 *(-21 worse)* | 17 / 32 *(-15 worse)* | 15 / 32 *(-17 worse)* |
| **Total PAR-2 ($T_{\max} = 300\;\text{s}$)** | 497.70 s *(1.18x slower)* | **420.07 s** *(fastest)* | 9,334.87 s *(22.2x slower)* | 12,834.03 s *(30.6x slower)* | 12,969.64 s *(30.9x slower)* | 9,518.51 s *(22.7x slower)* | 10,343.07 s *(24.6x slower)* |
| **Stopping Point (3 consec. T/O)** | *None (32/32)* | *None (32/32)* | $k = 18\text{--}20$ | $k = 13\text{--}15$ | $k = 12\text{--}14$ | $k = 18\text{--}20$ | $k = 16\text{--}18$ |

- **Full 32-Bit Single-Core Inversion & Overlap Highlights:** Both Frobenius tracks solve **all 32 / 32** instances inside the 300 s single-core cutoff with **zero timeouts** — completing full 32-bit 64-round FIPS 180-4 SHA-256 nonce inversion (`sha256_64r_k32`) in **`197.83 s` (`3.30 min`)** from flat DIMACS `.cnf` (`420.07 s` total PAR-2 across all 32 instances) and **`249.85 s` (`4.16 min`)** from native Binary AIGER `.aig` (`497.70 s` total PAR-2), achieving **`22.2x–30.9x` lower PAR-2** than all five CDCL tracks. Across $k = 1 \dots 15$ (all 15 instances solved by Kissat, CaDiCaL, dense-solver, and Frobenius), Frobenius 1C (`.aig`) totals **`0.566 s`** vs. Kissat 4.0.4 (`143.07 s`, **`253x` slower**), CaDiCaL 3.1.0 (`238.99 s`, **`422x` slower**), and dense-solver 0.0.4 (`256.98 s`, **`454x` slower**). Across $k = 1 \dots 17$ (all 17 instances solved by CaDiCaL and dense-solver), Frobenius 1C (`.aig`) totals **`0.695 s`** vs. CaDiCaL 3.1.0 (`334.87 s`, **`482x` slower**) and dense-solver 0.0.4 (`518.51 s`, **`746x` slower**), while Frobenius 1C (`.cnf`) totals **`1.764 s`** (**`190x` faster** than CaDiCaL, **`294x` faster** than dense-solver on identical flat `.cnf` files). At $k = 15$, Frobenius 1C (`.aig`) (`59.64 ms`) is **`600x`** faster than Kissat (`35.79 s`), **`2,673x`** faster than CaDiCaL (`159.39 s`), and **`2,991x`** faster than dense-solver (`178.36 s`).

### 2. Growth-Curve Modeling, Model Selection & Best-Fit Equations

![Growth-curve exponents, 32-bit nonce inversion times, and AICc model selection across all 7 tracks](growth_analysis.svg)

*Figure: Fitted per-bit doubling exponents $\alpha$ (uncensored M1 vs. right-censored Tobit MLE relative to exact $2^k$), log-scale full 32-bit nonce inversion times $T(32)$ (measured `3.30–4.16 min` `< 5m` cutoff for Frobenius 1C vs. extrapolated days for CDCL), and $\Delta\text{AICc}$ model-selection scores showing zero statistical support for sub-exponential scaling in any single-codepath regime across all 7 tracks. Regenerated via [`src/gen_diagram.py`](src/gen_diagram.py).*

Four nested/candidate runtime models were fitted in log-space (minimizing $\sum_i (\ln T_i - \ln \hat{T}(k_i))^2$ via multi-start grid seeding + nested Levenberg–Marquardt + Nelder–Mead with monotonicity constraint $\alpha \ge 0$, excluding the degenerate 0-AND $k = 1$ collapse):

- **M1 (Shifted Pure Exponential, $p = 3$):** $T(k) = c_0 + a \cdot 2^{\alpha k}$ (base $b = 2^\alpha$, bits per $10\times$ slowdown $= \log_2(10)/\alpha$)
- **M2 (Polynomial-Modulated Exponential, $p = 4$):** $T(k) = c_0 + a \cdot k^\beta \cdot 2^{\alpha k}$
- **M3 ($\sqrt{k}$-Modulated Exponential, $p = 4$):** $T(k) = c_0 + a \cdot 2^{\alpha k + \delta \sqrt{k}}$
- **M4 (Stretched Exponential, $p = 4$):** $T(k) = c_0 + a \cdot \exp(c_1 k^\gamma)$ ($\gamma < 1$ sub-exponential vs. $\gamma = 1$ pure exponential vs. $\gamma > 1$ super-exponential)

Model complexity is penalized via small-sample **AICc** and **BIC** (with $K = p + 1$ parameters including $\sigma^2$; positive $\Delta\text{AICc} = \text{AICc}_{\text{M1}} - \text{AICc}_{\text{M}_j} > 2$ is required to support modulation beyond M1). Because CDCL solvers exhibit large multiplicative variance near $T_{\max} = 300\;\text{s}$ (creating survivorship bias when lucky hits like CaDiCaL's `6.48 s` at $k = 17$ survive below cutoff), we also fit a **right-censored Tobit MLE** for M1 incorporating each CDCL track's 3 observed $T(k) \ge 300\;\text{s}$ timeouts (Frobenius solves all 32/32 with zero censoring).

| Solver Track | Fit Range ($n$) | Best Model (AICc / BIC) | M1 Floor $c_0$ | M1 Prefactor $a$ | Doubling Exp $\alpha$ ($b = 2^\alpha$) | Bits / $10\times$ | Log $R^2$ | Mult. RMS | $\Delta\text{AICc}$ (Best M2–M4 vs M1) | $T(32)$ (Meas.\* / Extrap.) |
|---|---:|:---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Frobenius 1C (`.aig`) | $k = 14\dots 32$ (19) | **M1** / M1 | 57.51 ms | `6.182e-08` s | **0.9973** (1.9963x) | 3.33 | 0.99954 | 1.062x | `-0.85` (M2) | **4.16 min\*** *(fit 4.17m)* |
| Frobenius 1C (`.aig`, Stage 0F) | $k = 14\dots 24$ (11) | **M1** / M1 | 58.26 ms | `6.225e-08` s | **0.9929** (1.9902x) | 3.35 | 0.99995 | 1.007x | `-7.28` (M2) | **4.16 min\*** *(fit 3.81m)* |
| Frobenius 1C (`.aig`, Probe+SIMD) | $k = 25\dots 32$ (8) | **M1** / M2 | 773.25 ms | `3.700e-08` s | **1.0200** (2.0280x) | 3.26 | 0.99995 | 1.011x | `-13.43` (M2) | **4.16 min\*** *(fit 4.14m)* |
| Frobenius 1C (`.cnf`) | $k = 14\dots 32$ (19) | M3§ / M3§ | 122.57 ms | `4.625e-08` s | **1.0042** (2.0058x) | 3.31 | 0.99908 | 1.079x | `+2.08`§ (M3) | **3.30 min\*** *(fit 3.63m)* |
| Frobenius 1C (`.cnf`, Stage 0F) | $k = 14\dots 24$ (11) | **M1** / M4 | 125.38 ms | `3.569e-08` s | **1.0130** (2.0181x) | 3.28 | 0.99978 | 1.009x | `-3.59` (M4) | **3.30 min\*** *(fit 3.41m)* |
| Frobenius 1C (`.cnf`, Probe+SIMD) | $k = 25\dots 32$ (8) | **M1** / M4 | 600.44 ms | `4.307e-08` s | **1.0059** (2.0082x) | 3.30 | 0.99842 | 1.062x | `-15.86` (M4) | **3.30 min\*** *(fit 3.53m)* |
| CaDiCaL 3.1.0 (`.cnf`) | $k = 2\dots 17$ (16) | **M1** / M1 | 7.62 ms | `2.389e-02` s | **0.6916** (1.6151x) | 4.80 | 0.85437 | 2.464x | `-2.27` (M2) | **1.27 days** |
| dense-solver 0.0.4 (`.cnf`) | $k = 2\dots 17$ (16) | **M1** / M1 | 898.26 ms | `2.713e-03` s | **0.9708** (1.9600x) | 3.42 | 0.97422 | 1.357x | `-2.26` (M2) | **70.61 days** |
| Kissat 4.0.4 (`.cnf`) | $k = 2\dots 15$ (14) | **M1** / M1 | 74.36 ms | `1.773e-02` s | **0.7613** (1.6950x) | 4.36 | 0.89101 | 1.956x | `-4.59` (M4) | **4.43 days** |
| CryptoMiniSat 5.18.0 (`.cnf`) | $k = 2\dots 12$ (11) | **M1** / M1 | 0.00 ms | `2.981e+00` s | **0.5337** (1.4476x) | 6.22 | 0.96929 | 1.231x | `-7.32` (M4) | **4.77 days** |
| CryptoMiniSat 5.18.0 (`.cnf`, post-floor) | $k = 5\dots 12$ (8) | **M1** / M1 | 14.74 s | `7.433e-01` s | **0.7067** (1.6321x) | 4.70 | 0.93485 | 1.245x | `-18.49` (M2) | **55.29 days** |
| CryptoMiniSat 5.18.0 (`.xcnf`) | $k = 2\dots 11$ (10) | **M1** / M2 | 0.00 ms | `7.158e-01` s | **0.7096** (1.6353x) | 4.68 | 0.76150 | 2.205x | `-1.66` (M2) | **56.72 days** |

*\*Actual measured single-core $T(32)$ on core 12 (`197.83 s = 3.30 min` `.cnf`, `249.85 s = 4.16 min` `.aig`; `3,367x–111,922x` faster than CDCL extrapolated $T(32)$). §On `frobenius_cnf` across $k = 14\dots 32$, the marginal $\Delta\text{AICc} = +2.08$ is strictly an additive regime-seam artifact from the `+0.64 s` shortcut-first probe turning on at $k = 25$ (plus CNF-to-AIG PI-order jitter at $k = 29\text{--}31$); splitting at the $k = 24 \to 25$ seam restores overwhelming M1 preference on BOTH halves (`-3.59` on $k = 14\dots 24$, `-15.86` on $k = 25\dots 32$), and even full $k = 2\dots 32$ favors M1 by `-2.76` AICc / `-3.33` BIC!*

#### Full M1–M4 Model-Selection Diagnostics & Right-Censored Tobit Estimates

| Solver Track | Range | M1 AICc (BIC) | M2 $\Delta\text{AICc}$ ($\beta$) | M3 $\Delta\text{AICc}$ ($\delta$) | M4 $\Delta\text{AICc}$ ($\gamma$) | Sub-Exp Supported? | Post-Floor $T(k)/T(k-1)$ (Med / Geo) | Tobit Censored M1 $\alpha$ ($T(32)$) |
|---|---:|---:|---:|---:|---:|:---:|---:|---:|
| Frobenius 1C (`.aig`) | $k=14\dots 32$ | -96.07 (-95.15) | `-0.85` (+3.68) | `-0.89` (+4.16) | `-0.91` (0.80) | No | 1.853x / 1.732x | — *(0 T/Os; meas. 4.16 min)* |
| Frobenius 1C (`.aig`, split) | $k=14\dots 24$ / $25\dots 32$ | -95.30 / -50.47 | `-7.28` / `-13.43` | `-7.28` / `-13.45` | `-7.29` / `-13.48` | No | — | — *(0 T/Os)* |
| Frobenius 1C (`.cnf`) | $k=14\dots 32$ | -86.94 (-86.02) | `+2.08`§ (+8.63) | `+2.08`§ (+9.68) | `+2.08`§ (0.54) | No *(k=25 seam§)* | 1.709x / 1.630x | — *(0 T/Os; meas. 3.30 min)* |
| Frobenius 1C (`.cnf`, split) | $k=14\dots 24$ / $25\dots 32$ | -88.61 / -23.67 | `-3.69` / `-16.89` | `-3.60` / `-16.98` | `-3.59` / `-15.86` | No | — | — *(0 T/Os)* |
| CaDiCaL 3.1.0 (`.cnf`) | $k=2\dots 17$ | 8.33 (7.79) | `-2.27` (+5.35) | `-3.04` (+4.68) | `-2.43` (0.15) | No | 1.197x / 1.276x | **0.8098** (7.71 days) |
| dense-solver 0.0.4 (`.cnf`) | $k=2\dots 17$ | -26.36 (-26.91) | `-2.26` (+8.91) | `-2.85` (+7.07) | `-2.35` (0.15) | No | 1.700x / 1.722x | **0.9753** (75.04 days) |
| Kissat 4.0.4 (`.cnf`) | $k=2\dots 15$ | 1.28 (-0.61) | `-5.00` (-0.43) | `-4.88` (-1.74) | `-4.59` (1.40) | No | 2.163x / 1.726x | **1.0073** (171.19 days) |
| CryptoMiniSat 5.18.0 (`.cnf`) | $k=2\dots 12$ | -19.86 (-24.93) | `-7.33` (+0.02) | `-7.33` (-0.04) | `-7.32` (1.02) | No | 1.316x / 1.368x | **0.5438** (5.63 days) |
| CryptoMiniSat 5.18.0 (`.xcnf`) | $k=2\dots 11$ | 11.30 (4.51) | `-1.66` (+2.90) | `-5.75` (+3.56) | `-2.96` (0.15) | No *(AICc)* / artifact *(BIC)* | 1.445x / 1.308x | **0.7905** (256.27 days) |

- **Zero Statistical Evidence for Sub-Exponential Scaling on Any Single-Codepath Track:** Across every single solver in its post-floor / single-codepath regime, **shifted pure exponential M1 wins decisively by AICc**:
  - On `frobenius_aig` across the entire 19-point `CompiledAig256` span ($k = 14\dots 32$), M1 wins BOTH AICc (`-0.85` to `-0.91`) and BIC (`-0.04` to `-0.10`) with **$\alpha = 0.9973$** ($R^2_{\log} = 0.99954$, RMS = `1.062x`), and matches measured $T(32) = 249.85\;\text{s}$ within **0.13%** (`250.18 s`).
  - On `frobenius_cnf`, fitting a single constant-floor M1 across the $k = 24 \to 25$ shortcut-probe seam ($k = 14\dots 32$) produces a marginal $\Delta\text{AICc} = +2.08$ because the `+643 ms` probe floor steps up at $k = 25$ (`1.395x` over pure Stage 0F) while CNF-to-AIG recovery shifts PI sweep fraction slightly at $k = 29\text{--}31$ (`0.638` vs. `0.554` at $k = 25\text{--}28, 32$); separating the two codepaths immediately restores strong M1 preference on both halves (`k = 14..24`: $\Delta\text{AICc} = -3.59$ to $-3.69$, $\alpha = 1.0130$, $R^2_{\log} = 0.99978$; `k = 25..32`: $\Delta\text{AICc} = -15.86$ to $-16.98$, $c_0 = 600.4\;\text{ms}$, $\alpha = 1.0059$, $R^2_{\log} = 0.99842$), and full $k = 2\dots 32$ also prefers M1 by both AICc (`-2.76`) and BIC (`-3.33`).
  - On `cms_xcnf` over $k = 2\dots 11$, the 19x discontinuity between $k = 2$ (`0.30 s` Gauss-solved) and $k = 3$ (`5.73 s` CDCL) mimics polynomial curvature on BIC while AICc still prefers M1 by `1.66`, and post-floor $k = 5\dots 11$ prefers M1 by both AICc and BIC.
- **CDCL Scaling Exponents vs. Exact $2^k$ ($\alpha = 1.000$):**
  - **dense-solver 0.0.4** shows the cleanest single-trajectory CDCL scaling of any external engine ($R^2_{\log} = 0.9742$, RMS = `1.36x`), landing right at **$\alpha = 0.9708$** ($1.960\times$/bit, Tobit **$\alpha = 0.9753$**, $T(32) \approx 71\text{--}75\;\text{days}$) — essentially pure $2^k$ brute-force scaling with **`~30,800x`** higher constant factor than Frobenius's 2048-lane AVX2 datapath!
  - **Kissat 4.0.4** uncensored $k = 2\dots 15$ gives $\alpha = 0.7613$ (post-floor $k = 8\dots 15$: $\alpha = 0.8590$), and once right-censored survivorship bias from $k = 16\dots 18$ timeouts is accounted for via Tobit MLE, Kissat snaps directly to **$\alpha = 1.0073$** ($2.010\times$/bit, $T(32) \approx 171\;\text{days}$, **`~74,800x`** slower than Frobenius `.cnf`).
  - **CaDiCaL 3.1.0** uncensored $k = 2\dots 17$ gives $\alpha = 0.6916$ (`RMS = 2.46x`) solely because of the 40x lucky draw at $k = 17$ (`6.48 s` vs. `159.39 s` at $k = 15$ and `89.40 s` at $k = 16$); excluding $k = 17$ gives $k = 2\dots 16$ M1 **$\alpha = 0.9033$** ($1.870\times$/bit, $R^2_{\log} = 0.9569$, RMS = `1.66x`, $T(32) \approx 34.1\;\text{days}$), and right-censored Tobit MLE over $k = 2\dots 20$ gives **$\alpha = 0.8098$** ($1.753\times$/bit, $T(32) \approx 7.71\;\text{days}$, **`3,367x`** slower than Frobenius `.cnf`).
  - **CryptoMiniSat 5.18.0** pays a large `6–28 s` Gaussian-elimination/inprocessing floor even at $k = 2\dots 5$, which compresses its apparent `k = 2..12` slope to $\alpha = 0.5337$ (`cnf`); separating the `c0 = 14.74 s` floor over $k = 5\dots 12$ lifts `.cnf` to **$\alpha = 0.7067$** ($1.632\times$/bit, $T(32) \approx 55.3\;\text{days}$, **`24,149x`** slower), while Tobit right-censored MLE lifts `.xcnf` to **$\alpha = 0.7905$** ($1.730\times$/bit, $T(32) \approx 256\;\text{days}$, **`111,922x`** slower).

### 3. Frobenius Cliff-Free Piecewise Regimes & 2048-Lane Early-Exit AVX2 Scaling

With commit `5f04ce8` replacing the old hardcoded $k \le 24$ guard with **shortcut-first cost-amortized dispatch + 2048-lane early-exit `CompiledAig256`**, Frobenius's wall-clock curve across $k = 1 \dots 32$ decomposes cleanly into five cliff-free architectural regimes with **zero timeouts**:

1. **$k = 1$ (0-AND Symbolic Collapse):** `1.32 ms` (`.aig`) / `1.48 ms` (`.cnf`), solved immediately by level-0 propagation.
2. **$k = 2 \dots 8$ (Stage 0C Single 256-Lane AVX2 DAG Pass):** `33.15–34.65 ms` (`.aig`) / `80.11–105.55 ms` (`.cnf`). Entire input space ($\le 256$ assignments) completes in a single AVX2 pass (`< 1 ms` solve time), completely dominated by flat AIGER parse (`~30 ms`) or CNF-to-AIG circuit lifting (`~75–100 ms`).
3. **$k = 9 \dots 13$ (Stage 0C Wide `CompiledAig256` Sweep, Small Budget):** `41.34–42.58 ms` (`.aig`) / `108.42–110.79 ms` (`.cnf`). Total SIMD gate work $2^{k-8} \cdot \lvert \text{COI} \rvert \le 2 \times 10^6$ fits inside Stage 0C, paying only `+8 ms` for wide `CompiledAig256` register allocation.
4. **$k = 14 \dots 24$ (Stage 0F Immediate Zero-CNF 2048-Lane Early-Exit `CompiledAig256`):**
   - When estimated SIMD gate work $2^{k-9}\cdot |\text{active\_coi}| \le 2.5 \times 10^9$ (cost-amortized strictly cheaper than compiling 282k CNF clauses + FRAIG + CDCL setup), Frobenius bypasses CNF entirely and runs direct branchless 2048-lane early-exit AVX2 batches (`eval_2048`).
   - **`.aig` ($k = 14\dots 24$):** $T(k) = 58.26\;\text{ms} + 6.225 \times 10^{-8}\cdot 2^{0.9929 k}\;\text{s}$ (**$R^2_{\log} = 0.99995$**, **RMS = `1.0068x`**). Exact 2048-lane batch counts double cleanly at `0.616` of the search space (`4 → 9 → 19 → 39 → 78 → 157 → 315 → 630 → 1,260 → 2,521 → 5,043`), hitting **`0.984 s`** at $k = 24$ (**`11.2M` 64R SHA-256 evals/s** on 1 core, `2.45x` faster than the prior 512-lane implementation!).
   - **`.cnf` ($k = 14\dots 24$):** $T(k) = 125.38\;\text{ms} + 3.569 \times 10^{-8}\cdot 2^{1.0130 k}\;\text{s}$ (**$R^2_{\log} = 0.99978$**, **RMS = `1.0092x`**), hitting **`0.859 s`** at $k = 24$ (**`11.6M` evals/s**; `4,539` batches).
5. **$k = 25 \dots 32$ (Shortcut-First Probe + Cost-Amortized 2048-Lane `CompiledAig256` Escalation — Zero Cliff!):**
   - Once $2^{k-9}\cdot |\text{active\_coi}| > 2.5 \times 10^9$ at $k = 25$, Frobenius first runs a bounded **shortcut probe** (Mini-FRAIG + Tseitin CNF + CDCL capped at `min(1,500 conflicts, 500 ms)` so structured/easy large-$k$ circuits still shortcut in milliseconds!). On full-diffusion 64-round SHA-256, the probe absorbs `~200–270` CDCL conflicts (`3.2M–4.4M` propagations) in a constant **`~0.60–0.64 s`**, detects full-diffusion stall, times 4 warmup 2048-lane batches (`< 1 ms`), verifies tractability (`est_simd_s <= 1 day || k <= 40`), and escalates seamlessly into the 2048-lane early-exit `CompiledAig256` sweep!
   - **Observable Shortcut-Probe Bump vs. Asymptotic Amortization:** At $k = 25$, this constant probe adds **`+0.609 s`** on `.aig` (`2.515 s` vs. `1.905 s` Stage 0F extrapolation, `1.320x`) and **`+0.643 s`** on `.cnf` (`2.269 s` vs. `1.626 s`, `1.395x`), cleanly captured as a shifted floor $c_0 = 773\;\text{ms}$ (`.aig`) / $600\;\text{ms}$ (`.cnf`) in the $k = 25\dots 32$ M1 fits ($R^2_{\log} = 0.99995$ `.aig` / $0.99842$ `.cnf`). Because the probe cost is strictly $O(1)$ while sweep work doubles each bit, the overhead amortizes to **`16.8%`** at $k = 26$, **`5.8%`** at $k = 28$, **`< 1.1%`** at $k = 30$, and **`< 0.3%`** at $k = 32$!
   - **Measured Frontier ($k = 30, 31, 32$, 1 Core):**
     - **`.aig`:** $T(30) = \mathbf{59.67\;\text{s}}$ (`11.2M` evals/s), $T(31) = \mathbf{124.63\;\text{s}}$, **$T(32) = \mathbf{249.85\;\text{s}}$ (`4.16 min`, `10.6M` evals/s sustained across `1,291,239` 2048-lane batches)**; full $k = 14\dots 32$ M1 fit: $T(k) = 57.51\;\text{ms} + 6.182 \times 10^{-8}\cdot 2^{0.9973 k}\;\text{s}$ ($R^2_{\log} = 0.99954$).
     - **`.cnf`:** $T(30) = \mathbf{54.12\;\text{s}}$ (`12.8M` evals/s), $T(31) = \mathbf{108.42\;\text{s}}$ (`12.7M` evals/s), **$T(32) = \mathbf{197.83\;\text{s}}$ (`3.30 min`, `12.1M` evals/s sustained across `1,162,250` 2048-lane batches)**; full $k = 14\dots 32$ M1 fit: $T(k) = 122.57\;\text{ms} + 4.625 \times 10^{-8}\cdot 2^{1.0042 k}\;\text{s}$ ($R^2_{\log} = 0.99908$). CNF-to-AIG lifting (`cnf_recover.rs`) outperforms native `.aig` from $k = 23$ onward (`1.26x` faster at $k = 32$) because recovered native `Xor3`/`Maj3`/`Mux` gate ordering avoids the 3-AND AIGER round-trip and yields higher sustained AVX2 throughput (`12.1–12.8M/s` vs. `10.6–11.2M/s`).

<!-- BEGIN_STRUCTURAL_ANALYSIS -->
## Phase-Transition & Structural Analysis

*Auto-generated by [`../src/analyze_benchmarks.py`](../src/analyze_benchmarks.py). Position relative to the critical phase transition is measured by $\rho_{\mathrm{crit}} = \frac{1}{n}\sum_k m_k / \alpha_c(k)$ (exact $\alpha/\alpha_c(k)$ for pure $k$-SAT; effective critical threshold $\alpha_c^{\mathrm{eff}} = \alpha/\rho_{\mathrm{crit}}$; `Under` $<0.90\times$, `Near-crit` $0.90\text{--}1.10\times$, `Over` $>1.10\times$), alongside Gent–Walsh annealed constrainedness $\kappa = -\frac{1}{n}\sum_i \log_2(1-2^{-k_i})$ (AAAI 1996), clause-length profile ($\bar{k}$, `%Bin`, `%Horn`), variable-degree CV ($\sigma_d/\bar{d}$, uniformity vs. hub skew), and extracted native XOR parity clauses.*

| Group / Family | Files | Med $n$ | Med $m$ | $\alpha=m/n$ (Med) | $\alpha_c^{\mathrm{eff}}$ (Med) | $\rho_{\mathrm{crit}}$ Med [Min–Max] (Regime) | Med $\kappa$ | Med $\bar{k}$ | Bin% | Horn% | Deg CV | Total XORs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `sha256-64r-nonce-scaling` | 32 | 43,788 | 280,477 | 6.41 | 5.60 | **1.14x** [1.14x–116x] (Over) | 0.92 | 3.53 | 2% | 50% | 0.64 | 720,860 |

**Collection Phase-Transition Summary (32 instances, 4 formats: 32 CNF / 32 AIG / 32 XCNF / 32 ANF):** median $\rho_{\mathrm{crit}} = 1.14\times$ (range `1.14x–116x`), median $\kappa = 0.92$, regime split **0 Under / 0 Near-critical / 32 Over**, total extracted native XOR parity clauses = **720,860**, total ANF equations = **2,874,038**.
<!-- END_STRUCTURAL_ANALYSIS -->

## References

- NIST, *Secure Hash Standard (SHS)*, FIPS PUB 180-4, August 2015.
- I. Mironov and L. Zhang, *Applications of SAT Solvers to Cryptanalysis of Hash Functions*, SAT 2006, LNCS 4121.
- V. Nossum, *SAT-based preimage attacks on SHA-1*, Master's Thesis, University of Oslo, 2012.
- S. Nejati, J. Liang, C. Gebotys, K. Czarnecki, and V. Ganesh, *Adaptive Restart and CEGAR-based Solver for Inverting Cryptographic Hash Functions*, VSTTE 2017.
- K. P. Burnham and D. R. Anderson, *Model Selection and Multimodel Inference: A Practical Information-Theoretic Approach* (AICc / BIC), 2nd ed., Springer, 2002.
