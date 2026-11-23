# SAT Benchmarks

A curated, **three-format** (**Binary AIGER 1.9 `.aig`**, **DIMACS `.cnf`**, and **CryptoMiniSat `.xcnf`**) collection of **24 benchmark suites** spanning Boolean satisfiability, circuit inversion, algebraic cryptanalysis, quantum LDPC code distance, matrix multiplication, graph theory, combinatorial chessboard puzzles, symmetry breaking, exact circuit synthesis, hardware verification, finite-automata complementation, and SAT Competition corpora.

Every benchmark suite lives in its own top-level directory containing:
- Native-format benchmark instances at the suite root (`.aig` for circuit-native suites; `.cnf` / `.cnf.xz` for clausal suites; `.mata.xz` for the MATA automata suite).
- Exact conversions for the two remaining formats in subdirectories:
  - Originally-`.aig` suites provide `cnf-version/` (`.cnf`) and `xcnf-version/` (`.xcnf`).
  - Originally-`.cnf` suites provide `aig-version/` (`.aig`) and `xcnf-version/` (`.xcnf` / `.xcnf.xz`, with all complete $2^{k-1}$-clause XOR parity blocks collapsed losslessly to native `x l1 ... lk 0` lines).
  - Every single `.aig` file across all suites (**387 / 387**) conforms to **Binary AIGER 1.9** (`L = 0`, `O = 1` combinational miter where `PO_0 = 1` iff SAT) and has been independently verified with Berkeley **ABC** (`read_aiger`, `0` errors).
- Standalone generator, exporter, fetcher, or converter source code in `src/` (including `cnf2aig.py` and `cnf2xcnf.py`).
- A detailed `README.md` documenting provenance, contributor credits, upstream links and licenses, mathematical/circuit parameters, exact data sizes, comparative 1-core solver timings (Frobenius 1C, `dense-solver 0.0.4`, Kissat 4.0.4, CaDiCaL 3.1.0, CryptoMiniSat 5.18.0 CNF & XCNF), proof verification status (`cake_lpr` / `lrat-check`), and literature citations.

## Benchmark Suites (24 Suites)

