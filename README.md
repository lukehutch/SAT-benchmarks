# SAT Benchmarks

A curated, dual-format (**Binary AIGER 1.9 `.aig`** and **DIMACS `.cnf` / `.xcnf`**) collection of Boolean satisfiability, circuit-inversion, algebraic, graph-theoretic, hardware-verification, and SAT Competition benchmark suites developed and imported during the development of the **Frobenius** SAT/circuit solver.

Every benchmark suite lives in its own top-level directory containing:
- Native-format benchmark instances at the suite root (`.aig` for circuit-native suites; `.cnf` for clausal suites).
- Exact dual-format conversions in `cnf-version/` (for originally-AIG suites) or `aig-version/` (for originally-CNF suites). Every single `.aig` file across all suites (**90 / 90**) conforms to **Binary AIGER 1.9** (`L = 0`, `O = 1` combinational miter where `PO_0 = 1` iff SAT) and has been independently verified with Berkeley **ABC** (`read_aiger` + `sat` spot-checks).
- Standalone, zero-dependency generator / fetcher / converter source code in `src/`.
- A detailed `README.md` documenting provenance, upstream links and licenses, mathematical/circuit parameters, exact data sizes, comparative 1-core solver timings (Frobenius 1C, Kissat 4.0.4, CaDiCaL 3.1.0, CryptoMiniSat 5.18.0 CNF & XCNF), proof verification status (`cake_lpr` / `lrat-check`), and literature citations.

## Benchmark Suites

| Suite | Origin Format | Provenance | Instances | SAT / UNSAT | Domain & Structural Focus | Generator / Scripts |
|---|---|---|---:|:---:|---|---|
| [`f2-frobenius-circulants/`](f2-frobenius-circulants/README.md) | AIG (`.aig`) | **Original** | 6 | 4 / 2 | Balanced $\mathbb{F}_2$ circulant parity circuits ($n=64\text{--}4{,}096$) | Rust (`src/`) |
| [`tseitin-expanders/`](tseitin-expanders/README.md) | AIG (`.aig`) | **Original** *(classic family)* | 4 | 0 / 4 | $\mathrm{MOD}_2$-Tseitin 3-regular expanders & prism ($n=60\text{--}400$) | Rust (`src/`) |
| [`coupled-linear-nonlinear/`](coupled-linear-nonlinear/README.md) | AIG (`.aig`) | **Original** | 4 | 3 / 1 | Coupled $\mathbb{F}_2$ nullspace + nonlinear $\mathrm{And}/\mathrm{Maj}_3/\mathrm{Mux}$ circuits | Rust (`src/`) |
| [`hard-spn/`](hard-spn/README.md) | AIG (`.aig`) | **Original** | 4 | 3 / 1 | LowMC-style linear-form + S-box SPN algebraic cryptanalysis | Rust (`src/`) |
| [`integer-factoring/`](integer-factoring/README.md) | AIG (`.aig`) | **Original** *(classic problem)* | 6 | 5 / 1 | Wallace & Karatsuba multiplier inversion (28–40b) + XOR-masked mult | Rust (`src/`) |
| [`sha256-preimage/`](sha256-preimage/README.md) | AIG (`.aig`) | **Original** *(FIPS 180-4)* | 5 | 4 / 1 | Exact FIPS 180-4 SHA-256 CSA preimages ($R = 16, 17, 64$; $k = 16, 20, 32$) | Rust (`src/`) |
| [`cec-arithmetic-miters/`](cec-arithmetic-miters/README.md) | AIG (`.aig`) | **Original** *(classic EDA)* | 5 | 0 / 5 | EDA CEC miters: Ripple-Carry vs. Kogge–Stone; Array vs. Wallace vs. Karatsuba | Rust (`src/`) |
| [`zed-adversarial-hub-php/`](zed-adversarial-hub-php/README.md) | AIG (`.aig`) | **Sourced** ([`zed-impl`](https://github.com/lukehutch/zed-impl), MIT) + PHP | 18 | 3 / 15 | Bit-vector Hub disjunctions ($n=20\text{--}80$) & Pigeonhole ($\mathrm{PHP}^9_8\text{--}\mathrm{PHP}^{50}_{49}$) | Rust (`src/`) |
| [`hamd-hamiltonian-cycle/`](hamd-hamiltonian-cycle/README.md) | CNF (`.cnf`) | **Original** *(classic graphs)* | 22 | 12 / 10 | 6 provably SAT/UNSAT graph families ($GP$, Snarks, Meredith, Chvátal, Broken Crown, Planted) | Rust (`src/`) |
| [`random-3sat-phase-transition/`](random-3sat-phase-transition/README.md) | CNF (`.cnf`) | **Original** *(classic ensemble)* | 2 | 1 / 1 | Uniform random 3-SAT at critical phase transition $m/n = 4.26$ ($n=200$) | Python (`src/`) |
| [`sat-competition-2023-2024-selected/`](sat-competition-2023-2024-selected/README.md) | CNF (`.cnf`) | **Sourced** ([SC 23/24](https://satcompetition.github.io/) / [GBD](https://benchmark-database.de/), CC-BY-4.0) | 14 | 5 / 9 | 14 curated SC 2023/2024 Main Track CNFs across 11 domains (with GBD hashes) | Python + manifest (`src/`) |
| [`sat-competition-2024-2026-main-track/`](sat-competition-2024-2026-main-track/README.md) | CNF (URIs) | **Sourced** ([SC 24–26](https://satcompetition.github.io/) / [GBD](https://benchmark-database.de/), CC-BY-4.0) | 1,166* | Mixed | Complete SC 2024, 2025, 2026 Main Track GBD URI manifests & eval harness | Python + `.uri` (`src/`) |

\* `sat-competition-2024-2026-main-track/` stores immutable GBD URI lists (`main_2024.uri`, `main_2025.uri`, `main_2026.uri`) and download/conversion scripts rather than duplicating ~11 GiB of raw `.cnf.xz` archives in Git. All other 11 suites (**90 benchmarks, 180 dual-format `.aig`/`.cnf` files + `.xcnf` files**) are committed directly in full.

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

### 3. SAT Competition 2024–2026 Main Track (1,166 Unique CNFs, 1-Core)

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

## License

- Repository-authored original suites and generator scripts are licensed under the **MIT License** — see [`LICENSE`](LICENSE).
- Sourced suites include their original upstream licenses and provenance links inside their respective directories:
  - [`zed-adversarial-hub-php/LICENSE`](zed-adversarial-hub-php/LICENSE) — MIT License (copied from [`zed-impl`](https://github.com/lukehutch/zed-impl)).
  - [`sat-competition-2023-2024-selected/LICENSE`](sat-competition-2023-2024-selected/LICENSE) — Creative Commons Attribution 4.0 International (**CC-BY-4.0**) for SAT Competition / GBD benchmark archives + MIT for scripts.
  - [`sat-competition-2024-2026-main-track/LICENSE`](sat-competition-2024-2026-main-track/LICENSE) — Creative Commons Attribution 4.0 International (**CC-BY-4.0**) for SAT Competition / GBD benchmark corpora + MIT for scripts.
