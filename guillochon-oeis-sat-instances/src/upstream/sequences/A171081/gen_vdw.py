#!/usr/bin/env python3
"""DIMACS CNF for the van der Waerden number w(2;3,t) (A171081, = A007783 shifted).

    python gen_vdw.py T N [-o out.cnf]

Variable i (1 <= i <= N) is true when i is colored RED. Every 3-term arithmetic progression in [1..N] gets the
clause "not all red", and every T-term progression gets "not all blue".

SAT   <=>  some 2-coloring of [1..N] has no red 3-AP and no blue T-AP  <=>  w(2;3,T) > N.
UNSAT <=>  w(2;3,T) <= N.

No symmetry breaking: the reflection i -> N+1-i is left in.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "common"))
from cnf import CNF  # noqa: E402


def aps(N, k):
    for d in range(1, (N - 1) // (k - 1) + 1):
        for a in range(1, N - (k - 1) * d + 1):
            yield [a + i * d for i in range(k)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("t", type=int)
    ap.add_argument("N", type=int)
    ap.add_argument("-o", "--out")
    a = ap.parse_args()
    t, N = a.t, a.N
    out = a.out or f"vdw_3_{t}_N{N}.cnf"
    f = CNF()
    f.vars(N)
    for p in aps(N, 3):
        f.add([-x for x in p])
    for p in aps(N, t):
        f.add(p)
    f.write(out, [f"van der Waerden w(2;3,{t}): 2-color [1..{N}], var i true = red",
                  "no red 3-term AP, no blue %d-term AP" % t,
                  f"SAT <=> w(2;3,{t}) > {N};  UNSAT <=> w(2;3,{t}) <= {N}"])
    json.dump({"problem": "vdw", "k": 3, "t": t, "N": N}, open(out + ".map.json", "w"))
    print(f"{out}: {f.nv} vars, {len(f.clauses)} clauses", file=sys.stderr)


if __name__ == "__main__":
    main()
