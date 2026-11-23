# MATA Presburger Explicit-Complement NFA Benchmarks — TPTP (`mata-presburger-nfa-tptp`)

## Provenance & Credit

- **Recommended by:** [`@TravisRudd`](https://twitter.com/TravisRudd) (Twitter/X)
- **Upstream Benchmark Repository:** [`VeriFIT/nfa-bench`](https://github.com/VeriFIT/nfa-bench) (`bench-single-presburger-explicit-complement.input` / Presburger explicit-complement set)
- **Upstream Automata Library:** [`VeriFIT/mata`](https://github.com/VeriFIT/mata) (Brno University of Technology, VeriFIT group)
- **License:** MIT License — see [`LICENSE`](LICENSE) (copied from `VeriFIT/mata`).
- **Companion Collection:** [`mata-presburger-nfa-ultimate-automizer/`](../mata-presburger-nfa-ultimate-automizer/README.md)
- **Primary Paper:** D. Chocholatý, T. Fiedor, V. Havlena, L. Holík, M. Hruška, O. Lengál, and J. Síč, *"Mata: A Fast and Simple Finite Automata Library"*, TACAS 2024, LNCS 14570, pp. 130–151, DOI: [`10.1007/978-3-031-57249-4_7`](https://doi.org/10.1007/978-3-031-57249-4_7).

## Problem Description

This collection contains non-deterministic finite automata (NFAs) in the `.mata` text format (stored xz-compressed in `mata-orig/`) arising from Presburger arithmetic decision procedures and program verification: **TPTP Presburger arithmetic encodings (`ARI*`, `NUM*`; 21 `.mata.xz` NFAs)**. The core benchmark task is **explicit NFA complementation** (determinization / subset construction + complementation), where intermediate DFA state spaces can blow up exponentially even for compact input NFAs.

Note: Unlike the propositional SAT collections in this repository, MATA instances represent **finite automata** (`.mata` transition relations over symbolic/explicit alphabets) rather than propositional SAT formulas, so no `.cnf`/`.aig`/`.xcnf`/`.anf` conversion is applied.

## Corpus & Data Sizes

- **`mata-orig/`** — **21 `.mata.xz` automata** (6.4 KB compressed total).
- **`src/fetch_mata_presburger.py`** — Standalone fetcher script to refresh `mata-orig/` directly from [`VeriFIT/nfa-bench`](https://github.com/VeriFIT/nfa-bench).

## Published Benchmarks & References

- **Chocholatý et al. (TACAS 2024):** Benchmarked [Mata](https://github.com/VeriFIT/mata) against [Awali](https://gitlab.in2p3.fr/vaucanson/awali), [Automata.net](https://github.com/AutomataDotNet/Automata), [Brics](https://www.brics.dk/automaton/), [DK.Brics](https://www.brics.dk/automaton/), [FAdo](https://fado.dcc.fc.up.pt/), [OpenFST](https://www.openfst.org/), and [VATA](https://github.com/ondrik/libvata) across string-constraint, regex, and Presburger complementation workloads, establishing Mata as a state-of-the-art C++ NFA engine.
- **Ergodis Notes ([`@TravisRudd`](https://twitter.com/TravisRudd)):** Evaluated all 169 entries of `bench-single-presburger-explicit-complement.input` as an automata complementation stress test alongside SAT workloads.

## Comparative 1-Core Benchmark Results (All 21 NFAs, Native `.mata.xz`, $T_{\max} = 5\;\text{s}$)

- **Hardware & Protocol:** **AMD Ryzen 9 5950X** (16C/32T Linux, **1 thread per run** pinned across 8 dedicated physical cores, $T_{\max} = 5\;\text{s}$ per mode, full wall-clock time including in-process `.xz` decompression and `.mata` parsing). **100% of all 21 automata** were run across three Frobenius NFA decision modes: non-emptiness ($L(A) \neq \emptyset$), antichain complement/universality (`--mata-complement`, $L(A) = \Sigma^*$ iff UNSAT), and explicit subset-construction complementation (`--mata-explicit-complement`). All SAT/UNSAT complement verdicts agreed **100%** between antichain and explicit modes (0 errors, 0 timeouts).

| Frobenius Mode | Solved | SAT / UNSAT | Total Time | Min | Median | Mean | Max |
|---|---:|:---:|---:|---:|---:|---:|---:|
| **Frobenius 1C — Emptiness** (default) | **21 / 21** | 21 / 0 | **49.67 ms** | 1.61 ms | 2.20 ms | 2.37 ms | 3.42 ms |
| **Frobenius 1C — Antichain Complement** (`--mata-complement`) | **21 / 21** | 17 / 4 | **42.56 ms** | 1.62 ms | 1.97 ms | 2.03 ms | 3.11 ms |
| **Frobenius 1C — Explicit Complement** (`--mata-explicit-complement`) | **21 / 21** | 17 / 4 | **42.00 ms** | 1.65 ms | 1.86 ms | 2.00 ms | 4.02 ms |

### Per-Automaton Timings (All 21 NFAs)

| Automaton | Emptiness Verdict | Frobenius Emptiness | Complement Verdict | Frobenius Antichain (`--mata-complement`) | Frobenius Explicit (`--mata-explicit-complement`) |
|---|:---:|---:|:---:|---:|---:|
| `ARI056_1` | SAT | 3.30 ms | SAT | 3.11 ms | 2.29 ms |
| `ARI083_1` | SAT | 3.09 ms | SAT | 2.38 ms | 2.11 ms |
| `ARI572_1` | SAT | 2.90 ms | UNSAT | 2.14 ms | 1.77 ms |
| `ARI590_1` | SAT | 2.52 ms | SAT | 1.99 ms | 1.88 ms |
| `ARI591_1` | SAT | 2.65 ms | SAT | 2.21 ms | 1.98 ms |
| `ARI592_1` | SAT | 2.59 ms | UNSAT | 2.16 ms | 2.00 ms |
| `NUM865_1` | SAT | 3.42 ms | UNSAT | 2.36 ms | 4.02 ms |
| `NUM868_1` | SAT | 2.03 ms | SAT | 2.00 ms | 1.87 ms |
| `NUM869_1` | SAT | 2.14 ms | SAT | 2.09 ms | 2.12 ms |
| `NUM870_1` | SAT | 1.61 ms | SAT | 1.62 ms | 1.75 ms |
| `NUM871_1` | SAT | 2.34 ms | SAT | 1.87 ms | 1.76 ms |
| `NUM874_1` | SAT | 2.07 ms | SAT | 1.76 ms | 1.73 ms |
| `NUM895_1` | SAT | 1.86 ms | UNSAT | 1.67 ms | 1.82 ms |
| `NUM896_1` | SAT | 1.96 ms | SAT | 1.95 ms | 2.10 ms |
| `NUM897_1` | SAT | 3.02 ms | SAT | 1.92 ms | 1.74 ms |
| `NUM898_1` | SAT | 1.87 ms | SAT | 1.97 ms | 1.86 ms |
| `NUM899_1` | SAT | 2.20 ms | SAT | 2.15 ms | 2.31 ms |
| `NUM915_1` | SAT | 2.37 ms | SAT | 1.68 ms | 1.65 ms |
| `NUM916_1` | SAT | 1.93 ms | SAT | 1.86 ms | 1.67 ms |
| `NUM917_1` | SAT | 2.01 ms | SAT | 1.89 ms | 1.79 ms |
| `NUM918_1` | SAT | 1.79 ms | SAT | 1.78 ms | 1.78 ms |

<!-- BEGIN_STRUCTURAL_ANALYSIS -->
## Automata Structural Analysis

*Auto-generated by [`../src/analyze_benchmarks.py`](../src/analyze_benchmarks.py). Because MATA benchmarks encode non-deterministic finite automata rather than clausal CNF formulas, clause-to-variable phase-transition ratios ($\alpha / \alpha_c$) do not apply; instead we report NFA state, transition, and alphabet densities (transition-to-state ratio $\delta = |\Delta|/|Q|$).*

| Directory | NFAs | States $|Q|$ (Med / Max) | Transitions $|\Delta|$ (Med / Max) | Symbols $|\Sigma|$ (Med / Max) | Transition Density $|\Delta|/|Q|$ (Med) |
|---|---:|---:|---:|---:|---:|
| `mata-orig/` | 21 | 7 / 15 | 34 / 1,792 | 8 / 128 | 8.00 |
<!-- END_STRUCTURAL_ANALYSIS -->
