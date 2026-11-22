# SAT Benchmarks

A curated, dual-format (**Binary AIGER 1.9 `.aig`** and **DIMACS `.cnf` / `.xcnf`**) collection of Boolean satisfiability, circuit-inversion, algebraic, graph-theoretic, hardware-verification, and SAT Competition benchmark suites developed and imported during the development of the **Frobenius** SAT/circuit solver.

Every benchmark suite lives in its own top-level directory containing:
- Native-format benchmark instances at the suite root (`.aig` for circuit-native suites; `.cnf` for clausal suites).
- Exact dual-format conversions in `cnf-version/` (for originally-AIG suites) or `aig-version/` (for originally-CNF suites). Every single `.aig` file across all suites (**87 / 87**) conforms to **Binary AIGER 1.9** (`L = 0`, `O = 1` combinational miter where `PO_0 = 1` iff SAT) and has been independently verified with Berkeley **ABC** (`read_aiger` + `sat` spot-checks).
- Standalone, zero-dependency generator / fetcher / converter source code in `src/`.
- A detailed `README.md` documenting provenance, mathematical/circuit parameters, exact data sizes, comparative 1-core solver timings (Frobenius 1C PGO, Kissat 4.0.4, CaDiCaL 3.1.0, CryptoMiniSat 5.18.0 CNF & XCNF), proof verification status (`cake_lpr` / `lrat-check`), and literature citations.

## Benchmark Suites

| Suite | Origin Format | Converted Dir | Instances | SAT / UNSAT | Domain & Structural Focus | Generator / Scripts |
|---|---|---|---:|:---:|---|---|
| [`f2-frobenius-circulants/`](f2-frobenius-circulants/README.md) | AIG (`.aig`) | `cnf-version/` | 4 | 4 / 0 | Invertible $\mathbb{F}_2$ circulant parity circuits ($n=64\text{--}4{,}096$) | Rust (`src/`) |
| [`tseitin-expanders/`](tseitin-expanders/README.md) | AIG (`.aig`) | `cnf-version/` | 4 | 0 / 4 | $\mathrm{MOD}_2$-Tseitin 3-regular expanders & prism ($n=60\text{--}400$) | Rust (`src/`) |
| [`coupled-linear-nonlinear/`](coupled-linear-nonlinear/README.md) | AIG (`.aig`) | `cnf-version/` | 3 | 3 / 0 | Coupled $\mathbb{F}_2$ nullspace + nonlinear $\mathrm{And}/\mathrm{Maj}_3/\mathrm{Mux}$ circuits | Rust (`src/`) |
| [`hard-spn/`](hard-spn/README.md) | AIG (`.aig`) | `cnf-version/` | 4 | 3 / 1 | LowMC-style linear-form + S-box SPN algebraic cryptanalysis | Rust (`src/`) |
| [`integer-factoring/`](integer-factoring/README.md) | AIG (`.aig`) | `cnf-version/` | 6 | 5 / 1 | Wallace & Karatsuba multiplier inversion (28–40b) + XOR-masked mult | Rust (`src/`) |
| [`sha256-preimage/`](sha256-preimage/README.md) | AIG (`.aig`) | `cnf-version/` | 5 | 4 / 1 | Exact FIPS 180-4 SHA-256 CSA preimages ($R = 16, 17, 64$; $k = 16, 20, 32$) | Rust (`src/`) |
| [`cec-arithmetic-miters/`](cec-arithmetic-miters/README.md) | AIG (`.aig`) | `cnf-version/` | 5 | 0 / 5 | EDA CEC miters: Ripple-Carry vs. Kogge–Stone; Array vs. Wallace vs. Karatsuba | Rust (`src/`) |
| [`zed-adversarial-hub-php/`](zed-adversarial-hub-php/README.md) | AIG (`.aig`) | `cnf-version/` | 18 | 3 / 15 | Bit-vector Hub disjunctions ($n=20\text{--}80$) & Pigeonhole ($\mathrm{PHP}^9_8\text{--}\mathrm{PHP}^{50}_{49}$) | Rust (`src/`) |
| [`hamd-hamiltonian-cycle/`](hamd-hamiltonian-cycle/README.md) | CNF (`.cnf`) | `aig-version/` | 22 | 12 / 10 | 6 provably SAT/UNSAT graph families ($GP$, Snarks, Meredith, Chvátal, Broken Crown, Planted) | Rust (`src/`) |
| [`random-3sat-phase-transition/`](random-3sat-phase-transition/README.md) | CNF (`.cnf`) | `aig-version/` | 2 | 1 / 1 | Uniform random 3-SAT at critical phase transition $m/n = 4.26$ ($n=200$) | Python (`src/`) |
| [`sat-competition-2023-2024-selected/`](sat-competition-2023-2024-selected/README.md) | CNF (`.cnf`) | `aig-version/` | 14 | 5 / 9 | 14 curated SC 2023/2024 Main Track CNFs across 11 domains (with GBD hashes) | Python + manifest (`src/`) |
| [`sat-competition-2024-2026-main-track/`](sat-competition-2024-2026-main-track/README.md) | CNF (URIs) | `src/cnf2aig.py` | 1,166* | Mixed | Complete SC 2024, 2025, 2026 Main Track GBD URI manifests & eval harness | Python + `.uri` (`src/`) |

