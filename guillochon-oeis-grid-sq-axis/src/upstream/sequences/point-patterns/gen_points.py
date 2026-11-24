#!/usr/bin/env python3
"""DIMACS CNF for "paint at least M points of a grid so that no forbidden pattern is fully painted".

    python gen_points.py PATTERN N M [-o out.cnf]

PATTERN       grid                                            forbidden configuration          max / min
sq-axis       N x N square grid (N^2 points)                  square, sides parallel to grid   A227133 / A152125
sq-any        N x N square grid                               square, any orientation          A240443
tri-up        triangular grid of side N (N(N+1)/2 points)     upward triangle, grid-aligned    A157795(N-1) / A319158(N)
tri-axis      triangular grid of side N                       triangle with sides along the
                                                              grid, either orientation         A227308 / A227116
tri-any       triangular grid of side N                       equilateral triangle, any
                                                              orientation                      A240114(N) / A319159(N-1)

(The "min" sequences count the points to remove so that every pattern is hit, i.e. points - max.)

Variables 1..P are the points, in the order of points() below (written to the .map.json sidecar). Each
forbidden configuration gets the clause "not all painted"; at least M painted (Sinz sequential counter).
SAT <=> max >= M.  No symmetry breaking.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "common"))
from cnf import CNF  # noqa: E402


def points(pattern, n):
    if pattern.startswith("sq"):
        return [(x, y) for y in range(n) for x in range(n)]
    # triangular grid in axial coordinates: x along the base, y along the left side; x, y >= 0, x + y <= n-1
    return [(x, y) for y in range(n) for x in range(n - y)]


def configurations(pattern, n):
    P = set(points(pattern, n))
    out = set()
    if pattern == "sq-axis":
        for (x, y) in P:
            for s in range(1, n):
                q = [(x, y), (x + s, y), (x, y + s), (x + s, y + s)]
                if all(p in P for p in q):
                    out.add(frozenset(q))
    elif pattern == "sq-any":
        # side vector (a, b) with a > 0, b >= 0 represents each square exactly once (from one corner)
        for (x, y) in P:
            for a in range(1, n):
                for b in range(0, n):
                    q = [(x, y), (x + a, y + b), (x + a - b, y + b + a), (x - b, y + a)]
                    if all(p in P for p in q):
                        out.add(frozenset(q))
    elif pattern in ("tri-up", "tri-axis"):
        for (x, y) in P:
            for s in range(1, n):
                up = [(x, y), (x + s, y), (x, y + s)]
                if all(p in P for p in up):
                    out.add(frozenset(up))
                down = [(x + s, y), (x, y + s), (x + s, y + s)]
                if pattern == "tri-axis" and all(p in P for p in down):
                    out.add(frozenset(down))
    elif pattern == "tri-any":
        pl = sorted(P)
        for i, p in enumerate(pl):
            for q in pl[i + 1:]:
                a, b = q[0] - p[0], q[1] - p[1]
                for (ra, rb) in ((-b, a + b), (a + b, -a)):      # rotate (a,b) by +60 and -60 degrees
                    r = (p[0] + ra, p[1] + rb)
                    if r in P:
                        out.add(frozenset((p, q, r)))
    else:
        raise SystemExit(f"unknown pattern {pattern}")
    return sorted(sorted(c) for c in out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pattern")
    ap.add_argument("n", type=int)
    ap.add_argument("m", type=int)
    ap.add_argument("-o", "--out")
    a = ap.parse_args()
    pts = points(a.pattern, a.n)
    idx = {p: i + 1 for i, p in enumerate(pts)}
    out = a.out or f"{a.pattern}_n{a.n}_m{a.m}.cnf"
    f = CNF()
    f.vars(len(pts))
    confs = configurations(a.pattern, a.n)
    for c in confs:
        f.add([-idx[p] for p in c])
    f.at_least(list(range(1, len(pts) + 1)), a.m)
    f.write(out, [f"point pattern avoidance: {a.pattern}, grid size {a.n} ({len(pts)} points), "
                  f"{len(confs)} forbidden configurations",
                  f"at least {a.m} painted points; vars 1..{len(pts)} = points (list in the .map.json)",
                  f"SAT <=> max painted >= {a.m}"])
    json.dump({"problem": "points", "pattern": a.pattern, "n": a.n, "m": a.m, "points": pts},
              open(out + ".map.json", "w"))
    print(f"{out}: {f.nv} vars, {len(f.clauses)} clauses, {len(confs)} configurations", file=sys.stderr)


if __name__ == "__main__":
    main()
