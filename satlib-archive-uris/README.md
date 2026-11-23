# UBC SATLIB Complete 97-Archive URI Manifest (`satlib-archive-uris`)

## Provenance & Credit

- **Recommended by:** [`@jasonslenderman`](https://twitter.com/jasonslenderman) (Twitter/X)
- **Upstream Archive:** [SATLIB — Benchmark Problems (UBC)](https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html)
- **Maintainers & Curators:** Holger H. Hoos and Thomas Stützle (University of British Columbia / TU Darmstadt)
- **Primary Paper:** H. H. Hoos and T. Stützle, *"SATLIB: An Online Resource for Research on SAT"*, SAT 2000, IOS Press, pp. 283–292 (2000).
- **License:** Classic public scientific benchmark collection redistributed by UBC SATLIB for academic SAT research; no separate upstream `LICENSE` file is bundled in the archives.

## Directory Layout & Usage

Rather than duplicating multi-gigabyte synthetic ensemble archives (50,000+ raw formulas) in Git, this collection stores the complete official manifest of all **97 UBC SATLIB `.tar.gz` archive URLs** alongside a parallel downloader script (parallel to [`../sat-competition-2024-2026-main-track/`](../sat-competition-2024-2026-main-track/README.md)):

- [`satlib_all_97_archives.uri`](satlib_all_97_archives.uri) — Complete list of all 97 official UBC SATLIB `.tar.gz` URLs.
- [`src/fetch_satlib.py`](src/fetch_satlib.py) — Parallel archive downloader (`python3 src/fetch_satlib.py --all-archives <out_dir>`).

## Committed Standalone SATLIB Collections (331 Instances Across 22 Collections, All 4 Formats)

Every instance from all 17 structured SATLIB/DIMACS/Beijing families (298 instances in full; Pretolani's `PRET` formulas live in [`../pretolani-pret/`](../pretolani-pret/README.md)) plus 33 stratified representatives across all 5 synthetic ensembles are committed directly in 22 standalone top-level collections (all 4 formats: `cnf-orig/`, `aig-converted/`, `xcnf-converted/`, `anf-converted/`):

| Collection | Category / Domain | Instances | `.cnf.xz` | `.aig.xz` | `.xcnf.xz` | `.anf.xz` |
|---|---|---:|---:|---:|---:|---:|
| [`satlib-ais/`](../satlib-ais/README.md) | All-Interval Series (full) | 4 | 13.4 KB | 19.3 KB | 13.1 KB | 21.6 KB |
| [`satlib-beijing/`](../satlib-beijing/README.md) | 1996 Beijing SAT Competition (full) | 16 | 637.2 KB | 1.05 MB | 623.8 KB | 1.92 MB |
| [`satlib-bmc/`](../satlib-bmc/README.md) | Bounded Model Checking — Shtrichman (full) | 13 | 4.67 MB | 5.41 MB | 4.53 MB | 12.83 MB |
| [`satlib-bms-rti/`](../satlib-bms-rti/README.md) | Backbone-Minimal Random 3-SAT (sample / 1,000*) | 4 | 6.9 KB | 8.6 KB | 7.1 KB | 12.8 KB |
| [`satlib-cbs/`](../satlib-cbs/README.md) | Controlled Backbone Random 3-SAT (sample / 40,000*) | 6 | 12.1 KB | 15.0 KB | 12.4 KB | 22.4 KB |
| [`satlib-dimacs-aim/`](../satlib-dimacs-aim/README.md) | Artificial Random 3-SAT — Iwama et al. (full) | 72 | 121.6 KB | 142.7 KB | 125.2 KB | 197.8 KB |
| [`satlib-dimacs-bf/`](../satlib-dimacs-bf/README.md) | Circuit Bridge-Fault Analysis (full) | 4 | 61.0 KB | 73.7 KB | 61.0 KB | 113.9 KB |
| [`satlib-dimacs-dubois/`](../satlib-dimacs-dubois/README.md) | Dubois Hard Parity UNSAT (full) | 13 | 11.6 KB | 13.7 KB | 7.3 KB | 5.4 KB |
| [`satlib-dimacs-gcp-large/`](../satlib-dimacs-gcp-large/README.md) | Large Graph Colouring `g125`/`g250` (full) | 4 | 586.2 KB | 294.7 KB | 476.6 KB | 994.4 KB |
| [`satlib-dimacs-hanoi/`](../satlib-dimacs-hanoi/README.md) | Towers of Hanoi `hanoi4`, `hanoi5` (full) | 2 | 33.4 KB | 39.4 KB | 33.3 KB | 64.1 KB |
| [`satlib-dimacs-ii/`](../satlib-dimacs-ii/README.md) | Inductive Inference (full) | 41 | 382.0 KB | 770.7 KB | 383.9 KB | 2.40 MB |
| [`satlib-dimacs-jnh/`](../satlib-dimacs-jnh/README.md) | Variable-Length Random SAT — Hooker (full) | 50 | 285.7 KB | 373.9 KB | 288.0 KB | 970.1 KB |
| [`satlib-dimacs-lran/`](../satlib-dimacs-lran/README.md) | Large Random 3-SAT `f600`/`f1000`/`f2000` (full) | 3 | 90.1 KB | 87.7 KB | 90.2 KB | 165.2 KB |
| [`satlib-dimacs-parity/`](../satlib-dimacs-parity/README.md) | Parity Learning `par8`/`par16`/`par32` (full) | 30 | 252.4 KB | 345.3 KB | 125.0 KB | 189.7 KB |
| [`satlib-dimacs-phole/`](../satlib-dimacs-phole/README.md) | Pigeonhole Principle `hole6..10` (full) | 5 | 4.6 KB | 5.2 KB | 4.8 KB | 6.1 KB |
| [`satlib-dimacs-ssa/`](../satlib-dimacs-ssa/README.md) | Single-Stuck-At Circuit Faults (full) | 8 | 147.5 KB | 176.3 KB | 146.9 KB | 282.7 KB |
| [`satlib-flat-gcp/`](../satlib-flat-gcp/README.md) | Flat 3-Colourable Graphs `flat30..200` (sample / 1,700*) | 8 | 19.5 KB | 21.0 KB | 20.0 KB | 29.6 KB |
| [`satlib-planning-blocksworld/`](../satlib-planning-blocksworld/README.md) | SATPLAN Blocks World (full) | 7 | 229.8 KB | 454.9 KB | 229.9 KB | 492.0 KB |
| [`satlib-planning-logistics/`](../satlib-planning-logistics/README.md) | SATPLAN Logistics `a..d` (full) | 4 | 79.7 KB | 126.2 KB | 80.0 KB | 223.0 KB |
| [`satlib-qg/`](../satlib-qg/README.md) | Quasigroup / Latin Squares — Zhang (full) | 22 | 1.64 MB | 4.23 MB | 1.64 MB | 4.91 MB |
| [`satlib-rnd3sat/`](../satlib-rnd3sat/README.md) | Uniform Random 3-SAT `uf`/`uuf50..250` (sample / 6,600*) | 10 | 33.1 KB | 37.1 KB | 33.6 KB | 59.2 KB |
| [`satlib-sw-gcp/`](../satlib-sw-gcp/README.md) | Morphed Small-World 5-Colouring `lp0..p0` (sample / 901*) | 5 | 19.1 KB | 23.7 KB | 19.5 KB | 35.9 KB |

<!-- BEGIN_STRUCTURAL_ANALYSIS -->
## Phase-Transition & Structural Analysis

*Auto-generated by [`../src/analyze_benchmarks.py`](../src/analyze_benchmarks.py). This directory stores **97 official UBC SATLIB `.tar.gz` archive URIs** across 1 manifest(s) rather than duplicating multi-gigabyte synthetic archives in Git; run `python3 src/fetch_satlib.py --all-archives <out_dir>` to download upstream tarballs, or inspect the 22 committed standalone SATLIB collections (`../satlib-*/`) for full four-format structural and phase-transition metrics.*
<!-- END_STRUCTURAL_ANALYSIS -->

## References

- H. H. Hoos and T. Stützle, *"SATLIB: An Online Resource for Research on SAT"*, SAT 2000, IOS Press, pp. 283–292 ([`cs.ubc.ca/~hoos/SATLIB/`](https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html)).
- D. S. Johnson and M. A. Trick (eds.), *Cliques, Coloring, and Satisfiability: Second DIMACS Implementation Challenge*, DIMACS Series vol. 26, AMS, 1996.
