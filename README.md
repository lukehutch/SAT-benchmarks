# SAT Benchmarks

A curated, **three-format** (**Binary AIGER 1.9 `.aig`**, **DIMACS `.cnf`**, and **[CryptoMiniSat](https://github.com/msoos/cryptominisat) `.xcnf`**) collection of **26 benchmark suites** spanning Boolean satisfiability, circuit inversion, algebraic cryptanalysis, quantum LDPC code distance, matrix multiplication, graph theory, combinatorial chessboard puzzles, symmetry breaking, exact circuit synthesis, hardware verification, finite-automata complementation, SATLIB/DIMACS classics, and SAT Competition corpora.

Every benchmark suite lives in its own top-level directory containing:
- Native-format benchmark instances at the suite root (`.aig` for circuit-native suites; `.cnf` / `.cnf.xz` for clausal suites; `.xcnf` for native XOR-CNF suites; `.mata.xz` for the MATA automata suite).
- Exact conversions for the two remaining formats in subdirectories:
  - Originally-`.aig` suites provide `cnf-version/` (`.cnf`) and `xcnf-version/` (`.xcnf`).
  - Originally-`.cnf` suites provide `aig-version/` (`.aig`) and `xcnf-version/` (`.xcnf` / `.xcnf.xz`, with all complete $2^{k-1}$-clause XOR parity blocks collapsed losslessly to native `x l1 ... lk 0` lines).
  - Originally-`.xcnf` suites provide `cnf-version/` (`.cnf.xz`) and `aig-version/` (`.aig`).
  - Every single `.aig` file across all suites (**773 / 773**) conforms to **Binary AIGER 1.9** (`L = 0`, `O = 1` combinational miter where `PO_0 = 1` iff SAT) and has been independently verified with [Berkeley **ABC**](https://github.com/berkeley-abc/abc) (`read_aiger`, `0` errors).
- Standalone generator, exporter, fetcher, or converter source code in `src/` (including `cnf2aig.py` and `cnf2xcnf.py`).
- A detailed `README.md` documenting provenance, contributor credits, upstream links and licenses, mathematical/circuit parameters, exact data sizes, comparative 1-core solver timings (Frobenius 1C, [`dense-solver 0.0.4`](https://github.com/libdense/dense-solver), [Kissat](https://github.com/arminbiere/kissat) 4.0.4, [CaDiCaL](https://github.com/arminbiere/cadical) 3.1.0, [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18.0 CNF & XCNF), proof verification status ([`cake_lpr`](https://github.com/tanyongkiam/cake_lpr) / [`lrat-check`](https://github.com/marijnheule/drat-trim)), and literature citations.

## Benchmark Suites (26 Suites)

| Suite | Origin Format | Provenance & Credit | Instances | SAT / UNSAT | Domain & Structural Focus | Generator / Scripts |
|---|---|---|---:|:---:|---|---|
| [`aloul-symmetry-benchmarks/`](aloul-symmetry-benchmarks/README.md) | CNF (`.cnf`) | **Sourced** — Fadi A. Aloul ([`aloul.net`](https://www.aloul.net/benchmarks.html), DAC 2002, via [`@merlin_numa`](https://twitter.com/merlin_numa)) | 82 | Mixed | Symmetry-rich FPGA switch-box (Homer/Bart), routing, Urquhart, Array/Wallace factoring | Python (`src/`) |
| [`cec-arithmetic-miters/`](cec-arithmetic-miters/README.md) | AIG (`.aig`) | **Original** *(classic EDA)* | 5 | 0 / 5 | EDA CEC miters: Ripple-Carry vs. Kogge–Stone; Array vs. Wallace vs. Karatsuba | Rust (`src/`) |
| [`coupled-linear-nonlinear/`](coupled-linear-nonlinear/README.md) | AIG (`.aig`) | **Original** | 4 | 3 / 1 | Coupled $\mathbb{F}_2$ linear + nonlinear $\mathrm{And}/\mathrm{Maj}_3/\mathrm{Mux}$ circuits | Rust (`src/`) |
| [`dense-solver-benchmarks/`](dense-solver-benchmarks/README.md) | CNF (`.cnf`) | **Sourced** — Merlin Numa ([`@merlin_numa`](https://twitter.com/merlin_numa), [`dense-solver`](https://github.com/libdense/dense-solver), [Zenodo](https://zenodo.org/records/24443907), MIT) | 50 | 18 / 32 | Multi-encoding PHP ($\mathrm{PHP}^{65}_{64}$), mutilated chessboards, 22 SATLIB + 8 SC25 CNFs | Python (`src/`) |
| [`f2-frobenius-circulants/`](f2-frobenius-circulants/README.md) | AIG (`.aig`) | **Original** | 6 | 4 / 2 | Balanced $\mathbb{F}_2$ circulant parity circuits ($n=64\text{--}4{,}096$) | Rust (`src/`) |
| [`hamd-hamiltonian-cycle/`](hamd-hamiltonian-cycle/README.md) | CNF (`.cnf`) | **Original** *(classic graphs)* | 22 | 12 / 10 | 6 provably SAT/UNSAT graph families ($GP$, Snarks, Meredith, Chvátal, Broken Crown, Planted) | Rust (`src/`) |
| [`hard-spn/`](hard-spn/README.md) | AIG (`.aig`) | **Original** | 4 | 3 / 1 | LowMC-style linear-form + S-box SPN algebraic cryptanalysis | Rust (`src/`) |
| [`heule-matrix-challenges/`](heule-matrix-challenges/README.md) | CNF (`.cnf.xz`) | **Sourced** — Heule, Kauers, Seidl ([repo](https://github.com/marijnheule/matrix-challenges), via [`@SMT_Solvers`](https://twitter.com/SMT_Solvers)) | 43 | Mixed / Open | $3\times 3$ matrix multiplication over $\mathbb{F}_2$ ($R=22, 23$, SAT 2019) | C + Python (`src/`) |
| [`integer-factoring/`](integer-factoring/README.md) | AIG (`.aig`) | **Original** *(classic problem)* | 6 | 5 / 1 | Wallace & Karatsuba multiplier inversion (28–40b) + XOR-masked mult | Rust (`src/`) |
| [`knights-tour-obstacles/`](knights-tour-obstacles/README.md) | CNF (`.cnf`) | **Original** | 10 | 5 / 5 | Obstacle Knight's Tour Hamiltonian cycles on punched $12\times 12\text{--}16\times 16$ boards ($d=0.15\text{--}0.26$) | Python (`src/`) |
| [`mata-presburger-nfa/`](mata-presburger-nfa/README.md) | NFA (`.mata.xz`) | **Sourced** — VeriFIT MATA ([`nfa-bench`](https://github.com/VeriFIT/nfa-bench), MIT, via [`@TravisRudd`](https://twitter.com/TravisRudd)) | 174 | Automata | TACAS 2024 Presburger explicit-complement NFA benchmark set | Python (`src/`) |
| [`mod-circuit-sat/`](mod-circuit-sat/README.md) | CNF (`.cnf`) | **Sourced** — [`@vzhilin_me`](https://twitter.com/vzhilin_me) ([`vzhn/mod-circuit-sat`](https://github.com/vzhn/mod-circuit-sat), arXiv:2102.12579) | 11 | 5 / 4 / 2 Open | Exact optimal $B_2$ circuit synthesis for $\mathrm{MOD}_n^{3,r}$ ($n=3\text{--}6$) | Python (`src/`) |
| [`pretolani-pret/`](pretolani-pret/README.md) | CNF (`.cnf`) | **Sourced** — Daniele Pretolani ([SATLIB PRET](https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/DIMACS/PRET/descr.html), via [`@MMarchidann`](https://twitter.com/MMarchidann)) | 8 | 0 / 8 | Parity-charged graph 2-coloring UNSAT formulas ($n=60, 150$; 25%–75% Horn) | Python (`src/`) |
| [`qdistsat-qldpc/`](qdistsat-qldpc/README.md) | Matrices / CNF | **Sourced** — [`QDistSAT`](https://github.com/guluchen/QDistSAT) (GPL-3.0+) & Bravyi et al., via [`@TravisRudd`](https://twitter.com/TravisRudd) | 10 | 5 / 5 | CSS Quantum LDPC bivariate-bicycle code distance ($[[30..756]]$, `.cnf`/`.xcnf`/`.aig`) | Python (`src/`) |
| [`queen-armies/`](queen-armies/README.md) | CNF (`.cnf`) | **Original** *(inspired by [Christopher Wolfram](https://christopherwolfram.com/projects/queen-armies/))* | 8 | 4 / 4 | Peaceable Queen Armies ($A \in \{2, 3, 4\}$, OEIS A250000/A277433/A277434, Sinz counter) | Python (`src/`) |
| [`random-3sat-phase-transition/`](random-3sat-phase-transition/README.md) | CNF (`.cnf`) | **Original** *(classic ensemble, via [`@jasonslenderman`](https://twitter.com/jasonslenderman) & [`@tingan87`](https://twitter.com/tingan87))* | 8 | 4 / 4 | Uniform random 3-SAT across the phase transition $m/n \in [3.80, 5.00]$ ($n=200$) | Python (`src/`) |
| [`rb-bench-model-rb/`](rb-bench-model-rb/README.md) | CNF (`.cnf`) | **Sourced** — Ke Xu ([`rb-bench.github.io`](https://rb-bench.github.io/), AIJ 2007, via [`@merlin_numa`](https://twitter.com/merlin_numa)) | 40 | 40 / 0 | Model RB forced-satisfiable phase-transition CSP-to-SAT (`frb30-15`–`frb59-26`) | Python (`src/`) |
| [`sat-competition-2023-2024-selected/`](sat-competition-2023-2024-selected/README.md) | CNF (`.cnf`) | **Sourced** ([SC 23/24](https://satcompetition.github.io/) / [GBD](https://benchmark-database.de/), CC-BY-4.0) | 14 | 5 / 9 | 14 curated SC 2023/2024 Main Track CNFs across 11 domains (with GBD hashes) | Python + manifest (`src/`) |
| [`sat-competition-2024-2026-main-track/`](sat-competition-2024-2026-main-track/README.md) | CNF (URIs) | **Sourced** ([SC 24–26](https://satcompetition.github.io/) / [GBD](https://benchmark-database.de/), CC-BY-4.0) | 1,166* | Mixed | Complete SC 2024, 2025, 2026 Main Track GBD URI manifests & eval harness | Python + `.uri` (`src/`) |
| [`sat-shortcut-challenge/`](sat-shortcut-challenge/README.md) | CNF (`.cnf`) | **Sourced** — Keith Adler ([`@keithadler`](https://twitter.com/keithadler), [repo](https://github.com/keithadler/sat-shortcut-challenge), Apache-2.0) | 72 | Mixed | Complete Tier-1 (47 structured across 9 families) + Tier-3 (25 random 3-SAT, $n=300\text{--}500$) | Python + C (`src/`) |
| [`satlib-benchmarks/`](satlib-benchmarks/README.md) | CNF (`.cnf.xz`) | **Sourced** — Hoos & Stützle ([UBC SATLIB](https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html), SAT 2000, via [`@jasonslenderman`](https://twitter.com/jasonslenderman)) | 331 + 97* | Mixed | All 17 structured SATLIB/DIMACS/Beijing families (298) + 33 ensemble samples + 97 archive URIs | Python + `.uri` (`src/`) |
| [`sha256-preimage/`](sha256-preimage/README.md) | AIG (`.aig`) | **Original** *(FIPS 180-4)* | 5 | 4 / 1 | Exact FIPS 180-4 SHA-256 CSA preimages ($R = 16, 17, 64$; $k = 16, 20, 32$) | Rust (`src/`) |
| [`sigal-aes256-xcnf/`](sigal-aes256-xcnf/README.md) | XCNF (`.xcnf`) | **Sourced** — Victor Sigal ([`@uniexpertise`](https://twitter.com/uniexpertise)) | 2 | 1 SAT / 1 Open | Full 14-round NIST FIPS 197 AES-256 2-pair key recovery (500 Boyar–Peralta S-boxes, 42.8k XORs) | Python (`src/`) |
| [`tseitin-expanders/`](tseitin-expanders/README.md) | AIG (`.aig`) | **Original** *(classic family)* | 4 | 0 / 4 | $\mathrm{MOD}_2$-Tseitin 3-regular expanders & prism ($n=60\text{--}400$) | Rust (`src/`) |
| [`vlsat-2/`](vlsat-2/README.md) | CNF (`.cnf`) | **Sourced** — Garavel / CADP INRIA ([VLSAT-2](https://cadp.inria.fr/resources/vlsat/2.html), via [`@TravisRudd`](https://twitter.com/TravisRudd)) | 10 + 100* | 1 / 9 *(first 10)* | Very Large SAT from Nested-Unit Petri Net decompositions (first 10 + 100 URIs) | Python + `.uri` (`src/`) |
| [`zed-adversarial-hub-php/`](zed-adversarial-hub-php/README.md) | AIG (`.aig`) | **Original** | 18 | 3 / 15 | Bit-vector Hub disjunctions ($n=20\text{--}80$) & Pigeonhole ($\mathrm{PHP}^9_8\text{--}\mathrm{PHP}^{50}_{49}$) | Rust (`src/`) |

\* `sat-competition-2024-2026-main-track/` stores immutable GBD URI lists (`main_2024.uri`, `main_2025.uri`, `main_2026.uri`, 1,166 unique CNFs), `vlsat-2/vlsat2_100.uri` stores all 100 INRIA URLs, and `satlib-benchmarks/satlib_all_97_archives.uri` stores all 97 official UBC SATLIB `.tar.gz` archive URLs rather than duplicating multi-gigabyte raw archives in Git. Across the repository, **773 SAT benchmark instances** are committed in **all three formats** (**773** verified Binary AIGER 1.9 `.aig`, **773** DIMACS `.cnf`/`.cnf.xz`, and **773** [CryptoMiniSat](https://github.com/msoos/cryptominisat) `.xcnf`/`.xcnf.xz` = **2,319** benchmark files), alongside **174 `.mata.xz` NFA benchmarks** and full generator/converter scripts.

## Highlighted Solver Summary

### 1. Unified 50-Benchmark Flat-CNF Gauntlet (1-Core, Identical Flat `.cnf` Input)

- **Timeout:** Part I (30 circuit/algebraic instances): $T_{\max} = 5{,}000\;\text{s}$ per instance (PAR-2 penalty $10{,}000\;\text{s}$); Part II (20 adversarial Zed, SC 2023/2024, and Random 3-SAT instances): $T_{\max} = 600\;\text{s}$ per instance (PAR-2 penalty $1{,}200\;\text{s}$).
- **Same machine?** **Yes** — all five solvers were run sequentially on the exact same machine (**AMD Ryzen 9 5950X**, 16-core/32-thread, Linux, 1 core per run, exact median of 3 runs).

| Solver (1C) | Solved | Fastest Wins | Part I PAR-2 (30, $T_{\max}=5{,}000\;\text{s}$) | Part II PAR-2 (20, $T_{\max}=600\;\text{s}$) | Unified 50 PAR-2 |
|---|---:|---:|---:|---:|---:|
| **Frobenius 1C** | **50 / 50** | **50 / 50** | **430.02 ms** *(fastest)* | **4,309.00 ms** *(fastest)* | **4,739.02 ms** *(fastest)* |
| [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18.0 (XCNF) | 40 / 50 | 0 / 50 | 20,471,425.77 ms *(47,606x slower)* | 9,720,466.50 ms *(2,256x slower)* | 30,191,892.27 ms *(6,371x slower)* |
| [CaDiCaL](https://github.com/arminbiere/cadical) 3.1.0 | 38 / 50 | 0 / 50 | 25,715,225.61 ms *(59,800x slower)* | 12,017,694.26 ms *(2,789x slower)* | 37,732,919.87 ms *(7,962x slower)* |
| [Kissat](https://github.com/arminbiere/kissat) 4.0.4 | 40 / 50 | 0 / 50 | 35,047,925.98 ms *(81,503x slower)* | 8,651,994.22 ms *(2,008x slower)* | 43,699,920.20 ms *(9,221x slower)* |
| [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18.0 (CNF) | 35 / 50 | 0 / 50 | 30,027,443.01 ms *(69,828x slower)* | 14,462,626.48 ms *(3,356x slower)* | 44,490,069.49 ms *(9,388x slower)* |

### 2. 22-Instance Provable HAMD Suite (1-Core, Identical Flat `.cnf` Input)

- **Timeout:** $T_{\max} = 15\;\text{s}$ per instance (PAR-2 penalty $30\;\text{s}$).
- **Same machine?** **Yes** — all four solvers were run sequentially on the exact same machine (**AMD Ryzen 9 5950X**, 1 core per run, exact median of 3 runs).

| Solver (1C) | Solved | Fastest Wins | Total PAR-2 ($T_{\max}=15\;\text{s}$) | Proof / Model Verification |
|---|---:|---:|---:|---|
| **Frobenius 1C** | **22 / 22** | **19 / 22** | **372.43 ms** *(fastest)* | 12/12 SAT cycles + 10/10 UNSAT [`cake_lpr`](https://github.com/tanyongkiam/cake_lpr) + [`lrat-check`](https://github.com/marijnheule/drat-trim) OK |
| [Kissat](https://github.com/arminbiere/kissat) 4.0.4 | 18 / 22 | 1 / 22 | 140,869.50 ms *(378x slower)* | 100% verdict agreement on solved instances |
| [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18.0 (CNF) | 18 / 22 | 0 / 22 | 148,852.60 ms *(400x slower)* | 100% verdict agreement on solved instances |
| [CaDiCaL](https://github.com/arminbiere/cadical) 3.1.0 | 17 / 22 | 2 / 22 | 163,592.80 ms *(439x slower)* | 100% verdict agreement on solved instances |

### 3. Combinatorial Chessboard Suites (1-Core, Identical Flat `.cnf` Input)

- **Timeout:** $T_{\max} = 15\;\text{s}$ per instance (PAR-2 penalty $30\;\text{s}$).
- **Same machine?** **Yes** — all five solvers were run sequentially on the exact same **AMD Ryzen 9 5950X** Linux workstation (1 core per run, 0 verdict disagreements).

| Suite (Instances, $T_{\max}$) | Frobenius 1C | [CaDiCaL](https://github.com/arminbiere/cadical) 3.1.0 | [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18.0 | [`dense-solver 0.0.4`](https://github.com/libdense/dense-solver) | [Kissat](https://github.com/arminbiere/kissat) 4.0.4 |
|---|---:|---:|---:|---:|---:|
| [**Obstacle Knight's Tour**](knights-tour-obstacles/README.md) (10, 15 s) | 10/10 — 54,045 ms *(6.23x)* | 10/10 — 11,302 ms *(1.30x)* | 10/10 — 9,121 ms *(1.05x)* | 2/10 — 250,274 ms *(28.8x)* | **10/10 — 8,678 ms** *(fastest)* |
| [**Peaceable Queen Armies**](queen-armies/README.md) (8, 15 s) | **8/8 — 56,672 ms** *(fastest)* | 1/8 — 214,106 ms *(3.78x)* | 1/8 — 211,830 ms *(3.74x)* | 2/8 — 204,847 ms *(3.61x)* | 4/8 — 160,604 ms *(2.83x)* |

### 4. Imported External Benchmark Suites (1-Core, Identical Flat `.cnf` Input)

- **Timeout:** Per-instance $T_{\max}$ is listed in each row (PAR-2 penalty $= 2\,T_{\max}$).
- **Same machine?** **Yes** — all solvers were run sequentially on the exact same **AMD Ryzen 9 5950X** Linux workstation (1 core per run, 0 verdict disagreements).

| External Suite (Instances, $T_{\max}$) | Frobenius 1C | [CaDiCaL](https://github.com/arminbiere/cadical) 3.1.0 | [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18.0 | [`dense-solver 0.0.4`](https://github.com/libdense/dense-solver) | [Kissat](https://github.com/arminbiere/kissat) 4.0.4 |
|---|---:|---:|---:|---:|---:|
| [**Aloul FPGA Switch-Box**](aloul-symmetry-benchmarks/README.md) (21, 5 s) | 21/21 — 70.76 ms *(2.58x)* | 11/21 — 100,091 ms *(3,646x)* | — | **21/21 — 27.45 ms** *(fastest)* | 12/21 — 92,980 ms *(3,387x)* |
| [**`dense-solver` Public**](dense-solver-benchmarks/README.md) (30, 5 s) | **29/30 — 10,713 ms** *(fastest)* | 24/30 — 63,765 ms *(5.95x)* | 20/30 — 100,871 ms *(9.42x)* | 28/30 — 20,413 ms *(1.91x)* | 25/30 — 53,065 ms *(4.95x)* |
| [**`dense-solver` Synth + `cb368`**](dense-solver-benchmarks/README.md) (21, 5 s) | **21/21 — 245.60 ms** *(fastest)* | 14/21 — 70,983 ms *(289x)* | 14/21 — 71,525 ms *(291x)* | 21/21 — 466.92 ms *(1.90x)* | 14/21 — 70,568 ms *(287x)* |
| [**`mod-circuit-sat`**](mod-circuit-sat/README.md) $n=3\text{--}5$ (9, 30 s) | **9/9 — 17,346 ms** *(fastest)* | 9/9 — 29,702 ms *(1.71x)* | 8/9 — 67,344 ms *(3.88x)* | 8/9 — 67,769 ms *(3.91x)* | 9/9 — 25,994 ms *(1.50x)* |
| [**Model RB `frb30-15`**](rb-bench-model-rb/README.md) (5, 5 s) | 5/5 — 3,165 ms *(3.43x)* | 5/5 — 1,377 ms *(1.49x)* | — | — | **5/5 — 923.51 ms** *(fastest)* |
| [**Pretolani PRET**](pretolani-pret/README.md) (8, 5 s) | 8/8 — 9.86 ms *(1.53x)* | 8/8 — 41.53 ms *(6.46x)* | 8/8 — 161.74 ms *(25.2x)* | **8/8 — 6.43 ms** *(fastest)* | 8/8 — 58.45 ms *(9.09x)* |
| [**QDistSAT `BB_30..144`**](qdistsat-qldpc/README.md) (6, 10 s) | 5/6 — 20,685 ms *(1.03x)* | **5/6 — 20,072 ms** *(fastest)* | 5/6 — 20,495 ms *(1.02x)* | — | 5/6 — 20,081 ms *(1.00x)* |
| [**SAT Competition 2023/2024 Selected**](sat-competition-2023-2024-selected/README.md)\* (12, 600 s) | **12/12 — 3,745 ms** *(fastest)* | 5/12 — 8,417,003 ms *(2,248x)* | 3/12 — 10,859,841 ms *(2,900x)* | — | 8/12 — 5,051,149 ms *(1,349x)* |
| [**SAT Shortcut Challenge**](sat-shortcut-challenge/README.md) Tier-1 (47, 10 s) | **46/47 — 26,120 ms** *(fastest)* | 41/47 — 150,936 ms *(5.78x)* | 42/47 — 121,715 ms *(4.66x)* | 44/47 — 67,653 ms *(2.59x)* | 43/47 — 95,355 ms *(3.65x)* |
| [**SAT Shortcut Challenge**](sat-shortcut-challenge/README.md) Tier-3 $n=300$ (5, 15 s) | **3/5 — 60,028 ms** *(fastest)* | 3/5 — 61,966 ms *(1.03x)* | — | — | 3/5 — 62,585 ms *(1.04x)* |
| [**SATLIB Classic Collection**](satlib-benchmarks/README.md) (331, 5 s) | **318/331 — 148,122 ms** *(fastest)* | 316/331 — 174,263 ms *(1.18x)* | 323/331 — 161,168 ms *(1.09x)* | 313/331 — 207,236 ms *(1.40x)* | 314/331 — 189,824 ms *(1.28x)* |
| [**VLSAT-2 First 10**](vlsat-2/README.md) (10, 5 s) | **7/10 — 30,042 ms** *(fastest)* | 0/10 — 100,000 ms *(3.33x)* | — | — | 4/10 — 64,398 ms *(2.14x)* |

*\*`sat-competition-2023-2024-selected/` is also included in Part II of the Unified 50-Benchmark Flat-CNF Gauntlet (Section 1 above). Among the remaining external suites, [`heule-matrix-challenges/`](heule-matrix-challenges/README.md) targets open/hard $3\times 3$ matrix multiplication, [`mata-presburger-nfa/`](mata-presburger-nfa/README.md) contains non-CNF finite automata (`.mata.xz`), [`sigal-aes256-xcnf/`](sigal-aes256-xcnf/README.md) contains full 14-round AES-256 XCNF cryptanalytic challenges (throughput benchmarked in its suite README), and [`sat-competition-2024-2026-main-track/`](sat-competition-2024-2026-main-track/README.md) (cross-machine vs. official competition logs) is summarized in Section 5 below.*

### 5. SAT Competition 2024–2026 Main Track (1,166 Unique CNFs, 1-Core)

- **Timeout:** Evaluated at $T_{\max} = 15\;\text{s}$ and $T_{\max} = 60\;\text{s}$ cutoffs (official competition full runs used $T_{\max} = 5{,}000\;\text{s}$).
- **Same machine?** **No (different machines)** — Frobenius 1C ran on our local **AMD Ryzen 9 5950X** workstation (1 core per instance, unrestricted available RAM), whereas competitor scores are taken directly from official published competition logs/slides (**StarExec** cluster for SC 2024; **LMU / competition sequential clusters** for SC 2025–2026). CPU differences affect absolute runtimes, so ratios below reflect cross-machine published PAR-2 comparisons.

| Track (400 CNFs each) | Solver (1C) | $T_{\max}=15\;\text{s}$ Solved & PAR-2 | $T_{\max}=60\;\text{s}$ Solved & PAR-2 |
|---|---|---:|---:|
| **SC 2024** | **Frobenius 1C** | **72 / 400 — 25.04 s** *(fastest)* | **111 / 400 — 91.02 s** *(fastest)* |
| | [`kissat-sc2024`](https://github.com/arminbiere/kissat) (Main #1 Gold) | 43 / 400 — 27.15 s *(1.08x slower)* | 81 / 400 — 99.47 s *(1.09x slower)* |
| | [`CaDiCaL`](https://github.com/arminbiere/cadical) (Main #7) | 26 / 400 — 28.24 s *(1.13x slower)* | 54 / 400 — 106.69 s *(1.17x slower)* |
| **SC 2025** | **Frobenius 1C** | **95 / 400 — 23.51 s** | **141 / 400 — 81.92 s** |
| | *(Official SC 2025 published aggregate 5,000 s slide totals only; no per-instance CSV)* | — | — |
| **SC 2026** | **Frobenius 1C** | **122 / 400 — 21.37 s** *(fastest)* | **139 / 400 — 80.24 s** *(fastest)* |
| | [`Lymphosat`](https://c.mov/lymphosat/) (AI-Track #1 Gold) | 81 / 400 — 24.58 s *(1.15x slower)* | 109 / 400 — 90.07 s *(1.12x slower)* |
| | [`satsuma-iter-kissat`](https://github.com/markusa4/satsuma) (Main #1 Gold) | 70 / 400 — 25.13 s *(1.18x slower)* | 112 / 400 — 90.46 s *(1.13x slower)* |

<!-- BEGIN_STRUCTURAL_ANALYSIS -->
## Cross-Suite Phase-Transition & Structural Profile

*Auto-generated across all 771 committed SAT instances by [`src/analyze_benchmarks.py`](src/analyze_benchmarks.py). Each row summarizes where the suite sits relative to the clause-length-weighted critical threshold $\rho_{\mathrm{crit}} = \frac{1}{n}\sum_k m_k / \alpha_c(k)$ (`Under` $<0.90\times$, `Near-crit` $0.90\text{--}1.10\times$, `Over` $>1.10\times$), Gent–Walsh constrainedness $\kappa$, clause geometry ($\bar{k}$, `%Bin`, `%Horn`), variable-degree skew (`Deg CV`), and extracted XOR parity blocks.*

| Suite | CNFs | Med $\alpha$ | Med $\alpha_c^{\mathrm{eff}}$ | Med $\rho_{\mathrm{crit}}$ [Min–Max] | Regime Split (U/N/O) | Med $\kappa$ | Med $\bar{k}$ | Bin% | Horn% | Deg CV | XORs |
|---|---:|---:|---:|---:|:---:|---:|---:|---:|---:|---:|---:|
| [`aloul-symmetry-benchmarks/`](aloul-symmetry-benchmarks/README.md) | 82 | 5.59 | 1.20 | **3.43x** [0.31x–9.75x] | 6 / 0 / 76 | 1.43 | 2.72 | 82% | 82% | 0.19 | 15,433 |
| [`cec-arithmetic-miters/`](cec-arithmetic-miters/README.md) | 5 | 5.20 | 3.69 | **1.36x** [1.36x–1.64x] | 0 / 0 / 5 | 0.91 | 3.30 | 12% | 56% | 0.35 | 831 |
| [`coupled-linear-nonlinear/`](coupled-linear-nonlinear/README.md) | 4 | 4.08 | 3.48 | **1.18x** [1.14x–1.22x] | 0 / 0 / 4 | 0.99 | 3.11 | 3% | 49% | 0.86 | 1,987 |
| [`dense-solver-benchmarks/`](dense-solver-benchmarks/README.md) | 50 | 3.97 | 1.16 | **2.17x** [0.48x–32.0x] | 4 / 12 / 34 | 1.01 | 2.28 | 84% | 85% | 0.20 | 323 |
| [`f2-frobenius-circulants/`](f2-frobenius-circulants/README.md) | 6 | 4.50 | 4.98 | **0.90x** [0.90x–0.91x] | 0 / 6 / 0 | 0.87 | 3.67 | 0% | 56% | 0.45 | 8,000 |
| [`hamd-hamiltonian-cycle/`](hamd-hamiltonian-cycle/README.md) | 22 | 2.64 | 2.60 | **0.99x** [0.75x–1.31x] | 6 / 7 / 9 | 0.54 | 3.19 | 28% | 73% | 0.71 | 0 |
| [`hard-spn/`](hard-spn/README.md) | 4 | 5.67 | 5.31 | **1.07x** [1.06x–1.11x] | 0 / 3 / 1 | 0.92 | 3.60 | 2% | 51% | 1.27 | 1,328 |
| [`heule-matrix-challenges/`](heule-matrix-challenges/README.md) | 43 | 4.48 | 2.43 | **1.83x** [1.82x–2.68x] | 0 / 0 / 43 | 0.95 | 3.20 | 32% | 73% | 0.95 | 253,692 |
| [`integer-factoring/`](integer-factoring/README.md) | 6 | 5.24 | 3.49 | **1.50x** [1.48x–1.51x] | 0 / 0 / 6 | 0.98 | 3.27 | 13% | 59% | 0.41 | 1,844 |
| [`knights-tour-obstacles/`](knights-tour-obstacles/README.md) | 10 | 2.77 | 2.87 | **0.97x** [0.96x–1.04x] | 0 / 10 / 0 | 0.54 | 3.29 | 24% | 74% | 1.05 | 0 |
| [`mod-circuit-sat/`](mod-circuit-sat/README.md) | 11 | 20.07 | 2.70 | **7.52x** [3.24x–14.2x] | 0 / 0 / 11 | 4.03 | 3.41 | 27% | 73% | 1.10 | 0 |
| [`pretolani-pret/`](pretolani-pret/README.md) | 8 | 2.67 | 4.27 | **0.62x** [0.62x–0.62x] | 8 / 0 / 0 | 0.51 | 3.00 | 0% | 51% | 0.00 | 560 |
| [`qdistsat-qldpc/`](qdistsat-qldpc/README.md) | 10 | 2.40 | 1.92 | **1.24x** [1.22x–1.25x] | 0 / 0 / 10 | 0.66 | 2.63 | 37% | 75% | 1.02 | 1,474 |
| [`queen-armies/`](queen-armies/README.md) | 8 | 2.04 | 1.48 | **1.39x** [1.29x–1.48x] | 0 / 0 / 8 | 0.66 | 2.42 | 58% | 58% | 0.68 | 0 |
| [`random-3sat-phase-transition/`](random-3sat-phase-transition/README.md) | 8 | 4.26 | 4.27 | **1.00x** [0.89x–1.17x] | 1 / 6 / 1 | 0.82 | 3.00 | 0% | 51% | 0.28 | 0 |
| [`rb-bench-model-rb/`](rb-bench-model-rb/README.md) | 40 | 69.47 | 1.00 | **69.4x** [42.3x–86.2x] | 0 / 0 / 40 | 28.81 | 2.01 | 100% | 100% | 0.19 | 0 |
| [`sat-competition-2023-2024-selected/`](sat-competition-2023-2024-selected/README.md) | 14 | 4.00 | 1.91 | **1.92x** [0.37x–62.9x] | 3 / 2 / 9 | 0.97 | 2.68 | 39% | 63% | 0.28 | 71,848 |
| [`sat-shortcut-challenge/`](sat-shortcut-challenge/README.md) | 72 | 4.26 | 4.27 | **1.00x** [0.62x–72.0x] | 9 / 33 / 30 | 0.82 | 3.00 | 0% | 52% | 0.27 | 6,793 |
| [`satlib-benchmarks/`](satlib-benchmarks/README.md) | 331 | 4.97 | 3.47 | **1.48x** [0.32x–62.7x] | 75 / 22 / 234 | 0.91 | 2.99 | 10% | 52% | 0.18 | 36,542 |
| [`sha256-preimage/`](sha256-preimage/README.md) | 5 | 6.50 | 5.58 | **1.16x** [1.16x–1.23x] | 0 / 0 / 5 | 0.94 | 3.52 | 2% | 50% | 0.65 | 77,329 |
| [`sigal-aes256-xcnf/`](sigal-aes256-xcnf/README.md) | 2 | 6.78 | 3.85 | **1.76x** [1.76x–1.76x] | 0 / 0 / 2 | 1.08 | 3.53 | 15% | 54% | 1.14 | 85,624 |
| [`tseitin-expanders/`](tseitin-expanders/README.md) | 4 | 3.60 | 4.98 | **0.72x** [0.72x–0.72x] | 4 / 0 / 0 | 0.70 | 3.67 | 0% | 56% | 0.26 | 880 |
| [`vlsat-2/`](vlsat-2/README.md) | 10 | 15.52 | 1.00 | **15.5x** [13.7x–22.2x] | 0 / 0 / 10 | 6.42 | 2.04 | 100% | 100% | 0.33 | 0 |
| [`zed-adversarial-hub-php/`](zed-adversarial-hub-php/README.md) | 18 | 3.44 | 1.25 | **2.76x** [1.42x–3.08x] | 0 / 0 / 18 | 1.69 | 2.03 | 51% | 97% | 1.38 | 10,146 |
<!-- END_STRUCTURAL_ANALYSIS -->

## Format Conventions

- **Binary AIGER 1.9 (`.aig`):** Standard Armin Biere combinational AIGER format (`aig M I 0 1 A`) with `L = 0` latches and `O = 1` primary output `PO_0` that evaluates to `1` iff all circuit assertions / CNF clauses are satisfied. Readable directly by Berkeley [`abc`](https://github.com/berkeley-abc/abc), `aigtoaig`, `aigtocnf`, [Yosys](https://github.com/YosysHQ/yosys), and HWMCC toolchains.
- **DIMACS CNF / XCNF (`.cnf`, `.xcnf`):** Standard SAT Competition `p cnf <vars> <clauses>` format; `.xcnf` files include native [CryptoMiniSat](https://github.com/msoos/cryptominisat) `x l1 ... lk 0` XOR parity clauses.
- **MATA Automata (`.mata.xz`):** Standard VeriFIT `.mata` NFA format stored xz-compressed.

## License

- Repository-authored original suites and generator/conversion scripts are licensed under the **MIT License** — see [`LICENSE`](LICENSE).
- Sourced suites retain their original upstream licenses, notices, and provenance links inside their respective directories:
  - [`sat-competition-2023-2024-selected/LICENSE`](sat-competition-2023-2024-selected/LICENSE) & [`sat-competition-2024-2026-main-track/LICENSE`](sat-competition-2024-2026-main-track/LICENSE) — Creative Commons Attribution 4.0 International (**CC-BY-4.0**) for SAT Competition / GBD archives + MIT for scripts.
  - [`sat-shortcut-challenge/LICENSE`](sat-shortcut-challenge/LICENSE) — **Apache License 2.0** (`keithadler/sat-shortcut-challenge`).
  - [`dense-solver-benchmarks/LICENSE`](dense-solver-benchmarks/LICENSE) & [`SOURCES.md`](dense-solver-benchmarks/SOURCES.md) — **MIT License** (`libdense/dense-solver`) + preserved SATLIB / SC 2025 attributions.
  - [`mata-presburger-nfa/LICENSE`](mata-presburger-nfa/LICENSE) — **MIT License** (`VeriFIT/mata`).
  - [`qdistsat-qldpc/LICENSE`](qdistsat-qldpc/LICENSE) & [`NOTICE`](qdistsat-qldpc/NOTICE) — **GNU General Public License v3.0 or later (`GPL-3.0-or-later`)** (`guluchen/QDistSAT` / `DistQLDPC`, with retained `codeDistancePYPI` MIT notices).
  - Public academic archives and community-contributed suites without dedicated upstream `LICENSE` files (`heule-matrix-challenges`, `vlsat-2`, `aloul-symmetry-benchmarks`, `rb-bench-model-rb`, `pretolani-pret`, `mod-circuit-sat`, `satlib-benchmarks`, `sigal-aes256-xcnf`) carry explicit author attributions, papers, and upstream links in each suite's `README.md`.
