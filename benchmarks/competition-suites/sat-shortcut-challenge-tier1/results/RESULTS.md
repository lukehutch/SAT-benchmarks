# Results

CPU time. "specialised" is the known shortcut; CaDiCaL is 1.5.3 through `python-sat` 1.9.dev24; Kissat is 4.0.4 (Homebrew) with default options. Taken on 22 November 2026 on an 8-core Apple laptop that was under heavy load from other work, so absolute times are rough. All answers agree wherever a solver finished.

## First run (`bench.py 20`, limit 20 s)

The specialised method here reads only the CNF.

| instance | vars | clauses | specialised | CaDiCaL | Kissat | method |
|---|---:|---:|---:|---:|---:|---|
| tseitin_n20_unsat | 30 | 80 | 0.30 ms | 0.8 ms | 2.4 ms | XOR + Gauss |
| tseitin_n30_unsat | 45 | 120 | 0.40 ms | 6.8 ms | 6.5 ms | XOR + Gauss |
| tseitin_n40_unsat | 60 | 160 | 0.50 ms | 44.3 ms | 36.8 ms | XOR + Gauss |
| tseitin_n60_unsat | 90 | 240 | 0.70 ms | 205.4 ms | 287.4 ms | XOR + Gauss |
| tseitin_n100_unsat | 150 | 400 | 1.10 ms | > 20 s | > 20 s | XOR + Gauss |
| tseitin_n200_unsat | 300 | 800 | 2.10 ms | > 20 s | > 20 s | XOR + Gauss |
| tseitin_n40_sat | 60 | 160 | 0.60 ms | 0.4 ms | 2.0 ms | XOR + Gauss |
| tseitin_n100_sat | 150 | 400 | 1.90 ms | 0.5 ms | 2.2 ms | XOR + Gauss |
| tseitin_n200_sat | 300 | 800 | 5.60 ms | 0.8 ms | 2.2 ms | XOR + Gauss |
| php_8_7 | 56 | 204 | 0.70 ms | 41.2 ms | 24.0 ms | matching bound |
| php_9_8 | 72 | 297 | 0.90 ms | 319.6 ms | 107.9 ms | matching bound |
| php_10_9 | 90 | 415 | 1.50 ms | 4991.0 ms | 389.6 ms | matching bound |
| php_11_10 | 110 | 561 | 1.80 ms | > 20 s | 2652.0 ms | matching bound |
| php_13_12 | 156 | 949 | 3.10 ms | > 20 s | > 20 s | matching bound |
| random3sat_n150_s1 | 150 | 639 | 4.50 ms | 2.3 ms | 29.1 ms | none (fallback) |
| random3sat_n200_s1 | 200 | 852 | 655.80 ms | 646.2 ms | 607.2 ms | none (fallback) |
| random3sat_n200_s2 | 200 | 852 | 149.80 ms | 152.3 ms | 167.4 ms | none (fallback) |
| random3sat_n250_s1 | 250 | 1065 | 3854.50 ms | 3852.5 ms | 1455.7 ms | none (fallback) |

## Second run (`more.py 10`, limit 10 s)

"(circuit)" and "(graph)" mean the specialised method was given the original object, not only the CNF.

| instance | vars | clauses | specialised | CaDiCaL | Kissat | method |
|---|---:|---:|---:|---:|---:|---|
| cec_adder_8b_rc_vs_ks | 144 | 424 | 1.65 ms | 1.7 ms | 5.9 ms | sweeping (circuit) |
| cec_adder_16b_rc_vs_ks | 336 | 992 | 4.57 ms | 5.2 ms | 11.1 ms | sweeping (circuit) |
| cec_adder_32b_rc_vs_ks | 768 | 2272 | 14.47 ms | 28.9 ms | 30.1 ms | sweeping (circuit) |
| cec_adder_64b_rc_vs_ks | 1728 | 5120 | 61.70 ms | 156.7 ms | 159.2 ms | sweeping (circuit) |
| cec_mult_5x5_arr_vs_wal | 373 | 1214 | 0.24 ms | 32.7 ms | 27.4 ms | simulate all inputs (circuit) |
| cec_mult_6x6_arr_vs_wal | 545 | 1784 | 0.54 ms | 222.4 ms | 229.8 ms | simulate all inputs (circuit) |
| cec_mult_8x8_arr_vs_wal | 1018 | 3358 | 14.09 ms | 7426.4 ms | 6007.1 ms | simulate all inputs (circuit) |
| cec_mult_10x10_arr_vs_wal | 1615 | 5347 | 184.38 ms | > 10 s | > 10 s | simulate all inputs (circuit) |
| mult_target_28b_sat | 2006 | 6677 | not tried | 8.9 ms | 36.0 ms | |
| mult_target_28b_unsat | 2006 | 6677 | not tried | 3.2 ms | 3.2 ms | |
| mult_target_32b_sat | 2644 | 8813 | not tried | 6.4 ms | 24.3 ms | |
| mult_target_36b_sat | 3370 | 11245 | not tried | 5.4 ms | 20.7 ms | |
| chessboard_6x6_unsat | 56 | 172 | 0.41 ms | 0.5 ms | 2.9 ms | perfect matching (CNF) |
| chessboard_8x8_unsat | 108 | 344 | 1.16 ms | 3.1 ms | 6.4 ms | perfect matching (CNF) |
| chessboard_10x10_unsat | 176 | 572 | 0.71 ms | 51.4 ms | 53.9 ms | perfect matching (CNF) |
| chessboard_14x14_unsat | 360 | 1196 | 2.69 ms | > 10 s | > 10 s | perfect matching (CNF) |
| chessboard_14x14_sat | 360 | 1196 | 3.62 ms | 0.9 ms | 2.2 ms | perfect matching (CNF) |
| ham_planted_n20 | 400 | 13641 | 0.35 ms | 17.4 ms | 49.7 ms | graph search (graph) |
| ham_planted_n30 | 900 | 47761 | 0.90 ms | 84.2 ms | 619.2 ms | graph search (graph) |
| ham_planted_n40 | 1600 | 115281 | 332.51 ms | 88.3 ms | 1280.4 ms | graph search (graph) |
| ham_bipartite_7_8 | 225 | 4651 | 0.19 ms | 41.3 ms | 100.0 ms | graph tests (graph) |
| ham_bipartite_10_11 | 441 | 13063 | 0.33 ms | 59.9 ms | 183.5 ms | graph tests (graph) |
| ham_bipartite_14_15 | 841 | 34975 | 0.82 ms | 97.8 ms | 351.0 ms | graph tests (graph) |
| ham_cutvertex_15 | 225 | 4651 | 0.13 ms | 89.1 ms | 47.4 ms | graph tests (graph) |
| ham_cutvertex_23 | 529 | 17251 | 0.26 ms | > 10 s | 84.6 ms | graph tests (graph) |
| xor_plus_clauses_n100_free14_s1 | 100 | 404 | 2.73 ms | 1.3 ms | 3.5 ms | Gauss + enumerate (CNF) |
| xor_plus_clauses_n160_free16_s2 | 160 | 666 | 9.48 ms | 3.1 ms | 8.4 ms | Gauss + enumerate (CNF) |
| xor_plus_clauses_n240_free18_s3 | 240 | 1008 | 136.07 ms | 20.9 ms | 26.9 ms | Gauss + enumerate (CNF) |
| xor_plus_clauses_n240_free18_s4 | 240 | 1048 | 3.21 ms | 35.5 ms | 65.5 ms | Gauss + enumerate (CNF) |

Tier 3 has not been run by us.
