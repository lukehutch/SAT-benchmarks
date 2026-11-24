#!/usr/bin/env python3
"""DIMACS CNF for peaceable queens (A250000): can m white and m black queens share an n X n board with no
queen attacking one of the other color?

    python gen_queens.py N M [-o out.cnf]

Variables: W(r,c) = r*n + c + 1 and B(r,c) = n*n + r*n + c + 1. Each square holds at most one queen. A white and
a black queen never share a row, column or diagonal. At least M of each color (Sinz sequential counters).

SAT <=> a(n) >= M.   UNSAT <=> a(n) < M.
No symmetry breaking (the board's 8 symmetries and the color swap are left in).
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "common"))
from cnf import CNF  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("n", type=int)
    ap.add_argument("m", type=int)
    ap.add_argument("-o", "--out")
    a = ap.parse_args()
    n, m = a.n, a.m
    out = a.out or f"queens_n{n}_m{m}.cnf"
    f = CNF()
    W = [[f.var() for c in range(n)] for r in range(n)]
    B = [[f.var() for c in range(n)] for r in range(n)]
    sq = [(r, c) for r in range(n) for c in range(n)]
    for r, c in sq:
        f.add([-W[r][c], -B[r][c]])
    for i, (r1, c1) in enumerate(sq):
        for r2, c2 in sq[i + 1:]:
            if r1 == r2 or c1 == c2 or r1 - c1 == r2 - c2 or r1 + c1 == r2 + c2:
                f.add([-W[r1][c1], -B[r2][c2]])
                f.add([-B[r1][c1], -W[r2][c2]])
    f.at_least([W[r][c] for r, c in sq], m)
    f.at_least([B[r][c] for r, c in sq], m)
    f.write(out, [f"peaceable queens: {m} white + {m} black on {n}x{n}, no cross-color attacks",
                  "vars 1..n^2 = white at (r,c) -> r*n+c+1; n^2+1..2n^2 = black",
                  f"SAT <=> A250000({n}) >= {m}"])
    json.dump({"problem": "queens", "n": n, "m": m}, open(out + ".map.json", "w"))
    print(f"{out}: {f.nv} vars, {len(f.clauses)} clauses", file=sys.stderr)


if __name__ == "__main__":
    main()
