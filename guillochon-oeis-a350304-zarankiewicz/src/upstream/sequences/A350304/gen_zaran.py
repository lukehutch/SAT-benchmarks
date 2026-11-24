#!/usr/bin/env python3
"""DIMACS CNF for the Zarankiewicz number z(n;3) (A350304): is there an n X n 0/1 matrix with at least M ones
and no all-ones 3 X 3 submatrix?

    python gen_zaran.py N M [-o out.cnf]

Variable r*n + c + 1 is entry (r,c). Each choice of 3 rows and 3 columns gets the clause "not all nine ones".
At least M ones (Sinz sequential counter).

SAT <=> z(n;3) >= M.  Related: A001198(n) = z+1, A347473(n) = n^2 - z - 1, A350237(n) = n^2 - z.
Symmetry breaking (default): rows and columns double-lex ordered; --no-symbreak omits it.
"""
import argparse
import json
import os
import sys
from itertools import combinations

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "common"))
from cnf import CNF  # noqa: E402


def lex_geq(f, a, b):
    """a >=_lex b (0/1 vectors, first position most significant).  e[k] is forced true while a and b agree
    on positions < k; wherever it is true, a[k] >= b[k] must hold."""
    e = [None] + [f.var() for _ in range(len(a) - 1)]
    for k in range(len(a)):
        pre = [] if k == 0 else [-e[k]]
        f.add(pre + [a[k], -b[k]])                       # prefix equal -> a[k] >= b[k]
        if k + 1 < len(a):
            f.add(pre + [-a[k], -b[k], e[k + 1]])        # prefix equal and a[k] = b[k] = 1 -> still equal
            f.add(pre + [a[k], b[k], e[k + 1]])          # prefix equal and a[k] = b[k] = 0 -> still equal


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("n", type=int)
    ap.add_argument("m", type=int)
    ap.add_argument("-o", "--out")
    ap.add_argument("--no-symbreak", action="store_true", help="omit the double-lex symmetry breaking")
    a = ap.parse_args()
    n, m = a.n, a.m
    out = a.out or f"zaran3_n{n}_m{m}.cnf"
    f = CNF()
    X = [[f.var() for c in range(n)] for r in range(n)]
    for rows in combinations(range(n), 3):
        for cols in combinations(range(n), 3):
            f.add([-X[r][c] for r in rows for c in cols])
    f.at_least([X[r][c] for r in range(n) for c in range(n)], m)
    if not a.no_symbreak:
        # Double lex: consecutive rows, and consecutive columns, are lexicographically non-increasing.
        # Every 0/1 matrix can be brought to this form by permuting rows and columns (Flener, Frisch,
        # Hnich, Kiziltan, Miguel, Pearson, Walsh, "Breaking row and column symmetries in matrix models", 2002).
        for i in range(n - 1):
            lex_geq(f, X[i], X[i + 1])
            lex_geq(f, [X[r][i] for r in range(n)], [X[r][i + 1] for r in range(n)])
    f.write(out, [f"Zarankiewicz z({n};3): {n}x{n} 0/1 matrix, >= {m} ones, no all-ones 3x3 submatrix",
                  "var r*n+c+1 = entry (r,c)",
                  "symmetry breaking: " + ("none" if a.no_symbreak else "double-lex rows and columns (non-increasing)"),
                  f"SAT <=> A350304({n}) >= {m}"])
    json.dump({"problem": "zarankiewicz", "n": n, "s": 3, "m": m}, open(out + ".map.json", "w"))
    print(f"{out}: {f.nv} vars, {len(f.clauses)} clauses", file=sys.stderr)


if __name__ == "__main__":
    main()
