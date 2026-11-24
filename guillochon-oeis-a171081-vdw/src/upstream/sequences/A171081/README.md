# Van der Waerden numbers w(2;3,t) as SAT: OEIS A171081 (and A007783)

**Open question:** is w(2;3,20) = 389?

w(2;3,t) is the least N such that every red/blue coloring of {1,…,N} has a red 3-term arithmetic progression
or a blue t-term one. [A171081](https://oeis.org/A171081) (= [A007783](https://oeis.org/A007783) for t ≥ 3) is
known up to t = 19, where w(2;3,19) = 349 (Ahmed, Kullmann, Snevily 2014). They exhibit a coloring showing
w(2;3,20) ≥ 389, conjecture equality, and remark that a proof "should be in reach" of a dedicated solver. It is
still not in the OEIS.

`cnf/vdw_3_20_N389.cnf.xz` decides it:

* **UNSAT** means w(2;3,20) = 389. That is a new OEIS term, and it needs a DRAT/LRAT proof.
* **SAT** means w(2;3,20) ≥ 390, which refutes the conjecture. `verify.py` checks the coloring in about a second.

## Encoding

Variable i is true when i is red. Every 3-term AP in [1..N] gets the clause "not all red", and every t-term AP gets
"not all blue". That's all: there are no auxiliary variables and no symmetry breaking (the reflection i ↦ N+1−i
is left in). The instances are small (N = 389: 389 variables and 41,426 clauses) but very hard.

## Instances

| instance | expected | notes |
|---|---|---|
| `vdw_3_t_N{w−1}` for t = 10…19 | SAT | a coloring exists; `verify.py` checks it |
| `vdw_3_t_N{w}` for t = 10…19 | UNSAT | w(2;3,t) from A171081; t = 19 took Ahmed et al. substantial CPU time |
| `vdw_3_20_N388` | SAT | a coloring is published by Ahmed–Kullmann–Snevily |
| **`vdw_3_20_N389`** | **open** | |

## Why it's a good test

A SAT answer is a coloring, and `verify.py` checks every progression directly without looking at the CNF. The
UNSAT rungs climb steeply in difficulty, so the run times on t = 15…19 show how a solver scales. The known-UNSAT
instances catch a solver that claims SAT wrongly.

## Files

`gen_vdw.py T N`: generator. `verify.py map.json model`: checks a coloring. `validate.py`: t = 3…9, SAT at
w−1 and UNSAT at w (all pass; needs `pip install python-sat`). `make_set.sh`: rebuilds `cnf/`.
