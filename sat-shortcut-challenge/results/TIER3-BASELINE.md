# Tier 3 baseline: Kissat 4.0.4, default options

Run on 22 November 2026 with `shortcuts/tier3_baseline.py 300 4`: a 300-second wall-clock limit per instance, four at a time, on an 8-core Apple laptop under heavy load from other work. Times are CPU seconds; under that load a run that hit the 300-second wall limit had used about 200 CPU seconds.

Solved: 17 of 25 (15 satisfiable, 2 unsatisfiable). Not solved within the limit: 8. Their status is unknown to us; they are probably unsatisfiable.

| instance | Kissat answer | CPU seconds |
|---|---|---:|
| random3sat_n300_s1.cnf | UNSAT | 43.15 |
| random3sat_n300_s2.cnf | SAT | 0.07 |
| random3sat_n300_s3.cnf | SAT | 1.76 |
| random3sat_n300_s4.cnf | SAT | 3.49 |
| random3sat_n300_s5.cnf | UNSAT | 56.21 |
| random3sat_n350_s1.cnf | not solved in 300 s | 195.06 |
| random3sat_n350_s2.cnf | not solved in 300 s | 195.29 |
| random3sat_n350_s3.cnf | SAT | 0.57 |
| random3sat_n350_s4.cnf | not solved in 300 s | 198.37 |
| random3sat_n350_s5.cnf | not solved in 300 s | 199.38 |
| random3sat_n400_s1.cnf | SAT | 8.71 |
| random3sat_n400_s2.cnf | SAT | 1.36 |
| random3sat_n400_s3.cnf | SAT | 1.78 |
| random3sat_n400_s4.cnf | not solved in 300 s | 197.81 |
| random3sat_n400_s5.cnf | SAT | 3.68 |
| random3sat_n450_s1.cnf | SAT | 49.37 |
| random3sat_n450_s2.cnf | SAT | 1.87 |
| random3sat_n450_s3.cnf | not solved in 300 s | 200.83 |
| random3sat_n450_s4.cnf | SAT | 3.13 |
| random3sat_n450_s5.cnf | not solved in 300 s | 206.07 |
| random3sat_n500_s1.cnf | SAT | 24.05 |
| random3sat_n500_s2.cnf | SAT | 4.85 |
| random3sat_n500_s3.cnf | not solved in 300 s | 218.38 |
| random3sat_n500_s4.cnf | SAT | 23.53 |
| random3sat_n500_s5.cnf | SAT | 2.09 |
