#!/usr/bin/env python3
"""Check a model of a gen_zaran.py instance: count the ones and confirm no 3 X 3 all-ones submatrix.

    python verify.py out.cnf.map.json solver_output.txt

Independent of the CNF: for each triple of rows, the columns where all three are 1 are computed as a
bitwise AND; a 3 X 3 all-ones submatrix exists iff some AND has >= 3 bits.
"""
import json
import os
import sys
from itertools import combinations

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "common"))
from cnf import read_model  # noqa: E402


def main():
    meta = json.load(open(sys.argv[1]))
    true = read_model(sys.argv[2])
    n, m = meta["n"], meta["m"]
    rows = [sum(1 << c for c in range(n) if r * n + c + 1 in true) for r in range(n)]
    print("\n".join(format(x, f"0{n}b")[::-1] for x in rows))
    ones = sum(bin(x).count("1") for x in rows)
    worst = max(bin(a & b & c).count("1") for a, b, c in combinations(rows, 3))
    ok = worst < 3 and ones >= m
    print(f"n={n}: {ones} ones; max common columns of 3 rows = {worst}: "
          + (f"VALID, so z({n};3) >= {ones}" if ok else "INVALID"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
