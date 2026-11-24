#!/usr/bin/env python3
"""Check a model of a gen_vdw.py instance: the coloring of [1..N] has no red 3-AP and no blue t-AP.

    python verify.py out.cnf.map.json solver_output.txt

Independent of the CNF: the check scans every progression by start and difference with run lengths.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "common"))
from cnf import read_model  # noqa: E402


def longest_mono_ap(col, color):
    """Length of the longest arithmetic progression all of `color` in col[1..N]."""
    N = len(col) - 1
    best = 0
    for d in range(1, N):
        for start in range(1, d + 1):      # walk each residue class, tracking runs
            run = 0
            for i in range(start, N + 1, d):
                run = run + 1 if col[i] == color else 0
                best = max(best, run)
    return best


def main():
    meta = json.load(open(sys.argv[1]))
    true = read_model(sys.argv[2])
    N, t = meta["N"], meta["t"]
    col = [None] + ["R" if i in true else "B" for i in range(1, N + 1)]
    r, b = longest_mono_ap(col, "R"), longest_mono_ap(col, "B")
    print("coloring:", "".join(col[1:]))
    ok = r < 3 and b < t
    print(f"N={N}: longest red AP {r} (< 3 needed), longest blue AP {b} (< {t} needed): "
          + (f"VALID, so w(2;3,{t}) > {N}" if ok else "INVALID"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
