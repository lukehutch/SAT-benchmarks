# SATLIB Classic Benchmark Collection (`satlib-benchmarks`)

## Provenance & Credit

- **Recommended by:** [`@jasonslenderman`](https://twitter.com/jasonslenderman) (Twitter/X)
- **Upstream Archive:** [SATLIB — Benchmark Problems (UBC)](https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html)
- **Maintainers & Curators:** Holger H. Hoos and Thomas Stützle (University of British Columbia / TU Darmstadt)
- **Primary Paper:** H. H. Hoos and T. Stützle, *"SATLIB: An Online Resource for Research on SAT"*, in I. P. Gent, H. van Maaren, and T. Walsh (eds.), *SAT 2000: Highlights of Satisfiability Research in the Year 2000*, IOS Press, pp. 283–292 (2000).
- **Upstream Contributors (across the 22 families):** Henry Kautz & Bart Selman (Planning: Blocks World, Logistics), Hantao Zhang (Quasigroup / Latin Squares), Ofer Shtrichman (Bounded Model Checking), Olivier Dubois (`dubois`), James Crawford (`parity`), Allen Van Gelder & Yumi Tsuji (`bf`, `ssa`), Joseph Culberson (`flat-gcp`), Ian Gent / Toby Walsh (`sw-gcp`), Josh Singer (`BMS`/`RTI`, `CBS`), John Hooker (`jnh`, `phole`), Kazuo Iwama et al. (`aim`), and the 1993 Second DIMACS Implementation Challenge & 1996 Beijing SAT Competition organizers.
- **License:** Classic public scientific benchmark collection redistributed by UBC SATLIB for academic SAT research; no separate upstream `LICENSE` file is bundled in the archives.
- **Format Hygiene Notes:**
  1. Legacy SATLIB trailing `%` / `0` EOF sentinels are stripped and wrapped multi-line clauses normalized to canonical 1-clause-per-line DIMACS CNF so every modern SAT solver parses all **331 / 331** files cleanly.
  2. Leading `c p ...` comment lines in 32 files (`dimacs-bf`, `dimacs-dubois`, `dimacs-ssa`, `flat-gcp`) are prefixed as `c - p ...` (zero clause/variable changes) so [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18's model-counting directive parser reads them without error.
  3. *Historical upstream quirk preserved:* Upstream SATLIB's `dimacs-dubois/dubois100.cnf` omits the trailing `0` terminator on 202 of its 800 lines in the original 1993 file, fusing adjacent clauses into tautologies (`598` `0`-terminated clauses); all five modern DIMACS solvers agree verbatim `dubois100.cnf` is SAT while `dubois20..50` are UNSAT.
  4. Pretolani's 8 `PRET` formulas from the same SATLIB DIMACS page live in their own dedicated suite [`../pretolani-pret/`](../pretolani-pret/README.md).

## Corpus & Data Sizes (331 Instances across All 22 Families + Full 97-Archive URI Manifest)

Every single instance from all **17 structured SATLIB, DIMACS, and Beijing collections** (298 instances in full, excluding `PRET` in `../pretolani-pret/`) plus **33 stratified representatives** spanning all **5 large synthetic ensembles** (`RND3SAT`, `BMS/RTI`, `CBS`, `flat-GCP`, `SW-GCP`) are committed in **all three formats**:
- `<family>/*.cnf.xz` — **331** sanitized DIMACS CNFs (`9.26 MB` xz-compressed)
- `aig-version/<family>/*.aig` — **331** exact Binary AIGER 1.9 conversions (`55.34 MB`, all **331 / 331** independently verified via [Berkeley ABC](https://github.com/berkeley-abc/abc) `read_aiger`, `0` errors)
- `xcnf-version/<family>/*.xcnf.xz` — **331** lossless [CryptoMiniSat](https://github.com/msoos/cryptominisat) XCNF conversions (`8.87 MB`, extracting **`36,542`** native XOR parity clauses)
- [`satlib_all_97_archives.uri`](satlib_all_97_archives.uri) & [`src/fetch_satlib.py`](src/fetch_satlib.py) — complete manifest of all **97 official UBC SATLIB `.tar.gz` URLs** (50,000+ total synthetic ensemble instances downloadable on demand), plus `src/cnf2aig.py` and `src/cnf2xcnf.py`.

| Family Directory | Category / Domain | Instances | Vars Range | Clauses Range | AIG ANDs Range | `.cnf.xz` Size |
|---|---|---:|---:|---:|---:|---:|
| `ais/` | All-Interval Series (full) | 4 | 61–265 | 581–5,666 | 1,166–10,834 | 13.4 KB |
| `beijing/` | 1996 Beijing SAT Competition (full) | 16 | 125–22,500 | 310–123,329 | 729–339,995 | 637.2 KB |
| `bmc/` | Bounded Model Checking — Shtrichman (full) | 13 | 2,810–63,624 | 11,683–368,352 | 26,769–838,395 | 4.67 MB |
| `bms-rti/` | Backbone-Minimal Random 3-SAT (sample / 1,000*) | 4 | 100 | 272–429 | 815–1,279 | 6.9 KB |
| `cbs/` | Controlled Backbone Random 3-SAT (sample / 40,000*) | 6 | 100 | 403–449 | 1,198–1,339 | 12.1 KB |
| `dimacs-aim/` | Artificial Random 3-SAT — Iwama et al. (full) | 72 | 50–200 | 80–1,200 | 224–3,535 | 121.6 KB |
| `dimacs-bf/` | Circuit Bridge-Fault Analysis (full) | 4 | 1,040–2,180 | 3,434–6,778 | 7,848–16,661 | 61.0 KB |
| `dimacs-dubois/` | Dubois Hard Parity UNSAT (full) | 13 | 60–300 | 160–598 | 479–1,199 | 11.6 KB |
| `dimacs-gcp-large/` | Large Graph Colouring `g125`/`g250` (full) | 4 | 2,125–7,250 | 66,272–454,622 | 134,418–915,993 | 586.2 KB |
| `dimacs-hanoi/` | Towers of Hanoi `hanoi4`, `hanoi5` (full) | 2 | 718–1,931 | 4,934–14,468 | 11,190–32,846 | 33.4 KB |
| `dimacs-ii/` | Inductive Inference (full) | 41 | 66–1,728 | 186–24,792 | 437–52,752 | 382.0 KB |
| `dimacs-jnh/` | Variable-Length Random SAT — Hooker (full) | 50 | 100 | 800–900 | 3,742–4,452 | 285.7 KB |
| `dimacs-lran/` | Large Random 3-SAT `f600`/`f1000`/`f2000` (full) | 3 | 600–2,000 | 2,550–8,500 | 7,643–25,494 | 90.1 KB |
| `dimacs-parity/` | Parity Learning `par8`/`par16`/`par32` (full) | 30 | 64–3,176 | 254–10,325 | 700–27,244 | 252.4 KB |
| `dimacs-phole/` | Pigeonhole Principle `hole6..10` (full) | 5 | 42–110 | 133–561 | 293–1,209 | 4.6 KB |
| `dimacs-ssa/` | Single-Stuck-At Circuit Faults (full) | 8 | 435–10,410 | 1,027–34,238 | 2,333–84,551 | 147.6 KB |
| `flat-gcp/` | Flat 3-Colourable Graphs `flat30..200` (sample / 1,700*) | 8 | 90–600 | 300–2,237 | 629–4,673 | 19.5 KB |
| `planning-blocksworld/` | SATPLAN Blocks World (full) | 7 | 48–6,325 | 261–131,973 | 525–294,117 | 229.8 KB |
| `planning-logistics/` | SATPLAN Logistics `a..d` (full) | 4 | 828–4,713 | 6,718–21,991 | 17,751–51,346 | 79.7 KB |
| `qg/` | Quasigroup / Latin Squares — Zhang (full) | 22 | 343–2,197 | 9,685–148,957 | 23,908–337,034 | 1.64 MB |
| `rnd3sat/` | Uniform Random 3-SAT `uf`/`uuf50..250` (sample / 6,600*) | 10 | 50–250 | 218–1,065 | 643–3,186 | 33.1 KB |
| `sw-gcp/` | Morphed Small-World 5-Colouring `lp0..p0` (sample / 901*) | 5 | 500 | 3,100 | 6,499 | 19.1 KB |
| **Total** | **22 SATLIB Families (+ 97-archive URI list)** | **331** | **42–63,624** | **80–454,622** | **331 `.aig` + 331 `.xcnf.xz`** | **9.26 MB** |

## Comparative 1-Core Benchmark Results (All 331 Instances, Flat `.cnf`, $T_{\max} = 5\;\text{s}$)

- **Hardware & Protocol:** Same machine (**AMD Ryzen 9 5950X**, Linux, 1 core per run, $T_{\max} = 5\;\text{s}$, PAR-2 penalty $10{,}000\;\text{ms}$, identical sanitized flat `.cnf` input). **0 verdict disagreements / 0 errors across all 331 × 5 = 1,655 solver runs**; all Frobenius SAT assignments verified clause-by-clause.

| Family (Instances) | Frobenius 1C | [`dense-solver 0.0.4`](https://github.com/libdense/dense-solver) | [Kissat](https://github.com/arminbiere/kissat) 4.0.4 | [CaDiCaL](https://github.com/arminbiere/cadical) 3.1.0 | [CryptoMiniSat](https://github.com/msoos/cryptominisat) 5.18.0 |
|---|---:|---:|---:|---:|---:|
| `ais` (4) | 4/4 — 26.0 ms | 4/4 — 39.1 ms | **4/4 — 24.2 ms** | 4/4 — 26.3 ms | 4/4 — 425.8 ms |
| `beijing` (16) | **16/16 — 2,502.3 ms** | 15/16 — 13,024.9 ms | 16/16 — 3,524.6 ms | 15/16 — 10,304.9 ms | 15/16 — 17,413.8 ms |
| `bmc` (13) | 13/13 — 8,640.7 ms | 13/13 — 11,642.4 ms | **13/13 — 2,690.7 ms** | 13/13 — 4,974.2 ms | 13/13 — 17,643.5 ms |
| `bms-rti` (4) | 4/4 — 16.2 ms | **4/4 — 8.2 ms** | 4/4 — 47.9 ms | 4/4 — 19.2 ms | 4/4 — 85.4 ms |
| `cbs` (6) | 6/6 — 14.3 ms | **6/6 — 8.9 ms** | 6/6 — 99.3 ms | 6/6 — 26.0 ms | 6/6 — 163.5 ms |
| `dimacs-aim` (72) | 72/72 — 1,189.4 ms | **72/72 — 259.7 ms** | 72/72 — 527.6 ms | 72/72 — 266.2 ms | 72/72 — 1,732.6 ms |
| `dimacs-bf` (4) | 4/4 — 217.3 ms | 4/4 — 80.5 ms | 4/4 — 23.8 ms | **4/4 — 18.8 ms** | 4/4 — 182.8 ms |
| `dimacs-dubois` (13) | 13/13 — 17.9 ms | **13/13 — 12.9 ms** | 13/13 — 19.2 ms | 13/13 — 26.9 ms | 13/13 — 219.7 ms |
| `dimacs-gcp-large` (4) | 1/4 — 30,681.3 ms | 0/4 — 40,000.0 ms | 0/4 — 40,000.0 ms | **2/4 — 22,679.2 ms** | 1/4 — 31,350.3 ms |
| `dimacs-hanoi` (2) | 2/2 — 771.4 ms | 2/2 — 195.1 ms | 2/2 — 513.1 ms | **2/2 — 169.5 ms** | 2/2 — 675.0 ms |
| `dimacs-ii` (41) | 41/41 — 5,252.5 ms | 41/41 — 544.0 ms | 41/41 — 537.2 ms | **41/41 — 250.6 ms** | 41/41 — 11,340.7 ms |
| `dimacs-jnh` (50) | 50/50 — 267.2 ms | **50/50 — 83.4 ms** | 50/50 — 271.5 ms | 50/50 — 135.8 ms | 50/50 — 1,093.0 ms |
| `dimacs-lran` (3) | **3/3 — 677.2 ms** | 0/3 — 30,000.0 ms | 0/3 — 30,000.0 ms | 2/3 — 13,354.1 ms | 0/3 — 30,000.0 ms |
| `dimacs-parity` (30) | 20/30 — 100,096.2 ms | 20/30 — 100,310.5 ms | 20/30 — 100,368.3 ms | 20/30 — 100,505.7 ms | **30/30 — 11,016.0 ms** |
| `dimacs-phole` (5) | 5/5 — 6.9 ms | **5/5 — 3.9 ms** | 5/5 — 1,471.3 ms | 4/5 — 13,510.0 ms | 4/5 — 15,254.6 ms |
| `dimacs-ssa` (8) | 8/8 — 224.7 ms | 8/8 — 90.8 ms | **8/8 — 37.6 ms** | 8/8 — 38.1 ms | 8/8 — 272.8 ms |
| `flat-gcp` (8) | 8/8 — 240.0 ms | **8/8 — 18.0 ms** | 8/8 — 51.1 ms | 8/8 — 30.8 ms | 8/8 — 242.1 ms |
| `planning-blocksworld` (7) | 7/7 — 1,301.5 ms | **7/7 — 218.5 ms** | 7/7 — 357.0 ms | 7/7 — 403.4 ms | 7/7 — 1,934.1 ms |
| `planning-logistics` (4) | 4/4 — 558.7 ms | 4/4 — 80.1 ms | 4/4 — 136.7 ms | **4/4 — 34.1 ms** | 4/4 — 1,018.0 ms |
| `qg` (22) | 22/22 — 7,910.1 ms | 22/22 — 7,336.5 ms | 22/22 — 6,595.7 ms | **22/22 — 3,938.2 ms** | 22/22 — 14,660.5 ms |
| `rnd3sat` (10) | **10/10 — 2,386.4 ms** | 10/10 — 3,264.0 ms | 10/10 — 2,481.1 ms | 10/10 — 3,536.1 ms | 10/10 — 4,166.5 ms |
| `sw-gcp` (5) | 5/5 — 245.0 ms | 5/5 — 15.0 ms | 5/5 — 46.2 ms | **5/5 — 14.5 ms** | 5/5 — 277.5 ms |
| **TOTAL (331 instances, PAR-2)** | 318/331 — 163,243 ms *(1.01x)* | 313/331 — 207,236 ms *(1.29x)* | 314/331 — 189,824 ms *(1.18x)* | 316/331 — 174,263 ms *(1.08x)* | **323/331 — 161,168 ms** *(fastest)* |

<!-- BEGIN_STRUCTURAL_ANALYSIS -->
## Phase-Transition & Structural Analysis

*Auto-generated by [`../src/analyze_benchmarks.py`](../src/analyze_benchmarks.py). Position relative to the critical phase transition is measured by $\rho_{\mathrm{crit}} = \frac{1}{n}\sum_k m_k / \alpha_c(k)$ (exact $\alpha/\alpha_c(k)$ for pure $k$-SAT; effective critical threshold $\alpha_c^{\mathrm{eff}} = \alpha/\rho_{\mathrm{crit}}$; `Under` $<0.90\times$, `Near-crit` $0.90\text{--}1.10\times$, `Over` $>1.10\times$), alongside Gent–Walsh annealed constrainedness $\kappa = -\frac{1}{n}\sum_i \log_2(1-2^{-k_i})$ (AAAI 1996), clause-length profile ($\bar{k}$, `%Bin`, `%Horn`), variable-degree CV ($\sigma_d/\bar{d}$, uniformity vs. hub skew), and extracted native XOR parity clauses.*

| Group / Family | Files | Med $n$ | Med $m$ | $\alpha=m/n$ (Med) | $\alpha_c^{\mathrm{eff}}$ (Med) | $\rho_{\mathrm{crit}}$ Med [Min–Max] (Regime) | Med $\kappa$ | Med $\bar{k}$ | Bin% | Horn% | Deg CV | Total XORs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `ais` | 4 | 147 | 2,335 | 15.43 | 1.26 | **12.3x** [7.47x–17.1x] (Over) | 5.47 | 2.31 | 73% | 99% | 0.16 | 0 |
| `beijing` | 16 | 2,549 | 31,813 | 5.98 | 2.37 | **3.49x** [2.50x–24.8x] (Over) | 1.48 | 2.76 | 24% | 100% | 1.16 | 0 |
| `bmc` | 13 | 28,161 | 139,716 | 4.96 | 1.20 | **3.94x** [3.47x–6.33x] (Over) | 1.74 | 2.63 | 81% | 82% | 1.64 | 17,125 |
| `bms-rti` | 4 | 100 | 357 | 3.60 | 4.27 | **0.84x** [0.64x–1.01x] (Under) | 0.69 | 3.00 | 0% | 48% | 0.33 | 0 |
| `cbs` | 6 | 100 | 429 | 4.29 | 4.27 | **1.01x** [0.94x–1.05x] (Near-crit) | 0.83 | 3.00 | 0% | 49% | 0.28 | 0 |
| `dimacs-aim` | 72 | 100 | 250 | 2.00 | 4.22 | **0.47x** [0.37x–1.45x] (Under) | 0.39 | 3.00 | 0% | 50% | 0.04 | 0 |
| `dimacs-bf` | 4 | 1,785 | 5,218 | 3.11 | 1.54 | **2.01x** [1.94x–2.11x] (Over) | 0.96 | 2.52 | 55% | 72% | 0.50 | 28 |
| `dimacs-dubois` | 13 | 78 | 208 | 2.67 | 4.27 | **0.62x** [0.32x–0.62x] (Under) | 0.51 | 3.00 | 0% | 74% | 0.00 | 749 |
| `dimacs-gcp-large` | 4 | 3,000 | 152,064 | 46.79 | 1.00 | **46.7x** [31.1x–62.7x] (Over) | 19.39 | 2.02 | 100% | 100% | 0.07 | 0 |
| `dimacs-hanoi` | 2 | 1,324 | 9,701 | 7.18 | 1.57 | **4.56x** [4.38x–4.74x] (Over) | 2.32 | 2.48 | 50% | 75% | 0.57 | 0 |
| `dimacs-ii` | 41 | 520 | 6,108 | 10.28 | 1.08 | **9.37x** [2.57x–24.1x] (Over) | 3.90 | 3.01 | 93% | 97% | 0.64 | 0 |
| `dimacs-jnh` | 50 | 100 | 850 | 8.50 | 6.05 | **1.37x** [1.10x–1.59x] (Over) | 0.87 | 4.89 | 9% | 26% | 0.14 | 0 |
| `dimacs-lran` | 3 | 1,000 | 4,250 | 4.25 | 4.27 | **1.00x** [1.00x–1.00x] (Near-crit) | 0.82 | 3.00 | 0% | 51% | 0.28 | 0 |
| `dimacs-parity` | 30 | 682 | 2,351 | 3.66 | 2.62 | **1.40x** [1.15x–1.59x] (Over) | 0.87 | 2.78 | 19% | 47% | 0.95 | 18,548 |
| `dimacs-phole` | 5 | 72 | 297 | 4.12 | 1.03 | **4.00x** [3.00x–5.00x] (Over) | 1.66 | 2.18 | 97% | 97% | 0.00 | 0 |
| `dimacs-ssa` | 8 | 1,363 | 3,080 | 2.35 | 1.22 | **1.90x** [1.84x–2.04x] (Over) | 0.84 | 2.28 | 77% | 78% | 1.30 | 92 |
| `flat-gcp` | 8 | 337 | 1,260 | 3.73 | 1.07 | **3.47x** [3.08x–3.49x] (Over) | 1.47 | 2.09 | 91% | 91% | 0.22 | 0 |
| `planning-blocksworld` | 7 | 459 | 7,054 | 12.67 | 1.21 | **9.82x** [4.50x–17.3x] (Over) | 4.43 | 2.24 | 78% | 87% | 0.36 | 0 |
| `planning-logistics` | 4 | 992 | 9,010 | 8.39 | 1.56 | **5.21x** [4.21x–6.02x] (Over) | 2.51 | 2.61 | 55% | 90% | 0.33 | 0 |
| `qg` | 22 | 864 | 49,369 | 39.81 | 1.84 | **20.4x** [12.5x–40.6x] (Over) | 10.96 | 2.66 | 40% | 99% | 0.02 | 0 |
| `rnd3sat` | 10 | 150 | 645 | 4.30 | 4.27 | **1.01x** [1.00x–1.02x] (Near-crit) | 0.83 | 3.00 | 0% | 50% | 0.27 | 0 |
| `sw-gcp` | 5 | 500 | 3,100 | 6.20 | 1.03 | **6.01x** [6.01x–6.01x] (Over) | 2.50 | 2.10 | 97% | 97% | 0.07 | 0 |

**Suite Phase-Transition Summary (331 instances):** median $\rho_{\mathrm{crit}} = 1.48\times$ (range `0.32x–62.7x`), median $\kappa = 0.91$, regime split **75 Under / 22 Near-critical / 234 Over**, total extracted native XOR parity clauses = **36,542**.
<!-- END_STRUCTURAL_ANALYSIS -->

## References

- H. H. Hoos and T. Stützle, *"SATLIB: An Online Resource for Research on SAT"*, SAT 2000, IOS Press, pp. 283–292 ([`cs.ubc.ca/~hoos/SATLIB/`](https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html)).
- D. S. Johnson and M. A. Trick (eds.), *Cliques, Coloring, and Satisfiability: Second DIMACS Implementation Challenge*, DIMACS Series vol. 26, AMS, 1996.
- J. M. Crawford, M. Kearns, and R. Schapire, *The Minimal Disagreement Parity Problem as a Hard Satisfiability Problem*, CIRL Technical Report, 1994.
- H. Kautz and B. Selman, *"Pushing the Envelope: Planning, Propositional Logic, and Stochastic Search"*, AAAI 1996.
- O. Shtrichman, *"Tuning SAT Checkers for Bounded Model Checking"*, CAV 2000, LNCS 1855, pp. 480–494.
