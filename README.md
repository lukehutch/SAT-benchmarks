# SAT Benchmarks

A curated, **four-format** (**Binary AIGER 1.9 `.aig.xz`**, **DIMACS `.cnf.xz`**, **[CryptoMiniSat](https://github.com/msoos/cryptominisat) `.xcnf.xz`**, and **DIMACS-ANF `.anf.xz`**) repository of **64 standalone top-level collections** (**60 SAT collections** totaling **785 instances × 4 formats = 3,140 compressed SAT benchmark files**, **2 MATA NFA collections** totaling **174 `.mata.xz` files**, and **2 URI-manifest collections**) spanning Boolean satisfiability, circuit inversion, algebraic cryptanalysis, quantum LDPC code distance, matrix multiplication, graph theory, combinatorial chessboard puzzles, symmetry breaking, exact circuit synthesis, hardware verification, finite-automata complementation, SATLIB/DIMACS classics, and SAT Competition corpora. All benchmark input files across the repository are stored xz-compressed (`.xz`).

## Uniform Collection Layout

Every collection lives at the repository root in its own flat, self-contained directory (`<collection>/`) with **zero** benchmark files at collection root and **zero** nested subcollection directories:

- **`README.md`** — Provenance, contributor credits, upstream links and licenses, problem parameters, exact four-format data sizes, comparative 1-core solver timings (Frobenius 1C, [CaDiCaL](https://github.com/arminbiere/cadical) 3.1.0, [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18.0, [`dense-solver 0.0.4`](https://github.com/libdense/dense-solver), [Kissat](https://github.com/arminbiere/kissat) 4.0.4), proof verification status ([`cake_lpr`](https://github.com/tanyongkiam/cake_lpr) / [`lrat-check`](https://github.com/marijnheule/drat-trim)), auto-generated phase-transition & structural analysis, and literature citations.
- **`<orig-fmt>-orig/`** — Native original compressed files directly inside: `aig-orig/` (8 collections, 52 instances), `cnf-orig/` (51 collections, 731 instances), `xcnf-orig/` (1 collection, 2 instances), or `mata-orig/` (2 NFA collections, 174 automata).
- **`<conv-fmt>-converted/`** — Exact lossless conversions for all remaining SAT formats directly inside:
  - `aig-converted/` (or `aig-orig/`): **785 / 785** **Binary AIGER 1.9** (`L = 0`, `O = 1` combinational miter where `PO_0 = 1` iff SAT; `45.76 MB` total, independently verified with [Berkeley **ABC**](https://github.com/berkeley-abc/abc) `read_aiger`, `0` errors).
  - `cnf-converted/` (or `cnf-orig/`): **785 / 785** **DIMACS `.cnf.xz`** (`43.00 MB` total).
  - `xcnf-converted/` (or `xcnf-orig/`): **785 / 785** **[CryptoMiniSat](https://github.com/msoos/cryptominisat) `.xcnf.xz`** (`29.96 MB` total, with complete $2^{k-1}$-clause XOR parity blocks collapsed losslessly to native `x l1 ... lk 0` lines).
  - `anf-converted/`: **785 / 785** **DIMACS-ANF `.anf.xz`** (`93.41 MB` total, linear-size degree-$\le 2$ from `aig-orig/` and degree-$\le 3$ from `xcnf-orig/` / `xcnf-converted/`, generated via [`src/to_anf.py`](src/to_anf.py)).
- **`src/`** — Standalone generator, exporter, fetcher, or converter source code (alongside repository-wide [`src/to_anf.py`](src/to_anf.py) and [`src/analyze_benchmarks.py`](src/analyze_benchmarks.py)).

## Benchmark Collections (64 Collections)

| Collection | Origin Format | Provenance & Credit | Instances | SAT / UNSAT | Domain & Structural Focus | Scripts (`src/`) |
|---|---|---|---:|:---:|---|---|
| [`aloul-dac02-bench/`](aloul-dac02-bench/README.md) | `cnf-orig/` | **Sourced** — Fadi A. Aloul ([`aloul.net`](https://www.aloul.net/benchmarks.html), DAC 2002, via [`@merlin_numa`](https://twitter.com/merlin_numa)) | 32 | Mixed | DAC 2002 symmetry suite: FPGA, routing, `hole`/`chnl`, Urquhart parity | Python |
| [`aloul-difp-a/`](aloul-difp-a/README.md) | `cnf-orig/` | **Sourced** — Fadi A. Aloul ([`aloul.net`](https://www.aloul.net/benchmarks.html), via [`@merlin_numa`](https://twitter.com/merlin_numa)) | 14 | 14 / 0 | Array-multiplier integer factoring ($19\text{--}21$-bit primes, scrambled) | Python |
| [`aloul-difp-w/`](aloul-difp-w/README.md) | `cnf-orig/` | **Sourced** — Fadi A. Aloul ([`aloul.net`](https://www.aloul.net/benchmarks.html), via [`@merlin_numa`](https://twitter.com/merlin_numa)) | 15 | 15 / 0 | Wallace-multiplier integer factoring ($19\text{--}21$-bit primes, scrambled) | Python |
| [`aloul-fpga-sb-sat/`](aloul-fpga-sb-sat/README.md) | `cnf-orig/` | **Sourced** — Fadi A. Aloul ([`aloul.net`](https://www.aloul.net/benchmarks.html), SAT 2002 *"Bart"*, via [`@merlin_numa`](https://twitter.com/merlin_numa)) | 11 | 11 / 0 | Satisfiable symmetry-rich FPGA switch-box routing (`fpga10..13`) | Python |
| [`aloul-fpga-sb-uns/`](aloul-fpga-sb-uns/README.md) | `cnf-orig/` | **Sourced** — Fadi A. Aloul ([`aloul.net`](https://www.aloul.net/benchmarks.html), SAT 2002 *"Homer"*, via [`@merlin_numa`](https://twitter.com/merlin_numa)) | 10 | 0 / 10 | Unsatisfiable symmetry-rich FPGA switch-box routing (`fpga10..11`) | Python |
| [`cec-arithmetic-miters/`](cec-arithmetic-miters/README.md) | `aig-orig/` | **Original** *(classic EDA)* | 5 | 0 / 5 | EDA CEC miters: Ripple-Carry vs. Kogge–Stone; Array vs. Wallace vs. Karatsuba | Rust |
| [`coupled-linear-nonlinear/`](coupled-linear-nonlinear/README.md) | `aig-orig/` | **Original** | 4 | 3 / 1 | Coupled $\mathbb{F}_2$ linear + nonlinear $\mathrm{And}/\mathrm{Maj}_3/\mathrm{Mux}$ circuits | Rust |
| [`dense-solver-public/`](dense-solver-public/README.md) | `cnf-orig/` | **Sourced** — Merlin Numa ([`@merlin_numa`](https://twitter.com/merlin_numa), [`dense-solver`](https://github.com/libdense/dense-solver), [Zenodo](https://zenodo.org/records/24443907), MIT) | 30 | 16 / 14 | 22 SATLIB classics + 8 compact SC 2025 Main Track CNFs | Python |
| [`dense-solver-synthetic/`](dense-solver-synthetic/README.md) | `cnf-orig/` | **Sourced** — Merlin Numa ([`@merlin_numa`](https://twitter.com/merlin_numa), [`dense-solver`](https://github.com/libdense/dense-solver), [Zenodo](https://zenodo.org/records/24443907), MIT) | 20 | 2 / 18 | Multi-encoding PHP ($\mathrm{PHP}^{65}_{64}$) & mutilated chessboards (`cb12..32`) | Python |
| [`f2-frobenius-circulants/`](f2-frobenius-circulants/README.md) | `aig-orig/` | **Original** | 6 | 4 / 2 | Balanced $\mathbb{F}_2$ circulant parity circuits ($n=64\text{--}4{,}096$) | Rust |
| [`fede-intern-challenge/`](fede-intern-challenge/README.md) | `cnf-orig/` | **Sourced** — [`@fede_intern`](https://twitter.com/fede_intern) (`frobenius-challenge-v2`, SC 2025 GBD CC-BY-4.0) | 12 | Mixed / Open | Random 3-SAT, quiet-planted 3-SAT, scrambled factoring ($40\text{--}64\text{b}$), SC25 unsolved (`R(4,4)`, clique-coloring) | Python |
| [`hamd-hamiltonian-cycle/`](hamd-hamiltonian-cycle/README.md) | `cnf-orig/` | **Original** *(classic graphs)* | 22 | 12 / 10 | 6 provably SAT/UNSAT graph families ($GP$, Snarks, Meredith, Chvátal, Broken Crown, Planted) | Rust + Python |
| [`hard-spn/`](hard-spn/README.md) | `aig-orig/` | **Original** | 4 | 3 / 1 | LowMC-style linear-form + S-box SPN algebraic cryptanalysis | Rust |
| [`heule-matrix-6pooled3and-c1/`](heule-matrix-6pooled3and-c1/README.md) | `cnf-orig/` | **Sourced** — Heule, Kauers, Seidl ([repo](https://github.com/marijnheule/matrix-challenges), via [`@SMT_Solvers`](https://twitter.com/SMT_Solvers)) | 10 | 10 / 0 | Pooled-AND `challenge1` ($3\times 3$ $\mathbb{F}_2$ matmul, $R=23$, SAT 2019) | C + Python |
| [`heule-matrix-6pooled3and-c3/`](heule-matrix-6pooled3and-c3/README.md) | `cnf-orig/` | **Sourced** — Heule, Kauers, Seidl ([repo](https://github.com/marijnheule/matrix-challenges), via [`@SMT_Solvers`](https://twitter.com/SMT_Solvers)) | 1 | Open | Pooled-AND `challenge3` ($3\times 3$ $\mathbb{F}_2$ matmul, $R=23$ no type-3 last) | C + Python |
| [`heule-matrix-6pooled3and-c4/`](heule-matrix-6pooled3and-c4/README.md) | `cnf-orig/` | **Sourced** — Heule, Kauers, Seidl ([repo](https://github.com/marijnheule/matrix-challenges), via [`@SMT_Solvers`](https://twitter.com/SMT_Solvers)) | 1 | Open | Pooled-AND `challenge4` ($3\times 3$ $\mathbb{F}_2$ matmul, open $R=22$) | C + Python |
| [`heule-matrix-challenge1/`](heule-matrix-challenge1/README.md) | `cnf-orig/` | **Sourced** — Heule, Kauers, Seidl ([repo](https://github.com/marijnheule/matrix-challenges), via [`@SMT_Solvers`](https://twitter.com/SMT_Solvers)) | 10 | 10 / 0 | Plain Brent `challenge1` ($3\times 3$ $\mathbb{F}_2$ matmul, $R=23$, hard for CDCL) | C + Python |
| [`heule-matrix-challenge2/`](heule-matrix-challenge2/README.md) | `cnf-orig/` | **Sourced** — Heule, Kauers, Seidl ([repo](https://github.com/marijnheule/matrix-challenges), via [`@SMT_Solvers`](https://twitter.com/SMT_Solvers)) | 10 | Exp. UNSAT | Plain Brent `challenge2` ($3\times 3$ $\mathbb{F}_2$ matmul, $R=23$ UNSAT targets) | C + Python |
| [`heule-matrix-challenge3/`](heule-matrix-challenge3/README.md) | `cnf-orig/` | **Sourced** — Heule, Kauers, Seidl ([repo](https://github.com/marijnheule/matrix-challenges), via [`@SMT_Solvers`](https://twitter.com/SMT_Solvers)) | 1 | Open | Plain Brent `challenge3` ($3\times 3$ $\mathbb{F}_2$ matmul, $R=23$ no type-3 last) | C + Python |
| [`heule-matrix-challenge4/`](heule-matrix-challenge4/README.md) | `cnf-orig/` | **Sourced** — Heule, Kauers, Seidl ([repo](https://github.com/marijnheule/matrix-challenges), via [`@SMT_Solvers`](https://twitter.com/SMT_Solvers)) | 1 | Open | Plain Brent `challenge4` ($3\times 3$ $\mathbb{F}_2$ matmul, open $R=22$) | C + Python |
| [`heule-matrix-fraction/`](heule-matrix-fraction/README.md) | `cnf-orig/` | **Sourced** — Heule, Kauers, Seidl ([repo](https://github.com/marijnheule/matrix-challenges), via [`@SMT_Solvers`](https://twitter.com/SMT_Solvers)) | 3 | Hard | Fractional / restricted-coefficient $3\times 3$ matmul variants (`f-d-3..6`) | C + Python |
| [`heule-matrix-xor6cut/`](heule-matrix-xor6cut/README.md) | `cnf-orig/` | **Sourced** — Heule, Kauers, Seidl ([repo](https://github.com/marijnheule/matrix-challenges), via [`@SMT_Solvers`](https://twitter.com/SMT_Solvers)) | 6 | Mixed | Compact XOR-6 cut $3\times 3$ $\mathbb{F}_2$ matmul encodings ($R=22\text{--}27$) | C + Python |
| [`integer-factoring/`](integer-factoring/README.md) | `aig-orig/` | **Original** *(classic problem)* | 6 | 5 / 1 | Wallace & Karatsuba multiplier inversion (28–40b) + XOR-masked mult | Rust |
| [`knights-tour-obstacles/`](knights-tour-obstacles/README.md) | `cnf-orig/` | **Original** | 10 | 5 / 5 | Obstacle Knight's Tour Hamiltonian cycles on punched $12\times 12\text{--}16\times 16$ boards | Python |
| [`mata-presburger-nfa-tptp/`](mata-presburger-nfa-tptp/README.md) | `mata-orig/` | **Sourced** — VeriFIT MATA ([`nfa-bench`](https://github.com/VeriFIT/nfa-bench), MIT, via [`@TravisRudd`](https://twitter.com/TravisRudd)) | 21 | Automata | TACAS 2024 Presburger explicit-complement NFAs (TPTP `ARI*`/`NUM*`) | Python |
| [`mata-presburger-nfa-ultimate-automizer/`](mata-presburger-nfa-ultimate-automizer/README.md) | `mata-orig/` | **Sourced** — VeriFIT MATA ([`nfa-bench`](https://github.com/VeriFIT/nfa-bench), MIT, via [`@TravisRudd`](https://twitter.com/TravisRudd)) | 153 | Automata | TACAS 2024 Presburger explicit-complement NFAs (Ultimate Automizer) | Python |
| [`mod-circuit-sat/`](mod-circuit-sat/README.md) | `cnf-orig/` | **Sourced** — [`@vzhilin_me`](https://twitter.com/vzhilin_me) ([`vzhn/mod-circuit-sat`](https://github.com/vzhn/mod-circuit-sat), arXiv:2102.12579) | 11 | 5 / 4 / 2 Open | Exact optimal $B_2$ circuit synthesis for $\mathrm{MOD}_n^{3,r}$ ($n=3\text{--}6$) | Python |
| [`pretolani-pret/`](pretolani-pret/README.md) | `cnf-orig/` | **Sourced** — Daniele Pretolani ([SATLIB PRET](https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/DIMACS/PRET/descr.html), via [`@MMarchidann`](https://twitter.com/MMarchidann)) | 8 | 0 / 8 | Parity-charged graph 2-coloring UNSAT formulas ($n=60, 150$; 25%–75% Horn) | Python |
| [`qdistsat-qldpc/`](qdistsat-qldpc/README.md) | `cnf-orig/` | **Sourced** — [`QDistSAT`](https://github.com/guluchen/QDistSAT) (GPL-3.0+) & Bravyi et al., via [`@TravisRudd`](https://twitter.com/TravisRudd) | 10 | 5 / 5 | CSS Quantum LDPC bivariate-bicycle code distance ($[[30..756]]$) + matrices | Python |
| [`queen-armies/`](queen-armies/README.md) | `cnf-orig/` | **Original** *(inspired by [Christopher Wolfram](https://christopherwolfram.com/projects/queen-armies/))* | 8 | 4 / 4 | Peaceable Queen Armies ($A \in \{2, 3, 4\}$, OEIS A250000/A277433/A277434) | Python |
| [`random-3sat-phase-transition/`](random-3sat-phase-transition/README.md) | `cnf-orig/` | **Original** *(classic ensemble, via [`@jasonslenderman`](https://twitter.com/jasonslenderman) & [`@tingan87`](https://twitter.com/tingan87))* | 8 | 4 / 4 | Uniform random 3-SAT across the phase transition $m/n \in [3.80, 5.00]$ ($n=200$) | Python |
| [`rb-bench-model-rb/`](rb-bench-model-rb/README.md) | `cnf-orig/` | **Sourced** — Ke Xu ([`rb-bench.github.io`](https://rb-bench.github.io/), AIJ 2007, via [`@merlin_numa`](https://twitter.com/merlin_numa)) | 40 | 40 / 0 | Model RB forced-satisfiable phase-transition CSP-to-SAT (`frb30-15`–`frb59-26`) | Python |
| [`sat-competition-2023-2024-selected/`](sat-competition-2023-2024-selected/README.md) | `cnf-orig/` | **Sourced** ([SC 23/24](https://satcompetition.github.io/) / [GBD](https://benchmark-database.de/), CC-BY-4.0) | 14 | 5 / 9 | 14 curated SC 2023/2024 Main Track CNFs across 11 domains (with GBD hashes) | Python + JSON |
| [`sat-competition-2024-2026-main-track/`](sat-competition-2024-2026-main-track/README.md) | URIs (`.uri`) | **Sourced** ([SC 24–26](https://satcompetition.github.io/) / [GBD](https://benchmark-database.de/), CC-BY-4.0) | 1,166* | Mixed | Complete SC 2024, 2025, 2026 Main Track GBD URI manifests & eval harness | Python + `.uri` |
| [`sat-shortcut-challenge-tier1/`](sat-shortcut-challenge-tier1/README.md) | `cnf-orig/` | **Sourced** — Keith Adler ([`@keithadler`](https://twitter.com/keithadler), [repo](https://github.com/keithadler/sat-shortcut-challenge), Apache-2.0) | 47 | Mixed | SAT Shortcut Challenge Tier-1: 47 structured CNFs across 9 families | Python |
| [`sat-shortcut-challenge-tier3/`](sat-shortcut-challenge-tier3/README.md) | `cnf-orig/` | **Sourced** — Keith Adler ([`@keithadler`](https://twitter.com/keithadler), [repo](https://github.com/keithadler/sat-shortcut-challenge), Apache-2.0) | 25 | 15 / 10 | SAT Shortcut Challenge Tier-3: random 3-SAT ($n=300\text{--}500$, $\alpha=4.26$) | Python + C |
| [`satlib-ais/`](satlib-ais/README.md) | `cnf-orig/` | **Sourced** — Hoos & Stützle ([UBC SATLIB](https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html), via [`@jasonslenderman`](https://twitter.com/jasonslenderman)) | 4 | Mixed | All-Interval Series (`ais6..12`, full) | Python |
| [`satlib-archive-uris/`](satlib-archive-uris/README.md) | URIs (`.uri`) | **Sourced** — Hoos & Stützle ([UBC SATLIB](https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html), via [`@jasonslenderman`](https://twitter.com/jasonslenderman)) | 97* | Mixed | Complete manifest of all 97 official UBC SATLIB `.tar.gz` archive URLs | Python + `.uri` |
| [`satlib-beijing/`](satlib-beijing/README.md) | `cnf-orig/` | **Sourced** — 1996 Beijing SAT Comp. ([UBC SATLIB](https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html)) | 16 | Mixed | 1996 Beijing SAT Competition benchmarks (full) | Python |
| [`satlib-bmc/`](satlib-bmc/README.md) | `cnf-orig/` | **Sourced** — Ofer Shtrichman ([UBC SATLIB](https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html), CAV 2000) | 13 | Mixed | Hardware Bounded Model Checking (`bmc-ibm-*` / `bmc-galileo-*`, full) | Python |
| [`satlib-bms-rti/`](satlib-bms-rti/README.md) | `cnf-orig/` | **Sourced** — Singer, Gent, Smaill ([UBC SATLIB](https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html)) | 4 | 4 / 0 | Backbone-Minimal Random 3-SAT (stratified sample / 1,000*) | Python |
| [`satlib-cbs/`](satlib-cbs/README.md) | `cnf-orig/` | **Sourced** — Singer, Gent, Smaill ([UBC SATLIB](https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html)) | 6 | 6 / 0 | Controlled Backbone Random 3-SAT (stratified sample / 40,000*) | Python |
| [`satlib-dimacs-aim/`](satlib-dimacs-aim/README.md) | `cnf-orig/` | **Sourced** — Iwama et al. ([UBC SATLIB](https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html), DIMACS 1993) | 72 | Mixed | Artificial Random 3-SAT `aim-50`/`100`/`200` (full) | Python |
| [`satlib-dimacs-bf/`](satlib-dimacs-bf/README.md) | `cnf-orig/` | **Sourced** — Van Gelder & Tsuji ([UBC SATLIB](https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html), DIMACS 1993) | 4 | Mixed | Circuit Bridge-Fault Analysis (full) | Python |
| [`satlib-dimacs-dubois/`](satlib-dimacs-dubois/README.md) | `cnf-orig/` | **Sourced** — Olivier Dubois ([UBC SATLIB](https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html), DIMACS 1993) | 13 | 1* / 12 | Dubois Hard Parity 3-SAT (`dubois20..100`, full) | Python |
| [`satlib-dimacs-gcp-large/`](satlib-dimacs-gcp-large/README.md) | `cnf-orig/` | **Sourced** — 2nd DIMACS Challenge ([UBC SATLIB](https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html)) | 4 | 4 / 0 | Large Graph Colouring `g125`/`g250` (full) | Python |
| [`satlib-dimacs-hanoi/`](satlib-dimacs-hanoi/README.md) | `cnf-orig/` | **Sourced** — 2nd DIMACS Challenge ([UBC SATLIB](https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html)) | 2 | 2 / 0 | Towers of Hanoi `hanoi4`, `hanoi5` (full) | Python |
| [`satlib-dimacs-ii/`](satlib-dimacs-ii/README.md) | `cnf-orig/` | **Sourced** — Kamath et al. ([UBC SATLIB](https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html), DIMACS 1993) | 41 | 41 / 0 | Inductive Inference `ii8`/`ii16`/`ii32` (full) | Python |
| [`satlib-dimacs-jnh/`](satlib-dimacs-jnh/README.md) | `cnf-orig/` | **Sourced** — John Hooker ([UBC SATLIB](https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html), DIMACS 1993) | 50 | Mixed | Variable-Length Random SAT `jnh*` (full) | Python |
| [`satlib-dimacs-lran/`](satlib-dimacs-lran/README.md) | `cnf-orig/` | **Sourced** — 2nd DIMACS Challenge ([UBC SATLIB](https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html)) | 3 | 3 / 0 | Large Random 3-SAT `f600`/`f1000`/`f2000` ($\alpha=4.25$, full) | Python |
| [`satlib-dimacs-parity/`](satlib-dimacs-parity/README.md) | `cnf-orig/` | **Sourced** — Crawford, Kearns, Schapire ([UBC SATLIB](https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html)) | 30 | 30 / 0 | Parity Learning `par8`/`par16`/`par32` (full) | Python |
| [`satlib-dimacs-phole/`](satlib-dimacs-phole/README.md) | `cnf-orig/` | **Sourced** — John Hooker ([UBC SATLIB](https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html), DIMACS 1993) | 5 | 0 / 5 | Classic DIMACS Pigeonhole Principle `hole6..10` (full) | Python |
| [`satlib-dimacs-ssa/`](satlib-dimacs-ssa/README.md) | `cnf-orig/` | **Sourced** — Van Gelder & Tsuji ([UBC SATLIB](https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html), DIMACS 1993) | 8 | Mixed | Single-Stuck-At Circuit Faults (full) | Python |
| [`satlib-flat-gcp/`](satlib-flat-gcp/README.md) | `cnf-orig/` | **Sourced** — Joseph Culberson ([UBC SATLIB](https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html)) | 8 | 8 / 0 | Flat 3-Colourable Graphs `flat30..200` (sample / 1,700*) | Python |
| [`satlib-planning-blocksworld/`](satlib-planning-blocksworld/README.md) | `cnf-orig/` | **Sourced** — Kautz & Selman ([UBC SATLIB](https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html), AAAI 1996) | 7 | 7 / 0 | SATPLAN Blocks World (full) | Python |
| [`satlib-planning-logistics/`](satlib-planning-logistics/README.md) | `cnf-orig/` | **Sourced** — Kautz & Selman ([UBC SATLIB](https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html), AAAI 1996) | 4 | 4 / 0 | SATPLAN Logistics `a..d` (full) | Python |
| [`satlib-qg/`](satlib-qg/README.md) | `cnf-orig/` | **Sourced** — Hantao Zhang ([UBC SATLIB](https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html)) | 22 | Mixed | Quasigroup / Latin Squares `qg1..7` (full) | Python |
| [`satlib-rnd3sat/`](satlib-rnd3sat/README.md) | `cnf-orig/` | **Sourced** — Hoos & Stützle ([UBC SATLIB](https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html)) | 10 | 5 / 5 | Uniform Random 3-SAT `uf`/`uuf50..250` (sample / 6,600*) | Python |
| [`satlib-sw-gcp/`](satlib-sw-gcp/README.md) | `cnf-orig/` | **Sourced** — Gent, Hoos, Prosser, Walsh ([UBC SATLIB](https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html)) | 5 | 5 / 0 | Morphed Small-World 5-Colouring `lp0..p0` (sample / 901*) | Python |
| [`sha256-preimage/`](sha256-preimage/README.md) | `aig-orig/` | **Original** *(FIPS 180-4)* | 5 | 4 / 1 | Exact FIPS 180-4 SHA-256 CSA preimages ($R = 16, 17, 64$; $k = 16, 20, 32$) | Rust |
| [`sigal-aes256-xcnf/`](sigal-aes256-xcnf/README.md) | `xcnf-orig/` | **Sourced** — Victor Sigal ([`@uniexpertise`](https://twitter.com/uniexpertise)) | 2 | 1 SAT / 1 Open | Full 14-round NIST FIPS 197 AES-256 2-pair key recovery (500 S-boxes, 42.8k XORs) | Python |
| [`tseitin-expanders/`](tseitin-expanders/README.md) | `aig-orig/` | **Original** *(classic family)* | 4 | 0 / 4 | $\mathrm{MOD}_2$-Tseitin 3-regular expanders & prism ($n=60\text{--}400$) | Rust |
| [`vlsat-2/`](vlsat-2/README.md) | `cnf-orig/` | **Sourced** — Garavel / CADP INRIA ([VLSAT-2](https://cadp.inria.fr/resources/vlsat/2.html), via [`@TravisRudd`](https://twitter.com/TravisRudd)) | 10 + 100* | 1 / 9 *(first 10)* | Very Large SAT from Nested-Unit Petri Net decompositions (first 10 + 100 URIs) | Python + `.uri` |
| [`zed-adversarial-hub-php/`](zed-adversarial-hub-php/README.md) | `aig-orig/` | **Original** | 18 | 3 / 15 | Bit-vector Hub disjunctions ($n=20\text{--}80$) & Pigeonhole ($\mathrm{PHP}^9_8\text{--}\mathrm{PHP}^{50}_{49}$) | Rust |

\* [`sat-competition-2024-2026-main-track/`](sat-competition-2024-2026-main-track/README.md) stores immutable GBD URI lists (`main_2024.uri`, `main_2025.uri`, `main_2026.uri`, 1,166 unique CNFs), [`vlsat-2/vlsat2_100.uri`](vlsat-2/vlsat2_100.uri) stores all 100 INRIA URLs, and [`satlib-archive-uris/satlib_all_97_archives.uri`](satlib-archive-uris/satlib_all_97_archives.uri) stores all 97 official UBC SATLIB `.tar.gz` archive URLs rather than duplicating multi-gigabyte raw archives in Git. Across the repository, **785 SAT benchmark instances** are committed in **all four formats** (**785** verified Binary AIGER 1.9 `.aig.xz`, **785** DIMACS `.cnf.xz`, **785** [CryptoMiniSat](https://github.com/msoos/cryptominisat) `.xcnf.xz`, and **785** DIMACS-ANF `.anf.xz` = **3,140** xz-compressed SAT benchmark files, `212.12 MB` total), alongside **174 `.mata.xz` NFA benchmarks** (`2.61 MB`) and full generator/converter scripts.

## Highlighted Solver Summary

### 1. Unified 50-Benchmark Flat-CNF Gauntlet (1-Core, Identical Flat `.cnf` Input)

- **Timeout:** Part I (30 circuit/algebraic instances): $T_{\max} = 5{,}000\;\text{s}$ per instance (PAR-2 penalty $10{,}000\;\text{s}$); Part II (20 adversarial Zed, SC 2023/2024, and Random 3-SAT instances): $T_{\max} = 600\;\text{s}$ per instance (PAR-2 penalty $1{,}200\;\text{s}$).
- **Same machine?** **Yes** — all five solvers were run sequentially on the exact same machine (**AMD Ryzen 9 5950X**, 16-core/32-thread, Linux, 1 core per run, exact median of 3 runs).

| Solver (1C) | Solved | Fastest Wins | Part I PAR-2 (30, $T_{\max}=5{,}000\;\text{s}$) | Part II PAR-2 (20, $T_{\max}=600\;\text{s}$) | Unified 50 PAR-2 |
|---|---:|---:|---:|---:|---:|
| **Frobenius 1C** | **50 / 50** | **50 / 50** | **430.02 ms** *(fastest)* | **4,309.00 ms** *(fastest)* | **4,739.02 ms** *(fastest)* |
| [CaDiCaL](https://github.com/arminbiere/cadical) 3.1.0 | 38 / 50 | 0 / 50 | 25,715,225.61 ms *(59,800x slower)* | 12,017,694.26 ms *(2,789x slower)* | 37,732,919.87 ms *(7,962x slower)* |
| [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18.0 (CNF) | 35 / 50 | 0 / 50 | 30,027,443.01 ms *(69,828x slower)* | 14,462,626.48 ms *(3,356x slower)* | 44,490,069.49 ms *(9,388x slower)* |
| [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18.0 (XCNF) | 40 / 50 | 0 / 50 | 20,471,425.77 ms *(47,606x slower)* | 9,720,466.50 ms *(2,256x slower)* | 30,191,892.27 ms *(6,371x slower)* |
| [Kissat](https://github.com/arminbiere/kissat) 4.0.4 | 40 / 50 | 0 / 50 | 35,047,925.98 ms *(81,503x slower)* | 8,651,994.22 ms *(2,008x slower)* | 43,699,920.20 ms *(9,221x slower)* |

### 2. 22-Instance Provable HAMD Suite (1-Core, Identical Flat `.cnf` Input)

- **Timeout:** $T_{\max} = 15\;\text{s}$ per instance (PAR-2 penalty $30\;\text{s}$).
- **Same machine?** **Yes** — all four solvers were run sequentially on the exact same machine (**AMD Ryzen 9 5950X**, 1 core per run, exact median of 3 runs).

| Solver (1C) | Solved | Fastest Wins | Total PAR-2 ($T_{\max}=15\;\text{s}$) | Proof / Model Verification |
|---|---:|---:|---:|---|
| **Frobenius 1C** | **22 / 22** | **19 / 22** | **372.43 ms** *(fastest)* | 12/12 SAT cycles + 10/10 UNSAT [`cake_lpr`](https://github.com/tanyongkiam/cake_lpr) + [`lrat-check`](https://github.com/marijnheule/drat-trim) OK |
| [CaDiCaL](https://github.com/arminbiere/cadical) 3.1.0 | 17 / 22 | 2 / 22 | 163,592.80 ms *(439x slower)* | 100% verdict agreement on solved instances |
| [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18.0 (CNF) | 18 / 22 | 0 / 22 | 148,852.60 ms *(400x slower)* | 100% verdict agreement on solved instances |
| [`dense-solver 0.0.4`](https://github.com/libdense/dense-solver) | 17 / 22 | 0 / 22 | 159,432.38 ms *(428x slower)* | 100% verdict agreement on solved instances |
| [Kissat](https://github.com/arminbiere/kissat) 4.0.4 | 18 / 22 | 1 / 22 | 140,869.50 ms *(378x slower)* | 100% verdict agreement on solved instances |

### 3. Combinatorial Chessboard Suites (1-Core, Identical Flat `.cnf` Input)

- **Timeout:** $T_{\max} = 15\;\text{s}$ per instance (PAR-2 penalty $30\;\text{s}$).
- **Same machine?** **Yes** — all five solvers were run sequentially on the exact same **AMD Ryzen 9 5950X** Linux workstation (1 core per run, 0 verdict disagreements).

| Collection (Instances, $T_{\max}$) | Frobenius 1C | [CaDiCaL](https://github.com/arminbiere/cadical) 3.1.0 | [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18.0 | [`dense-solver 0.0.4`](https://github.com/libdense/dense-solver) | [Kissat](https://github.com/arminbiere/kissat) 4.0.4 |
|---|---:|---:|---:|---:|---:|
| [**Obstacle Knight's Tour**](knights-tour-obstacles/README.md) (10, 15 s) | 10/10 — 54,045 ms *(6.23x)* | 10/10 — 11,302 ms *(1.30x)* | 10/10 — 9,121 ms *(1.05x)* | 2/10 — 250,274 ms *(28.8x)* | **10/10 — 8,678 ms** *(fastest)* |
| [**Peaceable Queen Armies**](queen-armies/README.md) (8, 15 s) | **8/8 — 56,672 ms** *(fastest)* | 1/8 — 214,106 ms *(3.78x)* | 1/8 — 211,830 ms *(3.74x)* | 2/8 — 204,847 ms *(3.61x)* | 4/8 — 160,604 ms *(2.83x)* |

### 4. Imported External Benchmark Collections (1-Core, Identical Flat `.cnf` Input; Plus Native `.mata.xz`)

- **Timeout:** Per-instance $T_{\max}$ is listed in each row (PAR-2 penalty $= 2\,T_{\max}$).
- **Same machine?** **Yes** — all solvers were run on the exact same **AMD Ryzen 9 5950X** Linux workstation (1 thread per run, 0 verdict disagreements, 100% SAT model verification; full-suite sweeps pinned across 8–14 dedicated physical cores with zero SMT sharing). **100% of every committed collection was benchmarked** (zero subsampling).

| External Collection (Instances, $T_{\max}$) | Frobenius 1C | [CaDiCaL](https://github.com/arminbiere/cadical) 3.1.0 | [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18.0 | [`dense-solver 0.0.4`](https://github.com/libdense/dense-solver) | [Kissat](https://github.com/arminbiere/kissat) 4.0.4 |
|---|---:|---:|---:|---:|---:|
| [**Aloul DAC02**](aloul-dac02-bench/README.md) (32, 5 s) | **32/32 — 360.3 ms** *(fastest)* | 17/32 — 154,076 ms *(428x)* | 23/32 — 96,866 ms *(269x)* | 32/32 — 450.7 ms *(1.25x)* | 24/32 — 87,033 ms *(242x)* |
| [**Aloul DIFP-A**](aloul-difp-a/README.md) (14, 5 s) | 7/14 — 84,203 ms *(1.04x)* | 8/14 — 82,148 ms *(1.02x)* | 7/14 — 85,065 ms *(1.05x)* | 5/14 — 106,012 ms *(1.31x)* | **8/14 — 80,636 ms** *(fastest)* |
| [**Aloul DIFP-W**](aloul-difp-w/README.md) (15, 5 s) | 5/15 — 113,241 ms *(1.28x)* | 6/15 — 101,152 ms *(1.14x)* | **7/15 — 88,571 ms** *(fastest)* | 4/15 — 115,672 ms *(1.31x)* | 7/15 — 97,101 ms *(1.10x)* |
| [**Aloul FPGA Switch-Box**](aloul-fpga-sb-sat/README.md) ([SAT](aloul-fpga-sb-sat/README.md) + [UNSAT](aloul-fpga-sb-uns/README.md), 21, 5 s) | 21/21 — 43.7 ms *(1.17x)* | 11/21 — 100,093 ms *(2,676x)* | 11/21 — 100,380 ms *(2,684x)* | **21/21 — 37.4 ms** *(fastest)* | 12/21 — 93,237 ms *(2,493x)* |
| [**`dense-solver` Public**](dense-solver-public/README.md) (30, 5 s) | **29/30 — 10,251 ms** *(fastest)* | 24/30 — 64,035 ms *(6.25x)* | 20/30 — 100,928 ms *(9.85x)* | 28/30 — 20,460 ms *(2.00x)* | 25/30 — 53,137 ms *(5.18x)* |
| [**`dense-solver` Synthetic**](dense-solver-synthetic/README.md) (20, 5 s) | 20/20 — 103.8 ms *(2.28x)* | 14/20 — 61,075 ms *(1,339x)* | 14/20 — 61,636 ms *(1,352x)* | **20/20 — 45.6 ms** *(fastest)* | 14/20 — 60,601 ms *(1,329x)* |
| [**`@fede_intern` 12-CNF Challenge**](fede-intern-challenge/README.md) (12, 60 s / 300 s) | **9/12 — 362.3 s** *(300 s: **10/12 — 1,264 s**)* | 3/12 — 1,120.2 s *(300 s: 4/12 — 5,002 s)* | 0/12 — 1,440.0 s | 0/12 — 1,440.0 s | 3/12 — 1,117.7 s *(300 s: 4/12 — 4,926 s)* |
| [**Heule Matrix `xor6cut`**](heule-matrix-xor6cut/README.md) (6, 60 s; other 8 suites 37, 10 s: all 0/37) | 2/6 — 523,063 ms *(1.25x)* | 2/6 — 493,170 ms *(1.18x)* | 2/6 — 510,399 ms *(XCNF: 3/6 — 455,099 ms)* | 0/6 — 720,000 ms *(1.72x)* | **3/6 — 418,266 ms** *(fastest)* |
| [**MATA Presburger NFAs**](mata-presburger-nfa-tptp/README.md) ([TPTP](mata-presburger-nfa-tptp/README.md) + [UAutomizer](mata-presburger-nfa-ultimate-automizer/README.md), 174, 5 s, `.mata.xz`) | **174/174 — 1,596 ms** *(antichain; emp 1,692 ms, exp 2,147 ms)* | — *(CNF only)* | — *(CNF/XCNF only)* | — *(CNF only)* | — *(CNF only)* |
| [**`mod-circuit-sat`**](mod-circuit-sat/README.md) $n=3\text{--}5$ (9, 30 s) | **9/9 — 17,346 ms** *(fastest)* | 9/9 — 29,702 ms *(1.71x)* | 8/9 — 67,344 ms *(3.88x)* | 8/9 — 67,769 ms *(3.91x)* | 9/9 — 25,994 ms *(1.50x)* |
| [**Model RB Full Suite**](rb-bench-model-rb/README.md) (40, 5 s) | 9/40 — 320,344 ms *(1.09x)* | **12/40 — 293,728 ms** *(fastest)* | 10/40 — 308,697 ms *(1.05x)* | 10/40 — 307,528 ms *(1.05x)* | 11/40 — 306,309 ms *(1.04x)* |
| [**Pretolani PRET**](pretolani-pret/README.md) (8, 5 s) | 8/8 — 9.86 ms *(1.53x)* | 8/8 — 41.53 ms *(6.46x)* | 8/8 — 161.74 ms *(25.2x)* | **8/8 — 6.43 ms** *(fastest)* | 8/8 — 58.45 ms *(9.09x)* |
| [**QDistSAT Full Suite**](qdistsat-qldpc/README.md) `BB_30..756` (10, 10 s) | 5/10 — 100,733 ms *(1.01x)* | **5/10 — 100,078 ms** *(fastest)* | 5/10 — 100,515 ms *(XCNF: 100,297 ms)* | 5/10 — 100,119 ms *(1.00x)* | 5/10 — 100,090 ms *(1.00x)* |
| [**SAT Competition 2023/2024 Selected**](sat-competition-2023-2024-selected/README.md)\* (12, 600 s) | **12/12 — 3,745 ms** *(fastest)* | 5/12 — 8,417,003 ms *(2,248x)* | 3/12 — 10,859,841 ms *(2,900x)* | — | 8/12 — 5,051,149 ms *(1,349x)* |
| [**SAT Shortcut Challenge Tier-1**](sat-shortcut-challenge-tier1/README.md) (47, 300 s) | **46/47 — 646.0 s** *(fastest)* | 45/47 — 1,730.8 s *(2.68x)* | 46/47 — 1,004.2 s *(1.55x)* | 45/47 — 1,225.7 s *(1.90x)* | 45/47 — 1,323.2 s *(2.05x)* |
| [**SAT Shortcut Challenge Tier-3**](sat-shortcut-challenge-tier3/README.md) (25, 300 s) | **17/25 — 4,920.5 s** *(fastest)* | 17/25 — 4,923.0 s *(1.001x)* | 12/25 — 8,583.6 s *(1.74x)* | 5/25 — 12,370.4 s *(2.51x)* | 17/25 — 5,055.9 s *(1.03x)* |
| [**SATLIB All 22 Collections**](satlib-archive-uris/README.md) (331, 5 s) | **318/331 — 151,909 ms** *(fastest)* | 316/331 — 174,495 ms *(1.15x)* | 323/331 — 164,024 ms *(1.08x)* | 313/331 — 207,808 ms *(1.37x)* | 314/331 — 189,408 ms *(1.25x)* |
| [**VLSAT-2 First 10**](vlsat-2/README.md) (10, 5 s) | **7/10 — 30,028 ms** *(fastest)* | 0/10 — 100,000 ms *(3.33x)* | 0/10 — 100,000 ms *(3.33x)* | 7/10 — 30,031 ms *(1.00x)* | 4/10 — 64,843 ms *(2.16x)* |

*\*[`sat-competition-2023-2024-selected/`](sat-competition-2023-2024-selected/README.md) is also included in Part II of the Unified 50-Benchmark Flat-CNF Gauntlet (Section 1 above). [`sigal-aes256-xcnf/`](sigal-aes256-xcnf/README.md) contains full 14-round AES-256 XCNF cryptanalytic challenges (throughput benchmarked in its collection README), and [`sat-competition-2024-2026-main-track/`](sat-competition-2024-2026-main-track/README.md) (1,166 CNFs vs. official competition logs) is summarized in Section 5 below.*

### 5. SAT Competition 2024–2026 Main Track (1,166 Unique CNFs, 1-Core)

- **Timeout:** Evaluated at $T_{\max} = 15\;\text{s}$ and $T_{\max} = 60\;\text{s}$ cutoffs (official competition full runs used $T_{\max} = 5{,}000\;\text{s}$).
- **Same machine?** **No (different machines)** — Frobenius 1C ran on our local **AMD Ryzen 9 5950X** workstation (1 core per instance, unrestricted available RAM), whereas competitor scores are taken directly from official published competition logs/slides (**StarExec** cluster for SC 2024; **LMU / competition sequential clusters** for SC 2025–2026). CPU differences affect absolute runtimes, so ratios below reflect cross-machine published PAR-2 comparisons.

| Track (400 CNFs each) | Solver (1C) | $T_{\max}=15\;\text{s}$ Solved & PAR-2 | $T_{\max}=60\;\text{s}$ Solved & PAR-2 |
|---|---|---:|---:|
| **SC 2024** | **Frobenius 1C** | **72 / 400 — 25.04 s** *(fastest)* | **111 / 400 — 91.02 s** *(fastest)* |
| | [`CaDiCaL`](https://github.com/arminbiere/cadical) (Main #7) | 26 / 400 — 28.24 s *(1.13x slower)* | 54 / 400 — 106.69 s *(1.17x slower)* |
| | [`kissat-sc2024`](https://github.com/arminbiere/kissat) (Main #1 Gold) | 43 / 400 — 27.15 s *(1.08x slower)* | 81 / 400 — 99.47 s *(1.09x slower)* |
| **SC 2025** | **Frobenius 1C** | **95 / 400 — 23.51 s** | **141 / 400 — 81.92 s** |
| | *(Official SC 2025 published aggregate 5,000 s slide totals only; no per-instance CSV)* | — | — |
| **SC 2026** | **Frobenius 1C** | **122 / 400 — 21.37 s** *(fastest)* | **139 / 400 — 80.24 s** *(fastest)* |
| | [`Lymphosat`](https://c.mov/lymphosat/) (AI-Track #1 Gold) | 81 / 400 — 24.58 s *(1.15x slower)* | 109 / 400 — 90.07 s *(1.12x slower)* |
| | [`satsuma-iter-kissat`](https://github.com/markusa4/satsuma) (Main #1 Gold) | 70 / 400 — 25.13 s *(1.18x slower)* | 112 / 400 — 90.46 s *(1.13x slower)* |

### 6. Four-Format Cross-Product Parity (`.aig.xz` × `.cnf.xz` × `.xcnf.xz` × `.anf.xz`, 1-Core)

- **Protocol:** **AMD Ryzen 9 5950X**, 1 core (`taskset -c 0`), 3-run median wall-clock time (including in-process `.xz` decompression, parsing, solving, and full model verification) at $T_{\max} = 30\;\text{s}$, across **18 representative benchmarks × 4 formats = 72 cells** (**70 / 72 solved**, **0 verdict disagreements**).

| Origin | Benchmark | Verdict | Frobenius (`.aig.xz`) | Frobenius (`.cnf.xz`) | Frobenius (`.xcnf.xz`) | Frobenius (`.anf.xz`) |
|---|---|---:|---:|---:|---:|---:|
| `aig-orig` | `f2_frobenius_n4096` | SAT | 15.55 ms | 15.24 ms | **8.07 ms** | 13.30 ms |
| `aig-orig` | `spn_sat_n96_d48` | SAT | 163.90 ms | 6.47 ms | **5.96 ms** | 102.18 ms |
| `aig-orig` | `factor_wallace_40b` | SAT | **4.20 ms** | 5.73 ms | 4.86 ms | 806.62 ms |
| `aig-orig` | `sha256_64r_k16_unsat` | UNSAT | **66.49 ms** | 112.04 ms | 81.58 ms | *>30 s* |
| `aig-orig` | `spn_sat_n128_d64` | SAT | 8,689.03 ms | 38.75 ms | **36.42 ms** | 1,243.61 ms |
| `aig-orig` | `coupled_n128_d32_unsat` | UNSAT | 2.45 ms | 2.66 ms | **2.21 ms** | 2.68 ms |
| `aig-orig` | `coupled_n512_d128` | SAT | **3.08 ms** | 3.62 ms | 4.36 ms | 3.47 ms |
| `cnf-orig` | `rand3sat_n200_unsat` | UNSAT | **175.49 ms** | 176.45 ms | 175.59 ms | 180.47 ms |
| `cnf-orig` | `hamd_meredith_k3_n50_unsat` | UNSAT | 4.90 ms | 3.78 ms | **3.58 ms** | 5.34 ms |
| `cnf-orig` | `php65x64-sequential` | UNSAT | 6.44 ms | **4.45 ms** | 4.50 ms | 9.40 ms |
| `cnf-orig` | `mod3_n4_r0_s6_unsat` | UNSAT | 148.26 ms | **147.69 ms** | 150.23 ms | 148.74 ms |
| `cnf-orig` | `pret150_25` | UNSAT | 1.96 ms | 2.08 ms | 1.77 ms | **1.70 ms** |
| `cnf-orig` | `BB_72_12_6_w5_unsat` | UNSAT | 100.01 ms | 94.15 ms | **46.02 ms** | 89.07 ms |
| `cnf-orig` | `BB_72_12_6_w6_sat` | SAT | 2.89 ms | **2.33 ms** | 3.03 ms | 21.02 ms |
| `cnf-orig` | `c04` *(Fede rand 3-SAT)* | SAT | 53.89 ms | 55.21 ms | 54.64 ms | **53.39 ms** |
| `cnf-orig` | `c08` *(Fede 48b factoring)* | SAT | 28.22 ms | 20.34 ms | **13.90 ms** | *>30 s* |
| `cnf-orig` | `c11` *(SC25 `ramsey_4_4_18`)* | UNSAT | 60.18 ms | 53.33 ms | **52.83 ms** | 64.33 ms |
| `cnf-orig` | `c12` *(SC25 `cliquecol`)* | UNSAT | 8.27 ms | 4.69 ms | **4.50 ms** | 7.45 ms |

<!-- BEGIN_STRUCTURAL_ANALYSIS -->
## Cross-Collection Phase-Transition & Structural Profile

*Auto-generated across all **785 committed SAT instances** spanning **60 SAT collections** (all four formats: 785 `.cnf.xz`, 785 `.aig.xz`, 785 `.xcnf.xz`, 785 `.anf.xz` = **3,140** compressed files) by [`src/analyze_benchmarks.py`](src/analyze_benchmarks.py). Each row summarizes where the collection sits relative to the clause-length-weighted critical threshold $\rho_{\mathrm{crit}} = \frac{1}{n}\sum_k m_k / \alpha_c(k)$ (`Under` $<0.90\times$, `Near-crit` $0.90\text{--}1.10\times$, `Over` $>1.10\times$), Gent–Walsh constrainedness $\kappa$, clause geometry ($\bar{k}$, `%Bin`, `%Horn`), variable-degree skew (`Deg CV`), extracted XOR parity blocks, and total ANF equations.*

| Collection | Inst | Med $\alpha$ | Med $\alpha_c^{\mathrm{eff}}$ | Med $\rho_{\mathrm{crit}}$ [Min–Max] | Regime Split (U/N/O) | Med $\kappa$ | Med $\bar{k}$ | Bin% | Horn% | Deg CV | XORs | ANF Eqs |
|---|---:|---:|---:|---:|:---:|---:|---:|---:|---:|---:|---:|---:|
| [`aloul-dac02-bench/`](aloul-dac02-bench/README.md) | 32 | 5.60 | 1.07 | **4.50x** [0.31x–9.75x] | 6 / 0 / 26 | 1.87 | 2.19 | 93% | 94% | 0.15 | 618 | 98,363 |
| [`aloul-difp-a/`](aloul-difp-a/README.md) | 14 | 5.46 | 3.70 | **1.48x** [1.48x–1.48x] | 0 / 0 / 14 | 0.98 | 3.33 | 12% | 59% | 0.45 | 5,730 | 59,288 |
| [`aloul-difp-w/`](aloul-difp-w/README.md) | 15 | 5.95 | 4.37 | **1.36x** [1.36x–1.36x] | 0 / 0 / 15 | 0.97 | 3.42 | 8% | 56% | 4.23 | 9,085 | 97,350 |
| [`aloul-fpga-sb-sat/`](aloul-fpga-sb-sat/README.md) | 11 | 4.56 | 1.18 | **3.85x** [3.03x–4.60x] | 0 / 0 / 11 | 1.61 | 2.70 | 84% | 84% | 0.15 | 0 | 14,184 |
| [`aloul-fpga-sb-uns/`](aloul-fpga-sb-uns/README.md) | 10 | 6.35 | 1.01 | **6.25x** [5.00x–9.50x] | 0 / 0 / 10 | 2.59 | 2.13 | 99% | 99% | 0.00 | 0 | 24,008 |
| [`cec-arithmetic-miters/`](cec-arithmetic-miters/README.md) | 5 | 5.20 | 3.69 | **1.36x** [1.36x–1.64x] | 0 / 0 / 5 | 0.91 | 3.30 | 12% | 56% | 0.35 | 831 | 3,819 |
| [`coupled-linear-nonlinear/`](coupled-linear-nonlinear/README.md) | 4 | 4.08 | 3.48 | **1.18x** [1.14x–1.22x] | 0 / 0 / 4 | 0.99 | 3.11 | 3% | 49% | 0.86 | 1,987 | 2,546 |
| [`dense-solver-public/`](dense-solver-public/README.md) | 30 | 4.36 | 1.25 | **2.96x** [0.48x–14.5x] | 2 / 9 / 19 | 1.25 | 2.32 | 74% | 72% | 0.23 | 323 | 24,963 |
| [`dense-solver-synthetic/`](dense-solver-synthetic/README.md) | 20 | 1.86 | 1.05 | **1.53x** [0.55x–32.0x] | 2 / 3 / 15 | 0.65 | 2.28 | 95% | 97% | 0.16 | 0 | 188,258 |
| [`f2-frobenius-circulants/`](f2-frobenius-circulants/README.md) | 6 | 4.50 | 4.98 | **0.90x** [0.90x–0.91x] | 0 / 6 / 0 | 0.87 | 3.67 | 0% | 56% | 0.45 | 8,000 | 6,720 |
| [`fede-intern-challenge/`](fede-intern-challenge/README.md) | 12 | 4.26 | 4.27 | **1.00x** [0.92x–8.19x] | 0 / 8 / 4 | 0.82 | 3.00 | 0% | 50% | 0.28 | 7,550 | 413,044 |
| [`hamd-hamiltonian-cycle/`](hamd-hamiltonian-cycle/README.md) | 22 | 2.64 | 2.60 | **0.99x** [0.75x–1.31x] | 6 / 7 / 9 | 0.54 | 3.19 | 28% | 73% | 0.71 | 0 | 298,001 |
| [`hard-spn/`](hard-spn/README.md) | 4 | 5.67 | 5.31 | **1.07x** [1.06x–1.11x] | 0 / 3 / 1 | 0.92 | 3.60 | 2% | 51% | 1.27 | 1,328 | 1,825 |
| [`heule-matrix-6pooled3and-c1/`](heule-matrix-6pooled3and-c1/README.md) | 10 | 8.88 | 3.37 | **2.64x** [2.64x–2.64x] | 0 / 0 / 10 | 1.22 | 4.69 | 27% | 48% | 0.53 | 43,740 | 882,928 |
| [`heule-matrix-6pooled3and-c3/`](heule-matrix-6pooled3and-c3/README.md) | 1 | 8.87 | 3.37 | **2.63x** [2.63x] | 0 / 0 / 1 | 1.22 | 4.70 | 27% | 48% | 0.53 | 4,374 | 88,236 |
| [`heule-matrix-6pooled3and-c4/`](heule-matrix-6pooled3and-c4/README.md) | 1 | 9.25 | 3.45 | **2.68x** [2.68x] | 0 / 0 / 1 | 1.23 | 4.76 | 27% | 48% | 0.53 | 3,645 | 83,835 |
| [`heule-matrix-challenge1/`](heule-matrix-challenge1/README.md) | 10 | 4.42 | 2.43 | **1.82x** [1.82x–1.82x] | 0 / 0 / 10 | 0.95 | 3.18 | 32% | 73% | 0.96 | 80,190 | 639,928 |
| [`heule-matrix-challenge2/`](heule-matrix-challenge2/README.md) | 10 | 4.42 | 2.43 | **1.82x** [1.82x–1.82x] | 0 / 0 / 10 | 0.95 | 3.18 | 32% | 73% | 0.96 | 80,190 | 639,895 |
| [`heule-matrix-challenge3/`](heule-matrix-challenge3/README.md) | 1 | 4.41 | 2.43 | **1.82x** [1.82x] | 0 / 0 / 1 | 0.94 | 3.18 | 32% | 73% | 0.96 | 8,019 | 63,936 |
| [`heule-matrix-challenge4/`](heule-matrix-challenge4/README.md) | 1 | 4.48 | 2.45 | **1.83x** [1.83x] | 0 / 0 / 1 | 0.95 | 3.20 | 32% | 74% | 0.95 | 7,290 | 60,750 |
| [`heule-matrix-fraction/`](heule-matrix-fraction/README.md) | 3 | 4.52 | 1.73 | **2.60x** [2.60x–2.60x] | 0 / 0 / 3 | 1.26 | 4.68 | 48% | 89% | 0.76 | 0 | 1,424,184 |
| [`heule-matrix-xor6cut/`](heule-matrix-xor6cut/README.md) | 6 | 8.94 | 3.39 | **2.65x** [2.62x–2.68x] | 0 / 0 / 6 | 1.22 | 4.71 | 27% | 48% | 0.53 | 26,244 | 565,146 |
| [`integer-factoring/`](integer-factoring/README.md) | 6 | 5.24 | 3.49 | **1.50x** [1.48x–1.51x] | 0 / 0 / 6 | 0.98 | 3.27 | 13% | 59% | 0.41 | 1,844 | 10,286 |
| [`knights-tour-obstacles/`](knights-tour-obstacles/README.md) | 10 | 2.77 | 2.87 | **0.97x** [0.96x–1.04x] | 0 / 10 / 0 | 0.54 | 3.29 | 24% | 74% | 1.05 | 0 | 356,221 |
| [`mod-circuit-sat/`](mod-circuit-sat/README.md) | 11 | 20.07 | 2.70 | **7.52x** [3.24x–14.2x] | 0 / 0 / 11 | 4.03 | 3.41 | 27% | 73% | 1.10 | 0 | 987,859 |
| [`pretolani-pret/`](pretolani-pret/README.md) | 8 | 2.67 | 4.27 | **0.62x** [0.62x–0.62x] | 8 / 0 / 0 | 0.51 | 3.00 | 0% | 51% | 0.00 | 560 | 560 |
| [`qdistsat-qldpc/`](qdistsat-qldpc/README.md) | 10 | 2.40 | 1.92 | **1.24x** [1.22x–1.25x] | 0 / 0 / 10 | 0.66 | 2.63 | 37% | 75% | 1.02 | 1,474 | 147,815 |
| [`queen-armies/`](queen-armies/README.md) | 8 | 2.04 | 1.48 | **1.39x** [1.29x–1.48x] | 0 / 0 / 8 | 0.66 | 2.42 | 58% | 58% | 0.68 | 0 | 104,931 |
| [`random-3sat-phase-transition/`](random-3sat-phase-transition/README.md) | 8 | 4.26 | 4.27 | **1.00x** [0.89x–1.17x] | 1 / 6 / 1 | 0.82 | 3.00 | 0% | 51% | 0.28 | 0 | 6,904 |
| [`rb-bench-model-rb/`](rb-bench-model-rb/README.md) | 40 | 69.47 | 1.00 | **69.4x** [42.3x–86.2x] | 0 / 0 / 40 | 28.81 | 2.01 | 100% | 100% | 0.19 | 0 | 2,959,100 |
| [`sat-competition-2023-2024-selected/`](sat-competition-2023-2024-selected/README.md) | 14 | 4.00 | 1.91 | **1.92x** [0.37x–62.9x] | 3 / 2 / 9 | 0.97 | 2.68 | 39% | 63% | 0.28 | 71,848 | 6,201,418 |
| [`sat-shortcut-challenge-tier1/`](sat-shortcut-challenge-tier1/README.md) | 47 | 3.33 | 1.89 | **1.75x** [0.62x–72.0x] | 9 / 8 / 30 | 0.92 | 2.61 | 38% | 68% | 0.10 | 6,793 | 310,239 |
| [`sat-shortcut-challenge-tier3/`](sat-shortcut-challenge-tier3/README.md) | 25 | 4.26 | 4.27 | **1.00x** [1.00x–1.00x] | 0 / 25 / 0 | 0.82 | 3.00 | 0% | 50% | 0.27 | 0 | 42,600 |
| [`satlib-ais/`](satlib-ais/README.md) | 4 | 15.43 | 1.26 | **12.3x** [7.47x–17.1x] | 0 / 0 / 4 | 5.47 | 2.31 | 73% | 99% | 0.16 | 0 | 11,334 |
| [`satlib-beijing/`](satlib-beijing/README.md) | 16 | 5.98 | 2.37 | **3.49x** [2.50x–24.8x] | 0 / 0 / 16 | 1.48 | 2.76 | 24% | 100% | 1.16 | 0 | 870,840 |
| [`satlib-bmc/`](satlib-bmc/README.md) | 13 | 4.96 | 1.20 | **3.94x** [3.47x–6.33x] | 0 / 0 / 13 | 1.74 | 2.63 | 81% | 82% | 1.64 | 17,125 | 2,930,376 |
| [`satlib-bms-rti/`](satlib-bms-rti/README.md) | 4 | 3.60 | 4.27 | **0.84x** [0.64x–1.01x] | 2 / 2 / 0 | 0.69 | 3.00 | 0% | 48% | 0.33 | 0 | 1,416 |
| [`satlib-cbs/`](satlib-cbs/README.md) | 6 | 4.29 | 4.27 | **1.01x** [0.94x–1.05x] | 0 / 6 / 0 | 0.83 | 3.00 | 0% | 49% | 0.28 | 0 | 2,542 |
| [`satlib-dimacs-aim/`](satlib-dimacs-aim/README.md) | 72 | 2.00 | 4.22 | **0.47x** [0.37x–1.45x] | 60 / 0 / 12 | 0.39 | 3.00 | 0% | 50% | 0.04 | 0 | 23,162 |
| [`satlib-dimacs-bf/`](satlib-dimacs-bf/README.md) | 4 | 3.11 | 1.54 | **2.01x** [1.94x–2.11x] | 0 / 0 / 4 | 0.96 | 2.52 | 55% | 72% | 0.50 | 28 | 22,223 |
| [`satlib-dimacs-dubois/`](satlib-dimacs-dubois/README.md) | 13 | 2.67 | 4.27 | **0.62x** [0.32x–0.62x] | 13 / 0 / 0 | 0.51 | 3.00 | 0% | 74% | 0.00 | 749 | 749 |
| [`satlib-dimacs-gcp-large/`](satlib-dimacs-gcp-large/README.md) | 4 | 46.79 | 1.00 | **46.7x** [31.1x–62.7x] | 0 / 0 / 4 | 19.39 | 2.02 | 100% | 100% | 0.07 | 0 | 838,147 |
| [`satlib-dimacs-hanoi/`](satlib-dimacs-hanoi/README.md) | 2 | 7.18 | 1.57 | **4.56x** [4.38x–4.74x] | 0 / 0 / 2 | 2.32 | 2.48 | 50% | 75% | 0.57 | 0 | 19,909 |
| [`satlib-dimacs-ii/`](satlib-dimacs-ii/README.md) | 41 | 10.28 | 1.08 | **9.37x** [2.57x–24.1x] | 0 / 0 / 41 | 3.90 | 3.01 | 93% | 97% | 0.64 | 0 | 736,164 |
| [`satlib-dimacs-jnh/`](satlib-dimacs-jnh/README.md) | 50 | 8.50 | 6.05 | **1.37x** [1.10x–1.59x] | 0 / 1 / 49 | 0.87 | 4.89 | 9% | 26% | 0.14 | 0 | 125,683 |
| [`satlib-dimacs-lran/`](satlib-dimacs-lran/README.md) | 3 | 4.25 | 4.27 | **1.00x** [1.00x–1.00x] | 0 / 3 / 0 | 0.82 | 3.00 | 0% | 51% | 0.28 | 0 | 15,300 |
| [`satlib-dimacs-parity/`](satlib-dimacs-parity/README.md) | 30 | 3.66 | 2.62 | **1.40x** [1.15x–1.59x] | 0 / 0 / 30 | 0.87 | 2.78 | 19% | 47% | 0.95 | 18,548 | 52,790 |
| [`satlib-dimacs-phole/`](satlib-dimacs-phole/README.md) | 5 | 4.12 | 1.03 | **4.00x** [3.00x–5.00x] | 0 / 0 / 5 | 1.66 | 2.18 | 97% | 97% | 0.00 | 0 | 1,845 |
| [`satlib-dimacs-ssa/`](satlib-dimacs-ssa/README.md) | 8 | 2.35 | 1.22 | **1.90x** [1.84x–2.04x] | 0 / 0 / 8 | 0.84 | 2.28 | 77% | 78% | 1.30 | 92 | 56,675 |
| [`satlib-flat-gcp/`](satlib-flat-gcp/README.md) | 8 | 3.73 | 1.07 | **3.47x** [3.08x–3.49x] | 0 / 0 / 8 | 1.47 | 2.09 | 91% | 91% | 0.22 | 0 | 10,073 |
| [`satlib-planning-blocksworld/`](satlib-planning-blocksworld/README.md) | 7 | 12.67 | 1.21 | **9.82x** [4.50x–17.3x] | 0 / 0 / 7 | 4.43 | 2.24 | 78% | 87% | 0.36 | 0 | 210,742 |
| [`satlib-planning-logistics/`](satlib-planning-logistics/README.md) | 4 | 8.39 | 1.56 | **5.21x** [4.21x–6.02x] | 0 / 0 / 4 | 2.51 | 2.61 | 55% | 90% | 0.33 | 0 | 55,604 |
| [`satlib-qg/`](satlib-qg/README.md) | 22 | 39.81 | 1.84 | **20.4x** [12.5x–40.6x] | 0 / 0 / 22 | 10.96 | 2.66 | 40% | 99% | 0.02 | 0 | 1,742,827 |
| [`satlib-rnd3sat/`](satlib-rnd3sat/README.md) | 10 | 4.30 | 4.27 | **1.01x** [1.00x–1.02x] | 0 / 10 / 0 | 0.83 | 3.00 | 0% | 50% | 0.27 | 0 | 6,436 |
| [`satlib-sw-gcp/`](satlib-sw-gcp/README.md) | 5 | 6.20 | 1.03 | **6.01x** [6.01x–6.01x] | 0 / 0 / 5 | 2.50 | 2.10 | 97% | 97% | 0.07 | 0 | 16,500 |
| [`sha256-preimage/`](sha256-preimage/README.md) | 5 | 6.50 | 5.58 | **1.16x** [1.16x–1.23x] | 0 / 0 / 5 | 0.94 | 3.52 | 2% | 50% | 0.65 | 77,329 | 309,573 |
| [`sigal-aes256-xcnf/`](sigal-aes256-xcnf/README.md) | 2 | 6.78 | 3.85 | **1.76x** [1.76x–1.76x] | 0 / 0 / 2 | 1.08 | 3.53 | 15% | 54% | 1.14 | 85,624 | 331,648 |
| [`tseitin-expanders/`](tseitin-expanders/README.md) | 4 | 3.60 | 4.98 | **0.72x** [0.72x–0.72x] | 4 / 0 / 0 | 0.70 | 3.67 | 0% | 56% | 0.26 | 880 | 880 |
| [`vlsat-2/`](vlsat-2/README.md) | 10 | 15.52 | 1.00 | **15.5x** [13.7x–22.2x] | 0 / 0 / 10 | 6.42 | 2.04 | 100% | 100% | 0.33 | 0 | 140,639 |
| [`zed-adversarial-hub-php/`](zed-adversarial-hub-php/README.md) | 18 | 3.44 | 1.25 | **2.76x** [1.42x–3.08x] | 0 / 0 / 18 | 1.69 | 2.03 | 51% | 97% | 1.38 | 10,146 | 151,922 |
<!-- END_STRUCTURAL_ANALYSIS -->

## Format Conventions

- **Binary AIGER 1.9 (`aig-orig/*.aig.xz`, `aig-converted/*.aig.xz`):** Standard Armin Biere combinational AIGER format (`aig M I 0 1 A`) with `L = 0` latches and `O = 1` primary output `PO_0` that evaluates to `1` iff all circuit assertions / CNF clauses are satisfied, stored xz-compressed. Readable directly after `xz -dc` by Berkeley [`abc`](https://github.com/berkeley-abc/abc), `aigtoaig`, `aigtocnf`, [Yosys](https://github.com/YosysHQ/yosys), and HWMCC toolchains (and natively in-process by Frobenius).
- **DIMACS CNF / XCNF (`cnf-orig/*.cnf.xz`, `cnf-converted/*.cnf.xz`, `xcnf-orig/*.xcnf.xz`, `xcnf-converted/*.xcnf.xz`):** Standard SAT Competition `p cnf <vars> <clauses>` format stored xz-compressed; `.xcnf.xz` files include native [CryptoMiniSat](https://github.com/msoos/cryptominisat) `x l1 ... lk 0` XOR parity clauses.
- **DIMACS-ANF (`anf-converted/*.anf.xz`):** Standard Bosphorus/PolyBoRi Algebraic Normal Form (`p anf <nv> <neq>`, `x <mon1> <mon2> ... 0` over $\mathbb{F}_2$ with `T` = constant `1` and `.` monomial products), generated losslessly in linear size by [`src/to_anf.py`](src/to_anf.py) (degree $\le 2$ from `aig-orig/`, degree $\le 3$ from `xcnf-orig/` / `xcnf-converted/`).
- **MATA Automata (`mata-orig/*.mata.xz`):** Standard VeriFIT `.mata` NFA format stored xz-compressed.

## License

- Repository-authored original collections and generator/conversion scripts are licensed under the **MIT License** — see [`LICENSE`](LICENSE).
- Sourced collections retain their original upstream licenses, notices, and provenance links inside their respective directories:
  - [`sat-competition-2023-2024-selected/LICENSE`](sat-competition-2023-2024-selected/LICENSE) & [`sat-competition-2024-2026-main-track/LICENSE`](sat-competition-2024-2026-main-track/LICENSE) — Creative Commons Attribution 4.0 International (**CC-BY-4.0**) for SAT Competition / GBD archives + MIT for scripts.
  - [`sat-shortcut-challenge-tier1/LICENSE`](sat-shortcut-challenge-tier1/LICENSE) & [`sat-shortcut-challenge-tier3/LICENSE`](sat-shortcut-challenge-tier3/LICENSE) — **Apache License 2.0** (`keithadler/sat-shortcut-challenge`).
  - [`dense-solver-public/LICENSE`](dense-solver-public/LICENSE), [`dense-solver-synthetic/LICENSE`](dense-solver-synthetic/LICENSE), & [`SOURCES.md`](dense-solver-public/SOURCES.md) — **MIT License** (`libdense/dense-solver`) + preserved SATLIB / SC 2025 attributions.
  - [`mata-presburger-nfa-tptp/LICENSE`](mata-presburger-nfa-tptp/LICENSE) & [`mata-presburger-nfa-ultimate-automizer/LICENSE`](mata-presburger-nfa-ultimate-automizer/LICENSE) — **MIT License** (`VeriFIT/mata`).
  - [`qdistsat-qldpc/LICENSE`](qdistsat-qldpc/LICENSE) & [`NOTICE`](qdistsat-qldpc/NOTICE) — **GNU General Public License v3.0 or later (`GPL-3.0-or-later`)** (`guluchen/QDistSAT` / `DistQLDPC`, with retained `codeDistancePYPI` MIT notices).
  - Public academic archives and community-contributed collections without dedicated upstream `LICENSE` files (`aloul-*`, `fede-intern-challenge`, `heule-matrix-*`, `mod-circuit-sat`, `pretolani-pret`, `rb-bench-model-rb`, `satlib-*`, `sigal-aes256-xcnf`, `vlsat-2`) carry explicit author attributions, papers, and upstream links in each collection's `README.md`.
