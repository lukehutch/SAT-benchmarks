# Optimal-depth sorting networks as SAT: OEIS A067782

**Open question:** does an 18-input sorting network of depth 10 exist?

[A067782](https://oeis.org/A067782) gives the least depth of an n-input sorting network. It is known for n ≤ 17
(a(17) = 10). For n = 18 the answer is 10 or 11: depth 11 is achievable, and a(18) ≥ a(17) = 10.

`cnf/sortnet_n18_d10.cnf.xz` decides it (`xz -dk` it to get the DIMACS file):

* **SAT** means a(18) = 10, a new result: the model *is* a sorting network, and `decode_verify.py` extracts it and
  checks it on all 2^18 inputs.
* **UNSAT** means a(18) = 11, also new, and it settles the OEIS term. To be accepted it needs a checkable
  proof (DRAT/LRAT, verifiable with `drat-trim` or `cake_lpr`), since an UNSAT answer alone cannot be checked.

## Why this is a good test of a new solver

On the SAT side the answer is quick to check, and it does not depend on trusting the solver or the encoding.

* **A SAT answer checks itself.** The model *is* the network. `decode_verify.py` reads off the comparators and
  runs them on all 2^n zero-one inputs, a bit-parallel check that takes milliseconds for n = 18. It never
  looks at the CNF, so a wrong model, or a bug in the encoding, cannot get through.
* **There are known-SAT instances at the frontier.** `n17_d10`, `n18_d11` and `n16_d9` are satisfiable, and each
  model is a sorting network that can be checked in seconds. The 17-input depth-10 network (Ehlers & Müller,
  2014) was a research result in its own right. A solver that returns a verified model for these quickly is
  showing real speed on exactly this encoding.
* **The known-UNSAT instances are a trap for a broken solver.** `n11_d7`, `n12_d7`, `n14_d8`, `n16_d8` and `n17_d9`
  are proven unsatisfiable. If a solver claims SAT on one of them, the verifier will reject the model at once.
  If it says UNSAT quickly, the answer is plausible, but it is only *checkable* with a DRAT/LRAT proof.
* **The open instance is new either way.** SAT gives a verified 18-input depth-10 network, so a(18) = 10, checked
  in milliseconds. UNSAT gives a(18) = 11, but only with a proof that an independent checker accepts. Checking that
  proof can take time comparable to the solve itself.

Suggested protocol: run the whole ladder with the same solver and settings. Report wall-clock time and hardware
for each instance. Send the models for every SAT answer and proofs, or at least proof sizes and checksums, for
every UNSAT answer.

## Files

| file | what |
|---|---|
| `cnf/sortnet_n18_d10.cnf.xz` | **the open instance** (76 MB xz; 1.6 GB, 2,598,203 vars, 63,274,184 clauses unpacked) |
| `cnf/sortnet_n{11,12,14,16,17}_d*.cnf.xz`, `cnf/sortnet_n18_d11.cnf.xz` | calibration instances with known answers (table below) |
| `cnf/SHA256SUMS` | checksums of the uncompressed `.cnf` files |
| `*.cnf.map.json` | which variables are which comparators (for decoding) |
| `gen_depth_cnf.py` | generator: `python gen_depth_cnf.py N D -o out.cnf [--prefix layers.json]` |
| `decode_verify.py` | `python decode_verify.py out.cnf.map.json solver_output.txt`: prints the network, exits 0 iff it sorts |
| `validate.py` | regenerates n = 3..10 and checks SAT at a(n), UNSAT at a(n)−1 (all pass; needs `pip install python-sat`) |

## Calibration ladder (known answers)

| instance | expected | notes |
|---|---|---|
| n=11, d=7 | UNSAT | a(11) = 8 (Bundala et al. 2014) |
| n=12, d=7 / d=8 | UNSAT / SAT | a(12) = 8 |
| n=14, d=8 | UNSAT | a(14) = 9 |
| n=16, d=8 / d=9 | UNSAT / SAT | a(16) = 9 (Bundala et al. 2014) |
| n=17, d=9 / d=10 | UNSAT / SAT | a(17) = 10 |
| n=18, d=11 | SAT | known depth-11 networks |
| **n=18, d=10** | **open** | |

The original proofs for n = 11–17 did not solve one monolithic CNF. They enumerated 2- or 3-layer prefixes up
to symmetry and solved one instance per prefix, with lots of CPU. So a solver that handles the monolithic
n=16/17 UNSAT instances quickly is already doing something remarkable.

### Baseline: off-the-shelf CaDiCaL

CaDiCaL 1.5.3 (via PySAT), default settings, 1 thread on an Intel i5-12600K, run at below-normal priority on a
shared machine:

| instance | result | time |
|---|---|---|
| n=11, d=7 | UNSAT (correct) | 1,264 s |
| n=12, d=8 | SAT (correct; the model is a 43-comparator network that passes `decode_verify.py`) | 111 s |
| n=12, d=7 | UNSAT (correct) | 2,142 s |

Larger rungs were not attempted. A time of about half an hour at n = 12 suggests that the n = 16–18 instances are
far out of reach for a standard solver run on the monolithic CNF.

## Encoding (sound and complete; details in the header of `gen_depth_cnf.py`)

* **First layer fixed** to (0,1),(2,3),…,(16,17). Parberry (1991) showed this loses no generality for optimal depth.
* **0/1 principle:** only the 19,664 distinct unsorted outputs of the first layer are encoded.
* **Comparator variables** for each free layer, with at most one comparator per channel.
* **One-sided value variables (upper bounds):** for an input with k ones, the outputs on channels 0..n−k−1 must
  be 0. Comparators preserve the number of ones, so this is equivalent to "sorted".
* **Last layer uses only adjacent comparators (i,i+1).** This holds for every non-redundant sorting network (Codish,
  Cruz-Filipe, Schneider-Kamp 2015). Pass `--no-last-adjacent` to drop it; `validate.py` checks both variants.
* **No symmetry breaking** beyond the fixed first layer (the reflection symmetry is still present), so the
  encoding is easy to audit. `--prefix` takes any longer fixed prefix, e.g. to split the problem into one CNF per
  symmetry-reduced 2-layer prefix, as the published proofs did.
