#!/usr/bin/env python3
"""Check a model of a gen_queens.py instance: draw the board and confirm no white queen attacks a black one.

    python verify.py out.cnf.map.json solver_output.txt

Independent of the CNF: every queen's attack rays are walked square by square.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "common"))
from cnf import read_model  # noqa: E402


def main():
    meta = json.load(open(sys.argv[1]))
    true = read_model(sys.argv[2])
    n, m = meta["n"], meta["m"]
    board = [["." for _ in range(n)] for _ in range(n)]
    for r in range(n):
        for c in range(n):
            w, b = r * n + c + 1 in true, n * n + r * n + c + 1 in true
            if w and b:
                print(f"square {(r, c)} holds both colors")
                sys.exit(1)
            board[r][c] = "W" if w else "B" if b else "."
    print("\n".join(" ".join(row) for row in board))
    bad = 0
    for r in range(n):
        for c in range(n):
            if board[r][c] != "W":
                continue
            for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1), (0, -1), (-1, 0), (-1, -1), (-1, 1)):
                rr, cc = r + dr, c + dc
                while 0 <= rr < n and 0 <= cc < n:
                    bad += board[rr][cc] == "B"
                    rr, cc = rr + dr, cc + dc
    nw = sum(row.count("W") for row in board)
    nb = sum(row.count("B") for row in board)
    ok = bad == 0 and nw >= m and nb >= m
    print(f"n={n}: {nw} white, {nb} black, {bad} attacking pairs: "
          + (f"VALID, so A250000({n}) >= {min(nw, nb)}" if ok else "INVALID"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
