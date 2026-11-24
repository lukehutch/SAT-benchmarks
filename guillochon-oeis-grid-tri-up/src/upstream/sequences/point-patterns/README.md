# Pattern-free point sets on grids as SAT

These are five problems with the same form: paint as many grid points as possible so that no forbidden shape has
all its corners painted. One generator (`gen_points.py PATTERN N M`) and one verifier cover all of them.

| pattern | grid | forbidden shape | sequences (max / complementary min) | known to | open instance |
|---|---|---|---|---|---|
| `sq-axis` | N × N | square, sides parallel to the grid | [A227133](https://oeis.org/A227133) / [A152125](https://oeis.org/A152125) | N = 13 | N = 14, m = 113 (112 known: Karpov 2016) |
| `sq-any` | N × N | square, any orientation | [A240443](https://oeis.org/A240443) | N = 10 | N = 11, m = 59 (58 known: Israel 2016) |
| `tri-up` | triangular, side N | upward triangle, sides along the grid | [A157795](https://oeis.org/A157795)(N−1) / [A319158](https://oeis.org/A319158)(N) | side 13 | side 14, m = 47 (46 found here) |
| `tri-axis` | triangular, side N | triangle with sides along the grid, either orientation | [A227308](https://oeis.org/A227308) / [A227116](https://oeis.org/A227116) | side 15 | side 16, m = 55 (54 found here) |
| `tri-any` | triangular, side N | equilateral triangle, any orientation | [A240114](https://oeis.org/A240114)(N) / [A319159](https://oeis.org/A319159)(N−1) | side 15 | side 16, m = 37 (36 found here) |

For each open instance, SAT gives a configuration that beats the best known one, and the verifier checks it in
milliseconds. UNSAT, backed by a DRAT/LRAT proof, settles the term, given that the configuration one below
exists. The min sequences follow as (number of points) − max.

The three triangular lower bounds come from our own simulated annealing (`../../common/anneal.py`) and are saved in
`certificates/`. As far as we know none of them was published before. **tri-up side 14 ≥ 46** is a jump of 6 over
side 13 (40). We checked it independently: the same search reproduces A157795 exactly for sides 8–13, and a
brute-force test of every triple of points finds no upward triangle.

## Encoding

One variable per point. Each forbidden shape gets the clause "not all corners painted". At least m points are
painted, enforced with a Sinz sequential counter. There is no symmetry breaking (the grid's 8 or 6 symmetries are
left in). The instances are small: a few thousand variables and up to about 30,000 clauses.

## Instances (`cnf/`)

Each pattern has a pair at each of its three largest known sizes: SAT at the max and UNSAT at max+1. It also has
a SAT rung at the open size (the best known configuration) and the open instance one above that.

## Files

`gen_points.py PATTERN N M`: generator. `verify.py map.json model`: an independent check that treats every pair
of painted points as a side of a square or triangle and tests the remaining corners. `validate.py tmpdir [NMAX]`:
checks every pattern against the OEIS for N = 2…6 by default; all 50 cases pass, and an extra run of tri-up
reproduces sides 8–13. `certificates/`: the configurations found here. `make_set.sh`: rebuilds `cnf/`.
