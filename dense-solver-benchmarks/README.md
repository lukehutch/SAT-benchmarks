# [`dense-solver`](https://github.com/libdense/dense-solver) Combinatorial & Public SAT Benchmarks (Merlin Numa)

## Provenance & Credit

- **Author & Recommended by:** Merlin Numa ([`@merlin_numa`](https://twitter.com/merlin_numa) on Twitter/X)
- **Upstream Repository:** [`libdense/dense-solver`](https://github.com/libdense/dense-solver)
- **Zenodo Archive (v0.0.4):** [`zenodo.org/records/24443907`](https://zenodo.org/records/24443907)
- **License & Attribution:**
  - [`dense-solver`](https://github.com/libdense/dense-solver) generator scripts and synthetic benchmarks are licensed under the **MIT License** — see [`LICENSE`](LICENSE).
  - Third-party public formulas in `public-instances/` retain their full upstream provenance, SHA-256 digests, and credits in [`SOURCES.md`](SOURCES.md), [`CITATION.cff`](CITATION.cff), and [`src/public-inputs.csv`](src/public-inputs.csv) (22 SATLIB formulas + 8 SAT Competition 2025 Main Track GBD formulas).

## Problem Description

This suite mirrors the complete benchmark corpus shipped with [`dense-solver v0.0.4`](https://github.com/libdense/dense-solver), organized into two complementary collections:

1. **`instances/` (20 structured cardinality & tiling CNFs):**
   - **Pigeonhole Principle ($\mathrm{PHP}^n_{n-1}$ UNSAT and $\mathrm{PHP}^8_8$ SAT) across 8 distinct CNF encodings:** pairwise, pairwise-functional, Sinz sequential counter, renamed sequential counter, bitwise, ladder, sorting network, cardinality network, totalizer, modulo-totalizer, and $k$-modulo-totalizer, scaling up to $\mathrm{PHP}^{65}_{64}$ (both pairwise and sequential).
   - **Mutilated Chessboard domino-tiling UNSAT formulas:** `chessboard12`, `chessboard16`, and `chessboard32` (plus the generator `src/chessboard.py`, which produces larger boards such as `chessboard368.cnf` with $270{,}108$ variables and $943{,}544$ clauses).
2. **`public-instances/` (30 third-party public CNFs):**
   - **22 SATLIB classics:** `hole6..10` (John Hooker), `uf50-01..04` & `uuf50-01..04` (uniform random 3-SAT), `flat30-1..3` (Joseph Culberson graph coloring), `anomaly`, `medium`, `bw_large.a` (SATPLAN Blocks World), and `par8-1-c..par8-3-c` (James Crawford parity learning).
   - **8 compact SAT Competition 2025 Main Track representatives** (sourced via GBD / RocSAT selection): `sc25-subset-cardinality`, `sc25-fpga-routing`, `sc25-scheduling`, `sc25-hgen`, `sc25-tseitin-formulas`, `sc25-mutilated-chessboard`, `sc25-hamiltonian`, and `sc25-pigeon-hole`.

## Corpus & Data Sizes

All **50 `.cnf.xz` files** are committed verbatim (xz-compressed) alongside **50 exact Binary AIGER 1.9 `.aig.xz` conversions** in `aig-version/` (all 50/50 verified with [Berkeley ABC](https://github.com/berkeley-abc/abc) `read_aiger`) and the upstream Python generators (`src/generate.py`, `src/chessboard.py`, `src/fetch_public.py`, `src/public-inputs.csv`, `src/cnf2aig.py`):

| Directory | Instances | SAT / UNSAT | Vars Range | Clauses Range | Total `.cnf.xz` Size | AIG Files |
|---|---:|:---:|---:|---:|---:|---:|
| `instances/` | 20 | 2 / 18 | 64–8,256 | 168–133,185 | 129.9 KB | 20 |
| `public-instances/` | 30 | 16 / 14 | 42–760 | 133–4,675 | 70.4 KB | 30 |
| **Total** | **50** | **18 / 32** | **42–8,256** | **133–133,185** | **200.3 KB** | **50** |

## Comparative 1-Core Benchmark Results

- **Hardware & Protocol:** Same machine (AMD Ryzen 9 5950X, Linux, 1 core per run, $T_{\max} = 5\;\text{s}$, PAR-2 penalty $10{,}000\;\text{ms}$, identical flat `.cnf` input, 0 verdict disagreements).

### A. 30-Instance Public Suite (`public-instances/`, $T_{\max} = 5\;\text{s}$)

| Solver (1C) | Solved | SAT / UNSAT | Total PAR-2 | Relative PAR-2 |
|---|---:|:---:|---:|---|
| **Frobenius 1C** | **29 / 30** | **16 / 13** | **10,712.87 ms** | *(fastest)* |
| [`dense-solver 0.0.4`](https://github.com/libdense/dense-solver) | 28 / 30 | 15 / 13 | 20,413.13 ms | *(1.91x slower)* |
| [Kissat](https://github.com/arminbiere/kissat) 4.0.4 | 25 / 30 | 16 / 9 | 53,065.48 ms | *(4.95x slower)* |
| [CaDiCaL](https://github.com/arminbiere/cadical) 3.1.0 | 24 / 30 | 16 / 8 | 63,765.07 ms | *(5.95x slower)* |
| [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18.0* | 20 / 30 | 12 / 8 | 100,870.73 ms | *(9.42x slower)* |

*\* [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18.0's strict parser rejected 4 legacy SATLIB files (`hole9.cnf`, `par8-1-c..3-c.cnf`) that contain trailing tokens/EOF formatting from the original SATLIB archive; all other four solvers parsed and solved all 4.*

### B. 20-Instance Synthetic Suite (`instances/`) + Generated `chessboard368.cnf` (21 Instances, $T_{\max} = 5\;\text{s}$)

| Solver (1C) | Solved | `chessboard368.cnf` (270k vars, 944k cls) | Total PAR-2 (21 files) | Relative PAR-2 |
|---|---:|---:|---:|---|
| **Frobenius 1C** | **21 / 21** | **171.98 ms** *(fastest)* | **245.60 ms** | *(fastest)* |
| [`dense-solver 0.0.4`](https://github.com/libdense/dense-solver) | **21 / 21** | 434.76 ms *(2.53x slower)* | 466.92 ms | *(1.90x slower)* |
| [Kissat](https://github.com/arminbiere/kissat) 4.0.4 | 14 / 21 | T/O ($>5\;\text{s}$) | 70,567.66 ms | *(287x slower)* |
| [CaDiCaL](https://github.com/arminbiere/cadical) 3.1.0 | 14 / 21 | T/O ($>5\;\text{s}$) | 70,982.94 ms | *(289x slower)* |
| [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18.0 | 14 / 21 | T/O ($>5\;\text{s}$) | 71,525.43 ms | *(291x slower)* |

<!-- BEGIN_STRUCTURAL_ANALYSIS -->
## Phase-Transition & Structural Analysis

*Auto-generated by [`../src/analyze_benchmarks.py`](../src/analyze_benchmarks.py). Position relative to the critical phase transition is measured by $\rho_{\mathrm{crit}} = \frac{1}{n}\sum_k m_k / \alpha_c(k)$ (exact $\alpha/\alpha_c(k)$ for pure $k$-SAT; effective critical threshold $\alpha_c^{\mathrm{eff}} = \alpha/\rho_{\mathrm{crit}}$; `Under` $<0.90\times$, `Near-crit` $0.90\text{--}1.10\times$, `Over` $>1.10\times$), alongside Gent–Walsh annealed constrainedness $\kappa = -\frac{1}{n}\sum_i \log_2(1-2^{-k_i})$ (AAAI 1996), clause-length profile ($\bar{k}$, `%Bin`, `%Horn`), variable-degree CV ($\sigma_d/\bar{d}$, uniformity vs. hub skew), and extracted native XOR parity clauses.*

| Group / Family | Files | Med $n$ | Med $m$ | $\alpha=m/n$ (Med) | $\alpha_c^{\mathrm{eff}}$ (Med) | $\rho_{\mathrm{crit}}$ Med [Min–Max] (Regime) | Med $\kappa$ | Med $\bar{k}$ | Bin% | Horn% | Deg CV | Total XORs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `instances` | 20 | 270 | 501 | 1.86 | 1.05 | **1.53x** [0.55x–32.0x] (Over) | 0.65 | 2.28 | 95% | 97% | 0.16 | 0 |
| `public-instances` | 30 | 82 | 299 | 4.36 | 1.25 | **2.96x** [0.48x–14.5x] (Over) | 1.25 | 2.32 | 74% | 72% | 0.23 | 323 |

**Suite Phase-Transition Summary (50 instances):** median $\rho_{\mathrm{crit}} = 2.17\times$ (range `0.48x–32.0x`), median $\kappa = 1.01$, regime split **4 Under / 12 Near-critical / 34 Over**, total extracted native XOR parity clauses = **323**.
<!-- END_STRUCTURAL_ANALYSIS -->

## References

- M. Numa, *[`dense-solver`](https://github.com/libdense/dense-solver) v0.0.4*, [GitHub](https://github.com/libdense/dense-solver) and [Zenodo `24443907`](https://zenodo.org/records/24443907) (2026).
- A. Biere, D. Le Berre, E. Lonca, and N. Manthey, *"Detecting Cardinality Constraints in CNF"*, SAT 2014, LNCS 8561, pp. 285–301.
- M. J. H. Heule, B. Kiesl, and A. Biere, *"Clausal Proofs of Mutilated Chessboards"*, NFM 2019, LNCS 11460, pp. 204–210.
- C. Sinz, *"Towards an Optimal CNF Encoding of Boolean Cardinality Constraints"*, CP 2005, LNCS 3709, pp. 827–831.
