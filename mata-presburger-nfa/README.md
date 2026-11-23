# MATA Presburger Explicit-Complement NFA Benchmarks (TACAS 2024)

## Provenance & Credit

- **Recommended by:** `@TravisRudd` (Twitter/X)
- **Upstream Benchmark Repository:** [`VeriFIT/nfa-bench`](https://github.com/VeriFIT/nfa-bench) (`bench-single-presburger-explicit-complement.input` / Presburger explicit-complement set)
- **Upstream Automata Library:** [`VeriFIT/mata`](https://github.com/VeriFIT/mata) (Brno University of Technology, VeriFIT group)
- **License:** MIT License — see [`LICENSE`](LICENSE) (copied from `VeriFIT/mata`).
- **Primary Paper:** D. Chocholatý, T. Fiedor, V. Havlena, L. Holík, M. Hruška, O. Lengál, and J. Síč, *"Mata: A Fast and Simple Finite Automata Library"*, TACAS 2024, LNCS 14570, pp. 130–151, DOI: [`10.1007/978-3-031-57249-4_7`](https://doi.org/10.1007/978-3-031-57249-4_7).

## Problem Description

This suite contains non-deterministic finite automata (NFAs) in the `.mata` text format (stored compressed as `.mata.xz`) arising from Presburger arithmetic decision procedures and program verification (Ultimate Automizer and TPTP Presburger encodings). The core benchmark task is **explicit NFA complementation** (determinization / subset construction + complementation), where intermediate DFA state spaces can blow up exponentially even for compact input NFAs.

Note: Unlike the clausal `.cnf` and combinational `.aig` suites in this repository, MATA instances represent **finite automata** (`.mata` transition relations over symbolic/explicit alphabets) rather than propositional SAT formulas, so no `.cnf`/`.aig` conversion is applied.

## Corpus & Data Sizes

The repository ships **174 `.mata.xz` automata** (`2.74 MB` compressed total), covering all 169 entries of `bench-single-presburger-explicit-complement.input` plus the remaining complement files in the same upstream directory:

| Subdirectory | Origin | Files (`.mata.xz`) | Compressed Size |
|---|---|---:|---:|
| `complement/UltimateAutomizer/` | Ultimate Automizer software model checking traces (e.g., `MADWiFi`, `Primes`, `recHanoi03`) | 153 | 2.66 MB |
| `complement/tptp/` | TPTP Presburger arithmetic encodings (`ARI*`, `NUM*`) | 21 | 0.08 MB |
| **Total** | | **174** | **2.74 MB** |

To regenerate or refresh the archive from upstream, see [`src/fetch_mata_presburger.py`](src/fetch_mata_presburger.py).

## Published Benchmarks & References

- **Chocholatý et al. (TACAS 2024):** Benchmarked `Mata` against `Awali`, `Automata.net`, `Brics`, `DK.Brics`, `FAdo`, `OpenFST`, and `VATA` across string-constraint, regex, and Presburger complementation workloads, establishing Mata as a state-of-the-art C++ NFA engine.
- **Ergodis Notes (`@TravisRudd`):** Evaluated all 169 entries of `bench-single-presburger-explicit-complement.input` as an automata complementation stress test alongside SAT workloads.
