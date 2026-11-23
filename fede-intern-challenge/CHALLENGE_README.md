# Frobenius challenge pack (12 CNF instances)

A small set of pure DIMACS CNF instances (no AIG / circuit files, no extra hints), offered in response to the public
invitation to send hard instances. All files are `xz`-compressed DIMACS (`p cnf V C`). Checksums of the
*uncompressed* `.cnf` files and of the `.cnf.xz` files are in `SHA256SUMS`.

We have the ground truth (or a way to check it) for every instance; answers and generator seeds are withheld and
will be published after results come back. Generated instances had their variables randomly renamed, literal
polarities randomly flipped, and literal/clause order shuffled.

| file | vars | clauses | description (neutral) |
|---|---:|---:|---|
| c01.cnf | 300 | 1278 | uniform random 3-CNF, clause/var ratio 4.26 |
| c02.cnf | 350 | 1491 | uniform random 3-CNF, ratio 4.26 |
| c03.cnf | 400 | 1704 | uniform random 3-CNF, ratio 4.26 |
| c04.cnf | 450 | 1917 | uniform random 3-CNF, ratio 4.26 |
| c05.cnf | 500 | 2130 | uniform random 3-CNF, ratio 4.26 |
| c06.cnf | 20000 | 85000 | random 3-CNF, ratio 4.25 (generator disclosed afterwards) |
| c07.cnf | 50000 | 212500 | random 3-CNF, ratio 4.25 (generator disclosed afterwards) |
| c08.cnf | 6627 | 36662 | integer factoring: N = A·B with A,B ≥ 2, plain multiplier circuit, Tseitin-encoded, renamed/shuffled (48-bit N) |
| c09.cnf | 11907 | 66278 | same encoding, 64-bit N |
| c10.cnf | 4563 | 25118 | same encoding, 40-bit N |
| c11.cnf | 153 | 6120 | SAT Competition 2025 main track, unmodified (GBD hash `1b84df53843ecd90ec8c3c7a01cada6c`) |
| c12.cnf | 300 | 6337 | SAT Competition 2025 main track, unmodified (GBD hash `b1c8eaa002ac2fa1c8bfd1002738e78e`) |

c11 and c12 are the files served by `https://benchmark-database.de/file/<hash>`, decompressed and otherwise unmodified.

## What we ask for

For each instance you attempt:

1. **SAT**: a full satisfying assignment in standard `v ... 0` format (we check it against the CNF).
2. **UNSAT**: a DRAT or LRAT proof against *this exact CNF file* (we check with `drat-trim` / `lrat-check` / `cake_lpr`).
3. **Wall-clock time** for the whole run (process start to answer, including parsing), plus CPU model, core count and
   number of threads used. Ideally a single-threaded run.
4. If no answer within your time budget, just say "timeout after X s" — that's useful too.

Please solve the CNF as given (no external hints about how it was generated).