| Suite | Origin Format | Provenance & Credit | Instances | SAT / UNSAT | Domain & Structural Focus | Generator / Scripts |
|---|---|---|---:|:---:|---|---|
| [`f2-frobenius-circulants/`](f2-frobenius-circulants/README.md) | AIG (`.aig`) | **Original** | 6 | 4 / 2 | Balanced $\mathbb{F}_2$ circulant parity circuits ($n=64\text{--}4{,}096$) | Rust (`src/`) |
| [`tseitin-expanders/`](tseitin-expanders/README.md) | AIG (`.aig`) | **Original** *(classic family)* | 4 | 0 / 4 | $\mathrm{MOD}_2$-Tseitin 3-regular expanders & prism ($n=60\text{--}400$) | Rust (`src/`) |
| [`coupled-linear-nonlinear/`](coupled-linear-nonlinear/README.md) | AIG (`.aig`) | **Original** | 4 | 3 / 1 | Coupled $\mathbb{F}_2$ linear + nonlinear $\mathrm{And}/\mathrm{Maj}_3/\mathrm{Mux}$ circuits | Rust (`src/`) |
| [`hard-spn/`](hard-spn/README.md) | AIG (`.aig`) | **Original** | 4 | 3 / 1 | LowMC-style linear-form + S-box SPN algebraic cryptanalysis | Rust (`src/`) |
| [`integer-factoring/`](integer-factoring/README.md) | AIG (`.aig`) | **Original** *(classic problem)* | 6 | 5 / 1 | Wallace & Karatsuba multiplier inversion (28–40b) + XOR-masked mult | Rust (`src/`) |
| [`sha256-preimage/`](sha256-preimage/README.md) | AIG (`.aig`) | **Original** *(FIPS 180-4)* | 5 | 4 / 1 | Exact FIPS 180-4 SHA-256 CSA preimages ($R = 16, 17, 64$; $k = 16, 20, 32$) | Rust (`src/`) |
| [`cec-arithmetic-miters/`](cec-arithmetic-miters/README.md) | AIG (`.aig`) | **Original** *(classic EDA)* | 5 | 0 / 5 | EDA CEC miters: Ripple-Carry vs. Kogge–Stone; Array vs. Wallace vs. Karatsuba | Rust (`src/`) |
| [`zed-adversarial-hub-php/`](zed-adversarial-hub-php/README.md) | AIG (`.aig`) | **Original** | 18 | 3 / 15 | Bit-vector Hub disjunctions ($n=20\text{--}80$) & Pigeonhole ($\mathrm{PHP}^9_8\text{--}\mathrm{PHP}^{50}_{49}$) | Rust (`src/`) |
| [`hamd-hamiltonian-cycle/`](hamd-hamiltonian-cycle/README.md) | CNF (`.cnf`) | **Original** *(classic graphs)* | 22 | 12 / 10 | 6 provably SAT/UNSAT graph families ($GP$, Snarks, Meredith, Chvátal, Broken Crown, Planted) | Rust (`src/`) |
| [`random-3sat-phase-transition/`](random-3sat-phase-transition/README.md) | CNF (`.cnf`) | **Original** *(classic ensemble)* | 2 | 1 / 1 | Uniform random 3-SAT at critical phase transition $m/n = 4.26$ ($n=200$) | Python (`src/`) |
| [`sat-competition-2023-2024-selected/`](sat-competition-2023-2024-selected/README.md) | CNF (`.cnf`) | **Sourced** ([SC 23/24](https://satcompetition.github.io/) / [GBD](https://benchmark-database.de/), CC-BY-4.0) | 14 | 5 / 9 | 14 curated SC 2023/2024 Main Track CNFs across 11 domains (with GBD hashes) | Python + manifest (`src/`) |
| [`sat-competition-2024-2026-main-track/`](sat-competition-2024-2026-main-track/README.md) | CNF (URIs) | **Sourced** ([SC 24–26](https://satcompetition.github.io/) / [GBD](https://benchmark-database.de/), CC-BY-4.0) | 1,166* | Mixed | Complete SC 2024, 2025, 2026 Main Track GBD URI manifests & eval harness | Python + `.uri` (`src/`) |
| [`sat-shortcut-challenge/`](sat-shortcut-challenge/README.md) | CNF (`.cnf`) | **Sourced** — Keith Adler (`@keithadler`, [repo](https://github.com/keithadler/sat-shortcut-challenge), Apache-2.0) | 25 | Mixed | Tier-3 uniform random 3-SAT ($n=300\text{--}500$, $m/n=4.26$) + Tier-1 generators | Python (`src/`) |
| [`heule-matrix-challenges/`](heule-matrix-challenges/README.md) | CNF (`.cnf.xz`) | **Sourced** — Heule, Kauers, Seidl ([repo](https://github.com/marijnheule/matrix-challenges), via `@SMT_Solvers`) | 43 | Mixed / Open | $3\times 3$ matrix multiplication over $\mathbb{F}_2$ ($R=22, 23$, SAT 2019) | C + Python (`src/`) |
| [`vlsat-2/`](vlsat-2/README.md) | CNF (`.cnf`) | **Sourced** — Garavel / CADP INRIA ([VLSAT-2](https://cadp.inria.fr/resources/vlsat/2.html), via `@TravisRudd`) | 10 + 100* | 1 / 9 *(first 10)* | Very Large SAT from Nested-Unit Petri Net decompositions (first 10 + 100 URIs) | Python + `.uri` (`src/`) |
| [`mata-presburger-nfa/`](mata-presburger-nfa/README.md) | NFA (`.mata.xz`) | **Sourced** — VeriFIT MATA ([`nfa-bench`](https://github.com/VeriFIT/nfa-bench), MIT, via `@TravisRudd`) | 174 | Automata | TACAS 2024 Presburger explicit-complement NFA benchmark set | Python (`src/`) |
| [`qdistsat-qldpc/`](qdistsat-qldpc/README.md) | Matrices / CNF | **Sourced** — [`QDistSAT`](https://github.com/guluchen/QDistSAT) (GPL-3.0+) & Bravyi et al., via `@TravisRudd` | 10 | 5 / 5 | CSS Quantum LDPC bivariate-bicycle code distance ($[[30..756]]$, `.cnf`/`.xcnf`/`.aig`) | Python (`src/`) |
| [`aloul-symmetry-benchmarks/`](aloul-symmetry-benchmarks/README.md) | CNF (`.cnf`) | **Sourced** — Fadi A. Aloul ([`aloul.net`](https://www.aloul.net/benchmarks.html), DAC 2002, via `@merlin_numa`) | 82 | Mixed | Symmetry-rich FPGA switch-box (Homer/Bart), routing, Urquhart, Array/Wallace factoring | Python (`src/`) |
| [`rb-bench-model-rb/`](rb-bench-model-rb/README.md) | CNF (`.cnf`) | **Sourced** — Ke Xu ([`rb-bench.github.io`](https://rb-bench.github.io/), AIJ 2007, via `@merlin_numa`) | 40 | 40 / 0 | Model RB forced-satisfiable phase-transition CSP-to-SAT (`frb30-15`–`frb59-26`) | Python (`src/`) |
| [`dense-solver-benchmarks/`](dense-solver-benchmarks/README.md) | CNF (`.cnf`) | **Sourced** — Merlin Numa (`@merlin_numa`, [`dense-solver`](https://github.com/libdense/dense-solver), [Zenodo](https://zenodo.org/records/24443907), MIT) | 50 | 18 / 32 | Multi-encoding PHP ($\mathrm{PHP}^{65}_{64}$), mutilated chessboards, 22 SATLIB + 8 SC25 CNFs | Python (`src/`) |
| [`pretolani-pret/`](pretolani-pret/README.md) | CNF (`.cnf`) | **Sourced** — Daniele Pretolani ([SATLIB PRET](https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/DIMACS/PRET/descr.html), via `@MMarchidann`) | 8 | 0 / 8 | Parity-charged graph 2-coloring UNSAT formulas ($n=60, 150$; 25%–75% Horn) | Python (`src/`) |
| [`mod-circuit-sat/`](mod-circuit-sat/README.md) | CNF (`.cnf`) | **Sourced** — `@vzhilin_me` ([`vzhn/mod-circuit-sat`](https://github.com/vzhn/mod-circuit-sat), arXiv:2102.12579) | 11 | 5 / 4 / 2 Open | Exact optimal $B_2$ circuit synthesis for $\mathrm{MOD}_n^{3,r}$ ($n=3\text{--}6$) | Python (`src/`) |
| [`queen-armies/`](queen-armies/README.md) | CNF (`.cnf`) | **Original** *(inspired by [Christopher Wolfram](https://christopherwolfram.com/projects/queen-armies/))* | 8 | 4 / 4 | Peaceable Queen Armies ($A \in \{2, 3, 4\}$, OEIS A250000/A277433/A277434, Sinz counter) | Python (`src/`) |
| [`knights-tour-obstacles/`](knights-tour-obstacles/README.md) | CNF (`.cnf`) | **Original** | 10 | 5 / 5 | Obstacle Knight's Tour Hamiltonian cycles on punched $12\times 12\text{--}16\times 16$ boards ($d=0.15\text{--}0.26$) | Python (`src/`) |

\* `sat-competition-2024-2026-main-track/` stores immutable GBD URI lists (`main_2024.uri`, `main_2025.uri`, `main_2026.uri`, 1,166 unique CNFs) and `vlsat-2/vlsat2_100.uri` stores all 100 INRIA URLs rather than duplicating multi-gigabyte raw archives in Git. Across the repository, **387 SAT benchmark instances** are committed in **all three formats** (**387** verified Binary AIGER 1.9 `.aig`, **387** DIMACS `.cnf`/`.cnf.xz`, and **387** CryptoMiniSat `.xcnf`/`.xcnf.xz` = **1,161** benchmark files), alongside **174 `.mata.xz` NFA benchmarks** and full generator/converter scripts.

## Highlighted Solver Summary

### 1. Unified 50-Benchmark Flat-CNF Gauntlet (1-Core, Identical Flat `.cnf` Input)

- **Timeout:** Part I (30 circuit/algebraic instances): $T_{\max} = 5{,}000\;\text{s}$ per instance (PAR-2 penalty $10{,}000\;\text{s}$); Part II (20 adversarial Zed, SC 2023/2024, and Random 3-SAT instances): $T_{\max} = 600\;\text{s}$ per instance (PAR-2 penalty $1{,}200\;\text{s}$).
- **Same machine?** **Yes** — all five solvers were run sequentially on the exact same machine (**AMD Ryzen 9 5950X**, 16-core/32-thread, Linux, 1 core per run, exact median of 3 runs).

| Solver (1C) | Solved | Fastest Wins | Part I PAR-2 (30, $T_{\max}=5{,}000\;\text{s}$) | Part II PAR-2 (20, $T_{\max}=600\;\text{s}$) | Unified 50 PAR-2 |
|---|---:|---:|---:|---:|---:|
| **Frobenius 1C** | **50 / 50** | **50 / 50** | **430.02 ms** *(fastest)* | **4,309.00 ms** *(fastest)* | **4,739.02 ms** *(fastest)* |
| CryptoMiniSat 5.18.0 (XCNF) | 40 / 50 | 0 / 50 | 20,471,425.77 ms *(47,606x slower)* | 9,720,466.50 ms *(2,256x slower)* | 30,191,892.27 ms *(6,371x slower)* |
| CaDiCaL 3.1.0 | 38 / 50 | 0 / 50 | 25,715,225.61 ms *(59,800x slower)* | 12,017,694.26 ms *(2,789x slower)* | 37,732,919.87 ms *(7,962x slower)* |
| Kissat 4.0.4 | 40 / 50 | 0 / 50 | 35,047,925.98 ms *(81,503x slower)* | 8,651,994.22 ms *(2,008x slower)* | 43,699,920.20 ms *(9,221x slower)* |
| CryptoMiniSat 5.18.0 (CNF) | 35 / 50 | 0 / 50 | 30,027,443.01 ms *(69,828x slower)* | 14,462,626.48 ms *(3,356x slower)* | 44,490,069.49 ms *(9,388x slower)* |

### 2. 22-Instance Provable HAMD Suite (1-Core, Identical Flat `.cnf` Input)

- **Timeout:** $T_{\max} = 15\;\text{s}$ per instance (PAR-2 penalty $30\;\text{s}$).
- **Same machine?** **Yes** — all four solvers were run sequentially on the exact same machine (**AMD Ryzen 9 5950X**, 1 core per run, exact median of 3 runs).

| Solver (1C) | Solved | Fastest Wins | Total PAR-2 ($T_{\max}=15\;\text{s}$) | Proof / Model Verification |
|---|---:|---:|---:|---|
| **Frobenius 1C** | **22 / 22** | **19 / 22** | **372.43 ms** *(fastest)* | 12/12 SAT cycles + 10/10 UNSAT `cake_lpr` + `lrat-check` OK |
| Kissat 4.0.4 | 18 / 22 | 1 / 22 | 140,869.50 ms *(378x slower)* | 100% verdict agreement on solved instances |
| CryptoMiniSat 5.18.0 (CNF) | 18 / 22 | 0 / 22 | 148,852.60 ms *(400x slower)* | 100% verdict agreement on solved instances |
| CaDiCaL 3.1.0 | 17 / 22 | 2 / 22 | 163,592.80 ms *(439x slower)* | 100% verdict agreement on solved instances |

### 3. Newly Imported & Combinatorial Suites (1-Core, Identical Flat `.cnf` Input)

- **Timeout:** $T_{\max} = 5\;\text{s}$ per instance (PAR-2 penalty $10\;\text{s}$), except `mod-circuit-sat` ($T_{\max} = 10\;\text{s}$) and `queen-armies` / `knights-tour-obstacles` ($T_{\max} = 15\;\text{s}$, PAR-2 penalty $30\;\text{s}$).
- **Same machine?** **Yes** — all solvers run sequentially on the exact same **AMD Ryzen 9 5950X** Linux workstation (1 core per run, 0 verdict disagreements).

| Suite (Instances, $T_{\max}$) | Frobenius 1C | `dense-solver 0.0.4` | Kissat 4.0.4 | CaDiCaL 3.1.0 | CryptoMiniSat 5.18.0 |
|---|---:|---:|---:|---:|---:|
| **`dense-solver` Public (30, 5 s)** | **29/30 — 10,550 ms** *(fastest)* | 28/30 — 20,413 ms *(1.93x)* | 25/30 — 53,065 ms *(5.03x)* | 24/30 — 63,765 ms *(6.04x)* | 20/30 — 100,871 ms *(9.56x)* |
| **`dense-solver` Synth + `cb368` (21, 5 s)** | **21/21 — 323.84 ms** *(fastest)* | 21/21 — 466.92 ms *(1.44x)* | 14/21 — 70,568 ms *(218x)* | 14/21 — 70,983 ms *(219x)* | 14/21 — 71,525 ms *(221x)* |
| **VLSAT-2 First 10 (10, 5 s)** | **7/10 — 30,042 ms** *(fastest)* | — | 4/10 — 64,398 ms *(2.14x)* | 0/10 — 100,000 ms *(3.33x)* | — |
| **Pretolani PRET (8, 5 s)** | 8/8 — 9.86 ms *(1.53x)* | **8/8 — 6.43 ms** *(fastest)* | 8/8 — 58.45 ms *(9.09x)* | 8/8 — 41.53 ms *(6.46x)* | 8/8 — 161.74 ms *(25.2x)* |
| **Aloul FPGA Switch-Box (21, 5 s)** | 21/21 — 219.53 ms *(8.00x)* | **21/21 — 27.45 ms** *(fastest)* | 12/21 — 92,980 ms *(3,387x)* | 11/21 — 100,091 ms *(3,646x)* | — |
| **Model RB `frb30-15` (5, 5 s)** | 5/5 — 3,165 ms *(3.43x)* | — | **5/5 — 923.51 ms** *(fastest)* | 5/5 — 1,377 ms *(1.49x)* | — |
| **`mod-circuit-sat` $n=3\text{--}5$ (9, 10 s)** | 8/9 — 30,054 ms *(1.20x)* | — | **8/9 — 25,054 ms** *(fastest)* | 8/9 — 27,363 ms *(1.09x)* | — |
| **Peaceable Queen Armies (8, 15 s)** | **8/8 — 56,672 ms** *(fastest)* | 2/8 — 204,847 ms *(3.61x)* | 4/8 — 160,604 ms *(2.83x)* | 1/8 — 214,106 ms *(3.78x)* | 1/8 — 211,830 ms *(3.74x)* |
| **Obstacle Knight's Tour (10, 15 s)** | 10/10 — 54,045 ms *(6.23x)* | 2/10 — 250,274 ms *(28.8x)* | **10/10 — 8,678 ms** *(fastest)* | 10/10 — 11,302 ms *(1.30x)* | 10/10 — 9,121 ms *(1.05x)* |

### 4. SAT Competition 2024–2026 Main Track (1,166 Unique CNFs, 1-Core)

- **Timeout:** Evaluated at $T_{\max} = 15\;\text{s}$ and $T_{\max} = 60\;\text{s}$ cutoffs (official competition full runs used $T_{\max} = 5{,}000\;\text{s}$).
- **Same machine?** **No (different machines)** — Frobenius 1C ran on our local **AMD Ryzen 9 5950X** workstation (1 core per instance, unrestricted available RAM), whereas competitor scores are taken directly from official published competition logs/slides (**StarExec** cluster for SC 2024; **LMU / competition sequential clusters** for SC 2025–2026). CPU differences affect absolute runtimes, so ratios below reflect cross-machine published PAR-2 comparisons.

| Track (400 CNFs each) | Solver (1C) | $T_{\max}=15\;\text{s}$ Solved & PAR-2 | $T_{\max}=60\;\text{s}$ Solved & PAR-2 |
|---|---|---:|---:|
| **SC 2024** | **Frobenius 1C** | **72 / 400 — 25.04 s** *(fastest)* | **111 / 400 — 91.02 s** *(fastest)* |
| | `kissat-sc2024` (Main #1 Gold) | 43 / 400 — 27.15 s *(1.08x slower)* | 81 / 400 — 99.47 s *(1.09x slower)* |
| | `CaDiCaL` (Main #7) | 26 / 400 — 28.24 s *(1.13x slower)* | 54 / 400 — 106.69 s *(1.17x slower)* |
| **SC 2025** | **Frobenius 1C** | **95 / 400 — 23.51 s** | **141 / 400 — 81.92 s** |
| | *(Official SC 2025 published aggregate 5,000 s slide totals only; no per-instance CSV)* | — | — |
| **SC 2026** | **Frobenius 1C** | **122 / 400 — 21.37 s** *(fastest)* | **139 / 400 — 80.24 s** *(fastest)* |
| | `Lymphosat` (AI-Track #1 Gold) | 81 / 400 — 24.58 s *(1.15x slower)* | 109 / 400 — 90.07 s *(1.12x slower)* |
| | `satsuma-iter-kissat` (Main #1 Gold) | 70 / 400 — 25.13 s *(1.18x slower)* | 112 / 400 — 90.46 s *(1.13x slower)* |

## Format Conventions

- **Binary AIGER 1.9 (`.aig`):** Standard Armin Biere combinational AIGER format (`aig M I 0 1 A`) with `L = 0` latches and `O = 1` primary output `PO_0` that evaluates to `1` iff all circuit assertions / CNF clauses are satisfied. Readable directly by Berkeley `abc`, `aigtoaig`, `aigtocnf`, Yosys, and HWMCC toolchains.
- **DIMACS CNF / XCNF (`.cnf`, `.xcnf`):** Standard SAT Competition `p cnf <vars> <clauses>` format; `.xcnf` files include native CryptoMiniSat `x l1 ... lk 0` XOR parity clauses.
- **MATA Automata (`.mata.xz`):** Standard VeriFIT `.mata` NFA format stored xz-compressed.

## License

- Repository-authored original suites and generator/conversion scripts are licensed under the **MIT License** — see [`LICENSE`](LICENSE).
- Sourced suites retain their original upstream licenses, notices, and provenance links inside their respective directories:
  - [`sat-competition-2023-2024-selected/LICENSE`](sat-competition-2023-2024-selected/LICENSE) & [`sat-competition-2024-2026-main-track/LICENSE`](sat-competition-2024-2026-main-track/LICENSE) — Creative Commons Attribution 4.0 International (**CC-BY-4.0**) for SAT Competition / GBD archives + MIT for scripts.
  - [`sat-shortcut-challenge/LICENSE`](sat-shortcut-challenge/LICENSE) — **Apache License 2.0** (`keithadler/sat-shortcut-challenge`).
  - [`dense-solver-benchmarks/LICENSE`](dense-solver-benchmarks/LICENSE) & [`SOURCES.md`](dense-solver-benchmarks/SOURCES.md) — **MIT License** (`libdense/dense-solver`) + preserved SATLIB / SC 2025 attributions.
  - [`mata-presburger-nfa/LICENSE`](mata-presburger-nfa/LICENSE) — **MIT License** (`VeriFIT/mata`).
  - [`qdistsat-qldpc/LICENSE`](qdistsat-qldpc/LICENSE) & [`NOTICE`](qdistsat-qldpc/NOTICE) — **GNU General Public License v3.0 or later (`GPL-3.0-or-later`)** (`guluchen/QDistSAT` / `DistQLDPC`, with retained `codeDistancePYPI` MIT notices).
  - Public academic archives without dedicated upstream `LICENSE` files (`heule-matrix-challenges`, `vlsat-2`, `aloul-symmetry-benchmarks`, `rb-bench-model-rb`, `pretolani-pret`, `mod-circuit-sat`) carry explicit author attributions, papers, and upstream links in each suite's `README.md`.
