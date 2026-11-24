#!/usr/bin/env python3
"""Check a model of a gen_points.py instance: draw the painted points and confirm no forbidden pattern.

    python verify.py out.cnf.map.json solver_output.txt

Independent of the generator's enumeration: every PAIR of painted points is taken as one side of a square (both
sides of the line) or of an equilateral triangle (both orientations), the remaining corners are computed, and
the pattern counts if those corners are painted and the shape is of the forbidden kind.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "common"))
from cnf import read_model  # noqa: E402


def violations(pattern, painted):
    S = set(painted)
    bad = []
    pl = sorted(S)
    for i, p in enumerate(pl):
        for q in pl[i + 1:]:
            a, b = q[0] - p[0], q[1] - p[1]
            if pattern.startswith("sq"):
                for (ra, rb) in ((-b, a), (b, -a)):              # rotate the side by +-90 degrees
                    r, s = (q[0] + ra, q[1] + rb), (p[0] + ra, p[1] + rb)
                    if r in S and s in S and (pattern == "sq-any" or a == 0 or b == 0):
                        bad.append((p, q, r, s))
            else:
                for (ra, rb) in ((-b, a + b), (a + b, -a)):      # rotate by +-60 degrees (axial coords)
                    r = (p[0] + ra, p[1] + rb)
                    if r not in S:
                        continue
                    tri = sorted((p, q, r))
                    sides = [(tri[j][0] - tri[k][0], tri[j][1] - tri[k][1]) for j, k in ((1, 0), (2, 0), (2, 1))]
                    aligned = all(dx == 0 or dy == 0 or dx == -dy for dx, dy in sides)
                    if pattern == "tri-any":
                        bad.append(tri)
                    elif aligned:
                        # upward iff two vertices share the lowest y (base on the bottom)
                        ys = sorted(v[1] for v in tri)
                        upward = ys[0] == ys[1]
                        if pattern == "tri-axis" or upward:
                            bad.append(tri)
    return sorted({tuple(sorted(c)) for c in bad})     # each shape is found once per side; count it once


def main():
    meta = json.load(open(sys.argv[1]))
    true = read_model(sys.argv[2])
    pts = [tuple(p) for p in meta["points"]]
    painted = [p for i, p in enumerate(pts) if i + 1 in true]
    n, pat = meta["n"], meta["pattern"]
    S = set(painted)
    for y in reversed(range(n)):
        row = [("#" if (x, y) in S else ".") for x in range(n) if (x, y) in set(pts)]
        indent = " " * y if pat.startswith("tri") else ""
        print(indent + " ".join(row))
    bad = violations(pat, painted)
    ok = not bad and len(painted) >= meta["m"]
    print(f"{pat} n={n}: {len(painted)} painted, {len(bad)} forbidden configurations: "
          + (f"VALID, so max >= {len(painted)}" if ok else f"INVALID {bad[:3]}"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
