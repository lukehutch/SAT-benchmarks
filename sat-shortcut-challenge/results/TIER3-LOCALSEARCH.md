# Tier 3, satisfiable instances: a textbook local search

Satisfiable uniform random 3-SAT is a known exception to "no shortcut": stochastic local search has beaten clause-learning solvers on it by large factors for decades. So a fast answer on the satisfiable Tier 3 instances does not, by itself, show a new method. This file records how fast a minimal, published method is on them.

`shortcuts/probsat.c` is a 60-line version of probSAT (Balint and Schöning, 2012), break-only polynomial variant with the paper's 3-SAT constants (`cb = 2.06`, `eps = 0.9`). No restarts, no tuning. Every answer is checked against the formula before it is printed.

Run on 22 November 2026 on an 8-core Apple laptop, one core, seeds 1 to 5. Times are wall-clock milliseconds for the search only (not reading the file). The Kissat column is CPU seconds from [TIER3-BASELINE.md](TIER3-BASELINE.md), same machine.

| instance | probSAT median (ms) | probSAT slowest of 5 (ms) | Kissat 4.0.4 (s) |
|---|---:|---:|---:|
| random3sat_n300_s2.cnf | 0.7 | 0.9 | 0.07 |
| random3sat_n300_s3.cnf | 12.0 | 22.2 | 1.76 |
| random3sat_n300_s4.cnf | 56.0 | 299.1 | 3.49 |
| random3sat_n350_s3.cnf | 22.1 | 32.7 | 0.57 |
| random3sat_n400_s1.cnf | 24.2 | 42.7 | 8.71 |
| random3sat_n400_s2.cnf | 2.1 | 4.6 | 1.36 |
| random3sat_n400_s3.cnf | 4.7 | 10.4 | 1.78 |
| random3sat_n400_s5.cnf | 11.4 | 54.0 | 3.68 |
| random3sat_n450_s1.cnf | 18.2 | 32.6 | 49.37 |
| random3sat_n450_s2.cnf | 65.5 | 130.0 | 1.87 |
| random3sat_n450_s4.cnf | 10.7 | 38.9 | 3.13 |
| random3sat_n500_s1.cnf | 17.7 | 28.7 | 24.05 |
| random3sat_n500_s2.cnf | 6.7 | 9.8 | 4.85 |
| random3sat_n500_s4.cnf | 23.6 | 66.3 | 23.53 |
| random3sat_n500_s5.cnf | 14.2 | 19.0 | 2.09 |

All 15 satisfiable instances were solved on all 5 seeds, the slowest run taking 0.3 seconds.

## What this means for Tier 3

- **The satisfiable instances are not the test.** A known 60-line method solves them in milliseconds.
- **The unsatisfiable instances are.** Local search cannot prove unsatisfiability. Kissat needs 43 and 56 seconds for the two at 300 variables and did not finish the other 8 in 300 seconds. A checked proof for any of those, in a small fraction of that time, is what would be new.

Reproduce:

```bash
cc -O2 -o probsat shortcuts/probsat.c -lm
```

```bash
./probsat instances/tier3/random3sat_n300_s3.cnf 1
```

The second argument is the seed.
