"""Write a domino-tiling CNF with the two opposite corners removed."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))
from families import chessboard_cells, chessboard_clauses


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("size", type=int)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.size < 2:
        parser.error("size must be at least 2")
    variables, cells = chessboard_cells(args.size)
    count = sum(1 + len(c) * (len(c) - 1) // 2 for c in cells)
    with args.output.open("x") as out:
        out.write(f"p cnf {variables} {count}\n")
        for clause in chessboard_clauses(cells):
            out.write(" ".join(map(str, clause)) + " 0\n")


if __name__ == "__main__":
    main()
