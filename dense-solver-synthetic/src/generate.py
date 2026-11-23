"""Recreate the published DIMACS files in a directory of your choice."""
import argparse
from itertools import combinations
from pathlib import Path
import sys

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))
import families  # noqa: E402

# At-most-one encodings from PySAT, by the file-name suffix they get.
PYSAT_ENCODINGS = {
    "sequential": EncType.seqcounter,
    "sortnetwrk": EncType.sortnetwrk,
    "cardnetwrk": EncType.cardnetwrk,
    "bitwise": EncType.bitwise,
    "ladder": EncType.ladder,
    "totalizer": EncType.totalizer,
    "mtotalizer": EncType.mtotalizer,
    "kmtotalizer": EncType.kmtotalizer,
}


def pigeonhole(pigeons, holes, encoding="pairwise"):
    formula = CNF()
    pool = IDPool(start_from=pigeons * holes + 1)
    rows = [list(range(1 + p * holes, 1 + (p + 1) * holes)) for p in range(pigeons)]
    for row in rows:
        formula.append(row)
    for hole in zip(*rows):
        if encoding == "pairwise":
            for first, second in combinations(hole, 2):
                formula.append([-first, -second])
        else:
            formula.extend(CardEnc.atmost(lits=list(hole), bound=1, vpool=pool,
                                          encoding=PYSAT_ENCODINGS[encoding]))
    return formula


def write_family(path, variables, clauses):
    path.write_text(families.dimacs(variables, clauses))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    args.directory.mkdir(parents=True, exist_ok=True)
    # The six original pairwise and sequential inputs.
    specs = [(9, 8, "pairwise"), (9, 8, "sequential"), (31, 30, "pairwise"), (31, 30, "sequential"),
             (65, 64, "pairwise"), (65, 64, "sequential")]
    specs += [(9, 8, name) for name in PYSAT_ENCODINGS if name != "sequential"]
    # Satisfiable controls: as many holes as pigeons.
    specs += [(8, 8, "pairwise"), (8, 8, "sequential")]
    for pigeons, holes, encoding in specs:
        name = f"php{pigeons}x{holes}-{encoding}.cnf"
        pigeonhole(pigeons, holes, encoding).to_file(str(args.directory / name))
    write_family(args.directory / "php9x8-pairwise-functional.cnf",
                 *families.pigeonhole(9, 8, "pairwise", functional=True))
    write_family(args.directory / "php9x8-sequential-renamed.cnf",
                 *families.rename(*families.pigeonhole(9, 8, "sequential"), seed=5))
    for size in (12, 16, 32):
        write_family(args.directory / f"chessboard{size}.cnf",
                     *families.mutilated_chessboard(size))


if __name__ == "__main__":
    main()
