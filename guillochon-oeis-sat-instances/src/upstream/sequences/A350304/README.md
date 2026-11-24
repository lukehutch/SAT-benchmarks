# Zarankiewicz numbers z(n;3) as SAT: OEIS A350304 (and A001198, A347473, A350237)

**Open question:** what is z(17;3), the maximum number of ones in a 17 × 17 0/1 matrix with no all-ones 3 × 3
submatrix?

[A350304](https://oeis.org/A350304) is known for n ≤ 16 (z(16;3) = 128, Tan 2022, by SAT). The same number gives
three related sequences: [A001198](https://oeis.org/A001198)(n) = z + 1, [A347473](https://oeis.org/A347473)(n)
= n² − z − 1, and [A350237](https://oeis.org/A350237)(n) = n² − z. Settling n = 17 adds a term to all four.

**Bounds for n = 17:**

* **Lower: 135.** This repo includes a verified matrix, `certificates/zaran3_n17_135.*`, found by simulated
  annealing. It is probably not optimal.
* **Upper: 150.** Tan's table gives z(16,17;3) ≤ 142. Deleting any one row of a 17 × 17 matrix leaves a
  16 × 17 matrix, so averaging over the rows gives z(17;3) ≤ ⌊17·142/16⌋ = 150.

The instances `zaran3_n17_m{136,140,144,148,151}` bracket the answer. Each SAT result is a verified matrix that
raises the lower bound. Each UNSAT result, backed by a DRAT/LRAT proof, lowers the upper bound. The exact value
comes from a SAT/UNSAT pair at m and m+1.

## Encoding

One variable per entry. Each choice of 3 rows and 3 columns gets the clause "not all nine are ones"
(C(17,3)² = 462,400 clauses). At least m ones, enforced with a Sinz sequential counter.

**Symmetry breaking (on by default):** rows and columns are each lexicographically non-increasing. Every matrix
can be permuted into this form (Flener et al. 2002), so this is sound. It matters a lot. Without it, CaDiCaL
needed 477 s for the n = 7 UNSAT case; with it, n = 8 is instant and n = 9 takes 27 s. Pass `--no-symbreak` for
the bare encoding.

## Instances

| instance | expected | notes |
|---|---|---|
| `zaran3_n{n}_m{z}` for n = 10…16 | SAT | the matrix is checkable |
| `zaran3_n{n}_m{z+1}` for n = 10…16 | UNSAT | known values (Tan 2022 for the largest) |
| `zaran3_n17_m135` | SAT | certificate included |
| **`zaran3_n17_m136/140/144/148`** | **open** | bracket |
| `zaran3_n17_m151` | UNSAT if the upper bound above is right | |

## Files

`gen_zaran.py N M [--no-symbreak]`: generator. `verify.py map.json model`: counts the ones, and checks every
triple of rows for 3 common columns with bitwise ANDs. `validate.py tmpdir [NMAX]`: n = 3…9 by default (all pass).
`make_set.sh`: rebuilds `cnf/`.