\* `sat-competition-2024-2026-main-track/` stores immutable GBD URI lists (`main_2024.uri`, `main_2025.uri`, `main_2026.uri`) and download/conversion scripts rather than duplicating ~11 GiB of raw `.cnf.xz` archives in Git. All other 11 suites (**87 benchmarks, 174 dual-format `.aig`/`.cnf` files + `.xcnf` files**) are committed directly in full.

## Highlighted Solver Summary

### Unified 50-Benchmark Flat-CNF Gauntlet (1-Core, Identical Flat `.cnf` Input)

30 circuit/algebraic instances ($T_{\max} = 5{,}000\;\text{s}$) + 20 adversarial Zed, SC 2023/2024, and Random 3-SAT instances ($T_{\max} = 600\;\text{s}$), AMD Ryzen 9 5950X, exact median of 3 runs:

| Solver (1C) | Solved | Fastest Wins | Part I PAR-2 (30) | Part II PAR-2 (20) | Unified 50 PAR-2 |
|---|---:|---:|---:|---:|---:|
| **Frobenius 1C PGO** | **50 / 50** | **50 / 50** | **430.02 ms** | **4,309.00 ms** | **4,739.02 ms** |
| Kissat 4.0.4 | 40 / 50 | 0 / 50 | 35,047,925.98 ms | 8,651,994.22 ms | 43,699,920.20 ms |
| CaDiCaL 3.1.0 | 38 / 50 | 0 / 50 | 25,715,225.61 ms | 12,017,694.26 ms | 37,732,919.87 ms |
| CryptoMiniSat 5.18.0 (CNF) | 35 / 50 | 0 / 50 | 30,027,443.01 ms | 14,462,626.48 ms | 44,490,069.49 ms |
| CryptoMiniSat 5.18.0 (XCNF) | 40 / 50 | 0 / 50 | 20,471,425.77 ms | 9,720,466.50 ms | 30,191,892.27 ms |

### 22-Instance Provable HAMD Suite (1-Core, $T_{\max} = 15\;\text{s}$)

- **Frobenius 1C PGO:** **22 / 22** solved (`372.43 ms` total PAR-2; **12/12** SAT cycles verified; **10/10** UNSAT LRAT proofs formally verified `s VERIFIED UNSAT` by HOL4/CakeML `cake_lpr` and `lrat-check`) vs. Kissat 4.0.4 (`18/22`, `140,869.50 ms`), CaDiCaL 3.1.0 (`17/22`, `163,592.80 ms`), and CryptoMiniSat 5.18.0 (`18/22`, `148,852.60 ms`).

### SAT Competition 2024–2026 Main Track (1,166 Unique CNFs, 1-Core, $T = 60\;\text{s}$)

- **SC 2024:** Frobenius **72/400** (`25.04 s`) at 15 s and **111/400** (`91.02 s`) at 60 s (#1 overall at both cutoffs vs. Gold `kissat-sc2024` 43/400 at 15 s, 81/400 at 60 s).
- **SC 2025:** Frobenius **95/400** (`23.51 s`) at 15 s and **141/400** (`81.92 s`) at 60 s.
- **SC 2026:** Frobenius **122/400** (`21.37 s`) at 15 s and **139/400** (`80.24 s`) at 60 s (#1 overall at both cutoffs vs. Main Gold `satsuma-iter-kissat` 70/400 at 15 s, 112/400 at 60 s).

## Format Conventions

- **Binary AIGER 1.9 (`.aig`):** Standard Armin Biere combinational AIGER format (`aig M I 0 1 A`) with `L = 0` latches and `O = 1` primary output `PO_0` that evaluates to `1` iff all circuit assertions / CNF clauses are satisfied. Readable directly by Berkeley `abc`, `aigtoaig`, `aigtocnf`, Yosys, and HWMCC toolchains.
- **DIMACS CNF / XCNF (`.cnf`, `.xcnf`):** Standard SAT Competition `p cnf <vars> <clauses>` format; `.xcnf` files include native CryptoMiniSat `x l1 ... lk 0` XOR parity clauses.

## License

See [`LICENSE`](LICENSE) for repository-authored benchmarks and generator scripts. Imported SAT Competition benchmarks in `sat-competition-2023-2024-selected/` and `sat-competition-2024-2026-main-track/` remain subject to their respective upstream competition / Global Benchmark Database licenses.
