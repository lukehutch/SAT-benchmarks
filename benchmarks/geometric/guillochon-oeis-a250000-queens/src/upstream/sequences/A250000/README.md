# Peaceable queens as SAT: OEIS A250000

**Open question:** can 65 white and 65 black queens coexist on a 21 × 21 board?

[A250000](https://oeis.org/A250000)(n) is the largest m such that m white and m black queens fit on an n × n
board with no queen attacking one of the other color. Ainley (1977) gave constructions achieving
floor(7n²/48) for most n ≤ 30. Exhaustive search confirmed them optimal for n ≤ 20; n = 16–20 were done by
Jason Davies, Nov 2026. The first open case is n = 21, where Ainley's construction gives 64.

`cnf/queens_n21_m65.cnf.xz` decides it:

* **UNSAT** means a(21) = 64, a new OEIS term. It needs a DRAT/LRAT proof.
* **SAT** means a(21) ≥ 65, which beats a construction that has stood since 1977. `verify.py` draws the board and
  checks it.

## Encoding

Variables W(r,c) and B(r,c) say whether there is a white or black queen on each square. Each square holds at most
one queen, and a white queen and a black queen never share a row, column or diagonal. There are at least m queens
of each color, enforced with Sinz sequential counters. No symmetry breaking: the 8 board symmetries and the color
swap are left in.

## Instances

| instance | expected | notes |
|---|---|---|
| `queens_n{n}_m{a(n)}` for n = 12…20 | SAT | the board is checkable |
| `queens_n{n}_m{a(n)+1}` for n = 12…20 | UNSAT | known optimal (n ≤ 15 classically; 16–20 by exhaustive search, 2026) |
| `queens_n21_m64` | SAT | Ainley's construction |
| **`queens_n21_m65`** | **open** | |

## Files

`gen_queens.py N M`: generator. `verify.py map.json model`: walks every queen's attack rays. `validate.py`:
n = 3…8, SAT at a(n) and UNSAT at a(n)+1 (all pass). `make_set.sh`: rebuilds `cnf/`.
